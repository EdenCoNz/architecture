"""
Global error handling middleware for consistent error responses.

This middleware catches exceptions raised during request processing
and returns properly formatted JSON error responses.
"""

import logging
import traceback
from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware:
    """
    Middleware to catch and handle exceptions globally.

    Provides consistent error responses in JSON format and logs
    exception details for debugging and monitoring.

    Handles:
    - HTTP 404 errors
    - DRF API exceptions (validation, authentication, permission)
    - Generic Python exceptions

    Error responses include appropriate status codes and messages.
    In DEBUG mode, detailed error information is included.
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
        Process the request and handle any exceptions.

        Args:
            request: Incoming HTTP request

        Returns:
            HttpResponse from the next middleware/view or error response
        """
        try:
            response = self.get_response(request)
            return response
        except Http404 as exc:
            return self._handle_http404(request, exc)
        except NotAuthenticated as exc:
            return self._handle_not_authenticated(request, exc)
        except AuthenticationFailed as exc:
            return self._handle_authentication_failed(request, exc)
        except PermissionDenied as exc:
            return self._handle_permission_denied(request, exc)
        except ValidationError as exc:
            return self._handle_validation_error(request, exc)
        except APIException as exc:
            return self._handle_api_exception(request, exc)
        except Exception as exc:
            return self._handle_generic_exception(request, exc)

    def _handle_http404(self, request: HttpRequest, _exc: Http404) -> JsonResponse:
        """
        Handle HTTP 404 Not Found errors.

        Args:
            request: HTTP request object
            _exc: Http404 exception (unused, required by signature)

        Returns:
            JSON response with 404 status
        """
        logger.warning("HTTP 404: method=%s path=%s", request.method, request.path)

        return JsonResponse(
            {
                "error": "Not Found",
                "message": "The requested resource was not found",
                "path": request.path,
            },
            status=404,
        )

    def _handle_not_authenticated(
        self, request: HttpRequest, _exc: NotAuthenticated
    ) -> JsonResponse:
        """
        Handle authentication required errors.

        Args:
            request: HTTP request object
            _exc: NotAuthenticated exception (unused, required by signature)

        Returns:
            JSON response with 401 status
        """
        logger.warning(
            "Authentication required: method=%s path=%s",
            request.method,
            request.path,
        )

        return JsonResponse(
            {
                "error": "Not Authenticated",
                "message": "Authentication credentials were not provided",
                "path": request.path,
            },
            status=401,
        )

    def _handle_authentication_failed(
        self, request: HttpRequest, exc: AuthenticationFailed
    ) -> JsonResponse:
        """
        Handle authentication failed errors.

        Args:
            request: HTTP request object
            exc: AuthenticationFailed exception

        Returns:
            JSON response with 401 status
        """
        logger.warning(
            "Authentication failed: method=%s path=%s message=%s",
            request.method,
            request.path,
            str(exc),
        )

        return JsonResponse(
            {
                "error": "Authentication Failed",
                "message": str(exc) if str(exc) else "Invalid authentication credentials",
                "path": request.path,
            },
            status=401,
        )

    def _handle_permission_denied(
        self, request: HttpRequest, exc: PermissionDenied
    ) -> JsonResponse:
        """
        Handle permission denied errors.

        Args:
            request: HTTP request object
            exc: PermissionDenied exception

        Returns:
            JSON response with 403 status
        """
        logger.warning(
            "Permission denied: method=%s path=%s message=%s",
            request.method,
            request.path,
            str(exc),
        )

        return JsonResponse(
            {
                "error": "Permission Denied",
                "message": (
                    str(exc) if str(exc) else "You do not have permission to access this resource"
                ),
                "path": request.path,
            },
            status=403,
        )

    def _handle_validation_error(self, request: HttpRequest, exc: ValidationError) -> JsonResponse:
        """
        Handle validation errors.

        Args:
            request: HTTP request object
            exc: ValidationError exception

        Returns:
            JSON response with 400 status
        """
        logger.info(
            "Validation error: method=%s path=%s errors=%s",
            request.method,
            request.path,
            exc.detail,
        )

        # ValidationError can have different formats
        if isinstance(exc.detail, dict):
            errors = exc.detail
        elif isinstance(exc.detail, list):
            errors = {"detail": exc.detail}
        else:
            errors = {"detail": [str(exc.detail)]}

        return JsonResponse(
            {
                "error": "Validation Error",
                "message": "The request contains invalid data",
                "errors": errors,
                "path": request.path,
            },
            status=400,
        )

    def _handle_api_exception(self, request: HttpRequest, exc: APIException) -> JsonResponse:
        """
        Handle DRF API exceptions.

        Args:
            request: HTTP request object
            exc: APIException

        Returns:
            JSON response with appropriate status code
        """
        logger.warning(
            "API exception: method=%s path=%s status=%s message=%s",
            request.method,
            request.path,
            exc.status_code,
            str(exc.detail),
        )

        return JsonResponse(
            {
                "error": exc.__class__.__name__,
                "message": str(exc.detail),
                "path": request.path,
            },
            status=exc.status_code,
        )

    def _handle_generic_exception(self, request: HttpRequest, exc: Exception) -> JsonResponse:
        """
        Handle generic Python exceptions.

        Args:
            request: HTTP request object
            exc: Generic exception

        Returns:
            JSON response with 500 status
        """
        # Log full exception details
        logger.error(
            "Internal server error: method=%s path=%s exception=%s",
            request.method,
            request.path,
            exc.__class__.__name__,
            exc_info=True,
        )

        # In debug mode, include detailed error information
        if settings.DEBUG:
            error_detail: dict[str, Any] = {
                "error": "Internal Server Error",
                "message": str(exc),
                "exception_type": exc.__class__.__name__,
                "path": request.path,
                "traceback": traceback.format_exc().split("\n"),
            }
        else:
            # In production, hide implementation details
            error_detail = {
                "error": "Internal Server Error",
                "message": "An internal server error occurred. Please try again later.",
                "path": request.path,
            }

        return JsonResponse(error_detail, status=500)
