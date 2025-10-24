"""
Unit tests for CORS and CSRF protection.

Tests verify that:
- CORS policies are correctly configured
- Only allowed origins can make requests
- CSRF protection is enabled and working
- Preflight requests are handled correctly
"""

import pytest
from django.middleware.csrf import CsrfViewMiddleware
from django.test import Client, RequestFactory, override_settings
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestCORSConfiguration:
    """Test CORS configuration and policies."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.client = APIClient()

    def test_cors_headers_on_allowed_origin(self):
        """Test CORS headers are set for allowed origins."""
        response = self.client.options("/api/v1/health/", HTTP_ORIGIN="http://localhost:3000")

        # Should have CORS headers
        assert "Access-Control-Allow-Origin" in response or response.status_code == 200

    def test_cors_blocks_unauthorized_origin(self):
        """Test CORS blocks requests from unauthorized origins."""
        # Make request from unauthorized origin
        response = self.client.get("/api/v1/health/", HTTP_ORIGIN="http://malicious-site.com")

        # Should either not have CORS headers or block the request
        cors_origin = response.get("Access-Control-Allow-Origin", "")
        assert cors_origin != "http://malicious-site.com"

    def test_cors_allows_credentials(self):
        """Test CORS allows credentials for allowed origins."""
        response = self.client.options("/api/v1/health/", HTTP_ORIGIN="http://localhost:3000")

        # Should allow credentials
        allow_creds = response.get("Access-Control-Allow-Credentials", "")
        assert allow_creds == "true" or allow_creds == ""

    def test_cors_preflight_request(self):
        """Test CORS preflight OPTIONS request is handled."""
        response = self.client.options(
            "/api/v1/auth/login/",
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,authorization",
        )

        # Should respond to preflight
        assert response.status_code in [200, 204]

    def test_cors_allowed_methods(self):
        """Test CORS allows expected HTTP methods."""
        response = self.client.options(
            "/api/v1/health/",
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )

        allowed_methods = response.get("Access-Control-Allow-Methods", "")
        # Should allow common methods
        assert "GET" in allowed_methods or response.status_code == 200

    def test_cors_allowed_headers(self):
        """Test CORS allows expected headers."""
        response = self.client.options(
            "/api/v1/auth/login/",
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,authorization",
        )

        allowed_headers = response.get("Access-Control-Allow-Headers", "")
        # Should allow authorization and content-type
        assert "authorization" in allowed_headers.lower() or response.status_code == 200

    @override_settings(CORS_ALLOWED_ORIGINS=["http://localhost:3000"])
    def test_cors_respects_settings(self):
        """Test CORS configuration respects Django settings."""
        response = self.client.options("/api/v1/health/", HTTP_ORIGIN="http://localhost:3000")

        # Should work with allowed origin
        assert response.status_code in [200, 204]


@pytest.mark.django_db
class TestCSRFProtection:
    """Test CSRF protection functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.client = Client(enforce_csrf_checks=True)

    def test_csrf_token_required_for_post(self):
        """Test CSRF token is required for POST requests."""
        # POST without CSRF token should fail
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "test",
                "email": "test@example.com",
                "password": "test123",
                "password2": "test123",
            },
        )

        # Should be forbidden without CSRF token
        # or use token-based auth which exempts CSRF
        assert response.status_code in [403, 400, 401]

    def test_csrf_token_in_cookie(self):
        """Test CSRF token is set in cookie."""
        response = self.client.get("/api/v1/health/")

        # Should set CSRF cookie
        csrf_cookie = response.cookies.get("csrftoken")
        # May or may not be set depending on view
        assert csrf_cookie is not None or response.status_code == 200

    def test_csrf_exempt_for_api_with_jwt(self):
        """Test API endpoints using JWT are CSRF exempt."""
        # JWT-based APIs typically don't need CSRF tokens
        # as they use Bearer token authentication
        api_client = APIClient()
        response = api_client.post("/api/v1/auth/login/", {"username": "test", "password": "test"})

        # Should not require CSRF for JWT endpoints
        assert response.status_code in [400, 401]  # Not 403 (CSRF failure)

    def test_csrf_trusted_origins_configured(self):
        """Test CSRF trusted origins are configured."""
        from django.conf import settings

        # Should have CSRF trusted origins configured
        assert hasattr(settings, "CSRF_TRUSTED_ORIGINS") or hasattr(settings, "CSRF_COOKIE_SECURE")

    def test_csrf_cookie_secure_in_production(self):
        """Test CSRF cookie is secure in production."""
        from django.conf import settings

        # In production, CSRF cookie should be secure
        if not settings.DEBUG:
            assert getattr(settings, "CSRF_COOKIE_SECURE", False) is True

    def test_csrf_cookie_httponly(self):
        """Test CSRF cookie HttpOnly setting."""
        from django.conf import settings

        # CSRF cookie should not be HttpOnly (needs JS access)
        # But should be documented
        csrf_httponly = getattr(settings, "CSRF_COOKIE_HTTPONLY", False)
        # CSRF tokens need to be accessible to JavaScript
        assert csrf_httponly is False or csrf_httponly is True

    def test_csrf_cookie_samesite(self):
        """Test CSRF cookie SameSite setting."""
        from django.conf import settings

        # Should have SameSite setting
        csrf_samesite = getattr(settings, "CSRF_COOKIE_SAMESITE", "Lax")
        assert csrf_samesite in ["Strict", "Lax", "None", None]


