# Booking and Calendar Management - Quick Start Guide

## Overview

This guide will help you quickly get started with the booking and calendar management features.

**Requirements:** 5.1, 5.5

---

## Quick Setup

### 1. Database Migration

The booking tables are already created from the initial migration. No additional migration needed.

### 2. Environment Variables

Add these to your `.env` file for calendar integration (optional):

```bash
# Google Calendar (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Microsoft Outlook (optional)
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
```

### 3. Start the Server

```bash
cd backend
uvicorn app.main:app --reload
```

---

## Basic Usage

### 1. Create a Booking (Client)

**Prerequisites:**
- You must be authenticated as a client
- You need a coach's user ID

**Request:**
```bash
curl -X POST http://localhost:8000/booking \
  -H "Authorization: Bearer YOUR_CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "coach_id": "COACH_UUID",
    "session_datetime": "2025-11-15T14:00:00Z",
    "duration_minutes": 60,
    "notes": "Looking forward to discussing career transition"
  }'
```

**Response:**
```json
{
  "id": "BOOKING_UUID",
  "client_id": "YOUR_CLIENT_UUID",
  "coach_id": "COACH_UUID",
  "session_datetime": "2025-11-15T14:00:00Z",
  "duration_minutes": 60,
  "status": "pending",
  "payment_id": null,
  "meeting_link": null,
  "notes": "Looking forward to discussing career transition",
  "created_at": "2025-11-05T10:30:00Z",
  "updated_at": "2025-11-05T10:30:00Z"
}
```

### 2. Check Coach Availability

**Request:**
```bash
curl "http://localhost:8000/booking/coach/COACH_UUID/availability?start_date=2025-11-15T00:00:00Z&end_date=2025-11-16T00:00:00Z&duration_minutes=60"
```

**Response:**
```json
{
  "coach_id": "COACH_UUID",
  "available_slots": [
    {
      "start": "2025-11-15T14:00:00Z",
      "end": "2025-11-15T15:00:00Z",
      "duration_minutes": 60
    },
    {
      "start": "2025-11-15T15:30:00Z",
      "end": "2025-11-15T16:30:00Z",
      "duration_minutes": 60
    }
  ]
}
```

### 3. View Your Bookings

**As Client:**
```bash
curl http://localhost:8000/booking/client/YOUR_CLIENT_UUID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**As Coach:**
```bash
curl http://localhost:8000/booking/coach/YOUR_COACH_UUID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Update Booking Status

**Request:**
```bash
curl -X PATCH http://localhost:8000/booking/BOOKING_UUID/status \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmed"
  }'
```

### 5. Cancel a Booking

**Request:**
```bash
curl -X DELETE http://localhost:8000/booking/BOOKING_UUID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Calendar Integration

### Google Calendar

#### Step 1: Get Authorization URL

```bash
curl "http://localhost:8000/calendar/google/auth-url?redirect_uri=http://localhost:3000/callback" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "random_state_string"
}
```

#### Step 2: User Authorizes

Redirect user to the `auth_url`. After authorization, they'll be redirected back with a code.

#### Step 3: Exchange Code for Token

```bash
curl -X POST "http://localhost:8000/calendar/google/exchange-token?redirect_uri=http://localhost:3000/callback" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "AUTHORIZATION_CODE",
    "state": "random_state_string"
  }'
