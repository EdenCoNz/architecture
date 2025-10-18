"""
Request logging middleware for tracking HTTP requests and responses.

This middleware logs all incoming requests and outgoing responses with
timing information, status codes, and optional request/response body logging.
"""
import time
import logging
import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextvars import ContextVar

# Context variable for request ID (for distributed tracing)
request_id_context: ContextVar[str] = ContextVar("request_id", default="")

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses.

    Features:
    - Logs request method, path, query parameters
    - Logs response status code and processing time
    - Adds unique request ID for distributed tracing
    - Adds request ID to response headers
    - Excludes health check and metrics endpoints from logs
    """

    # Paths to exclude from logging (typically health checks and metrics)
    EXCLUDED_PATHS = {"/health", "/metrics", "/favicon.ico"}

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process the request and log relevant information.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            Response: The HTTP response
        """
        # Generate unique request ID for tracing
        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)

        # Skip logging for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        # Start timer
        start_time = time.time()

        # Log incoming request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log exception
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(exc)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time_ms": round(process_time * 1000, 2),
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))

        # Log response
        log_level = logging.INFO if response.status_code < 400 else logging.WARNING
        logger.log(
            log_level,
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
            }
        )

        return response


def get_request_id() -> str:
    """
    Get the current request ID from context.

    Returns:
        str: The current request ID or empty string if not set
    """
    return request_id_context.get()
