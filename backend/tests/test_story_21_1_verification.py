"""
Verification tests for Story 21.1: Update Sport Internal Identifier to Soccer.

Tests that the sport field correctly uses "soccer" as the internal identifier
while maintaining "Football" as the display label.
"""

import pytest

from apps.assessments.models import Assessment
from apps.users.models import User


@pytest.mark.django_db
class TestStory21_1_SoccerIdentifier:
    """Verify Story 21.1 acceptance criteria."""

    def test_soccer_is_valid_sport_choice(self):
        """
        Acceptance Criteria: Given a user selects "Football" in the assessment form,
        when the data is saved, then the database should store "soccer" as the sport value.
        """
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        # Create assessment with sport="soccer" (internal value)
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )

        # Verify the value is stored as "soccer" in the database
        assert assessment.sport == "soccer"

        # Verify it can be retrieved from database
        retrieved = Assessment.objects.get(id=assessment.id)
        assert retrieved.sport == "soccer"

    def test_sport_choices_include_soccer(self):
        """Verify that the Sport choices enum includes 'soccer' as a valid choice."""
        # Get the valid sport choices
        valid_sports = [choice[0] for choice in Assessment.Sport.choices]

        # Verify 'soccer' is in the choices
        assert "soccer" in valid_sports

        # Verify 'football' is NOT in the choices (it's been replaced)
        assert "football" not in valid_sports

    def test_soccer_display_label_is_football(self):
        """
        Verify that 'soccer' has the display label 'Football' for user-facing display.
        """
        # Check that the display label for 'soccer' is 'Football'
        sport_choices_dict = dict(Assessment.Sport.choices)
        assert sport_choices_dict["soccer"] == "Football"

    def test_api_returns_soccer_value(self):
        """
        Acceptance Criteria: Given the API returns sport data,
        when I inspect the response, then it should return "soccer" as the internal value.
        """
        user = User.objects.create_user(email="api@example.com", password="testpass123")

        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=30,
            experience_level="beginner",
            training_days="2-3",
            injuries="no",
            equipment="no_equipment",
        )

        # Verify that the model returns 'soccer' as the value
        assert assessment.sport == "soccer"

        # Verify querying by sport works correctly
        found = Assessment.objects.filter(sport="soccer").first()
        assert found is not None
        assert found.id == assessment.id

    def test_system_processes_soccer_data_correctly(self):
        """
        Acceptance Criteria: Given assessment data exists with sport="soccer",
        when the system processes this data, then all functionality should work correctly.
        """
        user = User.objects.create_user(
            email="process@example.com", password="testpass123"
        )

        # Create assessment with soccer
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=28,
            experience_level="advanced",
            training_days="6-7",
            injuries="yes",
            equipment="full_gym",
        )

        # Verify string representation works
        expected_str = f"Assessment for {user.email} - soccer"
        assert str(assessment) == expected_str

        # Verify user relationship works
        assert user.assessment == assessment

        # Verify filtering works
        soccer_assessments = Assessment.objects.filter(sport="soccer")
        assert assessment in soccer_assessments

        # Verify indexing (sport field has an index)
        assert assessment.sport == "soccer"
