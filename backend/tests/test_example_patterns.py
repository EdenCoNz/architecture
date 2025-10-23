"""
Example test file demonstrating all testing patterns.

This file serves as a reference for writing tests in this project.
It demonstrates:
- Unit tests with factories
- Integration tests with API client
- Mocking external dependencies
- Using test utilities and helpers
- Test data management with factories
- Different assertion patterns
- Fixture usage

Use this file as a template when writing new tests.
"""

from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import AdminUserFactory, InactiveUserFactory, TestDataBuilder, UserFactory

# Import test utilities
from tests.utils import APITestHelper, AssertionHelper, AuthenticationTestHelper, DatabaseTestHelper

User = get_user_model()


# ==============================================================================
# UNIT TESTS
# ==============================================================================


@pytest.mark.unit
class TestUserModelExamples:
    """
    Examples of unit tests for models.

    Unit tests focus on testing individual components in isolation.
    They should be fast and not require database access when possible.
    """

    @pytest.mark.django_db
    def test_user_creation_with_factory(self):
        """
        Example: Creating a user with factory.

        This demonstrates the simplest form of factory usage.
        """
        # Create user with default factory values
        user = UserFactory()

        # Assert basic properties
        assert user.email is not None
        assert user.is_active is True
        assert user.check_password("testpass123")

    @pytest.mark.django_db
    def test_user_creation_with_custom_attributes(self):
        """
        Example: Creating a user with custom attributes.

        Factories allow overriding default values for specific test needs.
        """
        # Create user with custom attributes
        user = UserFactory(email="custom@example.com", first_name="John", last_name="Doe")

        # Assert custom attributes
        assert user.email == "custom@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.get_full_name() == "John Doe"

    @pytest.mark.django_db
    def test_creating_multiple_users(self):
        """
        Example: Creating multiple users in a batch.

        Use create_batch when you need multiple test objects.
        """
        # Create 5 users at once
        users = UserFactory.create_batch(5)

        # Assert we got 5 users
        assert len(users) == 5

        # Assert each user has unique email
        emails = [user.email for user in users]
        assert len(emails) == len(set(emails))  # All unique

    @pytest.mark.django_db
    def test_using_specialized_factories(self):
        """
        Example: Using specialized factories.

        The project provides specialized factories for common scenarios.
        """
        # Create regular user
        regular_user = UserFactory()
        assert not regular_user.is_staff

        # Create admin user
        admin_user = AdminUserFactory()
        assert admin_user.is_staff
        assert admin_user.is_superuser

        # Create inactive user
        inactive_user = InactiveUserFactory()
        assert not inactive_user.is_active

    def test_pure_unit_test_without_database(self):
        """
        Example: Pure unit test without database.

        Some tests don't need database access at all.
        Use build() instead of create() to avoid database hits.
        """
        # Build user without saving to database
        user = UserFactory.build()

        # Test business logic that doesn't require database
        full_name = f"{user.first_name} {user.last_name}"
        assert full_name == user.get_full_name()

    @pytest.mark.django_db
    def test_using_database_test_helper(self):
        """
        Example: Using DatabaseTestHelper for assertions.

        DatabaseTestHelper provides convenient assertions for database operations.
        """
        # Create a user
        user = UserFactory(email="helper@example.com")

        # Assert object exists
        DatabaseTestHelper.assert_object_exists(User, email="helper@example.com")

        # Assert count
        DatabaseTestHelper.assert_count(User, 1, email="helper@example.com")

        # Get or fail
        retrieved_user = DatabaseTestHelper.get_or_fail(User, email="helper@example.com")
        assert retrieved_user.id == user.id


# ==============================================================================
# INTEGRATION TESTS
# ==============================================================================


