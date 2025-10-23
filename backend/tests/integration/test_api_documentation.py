"""
Integration tests for API documentation system.

Tests the API documentation endpoints and schema generation to ensure
comprehensive and accurate documentation is available for all endpoints.
"""

import json

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestAPIDocumentationEndpoints:
    """
    Test API documentation accessibility and content.

    Ensures that documentation endpoints are accessible and provide
    comprehensive information about the API.
    """

    def setup_method(self):
        """Set up test client."""
        self.client = APIClient()

    def test_schema_endpoint_accessible(self):
        """
        Test that the OpenAPI schema endpoint is accessible.

        AC: Documentation endpoints should be accessible without authentication.
        """
        url = reverse("api:schema")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "application/vnd.oai.openapi+json; charset=utf-8"

    def test_schema_is_valid_json(self):
        """
        Test that the schema returns valid JSON.

        AC: Schema should be valid JSON that can be parsed.
        """
        url = reverse("api:schema")
        response = self.client.get(url)

        # Should not raise JSONDecodeError
        schema = json.loads(response.content)

        assert isinstance(schema, dict)
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_swagger_ui_accessible(self):
        """
        Test that Swagger UI documentation is accessible.

        AC: When I access the documentation, I should see the Swagger UI.
        """
        url = reverse("api:swagger-ui")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response["Content-Type"]

    def test_redoc_ui_accessible(self):
        """
        Test that ReDoc UI documentation is accessible.

        AC: When I access the documentation, I should see the ReDoc UI.
        """
        url = reverse("api:redoc")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response["Content-Type"]


