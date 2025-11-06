# Payment API Reference

## Base URL
```
http://localhost:8000  (development)
https://api.culturebridge.com  (production)
```

## Authentication
All endpoints except `/payment/webhook` require JWT authentication.

Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### 1. Create Checkout Session

Create a Stripe checkout session for a booking payment.

**Endpoint:** `POST /payment/checkout`

**Authentication:** Required (Client or Admin)

**Request Body:**
```json
{
  "booking_id": "uuid",
  "success_url": "string",
  "cancel_url": "string"
}
```

**Request Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| booking_id | UUID | Yes | ID of the booking to create payment for |
| success_url | string | Yes | URL to redirect after successful payment |
| cancel_url | string | Yes | URL to redirect after cancelled payment |

**Success Response:** `201 Created`
```json
{
  "session_id": "cs_test_a1b2c3d4e5f6g7h8i9j0",
  "url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "payment_id": "123e4567-e89b-12d3-a456-426614174000",
  "amount": 75.00,
  "currency": "USD"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| session_id | string | Stripe checkout session ID |
| url | string | Stripe checkout URL to redirect user |
| payment_id | UUID | Internal payment record ID |
| amount | float | Payment amount |
| currency | string | Payment currency code (e.g., "USD") |

**Error Responses:**

`400 Bad Request` - Invalid booking or payment already exists
```json
{
  "detail": "Payment already exists for this booking"
}
```

`403 Forbidden` - Not authorized for this booking
```json
{
  "detail": "Not authorized to create payment for this booking"
}
```

`404 Not Found` - Booking not found
```json
{
  "detail": "Booking not found"
}
```

`500 Internal Server Error` - Stripe API failure
```json
{
  "detail": "Failed to create checkout session: <error details>"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/payment/checkout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "123e4567-e89b-12d3-a456-426614174000",
    "success_url": "https://app.culturebridge.com/booking/success?session_id={CHECKOUT_SESSION_ID}",
    "cancel_url": "https://app.culturebridge.com/booking/cancel"
  }'
