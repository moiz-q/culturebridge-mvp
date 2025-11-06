"""
JWT utilities for token generation, validation, and refresh.

Requirements: 1.1, 1.2, 1.4
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from app.config import settings


class JWTError(Exception):
    """Custom exception for JWT-related errors"""
    pass


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a JWT access token.
    
    Args:
        data: Dictionary containing user data (sub, email, role)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
        
    Requirements: 1.2
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Generate a JWT refresh token with 7-day expiration.
    
    Args:
        data: Dictionary containing user data (sub, email, role)
        
    Returns:
        Encoded JWT refresh token string
        
    Requirements: 1.2
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid or expired
        
    Requirements: 1.2
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        raise JWTError("Token has expired")
    except InvalidTokenError as e:
        raise JWTError(f"Invalid token: {str(e)}")


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token without verification (for debugging).
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        return payload
    except Exception:
        return None


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """
    Verify a refresh token and ensure it's the correct type.
    
    Args:
        token: Refresh token string to verify
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid, expired, or not a refresh token
        
    Requirements: 1.2
    """
    payload = verify_token(token)
    
    if payload.get("type") != "refresh":
        raise JWTError("Invalid token type")
    
    return payload


def create_password_reset_token(email: str) -> str:
    """
    Generate a password reset token valid for 1 hour.
    
    Args:
        email: User email address
        
    Returns:
        Encoded JWT token for password reset
        
    Requirements: 1.3
    """
    expire = datetime.utcnow() + timedelta(hours=1)
    
    to_encode = {
        "sub": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "password_reset"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_password_reset_token(token: str) -> str:
    """
    Verify a password reset token and extract email.
    
    Args:
        token: Password reset token string
        
    Returns:
        Email address from token
        
    Raises:
        JWTError: If token is invalid, expired, or not a password reset token
        
    Requirements: 1.3
    """
    payload = verify_token(token)
    
    if payload.get("type") != "password_reset":
        raise JWTError("Invalid token type")
    
    email = payload.get("sub")
    if not email:
        raise JWTError("Invalid token payload")
    
    return email
