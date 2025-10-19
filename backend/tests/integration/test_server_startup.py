"""
Integration tests for server startup and configuration.

This module tests that the server can start successfully with all
middleware configured and basic endpoints are accessible.
"""

import pytest
from django.conf import settings
from django.core.management import call_command


class TestServerStartup:
    """Test suite for server startup and configuration."""

    def test_django_settings_are_configured(self) -> None:
        """Test that Django settings are properly configured."""
        assert settings.configured
        assert settings.SECRET_KEY is not None

    def test_middleware_is_configured(self) -> None:
        """Test that all required middleware is configured."""
        middleware_list = settings.MIDDLEWARE

        # Check Django default middleware
        assert "django.middleware.security.SecurityMiddleware" in middleware_list
        assert "django.middleware.common.CommonMiddleware" in middleware_list
        assert "django.contrib.sessions.middleware.SessionMiddleware" in middleware_list

        # Check custom middleware
        assert "common.middleware.error_handling.ErrorHandlingMiddleware" in middleware_list
        assert "common.middleware.request_logging.RequestLoggingMiddleware" in middleware_list

    def test_middleware_order_is_correct(self) -> None:
        """Test that middleware is in the correct order."""
        middleware_list = settings.MIDDLEWARE

        # Error handling should come before request logging
        error_idx = middleware_list.index(
            "common.middleware.error_handling.ErrorHandlingMiddleware"
        )
        logging_idx = middleware_list.index(
            "common.middleware.request_logging.RequestLoggingMiddleware"
        )

        assert error_idx < logging_idx, "Error handling must come before request logging"

    def test_installed_apps_include_required_apps(self) -> None:
        """Test that all required apps are installed."""
        installed_apps = settings.INSTALLED_APPS

        # Django default apps
        assert "django.contrib.admin" in installed_apps
        assert "django.contrib.auth" in installed_apps
        assert "django.contrib.contenttypes" in installed_apps

        # Third-party apps
        assert "rest_framework" in installed_apps
        assert "corsheaders" in installed_apps
        assert "drf_spectacular" in installed_apps

    def test_rest_framework_settings_are_configured(self) -> None:
        """Test that REST Framework settings are configured."""
        drf_settings = settings.REST_FRAMEWORK

        assert "DEFAULT_RENDERER_CLASSES" in drf_settings
        assert "DEFAULT_PARSER_CLASSES" in drf_settings
        assert "DEFAULT_AUTHENTICATION_CLASSES" in drf_settings
        assert "DEFAULT_PERMISSION_CLASSES" in drf_settings

    def test_database_settings_are_configured(self) -> None:
        """Test that database settings are configured."""
        db_config = settings.DATABASES["default"]

        assert "ENGINE" in db_config
        assert "NAME" in db_config
        assert db_config["ENGINE"] == "django.db.backends.postgresql"

    def test_logging_is_configured(self) -> None:
        """Test that logging is properly configured."""
        logging_config = settings.LOGGING

        assert logging_config["version"] == 1
        assert "handlers" in logging_config
        assert "formatters" in logging_config
        assert "loggers" in logging_config

        # Check custom middleware logger
        assert "common.middleware" in logging_config["loggers"]

    @pytest.mark.django_db
    def test_database_connection_works(self) -> None:
        """Test that database connection is working."""
        from django.db import connection

        # This will raise an exception if connection fails
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result == (1,)

    def test_check_command_passes(self) -> None:
        """Test that Django system check passes."""
        # This will raise CommandError if checks fail
        call_command("check")

    def test_static_url_is_configured(self) -> None:
        """Test that static files configuration is set."""
        assert settings.STATIC_URL is not None
        assert settings.STATIC_ROOT is not None

    def test_cors_settings_are_configured(self) -> None:
        """Test that CORS settings are configured."""
        assert hasattr(settings, "CORS_ALLOWED_ORIGINS")
        assert hasattr(settings, "CORS_ALLOW_CREDENTIALS")
        assert settings.CORS_ALLOW_CREDENTIALS is True
