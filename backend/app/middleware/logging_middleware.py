"""
Logging middleware for request/response tracking.

Requirements: 8.4
"""
import time
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses with timing information.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = time.time()
        
        # Get request details
        request_id = getattr(request.state, "request_id", "unknown")
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        # Extract user ID from request state if available (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        
        # Log incoming request
        logger.info(
            f"{method} {path}",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "endpoint": path,
                "method": method,
                "client_host": client_host,
                "event": "request_started"
            }
        )
        
        # Process request
        try:
            response: Response = await call_next(request)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log response
            logger.info(
                f"{method} {path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "user_id": user_id,
                    "endpoint": path,
                    "method": method,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "event": "request_completed"
                }
            )
            
            # Add duration header
            response.headers["X-Response-Time"] = f"{duration_ms}ms"
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log error
            logger.error(
                f"{method} {path} - Error: {str(e)}",
                extra={
                    "request_id": request_id,
                    "user_id": user_id,
                    "endpoint": path,
                    "method": method,
                    "duration_ms": duration_ms,
                    "event": "request_failed",
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            
            # Re-raise to be handled by error handlers
            raise
