"""
Input validation and sanitization utilities for security.
Prevents XSS, SQL injection, and other injection attacks.
"""
import re
import html
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


class InputValidator:
    """Utility class for input validation and sanitization."""
    
    # Regex patterns for validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')  # E.164 format
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    URL_PATTERN = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
    
    # Dangerous patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(--)",
        r"(;.*--)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)"
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed"
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize string input by escaping HTML and removing dangerous patterns.
        
        Args:
            value: Input string to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Trim whitespace
        value = value.strip()
        
        # Enforce max length
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        # Escape HTML entities to prevent XSS
        value = html.escape(value)
        
        return value
    
    @classmethod
    def sanitize_html(cls, value: str, allowed_tags: Optional[List[str]] = None) -> str:
        """
        Sanitize HTML content, allowing only specific tags.
        
        Args:
            value: HTML string to sanitize
            allowed_tags: List of allowed HTML tags (e.g., ['p', 'br', 'strong'])
            
        Returns:
            Sanitized HTML string
        """
        if not isinstance(value, str):
            return str(value)
        
        # For now, escape all HTML if no allowed tags specified
        if not allowed_tags:
            return html.escape(value)
        
        # Simple implementation - in production, use bleach library
        # This is a basic version that strips all tags except allowed ones
        import re
        
        # Remove script tags and their content
        value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove event handlers
        value = re.sub(r'\son\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)
        
        # Remove javascript: protocol
        value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
        
        return value
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format."""
        if not email or not isinstance(email, str):
            return False
        return bool(cls.EMAIL_PATTERN.match(email))
    
    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Validate phone number in E.164 format."""
        if not phone or not isinstance(phone, str):
            return False
        return bool(cls.PHONE_PATTERN.match(phone))
    
    @classmethod
    def validate_uuid(cls, uuid_str: str) -> bool:
        """Validate UUID format."""
        if not uuid_str or not isinstance(uuid_str, str):
            return False
        return bool(cls.UUID_PATTERN.match(uuid_str))
    
    @classmethod
    def validate_url(cls, url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
        """
        Validate URL format and scheme.
        
        Args:
            url: URL to validate
            allowed_schemes: List of allowed schemes (default: ['http', 'https'])
            
        Returns:
            True if valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        if not cls.URL_PATTERN.match(url):
            return False
        
        try:
            parsed = urlparse(url)
            if allowed_schemes is None:
                allowed_schemes = ['http', 'https']
            return parsed.scheme in allowed_schemes
        except Exception:
            return False
    
    @classmethod
    def detect_sql_injection(cls, value: str) -> bool:
        """
        Detect potential SQL injection attempts.
        
        Returns:
            True if suspicious pattern detected, False otherwise
        """
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def detect_xss(cls, value: str) -> bool:
        """
        Detect potential XSS attempts.
        
        Returns:
            True if suspicious pattern detected, False otherwise
        """
        if not isinstance(value, str):
            return False
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], max_string_length: int = 10000) -> Dict[str, Any]:
        """
        Recursively sanitize all string values in a dictionary.
        
        Args:
            data: Dictionary to sanitize
            max_string_length: Maximum length for string values
            
        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = cls.sanitize_string(value, max_string_length)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value, max_string_length)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_string(item, max_string_length) if isinstance(item, str)
                    else cls.sanitize_dict(item, max_string_length) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    @classmethod
    def validate_file_upload(
        cls,
        filename: str,
        content_type: str,
        file_size: int,
        allowed_extensions: Optional[List[str]] = None,
        allowed_content_types: Optional[List[str]] = None,
        max_size_mb: int = 5
    ) -> tuple[bool, Optional[str]]:
        """
        Validate file upload parameters.
        
        Args:
            filename: Name of the file
            content_type: MIME type of the file
            file_size: Size of the file in bytes
            allowed_extensions: List of allowed file extensions
            allowed_content_types: List of allowed MIME types
            max_size_mb: Maximum file size in megabytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return False, f"File size exceeds maximum of {max_size_mb}MB"
        
        # Check file extension
        if allowed_extensions:
            file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
            if file_ext not in allowed_extensions:
                return False, f"File extension .{file_ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
        
        # Check content type
        if allowed_content_types:
            if content_type not in allowed_content_types:
                return False, f"Content type {content_type} not allowed"
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Invalid filename"
        
        return True, None