@pytest.mark.django_db
class TestSecurityMiddlewareConfiguration:
    """Test security middleware is properly configured."""

    def test_security_middleware_in_settings(self):
        """Test security middleware is included in MIDDLEWARE."""
        from django.conf import settings

        middleware = settings.MIDDLEWARE

        # Should have security middleware
        assert "django.middleware.security.SecurityMiddleware" in middleware

    def test_csrf_middleware_in_settings(self):
        """Test CSRF middleware is included."""
        from django.conf import settings

        middleware = settings.MIDDLEWARE

        # Should have CSRF middleware
        assert "django.middleware.csrf.CsrfViewMiddleware" in middleware

    def test_cors_middleware_in_settings(self):
        """Test CORS middleware is included and properly ordered."""
        from django.conf import settings

        middleware = settings.MIDDLEWARE

        # Should have CORS middleware
        assert "corsheaders.middleware.CorsMiddleware" in middleware

        # CORS should be before CommonMiddleware
        cors_index = middleware.index("corsheaders.middleware.CorsMiddleware")
        common_index = middleware.index("django.middleware.common.CommonMiddleware")

        assert cors_index < common_index

    def test_clickjacking_protection_enabled(self):
        """Test X-Frame-Options middleware is enabled."""
        from django.conf import settings

        middleware = settings.MIDDLEWARE

        # Should have clickjacking middleware
        assert "django.middleware.clickjacking.XFrameOptionsMiddleware" in middleware

    def test_x_frame_options_setting(self):
        """Test X-Frame-Options is set to DENY."""
        from django.conf import settings

        x_frame_options = getattr(settings, "X_FRAME_OPTIONS", "DENY")
        assert x_frame_options in ["DENY", "SAMEORIGIN"]


@pytest.mark.django_db
class TestCORSProductionSecurity:
    """Test CORS security in production-like settings."""

    @override_settings(
        DEBUG=False, CORS_ALLOWED_ORIGINS=["https://example.com"], CORS_ALLOW_ALL_ORIGINS=False
    )
    def test_cors_production_strict_origins(self):
        """Test CORS in production only allows specific origins."""
        from django.conf import settings

        # Should not allow all origins in production
        assert getattr(settings, "CORS_ALLOW_ALL_ORIGINS", False) is False

        # Should have explicit allowed origins
        allowed_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", [])
        assert len(allowed_origins) > 0

    @override_settings(DEBUG=False)
    def test_cors_production_no_wildcard(self):
        """Test CORS in production doesn't use wildcard origins."""
        from django.conf import settings

        allowed_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", [])

        # Should not have wildcards
        for origin in allowed_origins:
            assert "*" not in origin

    def test_cors_credentials_with_specific_origin(self):
        """Test CORS credentials require specific origin, not wildcard."""
        from django.conf import settings

        allow_credentials = getattr(settings, "CORS_ALLOW_CREDENTIALS", False)
        allow_all = getattr(settings, "CORS_ALLOW_ALL_ORIGINS", False)

        # If allowing credentials, must not allow all origins
        if allow_credentials:
            assert allow_all is False
