"""
Redis cache utilities for match results and other cached data.

Requirements: 4.4
"""
import json
from typing import Optional, Any
from datetime import timedelta
import redis
from redis.exceptions import RedisError

from app.config import settings


class CacheService:
    """
    Service for Redis caching operations.
    
    Provides methods for storing and retrieving cached data with TTL support.
    """
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.is_available = True
        except (RedisError, Exception) as e:
            print(f"Redis connection failed: {e}")
            self.redis_client = None
            self.is_available = False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or cache unavailable
        """
        if not self.is_available or not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except (RedisError, json.JSONDecodeError) as e:
            print(f"Cache get error for key {key}: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 86400  # 24 hours default
    ) -> bool:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl_seconds: Time to live in seconds (default 24 hours)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available or not self.redis_client:
            return False
        
        try:
            serialized_value = json.dumps(value)
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl_seconds),
                serialized_value
            )
            return True
        except (RedisError, TypeError, json.JSONEncodeError) as e:
            print(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available or not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except RedisError as e:
            print(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Key pattern (e.g., "match:user_id:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.is_available or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except RedisError as e:
            print(f"Cache delete pattern error for pattern {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        if not self.is_available or not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except RedisError as e:
            print(f"Cache exists error for key {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for a key.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds or None if key doesn't exist or cache unavailable
        """
        if not self.is_available or not self.redis_client:
            return None
        
        try:
            ttl = self.redis_client.ttl(key)
            return ttl if ttl > 0 else None
        except RedisError as e:
            print(f"Cache TTL error for key {key}: {e}")
            return None
    
    def flush_all(self) -> bool:
        """
        Flush all cache data (use with caution).
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available or not self.redis_client:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except RedisError as e:
            print(f"Cache flush error: {e}")
            return False


# Global cache service instance
cache_service = CacheService()


# Convenience functions for match caching

def get_match_cache(cache_key: str) -> Optional[Any]:
    """
    Get cached match results.
    
    Args:
        cache_key: Cache key generated by MatchingService.generate_cache_key()
        
    Returns:
        Cached match results or None
    """
    return cache_service.get(cache_key)


def set_match_cache(
    cache_key: str,
    match_results: Any,
    ttl_hours: int = 24
) -> bool:
    """
    Cache match results with 24-hour TTL.
    
    Args:
        cache_key: Cache key generated by MatchingService.generate_cache_key()
        match_results: Match results to cache
        ttl_hours: Time to live in hours (default 24)
        
    Returns:
        True if successful, False otherwise
    """
    return cache_service.set(cache_key, match_results, ttl_seconds=ttl_hours * 3600)


def invalidate_client_match_cache(client_id: str) -> int:
    """
    Invalidate all match cache entries for a client.
    
    Called when client profile is updated.
    
    Args:
        client_id: Client's user ID
        
    Returns:
        Number of cache entries deleted
    """
    pattern = f"match:{client_id}:*"
    return cache_service.delete_pattern(pattern)


def invalidate_all_match_cache() -> int:
    """
    Invalidate all match cache entries.
    
    Called when coach profiles are updated.
    
    Returns:
        Number of cache entries deleted
    """
    pattern = "match:*"
    return cache_service.delete_pattern(pattern)
