"""
Pydantic schemas for profile operations.

Requirements: 2.1, 2.2, 2.3, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal


# Client Profile Schemas

class QuizData(BaseModel):
    """Quiz data structure with 20 required matching factors"""
    target_countries: List[str] = Field(..., min_length=1, description="Target countries for relocation")
    cultural_goals: List[str] = Field(..., min_length=1, description="Cultural adaptation goals")
    preferred_languages: List[str] = Field(..., min_length=1, description="Preferred coaching languages")
    industry: str = Field(..., description="Industry or profession")
    family_status: str = Field(..., description="Family status")
    previous_expat_experience: bool = Field(..., description="Has previous expat experience")
    timeline_urgency: int = Field(..., ge=1, le=5, description="Timeline urgency (1-5 scale)")
    budget_range: Dict[str, float] = Field(..., description="Budget range with min and max")
    coaching_style: str = Field(..., description="Preferred coaching style")
    specific_challenges: List[str] = Field(..., min_length=1, description="Specific challenges")
    
    @field_validator('budget_range')
    @classmethod
    def validate_budget_range(cls, v):
        if 'min' not in v or 'max' not in v:
            raise ValueError("Budget range must contain 'min' and 'max' keys")
        if v['min'] < 0 or v['max'] < 0:
            raise ValueError("Budget values must be positive")
        if v['min'] > v['max']:
            raise ValueError("Minimum budget cannot exceed maximum budget")
        return v


class ClientProfileCreate(BaseModel):
    """Schema for creating client profile"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    timezone: Optional[str] = Field(None, max_length=50)
    quiz_data: QuizData
    preferences: Optional[Dict[str, Any]] = None


class ClientProfileUpdate(BaseModel):
    """Schema for updating client profile"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    timezone: Optional[str] = Field(None, max_length=50)
    quiz_data: Optional[QuizData] = None
    preferences: Optional[Dict[str, Any]] = None


class ClientProfileResponse(BaseModel):
    """Schema for client profile response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    photo_url: Optional[str]
    phone: Optional[str]
    timezone: Optional[str]
    quiz_data: Dict[str, Any]
    preferences: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


# Coach Profile Schemas

class CoachProfileCreate(BaseModel):
    """Schema for creating coach profile"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    intro_video_url: Optional[str] = Field(None, max_length=500)
    expertise: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    countries: List[str] = Field(default_factory=list)
    hourly_rate: Optional[Decimal] = Field(None, ge=25, le=500, description="Hourly rate ($25-$500)")
    currency: str = Field(default="USD", max_length=3)
    availability: Optional[Dict[str, Any]] = None


class CoachProfileUpdate(BaseModel):
    """Schema for updating coach profile"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    intro_video_url: Optional[str] = Field(None, max_length=500)
    expertise: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    hourly_rate: Optional[Decimal] = Field(None, ge=25, le=500, description="Hourly rate ($25-$500)")
    currency: Optional[str] = Field(None, max_length=3)
    availability: Optional[Dict[str, Any]] = None


class CoachProfileResponse(BaseModel):
    """Schema for coach profile response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    photo_url: Optional[str]
    bio: Optional[str]
    intro_video_url: Optional[str]
    expertise: List[str]
    languages: List[str]
    countries: List[str]
    hourly_rate: Optional[Decimal]
    currency: str
    availability: Optional[Dict[str, Any]]
    rating: Decimal
    total_sessions: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class CoachListResponse(BaseModel):
    """Schema for coach listing response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    photo_url: Optional[str]
    bio: Optional[str]
    expertise: List[str]
    languages: List[str]
    countries: List[str]
    hourly_rate: Optional[Decimal]
    currency: str
    rating: Decimal
    total_sessions: int
    is_verified: bool


# Photo Upload Schema

class PhotoUploadResponse(BaseModel):
    """Schema for photo upload response"""
    photo_url: str
    message: str


# Generic Profile Response (for GET /profile endpoint)

class ProfileResponse(BaseModel):
    """Generic profile response that includes user info and role-specific profile"""
    user_id: UUID
    email: str
    role: str
    is_active: bool
    email_verified: bool
    profile: Optional[ClientProfileResponse | CoachProfileResponse] = None
