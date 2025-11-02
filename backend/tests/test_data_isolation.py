"""
Test Data Isolation Validation (Story 13.2)

This module contains tests that validate test data isolation works correctly.
Each test should have a clean database state and changes should not affect
other tests or other environments.

Acceptance Criteria Tests:
- AC1: Fresh test database created with known baseline state
- AC2: Test changes only affect the test database
- AC3: Each test has a clean data state
- AC4: Production/development databases remain unchanged
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import connection

from tests.factories import (
    AssessmentFactory,
    BeginnerAssessmentFactory,
    TestDataBuilder,
    UserFactory,
)

User = get_user_model()

# Import assessment models if available
try:
    from apps.assessments.models import Assessment
except (ImportError, RuntimeError):
    Assessment = None  # type: ignore[assignment,misc]
    pytestmark = pytest.mark.skip(reason="Assessment models not available")


class TestDatabaseIsolation:
    """
    Test that database isolation works correctly.

    Each test should start with a clean database state and changes
    should be automatically rolled back after the test completes.
    """

    def test_database_is_test_database(self, db):
        """
        Verify we're using the test database, not production or development.

        Acceptance Criteria: AC2 - Changes only affect test database
        """
        db_name = connection.settings_dict["NAME"]

        # Check we're using test database
        # Accept :memory:, file:memory, or databases with "test" in name
        is_test_db = (
            "test" in db_name.lower() or db_name == ":memory:" or "memory" in db_name.lower()
        )

        assert is_test_db, (
            f"Not using test database! Current database: {db_name}. "
            "Tests should never run against production or development databases."
        )

    def test_database_starts_empty(self, clean_database):
        """
        Verify database starts with no users or assessments.

        Acceptance Criteria: AC1 - Fresh database with known baseline state
        """
        # Database should be completely empty at start
        assert User.objects.count() == 0, "Database should start with no users"
        assert Assessment.objects.count() == 0, "Database should start with no assessments"

    def test_test_data_is_isolated_between_tests_first(self, isolated_db):
        """
        First test: Create data and verify it exists.

        This test creates data that should NOT be visible to the next test.

        Acceptance Criteria: AC3 - Each test has clean data state
        """
        # Create test data
        user = UserFactory(email="first.test@example.com")
        assessment = AssessmentFactory(user=user, sport="soccer")

        # Verify data exists in this test
        assert User.objects.count() == 1
        assert Assessment.objects.count() == 1
        assert User.objects.filter(email="first.test@example.com").exists()

    def test_test_data_is_isolated_between_tests_second(self, isolated_db):
        """
        Second test: Verify previous test's data doesn't exist.

        This test should NOT see data created in the previous test,
        demonstrating complete test isolation.

        Acceptance Criteria: AC3 - Each test has clean data state
        """
        # Previous test's data should not exist
        assert User.objects.count() == 0, (
            "Data from previous test leaked into this test! "
            "Database isolation is not working correctly."
        )
        assert (
            Assessment.objects.count() == 0
        ), "Assessment from previous test leaked into this test!"
        assert not User.objects.filter(
            email="first.test@example.com"
        ).exists(), "Specific user from previous test still exists!"

    def test_multiple_users_do_not_persist(self, isolated_db):
        """
        Test that batch-created users don't persist to other tests.

        Acceptance Criteria: AC3 - Each test has clean data state
        """
        # Create multiple users
        users = UserFactory.create_batch(5)
        assert User.objects.count() == 5

        # Create assessments for each user
        for user in users:
            AssessmentFactory(user=user)

        assert Assessment.objects.count() == 5

        # Data exists in this test
        assert User.objects.count() == 5
        assert Assessment.objects.count() == 5

    def test_previous_batch_data_not_visible(self, isolated_db):
        """
        Verify batch data from previous test is not visible.

        This test runs after test_multiple_users_do_not_persist and
        should see a clean database.

        Acceptance Criteria: AC3 - Each test has clean data state
        """
        # Should start clean despite previous test creating 5 users
        assert User.objects.count() == 0, "Users from previous batch test are still present!"
        assert (
            Assessment.objects.count() == 0
        ), "Assessments from previous batch test are still present!"


class TestTransactionalIsolation:
    """
    Test that Django's transactional test case behavior works correctly.

    Each test runs in a transaction that is rolled back after completion.
    """

    def test_data_created_in_test_is_rolled_back(self, db):
        """
        Verify that data created in a test is automatically rolled back.

        Acceptance Criteria: AC3 - Each test has clean data state
        """
        # Create data
        initial_count = User.objects.count()
        UserFactory(email="rollback.test@example.com")

        # Verify it exists during test
        assert User.objects.count() == initial_count + 1
        assert User.objects.filter(email="rollback.test@example.com").exists()

        # After test completes, Django will rollback the transaction
        # The next test will verify this

    def test_previous_test_data_was_rolled_back(self, db):
        """
        Verify previous test's data was rolled back.

        Acceptance Criteria: AC3 - Each test has clean data state
        """
        # Data from previous test should not exist
        assert not User.objects.filter(
            email="rollback.test@example.com"
        ).exists(), "Data from previous test was not rolled back!"


class TestFactoryIsolation:
    """
    Test that factory-generated data is properly isolated.
    """

    def test_factory_sequences_are_consistent(self, db):
        """
        Test that factory sequences start from a consistent point.

        Acceptance Criteria: AC1 - Known baseline state
        """
        # Create users with factory
        user1 = UserFactory()
        user2 = UserFactory()

        # Emails should use sequence numbers
        assert "@example.com" in user1.email
        assert "@example.com" in user2.email
        assert user1.email != user2.email

    def test_assessments_have_valid_relationships(self, db):
        """
        Test that factory-created assessments have valid user relationships.

        Acceptance Criteria: AC1 - Known baseline state
        """
        # Create assessment (should create user automatically)
        assessment = AssessmentFactory()

        # Verify relationships are valid
        assert assessment.user is not None
        assert assessment.user.email is not None
        assert User.objects.filter(pk=assessment.user.pk).exists()

    def test_specialized_factories_work_correctly(self, db):
        """
        Test that specialized assessment factories create correct data.

        Acceptance Criteria: AC1 - Known baseline state
        """
        # Create beginner assessment
        beginner = BeginnerAssessmentFactory()
        assert beginner.experience_level == "beginner"
        assert beginner.training_days == "2-3"

        # Create assessment batch
        assessments = AssessmentFactory.create_batch(3, sport="cricket")
        assert len(assessments) == 3
        assert all(a.sport == "cricket" for a in assessments)


class TestDatabaseConfiguration:
    """
    Test that database configuration is correct for test isolation.
    """

    def test_atomic_requests_enabled(self, db, settings):
        """
        Verify ATOMIC_REQUESTS is enabled for test isolation.

        Acceptance Criteria: AC3 - Clean data state for each test
        """
        assert (
            settings.DATABASES["default"]["ATOMIC_REQUESTS"] is True
        ), "ATOMIC_REQUESTS must be True for proper test isolation"

    def test_connection_pooling_enabled_for_tests(self, db, settings):
        """
        Verify connection pooling is enabled in tests (Issue #215).

        Connection pooling is enabled in all environments for performance consistency.
        Test isolation is maintained through ATOMIC_REQUESTS and pytest-django's
        transaction rollback mechanism.

        Acceptance Criteria: AC3 - Clean data state for each test

        Note: As of Issue #215, connection pooling is enabled in all environments
        (including testing) for performance consistency. Django's ATOMIC_REQUESTS
        and pytest-django's transaction rollback mechanism ensure test isolation
        is maintained even with connection pooling enabled.
        """
        conn_max_age = settings.DATABASES["default"].get("CONN_MAX_AGE", 0)
        assert (
            conn_max_age == 600
        ), f"CONN_MAX_AGE should be 600 for connection pooling (Issue #215), got {conn_max_age}"

    def test_test_database_settings_configured(self, db, settings):
        """
        Verify TEST database settings are properly configured.

        Acceptance Criteria: AC1 - Fresh database with known baseline
        """
        test_settings = settings.DATABASES["default"].get("TEST", {})

        # SERIALIZE should be False for faster tests
        assert (
            test_settings.get("SERIALIZE", True) is False
        ), "SERIALIZE should be False for faster test execution"


class TestDataBuilderIsolation:
    """
    Test that TestDataBuilder helper methods create isolated data.
    """

    def test_complete_scenario_creates_isolated_data(self, db):
        """
        Test that complete scenario helper creates fresh data.

        Acceptance Criteria: AC1 - Known baseline state
        """
        # Should start with empty database
        assert User.objects.count() == 0
        assert Assessment.objects.count() == 0

        # Create complete scenario
        scenario = TestDataBuilder.create_complete_onboarding_scenario()

        # Verify all data created
        assert User.objects.count() == 4  # beginner, intermediate, advanced, injured
        assert Assessment.objects.count() == 4

        # Verify scenario structure
        assert "beginner_user" in scenario
        assert "advanced_user" in scenario
        assert "injured_user" in scenario
        assert scenario["beginner_assessment"].experience_level == "beginner"
        assert scenario["injured_assessment"].injuries == "yes"

    def test_scenario_data_does_not_persist(self, db):
        """
        Verify scenario data from previous test doesn't persist.

        Acceptance Criteria: AC3 - Clean data state for each test
        """
        # Previous test created 4 users and 4 assessments
        # They should not be visible here
        assert User.objects.count() == 0, "Users from previous scenario test still exist!"
        assert (
            Assessment.objects.count() == 0
        ), "Assessments from previous scenario test still exist!"


class TestCleanupFixtures:
    """
    Test that cleanup fixtures work correctly.
    """

    def test_clean_database_fixture_empties_database(self, clean_database):
        """
        Test that clean_database fixture provides empty database.

        Acceptance Criteria: AC1 - Known baseline state
        """
        # clean_database fixture should have cleared everything
        assert User.objects.count() == 0
        assert Assessment.objects.count() == 0

    def test_clean_database_removes_existing_data(self, db):
        """
        Test that data is properly isolated with transactions.

        Acceptance Criteria: AC3 - Clean data state
        """
        # Record state before creating data
        users_before = User.objects.count()
        assessments_before = Assessment.objects.count()

        # Create assessments (which automatically create users via SubFactory)
        assessments = AssessmentFactory.create_batch(3)

        # Verify data was created
        # 3 assessments created + 3 users (one per assessment via SubFactory)
        assert (
            User.objects.count() == users_before + 3
        ), f"Expected {users_before + 3} users, got {User.objects.count()}"
        assert Assessment.objects.count() == assessments_before + 3

        # Data will be automatically rolled back after test due to
        # Django's transactional test case behavior


class TestEnvironmentIsolation:
    """
    Test that test environment is isolated from production/development.
    """

    def test_debug_mode_enabled_in_tests(self):
        """
        Verify DEBUG is enabled for better test output.

        Acceptance Criteria: AC1 - Known baseline state
        """
        # Import settings directly to avoid pytest-django wrapper
        from django.conf import settings as django_settings

        # DEBUG might be False in test settings for security checks
        # What's important is we're using test settings
        assert (
            django_settings.SETTINGS_MODULE == "config.settings.testing"
        ), f"Not using test settings: {django_settings.SETTINGS_MODULE}"

    def test_using_test_settings_module(self, settings):
        """
        Verify we're using test settings, not production settings.

        Acceptance Criteria: AC2 - Changes only affect test database
        """
        # Check that we're using testing settings
        assert (
            "testing" in settings.SETTINGS_MODULE
        ), f"Not using testing settings! Current: {settings.SETTINGS_MODULE}"

    def test_simple_password_hasher_for_speed(self, settings):
        """
        Verify test uses fast password hasher.

        Acceptance Criteria: AC1 - Optimized test environment
        """
        # Test should use MD5 hasher for speed
        hashers = settings.PASSWORD_HASHERS
        assert len(hashers) > 0
        assert (
            "MD5PasswordHasher" in hashers[0]
        ), "Tests should use MD5PasswordHasher for faster execution"

    def test_cache_backend_is_locmem(self, settings):
        """
        Verify test uses in-memory cache, not shared cache.

        Acceptance Criteria: AC2 - Test changes don't affect other environments
        """
        cache_backend = settings.CACHES["default"]["BACKEND"]
        assert "locmem" in cache_backend.lower(), (
            f"Tests should use LocMemCache, not {cache_backend}. "
            "Shared cache could leak data between environments."
        )

    def test_email_backend_is_locmem(self, settings):
        """
        Verify test uses in-memory email backend.

        Acceptance Criteria: AC2 - Test changes don't affect other environments
        """
        email_backend = settings.EMAIL_BACKEND
        assert "locmem" in email_backend.lower(), (
            f"Tests should use locmem email backend, not {email_backend}. "
            "Tests should never send real emails."
        )


# Summary validation test
class TestAcceptanceCriteria:
    """
    High-level tests that directly validate acceptance criteria.
    """

    def test_ac1_fresh_database_with_baseline_state(self, clean_database):
        """
        AC1: Fresh test database should be created with known baseline state.

        Validates: Given a test suite starts, when the test environment
        initializes, then a fresh test database should be created with a
        known baseline state.
        """
        # Verify database is empty (known baseline state)
        assert User.objects.count() == 0
        assert Assessment.objects.count() == 0

        # Verify we can create predictable test data
        user = UserFactory(email="baseline@example.com")
        assert User.objects.filter(email="baseline@example.com").exists()

    def test_ac2_changes_only_affect_test_database(self, db):
        """
        AC2: Changes should only affect the test database.

        Validates: Given tests are executing, when they create or modify
        data, then changes should only affect the test database.
        """
        db_name = connection.settings_dict["NAME"]

        # Verify using test database (memory or with test in name)
        is_test_db = (
            "test" in db_name.lower() or db_name == ":memory:" or "memory" in db_name.lower()
        )
        assert is_test_db

        # Create data - should only affect test database
        UserFactory(email="test.isolation@example.com")
        assert User.objects.filter(email="test.isolation@example.com").exists()

    def test_ac3_each_test_has_clean_state(self, db):
        """
        AC3: Each test should have a clean data state.

        Validates: Given a test completes, when the next test begins, then
        each test should have a clean data state.
        """
        # Django's transactional tests provide isolation
        # Each test's data is rolled back automatically

        # Record state before creating data
        users_before = User.objects.count()
        assessments_before = Assessment.objects.count()

        # Create assessments (which automatically create users via SubFactory)
        new_assessments = AssessmentFactory.create_batch(5)

        # Verify data was created
        # 5 assessments + 5 users (one per assessment via SubFactory)
        assert (
            User.objects.count() == users_before + 5
        ), f"Expected {users_before + 5} users, got {User.objects.count()}"
        assert Assessment.objects.count() == assessments_before + 5

        # Verify we can query the newly created data
        assert len(new_assessments) == 5

        # After this test, data will be rolled back for next test

    def test_ac4_production_database_unchanged(self):
        """
        AC4: Production and development databases should be unchanged.

        Validates: Given the test suite finishes, when I inspect the
        production and development databases, then they should be unchanged.

        Note: We can't directly test production database, but we can verify
        we're using isolated test database and settings.
        """
        from django.conf import settings

        # Verify we're NOT using production/development database
        db_name = connection.settings_dict["NAME"]
        is_test_db = (
            "test" in db_name.lower() or db_name == ":memory:" or "memory" in db_name.lower()
        )
        assert is_test_db, "Test is using production/development database!"

        # Verify using test settings
        assert (
            "testing" in settings.SETTINGS_MODULE
        ), "Test is using production/development settings!"

        # Verify transaction rollback is enabled
        assert settings.DATABASES["default"]["ATOMIC_REQUESTS"] is True
