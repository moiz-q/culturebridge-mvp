"""
Payment service for managing Stripe payment processing and booking confirmations.

Requirements: 5.2, 5.3
"""
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
import stripe
import asyncio
import logging

from app.config import settings
from app.models.booking import Booking, BookingStatus, Payment, PaymentStatus
from app.repositories.booking_repository import BookingRepository
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


# Initialize Stripe with API key
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentError(Exception):
    """Custom exception for payment errors"""
    pass


class PaymentService:
    """Service class for payment operations with Stripe integration"""
    
    def __init__(self, db: Session):
        self.db = db
        self.booking_repo = BookingRepository(db)
        # Track processed webhook events for idempotency
        self._processed_events = set()
    
    def create_checkout_session(
        self,
        booking_id: UUID,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for a booking.
        
        Args:
            booking_id: Booking ID to create payment for
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect after cancelled payment
            
        Returns:
            Dictionary containing checkout session details including session_id and url
            
        Raises:
            PaymentError: If booking not found, invalid, or Stripe API fails
            
        Requirements: 5.2
        """
        # Get booking
        booking = self.booking_repo.get_by_id(booking_id)
        
        if not booking:
            raise PaymentError("Booking not found")
        
        # Validate booking is pending
        if not booking.is_pending():
            raise PaymentError(f"Cannot create payment for booking with status {booking.status}")
        
        # Check if payment already exists
        if booking.payment:
            raise PaymentError("Payment already exists for this booking")
        
        # Get coach profile to get pricing
        coach_profile = booking.coach.coach_profile
        
        if not coach_profile:
            raise PaymentError("Coach profile not found")
        
        # Calculate amount (hourly rate * duration in hours)
        duration_hours = Decimal(booking.duration_minutes) / Decimal(60)
        amount = coach_profile.hourly_rate * duration_hours
        
        # Convert to cents for Stripe (Stripe uses smallest currency unit)
        amount_cents = int(amount * 100)
        
        try:
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': coach_profile.currency.lower(),
                        'unit_amount': amount_cents,
                        'product_data': {
                            'name': f'Coaching Session with {coach_profile.first_name} {coach_profile.last_name}',
                            'description': f'{booking.duration_minutes} minute session on {booking.session_datetime.strftime("%Y-%m-%d %H:%M")}',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(booking_id),
                metadata={
                    'booking_id': str(booking_id),
                    'client_id': str(booking.client_id),
                    'coach_id': str(booking.coach_id),
                }
            )
            
            # Create payment record in database
            payment = Payment(
                booking_id=booking_id,
                amount=amount,
                currency=coach_profile.currency,
                status=PaymentStatus.PENDING,
                stripe_session_id=checkout_session.id
            )
            
            self.db.add(payment)
            
            # Update booking with payment reference
            booking.payment_id = payment.id
            booking.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(payment)
            
            return {
                'session_id': checkout_session.id,
                'url': checkout_session.url,
                'payment_id': str(payment.id),
                'amount': float(amount),
                'currency': coach_profile.currency
            }
            
        except stripe.error.StripeError as e:
            self.db.rollback()
            raise PaymentError(f"Stripe API error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise PaymentError(f"Failed to create checkout session: {str(e)}")
    
    def get_payment(self, payment_id: UUID) -> Optional[Payment]:
        """
        Get payment by ID.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment object or None if not found
        """
        return self.db.query(Payment).filter(Payment.id == payment_id).first()
    
    def get_payment_by_booking(self, booking_id: UUID) -> Optional[Payment]:
        """
        Get payment by booking ID.
        
        Args:
            booking_id: Booking ID
            
        Returns:
            Payment object or None if not found
        """
        return self.db.query(Payment).filter(Payment.booking_id == booking_id).first()
    
    def handle_webhook_event(
        self,
        payload: bytes,
        signature: str
    ) -> Dict[str, Any]:
        """
        Handle Stripe webhook events with signature verification and idempotency.
        
        Args:
            payload: Raw webhook payload bytes
            signature: Stripe signature header
            
        Returns:
            Dictionary with processing result
            
        Raises:
            PaymentError: If signature verification fails or event processing fails
            
        Requirements: 5.2, 5.3
        """
        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise PaymentError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise PaymentError("Invalid signature")
        
        # Idempotency check - prevent processing same event twice
        event_id = event['id']
        if event_id in self._processed_events:
            return {'status': 'already_processed', 'event_id': event_id}
        
        # Handle different event types
        event_type = event['type']
        
        try:
            if event_type == 'checkout.session.completed':
                result = self._handle_checkout_completed(event['data']['object'])
            elif event_type == 'payment_intent.succeeded':
                result = self._handle_payment_succeeded(event['data']['object'])
            elif event_type == 'payment_intent.payment_failed':
                result = self._handle_payment_failed(event['data']['object'])
            elif event_type == 'charge.refunded':
                result = self._handle_charge_refunded(event['data']['object'])
            else:
                result = {'status': 'unhandled', 'event_type': event_type}
            
            # Mark event as processed
            self._processed_events.add(event_id)
            
            return result
            
        except Exception as e:
            self.db.rollback()
            raise PaymentError(f"Failed to process webhook event: {str(e)}")
    
    def _handle_checkout_completed(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle checkout.session.completed event.
        
        Updates payment record with payment intent ID and confirms booking.
        
        Requirements: 5.3
        """
        booking_id = UUID(session['metadata']['booking_id'])
        payment_intent_id = session.get('payment_intent')
        
        # Get payment by stripe session ID
        payment = self.db.query(Payment).filter(
            Payment.stripe_session_id == session['id']
        ).first()
        
        if not payment:
            raise PaymentError(f"Payment not found for session {session['id']}")
        
        # Update payment with payment intent ID
        payment.stripe_payment_intent_id = payment_intent_id
        payment.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            'status': 'processed',
            'event_type': 'checkout.session.completed',
            'booking_id': str(booking_id),
            'payment_id': str(payment.id)
        }
    
    def _handle_payment_succeeded(self, payment_intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle payment_intent.succeeded event.
        
        Updates payment status to SUCCEEDED and booking status to CONFIRMED.
        Sends confirmation emails to both client and coach.
        
        Requirements: 5.3, 5.4
        """
        payment_intent_id = payment_intent['id']
        
        # Get payment by payment intent ID
        payment = self.db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent_id
        ).first()
        
        if not payment:
            raise PaymentError(f"Payment not found for payment intent {payment_intent_id}")
        
        # Update payment status
        payment.status = PaymentStatus.SUCCEEDED
        payment.updated_at = datetime.utcnow()
        
        # Get booking and update status to CONFIRMED
        booking = self.booking_repo.get_by_id(payment.booking_id)
        
        if booking:
            booking.status = BookingStatus.CONFIRMED
            booking.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Send confirmation emails asynchronously (within 2 minutes requirement)
        if booking:
            try:
                # Run email sending in background
                asyncio.create_task(
                    email_service.send_booking_confirmations(
                        booking=booking,
                        client=booking.client,
                        coach=booking.coach
                    )
                )
                logger.info(f"Booking confirmation emails queued for booking {booking.id}")
            except Exception as e:
                # Log error but don't fail the webhook processing
                logger.error(f"Failed to queue confirmation emails: {str(e)}")
        
        return {
            'status': 'processed',
            'event_type': 'payment_intent.succeeded',
            'booking_id': str(payment.booking_id),
            'payment_id': str(payment.id)
        }
    
    def _handle_payment_failed(self, payment_intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle payment_intent.payment_failed event.
        
        Updates payment status to FAILED.
        
        Requirements: 5.3
        """
        payment_intent_id = payment_intent['id']
        
        # Get payment by payment intent ID
        payment = self.db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent_id
        ).first()
        
        if not payment:
            raise PaymentError(f"Payment not found for payment intent {payment_intent_id}")
        
        # Update payment status
        payment.status = PaymentStatus.FAILED
        payment.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            'status': 'processed',
            'event_type': 'payment_intent.payment_failed',
            'booking_id': str(payment.booking_id),
            'payment_id': str(payment.id)
        }
    
    def _handle_charge_refunded(self, charge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle charge.refunded event.
        
        Updates payment status to REFUNDED and booking status to CANCELLED.
        
        Requirements: 5.3
        """
        payment_intent_id = charge.get('payment_intent')
        
        if not payment_intent_id:
            raise PaymentError("No payment intent ID in charge object")
        
        # Get payment by payment intent ID
        payment = self.db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent_id
        ).first()
        
        if not payment:
            raise PaymentError(f"Payment not found for payment intent {payment_intent_id}")
        
        # Update payment status
        payment.status = PaymentStatus.REFUNDED
        payment.updated_at = datetime.utcnow()
        
        # Get booking and update status to CANCELLED
        booking = self.booking_repo.get_by_id(payment.booking_id)
        
        if booking:
            booking.status = BookingStatus.CANCELLED
            booking.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            'status': 'processed',
            'event_type': 'charge.refunded',
            'booking_id': str(payment.booking_id),
            'payment_id': str(payment.id)
        }
