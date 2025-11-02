"""
Tests for test data generation utilities (Story 13.14).

These tests verify that the test data generation utilities can create
realistic test data including users, assessments, and edge cases.

Acceptance Criteria:
1. Generate user accounts with realistic profile data
2. Generate valid assessment submissions with varied attributes
3. Support creating boundary values (min/max ages, all equipment combinations)
4. Generated data should be valid and representative of real user input
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.assessments.models import Assessment
from tests.test_data_generators import (
    AssessmentDataGenerator,
    EdgeCaseDataGenerator,
    TestDataGenerator,
    UserDataGenerator,
)

User = get_user_model()


class TestUserDataGenerator:
    """Test user data generation utilities (AC #1)."""

    def test_generate_user_creates_valid_user(self):
        """
        Test that generating a user creates a valid user with realistic profile data.

        Acceptance Criteria: Create user accounts with realistic profile data
        """
        generator = UserDataGenerator()
        user = generator.generate_user()

        # Verify user was created
        assert user is not None
        assert user.id is not None

        # Verify realistic profile data
        assert user.email is not None
        assert "@" in user.email
        assert user.first_name is not None
        assert len(user.first_name) > 0
        assert user.last_name is not None
        assert len(user.last_name) > 0

        # Verify user is active by default
        assert user.is_active is True

    def test_generate_user_with_custom_attributes(self):
        """
        Test that generating a user with custom attributes works correctly.

        Acceptance Criteria: Create user accounts with realistic profile data
        """
        generator = UserDataGenerator()
        custom_email = "custom@example.com"
        user = generator.generate_user(email=custom_email, first_name="John")

        assert user.email == custom_email
        assert user.first_name == "John"

    def test_generate_multiple_users_creates_unique_users(self):
        """
        Test that generating multiple users creates unique users.

        Acceptance Criteria: Create user accounts with realistic profile data
        """
        generator = UserDataGenerator()
        users = generator.generate_users(count=5)

        # Verify correct count
        assert len(users) == 5

        # Verify all users are unique
        emails = [user.email for user in users]
        assert len(emails) == len(set(emails)), "All emails should be unique"

        # Verify all have realistic data
        for user in users:
            assert user.first_name is not None
            assert user.last_name is not None
            assert "@" in user.email

    def test_generate_admin_user_creates_admin(self):
        """
        Test that generating an admin user creates a user with admin privileges.

        Acceptance Criteria: Create user accounts with realistic profile data
        """
        generator = UserDataGenerator()
        admin = generator.generate_admin_user()

        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.is_active is True

    def test_generate_inactive_user_creates_inactive_user(self):
        """
        Test that generating an inactive user works correctly.

        Acceptance Criteria: Create user accounts with realistic profile data
        """
        generator = UserDataGenerator()
        inactive_user = generator.generate_inactive_user()

        assert inactive_user.is_active is False


class TestAssessmentDataGenerator:
    """Test assessment data generation utilities (AC #2)."""

    def test_generate_assessment_creates_valid_assessment(self):
        """
        Test that generating an assessment creates valid data.

        Acceptance Criteria: Generate valid assessment submissions with varied attributes
        """
        generator = AssessmentDataGenerator()
        assessment = generator.generate_assessment()

        # Verify assessment was created
        assert assessment is not None
        assert assessment.id is not None

        # Verify required fields
        assert assessment.sport in ["soccer", "cricket"]
        assert 13 <= assessment.age <= 100
        assert assessment.experience_level in ["beginner", "intermediate", "advanced"]
        assert assessment.training_days in ["2-3", "4-5", "6-7"]
        assert assessment.injuries in ["no", "yes"]
        assert assessment.equipment in ["no_equipment", "basic_equipment", "full_gym"]

        # Verify user association
        assert assessment.user is not None

    def test_generate_assessment_with_custom_sport(self):
        """
        Test that generating an assessment with specific sport works.

        Acceptance Criteria: Generate valid assessment submissions with varied attributes
        """
        generator = AssessmentDataGenerator()
        assessment = generator.generate_assessment(sport="cricket")

        assert assessment.sport == "cricket"

    def test_generate_multiple_assessments_with_varied_attributes(self):
        """
        Test that generating multiple assessments creates varied data.

        Acceptance Criteria: Generate valid assessment submissions with varied attributes
        """
        generator = AssessmentDataGenerator()
        assessments = generator.generate_assessments(count=10)

        assert len(assessments) == 10

        # Verify variation in sports
        sports = [a.sport for a in assessments]
        assert len(set(sports)) > 1, "Should have varied sports"

        # Verify variation in experience levels
        levels = [a.experience_level for a in assessments]
        assert len(set(levels)) > 1, "Should have varied experience levels"

        # Verify variation in training days
        training = [a.training_days for a in assessments]
        assert len(set(training)) > 1, "Should have varied training days"

    def test_generate_soccer_assessment(self):
        """
        Test that generating a soccer-specific assessment works.

        Acceptance Criteria: Generate valid assessment submissions with varied attributes
        """
        generator = AssessmentDataGenerator()
        assessment = generator.generate_soccer_assessment()

        assert assessment.sport == "soccer"

    def test_generate_cricket_assessment(self):
        """
        Test that generating a cricket-specific assessment works.

        Acceptance Criteria: Generate valid assessment submissions with varied attributes
        """
        generator = AssessmentDataGenerator()
        assessment = generator.generate_cricket_assessment()

        assert assessment.sport == "cricket"

    def test_generate_beginner_assessment(self):
        """
        Test that generating a beginner assessment has appropriate characteristics.

        Acceptance Criteria: Generate valid assessment submissions with varied attributes
        """
        generator = AssessmentDataGenerator()
        assessment = generator.generate_beginner_assessment()

        assert assessment.experience_level == "beginner"

    def test_generate_advanced_assessment(self):
        """
        Test that generating an advanced assessment has appropriate characteristics.

        Acceptance Criteria: Generate valid assessment submissions with varied attributes
        """
        generator = AssessmentDataGenerator()
        assessment = generator.generate_advanced_assessment()

        assert assessment.experience_level == "advanced"

    def test_generate_assessment_with_injuries(self):
        """
        Test that generating an assessment with injury history works.

        Acceptance Criteria: Generate valid assessment submissions with varied attributes
        """
        generator = AssessmentDataGenerator()
        assessment = generator.generate_assessment_with_injuries()

        assert assessment.injuries == "yes"


class TestEdgeCaseDataGenerator:
    """Test edge case and boundary value data generation (AC #3)."""

    def test_generate_minimum_age_assessment(self):
        """
        Test that generating an assessment with minimum age (13) works.

        Acceptance Criteria: Support creating boundary values (minimum ages)
        """
        generator = EdgeCaseDataGenerator()
        assessment = generator.generate_minimum_age_assessment()

        assert assessment.age == 13

        # Verify it's valid
        assessment.full_clean()

    def test_generate_maximum_age_assessment(self):
        """
        Test that generating an assessment with maximum age (100) works.

        Acceptance Criteria: Support creating boundary values (maximum ages)
        """
        generator = EdgeCaseDataGenerator()
        assessment = generator.generate_maximum_age_assessment()

        assert assessment.age == 100

        # Verify it's valid
        assessment.full_clean()

    def test_generate_all_equipment_combinations(self):
        """
        Test that generating assessments with all equipment types works.

        Acceptance Criteria: Support creating all equipment combinations
        """
        generator = EdgeCaseDataGenerator()
        assessments = generator.generate_all_equipment_combinations()

        # Should have one assessment per equipment type
        assert len(assessments) == 3

        equipment_types = [a.equipment for a in assessments]
        assert "no_equipment" in equipment_types
        assert "basic_equipment" in equipment_types
        assert "full_gym" in equipment_types

    def test_generate_all_sport_combinations(self):
        """
        Test that generating assessments with all sports works.

        Acceptance Criteria: Support creating all combinations
        """
        generator = EdgeCaseDataGenerator()
        assessments = generator.generate_all_sport_combinations()

        # Should have one assessment per sport
        assert len(assessments) == 2

        sports = [a.sport for a in assessments]
        assert "soccer" in sports
        assert "cricket" in sports

    def test_generate_all_experience_level_combinations(self):
        """
        Test that generating assessments with all experience levels works.

        Acceptance Criteria: Support creating all combinations
        """
        generator = EdgeCaseDataGenerator()
        assessments = generator.generate_all_experience_level_combinations()

        # Should have one assessment per experience level
        assert len(assessments) == 3

        levels = [a.experience_level for a in assessments]
        assert "beginner" in levels
        assert "intermediate" in levels
        assert "advanced" in levels

    def test_generate_all_training_days_combinations(self):
        """
        Test that generating assessments with all training days works.

        Acceptance Criteria: Support creating all combinations
        """
        generator = EdgeCaseDataGenerator()
        assessments = generator.generate_all_training_days_combinations()

        # Should have one assessment per training days option
        assert len(assessments) == 3

        training = [a.training_days for a in assessments]
        assert "2-3" in training
        assert "4-5" in training
        assert "6-7" in training

    def test_generate_comprehensive_edge_cases(self):
        """
        Test that generating comprehensive edge cases covers all scenarios.

        Acceptance Criteria: Support creating boundary values
        """
        generator = EdgeCaseDataGenerator()
        edge_cases = generator.generate_comprehensive_edge_cases()

        # Should include minimum age, maximum age, and various combinations
        assert len(edge_cases) > 5

        # Verify we have both age boundaries
        ages = [a.age for a in edge_cases]
        assert 13 in ages, "Should include minimum age"
        assert 100 in ages, "Should include maximum age"


class TestTestDataGenerator:
    """Test the main TestDataGenerator utility (AC #4)."""

    def test_generate_realistic_test_scenario(self):
        """
        Test that generating a realistic test scenario creates valid data.

        Acceptance Criteria: Data should be valid and representative of real user input
        """
        generator = TestDataGenerator()
        scenario = generator.generate_realistic_scenario()

        # Should include multiple users
        assert "users" in scenario
        assert len(scenario["users"]) > 0

        # Should include assessments
        assert "assessments" in scenario
        assert len(scenario["assessments"]) > 0

        # Verify all data is valid
        for user in scenario["users"]:
            assert user.email is not None
            assert user.is_active is not None

        for assessment in scenario["assessments"]:
            assert assessment.user is not None
            assert assessment.sport in ["soccer", "cricket"]

    def test_generate_user_with_assessment(self):
        """
        Test that generating a complete user with assessment works.

        Acceptance Criteria: Data should be valid and representative of real user input
        """
        generator = TestDataGenerator()
        user, assessment = generator.generate_user_with_assessment()

        # Verify user and assessment are linked
        assert assessment.user.id == user.id

        # Verify both are valid
        assert user.email is not None
        assert assessment.sport is not None

    def test_generate_complete_onboarding_scenario(self):
        """
        Test that generating a complete onboarding scenario works.

        Acceptance Criteria: Data should be valid and representative of real user input
        """
        generator = TestDataGenerator()
        scenario = generator.generate_complete_onboarding_scenario()

        # Should include different user types
        assert "beginner_user" in scenario
        assert "intermediate_user" in scenario
        assert "advanced_user" in scenario
        assert "injured_user" in scenario

        # Verify assessments are properly linked
        assert scenario["beginner_assessment"].user == scenario["beginner_user"]
        assert scenario["intermediate_assessment"].user == scenario["intermediate_user"]
        assert scenario["advanced_assessment"].user == scenario["advanced_user"]
        assert scenario["injured_assessment"].user == scenario["injured_user"]

    def test_generate_bulk_test_data(self):
        """
        Test that generating bulk test data creates the requested amount.

        Acceptance Criteria: Data should be valid and representative of real user input
        """
        generator = TestDataGenerator()
        data = generator.generate_bulk_test_data(user_count=10, assessment_count=8)

        assert len(data["users"]) == 10
        assert len(data["assessments"]) == 8

        # Verify all data is valid
        for user in data["users"]:
            assert user.email is not None

        for assessment in data["assessments"]:
            assert assessment.sport in ["soccer", "cricket"]

    def test_generated_data_is_representative(self):
        """
        Test that generated data is representative of real user input.

        Acceptance Criteria: Data should be representative of real user input
        """
        generator = TestDataGenerator()
        data = generator.generate_bulk_test_data(user_count=20, assessment_count=20)

        # Check for realistic distribution of sports
        sports = [a.sport for a in data["assessments"]]
        soccer_count = sports.count("soccer")
        cricket_count = sports.count("cricket")

        # Should have a mix of both sports (not all one type)
        assert soccer_count > 0, "Should have some soccer assessments"
        assert cricket_count > 0, "Should have some cricket assessments"

        # Check for realistic age distribution
        ages = [a.age for a in data["assessments"]]
        assert min(ages) >= 13, "All ages should be valid"
        assert max(ages) <= 100, "All ages should be valid"

        # Should have variety in experience levels
        levels = [a.experience_level for a in data["assessments"]]
        unique_levels = set(levels)
        assert len(unique_levels) > 1, "Should have varied experience levels"


class TestDataValidation:
    """Test that all generated data is valid (AC #4)."""

    def test_generated_users_pass_validation(self):
        """
        Test that all generated users pass Django model validation.

        Acceptance Criteria: Generated data should be valid
        """
        generator = UserDataGenerator()
        users = generator.generate_users(count=10)

        for user in users:
            # Should not raise ValidationError
            user.full_clean()

    def test_generated_assessments_pass_validation(self):
        """
        Test that all generated assessments pass Django model validation.

        Acceptance Criteria: Generated data should be valid
        """
        generator = AssessmentDataGenerator()
        assessments = generator.generate_assessments(count=10)

        for assessment in assessments:
            # Should not raise ValidationError
            assessment.full_clean()

    def test_edge_case_assessments_pass_validation(self):
        """
        Test that edge case assessments pass Django model validation.

        Acceptance Criteria: Generated data should be valid
        """
        generator = EdgeCaseDataGenerator()
        edge_cases = generator.generate_comprehensive_edge_cases()

        for assessment in edge_cases:
            # Should not raise ValidationError
            assessment.full_clean()

    def test_generated_data_can_be_saved_to_database(self):
        """
        Test that generated data can be saved to the database.

        Acceptance Criteria: Generated data should be valid
        """
        generator = TestDataGenerator()
        user, assessment = generator.generate_user_with_assessment()

        # Should be able to save without errors
        user.save()
        assessment.save()

        # Verify it was saved
        assert User.objects.filter(id=user.id).exists()
        assert Assessment.objects.filter(id=assessment.id).exists()


class TestDataGeneratorUtils:
    """Test utility methods of the data generators."""

    def test_generate_assessment_dict_for_api_testing(self):
        """
        Test generating assessment data as dictionary for API testing.

        Acceptance Criteria: Data should be representative of real user input
        """
        generator = AssessmentDataGenerator()
        assessment_dict = generator.generate_assessment_dict()

        # Verify it's a dictionary with required fields
        assert isinstance(assessment_dict, dict)
        assert "sport" in assessment_dict
        assert "age" in assessment_dict
        assert "experience_level" in assessment_dict
        assert "training_days" in assessment_dict
        assert "injuries" in assessment_dict
        assert "equipment" in assessment_dict

        # Verify values are valid
        assert assessment_dict["sport"] in ["soccer", "cricket"]
        assert 13 <= assessment_dict["age"] <= 100

    def test_generate_user_credentials_for_authentication_testing(self):
        """
        Test generating user with credentials for authentication tests.

        Acceptance Criteria: Data should be representative of real user input
        """
        generator = UserDataGenerator()
        user, password = generator.generate_user_with_credentials()

        # Verify password is returned
        assert password is not None
        assert len(password) > 0

        # Verify user can authenticate with password
        assert user.check_password(password) is True
