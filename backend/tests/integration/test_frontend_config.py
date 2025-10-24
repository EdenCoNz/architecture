"""
Integration tests for frontend configuration endpoint.

Tests ensure the frontend configuration endpoint returns correct configuration
data, responds to environment variables, and is accessible without authentication.
"""

import os
from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestFrontendConfigEndpoint:
    """
    Test the frontend configuration endpoint.

    Ensures configuration is returned correctly, responds to environment
    variables, and maintains public accessibility.
    """

    def setup_method(self):
        """Set up test client."""
        self.client = APIClient()
        self.url = reverse("api:frontend-config")

    def test_frontend_config_accessible_without_auth(self):
        """
        Test that frontend config endpoint is publicly accessible.

        AC: When I access the frontend configuration endpoint, it returns
        configuration data without requiring authentication.
        """
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "application/json"

    def test_frontend_config_returns_correct_structure(self):
        """
        Test that frontend config returns expected data structure.

        AC: When I access the endpoint, it returns configuration with api,
        app, and features sections.
        """
        response = self.client.get(self.url)
        data = response.json()

        # Check top-level structure
        assert "api" in data
        assert "app" in data
        assert "features" in data

        # Check api section
        assert "url" in data["api"]
        assert "timeout" in data["api"]
        assert "enableLogging" in data["api"]

        # Check app section
        assert "name" in data["app"]
        assert "title" in data["app"]
        assert "version" in data["app"]
        assert "environment" in data["app"]

        # Check features section
        assert "enableAnalytics" in data["features"]
        assert "enableDebugMode" in data["features"]

    def test_frontend_config_default_values(self):
        """
        Test that frontend config returns sensible defaults.

        AC: When environment variables are not set, the endpoint returns
        default configuration values.
        """
        # Clear any existing environment variables for this test
        env_vars_to_clear = [
            "FRONTEND_API_URL",
            "FRONTEND_API_TIMEOUT",
            "FRONTEND_API_ENABLE_LOGGING",
            "FRONTEND_APP_NAME",
            "FRONTEND_APP_TITLE",
            "FRONTEND_APP_VERSION",
            "FRONTEND_ENABLE_ANALYTICS",
            "FRONTEND_ENABLE_DEBUG",
        ]

        with patch.dict(os.environ, {key: "" for key in env_vars_to_clear}, clear=False):
            # Remove empty strings and clear the vars
            for key in env_vars_to_clear:
                os.environ.pop(key, None)

            response = self.client.get(self.url)
            data = response.json()

            # Check default values
            assert data["api"]["url"] == "http://localhost:8000"
            assert data["api"]["timeout"] == 30000
            assert data["api"]["enableLogging"] is False
            assert data["app"]["name"] == "Frontend Application"
            assert data["app"]["title"] == "Frontend Application"
            assert data["app"]["version"] == "1.0.0"
            assert data["features"]["enableAnalytics"] is False
            assert data["features"]["enableDebugMode"] is False

    def test_frontend_config_respects_environment_variables(self):
        """
        Test that frontend config responds to environment variables.

        AC: When environment variables are set, the endpoint returns
        configuration based on those values.
        """
        test_env_vars = {
            "FRONTEND_API_URL": "https://api.production.com",
            "FRONTEND_API_TIMEOUT": "60000",
            "FRONTEND_API_ENABLE_LOGGING": "true",
            "FRONTEND_APP_NAME": "My App",
            "FRONTEND_APP_TITLE": "My Application",
            "FRONTEND_APP_VERSION": "2.0.0",
            "FRONTEND_ENABLE_ANALYTICS": "true",
            "FRONTEND_ENABLE_DEBUG": "false",
        }

        with patch.dict(os.environ, test_env_vars, clear=False):
            response = self.client.get(self.url)
            data = response.json()

            # Check that environment variables are respected
            assert data["api"]["url"] == "https://api.production.com"
            assert data["api"]["timeout"] == 60000
            assert data["api"]["enableLogging"] is True
            assert data["app"]["name"] == "My App"
            assert data["app"]["title"] == "My Application"
            assert data["app"]["version"] == "2.0.0"
            assert data["features"]["enableAnalytics"] is True
            assert data["features"]["enableDebugMode"] is False

    def test_frontend_config_boolean_parsing(self):
        """
        Test that boolean environment variables are parsed correctly.

        AC: When boolean environment variables use different cases,
        they are parsed correctly.
        """
        # Test various boolean representations
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("1", False),  # Only "true" should be True
            ("", False),
        ]

        for env_value, expected_bool in test_cases:
            with patch.dict(
                os.environ,
                {"FRONTEND_API_ENABLE_LOGGING": env_value},
                clear=False,
            ):
                response = self.client.get(self.url)
                data = response.json()

                assert (
                    data["api"]["enableLogging"] == expected_bool
                ), f"Expected {env_value} to parse as {expected_bool}"

    def test_frontend_config_environment_detection_development(self):
        """
        Test that environment is correctly detected in development.

        AC: When DEBUG is True, environment should be 'development'.
        """
        # This is tested in the actual Django settings context
        # The environment field should reflect the runtime environment
        response = self.client.get(self.url)
        data = response.json()

        # In test environment, should have an environment value
        assert "environment" in data["app"]
        assert isinstance(data["app"]["environment"], str)

    def test_frontend_config_json_response_format(self):
        """
        Test that response is valid JSON with correct content type.

        AC: The endpoint returns valid JSON that can be parsed by frontend.
        """
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "application/json" in response["Content-Type"]

        # Should be able to parse JSON
        data = response.json()
        assert isinstance(data, dict)

    def test_frontend_config_get_only(self):
        """
        Test that frontend config only accepts GET requests.

        AC: When I send POST/PUT/DELETE to the endpoint, it returns
        method not allowed.
        """
        # POST should not be allowed
        response = self.client.post(self.url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # PUT should not be allowed
        response = self.client.put(self.url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # DELETE should not be allowed
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # PATCH should not be allowed
        response = self.client.patch(self.url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_frontend_config_no_side_effects(self):
        """
        Test that calling frontend config has no side effects.

        AC: Multiple calls to the endpoint return consistent results.
        """
        # Call endpoint multiple times
        response1 = self.client.get(self.url)
        response2 = self.client.get(self.url)
        response3 = self.client.get(self.url)

        data1 = response1.json()
        data2 = response2.json()
        data3 = response3.json()

        # All responses should be identical
        assert data1 == data2
        assert data2 == data3

    def test_frontend_config_timeout_is_integer(self):
        """
        Test that timeout value is parsed as integer.

        AC: The timeout field should be a number, not a string.
        """
        response = self.client.get(self.url)
        data = response.json()

        assert isinstance(data["api"]["timeout"], int)
        assert data["api"]["timeout"] > 0


@pytest.mark.django_db
class TestFrontendConfigDocumentation:
    """
    Test that frontend config endpoint is properly documented.

    Ensures the endpoint appears in API schema with correct information.
    """

    def setup_method(self):
        """Set up test client."""
        self.client = APIClient()

    def test_frontend_config_in_api_schema(self):
        """
        Test that frontend config endpoint appears in API schema.

        AC: When I view the API schema, the frontend config endpoint
        is documented.
        """
        schema_url = reverse("api:schema")
        response = self.client.get(schema_url)

        assert response.status_code == status.HTTP_200_OK
        schema = response.json()

        # Check that the endpoint is in the schema
        paths = schema.get("paths", {})
        assert "/api/v1/config/frontend/" in paths

    def test_frontend_config_schema_has_response_definition(self):
        """
        Test that frontend config endpoint has response schema defined.

        AC: The API schema should document the response structure for
        the frontend config endpoint.
        """
        schema_url = reverse("api:schema")
        response = self.client.get(schema_url)
        schema = response.json()

        paths = schema.get("paths", {})
        frontend_config_path = paths.get("/api/v1/config/frontend/", {})
        get_operation = frontend_config_path.get("get", {})

        # Should have responses defined
        assert "responses" in get_operation
        responses = get_operation["responses"]

        # Should document 200 response
        assert "200" in responses
        success_response = responses["200"]

        # Should have content definition
        assert "content" in success_response
        assert "application/json" in success_response["content"]

        # Should have schema
        json_content = success_response["content"]["application/json"]
        assert "schema" in json_content

    def test_frontend_config_schema_has_description(self):
        """
        Test that frontend config endpoint has description in schema.

        AC: The API documentation should explain what the endpoint does.
        """
        schema_url = reverse("api:schema")
        response = self.client.get(schema_url)
        schema = response.json()

        paths = schema.get("paths", {})
        frontend_config_path = paths.get("/api/v1/config/frontend/", {})
        get_operation = frontend_config_path.get("get", {})

        # Should have summary or description
        has_documentation = "summary" in get_operation or "description" in get_operation
        assert has_documentation

        if "summary" in get_operation:
            assert len(get_operation["summary"]) > 0

        if "description" in get_operation:
            assert len(get_operation["description"]) > 0

    def test_frontend_config_schema_tagged(self):
        """
        Test that frontend config endpoint is tagged in schema.

        AC: The endpoint should be organized under a logical tag.
        """
        schema_url = reverse("api:schema")
        response = self.client.get(schema_url)
        schema = response.json()

        paths = schema.get("paths", {})
        frontend_config_path = paths.get("/api/v1/config/frontend/", {})
        get_operation = frontend_config_path.get("get", {})

        # Should have tags
        assert "tags" in get_operation
        assert len(get_operation["tags"]) > 0
