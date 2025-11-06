"""
Authentication API endpoints.

Requirements: 1.1, 1.2, 1.3, 1.5
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import AuthService, AuthenticationError
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    AuthResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordResetConfirmRequest,
    PasswordResetConfirmResponse,
    ChangePasswordRequest,
    UserResponse,
    ErrorResponse
)
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.config import settings


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
    }
)


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email, password, and role assignment",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input or email already exists"},
    }
)
async def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password.
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **role**: User role (client, coach, or admin)
    
    Returns user data and JWT tokens.
    
    Requirements: 1.1
    """
    auth_service = AuthService(db)
    
    try:
        user, access_token, refresh_token = auth_service.signup(
            email=request.email,
            password=request.password,
            role=request.role
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return AuthResponse(
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            email_verified=user.email_verified,
            created_at=user.created_at
        ),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRY_HOURS * 3600
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    description="Authenticate user with email and password, returns JWT tokens",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    }
)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with email and password.
    
    - **email**: Registered email address
    - **password**: User password
    
    Returns user data and JWT tokens (access token valid for 24 hours).
    
    Requirements: 1.2
    """
    auth_service = AuthService(db)
    
    try:
        user, access_token, refresh_token = auth_service.login(
            email=request.email,
            password=request.password
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return AuthResponse(
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            email_verified=user.email_verified,
            created_at=user.created_at
        ),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRY_HOURS * 3600
    )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="Generate new access token using refresh token",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid or expired refresh token"},
    }
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Generate new access token from refresh token.
    
    - **refresh_token**: Valid refresh token (7-day expiry)
    
    Returns new access token.
    
    Requirements: 1.2
    """
    auth_service = AuthService(db)
    
    try:
        access_token = auth_service.refresh_access_token(request.refresh_token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRY_HOURS * 3600
    )


@router.post(
    "/reset-password",
    response_model=PasswordResetResponse,
    summary="Request password reset",
    description="Send password reset link to user email",
    responses={
        200: {"description": "Reset link sent (if email exists)"},
    }
)
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset for user account.
    
    - **email**: Registered email address
    
    Sends password reset link to email (if exists).
    For security, always returns success message.
    
    Requirements: 1.3
    """
    auth_service = AuthService(db)
    
    try:
        reset_token = auth_service.request_password_reset(request.email)
        
        # TODO: Send email with reset link
        # email_service.send_password_reset_email(request.email, reset_token)
        
        # In development, return token for testing
        if settings.ENVIRONMENT == "development":
            return PasswordResetResponse(
                message="If email exists, reset link will be sent",
                reset_token=reset_token
            )
        
    except AuthenticationError:
        # Don't reveal if email exists
        pass
    
    return PasswordResetResponse(
        message="If email exists, reset link will be sent"
    )


@router.post(
    "/reset-password/confirm",
    response_model=PasswordResetConfirmResponse,
    summary="Confirm password reset",
    description="Reset password using token from email",
    responses={
        200: {"description": "Password reset successful"},
        400: {"description": "Invalid or expired token"},
    }
)
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using token from email.
    
    - **token**: Password reset token from email
    - **new_password**: New password (minimum 8 characters)
    
    Requirements: 1.3
    """
    auth_service = AuthService(db)
    
    try:
        auth_service.reset_password(
            token=request.token,
            new_password=request.new_password
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return PasswordResetConfirmResponse(
        message="Password reset successful"
    )


@router.post(
    "/change-password",
    response_model=PasswordResetConfirmResponse,
    summary="Change password",
    description="Change password for authenticated user",
    responses={
        200: {"description": "Password changed successfully"},
        400: {"description": "Invalid current password"},
        401: {"description": "Authentication required"},
    }
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for authenticated user.
    
    Requires authentication token.
    
    - **current_password**: Current password
    - **new_password**: New password (minimum 8 characters)
    """
    auth_service = AuthService(db)
    
    try:
        auth_service.change_password(
            user_id=str(current_user.id),
            current_password=request.current_password,
            new_password=request.new_password
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return PasswordResetConfirmResponse(
        message="Password changed successfully"
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information",
    responses={
        200: {"description": "User data"},
        401: {"description": "Authentication required"},
    }
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Requires authentication token.
    
    Returns user profile data.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User logout",
    description="Logout user (client-side token removal)",
    responses={
        204: {"description": "Logout successful"},
    }
)
async def logout():
    """
    Logout user.
    
    Since JWT is stateless, logout is handled client-side by removing tokens.
    This endpoint exists for API consistency and future token blacklisting.
    """
    # TODO: Implement token blacklisting in Redis if needed
    return None
