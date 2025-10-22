"""
Core app configuration.
"""
import sys
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'

    def ready(self):
        """
        Initialize core app components when Django is ready.

        This includes:
        - Database connectivity checks
        - Signal handler registration
        - Health monitoring setup
        """
        # Import signals here to avoid circular imports
        # import apps.core.signals

        # Check database connectivity on startup
        # Skip during migrations and other management commands that don't need DB
        skip_commands = [
            'makemigrations',
            'migrate',
            'check_database',
            'showmigrations',
            'sqlmigrate',
            'help',
            'version',
        ]

        # Only check database during runserver or production startup
        is_management_command = 'manage.py' in sys.argv[0] if sys.argv else False
        current_command = sys.argv[1] if len(sys.argv) > 1 else None

        if is_management_command and current_command in skip_commands:
            # Skip database check for commands that don't need it
            return

        # Perform database connectivity check
        # This provides immediate feedback if database is misconfigured
        if is_management_command and current_command == 'runserver':
            # For runserver, warn but allow startup (development convenience)
            from apps.core.management.commands.check_database import DatabaseReadyCheck
            DatabaseReadyCheck.check_and_warn()
        elif is_management_command:
            # For other commands, check but don't fail
            from apps.core.management.commands.check_database import DatabaseReadyCheck
            DatabaseReadyCheck.check_and_warn()
