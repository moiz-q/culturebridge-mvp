"""
Custom exception classes for CultureBridge API.

Requirements: 8.3, 8.4
"""
from typing import Optional, Dict, Any


class CultureBridgeException(Exception):
    """Base exception for all CultureBridge errors."""
    
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(CultureBridgeException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class UnauthorizedException(CultureBridgeException):
    """Raised when authentication fails or token is invalid."""
    
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
            details=details
        )


class ForbiddenException(CultureBridgeException):
    """Raised when user lacks permission for the requested resource."""
    
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
            details=details
        )


class NotFoundException(CultureBridgeException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details
        )


class ConflictException(CultureBridgeException):
    """Raised when a resource already exists or conflicts with existing data."""
    
    def __init__(self, message: str = "Resource already exists", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            details=details
        )


class RateLimitException(CultureBridgeException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details
        )


# Alias for compatibility
RateLimitExceeded = RateLimitException


class InternalServerException(CultureBridgeException):
    """Raised for unexpected server errors."""
    
    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="INTERNAL_ERROR",
            status_code=500,
            details=details
        )


class ServiceUnavailableException(CultureBridgeException):
    """Raised when an external service is unavailable."""
    
    def __init__(self, message: str = "Service temporarily unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            status_code=503,
            details=details
        )


class GatewayTimeoutException(CultureBridgeException):
    """Raised when an external service times out."""
    
    def __init__(self, message: str = "External service timeout", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="GATEWAY_TIMEOUT",
            status_code=504,
            details=details
        )
