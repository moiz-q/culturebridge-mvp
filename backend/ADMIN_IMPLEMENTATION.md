# Admin Implementation Guide

This document describes the implementation details of the Admin API endpoints.

**Requirements:** 7.1, 7.2, 7.3, 7.4, 7.5

## Architecture Overview

The admin functionality is implemented using a three-layer architecture:

1. **Router Layer** (`app/routers/admin.py`): FastAPI endpoints with request/response handling
2. **Service Layer** (`app/services/admin_service.py`): Business logic and analytics calculations
3. **Repository Layer**: Data access through SQLAlchemy ORM

## Components

### 1. Admin Router (`app/routers/admin.py`)

The router defines all admin API endpoints with:
- Role-based access control (admin only)
- Request validation using Pydantic schemas
- Response formatting
- Error handling
- Audit logging integration

**Key Features:**
- All endpoints require admin role via `require_role([UserRole.ADMIN])` dependency
- Consistent error responses
- Pagination support for list endpoints
- CSV export functionality
- Query parameter validation

### 2. Admin Service (`app/services/admin_service.py`)

The service layer contains business logic for:
- Platform metrics calculation
- Revenue reporting and aggregation
- User activity tracking
- CSV export generation
- Audit logging

**Key Methods:**

#### `get_platform_metrics(days: int) -> Dict[str, Any]`
Calculates platform-wide metrics including:
- Total users by role
- New users in period
- Active sessions and session volume
- Revenue by currency
- Average session duration
- Booking status breakdown

#### `get_revenue_report(start_date, end_date, group_by) -> List[Dict]`
Generates revenue reports with:
- Flexible date range
- Grouping by day/week/month
- Multi-currency support
- Transaction counts

#### `export_users_csv(filters) -> str`
Exports user data to CSV format with optional filters.

#### `export_bookings_csv(start_date, end_date) -> str`
Exports booking data to CSV format with date range filters.

#### `export_revenue_csv(start_date, end_date) -> str`
Exports payment/revenue data to CSV format.

#### `log_admin_action(admin_id, action, target_type, target_id, details)`
Logs all admin actions for audit purposes.

#### `get_user_activity_history(user_id) -> Dict`
Retrieves comprehensive activity history for a user including:
- Booking statistics
- Payment totals
- Community engagement

### 3. Schemas (`app/schemas/admin.py`)

Pydantic models for request/response validation:

- `PlatformMetricsResponse`: Platform analytics data
- `UserListResponse`: Paginated user list
- `UserListItem`: Individual user data
- `UserUpdateRequest`: User update payload
- `UserActivityResponse`: User activity history
- `BookingListResponse`: Paginated booking list
- `BookingListItem`: Individual booking data
- `RevenueReportResponse`: Revenue report data
- `RevenueDataPoint`: Single revenue data point

## Database Queries

### Metrics Calculation

The service uses efficient SQL queries with aggregations:

```python
# Total users by role
total_clients = db.query(func.count(User.id)).filter(
    User.role == UserRole.CLIENT,
    User.is_active == True
).scalar()

# Revenue aggregation
revenue_query = db.query(
    func.sum(Payment.amount).label('total'),
    Payment.currency
).join(Booking).filter(
    Payment.status == PaymentStatus.SUCCEEDED,
    Booking.session_datetime >= start_date
).group_by(Payment.currency).all()
```

### Pagination

All list endpoints use consistent pagination:

```python
query = db.query(Model)
# Apply filters...
total = query.count()
items = query.order_by(Model.created_at.desc()).offset(skip).limit(limit).all()
```

## Security Implementation

### Role-Based Access Control

All admin endpoints use the `require_role` dependency:

```python
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_role([UserRole.ADMIN]))]
)
```

This ensures:
1. User is authenticated (valid JWT)
2. User has admin role
3. Automatic 403 response for non-admins

### Self-Protection

Admins cannot delete their own accounts:

```python
if user_id == current_user.id:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Cannot delete your own account"
    )
```

### Audit Logging

All admin actions are logged:

```python
admin_service.log_admin_action(
    admin_id=current_user.id,
    action="delete_user",
    target_type="user",
    target_id=user_id,
    details={"email": user.email, "role": user.role.value}
)
```

## CSV Export Implementation

CSV exports use Python's `csv` module with `io.StringIO`:

```python
output = io.StringIO()
writer = csv.writer(output)

# Write header
writer.writerow(['ID', 'Email', 'Role', ...])

# Write data rows
for user in users:
    writer.writerow([str(user.id), user.email, user.role.value, ...])

return output.getvalue()
```

Response includes proper headers:

```python
return Response(
    content=csv_data,
    media_type="text/csv",
    headers={
        "Content-Disposition": f"attachment; filename=export_{timestamp}.csv"
    }
)
```

## Revenue Reporting

