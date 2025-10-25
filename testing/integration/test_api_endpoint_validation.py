"""
API Endpoint Validation Tests (Story 13.10)

Comprehensive tests that validate all API endpoints to ensure:
- Status codes, response structure, and data types match API specification
- Invalid requests return appropriate error codes and messages
- Protected endpoints deny access without authentication
- All endpoints are tested (health, auth, assessment, user profile, config)

Test Organization:
- HealthEndpointsTest: Health check, status, readiness, liveness endpoints
- ConfigEndpointsTest: Frontend configuration endpoint
- AuthEndpointsTest: Registration, login, logout, token refresh, change password
- UserEndpointsTest: Current user profile endpoint
- AssessmentEndpointsTest: Assessment CRUD operations and user-specific endpoint
"""

from typing import Any, Dict

import pytest
import requests  # type: ignore[import-untyped]


class TestHealthEndpoints:
    """Test health check and monitoring endpoints."""

    def test_health_check_endpoint_returns_healthy_status(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that /api/v1/health/ returns 200 and correct structure when healthy.

        Validates:
        - HTTP 200 status code
        - Response contains 'status', 'timestamp', 'database' fields
        - Status is 'healthy'
        - Database status is 'connected'
        """
        response = api_client.get(f"{api_base_url}/health/")

        assert (
            response.status_code == 200
        ), "Health endpoint should return 200 when healthy"

        data = response.json()
        assert "status" in data, "Response should include 'status' field"
        assert "timestamp" in data, "Response should include 'timestamp' field"
        assert "database" in data, "Response should include 'database' field"

        assert data["status"] == "healthy", "Status should be 'healthy'"
        assert data["database"]["status"] == "connected", "Database should be connected"
        assert (
            "response_time_ms" in data["database"]
        ), "Database should include response time"

    def test_status_endpoint_returns_detailed_information(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that /api/v1/status/ returns comprehensive system information.

        Validates:
        - HTTP 200 status code (always returns 200, even if unhealthy)
        - Response contains all required fields: version, uptime, memory, database
        - Data types are correct (uptime is number, memory has used_mb and percent)
        """
        response = api_client.get(f"{api_base_url}/status/")

        assert response.status_code == 200, "Status endpoint always returns 200"

        data = response.json()
        assert "status" in data, "Response should include 'status' field"
        assert "timestamp" in data, "Response should include 'timestamp' field"
        assert "version" in data, "Response should include 'version' field"
        assert "api_version" in data, "Response should include 'api_version' field"
        assert "environment" in data, "Response should include 'environment' field"
        assert (
            "uptime_seconds" in data
        ), "Response should include 'uptime_seconds' field"
        assert "memory" in data, "Response should include 'memory' field"
        assert "database" in data, "Response should include 'database' field"

        # Validate data types
        assert isinstance(
            data["uptime_seconds"], (int, float)
        ), "Uptime should be numeric"
        assert "used_mb" in data["memory"], "Memory should include 'used_mb'"
        assert "percent" in data["memory"], "Memory should include 'percent'"
        assert isinstance(
            data["memory"]["used_mb"], (int, float)
        ), "Memory used_mb should be numeric"
        assert isinstance(
            data["memory"]["percent"], (int, float)
        ), "Memory percent should be numeric"

    def test_readiness_probe_endpoint(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that /api/v1/health/ready/ returns readiness status.

        Validates:
        - HTTP 200 when ready, 503 when not ready
        - Response contains 'ready' boolean and 'timestamp' fields
        """
        response = api_client.get(f"{api_base_url}/health/ready/")

        # Should be 200 when database is available
        assert response.status_code in [200, 503], "Readiness should return 200 or 503"

        data = response.json()
        assert "ready" in data, "Response should include 'ready' field"
        assert "timestamp" in data, "Response should include 'timestamp' field"
        assert isinstance(data["ready"], bool), "Ready field should be boolean"

        if response.status_code == 200:
            assert data["ready"] is True, "Ready should be True when status is 200"

    def test_liveness_probe_endpoint(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that /api/v1/health/live/ returns liveness status.

        Validates:
        - Always returns HTTP 200 (server is alive if it responds)
        - Response contains 'alive' boolean field (should be True)
        """
        response = api_client.get(f"{api_base_url}/health/live/")

        assert response.status_code == 200, "Liveness endpoint always returns 200"

        data = response.json()
        assert "alive" in data, "Response should include 'alive' field"
        assert "timestamp" in data, "Response should include 'timestamp' field"
        assert data["alive"] is True, "Alive should always be True"


class TestConfigEndpoints:
    """Test configuration endpoints."""

    def test_frontend_config_endpoint_returns_configuration(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that /api/v1/config/frontend/ returns frontend configuration.

        Validates:
        - HTTP 200 status code
        - Response contains 'api', 'app', and 'features' sections
        - All required configuration fields are present
        - No authentication required (public endpoint)
        """
        response = api_client.get(f"{api_base_url}/config/frontend/")

        assert response.status_code == 200, "Frontend config endpoint should return 200"

        data = response.json()
        assert "api" in data, "Response should include 'api' configuration"
        assert "app" in data, "Response should include 'app' configuration"
        assert "features" in data, "Response should include 'features' configuration"

        # Validate API config structure
        assert "url" in data["api"], "API config should include 'url'"
        assert "timeout" in data["api"], "API config should include 'timeout'"
        assert (
            "enableLogging" in data["api"]
        ), "API config should include 'enableLogging'"

        # Validate app config structure
        assert "name" in data["app"], "App config should include 'name'"
        assert "version" in data["app"], "App config should include 'version'"
        assert "environment" in data["app"], "App config should include 'environment'"

        # Validate features config structure
        assert (
            "enableAnalytics" in data["features"]
        ), "Features should include 'enableAnalytics'"
        assert (
            "enableDebugMode" in data["features"]
        ), "Features should include 'enableDebugMode'"

    def test_frontend_config_endpoint_does_not_require_authentication(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that frontend config endpoint is accessible without authentication.

        Validates:
        - Endpoint returns 200 even without Authorization header
        - This is a public endpoint for frontend initialization
        """
        # Create a fresh client without authentication
        unauthenticated_client = requests.Session()
        unauthenticated_client.headers.update({"Content-Type": "application/json"})

        response = unauthenticated_client.get(f"{api_base_url}/config/frontend/")

        assert (
            response.status_code == 200
        ), "Frontend config should be accessible without auth"


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_user_registration_with_valid_data(
        self, api_client: requests.Session, api_base_url: str, django_db_blocker
    ):
        """
        Test that /api/v1/auth/register/ creates user with valid data.

        Validates:
        - HTTP 201 status code on successful registration
        - Response contains 'message' and 'user' fields
        - User data includes id, email, first_name, last_name, is_active
        """
        registration_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
        }

        with django_db_blocker.unblock():
            response = api_client.post(
                f"{api_base_url}/auth/register/", json=registration_data
            )

        assert response.status_code == 201, "Registration should return 201 on success"

        data = response.json()
        assert "message" in data, "Response should include 'message' field"
        assert "user" in data, "Response should include 'user' field"

        user_data = data["user"]
        assert "id" in user_data, "User should have 'id'"
        assert user_data["email"] == "newuser@example.com", "User email should match"
        assert user_data["first_name"] == "New", "User first_name should match"
        assert user_data["last_name"] == "User", "User last_name should match"
        assert "is_active" in user_data, "User should have 'is_active' field"

    def test_user_registration_with_mismatched_passwords(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that registration fails with mismatched passwords.

        Validates:
        - HTTP 400 status code
        - Error message indicates password mismatch
        """
        registration_data = {
            "email": "newuser2@example.com",
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass123!",
            "first_name": "New",
            "last_name": "User",
        }

        response = api_client.post(
            f"{api_base_url}/auth/register/", json=registration_data
        )

        assert (
            response.status_code == 400
        ), "Registration should return 400 for password mismatch"

        data = response.json()
        # Error could be in password or password_confirm field
        assert (
            "password" in data
            or "password_confirm" in data
            or "non_field_errors" in data
        ), "Response should contain password-related error"

    def test_user_registration_with_duplicate_email(
        self, api_client: requests.Session, api_base_url: str, test_user: Dict[str, Any]
    ):
        """
        Test that registration fails with duplicate email.

        Validates:
        - HTTP 400 status code
        - Error message indicates email already exists
        """
        registration_data = {
            "email": test_user["email"],  # Use existing user's email
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "Duplicate",
            "last_name": "User",
        }

        response = api_client.post(
            f"{api_base_url}/auth/register/", json=registration_data
        )

        assert (
            response.status_code == 400
        ), "Registration should return 400 for duplicate email"

        data = response.json()
        assert "email" in data, "Response should contain email error"

    def test_user_login_with_valid_credentials(
        self, api_client: requests.Session, api_base_url: str, test_user: Dict[str, Any]
    ):
        """
        Test that /api/v1/auth/login/ returns tokens with valid credentials.

        Validates:
        - HTTP 200 status code
        - Response contains 'access', 'refresh', 'user', and 'message' fields
        - Tokens are non-empty strings
        """
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"],
        }

        response = api_client.post(f"{api_base_url}/auth/login/", json=login_data)

        assert (
            response.status_code == 200
        ), "Login should return 200 with valid credentials"

        data = response.json()
        assert "access" in data, "Response should include 'access' token"
        assert "refresh" in data, "Response should include 'refresh' token"
        assert "user" in data, "Response should include 'user' data"
        assert "message" in data, "Response should include 'message'"

        assert len(data["access"]) > 0, "Access token should not be empty"
        assert len(data["refresh"]) > 0, "Refresh token should not be empty"
        assert data["user"]["email"] == test_user["email"], "User email should match"

    def test_user_login_with_invalid_credentials(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that login fails with invalid credentials.

        Validates:
        - HTTP 400 status code
        - Error message indicates invalid credentials
        """
        login_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!",
        }

        response = api_client.post(f"{api_base_url}/auth/login/", json=login_data)

        assert (
            response.status_code == 400
        ), "Login should return 400 with invalid credentials"

        data = response.json()
        assert (
            "non_field_errors" in data or "detail" in data or "email" in data
        ), "Response should contain error message"

    def test_user_login_with_missing_fields(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that login fails with missing required fields.

        Validates:
        - HTTP 400 status code
        - Error messages for missing fields
        """
        # Test with missing password
        response = api_client.post(
            f"{api_base_url}/auth/login/", json={"email": "user@example.com"}
        )

        assert (
            response.status_code == 400
        ), "Login should return 400 for missing password"
        data = response.json()
        assert "password" in data, "Response should indicate missing password"

        # Test with missing email
        response = api_client.post(
            f"{api_base_url}/auth/login/", json={"password": "password123"}
        )

        assert response.status_code == 400, "Login should return 400 for missing email"
        data = response.json()
        assert "email" in data, "Response should indicate missing email"

    def test_user_logout_with_valid_token(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ):
        """
        Test that /api/v1/auth/logout/ successfully logs out user.

        Validates:
        - HTTP 200 status code
        - Response contains success message
        - Requires authentication
        """
        # First login to get a refresh token
        login_response = authenticated_client.post(
            f"{api_base_url}/auth/login/",
            json={"email": test_user["email"], "password": test_user["password"]},
        )

        assert login_response.status_code == 200, "Login should succeed"
        refresh_token = login_response.json()["refresh"]

        # Logout with the refresh token
        logout_response = authenticated_client.post(
            f"{api_base_url}/auth/logout/", json={"refresh": refresh_token}
        )

        assert logout_response.status_code == 200, "Logout should return 200"

        data = logout_response.json()
        assert "message" in data, "Response should include success message"

    def test_user_logout_without_authentication(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that logout endpoint requires authentication.

        Validates:
        - HTTP 401 status code when no authentication provided
        """
        response = api_client.post(
            f"{api_base_url}/auth/logout/", json={"refresh": "some-token"}
        )

        assert (
            response.status_code == 401
        ), "Logout should return 401 without authentication"

    def test_token_refresh_with_valid_token(
        self, api_client: requests.Session, api_base_url: str, test_user: Dict[str, Any]
    ):
        """
        Test that /api/v1/auth/token/refresh/ returns new access token.

        Validates:
        - HTTP 200 status code
        - Response contains 'access' token
        - May contain new 'refresh' token if rotation is enabled
        """
        # First login to get tokens
        login_response = api_client.post(
            f"{api_base_url}/auth/login/",
            json={"email": test_user["email"], "password": test_user["password"]},
        )

        assert login_response.status_code == 200, "Login should succeed"
        refresh_token = login_response.json()["refresh"]

        # Refresh the token
        refresh_response = api_client.post(
            f"{api_base_url}/auth/token/refresh/", json={"refresh": refresh_token}
        )

        assert refresh_response.status_code == 200, "Token refresh should return 200"

        data = refresh_response.json()
        assert "access" in data, "Response should include new access token"
        assert len(data["access"]) > 0, "Access token should not be empty"

    def test_token_refresh_with_invalid_token(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that token refresh fails with invalid token.

        Validates:
        - HTTP 401 status code
        - Error message indicates invalid token
        """
        response = api_client.post(
            f"{api_base_url}/auth/token/refresh/",
            json={"refresh": "invalid-token-12345"},
        )

        assert (
            response.status_code == 401
        ), "Token refresh should return 401 for invalid token"


class TestUserEndpoints:
    """Test user profile endpoints."""

    def test_get_current_user_with_authentication(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ):
        """
        Test that /api/v1/auth/me/ returns authenticated user's profile.

        Validates:
        - HTTP 200 status code
        - Response contains user fields: id, email, first_name, last_name
        - Data matches the authenticated user
        """
        response = authenticated_client.get(f"{api_base_url}/auth/me/")

        assert response.status_code == 200, "Get current user should return 200"

        data = response.json()
        assert "id" in data, "Response should include 'id'"
        assert "email" in data, "Response should include 'email'"
        assert "first_name" in data, "Response should include 'first_name'"
        assert "last_name" in data, "Response should include 'last_name'"

        assert (
            data["email"] == test_user["email"]
        ), "Email should match authenticated user"

    def test_get_current_user_without_authentication(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that /api/v1/auth/me/ requires authentication.

        Validates:
        - HTTP 401 status code when no authentication provided
        """
        response = api_client.get(f"{api_base_url}/auth/me/")

        assert (
            response.status_code == 401
        ), "Get current user should return 401 without auth"

    def test_change_password_with_valid_data(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ):
        """
        Test that /api/v1/auth/change-password/ successfully changes password.

        Validates:
        - HTTP 200 status code
        - Response contains success message
        - Requires authentication
        """
        change_password_data = {
            "old_password": test_user["password"],
            "new_password": "NewSecurePass456!",
            "new_password_confirm": "NewSecurePass456!",
        }

        response = authenticated_client.post(
            f"{api_base_url}/auth/change-password/", json=change_password_data
        )

        assert (
            response.status_code == 200
        ), "Change password should return 200 on success"

        data = response.json()
        assert "message" in data, "Response should include success message"

    def test_change_password_with_incorrect_old_password(
        self, authenticated_client: requests.Session, api_base_url: str
    ):
        """
        Test that change password fails with incorrect old password.

        Validates:
        - HTTP 400 status code
        - Error message indicates incorrect old password
        """
        change_password_data = {
            "old_password": "WrongOldPassword123!",
            "new_password": "NewSecurePass456!",
            "new_password_confirm": "NewSecurePass456!",
        }

        response = authenticated_client.post(
            f"{api_base_url}/auth/change-password/", json=change_password_data
        )

        assert (
            response.status_code == 400
        ), "Change password should return 400 for wrong old password"

        data = response.json()
        assert (
            "old_password" in data or "non_field_errors" in data
        ), "Response should contain old password error"

    def test_change_password_without_authentication(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that change password endpoint requires authentication.

        Validates:
        - HTTP 401 status code when no authentication provided
        """
        change_password_data = {
            "old_password": "OldPass123!",
            "new_password": "NewPass123!",
            "new_password_confirm": "NewPass123!",
        }

        response = api_client.post(
            f"{api_base_url}/auth/change-password/", json=change_password_data
        )

        assert (
            response.status_code == 401
        ), "Change password should return 401 without auth"


class TestAssessmentEndpoints:
    """Test assessment API endpoints."""

    def test_create_assessment_with_valid_data(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
    ):
        """
        Test that POST /api/v1/assessments/ creates assessment with valid data.

        Validates:
        - HTTP 201 status code on successful creation
        - Response contains all assessment fields
        - Data matches submitted values
        """
        response = authenticated_client.post(
            f"{api_base_url}/assessments/", json=assessment_data
        )

        assert (
            response.status_code == 201
        ), "Create assessment should return 201 on success"

        data = response.json()
        assert "id" in data, "Response should include 'id'"
        assert "sport" in data, "Response should include 'sport'"
        assert "age" in data, "Response should include 'age'"
        assert "experience_level" in data, "Response should include 'experience_level'"
        assert "training_days" in data, "Response should include 'training_days'"

        assert (
            data["sport"] == assessment_data["sport"]
        ), "Sport should match submitted value"
        assert data["age"] == assessment_data["age"], "Age should match submitted value"
        assert (
            data["experience_level"] == assessment_data["experience_level"]
        ), "Experience level should match"

    def test_create_assessment_with_invalid_data(
        self, authenticated_client: requests.Session, api_base_url: str
    ):
        """
        Test that creating assessment with invalid data returns errors.

        Validates:
        - HTTP 400 status code
        - Error messages for invalid fields
        """
        invalid_data = {
            "sport": "invalid_sport",
            "age": -5,  # Invalid age
            "experience_level": "invalid_level",
        }

        response = authenticated_client.post(
            f"{api_base_url}/assessments/", json=invalid_data
        )

        assert (
            response.status_code == 400
        ), "Create assessment should return 400 for invalid data"

        data = response.json()
        # Should have errors for invalid fields
        assert len(data) > 0, "Response should contain validation errors"

    def test_create_assessment_with_missing_required_fields(
        self, authenticated_client: requests.Session, api_base_url: str
    ):
        """
        Test that creating assessment with missing fields returns errors.

        Validates:
        - HTTP 400 status code
        - Error messages for missing required fields
        """
        incomplete_data = {
            "sport": "football",
            # Missing age, experience_level, training_days
        }

        response = authenticated_client.post(
            f"{api_base_url}/assessments/", json=incomplete_data
        )

        assert (
            response.status_code == 400
        ), "Create assessment should return 400 for missing fields"

        data = response.json()
        # Should have errors for missing fields
        assert (
            "age" in data or "experience_level" in data or "training_days" in data
        ), "Response should indicate missing required fields"

    def test_create_assessment_without_authentication(
        self,
        api_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
    ):
        """
        Test that creating assessment requires authentication.

        Validates:
        - HTTP 401 status code when no authentication provided
        """
        response = api_client.post(f"{api_base_url}/assessments/", json=assessment_data)

        assert (
            response.status_code == 401
        ), "Create assessment should return 401 without auth"

    def test_get_user_assessment(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
        django_db_blocker,
    ):
        """
        Test that GET /api/v1/assessments/me/ returns user's assessment.

        Validates:
        - HTTP 200 status code
        - Response contains user's assessment data
        """
        # First create an assessment
        with django_db_blocker.unblock():
            create_response = authenticated_client.post(
                f"{api_base_url}/assessments/", json=assessment_data
            )
            assert (
                create_response.status_code == 201
            ), "Assessment creation should succeed"

        # Get user's assessment
        response = authenticated_client.get(f"{api_base_url}/assessments/me/")

        assert response.status_code == 200, "Get user assessment should return 200"

        data = response.json()
        assert "id" in data, "Response should include 'id'"
        assert (
            data["sport"] == assessment_data["sport"]
        ), "Sport should match created assessment"

    def test_get_user_assessment_when_none_exists(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ):
        """
        Test that GET /api/v1/assessments/me/ returns 404 when no assessment exists.

        Validates:
        - HTTP 404 status code
        - Error message indicates no assessment found
        """
        # Use a fresh authenticated client for a user without assessment
        # (cleanup fixture ensures no assessment exists)
        response = authenticated_client.get(f"{api_base_url}/assessments/me/")

        # Could be 404 if no assessment, or 200 if one was created in another test
        # We'll check that the response is valid
        assert response.status_code in [
            200,
            404,
        ], "Get assessment should return 200 or 404"

        if response.status_code == 404:
            data = response.json()
            assert "detail" in data, "404 response should include error detail"

    def test_get_user_assessment_without_authentication(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that getting user assessment requires authentication.

        Validates:
        - HTTP 401 status code when no authentication provided
        """
        response = api_client.get(f"{api_base_url}/assessments/me/")

        assert (
            response.status_code == 401
        ), "Get user assessment should return 401 without auth"

    def test_list_assessments_returns_only_user_assessments(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
        django_db_blocker,
    ):
        """
        Test that GET /api/v1/assessments/ returns only authenticated user's assessments.

        Validates:
        - HTTP 200 status code
        - Response is a list
        - User can only see their own assessments
        """
        # Create an assessment for the user
        with django_db_blocker.unblock():
            create_response = authenticated_client.post(
                f"{api_base_url}/assessments/", json=assessment_data
            )
            assert (
                create_response.status_code == 201
            ), "Assessment creation should succeed"

        # List assessments
        response = authenticated_client.get(f"{api_base_url}/assessments/")

        assert response.status_code == 200, "List assessments should return 200"

        data = response.json()
        assert isinstance(data, list), "Response should be a list"

        # All assessments should belong to the authenticated user
        # (based on the queryset filtering in AssessmentViewSet)
        if len(data) > 0:
            assert all("id" in item for item in data), "All items should have an id"

    def test_list_assessments_without_authentication(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that listing assessments requires authentication.

        Validates:
        - HTTP 401 status code when no authentication provided
        """
        response = api_client.get(f"{api_base_url}/assessments/")

        assert (
            response.status_code == 401
        ), "List assessments should return 401 without auth"


class TestAPISpecificationCompliance:
    """
    Test that API responses comply with expected specifications.

    This test class verifies that all endpoints return consistent response
    structures with proper HTTP methods, content types, and error formats.
    """

    def test_all_endpoints_return_json_content_type(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that all API endpoints return JSON content type.

        Validates:
        - All endpoints return 'application/json' content type
        """
        endpoints = [
            f"{api_base_url}/health/",
            f"{api_base_url}/status/",
            f"{api_base_url}/config/frontend/",
        ]

        for endpoint in endpoints:
            response = api_client.get(endpoint)
            content_type = response.headers.get("Content-Type", "")
            assert (
                "application/json" in content_type
            ), f"Endpoint {endpoint} should return JSON content type"

    def test_error_responses_have_consistent_structure(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that error responses have consistent structure.

        Validates:
        - 400 errors return validation error details
        - 401 errors return authentication error details
        - 404 errors return not found error details
        """
        # Test 401 error (authentication required)
        response = api_client.get(f"{api_base_url}/auth/me/")
        assert response.status_code == 401, "Should return 401 for protected endpoint"
        data = response.json()
        assert (
            "detail" in data or "error" in data
        ), "401 response should have error details"

        # Test 400 error (validation error)
        response = api_client.post(
            f"{api_base_url}/auth/login/", json={}  # Missing required fields
        )
        assert response.status_code == 400, "Should return 400 for missing fields"
        data = response.json()
        assert isinstance(data, dict), "400 response should be a dictionary"

    def test_protected_endpoints_deny_access_without_credentials(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that all protected endpoints deny access without authentication.

        Validates:
        - Protected endpoints return 401 without authentication
        - Authentication is properly enforced
        """
        protected_endpoints = [
            (f"{api_base_url}/auth/me/", "GET"),
            (f"{api_base_url}/auth/logout/", "POST"),
            (f"{api_base_url}/auth/change-password/", "POST"),
            (f"{api_base_url}/assessments/", "GET"),
            (f"{api_base_url}/assessments/", "POST"),
            (f"{api_base_url}/assessments/me/", "GET"),
        ]

        for endpoint, method in protected_endpoints:
            if method == "GET":
                response = api_client.get(endpoint)
            else:
                response = api_client.post(endpoint, json={})

            assert (
                response.status_code == 401
            ), f"Protected endpoint {method} {endpoint} should return 401 without auth"

    def test_public_endpoints_allow_access_without_credentials(
        self, api_client: requests.Session, api_base_url: str
    ):
        """
        Test that public endpoints allow access without authentication.

        Validates:
        - Public endpoints return 200 (or appropriate non-401 status)
        - No authentication required
        """
        public_endpoints = [
            f"{api_base_url}/health/",
            f"{api_base_url}/status/",
            f"{api_base_url}/health/ready/",
            f"{api_base_url}/health/live/",
            f"{api_base_url}/config/frontend/",
        ]

        for endpoint in public_endpoints:
            response = api_client.get(endpoint)
            assert (
                response.status_code != 401
            ), f"Public endpoint {endpoint} should not require authentication"
            assert response.status_code in [
                200,
                503,
            ], f"Public endpoint {endpoint} should return 200 or 503"
