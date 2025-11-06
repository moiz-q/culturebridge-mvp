"""
Configuration for data migration from Phase 1 to Phase 2.
"""
import os
from typing import Dict, Any


class MigrationConfig:
    """Configuration settings for migration process"""
    
    # Bubble API configuration
    BUBBLE_API_URL = os.getenv("BUBBLE_API_URL", "https://culturebridge-phase1.bubbleapps.io/api/1.1")
    BUBBLE_API_KEY = os.getenv("BUBBLE_API_KEY", "")
    
    # Migration batch size
    BATCH_SIZE = int(os.getenv("MIGRATION_BATCH_SIZE", "100"))
    
    # Export directory for CSV files
    EXPORT_DIR = os.getenv("MIGRATION_EXPORT_DIR", "./migration_data")
    
    # Report directory
    REPORT_DIR = os.getenv("MIGRATION_REPORT_DIR", "./migration_reports")
    
    # Bubble API endpoints
    BUBBLE_ENDPOINTS = {
        "users": "/obj/user",
        "client_profiles": "/obj/client_profile",
        "coach_profiles": "/obj/coach_profile",
        "bookings": "/obj/booking",
        "payments": "/obj/payment",
        "posts": "/obj/post",
        "comments": "/obj/comment",
        "resources": "/obj/resource"
    }
    
    # Field mappings from Phase 1 to Phase 2
    USER_FIELD_MAPPING: Dict[str, str] = {
        "email": "email",
        "password": "password_hash",  # Will be re-hashed
        "type": "role",  # Will be transformed
        "active": "is_active",
        "verified": "email_verified",
        "created_date": "created_at",
        "modified_date": "updated_at"
    }
    
    CLIENT_PROFILE_FIELD_MAPPING: Dict[str, str] = {
        "first_name": "first_name",
        "last_name": "last_name",
        "photo": "photo_url",
        "phone_number": "phone",
        "time_zone": "timezone",
        "quiz_responses": "quiz_data",  # Will be transformed to JSONB
        "user_preferences": "preferences"  # Will be transformed to JSONB
    }
    
    COACH_PROFILE_FIELD_MAPPING: Dict[str, str] = {
        "first_name": "first_name",
        "last_name": "last_name",
        "photo": "photo_url",
        "biography": "bio",
        "video_url": "intro_video_url",
        "expertise_areas": "expertise",  # Will be transformed to array
        "languages_spoken": "languages",  # Will be transformed to array
        "countries_experience": "countries",  # Will be transformed to array
        "rate": "hourly_rate",
        "currency_code": "currency",
        "availability_data": "availability",  # Will be transformed to JSONB
        "average_rating": "rating",
        "session_count": "total_sessions",
        "verified": "is_verified"
    }
    
    BOOKING_FIELD_MAPPING: Dict[str, str] = {
        "client_user_id": "client_id",
        "coach_user_id": "coach_id",
        "session_date": "session_datetime",
        "duration": "duration_minutes",
        "booking_status": "status",
        "payment_ref": "payment_id",
        "meeting_url": "meeting_link",
        "session_notes": "notes",
        "created_date": "created_at",
        "modified_date": "updated_at"
    }
    
    PAYMENT_FIELD_MAPPING: Dict[str, str] = {
        "booking_ref": "booking_id",
        "payment_amount": "amount",
        "currency_code": "currency",
        "payment_status": "status",
        "stripe_session": "stripe_session_id",
        "stripe_intent": "stripe_payment_intent_id",
        "created_date": "created_at",
        "modified_date": "updated_at"
    }
    
    # Role mapping from Phase 1 to Phase 2
    ROLE_MAPPING: Dict[str, str] = {
        "seeker": "client",
        "client": "client",
        "coach": "coach",
        "administrator": "admin",
        "admin": "admin"
    }
    
    # Status mapping for bookings
    BOOKING_STATUS_MAPPING: Dict[str, str] = {
        "pending": "pending",
        "confirmed": "confirmed",
        "complete": "completed",
        "completed": "completed",
        "canceled": "cancelled",
        "cancelled": "cancelled"
    }
    
    # Status mapping for payments
    PAYMENT_STATUS_MAPPING: Dict[str, str] = {
        "pending": "pending",
        "success": "succeeded",
        "succeeded": "succeeded",
        "failed": "failed",
        "refund": "refunded",
        "refunded": "refunded"
    }


config = MigrationConfig()
