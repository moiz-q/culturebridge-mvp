# Admin API Testing Checklist

Use this checklist to verify the admin API implementation.

## Prerequisites

- [ ] Backend server is running
- [ ] Database is set up with migrations applied
- [ ] Admin user account exists
- [ ] Admin JWT token is available

## Endpoint Testing

### 1. Platform Metrics (GET /admin/metrics)

- [ ] Returns metrics for default 30 days
- [ ] Accepts custom days parameter (1-365)
- [ ] Returns all required fields:
  - [ ] total_users
  - [ ] total_clients
  - [ ] total_coaches
  - [ ] new_users
  - [ ] active_sessions
  - [ ] session_volume
  - [ ] total_revenue_usd
  - [ ] revenue_by_currency
  - [ ] avg_session_duration_minutes
  - [ ] booking_status_breakdown
- [ ] Requires admin authentication
- [ ] Returns 403 for non-admin users

### 2. List Users (GET /admin/users)

- [ ] Returns paginated user list
- [ ] Default pagination works (skip=0, limit=20)
- [ ] Custom pagination works
- [ ] Filter by role works (client, coach, admin)
- [ ] Filter by is_active works (true/false)
- [ ] Filter by email works (partial match)
- [ ] Returns total count
- [ ] Requires admin authentication

### 3. Get User Activity (GET /admin/users/{user_id})

- [ ] Returns user activity for valid user_id
- [ ] Returns 404 for non-existent user
- [ ] Includes booking statistics
- [ ] Includes payment totals
- [ ] Includes community activity
- [ ] Requires admin authentication

### 4. Update User (PATCH /admin/users/{user_id})

- [ ] Updates user role
- [ ] Updates is_active status
- [ ] Updates email_verified status
- [ ] Accepts partial updates (only provided fields)
- [ ] Returns updated user data
- [ ] Returns 404 for non-existent user
- [ ] Requires admin authentication

### 5. Delete User (DELETE /admin/users/{user_id})

- [ ] Deletes user successfully
- [ ] Returns 204 No Content
- [ ] Cascades to related records
- [ ] Prevents self-deletion (400 error)
- [ ] Returns 404 for non-existent user
- [ ] Requires admin authentication

### 6. List Bookings (GET /admin/bookings)

- [ ] Returns paginated booking list
- [ ] Default pagination works
- [ ] Filter by client_id works
- [ ] Filter by coach_id works
- [ ] Filter by status works
- [ ] Includes client and coach emails
- [ ] Returns total count
- [ ] Requires admin authentication

### 7. Delete Post (DELETE /admin/posts/{post_id})

- [ ] Deletes post successfully
- [ ] Returns 204 No Content
- [ ] Cascades to comments
- [ ] Returns 404 for non-existent post
- [ ] Requires admin authentication

### 8. Get Revenue Report (GET /admin/revenue)

- [ ] Returns revenue data for date range
- [ ] Group by day works
- [ ] Group by week works
- [ ] Group by month works
- [ ] Includes multi-currency data
- [ ] Includes transaction counts
- [ ] Requires start_date and end_date
- [ ] Requires admin authentication

### 9. Export Users CSV (GET /admin/export/users)

- [ ] Returns CSV file
- [ ] Correct Content-Type (text/csv)
- [ ] Includes Content-Disposition header
- [ ] Filter by role works
- [ ] Filter by is_active works
- [ ] CSV format is correct
- [ ] All user fields included
- [ ] Requires admin authentication

### 10. Export Bookings CSV (GET /admin/export/bookings)

- [ ] Returns CSV file
- [ ] Correct Content-Type (text/csv)
- [ ] Includes Content-Disposition header
- [ ] Date range filter works
- [ ] CSV format is correct
- [ ] All booking fields included
- [ ] Includes client and coach emails
- [ ] Requires admin authentication

### 11. Export Revenue CSV (GET /admin/export/revenue)

- [ ] Returns CSV file
- [ ] Correct Content-Type (text/csv)
- [ ] Includes Content-Disposition header
- [ ] Date range filter works
- [ ] CSV format is correct
- [ ] All payment fields included
- [ ] Requires admin authentication

## Security Testing

- [ ] All endpoints require authentication
- [ ] All endpoints require admin role
- [ ] Non-admin users get 403 Forbidden
- [ ] Unauthenticated requests get 401 Unauthorized
- [ ] Admin cannot delete own account
- [ ] Input validation works (invalid UUIDs, dates, etc.)
- [ ] SQL injection protection works
- [ ] XSS protection works

## Audit Logging

- [ ] Admin actions are logged
- [ ] Logs include admin_id
- [ ] Logs include action type
- [ ] Logs include target type and ID
- [ ] Logs include additional details
- [ ] Logs include timestamp

## Performance Testing

- [ ] Metrics endpoint responds < 1 second
- [ ] List endpoints with pagination respond < 500ms
- [ ] CSV exports complete in reasonable time
- [ ] Large datasets don't cause timeouts
- [ ] Database queries are optimized

## Error Handling

- [ ] 404 errors return proper message
- [ ] 400 errors return proper message
- [ ] 403 errors return proper message
- [ ] 422 validation errors return details
- [ ] 500 errors are handled gracefully

## Documentation

- [ ] Swagger UI shows all endpoints
- [ ] Endpoint descriptions are clear
- [ ] Request/response examples are accurate
- [ ] Parameter descriptions are helpful
- [ ] Error responses are documented

## Integration Testing

- [ ] Admin router is registered in main.py
- [ ] All imports work correctly
- [ ] Database connections work
- [ ] Service layer integration works
- [ ] Schema validation works

## Sample Test Commands

```bash
# Set your admin token
export ADMIN_TOKEN="your_admin_token_here"
export BASE_URL="http://localhost:8000"

# Test metrics
curl -X GET "$BASE_URL/admin/metrics?days=30" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Test list users
curl -X GET "$BASE_URL/admin/users?limit=5" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Test user activity (replace USER_ID)
curl -X GET "$BASE_URL/admin/users/USER_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Test update user (replace USER_ID)
curl -X PATCH "$BASE_URL/admin/users/USER_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_verified": true}'

# Test list bookings
curl -X GET "$BASE_URL/admin/bookings?limit=5" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Test revenue report
curl -X GET "$BASE_URL/admin/revenue?start_date=2025-10-01T00:00:00Z&end_date=2025-10-31T23:59:59Z&group_by=day" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Test CSV export
curl -X GET "$BASE_URL/admin/export/users?is_active=true" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -o users_export.csv

# Test unauthorized access (should fail with 403)
curl -X GET "$BASE_URL/admin/metrics" \
  -H "Authorization: Bearer CLIENT_TOKEN"
```

## Notes

- Replace `USER_ID`, `POST_ID`, etc. with actual UUIDs from your database
- Ensure test data exists before running tests
- Check audit logs after each admin action
- Verify CSV files open correctly in spreadsheet software
- Test with different admin users to verify audit logging
