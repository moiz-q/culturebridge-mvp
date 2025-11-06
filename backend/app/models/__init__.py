"""
SQLAlchemy models for CultureBridge platform.

All models must be imported here for Alembic to detect them during migrations.
"""

from app.models.user import User, UserRole
from app.models.profile import ClientProfile, CoachProfile
from app.models.booking import Booking, BookingStatus, Payment, PaymentStatus
from app.models.community import (
    Post,
    PostType,
    Comment,
    Resource,
    ResourceType,
    Bookmark,
    MatchCache
)

__all__ = [
    # User models
    "User",
    "UserRole",
    
    # Profile models
    "ClientProfile",
    "CoachProfile",
    
    # Booking models
    "Booking",
    "BookingStatus",
    "Payment",
    "PaymentStatus",
    
    # Community models
    "Post",
    "PostType",
    "Comment",
    "Resource",
    "ResourceType",
    "Bookmark",
    "MatchCache",
]
