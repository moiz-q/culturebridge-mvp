"""
Community API endpoints for forum posts, comments, resources, and bookmarks.

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_role
from app.models.user import User
from app.models.community import Post, Comment, Resource, Bookmark, PostType, ResourceType
from app.repositories.community_repository import (
    PostRepository,
    CommentRepository,
    ResourceRepository,
    BookmarkRepository
)
from app.schemas.community import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListResponse,
    CommentCreate,
    CommentResponse,
    CommentListResponse,
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    ResourceListResponse,
    BookmarkResponse,
    BookmarkListResponse,
    UpvoteResponse
)

router = APIRouter(prefix="/community", tags=["community"])


# ============================================================================
# Post Endpoints
# ============================================================================

@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new forum post.
    
    Requirements: 6.1, 6.4
    """
    post_repo = PostRepository(db)
    
    # Create new post
    new_post = Post(
        author_id=current_user.id,
        title=post_data.title,
        content=post_data.content,
        post_type=post_data.post_type,
        is_private=post_data.is_private
    )
    
    created_post = post_repo.create(new_post)
    
    # Return response with author info
    response = PostResponse.from_orm(created_post)
    response.author = {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }
    response.comment_count = 0
    
    return response


@router.get("/posts", response_model=PostListResponse)
def get_posts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    post_type: Optional[PostType] = Query(None, description="Filter by post type"),
    is_private: Optional[bool] = Query(None, description="Filter by visibility"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all forum posts with pagination and filters.
    
    Requirements: 6.1, 6.5
    """
    post_repo = PostRepository(db)
    comment_repo = CommentRepository(db)
    
    # Get posts
    posts = post_repo.get_all(
        skip=skip,
        limit=limit,
        post_type=post_type,
        is_private=is_private
    )
    
    # Get total count
    total = post_repo.count(
        post_type=post_type,
        is_private=is_private
    )
    
    # Build response with author info and comment counts
    post_responses = []
    for post in posts:
        response = PostResponse.from_orm(post)
        if post.author:
            response.author = {
                "id": post.author.id,
                "email": post.author.email,
                "role": post.author.role
            }
        response.comment_count = comment_repo.count_by_post_id(post.id)
        post_responses.append(response)
    
    return PostListResponse(
        posts=post_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific post by ID.
    
    Requirements: 6.1
    """
    post_repo = PostRepository(db)
    comment_repo = CommentRepository(db)
    
    # Get post
    post = post_repo.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Build response with author info and comment count
    response = PostResponse.from_orm(post)
    if post.author:
        response.author = {
            "id": post.author.id,
            "email": post.author.email,
            "role": post.author.role
        }
    response.comment_count = comment_repo.count_by_post_id(post.id)
    
    return response


@router.post("/posts/{post_id}/comment", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: UUID,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a comment to a post.
    
    Requirements: 6.1
    """
    post_repo = PostRepository(db)
    comment_repo = CommentRepository(db)
    
    # Check if post exists
    post = post_repo.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Create new comment
    new_comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        content=comment_data.content
    )
    
    created_comment = comment_repo.create(new_comment)
    
    # Return response with author info
    response = CommentResponse.from_orm(created_comment)
    response.author = {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }
    
    return response


@router.get("/posts/{post_id}/comments", response_model=CommentListResponse)
def get_post_comments(
    post_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all comments for a specific post.
    
    Requirements: 6.1
    """
    post_repo = PostRepository(db)
    comment_repo = CommentRepository(db)
    
    # Check if post exists
    post = post_repo.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Get comments
    comments = comment_repo.get_by_post_id(post_id, skip=skip, limit=limit)
    total = comment_repo.count_by_post_id(post_id)
    
    # Build response with author info
    comment_responses = []
    for comment in comments:
        response = CommentResponse.from_orm(comment)
        if comment.author:
            response.author = {
                "id": comment.author.id,
                "email": comment.author.email,
                "role": comment.author.role
            }
        comment_responses.append(response)
    
    return CommentListResponse(
        comments=comment_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/posts/{post_id}/upvote", response_model=UpvoteResponse)
def upvote_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upvote a post.
    
    Requirements: 6.2
    """
    post_repo = PostRepository(db)
    
    # Get post
    post = post_repo.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Increment upvotes
    post.increment_upvotes()
    updated_post = post_repo.update(post)
    
    return UpvoteResponse(
        post_id=updated_post.id,
        upvotes=updated_post.upvotes,
        message="Post upvoted successfully"
    )


# ============================================================================
# Resource Endpoints
# ============================================================================

@router.get("/resources", response_model=ResourceListResponse)
def get_resources(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    resource_type: Optional[ResourceType] = Query(None, description="Filter by resource type"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags to filter by"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all resources with pagination and filters.
    
    Requirements: 6.2, 6.3
    """
    resource_repo = ResourceRepository(db)
    bookmark_repo = BookmarkRepository(db)
    
    # Parse tags if provided
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # Get resources
    resources = resource_repo.get_all(
        skip=skip,
        limit=limit,
        resource_type=resource_type,
        tags=tag_list
    )
    
    # Get total count
    total = resource_repo.count(
        resource_type=resource_type,
        tags=tag_list
    )
    
    # Build response with creator info and bookmark status
    resource_responses = []
    for resource in resources:
        response = ResourceResponse.from_orm(resource)
        if resource.creator:
            response.creator = {
                "id": resource.creator.id,
                "email": resource.creator.email,
                "role": resource.creator.role
            }
        # Check if current user has bookmarked this resource
        response.is_bookmarked = bookmark_repo.exists(current_user.id, resource.id)
        resource_responses.append(response)
    
    return ResourceListResponse(
        resources=resource_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/resources/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific resource by ID.
    
    Requirements: 6.2
    """
    resource_repo = ResourceRepository(db)
    bookmark_repo = BookmarkRepository(db)
    
    # Get resource
    resource = resource_repo.get_by_id(resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Build response with creator info and bookmark status
    response = ResourceResponse.from_orm(resource)
    if resource.creator:
        response.creator = {
            "id": resource.creator.id,
            "email": resource.creator.email,
            "role": resource.creator.role
        }
    response.is_bookmarked = bookmark_repo.exists(current_user.id, resource.id)
    
    return response


@router.post("/resources/{resource_id}/bookmark", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
def bookmark_resource(
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bookmark a resource.
    
    Requirements: 6.3
    """
    resource_repo = ResourceRepository(db)
    bookmark_repo = BookmarkRepository(db)
    
    # Check if resource exists
    resource = resource_repo.get_by_id(resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Check if bookmark already exists
    existing_bookmark = bookmark_repo.get_by_user_and_resource(current_user.id, resource_id)
    if existing_bookmark:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resource already bookmarked"
        )
    
    # Create new bookmark
    new_bookmark = Bookmark(
        user_id=current_user.id,
        resource_id=resource_id
    )
    
    created_bookmark = bookmark_repo.create(new_bookmark)
    
    # Return response with resource info
    response = BookmarkResponse.from_orm(created_bookmark)
    response.resource = ResourceResponse.from_orm(resource)
    
    return response


@router.delete("/resources/{resource_id}/bookmark", status_code=status.HTTP_204_NO_CONTENT)
def remove_bookmark(
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a bookmark from a resource.
    
    Requirements: 6.3
    """
    bookmark_repo = BookmarkRepository(db)
    
    # Get bookmark
    bookmark = bookmark_repo.get_by_user_and_resource(current_user.id, resource_id)
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    # Delete bookmark
    bookmark_repo.delete(bookmark)
    
    return None


@router.get("/bookmarks", response_model=BookmarkListResponse)
def get_user_bookmarks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all bookmarks for the current user.
    
    Requirements: 6.3
    """
    bookmark_repo = BookmarkRepository(db)
    
    # Get bookmarks
    bookmarks = bookmark_repo.get_by_user_id(current_user.id, skip=skip, limit=limit)
    total = bookmark_repo.count_by_user_id(current_user.id)
    
    # Build response with resource info
    bookmark_responses = []
    for bookmark in bookmarks:
        response = BookmarkResponse.from_orm(bookmark)
        if bookmark.resource:
            resource_response = ResourceResponse.from_orm(bookmark.resource)
            if bookmark.resource.creator:
                resource_response.creator = {
                    "id": bookmark.resource.creator.id,
                    "email": bookmark.resource.creator.email,
                    "role": bookmark.resource.creator.role
                }
            response.resource = resource_response
        bookmark_responses.append(response)
    
    return BookmarkListResponse(
        bookmarks=bookmark_responses,
        total=total,
        skip=skip,
        limit=limit
    )
