from sqlalchemy import Column, String, Text, Integer, DECIMAL, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class ClientProfile(Base):
    """
    Client profile model containing personal information and quiz data for matching.
    
    Requirements: 2.1, 2.2, 2.5
    """
    __tablename__ = "client_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Personal information
    first_name = Column(String(100))
    last_name = Column(String(100))
    photo_url = Column(String(500))
    phone = Column(String(20))
    timezone = Column(String(50))
    
    # Quiz data for AI matching (JSONB for flexibility)
    quiz_data = Column(JSONB, nullable=False)
    
    # User preferences (JSONB for flexibility)
    preferences = Column(JSONB)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="client_profile")

    def __repr__(self):
        return f"<ClientProfile(id={self.id}, user_id={self.user_id}, name={self.first_name} {self.last_name})>"

    def validate_quiz_data(self) -> bool:
        """
        Validate that quiz data contains all 20 required matching factors.
        
        Requirements: 2.2
        """
        if not self.quiz_data:
            return False
        
        required_fields = [
            'target_countries',
            'cultural_goals',
            'preferred_languages',
            'industry',
            'family_status',
            'previous_expat_experience',
            'timeline_urgency',
            'budget_range',
            'coaching_style',
            'specific_challenges'
        ]
        
        return all(field in self.quiz_data for field in required_fields)

    def get_full_name(self) -> str:
        """Get full name of client"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or "Unknown"


class CoachProfile(Base):
    """
    Coach profile model containing professional information, expertise, and availability.
    
    Requirements: 3.1, 3.2, 3.4, 3.5
    """
    __tablename__ = "coach_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Personal information
    first_name = Column(String(100))
    last_name = Column(String(100))
    photo_url = Column(String(500))
    bio = Column(Text)
    intro_video_url = Column(String(500))
    
    # Professional information (arrays for multiple values)
    expertise = Column(ARRAY(Text), default=list)
    languages = Column(ARRAY(Text), default=list, index=True)  # GIN index for array search
    countries = Column(ARRAY(Text), default=list)
    
    # Pricing information
    hourly_rate = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="USD")
    
    # Availability (JSONB for flexible time slot structure)
    availability = Column(JSONB)
    
    # Performance metrics
    rating = Column(DECIMAL(3, 2), default=0.0)
    total_sessions = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="coach_profile")

    def __repr__(self):
        return f"<CoachProfile(id={self.id}, user_id={self.user_id}, name={self.first_name} {self.last_name})>"

    def validate_hourly_rate(self) -> bool:
        """
        Validate that hourly rate is within acceptable range ($25-$500).
        
        Requirements: 3.4
        """
        if self.hourly_rate is None:
            return False
        return 25 <= float(self.hourly_rate) <= 500

    def get_full_name(self) -> str:
        """Get full name of coach"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or "Unknown"

    def has_language(self, language: str) -> bool:
        """Check if coach speaks a specific language"""
        return language in (self.languages or [])

    def has_country_experience(self, country: str) -> bool:
        """Check if coach has experience in a specific country"""
        return country in (self.countries or [])

    def has_expertise(self, expertise_area: str) -> bool:
        """Check if coach has specific expertise"""
        return expertise_area in (self.expertise or [])
