from sqlalchemy import Column, String, Integer, DECIMAL, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class BookingStatus(str, enum.Enum):
    """Booking status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(Base):
    """
    Booking model representing scheduled coaching sessions.
    
    Requirements: 5.1
    """
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    coach_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Session details
    session_datetime = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=60, nullable=False)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    
    # Payment and meeting information
    payment_id = Column(UUID(as_uuid=True))
    meeting_link = Column(String(500))
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    client = relationship("User", foreign_keys=[client_id], back_populates="client_bookings")
    coach = relationship("User", foreign_keys=[coach_id], back_populates="coach_bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)

    def __repr__(self):
        return f"<Booking(id={self.id}, client_id={self.client_id}, coach_id={self.coach_id}, status={self.status})>"

    def is_pending(self) -> bool:
        """Check if booking is pending"""
        return self.status == BookingStatus.PENDING

    def is_confirmed(self) -> bool:
        """Check if booking is confirmed"""
        return self.status == BookingStatus.CONFIRMED

    def is_completed(self) -> bool:
        """Check if booking is completed"""
        return self.status == BookingStatus.COMPLETED

    def is_cancelled(self) -> bool:
        """Check if booking is cancelled"""
        return self.status == BookingStatus.CANCELLED

    def can_be_cancelled(self) -> bool:
        """Check if booking can be cancelled"""
        return self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]

    def validate_duration(self) -> bool:
        """Validate that duration is positive"""
        return self.duration_minutes > 0

    def is_past(self) -> bool:
        """Check if booking is in the past"""
        return self.session_datetime < datetime.utcnow()


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    """
    Payment model representing payment transactions for bookings.
    
    Requirements: 5.2, 5.3
    """
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    
    # Payment details
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Stripe integration fields
    stripe_session_id = Column(String(255))
    stripe_payment_intent_id = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    booking = relationship("Booking", back_populates="payment")

    def __repr__(self):
        return f"<Payment(id={self.id}, booking_id={self.booking_id}, amount={self.amount}, status={self.status})>"

    def is_pending(self) -> bool:
        """Check if payment is pending"""
        return self.status == PaymentStatus.PENDING

    def is_succeeded(self) -> bool:
        """Check if payment succeeded"""
        return self.status == PaymentStatus.SUCCEEDED

    def is_failed(self) -> bool:
        """Check if payment failed"""
        return self.status == PaymentStatus.FAILED

    def is_refunded(self) -> bool:
        """Check if payment was refunded"""
        return self.status == PaymentStatus.REFUNDED

    def validate_amount(self) -> bool:
        """Validate that amount is positive"""
        return self.amount > 0
