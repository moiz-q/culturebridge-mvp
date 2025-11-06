# Payment Processing Quick Start Guide

## Setup

### 1. Install Dependencies
```bash
pip install stripe aiosmtplib
```

### 2. Configure Environment Variables
Create or update `.env` file:
```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@culturebridge.com
```

### 3. Get Stripe Test Keys
1. Sign up at https://stripe.com
2. Go to Developers → API keys
3. Copy your test secret key (starts with `sk_test_`)

### 4. Set Up Webhook Endpoint
1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Login: `stripe login`
3. Forward webhooks to local server:
```bash
stripe listen --forward-to localhost:8000/payment/webhook
```
4. Copy the webhook signing secret (starts with `whsec_`)

## Usage

### Create a Payment for a Booking

**Step 1: Create a booking** (if not already created)
```bash
curl -X POST http://localhost:8000/booking \
  -H "Authorization: Bearer <client_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "coach_id": "coach-uuid",
    "session_datetime": "2025-11-15T14:00:00Z",
    "duration_minutes": 60,
    "notes": "Looking forward to the session"
  }'
```

**Step 2: Create checkout session**
```bash
curl -X POST http://localhost:8000/payment/checkout \
  -H "Authorization: Bearer <client_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "booking-uuid",
    "success_url": "http://localhost:3000/booking/success?session_id={CHECKOUT_SESSION_ID}",
    "cancel_url": "http://localhost:3000/booking/cancel"
  }'
```

**Response:**
```json
{
  "session_id": "cs_test_...",
  "url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "payment_id": "payment-uuid",
  "amount": 75.00,
  "currency": "USD"
}
```

**Step 3: Redirect user to checkout URL**
```javascript
// Frontend code
window.location.href = response.url;
```

**Step 4: User completes payment on Stripe**
- User enters card details
- Stripe processes payment
- User redirected to success_url

**Step 5: Webhook updates booking status**
- Stripe sends `payment_intent.succeeded` webhook
- Backend updates booking to CONFIRMED
- Emails sent to client and coach

### Check Payment Status

```bash
curl -X GET http://localhost:8000/payment/{payment_id} \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "id": "payment-uuid",
  "booking_id": "booking-uuid",
  "amount": 75.00,
  "currency": "USD",
  "status": "succeeded",
  "stripe_session_id": "cs_test_...",
  "stripe_payment_intent_id": "pi_test_...",
  "created_at": "2025-11-05T10:30:00Z",
  "updated_at": "2025-11-05T10:31:00Z"
}
```

## Testing Payment Flow

### Test Cards (Stripe Test Mode)

**Successful Payment:**
```
Card: 4242 4242 4242 4242
Expiry: Any future date
CVC: Any 3 digits
ZIP: Any 5 digits
```

**Payment Declined:**
```
Card: 4000 0000 0000 0002
```

**Requires Authentication (3D Secure):**
```
Card: 4000 0025 0000 3155
```

### Complete Test Flow

1. **Start the backend server:**
```bash
cd backend
uvicorn app.main:app --reload
```

2. **Start Stripe webhook forwarding:**
```bash
stripe listen --forward-to localhost:8000/payment/webhook
```

3. **Create a test booking and payment:**
```bash
# Login as client
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"client@test.com","password":"password"}' \
  | jq -r '.access_token')

# Create booking
BOOKING_ID=$(curl -X POST http://localhost:8000/booking \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "coach_id":"coach-uuid",
    "session_datetime":"2025-11-15T14:00:00Z",
    "duration_minutes":60
  }' | jq -r '.id')

# Create checkout session
CHECKOUT_URL=$(curl -X POST http://localhost:8000/payment/checkout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"booking_id\":\"$BOOKING_ID\",
    \"success_url\":\"http://localhost:3000/success\",
    \"cancel_url\":\"http://localhost:3000/cancel\"
  }" | jq -r '.url')

echo "Visit this URL to complete payment: $CHECKOUT_URL"
```

4. **Complete payment in browser:**
   - Open the checkout URL
   - Use test card: 4242 4242 4242 4242
   - Complete the payment

5. **Verify booking status:**
```bash
curl -X GET http://localhost:8000/booking/$BOOKING_ID \
  -H "Authorization: Bearer $TOKEN"
```

Status should be "confirmed" and payment_id should be set.

## Email Testing

### Using Gmail SMTP

1. **Enable 2-factor authentication** on your Google account
2. **Generate app password:**
   - Go to Google Account → Security
   - 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Configure .env:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

### Using Mailtrap (Development)

1. Sign up at https://mailtrap.io
2. Get SMTP credentials from inbox settings
3. Configure .env:
```bash
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your-mailtrap-user
SMTP_PASSWORD=your-mailtrap-password
SMTP_FROM_EMAIL=noreply@culturebridge.com
```

## Troubleshooting

### Webhook Not Receiving Events

**Problem:** Stripe webhooks not reaching your local server

**Solution:**
1. Ensure Stripe CLI is running: `stripe listen --forward-to localhost:8000/payment/webhook`
2. Check webhook secret in .env matches CLI output
3. Verify server is running on port 8000

### Payment Status Not Updating

**Problem:** Booking status stays "pending" after payment

**Solution:**
1. Check webhook logs in Stripe CLI
2. Verify webhook signature verification passes
3. Check backend logs for errors
4. Ensure database transaction commits successfully

### Emails Not Sending

**Problem:** Confirmation emails not received

**Solution:**
1. Check SMTP credentials in .env
2. Verify SMTP server allows connections
3. Check backend logs for email errors
4. Test SMTP connection manually
5. Check spam folder

### Stripe API Errors

**Problem:** "Invalid API Key" or similar errors

**Solution:**
1. Verify STRIPE_SECRET_KEY in .env
2. Ensure using test key (sk_test_) in development
3. Check Stripe dashboard for API key status
4. Restart server after updating .env

## Production Deployment

### 1. Use Production Stripe Keys
```bash
STRIPE_SECRET_KEY=sk_live_your_production_key
```

### 2. Configure Production Webhook
1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://api.culturebridge.com/payment/webhook`
3. Select events:
   - checkout.session.completed
   - payment_intent.succeeded
   - payment_intent.payment_failed
   - charge.refunded
4. Copy webhook signing secret to production .env

### 3. Use Production Email Service
Consider using:
- AWS SES (Simple Email Service)
- SendGrid
- Mailgun
- Postmark

### 4. Enable HTTPS
Stripe requires HTTPS for production webhooks.

### 5. Monitor Webhooks
- Set up alerts for failed webhooks
- Monitor webhook delivery in Stripe Dashboard
- Log all webhook events for debugging

## Next Steps

1. **Test the complete flow** with test cards
2. **Verify email delivery** to both client and coach
3. **Check booking status updates** after payment
4. **Review Stripe Dashboard** for payment records
5. **Test refund flow** (if implemented)
6. **Set up monitoring** for production

## Support

- Stripe Documentation: https://stripe.com/docs
- Stripe API Reference: https://stripe.com/docs/api
- Stripe Testing: https://stripe.com/docs/testing
