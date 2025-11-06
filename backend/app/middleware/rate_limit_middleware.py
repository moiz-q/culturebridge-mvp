"""
Rate limiting middleware using Redis for distributed rate limiting.
Implements token bucket algorithm with 100 requests per minute per user.
"""
import time
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
from datetime import datetime

from app.config import settings
from app.exceptions import RateLimitExceeded


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware that limits requests to 100 per minute per user.
    Uses Redis for distributed rate limiting across multiple instances.
    """
    
    def __init__(self, app, redis_client: redis.Redis = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limit = 100  # requests per minute
        self.window = 60  # seconds
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health check and root endpoints
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get user identifier (IP address or user_id from token)
        user_id = self._get_user_identifier(request)
        
        # Check rate limit
        if self.redis_client:
            is_allowed = await self._check_rate_limit(user_id)
            if not is_allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": f"Rate limit exceeded. Maximum {self.rate_limit} requests per minute.",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": getattr(request.state, "request_id", None)
                        }
                    }
                )
        
        response = await call_next(request)
        return response
    
    def _get_user_identifier(self, request: Request) -> str:
        """
        Get user identifier for rate limiting.
        Uses user_id from JWT if available, otherwise uses IP address.
        """
        # Try to get user_id from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    async def _check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user has exceeded rate limit using token bucket algorithm.
        Returns True if request is allowed, False otherwise.
        """
        try:
            key = f"rate_limit:{user_id}"
            current_time = int(time.time())
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove old entries outside the time window
            pipe.zremrangebyscore(key, 0, current_time - self.window)
            
            # Count requests in current window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiry on the key
            pipe.expire(key, self.window)
            
            results = await pipe.execute()
            request_count = results[1]
            
            # Check if under limit
            return request_count < self.rate_limit
            
        except Exception as e:
            # If Redis fails, allow the request (fail open)
            print(f"Rate limit check failed: {e}")
            return True
