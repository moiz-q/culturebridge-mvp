# Admin API Reference

This document provides detailed information about the Admin API endpoints for platform management and analytics.

**Requirements:** 7.1, 7.2, 7.3, 7.4, 7.5

## Authentication

All admin endpoints require:
- Valid JWT token in Authorization header: `Bearer <token>`
- User role must be `admin`

## Endpoints

### 1. Get Platform Metrics

Get platform analytics including users, sessions, and revenue.

**Endpoint:** `GET /admin/metrics`

**Query Parameters:**
- `days` (optional): Number of days to look back (1-365, default: 30)

**Response:** `200 OK`
```json
{
  "period_days": 30,
  "start_date": "2025-10-06T10:30:00Z",
  "end_date": "2025-11-05T10:30:00Z",
  "total_users": 150,
  "total_clients": 100,
  "total_coaches": 45,
  "new_users": 25,
  "active_sessions": 80,
  "session_volume": 120,
  "total_revenue_usd": 4500.00,
  "revenue_by_currency": {
    "USD": 4500.00,
    "EUR": 1200.00
  },
  "avg_session_duration_minutes": 60.0,
  "booking_status_breakdown": {
    "pending": 10,
    "confirmed": 50,
    "completed": 40,
    "cancelled": 20
  }
}
```

**Requirements:** 7.1, 7.2

---

### 2. List Users

Get paginated list of all users with optional filters.

**Endpoint:** `GET /admin/users`

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (1-100, default: 20)
- `role` (optional): Filter by role (`client`, `coach`, `admin`)
- `is_active` (optional): Filter by active status (true/false)
- `email` (optional): Filter by email (partial match)

**Response:** `200 OK`
```json
{
  "users": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "role": "client",
      "is_active": true,
      "email_verified": true,
      "created_at": "2025-11-01T10:30:00Z",
      "updated_at": "2025-11-05T10:30:00Z"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 20
}
```

**Requirements:** 7.2

---

### 3. Get User Activity History

Get detailed activity history for a specific user.

**Endpoint:** `GET /admin/users/{user_id}`

**Path Parameters:**
- `user_id`: UUID of the user

**Response:** `200 OK`
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "role": "client",
  "created_at": "2025-11-01T10:30:00Z",
  "bookings": {
    "total": 5,
    "by_status": {
      "pending": 1,
      "confirmed": 2,
      "completed": 2,
      "cancelled": 0
    }
  },
  "payments": {
    "total": 4,
    "total_amount_usd": 400.00
  },
  "community": {
    "posts_created": 10,
    "comments_made": 25,
    "total_post_upvotes": 45
  }
}
```

**Error Responses:**
- `404 Not Found`: User not found

**Requirements:** 7.4

---

### 4. Update User

Update user role, active status, or email verification.

**Endpoint:** `PATCH /admin/users/{user_id}`

**Path Parameters:**
- `user_id`: UUID of the user

**Request Body:**
```json
{
  "role": "coach",
  "is_active": true,
  "email_verified": true
}
```

All fields are optional. Only provided fields will be updated.

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "role": "coach",
  "is_active": true,
  "email_verified": true,
  "created_at": "2025-11-01T10:30:00Z",
  "updated_at": "2025-11-05T10:30:00Z"
}
```

**Error Responses:**
- `404 Not Found`: User not found

**Requirements:** 7.2, 7.3

---

### 5. Delete User

Delete a user and all associated data.

**Endpoint:** `DELETE /admin/users/{user_id}`

**Path Parameters:**
- `user_id`: UUID of the user

**Response:** `204 No Content`

**Error Responses:**
- `400 Bad Request`: Cannot delete your own account
- `404 Not Found`: User not found

**Requirements:** 7.3

---

### 6. List Bookings

Get paginated list of all bookings with optional filters.

**Endpoint:** `GET /admin/bookings`

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (1-100, default: 20)
- `client_id` (optional): Filter by client UUID
- `coach_id` (optional): Filter by coach UUID
- `status` (optional): Filter by booking status

**Response:** `200 OK`
```json
{
  "bookings": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "client_id": "client-uuid",
      "client_email": "client@example.com",
      "coach_id": "coach-uuid",
      "coach_email": "coach@example.com",
      "session_datetime": "2025-11-10T14:00:00Z",
      "duration_minutes": 60,
      "status": "confirmed",
      "payment_id": "payment-uuid",
      "created_at": "2025-11-05T10:30:00Z",
      "updated_at": "2025-11-05T10:30:00Z"
    }
  ],
  "total": 120,
  "skip": 0,
  "limit": 20
}
```

