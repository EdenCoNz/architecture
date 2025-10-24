"""
Test the test environment database configuration.

Following TDD principles - these tests verify that the test environment
uses the correct database backend and credentials as specified in CI.
"""

import os
from unittest.mock import patch

import pytest
from django.conf import settings


@pytest.mark.unit
class TestTestDatabaseConfiguration:
    """Test that the test environment uses correct database configuration."""

    def test_uses_postgresql_when_env_var_set(self):
        """Test that PostgreSQL is used when USE_POSTGRES_FOR_TESTS is true."""
        # In CI environment, USE_POSTGRES_FOR_TESTS should be set to true
        # and the database should use PostgreSQL backend
        db_config = settings.DATABASES["default"]

        # When USE_POSTGRES_FOR_TESTS is set, should use PostgreSQL
        use_postgres = os.environ.get("USE_POSTGRES_FOR_TESTS", "false").lower() == "true"

        if use_postgres:
            assert (
                db_config["ENGINE"] == "django.db.backends.postgresql"
            ), "Should use PostgreSQL backend when USE_POSTGRES_FOR_TESTS is true"
        else:
            # Default to SQLite for fast unit tests
            assert db_config["ENGINE"] == "django.db.backends.sqlite3"

    def test_uses_correct_database_credentials_from_environment(self):
        """Test that database credentials come from environment variables."""
        db_config = settings.DATABASES["default"]

        use_postgres = os.environ.get("USE_POSTGRES_FOR_TESTS", "false").lower() == "true"

        if use_postgres:
            # Should read credentials from environment
            # In CI: DB_USER=test_user, DB_PASSWORD=test_password, DB_NAME=test_backend_db
            expected_user = os.environ.get("DB_USER", "postgres")
            expected_password = os.environ.get("DB_PASSWORD", "postgres")
            expected_base_name = os.environ.get("DB_NAME", "backend_test_db")
            expected_host = os.environ.get("DB_HOST", "localhost")
            expected_port = os.environ.get("DB_PORT", "5432")

            assert db_config["USER"] == expected_user, (
                f"Should use DB_USER from environment, "
                f"expected {expected_user} but got {db_config['USER']}"
            )
            assert (
                db_config["PASSWORD"] == expected_password
            ), "Should use DB_PASSWORD from environment"

            # Django automatically modifies test database names when using pytest-xdist:
            # 1. Prefixes with "test_" (e.g., test_backend_db -> test_test_backend_db)
            # 2. Adds worker suffix (e.g., _gw0, _gw1) for parallel execution
            # So we verify the base name is derived from the environment variable
            actual_db_name = db_config["NAME"]

            # The database name should contain the base name from environment
            # It may be prefixed with "test_" and suffixed with worker ID
            assert expected_base_name in actual_db_name, (
                f"Database name should be derived from DB_NAME environment variable. "
                f"Expected to find '{expected_base_name}' in '{actual_db_name}'"
            )

            # If it's a test database (has "test_" prefix or worker suffix),
            # verify it follows Django's naming convention
            if actual_db_name != expected_base_name:
                # Check for Django's "test_" prefix pattern
                assert actual_db_name.startswith("test_"), (
                    f"Test database should start with 'test_' prefix, "
                    f"but got '{actual_db_name}'"
                )

            assert db_config["HOST"] == expected_host, "Should use DB_HOST from environment"
            assert str(db_config["PORT"]) == expected_port, "Should use DB_PORT from environment"

    def test_no_hardcoded_root_user(self):
        """Test that the test environment doesn't use hardcoded 'root' user."""
        db_config = settings.DATABASES["default"]

        use_postgres = os.environ.get("USE_POSTGRES_FOR_TESTS", "false").lower() == "true"

        if use_postgres:
            # Should NEVER use 'root' user - this was causing authentication failures
            assert (
                db_config["USER"] != "root"
            ), "Test environment should not use 'root' user - this causes authentication failures"

    def test_connection_pooling_configured(self):
        """Test that connection pooling is configured for PostgreSQL tests."""
        db_config = settings.DATABASES["default"]

        use_postgres = os.environ.get("USE_POSTGRES_FOR_TESTS", "false").lower() == "true"

        if use_postgres:
            assert db_config.get("CONN_MAX_AGE", 0) > 0, "Connection pooling should be enabled"
            assert db_config.get("ATOMIC_REQUESTS") is True, "Atomic requests should be enabled"

    def test_separate_test_database_name(self):
        """Test that a separate test database name is configured."""
        db_config = settings.DATABASES["default"]

        use_postgres = os.environ.get("USE_POSTGRES_FOR_TESTS", "false").lower() == "true"

        if use_postgres:
            # Should have TEST configuration for separate test database
            assert "TEST" in db_config, "Should have TEST configuration for separate test database"
            test_db_name = db_config["TEST"].get("NAME")
            assert (
                test_db_name
            ), "Should specify a separate test database name to avoid affecting main database"
