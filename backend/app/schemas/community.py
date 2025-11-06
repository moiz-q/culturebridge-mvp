"""
Pydantic schemas for community features (posts, comments, resources, bookmarks).

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.community import PostType, ResourceType


# ============================================================================
# Post Schemas
# ============================================================================

class PostCreate(BaseModel):
    """Schema for creating a new post"""
    title: str = Field(..., min_length=1, max_length=255, description="Post title")
    content: str = Field(..., min_length=1, description="Post content")
    post_type: PostType = Field(default=PostType.DISCUSSION, description="Type of post")
    is_private: bool = Field(default=False, description="Whether post is private")
    
    class Config:
        use_enum_values = True


class PostUpdate(BaseModel):
    """Schema for updating a post"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Post title")
    content: Optional[str] = Field(None, min_length=1, description="Post content")
    post_type: Optional[PostType] = Field(None, description="Type of post")
    is_private: Optional[bool] = Field(None, description="Whether post is private")
    
    class Config:
        use_enum_values = True


class PostAuthor(BaseModel):
    """Schema for post author information"""
    id: UUID
    email: str
    role: str
    
    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    """Schema for post response"""
    id: UUID
    author_id: UUID
    title: str
    content: str
    post_type: str
    is_private: bool
    upvotes: int
    created_at: datetime
    updated_at: datetime
    author: Optional[PostAuthor] = None
    comment_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """Schema for paginated post list response"""
    posts: List[PostResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# Comment Schemas
# ============================================================================

class CommentCreate(BaseModel):
    """Schema for creating a new comment"""
    content: str = Field(..., min_length=1, description="Comment content")


class CommentAuthor(BaseModel):
    """Schema for comment author information"""
    id: UUID
    email: str
    role: str
    
    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Schema for comment response"""
    id: UUID
    post_id: UUID
    author_id: UUID
    content: str
    created_at: datetime
    author: Optional[CommentAuthor] = None
    
    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """Schema for paginated comment list response"""
    comments: List[CommentResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# Resource Schemas
# ============================================================================

class ResourceCreate(BaseModel):
    """Schema for creating a new resource"""
    title: str = Field(..., min_length=1, max_length=255, description="Resource title")
    description: Optional[str] = Field(None, description="Resource description")
    resource_type: ResourceType = Field(..., description="Type of resource")
    url: str = Field(..., min_length=1, max_length=500, description="Resource URL")
    tags: List[str] = Field(default_factory=list, description="Resource tags")
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    class Config:
        use_enum_values = True


class ResourceUpdate(BaseModel):
    """Schema for updating a resource"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Resource title")
    description: Optional[str] = Field(None, description="Resource description")
    resource_type: Optional[ResourceType] = Field(None, description="Type of resource")
    url: Optional[str] = Field(None, min_length=1, max_length=500, description="Resource URL")
    tags: Optional[List[str]] = Field(None, description="Resource tags")
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format"""
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    class Config:
        use_enum_values = True


class ResourceCreator(BaseModel):
    """Schema for resource creator information"""
    id: UUID
    email: str
    role: str
    
    class Config:
        from_attributes = True


class ResourceResponse(BaseModel):
    """Schema for resource response"""
    id: UUID
    title: str
    description: Optional[str]
    resource_type: str
    url: str
    tags: List[str]
    created_by: Optional[UUID]
    created_at: datetime
    creator: Optional[ResourceCreator] = None
    is_bookmarked: Optional[bool] = None
    
    class Config:
        from_attributes = True


class ResourceListResponse(BaseModel):
    """Schema for paginated resource list response"""
    resources: List[ResourceResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# Bookmark Schemas
# ============================================================================

class BookmarkResponse(BaseModel):
    """Schema for bookmark response"""
    id: UUID
    user_id: UUID
    resource_id: UUID
    created_at: datetime
    resource: Optional[ResourceResponse] = None
    
    class Config:
        from_attributes = True


class BookmarkListResponse(BaseModel):
    """Schema for paginated bookmark list response"""
    bookmarks: List[BookmarkResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# Upvote Schemas
# ============================================================================

class UpvoteResponse(BaseModel):
    """Schema for upvote response"""
    post_id: UUID
    upvotes: int
    message: str