```

**Usage Flow:**
1. Client creates a booking (status: PENDING)
2. Client calls this endpoint to create checkout session
3. Backend creates payment record (status: PENDING)
4. Client redirects user to returned `url`
5. User completes payment on Stripe
6. Stripe sends webhook to update payment status
7. User redirected to `success_url` or `cancel_url`

---

### 2. Handle Stripe Webhook

Receive and process Stripe webhook events.

**Endpoint:** `POST /payment/webhook`

**Authentication:** None (verified via Stripe signature)

**Headers:**
```
Stripe-Signature: t=1234567890,v1=abc123...
Content-Type: application/json
```

**Request Body:** Raw Stripe webhook payload (JSON)

**Success Response:** `200 OK`
```json
{
  "status": "processed",
  "event_type": "payment_intent.succeeded",
  "booking_id": "123e4567-e89b-12d3-a456-426614174000",
  "payment_id": "987e6543-e21b-12d3-a456-426614174000"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| status | string | Processing status: "processed", "already_processed", "unhandled" |
| event_type | string | Stripe event type |
| booking_id | string | Associated booking ID (if applicable) |
| payment_id | string | Associated payment ID (if applicable) |
| event_id | string | Stripe event ID (for already_processed status) |

**Webhook Events Handled:**

1. **checkout.session.completed**
   - Updates payment with payment_intent_id
   - Does not change booking status

2. **payment_intent.succeeded**
   - Updates payment status to SUCCEEDED
   - Updates booking status to CONFIRMED
   - Sends confirmation emails to client and coach

3. **payment_intent.payment_failed**
   - Updates payment status to FAILED
   - Booking remains PENDING

4. **charge.refunded**
   - Updates payment status to REFUNDED
   - Updates booking status to CANCELLED

**Error Responses:**

`400 Bad Request` - Invalid signature or payload
```json
{
  "detail": "Invalid signature"
}
```

`500 Internal Server Error` - Event processing failed
```json
{
  "detail": "Failed to process webhook event: <error details>"
}
```

**Example Webhook Payload (payment_intent.succeeded):**
```json
{
  "id": "evt_1234567890",
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_1234567890",
      "amount": 7500,
      "currency": "usd",
      "status": "succeeded",
      "metadata": {
        "booking_id": "123e4567-e89b-12d3-a456-426614174000"
      }
    }
  }
}
```

**Testing Webhooks Locally:**
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/payment/webhook

# Trigger test events
stripe trigger payment_intent.succeeded
```

**Security:**
- Webhook signature verified using STRIPE_WEBHOOK_SECRET
- Idempotency check prevents duplicate processing
- Invalid signatures rejected with 400 error

---

### 3. Get Payment Details

Retrieve payment information by payment ID.

**Endpoint:** `GET /payment/{payment_id}`

**Authentication:** Required (Client, Coach, or Admin)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| payment_id | UUID | Payment ID |

**Success Response:** `200 OK`
```json
{
  "id": "987e6543-e21b-12d3-a456-426614174000",
  "booking_id": "123e4567-e89b-12d3-a456-426614174000",
  "amount": 75.00,
  "currency": "USD",
  "status": "succeeded",
  "stripe_session_id": "cs_test_a1b2c3d4e5f6g7h8i9j0",
  "stripe_payment_intent_id": "pi_test_1234567890",
  "created_at": "2025-11-05T10:30:00Z",
  "updated_at": "2025-11-05T10:31:00Z"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Payment ID |
| booking_id | UUID | Associated booking ID |
| amount | decimal | Payment amount |
| currency | string | Payment currency code |
| status | string | Payment status: "pending", "succeeded", "failed", "refunded" |
| stripe_session_id | string | Stripe checkout session ID |
| stripe_payment_intent_id | string | Stripe payment intent ID |
| created_at | datetime | Payment creation timestamp |
| updated_at | datetime | Payment last update timestamp |

**Error Responses:**

`403 Forbidden` - Not authorized to view this payment
```json
{
  "detail": "Not authorized to view this payment"
}
```

`404 Not Found` - Payment not found
```json
{
  "detail": "Payment not found"
}
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/payment/987e6543-e21b-12d3-a456-426614174000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Authorization Rules:**
- Client can view payments for their own bookings
- Coach can view payments for bookings they're coaching
- Admin can view all payments

---

## Payment Status Flow

```
PENDING → SUCCEEDED (payment successful)
PENDING → FAILED (payment failed)
SUCCEEDED → REFUNDED (refund processed)
```

## Booking Status Updates

Payment events trigger booking status changes:

| Payment Event | Payment Status | Booking Status |
|---------------|----------------|----------------|
| checkout.session.completed | PENDING | PENDING |
| payment_intent.succeeded | SUCCEEDED | CONFIRMED |
| payment_intent.payment_failed | FAILED | PENDING |
| charge.refunded | REFUNDED | CANCELLED |

## Email Notifications

When `payment_intent.succeeded` event is processed:
1. Payment status updated to SUCCEEDED
2. Booking status updated to CONFIRMED
3. Confirmation email sent to client
4. Confirmation email sent to coach
5. Emails sent concurrently within 2 minutes
6. Retry logic: up to 5 attempts with exponential backoff

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (invalid input, validation error) |
| 401 | Unauthorized (missing or invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found (resource doesn't exist) |
| 500 | Internal Server Error (server-side error) |

## Rate Limiting

- Standard rate limit: 100 requests per minute per user
- Webhook endpoint: No rate limit (Stripe controlled)

## Idempotency

- Webhook events tracked by event ID
- Duplicate events return `already_processed` status
- Safe to retry webhook delivery

## Testing

### Test Mode
Use Stripe test keys (sk_test_...) for development.

### Test Cards
```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
Requires Auth: 4000 0025 0000 3155
```

### Test Webhooks
```bash
stripe trigger payment_intent.succeeded
stripe trigger payment_intent.payment_failed
stripe trigger charge.refunded
```

## Production Considerations

1. **Use production Stripe keys** (sk_live_...)
2. **Configure production webhook endpoint** in Stripe Dashboard
3. **Enable HTTPS** (required by Stripe)
4. **Monitor webhook delivery** in Stripe Dashboard
5. **Set up alerts** for failed payments
6. **Log all transactions** for audit trail
7. **Implement refund endpoint** for customer service

## Support

For issues or questions:
- Check Stripe Dashboard for payment details
- Review webhook logs in Stripe Dashboard
- Check backend logs for error details
- Verify environment variables are set correctly
