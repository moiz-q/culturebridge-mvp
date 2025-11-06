# Quick Start Guide - Database Models

## What Was Implemented

Task 2 "Implement database models and migrations" is now complete with:
- ✅ 10 database tables
- ✅ 5 enum types
- ✅ 6 performance indexes
- ✅ Complete relationships and cascade rules
- ✅ Initial Alembic migration

## File Structure

```
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py          # Model exports
│   │   ├── user.py              # User & UserRole
│   │   ├── profile.py           # ClientProfile & CoachProfile
│   │   ├── booking.py           # Booking & Payment
│   │   └── community.py         # Post, Comment, Resource, Bookmark, MatchCache
│   ├── database.py              # SQLAlchemy configuration
│   └── config.py                # Settings
├── alembic/
│   ├── versions/
│   │   └── 2025_11_05_1430-001_initial_migration_with_all_models.py
│   ├── env.py                   # Alembic environment
│   ├── README.md                # Migration guide
│   └── alembic.ini              # Alembic config
├── verify_models.py             # Model verification script
├── DATABASE_MODELS.md           # Detailed documentation
├── IMPLEMENTATION_SUMMARY.md    # Implementation details
└── QUICK_START.md               # This file
```

## Quick Commands

### Setup Database
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file with database URL
echo "DATABASE_URL=postgresql://user:password@localhost:5432/culturebridge" > .env

# 3. Run migrations
alembic upgrade head
```

### Common Operations
```bash
# Check current migration version
alembic current

# View migration history
alembic history

# Rollback one migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base

# Create new migration (after model changes)
alembic revision --autogenerate -m "description"
```

## Model Usage Examples

### Creating a User
```python
from app.models import User, UserRole
from app.database import SessionLocal

db = SessionLocal()

user = User(
    email="client@example.com",
    password_hash="hashed_password_here",
    role=UserRole.CLIENT,
    is_active=True,
    email_verified=False
)

db.add(user)
db.commit()
db.refresh(user)
```

### Creating a Client Profile
```python
from app.models import ClientProfile

profile = ClientProfile(
    user_id=user.id,
    first_name="John",
    last_name="Doe",
    quiz_data={
        "target_countries": ["Spain", "France"],
        "cultural_goals": ["career_transition"],
        "preferred_languages": ["English", "Spanish"],
        "industry": "Technology",
        "family_status": "single",
        "previous_expat_experience": True,
        "timeline_urgency": 4,
        "budget_range": {"min": 50, "max": 150},
        "coaching_style": "collaborative",
        "specific_challenges": ["language_barrier", "cultural_adaptation"]
    }
)

db.add(profile)
db.commit()
```

### Creating a Coach Profile
```python
from app.models import CoachProfile

coach_profile = CoachProfile(
    user_id=coach_user.id,
    first_name="Jane",
    last_name="Smith",
    bio="Experienced intercultural coach...",
    expertise=["career_coaching", "cultural_adaptation"],
    languages=["English", "Spanish", "French"],
    countries=["Spain", "France", "USA"],
    hourly_rate=100.00,
    currency="USD",
    availability={
        "monday": [{"start": "09:00", "end": "17:00"}],
        "tuesday": [{"start": "09:00", "end": "17:00"}]
    }
)

db.add(coach_profile)
db.commit()
```

### Creating a Booking
```python
from app.models import Booking, BookingStatus
from datetime import datetime, timedelta

booking = Booking(
    client_id=client_user.id,
    coach_id=coach_user.id,
    session_datetime=datetime.utcnow() + timedelta(days=7),
    duration_minutes=60,
    status=BookingStatus.PENDING
)

db.add(booking)
db.commit()
```

### Querying with Relationships
```python
# Get user with profile
user = db.query(User).filter(User.email == "client@example.com").first()
client_profile = user.client_profile

# Get all bookings for a client
client_bookings = user.client_bookings

# Get all posts by a user
user_posts = user.posts

# Get coach with high rating
from app.models import CoachProfile
top_coaches = db.query(CoachProfile).filter(
    CoachProfile.rating >= 4.5
).order_by(CoachProfile.rating.desc()).limit(10).all()
```

## Model Validation

All models include validation methods:

```python
# User validation
if user.validate_email():
    print("Valid email")

# Client profile validation
if client_profile.validate_quiz_data():
    print("Quiz data complete")

# Coach profile validation
if coach_profile.validate_hourly_rate():
    print("Rate within acceptable range")

# Booking validation
if booking.can_be_cancelled():
    booking.status = BookingStatus.CANCELLED
```

## Database Indexes

The following indexes are automatically created:
1. `users.email` - Fast email lookups
2. `bookings.client_id` - Client booking queries
3. `bookings.coach_id` - Coach booking queries
4. `bookings.session_datetime` - Time-based queries
5. `posts.created_at` - Chronological ordering
6. `coach_profiles.languages` - Array search (GIN index)

## Important Notes

1. **Connection Pooling**: Configured for 20 connections with 10 overflow
2. **Cascade Deletes**: Deleting a user cascades to profiles, posts, comments, bookmarks
3. **JSONB Fields**: Used for flexible data (quiz_data, preferences, availability, match_results)
4. **Enums**: Ensure data consistency for roles, statuses, and types
5. **Timestamps**: All models have created_at and updated_at (auto-updated)
6. **UUIDs**: All primary keys use UUID for better distribution and security

## Troubleshooting

### "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### "Can't connect to database"
Check your DATABASE_URL in .env file and ensure PostgreSQL is running.

### "Table already exists"
If you need to reset:
```bash
alembic downgrade base
alembic upgrade head
```

### "Import error for models"
Ensure you're in the backend directory and PYTHONPATH is set:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Next Steps

Now that database models are complete, proceed to:
1. **Task 3**: Authentication system (JWT, middleware, auth endpoints)
2. **Task 4**: Profile management (repositories, API endpoints)
3. **Task 5**: AI matching engine (OpenAI integration, caching)

## Documentation

- **DATABASE_MODELS.md** - Detailed model documentation
- **IMPLEMENTATION_SUMMARY.md** - What was implemented
- **alembic/README.md** - Migration guide
- **requirements.txt** - All dependencies

## Support

For issues or questions:
1. Check DATABASE_MODELS.md for model details
2. Review IMPLEMENTATION_SUMMARY.md for requirements mapping
3. See alembic/README.md for migration help