**Requirements:** 7.2

---

### 7. Delete Forum Post

Delete a forum post for content moderation.

**Endpoint:** `DELETE /admin/posts/{post_id}`

**Path Parameters:**
- `post_id`: UUID of the post

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found`: Post not found

**Requirements:** 7.4

---

### 8. Get Revenue Report

Get revenue report for a date range with grouping.

**Endpoint:** `GET /admin/revenue`

**Query Parameters:**
- `start_date` (required): Start date (ISO 8601 format)
- `end_date` (required): End date (ISO 8601 format)
- `group_by` (optional): Grouping period (`day`, `week`, `month`, default: `day`)

**Response:** `200 OK`
```json
{
  "start_date": "2025-10-01T00:00:00Z",
  "end_date": "2025-10-31T23:59:59Z",
  "group_by": "day",
  "data": [
    {
      "period": "2025-10-01",
      "total_usd": 450.00,
      "by_currency": {
        "USD": 450.00,
        "EUR": 120.00
      },
      "transaction_count": 5
    },
    {
      "period": "2025-10-02",
      "total_usd": 300.00,
      "by_currency": {
        "USD": 300.00
      },
      "transaction_count": 3
    }
  ]
}
```

**Requirements:** 7.5

---

### 9. Export Users to CSV

Export users data to CSV format.

**Endpoint:** `GET /admin/export/users`

**Query Parameters:**
- `role` (optional): Filter by role
- `is_active` (optional): Filter by active status

**Response:** `200 OK`
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename=users_export_YYYYMMDD_HHMMSS.csv`

**CSV Format:**
```csv
ID,Email,Role,Is Active,Email Verified,Created At,Updated At
123e4567-e89b-12d3-a456-426614174000,user@example.com,client,True,True,2025-11-01T10:30:00,2025-11-05T10:30:00
```

**Requirements:** 7.5

---

### 10. Export Bookings to CSV

Export bookings data to CSV format.

**Endpoint:** `GET /admin/export/bookings`

**Query Parameters:**
- `start_date` (optional): Start date filter (ISO 8601)
- `end_date` (optional): End date filter (ISO 8601)

**Response:** `200 OK`
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename=bookings_export_YYYYMMDD_HHMMSS.csv`

**CSV Format:**
```csv
Booking ID,Client ID,Client Email,Coach ID,Coach Email,Session DateTime,Duration (min),Status,Payment ID,Created At,Updated At
123e4567-e89b-12d3-a456-426614174000,client-id,client@example.com,coach-id,coach@example.com,2025-11-10T14:00:00,60,confirmed,payment-id,2025-11-05T10:30:00,2025-11-05T10:30:00
```

**Requirements:** 7.5

---

### 11. Export Revenue to CSV

Export revenue data to CSV format.

**Endpoint:** `GET /admin/export/revenue`

**Query Parameters:**
- `start_date` (required): Start date (ISO 8601)
- `end_date` (required): End date (ISO 8601)

**Response:** `200 OK`
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename=revenue_export_YYYYMMDD_HHMMSS.csv`

**CSV Format:**
```csv
Payment ID,Booking ID,Client ID,Coach ID,Amount,Currency,Status,Session DateTime,Payment Created At
payment-id,booking-id,client-id,coach-id,100.00,USD,succeeded,2025-11-10T14:00:00,2025-11-05T10:30:00
```

**Requirements:** 7.5

---

## Audit Logging

All admin actions are logged with the following information:
- Admin user ID
- Action performed
- Target type and ID
- Additional details
- Timestamp

Logged actions include:
- `view_metrics`
- `list_users`
- `view_user_activity`
- `update_user`
- `delete_user`
- `list_bookings`
- `delete_post`
- `view_revenue_report`
- `export_users_csv`
- `export_bookings_csv`
- `export_revenue_csv`

**Requirements:** 7.2

---

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["query", "days"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

---

## Rate Limiting

Admin endpoints are subject to rate limiting:
- 100 requests per minute per admin user

---

## Security Notes

1. All admin endpoints require admin role
2. Admins cannot delete their own accounts
3. All admin actions are logged for audit purposes
4. Sensitive data is not included in logs
5. CSV exports include timestamps in filenames for tracking
