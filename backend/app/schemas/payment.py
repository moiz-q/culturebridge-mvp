"""
Pydantic schemas for payment API requests and responses.

Requirements: 5.2, 5.3
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CheckoutSessionRequest(BaseModel):
    """Request schema for creating a Stripe checkout session"""
    booking_id: UUID4 = Field(..., description="Booking ID to create payment for")
    success_url: str = Field(..., description="URL to redirect after successful payment")
    cancel_url: str = Field(..., description="URL to redirect after cancelled payment")


class CheckoutSessionResponse(BaseModel):
    """Response schema for checkout session creation"""
    session_id: str = Field(..., description="Stripe checkout session ID")
    url: str = Field(..., description="Stripe checkout URL to redirect user")
    payment_id: str = Field(..., description="Internal payment record ID")
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(..., description="Payment currency code")


class PaymentResponse(BaseModel):
    """Response schema for payment details"""
    id: UUID4 = Field(..., description="Payment ID")
    booking_id: UUID4 = Field(..., description="Associated booking ID")
    amount: Decimal = Field(..., description="Payment amount")
    currency: str = Field(..., description="Payment currency code")
    status: str = Field(..., description="Payment status (pending, succeeded, failed, refunded)")
    stripe_session_id: Optional[str] = Field(None, description="Stripe checkout session ID")
    stripe_payment_intent_id: Optional[str] = Field(None, description="Stripe payment intent ID")
    created_at: datetime = Field(..., description="Payment creation timestamp")
    updated_at: datetime = Field(..., description="Payment last update timestamp")
    
    class Config:
        from_attributes = True


class WebhookEventResponse(BaseModel):
    """Response schema for webhook event processing"""
    status: str = Field(..., description="Processing status (processed, already_processed, unhandled)")
    event_type: Optional[str] = Field(None, description="Stripe event type")
    booking_id: Optional[str] = Field(None, description="Associated booking ID")
    payment_id: Optional[str] = Field(None, description="Associated payment ID")
    event_id: Optional[str] = Field(None, description="Stripe event ID")
