"""
Pydantic schemas for admin endpoints.

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from app.models.user import UserRole
from app.models.booking import BookingStatus


class PlatformMetricsResponse(BaseModel):
    """Response schema for platform metrics"""
    period_days: int
    start_date: str
    end_date: str
    total_users: int
    total_clients: int
    total_coaches: int
    new_users: int
    active_sessions: int
    session_volume: int
    total_revenue_usd: float
    revenue_by_currency: Dict[str, float]
    avg_session_duration_minutes: float
    booking_status_breakdown: Dict[str, int]
    
    class Config:
        from_attributes = True


class UserListItem(BaseModel):
    """Schema for user in list view"""
    id: UUID
    email: EmailStr
    role: UserRole
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Response schema for user list"""
    users: List[UserListItem]
    total: int
    skip: int
    limit: int


class UserUpdateRequest(BaseModel):
    """Request schema for updating user"""
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    email_verified: Optional[bool] = None


class UserActivityResponse(BaseModel):
    """Response schema for user activity history"""
    user_id: str
    email: str
    role: str
    created_at: str
    bookings: Dict[str, Any]
    payments: Dict[str, Any]
    community: Dict[str, Any]


class BookingListItem(BaseModel):
    """Schema for booking in admin list view"""
    id: UUID
    client_id: UUID
    client_email: str
    coach_id: UUID
    coach_email: str
    session_datetime: datetime
    duration_minutes: int
    status: BookingStatus
    payment_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Response schema for booking list"""
    bookings: List[BookingListItem]
    total: int
    skip: int
    limit: int


class RevenueDataPoint(BaseModel):
    """Schema for revenue data point"""
    period: str
    total_usd: float
    by_currency: Dict[str, float]
    transaction_count: int


class RevenueReportResponse(BaseModel):
    """Response schema for revenue report"""
    start_date: str
    end_date: str
    group_by: str
    data: List[RevenueDataPoint]


class CSVExportResponse(BaseModel):
    """Response schema for CSV export"""
    filename: str
    content_type: str = "text/csv"
    data: str
