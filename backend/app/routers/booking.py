"""
Booking API endpoints for managing coaching session bookings.

Requirements: 5.1
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.booking import BookingStatus
from app.services.booking_service import BookingService, BookingError
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingWithDetails,
    BookingListResponse,
    BookingStatusUpdate,
    AvailabilityResponse,
    AvailabilitySlot
)

router = APIRouter(prefix="/booking", tags=["booking"])


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new booking",
    description="Create a pending booking for a coaching session. Requires client role."
)
def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new booking with status PENDING.
    
    - **coach_id**: ID of the coach to book
    - **session_datetime**: Scheduled session date and time (UTC)
    - **duration_minutes**: Session duration in minutes (default 60)
    - **notes**: Optional booking notes
    
    Requirements: 5.1
    """
    # Only clients can create bookings
    if not current_user.is_client():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can create bookings"
        )
    
    booking_service = BookingService(db)
    
    try:
        booking = booking_service.create_booking(
            client_id=current_user.id,
            coach_id=booking_data.coach_id,
            session_datetime=booking_data.session_datetime,
            duration_minutes=booking_data.duration_minutes,
            notes=booking_data.notes
        )
        return booking
    except BookingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{booking_id}",
    response_model=BookingWithDetails,
    summary="Get booking details",
    description="Get detailed information about a specific booking"
)
def get_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get booking details by ID.
    
    Users can only view their own bookings (as client or coach).
    Admins can view all bookings.
    
    Requirements: 5.1
    """
    booking_service = BookingService(db)
    booking = booking_service.get_booking(booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Authorization: Only client, coach, or admin can view
    if not current_user.is_admin():
        if booking.client_id != current_user.id and booking.coach_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized to view this booking"
            )
    
    # Build response with details
    return BookingWithDetails(
        id=booking.id,
        client_id=booking.client_id,
        client_name=booking.client.client_profile.get_full_name() if booking.client.client_profile else "Unknown",
        client_email=booking.client.email,
        coach_id=booking.coach_id,
        coach_name=booking.coach.coach_profile.get_full_name() if booking.coach.coach_profile else "Unknown",
        coach_email=booking.coach.email,
        session_datetime=booking.session_datetime,
        duration_minutes=booking.duration_minutes,
        status=booking.status,
        payment_id=booking.payment_id,
        meeting_link=booking.meeting_link,
        notes=booking.notes,
        created_at=booking.created_at,
        updated_at=booking.updated_at
    )


@router.get(
    "/client/{client_id}",
    response_model=BookingListResponse,
    summary="Get client bookings",
    description="Get all bookings for a specific client"
)
def get_client_bookings(
    client_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[BookingStatus] = Query(None, description="Filter by booking status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all bookings for a client with pagination and optional status filter.
    
    Users can only view their own bookings unless they are admin.
    
    Requirements: 5.1
    """
    # Authorization: Only the client themselves or admin can view
    if not current_user.is_admin() and current_user.id != client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to view these bookings"
        )
    
    booking_service = BookingService(db)
    bookings = booking_service.get_client_bookings(client_id, skip, limit, status)
    total = booking_service.booking_repo.count(client_id=client_id, status=status)
    
    return BookingListResponse(
        bookings=bookings,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get(
    "/coach/{coach_id}",
    response_model=BookingListResponse,
    summary="Get coach bookings",
    description="Get all bookings for a specific coach"
)
def get_coach_bookings(
    coach_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[BookingStatus] = Query(None, description="Filter by booking status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all bookings for a coach with pagination and optional status filter.
    
    Users can only view their own bookings unless they are admin.
    
    Requirements: 5.1
    """
    # Authorization: Only the coach themselves or admin can view
    if not current_user.is_admin() and current_user.id != coach_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to view these bookings"
        )
    
    booking_service = BookingService(db)
    bookings = booking_service.get_coach_bookings(coach_id, skip, limit, status)
    total = booking_service.booking_repo.count(coach_id=coach_id, status=status)
    
    return BookingListResponse(
        bookings=bookings,
        total=total,
        skip=skip,
        limit=limit
    )


@router.patch(
    "/{booking_id}/status",
    response_model=BookingResponse,
    summary="Update booking status",
    description="Update the status of a booking"
)
def update_booking_status(
    booking_id: UUID,
    status_update: BookingStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update booking status.
    
    Valid status transitions:
    - PENDING -> CONFIRMED, CANCELLED
    - CONFIRMED -> COMPLETED, CANCELLED
    
    Requirements: 5.1
    """
    booking_service = BookingService(db)
    
    try:
        booking = booking_service.update_booking_status(
            booking_id=booking_id,
            new_status=status_update.status,
            user_id=current_user.id,
            user_role=current_user.role
        )
        return booking
    except BookingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel booking",
    description="Cancel a booking (sets status to CANCELLED)"
)
def cancel_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a booking by setting its status to CANCELLED.
    
    Only bookings with status PENDING or CONFIRMED can be cancelled.
    
    Requirements: 5.1
    """
    booking_service = BookingService(db)
    
    try:
        booking_service.cancel_booking(
            booking_id=booking_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        return None
    except BookingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/coach/{coach_id}/availability",
    response_model=AvailabilityResponse,
    summary="Get coach availability",
    description="Get available time slots for a coach within a date range"
)
def get_coach_availability(
    coach_id: UUID,
    start_date: datetime = Query(..., description="Start of date range (UTC)"),
    end_date: datetime = Query(..., description="End of date range (UTC)"),
    duration_minutes: int = Query(60, ge=15, le=480, description="Desired slot duration in minutes"),
    db: Session = Depends(get_db)
):
    """
    Get available time slots for a coach.
    
    This endpoint returns a list of available time slots based on:
    - Coach's existing bookings
    - Coach's availability preferences (simplified in this implementation)
    
    Note: This is a simplified implementation. In production, this would
    integrate with the coach's availability JSONB field.
    
    Requirements: 5.1
    """
    booking_service = BookingService(db)
    
    # Validate date range
    if end_date <= start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    # Limit date range to 30 days
    if (end_date - start_date).days > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 30 days"
        )
    
    slots = booking_service.get_coach_availability_slots(
        coach_id=coach_id,
        start_date=start_date,
        end_date=end_date,
        slot_duration_minutes=duration_minutes
    )
    
    return AvailabilityResponse(
        coach_id=coach_id,
        available_slots=[AvailabilitySlot(**slot) for slot in slots]
    )
