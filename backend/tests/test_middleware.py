"""
Tests for custom middleware components.
"""

import json
import logging
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from apps.core.middleware import RequestLoggingMiddleware


class RequestLoggingMiddlewareTestCase(TestCase):
    """Test cases for RequestLoggingMiddleware."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.get_response = MagicMock(return_value=HttpResponse("OK", status=200))
        self.middleware = RequestLoggingMiddleware(self.get_response)

    @patch("apps.core.middleware.logger")
    def test_middleware_logs_request_with_basic_info(self, mock_logger):
        """Test that middleware logs request with timestamp, method, path, and status."""
        request = self.factory.get("/api/v1/test/")
        request.user = AnonymousUser()

        self.middleware(request)

        # Verify logger.info was called
        self.assertTrue(mock_logger.info.called)

        # Get the logged message
        call_args = mock_logger.info.call_args
        log_message = call_args[0][0]

        # Verify basic request info is in the log
        self.assertIn("GET", log_message)
        self.assertIn("/api/v1/test/", log_message)
        self.assertIn("200", log_message)

    @patch("apps.core.middleware.logger")
    def test_middleware_logs_response_time(self, mock_logger):
        """Test that middleware logs response time."""
        request = self.factory.get("/api/v1/test/")
        request.user = AnonymousUser()

        self.middleware(request)

        # Verify logger.info was called
        call_args = mock_logger.info.call_args
        log_message = call_args[0][0]

        # Verify response time is logged
        self.assertIn("ms", log_message)

    @patch("apps.core.middleware.logger")
    def test_middleware_logs_user_info_for_authenticated_user(self, mock_logger):
        """Test that middleware logs user info for authenticated users."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Create a test user
        user = User(email="testuser@example.com", id=123)

        request = self.factory.get("/api/v1/test/")
        request.user = user

        self.middleware(request)

        call_args = mock_logger.info.call_args
        extra_data = call_args[1].get("extra", {})

        # Verify user info is in extra data
        self.assertEqual(extra_data.get("user_id"), 123)

    @patch("apps.core.middleware.logger")
    def test_middleware_logs_query_parameters(self, mock_logger):
        """Test that middleware logs query parameters."""
        request = self.factory.get("/api/v1/test/", {"page": "2", "limit": "10"})
        request.user = AnonymousUser()

        self.middleware(request)

        call_args = mock_logger.info.call_args
        extra_data = call_args[1].get("extra", {})

        # Verify query params are logged
        self.assertIn("page", str(extra_data.get("query_params", "")))

    @patch("apps.core.middleware.logger")
    def test_middleware_logs_different_http_methods(self, mock_logger):
        """Test that middleware logs different HTTP methods correctly."""
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

        for method in methods:
            mock_logger.reset_mock()

            if method == "GET":
                request = self.factory.get("/api/v1/test/")
            elif method == "POST":
                request = self.factory.post("/api/v1/test/", data={})
            elif method == "PUT":
                request = self.factory.put("/api/v1/test/", data={})
            elif method == "PATCH":
                request = self.factory.patch("/api/v1/test/", data={})
            elif method == "DELETE":
                request = self.factory.delete("/api/v1/test/")

            request.user = AnonymousUser()
            self.middleware(request)

            call_args = mock_logger.info.call_args
            log_message = call_args[0][0]

            self.assertIn(method, log_message)

    @patch("apps.core.middleware.logger")
    def test_middleware_logs_error_status_codes(self, mock_logger):
        """Test that middleware logs error status codes appropriately."""
        # Mock response with error status
        error_response = HttpResponse("Not Found", status=404)
        self.middleware.get_response = MagicMock(return_value=error_response)

        request = self.factory.get("/api/v1/nonexistent/")
        request.user = AnonymousUser()

        response = self.middleware(request)

        # Verify warning level for 4xx errors
        self.assertTrue(mock_logger.warning.called)

        call_args = mock_logger.warning.call_args
        log_message = call_args[0][0]

        self.assertIn("404", log_message)

    @patch("apps.core.middleware.logger")
    def test_middleware_logs_server_errors(self, mock_logger):
        """Test that middleware logs server errors with error level."""
        # Mock response with server error status
        error_response = HttpResponse("Internal Server Error", status=500)
        self.middleware.get_response = MagicMock(return_value=error_response)

        request = self.factory.get("/api/v1/test/")
        request.user = AnonymousUser()

        response = self.middleware(request)

        # Verify error level for 5xx errors
        self.assertTrue(mock_logger.error.called)

        call_args = mock_logger.error.call_args
        log_message = call_args[0][0]

        self.assertIn("500", log_message)

    @patch("apps.core.middleware.logger")
    def test_middleware_includes_request_id(self, mock_logger):
        """Test that middleware includes a unique request ID."""
        request = self.factory.get("/api/v1/test/")
        request.user = AnonymousUser()

        self.middleware(request)

        call_args = mock_logger.info.call_args
        extra_data = call_args[1].get("extra", {})

        # Verify request_id exists
        self.assertIn("request_id", extra_data)
        self.assertIsNotNone(extra_data["request_id"])

    @patch("apps.core.middleware.logger")
    def test_middleware_sanitizes_sensitive_data(self, mock_logger):
        """Test that middleware sanitizes sensitive data in logs."""
        request = self.factory.post(
            "/api/v1/auth/login/",
            data=json.dumps({"password": "secret123"}),
            content_type="application/json",
        )
        request.user = AnonymousUser()

        self.middleware(request)

        # Get all calls to logger
        all_calls = mock_logger.info.call_args_list + mock_logger.warning.call_args_list

        # Verify password is not in any log message
        for call in all_calls:
            log_message = str(call)
            self.assertNotIn("secret123", log_message)
