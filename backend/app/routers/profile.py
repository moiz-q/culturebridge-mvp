"""
Profile management API endpoints.

Requirements: 2.1, 2.2, 2.3, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.models.profile import ClientProfile, CoachProfile
from app.repositories.user_repository import UserRepository
from app.repositories.profile_repository import ClientProfileRepository, CoachProfileRepository
from app.schemas.profile import (
    ClientProfileCreate,
    ClientProfileUpdate,
    ClientProfileResponse,
    CoachProfileCreate,
    CoachProfileUpdate,
    CoachProfileResponse,
    CoachListResponse,
    PhotoUploadResponse,
    ProfileResponse
)
from app.middleware.auth_middleware import get_current_user
from app.utils.s3_utils import s3_service
from app.utils.response_cache import cache_response, invalidate_endpoint_cache


router = APIRouter(prefix="/profile", tags=["profile"])
coaches_router = APIRouter(prefix="/coaches", tags=["coaches"])


# Profile Endpoints

@router.get("", response_model=ProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile.
    
    Requirements: 2.1, 3.1
    """
    profile_data = None
    
    if current_user.role == UserRole.CLIENT:
        client_repo = ClientProfileRepository(db)
        profile = client_repo.get_by_user_id(current_user.id)
        if profile:
            profile_data = ClientProfileResponse.model_validate(profile)
    
    elif current_user.role == UserRole.COACH:
        coach_repo = CoachProfileRepository(db)
        profile = coach_repo.get_by_user_id(current_user.id)
        if profile:
            profile_data = CoachProfileResponse.model_validate(profile)
    
    return ProfileResponse(
        user_id=current_user.id,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        email_verified=current_user.email_verified,
        profile=profile_data
    )