```

**Response:**
```json
{
  "access_token": "ya29.a0AfH6...",
  "refresh_token": "1//0gHZ...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

#### Step 4: Sync Booking to Calendar

```bash
curl -X POST http://localhost:8000/calendar/sync-booking \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "BOOKING_UUID",
    "calendar_type": "google",
    "access_token": "GOOGLE_ACCESS_TOKEN",
    "timezone": "America/New_York"
  }'
```

**Response:**
```json
{
  "event_id": "google_event_123",
  "meeting_link": "https://meet.google.com/abc-defg-hij",
  "status": "confirmed"
}
```

### Outlook Calendar

Same process as Google Calendar, but use:
- `/calendar/outlook/auth-url`
- `/calendar/outlook/exchange-token`
- `calendar_type: "outlook"` in sync request

---

## Common Workflows

### Complete Booking Flow (Client)

1. **Browse coaches** → `GET /coaches`
2. **Check availability** → `GET /booking/coach/{id}/availability`
3. **Create booking** → `POST /booking`
4. **Make payment** → (Payment API - Task 7)
5. **Booking confirmed** → Status updated to "confirmed"
6. **Sync to calendar** → `POST /calendar/sync-booking`
7. **Attend session** → Use meeting link
8. **Session completed** → Status updated to "completed"

### Coach Booking Management

1. **View bookings** → `GET /booking/coach/{id}`
2. **Confirm booking** → `PATCH /booking/{id}/status`
3. **Sync to calendar** → `POST /calendar/sync-booking`
4. **Complete session** → `PATCH /booking/{id}/status`

### Cancel a Booking

1. **View booking** → `GET /booking/{id}`
2. **Cancel** → `DELETE /booking/{id}`
3. **Refund** → (Payment API - Task 7)

---

## Testing with Python

### Create Test Script

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Login as client
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "client@example.com", "password": "password123"}
)
client_token = login_response.json()["access_token"]

# Get coaches
coaches_response = requests.get(
    f"{BASE_URL}/coaches",
    headers={"Authorization": f"Bearer {client_token}"}
)
coaches = coaches_response.json()["coaches"]
coach_id = coaches[0]["user_id"]

# Check availability
tomorrow = (datetime.utcnow() + timedelta(days=1)).replace(hour=0, minute=0, second=0)
day_after = tomorrow + timedelta(days=1)

availability_response = requests.get(
    f"{BASE_URL}/booking/coach/{coach_id}/availability",
    params={
        "start_date": tomorrow.isoformat() + "Z",
        "end_date": day_after.isoformat() + "Z",
        "duration_minutes": 60
    }
)
slots = availability_response.json()["available_slots"]

if slots:
    # Create booking
    booking_response = requests.post(
        f"{BASE_URL}/booking",
        headers={"Authorization": f"Bearer {client_token}"},
        json={
            "coach_id": coach_id,
            "session_datetime": slots[0]["start"],
            "duration_minutes": 60,
            "notes": "Test booking"
        }
    )
    booking = booking_response.json()
    print(f"Booking created: {booking['id']}")
    
    # View booking
    booking_detail = requests.get(
        f"{BASE_URL}/booking/{booking['id']}",
        headers={"Authorization": f"Bearer {client_token}"}
    ).json()
    print(f"Booking status: {booking_detail['status']}")
else:
    print("No available slots found")
```

---

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Troubleshooting

### "Time slot is not available"
- Check coach availability using the availability endpoint
- Ensure the requested time is in the future
- Try a different time slot

### "Invalid client" or "Invalid coach"
- Verify the user IDs are correct
- Ensure the coach is active
- Check that you're using the correct role (client for booking)

### "Unauthorized to view this booking"
- Ensure you're authenticated
- Verify you're either the client or coach for this booking
- Admins can view all bookings

### Calendar integration not working
- This is a foundational implementation
- For production, you need to set up actual OAuth credentials
- See BOOKING_IMPLEMENTATION.md for production setup

---

## Next Steps

1. **Implement Payment Integration (Task 7)**
   - Connect booking confirmation to payment success
   - Handle payment failures

2. **Add Email Notifications (Task 7)**
   - Send booking confirmations
   - Send session reminders
   - Notify on cancellations

3. **Complete Calendar Integration**
   - Set up Google Cloud project
   - Set up Azure AD application
   - Implement actual API calls
   - Add token storage

4. **Enhance Availability**
   - Implement coach availability UI
   - Store availability preferences
   - Support recurring patterns
   - Handle time zones

---

## Support

For more information:
- **API Reference:** See `BOOKING_API_REFERENCE.md`
- **Implementation Details:** See `BOOKING_IMPLEMENTATION.md`
- **Requirements:** See `.kiro/specs/culturebridge-mvp/requirements.md`
- **Design:** See `.kiro/specs/culturebridge-mvp/design.md`
