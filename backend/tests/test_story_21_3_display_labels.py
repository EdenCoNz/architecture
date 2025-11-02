"""
Tests for Story 21.3: Maintain Football Display Label for Users.

Verifies that the API returns display labels for sport choices and that
saved assessments show "Football" as the display label for "soccer" value.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.assessments.models import Assessment
from apps.users.models import User


@pytest.mark.django_db
class TestSportDisplayLabels:
    """Test sport field display labels in API responses."""

    def test_sport_choices_endpoint_returns_display_labels(self) -> None:
        """
        Test that the sport choices endpoint returns both value and display label.

        Acceptance Criteria:
        - Given the system stores "soccer" internally, when the API returns sport choices,
          then it should include a display label "Football" for the "soccer" value
        """
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-sport-choices")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "choices" in response.data

        # Find soccer choice
        soccer_choice = next(
            (
                choice
                for choice in response.data["choices"]
                if choice["value"] == "soccer"
            ),
            None,
        )

        assert soccer_choice is not None, "Soccer choice not found in response"
        assert soccer_choice["value"] == "soccer", "Internal value should be 'soccer'"
        assert (
            soccer_choice["display_name"] == "Football"
        ), "Display name should be 'Football'"

        # Verify cricket is also present
        cricket_choice = next(
            (
                choice
                for choice in response.data["choices"]
                if choice["value"] == "cricket"
            ),
            None,
        )
        assert cricket_choice is not None, "Cricket choice not found in response"
        assert cricket_choice["display_name"] == "Cricket"

    def test_assessment_response_includes_sport_display_label(self) -> None:
        """
        Test that assessment responses include the sport display label.

        Acceptance Criteria:
        - Given I view my saved assessment, when the sport is displayed,
          then it should show "Football" not "soccer"
        """
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="no_equipment",
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("assessment-detail", kwargs={"pk": assessment.pk})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["sport"] == "soccer", "Value should be 'soccer'"
        assert (
            "sport_display" in response.data
        ), "Response should include sport_display field"
        assert (
            response.data["sport_display"] == "Football"
        ), "Display should be 'Football'"

    def test_assessment_list_includes_sport_display_labels(self) -> None:
        """
        Test that assessment list responses include sport display labels.

        Acceptance Criteria:
        - Given I view the sport selection options, when I see the available sports,
          then "Football" should be displayed as a choice
        """
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="no_equipment",
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("assessment-list")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["sport"] == "soccer"
        assert results[0]["sport_display"] == "Football"

    def test_assessment_me_endpoint_includes_sport_display_label(self) -> None:
        """
        Test that the /me endpoint includes sport display label.

        Acceptance Criteria:
        - Given I view my saved assessment, when the sport is displayed,
          then it should show "Football" not "soccer"
        """
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        Assessment.objects.create(
            user=user,
            sport="soccer",
            age=28,
            experience_level="advanced",
            training_days="6-7",
            injuries="no",
            equipment="full_gym",
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("assessment-me")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["sport"] == "soccer"
        assert response.data["sport_display"] == "Football"

    def test_cricket_assessment_has_correct_display_label(self) -> None:
        """
        Test that cricket assessments also have correct display labels.
        """
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        Assessment.objects.create(
            user=user,
            sport="cricket",
            age=30,
            experience_level="beginner",
            training_days="2-3",
            injuries="no",
            equipment="basic_equipment",
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("assessment-me")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["sport"] == "cricket"
        assert response.data["sport_display"] == "Cricket"

    def test_sport_choices_endpoint_requires_authentication(self) -> None:
        """Test that sport choices endpoint requires authentication."""
        client = APIClient()
        url = reverse("assessment-sport-choices")
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_created_assessment_returns_sport_display_label(self) -> None:
        """
        Test that creating an assessment returns the sport display label.
        """
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["sport"] == "soccer"
        assert response.data["sport_display"] == "Football"

    def test_updated_assessment_returns_sport_display_label(self) -> None:
        """
        Test that updating an assessment returns the sport display label.
        """
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        assessment = Assessment.objects.create(
            user=user,
            sport="cricket",
            age=25,
            experience_level="beginner",
            training_days="2-3",
            injuries="no",
            equipment="no_equipment",
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("assessment-detail", kwargs={"pk": assessment.pk})

        update_data = {
            "sport": "soccer",
            "age": 26,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell"],
        }

        response = client.put(url, update_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["sport"] == "soccer"
        assert response.data["sport_display"] == "Football"
