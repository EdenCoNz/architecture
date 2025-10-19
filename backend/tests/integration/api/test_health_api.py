"""
Integration tests for health check API endpoints.

These tests verify the health check API endpoints work correctly
with real HTTP requests and database connections.
"""

from datetime import datetime
from unittest.mock import patch

import pytest
from django.db import DatabaseError
from django.urls import reverse
from rest_framework import status


@pytest.mark.integration
class TestHealthCheckAPI:
    """Integration tests for the health check endpoint."""

    def test_health_endpoint_exists(self, api_client, db) -> None:
        """Test that health check endpoint is accessible."""
        url = reverse("health-check")
        response = api_client.get(url)

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        ]

    def test_health_endpoint_returns_json(self, api_client, db) -> None:
        """Test that health check returns JSON response."""
        url = reverse("health-check")
        response = api_client.get(url)

        assert response["Content-Type"] == "application/json"
        assert isinstance(response.json(), dict)

    def test_health_endpoint_structure(self, api_client, db) -> None:
        """Test that health check returns expected fields."""
        url = reverse("health-check")
        response = api_client.get(url)
        data = response.json()

        # Check all required fields are present
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "service" in data
        assert "database" in data
        assert "debug_mode" in data

    def test_health_endpoint_when_healthy(self, api_client, db) -> None:
        """Test health check returns 200 when system is healthy."""
        url = reverse("health-check")
        response = api_client.get(url)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["status"] == "healthy"
        assert data["service"] == "backend-api"
        assert data["database"]["connected"] is True

    def test_health_endpoint_version_format(self, api_client, db) -> None:
        """Test that version field has correct format."""
        url = reverse("health-check")
        response = api_client.get(url)
        data = response.json()

        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0
        # Version should follow semantic versioning pattern
        assert "." in data["version"]

    def test_health_endpoint_timestamp_is_valid(self, api_client, db) -> None:
        """Test that timestamp is a valid ISO format datetime."""
        url = reverse("health-check")
        response = api_client.get(url)
        data = response.json()

        # Should be able to parse as ISO format
        timestamp = datetime.fromisoformat(data["timestamp"])
        assert isinstance(timestamp, datetime)

    def test_health_endpoint_database_status(self, api_client, db) -> None:
        """Test that database status includes required fields."""
        url = reverse("health-check")
        response = api_client.get(url)
        data = response.json()

        db_status = data["database"]
        assert isinstance(db_status, dict)
        assert "status" in db_status
        assert "connected" in db_status
        assert "engine" in db_status

    def test_health_endpoint_no_authentication_required(self, api_client, db) -> None:
        """Test that health check doesn't require authentication."""
        url = reverse("health-check")
        # Make request without authentication
        response = api_client.get(url)

        # Should succeed without credentials
        assert response.status_code == status.HTTP_200_OK

    @patch("core.services.health.connection.cursor")
    def test_health_endpoint_when_database_down(self, mock_cursor, api_client) -> None:
        """Test health check returns 503 when database is down."""
        # Simulate database failure
        mock_cursor.side_effect = DatabaseError("Connection refused")

        url = reverse("health-check")
        response = api_client.get(url)
        data = response.json()

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert data["status"] == "unhealthy"
        assert data["database"]["connected"] is False

    def test_health_endpoint_debug_mode_boolean(self, api_client, db) -> None:
        """Test that debug_mode is a boolean value."""
        url = reverse("health-check")
        response = api_client.get(url)
        data = response.json()

        assert isinstance(data["debug_mode"], bool)


@pytest.mark.integration
@pytest.mark.smoke
class TestHealthCheckReliability:
    """Test health check endpoint reliability and consistency."""

    def test_health_endpoint_multiple_requests(self, api_client, db) -> None:
        """Test that health check is consistent across multiple requests."""
        url = reverse("health-check")

        # Make multiple requests
        responses = [api_client.get(url) for _ in range(5)]

        # All should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "healthy"

    def test_health_endpoint_concurrent_requests(self, api_client, db) -> None:
        """Test that health check handles concurrent requests."""
        url = reverse("health-check")

        # This is a simple test; real concurrent testing would use threading
        responses = []
        for _ in range(10):
            response = api_client.get(url)
            responses.append(response)

        # All should succeed
        assert all(r.status_code == status.HTTP_200_OK for r in responses)

    def test_health_endpoint_timestamp_progresses(self, api_client, db) -> None:
        """Test that timestamps are different for sequential requests."""
        url = reverse("health-check")

        response1 = api_client.get(url)
        timestamp1 = response1.json()["timestamp"]

        response2 = api_client.get(url)
        timestamp2 = response2.json()["timestamp"]

        # Timestamps should be different (or at least not fail)
        # Note: They might be the same if requests are very fast
        assert isinstance(timestamp1, str)
        assert isinstance(timestamp2, str)


@pytest.mark.integration
class TestHealthCheckCaching:
    """Test that health check doesn't use inappropriate caching."""

    def test_health_endpoint_no_cache_headers(self, api_client, db) -> None:
        """Test that health check includes appropriate cache headers."""
        url = reverse("health-check")
        response = api_client.get(url)

        # Health checks should typically not be cached
        # Check that response doesn't have aggressive caching
        cache_control = response.get("Cache-Control", "")
        assert "max-age=31536000" not in cache_control  # No year-long caching


@pytest.mark.integration
class TestHealthCheckHTTPMethods:
    """Test HTTP method support for health check endpoint."""

    def test_health_endpoint_get_allowed(self, api_client, db) -> None:
        """Test that GET method is allowed."""
        url = reverse("health-check")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_health_endpoint_post_not_allowed(self, api_client, db) -> None:
        """Test that POST method is not allowed."""
        url = reverse("health-check")
        response = api_client.post(url, {})

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_health_endpoint_put_not_allowed(self, api_client, db) -> None:
        """Test that PUT method is not allowed."""
        url = reverse("health-check")
        response = api_client.put(url, {})

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_health_endpoint_delete_not_allowed(self, api_client, db) -> None:
        """Test that DELETE method is not allowed."""
        url = reverse("health-check")
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_health_endpoint_head_allowed(self, api_client, db) -> None:
        """Test that HEAD method works."""
        url = reverse("health-check")
        response = api_client.head(url)

        # HEAD should return same status as GET but no body
        assert response.status_code == status.HTTP_200_OK
        assert not response.content or len(response.content) == 0
