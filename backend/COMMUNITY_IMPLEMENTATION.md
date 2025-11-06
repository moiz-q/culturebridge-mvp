# Community Features Implementation

This document describes the implementation of community features including forum posts, comments, resources, and bookmarks.

**Requirements:** 6.1, 6.2, 6.3, 6.4, 6.5

## Overview

The community module provides:
- **Forum Posts**: Discussion, question, and announcement posts with upvoting
- **Comments**: Threaded comments on posts
- **Resource Library**: Curated articles, videos, and documents
- **Bookmarks**: User bookmarking of resources
- **Filtering & Search**: Tag-based filtering and content type filtering
- **Pagination**: All list endpoints support pagination (20 items per page)

## Architecture

### Database Models

Located in `backend/app/models/community.py`:

1. **Post**: Forum posts with title, content, type, visibility, and upvotes
2. **Comment**: Comments on posts with author and timestamp
3. **Resource**: Educational resources with URL, type, tags, and creator
4. **Bookmark**: User bookmarks of resources
5. **MatchCache**: Cached AI match results (separate feature)

### Repositories

Located in `backend/app/repositories/community_repository.py`:

1. **PostRepository**: CRUD operations for posts with filtering by type and visibility
2. **CommentRepository**: CRUD operations for comments with post-based queries
3. **ResourceRepository**: CRUD operations for resources with tag and type filtering
4. **BookmarkRepository**: CRUD operations for bookmarks with user-based queries

### Schemas

Located in `backend/app/schemas/community.py`:

- Request schemas: `PostCreate`, `CommentCreate`, `ResourceCreate`
- Response schemas: `PostResponse`, `CommentResponse`, `ResourceResponse`, `BookmarkResponse`
- List schemas: `PostListResponse`, `CommentListResponse`, `ResourceListResponse`, `BookmarkListResponse`

### API Endpoints

Located in `backend/app/routers/community.py`:

**Posts:**
- `POST /community/posts` - Create post
- `GET /community/posts` - List posts with filters
- `GET /community/posts/{post_id}` - Get post details
- `POST /community/posts/{post_id}/upvote` - Upvote post
- `POST /community/posts/{post_id}/comment` - Add comment
- `GET /community/posts/{post_id}/comments` - Get post comments

**Resources:**
- `GET /community/resources` - List resources with filters
- `GET /community/resources/{resource_id}` - Get resource details
- `POST /community/resources/{resource_id}/bookmark` - Bookmark resource
- `DELETE /community/resources/{resource_id}/bookmark` - Remove bookmark
- `GET /community/bookmarks` - Get user bookmarks

## Key Features

### 1. Forum Posts (Requirements 6.1, 6.4, 6.5)

**Post Types:**
- `discussion`: General discussion posts
- `question`: Question posts
- `announcement`: Announcement posts

**Visibility:**
- Public posts: Visible to all users
- Private posts: Restricted visibility (future: role-based access)

**Engagement:**
- Upvoting: Users can upvote posts
- Comments: Users can comment on posts
- Comment count: Displayed with each post

**Filtering:**
- By post type
- By visibility (public/private)
- Pagination with 20 items per page

### 2. Comments (Requirement 6.1)

**Features:**
- Add comments to any post
- Comments ordered chronologically (oldest first)
- Author information included
- Pagination support

**Data Model:**
```python
class Comment:
    id: UUID
    post_id: UUID
    author_id: UUID
    content: Text
    created_at: DateTime
```

### 3. Resource Library (Requirements 6.2, 6.3)

**Resource Types:**
- `article`: Written content
- `video`: Video content
- `document`: Downloadable documents

