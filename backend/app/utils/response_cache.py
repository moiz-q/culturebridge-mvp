"""
API response caching decorator using Redis.
Caches GET endpoint responses to improve performance.
"""
import hashlib
import json
from functools import wraps
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.utils.cache_utils import cache_service


def cache_response(
    ttl_seconds: int = 300,  # 5 minutes default
    key_prefix: Optional[str] = None,
    include_query_params: bool = True,
    include_user_id: bool = False
):
    """
    Decorator to cache API responses in Redis.
    
    Args:
        ttl_seconds: Time to live in seconds (default 5 minutes)
        key_prefix: Optional prefix for cache key
        include_query_params: Include query parameters in cache key
        include_user_id: Include user ID in cache key for user-specific caching
        
    Usage:
        @router.get("/coaches")
        @cache_response(ttl_seconds=300, key_prefix="coaches_list")
        async def get_coaches(request: Request):
            # ... endpoint logic
            return coaches
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Only cache if Redis is available
            if not cache_service.is_available:
                return await func(*args, **kwargs)
            
            # Extract request from kwargs
            request = kwargs.get('request') or next((arg for arg in args if isinstance(arg, Request)), None)
            
            if not request:
                # No request object, skip caching
                return await func(*args, **kwargs)
            
            # Only cache GET requests
            if request.method != "GET":
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = _generate_cache_key(
                request=request,
                key_prefix=key_prefix or func.__name__,
                include_query_params=include_query_params,
                include_user_id=include_user_id
            )
            
            # Try to get from cache
            cached_response = cache_service.get(cache_key)
            if cached_response is not None:
                # Return cached response
                return JSONResponse(
                    content=cached_response,
                    headers={"X-Cache": "HIT"}
                )
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache the result if it's a successful response
            if result is not None:
                # Extract response data
                if isinstance(result, Response):
                    # Don't cache Response objects, only dict/list
                    return result
                
                # Cache the result
                cache_service.set(cache_key, result, ttl_seconds=ttl_seconds)
                
                # Return with cache miss header
                if isinstance(result, dict) or isinstance(result, list):
                    return JSONResponse(
                        content=result,
                        headers={"X-Cache": "MISS"}
                    )
            
            return result
        
        return wrapper
    return decorator


def _generate_cache_key(
    request: Request,
    key_prefix: str,
    include_query_params: bool,
    include_user_id: bool
) -> str:
    """
    Generate a cache key based on request parameters.
    
    Args:
        request: FastAPI request object
        key_prefix: Prefix for the cache key
        include_query_params: Include query parameters in key
        include_user_id: Include user ID in key
        
    Returns:
        Cache key string
    """
    key_parts = [f"api_cache:{key_prefix}"]
    
    # Add path
    key_parts.append(request.url.path)
    
    # Add query parameters
    if include_query_params and request.query_params:
        # Sort query params for consistent cache keys
        sorted_params = sorted(request.query_params.items())
        params_str = json.dumps(sorted_params)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        key_parts.append(params_hash)
    
    # Add user ID if requested
    if include_user_id:
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            key_parts.append(str(user_id))
    
    return ":".join(key_parts)


def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate all cache entries matching a pattern.
    
    Args:
        pattern: Cache key pattern (e.g., "api_cache:coaches_list:*")
        
    Returns:
        Number of cache entries deleted
    """
    return cache_service.delete_pattern(pattern)


def invalidate_endpoint_cache(endpoint_name: str) -> int:
    """
    Invalidate all cache entries for a specific endpoint.
    
    Args:
        endpoint_name: Name of the endpoint (e.g., "get_coaches")
        
    Returns:
        Number of cache entries deleted
    """
    pattern = f"api_cache:{endpoint_name}:*"
    return cache_service.delete_pattern(pattern)
