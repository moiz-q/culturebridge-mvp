# AI Matching Engine - Quick Start Guide

## Prerequisites

1. **Backend running** on `http://localhost:8000`
2. **PostgreSQL database** with migrations applied
3. **Redis** (optional but recommended)
4. **OpenAI API key** configured

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create or update `.env` file:

```bash
# Required
DATABASE_URL=postgresql://user:password@localhost:5432/culturebridge
OPENAI_API_KEY=sk-your-openai-api-key

# Optional (for caching)
REDIS_URL=redis://localhost:6379

# Other settings
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000
```

### 3. Start Redis (Optional)

```bash
docker run -d -p 6379:6379 redis:latest
```

Or if you have Redis installed locally:

```bash
redis-server
```

### 4. Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## Testing the Matching Engine

### Step 1: Create Test Users

#### Create a Client User

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "password": "SecurePass123!",
    "role": "client"
  }'
```

Save the JWT token from the response.

#### Create Coach Users

```bash
# Coach 1 - Spanish/French expert
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "coach1@example.com",
    "password": "SecurePass123!",
    "role": "coach"
  }'

# Coach 2 - German/English expert
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "coach2@example.com",
    "password": "SecurePass123!",
    "role": "coach"
  }'
```

### Step 2: Complete Client Profile

Login as client and complete profile with quiz data:

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "password": "SecurePass123!"
  }'

# Save the token
export CLIENT_TOKEN="your-jwt-token-here"

# Update profile with quiz data
curl -X PUT http://localhost:8000/profile \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "timezone": "Europe/Madrid",
    "quiz_data": {
      "target_countries": ["Spain", "France"],
      "cultural_goals": ["career_transition", "family_adaptation", "language_learning"],
      "preferred_languages": ["English", "Spanish"],
      "industry": "Technology",
      "family_status": "married_with_children",
      "previous_expat_experience": false,
      "timeline_urgency": 4,
      "budget_range": {
        "min": 100,
        "max": 200
      },
      "coaching_style": "collaborative",
      "specific_challenges": ["language_barriers", "cultural_differences", "work_life_balance"]
    }
  }'
```

### Step 3: Complete Coach Profiles

#### Coach 1 Profile

```bash
# Login as coach1
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "coach1@example.com",
    "password": "SecurePass123!"
  }'

export COACH1_TOKEN="coach1-jwt-token"

# Update coach profile
curl -X PUT http://localhost:8000/profile \
  -H "Authorization: Bearer $COACH1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Maria",
    "last_name": "Garcia",
    "bio": "Experienced intercultural coach specializing in Spanish and French cultures. 10+ years helping expats adapt to life in Southern Europe.",
    "expertise": ["career_transition", "cultural_adaptation", "language_learning", "family_relocation"],
    "languages": ["English", "Spanish", "French"],
    "countries": ["Spain", "France", "Portugal"],
    "hourly_rate": 150,
    "currency": "USD",
    "availability": {
      "monday": ["09:00-17:00"],
      "tuesday": ["09:00-17:00"],
      "wednesday": ["09:00-17:00"],
      "thursday": ["09:00-17:00"],
      "friday": ["09:00-15:00"]
    }
  }'

# Mark as verified (requires admin - for testing, update directly in DB)
# UPDATE coach_profiles SET is_verified = true, rating = 4.8, total_sessions = 50 WHERE user_id = 'coach1_user_id';
```

#### Coach 2 Profile

```bash
# Login as coach2
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "coach2@example.com",
    "password": "SecurePass123!"
  }'

export COACH2_TOKEN="coach2-jwt-token"

# Update coach profile
curl -X PUT http://localhost:8000/profile \
  -H "Authorization: Bearer $COACH2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Hans",
    "last_name": "Mueller",
    "bio": "German intercultural expert with focus on business culture and corporate relocations.",
    "expertise": ["business_culture", "corporate_relocation", "leadership_development"],
    "languages": ["English", "German", "Dutch"],
    "countries": ["Germany", "Netherlands", "Switzerland"],
    "hourly_rate": 180,
    "currency": "USD",
    "availability": {
      "monday": ["10:00-18:00"],
      "tuesday": ["10:00-18:00"],
      "wednesday": ["10:00-18:00"],
      "thursday": ["10:00-18:00"]
    }
  }'

# Mark as verified (requires admin - for testing, update directly in DB)
# UPDATE coach_profiles SET is_verified = true, rating = 4.5, total_sessions = 30 WHERE user_id = 'coach2_user_id';
```

### Step 4: Request Matches

Now request AI-generated matches as the client:

```bash
curl -X POST http://localhost:8000/match \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 10,
    "use_cache": true
  }'
```

**Expected Response:**

