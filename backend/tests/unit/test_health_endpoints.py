"""
Unit tests for health check endpoints.

Following TDD best practices - these tests are written before implementation
to define expected behavior and validate acceptance criteria.
"""

from unittest.mock import MagicMock, patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.unit
class TestHealthEndpoint:
    """Tests for the basic health check endpoint."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_health_endpoint_returns_200_when_operational(self, client):
        """
        Acceptance Criteria: When I send a request to the health endpoint,
        I should receive a response indicating the server is operational.
        """
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/health/")

            assert response.status_code == status.HTTP_200_OK
            assert response.data["status"] == "healthy"

    def test_health_endpoint_is_machine_readable(self, client):
        """
        Acceptance Criteria: When monitoring systems query the health endpoint,
        they should receive a machine-readable response.
        """
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/health/")

            # Verify JSON response
            assert response["Content-Type"] == "application/json"

            # Verify expected structure
            assert "status" in response.data
            assert "timestamp" in response.data
            assert "database" in response.data

            # Verify consistent status values
            assert response.data["status"] in ["healthy", "degraded", "unhealthy"]

    def test_health_endpoint_returns_503_when_database_unavailable(self, client):
        """
        Acceptance Criteria: When the data store is unavailable,
        I should see the health endpoint report degraded status.
        """
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

            response = client.get("/api/v1/health/")

            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert response.data["status"] == "unhealthy"
            assert "database" in response.data
            assert response.data["database"]["status"] == "disconnected"

    def test_health_endpoint_includes_database_connectivity(self, client):
        """Health check should include database connectivity status."""
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/health/")

            assert "database" in response.data
            assert response.data["database"]["status"] in ["connected", "disconnected"]
            assert "response_time_ms" in response.data["database"]

    def test_health_endpoint_includes_timestamp(self, client):
        """Health check should include timestamp of the check."""
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/health/")

            assert "timestamp" in response.data
            # Timestamp should be ISO 8601 format
            from datetime import datetime

            datetime.fromisoformat(response.data["timestamp"].replace("Z", "+00:00"))

    def test_health_endpoint_handles_partial_failure(self, client):
        """Health check should report degraded status for partial failures."""
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            # Simulate slow database response (still functional but degraded)
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 5500.0,  # Very slow (> 5 seconds)
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/health/")

            # Should still be accessible but might report degraded
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]


@pytest.mark.unit
class TestStatusEndpoint:
    """Tests for the detailed status endpoint."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_status_endpoint_includes_version_information(self, client):
        """
        Acceptance Criteria: When I query the status endpoint,
        I should see version information.
        """
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/status/")

            assert response.status_code == status.HTTP_200_OK
            assert "version" in response.data
            assert "api_version" in response.data

    def test_status_endpoint_includes_uptime_statistics(self, client):
        """
        Acceptance Criteria: When I query the status endpoint,
        I should see uptime statistics.
        """
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/status/")

            assert response.status_code == status.HTTP_200_OK
            assert "uptime_seconds" in response.data
            assert isinstance(response.data["uptime_seconds"], (int, float))
            assert response.data["uptime_seconds"] >= 0

    def test_status_endpoint_includes_memory_usage(self, client):
        """Status endpoint should include memory usage information."""
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/status/")

            assert response.status_code == status.HTTP_200_OK
            assert "memory" in response.data
            assert "used_mb" in response.data["memory"]
            assert "percent" in response.data["memory"]

    def test_status_endpoint_includes_database_details(self, client):
        """Status endpoint should include comprehensive database information."""
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/status/")

            assert "database" in response.data
            assert "status" in response.data["database"]
            assert "response_time_ms" in response.data["database"]
            assert "engine" in response.data["database"]

    def test_status_endpoint_includes_environment(self, client):
        """Status endpoint should include environment information."""
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/status/")

            assert "environment" in response.data
            assert response.data["environment"] in ["development", "production", "testing"]

    def test_status_endpoint_includes_timestamp(self, client):
        """Status endpoint should include timestamp."""
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/status/")

            assert "timestamp" in response.data
            # Timestamp should be ISO 8601 format
            from datetime import datetime

            datetime.fromisoformat(response.data["timestamp"].replace("Z", "+00:00"))

    def test_status_endpoint_handles_database_failure_gracefully(self, client):
        """Status endpoint should still respond when database is down."""
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

            # Status endpoint should still respond with 200 and show details
            assert response.status_code == status.HTTP_200_OK
            assert response.data["status"] == "unhealthy"
            assert response.data["database"]["status"] == "disconnected"


