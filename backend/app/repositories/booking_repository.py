"""
Booking repository for CRUD operations on Booking model.

Requirements: 5.1
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.booking import Booking, BookingStatus


class BookingRepository:
    """Repository for Booking model CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, booking: Booking) -> Booking:
        """Create a new booking"""
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking
    
    def get_by_id(self, booking_id: UUID) -> Optional[Booking]:
        """Get booking by ID"""
        return self.db.query(Booking).filter(Booking.id == booking_id).first()
    
    def get_by_client_id(
        self,
        client_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[BookingStatus] = None
    ) -> List[Booking]:
        """
        Get all bookings for a specific client with optional filters.
        
        Args:
            client_id: Client user ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (default 20)
            status: Filter by booking status
        """
        query = self.db.query(Booking).filter(Booking.client_id == client_id)
        
        if status:
            query = query.filter(Booking.status == status)
        
        return query.order_by(Booking.session_datetime.desc()).offset(skip).limit(limit).all()
    
    def get_by_coach_id(
        self,
        coach_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[BookingStatus] = None
    ) -> List[Booking]:
        """
        Get all bookings for a specific coach with optional filters.
        
        Args:
            coach_id: Coach user ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (default 20)
            status: Filter by booking status
        """
        query = self.db.query(Booking).filter(Booking.coach_id == coach_id)
        
        if status:
            query = query.filter(Booking.status == status)
        
        return query.order_by(Booking.session_datetime.desc()).offset(skip).limit(limit).all()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[BookingStatus] = None,
        client_id: Optional[UUID] = None,
        coach_id: Optional[UUID] = None
    ) -> List[Booking]:
        """
        Get all bookings with optional filters and pagination.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (default 20)
            status: Filter by booking status
            client_id: Filter by client ID
            coach_id: Filter by coach ID
        """
        query = self.db.query(Booking)
        
        if status:
            query = query.filter(Booking.status == status)
        
        if client_id:
            query = query.filter(Booking.client_id == client_id)
        
        if coach_id:
            query = query.filter(Booking.coach_id == coach_id)
        
        return query.order_by(Booking.session_datetime.desc()).offset(skip).limit(limit).all()
    
    def count(
        self,
        status: Optional[BookingStatus] = None,
        client_id: Optional[UUID] = None,
        coach_id: Optional[UUID] = None
    ) -> int:
        """Count bookings with optional filters"""
        query = self.db.query(Booking)
        
        if status:
            query = query.filter(Booking.status == status)
        
        if client_id:
            query = query.filter(Booking.client_id == client_id)
        
        if coach_id:
            query = query.filter(Booking.coach_id == coach_id)
        
        return query.count()
    
    def update(self, booking: Booking) -> Booking:
        """Update booking"""
        self.db.commit()
        self.db.refresh(booking)
        return booking
    
    def delete(self, booking: Booking) -> None:
        """Delete booking"""
        self.db.delete(booking)
        self.db.commit()
    
    def get_coach_bookings_in_timerange(
        self,
        coach_id: UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: Optional[UUID] = None
    ) -> List[Booking]:
        """
        Get all bookings for a coach within a specific time range.
        Used for availability checking.
        
        Args:
            coach_id: Coach user ID
            start_time: Start of time range
            end_time: End of time range
            exclude_booking_id: Optional booking ID to exclude (for updates)
            
        Returns:
            List of bookings that overlap with the time range
        """
        query = self.db.query(Booking).filter(
            and_(
                Booking.coach_id == coach_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                or_(
                    # Booking starts within the range
                    and_(
                        Booking.session_datetime >= start_time,
                        Booking.session_datetime < end_time
                    ),
                    # Booking ends within the range
                    and_(
                        Booking.session_datetime < start_time,
                        Booking.session_datetime + self.db.func.make_interval(0, 0, 0, 0, 0, Booking.duration_minutes) > start_time
                    )
                )
            )
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        return query.all()
    
    def exists_by_id(self, booking_id: UUID) -> bool:
        """Check if booking exists by ID"""
        return self.db.query(Booking).filter(Booking.id == booking_id).count() > 0