```json
{
  "matches": [
    {
      "coach_id": "uuid",
      "user_id": "uuid",
      "first_name": "Maria",
      "last_name": "Garcia",
      "photo_url": null,
      "bio": "Experienced intercultural coach...",
      "expertise": ["career_transition", "cultural_adaptation", "language_learning", "family_relocation"],
      "languages": ["English", "Spanish", "French"],
      "countries": ["Spain", "France", "Portugal"],
      "hourly_rate": 150.0,
      "currency": "USD",
      "rating": 4.8,
      "total_sessions": 50,
      "is_verified": true,
      "match_score": 87.5,
      "confidence_score": 87.5
    },
    {
      "coach_id": "uuid",
      "user_id": "uuid",
      "first_name": "Hans",
      "last_name": "Mueller",
      "bio": "German intercultural expert...",
      "expertise": ["business_culture", "corporate_relocation", "leadership_development"],
      "languages": ["English", "German", "Dutch"],
      "countries": ["Germany", "Netherlands", "Switzerland"],
      "hourly_rate": 180.0,
      "currency": "USD",
      "rating": 4.5,
      "total_sessions": 30,
      "is_verified": true,
      "match_score": 45.2,
      "confidence_score": 45.2
    }
  ],
  "total_matches": 2,
  "cached": false,
  "generated_at": "2025-11-05T10:30:00Z"
}
```

**Note:** Maria should score higher because:
- Language match: Spanish (perfect overlap)
- Country match: Spain, France (perfect overlap)
- Expertise match: career_transition, cultural_adaptation (high overlap)
- Budget: $150 within client's $100-$200 range
- Availability: Has availability defined

### Step 5: Test Caching

#### Check Cache Status

```bash
curl -X GET http://localhost:8000/match/cache/info \
  -H "Authorization: Bearer $CLIENT_TOKEN"
```

**Response:**
```json
{
  "cache_key": "match:client_id:quiz_hash",
  "exists": true,
  "ttl_seconds": 86395
}
```

#### Request Matches Again (Should Use Cache)

```bash
curl -X POST http://localhost:8000/match \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 10,
    "use_cache": true
  }'
```

**Response should have:**
```json
{
  "cached": true,
  ...
}
```

#### Clear Cache

```bash
curl -X DELETE http://localhost:8000/match/cache \
  -H "Authorization: Bearer $CLIENT_TOKEN"
```

### Step 6: Test Cache Invalidation

Update client profile and verify cache is cleared:

```bash
# Update profile
curl -X PUT http://localhost:8000/profile \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quiz_data": {
      "target_countries": ["Germany", "Netherlands"],
      "cultural_goals": ["business_culture", "corporate_relocation"],
      "preferred_languages": ["English", "German"],
      "industry": "Finance",
      "family_status": "single",
      "previous_expat_experience": true,
      "timeline_urgency": 5,
      "budget_range": {
        "min": 150,
        "max": 250
      },
      "coaching_style": "directive",
      "specific_challenges": ["business_etiquette", "networking"]
    }
  }'

# Check cache (should not exist)
curl -X GET http://localhost:8000/match/cache/info \
  -H "Authorization: Bearer $CLIENT_TOKEN"

# Request new matches (should generate fresh results)
curl -X POST http://localhost:8000/match \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'
```

**Now Hans should score higher** because the client's updated profile matches his expertise better.

## Troubleshooting

### Issue: "Client profile not found"

**Solution:** Make sure you've created and updated the client profile with quiz data.

### Issue: "Incomplete quiz data"

**Solution:** Ensure all 20 required quiz factors are present in the quiz_data object.

### Issue: Empty matches array

**Solution:** 
1. Verify coaches exist in database
2. Check coaches are marked as verified (`is_verified = true`)
3. Check coaches' users are active (`is_active = true`)

### Issue: Low match scores

**Solution:** This is expected if there's little overlap between client preferences and coach profiles. Try creating coaches with profiles that better match the client's quiz data.

### Issue: Slow response times

**Solution:**
1. Check OpenAI API key is valid
2. Verify Redis is running (for caching)
3. First request will be slow (2-5s), subsequent requests should be fast (<50ms)

### Issue: "OpenAI API error"

**Solution:**
1. Verify `OPENAI_API_KEY` is set correctly
2. Check OpenAI API quota/billing
3. System will fallback to top-rated coaches automatically

## API Documentation

For complete API documentation, see:
- `MATCHING_API_REFERENCE.md` - Detailed API reference
- `MATCHING_IMPLEMENTATION.md` - Implementation details

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from the browser using these interfaces.

## Next Steps

1. **Create more test data**: Add more coaches with varied profiles
2. **Test different scenarios**: Try different quiz data combinations
3. **Monitor performance**: Check response times and cache hit rates
4. **Integrate with frontend**: Use the API in your React/Next.js application
5. **Add unit tests**: Write tests for matching logic (optional)

## Support

For issues or questions:
1. Check the implementation documentation
2. Review the API reference
3. Check FastAPI logs for errors
4. Verify environment variables are set correctly
