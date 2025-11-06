# Community Features Quick Start Guide

Get started with the CultureBridge community features in minutes.

**Requirements:** 6.1, 6.2, 6.3, 6.4, 6.5

## Prerequisites

- Backend server running on `http://localhost:8000`
- Valid JWT authentication token
- Database migrations applied

## Quick Setup

### 1. Verify Community Endpoints

Check that the community router is registered:

```bash
curl http://localhost:8000/docs
```

Look for `/community` endpoints in the Swagger UI.

### 2. Get Authentication Token

First, login to get a JWT token:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

## Basic Usage

### Create a Forum Post

```bash
curl -X POST http://localhost:8000/community/posts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Welcome to CultureBridge!",
    "content": "This is my first post on the platform.",
    "post_type": "discussion",
    "is_private": false
  }'
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Welcome to CultureBridge!",
  "content": "This is my first post on the platform.",
  "post_type": "discussion",
  "is_private": false,
  "upvotes": 0,
  "comment_count": 0,
  "created_at": "2025-11-05T10:30:00Z"
}
```

### List All Posts

```bash
curl -X GET "http://localhost:8000/community/posts?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Add a Comment

```bash
curl -X POST http://localhost:8000/community/posts/POST_ID/comment \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Great post! Thanks for sharing."
  }'
```

### Upvote a Post

```bash
curl -X POST http://localhost:8000/community/posts/POST_ID/upvote \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Browse Resources

```bash
curl -X GET "http://localhost:8000/community/resources?resource_type=article&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Bookmark a Resource

```bash
curl -X POST http://localhost:8000/community/resources/RESOURCE_ID/bookmark \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### View Your Bookmarks

```bash
curl -X GET http://localhost:8000/community/bookmarks \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Common Workflows

### 1. Create and Engage with a Post

```bash
# Step 1: Create a post
POST_ID=$(curl -X POST http://localhost:8000/community/posts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Question about cultural adaptation",
    "content": "How long does it typically take to adapt?",
    "post_type": "question"
  }' | jq -r '.id')

# Step 2: Add a comment
curl -X POST http://localhost:8000/community/posts/$POST_ID/comment \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "It varies, but typically 3-6 months."
  }'

# Step 3: Upvote the post
curl -X POST http://localhost:8000/community/posts/$POST_ID/upvote \
  -H "Authorization: Bearer YOUR_TOKEN"

# Step 4: View the post with comments
curl -X GET http://localhost:8000/community/posts/$POST_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Search and Bookmark Resources

```bash
# Step 1: Search for resources by tags
curl -X GET "http://localhost:8000/community/resources?tags=culture,adaptation" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Step 2: Bookmark a resource
RESOURCE_ID="123e4567-e89b-12d3-a456-426614174004"
curl -X POST http://localhost:8000/community/resources/$RESOURCE_ID/bookmark \
  -H "Authorization: Bearer YOUR_TOKEN"

# Step 3: View all your bookmarks
curl -X GET http://localhost:8000/community/bookmarks \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Browse Different Post Types

```bash
# Get all discussions
curl -X GET "http://localhost:8000/community/posts?post_type=discussion" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get all questions
curl -X GET "http://localhost:8000/community/posts?post_type=question" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get all announcements
curl -X GET "http://localhost:8000/community/posts?post_type=announcement" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Python Examples

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"
TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Create a post
post_data = {
    "title": "My Python Post",
    "content": "Created using Python requests",
    "post_type": "discussion",
    "is_private": False
}
response = requests.post(f"{BASE_URL}/community/posts", json=post_data, headers=headers)
post = response.json()
print(f"Created post: {post['id']}")

# Add a comment
comment_data = {"content": "Great post!"}
response = requests.post(
    f"{BASE_URL}/community/posts/{post['id']}/comment",
    json=comment_data,
    headers=headers
)
comment = response.json()
print(f"Added comment: {comment['id']}")

# Upvote the post
response = requests.post(
    f"{BASE_URL}/community/posts/{post['id']}/upvote",
    headers=headers
)
result = response.json()
print(f"Post now has {result['upvotes']} upvotes")

# Get all posts
response = requests.get(f"{BASE_URL}/community/posts", headers=headers)
posts = response.json()
print(f"Total posts: {posts['total']}")

