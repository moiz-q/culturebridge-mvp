"""
Field mapping utilities for transforming Phase 1 data to Phase 2 schema.

Requirements: 10.2
"""
import json
import bcrypt
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from migration.config import config

logger = logging.getLogger(__name__)


class FieldMapper:
    """Utility class for mapping and transforming fields from Phase 1 to Phase 2"""
    
    @staticmethod
    def map_user_fields(phase1_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map user fields from Phase 1 to Phase 2 schema.
        
        Args:
            phase1_data: User data from Phase 1
            
        Returns:
            Mapped user data for Phase 2
        """
        mapped = {}
        
        for phase1_field, phase2_field in config.USER_FIELD_MAPPING.items():
            if phase1_field in phase1_data:
                value = phase1_data[phase1_field]
                
                # Special handling for specific fields
                if phase2_field == "password_hash":
                    # Re-hash password with bcrypt (12 salt rounds)
                    if value:
                        mapped[phase2_field] = FieldMapper.hash_password(value)
                    else:
                        # Generate random password if missing
                        import secrets
                        random_password = secrets.token_urlsafe(16)
                        mapped[phase2_field] = FieldMapper.hash_password(random_password)
                        logger.warning(f"Generated random password for user {phase1_data.get('email')}")
                
                elif phase2_field == "role":
                    # Map role from Phase 1 to Phase 2
                    mapped[phase2_field] = config.ROLE_MAPPING.get(value.lower() if value else "", "client")
                
                elif phase2_field in ["created_at", "updated_at"]:
                    # Parse datetime
                    mapped[phase2_field] = FieldMapper.parse_datetime(value)
                
                else:
                    mapped[phase2_field] = value
        
        # Set defaults for missing fields
        if "is_active" not in mapped:
            mapped["is_active"] = True
        if "email_verified" not in mapped:
            mapped["email_verified"] = False
        
        return mapped
    
    @staticmethod
    def map_client_profile_fields(phase1_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map client profile fields from Phase 1 to Phase 2 schema.
        
        Args:
            phase1_data: Client profile data from Phase 1
            
        Returns:
            Mapped client profile data for Phase 2
        """
        mapped = {}
        
        for phase1_field, phase2_field in config.CLIENT_PROFILE_FIELD_MAPPING.items():
            if phase1_field in phase1_data:
                value = phase1_data[phase1_field]
                
                # Special handling for JSONB fields
                if phase2_field == "quiz_data":
                    mapped[phase2_field] = FieldMapper.parse_json_field(value)
                elif phase2_field == "preferences":
                    mapped[phase2_field] = FieldMapper.parse_json_field(value)
                else:
                    mapped[phase2_field] = value
        
        # Ensure quiz_data exists (required field)
        if "quiz_data" not in mapped or not mapped["quiz_data"]:
            mapped["quiz_data"] = {}
        
        return mapped
    
    @staticmethod
    def map_coach_profile_fields(phase1_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map coach profile fields from Phase 1 to Phase 2 schema.
        
        Args:
            phase1_data: Coach profile data from Phase 1
            
        Returns:
            Mapped coach profile data for Phase 2
        """
        mapped = {}
        
        for phase1_field, phase2_field in config.COACH_PROFILE_FIELD_MAPPING.items():
            if phase1_field in phase1_data:
                value = phase1_data[phase1_field]
                
                # Special handling for array fields
                if phase2_field in ["expertise", "languages", "countries"]:
                    mapped[phase2_field] = FieldMapper.parse_array_field(value)
                
                # Special handling for JSONB fields
                elif phase2_field == "availability":
                    mapped[phase2_field] = FieldMapper.parse_json_field(value)
                
                # Special handling for numeric fields
                elif phase2_field == "hourly_rate":
                    mapped[phase2_field] = FieldMapper.parse_decimal(value)
                elif phase2_field == "rating":
                    mapped[phase2_field] = FieldMapper.parse_decimal(value, default=0.0)
                elif phase2_field == "total_sessions":
                    mapped[phase2_field] = FieldMapper.parse_int(value, default=0)
                
                else:
                    mapped[phase2_field] = value
        
        # Set defaults
        if "currency" not in mapped:
            mapped["currency"] = "USD"
        if "rating" not in mapped:
            mapped["rating"] = 0.0
        if "total_sessions" not in mapped:
            mapped["total_sessions"] = 0
        if "is_verified" not in mapped:
            mapped["is_verified"] = False
        
        return mapped
    
    @staticmethod
    def map_booking_fields(phase1_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map booking fields from Phase 1 to Phase 2 schema.
        
        Args:
            phase1_data: Booking data from Phase 1
            
        Returns:
            Mapped booking data for Phase 2
        """
        mapped = {}
        
        for phase1_field, phase2_field in config.BOOKING_FIELD_MAPPING.items():
            if phase1_field in phase1_data:
                value = phase1_data[phase1_field]
                
                # Special handling for datetime
                if phase2_field == "session_datetime":
                    mapped[phase2_field] = FieldMapper.parse_datetime(value)
                
                # Special handling for status
                elif phase2_field == "status":
                    mapped[phase2_field] = config.BOOKING_STATUS_MAPPING.get(
                        value.lower() if value else "", "pending"
                    )
                
                # Special handling for duration
                elif phase2_field == "duration_minutes":
                    mapped[phase2_field] = FieldMapper.parse_int(value, default=60)
                
                elif phase2_field in ["created_at", "updated_at"]:
                    mapped[phase2_field] = FieldMapper.parse_datetime(value)
                
                else:
                    mapped[phase2_field] = value
        
        # Set defaults
        if "duration_minutes" not in mapped:
            mapped["duration_minutes"] = 60
        if "status" not in mapped:
            mapped["status"] = "pending"
        
        return mapped
    
    @staticmethod
    def map_payment_fields(phase1_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map payment fields from Phase 1 to Phase 2 schema.
        
        Args:
            phase1_data: Payment data from Phase 1
            
        Returns:
            Mapped payment data for Phase 2
        """
        mapped = {}
        
        for phase1_field, phase2_field in config.PAYMENT_FIELD_MAPPING.items():
            if phase1_field in phase1_data:
                value = phase1_data[phase1_field]
                
                # Special handling for amount
                if phase2_field == "amount":
                    mapped[phase2_field] = FieldMapper.parse_decimal(value)
                
                # Special handling for status
                elif phase2_field == "status":
                    mapped[phase2_field] = config.PAYMENT_STATUS_MAPPING.get(
                        value.lower() if value else "", "pending"
                    )
                
                elif phase2_field in ["created_at", "updated_at"]:
                    mapped[phase2_field] = FieldMapper.parse_datetime(value)
                
                else:
                    mapped[phase2_field] = value
        
        # Set defaults
        if "currency" not in mapped:
            mapped["currency"] = "USD"
        if "status" not in mapped:
            mapped["status"] = "pending"
        
        return mapped
    
    # Helper methods
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt with 12 salt rounds.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def parse_datetime(value: Any) -> Optional[datetime]:
        """
        Parse datetime from various formats.
        
        Args:
            value: Datetime value (string or datetime object)
            
        Returns:
            Parsed datetime or None
        """
        if not value:
            return None
        
        if isinstance(value, datetime):
            return value
        
        # Try common datetime formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format with microseconds
            "%Y-%m-%dT%H:%M:%SZ",      # ISO format
            "%Y-%m-%d %H:%M:%S",       # Standard format
            "%Y-%m-%d",                # Date only
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(value), fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse datetime: {value}")
        return None
    
    @staticmethod
    def parse_json_field(value: Any) -> Dict[str, Any]:
        """
        Parse JSON field from string or dict.
        
        Args:
            value: JSON value (string or dict)
            
        Returns:
            Parsed dictionary
        """
        if not value:
            return {}
        
        if isinstance(value, dict):
            return value
        
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse JSON: {value}")
                return {}
        
        return {}
    
    @staticmethod
    def parse_array_field(value: Any) -> List[str]:
        """
        Parse array field from string or list.
        
        Args:
            value: Array value (string, list, or comma-separated)
            
        Returns:
            Parsed list
        """
        if not value:
            return []
        
        if isinstance(value, list):
            return [str(item) for item in value]
        
        if isinstance(value, str):
            # Try parsing as JSON array
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except json.JSONDecodeError:
                pass
            
            # Try comma-separated values
            return [item.strip() for item in value.split(',') if item.strip()]
        
        return []
    
    @staticmethod
    def parse_decimal(value: Any, default: float = 0.0) -> float:
        """
        Parse decimal value.
        
        Args:
            value: Numeric value
            default: Default value if parsing fails
            
        Returns:
            Parsed float
        """
        if value is None:
            return default
        
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse decimal: {value}")
            return default
    
    @staticmethod
    def parse_int(value: Any, default: int = 0) -> int:
        """
        Parse integer value.
        
        Args:
            value: Numeric value
            default: Default value if parsing fails
            
        Returns:
            Parsed integer
        """
        if value is None:
            return default
        
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse integer: {value}")
            return default
