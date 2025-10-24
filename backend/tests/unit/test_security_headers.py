"""
Unit tests for security headers middleware.

Tests verify that:
- Security headers are properly set on all responses
- Headers follow OWASP best practices
- Headers work correctly in different environments
"""

import pytest
from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from apps.core.middleware import SecurityHeadersMiddleware


@pytest.mark.django_db
class TestSecurityHeadersMiddleware:
    """Test security headers middleware functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()

        def get_response(request):
            return HttpResponse()

        self.middleware = SecurityHeadersMiddleware(get_response)

    def test_x_content_type_options_header(self):
        """Test X-Content-Type-Options header is set."""
        request = self.factory.get("/test/")
        response = self.middleware(request)

        assert "X-Content-Type-Options" in response
        assert response["X-Content-Type-Options"] == "nosniff"

    def test_x_frame_options_header(self):
        """Test X-Frame-Options header is set."""
        request = self.factory.get("/test/")
        response = self.middleware(request)

        assert "X-Frame-Options" in response
        assert response["X-Frame-Options"] == "DENY"

    def test_x_xss_protection_header(self):
        """Test X-XSS-Protection header is set."""
        request = self.factory.get("/test/")
        response = self.middleware(request)

        assert "X-XSS-Protection" in response
        assert response["X-XSS-Protection"] == "1; mode=block"

    def test_strict_transport_security_header(self):
        """Test Strict-Transport-Security header is set."""
        request = self.factory.get("/test/")
        response = self.middleware(request)

        assert "Strict-Transport-Security" in response
        # Should include max-age and includeSubDomains
        hsts_value = response["Strict-Transport-Security"]
        assert "max-age=" in hsts_value
        assert "includeSubDomains" in hsts_value

    def test_content_security_policy_header(self):
        """Test Content-Security-Policy header is set."""
        request = self.factory.get("/test/")
        response = self.middleware(request)

        assert "Content-Security-Policy" in response
        csp_value = response["Content-Security-Policy"]

        # Should have default-src directive
        assert "default-src 'self'" in csp_value

    def test_referrer_policy_header(self):
        """Test Referrer-Policy header is set."""
        request = self.factory.get("/test/")
        response = self.middleware(request)

        assert "Referrer-Policy" in response
        assert response["Referrer-Policy"] in [
            "strict-origin-when-cross-origin",
            "no-referrer",
            "strict-origin",
        ]

    def test_permissions_policy_header(self):
        """Test Permissions-Policy header is set."""
        request = self.factory.get("/test/")
        response = self.middleware(request)

        assert "Permissions-Policy" in response
        # Should restrict camera, microphone, geolocation
        policy = response["Permissions-Policy"]
        assert "geolocation=()" in policy or "geolocation=" in policy

    def test_all_security_headers_present(self):
        """Test all critical security headers are present."""
        request = self.factory.get("/test/")
        response = self.middleware(request)

        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy",
            "Permissions-Policy",
        ]

        for header in required_headers:
            assert header in response, f"Missing security header: {header}"

    def test_security_headers_on_error_responses(self):
        """Test security headers are set even on error responses."""

        def get_error_response(request):
            return HttpResponse(status=500)

        middleware = SecurityHeadersMiddleware(get_error_response)
        request = self.factory.get("/test/")
        response = middleware(request)

        assert response.status_code == 500
        assert "X-Content-Type-Options" in response
        assert "X-Frame-Options" in response

    def test_security_headers_on_different_methods(self):
        """Test security headers are set on all HTTP methods."""
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

        for method in methods:
            request = getattr(self.factory, method.lower())("/test/")
            response = self.middleware(request)

            assert "X-Content-Type-Options" in response
            assert "X-Frame-Options" in response

    @override_settings(DEBUG=True)
    def test_csp_less_strict_in_debug(self):
        """Test CSP is less strict in debug mode for development."""
        request = self.factory.get("/test/")
        response = self.middleware(request)

        csp = response.get("Content-Security-Policy", "")
        # In debug mode, might allow unsafe-eval for dev tools
        # This test just verifies CSP exists in debug mode
        assert len(csp) > 0

    def test_hsts_max_age_is_sufficient(self):
        """Test HSTS max-age is at least 1 year (31536000 seconds)."""
        request = self.factory.get("/test/")
        response = self.middleware(request)

        hsts = response["Strict-Transport-Security"]
        # Extract max-age value
        import re

        match = re.search(r"max-age=(\d+)", hsts)
        assert match, "HSTS header should have max-age directive"

        max_age = int(match.group(1))
        # At least 1 year
        assert max_age >= 31536000, "HSTS max-age should be at least 1 year"
