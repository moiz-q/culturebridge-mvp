# Security and Performance Quick Reference

Quick reference guide for developers working with CultureBridge API security and performance features.

## Input Validation

```python
from app.utils.input_validation import InputValidator

# Sanitize string input
clean_text = InputValidator.sanitize_string(user_input, max_length=1000)

# Validate email
if not InputValidator.validate_email(email):
    raise ValidationException("Invalid email")

# Validate URL
if not InputValidator.validate_url(url, allowed_schemes=['https']):
    raise ValidationException("Invalid URL")

# Sanitize entire dictionary
clean_data = InputValidator.sanitize_dict(request_data)

# Validate file upload
is_valid, error = InputValidator.validate_file_upload(
    filename="photo.jpg",
    content_type="image/jpeg",
    file_size=2_000_000,  # 2MB
    allowed_extensions=['jpg', 'jpeg', 'png'],
    max_size_mb=5
)
```

## Response Caching

```python
from fastapi import Request
from app.utils.response_cache import cache_response, invalidate_endpoint_cache

# Cache GET endpoint responses
@router.get("/coaches")
@cache_response(ttl_seconds=300, key_prefix="coaches_list")
async def get_coaches(request: Request, ...):
    return coaches

# Invalidate cache when data changes
@router.put("/coaches/{id}")
async def update_coach(...):
    # Update logic
    invalidate_endpoint_cache("coaches_list")
    return updated_coach
```

## Metrics Tracking

```python
from app.utils.metrics import track_latency, track_external_call, metrics_collector

# Track endpoint latency (automatic with decorator)
@track_latency("get_coaches")
async def get_coaches():
    return coaches

# Track external service calls
@track_external_call("OpenAI", "generate_embeddings")
async def call_openai():
    return embeddings

# Manual metric recording
metrics_collector.record_api_latency(
    endpoint="/coaches",
    method="GET",
    latency_ms=150.5,
    status_code=200
)

metrics_collector.record_cache_hit_rate(
    cache_type="match_results",
    hit=True
)
```

## Rate Limiting

Rate limiting is automatic via middleware:
- 100 requests per minute per user
- Identified by JWT token or IP address
- Returns 429 when exceeded

To check rate limit status:
```python
# Rate limit info is in Redis
# Key format: rate_limit:user:{user_id} or rate_limit:ip:{ip_address}
```

## CSRF Protection

Frontend integration:
```javascript
// Get CSRF token from cookie
const csrfToken = document.cookie
  .split('; ')
  .find(row => row.startsWith('csrf_token='))
  ?.split('=')[1];

// Include in POST/PUT/PATCH/DELETE requests
fetch('/api/booking', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'X-CSRF-Token': csrfToken,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
});
```

## Health Checks

```bash
# Comprehensive health check
curl http://localhost:8000/health

# Liveness probe (Kubernetes)
curl http://localhost:8000/health/live

# Readiness probe (Kubernetes)
curl http://localhost:8000/health/ready
```

## Security Headers

All responses automatically include:
- Content-Security-Policy
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy

No action required - handled by middleware.

## Database Best Practices

```python
# Use pagination for all list queries
def get_all(self, skip: int = 0, limit: int = 20):
    return self.db.query(Model)\
        .offset(skip)\
        .limit(limit)\
        .all()

# Use indexes for filtered queries
# Indexes already created for:
# - users.email
# - bookings.client_id, coach_id, session_datetime
# - posts.created_at
# - coach_profiles.languages (GIN index)
```

## Common Patterns

### Protected Endpoint with Caching
```python
@router.get("/coaches", response_model=List[CoachResponse])
@cache_response(ttl_seconds=300)
async def get_coaches(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Endpoint logic
    return coaches
```

### Input Validation in Endpoint
```python
@router.post("/profile/photo")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Validate file
    is_valid, error = InputValidator.validate_file_upload(
        filename=file.filename,
        content_type=file.content_type,
        file_size=len(await file.read()),
        allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
        max_size_mb=5
    )
    
    if not is_valid:
        raise ValidationException(error)
    
    # Upload logic
    return {"url": photo_url}
```

### External Service Call with Metrics
```python
@track_external_call("Stripe", "create_checkout_session")
async def create_stripe_session(amount: float):
    try:
        session = stripe.checkout.Session.create(...)
        return session
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise ServiceUnavailableException("Payment service unavailable")
```

## Testing Security Features

### Test Rate Limiting
```python
# pytest
async def test_rate_limiting(client, auth_token):
    # Send 101 requests
    for i in range(101):
        response = await client.get(
            "/coaches",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    # Last request should be rate limited
    assert response.status_code == 429
```

### Test CSRF Protection
```python
async def test_csrf_required(client, auth_token):
    # POST without CSRF token should fail
    response = await client.post(
        "/booking",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"coach_id": "123", "session_datetime": "2025-11-10T14:00:00Z"}
    )
    assert response.status_code == 403
```

### Test Input Validation
```python
def test_xss_detection():
    malicious_input = "<script>alert('xss')</script>"
    assert InputValidator.detect_xss(malicious_input) == True
    
    clean_input = InputValidator.sanitize_string(malicious_input)
    assert "<script>" not in clean_input
```

## Environment Variables

```bash
# Required for security features
CORS_ORIGINS=https://culturebridge.com
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key

# Required for monitoring
AWS_REGION=us-east-1
ENVIRONMENT=production

# Optional
RATE_LIMIT_PER_MINUTE=100
CACHE_TTL_SECONDS=300
```

## Troubleshooting

### "Rate limit exceeded" errors
- Check Redis connectivity
- Verify user is not making excessive requests
- Consider whitelisting specific users/IPs

### "CSRF token missing" errors
- Ensure frontend includes X-CSRF-Token header
- Check that csrf_token cookie is set
- Verify cookie is not expired

### Cache not working
- Check Redis is running: `redis-cli ping`
- Verify REDIS_URL is correct
- Check cache TTL settings

### Metrics not appearing
- Verify AWS credentials are configured
- Check IAM permissions for CloudWatch
- Ensure ENVIRONMENT=production

## Security Checklist

Before deploying to production:

- [ ] Set strong JWT_SECRET_KEY
- [ ] Configure specific CORS_ORIGINS (not *)
- [ ] Enable HTTPS only
- [ ] Set up Redis for rate limiting
- [ ] Configure CloudWatch alarms
- [ ] Review and test input validation
- [ ] Enable CSRF protection
- [ ] Test rate limiting
- [ ] Set up monitoring dashboard
- [ ] Configure SNS for alerts
- [ ] Review security headers
- [ ] Test health check endpoints
- [ ] Enable response compression
- [ ] Verify database indexes
- [ ] Test cache invalidation

## Performance Checklist

- [ ] Enable response caching for GET endpoints
- [ ] Use pagination for all list endpoints
- [ ] Add database indexes for filtered queries
- [ ] Enable GZip compression
- [ ] Monitor API latency metrics
- [ ] Optimize slow database queries
- [ ] Configure connection pooling
- [ ] Set appropriate cache TTLs
- [ ] Use SSG for static pages
- [ ] Monitor cache hit rates

## Support

For questions or issues:
- Check [SECURITY_PERFORMANCE_IMPLEMENTATION.md](SECURITY_PERFORMANCE_IMPLEMENTATION.md)
- Review [MONITORING_SETUP.md](MONITORING_SETUP.md)
- Check CloudWatch metrics and logs
- Contact DevOps team for infrastructure issues