@pytest.mark.integration
@pytest.mark.django_db
class TestAPIEndpointExamples:
    """
    Examples of integration tests for API endpoints.

    Integration tests verify that components work together correctly.
    They test the full request/response cycle.
    """

    @pytest.fixture
    def api_client(self):
        """Provide API client for tests."""
        return APIClient()

    @pytest.fixture
    def api_helper(self, api_client):
        """Provide API test helper."""
        return APITestHelper(api_client)

    @pytest.fixture
    def sample_user(self):
        """Provide a sample user for tests."""
        return UserFactory()

    def test_api_endpoint_with_helper(self, api_helper):
        """
        Example: Testing API endpoint with APITestHelper.

        APITestHelper provides convenient methods for API testing.
        """
        # Make GET request
        response = api_helper.get("/api/v1/health/")

        # Assert success
        api_helper.assert_success(response, 200)

        # Assert response has required keys
        api_helper.assert_has_keys(response.data, ["status", "timestamp"])

    def test_authenticated_endpoint(self, api_helper, sample_user):
        """
        Example: Testing authenticated endpoints.

        Shows how to authenticate and test protected endpoints.
        """
        # Authenticate as user
        access_token, refresh_token = api_helper.authenticate(sample_user)

        # Make authenticated request
        response = api_helper.get("/api/v1/auth/me/")

        # Assert success
        api_helper.assert_success(response, 200)

        # Assert response contains user data
        assert response.data["email"] == sample_user.email

        # Clear credentials
        api_helper.clear_credentials()

    def test_authentication_flow(self, api_client):
        """
        Example: Testing complete authentication flow.

        Demonstrates testing login, token usage, and logout.
        """
        # Create user with known credentials
        user, password = TestDataBuilder.create_user_with_credentials(
            email="flow@example.com", password="testpass123"
        )

        # Initialize helper
        auth_helper = AuthenticationTestHelper(api_client)

        # Test login
        tokens = auth_helper.login(user.email, password)
        assert "access" in tokens
        assert "refresh" in tokens

        # Test token refresh
        new_tokens = auth_helper.refresh_token(tokens["refresh"])
        assert "access" in new_tokens

        # Test logout
        response = auth_helper.logout(tokens["refresh"])
        assert response.status_code == status.HTTP_200_OK

    def test_creating_resource_via_api(self, api_helper, sample_user):
        """
        Example: Testing resource creation via API.

        Shows POST request testing and database verification.
        """
        # Authenticate
        api_helper.authenticate(sample_user)

        # Note: This is an example - adjust endpoint to your actual API
        # POST request to create resource
        payload = {"title": "Test Item", "description": "Test Description"}

        # This endpoint doesn't exist - it's just an example pattern
        # response = api_helper.post('/api/v1/items/', payload)
        # api_helper.assert_success(response, 201)

        # Verify in database
        # DatabaseTestHelper.assert_object_exists(Item, title='Test Item')


# ==============================================================================
# MOCKING EXAMPLES
# ==============================================================================


@pytest.mark.unit
class TestMockingExamples:
    """
    Examples of mocking external dependencies.

    Mocking allows testing in isolation without external dependencies.
    """

    @patch("apps.core.database.DatabaseHealthCheck.check")
    def test_mocking_database_health_check(self, mock_check):
        """
        Example: Mocking database health check.

        Shows how to mock external dependencies for isolated testing.
        """
        # Configure mock return value
        mock_check.return_value = {
            "status": "healthy",
            "database": "connected",
            "response_time_ms": 15.5,
        }

        # Create API client
        client = APIClient()

        # Make request (will use mocked health check)
        response = client.get("/api/v1/health/")

        # Assert mock was called
        assert mock_check.called

        # Assert response uses mocked data
        assert response.data["status"] == "healthy"

    @patch("django.core.mail.send_mail")
    def test_mocking_email_sending(self, mock_send_mail):
        """
        Example: Mocking email sending.

        Shows how to test email functionality without actually sending emails.
        """
        # Configure mock
        mock_send_mail.return_value = 1

        # Code that would send email
        from django.core.mail import send_mail

        result = send_mail("Test Subject", "Test Message", "from@example.com", ["to@example.com"])

        # Assert email was "sent"
        assert result == 1
        assert mock_send_mail.called

        # Assert called with correct arguments
        mock_send_mail.assert_called_once_with(
            "Test Subject", "Test Message", "from@example.com", ["to@example.com"]
        )


# ==============================================================================
# ASSERTION EXAMPLES
# ==============================================================================


