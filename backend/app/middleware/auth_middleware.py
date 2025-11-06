"""
Authentication middleware and dependencies for FastAPI.

Requirements: 1.2, 7.3
"""
from typing import Optional, List, Callable
from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.jwt_utils import verify_token, JWTError


# HTTP Bearer token security scheme
security = HTTPBearer()


class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to extract and validate current user from JWT token.
    
    Args:
        credentials: HTTP Bearer token from request header
        db: Database session
        
    Returns:
        Current authenticated User object
        
    Raises:
        AuthenticationError: If token is invalid or user not found
        
    Requirements: 1.2
    """
    token = credentials.credentials
    
    try:
        # Verify and decode token
        payload = verify_token(token)
    except JWTError as e:
        raise AuthenticationError(detail=str(e))
    
    # Extract user ID from token
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError(detail="Invalid token payload")
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise AuthenticationError(detail="User not found")
    
    if not user.is_active:
        raise AuthenticationError(detail="User account is inactive")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    FastAPI dependency to get current active user.
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        Current active User object
        
    Raises:
        AuthenticationError: If user is inactive
        
    Requirements: 1.2
    """
    if not current_user.is_active:
        raise AuthenticationError(detail="Inactive user")
    
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    FastAPI dependency to optionally extract user from JWT token.
    Returns None if no token provided.
    
    Args:
        credentials: Optional HTTP Bearer token from request header
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.is_active:
                return user
    except JWTError:
        pass
    
    return None


def require_role(allowed_roles: List[UserRole]):
    """
    Decorator factory for role-based access control.
    
    Args:
        allowed_roles: List of UserRole enums that are allowed
        
    Returns:
        Dependency function that checks user role
        
    Requirements: 7.3
    
    Example:
        @router.get("/admin/users")
        async def get_users(user: User = Depends(require_role([UserRole.ADMIN]))):
            ...
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AuthorizationError(
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    
    return role_checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency to require admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if admin
        
    Raises:
        AuthorizationError: If user is not admin
        
    Requirements: 7.3
    """
    if current_user.role != UserRole.ADMIN:
        raise AuthorizationError(detail="Admin access required")
    
    return current_user


def require_client(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency to require client role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if client
        
    Raises:
        AuthorizationError: If user is not client
        
    Requirements: 7.3
    """
    if current_user.role != UserRole.CLIENT:
        raise AuthorizationError(detail="Client access required")
    
    return current_user


def require_coach(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency to require coach role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if coach
        
    Raises:
        AuthorizationError: If user is not coach
        
    Requirements: 7.3
    """
    if current_user.role != UserRole.COACH:
        raise AuthorizationError(detail="Coach access required")
    
    return current_user


def require_client_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency to require client or admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if client or admin
        
    Raises:
        AuthorizationError: If user is neither client nor admin
    """
    if current_user.role not in [UserRole.CLIENT, UserRole.ADMIN]:
        raise AuthorizationError(detail="Client or admin access required")
    
    return current_user


def require_coach_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency to require coach or admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if coach or admin
        
    Raises:
        AuthorizationError: If user is neither coach nor admin
    """
    if current_user.role not in [UserRole.COACH, UserRole.ADMIN]:
        raise AuthorizationError(detail="Coach or admin access required")
    
    return current_user


class ResourceOwnershipChecker:
    """
    Dependency class for checking resource ownership.
    
    Requirements: 7.3
    
    Example:
        ownership_checker = ResourceOwnershipChecker()
        
        @router.put("/coaches/{coach_id}")
        async def update_coach(
            coach_id: UUID,
            user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            ownership_checker.check_ownership(user, coach_id, db)
            ...
    """
    
    def check_ownership(
        self,
        current_user: User,
        resource_user_id: str,
        allow_admin: bool = True
    ) -> bool:
        """
        Check if current user owns the resource or is admin.
        
        Args:
            current_user: Current authenticated user
            resource_user_id: User ID that owns the resource
            allow_admin: Whether to allow admin access (default True)
            
        Returns:
            True if user has access
            
        Raises:
            AuthorizationError: If user doesn't have access
        """
        # Convert to string for comparison
        current_user_id = str(current_user.id)
        resource_user_id = str(resource_user_id)
        
        # Admin can access everything (if allowed)
        if allow_admin and current_user.role == UserRole.ADMIN:
            return True
        
        # Check ownership
        if current_user_id != resource_user_id:
            raise AuthorizationError(
                detail="You don't have permission to access this resource"
            )
        
        return True
    
    def check_coach_ownership(
        self,
        current_user: User,
        coach_id: str,
        db: Session
    ) -> bool:
        """
        Check if current user is the coach or admin.
        
        Args:
            current_user: Current authenticated user
            coach_id: Coach user ID
            db: Database session
            
        Returns:
            True if user has access
            
        Raises:
            AuthorizationError: If user doesn't have access
        """
        return self.check_ownership(current_user, coach_id, allow_admin=True)
    
    def check_client_ownership(
        self,
        current_user: User,
        client_id: str,
        db: Session
    ) -> bool:
        """
        Check if current user is the client or admin.
        
        Args:
            current_user: Current authenticated user
            client_id: Client user ID
            db: Database session
            
        Returns:
            True if user has access
            
        Raises:
            AuthorizationError: If user doesn't have access
        """
        return self.check_ownership(current_user, client_id, allow_admin=True)


# Create singleton instance
ownership_checker = ResourceOwnershipChecker()


def require_ownership(resource_user_id: str):
    """
    Decorator factory for ownership-based access control.
    
    Args:
        resource_user_id: User ID that owns the resource
        
    Returns:
        Dependency function that checks ownership
        
    Requirements: 7.3
    """
    async def ownership_checker_dep(
        current_user: User = Depends(get_current_user)
    ) -> User:
        ownership_checker.check_ownership(current_user, resource_user_id)
        return current_user
    
    return ownership_checker_dep
