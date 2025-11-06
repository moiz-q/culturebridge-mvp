"""
Retry utilities for external service calls.

Requirements: 8.3, 8.4
"""
import asyncio
import time
from typing import Callable, TypeVar, Optional, Type, Tuple
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        backoff_factor: Multiplier for delay between retries
        exceptions: Tuple of exception types to catch and retry
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                        )
            
            raise last_exception
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                        )
            
            raise last_exception
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_openai(func: Callable[..., T]) -> Callable[..., T]:
    """
    Retry decorator specifically for OpenAI API calls.
    Uses 3 retries with exponential backoff.
    
    Requirements: 8.3
    """
    return retry_with_backoff(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(Exception,)  # Catch all exceptions for OpenAI
    )(func)


def retry_stripe(func: Callable[..., T]) -> Callable[..., T]:
    """
    Retry decorator specifically for Stripe API calls.
    Uses 2 retries with 1 second delay.
    
    Requirements: 8.3
    """
    return retry_with_backoff(
        max_retries=2,
        initial_delay=1.0,
        backoff_factor=1.0,  # Fixed delay
        exceptions=(Exception,)  # Catch all exceptions for Stripe
    )(func)


async def with_timeout(coro, timeout: float, timeout_exception: Optional[Exception] = None):
    """
    Execute a coroutine with a timeout.
    
    Args:
        coro: Coroutine to execute
        timeout: Timeout in seconds
        timeout_exception: Exception to raise on timeout (default: asyncio.TimeoutError)
        
    Returns:
        Result of the coroutine
        
    Raises:
        timeout_exception or asyncio.TimeoutError if timeout is exceeded
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        if timeout_exception:
            raise timeout_exception
        raise
