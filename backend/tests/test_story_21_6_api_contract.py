"""
Tests for Story 21.6: Update API Contract Documentation

Verifies that the API behaves according to the documented contract,
specifically around sport field values and display labels.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.assessments.models import Assessment

User = get_user_model()


@pytest.mark.django_db
class TestStory21_6_SportFieldDocumentation:
    """
    Test that the API documentation requirements are met for the sport field.

    Acceptance Criteria:
    - API documentation clearly documents "soccer" as internal value with display label "Football"
    - Request/response examples show "soccer" as the value being sent and received
    - API contract lists all valid sport values including "soccer"
    - API schema enumerations include "soccer" as a valid choice
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test client and user for each test."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        self.client.force_authenticate(user=self.user)

    def test_sport_choices_endpoint_documents_soccer_with_football_label(self):
        """
        Verify sport-choices endpoint clearly shows internal value and display label.

        Acceptance: API documentation shows "soccer" is internal value with "Football" display.
        """
        response = self.client.get("/api/v1/assessments/sport-choices/")

        assert response.status_code == status.HTTP_200_OK
        choices = response.json()["choices"]

        # Find soccer choice
        soccer_choice = next((c for c in choices if c["value"] == "soccer"), None)
        assert soccer_choice is not None, "Soccer should be in sport choices"

        # Verify internal value and display label are clearly distinguished
        assert soccer_choice["value"] == "soccer", "Internal value should be 'soccer'"
        assert soccer_choice["display_name"] == "Football", "Display label should be 'Football'"

    def test_create_assessment_request_uses_soccer_value(self):
        """
        Verify request examples show "soccer" as the value being sent.

        Acceptance: Request examples show "soccer" as the value being sent.
        """
        # Simulate the documented example request
        request_data = {
            "sport": "soccer",  # Internal value as documented
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        response = self.client.post("/api/v1/assessments/", data=request_data, format="json")

        # Request should succeed with documented value
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["sport"] == "soccer"

    def test_create_assessment_response_includes_both_value_and_display(self):
        """
        Verify response examples show both "soccer" value and "Football" display.

        Acceptance: Response examples show "soccer" as the value being received.
        """
        request_data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        response = self.client.post("/api/v1/assessments/", data=request_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()

        # Response should include both internal value and display label as documented
        assert response_data["sport"] == "soccer", "Internal value should be 'soccer'"
        assert response_data["sport_display"] == "Football", "Display label should be 'Football'"

    def test_retrieve_assessment_response_includes_both_value_and_display(self):
        """
        Verify GET responses include both sport value and display label.

        Acceptance: Response examples show both internal value and display label.
        """
        # Create an assessment
        assessment = Assessment.objects.create(
            user=self.user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="no_equipment",
        )

        response = self.client.get(f"/api/v1/assessments/{assessment.id}/")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        # Response should include both as documented
        assert response_data["sport"] == "soccer"
        assert response_data["sport_display"] == "Football"

    def test_assessment_me_endpoint_includes_both_value_and_display(self):
        """
        Verify /me endpoint includes both sport value and display label.

        Acceptance: All assessment endpoints show both value and display.
        """
        # Create an assessment
        Assessment.objects.create(
            user=self.user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="no_equipment",
        )

        response = self.client.get("/api/v1/assessments/me/")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        # Response should include both as documented
        assert response_data["sport"] == "soccer"
        assert response_data["sport_display"] == "Football"

    def test_api_contract_valid_sport_values(self):
        """
        Verify API contract lists all valid sport values including "soccer".

        Acceptance: API contract lists all valid sport values including "soccer".
        """
        # Valid values as documented in API contract
        valid_values = ["soccer", "cricket"]

        for sport_value in valid_values:
            request_data = {
                "sport": sport_value,
                "age": 25,
                "experience_level": "intermediate",
                "training_days": "4-5",
                "injuries": "no",
                "equipment": "no_equipment",
            }

            # Clean up before each test
            Assessment.objects.filter(user=self.user).delete()

            response = self.client.post("/api/v1/assessments/", data=request_data, format="json")

            assert (
                response.status_code == status.HTTP_201_CREATED
            ), f"Valid value '{sport_value}' should be accepted"

    def test_api_rejects_invalid_sport_values(self):
        """
        Verify API rejects values not listed in the contract.

        Acceptance: Only documented values are accepted.
        """
        # Invalid values that should be rejected according to contract
        invalid_values = [
            "football",  # Old internal value
            "Football",  # Display label, not internal value
            "Soccer",  # Wrong case
            "tennis",  # Not supported
            "",  # Empty string
        ]

        for sport_value in invalid_values:
            request_data = {
                "sport": sport_value,
                "age": 25,
                "experience_level": "intermediate",
                "training_days": "4-5",
                "injuries": "no",
                "equipment": "no_equipment",
            }

            response = self.client.post("/api/v1/assessments/", data=request_data, format="json")

            assert (
                response.status_code == status.HTTP_400_BAD_REQUEST
            ), f"Invalid value '{sport_value}' should be rejected"
            response_data = response.json()
            # Error may be wrapped in "errors" field or directly in response
            errors = response_data.get("errors", response_data)
            assert "sport" in errors, "Error should be for sport field"

    def test_api_schema_enumerates_soccer_as_valid_choice(self):
        """
        Verify the sport field has correct enumeration constraints.

        Acceptance: API schema enumerations include "soccer" as a valid choice.
        """
        # Get the sport choices from the model (this is what the schema is generated from)
        sport_choices = Assessment.Sport.choices

        # Verify soccer is in the choices
        sport_values = [choice[0] for choice in sport_choices]
        assert "soccer" in sport_values, "soccer should be in sport enumeration"

        # Verify the display label for soccer
        sport_labels = {choice[0]: choice[1] for choice in sport_choices}
        assert (
            sport_labels["soccer"] == "Football"
        ), "soccer should have 'Football' as display label"

    def test_sport_choices_endpoint_lists_all_valid_values(self):
        """
        Verify sport-choices endpoint returns all valid values from the schema.

        Acceptance: Endpoint provides complete list of valid sport values.
        """
        response = self.client.get("/api/v1/assessments/sport-choices/")

        assert response.status_code == status.HTTP_200_OK
        choices = response.json()["choices"]

        # Extract values from response
        returned_values = [choice["value"] for choice in choices]

        # Should include all model choices
        expected_values = [choice[0] for choice in Assessment.Sport.choices]

        assert returned_values == expected_values, "sport-choices should return all valid values"

    def test_error_message_documents_valid_values(self):
        """
        Verify error messages reference the valid sport values (soccer, cricket).

        Acceptance: Error messages help developers understand valid values.
        """
        request_data = {
            "sport": "invalid",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "no_equipment",
        }

        response = self.client.post("/api/v1/assessments/", data=request_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        # Error may be wrapped in "errors" field or directly in response
        errors = response_data.get("errors", response_data)
        error_message = errors["sport"][0]

        # Error message should reference the valid values
        assert (
            "soccer" in error_message or "cricket" in error_message
        ), "Error message should document valid values"


@pytest.mark.django_db
class TestStory21_6_APIContractExamples:
    """
    Test that API behaves exactly as documented in the contract examples.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test client and user for each test."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        self.client.force_authenticate(user=self.user)

    def test_example_create_soccer_assessment(self):
        """
        Test the documented example for creating a soccer assessment.

        This matches the example request in the API contract documentation.
        """
        # Example from API contract
        request_data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbells", "resistance_bands"],
        }

        response = self.client.post("/api/v1/assessments/", data=request_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify response matches documented structure
        assert data["sport"] == "soccer"
        assert data["sport_display"] == "Football"
        assert data["age"] == 25
        assert data["experience_level"] == "intermediate"
        assert data["training_days"] == "4-5"
        assert data["injuries"] == "no"
        assert data["equipment"] == "basic_equipment"
        assert data["equipment_items"] == ["dumbbells", "resistance_bands"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_example_create_cricket_assessment(self):
        """
        Test the documented example for creating a cricket assessment.

        This matches the example request in the API contract documentation.
        """
        # Example from API contract
        request_data = {
            "sport": "cricket",
            "age": 30,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "yes",
            "equipment": "full_gym",
            "equipment_items": [],
        }

        response = self.client.post("/api/v1/assessments/", data=request_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify response matches documented structure
        assert data["sport"] == "cricket"
        assert data["sport_display"] == "Cricket"
        assert data["age"] == 30
        assert data["experience_level"] == "advanced"

    def test_example_error_using_display_label(self):
        """
        Test the documented error example when using display label instead of value.

        API contract specifically documents this common error.
        """
        # Common mistake: using display label instead of internal value
        request_data = {
            "sport": "Football",  # ❌ Display label, not internal value
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "equipment": "no_equipment",
        }

        response = self.client.post("/api/v1/assessments/", data=request_data, format="json")

        # Should fail as documented
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        # Error may be wrapped in "errors" field or directly in response
        errors = response_data.get("errors", response_data)
        assert "sport" in errors

    def test_example_sport_choices_response(self):
        """
        Test that sport-choices response matches documented example.

        API contract provides specific example response structure.
        """
        response = self.client.get("/api/v1/assessments/sport-choices/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure matches documentation
        assert "choices" in data
        assert isinstance(data["choices"], list)
        assert len(data["choices"]) >= 2  # At least soccer and cricket

        # Verify each choice has documented structure
        for choice in data["choices"]:
            assert "value" in choice
            assert "display_name" in choice
            assert isinstance(choice["value"], str)
            assert isinstance(choice["display_name"], str)

        # Verify soccer entry matches documentation
        soccer_choice = next((c for c in data["choices"] if c["value"] == "soccer"), None)
        assert soccer_choice is not None
        assert soccer_choice == {"value": "soccer", "display_name": "Football"}


@pytest.mark.django_db
class TestStory21_6_ValidationErrors:
    """
    Test that validation errors match the documented error responses.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test client and user for each test."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        self.client.force_authenticate(user=self.user)

    def test_error_invalid_sport_value(self):
        """
        Test error response for invalid sport value matches documentation.
        """
        request_data = {
            "sport": "football",  # Invalid - should be "soccer"
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "equipment": "no_equipment",
        }

        response = self.client.post("/api/v1/assessments/", data=request_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        # Error may be wrapped in "errors" field or directly in response
        errors = response_data.get("errors", response_data)
        assert "sport" in errors
        assert isinstance(errors["sport"], list)

    def test_error_missing_sport(self):
        """
        Test error response for missing sport field matches documentation.
        """
        request_data = {
            # Missing sport field
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "equipment": "no_equipment",
        }

        response = self.client.post("/api/v1/assessments/", data=request_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        # Error may be wrapped in "errors" field or directly in response
        errors = response_data.get("errors", response_data)
        assert "sport" in errors

    def test_error_empty_sport(self):
        """
        Test error response for empty sport field matches documentation.
        """
        request_data = {
            "sport": "",  # Empty value
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "equipment": "no_equipment",
        }

        response = self.client.post("/api/v1/assessments/", data=request_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        # Error may be wrapped in "errors" field or directly in response
        errors = response_data.get("errors", response_data)
        assert "sport" in errors
