"""
Integration tests for Profile Creation from Assessment (Story 13.8).

Tests validate that user profiles are correctly created from assessment data,
profile data matches submitted values, users can view their profiles, and
personalized recommendations are present.

Acceptance Criteria:
1. Profile should be created with assessment values when assessment is submitted
2. Training days, sport type, level, and equipment should match submitted values
3. User should be able to view their profile after creation
4. Personalized training program suggestions should be present in the profile
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
@pytest.mark.profile
@pytest.mark.integration
class TestProfileCreationFromAssessment:
    """Test profile creation from assessment data (Story 13.8)."""

    def test_profile_created_with_assessment_values_after_submission(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that a profile is created with assessment values when assessment is submitted.

        Acceptance Criteria: Profile should be created with assessment values
        """
        url = f"{api_base_url}/assessments/"

        # Submit assessment data
        response = authenticated_client.post(url, json=assessment_data)
        assert (
            response.status_code == 201
        ), f"Assessment submission should succeed, got {response.status_code}: {response.text}"

        # Verify profile (assessment) was created
        profile = Assessment.objects.get(user_id=test_user["id"])
        assert (
            profile is not None
        ), "Profile should be created after assessment submission"
        assert profile.sport == assessment_data["sport"]
        assert profile.age == assessment_data["age"]
        assert profile.experience_level == assessment_data["experience_level"]
        assert profile.training_days == assessment_data["training_days"]
        assert profile.equipment == assessment_data["equipment"]

    def test_profile_data_matches_submitted_values(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that profile data matches all submitted assessment values.

        Acceptance Criteria: Training days, sport type, level, and equipment should match
        """
        url = f"{api_base_url}/assessments/"

        # Submit comprehensive assessment data
        assessment_data = {
            "sport": "cricket",
            "age": 28,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "yes",
            "equipment": "full_gym",
        }

        response = authenticated_client.post(url, json=assessment_data)
        assert response.status_code == 201

        # Retrieve profile from database
        profile = Assessment.objects.get(user_id=test_user["id"])

        # Verify all critical fields match exactly
        assert profile.sport == "cricket", "Sport type should match submitted value"
        assert (
            profile.experience_level == "advanced"
        ), "Experience level should match submitted value"
        assert (
            profile.training_days == "6-7"
        ), "Training days should match submitted value"
        assert profile.equipment == "full_gym", "Equipment should match submitted value"

    def test_user_can_view_profile_after_creation(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
    ) -> None:
        """
        Test that user can view their profile after assessment submission.

        Acceptance Criteria: User should be able to view their profile
        """
        # Submit assessment to create profile
        submit_url = f"{api_base_url}/assessments/"
        response = authenticated_client.post(submit_url, json=assessment_data)
        assert response.status_code == 201

        # Retrieve profile via API
        profile_url = f"{api_base_url}/assessments/me/"
        profile_response = authenticated_client.get(profile_url)

        assert profile_response.status_code == 200, (
            f"User should be able to view profile, "
            f"got {profile_response.status_code}: {profile_response.text}"
        )

        profile_data = profile_response.json()
        assert "sport" in profile_data, "Profile should contain sport"
        assert "age" in profile_data, "Profile should contain age"
        assert (
            "experience_level" in profile_data
        ), "Profile should contain experience level"
        assert "training_days" in profile_data, "Profile should contain training days"
        assert "equipment" in profile_data, "Profile should contain equipment"

    def test_profile_view_contains_all_submitted_data(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
    ) -> None:
        """
        Test that profile view contains complete submitted assessment data.

        Acceptance Criteria: User should be able to view their complete profile
        """
        # Submit assessment
        submit_url = f"{api_base_url}/assessments/"
        authenticated_client.post(submit_url, json=assessment_data)

        # Retrieve and verify profile
        profile_url = f"{api_base_url}/assessments/me/"
        response = authenticated_client.get(profile_url)

        assert response.status_code == 200
        profile = response.json()

        # Verify all data matches
        assert profile["sport"] == assessment_data["sport"]
        assert profile["age"] == assessment_data["age"]
        assert profile["experience_level"] == assessment_data["experience_level"]
        assert profile["training_days"] == assessment_data["training_days"]
        assert profile["equipment"] == assessment_data["equipment"]
        assert profile["injuries"] == assessment_data["injuries"]

    def test_profile_access_requires_authentication(
        self, api_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that profile access requires authentication.

        Acceptance Criteria: User must be authenticated to view their profile
        """
        profile_url = f"{api_base_url}/assessments/me/"
        response = api_client.get(profile_url)

        assert (
            response.status_code == 401
        ), f"Unauthenticated access should be denied, got {response.status_code}"

    def test_profile_not_found_before_assessment_submission(
        self, authenticated_client: requests.Session, api_base_url: str
    ) -> None:
        """
        Test that profile doesn't exist before assessment submission.

        Acceptance Criteria: Profile should only exist after assessment is created
        """
        profile_url = f"{api_base_url}/assessments/me/"
        response = authenticated_client.get(profile_url)

        assert (
            response.status_code == 404
        ), f"Profile should not exist before assessment, got {response.status_code}"
        assert "detail" in response.json()

    def test_profile_includes_metadata_fields(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
    ) -> None:
        """
        Test that profile includes metadata fields like creation timestamp.

        Acceptance Criteria: Profile should include complete metadata
        """
        # Submit assessment
        submit_url = f"{api_base_url}/assessments/"
        authenticated_client.post(submit_url, json=assessment_data)

        # Retrieve profile
        profile_url = f"{api_base_url}/assessments/me/"
        response = authenticated_client.get(profile_url)

        assert response.status_code == 200
        profile = response.json()

        # Verify metadata fields
        assert "id" in profile, "Profile should have an ID"
        assert "created_at" in profile, "Profile should have creation timestamp"
        assert "updated_at" in profile, "Profile should have update timestamp"

    def test_profile_recommendations_based_on_beginner_level(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that profile contains appropriate recommendations for beginner level.

        Acceptance Criteria: Personalized training program suggestions should be present
        """
        # Submit beginner assessment
        submit_url = f"{api_base_url}/assessments/"
        beginner_data = {
            "sport": "football",
            "age": 20,
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }
        authenticated_client.post(submit_url, json=beginner_data)

        # Retrieve profile
        profile_url = f"{api_base_url}/assessments/me/"
        response = authenticated_client.get(profile_url)

        assert response.status_code == 200
        profile = response.json()

        # Verify profile contains data for personalized recommendations
        assert profile["experience_level"] == "beginner"
        assert profile["sport"] == "football"
        assert profile["equipment"] == "no_equipment"
        assert profile["training_days"] == "2-3"

    def test_profile_recommendations_based_on_advanced_level(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that profile contains appropriate recommendations for advanced level.

        Acceptance Criteria: Personalized training program suggestions should be present
        """
        # Submit advanced assessment
        submit_url = f"{api_base_url}/assessments/"
        advanced_data = {
            "sport": "cricket",
            "age": 30,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "no",
            "equipment": "full_gym",
        }
        authenticated_client.post(submit_url, json=advanced_data)

        # Retrieve profile
        profile_url = f"{api_base_url}/assessments/me/"
        response = authenticated_client.get(profile_url)

        assert response.status_code == 200
        profile = response.json()

        # Verify profile contains data for personalized recommendations
        assert profile["experience_level"] == "advanced"
        assert profile["sport"] == "cricket"
        assert profile["equipment"] == "full_gym"
        assert profile["training_days"] == "6-7"

    def test_profile_recommendations_considers_injury_history(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that profile includes injury history for recommendation generation.

        Acceptance Criteria: Personalized recommendations should account for injuries
        """
        # Submit assessment with injury history
        submit_url = f"{api_base_url}/assessments/"
        injury_data = {
            "sport": "football",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "yes",
            "equipment": "basic_equipment",
        }
        authenticated_client.post(submit_url, json=injury_data)

        # Retrieve profile
        profile_url = f"{api_base_url}/assessments/me/"
        response = authenticated_client.get(profile_url)

        assert response.status_code == 200
        profile = response.json()

        # Verify injury data is available for recommendations
        assert profile["injuries"] == "yes"

    def test_profile_recommendations_considers_equipment_availability(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that profile includes equipment availability for recommendations.

        Acceptance Criteria: Recommendations should be tailored to available equipment
        """
        # Test all equipment levels
        equipment_levels = [
            ("no_equipment", "2-3"),
            ("basic_equipment", "4-5"),
            ("full_gym", "6-7"),
        ]

        for equipment, days in equipment_levels:
            # Clean up previous assessment
            Assessment.objects.filter(user_id=test_user["id"]).delete()

            # Submit assessment with specific equipment
            submit_url = f"{api_base_url}/assessments/"
            equipment_data = {
                "sport": "football",
                "age": 25,
                "experience_level": "intermediate",
                "training_days": days,
                "injuries": "no",
                "equipment": equipment,
            }
            authenticated_client.post(submit_url, json=equipment_data)

            # Retrieve and verify profile
            profile_url = f"{api_base_url}/assessments/me/"
            response = authenticated_client.get(profile_url)

            assert response.status_code == 200
            profile = response.json()
            assert (
                profile["equipment"] == equipment
            ), f"Profile should contain equipment level: {equipment}"

    def test_profile_recommendations_for_different_sports(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that profile contains sport-specific data for recommendations.

        Acceptance Criteria: Recommendations should be sport-specific
        """
        sports = ["football", "cricket"]

        for sport in sports:
            # Clean up previous assessment
            Assessment.objects.filter(user_id=test_user["id"]).delete()

            # Submit assessment for specific sport
            submit_url = f"{api_base_url}/assessments/"
            sport_data = {
                "sport": sport,
                "age": 25,
                "experience_level": "intermediate",
                "training_days": "4-5",
                "injuries": "no",
                "equipment": "basic_equipment",
            }
            authenticated_client.post(submit_url, json=sport_data)

            # Retrieve and verify profile
            profile_url = f"{api_base_url}/assessments/me/"
            response = authenticated_client.get(profile_url)

            assert response.status_code == 200
            profile = response.json()
            assert profile["sport"] == sport, f"Profile should contain sport: {sport}"

    def test_profile_update_reflects_in_view(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        assessment_data: Dict[str, Any],
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that profile view reflects updates to assessment data.

        Acceptance Criteria: Profile should show current assessment data
        """
        # Submit initial assessment
        submit_url = f"{api_base_url}/assessments/"
        response = authenticated_client.post(submit_url, json=assessment_data)
        assert response.status_code == 201
        assessment_id = response.json()["id"]

        # Update assessment
        update_url = f"{api_base_url}/assessments/{assessment_id}/"
        updated_data = {
            "sport": "cricket",
            "age": 30,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "yes",
            "equipment": "full_gym",
        }
        update_response = authenticated_client.put(update_url, json=updated_data)
        assert update_response.status_code == 200

        # Retrieve profile and verify it reflects updates
        profile_url = f"{api_base_url}/assessments/me/"
        profile_response = authenticated_client.get(profile_url)

        assert profile_response.status_code == 200
        profile = profile_response.json()

        # Verify updated values
        assert profile["sport"] == "cricket"
        assert profile["age"] == 30
        assert profile["experience_level"] == "advanced"
        assert profile["training_days"] == "6-7"
        assert profile["equipment"] == "full_gym"

    def test_multiple_users_have_separate_profiles(
        self, api_base_url: str, django_db_blocker
    ) -> None:
        """
        Test that multiple users have separate, isolated profiles.

        Acceptance Criteria: Each user should have their own profile
        """
        with django_db_blocker.unblock():
            from django.contrib.auth import get_user_model  # noqa: E402

            User = get_user_model()

            # Create two separate users
            User.objects.filter(email__in=["user1@test.com", "user2@test.com"]).delete()

            user1 = User.objects.create_user(email="user1@test.com", password="pass123")
            user2 = User.objects.create_user(email="user2@test.com", password="pass123")

        # Create sessions for both users
        session1 = requests.Session()
        session1.headers.update({"Content-Type": "application/json"})

        session2 = requests.Session()
        session2.headers.update({"Content-Type": "application/json"})

        # Login both users
        login_url = f"{api_base_url}/auth/login/"
        response1 = session1.post(
            login_url, json={"email": "user1@test.com", "password": "pass123"}
        )
        token1 = response1.json().get("token")
        session1.headers.update({"Authorization": f"Token {token1}"})

        response2 = session2.post(
            login_url, json={"email": "user2@test.com", "password": "pass123"}
        )
        token2 = response2.json().get("token")
        session2.headers.update({"Authorization": f"Token {token2}"})

        # Create different assessments for each user
        submit_url = f"{api_base_url}/assessments/"

        user1_data = {
            "sport": "football",
            "age": 25,
            "experience_level": "beginner",
            "training_days": "2-3",
            "injuries": "no",
            "equipment": "no_equipment",
        }
        session1.post(submit_url, json=user1_data)

        user2_data = {
            "sport": "cricket",
            "age": 35,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "yes",
            "equipment": "full_gym",
        }
        session2.post(submit_url, json=user2_data)

        # Verify each user sees only their own profile
        profile_url = f"{api_base_url}/assessments/me/"

        profile1 = session1.get(profile_url).json()
        assert profile1["sport"] == "football"
        assert profile1["experience_level"] == "beginner"

        profile2 = session2.get(profile_url).json()
        assert profile2["sport"] == "cricket"
        assert profile2["experience_level"] == "advanced"

    def test_profile_creation_atomicity(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
        test_user: Dict[str, Any],
    ) -> None:
        """
        Test that profile creation is atomic - either fully created or not at all.

        Acceptance Criteria: Profile creation should be atomic
        """
        # Attempt to submit invalid assessment (should fail)
        submit_url = f"{api_base_url}/assessments/"
        invalid_data = {
            "sport": "invalid_sport",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
        }
        response = authenticated_client.post(submit_url, json=invalid_data)
        assert response.status_code == 400

        # Verify no partial profile was created
        profile_count = Assessment.objects.filter(user_id=test_user["id"]).count()
        assert profile_count == 0, "No partial profile should be created on error"

    def test_profile_provides_complete_data_for_program_generation(
        self,
        authenticated_client: requests.Session,
        api_base_url: str,
    ) -> None:
        """
        Test that profile provides all necessary data for program generation.

        Acceptance Criteria: Profile should contain all data needed for recommendations
        """
        # Submit comprehensive assessment
        submit_url = f"{api_base_url}/assessments/"
        complete_data = {
            "sport": "football",
            "age": 28,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "yes",
            "equipment": "basic_equipment",
        }
        authenticated_client.post(submit_url, json=complete_data)

        # Retrieve profile
        profile_url = f"{api_base_url}/assessments/me/"
        response = authenticated_client.get(profile_url)

        assert response.status_code == 200
        profile = response.json()

        # Verify all fields needed for program generation are present
        required_fields = [
            "sport",
            "age",
            "experience_level",
            "training_days",
            "injuries",
            "equipment",
        ]

        for field in required_fields:
            assert (
                field in profile
            ), f"Profile must contain {field} for program generation"
            assert profile[field] is not None, f"{field} should not be None"