@pytest.mark.unit
class TestAssertionExamples:
    """
    Examples of different assertion patterns.

    Shows various ways to assert conditions in tests.
    """

    def test_basic_assertions(self):
        """
        Example: Basic Python assertions.

        Standard assertion patterns.
        """
        user = UserFactory.build()

        # Equality
        assert user.is_active is True
        assert user.is_staff is False

        # String operations
        assert "@" in user.email
        assert user.email.endswith(".com")

        # Collections
        assert isinstance(user.email, str)

    def test_using_assertion_helpers(self):
        """
        Example: Using custom assertion helpers.

        Project provides specialized assertion helpers.
        """
        # Valid UUID assertion
        import uuid

        test_uuid = str(uuid.uuid4())
        AssertionHelper.assert_valid_uuid(test_uuid)

        # Valid timestamp assertion
        from datetime import datetime

        timestamp = datetime.now().isoformat()
        AssertionHelper.assert_valid_timestamp(timestamp)

        # Dictionary subset assertion
        full_dict = {"a": 1, "b": 2, "c": 3}
        subset = {"a": 1, "b": 2}
        AssertionHelper.assert_dict_subset(subset, full_dict)


# ==============================================================================
# FIXTURE EXAMPLES
# ==============================================================================


@pytest.mark.integration
@pytest.mark.django_db
class TestFixtureExamples:
    """
    Examples of using pytest fixtures.

    Fixtures provide reusable test setup and teardown.
    """

    @pytest.fixture
    def users(self):
        """
        Example: Fixture providing multiple users.

        Fixtures can create and return test data.
        """
        return UserFactory.create_batch(3)

    @pytest.fixture
    def admin(self):
        """Example: Fixture providing admin user."""
        return AdminUserFactory()

    @pytest.fixture
    def authenticated_client(self, api_client, users):
        """
        Example: Fixture providing authenticated client.

        Fixtures can use other fixtures and perform setup.
        """
        helper = APITestHelper(api_client)
        helper.authenticate(users[0])
        return api_client

    def test_using_fixtures(self, users, admin):
        """
        Example: Test using fixtures.

        Fixtures are automatically provided to test methods.
        """
        # Use fixture data
        assert len(users) == 3
        assert admin.is_staff is True

        # All fixtures are available
        for user in users:
            assert user.is_active is True

    def test_using_authenticated_client(self, authenticated_client):
        """
        Example: Test using authenticated client fixture.

        Shows how fixtures can provide ready-to-use clients.
        """
        # Client is already authenticated
        response = authenticated_client.get("/api/v1/auth/me/")
        assert response.status_code == status.HTTP_200_OK


# ==============================================================================
# PARAMETERIZED TESTS
# ==============================================================================


@pytest.mark.unit
class TestParameterizedExamples:
    """
    Examples of parameterized tests.

    Parameterized tests allow testing multiple scenarios with the same logic.
    """

    @pytest.mark.parametrize(
        "email,expected",
        [
            ("Test@Example.com", "Test@example.com"),
            ("USER@DOMAIN.COM", "USER@domain.com"),
            ("test@test.com", "test@test.com"),
        ],
    )
    def test_email_normalization(self, email, expected):
        """
        Example: Parameterized test for email normalization.

        One test method runs multiple times with different inputs.
        """
        # Normalize email (domain part only)
        normalized = email.split("@")[0] + "@" + email.split("@")[1].lower()
        assert normalized == expected

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "is_staff,is_superuser,expected_admin",
        [
            (False, False, False),
            (True, False, False),
            (False, True, False),
            (True, True, True),
        ],
    )
    def test_admin_status(self, is_staff, is_superuser, expected_admin):
        """
        Example: Parameterized test for admin status.

        Tests multiple combinations of user permissions.
        """
        user = UserFactory(is_staff=is_staff, is_superuser=is_superuser)

        # Only users with both flags should be considered full admins
        is_admin = user.is_staff and user.is_superuser
        assert is_admin == expected_admin


# ==============================================================================
# COMPLEX SCENARIO EXAMPLES
# ==============================================================================


