"""
Request logging middleware for tracking HTTP requests.

This middleware logs incoming HTTP requests with relevant information
such as method, path, IP address, user agent, and response status.
"""

import logging
import time
from typing import Callable

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

# Paths to skip logging to reduce noise
SKIP_LOGGING_PATHS = ["/health/", "/favicon.ico"]


class RequestLoggingMiddleware:
    """
    Middleware to log incoming HTTP requests.

    Logs request information including:
    - HTTP method
    - Request path
    - Client IP address
    - User agent
    - Response status code
    - Request processing duration

    Health check endpoints are excluded from logging to reduce log volume.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """
        Initialize the middleware.

        Args:
            get_response: Callable that takes a request and returns a response
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process the request and log information.

        Args:
            request: Incoming HTTP request

        Returns:
            HttpResponse from the next middleware or view
        """
        # Skip logging for certain paths
        if request.path in SKIP_LOGGING_PATHS:
            return self.get_response(request)

        # Record start time for duration calculation
        start_time = time.time()

        # Get client IP address
        client_ip = self._get_client_ip(request)

        # Get user agent
        user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

        # Process the request
        response = self.get_response(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log the request
        logger.info(
            "Request: method=%s path=%s ip=%s status=%s duration=%.2fms user_agent=%s",
            request.method,
            request.path,
            client_ip,
            response.status_code,
            duration_ms,
            user_agent,
        )

        return response

    def _get_client_ip(self, request: HttpRequest) -> str:
        """
        Extract client IP address from request.

        Handles proxied requests by checking X-Forwarded-For header.

        Args:
            request: HTTP request object

        Returns:
            Client IP address as string
        """
        # Check X-Forwarded-For header first (for proxied requests)
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # Take the first IP in the chain
            return x_forwarded_for.split(",")[0].strip()

        # Fall back to REMOTE_ADDR
        return request.META.get("REMOTE_ADDR", "Unknown")
