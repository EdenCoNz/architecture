"""
Test data factories using factory-boy.

This module provides factories for creating test data in a consistent, maintainable way.
Factories follow the Factory Boy pattern and provide:
- Consistent test data generation
- Customizable attributes
- Automatic handling of relationships
- Faker integration for realistic data

Usage Examples:
    # Basic usage
    user = UserFactory()

    # Custom attributes
    user = UserFactory(email='custom@example.com')

    # Create multiple instances
    users = UserFactory.create_batch(5)

    # Build without saving to database
    user = UserFactory.build()
"""

import random

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker()
User = get_user_model()

# Import assessment models - wrapped in try/except for test discovery
try:
    from apps.assessments.models import Assessment
except (ImportError, RuntimeError):
    Assessment = None  # type: ignore[assignment,misc]


class UserFactory(DjangoModelFactory):
    """
    Factory for creating User instances.

    Default values:
    - email: Unique email address using sequence
    - password: 'testpass123' (hashed automatically)
    - first_name: Random first name
    - last_name: Random last name
    - is_active: True
    - is_staff: False
    - is_superuser: False

    Examples:
        # Create regular user
        user = UserFactory()

        # Create admin user
        admin = UserFactory(is_staff=True, is_superuser=True)

        # Create inactive user
        inactive_user = UserFactory(is_active=False)

        # Create with specific email
        user = UserFactory(email='specific@example.com')
    """

    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """
        Set the password after creating the user.

        If a password is provided via extracted, use it.
        Otherwise, use default password 'testpass123'.
        """
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password("testpass123")

        if create:
            self.save()


class AdminUserFactory(UserFactory):
    """
    Factory for creating admin/superuser instances.

    Inherits from UserFactory and sets staff/superuser flags.

    Examples:
        # Create admin user
        admin = AdminUserFactory()

        # Create admin with specific email
        admin = AdminUserFactory(email='admin@example.com')
    """

    is_staff = True
    is_superuser = True
    email = factory.Sequence(lambda n: f"admin{n}@example.com")


class InactiveUserFactory(UserFactory):
    """
    Factory for creating inactive user instances.

    Useful for testing authentication and permission logic.

    Examples:
        # Create inactive user
        user = InactiveUserFactory()
    """

    is_active = False
    email = factory.Sequence(lambda n: f"inactive{n}@example.com")


# ==============================================================================
# Assessment Factories
# ==============================================================================


class AssessmentFactory(DjangoModelFactory):
    """
    Factory for creating Assessment instances.

    Default values:
    - user: Created via UserFactory (unique)
    - sport: Random choice between soccer/cricket
    - age: Random age between 18-65
    - experience_level: Random choice (beginner/intermediate/advanced)
    - training_days: Random choice (2-3, 4-5, 6-7)
    - injuries: Default "no"
    - equipment: Random choice (no_equipment/basic_equipment/full_gym)

    Examples:
        # Create assessment with default values
        assessment = AssessmentFactory()

        # Create soccer assessment for existing user
        assessment = AssessmentFactory(user=user, sport='soccer')

        # Create beginner assessment with no equipment
        assessment = AssessmentFactory(
            experience_level='beginner',
            equipment='no_equipment'
        )

        # Create multiple assessments
        assessments = AssessmentFactory.create_batch(5)
    """

    class Meta:
        model = "assessments.Assessment"
        django_get_or_create = ("user",)

    # User relationship - creates a unique user for each assessment
    user = factory.SubFactory(UserFactory)

    # Sport selection - random choice
    sport = factory.LazyFunction(lambda: random.choice(["soccer", "cricket"]))

    # Age with realistic distribution
    age = factory.LazyFunction(lambda: random.randint(18, 65))

    # Experience level - random choice
    experience_level = factory.LazyFunction(
        lambda: random.choice(["beginner", "intermediate", "advanced"])
    )

    # Training days - random choice
    training_days = factory.LazyFunction(lambda: random.choice(["2-3", "4-5", "6-7"]))

    # Injury history - default to no injuries
    injuries = "no"

    # Equipment - random choice
    equipment = factory.LazyFunction(
        lambda: random.choice(["no_equipment", "basic_equipment", "full_gym"])
    )


