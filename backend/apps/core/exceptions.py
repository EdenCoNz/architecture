"""
Custom exception handlers for the API.
"""

import logging
import traceback
from datetime import datetime

from django.conf import settings
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("apps.exceptions")


class BaseAPIException(APIException):
    """Base exception class for custom API exceptions."""

    def __init__(self, detail=None, code=None):
        """Initialize exception with detail and code."""
        super().__init__(detail, code)


class ServiceUnavailableException(BaseAPIException):
    """Exception for service unavailable errors."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service temporarily unavailable. Please try again later."
    default_code = "service_unavailable"


class RateLimitExceededException(BaseAPIException):
    """Exception for rate limit exceeded errors."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Rate limit exceeded. Please try again later."
    default_code = "rate_limit_exceeded"


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.

    Features:
    - Consistent error response structure
    - Environment-aware error detail exposure
    - Comprehensive logging with context
    - Sensitive data sanitization
    - Request tracking with request_id
    """
    # Get request from context
    request = context.get("request")
    view = context.get("view")

    # Get request ID if available
    request_id = getattr(request, "request_id", "unknown") if request else "unknown"

    # Convert Django exceptions to DRF exceptions
    if isinstance(exc, Http404):
        exc = NotFound("Resource not found.")
    elif isinstance(exc, DjangoPermissionDenied):
        exc = PermissionDenied("You do not have permission to perform this action.")

    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Build extra logging context
    extra_context = {
        "request_id": request_id,
        "exception_type": type(exc).__name__,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if request:
        extra_context.update(
            {
                "method": request.method,
                "path": request.path,
                "user": str(request.user) if hasattr(request, "user") else "anonymous",
            }
        )

    if view:
        extra_context["view"] = view.__class__.__name__

    # Determine log level and log message based on exception type
    if response is not None:
        # DRF handled the exception
        status_code = response.status_code

        if status_code >= 500:
            # Server errors - log with error level
            logger.error(
                f"Server error ({status_code}): {str(exc)}",
                exc_info=settings.DEBUG,  # Include stack trace in debug mode
                extra=extra_context,
            )
        elif status_code >= 400:
            # Client errors - log with warning level
            logger.warning(f"Client error ({status_code}): {str(exc)}", extra=extra_context)

        # Customize the response data structure
        error_data = _format_error_response(exc, response, request_id)
        response.data = error_data

    else:
        # Unhandled exception - log with error level
        logger.error(
            f"Unhandled exception: {str(exc)}",
            exc_info=True,  # Always include stack trace for unhandled exceptions
            extra=extra_context,
        )

        # Create response for unhandled exception
        error_data = _format_unhandled_error(exc, request_id)
        response = Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Add request ID to response headers for debugging
    if request_id != "unknown":
        response["X-Request-ID"] = request_id

    return response


def _format_error_response(exc, response, request_id):
    """
    Format error response with consistent structure.

    Args:
        exc: The exception that occurred
        response: The DRF response object
        request_id: Unique request identifier

    Returns:
        Dictionary with formatted error data
    """
    # Get error message
    if isinstance(response.data, dict):
        message = response.data.get("detail", "An error occurred")

        # For validation errors, collect all field errors
        errors = None
        if isinstance(exc, ValidationError):
            errors = response.data

    elif isinstance(response.data, list):
        message = response.data[0] if response.data else "An error occurred"
        errors = response.data
    else:
        message = str(response.data)
        errors = None

    # Build response structure
    error_response = {
        "error": True,
        "status_code": response.status_code,
        "message": message,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Add detailed errors if present and not just a simple detail message
    if errors and (not isinstance(errors, dict) or len(errors) > 1 or "detail" not in errors):
        error_response["errors"] = errors

    # In development mode, add more debug information
    if settings.DEBUG:
        error_response["debug"] = {
            "exception_type": type(exc).__name__,
        }

    return error_response


def _format_unhandled_error(exc, request_id):
    """
    Format unhandled error response.

    In production: Hide implementation details
    In development: Include exception details for debugging

    Args:
        exc: The exception that occurred
        request_id: Unique request identifier

    Returns:
        Dictionary with formatted error data
    """
    error_response = {
        "error": True,
        "status_code": 500,
        "message": "An unexpected error occurred. Please try again later.",
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # In development mode, include exception details
    if settings.DEBUG:
        error_response["debug"] = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    return error_response


def _sanitize_data(data):
    """
    Sanitize sensitive data from error responses.

    Args:
        data: Data to sanitize (dict, list, or primitive)

    Returns:
        Sanitized data with sensitive fields redacted
    """
    sensitive_fields = [
        "password",
        "token",
        "secret",
        "api_key",
        "apikey",
        "authorization",
        "credentials",
    ]

    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, (dict, list)):
                sanitized[key] = _sanitize_data(value)
            else:
                sanitized[key] = value
        return sanitized

    elif isinstance(data, list):
        return [_sanitize_data(item) for item in data]

    return data