@pytest.mark.integration
@pytest.mark.django_db
class TestComplexScenarioExamples:
    """
    Examples of testing complex scenarios.

    Shows how to test multi-step workflows and complex interactions.
    """

    def test_complete_user_lifecycle(self):
        """
        Example: Testing complete user lifecycle.

        Tests multiple operations in sequence to verify a complete workflow.
        """
        # 1. Create user via factory
        user = UserFactory(email="lifecycle@example.com")
        DatabaseTestHelper.assert_object_exists(User, email="lifecycle@example.com")

        # 2. Verify user can authenticate
        client = APIClient()
        auth_helper = AuthenticationTestHelper(client)
        tokens = auth_helper.login(user.email, "testpass123")
        assert "access" in tokens

        # 3. Update user profile (example pattern)
        api_helper = APITestHelper(client)
        api_helper.authenticate(user)

        # 4. Verify changes (example)
        user.refresh_from_db()
        assert user.is_active is True

        # 5. Deactivate user
        user.is_active = False
        user.save()

        # 6. Verify deactivated user cannot login
        # (This would fail in login endpoint validation)
        DatabaseTestHelper.assert_object_exists(
            User, email="lifecycle@example.com", is_active=False
        )

    def test_multiple_users_scenario(self):
        """
        Example: Testing scenario with multiple users.

        Uses TestDataBuilder for complex setups.
        """
        # Create scenario with multiple user types
        scenario = TestDataBuilder.create_authenticated_scenario()

        # Verify each user type
        assert scenario["user"].is_staff is False
        assert scenario["admin"].is_staff is True
        assert scenario["inactive_user"].is_active is False

        # Test interactions between users
        DatabaseTestHelper.assert_count(User, 3)


# ==============================================================================
# EDGE CASE AND ERROR HANDLING EXAMPLES
# ==============================================================================


@pytest.mark.unit
@pytest.mark.django_db
class TestEdgeCaseExamples:
    """
    Examples of testing edge cases and error handling.

    Important for robust testing.
    """

    def test_duplicate_email_raises_error(self):
        """
        Example: Testing that duplicate email raises error.

        Tests error conditions and validation.
        """
        email = "duplicate@example.com"

        # Create first user
        UserFactory(email=email)

        # Attempt to create second user with same email should fail
        from django.db import IntegrityError

        with pytest.raises(IntegrityError):
            UserFactory(email=email)

    def test_invalid_email_format(self):
        """
        Example: Testing invalid email handling.

        Tests validation logic.
        """
        # This would typically be tested at the serializer level
        invalid_emails = ["not-an-email", "@example.com", "test@", ""]

        for email in invalid_emails:
            # In a real scenario, you'd test serializer validation
            # For this example, we just check the format
            assert "@" not in email or "." not in email

    def test_missing_required_fields(self):
        """
        Example: Testing missing required fields.

        Verifies proper error handling for missing data.
        """
        # Attempt to create user without email
        from django.core.exceptions import ValidationError

        with pytest.raises(ValueError):
            User.objects.create_user("", "password")


"""
SUMMARY: Key Testing Patterns Demonstrated

1. Factory Usage:
   - UserFactory() for basic user creation
   - Factory.create_batch() for multiple objects
   - Factory.build() for non-persisted objects
   - Specialized factories (AdminUserFactory, InactiveUserFactory)

2. Test Helpers:
   - APITestHelper for API testing
   - AuthenticationTestHelper for auth flows
   - DatabaseTestHelper for database assertions
   - AssertionHelper for common assertions

3. Test Organization:
   - @pytest.mark.unit for unit tests
   - @pytest.mark.integration for integration tests
   - @pytest.mark.django_db for tests needing database
   - Clear docstrings explaining what each test does

4. Best Practices:
   - One assertion per test (when possible)
   - Clear test names describing what is tested
   - Arrange-Act-Assert pattern
   - Use fixtures for reusable setup
   - Mock external dependencies
   - Test both success and failure cases

5. TDD Approach:
   - Write test first (Red)
   - Implement minimal code to pass (Green)
   - Refactor while keeping tests green (Refactor)

Use these patterns as templates when writing new tests!
"""
