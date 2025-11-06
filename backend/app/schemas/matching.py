"""
Pydantic schemas for AI matching operations.

Requirements: 4.1, 4.3, 4.4, 4.5
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from decimal import Decimal


class MatchRequest(BaseModel):
    """Schema for match request"""
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of matches to return")
    use_cache: bool = Field(default=True, description="Whether to use cached results")


class CoachMatchResult(BaseModel):
    """Schema for individual coach match result"""
    coach_id: str
    user_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    photo_url: Optional[str]
    bio: Optional[str]
    expertise: List[str]
    languages: List[str]
    countries: List[str]
    hourly_rate: Optional[float]
    currency: str
    rating: float
    total_sessions: int
    is_verified: bool
    match_score: float = Field(description="Match score (0-100)")
    confidence_score: float = Field(description="Confidence score (0-100)")


class MatchResponse(BaseModel):
    """Schema for match response"""
    matches: List[CoachMatchResult]
    total_matches: int
    cached: bool = Field(description="Whether results were retrieved from cache")
    generated_at: str = Field(description="Timestamp when matches were generated")


class MatchCacheInfo(BaseModel):
    """Schema for match cache information"""
    cache_key: str
    exists: bool
    ttl_seconds: Optional[int] = Field(None, description="Time to live in seconds")