# Search resources by tags
response = requests.get(
    f"{BASE_URL}/community/resources",
    params={"tags": "culture,adaptation", "resource_type": "article"},
    headers=headers
)
resources = response.json()
print(f"Found {resources['total']} resources")
```

## Testing with Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Click "Authorize" button
3. Enter your JWT token: `Bearer YOUR_TOKEN`
4. Try out the community endpoints interactively

## Filtering and Pagination

### Pagination

All list endpoints support pagination:

```bash
# Get first page (20 items)
curl -X GET "http://localhost:8000/community/posts?skip=0&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get second page
curl -X GET "http://localhost:8000/community/posts?skip=20&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filtering Posts

```bash
# Filter by post type
curl -X GET "http://localhost:8000/community/posts?post_type=question" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by visibility
curl -X GET "http://localhost:8000/community/posts?is_private=false" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Combine filters
curl -X GET "http://localhost:8000/community/posts?post_type=discussion&is_private=false&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filtering Resources

```bash
# Filter by resource type
curl -X GET "http://localhost:8000/community/resources?resource_type=video" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by tags (OR logic)
curl -X GET "http://localhost:8000/community/resources?tags=culture,expat,adaptation" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Combine filters
curl -X GET "http://localhost:8000/community/resources?resource_type=article&tags=culture" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Response Structure

### Post Response
```json
{
  "id": "uuid",
  "author_id": "uuid",
  "title": "string",
  "content": "string",
  "post_type": "discussion|question|announcement",
  "is_private": false,
  "upvotes": 0,
  "created_at": "2025-11-05T10:30:00Z",
  "updated_at": "2025-11-05T10:30:00Z",
  "author": {
    "id": "uuid",
    "email": "string",
    "role": "client|coach|admin"
  },
  "comment_count": 0
}
```

### Resource Response
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "resource_type": "article|video|document",
  "url": "https://example.com",
  "tags": ["tag1", "tag2"],
  "created_by": "uuid",
  "created_at": "2025-11-05T10:30:00Z",
  "creator": {
    "id": "uuid",
    "email": "string",
    "role": "coach"
  },
  "is_bookmarked": false
}
```

## Error Handling

### Common Errors

**401 Unauthorized**
```json
{"detail": "Not authenticated"}
```
Solution: Include valid JWT token in Authorization header

**404 Not Found**
```json
{"detail": "Post not found"}
```
Solution: Verify the resource ID exists

**409 Conflict**
```json
{"detail": "Resource already bookmarked"}
```
Solution: Check if bookmark already exists before creating

**422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
Solution: Ensure all required fields are provided

## Next Steps

1. **Explore the API**: Try all endpoints in Swagger UI
2. **Read the API Reference**: See `COMMUNITY_API_REFERENCE.md` for detailed documentation
3. **Review Implementation**: See `COMMUNITY_IMPLEMENTATION.md` for technical details
4. **Build Frontend**: Integrate community features into your React/Next.js app

## Troubleshooting

### Posts not appearing
- Check authentication token is valid
- Verify post was created successfully (check response)
- Try listing posts with no filters

### Bookmarks not working
- Ensure resource exists before bookmarking
- Check for duplicate bookmarks (409 error)
- Verify user has permission to bookmark

### Filtering returns no results
- Check filter values match enum types exactly
- Verify tags are spelled correctly
- Try without filters to see all results

## Support

For more information:
- API Reference: `COMMUNITY_API_REFERENCE.md`
- Implementation Details: `COMMUNITY_IMPLEMENTATION.md`
- Main Documentation: `README.md`

## Quick Reference

| Action | Method | Endpoint |
|--------|--------|----------|
| Create post | POST | `/community/posts` |
| List posts | GET | `/community/posts` |
| Get post | GET | `/community/posts/{id}` |
| Upvote post | POST | `/community/posts/{id}/upvote` |
| Add comment | POST | `/community/posts/{id}/comment` |
| Get comments | GET | `/community/posts/{id}/comments` |
| List resources | GET | `/community/resources` |
| Get resource | GET | `/community/resources/{id}` |
| Bookmark | POST | `/community/resources/{id}/bookmark` |
| Remove bookmark | DELETE | `/community/resources/{id}/bookmark` |
| Get bookmarks | GET | `/community/bookmarks` |
