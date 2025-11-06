"""
Global error handler for consistent error responses.

Requirements: 8.3, 8.4
"""
from datetime import datetime
from typing import Union
import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import CultureBridgeException

logger = logging.getLogger(__name__)


async def culturebridge_exception_handler(request: Request, exc: CultureBridgeException) -> JSONResponse:
    """
    Handler for custom CultureBridge exceptions.
    
    Args:
        request: FastAPI request object
        exc: CultureBridge exception instance
        
    Returns:
        JSONResponse with error details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    error_response = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id
        }
    }
    
    # Log error
    logger.error(
        f"CultureBridge error: {exc.code} - {exc.message}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    Handler for Pydantic validation errors.
    
    Args:
        request: FastAPI request object
        exc: Validation error instance
        
    Returns:
        JSONResponse with validation error details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Extract validation errors
    errors = []
    if isinstance(exc, RequestValidationError):
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
    else:
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
    
    error_response = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "details": {
                "errors": errors
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id
        }
    }
    
    # Log validation error
    logger.warning(
        f"Validation error: {len(errors)} field(s) failed validation",
        extra={
            "request_id": request_id,
            "errors": errors,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handler for SQLAlchemy database errors.
    
    Args:
        request: FastAPI request object
        exc: SQLAlchemy error instance
        
    Returns:
        JSONResponse with error details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    error_response = {
        "error": {
            "code": "DATABASE_ERROR",
            "message": "A database error occurred",
            "details": {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id
        }
    }
    
    # Log database error with full details
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "request_id": request_id,
            "exception_type": type(exc).__name__,
            "path": request.url.path
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unexpected exceptions.
    
    Args:
        request: FastAPI request object
        exc: Exception instance
        
    Returns:
        JSONResponse with error details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    error_response = {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id
        }
    }
    
    # Log unexpected error with full stack trace
    logger.critical(
        f"Unexpected error: {str(exc)}",
        extra={
            "request_id": request_id,
            "exception_type": type(exc).__name__,
            "path": request.url.path
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )
