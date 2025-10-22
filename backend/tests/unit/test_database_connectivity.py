"""
Unit tests for database connectivity and connection management.

Following TDD principles - these tests define the expected behavior
before implementation.
"""

import pytest
from django.db import connection, connections
from django.db.utils import OperationalError
from unittest.mock import patch, MagicMock
from apps.core.database import DatabaseHealthCheck


@pytest.mark.unit
@pytest.mark.django_db
class TestDatabaseConnectivity:
    """Test database connection functionality."""

    def test_database_connection_successful(self):
        """Test that database connection can be established."""
        # This will fail until we ensure connection works
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result == (1,)

    def test_database_connection_can_be_closed_and_reopened(self):
        """Test that connection can be closed and reopened."""
        connection.close()

        # Should be able to reopen
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result == (1,)

    def test_multiple_database_queries(self):
        """Test that multiple queries work correctly."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result1 = cursor.fetchone()

            cursor.execute("SELECT 2")
            result2 = cursor.fetchone()

            assert result1 == (1,)
            assert result2 == (2,)

    def test_connection_pool_settings(self):
        """Test that connection pooling is configured correctly."""
        db_settings = connections['default'].settings_dict

        # Should have connection pooling enabled
        assert db_settings.get('CONN_MAX_AGE', 0) > 0
        assert db_settings.get('ATOMIC_REQUESTS') is True


@pytest.mark.unit
class TestDatabaseHealthCheck:
    """Test database health check utility."""

    @pytest.mark.django_db
    def test_health_check_success(self):
        """Test health check returns success when database is available."""
        checker = DatabaseHealthCheck()
        result = checker.check()

        assert result['status'] == 'healthy'
        assert result['database'] == 'connected'
        assert 'response_time_ms' in result
        assert result['response_time_ms'] > 0

    def test_health_check_failure(self):
        """Test health check returns failure when database is unavailable."""
        checker = DatabaseHealthCheck()

        # Mock connection.cursor to raise OperationalError
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.side_effect = OperationalError("Connection refused")

            result = checker.check()

            assert result['status'] == 'unhealthy'
            assert result['database'] == 'disconnected'
            assert 'error' in result
            assert 'Connection refused' in result['error']

    def test_health_check_includes_connection_info(self):
        """Test health check includes connection information."""
        checker = DatabaseHealthCheck()
        result = checker.check()

        assert 'connection_info' in result
        assert 'engine' in result['connection_info']
        assert 'host' in result['connection_info']
        assert 'name' in result['connection_info']
        # Should not expose password
        assert 'password' not in str(result).lower()

    @pytest.mark.django_db
    def test_health_check_measures_response_time(self):
        """Test that health check accurately measures response time."""
        checker = DatabaseHealthCheck()
        result = checker.check()

        assert 'response_time_ms' in result
        # Response time should be reasonable (< 1000ms for local DB)
        assert 0 < result['response_time_ms'] < 1000


@pytest.mark.unit
class TestConnectionErrorHandling:
    """Test connection error handling and graceful degradation."""

    def test_connection_error_message_is_clear(self):
        """Test that connection errors produce clear messages."""
        checker = DatabaseHealthCheck()

        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.side_effect = OperationalError(
                "FATAL: database 'backend_db' does not exist"
            )

            result = checker.check()

            assert 'error' in result
            assert 'database' in result['error'].lower()
            assert 'does not exist' in result['error'].lower()

    def test_authentication_error_message(self):
        """Test that authentication errors produce clear messages."""
        checker = DatabaseHealthCheck()

        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.side_effect = OperationalError(
                "FATAL: password authentication failed for user 'postgres'"
            )

            result = checker.check()

            assert 'error' in result
            assert 'authentication' in result['error'].lower()

    def test_connection_refused_error_message(self):
        """Test that connection refused errors produce clear messages."""
        checker = DatabaseHealthCheck()

        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.side_effect = OperationalError(
                "could not connect to server: Connection refused"
            )

            result = checker.check()

            assert 'error' in result
            assert 'connect' in result['error'].lower()


@pytest.mark.unit
class TestEnvironmentConfiguration:
    """Test environment-specific database configurations."""

    def test_database_settings_loaded_from_environment(self):
        """Test that database settings are loaded from environment variables."""
        from django.conf import settings

        db_config = settings.DATABASES['default']

        # Should be using environment variables (via python-decouple)
        assert db_config['ENGINE'] == 'django.db.backends.postgresql'
        assert 'NAME' in db_config
        assert 'USER' in db_config
        assert 'HOST' in db_config
        assert 'PORT' in db_config

        # Should have connection pooling
        assert db_config.get('CONN_MAX_AGE', 0) == 600
        assert db_config.get('ATOMIC_REQUESTS') is True

    def test_no_hardcoded_credentials(self):
        """Test that no credentials are hardcoded in settings."""
        from django.conf import settings
        import config.settings.base as base_settings
        import inspect

        # Get the source code of the settings file
        source = inspect.getsource(base_settings)

        # Should use config() or environment variables, not hardcoded values
        # (except for defaults which are safe for development)
        assert "config('DB_NAME'" in source
        assert "config('DB_USER'" in source
        assert "config('DB_PASSWORD'" in source
        assert "config('DB_HOST'" in source
        assert "config('DB_PORT'" in source

    def test_connection_pool_configured(self):
        """Test that connection pooling is properly configured."""
        from django.conf import settings

        db_config = settings.DATABASES['default']

        # CONN_MAX_AGE should be set for connection pooling
        conn_max_age = db_config.get('CONN_MAX_AGE', 0)
        assert conn_max_age > 0, "Connection pooling should be enabled"
        assert conn_max_age == 600, "Connection pool timeout should be 600 seconds"

    def test_atomic_requests_enabled(self):
        """Test that atomic requests are enabled for data integrity."""
        from django.conf import settings

        db_config = settings.DATABASES['default']

        # ATOMIC_REQUESTS should be True for data integrity
        assert db_config.get('ATOMIC_REQUESTS') is True
