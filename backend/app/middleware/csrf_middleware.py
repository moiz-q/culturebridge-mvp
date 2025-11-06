"""
CSRF protection middleware for state-changing operations.
Implements double-submit cookie pattern for CSRF protection.
"""
import secrets
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime

from app.config import settings


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection middleware using double-submit cookie pattern.
    Validates CSRF tokens for state-changing operations (POST, PUT, PATCH, DELETE).
    """
    
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
    CSRF_HEADER_NAME = "X-CSRF-Token"
    CSRF_COOKIE_NAME = "csrf_token"
    
    def __init__(self, app):
        super().__init__(app)
        self.exempt_paths = [
            "/auth/login",
            "/auth/signup",
            "/auth/refresh",
            "/payment/webhook",  # Stripe webhooks don't send CSRF tokens
            "/health",
            "/",
            "/docs",
            "/openapi.json"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip CSRF check for safe methods
        if request.method in self.SAFE_METHODS:
            response = await call_next(request)
            # Set CSRF token cookie for safe requests
            if self.CSRF_COOKIE_NAME not in request.cookies:
                csrf_token = self._generate_csrf_token()
                response.set_cookie(
                    key=self.CSRF_COOKIE_NAME,
                    value=csrf_token,
                    httponly=True,
                    secure=settings.ENVIRONMENT == "production",
                    samesite="strict",
                    max_age=86400  # 24 hours
                )
            return response
        
        # Skip CSRF check for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        
        # Validate CSRF token for state-changing operations
        csrf_token_header = request.headers.get(self.CSRF_HEADER_NAME)
        csrf_token_cookie = request.cookies.get(self.CSRF_COOKIE_NAME)
        
        if not csrf_token_header or not csrf_token_cookie:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": {
                        "code": "CSRF_TOKEN_MISSING",
                        "message": "CSRF token is missing. Include X-CSRF-Token header.",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": getattr(request.state, "request_id", None)
                    }
                }
            )
        
        # Compare tokens using constant-time comparison
        if not secrets.compare_digest(csrf_token_header, csrf_token_cookie):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": {
                        "code": "CSRF_TOKEN_INVALID",
                        "message": "CSRF token validation failed.",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": getattr(request.state, "request_id", None)
                    }
                }
            )
        
        response = await call_next(request)
        return response
    
    def _generate_csrf_token(self) -> str:
        """Generate a secure random CSRF token."""
        return secrets.token_urlsafe(32)
