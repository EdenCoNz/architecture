"""
Integration tests for Assessment Data Submission (Story 13.7).

Tests validate that assessment data is correctly submitted to the backend,
stored in the database, and proper responses are returned for valid and invalid data.

Acceptance Criteria:
1. Assessment form data is stored in database exactly as entered
2. Success confirmation is returned when data is submitted
3. Validation errors are returned for incomplete data
4. Special characters and edge cases are properly handled
"""

import os
import sys
from typing import Any, Dict

import django
import pytest
import requests  # type: ignore[import-untyped]

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.testing")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
django.setup()

from apps.assessments.models import Assessment  # noqa: E402


@pytest.mark.django_db
@pytest.mark.assessment
@pytest.mark.integration
class TestAssessmentDataSubmission:
    """Test assessment data submission to backend API (Story 13.7)."""

    def test_submit_valid_assessment_returns_success(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
    ) -> None:
        """
        Test that submitting valid assessment data returns success confirmation.

        Acceptance Criteria: Success confirmation should be returned
        """
        url = f"{api_base_url}/assessments/"

        response = authenticated_client.post(url, json=assessment_data)

        # Verify success response
        assert (
            response.status_code == 201
        ), f"Expected 201 Created, got {response.status_code}: {response.text}"
        assert response.headers.get("Content-Type") == "application/json"

        # Verify response contains confirmation data
        data = response.json()
        assert "id" in data, "Response should include assessment ID"
        assert "created_at" in data, "Response should include creation timestamp"
        assert data["sport"] == assessment_data["sport"]
        assert data["age"] == assessment_data["age"]

    def test_submitted_data_stored_exactly_as_entered(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that assessment data is stored in database exactly as entered.

        Acceptance Criteria: Data should be stored in database exactly as entered
        """
        url = f"{api_base_url}/assessments/"

        # Submit assessment data
        response = authenticated_client.post(url, json=assessment_data)
        assert response.status_code == 201

        # Retrieve from database and verify
        assessment = Assessment.objects.get(user_id=test_user["id"])

        assert assessment.sport == assessment_data["sport"]
        assert assessment.age == assessment_data["age"]
        assert assessment.experience_level == assessment_data["experience_level"]
        assert assessment.training_days == assessment_data["training_days"]
        assert assessment.injuries == assessment_data["injuries"]
        assert assessment.equipment == assessment_data["equipment"]

    def test_submit_incomplete_data_returns_validation_errors(
        self, authenticated_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that submitting incomplete data returns validation errors.

        Acceptance Criteria: Validation errors should be returned for incomplete data
        """
        url = f"{api_base_url}/assessments/"

        # Submit empty data
        response = authenticated_client.post(url, json={})

        # Verify validation error response
        assert (
            response.status_code == 400
        ), f"Expected 400 Bad Request, got {response.status_code}"

        data = response.json()
        # Check for errors in either direct format or wrapped format
        errors = data.get("errors", data)

        # Verify all required fields have errors
        assert "sport" in errors, "Missing sport should return error"
        assert "age" in errors, "Missing age should return error"
        assert (
            "experience_level" in errors
        ), "Missing experience_level should return error"
        assert "training_days" in errors, "Missing training_days should return error"
        assert "equipment" in errors, "Missing equipment should return error"

    def test_submit_missing_single_field_returns_specific_error(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
    ) -> None:
        """
        Test that submitting data with one missing field returns specific error.

        Acceptance Criteria: Validation errors should be returned for incomplete data
        """
        url = f"{api_base_url}/assessments/"

        # Test each required field
        required_fields = [
            "sport",
            "age",
            "experience_level",
            "training_days",
            "equipment",
        ]

        for field in required_fields:
            # Create data missing one field
            incomplete_data = assessment_data.copy()
            del incomplete_data[field]

            response = authenticated_client.post(url, json=incomplete_data)

            assert (
                response.status_code == 400
            ), f"Missing {field} should return 400, got {response.status_code}"

            data = response.json()
            errors = data.get("errors", data)
            assert (
                field in errors
            ), f"Missing {field} should be reported in errors, got {errors}"

    def test_submit_assessment_with_special_characters_in_allowed_fields(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that special characters are handled properly in fields that allow them.

        Acceptance Criteria: Special characters should be properly handled
        Note: Current model uses choices for all fields, so special chars would be
        rejected as invalid choices, which is correct behavior.
        """
        url = f"{api_base_url}/assessments/"

        # Test with invalid sport containing special characters
        data = {
            "sport": "soccer!@#",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
        }

        response = authenticated_client.post(url, json=data)

        # Should return validation error for invalid choice
        assert response.status_code == 400
        response_data = response.json()
        errors = response_data.get("errors", response_data)
        assert "sport" in errors

    def test_submit_assessment_with_edge_case_age_minimum(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that minimum age boundary (13) is handled correctly.

        Acceptance Criteria: Edge cases should be properly handled
        """
        url = f"{api_base_url}/assessments/"

        # Test minimum valid age
        data = assessment_data.copy()
        data["age"] = 13

        response = authenticated_client.post(url, json=data)

        assert (
            response.status_code == 201
        ), f"Age 13 should be valid, got {response.status_code}: {response.text}"

        # Verify stored correctly
        assessment = Assessment.objects.get(user_id=test_user["id"])
        assert assessment.age == 13

    def test_submit_assessment_with_edge_case_age_below_minimum(
        self, authenticated_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that age below minimum (12) is rejected.

        Acceptance Criteria: Edge cases should be properly handled
        """
        url = f"{api_base_url}/assessments/"

        data = {
            "sport": "soccer",
            "age": 12,  # Below minimum
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        response = authenticated_client.post(url, json=data)

        assert (
            response.status_code == 400
        ), f"Age 12 should be rejected, got {response.status_code}"

        response_data = response.json()
        errors = response_data.get("errors", response_data)
        assert "age" in errors
        assert "13 years old" in str(errors["age"]).lower()

    def test_submit_assessment_with_edge_case_age_maximum(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that maximum age boundary (100) is handled correctly.

        Acceptance Criteria: Edge cases should be properly handled
        """
        url = f"{api_base_url}/assessments/"

        # Test maximum valid age
        data = assessment_data.copy()
        data["age"] = 100

        response = authenticated_client.post(url, json=data)

        assert (
            response.status_code == 201
        ), f"Age 100 should be valid, got {response.status_code}: {response.text}"

        # Verify stored correctly
        assessment = Assessment.objects.get(user_id=test_user["id"])
        assert assessment.age == 100

    def test_submit_assessment_with_edge_case_age_above_maximum(
        self, authenticated_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that age above maximum (101) is rejected.

        Acceptance Criteria: Edge cases should be properly handled
        """
        url = f"{api_base_url}/assessments/"

        data = {
            "sport": "soccer",
            "age": 101,  # Above maximum
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        response = authenticated_client.post(url, json=data)

        assert (
            response.status_code == 400
        ), f"Age 101 should be rejected, got {response.status_code}"

        response_data = response.json()
        errors = response_data.get("errors", response_data)
        assert "age" in errors
        assert "valid age" in str(errors["age"]).lower()

    def test_submit_assessment_with_null_age(
        self, authenticated_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that null age is rejected with proper error.

        Acceptance Criteria: Edge cases should be properly handled
        """
        url = f"{api_base_url}/assessments/"

        data = {
            "sport": "soccer",
            "age": None,
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        response = authenticated_client.post(url, json=data)

        assert (
            response.status_code == 400
        ), f"Null age should be rejected, got {response.status_code}"

        response_data = response.json()
        errors = response_data.get("errors", response_data)
        assert "age" in errors

    def test_submit_assessment_with_non_numeric_age(
        self, authenticated_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that non-numeric age is rejected with proper error.

        Acceptance Criteria: Edge cases should be properly handled
        """
        url = f"{api_base_url}/assessments/"

        data = {
            "sport": "soccer",
            "age": "twenty-five",
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        response = authenticated_client.post(url, json=data)

        assert (
            response.status_code == 400
        ), f"Non-numeric age should be rejected, got {response.status_code}"

        response_data = response.json()
        errors = response_data.get("errors", response_data)
        assert "age" in errors

    def test_submit_assessment_with_invalid_sport_choice(
        self, authenticated_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that invalid sport choice is rejected.

        Acceptance Criteria: Validation errors should be returned for invalid data
        """
        url = f"{api_base_url}/assessments/"

        data = {
            "sport": "basketball",  # Invalid choice
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
        }

        response = authenticated_client.post(url, json=data)

        assert response.status_code == 400
        response_data = response.json()
        errors = response_data.get("errors", response_data)
        assert "sport" in errors

    def test_submit_assessment_with_invalid_experience_level(
        self, authenticated_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that invalid experience level is rejected.

        Acceptance Criteria: Validation errors should be returned for invalid data
        """
        url = f"{api_base_url}/assessments/"

        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "expert",  # Invalid choice
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
        }

        response = authenticated_client.post(url, json=data)

        assert response.status_code == 400
        response_data = response.json()
        errors = response_data.get("errors", response_data)
        assert "experience_level" in errors

    def test_submit_assessment_with_invalid_training_days(
        self, authenticated_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that invalid training days is rejected.

        Acceptance Criteria: Validation errors should be returned for invalid data
        """
        url = f"{api_base_url}/assessments/"

        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "10",  # Invalid choice
            "injuries": "no",
            "equipment": "basic_equipment",
        }

        response = authenticated_client.post(url, json=data)

        assert response.status_code == 400
        response_data = response.json()
        errors = response_data.get("errors", response_data)
        assert "training_days" in errors

    def test_submit_assessment_with_invalid_equipment(
        self, authenticated_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that invalid equipment is rejected.

        Acceptance Criteria: Validation errors should be returned for invalid data
        """
        url = f"{api_base_url}/assessments/"

        data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "professional_gym",  # Invalid choice
        }

        response = authenticated_client.post(url, json=data)

        assert response.status_code == 400
        response_data = response.json()
        errors = response_data.get("errors", response_data)
        assert "equipment" in errors

    def test_submit_assessment_with_multiple_validation_errors(
        self, authenticated_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that multiple validation errors are returned together.

        Acceptance Criteria: Validation errors should be returned for invalid data
        """
        url = f"{api_base_url}/assessments/"

        data = {
            "sport": "basketball",  # Invalid
            "age": 150,  # Invalid
            "experience_level": "expert",  # Invalid
            "training_days": "10",  # Invalid
            "injuries": "maybe",  # Invalid
            "equipment": "professional",  # Invalid
        }

        response = authenticated_client.post(url, json=data)

        assert response.status_code == 400
        response_data = response.json()
        errors = response_data.get("errors", response_data)

        # Verify all invalid fields are reported
        assert "sport" in errors
        assert "age" in errors
        assert "experience_level" in errors
        assert "training_days" in errors
        assert "injuries" in errors
        assert "equipment" in errors

    def test_submit_assessment_with_all_valid_choices(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test all valid choice combinations are accepted and stored correctly.

        Acceptance Criteria: Data should be stored exactly as entered
        """
        url = f"{api_base_url}/assessments/"

        # Test soccer with all valid combinations
        test_cases = [
            {
                "sport": "soccer",
                "age": 25,
                "experience_level": "beginner",
                "training_days": "2-3",
                "injuries": "no",
                "equipment": "no_equipment",
            },
            {
                "sport": "cricket",
                "age": 30,
                "experience_level": "intermediate",
                "training_days": "4-5",
                "injuries": "yes",
                "equipment": "basic_equipment",
            },
            {
                "sport": "soccer",
                "age": 35,
                "experience_level": "advanced",
                "training_days": "6-7",
                "injuries": "no",
                "equipment": "full_gym",
            },
        ]

        for test_data in test_cases:
            # Clean up previous assessment
            Assessment.objects.filter(user_id=test_user["id"]).delete()

            response = authenticated_client.post(url, json=test_data)

            assert response.status_code == 201, (
                f"Valid data should be accepted: {test_data}, "
                f"got {response.status_code}: {response.text}"
            )

            # Verify stored correctly
            assessment = Assessment.objects.get(user_id=test_user["id"])
            assert assessment.sport == test_data["sport"]
            assert assessment.age == test_data["age"]
            assert assessment.experience_level == test_data["experience_level"]
            assert assessment.training_days == test_data["training_days"]
            assert assessment.injuries == test_data["injuries"]
            assert assessment.equipment == test_data["equipment"]

    def test_submit_assessment_without_authentication_returns_401(
        self,
        api_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
    ) -> None:
        """
        Test that unauthenticated request is rejected.

        Acceptance Criteria: API should require authentication
        """
        url = f"{api_base_url}/assessments/"

        response = api_client.post(url, json=assessment_data)

        assert (
            response.status_code == 401
        ), f"Unauthenticated request should return 401, got {response.status_code}"

    def test_submit_duplicate_assessment_returns_error(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
    ) -> None:
        """
        Test that submitting duplicate assessment for same user returns error.

        Acceptance Criteria: User should only have one assessment
        """
        url = f"{api_base_url}/assessments/"

        # Submit first assessment
        response1 = authenticated_client.post(url, json=assessment_data)
        assert response1.status_code == 201

        # Attempt to submit second assessment
        response2 = authenticated_client.post(url, json=assessment_data)
        assert (
            response2.status_code == 400
        ), f"Duplicate assessment should be rejected, got {response2.status_code}"

    def test_submit_assessment_response_includes_all_fields(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
    ) -> None:
        """
        Test that success response includes all submitted fields.

        Acceptance Criteria: Success confirmation should include complete data
        """
        url = f"{api_base_url}/assessments/"

        response = authenticated_client.post(url, json=assessment_data)

        assert response.status_code == 201

        data = response.json()

        # Verify all fields are in response
        assert data["sport"] == assessment_data["sport"]
        assert data["age"] == assessment_data["age"]
        assert data["experience_level"] == assessment_data["experience_level"]
        assert data["training_days"] == assessment_data["training_days"]
        assert data["injuries"] == assessment_data["injuries"]
        assert data["equipment"] == assessment_data["equipment"]

        # Verify metadata fields
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_submit_assessment_with_empty_string_fields(
        self, authenticated_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that empty string fields are rejected.

        Acceptance Criteria: Empty values should be rejected
        """
        url = f"{api_base_url}/assessments/"

        data = {
            "sport": "",  # Empty string
            "age": 25,
            "experience_level": "",  # Empty string
            "training_days": "",  # Empty string
            "injuries": "no",
            "equipment": "",  # Empty string
        }

        response = authenticated_client.post(url, json=data)

        assert response.status_code == 400
        response_data = response.json()
        errors = response_data.get("errors", response_data)

        # Verify empty fields are reported as errors
        assert "sport" in errors
        assert "experience_level" in errors
        assert "training_days" in errors
        assert "equipment" in errors
