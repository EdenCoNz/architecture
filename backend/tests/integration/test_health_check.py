"""
Integration tests for health check endpoint.

This module tests the health check endpoint functionality to ensure
the server responds correctly with status information.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestHealthCheckEndpoint:
    """Test suite for health check endpoint."""

    def test_health_check_returns_ok_status(self, api_client: APIClient) -> None:
        """Test that health check endpoint returns 200 OK status."""
        url = reverse("health-check")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_health_check_returns_expected_structure(self, api_client: APIClient) -> None:
        """Test that health check endpoint returns expected JSON structure."""
        url = reverse("health-check")
        response = api_client.get(url)

        assert "status" in response.data
        assert "timestamp" in response.data
        assert "service" in response.data

    def test_health_check_status_is_healthy(self, api_client: APIClient) -> None:
        """Test that health check status is 'healthy'."""
        url = reverse("health-check")
        response = api_client.get(url)

        assert response.data["status"] == "healthy"

    def test_health_check_service_name_is_set(self, api_client: APIClient) -> None:
        """Test that health check service name is set."""
        url = reverse("health-check")
        response = api_client.get(url)

        assert response.data["service"] == "backend-api"

    def test_health_check_timestamp_is_iso_format(self, api_client: APIClient) -> None:
        """Test that health check timestamp is in ISO format."""
        url = reverse("health-check")
        response = api_client.get(url)

        timestamp = response.data["timestamp"]
        # Verify it's a valid ISO format timestamp
        assert "T" in timestamp
        assert isinstance(timestamp, str)

    def test_health_check_does_not_require_authentication(self, api_client: APIClient) -> None:
        """Test that health check endpoint is publicly accessible."""
        # api_client is unauthenticated by default, no need to force
        # Note: calling force_authenticate(user=None) would trigger session
        # table access which requires migrations that may not be run

        url = reverse("health-check")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_health_check_only_accepts_get_method(self, api_client: APIClient) -> None:
        """Test that health check endpoint only accepts GET requests."""
        url = reverse("health-check")

        # POST should not be allowed
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # PUT should not be allowed
        response = api_client.put(url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # DELETE should not be allowed
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
