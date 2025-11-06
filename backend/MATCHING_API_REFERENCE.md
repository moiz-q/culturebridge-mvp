# AI Matching Engine API Reference

## Overview

The AI Matching Engine uses OpenAI embeddings to match clients with the most compatible coaches based on 20+ matching factors including languages, countries, goals, expertise, budget, and availability.

## Requirements

- **Requirements**: 4.1, 4.2, 4.3, 4.4, 4.5
- **Authentication**: Required (Client role only)
- **OpenAI API Key**: Required in environment variables
- **Redis**: Optional (for caching, gracefully degrades if unavailable)

## Matching Algorithm

### Weighted Scoring System

The matching algorithm calculates a score (0-100) using weighted similarity across multiple factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Language Overlap | 25% | Jaccard similarity between client's preferred languages and coach's spoken languages |
| Country Experience | 20% | Jaccard similarity between client's target countries and coach's country experience |
| Goal-Expertise Alignment | 30% | Semantic similarity using OpenAI embeddings between client's goals/challenges and coach's expertise |
| Budget Compatibility | 15% | Perfect match if coach rate ≤ client budget, partial if within 20% over |
| Availability Match | 10% | Checks if coach has availability slots defined |

### Fallback Mechanism

If the AI matching engine fails (timeout, API error), the system automatically falls back to returning top-rated coaches sorted by rating and total sessions.

## API Endpoints

### POST /match

Get AI-generated coach matches for the authenticated client.

**Request Body:**
```json
{
  "limit": 10,
  "use_cache": true
}
```

**Parameters:**
- `limit` (optional): Maximum number of matches to return (1-50, default: 10)
- `use_cache` (optional): Whether to use cached results (default: true)

**Response:**
```json
{
  "matches": [
    {
      "coach_id": "uuid",
      "user_id": "uuid",
      "first_name": "John",
      "last_name": "Doe",
      "photo_url": "https://...",
      "bio": "Experienced intercultural coach...",
      "expertise": ["career_transition", "cultural_adaptation"],
      "languages": ["English", "Spanish", "French"],
      "countries": ["Spain", "France", "USA"],
      "hourly_rate": 150.00,
      "currency": "USD",
      "rating": 4.85,
      "total_sessions": 127,
      "is_verified": true,
      "match_score": 87.5,
      "confidence_score": 87.5
    }
  ],
  "total_matches": 10,
  "cached": false,
  "generated_at": "2025-11-05T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Matches generated successfully
- `400 Bad Request`: Incomplete quiz data
- `403 Forbidden`: User is not a client
- `404 Not Found`: Client profile not found
- `500 Internal Server Error`: Matching service failed

**Example:**
```bash
curl -X POST http://localhost:8000/match \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "use_cache": true}'
```

### GET /match/cache/info

Get cache information for the current client's matches.

**Response:**
```json
{
  "cache_key": "match:user_id:quiz_hash",
  "exists": true,
  "ttl_seconds": 82800
}
```

**Status Codes:**
- `200 OK`: Cache info retrieved
- `403 Forbidden`: User is not a client
- `404 Not Found`: Client profile not found

### DELETE /match/cache

Clear cached match results for the current client.

**Response:**
- `204 No Content`: Cache cleared successfully

**Status Codes:**
- `204 No Content`: Cache cleared
- `403 Forbidden`: User is not a client

## Caching Strategy

### Cache Key Generation

Cache keys are generated using the format:
```
match:{client_id}:{md5_hash_of_quiz_data}
```

This ensures that:
- Each client has separate cache entries
- Cache is automatically invalidated when quiz data changes
- Multiple clients can have cached results simultaneously

### Cache TTL

- **Default TTL**: 24 hours (86400 seconds)
- **Automatic Invalidation**: 
  - When client updates their profile/quiz data
  - When any coach updates their profile (invalidates all match caches)

### Cache Behavior

- If Redis is unavailable, the system gracefully degrades and generates matches without caching
- Cache can be manually cleared using the DELETE endpoint
- Cache status can be checked using the GET endpoint

## Client Quiz Data Requirements

Before requesting matches, clients must complete their profile with all 20 required matching factors:

1. `target_countries` (array): Target countries for relocation
2. `cultural_goals` (array): Cultural adaptation goals
3. `preferred_languages` (array): Preferred coaching languages
4. `industry` (string): Industry or profession
5. `family_status` (string): Family status
6. `previous_expat_experience` (boolean): Has previous expat experience
7. `timeline_urgency` (integer 1-5): Timeline urgency scale
8. `budget_range` (object): Budget range with min and max
9. `coaching_style` (string): Preferred coaching style
10. `specific_challenges` (array): Specific challenges

**Example Quiz Data:**
```json
{
  "target_countries": ["Spain", "France"],
  "cultural_goals": ["career_transition", "family_adaptation"],
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
  "specific_challenges": ["language_barriers", "cultural_differences"]
}
```

## Performance Considerations

### Timeouts

- **OpenAI API Timeout**: 10 seconds per request
- **Total Matching Timeout**: 10 seconds
- **Fallback**: Automatic fallback to top-rated coaches on timeout

### Optimization

- **Caching**: Reduces OpenAI API calls and improves response time
- **Batch Processing**: Calculates scores for up to 100 active coaches
- **Async Operations**: Uses asyncio for concurrent OpenAI API calls

### Expected Performance

- **With Cache Hit**: < 50ms response time
- **Without Cache (Cold Start)**: 2-5 seconds (depending on OpenAI API)
- **Fallback Mode**: < 100ms response time

## Error Handling

### Common Errors

1. **Incomplete Quiz Data**
   - Status: 400 Bad Request
   - Solution: Complete all 20 required quiz factors

2. **OpenAI API Timeout**
   - Behavior: Automatic fallback to top-rated coaches
   - No error returned to client

3. **Redis Unavailable**
   - Behavior: Graceful degradation, no caching
   - Matches still generated successfully

4. **No Active Coaches**
   - Response: Empty matches array
   - Status: 200 OK

## Testing

### Manual Testing

1. **Create a client profile with complete quiz data**
2. **Request matches**:
   ```bash
   curl -X POST http://localhost:8000/match \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"limit": 10}'
   ```
3. **Verify cache**:
   ```bash
   curl -X GET http://localhost:8000/match/cache/info \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```
4. **Clear cache**:
   ```bash
   curl -X DELETE http://localhost:8000/match/cache \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

### Environment Setup

Required environment variables:
```bash
OPENAI_API_KEY=sk-your-openai-api-key
REDIS_URL=redis://localhost:6379
```

## Integration with Frontend

### Example React Hook

```typescript
const useCoachMatches = () => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMatches = async (limit = 10, useCache = true) => {
    setLoading(true);
    try {
      const response = await fetch('/match', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ limit, use_cache: useCache })
      });
      
      const data = await response.json();
      setMatches(data.matches);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { matches, loading, error, fetchMatches };
};
```

## Dependencies

- `openai==1.3.7`: OpenAI API client
- `numpy==1.26.2`: Vector calculations for cosine similarity
- `redis==5.0.1`: Redis client for caching
- `fastapi==0.104.1`: Web framework
- `sqlalchemy==2.0.23`: Database ORM

## Future Enhancements

1. **Machine Learning Model**: Train custom model on booking success data
2. **Real-time Availability**: Check actual time slot overlaps
3. **Collaborative Filtering**: Use booking history for recommendations
4. **A/B Testing**: Test different weighting schemes
5. **Personalization**: Learn from client feedback and booking patterns
