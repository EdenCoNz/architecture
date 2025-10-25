"""
Example usage of test data generators.

This file demonstrates practical usage patterns for the test data generation utilities.
These examples can be used as reference when writing new tests.
"""

import pytest
from django.contrib.auth import get_user_model

from apps.assessments.models import Assessment
from tests.test_data_generators import (
    AssessmentDataGenerator,
    EdgeCaseDataGenerator,
    TestDataGenerator,
    UserDataGenerator,
)

User = get_user_model()


class TestUserGenerationExamples:
    """Examples of user data generation."""

    def test_create_simple_user(self):
        """Example: Create a simple user for testing."""
        user_gen = UserDataGenerator()
        user = user_gen.generate_user()

        # User is ready to use in tests
        assert user.email is not None
        assert user.is_active is True

    def test_create_user_with_specific_attributes(self):
        """Example: Create a user with specific attributes."""
        user_gen = UserDataGenerator()
        user = user_gen.generate_user(
            email="johndoe@example.com", first_name="John", last_name="Doe"
        )

        assert user.email == "johndoe@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    def test_create_admin_for_permission_testing(self):
        """Example: Create an admin user for permission tests."""
        user_gen = UserDataGenerator()
        admin = user_gen.generate_admin_user()

        # Admin has all privileges
        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_create_user_for_authentication_testing(self):
        """Example: Create a user with known credentials for auth tests."""
        user_gen = UserDataGenerator()
        user, password = user_gen.generate_user_with_credentials(
            password="SecurePass123!"
        )

        # Password is available for login tests
        assert user.check_password("SecurePass123!")


class TestAssessmentGenerationExamples:
    """Examples of assessment data generation."""

    def test_create_simple_assessment(self):
        """Example: Create a simple assessment for testing."""
        assessment_gen = AssessmentDataGenerator()
        assessment = assessment_gen.generate_assessment()

        # Assessment is ready to use
        assert assessment.sport in ["football", "cricket"]
        assert 13 <= assessment.age <= 100

    def test_create_sport_specific_assessment(self):
        """Example: Create a football-specific assessment."""
        assessment_gen = AssessmentDataGenerator()
        football = assessment_gen.generate_football_assessment()

        # Use for sport-specific logic tests
        assert football.sport == "football"

    def test_create_level_specific_assessment(self):
        """Example: Create a beginner assessment for training logic."""
        assessment_gen = AssessmentDataGenerator()
        beginner = assessment_gen.generate_beginner_assessment()

        # Use for experience-level-specific tests
        assert beginner.experience_level == "beginner"
        # Beginners typically have 2-3 training days
        assert beginner.training_days == "2-3"

    def test_create_assessment_dict_for_api(self):
        """Example: Create assessment data for API endpoint testing."""
        assessment_gen = AssessmentDataGenerator()
        data = assessment_gen.generate_assessment_dict(sport="cricket", age=25)

        # Use in API client requests
        assert data["sport"] == "cricket"
        assert data["age"] == 25
        # Can be used with: client.post('/api/assessments/', json=data)

    def test_create_varied_assessments(self):
        """Example: Create multiple varied assessments."""
        assessment_gen = AssessmentDataGenerator()
        assessments = assessment_gen.generate_assessments(count=10)

        # Verify we have variation
        sports = {a.sport for a in assessments}
        levels = {a.experience_level for a in assessments}

        # Good for testing list endpoints and filtering
        assert len(assessments) == 10
        assert len(sports) > 1  # Multiple sports
        assert len(levels) > 1  # Multiple levels


class TestEdgeCaseExamples:
    """Examples of edge case data generation."""

    def test_validate_minimum_age(self):
        """Example: Test minimum age validation."""
        edge_gen = EdgeCaseDataGenerator()
        min_age_assessment = edge_gen.generate_minimum_age_assessment()

        # Test minimum age boundary
        assert min_age_assessment.age == 13
        min_age_assessment.full_clean()  # Should not raise

    def test_validate_maximum_age(self):
        """Example: Test maximum age validation."""
        edge_gen = EdgeCaseDataGenerator()
        max_age_assessment = edge_gen.generate_maximum_age_assessment()

        # Test maximum age boundary
        assert max_age_assessment.age == 100
        max_age_assessment.full_clean()  # Should not raise

    def test_all_equipment_scenarios(self):
        """Example: Test logic for all equipment types."""
        edge_gen = EdgeCaseDataGenerator()
        equipment_assessments = edge_gen.generate_all_equipment_combinations()

        # Test equipment-specific logic for all types
        for assessment in equipment_assessments:
            if assessment.equipment == "no_equipment":
                # Test no-equipment workout logic
                pass
            elif assessment.equipment == "basic_equipment":
                # Test basic equipment workout logic
                pass
            elif assessment.equipment == "full_gym":
                # Test gym-based workout logic
                pass

    def test_comprehensive_boundary_testing(self):
        """Example: Comprehensive boundary value testing."""
        edge_gen = EdgeCaseDataGenerator()
        edge_cases = edge_gen.generate_comprehensive_edge_cases()

        # All edge cases should be valid
        for assessment in edge_cases:
            assessment.full_clean()


