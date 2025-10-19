"""
Unit tests for request logging middleware.

This module tests the request logging middleware to ensure it properly
logs incoming HTTP requests with relevant information.
"""

import logging
from unittest.mock import Mock

import pytest
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory

from common.middleware.request_logging import RequestLoggingMiddleware


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
def middleware(mock_get_response: Mock) -> RequestLoggingMiddleware:
    """Provide an instance of RequestLoggingMiddleware."""
    return RequestLoggingMiddleware(mock_get_response)


class TestRequestLoggingMiddleware:
    """Test suite for request logging middleware."""

    def test_middleware_logs_get_request(
        self,
        middleware: RequestLoggingMiddleware,
        request_factory: RequestFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that middleware logs GET requests."""
        request = request_factory.get("/api/test/")

        with caplog.at_level(logging.INFO):
            middleware(request)

        assert len(caplog.records) > 0
        assert "GET" in caplog.text
        assert "/api/test/" in caplog.text

    def test_middleware_logs_post_request(
        self,
        middleware: RequestLoggingMiddleware,
        request_factory: RequestFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that middleware logs POST requests."""
        request = request_factory.post("/api/create/", {"data": "test"})

        with caplog.at_level(logging.INFO):
            middleware(request)

        assert len(caplog.records) > 0
        assert "POST" in caplog.text
        assert "/api/create/" in caplog.text

    def test_middleware_logs_response_status(
        self,
        request_factory: RequestFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that middleware logs response status code."""
        mock_get_response = Mock()
        mock_get_response.return_value = HttpResponse("OK", status=200)
        middleware = RequestLoggingMiddleware(mock_get_response)

        request = request_factory.get("/api/test/")

        with caplog.at_level(logging.INFO):
            middleware(request)

        assert "200" in caplog.text

    def test_middleware_logs_client_ip(
        self,
        middleware: RequestLoggingMiddleware,
        request_factory: RequestFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that middleware logs client IP address."""
        request = request_factory.get("/api/test/", REMOTE_ADDR="192.168.1.100")

        with caplog.at_level(logging.INFO):
            middleware(request)

        assert "192.168.1.100" in caplog.text

    def test_middleware_logs_user_agent(
        self,
        middleware: RequestLoggingMiddleware,
        request_factory: RequestFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that middleware logs user agent."""
        request = request_factory.get(
            "/api/test/", HTTP_USER_AGENT="Mozilla/5.0 Test Browser"
        )

        with caplog.at_level(logging.INFO):
            middleware(request)

        assert "Mozilla/5.0 Test Browser" in caplog.text

    def test_middleware_calls_next_middleware(
        self,
        middleware: RequestLoggingMiddleware,
        request_factory: RequestFactory,
        mock_get_response: Mock,
    ) -> None:
        """Test that middleware calls the next middleware in chain."""
        request = request_factory.get("/api/test/")

        middleware(request)

        mock_get_response.assert_called_once_with(request)

    def test_middleware_returns_response_from_chain(
        self,
        request_factory: RequestFactory,
    ) -> None:
        """Test that middleware returns the response from the chain."""
        expected_response = HttpResponse("Custom response", status=201)
        mock_get_response = Mock(return_value=expected_response)
        middleware = RequestLoggingMiddleware(mock_get_response)

        request = request_factory.get("/api/test/")
        response = middleware(request)

        assert response == expected_response
        assert response.status_code == 201

    def test_middleware_handles_exceptions_gracefully(
        self,
        request_factory: RequestFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that middleware handles exceptions from next middleware."""
        mock_get_response = Mock(side_effect=Exception("Test error"))
        middleware = RequestLoggingMiddleware(mock_get_response)

        request = request_factory.get("/api/test/")

        with pytest.raises(Exception, match="Test error"):
            with caplog.at_level(logging.INFO):
                middleware(request)

        # Should still log the request even if there's an error
        assert len(caplog.records) > 0

    def test_middleware_does_not_log_health_check_endpoint(
        self,
        middleware: RequestLoggingMiddleware,
        request_factory: RequestFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that middleware skips logging health check endpoint."""
        request = request_factory.get("/health/")

        with caplog.at_level(logging.INFO):
            middleware(request)

        # Should not log health check requests to reduce noise
        assert "/health/" not in caplog.text or "Skipping" in caplog.text

    def test_middleware_logs_request_duration(
        self,
        middleware: RequestLoggingMiddleware,
        request_factory: RequestFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that middleware logs request processing duration."""
        request = request_factory.get("/api/test/")

        with caplog.at_level(logging.INFO):
            middleware(request)

        # Should include duration in milliseconds
        assert "ms" in caplog.text or "duration" in caplog.text.lower()
