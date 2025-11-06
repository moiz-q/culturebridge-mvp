# Payment Processing Implementation

## Overview

This document describes the Stripe payment processing implementation for CultureBridge, including checkout session creation, webhook handling, and email notifications.

**Requirements Implemented:** 5.2, 5.3, 5.4

## Architecture

### Components

1. **PaymentService** (`app/services/payment_service.py`)
   - Stripe API integration
   - Checkout session creation
   - Webhook event processing
   - Payment record management
   - Idempotency handling

2. **EmailService** (`app/services/email_service.py`)
   - SMTP email sending
   - Retry logic (max 5 attempts)
   - HTML email templates
   - Concurrent email delivery

3. **Payment Router** (`app/routers/payment.py`)
   - POST /payment/checkout - Create checkout session
   - POST /payment/webhook - Handle Stripe webhooks
   - GET /payment/{id} - Get payment details

## Payment Flow

### 1. Checkout Session Creation

```
Client → POST /payment/checkout
  ↓
PaymentService.create_checkout_session()
  ↓
Stripe API (create checkout session)
  ↓
Create Payment record (status: PENDING)
  ↓
Return checkout URL to client
  ↓
Client redirected to Stripe checkout page
```

**Request:**
```json
{
  "booking_id": "uuid",
  "success_url": "https://app.culturebridge.com/booking/success",
  "cancel_url": "https://app.culturebridge.com/booking/cancel"
}
```

**Response:**
```json
{
  "session_id": "cs_test_...",
  "url": "https://checkout.stripe.com/...",
  "payment_id": "uuid",
  "amount": 75.00,
  "currency": "USD"
}
```

### 2. Webhook Event Processing

```
Stripe → POST /payment/webhook (with signature)
  ↓
Verify webhook signature
  ↓
Check idempotency (event already processed?)
  ↓
Process event based on type:
  - checkout.session.completed
  - payment_intent.succeeded
  - payment_intent.payment_failed
  - charge.refunded
  ↓
Update Payment and Booking status
  ↓
Send confirmation emails (on success)
```

### 3. Email Notifications

When payment succeeds:
```
payment_intent.succeeded event
  ↓
Update Payment status → SUCCEEDED
Update Booking status → CONFIRMED
  ↓
Queue email tasks (concurrent)
  ├─→ Send email to client
  └─→ Send email to coach
  ↓
Retry up to 5 times with exponential backoff
```

## Webhook Events Handled

### checkout.session.completed
- Updates payment record with payment_intent_id
- Does not change booking status yet

### payment_intent.succeeded
- Updates payment status to SUCCEEDED
- Updates booking status to CONFIRMED
- Sends confirmation emails to client and coach

### payment_intent.payment_failed
- Updates payment status to FAILED
- Booking remains PENDING

### charge.refunded
- Updates payment status to REFUNDED
- Updates booking status to CANCELLED

## Database Models

### Payment Model
```python
class Payment(Base):
    id: UUID
    booking_id: UUID
    amount: Decimal
    currency: str (default: "USD")
    status: PaymentStatus (pending, succeeded, failed, refunded)
    stripe_session_id: str
    stripe_payment_intent_id: str
    created_at: datetime
    updated_at: datetime
```

### Payment Status Transitions
```
PENDING → SUCCEEDED (payment successful)
PENDING → FAILED (payment failed)
SUCCEEDED → REFUNDED (refund processed)
```

## Email Templates

### Client Confirmation Email
- Subject: "Booking Confirmed: Session with [Coach Name]"
- Content:
  - Greeting with client name
  - Session details (coach, date, time, duration)
  - Booking ID
  - Next steps information

### Coach Confirmation Email
- Subject: "New Booking: Session with [Client Name]"
- Content:
  - Greeting with coach name
  - Session details (client, date, time, duration)
  - Payment amount
  - Booking ID
  - Preparation instructions

## Security Features

### Webhook Signature Verification
```python
event = stripe.Webhook.construct_event(
    payload, signature, settings.STRIPE_WEBHOOK_SECRET
)
```

### Idempotency
- Tracks processed event IDs
- Prevents duplicate processing
- Returns "already_processed" status for duplicates

### Authorization
- Checkout: Only booking client or admin can create payment
- Payment details: Only client, coach, or admin can view

## Error Handling

### Payment Errors
- Invalid booking (not found, not pending)
- Payment already exists
- Stripe API failures
- Webhook signature verification failures

### Email Errors
- SMTP connection failures
- Retry logic with exponential backoff (1s, 2s, 4s, 8s, 16s)
- Max 5 retry attempts
- Errors logged but don't fail webhook processing

## Configuration

### Environment Variables
```bash
# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@culturebridge.com
```

## Testing

### Test Stripe Cards
```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
Requires Auth: 4000 0025 0000 3155
```

### Webhook Testing
Use Stripe CLI to forward webhooks to local development:
```bash
stripe listen --forward-to localhost:8000/payment/webhook
```

### Email Testing
For development, use a service like Mailtrap or configure a test SMTP server.

## API Examples

### Create Checkout Session
```bash
curl -X POST http://localhost:8000/payment/checkout \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "123e4567-e89b-12d3-a456-426614174000",
    "success_url": "https://app.culturebridge.com/booking/success",
    "cancel_url": "https://app.culturebridge.com/booking/cancel"
  }'
```

### Get Payment Details
```bash
curl -X GET http://localhost:8000/payment/{payment_id} \
  -H "Authorization: Bearer <token>"
```

### Webhook Endpoint (Stripe calls this)
```bash
POST http://localhost:8000/payment/webhook
Headers:
  Stripe-Signature: t=...,v1=...
Body: <raw webhook payload>
```

## Monitoring

### Key Metrics
- Payment success rate
- Webhook processing time
- Email delivery rate
- Failed payment reasons

### Logging
- All payment operations logged with booking_id
- Webhook events logged with event_id and type
- Email send attempts and failures logged
- Stripe API errors logged with full details

## Future Enhancements

1. **Refund API**: Add endpoint for processing refunds
2. **Payment History**: Add endpoint to list all payments for a user
3. **Email Queue**: Use Redis or message queue for email delivery
4. **Email Templates**: Move templates to database for easy updates
5. **Payment Analytics**: Add dashboard for payment metrics
6. **Multi-currency**: Support multiple currencies based on coach location
7. **Subscription Support**: Add support for subscription-based coaching packages