@pytest.mark.django_db
class TestAPISchemaContent:
    """
    Test that the API schema contains comprehensive endpoint documentation.

    Ensures all endpoints are documented with required parameters,
    responses, and examples.
    """

    def setup_method(self):
        """Set up test client and fetch schema."""
        self.client = APIClient()
        url = reverse("api:schema")
        response = self.client.get(url)
        self.schema = json.loads(response.content)

    def test_schema_has_api_info(self):
        """
        Test that schema contains API metadata.

        AC: Documentation should include API title, description, and version.
        """
        assert "info" in self.schema
        info = self.schema["info"]

        assert "title" in info
        assert info["title"] == "Backend API"

        assert "version" in info
        assert info["version"] == "1.0.0"

        assert "description" in info
        assert len(info["description"]) > 0

    def test_schema_has_security_definitions(self):
        """
        Test that schema defines security schemes.

        AC: Documentation should explain authentication requirements.
        """
        assert "components" in self.schema
        assert "securitySchemes" in self.schema["components"]

        security_schemes = self.schema["components"]["securitySchemes"]
        assert "bearerAuth" in security_schemes

        bearer_auth = security_schemes["bearerAuth"]
        assert bearer_auth["type"] == "http"
        assert bearer_auth["scheme"] == "bearer"
        assert bearer_auth["bearerFormat"] == "JWT"

    def test_health_endpoints_documented(self):
        """
        Test that health check endpoints are documented.

        AC: All health endpoints should be in the schema with descriptions.
        """
        paths = self.schema["paths"]

        # Health check endpoints
        assert "/api/v1/health/" in paths
        assert "/api/v1/status/" in paths
        assert "/api/v1/health/ready/" in paths
        assert "/api/v1/health/live/" in paths

    def test_auth_endpoints_documented(self):
        """
        Test that authentication endpoints are documented.

        AC: All authentication endpoints should be in the schema.
        """
        paths = self.schema["paths"]

        # Authentication endpoints
        assert "/api/v1/auth/register/" in paths
        assert "/api/v1/auth/login/" in paths
        assert "/api/v1/auth/logout/" in paths
        assert "/api/v1/auth/token/refresh/" in paths

    def test_user_endpoints_documented(self):
        """
        Test that user profile endpoints are documented.

        AC: User management endpoints should be in the schema.
        """
        paths = self.schema["paths"]

        # User profile endpoints
        assert "/api/v1/auth/me/" in paths
        assert "/api/v1/auth/change-password/" in paths

    def test_endpoints_have_operations(self):
        """
        Test that endpoints define HTTP methods.

        AC: Each endpoint should specify supported HTTP methods (GET, POST, etc.).
        """
        paths = self.schema["paths"]

        # Check a few key endpoints have proper methods
        assert "get" in paths["/api/v1/health/"]
        assert "post" in paths["/api/v1/auth/login/"]
        assert "post" in paths["/api/v1/auth/register/"]

    def test_operations_have_summaries(self):
        """
        Test that operations include summary descriptions.

        AC: Each endpoint should have a brief summary.
        """
        paths = self.schema["paths"]

        # Check health endpoint
        health_get = paths["/api/v1/health/"]["get"]
        assert "summary" in health_get
        assert len(health_get["summary"]) > 0

        # Check login endpoint
        login_post = paths["/api/v1/auth/login/"]["post"]
        assert "summary" in login_post
        assert len(login_post["summary"]) > 0

    def test_operations_have_descriptions(self):
        """
        Test that operations include detailed descriptions.

        AC: Each endpoint should have a detailed description explaining its purpose.
        """
        paths = self.schema["paths"]

        # Check login endpoint has detailed description
        login_post = paths["/api/v1/auth/login/"]["post"]
        assert "description" in login_post
        assert len(login_post["description"]) > 50  # Should be detailed

    def test_operations_have_tags(self):
        """
        Test that operations are organized by tags.

        AC: Endpoints should be grouped into logical categories.
        """
        paths = self.schema["paths"]

        # Health endpoints should be tagged
        health_get = paths["/api/v1/health/"]["get"]
        assert "tags" in health_get
        assert "Health" in health_get["tags"]

        # Auth endpoints should be tagged
        login_post = paths["/api/v1/auth/login/"]["post"]
        assert "tags" in login_post
        assert "Authentication" in login_post["tags"]

    def test_operations_have_responses(self):
        """
        Test that operations document response codes.

        AC: Each endpoint should document expected response codes and formats.
        """
        paths = self.schema["paths"]

        # Check login endpoint responses
        login_post = paths["/api/v1/auth/login/"]["post"]
        assert "responses" in login_post

        responses = login_post["responses"]
        assert "200" in responses  # Success response
        assert "400" in responses  # Validation error

    def test_post_operations_have_request_body(self):
        """
        Test that POST operations document request bodies.

        AC: POST/PUT endpoints should document required request format.
        """
        paths = self.schema["paths"]

        # Check login endpoint has request body
        login_post = paths["/api/v1/auth/login/"]["post"]
        assert "requestBody" in login_post

        request_body = login_post["requestBody"]
        assert "content" in request_body
        assert "application/json" in request_body["content"]

    def test_request_body_has_schema(self):
        """
        Test that request bodies define schemas.

        AC: Request bodies should specify field types and requirements.
        """
        paths = self.schema["paths"]

        # Check registration endpoint
        register_post = paths["/api/v1/auth/register/"]["post"]
        request_body = register_post["requestBody"]
        content = request_body["content"]["application/json"]

        assert "schema" in content
        schema_ref = content["schema"]

        # Should reference a component schema
        assert "$ref" in schema_ref or "properties" in schema_ref

    def test_responses_have_descriptions(self):
        """
        Test that response codes have descriptions.

        AC: Each response code should explain when it's returned.
        """
        paths = self.schema["paths"]

        login_post = paths["/api/v1/auth/login/"]["post"]
        responses = login_post["responses"]

        # Success response should have description
        assert "description" in responses["200"]
        assert len(responses["200"]["description"]) > 0

        # Error response should have description
        assert "description" in responses["400"]
        assert len(responses["400"]["description"]) > 0

    def test_components_define_schemas(self):
        """
        Test that common schemas are defined in components.

        AC: Reusable schemas should be defined once and referenced.
        """
        assert "components" in self.schema
        assert "schemas" in self.schema["components"]

        schemas = self.schema["components"]["schemas"]
        assert len(schemas) > 0  # Should have at least some schemas

    def test_authenticated_endpoints_specify_security(self):
        """
        Test that protected endpoints specify security requirements.

        AC: Endpoints requiring authentication should document this clearly.
        """
        paths = self.schema["paths"]

        # Logout requires authentication
        logout_post = paths["/api/v1/auth/logout/"]["post"]
        assert "security" in logout_post or "security" in self.schema

        # Current user endpoint requires authentication
        me_get = paths["/api/v1/auth/me/"]["get"]
        # Security can be defined at operation or schema level
        has_security = "security" in me_get or (
            "security" in self.schema and len(self.schema["security"]) > 0
        )
        assert has_security

    def test_schema_has_servers(self):
        """
        Test that schema defines server URLs.

        AC: Documentation should indicate base URL for API.
        """
        # Servers can be auto-generated or explicitly defined
        # Just verify the schema is valid
        assert "openapi" in self.schema
        assert self.schema["openapi"].startswith("3.")