@pytest.mark.unit
class TestReadinessEndpoint:
    """Tests for the readiness endpoint (Kubernetes readiness probe)."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_readiness_endpoint_returns_200_when_ready(self, client):
        """Readiness endpoint should return 200 when service is ready."""
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/health/ready/")

            assert response.status_code == status.HTTP_200_OK
            assert response.data["ready"] is True

    def test_readiness_endpoint_returns_503_when_not_ready(self, client):
        """Readiness endpoint should return 503 when service is not ready."""
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


@pytest.mark.unit
class TestLivenessEndpoint:
    """Tests for the liveness endpoint (Kubernetes liveness probe)."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_liveness_endpoint_always_returns_200(self, client):
        """Liveness endpoint should always return 200 if server is running."""
        response = client.get("/api/v1/health/live/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["alive"] is True

    def test_liveness_endpoint_does_not_check_database(self, client):
        """Liveness endpoint should not depend on database availability."""
        # No database mock needed - liveness should not check database
        response = client.get("/api/v1/health/live/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["alive"] is True


@pytest.mark.unit
class TestHealthCheckSecurity:
    """Tests for security aspects of health check endpoints."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_health_endpoints_do_not_expose_credentials(self, client):
        """Health endpoints should never expose database passwords or credentials."""
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                    # PASSWORD should never be included
                },
            }

            response = client.get("/api/v1/health/")

            # Verify password is not in response
            response_str = str(response.data)
            assert "password" not in response_str.lower()
            assert "PASSWORD" not in response_str

            # Also check status endpoint
            response = client.get("/api/v1/status/")
            response_str = str(response.data)
            assert "password" not in response_str.lower()

    def test_health_endpoints_accessible_without_authentication(self, client):
        """Health endpoints should be accessible without authentication for monitoring."""
        # No authentication provided
        response = client.get("/api/v1/health/")

        # Should still be accessible
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]


@pytest.mark.unit
class TestVersionExposure:
    """
    Tests for Story 16.7: Expose Backend Version Through Status Endpoint.

    Acceptance Criteria:
    - Status endpoint response includes current application version
    - Version information is in standard, machine-readable format
    - All instances report the same version from the same deployment
    - Version updates reflect immediately after deployment restart
    """

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_status_endpoint_includes_application_version(self, client):
        """
        Acceptance Criteria: Given the backend is running, when I send a
        request to the status endpoint, then the response should include
        the current application version (e.g., "version": "1.0.0").
        """
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/status/")

            assert response.status_code == status.HTTP_200_OK
            assert "version" in response.data
            assert isinstance(response.data["version"], str)
            # Version should match semantic versioning format
            assert len(response.data["version"].split(".")) == 3

    def test_version_format_is_machine_readable(self, client):
        """
        Acceptance Criteria: Given I query the status endpoint, when I parse
        the response, then the version information should be in a standard,
        machine-readable format.
        """
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/status/")

            assert response.status_code == status.HTTP_200_OK
            # Response should be JSON
            assert response["Content-Type"] == "application/json"

            # Version should be a string at the top level
            assert isinstance(response.data["version"], str)

            # Version should follow semantic versioning (MAJOR.MINOR.PATCH)
            import re

            semver_pattern = r"^\d+\.\d+\.\d+$"
            assert re.match(semver_pattern, response.data["version"])

    def test_version_comes_from_config_package(self, client):
        """
        Acceptance Criteria: Given multiple backend instances are running,
        when I query each instance's status endpoint, then all instances
        should report the same version if they're from the same deployment.

        This test verifies that the version is sourced from config package,
        ensuring all instances use the same version source of truth.
        """
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            # Import version directly from config package
            from config import __version__ as config_version

            response = client.get("/api/v1/status/")

            # Version in response should match config package version
            assert response.data["version"] == config_version

    def test_version_reflects_config_changes_immediately(self, client):
        """
        Acceptance Criteria: Given the backend version changes, when I query
        the status endpoint after deployment, then it should immediately
        reflect the new version without requiring service restart beyond
        the deployment restart.

        This test verifies that the version is dynamically imported from
        config package, not hardcoded, so changes are reflected on restart.
        """
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            # First request
            response1 = client.get("/api/v1/status/")

            # Import version after first request
            from config import __version__

            # Second request
            response2 = client.get("/api/v1/status/")

            # Both requests should return same version from config
            assert response1.data["version"] == __version__
            assert response2.data["version"] == __version__
            assert response1.data["version"] == response2.data["version"]

    def test_status_endpoint_version_field_type_safety(self, client):
        """
        Verify that the version field is always a string type for
        type safety and consistency across API consumers.
        """
        with patch("apps.core.database.DatabaseHealthCheck.check") as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": 15.5,
                "connection_info": {
                    "engine": "django.db.backends.postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb",
                    "user": "testuser",
                },
            }

            response = client.get("/api/v1/status/")

            # Version must be string type
            assert isinstance(response.data["version"], str)
            # Should not be None or empty
            assert response.data["version"]
            assert len(response.data["version"]) > 0
