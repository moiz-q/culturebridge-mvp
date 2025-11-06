# Error Handling and Logging Implementation

## Overview

This document describes the error handling and logging infrastructure implemented for the CultureBridge API.

**Requirements:** 8.3, 8.4

## Error Handling

### Custom Exception Classes

Created a hierarchy of custom exceptions in `app/exceptions.py`:

- **CultureBridgeException** - Base exception for all custom errors
- **ValidationException** (400) - Input validation failures
- **UnauthorizedException** (401) - Authentication failures
- **ForbiddenException** (403) - Insufficient permissions
- **NotFoundException** (404) - Resource not found
- **ConflictException** (409) - Resource conflicts
- **RateLimitException** (429) - Rate limit exceeded
- **InternalServerException** (500) - Unexpected server errors
- **ServiceUnavailableException** (503) - External service unavailable
- **GatewayTimeoutException** (504) - External service timeout

### Consistent Error Response Format

All errors return a standardized JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "additional context"
    },
    "timestamp": "2025-11-05T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### Exception Handlers

Registered global exception handlers in `app/middleware/error_handler.py`:

- **culturebridge_exception_handler** - Handles custom CultureBridge exceptions
- **validation_exception_handler** - Handles Pydantic validation errors
- **sqlalchemy_exception_handler** - Handles database errors
- **generic_exception_handler** - Catches all unexpected exceptions

### Retry Logic

Created retry utilities in `app/utils/retry_utils.py`:

- **retry_with_backoff** - Generic retry decorator with exponential backoff
- **retry_openai** - Specialized for OpenAI API (3 retries, exponential backoff)
- **retry_stripe** - Specialized for Stripe API (2 retries, 1s fixed delay)
- **with_timeout** - Execute coroutines with timeout

Usage example:
```python
from app.utils.retry_utils import retry_openai

@retry_openai
async def call_openai_api():
    # API call here
    pass
```

## Structured Logging

### Logging Configuration

Created structured logging setup in `app/utils/logging_config.py`:

- **Production**: JSON-formatted logs for CloudWatch integration
- **Development**: Pretty-printed logs for readability
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### JSON Log Format

Production logs include:

```json
{
  "timestamp": "2025-11-05T10:30:00Z",
  "level": "INFO",
  "service": "culturebridge-api",
  "logger": "app.routers.auth",
  "message": "User logged in successfully",
  "request_id": "req_abc123",
  "user_id": "user_xyz",
  "endpoint": "/auth/login",
  "duration_ms": 150
}
```

### Middleware

#### Request ID Middleware
- Generates unique UUID for each request
- Adds `X-Request-ID` header to responses
- Attaches request ID to request state for logging

#### Logging Middleware
- Logs all incoming requests
- Logs all responses with status code and duration
- Adds `X-Response-Time` header to responses
- Logs errors with full context

### Log Levels by Component

- **Application**: INFO (configurable via LOG_LEVEL env var)
- **Uvicorn**: INFO
- **SQLAlchemy**: WARNING
- **OpenAI**: WARNING
- **Stripe**: WARNING

## Integration

### Main Application Setup

The error handling and logging are initialized in `app/main.py`:

```python
from app.utils.logging_config import setup_logging
from app.middleware.request_id_middleware import RequestIDMiddleware
from app.middleware.logging_middleware import LoggingMiddleware

# Initialize logging
setup_logging()

# Add middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)

# Register exception handlers
app.add_exception_handler(CultureBridgeException, culturebridge_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
```

## Usage Examples

### Raising Custom Exceptions

```python
from app.exceptions import NotFoundException, ValidationException

# Not found
raise NotFoundException(
    message="Coach not found",
    details={"coach_id": coach_id}
)

# Validation error
raise ValidationException(
    message="Invalid email format",
    details={"field": "email", "value": email}
)
```

### Logging with Context

```python
import logging

logger = logging.getLogger(__name__)

# Info log
logger.info(
    "User profile updated",
    extra={
        "user_id": user.id,
        "fields_updated": ["bio", "languages"]
    }
)

# Error log
logger.error(
    "Failed to process payment",
    extra={
        "booking_id": booking.id,
        "amount": amount,
        "error_type": "stripe_error"
    },
    exc_info=True  # Include stack trace
)
```

### Using Retry Decorators

```python
from app.utils.retry_utils import retry_openai, retry_stripe

@retry_openai
async def generate_embeddings(text: str):
    response = await openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

@retry_stripe
def create_checkout_session(amount: int):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': 'Coaching Session'},
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        mode='payment',
    )
    return session
```

## Environment Configuration

Add to `.env`:

```bash
# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENVIRONMENT=production  # development, staging, production
```

## CloudWatch Integration

For production deployment, logs are automatically formatted as JSON and can be sent to AWS CloudWatch:

1. Configure CloudWatch log group in AWS
2. Update ECS task definition to send logs to CloudWatch
3. Set up log retention policies (e.g., 30 days)
4. Create CloudWatch alarms for error rates and latency

## Monitoring and Alerts

Recommended CloudWatch alarms:

- **Error Rate**: Alert when 5xx errors exceed 5% for 5 minutes
- **API Latency**: Alert when p95 latency exceeds 500ms
- **Database Errors**: Alert on any SQLAlchemy errors
- **External Service Failures**: Alert on OpenAI/Stripe failures

## Dependencies

Added to `requirements.txt`:
- `python-json-logger==2.0.7` - JSON log formatting

## Files Created

1. `app/exceptions.py` - Custom exception classes
2. `app/utils/retry_utils.py` - Retry logic for external services
3. `app/middleware/request_id_middleware.py` - Request ID generation
4. `app/middleware/error_handler.py` - Global exception handlers
5. `app/utils/logging_config.py` - Structured logging configuration
6. `app/middleware/logging_middleware.py` - Request/response logging

## Files Modified

1. `app/main.py` - Integrated error handling and logging
2. `requirements.txt` - Added python-json-logger dependency
