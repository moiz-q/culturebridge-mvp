# Community API Reference

This document provides detailed API reference for the community features including forum posts, comments, resources, and bookmarks.

**Requirements:** 6.1, 6.2, 6.3, 6.4, 6.5

## Base URL

All endpoints are prefixed with `/community`

## Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

---

## Forum Posts

### Create Post

Create a new forum post.

**Endpoint:** `POST /community/posts`

**Request Body:**
```json
{
  "title": "My First Post",
  "content": "This is the content of my post...",
  "post_type": "discussion",  // "discussion", "question", or "announcement"
  "is_private": false
}
```

**Response:** `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "author_id": "123e4567-e89b-12d3-a456-426614174001",
  "title": "My First Post",
  "content": "This is the content of my post...",
  "post_type": "discussion",
  "is_private": false,
  "upvotes": 0,
  "created_at": "2025-11-05T10:30:00Z",
  "updated_at": "2025-11-05T10:30:00Z",
  "author": {
    "id": "123e4567-e89b-12d3-a456-426614174001",
    "email": "user@example.com",
    "role": "client"
  },
  "comment_count": 0
}
```

---

### Get Posts

Get all forum posts with pagination and filters.

**Endpoint:** `GET /community/posts`

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 20, max: 100)
- `post_type` (string, optional): Filter by post type ("discussion", "question", "announcement")
- `is_private` (boolean, optional): Filter by visibility

**Response:** `200 OK`
```json
{
  "posts": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "author_id": "123e4567-e89b-12d3-a456-426614174001",
      "title": "My First Post",
      "content": "This is the content of my post...",
      "post_type": "discussion",
      "is_private": false,
      "upvotes": 5,
      "created_at": "2025-11-05T10:30:00Z",
      "updated_at": "2025-11-05T10:30:00Z",
      "author": {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "email": "user@example.com",
        "role": "client"
      },
      "comment_count": 3
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 20
}
```

---

### Get Post by ID

Get a specific post by ID.

**Endpoint:** `GET /community/posts/{post_id}`

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "author_id": "123e4567-e89b-12d3-a456-426614174001",
  "title": "My First Post",
  "content": "This is the content of my post...",
  "post_type": "discussion",
  "is_private": false,
  "upvotes": 5,
  "created_at": "2025-11-05T10:30:00Z",
  "updated_at": "2025-11-05T10:30:00Z",
  "author": {
    "id": "123e4567-e89b-12d3-a456-426614174001",
    "email": "user@example.com",
    "role": "client"
  },
  "comment_count": 3
}
```

**Error Responses:**
- `404 Not Found`: Post not found

---

### Upvote Post

Upvote a post.

**Endpoint:** `POST /community/posts/{post_id}/upvote`

**Response:** `200 OK`
```json
{
  "post_id": "123e4567-e89b-12d3-a456-426614174000",
  "upvotes": 6,
  "message": "Post upvoted successfully"
}
```

**Error Responses:**
- `404 Not Found`: Post not found

---

## Comments

### Create Comment

Add a comment to a post.

**Endpoint:** `POST /community/posts/{post_id}/comment`

**Request Body:**
```json
{
  "content": "Great post! I totally agree with your points."
}
```

**Response:** `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "post_id": "123e4567-e89b-12d3-a456-426614174000",
  "author_id": "123e4567-e89b-12d3-a456-426614174003",
  "content": "Great post! I totally agree with your points.",
  "created_at": "2025-11-05T10:35:00Z",
  "author": {
    "id": "123e4567-e89b-12d3-a456-426614174003",
    "email": "commenter@example.com",
    "role": "coach"
  }
}
```

**Error Responses:**
- `404 Not Found`: Post not found

---

### Get Post Comments

Get all comments for a specific post.

**Endpoint:** `GET /community/posts/{post_id}/comments`

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 20, max: 100)

**Response:** `200 OK`
```json
{
  "comments": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174002",
      "post_id": "123e4567-e89b-12d3-a456-426614174000",
      "author_id": "123e4567-e89b-12d3-a456-426614174003",
      "content": "Great post! I totally agree with your points.",
      "created_at": "2025-11-05T10:35:00Z",
      "author": {
        "id": "123e4567-e89b-12d3-a456-426614174003",
        "email": "commenter@example.com",
        "role": "coach"
      }
    }
  ],
  "total": 3,
  "skip": 0,
  "limit": 20
}
```

**Error Responses:**
- `404 Not Found`: Post not found

---

## Resources

### Get Resources

Get all resources with pagination and filters.

**Endpoint:** `GET /community/resources`

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 20, max: 100)
- `resource_type` (string, optional): Filter by resource type ("article", "video", "document")
- `tags` (string, optional): Comma-separated list of tags to filter by

**Response:** `200 OK`
```json
{
  "resources": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174004",
      "title": "Cultural Adaptation Guide",
      "description": "A comprehensive guide to adapting to new cultures",
      "resource_type": "article",
      "url": "https://example.com/guide",
      "tags": ["culture", "adaptation", "expat"],
      "created_by": "123e4567-e89b-12d3-a456-426614174005",
      "created_at": "2025-11-05T09:00:00Z",
      "creator": {
        "id": "123e4567-e89b-12d3-a456-426614174005",
        "email": "creator@example.com",
        "role": "coach"
      },
      "is_bookmarked": false
    }
  ],
  "total": 25,
  "skip": 0,
  "limit": 20
}
```

---

### Get Resource by ID

Get a specific resource by ID.

**Endpoint:** `GET /community/resources/{resource_id}`

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174004",
  "title": "Cultural Adaptation Guide",
  "description": "A comprehensive guide to adapting to new cultures",
  "resource_type": "article",
  "url": "https://example.com/guide",
  "tags": ["culture", "adaptation", "expat"],
  "created_by": "123e4567-e89b-12d3-a456-426614174005",
  "created_at": "2025-11-05T09:00:00Z",
  "creator": {
    "id": "123e4567-e89b-12d3-a456-426614174005",
    "email": "creator@example.com",
    "role": "coach"
  },
  "is_bookmarked": false
}
```

