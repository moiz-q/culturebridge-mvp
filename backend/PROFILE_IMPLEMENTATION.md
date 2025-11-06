# Profile Management Implementation

## Overview

This document describes the implementation of Task 4: User Profile Management for the CultureBridge MVP platform.

## Implemented Components

### 1. Repositories (Task 4.1)

#### UserRepository (`app/repositories/user_repository.py`)
- CRUD operations for User model
- Query methods with filters (role, active status, search)
- Pagination support (default 20 items per page)
- Email existence checking

#### ClientProfileRepository (`app/repositories/profile_repository.py`)
- CRUD operations for ClientProfile model
- User ID-based queries
- Pagination support

#### CoachProfileRepository (`app/repositories/profile_repository.py`)
- CRUD operations for CoachProfile model
- Advanced filtering:
  - Language (array contains)
  - Country (array contains)
  - Expertise (array contains)
  - Hourly rate range
  - Verification status
  - Minimum rating
- Ordered by rating and total sessions
- Active coaches query for AI matching
- Pagination support

### 2. API Endpoints (Task 4.2)

#### Profile Endpoints (`/profile`)

**GET /profile**
- Fetch current user's profile
- Returns user info + role-specific profile (client or coach)
- Requirements: 2.1, 3.1

**PUT /profile**
- Update current user's profile
- Auto-creates profile if doesn't exist
- Validates quiz data (20 required factors for clients)
- Validates hourly rate ($25-$500 for coaches)
- Requirements: 2.1, 2.2, 3.1, 3.2, 3.3, 3.4, 3.5

**POST /profile/photo**
- Upload profile photo to S3
- Validates file size (5MB max)
- Validates file format (JPEG/PNG/WebP)
- Deletes old photo when uploading new one
- Requirements: 2.3

#### Coach Discovery Endpoints (`/coaches`)

**GET /coaches**
- List coaches with optional filters:
  - language
  - country
  - expertise
  - min_rate / max_rate
  - is_verified
  - min_rating
- Pagination support (skip, limit)
- Ordered by rating and sessions
- Requirements: 3.1, 3.2, 3.3, 3.4, 3.5

**GET /coaches/{coach_id}**
- Get detailed coach profile by ID
- Requirements: 3.1

**PUT /coaches/{coach_id}**
- Update coach profile
- Authorization: Coach can only update own profile (or admin)
- Validates hourly rate
- Requirements: 3.1, 3.2, 3.3, 3.4, 3.5

### 3. GDPR Compliance (Task 4.3)

**GET /profile/export**
- Export all user data as JSON
- Includes:
  - User account info
  - Profile data (client or coach)
  - All bookings (as client or coach)
  - All posts
  - All comments
  - All bookmarks
- Requirements: 2.4

**DELETE /profile**
- Delete user account and all associated data
- Cascade deletion for:
  - Profile (client or coach)
  - Bookings
  - Posts
  - Comments
  - Bookmarks
  - Resources created
- Deletes profile photos from S3
- Requirements: 2.4

### 4. Supporting Components

#### Pydantic Schemas (`app/schemas/profile.py`)
- `QuizData`: Validates 20 required matching factors
- `ClientProfileCreate/Update/Response`
- `CoachProfileCreate/Update/Response`
- `CoachListResponse`: Simplified for listings
- `PhotoUploadResponse`
- `ProfileResponse`: Generic profile with user info

#### S3 Service (`app/utils/s3_utils.py`)
- File validation (size, format, MIME type)
- Profile photo upload with unique naming
- File deletion
- Public URL generation
- Error handling for AWS operations

## Data Validation

### Client Profile
- Quiz data must contain all 20 required factors:
  1. target_countries
  2. cultural_goals
  3. preferred_languages
  4. industry
  5. family_status
  6. previous_expat_experience
  7. timeline_urgency (1-5 scale)
  8. budget_range (min/max)
  9. coaching_style
  10. specific_challenges

### Coach Profile
- Hourly rate: $25 - $500
- Languages: Array of strings
- Countries: Array of strings
- Expertise: Array of strings
- Availability: JSONB flexible structure

### Photo Upload
- Max size: 5MB
- Allowed formats: JPEG, PNG, WebP
- Stored in S3: `profiles/{user_id}/{uuid}.{ext}`

## Security

- All endpoints require authentication (JWT token)
- Role-based access control:
  - Clients can only update client profiles
  - Coaches can only update their own coach profiles
  - Admins can update any profile
- Profile photos are publicly accessible (ACL: public-read)
- S3 operations use AWS credentials from environment

## Database Relationships

- User → ClientProfile (one-to-one, cascade delete)
- User → CoachProfile (one-to-one, cascade delete)
- User → Bookings (one-to-many, cascade delete)
- User → Posts (one-to-many, cascade delete)
- User → Comments (one-to-many, cascade delete)
- User → Bookmarks (one-to-many, cascade delete)

## API Integration

Routers registered in `app/main.py`:
- `profile_router`: Profile management endpoints
- `coaches_router`: Coach discovery endpoints

## Testing Recommendations

1. **Unit Tests**:
   - Repository CRUD operations
   - Quiz data validation
   - Hourly rate validation
   - S3 file validation

2. **Integration Tests**:
   - Profile creation and update flow
   - Photo upload with mocked S3
   - Coach filtering and pagination
   - GDPR export completeness
   - Cascade deletion verification

3. **E2E Tests**:
   - Client profile setup with quiz
   - Coach profile setup with pricing
   - Photo upload and display
   - Coach discovery and filtering
   - Account deletion flow

## Environment Variables Required

```bash
# AWS S3 (for photo uploads)
AWS_REGION=us-east-1
S3_BUCKET_NAME=culturebridge-uploads
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
```

## Next Steps

This implementation completes Task 4. The next task (Task 5) will implement the AI matching engine that uses the coach profiles and client quiz data to generate personalized coach recommendations.

## Requirements Coverage

- ✅ Requirement 2.1: Client profile management
- ✅ Requirement 2.2: Quiz data validation (20 factors)
- ✅ Requirement 2.3: Profile photo upload (5MB, JPEG/PNG/WebP)
- ✅ Requirement 2.4: GDPR compliance (export/delete)
- ✅ Requirement 2.5: Client profile storage
- ✅ Requirement 3.1: Coach profile management
- ✅ Requirement 3.2: Coach availability management
- ✅ Requirement 3.3: Coach intro video URL
- ✅ Requirement 3.4: Coach pricing ($25-$500)
- ✅ Requirement 3.5: Coach language support
