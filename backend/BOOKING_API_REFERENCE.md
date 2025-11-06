# Booking and Calendar API Reference

## Overview

This document provides a comprehensive reference for the booking and calendar management APIs implemented for CultureBridge Phase 2.

**Requirements Covered:** 5.1, 5.5

## Booking Management

### Create Booking

**Endpoint:** `POST /booking`

**Description:** Create a new booking for a coaching session with status PENDING.

**Authentication:** Required (Client role only)

**Request Body:**
```json
{
  "coach_id": "323e4567-e89b-12d3-a456-426614174000",
  "session_datetime": "2025-11-15T14:00:00Z",
  "duration_minutes": 60,
  "notes": "Looking forward to discussing career transition strategies"
}
```

**Response:** `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "client_id": "223e4567-e89b-12d3-a456-426614174000",
  "coach_id": "323e4567-e89b-12d3-a456-426614174000",
  "session_datetime": "2025-11-15T14:00:00Z",
  "duration_minutes": 60,
  "status": "pending",
  "payment_id": null,
  "meeting_link": null,
  "notes": "Looking forward to discussing career transition strategies",
  "created_at": "2025-11-05T10:30:00Z",
  "updated_at": "2025-11-05T10:30:00Z"
}
```

**Validation:**
- Session must be scheduled in the future
- Duration must be between 15 and 480 minutes
- Time slot must be available for the coach
- Coach must be active

---

### Get Booking Details

**Endpoint:** `GET /booking/{booking_id}`

**Description:** Get detailed information about a specific booking.

**Authentication:** Required (Client, Coach, or Admin)

**Authorization:** Users can only view their own bookings (as client or coach). Admins can view all bookings.

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "client_id": "223e4567-e89b-12d3-a456-426614174000",
  "client_name": "John Doe",
  "client_email": "john@example.com",
  "coach_id": "323e4567-e89b-12d3-a456-426614174000",
  "coach_name": "Jane Smith",
  "coach_email": "jane@example.com",
  "session_datetime": "2025-11-15T14:00:00Z",
  "duration_minutes": 60,
  "status": "pending",
  "payment_id": null,
  "meeting_link": null,
  "notes": "Looking forward to discussing career transition strategies",
  "created_at": "2025-11-05T10:30:00Z",
  "updated_at": "2025-11-05T10:30:00Z"
}
```

---

### Get Client Bookings

**Endpoint:** `GET /booking/client/{client_id}`

**Description:** Get all bookings for a specific client with pagination.

**Authentication:** Required

**Authorization:** Users can only view their own bookings unless they are admin.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 20, max: 100)
- `status` (optional): Filter by booking status (pending, confirmed, completed, cancelled)

**Response:** `200 OK`
```json
{
  "bookings": [...],
  "total": 5,
  "skip": 0,
  "limit": 20
}
```

---

### Get Coach Bookings

**Endpoint:** `GET /booking/coach/{coach_id}`

**Description:** Get all bookings for a specific coach with pagination.

**Authentication:** Required

**Authorization:** Users can only view their own bookings unless they are admin.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 20, max: 100)
- `status` (optional): Filter by booking status (pending, confirmed, completed, cancelled)

**Response:** `200 OK`
```json
{
  "bookings": [...],
  "total": 12,
  "skip": 0,
  "limit": 20
}
```

---

### Update Booking Status

**Endpoint:** `PATCH /booking/{booking_id}/status`

**Description:** Update the status of a booking.

**Authentication:** Required (Client, Coach, or Admin)

**Authorization:** Only the client, coach, or admin can update the booking.

**Request Body:**
```json
{
  "status": "confirmed"
}
```

**Valid Status Transitions:**
- `pending` → `confirmed`, `cancelled`
- `confirmed` → `completed`, `cancelled`
- `completed` → (no transitions)
- `cancelled` → (no transitions)

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "confirmed",
  ...
}
```

---

### Cancel Booking

**Endpoint:** `DELETE /booking/{booking_id}`

**Description:** Cancel a booking by setting its status to CANCELLED.

**Authentication:** Required (Client, Coach, or Admin)

**Authorization:** Only the client, coach, or admin can cancel the booking.

**Response:** `204 No Content`

**Note:** Only bookings with status PENDING or CONFIRMED can be cancelled.

---

### Get Coach Availability

**Endpoint:** `GET /booking/coach/{coach_id}/availability`

**Description:** Get available time slots for a coach within a date range.

**Authentication:** Not required (public endpoint)

**Query Parameters:**
- `start_date` (required): Start of date range (UTC)
- `end_date` (required): End of date range (UTC)
- `duration_minutes` (optional): Desired slot duration in minutes (default: 60, min: 15, max: 480)

**Validation:**
- End date must be after start date
- Date range cannot exceed 30 days

**Response:** `200 OK`
```json
{
  "coach_id": "323e4567-e89b-12d3-a456-426614174000",
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

**Note:** This is a simplified implementation that assumes 9 AM - 5 PM working hours. In production, this would integrate with the coach's availability JSONB field.

---

## Calendar Integration

### Get Google Calendar Authorization URL

**Endpoint:** `GET /calendar/google/auth-url`

**Description:** Generate OAuth authorization URL for Google Calendar integration.

**Authentication:** Required

**Query Parameters:**
- `redirect_uri` (required): Redirect URI after authorization

**Response:** `200 OK`
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "random_state_string"
}
```