**Error Responses:**
- `404 Not Found`: Resource not found

---

### Bookmark Resource

Bookmark a resource.

**Endpoint:** `POST /community/resources/{resource_id}/bookmark`

**Response:** `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174006",
  "user_id": "123e4567-e89b-12d3-a456-426614174001",
  "resource_id": "123e4567-e89b-12d3-a456-426614174004",
  "created_at": "2025-11-05T10:40:00Z",
  "resource": {
    "id": "123e4567-e89b-12d3-a456-426614174004",
    "title": "Cultural Adaptation Guide",
    "description": "A comprehensive guide to adapting to new cultures",
    "resource_type": "article",
    "url": "https://example.com/guide",
    "tags": ["culture", "adaptation", "expat"],
    "created_by": "123e4567-e89b-12d3-a456-426614174005",
    "created_at": "2025-11-05T09:00:00Z"
  }
}
```

**Error Responses:**
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already bookmarked

---

### Remove Bookmark

Remove a bookmark from a resource.

**Endpoint:** `DELETE /community/resources/{resource_id}/bookmark`

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found`: Bookmark not found

---

### Get User Bookmarks

Get all bookmarks for the current user.

**Endpoint:** `GET /community/bookmarks`

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 20, max: 100)

**Response:** `200 OK`
```json
{
  "bookmarks": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174006",
      "user_id": "123e4567-e89b-12d3-a456-426614174001",
      "resource_id": "123e4567-e89b-12d3-a456-426614174004",
      "created_at": "2025-11-05T10:40:00Z",
      "resource": {
        "id": "123e4567-e89b-12d3-a456-426614174004",
        "title": "Cultural Adaptation Guide",
        "description": "A comprehensive guide to adapting to new cultures",
        "resource_type": "article",
        "url": "https://example.com/guide",
        "tags": ["culture", "adaptation", "expat"],
        "created_by": "123e4567-e89b-12d3-a456-426614174005",
        "created_at": "2025-11-05T09:00:00Z",
        "creator": {
          "id": "123e4567-e89b-12d3-a456-426614174005",
          "email": "creator@example.com",
          "role": "coach"
        }
      }
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 20
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 422 Validation Error
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

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Pagination

All list endpoints support pagination with the following parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 20, max: 100)

The response includes:
- `total`: Total number of records matching the filters
- `skip`: Number of records skipped
- `limit`: Maximum number of records returned

---

## Filtering

### Posts
- `post_type`: Filter by post type ("discussion", "question", "announcement")
- `is_private`: Filter by visibility (true for private, false for public)

### Resources
- `resource_type`: Filter by resource type ("article", "video", "document")
- `tags`: Comma-separated list of tags (resources with at least one matching tag)

---

## Data Models

### Post Types
- `discussion`: General discussion post
- `question`: Question post
- `announcement`: Announcement post

### Resource Types
- `article`: Written article or blog post
- `video`: Video content
- `document`: Downloadable document (PDF, etc.)

### User Roles
- `client`: Client seeking coaching
- `coach`: Coach providing services
- `admin`: Platform administrator
