"""
Test Data Generation Utilities (Story 13.14).

This module provides utilities to generate realistic test data for users and assessments.
It supports generating:
- User accounts with realistic profile data
- Valid assessment submissions with varied attributes
- Boundary values and edge cases
- Bulk test data for performance testing

Usage Examples:
    # Generate a single user
    user_gen = UserDataGenerator()
    user = user_gen.generate_user()

    # Generate multiple assessments with variation
    assessment_gen = AssessmentDataGenerator()
    assessments = assessment_gen.generate_assessments(count=10)

    # Generate edge cases
    edge_gen = EdgeCaseDataGenerator()
    min_age = edge_gen.generate_minimum_age_assessment()
    max_age = edge_gen.generate_maximum_age_assessment()

    # Generate complete test scenario
    test_gen = TestDataGenerator()
    scenario = test_gen.generate_realistic_scenario()
"""

import random
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model

from apps.assessments.models import Assessment

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser as User
else:
    User = get_user_model()
from tests.factories import (
    AdminUserFactory,
    AdvancedAssessmentFactory,
    AssessmentFactory,
    BeginnerAssessmentFactory,
    CricketAssessmentFactory,
    FootballAssessmentFactory,
    InactiveUserFactory,
    InjuredAssessmentFactory,
    UserFactory,
)


class UserDataGenerator:
    """
    Generator for creating realistic user test data.

    This class provides methods to create users with varied profiles,
    including regular users, admin users, and inactive users.
    """

    def generate_user(self, **kwargs: Any) -> User:
        """
        Generate a single user with realistic profile data.

        Args:
            **kwargs: Optional attributes to override defaults

        Returns:
            User instance with realistic profile data

        Examples:
            >>> generator = UserDataGenerator()
            >>> user = generator.generate_user()
            >>> user = generator.generate_user(email='custom@example.com')
        """
        return UserFactory(**kwargs)

    def generate_users(self, count: int = 5, **kwargs: Any) -> List[User]:
        """
        Generate multiple users with realistic profile data.

        Args:
            count: Number of users to create
            **kwargs: Optional attributes to apply to all users

        Returns:
            List of User instances

        Examples:
            >>> generator = UserDataGenerator()
            >>> users = generator.generate_users(count=10)
        """
        return UserFactory.create_batch(count, **kwargs)

    def generate_admin_user(self, **kwargs: Any) -> User:
        """
        Generate an admin user with realistic profile data.

        Args:
            **kwargs: Optional attributes to override defaults

        Returns:
            User instance with admin privileges

        Examples:
            >>> generator = UserDataGenerator()
            >>> admin = generator.generate_admin_user()
        """
        return AdminUserFactory(**kwargs)

    def generate_inactive_user(self, **kwargs: Any) -> User:
        """
        Generate an inactive user.

        Args:
            **kwargs: Optional attributes to override defaults

        Returns:
            Inactive User instance

        Examples:
            >>> generator = UserDataGenerator()
            >>> inactive = generator.generate_inactive_user()
        """
        return InactiveUserFactory(**kwargs)

    def generate_user_with_credentials(
        self, email: Optional[str] = None, password: str = "TestPass123!"
    ) -> Tuple[User, str]:
        """
        Generate a user with known credentials for authentication testing.

        Args:
            email: Optional email address
            password: Password to set (default: TestPass123!)

        Returns:
            Tuple of (User instance, password string)

        Examples:
            >>> generator = UserDataGenerator()
            >>> user, password = generator.generate_user_with_credentials()
            >>> # Use for login testing
        """
        kwargs = {"password": password}
        if email:
            kwargs["email"] = email

        user = UserFactory(**kwargs)
        return user, password


