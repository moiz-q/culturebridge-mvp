"""
Profile repositories for ClientProfile and CoachProfile models.

Requirements: 2.1, 3.1
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.profile import ClientProfile, CoachProfile


class ClientProfileRepository:
    """Repository for ClientProfile model CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, profile: ClientProfile) -> ClientProfile:
        """Create a new client profile"""
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def get_by_id(self, profile_id: UUID) -> Optional[ClientProfile]:
        """Get client profile by ID"""
        return self.db.query(ClientProfile).filter(ClientProfile.id == profile_id).first()
    
    def get_by_user_id(self, user_id: UUID) -> Optional[ClientProfile]:
        """Get client profile by user ID"""
        return self.db.query(ClientProfile).filter(ClientProfile.user_id == user_id).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> List[ClientProfile]:
        """
        Get all client profiles with pagination.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (default 20)
        """
        return self.db.query(ClientProfile).offset(skip).limit(limit).all()
    
    def count(self) -> int:
        """Count all client profiles"""
        return self.db.query(ClientProfile).count()
    
    def update(self, profile: ClientProfile) -> ClientProfile:
        """Update client profile"""
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def delete(self, profile: ClientProfile) -> None:
        """Delete client profile"""
        self.db.delete(profile)
        self.db.commit()
    
    def exists_by_user_id(self, user_id: UUID) -> bool:
        """Check if client profile exists for user"""
        return self.db.query(ClientProfile).filter(ClientProfile.user_id == user_id).count() > 0


class CoachProfileRepository:
    """Repository for CoachProfile model CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, profile: CoachProfile) -> CoachProfile:
        """Create a new coach profile"""
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def get_by_id(self, profile_id: UUID) -> Optional[CoachProfile]:
        """Get coach profile by ID"""
        return self.db.query(CoachProfile).filter(CoachProfile.id == profile_id).first()
    
    def get_by_user_id(self, user_id: UUID) -> Optional[CoachProfile]:
        """Get coach profile by user ID"""
        return self.db.query(CoachProfile).filter(CoachProfile.user_id == user_id).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        language: Optional[str] = None,
        country: Optional[str] = None,
        expertise: Optional[str] = None,
        min_rate: Optional[float] = None,
        max_rate: Optional[float] = None,
        is_verified: Optional[bool] = None,
        min_rating: Optional[float] = None
    ) -> List[CoachProfile]:
        """
        Get all coach profiles with optional filters and pagination.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (default 20)
            language: Filter by language (array contains)
            country: Filter by country (array contains)
            expertise: Filter by expertise (array contains)
            min_rate: Minimum hourly rate
            max_rate: Maximum hourly rate
            is_verified: Filter by verification status
            min_rating: Minimum rating
        """
        query = self.db.query(CoachProfile)
        
        # Filter by language (array contains)
        if language:
            query = query.filter(CoachProfile.languages.contains([language]))
        
        # Filter by country (array contains)
        if country:
            query = query.filter(CoachProfile.countries.contains([country]))
        
        # Filter by expertise (array contains)
        if expertise:
            query = query.filter(CoachProfile.expertise.contains([expertise]))
        
        # Filter by hourly rate range
        if min_rate is not None:
            query = query.filter(CoachProfile.hourly_rate >= min_rate)
        
        if max_rate is not None:
            query = query.filter(CoachProfile.hourly_rate <= max_rate)
        
        # Filter by verification status
        if is_verified is not None:
            query = query.filter(CoachProfile.is_verified == is_verified)
        
        # Filter by minimum rating
        if min_rating is not None:
            query = query.filter(CoachProfile.rating >= min_rating)
        
        # Order by rating (descending) and total sessions (descending)
        query = query.order_by(CoachProfile.rating.desc(), CoachProfile.total_sessions.desc())
        
        return query.offset(skip).limit(limit).all()
    
    def count(
        self,
        language: Optional[str] = None,
        country: Optional[str] = None,
        expertise: Optional[str] = None,
        min_rate: Optional[float] = None,
        max_rate: Optional[float] = None,
        is_verified: Optional[bool] = None,
        min_rating: Optional[float] = None
    ) -> int:
        """Count coach profiles with optional filters"""
        query = self.db.query(CoachProfile)
        
        if language:
            query = query.filter(CoachProfile.languages.contains([language]))
        
        if country:
            query = query.filter(CoachProfile.countries.contains([country]))
        
        if expertise:
            query = query.filter(CoachProfile.expertise.contains([expertise]))
        
        if min_rate is not None:
            query = query.filter(CoachProfile.hourly_rate >= min_rate)
        
        if max_rate is not None:
            query = query.filter(CoachProfile.hourly_rate <= max_rate)
        
        if is_verified is not None:
            query = query.filter(CoachProfile.is_verified == is_verified)
        
        if min_rating is not None:
            query = query.filter(CoachProfile.rating >= min_rating)
        
        return query.count()
    
    def update(self, profile: CoachProfile) -> CoachProfile:
        """Update coach profile"""
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def delete(self, profile: CoachProfile) -> None:
        """Delete coach profile"""
        self.db.delete(profile)
        self.db.commit()
    
    def exists_by_user_id(self, user_id: UUID) -> bool:
        """Check if coach profile exists for user"""
        return self.db.query(CoachProfile).filter(CoachProfile.user_id == user_id).count() > 0
    
    def get_active_coaches(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[CoachProfile]:
        """
        Get all active coaches (verified with positive rating).
        Used for AI matching engine.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return (default 100 for matching)
        """
        return self.db.query(CoachProfile).join(
            CoachProfile.user
        ).filter(
            and_(
                CoachProfile.is_verified == True,
                CoachProfile.user.has(is_active=True)
            )
        ).order_by(
            CoachProfile.rating.desc()
        ).offset(skip).limit(limit).all()
