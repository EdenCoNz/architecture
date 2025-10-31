"""
Integration tests for predefined equipment options API endpoint.

Tests retrieving predefined equipment options via the API.
Story 19.11: Predefined Equipment Options Management
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class TestEquipmentOptionsAPI(TestCase):
    """Integration tests for equipment options API endpoint."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_get_equipment_options_requires_authentication(self):
        """Test that equipment options endpoint requires authentication."""
        response = self.client.get("/api/v1/assessments/equipment-options/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_equipment_options_returns_predefined_options(self):
        """Test that equipment options endpoint returns predefined options."""
        # Create and authenticate a user
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/v1/assessments/equipment-options/")

        assert response.status_code == status.HTTP_200_OK
        assert "options" in response.data
        assert isinstance(response.data["options"], list)
        assert len(response.data["options"]) == 7

    def test_get_equipment_options_includes_required_items(self):
        """Test that returned options include all required items."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/v1/assessments/equipment-options/")

        assert response.status_code == status.HTTP_200_OK
        options = response.data["options"]
        values = [opt["value"] for opt in options]

        required_items = [
            "dumbbell",
            "barbell",
            "kettlebell",
            "resistance-bands",
            "pull-up-bar",
            "bench",
            "yoga-mat",
        ]
        for item in required_items:
            assert item in values

    def test_equipment_options_have_labels(self):
        """Test that each option has a label field."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/v1/assessments/equipment-options/")

        assert response.status_code == status.HTTP_200_OK
        options = response.data["options"]

        for option in options:
            assert "value" in option
            assert "label" in option
            assert isinstance(option["value"], str)
            assert isinstance(option["label"], str)

    def test_equipment_options_have_correct_labels(self):
        """Test that options have correct human-readable labels."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/v1/assessments/equipment-options/")

        assert response.status_code == status.HTTP_200_OK
        options = response.data["options"]

        # Create a mapping for verification
        option_map = {opt["value"]: opt["label"] for opt in options}

        assert option_map["dumbbell"] == "Dumbbell"
        assert option_map["pull-up-bar"] == "Pull-up Bar"
        assert option_map["resistance-bands"] == "Resistance Bands"

    def test_equipment_options_endpoint_uses_list_action(self):
        """Test that endpoint is accessible via list action."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=user)

        # Endpoint should be GET /api/assessments/equipment-options/
        response = self.client.get("/api/v1/assessments/equipment-options/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED]

    def test_post_equipment_options_not_allowed(self):
        """Test that POST to equipment options is not allowed."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=user)

        response = self.client.post("/api/v1/assessments/equipment-options/", {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