**Features:**
- Tag-based filtering (array overlap)
- Content type filtering
- Creator attribution
- Bookmark status for current user
- URL validation (must start with http:// or https://)

**Tag Filtering:**
Resources can have multiple tags. Filtering returns resources that have at least one of the specified tags:
```python
# Filter by tags: "culture,adaptation"
# Returns resources with "culture" OR "adaptation" tag
```

### 4. Bookmarks (Requirement 6.3)

**Features:**
- Bookmark any resource
- View all user bookmarks
- Remove bookmarks
- Unique constraint: One bookmark per user-resource pair
- Bookmark status included in resource responses

**Data Model:**
```python
class Bookmark:
    id: UUID
    user_id: UUID
    resource_id: UUID
    created_at: DateTime
    # Unique constraint on (user_id, resource_id)
```

## Implementation Details

### Pagination

All list endpoints follow the same pagination pattern:
- Default: 20 items per page
- Maximum: 100 items per page
- Query parameters: `skip` (offset) and `limit` (page size)
- Response includes: `total`, `skip`, `limit`

Example:
```python
@router.get("/posts", response_model=PostListResponse)
def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    ...
):
    posts = post_repo.get_all(skip=skip, limit=limit)
    total = post_repo.count()
    return PostListResponse(posts=posts, total=total, skip=skip, limit=limit)
```

### Filtering

**Posts:**
- `post_type`: Enum filter (discussion, question, announcement)
- `is_private`: Boolean filter

**Resources:**
- `resource_type`: Enum filter (article, video, document)
- `tags`: Array overlap filter (comma-separated string converted to list)

### Author/Creator Information

All responses include author/creator information when available:
```python
response.author = {
    "id": user.id,
    "email": user.email,
    "role": user.role
}
```

### Error Handling

Standard HTTP status codes:
- `200 OK`: Successful GET request
- `201 Created`: Successful POST request
- `204 No Content`: Successful DELETE request
- `404 Not Found`: Resource not found
- `409 Conflict`: Duplicate bookmark
- `422 Validation Error`: Invalid request data

### Database Relationships

**User Model:**
```python
class User:
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    bookmarks = relationship("Bookmark", back_populates="user")
    resources_created = relationship("Resource", back_populates="creator")
```

**Post Model:**
```python
class Post:
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
```

**Resource Model:**
```python
class Resource:
    creator = relationship("User", back_populates="resources_created")
    bookmarks = relationship("Bookmark", back_populates="resource", cascade="all, delete-orphan")
```

## Security

### Authentication
All endpoints require JWT authentication via `get_current_user` dependency.

### Authorization
- Users can create posts, comments, and bookmarks
- Users can only delete their own content (future enhancement)
- Admin role can moderate content (future enhancement)

### Data Validation
- Pydantic schemas validate all input data
- URL validation for resources
- String length constraints
- Enum validation for types

## Testing

### Unit Tests
Test repositories with mocked database:
```python
def test_post_repository_create():
    post = Post(title="Test", content="Content", author_id=user_id)
    created_post = post_repo.create(post)
    assert created_post.id is not None
```

### Integration Tests
Test API endpoints with test database:
```python
def test_create_post_endpoint(client, auth_token):
    response = client.post(
        "/community/posts",
        json={"title": "Test", "content": "Content"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
```

## Performance Considerations

### Database Indexes
- `posts.created_at`: Index for chronological ordering
- `posts.author_id`: Index for author queries
- `comments.post_id`: Index for post comments
- `bookmarks.user_id`: Index for user bookmarks
- `bookmarks.resource_id`: Index for resource bookmarks
- Unique index on `(bookmarks.user_id, bookmarks.resource_id)`

### Query Optimization
- Pagination limits result set size
- Eager loading of relationships where needed
- Array overlap operator for tag filtering (GIN index recommended)

### Caching Opportunities (Future)
- Popular posts (high upvote count)
- Resource library (relatively static)
- User bookmark counts

## Future Enhancements

### Content Moderation
- Admin endpoints to delete posts/comments
- Flagging system for inappropriate content
- Automated content filtering

### Advanced Features
- Post editing
- Comment threading (nested replies)
- Resource ratings/reviews
- Search functionality (full-text search)
- Notifications for comments/replies
- Post categories/topics
- User following/subscriptions

### Analytics
- Most popular posts
- Most bookmarked resources
- User engagement metrics
- Content type distribution

## API Usage Examples

### Create a Discussion Post
```bash
curl -X POST http://localhost:8000/community/posts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tips for adapting to Japanese culture",
    "content": "I recently moved to Tokyo and wanted to share...",
    "post_type": "discussion",
    "is_private": false
  }'
```

### Get Posts with Filters
```bash
curl -X GET "http://localhost:8000/community/posts?post_type=question&limit=10" \
  -H "Authorization: Bearer <token>"
```

### Bookmark a Resource
```bash
curl -X POST http://localhost:8000/community/resources/{resource_id}/bookmark \
  -H "Authorization: Bearer <token>"
```

### Search Resources by Tags
```bash
curl -X GET "http://localhost:8000/community/resources?tags=culture,adaptation&resource_type=article" \
  -H "Authorization: Bearer <token>"
```

## Troubleshooting

### Common Issues

**Issue: Bookmark already exists**
- Error: 409 Conflict
- Solution: Check if bookmark exists before creating

**Issue: Post not found**
- Error: 404 Not Found
- Solution: Verify post_id is correct and post exists

**Issue: Tag filtering returns no results**
- Check tag spelling and case sensitivity
- Verify resources have the specified tags

**Issue: Pagination not working**
- Ensure skip and limit parameters are within valid ranges
- Check total count to verify expected results

## Database Schema

### Posts Table
```sql
CREATE TABLE posts (
    id UUID PRIMARY KEY,
    author_id UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    post_type VARCHAR(20) NOT NULL,
    is_private BOOLEAN DEFAULT false,
    upvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_posts_created_at ON posts(created_at);
CREATE INDEX idx_posts_author_id ON posts(author_id);
```

### Comments Table
```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY,
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_comments_post_id ON comments(post_id);
```

### Resources Table
```sql
CREATE TABLE resources (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    resource_type VARCHAR(20) NOT NULL,
    url VARCHAR(500) NOT NULL,
    tags TEXT[],
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_resources_tags ON resources USING GIN(tags);
```

### Bookmarks Table
```sql
CREATE TABLE bookmarks (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    resource_id UUID REFERENCES resources(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, resource_id)
);
CREATE INDEX idx_bookmarks_user_id ON bookmarks(user_id);
CREATE INDEX idx_bookmarks_resource_id ON bookmarks(resource_id);
```

## Conclusion

The community features implementation provides a complete forum and resource library system with:
- ✅ Forum posts with multiple types
- ✅ Comments on posts
- ✅ Upvoting functionality
- ✅ Resource library with tags
- ✅ Bookmark system
- ✅ Filtering and pagination
- ✅ Public and private content support

All requirements (6.1, 6.2, 6.3, 6.4, 6.5) have been successfully implemented.
