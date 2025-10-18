"""
Tests for health check endpoints.

This module tests the health check endpoints including overall health,
liveness, and readiness probes.
"""
import pytest
from httpx import AsyncClient


class TestHealthCheckEndpoint:
    """Tests for the main health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_returns_200_when_healthy(self, client: AsyncClient, mock_db_healthy):
        """Test that health check returns 200 when all systems are healthy."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["environment"] == "development"
        assert "version" in data
        assert "checks" in data
        assert data["checks"]["database"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_returns_503_when_degraded(self, client: AsyncClient, mock_db_unhealthy):
        """Test that health check returns 503 when database is unhealthy."""
        response = await client.get("/health")

        assert response.status_code == 503
        data = response.json()

        assert data["status"] == "degraded"
        assert "checks" in data
        assert data["checks"]["database"]["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_health_check_includes_all_checks(self, client: AsyncClient, mock_db_healthy):
        """Test that health check includes all component checks."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Should have database check
        assert "database" in data["checks"]
        assert "status" in data["checks"]["database"]
        assert "message" in data["checks"]["database"]

    @pytest.mark.asyncio
    async def test_health_check_includes_version_info(self, client: AsyncClient, mock_db_healthy):
        """Test that health check includes version and environment info."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "version" in data
        assert "environment" in data
        assert data["version"] == "0.1.0"  # Default from settings


class TestLivenessProbe:
    """Tests for the liveness probe endpoint."""

    @pytest.mark.asyncio
    async def test_liveness_probe_returns_200(self, client: AsyncClient):
        """Test that liveness probe always returns 200 if application is running."""
        response = await client.get("/health/live")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "alive"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_liveness_probe_does_not_check_dependencies(self, client: AsyncClient, mock_db_unhealthy):
        """Test that liveness probe returns 200 even if database is down."""
        # Liveness should not check dependencies
        response = await client.get("/health/live")

        # Should still return 200 because the application process is running
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"


class TestReadinessProbe:
    """Tests for the readiness probe endpoint."""

    @pytest.mark.asyncio
    async def test_readiness_probe_returns_200_when_ready(self, client: AsyncClient, mock_db_healthy):
        """Test that readiness probe returns 200 when application is ready."""
        response = await client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ready"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_readiness_probe_returns_503_when_not_ready(self, client: AsyncClient, mock_db_unhealthy):
        """Test that readiness probe returns 503 when dependencies are not ready."""
        response = await client.get("/health/ready")

        assert response.status_code == 503
        data = response.json()

        assert data["status"] == "not_ready"

    @pytest.mark.asyncio
    async def test_readiness_probe_checks_database(self, client: AsyncClient, mock_db_healthy):
        """Test that readiness probe checks database connectivity."""
        response = await client.get("/health/ready")

        # Should check database and return ready when database is healthy
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


class TestHealthEndpointIntegration:
    """Integration tests for health endpoints."""

    @pytest.mark.asyncio
    async def test_all_health_endpoints_accessible(self, client: AsyncClient, mock_db_healthy):
        """Test that all health endpoints are accessible."""
        endpoints = ["/health", "/health/live", "/health/ready"]

        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code in [200, 503]
            assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_health_endpoints_return_json(self, client: AsyncClient, mock_db_healthy):
        """Test that all health endpoints return valid JSON."""
        endpoints = ["/health", "/health/live", "/health/ready"]

        for endpoint in endpoints:
            response = await client.get(endpoint)
            # Should be able to parse JSON
            data = response.json()
            assert isinstance(data, dict)
            assert "status" in data

    @pytest.mark.asyncio
    async def test_health_check_has_request_id(self, client: AsyncClient, mock_db_healthy):
        """Test that health check responses include request ID from middleware."""
        response = await client.get("/health")

        assert response.status_code == 200
        # Should have request ID from middleware
        assert "X-Request-ID" in response.headers
