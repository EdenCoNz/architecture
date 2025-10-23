"""
Custom middleware for the application.
"""

import logging
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Union

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("apps.middleware")


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests with structured information.

    Logs include:
    - Timestamp (automatic from logging)
    - HTTP method
    - Request path
    - Response status code
    - Response time in milliseconds
    - User information (if authenticated)
    - Query parameters
    - Unique request ID

    Sensitive data (passwords, tokens, etc.) is sanitized before logging.
    """

    # Fields to sanitize in request data
    SENSITIVE_FIELDS = [
        "password",
        "token",
        "secret",
        "api_key",
        "apikey",
        "authorization",
        "auth",
        "credentials",
        "csrf_token",
        "csrfmiddlewaretoken",
    ]

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize middleware."""
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request: HttpRequest) -> None:
        """Process request before view execution."""
        # Add request ID for tracking
        request.request_id = str(uuid.uuid4())  # type: ignore[attr-defined]

        # Record start time
        request.start_time = time.time()  # type: ignore[attr-defined]

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Process response after view execution."""
        # Calculate response time
        if hasattr(request, "start_time"):
            response_time = (time.time() - request.start_time) * 1000  # Convert to ms
        else:
            response_time = 0

        # Get request ID
        request_id = getattr(request, "request_id", "unknown")

        # Get user information
        user_id = None
        username = "anonymous"
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = request.user.id
            username = str(getattr(request.user, "email", "authenticated"))

        # Get query parameters (sanitized)
        query_params = self._sanitize_data(dict(request.GET.items()))

        # Build log message
        log_message = (
            f"{request.method} {request.path} "
            f"- Status: {response.status_code} "
            f"- Duration: {response_time:.2f}ms "
            f"- User: {username}"
        )

        # Build extra context for structured logging
        extra = {
            "request_id": request_id,
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "response_time_ms": round(response_time, 2),
            "user_id": user_id,
            "username": username,
            "query_params": query_params,
            "ip_address": self._get_client_ip(request),
            "user_agent": (request.META.get("HTTP_USER_AGENT", "unknown")[:200]),
        }

        # Log at appropriate level based on status code
        if response.status_code >= 500:
            logger.error(log_message, extra=extra)
        elif response.status_code >= 400:
            logger.warning(log_message, extra=extra)
        else:
            logger.info(log_message, extra=extra)

        # Add request ID to response headers for debugging
        response["X-Request-ID"] = request_id

        return response

    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """Process exceptions that occur during request processing."""
        request_id = getattr(request, "request_id", "unknown")

        logger.error(
            f"Exception during request {request.method} {request.path}: " f"{str(exception)}",
            exc_info=True,
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "exception_type": type(exception).__name__,
            },
        )

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip: str = str(x_forwarded_for).split(",")[0].strip()
        else:
            ip = str(request.META.get("REMOTE_ADDR", "unknown"))
        return ip

    def _sanitize_data(self, data: Any) -> Any:
        """
        Sanitize sensitive data from dictionary.

        Args:
            data: Dictionary to sanitize

        Returns:
            Dictionary with sensitive fields replaced with '***REDACTED***'
        """
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list):
                sanitized[key] = [  # type: ignore[assignment]
                    self._sanitize_data(item) if isinstance(item, dict) else item for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized


class PerformanceLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log slow requests for performance monitoring.

    Logs requests that exceed the configured threshold.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize middleware."""
        self.get_response = get_response
        # Configurable threshold (default 1000ms)
        self.slow_request_threshold = getattr(settings, "SLOW_REQUEST_THRESHOLD_MS", 1000)
        super().__init__(get_response)

    def process_request(self, request: HttpRequest) -> None:
        """Process request before view execution."""
        request.perf_start_time = time.time()  # type: ignore[attr-defined]

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Process response and log if slow."""
        if hasattr(request, "perf_start_time"):
            response_time = (time.time() - request.perf_start_time) * 1000

            if response_time > self.slow_request_threshold:
                logger.warning(
                    f"SLOW REQUEST: {request.method} {request.path} "
                    f"took {response_time:.2f}ms "
                    f"(threshold: {self.slow_request_threshold}ms)",
                    extra={
                        "request_id": getattr(request, "request_id", "unknown"),
                        "method": request.method,
                        "path": request.path,
                        "response_time_ms": round(response_time, 2),
                        "threshold_ms": self.slow_request_threshold,
                        "is_slow": True,
                    },
                )

        return response


class HealthCheckLoggingExemptionMiddleware(MiddlewareMixin):
    """
    Middleware to skip logging for health check endpoints.

    Prevents log spam from monitoring tools.
    """

    # Endpoints to skip logging
    EXEMPT_PATHS = [
        "/health/",
        "/health/ready/",
        "/health/live/",
        "/api/v1/health/",
    ]

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize middleware."""
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request: HttpRequest) -> None:
        """Mark health check requests to skip logging."""
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            request.skip_logging = True  # type: ignore[attr-defined]


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add comprehensive security headers to all responses.

    Implements OWASP best practices for HTTP security headers:
    - X-Content-Type-Options: Prevents MIME type sniffing
    - X-Frame-Options: Prevents clickjacking attacks
    - X-XSS-Protection: Enables browser XSS filtering
    - Strict-Transport-Security: Enforces HTTPS
    - Content-Security-Policy: Prevents XSS and data injection
    - Referrer-Policy: Controls referrer information
    - Permissions-Policy: Controls browser features
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize middleware."""
        self.get_response = get_response
        super().__init__(get_response)

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Add security headers to response."""
        # X-Content-Type-Options: Prevent MIME type sniffing
        response["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Prevent clickjacking
        response["X-Frame-Options"] = "DENY"

        # X-XSS-Protection: Enable browser XSS filter
        response["X-XSS-Protection"] = "1; mode=block"

        # Strict-Transport-Security: Enforce HTTPS (1 year + subdomains)
        response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content-Security-Policy: Prevent XSS and data injection
        csp_directives = [
            "default-src 'self'",
            "script-src 'self'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]

        # In debug mode, relax CSP for development tools
        if settings.DEBUG:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https:",
                "font-src 'self' data:",
                "connect-src 'self'",
                "frame-ancestors 'none'",
            ]

        response["Content-Security-Policy"] = "; ".join(csp_directives)

        # Referrer-Policy: Control referrer information
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy: Restrict browser features
        permissions_policies = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
        ]
        response["Permissions-Policy"] = ", ".join(permissions_policies)

        return response
