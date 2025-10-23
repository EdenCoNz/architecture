"""
Tests for custom exception handlers.
"""

import logging
from unittest.mock import MagicMock, patch

from django.http import Http404
from django.test import RequestFactory, TestCase, override_settings
from rest_framework.exceptions import (
    APIException,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import custom_exception_handler


class ExceptionHandlerTestCase(TestCase):
    """Test cases for custom exception handler."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.view = APIView()

    def _get_context(self, request):
        """Helper to create exception context."""
        return {"view": self.view, "args": (), "kwargs": {}, "request": request}

    @patch("apps.core.exceptions.logger")
    def test_validation_error_returns_consistent_format(self, mock_logger):
        """Test that validation errors return consistent error format."""
        request = self.factory.post("/api/v1/test/")
        context = self._get_context(request)

        exc = ValidationError({"email": ["This field is required."]})
        response = custom_exception_handler(exc, context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertIn("message", response.data)
        self.assertIn("status_code", response.data)

    @patch("apps.core.exceptions.logger")
    def test_permission_denied_error_logged_and_returned(self, mock_logger):
        """Test that permission denied errors are logged and returned properly."""
        request = self.factory.get("/api/v1/test/")
        context = self._get_context(request)

        exc = PermissionDenied("You do not have permission to perform this action.")
        response = custom_exception_handler(exc, context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(mock_logger.warning.called)

    @patch("apps.core.exceptions.logger")
    def test_authentication_error_logged_and_returned(self, mock_logger):
        """Test that authentication errors are logged and returned properly."""
        request = self.factory.get("/api/v1/test/")
        context = self._get_context(request)

        exc = NotAuthenticated("Authentication credentials were not provided.")
        response = custom_exception_handler(exc, context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 401)
        self.assertTrue(mock_logger.warning.called)

    @patch("apps.core.exceptions.logger")
    @override_settings(DEBUG=True)
    def test_unhandled_exception_in_development_includes_details(self, mock_logger):
        """Test that unhandled exceptions include details in development mode."""
        request = self.factory.get("/api/v1/test/")
        context = self._get_context(request)

        exc = Exception("Something went wrong")
        response = custom_exception_handler(exc, context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 500)
        self.assertTrue(mock_logger.error.called)

        # In development, should include more details
        self.assertIn("error", response.data)

    @patch("apps.core.exceptions.logger")
    @override_settings(DEBUG=False)
    def test_unhandled_exception_in_production_hides_details(self, mock_logger):
        """Test that unhandled exceptions hide sensitive details in production."""
        request = self.factory.get("/api/v1/test/")
        context = self._get_context(request)

        exc = Exception("Database connection failed: password=secret123")
        response = custom_exception_handler(exc, context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 500)
        self.assertTrue(mock_logger.error.called)

        # In production, should not expose internal details
        response_str = str(response.data)
        self.assertNotIn("password", response_str)
        self.assertNotIn("secret123", response_str)
        self.assertIn("error", response.data)

    @patch("apps.core.exceptions.logger")
    def test_exception_logs_include_stack_trace_in_dev(self, mock_logger):
        """Test that exception logs include stack trace in development mode."""
        request = self.factory.get("/api/v1/test/")
        context = self._get_context(request)

        exc = Exception("Test exception")

        with override_settings(DEBUG=True):
            response = custom_exception_handler(exc, context)

        # Verify logger.error was called with exc_info=True
        self.assertTrue(mock_logger.error.called)
        call_args = mock_logger.error.call_args
        self.assertTrue(call_args[1].get("exc_info", False))

    @patch("apps.core.exceptions.logger")
    def test_exception_includes_request_context(self, mock_logger):
        """Test that exception logs include request context."""
        request = self.factory.post("/api/v1/test/", {"key": "value"})
        context = self._get_context(request)

        exc = ValidationError("Invalid data")
        response = custom_exception_handler(exc, context)

        self.assertTrue(mock_logger.warning.called)
        call_args = mock_logger.warning.call_args

        # Verify extra context is included
        extra = call_args[1].get("extra", {})
        self.assertIn("view", extra)
        self.assertIn("method", extra)
        self.assertIn("path", extra)

    @patch("apps.core.exceptions.logger")
    def test_http_404_error_handled_properly(self, mock_logger):
        """Test that 404 errors are handled properly."""
        request = self.factory.get("/api/v1/nonexistent/")
        context = self._get_context(request)

        exc = Http404("Resource not found")
        response = custom_exception_handler(exc, context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(mock_logger.warning.called)

    @patch("apps.core.exceptions.logger")
    def test_generic_api_exception_handled(self, mock_logger):
        """Test that generic API exceptions are handled."""
        request = self.factory.get("/api/v1/test/")
        context = self._get_context(request)

        exc = APIException("Service temporarily unavailable")
        response = custom_exception_handler(exc, context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 500)
        self.assertTrue(mock_logger.error.called)

    @patch("apps.core.exceptions.logger")
    def test_exception_handler_includes_timestamp(self, mock_logger):
        """Test that exception response includes timestamp."""
        request = self.factory.get("/api/v1/test/")
        context = self._get_context(request)

        exc = ValidationError("Invalid data")
        response = custom_exception_handler(exc, context)

        # Check if timestamp is in response or logs
        self.assertTrue(mock_logger.warning.called)
        call_args = mock_logger.warning.call_args
        extra = call_args[1].get("extra", {})

        # Timestamp should be in extra data
        self.assertIn("timestamp", extra)

    @patch("apps.core.exceptions.logger")
    def test_exception_handler_sanitizes_sensitive_fields(self, mock_logger):
        """Test that exception handler sanitizes sensitive fields."""
        request = self.factory.post(
            "/api/v1/auth/login/", {"password": "secret123", "token": "abc123"}
        )
        context = self._get_context(request)

        exc = ValidationError("Invalid credentials")
        response = custom_exception_handler(exc, context)

        # Verify sensitive data is not logged
        all_calls = mock_logger.warning.call_args_list + mock_logger.error.call_args_list

        for call in all_calls:
            call_str = str(call)
            self.assertNotIn("secret123", call_str)
            self.assertNotIn("abc123", call_str)

    @patch("apps.core.exceptions.logger")
    def test_exception_response_structure_consistency(self, mock_logger):
        """Test that all exception responses follow the same structure."""
        request = self.factory.get("/api/v1/test/")
        context = self._get_context(request)

        exceptions = [
            ValidationError("Invalid data"),
            PermissionDenied("No permission"),
            NotAuthenticated("Not authenticated"),
        ]

        for exc in exceptions:
            response = custom_exception_handler(exc, context)

            # All responses should have consistent structure
            self.assertIn("error", response.data)
            self.assertIn("message", response.data)
            self.assertIn("status_code", response.data)
            self.assertIsInstance(response.data["error"], bool)
            self.assertTrue(response.data["error"])
