"""
Middleware for automatic metrics collection.

Requirements: 8.5
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.metrics import metrics_collector


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically collect metrics for all API requests.
    Tracks latency, request count, and error rates.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics for health check endpoints
        if request.url.path in ["/health", "/health/live", "/health/ready"]:
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            metrics_collector.record_api_latency(
                endpoint=request.url.path,
                method=request.method,
                latency_ms=latency_ms,
                status_code=response.status_code
            )
            
            metrics_collector.record_request_count(
                endpoint=request.url.path,
                method=request.method
            )
            
            # Record errors
            if response.status_code >= 400:
                error_type = "4xx" if response.status_code < 500 else "5xx"
                metrics_collector.record_error_rate(
                    endpoint=request.url.path,
                    error_type=error_type
                )
            
            return response
        
        except Exception as e:
            # Record error metrics
            latency_ms = (time.time() - start_time) * 1000
            
            metrics_collector.record_api_latency(
                endpoint=request.url.path,
                method=request.method,
                latency_ms=latency_ms,
                status_code=500
            )
            
            metrics_collector.record_error_rate(
                endpoint=request.url.path,
                error_type="5xx"
            )
            
            raise