class AssessmentDataGenerator:
    """
    Generator for creating realistic assessment test data.

    This class provides methods to create assessments with varied attributes
    including different sports, experience levels, training frequencies, and equipment.
    """

    def generate_assessment(self, **kwargs: Any) -> Assessment:
        """
        Generate a single assessment with realistic data.

        Args:
            **kwargs: Optional attributes to override defaults

        Returns:
            Assessment instance with realistic data

        Examples:
            >>> generator = AssessmentDataGenerator()
            >>> assessment = generator.generate_assessment()
            >>> assessment = generator.generate_assessment(sport='cricket')
        """
        return AssessmentFactory(**kwargs)

    def generate_assessments(self, count: int = 5, **kwargs: Any) -> List[Assessment]:
        """
        Generate multiple assessments with varied attributes.

        Creates assessments with variation in sports, experience levels,
        training days, and equipment to simulate realistic test scenarios.

        Args:
            count: Number of assessments to create
            **kwargs: Optional attributes to apply to all assessments

        Returns:
            List of Assessment instances with varied attributes

        Examples:
            >>> generator = AssessmentDataGenerator()
            >>> assessments = generator.generate_assessments(count=10)
        """
        return AssessmentFactory.create_batch(count, **kwargs)

    def generate_football_assessment(self, **kwargs: Any) -> Assessment:
        """
        Generate an assessment for football sport.

        Args:
            **kwargs: Optional attributes to override defaults

        Returns:
            Assessment instance with sport set to football

        Examples:
            >>> generator = AssessmentDataGenerator()
            >>> assessment = generator.generate_football_assessment()
        """
        return FootballAssessmentFactory(**kwargs)

    def generate_cricket_assessment(self, **kwargs: Any) -> Assessment:
        """
        Generate an assessment for cricket sport.

        Args:
            **kwargs: Optional attributes to override defaults

        Returns:
            Assessment instance with sport set to cricket

        Examples:
            >>> generator = AssessmentDataGenerator()
            >>> assessment = generator.generate_cricket_assessment()
        """
        return CricketAssessmentFactory(**kwargs)

    def generate_beginner_assessment(self, **kwargs: Any) -> Assessment:
        """
        Generate a beginner-level assessment with appropriate characteristics.

        Args:
            **kwargs: Optional attributes to override defaults

        Returns:
            Assessment instance with beginner experience level

        Examples:
            >>> generator = AssessmentDataGenerator()
            >>> assessment = generator.generate_beginner_assessment()
        """
        return BeginnerAssessmentFactory(**kwargs)

    def generate_advanced_assessment(self, **kwargs: Any) -> Assessment:
        """
        Generate an advanced-level assessment with appropriate characteristics.

        Args:
            **kwargs: Optional attributes to override defaults

        Returns:
            Assessment instance with advanced experience level

        Examples:
            >>> generator = AssessmentDataGenerator()
            >>> assessment = generator.generate_advanced_assessment()
        """
        return AdvancedAssessmentFactory(**kwargs)

    def generate_assessment_with_injuries(self, **kwargs: Any) -> Assessment:
        """
        Generate an assessment with injury history.

        Args:
            **kwargs: Optional attributes to override defaults

        Returns:
            Assessment instance with injuries='yes'

        Examples:
            >>> generator = AssessmentDataGenerator()
            >>> assessment = generator.generate_assessment_with_injuries()
        """
        return InjuredAssessmentFactory(**kwargs)

    def generate_assessment_dict(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Generate assessment data as a dictionary for API testing.

        Args:
            **kwargs: Optional attributes to override defaults

        Returns:
            Dictionary with assessment data suitable for API requests

        Examples:
            >>> generator = AssessmentDataGenerator()
            >>> data = generator.generate_assessment_dict()
            >>> # Use in API tests: client.post('/api/assessments/', json=data)
        """
        # Build with defaults
        data = {
            "sport": kwargs.get("sport", random.choice(["football", "cricket"])),
            "age": kwargs.get("age", random.randint(18, 65)),
            "experience_level": kwargs.get(
                "experience_level",
                random.choice(["beginner", "intermediate", "advanced"]),
            ),
            "training_days": kwargs.get("training_days", random.choice(["2-3", "4-5", "6-7"])),
            "injuries": kwargs.get("injuries", "no"),
            "equipment": kwargs.get(
                "equipment",
                random.choice(["no_equipment", "basic_equipment", "full_gym"]),
            ),
        }

        # Override with any additional kwargs
        for key, value in kwargs.items():
            if key in data:
                data[key] = value

        return data


class EdgeCaseDataGenerator:
    """
    Generator for creating edge case and boundary value test data.

    This class provides methods to create assessments with boundary values
    such as minimum/maximum ages and all possible combinations of enum values.
    """

    def generate_minimum_age_assessment(self, **kwargs: Any) -> Assessment:
        """
        Generate an assessment with the minimum valid age (13).

        Args:
            **kwargs: Optional attributes to override defaults

        Returns:
            Assessment instance with age=13

        Examples:
            >>> generator = EdgeCaseDataGenerator()
            >>> assessment = generator.generate_minimum_age_assessment()
            >>> assert assessment.age == 13
        """
        kwargs["age"] = 13
        return AssessmentFactory(**kwargs)

    def generate_maximum_age_assessment(self, **kwargs: Any) -> Assessment:
        """
        Generate an assessment with the maximum valid age (100).

        Args:
            **kwargs: Optional attributes to override defaults

        Returns:
            Assessment instance with age=100

        Examples:
            >>> generator = EdgeCaseDataGenerator()
            >>> assessment = generator.generate_maximum_age_assessment()
            >>> assert assessment.age == 100
        """
        kwargs["age"] = 100
        return AssessmentFactory(**kwargs)

    def generate_all_equipment_combinations(self) -> List[Assessment]:
        """
        Generate assessments with all equipment types.

        Returns:
            List of Assessment instances, one for each equipment type

        Examples:
            >>> generator = EdgeCaseDataGenerator()
            >>> assessments = generator.generate_all_equipment_combinations()
            >>> assert len(assessments) == 3
        """
        equipment_types = ["no_equipment", "basic_equipment", "full_gym"]
        assessments = []

        for equipment in equipment_types:
            assessment = AssessmentFactory(equipment=equipment)
            assessments.append(assessment)

        return assessments

    def generate_all_sport_combinations(self) -> List[Assessment]:
        """
        Generate assessments with all sport types.

        Returns:
            List of Assessment instances, one for each sport

        Examples:
            >>> generator = EdgeCaseDataGenerator()
            >>> assessments = generator.generate_all_sport_combinations()
            >>> assert len(assessments) == 2
        """
        sports = ["football", "cricket"]
        assessments = []

        for sport in sports:
            assessment = AssessmentFactory(sport=sport)
            assessments.append(assessment)

        return assessments

    def generate_all_experience_level_combinations(self) -> List[Assessment]:
        """
        Generate assessments with all experience levels.

        Returns:
            List of Assessment instances, one for each experience level

        Examples:
            >>> generator = EdgeCaseDataGenerator()
            >>> assessments = generator.generate_all_experience_level_combinations()
            >>> assert len(assessments) == 3
        """
        levels = ["beginner", "intermediate", "advanced"]
        assessments = []

        for level in levels:
            assessment = AssessmentFactory(experience_level=level)
            assessments.append(assessment)

        return assessments

    def generate_all_training_days_combinations(self) -> List[Assessment]:
        """
        Generate assessments with all training day options.

        Returns:
            List of Assessment instances, one for each training days option

        Examples:
            >>> generator = EdgeCaseDataGenerator()
            >>> assessments = generator.generate_all_training_days_combinations()
            >>> assert len(assessments) == 3
        """
        training_options = ["2-3", "4-5", "6-7"]
        assessments = []

        for training_days in training_options:
            assessment = AssessmentFactory(training_days=training_days)
            assessments.append(assessment)

        return assessments

    def generate_comprehensive_edge_cases(self) -> List[Assessment]:
        """
        Generate a comprehensive set of edge case assessments.

        Creates assessments covering:
        - Minimum age boundary
        - Maximum age boundary
        - All equipment types
        - All sports
        - All experience levels
        - All training day options

        Returns:
            List of Assessment instances covering all edge cases

        Examples:
            >>> generator = EdgeCaseDataGenerator()
            >>> edge_cases = generator.generate_comprehensive_edge_cases()
            >>> assert len(edge_cases) > 5
        """
        edge_cases = []

        # Age boundaries
        edge_cases.append(self.generate_minimum_age_assessment())
        edge_cases.append(self.generate_maximum_age_assessment())

        # All equipment types
        edge_cases.extend(self.generate_all_equipment_combinations())

        # All sports
        edge_cases.extend(self.generate_all_sport_combinations())

        # All experience levels
        edge_cases.extend(self.generate_all_experience_level_combinations())

        # All training days
        edge_cases.extend(self.generate_all_training_days_combinations())

        return edge_cases


class TestDataGenerator:
    """
    Main test data generator utility.

    This class provides high-level methods to generate complete test scenarios
    including users, assessments, and realistic data distributions.
    """

    def __init__(self):
        """Initialize the test data generator with component generators."""
        self.user_generator = UserDataGenerator()
        self.assessment_generator = AssessmentDataGenerator()
        self.edge_case_generator = EdgeCaseDataGenerator()

    def generate_realistic_scenario(
        self, user_count: int = 5, assessment_count: int = 5
    ) -> Dict[str, List[Any]]:
        """
        Generate a realistic test scenario with users and assessments.

        Args:
            user_count: Number of users to create
            assessment_count: Number of assessments to create

        Returns:
            Dictionary containing 'users' and 'assessments' lists

        Examples:
            >>> generator = TestDataGenerator()
            >>> scenario = generator.generate_realistic_scenario()
            >>> users = scenario['users']
            >>> assessments = scenario['assessments']
        """
        users = self.user_generator.generate_users(count=user_count)
        assessments = self.assessment_generator.generate_assessments(count=assessment_count)

        return {"users": users, "assessments": assessments}

    def generate_user_with_assessment(
        self,
        sport: Optional[str] = None,
        experience_level: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[User, Assessment]:
        """
        Generate a user with an associated assessment.

        Args:
            sport: Optional sport type
            experience_level: Optional experience level
            **kwargs: Additional assessment attributes

        Returns:
            Tuple of (User instance, Assessment instance)

        Examples:
            >>> generator = TestDataGenerator()
            >>> user, assessment = generator.generate_user_with_assessment(
            ...     sport='football',
            ...     experience_level='beginner'
            ... )
        """
        user = self.user_generator.generate_user()

        assessment_kwargs = {"user": user}
        if sport:
            assessment_kwargs["sport"] = sport
        if experience_level:
            assessment_kwargs["experience_level"] = experience_level
        assessment_kwargs.update(kwargs)

        assessment = self.assessment_generator.generate_assessment(**assessment_kwargs)

        return user, assessment

    def generate_complete_onboarding_scenario(self) -> Dict[str, Any]:
        """
        Generate a complete onboarding test scenario.

        Creates users with different experience levels and characteristics:
        - Beginner user with beginner assessment
        - Intermediate user with intermediate assessment
        - Advanced user with advanced assessment
        - User with injury history

        Returns:
            Dictionary containing users and their assessments

        Examples:
            >>> generator = TestDataGenerator()
            >>> scenario = generator.generate_complete_onboarding_scenario()
            >>> beginner = scenario['beginner_user']
            >>> advanced = scenario['advanced_user']
        """
        # Create beginner user
        beginner_user = self.user_generator.generate_user()
        beginner_assessment = BeginnerAssessmentFactory(user=beginner_user)

        # Create intermediate user
        intermediate_user = self.user_generator.generate_user()
        intermediate_assessment = AssessmentFactory(
            user=intermediate_user, experience_level="intermediate"
        )

        # Create advanced user
        advanced_user = self.user_generator.generate_user()
        advanced_assessment = AdvancedAssessmentFactory(user=advanced_user)

        # Create injured user
        injured_user = self.user_generator.generate_user()
        injured_assessment = InjuredAssessmentFactory(user=injured_user)

        return {
            "beginner_user": beginner_user,
            "beginner_assessment": beginner_assessment,
            "intermediate_user": intermediate_user,
            "intermediate_assessment": intermediate_assessment,
            "advanced_user": advanced_user,
            "advanced_assessment": advanced_assessment,
            "injured_user": injured_user,
            "injured_assessment": injured_assessment,
        }

    def generate_bulk_test_data(
        self, user_count: int = 10, assessment_count: int = 10
    ) -> Dict[str, List[Any]]:
        """
        Generate bulk test data for performance and load testing.

        Args:
            user_count: Number of users to create
            assessment_count: Number of assessments to create

        Returns:
            Dictionary containing 'users' and 'assessments' lists

        Examples:
            >>> generator = TestDataGenerator()
            >>> data = generator.generate_bulk_test_data(
            ...     user_count=100,
            ...     assessment_count=80
            ... )
        """
        users = self.user_generator.generate_users(count=user_count)
        assessments = self.assessment_generator.generate_assessments(count=assessment_count)

        return {"users": users, "assessments": assessments}
