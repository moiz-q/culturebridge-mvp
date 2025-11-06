from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, ARRAY, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class PostType(str, enum.Enum):
    """Post type enumeration"""
    DISCUSSION = "discussion"
    QUESTION = "question"
    ANNOUNCEMENT = "announcement"


class Post(Base):
    """
    Post model representing forum posts and discussions.
    
    Requirements: 6.1, 6.4, 6.5
    """
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Post content
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    post_type = Column(SQLEnum(PostType), default=PostType.DISCUSSION, nullable=False)
    
    # Visibility and engagement
    is_private = Column(Boolean, default=False, nullable=False)
    upvotes = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title}, author_id={self.author_id})>"

    def is_discussion(self) -> bool:
        """Check if post is a discussion"""
        return self.post_type == PostType.DISCUSSION

    def is_question(self) -> bool:
        """Check if post is a question"""
        return self.post_type == PostType.QUESTION

    def is_announcement(self) -> bool:
        """Check if post is an announcement"""
        return self.post_type == PostType.ANNOUNCEMENT

    def increment_upvotes(self):
        """Increment upvote count"""
        self.upvotes += 1

    def decrement_upvotes(self):
        """Decrement upvote count (minimum 0)"""
        if self.upvotes > 0:
            self.upvotes -= 1


class Comment(Base):
    """
    Comment model representing comments on forum posts.
    
    Requirements: 6.1
    """
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Comment content
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, post_id={self.post_id}, author_id={self.author_id})>"


class ResourceType(str, enum.Enum):
    """Resource type enumeration"""
    ARTICLE = "article"
    VIDEO = "video"
    DOCUMENT = "document"


class Resource(Base):
    """
    Resource model representing educational resources in the library.
    
    Requirements: 6.2, 6.3
    """
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Resource information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    resource_type = Column(SQLEnum(ResourceType), nullable=False)
    url = Column(String(500), nullable=False)
    tags = Column(ARRAY(Text), default=list)
    
    # Creator information
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User", back_populates="resources_created")
    bookmarks = relationship("Bookmark", back_populates="resource", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Resource(id={self.id}, title={self.title}, type={self.resource_type})>"

    def is_article(self) -> bool:
        """Check if resource is an article"""
        return self.resource_type == ResourceType.ARTICLE

    def is_video(self) -> bool:
        """Check if resource is a video"""
        return self.resource_type == ResourceType.VIDEO

    def is_document(self) -> bool:
        """Check if resource is a document"""
        return self.resource_type == ResourceType.DOCUMENT

    def has_tag(self, tag: str) -> bool:
        """Check if resource has a specific tag"""
        return tag in (self.tags or [])


class Bookmark(Base):
    """
    Bookmark model representing user bookmarks of resources.
    
    Requirements: 6.3
    """
    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint('user_id', 'resource_id', name='unique_user_resource_bookmark'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="bookmarks")
    resource = relationship("Resource", back_populates="bookmarks")

    def __repr__(self):
        return f"<Bookmark(id={self.id}, user_id={self.user_id}, resource_id={self.resource_id})>"


class MatchCache(Base):
    """
    MatchCache model for storing AI-generated coach match results.
    
    Requirements: 4.4
    """
    __tablename__ = "match_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Cached match results (JSONB for flexible structure)
    match_results = Column(JSONB, nullable=False)
    
    # Cache expiration
    expires_at = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<MatchCache(id={self.id}, client_id={self.client_id}, expires_at={self.expires_at})>"

    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.utcnow() > self.expires_at
