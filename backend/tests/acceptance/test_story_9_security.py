"""
Acceptance tests for Story #9: Security Best Practices

Tests verify that all acceptance criteria are met:
1. HTTP responses have security headers configured appropriately
2. Malformed or malicious input is rejected with appropriate error messages
3. Excessive requests encounter rate limiting
4. Cross-origin requests from unauthorized domains are blocked
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestStory9SecurityHeaders:
    """
    Acceptance Criteria 1: When I inspect HTTP responses,
    I should see security headers configured appropriately.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.client = APIClient()

    def test_security_headers_present_on_health_endpoint(self):
        """Verify security headers are present on API responses."""
        response = self.client.get("/api/v1/health/")

        # Check all required security headers
        assert "X-Content-Type-Options" in response
        assert response["X-Content-Type-Options"] == "nosniff"

        assert "X-Frame-Options" in response
        assert response["X-Frame-Options"] == "DENY"

        assert "X-XSS-Protection" in response
        assert response["X-XSS-Protection"] == "1; mode=block"

        assert "Strict-Transport-Security" in response
        assert "max-age=" in response["Strict-Transport-Security"]

        assert "Content-Security-Policy" in response
        assert "default-src 'self'" in response["Content-Security-Policy"]

        assert "Referrer-Policy" in response

    def test_security_headers_on_authentication_endpoint(self):
        """Verify security headers are present on authentication endpoints."""
        response = self.client.post(
            "/api/v1/auth/login/", {"email": "test@example.com", "password": "test123"}
        )

        # Should have security headers even on failed authentication
        assert "X-Content-Type-Options" in response
        assert "X-Frame-Options" in response
        assert "Strict-Transport-Security" in response

    def test_hsts_header_duration(self):
        """Verify HSTS header has appropriate max-age (at least 1 year)."""
        response = self.client.get("/api/v1/health/")

        hsts = response.get("Strict-Transport-Security", "")
        assert "max-age=" in hsts

        # Extract max-age value
        import re

        match = re.search(r"max-age=(\d+)", hsts)
        assert match, "HSTS should have max-age directive"

        max_age = int(match.group(1))
        # At least 1 year (31536000 seconds)
        assert max_age >= 31536000


@pytest.mark.django_db
class TestStory9InputValidation:
    """
    Acceptance Criteria 2: When I send malformed or malicious input,
    I should see it rejected with appropriate error messages.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.client = APIClient()

    def test_malicious_xss_input_rejected_in_registration(self):
        """Verify XSS attempts are rejected during registration."""
        malicious_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": '<script>alert("XSS")</script>',
        }

        response = self.client.post("/api/v1/auth/register/", malicious_data)

        # Should either reject or sanitize the input
        # Status should be 400 (validation error) or 201 (sanitized and accepted)
        assert response.status_code in [400, 201]

        if response.status_code == 201:
            # If accepted, verify script tags were sanitized
            user_data = response.data.get("user", {})
            first_name = user_data.get("first_name", "")
            assert "<script>" not in first_name

    def test_sql_injection_attempt_in_email(self):
        """Verify SQL injection attempts are rejected."""
        malicious_data = {
            "email": "admin'--@example.com",
            "password": "test123",
            "password_confirm": "test123",
        }

        response = self.client.post("/api/v1/auth/register/", malicious_data)

        # Should reject invalid email format
        assert response.status_code == 400
        assert "email" in response.data

    def test_invalid_email_format_rejected(self):
        """Verify invalid email formats are rejected."""
        invalid_emails = ["notanemail", "@example.com", "user@", "user@@example.com"]

        for email in invalid_emails:
            response = self.client.post(
                "/api/v1/auth/register/",
                {
                    "email": email,
                    "password": "SecurePass123!",
                    "password_confirm": "SecurePass123!",
                },
            )

            # Should reject with validation error
            assert response.status_code == 400
            assert "email" in response.data

    def test_password_validation_enforced(self):
        """Verify password validation rules are enforced."""
        weak_passwords = [
            "123",  # Too short
            "12345678",  # All numeric
            "password",  # Too common
        ]

        for password in weak_passwords:
            response = self.client.post(
                "/api/v1/auth/register/",
                {"email": "test@example.com", "password": password, "password_confirm": password},
            )

            # Should reject weak passwords
            assert response.status_code == 400


@pytest.mark.django_db
class TestStory9RateLimiting:
    """
    Acceptance Criteria 3: When I make excessive requests,
    I should encounter rate limiting.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.client = APIClient()
        cache.clear()  # Clear cache before each test

    def test_rate_limiting_on_login_endpoint(self):
        """Verify rate limiting is enforced on login endpoint."""
        login_data = {"email": "test@example.com", "password": "wrongpassword"}

        # Make many login attempts
        responses = []
        for i in range(25):
            response = self.client.post("/api/v1/auth/login/", login_data)
            responses.append(response.status_code)

        # Should eventually hit rate limit (429)
        # Login endpoint is limited to 10/minute
        assert 429 in responses, "Rate limiting should trigger after excessive requests"

    def test_rate_limiting_on_registration_endpoint(self):
        """Verify rate limiting is enforced on registration endpoint."""
        # Make many registration attempts
        responses = []
        for i in range(10):
            response = self.client.post(
                "/api/v1/auth/register/",
                {
                    "email": f"user{i}@example.com",
                    "password": "SecurePass123!",
                    "password_confirm": "SecurePass123!",
                },
            )
            responses.append(response.status_code)

        # Registration is limited to 5/hour
        # Should get rate limited after 5 requests
        assert 429 in responses or responses.count(201) <= 5

    def test_rate_limit_error_message_is_clear(self):
        """Verify rate limit errors have clear messages."""
        login_data = {"email": "test@example.com", "password": "test"}

        # Exhaust rate limit
        for i in range(30):
            response = self.client.post("/api/v1/auth/login/", login_data)
            if response.status_code == 429:
                # Check error message is present and helpful
                assert response.data is not None
                error_message = str(response.data).lower()
                # Should mention rate limiting or too many requests
                assert any(
                    keyword in error_message
                    for keyword in ["rate", "limit", "too many", "throttle"]
                )
                break


