"""
Unit tests for Assessment models.
Tests model validation, creation, and user association.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.assessments.models import Assessment
from apps.users.models import User


@pytest.mark.django_db
class TestAssessmentModel:
    """Test Assessment model functionality."""

    def test_create_assessment_with_valid_data(self) -> None:
        """Test creating assessment with all valid required fields."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )

        assert assessment.user == user
        assert assessment.sport == "soccer"
        assert assessment.age == 25
        assert assessment.experience_level == "intermediate"
        assert assessment.training_days == "4-5"
        assert assessment.injuries == "no"
        assert assessment.equipment == "basic_equipment"
        assert str(assessment) == f"Assessment for {user.email} - soccer"

    def test_assessment_associated_with_correct_user(self) -> None:
        """Test assessment is correctly associated with user account."""
        user = User.objects.create_user(email="user1@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="cricket",
            age=30,
            experience_level="advanced",
            training_days="6-7",
            injuries="no",
            equipment="full_gym",
        )

        # Verify relationship
        assert assessment.user == user
        assert user.assessment == assessment
        assert Assessment.objects.filter(user=user).first() == assessment

    def test_one_assessment_per_user(self) -> None:
        """Test OneToOneField ensures only one assessment per user."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )

        # Attempt to create second assessment for same user should fail
        with pytest.raises(IntegrityError):
            Assessment.objects.create(
                user=user,
                sport="cricket",
                age=26,
                experience_level="beginner",
                training_days="2-3",
                injuries="no",
                equipment="no_equipment",
            )

    def test_age_validation_minimum(self) -> None:
        """Test age validation rejects values below 13."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment(
            user=user,
            sport="soccer",
            age=12,  # Below minimum
            experience_level="beginner",
            training_days="2-3",
            injuries="no",
            equipment="no_equipment",
        )

        with pytest.raises(ValidationError) as exc_info:
            assessment.full_clean()

        assert "age" in exc_info.value.error_dict
        assert "You must be at least 13 years old" in str(exc_info.value)

    def test_age_validation_maximum(self) -> None:
        """Test age validation rejects values above 100."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment(
            user=user,
            sport="soccer",
            age=101,  # Above maximum
            experience_level="beginner",
            training_days="2-3",
            injuries="no",
            equipment="no_equipment",
        )

        with pytest.raises(ValidationError) as exc_info:
            assessment.full_clean()

        assert "age" in exc_info.value.error_dict
        assert "Please enter a valid age" in str(exc_info.value)

    def test_age_validation_accepts_valid_range(self) -> None:
        """Test age validation accepts values in range 13-100."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")

        # Test minimum valid age
        assessment1 = Assessment(
            user=user,
            sport="soccer",
            age=13,
            experience_level="beginner",
            training_days="2-3",
            injuries="no",
            equipment="no_equipment",
        )
        assessment1.full_clean()  # Should not raise

        user.delete()
        user2 = User.objects.create_user(email="test2@example.com", password="testpass123")

        # Test maximum valid age
        assessment2 = Assessment(
            user=user2,
            sport="cricket",
            age=100,
            experience_level="advanced",
            training_days="2-3",
            injuries="no",
            equipment="full_gym",
        )
        assessment2.full_clean()  # Should not raise

    def test_sport_choices_validation(self) -> None:
        """Test sport field only accepts valid choices."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment(
            user=user,
            sport="basketball",  # Invalid choice
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )

        with pytest.raises(ValidationError) as exc_info:
            assessment.full_clean()

        assert "sport" in exc_info.value.error_dict

    def test_experience_level_choices_validation(self) -> None:
        """Test experience_level field only accepts valid choices."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment(
            user=user,
            sport="soccer",
            age=25,
            experience_level="expert",  # Invalid choice
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )

        with pytest.raises(ValidationError) as exc_info:
            assessment.full_clean()

        assert "experience_level" in exc_info.value.error_dict

    def test_training_days_choices_validation(self) -> None:
        """Test training_days field only accepts valid choices."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="8-10",  # Invalid choice
            injuries="no",
            equipment="basic_equipment",
        )

        with pytest.raises(ValidationError) as exc_info:
            assessment.full_clean()

        assert "training_days" in exc_info.value.error_dict

    def test_equipment_choices_validation(self) -> None:
        """Test equipment field only accepts valid choices."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="professional_gym",  # Invalid choice
        )

        with pytest.raises(ValidationError) as exc_info:
            assessment.full_clean()

        assert "equipment" in exc_info.value.error_dict

    def test_has_injuries_property(self) -> None:
        """Test has_injuries property correctly identifies injury status."""
        user1 = User.objects.create_user(email="user1@example.com", password="testpass123")
        user2 = User.objects.create_user(email="user2@example.com", password="testpass123")

        assessment_no_injuries = Assessment.objects.create(
            user=user1,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )

        assessment_with_injuries = Assessment.objects.create(
            user=user2,
            sport="cricket",
            age=28,
            experience_level="advanced",
            training_days="6-7",
            injuries="yes",
            equipment="full_gym",
        )

        assert assessment_no_injuries.has_injuries is False
        assert assessment_with_injuries.has_injuries is True

    def test_retrieved_assessment_matches_submitted_data(self) -> None:
        """Test assessment data retrieved from DB matches what was submitted."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        original_data = {
            "user": user,
            "sport": "cricket",
            "age": 32,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "yes",
            "equipment": "full_gym",
        }

        # Create assessment
        assessment = Assessment.objects.create(**original_data)
        assessment_id = assessment.id

        # Retrieve assessment from database
        retrieved = Assessment.objects.get(id=assessment_id)

        # Verify all fields match
        assert retrieved.user == original_data["user"]
        assert retrieved.sport == original_data["sport"]
        assert retrieved.age == original_data["age"]
        assert retrieved.experience_level == original_data["experience_level"]
        assert retrieved.training_days == original_data["training_days"]
        assert retrieved.injuries == original_data["injuries"]
        assert retrieved.equipment == original_data["equipment"]

    def test_assessment_timestamps(self) -> None:
        """Test assessment has created_at and updated_at timestamps from TimeStampedModel."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )

        assert assessment.created_at is not None
        assert assessment.updated_at is not None
        assert assessment.created_at <= assessment.updated_at

    def test_assessment_cascade_delete_with_user(self) -> None:
        """Test assessment is deleted when associated user is deleted."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )
        assessment_id = assessment.id

        # Delete user
        user.delete()

        # Assessment should also be deleted
        assert not Assessment.objects.filter(id=assessment_id).exists()
