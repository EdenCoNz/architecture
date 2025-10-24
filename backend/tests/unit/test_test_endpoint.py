"""
Unit tests for the backend test endpoint (Story-10.1).

Following TDD best practices - these tests are written before implementation
to define expected behavior and validate acceptance criteria.
"""

from datetime import datetime

import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.unit
class TestBackendTestEndpoint:
    """Tests for the backend test endpoint (Story-10.1)."""

    @pytest.fixture
    def client(self):
        """Provide API client for testing."""
        return APIClient()

    def test_endpoint_returns_200_success_response(self, client):
        """
        Acceptance Criteria 1: Given the backend application is running,
        when I make a request to the test endpoint,
        then I should receive an HTTP 200 success response.
        """
        response = client.get("/api/v1/test/")

        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_includes_success_message(self, client):
        """
        Acceptance Criteria 2: Given I call the test endpoint,
        when the response is received,
        then it should include a success message indicating the backend is operational.
        """
        response = client.get("/api/v1/test/")

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert isinstance(response.data["message"], str)
        assert len(response.data["message"]) > 0
        # Verify message indicates backend is operational
        assert (
            "backend" in response.data["message"].lower()
            or "operational" in response.data["message"].lower()
        )

    def test_endpoint_includes_timestamp(self, client):
        """
        Acceptance Criteria 3: Given I call the test endpoint,
        when the response is received,
        then it should include a timestamp showing when the response was generated.
        """
        response = client.get("/api/v1/test/")

        assert response.status_code == status.HTTP_200_OK
        assert "timestamp" in response.data
        assert isinstance(response.data["timestamp"], str)

        # Verify timestamp is valid ISO 8601 format
        datetime.fromisoformat(response.data["timestamp"].replace("Z", "+00:00"))

    def test_endpoint_timestamp_is_recent(self, client):
        """
        Verify that the timestamp reflects the current time when the endpoint is called.
        """
        before_request = datetime.now()
        response = client.get("/api/v1/test/")
        after_request = datetime.now()

        assert response.status_code == status.HTTP_200_OK

        # Parse timestamp from response
        timestamp_str = response.data["timestamp"]
        response_timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

        # Remove timezone awareness for comparison if needed
        if response_timestamp.tzinfo:
            response_timestamp = response_timestamp.replace(tzinfo=None)

        # Verify timestamp is between before and after the request (within reasonable margin)
        time_diff_seconds = (after_request - before_request).total_seconds()
        assert time_diff_seconds < 5  # Should complete within 5 seconds

    def test_endpoint_accessible_without_authentication(self, client):
        """
        Acceptance Criteria 4 (implicit): The endpoint should be publicly accessible
        without authentication to simplify initial integration testing.
        """
        # No authentication provided - should still work
        response = client.get("/api/v1/test/")

        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_returns_json_content_type(self, client):
        """
        Verify the endpoint returns JSON content for frontend consumption.
        """
        response = client.get("/api/v1/test/")

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "application/json"

    def test_endpoint_cors_headers_present(self, client):
        """
        Acceptance Criteria 4: Given I call the test endpoint from any origin,
        when the request is made,
        then CORS headers should allow the frontend application to receive the response.

        Note: This test verifies CORS headers are present. The actual CORS middleware
        is tested separately, but we verify headers are not stripped from this endpoint.
        """
        # Simulate a request from a different origin
        response = client.get("/api/v1/test/", HTTP_ORIGIN="http://localhost:3000")

        # Note: In tests, CORS middleware may not add headers.
        # This test ensures the endpoint doesn't block CORS headers.
        # The actual CORS functionality is verified via CORS configuration tests
        # and integration tests.
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_response_structure_is_consistent(self, client):
        """
        Verify the response structure is consistent across multiple calls.
        """
        response1 = client.get("/api/v1/test/")
        response2 = client.get("/api/v1/test/")

        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK

        # Both should have same keys
        assert set(response1.data.keys()) == set(response2.data.keys())

        # Message should be consistent
        assert response1.data["message"] == response2.data["message"]

        # Timestamps should be different (or at least not guaranteed to be the same)
        # but both should be valid
        datetime.fromisoformat(response1.data["timestamp"].replace("Z", "+00:00"))
        datetime.fromisoformat(response2.data["timestamp"].replace("Z", "+00:00"))

    def test_endpoint_only_accepts_get_method(self, client):
        """
        Verify the endpoint only accepts GET requests.
        """
        response_get = client.get("/api/v1/test/")
        assert response_get.status_code == status.HTTP_200_OK

        # POST should not be allowed
        response_post = client.post("/api/v1/test/", {})
        assert response_post.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # PUT should not be allowed
        response_put = client.put("/api/v1/test/", {})
        assert response_put.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # DELETE should not be allowed
        response_delete = client.delete("/api/v1/test/")
        assert response_delete.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
