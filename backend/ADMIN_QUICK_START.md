# Admin API Quick Start Guide

This guide helps you quickly get started with the Admin API endpoints.

**Requirements:** 7.1, 7.2, 7.3, 7.4, 7.5

## Prerequisites

1. Admin user account created
2. Valid JWT token with admin role
3. API running on `http://localhost:8000`

## Quick Examples

### 1. Get Platform Metrics

View platform analytics for the last 30 days:

```bash
curl -X GET "http://localhost:8000/admin/metrics?days=30" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 2. List All Users

Get first 20 users:

```bash
curl -X GET "http://localhost:8000/admin/users?skip=0&limit=20" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Filter by role:

```bash
curl -X GET "http://localhost:8000/admin/users?role=client" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Search by email:

```bash
curl -X GET "http://localhost:8000/admin/users?email=john" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 3. View User Activity

Get detailed activity for a specific user:

```bash
curl -X GET "http://localhost:8000/admin/users/USER_UUID" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 4. Update User

Change user role to coach:

```bash
curl -X PATCH "http://localhost:8000/admin/users/USER_UUID" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "coach"
  }'
```

Deactivate user:

```bash
curl -X PATCH "http://localhost:8000/admin/users/USER_UUID" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

### 5. Delete User

Delete a user and all associated data:

```bash
curl -X DELETE "http://localhost:8000/admin/users/USER_UUID" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 6. List Bookings

Get all bookings:

```bash
curl -X GET "http://localhost:8000/admin/bookings?skip=0&limit=20" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Filter by client:

```bash
curl -X GET "http://localhost:8000/admin/bookings?client_id=CLIENT_UUID" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Filter by status:

```bash
curl -X GET "http://localhost:8000/admin/bookings?status=confirmed" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 7. Delete Forum Post

Remove inappropriate content:

```bash
curl -X DELETE "http://localhost:8000/admin/posts/POST_UUID" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 8. Get Revenue Report

Daily revenue for October 2025:

```bash
curl -X GET "http://localhost:8000/admin/revenue?start_date=2025-10-01T00:00:00Z&end_date=2025-10-31T23:59:59Z&group_by=day" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Weekly revenue:

```bash
curl -X GET "http://localhost:8000/admin/revenue?start_date=2025-10-01T00:00:00Z&end_date=2025-10-31T23:59:59Z&group_by=week" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 9. Export Users to CSV

Export all active clients:

```bash
curl -X GET "http://localhost:8000/admin/export/users?role=client&is_active=true" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -o users_export.csv
```

### 10. Export Bookings to CSV

Export bookings for a date range:

```bash
curl -X GET "http://localhost:8000/admin/export/bookings?start_date=2025-10-01T00:00:00Z&end_date=2025-10-31T23:59:59Z" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -o bookings_export.csv
```

### 11. Export Revenue to CSV

Export revenue data:

```bash
curl -X GET "http://localhost:8000/admin/export/revenue?start_date=2025-10-01T00:00:00Z&end_date=2025-10-31T23:59:59Z" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -o revenue_export.csv
```

## Python Examples

### Using requests library

```python
import requests
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = "your_admin_token_here"

headers = {
    "Authorization": f"Bearer {ADMIN_TOKEN}"
}

# Get platform metrics
response = requests.get(
    f"{BASE_URL}/admin/metrics",
    params={"days": 30},
    headers=headers
)
metrics = response.json()
print(f"Total users: {metrics['total_users']}")
print(f"Total revenue: ${metrics['total_revenue_usd']}")

# List users
response = requests.get(
    f"{BASE_URL}/admin/users",
    params={"role": "client", "limit": 50},
    headers=headers
)
users_data = response.json()
print(f"Found {users_data['total']} clients")

# Update user
user_id = "123e4567-e89b-12d3-a456-426614174000"
response = requests.patch(
    f"{BASE_URL}/admin/users/{user_id}",
    json={"email_verified": True},
    headers=headers
)
updated_user = response.json()
print(f"Updated user: {updated_user['email']}")

# Get revenue report
end_date = datetime.utcnow()
start_date = end_date - timedelta(days=30)

response = requests.get(
    f"{BASE_URL}/admin/revenue",
    params={
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "group_by": "day"
    },
    headers=headers
)
revenue_report = response.json()
print(f"Revenue data points: {len(revenue_report['data'])}")

# Export users to CSV
response = requests.get(
    f"{BASE_URL}/admin/export/users",
    params={"is_active": True},
    headers=headers
)
with open("users_export.csv", "w") as f:
    f.write(response.text)
print("Users exported to users_export.csv")
```

## Common Use Cases

### 1. Daily Admin Dashboard Check

```bash
# Get today's metrics
curl -X GET "http://localhost:8000/admin/metrics?days=1" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 2. User Management

```bash
# Find user by email
curl -X GET "http://localhost:8000/admin/users?email=user@example.com" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# View their activity
curl -X GET "http://localhost:8000/admin/users/USER_UUID" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Update if needed
curl -X PATCH "http://localhost:8000/admin/users/USER_UUID" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

### 3. Content Moderation

```bash
# List recent posts (via community endpoint)
curl -X GET "http://localhost:8000/community/posts?skip=0&limit=20" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Delete inappropriate post
curl -X DELETE "http://localhost:8000/admin/posts/POST_UUID" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 4. Monthly Reporting

```bash
# Get monthly metrics
curl -X GET "http://localhost:8000/admin/metrics?days=30" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Get monthly revenue report
curl -X GET "http://localhost:8000/admin/revenue?start_date=2025-10-01T00:00:00Z&end_date=2025-10-31T23:59:59Z&group_by=month" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Export data for analysis
curl -X GET "http://localhost:8000/admin/export/users" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -o users_october.csv

curl -X GET "http://localhost:8000/admin/export/bookings?start_date=2025-10-01T00:00:00Z&end_date=2025-10-31T23:59:59Z" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -o bookings_october.csv

curl -X GET "http://localhost:8000/admin/export/revenue?start_date=2025-10-01T00:00:00Z&end_date=2025-10-31T23:59:59Z" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -o revenue_october.csv
```

## Testing with Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Click "Authorize" button
3. Enter your admin JWT token: `Bearer YOUR_TOKEN`
4. Click "Authorize"
5. Expand any admin endpoint
6. Click "Try it out"
7. Fill in parameters
8. Click "Execute"

## Error Handling

All endpoints return standard error responses:

```python
try:
    response = requests.get(
        f"{BASE_URL}/admin/users/{user_id}",
        headers=headers
    )
    response.raise_for_status()
    user_activity = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("User not found")
    elif e.response.status_code == 403:
        print("Insufficient permissions")
    else:
        print(f"Error: {e.response.json()['detail']}")
```

## Security Best Practices

1. **Never commit tokens**: Store admin tokens in environment variables
2. **Use HTTPS**: Always use HTTPS in production
3. **Rotate tokens**: Regularly rotate admin JWT tokens
4. **Audit logs**: Review audit logs regularly
5. **Least privilege**: Only grant admin access when necessary
6. **Monitor usage**: Track admin API usage for anomalies

## Next Steps

- Review [ADMIN_API_REFERENCE.md](./ADMIN_API_REFERENCE.md) for detailed endpoint documentation
- Review [ADMIN_IMPLEMENTATION.md](./ADMIN_IMPLEMENTATION.md) for implementation details
- Set up monitoring and alerting for admin actions
- Create admin dashboard UI using these endpoints
