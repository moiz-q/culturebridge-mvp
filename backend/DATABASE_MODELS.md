# Database Models Documentation

This document describes the database models implemented for the CultureBridge platform.

## Overview

The database schema consists of 10 main tables organized into four categories:
1. **User Management**: users, client_profiles, coach_profiles
2. **Booking System**: bookings, payments
3. **Community Features**: posts, comments, resources, bookmarks
4. **AI Matching**: match_cache

## Models

### 1. User Management

#### User Model (`users` table)
Core user model for all platform users (clients, coaches, admins).

**Fields:**
- `id` (UUID): Primary key
- `email` (String): Unique email address (indexed)
- `password_hash` (String): Bcrypt hashed password
- `role` (Enum): User role (client, coach, admin)
- `is_active` (Boolean): Account active status
- `email_verified` (Boolean): Email verification status
- `created_at` (DateTime): Account creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- One-to-one with ClientProfile or CoachProfile
- One-to-many with Bookings (as client and coach)
- One-to-many with Posts, Comments, Bookmarks

**Methods:**
- `validate_email()`: Validate email format
- `is_client()`, `is_coach()`, `is_admin()`: Role checking

**Requirements:** 1.1, 2.1, 3.1

---

#### ClientProfile Model (`client_profiles` table)
Extended profile for clients seeking coaching services.

**Fields:**
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to users (unique, cascade delete)
- `first_name`, `last_name` (String): Personal information
- `photo_url` (String): Profile photo URL
- `phone` (String): Contact number
- `timezone` (String): User timezone
- `quiz_data` (JSONB): Quiz responses for AI matching (required)
- `preferences` (JSONB): User preferences
- `created_at`, `updated_at` (DateTime): Timestamps

**Methods:**
- `validate_quiz_data()`: Ensures all 20 required matching factors are present
- `get_full_name()`: Returns formatted full name

**Requirements:** 2.1, 2.2, 2.5

---

#### CoachProfile Model (`coach_profiles` table)
Extended profile for coaches providing services.

**Fields:**
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to users (unique, cascade delete)
- `first_name`, `last_name` (String): Personal information
- `photo_url` (String): Profile photo URL
- `bio` (Text): Professional biography
- `intro_video_url` (String): Introduction video URL
- `expertise` (Array[Text]): Areas of expertise
- `languages` (Array[Text]): Languages spoken (GIN indexed)
- `countries` (Array[Text]): Countries of experience
- `hourly_rate` (Decimal): Hourly rate ($25-$500)
- `currency` (String): Currency code (default: USD)
- `availability` (JSONB): Available time slots
- `rating` (Decimal): Average rating (0.00-5.00)
- `total_sessions` (Integer): Completed sessions count
- `is_verified` (Boolean): Verification status
- `created_at`, `updated_at` (DateTime): Timestamps

**Methods:**
- `validate_hourly_rate()`: Ensures rate is within $25-$500 range
- `get_full_name()`: Returns formatted full name
- `has_language()`, `has_country_experience()`, `has_expertise()`: Query helpers

**Requirements:** 3.1, 3.2, 3.4, 3.5

---

### 2. Booking System

#### Booking Model (`bookings` table)
Represents scheduled coaching sessions.

**Fields:**
- `id` (UUID): Primary key
- `client_id` (UUID): Foreign key to users (indexed)
- `coach_id` (UUID): Foreign key to users (indexed)
- `session_datetime` (DateTime): Session start time (indexed)
- `duration_minutes` (Integer): Session duration (default: 60)
- `status` (Enum): Booking status (pending, confirmed, completed, cancelled)
- `payment_id` (UUID): Reference to payment
- `meeting_link` (String): Video meeting URL
- `notes` (Text): Additional notes
- `created_at`, `updated_at` (DateTime): Timestamps

**Methods:**
- `is_pending()`, `is_confirmed()`, `is_completed()`, `is_cancelled()`: Status checks
- `can_be_cancelled()`: Check if cancellation is allowed
- `validate_duration()`: Ensure positive duration
- `is_past()`: Check if session is in the past

**Requirements:** 5.1

---

#### Payment Model (`payments` table)
Represents payment transactions for bookings.

**Fields:**
- `id` (UUID): Primary key
- `booking_id` (UUID): Foreign key to bookings
- `amount` (Decimal): Payment amount
- `currency` (String): Currency code (default: USD)
- `status` (Enum): Payment status (pending, succeeded, failed, refunded)
- `stripe_session_id` (String): Stripe checkout session ID
- `stripe_payment_intent_id` (String): Stripe payment intent ID
- `created_at`, `updated_at` (DateTime): Timestamps

**Methods:**
- `is_pending()`, `is_succeeded()`, `is_failed()`, `is_refunded()`: Status checks
- `validate_amount()`: Ensure positive amount

**Requirements:** 5.2, 5.3

---

### 3. Community Features

#### Post Model (`posts` table)
Forum posts and discussions.

