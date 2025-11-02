"""
Integration tests for Assessment API endpoints.
Tests authentication, storage, and retrieval of assessment data.
"""

from typing import Any, Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.assessments.models import Assessment
from apps.users.models import User


@pytest.mark.django_db
class TestAssessmentAPI:
    """Test Assessment API endpoint functionality."""

    def test_create_assessment_requires_authentication(self) -> None:
        """Test creating assessment without authentication returns 401."""
        client = APIClient()
        url = reverse("assessment-list")
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell", "barbell"],
        }

        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_assessment_with_valid_data(self) -> None:
        """Test authenticated user can create assessment with valid data."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "cricket",
            "age": 28,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "yes",
            "equipment": "full_gym",
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["sport"] == "cricket"
        assert response.data["age"] == 28
        assert response.data["experience_level"] == "advanced"
        assert response.data["training_days"] == "6-7"
        assert response.data["injuries"] == "yes"
        assert response.data["equipment"] == "full_gym"
        assert "id" in response.data
        assert "created_at" in response.data

    def test_assessment_associated_with_authenticated_user(self) -> None:
        """Test assessment is stored with correct user association."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell", "resistance-bands"],
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        # Verify assessment is associated with the user
        assessment = Assessment.objects.get(id=response.data["id"])
        assert assessment.user == user

    def test_create_assessment_validates_age_minimum(self) -> None:
        """Test age validation rejects values below 13."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "soccer",
            "age": 12,  # Below minimum
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Check for errors in either direct format or wrapped format
        errors = response.data.get("errors", response.data)
        assert "age" in errors
        assert "You must be at least 13 years old" in str(errors["age"])

    def test_create_assessment_validates_age_maximum(self) -> None:
        """Test age validation rejects values above 100."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "soccer",
            "age": 101,  # Above maximum
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Check for errors in either direct format or wrapped format
        errors = response.data.get("errors", response.data)
        assert "age" in errors
        assert "Please enter a valid age" in str(errors["age"])

    def test_create_assessment_validates_required_fields(self) -> None:
        """Test creating assessment with missing required fields."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data: Dict[str, Any] = {}  # Missing all required fields

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Check for errors in either direct format or wrapped format
        errors = response.data.get("errors", response.data)
        assert "sport" in errors
        assert "age" in errors
        assert "experience_level" in errors
        assert "training_days" in errors
        assert "equipment" in errors

    def test_create_assessment_validates_sport_choices(self) -> None:
        """Test sport field only accepts valid choices."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "basketball",  # Invalid choice
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell"],
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Check for errors in either direct format or wrapped format
        errors = response.data.get("errors", response.data)
        assert "sport" in errors

    def test_retrieved_assessment_matches_submitted_data(self) -> None:
        """Test assessment data retrieved matches what was submitted."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        submit_data = {
            "sport": "cricket",
            "age": 32,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "yes",
            "equipment": "full_gym",
        }

        # Create assessment
        response = client.post(url, submit_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Retrieve assessment from database
        assessment = Assessment.objects.get(user=user)

        # Verify all fields match
        assert assessment.sport == submit_data["sport"]
        assert assessment.age == submit_data["age"]
        assert assessment.experience_level == submit_data["experience_level"]
        assert assessment.training_days == submit_data["training_days"]
        assert assessment.injuries == submit_data["injuries"]
        assert assessment.equipment == submit_data["equipment"]

    def test_storage_failure_returns_error(self) -> None:
        """Test storage failure returns appropriate error."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        # Create initial assessment
        url = reverse("assessment-list")
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell"],
        }
        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Attempt to create second assessment for same user (violates OneToOne)
        response2 = client.post(url, data, format="json")
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_can_only_access_own_assessment(self) -> None:
        """Test user can only retrieve their own assessment."""
        user1 = User.objects.create_user(email="user1@example.com", password="testpass123")
        user2 = User.objects.create_user(email="user2@example.com", password="testpass123")

        # Create assessment for user1
        Assessment.objects.create(
            user=user1,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )

        # User2 tries to list assessments
        client = APIClient()
        client.force_authenticate(user=user2)
        url = reverse("assessment-list")
        response = client.get(url)

        # Should return empty list (user2 has no assessment)
        assert response.status_code == status.HTTP_200_OK
        # Handle paginated response
        results = response.data.get("results", response.data)
        assert len(results) == 0

    def test_get_assessment_returns_user_assessment(self) -> None:
        """Test GET request returns authenticated user's assessment."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="cricket",
            age=30,
            experience_level="advanced",
            training_days="6-7",
            injuries="yes",
            equipment="full_gym",
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("assessment-list")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Handle paginated response
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["id"] == assessment.id
        assert results[0]["sport"] == "cricket"
        assert results[0]["age"] == 30

    def test_unauthenticated_get_assessment_returns_401(self) -> None:
        """Test GET request without authentication returns 401."""
        client = APIClient()
        url = reverse("assessment-list")
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_assessment_with_valid_data(self) -> None:
        """Test authenticated user can update their assessment."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
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
            "sport": "cricket",
            "age": 26,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "yes",
            "equipment": "basic_equipment",
            "equipment_items": ["barbell", "bench"],
        }

        response = client.put(url, update_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["sport"] == "cricket"
        assert response.data["age"] == 26
        assert response.data["experience_level"] == "intermediate"

        # Verify database was updated
        assessment.refresh_from_db()
        assert assessment.sport == "cricket"
        assert assessment.age == 26

    def test_create_assessment_validates_age_non_numeric(self) -> None:
        """Test age validation rejects non-numeric values via API."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "soccer",
            "age": "twenty-five",  # Non-numeric string
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data.get("errors", response.data)
        assert "age" in errors

    def test_create_assessment_validates_age_null(self) -> None:
        """Test age validation rejects null values via API."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "soccer",
            "age": None,  # Null age
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data.get("errors", response.data)
        assert "age" in errors

    def test_create_assessment_validates_multiple_errors(self) -> None:
        """Test API returns all validation errors for multiple invalid fields."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "basketball",  # Invalid sport
            "age": 150,  # Invalid age
            "experience_level": "expert",  # Invalid level
            "training_days": "10",  # Invalid days
            "injuries": "maybe",  # Invalid injury status
            "equipment": "professional",  # Invalid equipment
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data.get("errors", response.data)
        assert "sport" in errors
        assert "age" in errors
        assert "experience_level" in errors
        assert "training_days" in errors
        assert "injuries" in errors
        assert "equipment" in errors

    def test_create_assessment_validates_sport_empty_string(self) -> None:
        """Test sport validation rejects empty strings via API."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "",  # Empty string
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell"],
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data.get("errors", response.data)
        assert "sport" in errors

    def test_create_assessment_validates_sport_case_sensitive(self) -> None:
        """Test sport validation is case-sensitive via API."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "SOCCER",  # Uppercase
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell"],
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data.get("errors", response.data)
        assert "sport" in errors

    def test_create_assessment_all_fields_valid_stores_successfully(self) -> None:
        """Test when all validations pass, assessment is stored successfully."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "cricket",
            "age": 28,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "yes",
            "equipment": "full_gym",
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Assessment.objects.filter(user=user).exists()
        assessment = Assessment.objects.get(user=user)
        assert assessment.sport == "cricket"
        assert assessment.age == 28
        assert assessment.experience_level == "advanced"
        assert assessment.training_days == "6-7"
        assert assessment.injuries == "yes"
        assert assessment.equipment == "full_gym"

    def test_create_assessment_validates_age_boundary_values(self) -> None:
        """Test age validation at exact boundary values via API."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("assessment-list")

        # Test age = 13 (minimum valid) - should succeed
        data_min = {
            "sport": "soccer",
            "age": 13,
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }
        response = client.post(url, data_min, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Clean up
        Assessment.objects.filter(user=user).delete()

        # Test age = 12 (below minimum) - should fail
        data_below = {
            "sport": "soccer",
            "age": 12,
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }
        response = client.post(url, data_below, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data.get("errors", response.data)
        assert "age" in errors
        assert "You must be at least 13 years old" in str(errors["age"])

    def test_create_assessment_validates_single_equipment_selection(self) -> None:
        """Test single equipment selection is enforced via API."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        # Valid single selection
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell", "barbell"],
        }

        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["equipment"] == "basic_equipment"

    def test_create_assessment_rejects_multiple_equipment_selections(self) -> None:
        """Test API rejects multiple equipment selections (Story 19.7)."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        # Multiple selections as list
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": ["no_equipment", "basic_equipment"],
        }

        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data.get("errors", response.data)
        assert "equipment" in errors
        assert "Please select only one equipment level" in str(errors["equipment"])

    def test_create_assessment_requires_equipment_level(self) -> None:
        """Test API requires equipment level to be provided (Story 19.7)."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        # Missing equipment field
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            # equipment missing
        }

        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data.get("errors", response.data)
        assert "equipment" in errors
        assert "Equipment level is required" in str(errors["equipment"])

    def test_create_assessment_rejects_empty_string_equipment(self) -> None:
        """Test API rejects empty string for equipment (Story 19.7)."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "",
        }

        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data.get("errors", response.data)
        assert "equipment" in errors
        assert "Equipment level is required" in str(errors["equipment"])

    def test_create_assessment_rejects_null_equipment(self) -> None:
        """Test API rejects null value for equipment (Story 19.7)."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-list")
        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": None,
        }

        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data.get("errors", response.data)
        assert "equipment" in errors
        assert "Equipment level is required" in str(errors["equipment"])

    def test_create_assessment_accepts_all_valid_equipment_levels(self) -> None:
        """Test API accepts all valid equipment levels (Story 19.7)."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("assessment-list")

        valid_equipment_levels = ["no_equipment", "basic_equipment", "full_gym"]

        for equipment in valid_equipment_levels:
            # Clean up previous assessment
            Assessment.objects.filter(user=user).delete()

            data = {
                "sport": "soccer",
                "age": 25,
                "experience_level": "intermediate",
                "training_days": "4-5",
                "injuries": "no",
                "equipment": equipment,
            }

            # Add equipment_items only for basic_equipment
            if equipment == "basic_equipment":
                data["equipment_items"] = ["dumbbell"]

            response = client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["equipment"] == equipment


@pytest.mark.django_db
class TestAssessmentRetrieval:
    """Test Assessment retrieval functionality (Story 11.10)."""

    def test_retrieve_current_user_assessment_via_me_endpoint(self) -> None:
        """Test retrieving current user's assessment via /me endpoint."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="cricket",
            age=30,
            experience_level="advanced",
            training_days="6-7",
            injuries="yes",
            equipment="full_gym",
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("assessment-me")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == assessment.id
        assert response.data["sport"] == "cricket"
        assert response.data["age"] == 30
        assert response.data["experience_level"] == "advanced"
        assert response.data["training_days"] == "6-7"
        assert response.data["injuries"] == "yes"
        assert response.data["equipment"] == "full_gym"

    def test_retrieve_nonexistent_assessment_returns_404(self) -> None:
        """Test retrieving assessment when none exists returns 404 with clear message."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("assessment-me")
        response = client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.data
        assert "No assessment found" in response.data["detail"]

    def test_retrieve_assessment_includes_all_submitted_fields(self) -> None:
        """Test retrieved assessment includes all fields that were submitted."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        submitted_data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbell", "barbell"],
        }
        assessment = Assessment.objects.create(user=user, **submitted_data)

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("assessment-me")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Verify all submitted fields are present
        assert response.data["sport"] == submitted_data["sport"]
        assert response.data["age"] == submitted_data["age"]
        assert response.data["experience_level"] == submitted_data["experience_level"]
        assert response.data["training_days"] == submitted_data["training_days"]
        assert response.data["injuries"] == submitted_data["injuries"]
        assert response.data["equipment"] == submitted_data["equipment"]
        assert response.data["equipment_items"] == submitted_data["equipment_items"]
        # Also verify metadata fields
        assert "id" in response.data
        assert "created_at" in response.data
        assert "updated_at" in response.data

    def test_retrieve_assessment_for_program_generation(self) -> None:
        """Test retrieving assessment data for program generation use case."""
        user = User.objects.create_user(email="athlete@example.com", password="testpass123")
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
        # Verify complete assessment is provided for program generation
        assert response.data["sport"] == "soccer"
        assert response.data["age"] == 28
        assert response.data["experience_level"] == "advanced"
        assert response.data["training_days"] == "6-7"
        assert response.data["injuries"] == "no"
        assert response.data["equipment"] == "full_gym"

    def test_retrieve_assessment_for_profile_display(self) -> None:
        """Test retrieving assessment data for profile display use case."""
        user = User.objects.create_user(email="user@example.com", password="testpass123")
        Assessment.objects.create(
            user=user,
            sport="cricket",
            age=35,
            experience_level="intermediate",
            training_days="4-5",
            injuries="yes",
            equipment="basic_equipment",
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("assessment-me")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Verify all information is available for profile display
        assert response.data["sport"] == "cricket"
        assert response.data["age"] == 35
        assert response.data["experience_level"] == "intermediate"
        assert response.data["training_days"] == "4-5"
        assert response.data["injuries"] == "yes"
        assert response.data["equipment"] == "basic_equipment"
        assert "created_at" in response.data

    def test_retrieve_assessment_requires_authentication(self) -> None:
        """Test retrieving assessment without authentication returns 401."""
        client = APIClient()
        url = reverse("assessment-me")
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_assessment_detail_by_id(self) -> None:
        """Test retrieving specific assessment by ID."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=27,
            experience_level="beginner",
            training_days="2-3",
            injuries="no",
            equipment="no_equipment",
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("assessment-detail", kwargs={"pk": assessment.pk})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == assessment.id
        assert response.data["sport"] == "soccer"
        assert response.data["age"] == 27

    def test_retrieve_other_user_assessment_returns_404(self) -> None:
        """Test user cannot retrieve another user's assessment by ID."""
        user1 = User.objects.create_user(email="user1@example.com", password="testpass123")
        user2 = User.objects.create_user(email="user2@example.com", password="testpass123")

        assessment = Assessment.objects.create(
            user=user1,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )

        # User2 tries to access user1's assessment
        client = APIClient()
        client.force_authenticate(user=user2)
        url = reverse("assessment-detail", kwargs={"pk": assessment.pk})
        response = client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_assessments_returns_only_user_assessments(self) -> None:
        """Test list endpoint returns only authenticated user's assessments."""
        user1 = User.objects.create_user(email="user1@example.com", password="testpass123")
        user2 = User.objects.create_user(email="user2@example.com", password="testpass123")

        # Create assessments for both users
        assessment1 = Assessment.objects.create(
            user=user1,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )
        Assessment.objects.create(
            user=user2,
            sport="cricket",
            age=30,
            experience_level="advanced",
            training_days="6-7",
            injuries="yes",
            equipment="full_gym",
        )

        # User1 requests list
        client = APIClient()
        client.force_authenticate(user=user1)
        url = reverse("assessment-list")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["id"] == assessment1.id
        assert results[0]["sport"] == "soccer"

    def test_retrieve_assessment_after_update(self) -> None:
        """Test retrieving assessment returns updated data after modification."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="beginner",
            training_days="2-3",
            injuries="no",
            equipment="no_equipment",
        )

        client = APIClient()
        client.force_authenticate(user=user)

        # Update assessment
        update_url = reverse("assessment-detail", kwargs={"pk": assessment.pk})
        update_data = {
            "sport": "cricket",
            "age": 26,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "yes",
            "equipment": "basic_equipment",
            "equipment_items": ["kettlebell", "pull-up-bar"],
        }
        update_response = client.put(update_url, update_data, format="json")
        assert update_response.status_code == status.HTTP_200_OK

        # Retrieve via /me endpoint
        me_url = reverse("assessment-me")
        response = client.get(me_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["sport"] == "cricket"
        assert response.data["age"] == 26
        assert response.data["experience_level"] == "intermediate"
        assert response.data["training_days"] == "4-5"
        assert response.data["injuries"] == "yes"
        assert response.data["equipment"] == "basic_equipment"
