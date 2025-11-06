# Integration Testing Guide

This guide provides instructions for running comprehensive integration tests on the CultureBridge platform.

## Overview

Integration testing verifies that all components of the system work together correctly, including:
- Backend API endpoints
- Database operations
- External service integrations (OpenAI, Stripe, AWS S3, Email)
- Frontend-backend communication
- End-to-end user workflows

## Prerequisites

### For Staging Environment Testing

- Access to staging environment
- Staging API URL
- Staging frontend URL
- Test credentials for all user roles
- Test API keys for external services

### For Local Testing

- Docker and Docker Compose installed
- All services running locally
- Test database populated
- External service test accounts configured

## Test Execution

### 1. Smoke Tests

Smoke tests verify critical functionality is working.

**Using PowerShell (Windows)**:
```powershell
cd scripts
.\run_smoke_tests.ps1 -ApiUrl "https://staging-api.culturebridge.com" -FrontendUrl "https://staging.culturebridge.com"
```

**Using Bash (macOS/Linux)**:
```bash
cd scripts
chmod +x run_smoke_tests.sh
./run_smoke_tests.sh
```

**Expected Results**:
- All 11 tests should pass
- Health check returns 200
- Authentication flow works
- Basic CRUD operations succeed

### 2. Unit and Integration Tests

Run the full test suite:

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Run only integration tests
pytest tests/integration/

# Run smoke tests specifically
pytest tests/integration/test_smoke.py -v

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

**Expected Results**:
- All tests pass
- Code coverage > 80%
- No critical warnings

### 3. Load Testing

Load testing verifies the system can handle expected traffic.

#### Setup

```bash
cd backend/tests/load
pip install locust
```

#### Run Load Tests

**Interactive Mode** (with web UI):
```bash
locust -f locustfile.py --host=https://staging-api.culturebridge.com
```

Then open http://localhost:8089 and configure:
- Number of users: 100
- Spawn rate: 10 users/second
- Run time: 5 minutes

**Headless Mode** (automated):
```bash
locust -f locustfile.py \
  --host=https://staging-api.culturebridge.com \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless \
  --html=load_test_report.html
```

**Expected Results**:
- System handles 100 concurrent users
- Average response time < 250ms
- P95 response time < 500ms
- P99 response time < 1000ms
- Error rate < 1%
- No timeouts or connection errors

#### Interpreting Results

Good indicators:
- ✓ Response times stable throughout test
- ✓ No increase in error rate over time
- ✓ CPU and memory usage within limits
- ✓ Database connections stable

Warning signs:
- ⚠ Response times increasing over time
- ⚠ Error rate > 1%
- ⚠ Memory usage growing continuously
- ⚠ Database connection pool exhausted

### 4. External Service Integration Tests

#### OpenAI Integration

Test AI matching functionality:

```bash
cd backend
python -c "
from app.services.matching_service import MatchingService
from app.database import SessionLocal

db = SessionLocal()
service = MatchingService(db)

# Test with sample client data
client_data = {
    'target_countries': ['Spain'],
    'goals': ['career_transition'],
    'languages': ['English', 'Spanish'],
    'budget_max': 150
}

try:
    matches = service.generate_matches('test_client_id', client_data)
    print(f'✓ OpenAI integration working: {len(matches)} matches generated')
except Exception as e:
    print(f'✗ OpenAI integration failed: {e}')
"
```

**Expected Results**:
- Matches generated successfully
- Match scores between 0-100
- Response time < 10 seconds
- No API errors

#### Stripe Integration

Test payment processing:

```bash
# Use Stripe CLI to test webhooks
stripe listen --forward-to localhost:8000/payment/webhook

# In another terminal, trigger test payment
stripe trigger payment_intent.succeeded
```

**Test Cards**:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Requires authentication: `4000 0025 0000 3155`

**Expected Results**:
- Checkout session created
- Payment processed successfully
- Webhook received and processed
- Booking status updated
- Confirmation emails sent

#### AWS S3 Integration

Test file uploads:

```bash
cd backend
python -c "
from app.utils.s3_utils import upload_file
import io

# Create test file
test_file = io.BytesIO(b'Test file content')
test_file.name = 'test.txt'

try:
    url = upload_file(test_file, 'test-uploads')
    print(f'✓ S3 upload successful: {url}')
except Exception as e:
    print(f'✗ S3 upload failed: {e}')
"
```

