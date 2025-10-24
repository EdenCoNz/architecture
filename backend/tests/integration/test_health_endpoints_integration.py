"""
Integration tests for health check endpoints.

These tests verify the health check endpoints work correctly with real
dependencies and validate the complete acceptance criteria.
"""

from unittest.mock import patch

import pytest
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.integration
class TestHealthEndpointIntegration:
    """Integration tests for health check endpoint."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_health_endpoint_with_healthy_database(self, client, db):
        """
        Verify health endpoint returns operational status with healthy database.

        Acceptance Criteria: When I send a request to the health endpoint,
        I should receive a response indicating the server is operational.
        """
        response = client.get("/api/v1/health/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "healthy"
        assert "timestamp" in response.data
        assert "database" in response.data
        assert response.data["database"]["status"] == "connected"

    def test_health_endpoint_machine_readable_format(self, client, db):
        """
        Verify health endpoint returns machine-readable JSON.

        Acceptance Criteria: When monitoring systems query the health endpoint,
        they should receive a machine-readable response.
        """
        response = client.get("/api/v1/health/")

        # Verify JSON content type
        assert response["Content-Type"] == "application/json"

        # Verify consistent structure
        required_fields = ["status", "timestamp", "database"]
        for field in required_fields:
            assert field in response.data, f"Missing required field: {field}"

        # Verify status is one of expected values
        assert response.data["status"] in ["healthy", "degraded", "unhealthy"]

    def test_health_endpoint_with_database_failure(self, client):
        """
        Verify health endpoint reports degraded status when database fails.

        Acceptance Criteria: When the data store is unavailable,
        I should see the health endpoint report degraded status.
        """
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "unhealthy",
                "database": "disconnected",
                "error": "Could not connect to database server at localhost:5432",
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/health/")

            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert response.data["status"] == "unhealthy"
            assert response.data["database"]["status"] == "disconnected"
            assert "error" in response.data["database"]

    def test_health_endpoint_response_time_measurement(self, client, db):
        """Verify health endpoint includes database response time."""
        response = client.get("/api/v1/health/")

        assert "database" in response.data
        assert "response_time_ms" in response.data["database"]
        assert isinstance(response.data["database"]["response_time_ms"], (int, float))
        assert response.data["database"]["response_time_ms"] >= 0


@pytest.mark.integration
class TestStatusEndpointIntegration:
    """Integration tests for status endpoint."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_status_endpoint_complete_information(self, client, db):
        """
        Verify status endpoint returns complete system information.

        Acceptance Criteria: When I query the status endpoint,
        I should see version information and uptime statistics.
        """
        response = client.get("/api/v1/status/")

        assert response.status_code == status.HTTP_200_OK

        # Verify version information
        assert "version" in response.data
        assert "api_version" in response.data

        # Verify uptime statistics
        assert "uptime_seconds" in response.data
        assert isinstance(response.data["uptime_seconds"], (int, float))
        assert response.data["uptime_seconds"] >= 0

        # Verify memory usage
        assert "memory" in response.data
        assert "used_mb" in response.data["memory"]
        assert "percent" in response.data["memory"]

        # Verify database information
        assert "database" in response.data
        assert "status" in response.data["database"]

        # Verify environment
        assert "environment" in response.data

        # Verify timestamp
        assert "timestamp" in response.data

    def test_status_endpoint_with_database_failure(self, client):
        """Verify status endpoint handles database failure gracefully."""
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "unhealthy",
                "database": "disconnected",
                "error": "Could not connect to database server",
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/status/")

            # Status endpoint should still respond with 200
            assert response.status_code == status.HTTP_200_OK

            # But show unhealthy status
            assert response.data["status"] == "unhealthy"
            assert response.data["database"]["status"] == "disconnected"

            # Other information should still be present
            assert "version" in response.data
            assert "uptime_seconds" in response.data
            assert "memory" in response.data


