"""
Unit tests for global error handling middleware.

This module tests the error handling middleware to ensure it properly
catches and formats exceptions in a consistent manner.
"""

import logging
from unittest.mock import Mock

import pytest
from django.http import Http404, HttpRequest, HttpResponse
from django.test import RequestFactory
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)

from common.middleware.error_handling import ErrorHandlingMiddleware


@pytest.fixture
def request_factory() -> RequestFactory:
    """Provide a request factory for creating test requests."""
    return RequestFactory()


@pytest.fixture
def mock_get_response() -> Mock:
    """Provide a mock get_response callable."""
    mock = Mock()
    mock.return_value = HttpResponse("OK", status=200)
    return mock


@pytest.fixture
def middleware(mock_get_response: Mock) -> ErrorHandlingMiddleware:
    """Provide an instance of ErrorHandlingMiddleware."""
    return ErrorHandlingMiddleware(mock_get_response)


class TestErrorHandlingMiddleware:
    """Test suite for error handling middleware."""

    def test_middleware_allows_successful_requests(
        self,
        middleware: ErrorHandlingMiddleware,
        request_factory: RequestFactory,
        mock_get_response: Mock,
    ) -> None:
        """Test that middleware passes through successful requests."""
        request = request_factory.get("/api/test/")

        response = middleware(request)

        assert response.status_code == 200
        mock_get_response.assert_called_once_with(request)

    def test_middleware_catches_generic_exceptions(
        self,
        request_factory: RequestFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that middleware catches and handles generic exceptions."""
        mock_get_response = Mock(side_effect=Exception("Something went wrong"))
        middleware = ErrorHandlingMiddleware(mock_get_response)

        request = request_factory.get("/api/test/")

        with caplog.at_level(logging.ERROR):
            response = middleware(request)

        assert response.status_code == 500
        assert b"error" in response.content.lower()
        assert len(caplog.records) > 0

    def test_middleware_catches_http404_exceptions(
        self,
        request_factory: RequestFactory,
    ) -> None:
        """Test that middleware catches Http404 exceptions."""
        mock_get_response = Mock(side_effect=Http404("Not found"))
        middleware = ErrorHandlingMiddleware(mock_get_response)

        request = request_factory.get("/api/test/")
        response = middleware(request)

        assert response.status_code == 404

    def test_middleware_catches_validation_errors(
        self,
        request_factory: RequestFactory,
    ) -> None:
        """Test that middleware catches DRF ValidationError exceptions."""
        mock_get_response = Mock(
            side_effect=ValidationError({"field": ["This field is required"]})
        )
        middleware = ErrorHandlingMiddleware(mock_get_response)

        request = request_factory.post("/api/test/")
        response = middleware(request)

        assert response.status_code == 400

    def test_middleware_catches_permission_denied(
        self,
        request_factory: RequestFactory,
    ) -> None:
        """Test that middleware catches PermissionDenied exceptions."""
        mock_get_response = Mock(side_effect=PermissionDenied("Access denied"))
        middleware = ErrorHandlingMiddleware(mock_get_response)

        request = request_factory.get("/api/test/")
        response = middleware(request)

        assert response.status_code == 403

    def test_middleware_catches_not_authenticated(
        self,
        request_factory: RequestFactory,
    ) -> None:
        """Test that middleware catches NotAuthenticated exceptions."""
        mock_get_response = Mock(side_effect=NotAuthenticated("Not authenticated"))
        middleware = ErrorHandlingMiddleware(mock_get_response)

        request = request_factory.get("/api/test/")
        response = middleware(request)

        assert response.status_code == 401

    def test_middleware_catches_authentication_failed(
        self,
        request_factory: RequestFactory,
    ) -> None:
        """Test that middleware catches AuthenticationFailed exceptions."""
        mock_get_response = Mock(
            side_effect=AuthenticationFailed("Invalid credentials")
        )
        middleware = ErrorHandlingMiddleware(mock_get_response)

        request = request_factory.get("/api/test/")
        response = middleware(request)

        assert response.status_code == 401

    def test_middleware_returns_json_error_response(
        self,
        request_factory: RequestFactory,
    ) -> None:
        """Test that middleware returns JSON formatted error responses."""
        mock_get_response = Mock(side_effect=Exception("Test error"))
        middleware = ErrorHandlingMiddleware(mock_get_response)

        request = request_factory.get("/api/test/")
        response = middleware(request)

        # Check content type is JSON
        assert response["Content-Type"] == "application/json"

    def test_middleware_logs_exception_details(
        self,
        request_factory: RequestFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that middleware logs exception details."""
        error_message = "Detailed error message"
        mock_get_response = Mock(side_effect=Exception(error_message))
        middleware = ErrorHandlingMiddleware(mock_get_response)

        request = request_factory.get("/api/test/")

        with caplog.at_level(logging.ERROR):
            middleware(request)

        assert error_message in caplog.text
        assert "Exception" in caplog.text

    def test_middleware_hides_sensitive_error_details_in_production(
        self,
        request_factory: RequestFactory,
    ) -> None:
        """Test that middleware doesn't expose sensitive details in production."""
        mock_get_response = Mock(side_effect=Exception("Database password is: secret123"))
        middleware = ErrorHandlingMiddleware(mock_get_response)

        request = request_factory.get("/api/test/")
        response = middleware(request)

        # Should not contain the actual error message
        assert b"secret123" not in response.content
        assert b"Internal server error" in response.content.lower()

    def test_middleware_includes_error_details_in_debug_mode(
        self,
        request_factory: RequestFactory,
        settings,
    ) -> None:
        """Test that middleware includes error details when DEBUG=True."""
        settings.DEBUG = True
        error_message = "Specific error for debugging"
        mock_get_response = Mock(side_effect=Exception(error_message))
        middleware = ErrorHandlingMiddleware(mock_get_response)

        request = request_factory.get("/api/test/")
        response = middleware(request)

        # In debug mode, should include error details
        assert error_message.encode() in response.content

    def test_middleware_includes_request_path_in_logs(
        self,
        request_factory: RequestFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that middleware includes request path in error logs."""
        mock_get_response = Mock(side_effect=Exception("Test error"))
        middleware = ErrorHandlingMiddleware(mock_get_response)

        request = request_factory.get("/api/specific/path/")

        with caplog.at_level(logging.ERROR):
            middleware(request)

        assert "/api/specific/path/" in caplog.text

    def test_middleware_includes_request_method_in_logs(
        self,
        request_factory: RequestFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that middleware includes request method in error logs."""
        mock_get_response = Mock(side_effect=Exception("Test error"))
        middleware = ErrorHandlingMiddleware(mock_get_response)

        request = request_factory.post("/api/test/")

        with caplog.at_level(logging.ERROR):
            middleware(request)

        assert "POST" in caplog.text