Revenue reports support flexible grouping:

```python
# Determine period key based on grouping
if group_by == 'day':
    period_key = payment.session_datetime.strftime('%Y-%m-%d')
elif group_by == 'week':
    period_key = payment.session_datetime.strftime('%Y-W%U')
elif group_by == 'month':
    period_key = payment.session_datetime.strftime('%Y-%m')
```

Data is aggregated by period and currency:

```python
revenue_data[period_key] = {
    'period': period_key,
    'total_usd': Decimal('0.00'),
    'by_currency': {},
    'transaction_count': 0
}
```

## Error Handling

### Standard Error Responses

All endpoints use consistent error handling:

```python
try:
    # Operation
except AdminError as e:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
```

### Validation Errors

FastAPI automatically handles validation errors with detailed messages:

```python
@router.get("/metrics")
async def get_platform_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days")
):
    # FastAPI validates: 1 <= days <= 365
```

## Performance Considerations

### Database Indexes

Ensure proper indexes exist:
- `users.email` (for email search)
- `users.created_at` (for sorting)
- `bookings.client_id`, `bookings.coach_id` (for filtering)
- `bookings.created_at` (for date range queries)
- `payments.status` (for revenue queries)

### Query Optimization

1. **Use aggregations**: Calculate metrics in database, not in Python
2. **Limit data transfer**: Only select needed columns
3. **Pagination**: Always use offset/limit for large datasets
4. **Caching**: Consider caching metrics for short periods

### CSV Export Limits

For large exports, consider:
- Streaming responses for very large datasets
- Background job processing
- Pagination in exports
- Compression

## Testing

### Unit Tests

Test service methods with mocked database:

```python
def test_get_platform_metrics(mock_db):
    admin_service = AdminService(mock_db)
    metrics = admin_service.get_platform_metrics(days=30)
    
    assert metrics['total_users'] >= 0
    assert 'total_revenue_usd' in metrics
```

### Integration Tests

Test endpoints with test database:

```python
def test_list_users_endpoint(client, admin_token, db_session):
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert 'users' in data
    assert 'total' in data
```

### Authorization Tests

Test role-based access:

```python
def test_admin_endpoint_requires_admin_role(client, client_token):
    response = client.get(
        "/admin/metrics",
        headers={"Authorization": f"Bearer {client_token}"}
    )
    
    assert response.status_code == 403
```

## Monitoring and Logging

### Audit Log Format

Audit logs include:
- Admin user ID
- Action type
- Target type and ID
- Additional details
- Timestamp

Example:
```
[AUDIT] <AuditLog(admin=admin-uuid, action=delete_user, target=user:user-uuid)>
```

### Metrics to Monitor

1. **Admin API usage**: Track requests per admin
2. **Action frequency**: Monitor delete/update operations
3. **Export sizes**: Track CSV export sizes
4. **Query performance**: Monitor slow queries
5. **Error rates**: Track 4xx/5xx responses

### Alerting

Set up alerts for:
- High frequency of delete operations
- Large CSV exports
- Failed admin actions
- Unauthorized access attempts

## Deployment Considerations

### Environment Variables

No additional environment variables needed beyond standard app config.

### Database Migrations

No schema changes required - uses existing models.

### Scaling

Admin endpoints are typically low-traffic:
- No special scaling needed
- Consider rate limiting per admin user
- Cache metrics for short periods (1-5 minutes)

### Security Hardening

1. **Rate limiting**: Implement stricter limits for admin endpoints
2. **IP whitelisting**: Consider restricting admin access by IP
3. **MFA**: Require multi-factor authentication for admin users
4. **Session timeout**: Use shorter JWT expiry for admin tokens
5. **Audit review**: Regularly review audit logs

## Future Enhancements

Potential improvements:

1. **Real-time metrics**: WebSocket support for live dashboard
2. **Advanced filtering**: More complex query builders
3. **Bulk operations**: Batch user updates
4. **Scheduled reports**: Automated email reports
5. **Data visualization**: Built-in charts and graphs
6. **Audit log persistence**: Store audit logs in database
7. **Role management**: More granular admin permissions
8. **Activity alerts**: Real-time notifications for admin actions

## API Documentation

The admin API is fully documented in:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

All endpoints include:
- Detailed descriptions
- Parameter documentation
- Request/response examples
- Error response documentation

## Related Documentation

- [ADMIN_API_REFERENCE.md](./ADMIN_API_REFERENCE.md) - Complete API reference
- [ADMIN_QUICK_START.md](./ADMIN_QUICK_START.md) - Quick start guide
- [AUTHENTICATION_IMPLEMENTATION.md](./AUTHENTICATION_IMPLEMENTATION.md) - Auth details
- [DATABASE_MODELS.md](./DATABASE_MODELS.md) - Database schema