@pytest.mark.integration
class TestReadinessAndLivenessIntegration:
    """Integration tests for Kubernetes readiness and liveness probes."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_readiness_probe_with_healthy_dependencies(self, client, db):
        """Verify readiness probe returns 200 when all dependencies are healthy."""
        response = client.get("/api/v1/health/ready/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["ready"] is True

    def test_readiness_probe_with_unhealthy_dependencies(self, client):
        """Verify readiness probe returns 503 when dependencies are unhealthy."""
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "unhealthy",
                "database": "disconnected",
                "error": "Could not connect to database server",
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/health/ready/")

            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert response.data["ready"] is False

    def test_liveness_probe_always_responds(self, client):
        """Verify liveness probe always returns 200 when server is running."""
        response = client.get("/api/v1/health/live/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["alive"] is True


@pytest.mark.integration
class TestHealthEndpointAccessibility:
    """Integration tests for health endpoint accessibility."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_health_endpoints_no_authentication_required(self, client, db):
        """Verify health endpoints are accessible without authentication."""
        # Health endpoint
        response = client.get("/api/v1/health/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]

        # Status endpoint
        response = client.get("/api/v1/status/")
        assert response.status_code == status.HTTP_200_OK

        # Readiness endpoint
        response = client.get("/api/v1/health/ready/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]

        # Liveness endpoint
        response = client.get("/api/v1/health/live/")
        assert response.status_code == status.HTTP_200_OK

    def test_health_endpoints_no_credentials_exposed(self, client, db):
        """Verify health endpoints never expose database credentials."""
        endpoints = [
            "/api/v1/health/",
            "/api/v1/status/",
            "/api/v1/health/ready/",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)

            # Convert response to string and check for password
            response_str = str(response.data).lower()
            assert "password" not in response_str
            assert "secret" not in response_str

            # Verify connection_info doesn't include PASSWORD key
            if "database" in response.data:
                db_info = response.data["database"]
                if isinstance(db_info, dict):
                    assert "password" not in str(db_info).lower()
                    assert "PASSWORD" not in str(db_info)


@pytest.mark.integration
class TestHealthEndpointPerformance:
    """Integration tests for health endpoint performance."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_health_endpoint_responds_quickly(self, client, db):
        """Verify health endpoint responds within acceptable time."""
        import time

        start = time.time()
        response = client.get("/api/v1/health/")
        duration = (time.time() - start) * 1000  # Convert to ms

        assert response.status_code == status.HTTP_200_OK
        # Health check should respond in less than 1 second
        assert duration < 1000, f"Health check took {duration}ms, expected < 1000ms"

    def test_liveness_endpoint_responds_immediately(self, client):
        """Verify liveness endpoint responds very quickly (no DB checks)."""
        import time

        start = time.time()
        response = client.get("/api/v1/health/live/")
        duration = (time.time() - start) * 1000  # Convert to ms

        assert response.status_code == status.HTTP_200_OK
        # Liveness should respond in less than 100ms (no database checks)
        assert duration < 100, f"Liveness check took {duration}ms, expected < 100ms"


@pytest.mark.integration
class TestHealthEndpointProductionMode:
    """Integration tests for health endpoint in production mode (Story #188)."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    @override_settings(
        SECURE_SSL_REDIRECT=True,
        SECURE_REDIRECT_EXEMPT=[
            r"^api/v1/health/$",
            r"^api/v1/health/ready/$",
            r"^api/v1/health/live/$",
        ],
    )
    def test_health_endpoint_no_redirect_with_ssl_redirect_enabled(self, client, db):
        """
        Verify health endpoint returns HTTP 200 directly without redirects.

        Story #188 - Acceptance Criteria:
        - Given the backend container is running, when I send a GET request to
          the health endpoint, then I receive HTTP 200 status code
        - Given the health endpoint is called, when checking the response headers,
          then there are no redirect location headers present
        """
        response = client.get("/api/v1/health/")

        # Should return 200 OK, not 301 or 302 redirect
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "healthy"

        # Verify no redirect headers present
        assert "Location" not in response
        assert response.status_code not in [301, 302, 303, 307, 308]

    @override_settings(
        SECURE_SSL_REDIRECT=True,
        SECURE_REDIRECT_EXEMPT=[
            r"^api/v1/health/$",
            r"^api/v1/health/ready/$",
            r"^api/v1/health/live/$",
        ],
    )
    def test_health_endpoint_response_time_under_100ms(self, client, db):
        """
        Verify health endpoint responds within 100ms.

        Story #188 - Acceptance Criteria:
        - Given I access the health endpoint, when the response is received,
          then the response time is under 100ms
        """
        import time

        start = time.time()
        response = client.get("/api/v1/health/")
        duration = (time.time() - start) * 1000  # Convert to ms

        assert response.status_code == status.HTTP_200_OK
        assert duration < 100, f"Health check took {duration}ms, expected < 100ms"

    @override_settings(
        SECURE_SSL_REDIRECT=True,
        SECURE_REDIRECT_EXEMPT=[
            r"^api/v1/health/$",
            r"^api/v1/health/ready/$",
            r"^api/v1/health/live/$",
        ],
    )
    def test_health_endpoint_consecutive_requests_all_return_200(self, client, db):
        """
        Verify 20 consecutive health endpoint requests all return HTTP 200.

        Story #188 - Acceptance Criteria:
        - Given the CI/CD pipeline tests the health endpoint, when making 20
          consecutive requests, then all 20 requests return HTTP 200 status code
        """
        for i in range(20):
            response = client.get("/api/v1/health/")
            assert (
                response.status_code == status.HTTP_200_OK
            ), f"Request {i+1}/20 failed with status {response.status_code}"
            assert response.data["status"] == "healthy"

    @override_settings(
        SECURE_SSL_REDIRECT=True,
        SECURE_REDIRECT_EXEMPT=[
            r"^api/v1/health/$",
            r"^api/v1/health/ready/$",
            r"^api/v1/health/live/$",
        ],
    )
    def test_readiness_probe_no_redirect_in_production(self, client, db):
        """Verify readiness probe endpoint is also exempt from SSL redirect."""
        response = client.get("/api/v1/health/ready/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["ready"] is True
        assert "Location" not in response

    @override_settings(
        SECURE_SSL_REDIRECT=True,
        SECURE_REDIRECT_EXEMPT=[
            r"^api/v1/health/$",
            r"^api/v1/health/ready/$",
            r"^api/v1/health/live/$",
        ],
    )
    def test_liveness_probe_no_redirect_in_production(self, client):
        """Verify liveness probe endpoint is also exempt from SSL redirect."""
        response = client.get("/api/v1/health/live/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["alive"] is True
        assert "Location" not in response
