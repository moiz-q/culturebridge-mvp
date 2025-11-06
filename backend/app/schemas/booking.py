"""
Pydantic schemas for booking API endpoints.

Requirements: 5.1
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    """Schema for creating a new booking"""
    coach_id: UUID = Field(..., description="Coach user ID")
    session_datetime: datetime = Field(..., description="Scheduled session date and time (UTC)")
    duration_minutes: int = Field(60, ge=15, le=480, description="Session duration in minutes (15-480)")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional booking notes")
    
    @validator('session_datetime')
    def validate_future_datetime(cls, v):
        """Ensure session is scheduled in the future"""
        if v <= datetime.utcnow():
            raise ValueError("Session must be scheduled in the future")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "coach_id": "123e4567-e89b-12d3-a456-426614174000",
                "session_datetime": "2025-11-15T14:00:00Z",
                "duration_minutes": 60,
                "notes": "Looking forward to discussing career transition strategies"
            }
        }


class BookingStatusUpdate(BaseModel):
    """Schema for updating booking status"""
    status: BookingStatus = Field(..., description="New booking status")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "confirmed"
            }
        }


class BookingResponse(BaseModel):
    """Schema for booking response"""
    id: UUID
    client_id: UUID
    coach_id: UUID
    session_datetime: datetime
    duration_minutes: int
    status: BookingStatus
    payment_id: Optional[UUID]
    meeting_link: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "client_id": "223e4567-e89b-12d3-a456-426614174000",
                "coach_id": "323e4567-e89b-12d3-a456-426614174000",
                "session_datetime": "2025-11-15T14:00:00Z",
                "duration_minutes": 60,
                "status": "pending",
                "payment_id": None,
                "meeting_link": None,
                "notes": "Looking forward to discussing career transition strategies",
                "created_at": "2025-11-05T10:30:00Z",
                "updated_at": "2025-11-05T10:30:00Z"
            }
        }


class BookingWithDetails(BaseModel):
    """Schema for booking response with client and coach details"""
    id: UUID
    client_id: UUID
    client_name: str
    client_email: str
    coach_id: UUID
    coach_name: str
    coach_email: str
    session_datetime: datetime
    duration_minutes: int
    status: BookingStatus
    payment_id: Optional[UUID]
    meeting_link: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "client_id": "223e4567-e89b-12d3-a456-426614174000",
                "client_name": "John Doe",
                "client_email": "john@example.com",
                "coach_id": "323e4567-e89b-12d3-a456-426614174000",
                "coach_name": "Jane Smith",
                "coach_email": "jane@example.com",
                "session_datetime": "2025-11-15T14:00:00Z",
                "duration_minutes": 60,
                "status": "pending",
                "payment_id": None,
                "meeting_link": None,
                "notes": "Looking forward to discussing career transition strategies",
                "created_at": "2025-11-05T10:30:00Z",
                "updated_at": "2025-11-05T10:30:00Z"
            }
        }


class BookingListResponse(BaseModel):
    """Schema for paginated booking list response"""
    bookings: list[BookingResponse]
    total: int
    skip: int
    limit: int
    
    class Config:
        schema_extra = {
            "example": {
                "bookings": [],
                "total": 0,
                "skip": 0,
                "limit": 20
            }
        }


class AvailabilitySlot(BaseModel):
    """Schema for availability time slot"""
    start: str = Field(..., description="Slot start time (ISO format)")
    end: str = Field(..., description="Slot end time (ISO format)")
    duration_minutes: int = Field(..., description="Slot duration in minutes")
    
    class Config:
        schema_extra = {
            "example": {
                "start": "2025-11-15T14:00:00Z",
                "end": "2025-11-15T15:00:00Z",
                "duration_minutes": 60
            }
        }


class AvailabilityResponse(BaseModel):
    """Schema for coach availability response"""
    coach_id: UUID
    available_slots: list[AvailabilitySlot]
    
    class Config:
        schema_extra = {
            "example": {
                "coach_id": "323e4567-e89b-12d3-a456-426614174000",
                "available_slots": []
            }
        }