class FootballAssessmentFactory(AssessmentFactory):
    """
    Factory for creating soccer-focused assessments.

    Note: Named 'Football' for legacy reasons but creates assessments with sport="soccer".
    This aligns with the internal identifier change from "football" to "soccer".

    Examples:
        # Create soccer assessment
        assessment = FootballAssessmentFactory()
        assert assessment.sport == "soccer"
    """

    sport = "soccer"


class CricketAssessmentFactory(AssessmentFactory):
    """
    Factory for creating cricket-focused assessments.

    Examples:
        # Create cricket assessment
        assessment = CricketAssessmentFactory()
    """

    sport = "cricket"


class BeginnerAssessmentFactory(AssessmentFactory):
    """
    Factory for creating beginner-level assessments.

    Realistic defaults for beginners:
    - Age: 16-30
    - Experience: Beginner
    - Training: 2-3 days per week
    - Equipment: No equipment or basic equipment

    Examples:
        # Create beginner assessment
        assessment = BeginnerAssessmentFactory()
    """

    age = factory.LazyFunction(lambda: random.randint(16, 30))
    experience_level = "beginner"
    training_days = "2-3"
    equipment = factory.LazyFunction(lambda: random.choice(["no_equipment", "basic_equipment"]))


class AdvancedAssessmentFactory(AssessmentFactory):
    """
    Factory for creating advanced-level assessments.

    Realistic defaults for advanced users:
    - Age: 20-45
    - Experience: Advanced
    - Training: 4-5 or 6-7 days per week
    - Equipment: Basic equipment or full gym

    Examples:
        # Create advanced assessment
        assessment = AdvancedAssessmentFactory()
    """

    age = factory.LazyFunction(lambda: random.randint(20, 45))
    experience_level = "advanced"
    training_days = factory.LazyFunction(lambda: random.choice(["4-5", "6-7"]))
    equipment = factory.LazyFunction(lambda: random.choice(["basic_equipment", "full_gym"]))


class InjuredAssessmentFactory(AssessmentFactory):
    """
    Factory for creating assessments with injury history.

    Examples:
        # Create assessment with injury history
        assessment = InjuredAssessmentFactory()
    """

    injuries = "yes"


# Test Data Helpers
class TestDataBuilder:
    """
    Helper class for building complex test scenarios.

    This class provides methods for creating common test data patterns
    and relationships needed across multiple tests.

    Examples:
        # Create a test scenario with multiple users
        builder = TestDataBuilder()
        users = builder.create_users_batch(5)

        # Create authenticated test scenario
        scenario = builder.create_authenticated_scenario()
    """

    @staticmethod
    def create_users_batch(count=5, **kwargs):
        """
        Create a batch of users.

        Args:
            count (int): Number of users to create
            **kwargs: Additional attributes to apply to all users

        Returns:
            list: List of User instances

        Examples:
            # Create 10 active users
            users = TestDataBuilder.create_users_batch(10, is_active=True)
        """
        return UserFactory.create_batch(count, **kwargs)

    @staticmethod
    def create_authenticated_scenario():
        """
        Create a complete authentication test scenario.

        Returns:
            dict: Dictionary containing:
                - user: Regular user
                - admin: Admin user
                - inactive_user: Inactive user

        Examples:
            scenario = TestDataBuilder.create_authenticated_scenario()
            regular_user = scenario['user']
            admin_user = scenario['admin']
        """
        return {
            "user": UserFactory(),
            "admin": AdminUserFactory(),
            "inactive_user": InactiveUserFactory(),
        }

    @staticmethod
    def create_user_with_credentials(email=None, password="testpass123"):
        """
        Create a user with known credentials for login testing.

        Args:
            email (str): Email address (generated if not provided)
            password (str): Password to set

        Returns:
            tuple: (user, password) for use in login tests

        Examples:
            user, password = (
                TestDataBuilder.create_user_with_credentials()
            )
            # Use for login testing
        """
        email = email or fake.email()
        user = UserFactory(email=email, password=password)
        return user, password

    @staticmethod
    def create_assessment_batch(count=5, **kwargs):
        """
        Create a batch of assessments.

        Args:
            count (int): Number of assessments to create
            **kwargs: Additional attributes to apply to all assessments

        Returns:
            list: List of Assessment instances

        Examples:
            # Create 10 soccer assessments
            assessments = TestDataBuilder.create_assessment_batch(
                10, sport='soccer'
            )
        """
        return AssessmentFactory.create_batch(count, **kwargs)

    @staticmethod
    def create_user_with_assessment(sport="soccer", experience_level="beginner", **kwargs):
        """
        Create a user with an associated assessment.

        Args:
            sport (str): Sport type (soccer/cricket)
            experience_level (str): Experience level
            **kwargs: Additional assessment attributes

        Returns:
            tuple: (user, assessment)

        Examples:
            user, assessment = (
                TestDataBuilder.create_user_with_assessment(
                    sport='soccer',
                    experience_level='advanced'
                )
            )
        """
        user = UserFactory()
        assessment = AssessmentFactory(
            user=user, sport=sport, experience_level=experience_level, **kwargs
        )
        return user, assessment

    @staticmethod
    def create_complete_onboarding_scenario():
        """
        Create a complete onboarding test scenario.

        Returns:
            dict: Dictionary containing:
                - beginner_user: User with beginner assessment
                - intermediate_user: User with intermediate assessment
                - advanced_user: User with advanced assessment
                - injured_user: User with injury history

        Examples:
            scenario = TestDataBuilder.create_complete_onboarding_scenario()
            beginner = scenario['beginner_user']
            advanced = scenario['advanced_user']
        """
        beginner_user = UserFactory()
        beginner_assessment = BeginnerAssessmentFactory(user=beginner_user)

        intermediate_user = UserFactory()
        intermediate_assessment = AssessmentFactory(
            user=intermediate_user, experience_level="intermediate"
        )

        advanced_user = UserFactory()
        advanced_assessment = AdvancedAssessmentFactory(user=advanced_user)

        injured_user = UserFactory()
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


