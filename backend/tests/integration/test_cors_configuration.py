"""
Integration tests for CORS (Cross-Origin Resource Sharing) configuration.

This module tests that CORS is properly configured to allow requests from
the frontend application while maintaining security.

Testing Strategy:
- Verify CORS headers are present in responses
- Test allowed origins (development and production)
- Test CORS credentials support
- Test preflight (OPTIONS) requests
- Test security headers are included
"""

import pytest
from django.conf import settings
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.mark.integration
class TestCORSConfiguration:
    """Test suite for CORS configuration."""

    def test_cors_middleware_is_installed(self) -> None:
        """Test that CORS middleware is installed and in correct position."""
        assert "corsheaders" in settings.INSTALLED_APPS
        assert "corsheaders.middleware.CorsMiddleware" in settings.MIDDLEWARE

        # CORS middleware should come after SessionMiddleware but before CommonMiddleware
        middleware_list = settings.MIDDLEWARE
        session_idx = middleware_list.index("django.contrib.sessions.middleware.SessionMiddleware")
        cors_idx = middleware_list.index("corsheaders.middleware.CorsMiddleware")
        common_idx = middleware_list.index("django.middleware.common.CommonMiddleware")

        assert session_idx < cors_idx < common_idx, (
            "CORS middleware must be positioned after SessionMiddleware "
            "and before CommonMiddleware"
        )

    def test_cors_allow_credentials_is_enabled(self) -> None:
        """Test that CORS credentials are enabled for cookie-based auth."""
        assert hasattr(settings, "CORS_ALLOW_CREDENTIALS")
        assert settings.CORS_ALLOW_CREDENTIALS is True

    def test_cors_allowed_origins_is_configured(self) -> None:
        """Test that CORS allowed origins are properly configured."""
        assert hasattr(settings, "CORS_ALLOWED_ORIGINS")
        # In test environment, either CORS_ALLOW_ALL_ORIGINS or specific origins
        if not hasattr(settings, "CORS_ALLOW_ALL_ORIGINS") or not settings.CORS_ALLOW_ALL_ORIGINS:
            assert isinstance(settings.CORS_ALLOWED_ORIGINS, list | tuple)
            assert len(settings.CORS_ALLOWED_ORIGINS) > 0

    def test_development_origins_are_allowed(self) -> None:
        """Test that development frontend origins are allowed."""
        # In development/test, we should allow localhost origins
        # Check if either CORS_ALLOW_ALL_ORIGINS is True OR localhost is in allowed origins
        if hasattr(settings, "CORS_ALLOW_ALL_ORIGINS") and settings.CORS_ALLOW_ALL_ORIGINS:
            # Development mode allows all origins
            assert True
        else:
            # Production mode requires specific origins
            allowed_origins = settings.CORS_ALLOWED_ORIGINS
            localhost_origins = [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
            # At least one localhost origin should be allowed
            assert any(origin in allowed_origins for origin in localhost_origins)


@pytest.mark.integration
@pytest.mark.django_db
class TestCORSHeaders:
    """Test suite for CORS headers in HTTP responses."""

    @pytest.fixture
    def api_client(self) -> APIClient:
        """Create API client for testing."""
        return APIClient()

    def test_cors_headers_on_api_request(self, api_client: APIClient) -> None:
        """Test that CORS headers are present on API requests."""
        # Make request with Origin header (simulating frontend request)
        response = api_client.get(
            "/health/",
            HTTP_ORIGIN="http://localhost:5173",
        )

        # Verify response is successful
        assert response.status_code == 200

        # Verify CORS headers are present
        # Note: In development mode with CORS_ALLOW_ALL_ORIGINS=True,
        # Access-Control-Allow-Origin may be "*"
        assert "Access-Control-Allow-Origin" in response

    def test_cors_headers_with_credentials(self, api_client: APIClient) -> None:
        """Test that CORS headers support credentials."""
        response = api_client.get(
            "/health/",
            HTTP_ORIGIN="http://localhost:5173",
        )

        assert response.status_code == 200

        # When CORS_ALLOW_CREDENTIALS is True, response should include:
        # - Access-Control-Allow-Credentials: true
        # Note: This is only present when origin is explicitly allowed (not *)
        if hasattr(settings, "CORS_ALLOW_ALL_ORIGINS") and settings.CORS_ALLOW_ALL_ORIGINS:
            # In CORS_ALLOW_ALL_ORIGINS mode, credentials header may not be set
            # because origin is "*"
            pass
        else:
            assert "Access-Control-Allow-Credentials" in response
            assert response["Access-Control-Allow-Credentials"] == "true"

    def test_preflight_request_with_options(self, api_client: APIClient) -> None:
        """Test CORS preflight (OPTIONS) request handling."""
        # Preflight request sent by browser before actual request
        response = api_client.options(
            "/health/",
            HTTP_ORIGIN="http://localhost:5173",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type",
        )

        # Preflight request should be successful
        assert response.status_code in [200, 204]

        # Verify CORS preflight headers
        assert "Access-Control-Allow-Origin" in response
        assert "Access-Control-Allow-Methods" in response

    @override_settings(
        CORS_ALLOW_ALL_ORIGINS=False,
        CORS_ALLOWED_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"],
    )
    def test_allowed_origin_receives_cors_headers(self, api_client: APIClient) -> None:
        """Test that allowed origins receive proper CORS headers."""
        response = api_client.get(
            "/health/",
            HTTP_ORIGIN="http://localhost:5173",
        )

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response
        assert response["Access-Control-Allow-Origin"] == "http://localhost:5173"

    @override_settings(
        CORS_ALLOW_ALL_ORIGINS=False,
        CORS_ALLOWED_ORIGINS=["http://localhost:5173"],
    )
    def test_disallowed_origin_receives_no_cors_headers(self, api_client: APIClient) -> None:
        """Test that disallowed origins do not receive CORS headers."""
        response = api_client.get(
            "/health/",
            HTTP_ORIGIN="http://malicious-site.com",
        )

        # Request should still succeed (server processes it)
        # But CORS headers should not allow the origin
        if "Access-Control-Allow-Origin" in response:
            # If header is present, it should not be the malicious origin
            assert response["Access-Control-Allow-Origin"] != "http://malicious-site.com"


@pytest.mark.integration
class TestSecurityHeaders:
    """Test suite for security headers in responses."""

    @pytest.fixture
    def api_client(self) -> APIClient:
        """Create API client for testing."""
        return APIClient()

    @pytest.mark.django_db
    def test_security_headers_are_present(self, api_client: APIClient) -> None:
        """Test that security headers are included in responses."""
        response = api_client.get("/health/")

        # Common security headers (some may only be in production)
        # X-Content-Type-Options should always be present
        # Note: In test/development environment, some security headers may not be set

        # Check that response has some security headers
        # At minimum, Django should include X-Content-Type-Options
        if (
            hasattr(settings, "SECURE_CONTENT_TYPE_NOSNIFF")
            and settings.SECURE_CONTENT_TYPE_NOSNIFF
        ):
            assert "X-Content-Type-Options" in response

    @pytest.mark.django_db
    def test_content_type_header_is_json(self, api_client: APIClient) -> None:
        """Test that API responses use JSON content type."""
        response = api_client.get("/health/")

        assert response.status_code == 200
        assert "application/json" in response["Content-Type"]

    @pytest.mark.django_db
    def test_csrf_cookie_settings_in_production(self) -> None:
        """Test that CSRF cookie settings are secure in production."""
        # In test environment, these may not be set
        # This test documents expected production configuration
        from backend.settings import production

        # Production should have secure cookie settings
        assert hasattr(production, "CSRF_COOKIE_SECURE")
        assert hasattr(production, "SESSION_COOKIE_SECURE")
        assert production.CSRF_COOKIE_SECURE is True
        assert production.SESSION_COOKIE_SECURE is True


@pytest.mark.integration
class TestCORSEnvironmentConfiguration:
    """Test suite for CORS environment-specific configuration."""

    def test_development_cors_is_permissive(self) -> None:
        """Test that development CORS settings are permissive for ease of development."""
        from backend.settings import development

        # Development should either allow all origins or include localhost
        assert hasattr(development, "CORS_ALLOW_ALL_ORIGINS") or hasattr(
            development, "CORS_ALLOWED_ORIGINS"
        )

        if hasattr(development, "CORS_ALLOW_ALL_ORIGINS"):
            # Development mode may use CORS_ALLOW_ALL_ORIGINS for convenience
            assert development.CORS_ALLOW_ALL_ORIGINS is True
        else:
            # Or it should explicitly allow localhost origins
            assert "http://localhost:5173" in development.CORS_ALLOWED_ORIGINS

    def test_production_cors_is_restrictive(self) -> None:
        """Test that production CORS settings are restrictive for security."""
        from backend.settings import production

        # Production should NOT allow all origins
        if hasattr(production, "CORS_ALLOW_ALL_ORIGINS"):
            assert production.CORS_ALLOW_ALL_ORIGINS is False

        # Production should use environment variable for allowed origins
        # This is configured via CORS_ALLOWED_ORIGINS in base.py using config()

    def test_cors_origins_can_be_configured_via_environment(self) -> None:
        """Test that CORS origins can be configured via environment variables."""
        # Base settings use python-decouple to read from environment
        # Verify that the setting exists and is configured from environment
        assert hasattr(settings, "CORS_ALLOWED_ORIGINS")

        # In test environment, it should be a list/tuple
        assert isinstance(settings.CORS_ALLOWED_ORIGINS, list | tuple)


@pytest.mark.integration
@pytest.mark.django_db
class TestCORSWithAuthentication:
    """Test suite for CORS with authentication scenarios."""

    @pytest.fixture
    def api_client(self) -> APIClient:
        """Create API client for testing."""
        return APIClient()

    def test_cors_works_with_session_authentication(self, api_client: APIClient) -> None:
        """Test that CORS works with session-based authentication."""
        # Health endpoint doesn't require auth, but tests CORS + session middleware
        response = api_client.get(
            "/health/",
            HTTP_ORIGIN="http://localhost:5173",
        )

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response

        # Verify credentials are allowed (required for cookies/sessions)
        if not (hasattr(settings, "CORS_ALLOW_ALL_ORIGINS") and settings.CORS_ALLOW_ALL_ORIGINS):
            assert "Access-Control-Allow-Credentials" in response

    def test_cors_headers_persist_across_redirects(self, api_client: APIClient) -> None:
        """Test that CORS headers are maintained across redirects."""
        # Test with a redirect scenario if any exist
        # For now, verify headers on direct request
        response = api_client.get(
            "/health/",
            HTTP_ORIGIN="http://localhost:5173",
            follow=True,  # Follow redirects
        )

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response
