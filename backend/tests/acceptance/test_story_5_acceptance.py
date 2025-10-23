"""
Acceptance tests for Story #5: Implement Health Check and Status Endpoints.

These tests validate that all acceptance criteria from the user story are met:

1. When I send a request to the health endpoint, I should receive a response
   indicating the server is operational
2. When the data store is unavailable, I should see the health endpoint
   report degraded status
3. When I query the status endpoint, I should see version information and
   uptime statistics
4. When monitoring systems query the health endpoint, they should receive
   a machine-readable response
"""

from datetime import datetime
from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.acceptance
class TestAcceptanceCriteria1:
    """
    Acceptance Criteria 1: When I send a request to the health endpoint,
    I should receive a response indicating the server is operational.
    """

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_health_endpoint_indicates_server_operational(self, client, db):
        """
        GIVEN a healthy API server with working database
        WHEN I send a GET request to /api/v1/health/
        THEN I should receive a response indicating the server is operational
        """
        response = client.get("/api/v1/health/")

        # Verify response indicates server is operational
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "healthy"
        assert "timestamp" in response.data
        assert "database" in response.data

    def test_health_endpoint_shows_database_connected(self, client, db):
        """
        GIVEN a healthy API server with working database
        WHEN I send a GET request to /api/v1/health/
        THEN the response should show database is connected
        """
        response = client.get("/api/v1/health/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["database"]["status"] == "connected"
        assert "response_time_ms" in response.data["database"]

    def test_health_endpoint_accessible(self, client, db):
        """
        GIVEN a running API server
        WHEN I send a GET request to /api/v1/health/
        THEN the endpoint should be accessible and respond
        """
        response = client.get("/api/v1/health/")

        # Endpoint must be accessible
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]


