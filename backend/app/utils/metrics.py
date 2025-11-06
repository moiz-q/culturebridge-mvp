"""
Metrics collection and CloudWatch integration for monitoring.

Requirements: 8.5
"""
import time
from typing import Optional, Dict, Any
from datetime import datetime
from functools import wraps
import logging

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from app.config import settings


logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and publishes application metrics to CloudWatch.
    """
    
    def __init__(self):
        self.cloudwatch = None
        self.namespace = "CultureBridge/API"
        
        if BOTO3_AVAILABLE and settings.ENVIRONMENT == "production":
            try:
                self.cloudwatch = boto3.client(
                    'cloudwatch',
                    region_name=settings.AWS_REGION
                )
            except Exception as e:
                logger.warning(f"Could not initialize CloudWatch client: {e}")
    
    def record_api_latency(
        self,
        endpoint: str,
        method: str,
        latency_ms: float,
        status_code: int
    ):
        """
        Record API endpoint latency.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            latency_ms: Response time in milliseconds
            status_code: HTTP status code
        """
        if not self.cloudwatch:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'APILatency',
                        'Value': latency_ms,
                        'Unit': 'Milliseconds',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {'Name': 'Endpoint', 'Value': endpoint},
                            {'Name': 'Method', 'Value': method},
                            {'Name': 'StatusCode', 'Value': str(status_code)}
                        ]
                    }
                ]
            )
        except ClientError as e:
            logger.error(f"Failed to publish latency metric: {e}")
    
    def record_error_rate(
        self,
        endpoint: str,
        error_type: str,
        count: int = 1
    ):
        """
        Record API error occurrence.
        
        Args:
            endpoint: API endpoint path
            error_type: Type of error (4xx, 5xx, etc.)
            count: Number of errors (default 1)
        """
        if not self.cloudwatch:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'ErrorCount',
                        'Value': count,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {'Name': 'Endpoint', 'Value': endpoint},
                            {'Name': 'ErrorType', 'Value': error_type}
                        ]
                    }
                ]
            )
        except ClientError as e:
            logger.error(f"Failed to publish error metric: {e}")
    
    def record_request_count(
        self,
        endpoint: str,
        method: str,
        count: int = 1
    ):
        """
        Record API request count.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            count: Number of requests (default 1)
        """
        if not self.cloudwatch:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'RequestCount',
                        'Value': count,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {'Name': 'Endpoint', 'Value': endpoint},
                            {'Name': 'Method', 'Value': method}
                        ]
                    }
                ]
            )
        except ClientError as e:
            logger.error(f"Failed to publish request count metric: {e}")
    
    def record_database_query_time(
        self,
        query_type: str,
        duration_ms: float
    ):
        """
        Record database query execution time.
        
        Args:
            query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
            duration_ms: Query duration in milliseconds
        """
        if not self.cloudwatch:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'DatabaseQueryTime',
                        'Value': duration_ms,
                        'Unit': 'Milliseconds',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {'Name': 'QueryType', 'Value': query_type}
                        ]
                    }
                ]
            )
        except ClientError as e:
            logger.error(f"Failed to publish database metric: {e}")
    
    def record_cache_hit_rate(
        self,
        cache_type: str,
        hit: bool
    ):
        """
        Record cache hit or miss.
        
        Args:
            cache_type: Type of cache (match, api_response, etc.)
            hit: True if cache hit, False if miss
        """
        if not self.cloudwatch:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'CacheHit' if hit else 'CacheMiss',
                        'Value': 1,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {'Name': 'CacheType', 'Value': cache_type}
                        ]
                    }
                ]
            )
        except ClientError as e:
            logger.error(f"Failed to publish cache metric: {e}")
    
    def record_external_service_latency(
        self,
        service_name: str,
        operation: str,
        latency_ms: float,
        success: bool
    ):
        """
        Record external service call latency.
        
        Args:
            service_name: Name of external service (OpenAI, Stripe, etc.)
            operation: Operation performed
            latency_ms: Call duration in milliseconds
            success: Whether the call succeeded
        """
        if not self.cloudwatch:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'ExternalServiceLatency',
                        'Value': latency_ms,
                        'Unit': 'Milliseconds',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {'Name': 'Service', 'Value': service_name},
                            {'Name': 'Operation', 'Value': operation},
                            {'Name': 'Success', 'Value': str(success)}
                        ]
                    }
                ]
            )
        except ClientError as e:
            logger.error(f"Failed to publish external service metric: {e}")


# Global metrics collector instance
metrics_collector = MetricsCollector()


def track_latency(endpoint_name: Optional[str] = None):
    """
    Decorator to track endpoint latency.
    
    Usage:
        @track_latency("get_coaches")
        async def get_coaches():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000
                
                # Record successful request
                endpoint = endpoint_name or func.__name__
                metrics_collector.record_api_latency(
                    endpoint=endpoint,
                    method="GET",  # Default, can be enhanced
                    latency_ms=latency_ms,
                    status_code=200
                )
                
                return result
            
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                
                # Record failed request
                endpoint = endpoint_name or func.__name__
                metrics_collector.record_api_latency(
                    endpoint=endpoint,
                    method="GET",
                    latency_ms=latency_ms,
                    status_code=500
                )
                metrics_collector.record_error_rate(
                    endpoint=endpoint,
                    error_type="5xx"
                )
                
                raise
        
        return wrapper
    return decorator


def track_external_call(service_name: str, operation: str):
    """
    Decorator to track external service calls.
    
    Usage:
        @track_external_call("OpenAI", "generate_embeddings")
        async def call_openai():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000
                
                metrics_collector.record_external_service_latency(
                    service_name=service_name,
                    operation=operation,
                    latency_ms=latency_ms,
                    success=True
                )
                
                return result
            
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                
                metrics_collector.record_external_service_latency(
                    service_name=service_name,
                    operation=operation,
                    latency_ms=latency_ms,
                    success=False
                )
                
                raise
        
        return wrapper
    return decorator
