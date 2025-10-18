"""
Error handling middleware for catching and formatting exceptions.

This middleware catches all unhandled exceptions and formats them
into consistent JSON responses with appropriate status codes and
error messages.
"""
import logging
import traceback
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from .request_logging import get_request_id

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle exceptions and format error responses.

    Features:
    - Catches all unhandled exceptions
    - Formats errors into consistent JSON responses
    - Includes request ID for tracking
    - Hides sensitive details in production
    - Logs all errors with full stack traces
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> JSONResponse:
        """
        Process the request and handle any exceptions.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            JSONResponse: The HTTP response or error response
        """
        try:
            response = await call_next(request)
            return response

        except StarletteHTTPException as exc:
            # HTTP exceptions (404, 403, etc.)
            return self._format_http_exception(exc, request)

        except RequestValidationError as exc:
            # Pydantic validation errors
            return self._format_validation_error(exc, request)

        except Exception as exc:
            # Unexpected exceptions
            return self._format_unexpected_error(exc, request)

    def _format_http_exception(
        self, exc: StarletteHTTPException, request: Request
    ) -> JSONResponse:
        """
        Format HTTP exceptions into JSON response.

        Args:
            exc: The HTTP exception
            request: The HTTP request

        Returns:
            JSONResponse: Formatted error response
        """
        request_id = get_request_id()

        # Log the error
        logger.warning(
            f"HTTP {exc.status_code}: {request.method} {request.url.path} - {exc.detail}",
            extra={
                "request_id": request_id,
                "status_code": exc.status_code,
                "method": request.method,
                "path": request.url.path,
                "error": exc.detail,
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "http_error",
                    "message": exc.detail,
                    "status_code": exc.status_code,
                    "request_id": request_id,
                }
            },
            headers={"X-Request-ID": request_id},
        )

    def _format_validation_error(
        self, exc: RequestValidationError, request: Request
    ) -> JSONResponse:
        """
        Format validation errors into JSON response.

        Args:
            exc: The validation error
            request: The HTTP request

        Returns:
            JSONResponse: Formatted error response
        """
        request_id = get_request_id()

        # Extract validation error details
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })

        # Log the validation error
        logger.warning(
            f"Validation error: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "validation_errors": errors,
            }
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "type": "validation_error",
                    "message": "Request validation failed",
                    "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "request_id": request_id,
                    "details": errors,
                }
            },
            headers={"X-Request-ID": request_id},
        )

    def _format_unexpected_error(
        self, exc: Exception, request: Request
    ) -> JSONResponse:
        """
        Format unexpected errors into JSON response.

        Args:
            exc: The unexpected exception
            request: The HTTP request

        Returns:
            JSONResponse: Formatted error response
        """
        request_id = get_request_id()

        # Log the full error with stack trace
        logger.error(
            f"Unexpected error: {request.method} {request.url.path} - {str(exc)}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            exc_info=True,
        )

        # In production, hide error details
        if settings.is_production:
            error_message = "An unexpected error occurred"
            error_details = None
        else:
            error_message = str(exc)
            error_details = {
                "type": type(exc).__name__,
                "traceback": traceback.format_exc().split("\n"),
            }

        content = {
            "error": {
                "type": "internal_error",
                "message": error_message,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "request_id": request_id,
            }
        }

        if error_details:
            content["error"]["details"] = error_details

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
            headers={"X-Request-ID": request_id},
        )
