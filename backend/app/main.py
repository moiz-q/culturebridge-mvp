from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
import redis.asyncio as redis

from app.config import settings
from app.routers import auth
from app.routers.profile import router as profile_router, coaches_router
from app.routers import matching
from app.routers import booking
from app.routers import calendar
from app.routers import payment
from app.routers import community
from app.routers import admin
from app.routers import health
from app.exceptions import CultureBridgeException
from app.middleware.request_id_middleware import RequestIDMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limit_middleware import RateLimitMiddleware
from app.middleware.security_headers_middleware import SecurityHeadersMiddleware
from app.middleware.csrf_middleware import CSRFMiddleware
from app.middleware.metrics_middleware import MetricsMiddleware
from app.middleware.error_handler import (
    culturebridge_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler
)
from app.utils.logging_config import setup_logging

# Initialize logging
setup_logging()

app = FastAPI(
    title="CultureBridge API",
    description="""
# CultureBridge API

AI-powered intercultural coaching platform connecting coaches with clients worldwide.

## Features

* **Authentication**: Secure JWT-based authentication with role-based access control
* **AI Matching**: OpenAI-powered coach matching based on 20+ factors
* **Booking System**: Complete session booking and calendar management
* **Payment Processing**: Secure Stripe integration for payments
* **Community Features**: Forums, resources, and user engagement
* **Admin Dashboard**: Analytics, user management, and content moderation

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

To obtain a token, use the `/auth/login` endpoint with valid credentials.

## Rate Limiting

API requests are rate-limited to 100 requests per minute per user. Rate limit information is included in response headers:

* `X-RateLimit-Limit`: Maximum requests allowed
* `X-RateLimit-Remaining`: Remaining requests in current window
* `X-RateLimit-Reset`: Time when the rate limit resets

## Error Responses

All errors follow a consistent JSON format:

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

Common error codes:
* `VALIDATION_ERROR` (400): Invalid input data
* `UNAUTHORIZED` (401): Missing or invalid authentication
* `FORBIDDEN` (403): Insufficient permissions
* `NOT_FOUND` (404): Resource not found
* `CONFLICT` (409): Resource already exists
* `RATE_LIMIT_EXCEEDED` (429): Too many requests
* `INTERNAL_ERROR` (500): Server error
* `SERVICE_UNAVAILABLE` (503): External service unavailable

## Pagination

List endpoints support pagination with the following query parameters:

* `skip`: Number of items to skip (default: 0)
* `limit`: Maximum items to return (default: 20, max: 100)

Paginated responses include metadata:

```json
{
  "items": [...],
  "total": 150,
  "skip": 0,
  "limit": 20
}
```
    """,
    version="2.0.0",
    contact={
        "name": "CultureBridge Support",
        "email": "support@culturebridge.com",
        "url": "https://culturebridge.com/support"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://culturebridge.com/terms"
    },
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check and system status endpoints"
        },
        {
            "name": "auth",
            "description": "Authentication and authorization operations including signup, login, and password reset"
        },
        {
            "name": "profile",
            "description": "User profile management for clients and coaches"
        },
        {
            "name": "coaches",
            "description": "Coach discovery and profile viewing"
        },
        {
            "name": "matching",
            "description": "AI-powered coach matching based on client preferences and quiz data"
        },
        {
            "name": "booking",
            "description": "Session booking and calendar management"
        },
        {
            "name": "calendar",
            "description": "Calendar integration with Google Calendar and Outlook"
        },
        {
            "name": "payment",
            "description": "Payment processing with Stripe"
        },
        {
            "name": "community",
            "description": "Community forums, posts, and resource library"
        },
        {
            "name": "admin",
            "description": "Admin-only endpoints for platform management and analytics"
        }
    ]
)

# Initialize Redis client for rate limiting
redis_client = None
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False)
except Exception as e:
    print(f"Warning: Could not connect to Redis for rate limiting: {e}")

# Add middleware in order (first added = outermost layer)
# 1. Security headers (outermost)
app.add_middleware(SecurityHeadersMiddleware)

# 2. CSRF protection
app.add_middleware(CSRFMiddleware)

# 3. Rate limiting
app.add_middleware(RateLimitMiddleware, redis_client=redis_client)

# 4. Response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 5. Request ID middleware
app.add_middleware(RequestIDMiddleware)

# 6. Logging middleware
app.add_middleware(LoggingMiddleware)

# 7. Metrics middleware
app.add_middleware(MetricsMiddleware)

# 8. CORS configuration (innermost, closest to routes)
cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-CSRF-Token"],
)

# Register exception handlers
app.add_exception_handler(CultureBridgeException, culturebridge_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(health.router)  # Health checks first
app.include_router(auth.router)
app.include_router(profile_router)
app.include_router(coaches_router)
app.include_router(matching.router)
app.include_router(booking.router)
app.include_router(calendar.router)
app.include_router(payment.router)
app.include_router(community.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"message": "CultureBridge API v2.0", "version": "2.0.0"}


# Setup monitoring alarms on startup (production only)
@app.on_event("startup")
async def startup_event():
    """Initialize monitoring and alerting on application startup."""
    from app.utils.alerting import alert_manager
    alert_manager.setup_all_alarms()