class TestCompleteScenarioExamples:
    """Examples of complete scenario generation."""

    def test_onboarding_workflow(self):
        """Example: Test complete onboarding workflow."""
        test_gen = TestDataGenerator()
        scenario = test_gen.generate_complete_onboarding_scenario()

        # Test onboarding for different user types
        beginner = scenario["beginner_user"]
        beginner_assessment = scenario["beginner_assessment"]

        # Verify beginner gets appropriate program
        assert beginner_assessment.experience_level == "beginner"
        assert beginner_assessment.user == beginner

    def test_user_with_assessment_workflow(self):
        """Example: Test user with assessment creation workflow."""
        test_gen = TestDataGenerator()
        user, assessment = test_gen.generate_user_with_assessment(
            sport="football", experience_level="intermediate"
        )

        # User and assessment are linked
        assert assessment.user == user
        assert assessment.sport == "football"
        assert assessment.experience_level == "intermediate"

    def test_bulk_data_for_performance(self):
        """Example: Generate bulk data for performance testing."""
        test_gen = TestDataGenerator()
        bulk_data = test_gen.generate_bulk_test_data(
            user_count=100, assessment_count=80
        )

        # Use for load testing, pagination testing, etc.
        assert len(bulk_data["users"]) == 100
        assert len(bulk_data["assessments"]) == 80


class TestPracticalUseCases:
    """Practical use cases combining generators."""

    def test_user_registration_and_onboarding(self):
        """
        Example: Test complete user registration and onboarding flow.

        Simulates: User signs up -> completes assessment -> gets recommendations
        """
        # 1. User registers
        user_gen = UserDataGenerator()
        user, password = user_gen.generate_user_with_credentials()

        # 2. User completes assessment
        assessment_gen = AssessmentDataGenerator()
        assessment_data = assessment_gen.generate_assessment_dict(
            sport="football", experience_level="beginner"
        )

        # 3. Create assessment for user (simulating API submission)
        assessment = Assessment.objects.create(user=user, **assessment_data)

        # Verify complete flow
        assert user.assessment == assessment
        assert assessment.sport == "football"

    def test_multiple_users_with_different_profiles(self):
        """
        Example: Test system with multiple user profiles.

        Useful for testing: list views, filtering, search, recommendations
        """
        test_gen = TestDataGenerator()

        # Create diverse user base
        beginner_user, beginner_assessment = test_gen.generate_user_with_assessment(
            experience_level="beginner"
        )

        advanced_user, advanced_assessment = test_gen.generate_user_with_assessment(
            experience_level="advanced"
        )

        # Test filtering by experience level
        beginners = Assessment.objects.filter(experience_level="beginner")
        assert beginner_assessment in beginners

        advanced = Assessment.objects.filter(experience_level="advanced")
        assert advanced_assessment in advanced

    def test_permission_based_on_user_type(self):
        """
        Example: Test permissions for different user types.

        Useful for testing: admin vs regular user permissions
        """
        user_gen = UserDataGenerator()

        # Create regular user
        regular_user = user_gen.generate_user()

        # Create admin user
        admin_user = user_gen.generate_admin_user()

        # Test permission logic
        assert not regular_user.is_staff
        assert admin_user.is_staff

    def test_data_validation_edge_cases(self):
        """
        Example: Test data validation with edge cases.

        Useful for testing: form validation, API validation
        """
        edge_gen = EdgeCaseDataGenerator()

        # Test all valid edge cases
        min_age = edge_gen.generate_minimum_age_assessment()
        max_age = edge_gen.generate_maximum_age_assessment()

        # All should pass validation
        min_age.full_clean()
        max_age.full_clean()


# Pytest fixtures using generators
@pytest.fixture
def sample_user():
    """Fixture: Provide a sample user for tests."""
    user_gen = UserDataGenerator()
    return user_gen.generate_user()


@pytest.fixture
def sample_assessment():
    """Fixture: Provide a sample assessment for tests."""
    assessment_gen = AssessmentDataGenerator()
    return assessment_gen.generate_assessment()


@pytest.fixture
def onboarding_scenario():
    """Fixture: Provide a complete onboarding scenario."""
    test_gen = TestDataGenerator()
    return test_gen.generate_complete_onboarding_scenario()


# Example tests using fixtures
class TestWithFixtures:
    """Examples using pytest fixtures."""

    def test_with_user_fixture(self, sample_user):
        """Example: Use user fixture in test."""
        assert sample_user.is_active is True

    def test_with_assessment_fixture(self, sample_assessment):
        """Example: Use assessment fixture in test."""
        assert sample_assessment.sport in ["football", "cricket"]

    def test_with_scenario_fixture(self, onboarding_scenario):
        """Example: Use complete scenario fixture in test."""
        beginner = onboarding_scenario["beginner_user"]
        assert beginner is not None
