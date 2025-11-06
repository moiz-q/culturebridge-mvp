# Profile Management API Reference

## Authentication
All endpoints require JWT authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Profile Endpoints

### Get Current User Profile
```http
GET /profile
```

**Response:**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "role": "client|coach|admin",
  "is_active": true,
  "email_verified": false,
  "profile": {
    // ClientProfileResponse or CoachProfileResponse
  }
}
```

### Update Profile
```http
PUT /profile
Content-Type: application/json
```

**Client Profile Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "timezone": "America/New_York",
  "quiz_data": {
    "target_countries": ["Spain", "France"],
    "cultural_goals": ["career_transition", "family_adaptation"],
    "preferred_languages": ["English", "Spanish"],
    "industry": "Technology",
    "family_status": "married_with_children",
    "previous_expat_experience": true,
    "timeline_urgency": 4,
    "budget_range": {
      "min": 50,
      "max": 150
    },
    "coaching_style": "collaborative",
    "specific_challenges": ["language_barrier", "cultural_adjustment"]
  },
  "preferences": {
    "communication_preference": "video",
    "session_frequency": "weekly"
  }
}
```

**Coach Profile Request:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "bio": "Experienced intercultural coach with 10+ years...",
  "intro_video_url": "https://youtube.com/watch?v=...",
  "expertise": ["career_coaching", "family_relocation", "cultural_adaptation"],
  "languages": ["English", "Spanish", "French"],
  "countries": ["Spain", "France", "USA"],
  "hourly_rate": 100.00,
  "currency": "USD",
  "availability": {
    "timezone": "Europe/Madrid",
    "slots": [
      {
        "day": "monday",
        "start": "09:00",
        "end": "17:00"
      }
    ]
  }
}
```

### Upload Profile Photo
```http
POST /profile/photo
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Image file (JPEG/PNG/WebP, max 5MB)

**Response:**
```json
{
  "photo_url": "https://bucket.s3.region.amazonaws.com/profiles/user-id/uuid.jpg",
  "message": "Profile photo uploaded successfully"
}
```

### Export User Data (GDPR)
```http
GET /profile/export
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "client",
    "is_active": true,
    "email_verified": false,
    "created_at": "2025-11-05T10:00:00",
    "updated_at": "2025-11-05T10:00:00"
  },
  "profile": { /* profile data */ },
  "bookings": [ /* booking records */ ],
  "posts": [ /* forum posts */ ],
  "comments": [ /* comments */ ],
  "bookmarks": [ /* bookmarked resources */ ]
}
```

### Delete Account (GDPR)
```http
DELETE /profile
```

**Response:**
```json
{
  "message": "User account and all associated data have been permanently deleted",
  "user_id": "uuid"
}
```

## Coach Discovery Endpoints

### List Coaches
```http
GET /coaches?skip=0&limit=20&language=Spanish&country=Spain&expertise=career_coaching&min_rate=50&max_rate=150&is_verified=true&min_rating=4.0
```

**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip for pagination
- `limit` (int, default: 20): Maximum number of records to return
- `language` (string, optional): Filter by language
- `country` (string, optional): Filter by country experience
- `expertise` (string, optional): Filter by expertise area
- `min_rate` (float, optional): Minimum hourly rate
- `max_rate` (float, optional): Maximum hourly rate
- `is_verified` (bool, optional): Filter by verification status
- `min_rating` (float, optional): Minimum rating

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "first_name": "Jane",
    "last_name": "Smith",
    "photo_url": "https://...",
    "bio": "Experienced coach...",
    "expertise": ["career_coaching", "family_relocation"],
    "languages": ["English", "Spanish"],
    "countries": ["Spain", "USA"],
    "hourly_rate": 100.00,
    "currency": "USD",
    "rating": 4.8,
    "total_sessions": 150,
    "is_verified": true
  }
]
```

### Get Coach by ID
```http
GET /coaches/{coach_id}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "first_name": "Jane",
  "last_name": "Smith",
  "photo_url": "https://...",
  "bio": "Experienced coach...",
  "intro_video_url": "https://youtube.com/...",
  "expertise": ["career_coaching", "family_relocation"],
  "languages": ["English", "Spanish"],
  "countries": ["Spain", "USA"],
  "hourly_rate": 100.00,
  "currency": "USD",
  "availability": { /* availability data */ },
  "rating": 4.8,
  "total_sessions": 150,
  "is_verified": true,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-11-05T10:00:00"
}
```

### Update Coach Profile
```http
PUT /coaches/{coach_id}
Content-Type: application/json
```

**Authorization:** Coach can only update their own profile (or admin)

**Request:** Same as PUT /profile for coach

**Response:** Full coach profile

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Quiz data must contain all 20 required matching factors"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "You can only update your own profile"
}
```

### 404 Not Found
```json
{
  "detail": "Coach not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to upload photo: S3 error message"
}
```

## Quiz Data Requirements

All 20 required factors for client profiles:

1. **target_countries** (array of strings): Countries for relocation
2. **cultural_goals** (array of strings): Cultural adaptation goals
3. **preferred_languages** (array of strings): Preferred coaching languages
4. **industry** (string): Industry or profession
5. **family_status** (string): Family status
6. **previous_expat_experience** (boolean): Has previous expat experience
7. **timeline_urgency** (integer, 1-5): Timeline urgency scale
8. **budget_range** (object): Budget with min and max values
9. **coaching_style** (string): Preferred coaching style
10. **specific_challenges** (array of strings): Specific challenges

## Photo Upload Requirements

- **Max file size:** 5MB
- **Allowed formats:** JPEG, PNG, WebP
- **MIME types:** image/jpeg, image/png, image/webp
- **Storage:** AWS S3 with public-read ACL
- **Naming:** profiles/{user_id}/{uuid}.{extension}

## Pagination

All list endpoints support pagination:
- Default page size: 20 items
- Use `skip` and `limit` query parameters
- Example: `?skip=20&limit=20` for page 2

## Filtering

Coach listing supports multiple filters that can be combined:
- Array filters (language, country, expertise) use PostgreSQL array contains
- Range filters (min_rate, max_rate, min_rating) use comparison operators
- Boolean filters (is_verified) use exact match
- Results are ordered by rating (desc) and total_sessions (desc)
