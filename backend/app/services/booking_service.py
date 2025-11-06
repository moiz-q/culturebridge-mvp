"""
Booking service for managing coaching session bookings and availability.

Requirements: 5.1
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.user import User, UserRole
from app.models.profile import CoachProfile
from app.repositories.booking_repository import BookingRepository
from app.repositories.user_repository import UserRepository
from app.repositories.profile_repository import CoachProfileRepository


class BookingError(Exception):
    """Custom exception for booking errors"""
    pass


class BookingService:
    """Service class for booking operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.user_repo = UserRepository(db)
        self.coach_repo = CoachProfileRepository(db)
    
    def create_booking(
        self,
        client_id: UUID,
        coach_id: UUID,
        session_datetime: datetime,
        duration_minutes: int = 60,
        notes: Optional[str] = None
    ) -> Booking:
        """
        Create a new booking with availability validation.
        
        Args:
            client_id: Client user ID
            coach_id: Coach user ID
            session_datetime: Scheduled session date and time
            duration_minutes: Session duration in minutes (default 60)
            notes: Optional booking notes
            
        Returns:
            Created Booking object with status PENDING
            
        Raises:
            BookingError: If validation fails or time slot is unavailable
            
        Requirements: 5.1
        """
        # Validate client exists and is a client
        client = self.user_repo.get_by_id(client_id)
        if not client or not client.is_client():
            raise BookingError("Invalid client")
        
        # Validate coach exists and is a coach
        coach = self.user_repo.get_by_id(coach_id)
        if not coach or not coach.is_coach():
            raise BookingError("Invalid coach")
        
        # Validate coach is active
        if not coach.is_active:
            raise BookingError("Coach is not active")
        
        # Validate duration
        if duration_minutes <= 0:
            raise BookingError("Duration must be positive")
        
        # Validate session is in the future
        if session_datetime <= datetime.utcnow():
            raise BookingError("Session must be scheduled in the future")
        
        # Check time slot availability
        if not self.check_availability(coach_id, session_datetime, duration_minutes):
            raise BookingError("Time slot is not available")
        
        # Create booking with PENDING status
        booking = Booking(
            client_id=client_id,
            coach_id=coach_id,
            session_datetime=session_datetime,
            duration_minutes=duration_minutes,
            status=BookingStatus.PENDING,
            notes=notes
        )
        
        return self.booking_repo.create(booking)
    
    def get_booking(self, booking_id: UUID) -> Optional[Booking]:
        """
        Get booking by ID.
        
        Args:
            booking_id: Booking ID
            
        Returns:
            Booking object or None if not found
        """
        return self.booking_repo.get_by_id(booking_id)
    
    def get_client_bookings(
        self,
        client_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[BookingStatus] = None
    ) -> List[Booking]:
        """
        Get all bookings for a client.
        
        Args:
            client_id: Client user ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            status: Optional status filter
            
        Returns:
            List of Booking objects
        """
        return self.booking_repo.get_by_client_id(client_id, skip, limit, status)
    
    def get_coach_bookings(
        self,
        coach_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[BookingStatus] = None
    ) -> List[Booking]:
        """
        Get all bookings for a coach.
        
        Args:
            coach_id: Coach user ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            status: Optional status filter
            
        Returns:
            List of Booking objects
        """
        return self.booking_repo.get_by_coach_id(coach_id, skip, limit, status)
    
    def update_booking_status(
        self,
        booking_id: UUID,
        new_status: BookingStatus,
        user_id: UUID,
        user_role: UserRole
    ) -> Booking:
        """
        Update booking status with authorization checks.
        
        Args:
            booking_id: Booking ID
            new_status: New booking status
            user_id: User making the update
            user_role: Role of user making the update
            
        Returns:
            Updated Booking object
            
        Raises:
            BookingError: If booking not found or unauthorized
            
        Requirements: 5.1
        """
        booking = self.booking_repo.get_by_id(booking_id)
        
        if not booking:
            raise BookingError("Booking not found")
        
        # Authorization: Only client, coach, or admin can update
        if user_role != UserRole.ADMIN:
            if booking.client_id != user_id and booking.coach_id != user_id:
                raise BookingError("Unauthorized to update this booking")
        
        # Validate status transition
        if not self._is_valid_status_transition(booking.status, new_status):
            raise BookingError(f"Invalid status transition from {booking.status} to {new_status}")
        
        booking.status = new_status
        booking.updated_at = datetime.utcnow()
        
        return self.booking_repo.update(booking)
    
    def cancel_booking(
        self,
        booking_id: UUID,
        user_id: UUID,
        user_role: UserRole
    ) -> Booking:
        """
        Cancel a booking.
        
        Args:
            booking_id: Booking ID
            user_id: User requesting cancellation
            user_role: Role of user requesting cancellation
            
        Returns:
            Updated Booking object with CANCELLED status
            
        Raises:
            BookingError: If booking cannot be cancelled
            
        Requirements: 5.1
        """
        booking = self.booking_repo.get_by_id(booking_id)
        
        if not booking:
            raise BookingError("Booking not found")
        
        # Authorization: Only client, coach, or admin can cancel
        if user_role != UserRole.ADMIN:
            if booking.client_id != user_id and booking.coach_id != user_id:
                raise BookingError("Unauthorized to cancel this booking")
        
        # Check if booking can be cancelled
        if not booking.can_be_cancelled():
            raise BookingError(f"Cannot cancel booking with status {booking.status}")
        
        booking.status = BookingStatus.CANCELLED
        booking.updated_at = datetime.utcnow()
        
        return self.booking_repo.update(booking)
    
    def check_availability(
        self,
        coach_id: UUID,
        session_datetime: datetime,
        duration_minutes: int,
        exclude_booking_id: Optional[UUID] = None
    ) -> bool:
        """
        Check if a time slot is available for a coach.
        
        Args:
            coach_id: Coach user ID
            session_datetime: Requested session start time
            duration_minutes: Session duration in minutes
            exclude_booking_id: Optional booking ID to exclude (for updates)
            
        Returns:
            True if time slot is available, False otherwise
            
        Requirements: 5.1
        """
        # Calculate end time
        end_time = session_datetime + timedelta(minutes=duration_minutes)
        
        # Get overlapping bookings
        overlapping_bookings = self.booking_repo.get_coach_bookings_in_timerange(
            coach_id=coach_id,
            start_time=session_datetime,
            end_time=end_time,
            exclude_booking_id=exclude_booking_id
        )
        
        # If there are any overlapping bookings, slot is not available
        return len(overlapping_bookings) == 0
    
    def get_coach_availability_slots(
        self,
        coach_id: UUID,
        start_date: datetime,
        end_date: datetime,
        slot_duration_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Get available time slots for a coach within a date range.
        
        Args:
            coach_id: Coach user ID
            start_date: Start of date range
            end_date: End of date range
            slot_duration_minutes: Duration of each slot in minutes
            
        Returns:
            List of available time slots with start and end times
            
        Note: This is a simplified implementation. In production, this would
        integrate with the coach's availability JSONB field to respect their
        working hours and preferences.
        """
        # Get coach profile to check availability preferences
        coach_profile = self.coach_repo.get_by_user_id(coach_id)
        
        if not coach_profile:
            return []
        
        # Get all bookings in the date range
        bookings = self.booking_repo.get_coach_bookings_in_timerange(
            coach_id=coach_id,
            start_time=start_date,
            end_time=end_date
        )
        
        # Create a simple list of booked time ranges
        booked_ranges = []
        for booking in bookings:
            booking_end = booking.session_datetime + timedelta(minutes=booking.duration_minutes)
            booked_ranges.append({
                'start': booking.session_datetime,
                'end': booking_end
            })
        
        # Generate potential slots (simplified - assumes 9 AM to 5 PM working hours)
        # In production, this would use coach_profile.availability JSONB
        available_slots = []
        current_time = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        while current_time < end_date:
            slot_end = current_time + timedelta(minutes=slot_duration_minutes)
            
            # Check if slot is within working hours (9 AM - 5 PM)
            if current_time.hour >= 9 and slot_end.hour <= 17:
                # Check if slot overlaps with any booking
                is_available = True
                for booked in booked_ranges:
                    if (current_time < booked['end'] and slot_end > booked['start']):
                        is_available = False
                        break
                
                if is_available and current_time > datetime.utcnow():
                    available_slots.append({
                        'start': current_time.isoformat(),
                        'end': slot_end.isoformat(),
                        'duration_minutes': slot_duration_minutes
                    })
            
            # Move to next slot
            current_time += timedelta(minutes=30)  # 30-minute increments
            
            # Skip to next day if past 5 PM
            if current_time.hour >= 17:
                current_time = (current_time + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        
        return available_slots
    
    def _is_valid_status_transition(
        self,
        current_status: BookingStatus,
        new_status: BookingStatus
    ) -> bool:
        """
        Validate if a status transition is allowed.
        
        Valid transitions:
        - PENDING -> CONFIRMED, CANCELLED
        - CONFIRMED -> COMPLETED, CANCELLED
        - COMPLETED -> (no transitions)
        - CANCELLED -> (no transitions)
        """
        valid_transitions = {
            BookingStatus.PENDING: [BookingStatus.CONFIRMED, BookingStatus.CANCELLED],
            BookingStatus.CONFIRMED: [BookingStatus.COMPLETED, BookingStatus.CANCELLED],
            BookingStatus.COMPLETED: [],
            BookingStatus.CANCELLED: []
        }
        
        return new_status in valid_transitions.get(current_status, [])
