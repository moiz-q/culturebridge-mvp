# CultureBridge API Documentation

## Overview

The CultureBridge API is a RESTful API built with FastAPI that powers an AI-driven intercultural coaching platform. This document provides comprehensive information about all available endpoints, authentication requirements, request/response formats, and error handling.

**Base URL**: `https://api.culturebridge.com` (Production)  
**Base URL**: `https://staging-api.culturebridge.com` (Staging)  
**Base URL**: `http://localhost:8000` (Local Development)

**API Version**: 2.0.0

## Table of Contents

1. [Authentication](#authentication)
2. [Rate Limiting](#rate-limiting)
3. [Error Handling](#error-handling)
4. [Pagination](#pagination)
5. [Endpoints](#endpoints)
   - [Health](#health-endpoints)
   - [Authentication](#authentication-endpoints)
   - [Profile Management](#profile-management-endpoints)
   - [Coach Discovery](#coach-discovery-endpoints)
   - [AI Matching](#ai-matching-endpoints)
   - [Booking](#booking-endpoints)
   - [Calendar Integration](#calendar-integration-endpoints)
   - [Payment Processing](#payment-processing-endpoints)
   - [Community](#community-endpoints)
   - [Admin](#admin-endpoints)

## Authentication

### Overview

The CultureBridge API uses JWT (JSON Web Tokens) for authentication. Most endpoints require a valid JWT token in the Authorization header.

### Obtaining a Token

Use the `/auth/login` endpoint to obtain an access token:

```bash
curl -X POST https://api.culturebridge.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "client"
  }
}
```

### Using the Token

Include the access token in the Authorization header for all authenticated requests:

```bash
curl -X GET https://api.culturebridge.com/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Token Expiration

- **Access Token**: Valid for 24 hours
- **Refresh Token**: Valid for 7 days

Use the `/auth/refresh` endpoint to obtain a new access token before expiration.

### Role-Based Access Control

The API implements role-based access control with three roles:

- **client**: Can book sessions, view coaches, participate in community
- **coach**: Can manage profile, view bookings, participate in community
- **admin**: Full access to all endpoints including analytics and user management

## Rate Limiting

API requests are rate-limited to **100 requests per minute per user** to ensure fair usage and system stability.

### Rate Limit Headers

Each response includes rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699200000
```

### Rate Limit Exceeded

When the rate limit is exceeded, the API returns a 429 status code:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "timestamp": "2025-11-05T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

## Error Handling

### Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {},
    "timestamp": "2025-11-05T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable - External service down |
| 504 | Gateway Timeout - External service timeout |

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input data or missing required fields |
| `UNAUTHORIZED` | 401 | Missing, expired, or invalid JWT token |
| `FORBIDDEN` | 403 | User lacks required permissions for this action |
| `NOT_FOUND` | 404 | Requested resource does not exist |
| `CONFLICT` | 409 | Resource already exists (e.g., duplicate email) |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests in time window |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
| `SERVICE_UNAVAILABLE` | 503 | External service (OpenAI, Stripe) unavailable |
| `GATEWAY_TIMEOUT` | 504 | External service timeout |

## Pagination

List endpoints support pagination using query parameters:

### Query Parameters

- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum items to return (default: 20, max: 100)

### Example Request

```bash
curl -X GET "https://api.culturebridge.com/coaches?skip=20&limit=20" \
  -H "Authorization: Bearer <token>"
```

### Paginated Response Format

```json
{
  "items": [...],
  "total": 150,
  "skip": 20,
  "limit": 20
}
```

---

## Endpoints


### Health Endpoints

#### GET /health

Check API health and database connectivity.

**Authentication**: Not required

**Response**: 200 OK
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T10:30:00Z",
  "version": "2.0.0",
  "database": "connected",
  "redis": "connected"
}
```

---

### Authentication Endpoints

#### POST /auth/signup

Register a new user account.

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "role": "client"
}
```

**Validation**:
- Email must be valid format and unique
- Password minimum 8 characters, must include uppercase, lowercase, number, special character
- Role must be one of: `client`, `coach`, `admin`

**Response**: 201 Created
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "client",
  "is_active": true,
  "email_verified": false,
  "created_at": "2025-11-05T10:30:00Z"
}
```

**Errors**:
- 400: Invalid email or password format
- 409: Email already registered

---

#### POST /auth/login

Authenticate and obtain JWT tokens.

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response**: 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "client"
  }
}
```

**Errors**:
- 401: Invalid credentials
- 403: Account inactive or not verified

---

#### POST /auth/refresh

Refresh access token using refresh token.

**Authentication**: Refresh token required

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response**: 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

#### POST /auth/reset-password

Request password reset email.

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response**: 200 OK
```json
{
  "message": "Password reset email sent if account exists"
}
```

**Note**: Returns success even if email doesn't exist (security best practice).

---

#### POST /auth/reset-password/confirm

Confirm password reset with token.

**Authentication**: Not required

**Request Body**:
```json
{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePassword123!"
}
```

**Response**: 200 OK
```json
{
  "message": "Password reset successful"
}
```

**Errors**:
- 400: Invalid or expired token
- 400: Password doesn't meet requirements

---

### Profile Management Endpoints

#### GET /profile

Get current user's profile.

**Authentication**: Required (any role)

**Response**: 200 OK

For client:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "first_name": "John",
  "last_name": "Doe",
  "photo_url": "https://s3.amazonaws.com/...",
  "phone": "+1234567890",
  "timezone": "America/New_York",
  "quiz_data": {
    "target_countries": ["Spain", "France"],
    "goals": ["career_transition"],
    "languages": ["English", "Spanish"],
    "budget_max": 150
  },
  "preferences": {},
  "created_at": "2025-11-05T10:30:00Z"
}
```


For coach:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "first_name": "Jane",
  "last_name": "Smith",
  "photo_url": "https://s3.amazonaws.com/...",
  "bio": "Experienced intercultural coach...",
  "intro_video_url": "https://youtube.com/...",
  "expertise": ["career_coaching", "cultural_adaptation"],
  "languages": ["English", "Spanish", "French"],
  "countries": ["Spain", "France", "USA"],
  "hourly_rate": 100.00,
  "currency": "USD",
  "availability": {
    "monday": ["09:00-12:00", "14:00-17:00"],
    "tuesday": ["09:00-12:00"]
  },
  "rating": 4.8,
  "total_sessions": 150,
  "is_verified": true,
  "created_at": "2025-11-05T10:30:00Z"
}
```

---

#### PUT /profile

Update current user's profile.

**Authentication**: Required (any role)

**Request Body** (client):
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "timezone": "America/New_York",
  "quiz_data": {
    "target_countries": ["Spain"],
    "goals": ["career_transition"],
    "languages": ["English"],
    "budget_max": 150
  }
}
```

**Request Body** (coach):
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "bio": "Updated bio...",
  "expertise": ["career_coaching"],
  "languages": ["English", "Spanish"],
  "countries": ["Spain", "USA"],
  "hourly_rate": 120.00,
  "availability": {
    "monday": ["09:00-17:00"]
  }
}
```

**Response**: 200 OK (returns updated profile)

**Errors**:
- 400: Invalid data format
- 400: Quiz data missing required fields (client)
- 400: Hourly rate outside allowed range $25-$500 (coach)

---

#### POST /profile/photo

Upload profile photo.

**Authentication**: Required (any role)

**Request**: multipart/form-data
```
photo: <file>
```

**Validation**:
- Max file size: 5MB
- Allowed formats: JPEG, PNG, WebP

**Response**: 200 OK
```json
{
  "photo_url": "https://s3.amazonaws.com/culturebridge-uploads/..."
}
```


**Errors**:
- 400: File too large or invalid format

---

#### GET /profile/export

Export all user data (GDPR compliance).

**Authentication**: Required (any role)

**Response**: 200 OK
```json
{
  "user": {...},
  "profile": {...},
  "bookings": [...],
  "payments": [...],
  "posts": [...],
  "comments": [...],
  "exported_at": "2025-11-05T10:30:00Z"
}
```

---

#### DELETE /profile

Delete user account and all associated data (GDPR compliance).

**Authentication**: Required (any role)

**Response**: 204 No Content

**Note**: This action is irreversible and cascades to all related data.

---

### Coach Discovery Endpoints

#### GET /coaches

List all coaches with optional filters.

**Authentication**: Required (client or admin)

**Query Parameters**:
- `skip`: Pagination offset (default: 0)
- `limit`: Items per page (default: 20, max: 100)
- `language`: Filter by language (e.g., "Spanish")
- `country`: Filter by country experience (e.g., "Spain")
- `expertise`: Filter by expertise area (e.g., "career_coaching")
- `min_rate`: Minimum hourly rate
- `max_rate`: Maximum hourly rate
- `min_rating`: Minimum rating (0-5)

**Example Request**:
```bash
curl -X GET "https://api.culturebridge.com/coaches?language=Spanish&max_rate=150&skip=0&limit=20" \
  -H "Authorization: Bearer <token>"
```

**Response**: 200 OK
```json
{
  "items": [
    {
      "id": "uuid",
      "first_name": "Jane",
      "last_name": "Smith",
      "photo_url": "https://s3.amazonaws.com/...",
      "bio": "Experienced coach...",
      "expertise": ["career_coaching"],
      "languages": ["English", "Spanish"],
      "countries": ["Spain", "USA"],
      "hourly_rate": 100.00,
      "rating": 4.8,
      "total_sessions": 150,
      "is_verified": true
    }
  ],
  "total": 45,
  "skip": 0,
  "limit": 20
}
```

---

#### GET /coaches/{coach_id}

Get detailed coach profile.

**Authentication**: Required (any role)

**Response**: 200 OK
```json
{
  "id": "uuid",
  "first_name": "Jane",
  "last_name": "Smith",
  "photo_url": "https://s3.amazonaws.com/...",
  "bio": "Detailed bio...",
  "intro_video_url": "https://youtube.com/...",
  "expertise": ["career_coaching", "cultural_adaptation"],
  "languages": ["English", "Spanish", "French"],
  "countries": ["Spain", "France", "USA"],
  "hourly_rate": 100.00,
  "currency": "USD",
  "availability": {
    "monday": ["09:00-12:00", "14:00-17:00"],
    "tuesday": ["09:00-12:00"]
  },
  "rating": 4.8,
  "total_sessions": 150,
  "is_verified": true
}
```

**Errors**:
- 404: Coach not found

---

### AI Matching Endpoints

#### POST /match

Get AI-generated coach recommendations.

**Authentication**: Required (client only)

**Request Body**:
```json
{
  "force_refresh": false
}
```

**Note**: Results are cached for 24 hours. Set `force_refresh: true` to bypass cache.

**Response**: 200 OK
```json
{
  "matches": [
    {
      "coach": {
        "id": "uuid",
        "first_name": "Jane",
        "last_name": "Smith",
        "photo_url": "https://s3.amazonaws.com/...",
        "bio": "Experienced coach...",
        "expertise": ["career_coaching"],
        "languages": ["English", "Spanish"],
        "countries": ["Spain"],
        "hourly_rate": 100.00,
        "rating": 4.8,
        "total_sessions": 150
      },
      "match_score": 92,
      "confidence": "high",
      "match_reasons": [
        "Strong language match (English, Spanish)",
        "Experience in target country (Spain)",
        "Expertise aligns with goals (career transition)"
      ]
    }
  ],
  "total_matches": 10,
  "cached": true,
  "generated_at": "2025-11-05T10:30:00Z"
}
```

**Match Score**: 0-100, where:
- 90-100: Excellent match
- 75-89: Good match
- 60-74: Fair match
- Below 60: Poor match

**Errors**:
- 400: Client profile incomplete (missing quiz data)
- 503: OpenAI service unavailable (returns fallback top-rated coaches)
- 504: Matching timeout (returns fallback top-rated coaches)

---

### Booking Endpoints

#### POST /booking

Create a new booking.

**Authentication**: Required (client only)

**Request Body**:
```json
{
  "coach_id": "uuid",
  "session_datetime": "2025-11-10T14:00:00Z",
  "duration_minutes": 60,
  "notes": "Looking forward to discussing career transition"
}
```

**Validation**:
- Session must be in the future
- Duration must be 30, 60, or 90 minutes
- Time slot must be available in coach's schedule


**Response**: 201 Created
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "coach_id": "uuid",
  "session_datetime": "2025-11-10T14:00:00Z",
  "duration_minutes": 60,
  "status": "pending",
  "notes": "Looking forward to discussing career transition",
  "created_at": "2025-11-05T10:30:00Z"
}
```

**Errors**:
- 400: Invalid datetime or duration
- 404: Coach not found
- 409: Time slot not available

---

#### GET /booking/{booking_id}

Get booking details.

**Authentication**: Required (client/coach who owns booking, or admin)

**Response**: 200 OK
```json
{
  "id": "uuid",
  "client": {
    "id": "uuid",
    "first_name": "John",
    "last_name": "Doe",
    "photo_url": "https://s3.amazonaws.com/..."
  },
  "coach": {
    "id": "uuid",
    "first_name": "Jane",
    "last_name": "Smith",
    "photo_url": "https://s3.amazonaws.com/..."
  },
  "session_datetime": "2025-11-10T14:00:00Z",
  "duration_minutes": 60,
  "status": "confirmed",
  "payment_id": "uuid",
  "meeting_link": "https://zoom.us/j/...",
  "notes": "Looking forward to discussing career transition",
  "created_at": "2025-11-05T10:30:00Z"
}
```

**Errors**:
- 403: Not authorized to view this booking
- 404: Booking not found

---

#### GET /booking/client/{client_id}

Get all bookings for a client.

**Authentication**: Required (client who owns bookings, or admin)

**Query Parameters**:
- `skip`, `limit`: Pagination
- `status`: Filter by status (pending, confirmed, completed, cancelled)

**Response**: 200 OK (paginated list of bookings)

---

#### GET /booking/coach/{coach_id}

Get all bookings for a coach.

**Authentication**: Required (coach who owns bookings, or admin)

**Query Parameters**:
- `skip`, `limit`: Pagination
- `status`: Filter by status

**Response**: 200 OK (paginated list of bookings)

---

#### PATCH /booking/{booking_id}/status

Update booking status.

**Authentication**: Required (coach who owns booking, or admin)

**Request Body**:
```json
{
  "status": "confirmed",
  "meeting_link": "https://zoom.us/j/..."
}
```

**Valid Status Transitions**:
- pending → confirmed (coach confirms)
- pending → cancelled (coach or client cancels)
- confirmed → completed (after session)
- confirmed → cancelled (before session)

**Response**: 200 OK (returns updated booking)


**Errors**:
- 400: Invalid status transition
- 403: Not authorized to update this booking

---

#### DELETE /booking/{booking_id}

Cancel a booking.

**Authentication**: Required (client/coach who owns booking, or admin)

**Response**: 204 No Content

**Note**: Triggers refund if payment was made and cancellation is within policy.

---

### Calendar Integration Endpoints

#### POST /calendar/connect

Connect Google Calendar or Outlook.

**Authentication**: Required (coach only)

**Request Body**:
```json
{
  "provider": "google",
  "auth_code": "authorization_code_from_oauth"
}
```

**Response**: 200 OK
```json
{
  "message": "Calendar connected successfully",
  "provider": "google",
  "calendar_id": "primary"
}
```

---

#### POST /calendar/sync/{booking_id}

Sync booking to connected calendar.

**Authentication**: Required (coach who owns booking)

**Response**: 200 OK
```json
{
  "message": "Booking synced to calendar",
  "event_id": "google_calendar_event_id"
}
```

---

### Payment Processing Endpoints

#### POST /payment/checkout

Create Stripe checkout session.

**Authentication**: Required (client only)

**Request Body**:
```json
{
  "booking_id": "uuid"
}
```

**Response**: 200 OK
```json
{
  "session_id": "cs_test_...",
  "checkout_url": "https://checkout.stripe.com/pay/cs_test_...",
  "expires_at": "2025-11-05T11:30:00Z"
}
```

**Flow**:
1. Client creates booking (status: pending)
2. Client initiates checkout
3. Client redirected to Stripe
4. After payment, Stripe webhook updates booking (status: confirmed)
5. Client redirected back to success page

---

#### POST /payment/webhook

Stripe webhook handler (internal use).

**Authentication**: Stripe signature verification

**Events Handled**:
- `checkout.session.completed`
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `charge.refunded`

---

#### GET /payment/{payment_id}

Get payment details.

**Authentication**: Required (client/coach who owns payment, or admin)

**Response**: 200 OK
```json
{
  "id": "uuid",
  "booking_id": "uuid",
  "amount": 100.00,
  "currency": "USD",
  "status": "succeeded",
  "stripe_payment_intent_id": "pi_...",
  "created_at": "2025-11-05T10:30:00Z"
}
```


---

### Community Endpoints

#### GET /community/posts

List forum posts.

**Authentication**: Required (any role)

**Query Parameters**:
- `skip`, `limit`: Pagination
- `post_type`: Filter by type (discussion, question, announcement)
- `is_private`: Filter by visibility (true/false)

**Response**: 200 OK
```json
{
  "items": [
    {
      "id": "uuid",
      "author": {
        "id": "uuid",
        "first_name": "John",
        "last_name": "Doe"
      },
      "title": "Tips for adapting to Spanish culture",
      "content": "I recently moved to Spain and...",
      "post_type": "discussion",
      "is_private": false,
      "upvotes": 15,
      "comment_count": 8,
      "created_at": "2025-11-05T10:30:00Z"
    }
  ],
  "total": 250,
  "skip": 0,
  "limit": 20
}
```

---

#### POST /community/posts

Create a new forum post.

**Authentication**: Required (any role)

**Request Body**:
```json
{
  "title": "Tips for adapting to Spanish culture",
  "content": "I recently moved to Spain and wanted to share...",
  "post_type": "discussion",
  "is_private": false
}
```

**Response**: 201 Created (returns created post)

---

#### GET /community/posts/{post_id}

Get post details with comments.

**Authentication**: Required (any role)

**Response**: 200 OK
```json
{
  "id": "uuid",
  "author": {
    "id": "uuid",
    "first_name": "John",
    "last_name": "Doe"
  },
  "title": "Tips for adapting to Spanish culture",
  "content": "I recently moved to Spain and...",
  "post_type": "discussion",
  "is_private": false,
  "upvotes": 15,
  "comments": [
    {
      "id": "uuid",
      "author": {
        "id": "uuid",
        "first_name": "Jane",
        "last_name": "Smith"
      },
      "content": "Great tips! I would also add...",
      "created_at": "2025-11-05T11:00:00Z"
    }
  ],
  "created_at": "2025-11-05T10:30:00Z"
}
```

---

#### POST /community/posts/{post_id}/comment

Add comment to a post.

**Authentication**: Required (any role)

**Request Body**:
```json
{
  "content": "Great tips! I would also add..."
}
```

**Response**: 201 Created (returns created comment)

---

#### POST /community/posts/{post_id}/upvote

Upvote a post.

**Authentication**: Required (any role)

**Response**: 200 OK
```json
{
  "upvotes": 16
}
```


---

#### GET /community/resources

List resource library items.

**Authentication**: Required (any role)

**Query Parameters**:
- `skip`, `limit`: Pagination
- `resource_type`: Filter by type (article, video, document)
- `tags`: Filter by tags (comma-separated)

**Response**: 200 OK
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Guide to Working in Spain",
      "description": "Comprehensive guide covering...",
      "resource_type": "article",
      "url": "https://culturebridge.com/resources/...",
      "tags": ["spain", "work", "visa"],
      "created_by": {
        "id": "uuid",
        "first_name": "Admin"
      },
      "created_at": "2025-11-05T10:30:00Z"
    }
  ],
  "total": 120,
  "skip": 0,
  "limit": 20
}
```

---

#### POST /community/resources/{resource_id}/bookmark

Bookmark a resource.

**Authentication**: Required (any role)

**Response**: 201 Created
```json
{
  "message": "Resource bookmarked successfully"
}
```

---

#### GET /community/resources/bookmarks

Get user's bookmarked resources.

**Authentication**: Required (any role)

**Response**: 200 OK (paginated list of resources)

---

### Admin Endpoints

**Note**: All admin endpoints require `admin` role.

#### GET /admin/metrics

Get platform analytics.

**Authentication**: Required (admin only)

**Query Parameters**:
- `days`: Number of days to include (default: 30)

**Response**: 200 OK
```json
{
  "period": {
    "start_date": "2025-10-06",
    "end_date": "2025-11-05",
    "days": 30
  },
  "users": {
    "total": 1250,
    "new_this_period": 85,
    "active_this_period": 420,
    "by_role": {
      "client": 950,
      "coach": 280,
      "admin": 20
    }
  },
  "bookings": {
    "total": 3500,
    "this_period": 180,
    "by_status": {
      "pending": 15,
      "confirmed": 45,
      "completed": 110,
      "cancelled": 10
    }
  },
  "revenue": {
    "total": 350000.00,
    "this_period": 18000.00,
    "currency": "USD",
    "average_booking_value": 100.00
  },
  "community": {
    "total_posts": 450,
    "total_comments": 1200,
    "total_resources": 120
  }
}
```

---

#### GET /admin/users

List all users with filters.

**Authentication**: Required (admin only)

**Query Parameters**:
- `skip`, `limit`: Pagination
- `role`: Filter by role
- `is_active`: Filter by active status
- `search`: Search by email or name

**Response**: 200 OK (paginated list of users)

---

#### PATCH /admin/users/{user_id}

Update user account.

**Authentication**: Required (admin only)

**Request Body**:
```json
{
  "role": "coach",
  "is_active": true,
  "email_verified": true
}
```

**Response**: 200 OK (returns updated user)

---

#### DELETE /admin/users/{user_id}

Delete user account.

**Authentication**: Required (admin only)

**Response**: 204 No Content

**Note**: Cascades to all related data.

---

#### GET /admin/bookings

List all bookings.

**Authentication**: Required (admin only)

**Query Parameters**:
- `skip`, `limit`: Pagination
- `status`: Filter by status
- `coach_id`: Filter by coach
- `client_id`: Filter by client
- `start_date`, `end_date`: Filter by date range

**Response**: 200 OK (paginated list of bookings)

---

#### DELETE /admin/posts/{post_id}

Delete forum post (content moderation).

**Authentication**: Required (admin only)

**Response**: 204 No Content

---

#### GET /admin/revenue

Get revenue reports.

**Authentication**: Required (admin only)

**Query Parameters**:
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `format`: Response format (json or csv)

**Response**: 200 OK
```json
{
  "period": {
    "start_date": "2025-10-01",
    "end_date": "2025-10-31"
  },
  "total_revenue": 15000.00,
  "total_bookings": 150,
  "average_booking_value": 100.00,
  "by_coach": [
    {
      "coach_id": "uuid",
      "coach_name": "Jane Smith",
      "bookings": 25,
      "revenue": 2500.00
    }
  ],
  "daily_breakdown": [
    {
      "date": "2025-10-01",
      "bookings": 5,
      "revenue": 500.00
    }
  ]
}
```

---

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `https://api.culturebridge.com/docs`
- **ReDoc**: `https://api.culturebridge.com/redoc`
- **OpenAPI JSON**: `https://api.culturebridge.com/openapi.json`

These interfaces allow you to:
- Browse all available endpoints
- View request/response schemas
- Test endpoints directly in the browser
- Download OpenAPI specification

---

## Code Examples

### Python

```python
import requests

# Login
response = requests.post(
    "https://api.culturebridge.com/auth/login",
    json={"email": "user@example.com", "password": "password"}
)
token = response.json()["access_token"]

# Get coaches
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "https://api.culturebridge.com/coaches?language=Spanish",
    headers=headers
)
coaches = response.json()["items"]
```

### JavaScript

```javascript
// Login
const loginResponse = await fetch('https://api.culturebridge.com/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password'
  })
});
const { access_token } = await loginResponse.json();

// Get coaches
const coachesResponse = await fetch(
  'https://api.culturebridge.com/coaches?language=Spanish',
  {
    headers: { 'Authorization': `Bearer ${access_token}` }
  }
);
const { items: coaches } = await coachesResponse.json();
```

### cURL

```bash
# Login
curl -X POST https://api.culturebridge.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Get coaches (replace TOKEN with actual token)
curl -X GET "https://api.culturebridge.com/coaches?language=Spanish" \
  -H "Authorization: Bearer TOKEN"
```

---

## Support

For API support, please contact:
- Email: api-support@culturebridge.com
- Documentation: https://docs.culturebridge.com
- Status Page: https://status.culturebridge.com

