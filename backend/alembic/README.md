# Database Migrations

This directory contains Alembic database migrations for the CultureBridge platform.

## Prerequisites

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your database connection in `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/culturebridge
   ```

## Running Migrations

### Apply migrations (upgrade to latest)
```bash
alembic upgrade head
```

### Rollback migrations (downgrade one version)
```bash
alembic downgrade -1
```

### Rollback all migrations
```bash
alembic downgrade base
```

### View migration history
```bash
alembic history
```

### View current migration version
```bash
alembic current
```

## Creating New Migrations

### Auto-generate migration from model changes
```bash
alembic revision --autogenerate -m "description of changes"
```

### Create empty migration
```bash
alembic revision -m "description of changes"
```

## Migration Details

### Initial Migration (001)
- Creates all core tables: users, client_profiles, coach_profiles, bookings, payments, posts, comments, resources, bookmarks, match_cache
- Creates required indexes:
  - `users.email` (unique index)
  - `bookings.client_id` (index)
  - `bookings.coach_id` (index)
  - `bookings.session_datetime` (index)
  - `posts.created_at` (index)
  - `coach_profiles.languages` (GIN index for array search)
- Creates enum types: UserRole, BookingStatus, PaymentStatus, PostType, ResourceType

## Testing Migrations

### Test upgrade
```bash
alembic upgrade head
```

### Test downgrade
```bash
alembic downgrade base
```

### Test upgrade again to ensure idempotency
```bash
alembic upgrade head
```

## Notes

- Always review auto-generated migrations before applying them
- Test migrations on a development database before applying to production
- Keep migrations small and focused on specific changes
- Never modify existing migrations that have been applied to production
- Use descriptive names for migrations