**Fields:**
- `id` (UUID): Primary key
- `author_id` (UUID): Foreign key to users
- `title` (String): Post title
- `content` (Text): Post content
- `post_type` (Enum): Type (discussion, question, announcement)
- `is_private` (Boolean): Visibility flag
- `upvotes` (Integer): Upvote count
- `created_at` (DateTime): Creation timestamp (indexed)
- `updated_at` (DateTime): Last update timestamp

**Methods:**
- `is_discussion()`, `is_question()`, `is_announcement()`: Type checks
- `increment_upvotes()`, `decrement_upvotes()`: Vote management

**Requirements:** 6.1, 6.4, 6.5

---

#### Comment Model (`comments` table)
Comments on forum posts.

**Fields:**
- `id` (UUID): Primary key
- `post_id` (UUID): Foreign key to posts (cascade delete)
- `author_id` (UUID): Foreign key to users
- `content` (Text): Comment content
- `created_at` (DateTime): Creation timestamp

**Requirements:** 6.1

---

#### Resource Model (`resources` table)
Educational resources in the library.

**Fields:**
- `id` (UUID): Primary key
- `title` (String): Resource title
- `description` (Text): Resource description
- `resource_type` (Enum): Type (article, video, document)
- `url` (String): Resource URL
- `tags` (Array[Text]): Tags for categorization
- `created_by` (UUID): Foreign key to users
- `created_at` (DateTime): Creation timestamp

**Methods:**
- `is_article()`, `is_video()`, `is_document()`: Type checks
- `has_tag()`: Tag query helper

**Requirements:** 6.2, 6.3

---

#### Bookmark Model (`bookmarks` table)
User bookmarks of resources.

**Fields:**
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to users
- `resource_id` (UUID): Foreign key to resources
- `created_at` (DateTime): Creation timestamp

**Constraints:**
- Unique constraint on (user_id, resource_id)

**Requirements:** 6.3

---

### 4. AI Matching

#### MatchCache Model (`match_cache` table)
Cached AI-generated coach match results.

**Fields:**
- `id` (UUID): Primary key
- `client_id` (UUID): Foreign key to users
- `match_results` (JSONB): Cached match data
- `expires_at` (DateTime): Cache expiration time
- `created_at` (DateTime): Creation timestamp

**Methods:**
- `is_expired()`: Check if cache entry is expired

**Requirements:** 4.4

---

## Database Indexes

The following indexes are created for performance optimization (Requirement 8.2):

1. **users.email** - Unique index for fast email lookups
2. **bookings.client_id** - Index for client booking queries
3. **bookings.coach_id** - Index for coach booking queries
4. **bookings.session_datetime** - Index for time-based queries
5. **posts.created_at** - Index for chronological post ordering
6. **coach_profiles.languages** - GIN index for array search operations

## Enumerations

### UserRole
- `client`: Client seeking coaching
- `coach`: Coach providing services
- `admin`: Platform administrator

### BookingStatus
- `pending`: Booking created, awaiting payment
- `confirmed`: Payment successful, booking confirmed
- `completed`: Session completed
- `cancelled`: Booking cancelled

### PaymentStatus
- `pending`: Payment initiated
- `succeeded`: Payment successful
- `failed`: Payment failed
- `refunded`: Payment refunded

### PostType
- `discussion`: General discussion
- `question`: Question post
- `announcement`: Announcement

### ResourceType
- `article`: Written article
- `video`: Video content
- `document`: Document file

## Relationships

### User Relationships
- User → ClientProfile (one-to-one)
- User → CoachProfile (one-to-one)
- User → Bookings as client (one-to-many)
- User → Bookings as coach (one-to-many)
- User → Posts (one-to-many)
- User → Comments (one-to-many)
- User → Bookmarks (one-to-many)
- User → Resources created (one-to-many)

### Booking Relationships
- Booking → Client (many-to-one)
- Booking → Coach (many-to-one)
- Booking → Payment (one-to-one)

### Community Relationships
- Post → Author (many-to-one)
- Post → Comments (one-to-many)
- Comment → Post (many-to-one)
- Comment → Author (many-to-one)
- Resource → Creator (many-to-one)
- Resource → Bookmarks (one-to-many)
- Bookmark → User (many-to-one)
- Bookmark → Resource (many-to-one)

## Cascade Deletes

The following cascade delete rules are implemented:

- Deleting a User cascades to:
  - ClientProfile
  - CoachProfile
  - Posts
  - Comments
  - Bookmarks

- Deleting a Post cascades to:
  - Comments

- Deleting a Resource cascades to:
  - Bookmarks

## Migration Files

### Initial Migration (001)
File: `alembic/versions/2025_11_05_1430-001_initial_migration_with_all_models.py`

This migration creates:
- All 10 tables with proper constraints
- All 6 required indexes
- 5 enum types
- Foreign key relationships
- Cascade delete rules

To apply: `alembic upgrade head`
To rollback: `alembic downgrade base`

## Testing

To verify models are properly configured:
```bash
python verify_models.py
```

Note: This requires a database connection. Ensure DATABASE_URL is set in your .env file.

## Next Steps

After implementing these models, the next tasks are:
1. Implement authentication and authorization system (Task 3)
2. Create profile repositories and API endpoints (Task 4)
3. Implement AI matching engine (Task 5)
