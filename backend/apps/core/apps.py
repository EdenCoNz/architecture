"""
Core app configuration.
"""

import sys

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        """
        Initialize core app components when Django is ready.

        This includes:
        - Signal handler registration
        - Health monitoring setup

        Note: Database connectivity checks have been removed from ready() to avoid
        the RuntimeWarning about accessing the database during app initialization.
        Database health checks are available via:
        - Health check endpoints: /api/v1/health/
        - Management command: python manage.py check_database
        - Startup scripts in Docker entrypoint
        """
        # Import signals here to avoid circular imports
        # import apps.core.signals

        # DO NOT perform database checks here - it causes RuntimeWarning
        # Django discourages database access during AppConfig.ready()
        # Database connectivity should be checked via:
        # 1. Health check endpoints (/api/v1/health/)
        # 2. Management commands (python manage.py check_database)
        # 3. Docker entrypoint startup scripts
        pass