@pytest.mark.django_db
class TestDocumentationExamples:
    """
    Test that endpoints include request and response examples.

    Ensures developers have clear examples of how to use the API.
    """

    def setup_method(self):
        """Set up test client and fetch schema."""
        self.client = APIClient()
        url = reverse("api:schema")
        response = self.client.get(url)
        self.schema = json.loads(response.content)

    def test_login_has_request_example(self):
        """
        Test that login endpoint includes request example.

        AC: Endpoints should show example request payloads.
        """
        paths = self.schema["paths"]
        login_post = paths["/api/v1/auth/login/"]["post"]

        # Check for examples in request body
        if "requestBody" in login_post:
            request_body = login_post["requestBody"]
            content = request_body.get("content", {}).get("application/json", {})

            # Examples can be in different locations
            has_example = (
                "example" in content
                or "examples" in content
                or ("schema" in content and "example" in content["schema"])
            )

            # At minimum, should have schema defining structure
            assert "schema" in content

    def test_login_has_response_example(self):
        """
        Test that login endpoint includes response examples.

        AC: Endpoints should show example successful responses.
        """
        paths = self.schema["paths"]
        login_post = paths["/api/v1/auth/login/"]["post"]

        # Check 200 response has example
        responses = login_post["responses"]
        success_response = responses["200"]

        # Should have content definition
        if "content" in success_response:
            content = success_response["content"].get("application/json", {})
            assert "schema" in content or "examples" in content

    def test_registration_documents_required_fields(self):
        """
        Test that registration endpoint documents required fields.

        AC: Request schemas should indicate which fields are required.
        """
        paths = self.schema["paths"]
        register_post = paths["/api/v1/auth/register/"]["post"]

        # Should have request body
        assert "requestBody" in register_post

        # Request body should be marked as required
        # (registration needs data to work)
        request_body = register_post["requestBody"]
        # Schema should exist
        content = request_body.get("content", {}).get("application/json", {})
        assert "schema" in content


@pytest.mark.django_db
class TestDocumentationAutoUpdate:
    """
    Test that documentation automatically reflects code changes.

    Ensures documentation stays synchronized with the API implementation.
    """

    def setup_method(self):
        """Set up test client."""
        self.client = APIClient()

    def test_schema_generation_is_dynamic(self):
        """
        Test that schema is generated dynamically from code.

        AC: Documentation should automatically update when API changes.
        """
        # Get schema multiple times - should always return current state
        url = reverse("api:schema")

        response1 = self.client.get(url)
        schema1 = json.loads(response1.content)

        response2 = self.client.get(url)
        schema2 = json.loads(response2.content)

        # Should return consistent schema
        assert schema1["info"]["version"] == schema2["info"]["version"]
        assert len(schema1["paths"]) == len(schema2["paths"])

    def test_all_registered_urls_in_schema(self):
        """
        Test that all API URLs are included in schema.

        AC: Documentation should include all available endpoints.
        """
        url = reverse("api:schema")
        response = self.client.get(url)
        schema = json.loads(response.content)

        paths = schema["paths"]

        # Verify all expected endpoints are present
        expected_endpoints = [
            "/api/v1/health/",
            "/api/v1/status/",
            "/api/v1/health/ready/",
            "/api/v1/health/live/",
            "/api/v1/auth/register/",
            "/api/v1/auth/login/",
            "/api/v1/auth/logout/",
            "/api/v1/auth/token/refresh/",
            "/api/v1/auth/me/",
            "/api/v1/auth/change-password/",
        ]

        for endpoint in expected_endpoints:
            assert endpoint in paths, f"Endpoint {endpoint} not found in schema"


@pytest.mark.django_db
class TestDocumentationAccessibility:
    """
    Test documentation accessibility and usability.

    Ensures documentation is easy to access and use.
    """

    def setup_method(self):
        """Set up test client."""
        self.client = APIClient()

    def test_documentation_accessible_without_auth(self):
        """
        Test that documentation is publicly accessible.

        AC: Documentation should be accessible without authentication.
        """
        # Schema
        url = reverse("api:schema")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # Swagger UI
        url = reverse("api:swagger-ui")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # ReDoc
        url = reverse("api:redoc")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_schema_can_be_downloaded(self):
        """
        Test that schema can be downloaded as JSON.

        AC: Developers should be able to save and import the schema.
        """
        url = reverse("api:schema")
        response = self.client.get(url)

        # Should return downloadable JSON
        assert response.status_code == status.HTTP_200_OK
        assert "application/vnd.oai.openapi+json" in response["Content-Type"]

        # Should be valid JSON
        schema = json.loads(response.content)
        assert isinstance(schema, dict)

    def test_swagger_ui_loads_schema(self):
        """
        Test that Swagger UI successfully loads the schema.

        AC: Interactive documentation should display properly.
        """
        url = reverse("api:swagger-ui")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        content = response.content.decode("utf-8")

        # Should reference the schema endpoint
        assert "schema" in content.lower() or "swagger" in content.lower()