@router.put("", response_model=ClientProfileResponse | CoachProfileResponse)
async def update_profile(
    profile_update: ClientProfileUpdate | CoachProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    Requirements: 2.1, 2.2, 3.1, 3.2, 3.3, 3.4, 3.5
    """
    if current_user.role == UserRole.CLIENT:
        if not isinstance(profile_update, ClientProfileUpdate):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid profile data for client"
            )
        
        client_repo = ClientProfileRepository(db)
        profile = client_repo.get_by_user_id(current_user.id)
        
        if not profile:
            # Create new profile if doesn't exist
            if not isinstance(profile_update, ClientProfileCreate):
                # Convert update to create by ensuring quiz_data is present
                if not profile_update.quiz_data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="quiz_data is required for new client profile"
                    )
            
            profile = ClientProfile(
                user_id=current_user.id,
                quiz_data=profile_update.quiz_data.model_dump() if profile_update.quiz_data else {}
            )
            profile = client_repo.create(profile)
        
        # Update fields
        update_data = profile_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'quiz_data' and value:
                # Validate quiz data has all 20 required factors
                setattr(profile, field, value.model_dump())
                if not profile.validate_quiz_data():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Quiz data must contain all 20 required matching factors"
                    )
            elif value is not None:
                setattr(profile, field, value)
        
        profile = client_repo.update(profile)
        
        # Invalidate match cache when client profile is updated
        from app.utils.cache_utils import invalidate_client_match_cache
        invalidate_client_match_cache(str(current_user.id))
        
        return ClientProfileResponse.model_validate(profile)
    
    elif current_user.role == UserRole.COACH:
        if not isinstance(profile_update, CoachProfileUpdate):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid profile data for coach"
            )
        
        coach_repo = CoachProfileRepository(db)
        profile = coach_repo.get_by_user_id(current_user.id)
        
        if not profile:
            # Create new profile if doesn't exist
            profile = CoachProfile(user_id=current_user.id)
            profile = coach_repo.create(profile)
        
        # Update fields
        update_data = profile_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(profile, field, value)
        
        # Validate hourly rate if updated
        if profile.hourly_rate and not profile.validate_hourly_rate():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hourly rate must be between $25 and $500"
            )
        
        profile = coach_repo.update(profile)
        
        # Invalidate all match cache when coach profile is updated
        from app.utils.cache_utils import invalidate_all_match_cache
        invalidate_all_match_cache()
        
        return CoachProfileResponse.model_validate(profile)
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users do not have profiles"
        )


@router.post("/photo", response_model=PhotoUploadResponse)
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload profile photo to S3.
    
    Requirements: 2.3
    Validates: 5MB max, JPEG/PNG/WebP formats
    """
    # Read file content
    file_content = await file.read()
    
    try:
        # Upload to S3
        photo_url = s3_service.upload_profile_photo(
            file_content=file_content,
            filename=file.filename,
            user_id=str(current_user.id)
        )
        
        # Update profile with photo URL
        if current_user.role == UserRole.CLIENT:
            client_repo = ClientProfileRepository(db)
            profile = client_repo.get_by_user_id(current_user.id)
            if profile:
                # Delete old photo if exists
                if profile.photo_url:
                    s3_service.delete_file(profile.photo_url)
                profile.photo_url = photo_url
                client_repo.update(profile)
        
        elif current_user.role == UserRole.COACH:
            coach_repo = CoachProfileRepository(db)
            profile = coach_repo.get_by_user_id(current_user.id)
            if profile:
                # Delete old photo if exists
                if profile.photo_url:
                    s3_service.delete_file(profile.photo_url)
                profile.photo_url = photo_url
                coach_repo.update(profile)
        
        return PhotoUploadResponse(
            photo_url=photo_url,
            message="Profile photo uploaded successfully"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload photo: {str(e)}"
        )


# Coach Discovery Endpoints

@coaches_router.get("", response_model=List[CoachListResponse])
@cache_response(ttl_seconds=300, key_prefix="coaches_list", include_query_params=True)
async def get_coaches(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    language: Optional[str] = None,
    country: Optional[str] = None,
    expertise: Optional[str] = None,
    min_rate: Optional[float] = None,
    max_rate: Optional[float] = None,
    is_verified: Optional[bool] = None,
    min_rating: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of coaches with optional filters.
    Cached for 5 minutes to improve performance.
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 8.1
    """
    coach_repo = CoachProfileRepository(db)
    
    coaches = coach_repo.get_all(
        skip=skip,
        limit=limit,
        language=language,
        country=country,
        expertise=expertise,
        min_rate=min_rate,
        max_rate=max_rate,
        is_verified=is_verified,
        min_rating=min_rating
    )
    
    return [CoachListResponse.model_validate(coach) for coach in coaches]


@coaches_router.get("/{coach_id}", response_model=CoachProfileResponse)
async def get_coach_by_id(
    coach_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get coach profile by ID.
    
    Requirements: 3.1
    """
    coach_repo = CoachProfileRepository(db)
    coach = coach_repo.get_by_user_id(coach_id)
    
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach not found"
        )
    
    return CoachProfileResponse.model_validate(coach)


@coaches_router.put("/{coach_id}", response_model=CoachProfileResponse)
async def update_coach_profile(
    coach_id: UUID,
    profile_update: CoachProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update coach profile (coach can only update their own profile).
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
    """
    # Check if user is updating their own profile or is admin
    if current_user.id != coach_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    # Check if user is a coach
    if current_user.id == coach_id and current_user.role != UserRole.COACH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coaches can update coach profiles"
        )
    
    coach_repo = CoachProfileRepository(db)
    profile = coach_repo.get_by_user_id(coach_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach profile not found"
        )
    
    # Update fields
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(profile, field, value)
    
    # Validate hourly rate if updated
    if profile.hourly_rate and not profile.validate_hourly_rate():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hourly rate must be between $25 and $500"
        )
    
    profile = coach_repo.update(profile)
    
    # Invalidate all match cache when coach profile is updated
    from app.utils.cache_utils import invalidate_all_match_cache
    invalidate_all_match_cache()
    
    # Invalidate coaches list cache
    invalidate_endpoint_cache("coaches_list")
    
    return CoachProfileResponse.model_validate(profile)


# GDPR Compliance Endpoints

@router.get("/export")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export all user data as JSON (GDPR compliance).
    
    Requirements: 2.4
    """
    from app.models.booking import Booking
    from app.models.community import Post, Comment, Bookmark
    
    user_data = {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role.value,
            "is_active": current_user.is_active,
            "email_verified": current_user.email_verified,
            "created_at": current_user.created_at.isoformat(),
            "updated_at": current_user.updated_at.isoformat()
        },
        "profile": None,
        "bookings": [],
        "posts": [],
        "comments": [],
        "bookmarks": []
    }
    
    # Export profile data
    if current_user.role == UserRole.CLIENT:
        client_repo = ClientProfileRepository(db)
        profile = client_repo.get_by_user_id(current_user.id)
        if profile:
            user_data["profile"] = {
                "id": str(profile.id),
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "photo_url": profile.photo_url,
                "phone": profile.phone,
                "timezone": profile.timezone,
                "quiz_data": profile.quiz_data,
                "preferences": profile.preferences,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat()
            }
    
    elif current_user.role == UserRole.COACH:
        coach_repo = CoachProfileRepository(db)
        profile = coach_repo.get_by_user_id(current_user.id)
        if profile:
            user_data["profile"] = {
                "id": str(profile.id),
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "photo_url": profile.photo_url,
                "bio": profile.bio,
                "intro_video_url": profile.intro_video_url,
                "expertise": profile.expertise,
                "languages": profile.languages,
                "countries": profile.countries,
                "hourly_rate": float(profile.hourly_rate) if profile.hourly_rate else None,
                "currency": profile.currency,
                "availability": profile.availability,
                "rating": float(profile.rating),
                "total_sessions": profile.total_sessions,
                "is_verified": profile.is_verified,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat()
            }
    
    # Export bookings
    bookings = db.query(Booking).filter(
        (Booking.client_id == current_user.id) | (Booking.coach_id == current_user.id)
    ).all()
    
    for booking in bookings:
        user_data["bookings"].append({
            "id": str(booking.id),
            "client_id": str(booking.client_id),
            "coach_id": str(booking.coach_id),
            "session_datetime": booking.session_datetime.isoformat(),
            "duration_minutes": booking.duration_minutes,
            "status": booking.status.value,
            "meeting_link": booking.meeting_link,
            "notes": booking.notes,
            "created_at": booking.created_at.isoformat()
        })
    
    # Export posts
    posts = db.query(Post).filter(Post.author_id == current_user.id).all()
    for post in posts:
        user_data["posts"].append({
            "id": str(post.id),
            "title": post.title,
            "content": post.content,
            "post_type": post.post_type.value,
            "is_private": post.is_private,
            "upvotes": post.upvotes,
            "created_at": post.created_at.isoformat()
        })
    
    # Export comments
    comments = db.query(Comment).filter(Comment.author_id == current_user.id).all()
    for comment in comments:
        user_data["comments"].append({
            "id": str(comment.id),
            "post_id": str(comment.post_id),
            "content": comment.content,
            "created_at": comment.created_at.isoformat()
        })
    
    # Export bookmarks
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
    for bookmark in bookmarks:
        user_data["bookmarks"].append({
            "id": str(bookmark.id),
            "resource_id": str(bookmark.resource_id),
            "created_at": bookmark.created_at.isoformat()
        })
    
    return user_data


@router.delete("")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account and all associated data (GDPR compliance).
    Implements cascade deletion for related records.
    
    Requirements: 2.4
    """
    user_repo = UserRepository(db)
    
    # Delete profile photo from S3 if exists
    if current_user.role == UserRole.CLIENT:
        client_repo = ClientProfileRepository(db)
        profile = client_repo.get_by_user_id(current_user.id)
        if profile and profile.photo_url:
            s3_service.delete_file(profile.photo_url)
    
    elif current_user.role == UserRole.COACH:
        coach_repo = CoachProfileRepository(db)
        profile = coach_repo.get_by_user_id(current_user.id)
        if profile and profile.photo_url:
            s3_service.delete_file(profile.photo_url)
    
    # Delete user (cascade will delete all related records)
    # Related records deleted by cascade:
    # - ClientProfile or CoachProfile
    # - Bookings (as client or coach)
    # - Posts
    # - Comments
    # - Bookmarks
    # - Resources created
    user_repo.delete(current_user)
    
    return {
        "message": "User account and all associated data have been permanently deleted",
        "user_id": str(current_user.id)
    }
