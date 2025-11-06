"""
Community repositories for CRUD operations on Post, Comment, Resource, and Bookmark models.

Requirements: 6.1, 6.3, 6.5
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.community import Post, Comment, Resource, Bookmark, PostType, ResourceType


class PostRepository:
    """Repository for Post model CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, post: Post) -> Post:
        """Create a new post"""
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post
    
    def get_by_id(self, post_id: UUID) -> Optional[Post]:
        """Get post by ID"""
        return self.db.query(Post).filter(Post.id == post_id).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        post_type: Optional[PostType] = None,
        is_private: Optional[bool] = None,
        author_id: Optional[UUID] = None
    ) -> List[Post]:
        """
        Get all posts with optional filters and pagination.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (default 20)
            post_type: Filter by post type
            is_private: Filter by visibility (True for private, False for public)
            author_id: Filter by author ID
        
        Requirements: 6.1, 6.5
        """
        query = self.db.query(Post)
        
        if post_type:
            query = query.filter(Post.post_type == post_type)
        
        if is_private is not None:
            query = query.filter(Post.is_private == is_private)
        
        if author_id:
            query = query.filter(Post.author_id == author_id)
        
        return query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    
    def count(
        self,
        post_type: Optional[PostType] = None,
        is_private: Optional[bool] = None,
        author_id: Optional[UUID] = None
    ) -> int:
        """Count posts with optional filters"""
        query = self.db.query(Post)
        
        if post_type:
            query = query.filter(Post.post_type == post_type)
        
        if is_private is not None:
            query = query.filter(Post.is_private == is_private)
        
        if author_id:
            query = query.filter(Post.author_id == author_id)
        
        return query.count()
    
    def update(self, post: Post) -> Post:
        """Update post"""
        self.db.commit()
        self.db.refresh(post)
        return post
    
    def delete(self, post: Post) -> None:
        """Delete post"""
        self.db.delete(post)
        self.db.commit()
    
    def exists_by_id(self, post_id: UUID) -> bool:
        """Check if post exists by ID"""
        return self.db.query(Post).filter(Post.id == post_id).count() > 0


class CommentRepository:
    """Repository for Comment model CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, comment: Comment) -> Comment:
        """Create a new comment"""
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment
    
    def get_by_id(self, comment_id: UUID) -> Optional[Comment]:
        """Get comment by ID"""
        return self.db.query(Comment).filter(Comment.id == comment_id).first()
    
    def get_by_post_id(
        self,
        post_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[Comment]:
        """
        Get all comments for a specific post with pagination.
        
        Args:
            post_id: Post ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (default 20)
        
        Requirements: 6.1
        """
        return (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_by_post_id(self, post_id: UUID) -> int:
        """Count comments for a specific post"""
        return self.db.query(Comment).filter(Comment.post_id == post_id).count()
    
    def delete(self, comment: Comment) -> None:
        """Delete comment"""
        self.db.delete(comment)
        self.db.commit()


class ResourceRepository:
    """Repository for Resource model CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, resource: Resource) -> Resource:
        """Create a new resource"""
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        return resource
    
    def get_by_id(self, resource_id: UUID) -> Optional[Resource]:
        """Get resource by ID"""
        return self.db.query(Resource).filter(Resource.id == resource_id).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        resource_type: Optional[ResourceType] = None,
        tags: Optional[List[str]] = None
    ) -> List[Resource]:
        """
        Get all resources with optional filters and pagination.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (default 20)
            resource_type: Filter by resource type
            tags: Filter by tags (resources must have at least one of the provided tags)
        
        Requirements: 6.2, 6.3
        """
        query = self.db.query(Resource)
        
        if resource_type:
            query = query.filter(Resource.resource_type == resource_type)
        
        if tags:
            # Filter resources that have at least one of the provided tags
            query = query.filter(Resource.tags.overlap(tags))
        
        return query.order_by(Resource.created_at.desc()).offset(skip).limit(limit).all()
    
    def count(
        self,
        resource_type: Optional[ResourceType] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """Count resources with optional filters"""
        query = self.db.query(Resource)
        
        if resource_type:
            query = query.filter(Resource.resource_type == resource_type)
        
        if tags:
            query = query.filter(Resource.tags.overlap(tags))
        
        return query.count()
    
    def update(self, resource: Resource) -> Resource:
        """Update resource"""
        self.db.commit()
        self.db.refresh(resource)
        return resource
    
    def delete(self, resource: Resource) -> None:
        """Delete resource"""
        self.db.delete(resource)
        self.db.commit()
    
    def exists_by_id(self, resource_id: UUID) -> bool:
        """Check if resource exists by ID"""
        return self.db.query(Resource).filter(Resource.id == resource_id).count() > 0


class BookmarkRepository:
    """Repository for Bookmark model CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, bookmark: Bookmark) -> Bookmark:
        """Create a new bookmark"""
        self.db.add(bookmark)
        self.db.commit()
        self.db.refresh(bookmark)
        return bookmark
    
    def get_by_id(self, bookmark_id: UUID) -> Optional[Bookmark]:
        """Get bookmark by ID"""
        return self.db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    
    def get_by_user_and_resource(
        self,
        user_id: UUID,
        resource_id: UUID
    ) -> Optional[Bookmark]:
        """Get bookmark by user ID and resource ID"""
        return (
            self.db.query(Bookmark)
            .filter(
                and_(
                    Bookmark.user_id == user_id,
                    Bookmark.resource_id == resource_id
                )
            )
            .first()
        )
    
    def get_by_user_id(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[Bookmark]:
        """
        Get all bookmarks for a specific user with pagination.
        
        Args:
            user_id: User ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (default 20)
        
        Requirements: 6.3
        """
        return (
            self.db.query(Bookmark)
            .filter(Bookmark.user_id == user_id)
            .order_by(Bookmark.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_by_user_id(self, user_id: UUID) -> int:
        """Count bookmarks for a specific user"""
        return self.db.query(Bookmark).filter(Bookmark.user_id == user_id).count()
    
    def delete(self, bookmark: Bookmark) -> None:
        """Delete bookmark"""
        self.db.delete(bookmark)
        self.db.commit()
    
    def exists(self, user_id: UUID, resource_id: UUID) -> bool:
        """Check if bookmark exists for user and resource"""
        return (
            self.db.query(Bookmark)
            .filter(
                and_(
                    Bookmark.user_id == user_id,
                    Bookmark.resource_id == resource_id
                )
            )
            .count() > 0
        )