**Usage:**
1. Call this endpoint to get the authorization URL
2. Redirect user to the `auth_url`
3. User authorizes the application
4. User is redirected back to `redirect_uri` with authorization code
5. Exchange the code for tokens using `/calendar/google/exchange-token`

---

### Get Outlook Calendar Authorization URL

**Endpoint:** `GET /calendar/outlook/auth-url`

**Description:** Generate OAuth authorization URL for Outlook Calendar integration.

**Authentication:** Required

**Query Parameters:**
- `redirect_uri` (required): Redirect URI after authorization

**Response:** `200 OK`
```json
{
  "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?...",
  "state": "random_state_string"
}
```

---

### Exchange Google Authorization Code

**Endpoint:** `POST /calendar/google/exchange-token`

**Description:** Exchange authorization code for Google Calendar access token.

**Authentication:** Required

**Query Parameters:**
- `redirect_uri` (required): Redirect URI used in authorization

**Request Body:**
```json
{
  "code": "4/0AY0e-g7...",
  "state": "random_state_string"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "ya29.a0AfH6...",
  "refresh_token": "1//0gHZ...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

**Note:** In production, tokens should be stored securely in the database associated with the user.

---

### Exchange Outlook Authorization Code

**Endpoint:** `POST /calendar/outlook/exchange-token`

**Description:** Exchange authorization code for Outlook Calendar access token.

**Authentication:** Required

**Query Parameters:**
- `redirect_uri` (required): Redirect URI used in authorization

**Request Body:**
```json
{
  "code": "M.R3_BAY...",
  "state": "random_state_string"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "EwBwA8l6BAAURSN...",
  "refresh_token": "M.R3_BAY...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

---

### Sync Booking to Calendar

**Endpoint:** `POST /calendar/sync-booking`

**Description:** Create a calendar event for a booking in Google Calendar or Outlook Calendar.

**Authentication:** Required

**Authorization:** Only the client or coach can sync their bookings.

**Request Body:**
```json
{
  "booking_id": "123e4567-e89b-12d3-a456-426614174000",
  "calendar_type": "google",
  "access_token": "ya29.a0AfH6...",
  "timezone": "America/New_York"
}
```

**Response:** `200 OK`
```json
{
  "event_id": "google_event_123",
  "meeting_link": "https://meet.google.com/abc-defg-hij",
  "status": "confirmed"
}
```

**Calendar Types:**
- `google` - Google Calendar
- `outlook` - Outlook Calendar

**Note:** The meeting link is automatically added to the booking record.

---

## Booking Status Flow

```
PENDING → CONFIRMED → COMPLETED
   ↓           ↓
CANCELLED   CANCELLED
```

**Status Descriptions:**
- `PENDING`: Booking created, awaiting payment confirmation
- `CONFIRMED`: Payment successful, booking confirmed
- `COMPLETED`: Session has been completed
- `CANCELLED`: Booking cancelled by client, coach, or admin

---

## Error Responses

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "detail": "Time slot is not available"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden:**
```json
{
  "detail": "Unauthorized to view this booking"
}
```

**404 Not Found:**
```json
{
  "detail": "Booking not found"
}
```

---

## Implementation Notes

### Availability Checking

The booking service implements availability checking by:
1. Calculating the requested time slot (start time + duration)
2. Querying for overlapping bookings with status PENDING or CONFIRMED
3. Checking if any bookings overlap with the requested slot
4. Returning availability status

### Calendar Integration

The calendar integration is implemented as a foundational structure:
- OAuth flow endpoints are provided for both Google and Outlook
- Calendar event creation methods are implemented with proper data structures
- In production, these would integrate with actual Google Calendar API and Microsoft Graph API
- Token storage and refresh logic would be added to the database

### Security Considerations

- All booking endpoints require authentication
- Role-based access control ensures users can only access their own bookings
- OAuth state parameters provide CSRF protection
- Calendar tokens should be encrypted at rest in production

---

## Testing

To test the booking endpoints:

1. **Create a booking:**
   ```bash
   curl -X POST http://localhost:8000/booking \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "coach_id": "COACH_UUID",
       "session_datetime": "2025-11-15T14:00:00Z",
       "duration_minutes": 60
     }'
   ```

2. **Get booking details:**
   ```bash
   curl http://localhost:8000/booking/BOOKING_UUID \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **Check availability:**
   ```bash
   curl "http://localhost:8000/booking/coach/COACH_UUID/availability?start_date=2025-11-15T00:00:00Z&end_date=2025-11-16T00:00:00Z"
   ```

---

## Future Enhancements

1. **Advanced Availability Management:**
   - Integrate with coach's availability JSONB field
   - Support recurring availability patterns
   - Handle multiple time zones properly

2. **Calendar Integration:**
   - Implement actual Google Calendar API integration
   - Implement actual Microsoft Graph API integration
   - Add token refresh logic
   - Store calendar tokens securely in database
   - Support calendar event updates and deletions

3. **Notifications:**
   - Send email notifications on booking creation
   - Send reminders before sessions
   - Notify on booking status changes

4. **Booking Management:**
   - Support recurring bookings
   - Add booking notes and attachments
   - Implement booking history and analytics