@pytest.mark.acceptance
class TestAcceptanceCriteria2:
    """
    Acceptance Criteria 2: When the data store is unavailable, I should see
    the health endpoint report degraded status.
    """

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_health_endpoint_reports_degraded_when_database_down(self, client):
        """
        GIVEN an API server with unavailable database
        WHEN I send a GET request to /api/v1/health/
        THEN I should see the health endpoint report unhealthy/degraded status
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

            # Verify degraded status is reported
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert response.data["status"] == "unhealthy"

    def test_health_endpoint_shows_database_disconnected(self, client):
        """
        GIVEN an API server with unavailable database
        WHEN I send a GET request to /api/v1/health/
        THEN the response should show database is disconnected
        """
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "unhealthy",
                "database": "disconnected",
                "error": "Connection refused",
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/health/")

            assert response.data["database"]["status"] == "disconnected"
            assert "error" in response.data["database"]

    def test_health_endpoint_still_responds_when_database_down(self, client):
        """
        GIVEN an API server with unavailable database
        WHEN I send a GET request to /api/v1/health/
        THEN the endpoint should still respond (not time out or crash)
        """
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "unhealthy",
                "database": "disconnected",
                "error": "Connection refused",
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/health/")

            # Endpoint must respond even when database is down
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert "status" in response.data


@pytest.mark.acceptance
class TestAcceptanceCriteria3:
    """
    Acceptance Criteria 3: When I query the status endpoint, I should see
    version information and uptime statistics.
    """

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_status_endpoint_includes_version_information(self, client, db):
        """
        GIVEN a running API server
        WHEN I send a GET request to /api/v1/status/
        THEN I should see version information in the response
        """
        response = client.get("/api/v1/status/")

        assert response.status_code == status.HTTP_200_OK

        # Verify version information is present
        assert "version" in response.data
        assert isinstance(response.data["version"], str)
        assert len(response.data["version"]) > 0

        assert "api_version" in response.data
        assert isinstance(response.data["api_version"], str)

    def test_status_endpoint_includes_uptime_statistics(self, client, db):
        """
        GIVEN a running API server
        WHEN I send a GET request to /api/v1/status/
        THEN I should see uptime statistics in the response
        """
        response = client.get("/api/v1/status/")

        assert response.status_code == status.HTTP_200_OK

        # Verify uptime statistics are present
        assert "uptime_seconds" in response.data
        assert isinstance(response.data["uptime_seconds"], (int, float))
        assert response.data["uptime_seconds"] >= 0

    def test_status_endpoint_includes_memory_usage(self, client, db):
        """
        GIVEN a running API server
        WHEN I send a GET request to /api/v1/status/
        THEN I should see memory usage information
        """
        response = client.get("/api/v1/status/")

        assert response.status_code == status.HTTP_200_OK

        # Verify memory usage is present
        assert "memory" in response.data
        assert "used_mb" in response.data["memory"]
        assert "percent" in response.data["memory"]
        assert isinstance(response.data["memory"]["used_mb"], (int, float))
        assert isinstance(response.data["memory"]["percent"], (int, float))

    def test_status_endpoint_includes_database_connectivity(self, client, db):
        """
        GIVEN a running API server
        WHEN I send a GET request to /api/v1/status/
        THEN I should see database connectivity information
        """
        response = client.get("/api/v1/status/")

        assert response.status_code == status.HTTP_200_OK

        # Verify database information is present
        assert "database" in response.data
        assert "status" in response.data["database"]
        assert response.data["database"]["status"] in ["connected", "disconnected"]

    def test_status_endpoint_accessible(self, client, db):
        """
        GIVEN a running API server
        WHEN I send a GET request to /api/v1/status/
        THEN the endpoint should be accessible
        """
        response = client.get("/api/v1/status/")

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.acceptance
class TestAcceptanceCriteria4:
    """
    Acceptance Criteria 4: When monitoring systems query the health endpoint,
    they should receive a machine-readable response.
    """

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_health_endpoint_returns_json(self, client, db):
        """
        GIVEN a monitoring system
        WHEN it queries /api/v1/health/
        THEN it should receive a JSON response
        """
        response = client.get("/api/v1/health/")

        # Verify JSON content type
        assert response["Content-Type"] == "application/json"

    def test_health_endpoint_has_consistent_structure(self, client, db):
        """
        GIVEN a monitoring system
        WHEN it queries /api/v1/health/
        THEN the response should have a consistent, predictable structure
        """
        response = client.get("/api/v1/health/")

        # Verify consistent structure
        required_fields = ["status", "timestamp", "database"]
        for field in required_fields:
            assert field in response.data, f"Missing required field: {field}"

    def test_health_endpoint_status_values_are_standardized(self, client, db):
        """
        GIVEN a monitoring system
        WHEN it queries /api/v1/health/
        THEN the status values should be standardized and predictable
        """
        response = client.get("/api/v1/health/")

        # Verify status is one of expected values
        assert response.data["status"] in ["healthy", "degraded", "unhealthy"]

    def test_health_endpoint_timestamp_is_iso8601(self, client, db):
        """
        GIVEN a monitoring system
        WHEN it queries /api/v1/health/
        THEN the timestamp should be in ISO 8601 format
        """
        response = client.get("/api/v1/health/")

        # Verify timestamp is ISO 8601 format
        timestamp = response.data["timestamp"]
        assert isinstance(timestamp, str)

        # Should be parseable as ISO 8601
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    def test_status_endpoint_returns_json(self, client, db):
        """
        GIVEN a monitoring system
        WHEN it queries /api/v1/status/
        THEN it should receive a JSON response
        """
        response = client.get("/api/v1/status/")

        # Verify JSON content type
        assert response["Content-Type"] == "application/json"

    def test_status_endpoint_has_consistent_structure(self, client, db):
        """
        GIVEN a monitoring system
        WHEN it queries /api/v1/status/
        THEN the response should have a consistent, predictable structure
        """
        response = client.get("/api/v1/status/")

        # Verify consistent structure
        required_fields = [
            "status",
            "timestamp",
            "version",
            "api_version",
            "environment",
            "uptime_seconds",
            "memory",
            "database",
        ]
        for field in required_fields:
            assert field in response.data, f"Missing required field: {field}"

    def test_readiness_endpoint_returns_json(self, client, db):
        """
        GIVEN a monitoring system (Kubernetes)
        WHEN it queries /api/v1/health/ready/
        THEN it should receive a JSON response
        """
        response = client.get("/api/v1/health/ready/")

        assert response["Content-Type"] == "application/json"

    def test_liveness_endpoint_returns_json(self, client, db):
        """
        GIVEN a monitoring system (Kubernetes)
        WHEN it queries /api/v1/health/live/
        THEN it should receive a JSON response
        """
        response = client.get("/api/v1/health/live/")

        assert response["Content-Type"] == "application/json"

    def test_health_endpoints_use_standard_http_status_codes(self, client, db):
        """
        GIVEN a monitoring system
        WHEN it queries health endpoints
        THEN the responses should use standard HTTP status codes
        """
        # Healthy response should be 200
        response = client.get("/api/v1/health/")
        assert response.status_code == status.HTTP_200_OK

        # Liveness should always be 200
        response = client.get("/api/v1/health/live/")
        assert response.status_code == status.HTTP_200_OK

    def test_health_endpoints_do_not_require_authentication(self, client, db):
        """
        GIVEN a monitoring system without credentials
        WHEN it queries health endpoints
        THEN the endpoints should be accessible without authentication
        """
        # No authentication provided
        endpoints = [
            "/api/v1/health/",
            "/api/v1/status/",
            "/api/v1/health/ready/",
            "/api/v1/health/live/",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should be accessible (not 401 or 403)
            assert response.status_code not in [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]


@pytest.mark.acceptance
class TestAdditionalRequirements:
    """Additional acceptance tests for comprehensive validation."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_all_endpoints_exist(self, client, db):
        """Verify all expected health check endpoints exist."""
        endpoints = [
            "/api/v1/health/",
            "/api/v1/status/",
            "/api/v1/health/ready/",
            "/api/v1/health/live/",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not be 404
            assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_endpoints_do_not_expose_credentials(self, client, db):
        """Verify no credentials are exposed in health check responses."""
        endpoints = [
            "/api/v1/health/",
            "/api/v1/status/",
            "/api/v1/health/ready/",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            response_str = str(response.data).lower()

            # Should not contain password or other credentials
            assert "password" not in response_str
            assert "secret" not in response_str
            assert "api_key" not in response_str
            assert "apikey" not in response_str

    def test_status_endpoint_responds_even_when_database_down(self, client):
        """Verify status endpoint remains accessible for troubleshooting."""
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "unhealthy",
                "database": "disconnected",
                "error": "Connection refused",
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/status/")

            # Status endpoint should still return 200 for troubleshooting
            assert response.status_code == status.HTTP_200_OK
            assert response.data["status"] == "unhealthy"

    def test_liveness_endpoint_always_returns_200(self, client):
        """Verify liveness endpoint doesn't depend on database."""
        # Liveness should work even without database
        response = client.get("/api/v1/health/live/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["alive"] is True
