"""
Integration tests for database management commands and utilities.

Tests the full database connectivity stack including Django management
commands and graceful degradation.
"""

import pytest
from io import StringIO
from django.core.management import call_command
from django.core.management.base import CommandError
from unittest.mock import patch
from apps.core.management.commands.check_database import DatabaseReadyCheck


@pytest.mark.integration
@pytest.mark.django_db
class TestCheckDatabaseCommand:
    """Test the check_database management command."""

    def test_command_success_with_database_available(self):
        """Test command succeeds when database is available."""
        out = StringIO()
        call_command('check_database', stdout=out)

        output = out.getvalue()
        assert '✓ Database connection successful' in output
        assert 'Connection Details:' in output
        assert 'Database:' in output
        assert 'Host:' in output

    def test_command_displays_connection_details(self):
        """Test command displays detailed connection information."""
        out = StringIO()
        call_command('check_database', stdout=out)

        output = out.getvalue()
        # Should show database details
        assert 'backend_db' in output or 'Database:' in output
        assert 'localhost' in output or 'Host:' in output
        # Should show performance metrics
        assert 'ms' in output  # Response time
        # Should show configuration
        assert 'Connection Pooling' in output
        assert 'Atomic Requests' in output

    def test_command_failure_without_database(self):
        """Test command fails gracefully when database is unavailable."""
        out = StringIO()
        err = StringIO()

        # Mock database connection failure
        with patch('apps.core.database.connections') as mock_conn:
            mock_cursor = mock_conn.__getitem__.return_value.cursor
            mock_cursor.side_effect = Exception("Connection refused")

            with pytest.raises(CommandError):
                call_command('check_database', stdout=out, stderr=err)

            output = out.getvalue()
            assert '✗ Database connection failed' in output
            assert 'Troubleshooting:' in output

    def test_command_shows_troubleshooting_on_failure(self):
        """Test command shows helpful troubleshooting steps on failure."""
        out = StringIO()

        with patch('apps.core.database.connections') as mock_conn:
            mock_cursor = mock_conn.__getitem__.return_value.cursor
            mock_cursor.side_effect = Exception("Database does not exist")

            try:
                call_command('check_database', stdout=out)
            except CommandError:
                pass

            output = out.getvalue()
            assert 'Troubleshooting:' in output
            assert 'PostgreSQL is running' in output
            assert 'createdb' in output or 'database' in output.lower()


@pytest.mark.integration
class TestDatabaseReadyCheck:
    """Test database ready check utility."""

    @pytest.mark.django_db
    def test_check_and_warn_success(self, capsys):
        """Test check_and_warn returns True when database is available."""
        result = DatabaseReadyCheck.check_and_warn()

        assert result is True

        # Should not print warnings on success
        captured = capsys.readouterr()
        assert 'WARNING' not in captured.err

    def test_check_and_warn_failure(self, capsys):
        """Test check_and_warn returns False and prints warning on failure."""
        with patch('apps.core.database.connections') as mock_conn:
            mock_cursor = mock_conn.__getitem__.return_value.cursor
            mock_cursor.side_effect = Exception("Connection refused")

            result = DatabaseReadyCheck.check_and_warn()

            assert result is False

            # Should print warning to stderr
            captured = capsys.readouterr()
            assert 'WARNING' in captured.err
            assert 'Database connection failed' in captured.err
            assert 'check_database' in captured.err

    @pytest.mark.django_db
    def test_ensure_or_fail_success(self, capsys):
        """Test ensure_or_fail succeeds when database is available."""
        # Should not raise
        DatabaseReadyCheck.ensure_or_fail()

        captured = capsys.readouterr()
        assert '✓ Database connected' in captured.out

    def test_ensure_or_fail_exits_on_failure(self, capsys):
        """Test ensure_or_fail exits application on database failure."""
        with patch('apps.core.database.connections') as mock_conn:
            mock_cursor = mock_conn.__getitem__.return_value.cursor
            mock_cursor.side_effect = Exception("Connection refused")

            with pytest.raises(SystemExit) as exc_info:
                DatabaseReadyCheck.ensure_or_fail()

            assert exc_info.value.code == 1

            captured = capsys.readouterr()
            assert 'FATAL' in captured.err
            assert 'Database connection failed' in captured.err


@pytest.mark.integration
@pytest.mark.django_db
class TestDatabaseConfiguration:
    """Test database configuration across environments."""

    def test_database_engine_is_postgresql(self):
        """Test that PostgreSQL is configured as the database engine."""
        from django.conf import settings

        assert settings.DATABASES['default']['ENGINE'] == \
            'django.db.backends.postgresql'

    def test_connection_pooling_configuration(self):
        """Test connection pooling is properly configured."""
        from django.conf import settings

        db_settings = settings.DATABASES['default']

        # Should have connection pooling enabled
        assert db_settings['CONN_MAX_AGE'] == 600
        assert db_settings['ATOMIC_REQUESTS'] is True

    def test_database_can_execute_queries(self):
        """Test that database can execute SQL queries."""
        from django.db import connection

        with connection.cursor() as cursor:
            # Execute a simple query
            cursor.execute("SELECT version()")
            result = cursor.fetchone()

            # Should return PostgreSQL version
            assert result is not None
            assert 'PostgreSQL' in result[0]

    def test_transaction_support(self):
        """Test that database supports transactions."""
        from django.db import connection

        # PostgreSQL should support transactions
        assert connection.features.supports_transactions is True
        assert connection.features.uses_savepoints is True

    def test_database_supports_jsonb(self):
        """Test that database supports JSONB fields (PostgreSQL feature)."""
        from django.db import connection

        # PostgreSQL should support JSONB
        with connection.cursor() as cursor:
            cursor.execute("SELECT '{}'::jsonb")
            result = cursor.fetchone()
            assert result is not None


@pytest.mark.integration
@pytest.mark.django_db
class TestDatabaseMigrations:
    """Test database migration readiness."""

    def test_migrations_can_be_checked(self):
        """Test that Django can check migration status."""
        from io import StringIO
        from django.core.management import call_command

        out = StringIO()
        # This should not raise an error
        call_command('showmigrations', stdout=out)

        output = out.getvalue()
        # Should show migration status (even if no migrations yet)
        assert output is not None

    def test_database_schema_can_be_inspected(self):
        """Test that database schema can be inspected."""
        from django.db import connection

        # Should be able to get table names
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()

            # May or may not have tables, but query should work
            assert tables is not None
            assert isinstance(tables, (list, tuple))
