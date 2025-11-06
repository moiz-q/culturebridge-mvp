"""
Pydantic schemas for API request/response validation.
"""
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm
)
from app.schemas.profile import (
    QuizData,
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

__all__ = [
    # Auth schemas
    "SignupRequest",
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    # Profile schemas
    "QuizData",
    "ClientProfileCreate",
    "ClientProfileUpdate",
    "ClientProfileResponse",
    "CoachProfileCreate",
    "CoachProfileUpdate",
    "CoachProfileResponse",
    "CoachListResponse",
    "PhotoUploadResponse",
    "ProfileResponse"
]
