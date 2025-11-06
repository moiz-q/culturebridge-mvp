"""
Health check and monitoring endpoints.

Requirements: 8.5
"""
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import time
from typing import Dict, Any

from app.database import get_db
from app.utils.cache_utils import cache_service
from app.config import settings


router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Comprehensive health check endpoint.
    
    Checks:
    - API responsiveness
    - Database connectivity
    - Redis connectivity
    - Overall system status
    
    Returns 200 if all systems operational, 503 if any critical system is down.
    
    Requirements: 8.5
    """
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    all_healthy = True
    
    # Check database connectivity
    db_healthy, db_details = await _check_database(db)
    health_status["checks"]["database"] = db_details
    if not db_healthy:
        all_healthy = False
    
    # Check Redis connectivity
    redis_healthy, redis_details = await _check_redis()
    health_status["checks"]["redis"] = redis_details
    if not redis_healthy:
        # Redis is not critical, just a warning
        pass
    
    # Check external services (optional, non-blocking)
    health_status["checks"]["external_services"] = {
        "openai": {"configured": bool(settings.OPENAI_API_KEY)},
        "stripe": {"configured": bool(settings.STRIPE_SECRET_KEY)},
        "s3": {"configured": bool(settings.S3_BUCKET_NAME)}
    }
    
    # Calculate response time
    response_time_ms = (time.time() - start_time) * 1000
    health_status["response_time_ms"] = round(response_time_ms, 2)
    
    # Set overall status
    if not all_healthy:
        health_status["status"] = "unhealthy"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=health_status
    )


@router.get("/health/live")
async def liveness_probe() -> Dict[str, str]:
    """
    Kubernetes liveness probe endpoint.
    Returns 200 if the application is running.
    
    Requirements: 8.5
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/ready")
async def readiness_probe(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Kubernetes readiness probe endpoint.
    Returns 200 if the application is ready to serve traffic.
    
    Checks database connectivity before marking as ready.
    
    Requirements: 8.5
    """
    # Check if database is accessible
    db_healthy, _ = await _check_database(db)
    
    if not db_healthy:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "reason": "database_unavailable",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def _check_database(db: Session) -> tuple[bool, Dict[str, Any]]:
    """
    Check database connectivity and performance.
    
    Returns:
        Tuple of (is_healthy, details_dict)
    """
    try:
        start_time = time.time()
        
        # Execute simple query
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        
        query_time_ms = (time.time() - start_time) * 1000
        
        # Check connection pool status
        pool = db.get_bind().pool
        pool_status = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow()
        }
        
        return True, {
            "status": "healthy",
            "query_time_ms": round(query_time_ms, 2),
            "pool": pool_status
        }
    
    except Exception as e:
        return False, {
            "status": "unhealthy",
            "error": str(e)
        }


async def _check_redis() -> tuple[bool, Dict[str, Any]]:
    """
    Check Redis connectivity and performance.
    
    Returns:
        Tuple of (is_healthy, details_dict)
    """
    if not cache_service.is_available:
        return False, {
            "status": "unavailable",
            "message": "Redis client not initialized"
        }
    
    try:
        start_time = time.time()
        
        # Test Redis with ping
        cache_service.redis_client.ping()
        
        ping_time_ms = (time.time() - start_time) * 1000
        
        # Get Redis info
        info = cache_service.redis_client.info()
        
        return True, {
            "status": "healthy",
            "ping_time_ms": round(ping_time_ms, 2),
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "unknown")
        }
    
    except Exception as e:
        return False, {
            "status": "unhealthy",
            "error": str(e)
        }
