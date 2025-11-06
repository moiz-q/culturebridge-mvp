"""
Payment API endpoints for Stripe payment processing.

Requirements: 5.2, 5.3
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_role
from app.models.user import User, UserRole
from app.services.payment_service import PaymentService, PaymentError
from app.schemas.payment import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    PaymentResponse,
    WebhookEventResponse
)


router = APIRouter(prefix="/payment", tags=["payment"])


@router.post("/checkout", response_model=CheckoutSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe checkout session for a booking.
    
    This endpoint initiates the payment process by creating a Stripe checkout session.
    The user will be redirected to Stripe's hosted checkout page.
    
    Requirements: 5.2
    
    Args:
        request: Checkout session request with booking_id and redirect URLs
        current_user: Authenticated user (must be client or admin)
        db: Database session
        
    Returns:
        CheckoutSessionResponse with session_id and checkout URL
        
    Raises:
        HTTPException 400: If booking is invalid or payment already exists
        HTTPException 403: If user is not authorized for this booking
        HTTPException 404: If booking not found
        HTTPException 500: If Stripe API fails
    """
    payment_service = PaymentService(db)
    
    try:
        # Get booking to verify ownership
        booking = db.query(payment_service.booking_repo.model).filter(
            payment_service.booking_repo.model.id == request.booking_id
        ).first()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Verify user is the client who made the booking (or admin)
        if current_user.role != UserRole.ADMIN and booking.client_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create payment for this booking"
            )
        
        # Create checkout session
        result = payment_service.create_checkout_session(
            booking_id=request.booking_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )
        
        return CheckoutSessionResponse(**result)
        
    except PaymentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post("/webhook", response_model=WebhookEventResponse, status_code=status.HTTP_200_OK)
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    
    This endpoint receives webhook events from Stripe to process payment status updates.
    It verifies the webhook signature and processes events like payment success, failure, and refunds.
    
    Requirements: 5.2, 5.3
    
    Webhook Events Handled:
    - checkout.session.completed: Payment session completed
    - payment_intent.succeeded: Payment successful, booking confirmed
    - payment_intent.payment_failed: Payment failed
    - charge.refunded: Payment refunded, booking cancelled
    
    Args:
        request: FastAPI request object containing raw payload
        stripe_signature: Stripe signature header for verification
        db: Database session
        
    Returns:
        WebhookEventResponse with processing status
        
    Raises:
        HTTPException 400: If signature verification fails or payload is invalid
        HTTPException 500: If event processing fails
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header"
        )
    
    payment_service = PaymentService(db)
    
    try:
        # Get raw request body
        payload = await request.body()
        
        # Handle webhook event with signature verification
        result = payment_service.handle_webhook_event(
            payload=payload,
            signature=stripe_signature
        )
        
        return WebhookEventResponse(**result)
        
    except PaymentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook event: {str(e)}"
        )


@router.get("/{payment_id}", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
async def get_payment_details(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment details by payment ID.
    
    Requirements: 5.2
    
    Args:
        payment_id: Payment ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        PaymentResponse with payment details
        
    Raises:
        HTTPException 403: If user is not authorized to view this payment
        HTTPException 404: If payment not found
    """
    payment_service = PaymentService(db)
    
    payment = payment_service.get_payment(payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Get booking to verify authorization
    booking = payment_service.booking_repo.get_by_id(payment.booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated booking not found"
        )
    
    # Verify user is client, coach, or admin
    if current_user.role != UserRole.ADMIN:
        if booking.client_id != current_user.id and booking.coach_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this payment"
            )
    
    return PaymentResponse.model_validate(payment)
