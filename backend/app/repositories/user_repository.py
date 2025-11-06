"""
User repository for CRUD operations on User model.

Requirements: 2.1, 3.1
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User, UserRole


class UserRepository:
    """Repository for User model CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: User) -> User:
        """Create a new user"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """
        Get all users with optional filters and pagination.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (default 20)
            role: Filter by user role
            is_active: Filter by active status
            search: Search by email (partial match)
        """
        query = self.db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if search:
            query = query.filter(User.email.ilike(f"%{search}%"))
        
        return query.offset(skip).limit(limit).all()
    
    def count(
        self,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Count users with optional filters"""
        query = self.db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.count()
    
    def update(self, user: User) -> User:
        """Update user"""
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        """Delete user (cascade deletes related profiles)"""
        self.db.delete(user)
        self.db.commit()
    
    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        return self.db.query(User).filter(User.email == email).count() > 0
