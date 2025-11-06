"""
API endpoints for AI-powered coach matching.

Requirements: 4.1, 4.3, 4.4, 4.5
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import asyncio

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.models.profile import ClientProfile
from app.repositories.profile_repository import ClientProfileRepository
from app.services.matching_service import MatchingService
from app.schemas.matching import (
    MatchRequest,
    MatchResponse,
    CoachMatchResult,
    MatchCacheInfo
)
from app.utils.cache_utils import (
    get_match_cache,
    set_match_cache,
    cache_service
)


router = APIRouter(prefix="/match", tags=["matching"])


@router.post("", response_model=MatchResponse, status_code=status.HTTP_200_OK)
async def get_coach_matches(
    request: MatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated coach matches for the current client.
    
    Requirements: 4.1, 4.3, 4.4, 4.5
    
    - Analyzes client quiz data and profile preferences
    - Returns ranked list of up to 10 coaches with confidence scores
    - Caches results for 24 hours to reduce API calls
    - Falls back to top-rated coaches if AI matching fails
    
    **Authentication required**: Client role only
    
    Args:
        request: Match request parameters
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        MatchResponse with ranked coach matches
        
    Raises:
        HTTPException 403: If user is not a client
        HTTPException 404: If client profile not found
        HTTPException 500: If matching service fails
    """
    # Verify user is a client
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can request coach matches"
        )
    
    # Get client profile
    client_repo = ClientProfileRepository(db)
    client_profile = client_repo.get_by_user_id(current_user.id)
    
    if not client_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found. Please complete your profile first."
        )
    
    # Validate quiz data
    if not client_profile.validate_quiz_data():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incomplete quiz data. Please complete all 20 required matching factors."
        )
    
    # Generate cache key
    matching_service = MatchingService(db)
    cache_key = MatchingService.generate_cache_key(
        current_user.id,
        client_profile.quiz_data
    )
    
    # Check cache if requested
    cached_results = None
    if request.use_cache:
        cached_results = get_match_cache(cache_key)
    
    if cached_results:
        # Return cached results
        return MatchResponse(
            matches=[CoachMatchResult(**match) for match in cached_results['matches']],
            total_matches=cached_results['total_matches'],
            cached=True,
            generated_at=cached_results['generated_at']
        )
    
    # Generate new matches
    try:
        matches = await matching_service.find_matches(
            client=client_profile,
            limit=request.limit
        )
        
        # Prepare response
        generated_at = datetime.utcnow().isoformat()
        response_data = {
            'matches': matches,
            'total_matches': len(matches),
            'generated_at': generated_at
        }
        
        # Cache results for 24 hours
        set_match_cache(cache_key, response_data, ttl_hours=24)
        
        return MatchResponse(
            matches=[CoachMatchResult(**match) for match in matches],
            total_matches=len(matches),
            cached=False,
            generated_at=generated_at
        )
        
    except asyncio.TimeoutError:
        # Timeout - return fallback matches
        fallback_matches = await matching_service.get_fallback_matches(limit=request.limit)
        
        return MatchResponse(
            matches=[CoachMatchResult(**match) for match in fallback_matches],
            total_matches=len(fallback_matches),
            cached=False,
            generated_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        print(f"Error in get_coach_matches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate coach matches. Please try again later."
        )


@router.get("/cache/info", response_model=MatchCacheInfo, status_code=status.HTTP_200_OK)
async def get_match_cache_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cache information for current client's matches.
    
    **Authentication required**: Client role only
    
    Args:
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        MatchCacheInfo with cache status and TTL
        
    Raises:
        HTTPException 403: If user is not a client
        HTTPException 404: If client profile not found
    """
    # Verify user is a client
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can access match cache info"
        )
    
    # Get client profile
    client_repo = ClientProfileRepository(db)
    client_profile = client_repo.get_by_user_id(current_user.id)
    
    if not client_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )
    
    # Generate cache key
    cache_key = MatchingService.generate_cache_key(
        current_user.id,
        client_profile.quiz_data
    )
    
    # Check cache status
    exists = cache_service.exists(cache_key)
    ttl = cache_service.get_ttl(cache_key) if exists else None
    
    return MatchCacheInfo(
        cache_key=cache_key,
        exists=exists,
        ttl_seconds=ttl
    )


@router.delete("/cache", status_code=status.HTTP_204_NO_CONTENT)
async def clear_match_cache(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear cached match results for current client.
    
    Useful when client wants to force refresh of match results.
    
    **Authentication required**: Client role only
    
    Args:
        current_user: Authenticated user from JWT token
        db: Database session
        
    Raises:
        HTTPException 403: If user is not a client
    """
    # Verify user is a client
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can clear match cache"
        )
    
    # Clear all match cache for this client
    from app.utils.cache_utils import invalidate_client_match_cache
    invalidate_client_match_cache(str(current_user.id))
    
    return None