**Expected Results**:
- File uploaded successfully
- URL returned
- File accessible via URL
- Proper permissions set

#### Email Service Integration

Test email sending:

```bash
cd backend
python -c "
from app.services.email_service import EmailService

service = EmailService()

try:
    service.send_booking_confirmation(
        to_email='test@example.com',
        client_name='Test Client',
        coach_name='Test Coach',
        session_datetime='2025-12-01T14:00:00Z'
    )
    print('✓ Email sent successfully')
except Exception as e:
    print(f'✗ Email sending failed: {e}')
"
```

**Expected Results**:
- Email sent without errors
- Email received in inbox (check spam)
- Email content formatted correctly
- Links in email work

### 5. End-to-End User Journey Tests

#### Client Journey

Manual testing steps:

1. **Sign Up**
   - Navigate to `/auth/signup`
   - Enter email, password, select "Client"
   - Verify account created
   - Check confirmation email

2. **Complete Profile**
   - Navigate to `/profile/client`
   - Fill in personal information
   - Complete 20-question quiz
   - Upload profile photo
   - Save profile

3. **Find Coaches**
   - Navigate to `/coaches`
   - Apply filters (language, country, rate)
   - View coach profiles
   - Check match scores

4. **Request Matches**
   - Navigate to `/match`
   - View AI-generated matches
   - Verify match scores and reasons
   - Check that results are cached

5. **Book Session**
   - Select a coach
   - Choose available time slot
   - Create booking
   - Verify booking status "pending"

6. **Complete Payment**
   - Initiate checkout
   - Redirected to Stripe
   - Enter test card: 4242 4242 4242 4242
   - Complete payment
   - Verify booking status "confirmed"
   - Check confirmation email

7. **View Booking History**
   - Navigate to `/booking/history`
   - Verify booking appears
   - Check booking details

8. **Participate in Community**
   - Navigate to `/community`
   - Create a post
   - Comment on existing post
   - Upvote a post
   - Browse resources
   - Bookmark a resource

#### Coach Journey

Manual testing steps:

1. **Sign Up**
   - Navigate to `/auth/signup`
   - Enter email, password, select "Coach"
   - Verify account created

2. **Complete Profile**
   - Navigate to `/profile/coach`
   - Fill in bio and experience
   - Add expertise areas
   - Set languages and countries
   - Set hourly rate
   - Configure availability
   - Upload profile photo
   - Save profile

3. **Receive Booking**
   - Wait for client booking (or create test booking)
   - Check email notification
   - View booking in dashboard

4. **Confirm Booking**
   - Navigate to booking details
   - Add meeting link (Zoom/Google Meet)
   - Confirm booking
   - Verify client receives confirmation

5. **Connect Calendar**
   - Navigate to calendar settings
   - Connect Google Calendar or Outlook
   - Verify booking synced to calendar

6. **View Booking History**
   - Navigate to `/booking/history`
   - Filter by status
   - View completed sessions

7. **Participate in Community**
   - Create posts
   - Share resources
   - Engage with clients

#### Admin Journey

Manual testing steps:

1. **Log In**
   - Navigate to `/auth/login`
   - Enter admin credentials
   - Verify redirected to admin dashboard

2. **View Analytics**
   - Navigate to `/admin`
   - Verify metrics displayed:
     - Total users
     - Active sessions
     - Revenue
     - Community stats
   - Change date range
   - Verify data updates

3. **Manage Users**
   - Navigate to `/admin/users`
   - Search for user
   - View user details
   - Update user role
   - Activate/deactivate user
   - Verify changes saved

4. **View Bookings**
   - Navigate to `/admin/bookings`
   - Filter by status
   - Filter by date range
   - View booking details

5. **Moderate Content**
   - Navigate to `/admin/moderation`
   - View flagged posts
   - Delete inappropriate content
   - Verify deletion cascades

6. **Export Reports**
   - Navigate to `/admin/revenue`
   - Select date range
   - Export CSV
   - Verify data accuracy

### 6. Performance Monitoring

During testing, monitor:

#### Application Metrics

