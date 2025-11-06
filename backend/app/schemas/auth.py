"""
Pydantic schemas for authentication endpoints.

Requirements: 1.1, 1.2, 1.3, 1.5
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class SignupRequest(BaseModel):
    """
    Request schema for user signup.
    
    Requirements: 1.1
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    role: UserRole = Field(..., description="User role (client, coach, or admin)")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "role": "client"
            }
        }


class LoginRequest(BaseModel):
    """
    Request schema for user login.
    
    Requirements: 1.2
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class TokenResponse(BaseModel):
    """
    Response schema for authentication tokens.
    
    Requirements: 1.2
    """
    access_token: str = Field(..., description="JWT access token (24h expiry)")
    refresh_token: str = Field(..., description="JWT refresh token (7d expiry)")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=86400, description="Token expiry in seconds (24 hours)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


class RefreshTokenRequest(BaseModel):
    """
    Request schema for token refresh.
    
    Requirements: 1.2
    """
    refresh_token: str = Field(..., description="Valid refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class RefreshTokenResponse(BaseModel):
    """
    Response schema for token refresh.
    
    Requirements: 1.2
    """
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=86400, description="Token expiry in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


class PasswordResetRequest(BaseModel):
    """
    Request schema for password reset.
    
    Requirements: 1.3
    """
    email: EmailStr = Field(..., description="User email address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetResponse(BaseModel):
    """
    Response schema for password reset request.
    
    Requirements: 1.3
    """
    message: str = Field(..., description="Success message")
    reset_token: Optional[str] = Field(None, description="Password reset token (for testing only)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "If email exists, reset link will be sent"
            }
        }


class PasswordResetConfirmRequest(BaseModel):
    """
    Request schema for password reset confirmation.
    
    Requirements: 1.3
    """
    token: str = Field(..., description="Password reset token from email")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "new_password": "newsecurepassword123"
            }
        }


class PasswordResetConfirmResponse(BaseModel):
    """
    Response schema for password reset confirmation.
    
    Requirements: 1.3
    """
    message: str = Field(..., description="Success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Password reset successful"
            }
        }


class ChangePasswordRequest(BaseModel):
    """
    Request schema for password change (authenticated user).
    """
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newsecurepassword123"
            }
        }


class UserResponse(BaseModel):
    """
    Response schema for user data.
    
    Requirements: 1.1
    """
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Account active status")
    email_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "role": "client",
                "is_active": True,
                "email_verified": False,
                "created_at": "2025-11-05T10:30:00Z"
            }
        }


class AuthResponse(BaseModel):
    """
    Combined response schema for signup/login with user data and tokens.
    
    Requirements: 1.1, 1.2
    """
    user: UserResponse = Field(..., description="User data")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=86400, description="Token expiry in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "role": "client",
                    "is_active": True,
                    "email_verified": False,
                    "created_at": "2025-11-05T10:30:00Z"
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response schema.
    """
    detail: str = Field(..., description="Error message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid email or password"
            }
        }
