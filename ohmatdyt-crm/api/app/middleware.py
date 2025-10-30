"""
BE-015: Middleware for request tracking and logging

Provides middleware for automatic request-id generation and tracking.
"""
import uuid
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logging_config import set_request_id, clear_request_id, get_logger

logger = get_logger(__name__)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking requests with unique request IDs.
    
    Features:
    - Generates unique request-id for each request
    - Stores request-id in context (available for logging)
    - Adds X-Request-ID header to response
    - Logs request/response with timing information
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add request tracking"""
        # Generate or use existing request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Set request ID in context
        set_request_id(request_id)
        
        # Log incoming request
        start_time = time.time()
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                'extra_fields': {
                    'method': request.method,
                    'path': request.url.path,
                    'client_host': request.client.host if request.client else None,
                    'user_agent': request.headers.get('user-agent'),
                }
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    'extra_fields': {
                        'method': request.method,
                        'path': request.url.path,
                        'status_code': response.status_code,
                        'process_time': round(process_time, 3),
                    }
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    'extra_fields': {
                        'method': request.method,
                        'path': request.url.path,
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'process_time': round(process_time, 3),
                    }
                },
                exc_info=True
            )
            raise
            
        finally:
            # Clear request ID from context
            clear_request_id()