```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s https://staging-api.culturebridge.com/health

# Create curl-format.txt:
echo "time_namelookup:  %{time_namelookup}\n\
time_connect:  %{time_connect}\n\
time_appconnect:  %{time_appconnect}\n\
time_pretransfer:  %{time_pretransfer}\n\
time_redirect:  %{time_redirect}\n\
time_starttransfer:  %{time_starttransfer}\n\
----------\n\
time_total:  %{time_total}\n" > curl-format.txt
```

#### Database Performance

```sql
-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check connection count
SELECT count(*) FROM pg_stat_activity;

-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### Cache Performance

```bash
# Check Redis stats
redis-cli INFO stats

# Check cache hit rate
redis-cli INFO stats | grep keyspace_hits
redis-cli INFO stats | grep keyspace_misses
```

### 7. Security Testing

#### Authentication Tests

```bash
# Test without token
curl -X GET https://staging-api.culturebridge.com/profile

# Test with invalid token
curl -X GET https://staging-api.culturebridge.com/profile \
  -H "Authorization: Bearer invalid_token"

# Test with expired token
curl -X GET https://staging-api.culturebridge.com/profile \
  -H "Authorization: Bearer expired_token"
```

#### Authorization Tests

```bash
# Test client accessing admin endpoint
curl -X GET https://staging-api.culturebridge.com/admin/metrics \
  -H "Authorization: Bearer client_token"

# Test accessing other user's data
curl -X GET https://staging-api.culturebridge.com/booking/other_user_id \
  -H "Authorization: Bearer user_token"
```

#### Input Validation Tests

```bash
# Test SQL injection
curl -X POST https://staging-api.culturebridge.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com OR 1=1--","password":"test"}'

# Test XSS
curl -X POST https://staging-api.culturebridge.com/community/posts \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{"title":"<script>alert(1)</script>","content":"test"}'
```

**Expected Results**:
- All malicious inputs rejected
- Proper error messages returned
- No sensitive information leaked

## Test Results Documentation

### Recording Results

Use the testing checklist: `docs/TESTING_CHECKLIST.md`

For each test:
- [ ] Mark as complete
- Document any issues
- Note workarounds
- Record performance metrics

### Generating Reports

```bash
# Generate test coverage report
cd backend
pytest --cov=app --cov-report=html
# Report saved to htmlcov/index.html

# Generate load test report
cd tests/load
locust -f locustfile.py --headless --html=report.html
# Report saved to report.html
```

### Issue Tracking

For any failures:
1. Document the issue
2. Include steps to reproduce
3. Attach logs and screenshots
4. Assign severity (Critical/High/Medium/Low)
5. Create GitHub issue if needed

## Troubleshooting

### Tests Failing

1. **Check service status**:
   ```bash
   docker-compose ps
   curl https://staging-api.culturebridge.com/health
   ```

2. **Check logs**:
   ```bash
   docker-compose logs backend --tail=100
   docker-compose logs frontend --tail=100
   ```

3. **Verify environment variables**:
   ```bash
   docker-compose exec backend env | grep -E "DATABASE|REDIS|OPENAI|STRIPE"
   ```

4. **Reset test data**:
   ```bash
   docker-compose down -v
   docker-compose up -d
   docker-compose exec backend alembic upgrade head
   ```

### Performance Issues

1. **Check resource usage**:
   ```bash
   docker stats
   ```

2. **Check database performance**:
   ```sql
   SELECT * FROM pg_stat_activity WHERE state = 'active';
   ```

3. **Check cache hit rate**:
   ```bash
   redis-cli INFO stats
   ```

### External Service Issues

1. **OpenAI**: Check API key and credits
2. **Stripe**: Verify test mode enabled
3. **AWS S3**: Check bucket permissions
4. **Email**: Verify SMTP credentials

## Sign-Off

After completing all tests:

1. Review test results
2. Document any known issues
3. Get approval from:
   - QA Team
   - Development Team
   - Product Team

4. Update deployment checklist
5. Proceed to production deployment

## Additional Resources

- [Testing Checklist](TESTING_CHECKLIST.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Deployment Guide](DEPLOYMENT.md)
- [API Documentation](../backend/API_DOCUMENTATION.md)
