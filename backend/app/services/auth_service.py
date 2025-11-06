"""
Authentication service for user signup, login, and password reset.

Requirements: 1.1, 1.2, 1.3, 1.4
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.user import User, UserRole
from app.utils.password import hash_password, verify_password
from app.utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    verify_password_reset_token,
    JWTError
)


class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass


class AuthService:
    """Service class for authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def signup(
        self,
        email: str,
        password: str,
        role: UserRole
    ) -> Tuple[User, str, str]:
        """
        Register a new user with email and password.
        
        Args:
            email: User email address
            password: Plain text password
            role: User role (client, coach, or admin)
            
        Returns:
            Tuple of (User object, access_token, refresh_token)
            
        Raises:
            AuthenticationError: If email already exists or validation fails
            
        Requirements: 1.1
        """
        # Validate email format
        if not self._validate_email(email):
            raise AuthenticationError("Invalid email format")
        
        # Validate password strength
        if not self._validate_password(password):
            raise AuthenticationError(
                "Password must be at least 8 characters long"
            )
        
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise AuthenticationError("Email already registered")
        
        # Hash password with bcrypt (12 salt rounds)
        password_hash = hash_password(password)
        
        # Create new user
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
            email_verified=False
        )
        
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            raise AuthenticationError("Email already registered")
        
        # Generate tokens
        access_token = self._create_user_token(user)
        refresh_token = self._create_user_refresh_token(user)
        
        return user, access_token, refresh_token
    
    def login(self, email: str, password: str) -> Tuple[User, str, str]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            Tuple of (User object, access_token, refresh_token)
            
        Raises:
            AuthenticationError: If credentials are invalid
            
        Requirements: 1.2
        """
        # Find user by email
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationError("Account is deactivated")
        
        # Update last login (optional - can be added to User model)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        # Generate tokens
        access_token = self._create_user_token(user)
        refresh_token = self._create_user_refresh_token(user)
        
        return user, access_token, refresh_token
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
            
        Raises:
            AuthenticationError: If refresh token is invalid
            
        Requirements: 1.2
        """
        try:
            from app.utils.jwt_utils import verify_refresh_token
            payload = verify_refresh_token(refresh_token)
        except JWTError as e:
            raise AuthenticationError(str(e))
        
        # Get user from database
        user_id = payload.get("sub")
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        
        # Generate new access token
        access_token = self._create_user_token(user)
        
        return access_token
    
    def request_password_reset(self, email: str) -> str:
        """
        Generate password reset token for user.
        
        Args:
            email: User email address
            
        Returns:
            Password reset token
            
        Raises:
            AuthenticationError: If user not found
            
        Requirements: 1.3
        """
        # Find user by email
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists for security
            # But still raise error for API to handle
            raise AuthenticationError("If email exists, reset link will be sent")
        
        # Generate password reset token
        reset_token = create_password_reset_token(email)
        
        return reset_token
    
    def reset_password(self, token: str, new_password: str) -> User:
        """
        Reset user password with valid reset token.
        
        Args:
            token: Password reset token
            new_password: New plain text password
            
        Returns:
            Updated User object
            
        Raises:
            AuthenticationError: If token is invalid or password validation fails
            
        Requirements: 1.3
        """
        # Verify token and extract email
        try:
            email = verify_password_reset_token(token)
        except JWTError as e:
            raise AuthenticationError(str(e))
        
        # Validate new password
        if not self._validate_password(new_password):
            raise AuthenticationError(
                "Password must be at least 8 characters long"
            )
        
        # Find user
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            raise AuthenticationError("User not found")
        
        # Hash new password
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> User:
        """
        Change user password (requires current password).
        
        Args:
            user_id: User ID
            current_password: Current plain text password
            new_password: New plain text password
            
        Returns:
            Updated User object
            
        Raises:
            AuthenticationError: If current password is wrong or validation fails
        """
        # Find user
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise AuthenticationError("User not found")
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")
        
        # Validate new password
        if not self._validate_password(new_password):
            raise AuthenticationError(
                "Password must be at least 8 characters long"
            )
        
        # Hash new password
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def _create_user_token(self, user: User) -> str:
        """Create access token for user"""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
        return create_access_token(token_data)
    
    def _create_user_refresh_token(self, user: User) -> str:
        """Create refresh token for user"""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
        return create_refresh_token(token_data)
    
    @staticmethod
    def _validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def _validate_password(password: str) -> bool:
        """Validate password strength (minimum 8 characters)"""
        return len(password) >= 8