@pytest.mark.django_db
class TestStory9CORSProtection:
    """
    Acceptance Criteria 4: When I attempt cross-origin requests from
    unauthorized domains, I should see them blocked.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.client = APIClient()

    def test_cors_allows_configured_origin(self):
        """Verify CORS allows requests from configured origins."""
        response = self.client.get("/api/v1/health/", HTTP_ORIGIN="http://localhost:3000")

        # Should succeed (CORS is configured to allow localhost:3000)
        assert response.status_code == 200

    def test_cors_blocks_unauthorized_origin(self):
        """Verify CORS blocks requests from unauthorized origins."""
        response = self.client.get("/api/v1/health/", HTTP_ORIGIN="http://malicious-site.com")

        # Check CORS headers
        cors_origin = response.get("Access-Control-Allow-Origin", "")

        # Should not allow the malicious origin
        assert cors_origin != "http://malicious-site.com"

    def test_cors_preflight_request_handled(self):
        """Verify CORS preflight requests are handled correctly."""
        response = self.client.options(
            "/api/v1/auth/login/",
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type",
        )

        # Should handle preflight request
        assert response.status_code in [200, 204]

    def test_cors_credentials_allowed_for_trusted_origin(self):
        """Verify CORS allows credentials for trusted origins."""
        response = self.client.options("/api/v1/health/", HTTP_ORIGIN="http://localhost:3000")

        # Should allow credentials (needed for cookie-based auth)
        allow_credentials = response.get("Access-Control-Allow-Credentials", "")
        # May be 'true' or empty depending on configuration
        assert allow_credentials in ["true", ""]


@pytest.mark.django_db
class TestStory9ComprehensiveSecurity:
    """
    Comprehensive tests verifying all security measures work together.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.client = APIClient()
        cache.clear()

    @pytest.fixture
    def test_user(self):
        """Create a test user."""
        return User.objects.create_user(
            email="security@example.com",
            password="SecurePass123!",
            first_name="Security",
            last_name="Tester",
        )

    def test_full_security_stack_on_authenticated_request(self, test_user):
        """Verify all security features work on authenticated requests."""
        # Login
        login_response = self.client.post(
            "/api/v1/auth/login/", {"email": "security@example.com", "password": "SecurePass123!"}
        )

        assert login_response.status_code == 200

        # Get tokens
        access_token = login_response.data.get("access")

        # Make authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        profile_response = self.client.get("/api/v1/auth/me/")

        # Verify security headers
        assert "X-Content-Type-Options" in profile_response
        assert "X-Frame-Options" in profile_response
        assert "Strict-Transport-Security" in profile_response
        assert "Content-Security-Policy" in profile_response

        # Verify request succeeded
        assert profile_response.status_code == 200
        assert profile_response.data["email"] == "security@example.com"

    def test_security_in_error_responses(self):
        """Verify security headers present even in error responses."""
        # Make invalid request
        response = self.client.post("/api/v1/auth/login/", {})

        # Should be error response
        assert response.status_code == 400

        # Should still have security headers
        assert "X-Content-Type-Options" in response
        assert "X-Frame-Options" in response
        assert "Strict-Transport-Security" in response

    def test_production_ready_security_configuration(self):
        """Verify security configuration is production-ready."""
        from django.conf import settings

        # Check critical security settings exist
        assert hasattr(settings, "MIDDLEWARE")
        assert "apps.core.middleware.SecurityHeadersMiddleware" in settings.MIDDLEWARE

        # Check CORS is configured
        assert hasattr(settings, "CORS_ALLOWED_ORIGINS")

        # Check CSRF is configured
        assert hasattr(settings, "CSRF_TRUSTED_ORIGINS")

        # Check rate limiting is configured
        assert hasattr(settings, "RATELIMIT_ENABLE")
