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

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker()
User = get_user_model()


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
        factory.random.reseed_random("test-seed")
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