# Test Fixtures Helper
class FixtureHelper:
    """
    Helper class for common test fixture operations.

    Provides utilities for setting up and tearing down test data,
    resetting sequences, and managing test database state.
    """

    @staticmethod
    def reset_sequences():
        """
        Reset all factory sequences to start from 1.

        Useful for ensuring consistent test data across test runs.

        Examples:
            FixtureHelper.reset_sequences()
        """
        # Reset sequences for all factories
        factory.Faker._get_faker().seed_instance(0)
        # Note: Individual factory sequences are automatically reset by
        # pytest-django between tests, so explicit reset is typically not
        # needed

    @staticmethod
    def cleanup_users():
        """
        Remove all users from the test database.

        Examples:
            FixtureHelper.cleanup_users()
        """
        User.objects.all().delete()

    @staticmethod
    def cleanup_assessments():
        """
        Remove all assessments from the test database.

        Examples:
            FixtureHelper.cleanup_assessments()
        """
        if Assessment is not None:
            Assessment.objects.all().delete()

    @staticmethod
    def cleanup_all():
        """
        Remove all test data from the database.

        Cleans up users, assessments, and all related data.

        Examples:
            FixtureHelper.cleanup_all()
        """
        # Order matters: delete assessments before users due to foreign keys
        FixtureHelper.cleanup_assessments()
        FixtureHelper.cleanup_users()


# Usage Documentation for Test Files
"""
How to use factories in your tests:

1. Unit Tests:
   ```python
   from tests.factories import UserFactory

   def test_user_creation():
       user = UserFactory()
       assert user.email is not None
   ```

2. Integration Tests:
   ```python
   from tests.factories import UserFactory, TestDataBuilder

   def test_user_list_endpoint(api_client):
       # Create test users
       users = UserFactory.create_batch(5)

       # Test endpoint
       response = api_client.get('/api/v1/users/')
       assert len(response.data) == 5
   ```

3. With pytest fixtures:
   ```python
   import pytest
   from tests.factories import UserFactory

   @pytest.fixture
   def sample_user():
       return UserFactory()

   def test_with_fixture(sample_user):
       assert sample_user.is_active is True
   ```

4. Complex scenarios:
   ```python
   from tests.factories import TestDataBuilder

   def test_authentication_flow():
       scenario = TestDataBuilder.create_authenticated_scenario()

       # Test with regular user
       assert not scenario['user'].is_staff

       # Test with admin
       assert scenario['admin'].is_staff

       # Test with inactive user
       assert not scenario['inactive_user'].is_active
   ```

5. Custom attributes:
   ```python
   from tests.factories import UserFactory

   def test_custom_user():
       user = UserFactory(
           email='custom@test.com',
           first_name='John',
           last_name='Doe'
       )
       assert user.email == 'custom@test.com'
       assert user.get_full_name() == 'John Doe'
   ```
"""
