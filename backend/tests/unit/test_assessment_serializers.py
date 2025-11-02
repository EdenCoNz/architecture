"""
Unit tests for Assessment serializers.
Tests serialization, deserialization, and validation.
"""

import pytest
from rest_framework.exceptions import ValidationError

from apps.assessments.models import Assessment
from apps.assessments.serializers import AssessmentSerializer
from apps.users.models import User


@pytest.mark.django_db
class TestAssessmentSerializer:
    """Test AssessmentSerializer functionality."""

    def test_serialize_assessment(self) -> None:
        """Test serializing an assessment to JSON."""
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
            equipment="basic_equipment",
        )

        serializer = AssessmentSerializer(assessment)
        data = serializer.data

        assert data["sport"] == "soccer"
        assert data["age"] == 25
        assert data["experience_level"] == "intermediate"
        assert data["training_days"] == "4-5"
        assert data["injuries"] == "no"
        assert data["equipment"] == "basic_equipment"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_deserialize_valid_assessment_data(self) -> None:
        """Test deserializing valid JSON to assessment."""
        data = {
            "sport": "cricket",
            "age": 30,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "yes",
            "equipment": "full_gym",
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["sport"] == "cricket"
        assert serializer.validated_data["age"] == 30
        assert serializer.validated_data["experience_level"] == "advanced"
        assert serializer.validated_data["training_days"] == "6-7"
        assert serializer.validated_data["injuries"] == "yes"
        assert serializer.validated_data["equipment"] == "full_gym"

    def test_validate_age_minimum(self) -> None:
        """Test age validation rejects values below 13."""
        data = {
            "sport": "soccer",
            "age": 12,  # Below minimum
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "age" in serializer.errors
        assert "You must be at least 13 years old" in str(serializer.errors["age"])

    def test_validate_age_maximum(self) -> None:
        """Test age validation rejects values above 100."""
        data = {
            "sport": "soccer",
            "age": 101,  # Above maximum
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "age" in serializer.errors
        assert "Please enter a valid age" in str(serializer.errors["age"])

    def test_validate_age_accepts_valid_range(self) -> None:
        """Test age validation accepts values in range 13-100."""
        # Test minimum valid age
        data1 = {
            "sport": "soccer",
            "age": 13,
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }
        serializer1 = AssessmentSerializer(data=data1)
        assert serializer1.is_valid()

        # Test maximum valid age
        data2 = {
            "sport": "cricket",
            "age": 100,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "no",
            "equipment": "full_gym",
        }
        serializer2 = AssessmentSerializer(data=data2)
        assert serializer2.is_valid()

    def test_validate_sport_choices(self) -> None:
        """Test sport field only accepts valid choices."""
        data = {
            "sport": "basketball",  # Invalid choice
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "sport" in serializer.errors

    def test_validate_experience_level_choices(self) -> None:
        """Test experience_level field only accepts valid choices."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "expert",  # Invalid choice
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "experience_level" in serializer.errors

    def test_validate_training_days_choices(self) -> None:
        """Test training_days field only accepts valid choices."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "8-10",  # Invalid choice
            "injuries": "no",
            "equipment": "basic_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "training_days" in serializer.errors

    def test_validate_equipment_choices(self) -> None:
        """Test equipment field only accepts valid choices."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "professional_gym",  # Invalid choice
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "equipment" in serializer.errors

    def test_required_fields_validation(self) -> None:
        """Test all required fields are validated."""
        # Missing all fields
        serializer = AssessmentSerializer(data={})
        assert not serializer.is_valid()
        assert "sport" in serializer.errors
        assert "age" in serializer.errors
        assert "experience_level" in serializer.errors
        assert "training_days" in serializer.errors
        assert "equipment" in serializer.errors
        # injuries has default, so not required

    def test_create_assessment_via_serializer(self) -> None:
        """Test creating assessment instance via serializer."""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        data = {
            "sport": "cricket",
            "age": 28,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "yes",
            "equipment": "full_gym",
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()

        # Save with user context
        assessment = serializer.save(user=user)

        assert assessment.user == user
        assert assessment.sport == "cricket"
        assert assessment.age == 28
        assert assessment.experience_level == "advanced"
        assert assessment.training_days == "6-7"
        assert assessment.injuries == "yes"
        assert assessment.equipment == "full_gym"

    def test_update_assessment_via_serializer(self) -> None:
        """Test updating assessment instance via serializer."""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="beginner",
            training_days="2-3",
            injuries="no",
            equipment="no_equipment",
            equipment_items=[],
        )

        # Update data
        update_data = {
            "sport": "cricket",
            "age": 26,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "yes",
            "equipment": "full_gym",
            "equipment_items": [],
        }

        serializer = AssessmentSerializer(assessment, data=update_data)
        assert serializer.is_valid()
        updated = serializer.save()

        assert updated.id == assessment.id  # Same instance
        assert updated.sport == "cricket"
        assert updated.age == 26
        assert updated.experience_level == "intermediate"
        assert updated.training_days == "4-5"
        assert updated.injuries == "yes"
        assert updated.equipment == "full_gym"

    def test_serializer_excludes_user_field(self) -> None:
        """Test serializer doesn't expose user field in output."""
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
            equipment="basic_equipment",
        )

        serializer = AssessmentSerializer(assessment)
        assert "user" not in serializer.data

    def test_serializer_read_only_fields(self) -> None:
        """Test id, created_at, updated_at are read-only."""
        data = {
            "id": 999,  # Should be ignored
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "no_equipment",
            "equipment_items": [],
            "created_at": "2020-01-01T00:00:00Z",  # Should be ignored
            "updated_at": "2020-01-01T00:00:00Z",  # Should be ignored
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()

        # id, created_at, updated_at should not be in validated_data
        assert "id" not in serializer.validated_data
        assert "created_at" not in serializer.validated_data
        assert "updated_at" not in serializer.validated_data

    def test_validate_age_non_numeric_string(self) -> None:
        """Test age validation rejects non-numeric string values."""
        data = {
            "sport": "soccer",
            "age": "twenty-five",  # Non-numeric string
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "age" in serializer.errors
        assert "Please enter a valid age" in str(serializer.errors["age"])

    def test_validate_age_negative_value(self) -> None:
        """Test age validation rejects negative values."""
        data = {
            "sport": "soccer",
            "age": -5,  # Negative age
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "age" in serializer.errors

    def test_validate_age_zero_value(self) -> None:
        """Test age validation rejects zero value."""
        data = {
            "sport": "soccer",
            "age": 0,  # Zero age
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "age" in serializer.errors
        assert "You must be at least 13 years old" in str(serializer.errors["age"])

    def test_validate_age_float_value(self) -> None:
        """Test age validation rejects float values."""
        data = {
            "sport": "soccer",
            "age": 25.7,  # Float age
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        # IntegerField rejects float values
        assert not serializer.is_valid()
        assert "age" in serializer.errors

    def test_validate_age_null_value(self) -> None:
        """Test age validation rejects null values."""
        data = {
            "sport": "soccer",
            "age": None,  # Null age
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "age" in serializer.errors

    def test_validate_sport_null_value(self) -> None:
        """Test sport validation rejects null values."""
        data = {
            "sport": None,  # Null sport
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "sport" in serializer.errors

    def test_validate_sport_empty_string(self) -> None:
        """Test sport validation rejects empty strings."""
        data = {
            "sport": "",  # Empty string
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "sport" in serializer.errors

    def test_validate_sport_case_sensitivity(self) -> None:
        """Test sport validation is case-sensitive."""
        data = {
            "sport": "SOCCER",  # Uppercase
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "sport" in serializer.errors

    def test_validate_multiple_field_errors(self) -> None:
        """Test validation returns errors for multiple invalid fields."""
        data = {
            "sport": "basketball",  # Invalid sport
            "age": 150,  # Invalid age
            "experience_level": "expert",  # Invalid level
            "training_days": "10",  # Invalid days
            "injuries": "maybe",  # Invalid injury status
            "equipment": "professional",  # Invalid equipment
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "sport" in serializer.errors
        assert "age" in serializer.errors
        assert "experience_level" in serializer.errors
        assert "training_days" in serializer.errors
        assert "injuries" in serializer.errors
        assert "equipment" in serializer.errors

    def test_validate_partial_data_missing_fields(self) -> None:
        """Test validation with only some required fields present."""
        data = {
            "sport": "soccer",
            "age": 25,
            # Missing: experience_level, training_days, equipment
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "experience_level" in serializer.errors
        assert "training_days" in serializer.errors
        assert "equipment" in serializer.errors

    def test_validate_experience_level_null_value(self) -> None:
        """Test experience_level validation rejects null values."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": None,  # Null level
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "experience_level" in serializer.errors

    def test_validate_training_days_null_value(self) -> None:
        """Test training_days validation rejects null values."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": None,  # Null training days
            "injuries": "no",
            "equipment": "basic_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "training_days" in serializer.errors

    def test_validate_equipment_null_value(self) -> None:
        """Test equipment validation rejects null values."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": None,  # Null equipment
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "equipment" in serializer.errors

    def test_validate_boundary_age_values(self) -> None:
        """Test age validation at exact boundary values."""
        # Test age = 13 (minimum valid)
        data_min = {
            "sport": "soccer",
            "age": 13,
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }
        serializer_min = AssessmentSerializer(data=data_min)
        assert serializer_min.is_valid()

        # Test age = 12 (below minimum)
        data_below = {
            "sport": "soccer",
            "age": 12,
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }
        serializer_below = AssessmentSerializer(data=data_below)
        assert not serializer_below.is_valid()
        assert "age" in serializer_below.errors

        # Test age = 100 (maximum valid)
        data_max = {
            "sport": "cricket",
            "age": 100,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "no",
            "equipment": "full_gym",
        }
        serializer_max = AssessmentSerializer(data=data_max)
        assert serializer_max.is_valid()

        # Test age = 101 (above maximum)
        data_above = {
            "sport": "cricket",
            "age": 101,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "no",
            "equipment": "full_gym",
        }
        serializer_above = AssessmentSerializer(data=data_above)
        assert not serializer_above.is_valid()
        assert "age" in serializer_above.errors

    def test_validate_equipment_single_selection_valid(self) -> None:
        """Test equipment validation accepts single valid selection."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "full_gym",
            "equipment_items": [],
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["equipment"] == "full_gym"

    def test_validate_equipment_single_selection_no_equipment(self) -> None:
        """Test equipment validation accepts single no_equipment selection."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["equipment"] == "no_equipment"

    def test_validate_equipment_single_selection_full_gym(self) -> None:
        """Test equipment validation accepts single full_gym selection."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "full_gym",
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["equipment"] == "full_gym"

    def test_validate_equipment_multiple_selections_list_rejected(self) -> None:
        """Test equipment validation rejects multiple selections as list."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": ["no_equipment", "basic_equipment"],
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "equipment" in serializer.errors
        assert "Please select only one equipment level" in str(
            serializer.errors["equipment"]
        )

    def test_validate_equipment_empty_string_rejected(self) -> None:
        """Test equipment validation rejects empty string."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "",
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "equipment" in serializer.errors
        assert "Equipment level is required" in str(serializer.errors["equipment"])

    def test_validate_equipment_null_rejected(self) -> None:
        """Test equipment validation rejects null value."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": None,
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "equipment" in serializer.errors
        assert "Equipment level is required" in str(serializer.errors["equipment"])

    def test_validate_basic_equipment_requires_items(self) -> None:
        """Test basic equipment selection requires equipment items to be specified."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": [],  # No items provided
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "equipment_items" in serializer.errors
        assert "Please specify at least one equipment item" in str(
            serializer.errors["equipment_items"]
        )

    def test_validate_basic_equipment_missing_items_field(self) -> None:
        """Test basic equipment without items field is rejected."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            # equipment_items field missing entirely
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "equipment_items" in serializer.errors
        assert "Please specify at least one equipment item" in str(
            serializer.errors["equipment_items"]
        )

    def test_validate_basic_equipment_with_single_item(self) -> None:
        """Test basic equipment with single equipment item is accepted."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell"],
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["equipment"] == "basic_equipment"
        assert serializer.validated_data["equipment_items"] == ["dumbbell"]

    def test_validate_basic_equipment_with_multiple_items(self) -> None:
        """Test basic equipment with multiple equipment items is accepted."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell", "barbell", "resistance bands"],
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["equipment"] == "basic_equipment"
        assert len(serializer.validated_data["equipment_items"]) == 3
        assert "dumbbell" in serializer.validated_data["equipment_items"]
        assert "barbell" in serializer.validated_data["equipment_items"]
        assert "resistance bands" in serializer.validated_data["equipment_items"]

    def test_validate_basic_equipment_with_custom_items(self) -> None:
        """Test basic equipment with custom equipment items is accepted."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell", "My Custom Equipment"],
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["equipment"] == "basic_equipment"
        assert "My Custom Equipment" in serializer.validated_data["equipment_items"]

    def test_validate_basic_equipment_with_predefined_and_custom_items(self) -> None:
        """Test basic equipment with both predefined and custom items is accepted."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": [
                "dumbbell",
                "barbell",
                "kettlebell",
                "My Custom Band",
                "Other Equipment",
            ],
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()
        assert len(serializer.validated_data["equipment_items"]) == 5
        assert "dumbbell" in serializer.validated_data["equipment_items"]
        assert "My Custom Band" in serializer.validated_data["equipment_items"]
        assert "Other Equipment" in serializer.validated_data["equipment_items"]

    def test_validate_no_equipment_clears_items(self) -> None:
        """Test non-basic equipment clears items even if provided."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "no_equipment",
            "equipment_items": ["dumbbell", "barbell"],  # Should be cleared
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["equipment"] == "no_equipment"
        assert serializer.validated_data["equipment_items"] == []

    def test_validate_full_gym_clears_items(self) -> None:
        """Test full_gym equipment clears items even if provided."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "full_gym",
            "equipment_items": ["dumbbell", "barbell"],  # Should be cleared
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["equipment"] == "full_gym"
        assert serializer.validated_data["equipment_items"] == []

    def test_create_assessment_with_basic_equipment_items(self) -> None:
        """Test creating assessment with basic equipment and items."""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell", "barbell", "Custom Item"],
        }

        serializer = AssessmentSerializer(data=data)
        assert serializer.is_valid()
        assessment = serializer.save(user=user)

        assert assessment.equipment == "basic_equipment"
        assert assessment.equipment_items == ["dumbbell", "barbell", "Custom Item"]
        assert len(assessment.equipment_items) == 3

    def test_update_assessment_equipment_and_items(self) -> None:
        """Test updating assessment to add equipment items."""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="beginner",
            training_days="2-3",
            injuries="no",
            equipment="full_gym",
            equipment_items=[],
        )

        # Update to basic equipment with items
        update_data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell", "resistance bands"],
        }

        serializer = AssessmentSerializer(assessment, data=update_data)
        assert serializer.is_valid()
        updated = serializer.save()

        assert updated.equipment == "basic_equipment"
        assert updated.equipment_items == ["dumbbell", "resistance bands"]

    def test_serialize_assessment_with_equipment_items(self) -> None:
        """Test serializing assessment with equipment items to JSON."""
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
            equipment="basic_equipment",
            equipment_items=["dumbbell", "barbell", "Custom Equipment"],
        )

        serializer = AssessmentSerializer(assessment)
        data = serializer.data

        assert data["equipment"] == "basic_equipment"
        assert len(data["equipment_items"]) == 3
        assert "dumbbell" in data["equipment_items"]
        assert "barbell" in data["equipment_items"]
        assert "Custom Equipment" in data["equipment_items"]

    def test_validate_equipment_items_empty_string_rejected(self) -> None:
        """Test equipment items with empty strings are rejected."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell", "", "barbell"],
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "equipment_items" in serializer.errors

    def test_validate_equipment_items_whitespace_only_rejected(self) -> None:
        """Test equipment items with whitespace only are rejected."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell", "   ", "barbell"],
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "equipment_items" in serializer.errors

    def test_validate_equipment_items_not_list_rejected(self) -> None:
        """Test equipment items that are not a list are rejected."""
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": "dumbbell",  # String instead of list
        }

        serializer = AssessmentSerializer(data=data)
        assert not serializer.is_valid()
        assert "equipment_items" in serializer.errors
