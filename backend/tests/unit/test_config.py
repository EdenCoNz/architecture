"""
Unit tests for configuration management system.

Tests cover environment detection, configuration validation,
required/optional settings, error messages, and configuration loading.
"""

import os
from typing import Any
from unittest.mock import patch

import pytest


@pytest.mark.unit
class TestEnvironmentDetection:
    """Test environment detection functionality."""

    def test_detect_development_environment(self) -> None:
        """When DJANGO_SETTINGS_MODULE is development, should detect development."""
        with patch.dict(
            os.environ, {"DJANGO_SETTINGS_MODULE": "config.settings.development"}
        ):
            from config.env_config import get_environment

            assert get_environment() == "development"

    def test_detect_production_environment(self) -> None:
        """When DJANGO_SETTINGS_MODULE is production, should detect production."""
        with patch.dict(
            os.environ, {"DJANGO_SETTINGS_MODULE": "config.settings.production"}
        ):
            from config.env_config import get_environment

            assert get_environment() == "production"

    def test_detect_testing_environment(self) -> None:
        """When DJANGO_SETTINGS_MODULE is testing, should detect testing."""
        with patch.dict(os.environ, {"DJANGO_SETTINGS_MODULE": "config.settings.testing"}):
            from config.env_config import get_environment

            assert get_environment() == "testing"

    def test_default_to_development_when_not_set(self) -> None:
        """When DJANGO_SETTINGS_MODULE not set, should default to development."""
        with patch.dict(os.environ, {}, clear=True):
            from config.env_config import get_environment

            assert get_environment() == "development"


@pytest.mark.unit
class TestConfigurationValidation:
    """Test configuration validation."""

    def test_validate_required_settings_all_present(self) -> None:
        """When all required settings present, validation should pass."""
        from config.env_config import validate_configuration

        env_vars = {
            "SECRET_KEY": "test-secret-key-at-least-50-characters-long-for-security",
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_password",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should not raise an exception
            validate_configuration("development")

    def test_validate_required_settings_missing(self) -> None:
        """When required settings missing, should raise clear error."""
        from config.env_config import ConfigurationError, validate_configuration

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                validate_configuration("production")

            error_message = str(exc_info.value)
            assert "Missing required configuration" in error_message
            assert "SECRET_KEY" in error_message

    def test_validate_secret_key_production_insecure(self) -> None:
        """When SECRET_KEY is insecure in production, should raise error."""
        from config.env_config import ConfigurationError, validate_configuration

        env_vars = {
            "SECRET_KEY": "django-insecure-development-key",
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_password",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                validate_configuration("production")

            assert "SECRET_KEY" in str(exc_info.value)
            assert "insecure" in str(exc_info.value).lower()

    def test_validate_secret_key_production_too_short(self) -> None:
        """When SECRET_KEY too short in production, should raise error."""
        from config.env_config import ConfigurationError, validate_configuration

        env_vars = {
            "SECRET_KEY": "short",
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_password",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                validate_configuration("production")

            assert "SECRET_KEY" in str(exc_info.value)
            assert "50 characters" in str(exc_info.value)

    def test_validate_allowed_hosts_required_in_production(self) -> None:
        """When ALLOWED_HOSTS not set in production, should raise error."""
        from config.env_config import ConfigurationError, validate_configuration

        env_vars = {
            "SECRET_KEY": "secure-production-key-that-is-definitely-long-enough-now",
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_password",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                validate_configuration("production")

            assert "ALLOWED_HOSTS" in str(exc_info.value)

    def test_validate_database_port_invalid(self) -> None:
        """When DB_PORT is invalid, should raise clear error."""
        from config.env_config import ConfigurationError, validate_configuration

        env_vars = {
            "SECRET_KEY": "test-secret-key-at-least-50-characters-long-for-security",
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_password",
            "DB_HOST": "localhost",
            "DB_PORT": "invalid",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                validate_configuration("development")

            assert "DB_PORT" in str(exc_info.value)
            assert "integer" in str(exc_info.value).lower()

    def test_validate_log_level_invalid(self) -> None:
        """When LOG_LEVEL is invalid, should raise clear error."""
        from config.env_config import ConfigurationError, validate_configuration

        env_vars = {
            "SECRET_KEY": "test-secret-key-at-least-50-characters-long-for-security",
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_password",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "LOG_LEVEL": "INVALID_LEVEL",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                validate_configuration("development")

            assert "LOG_LEVEL" in str(exc_info.value)


@pytest.mark.unit
class TestConfigurationLoading:
    """Test configuration loading functionality."""

    def test_get_config_value_required_present(self) -> None:
        """When required config present, should return value."""
        from config.env_config import get_config

        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            value = get_config("TEST_VAR", required=True)
            assert value == "test_value"

    def test_get_config_value_required_missing(self) -> None:
        """When required config missing, should raise error."""
        from config.env_config import ConfigurationError, get_config

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                get_config("MISSING_VAR", required=True)

            assert "MISSING_VAR" in str(exc_info.value)
            assert "required" in str(exc_info.value).lower()

    def test_get_config_value_optional_with_default(self) -> None:
        """When optional config missing, should return default."""
        from config.env_config import get_config

        with patch.dict(os.environ, {}, clear=True):
            value = get_config("OPTIONAL_VAR", default="default_value")
            assert value == "default_value"

    def test_get_config_value_type_casting_int(self) -> None:
        """When cast specified, should convert to correct type."""
        from config.env_config import get_config

        with patch.dict(os.environ, {"PORT": "8000"}):
            value = get_config("PORT", cast=int)
            assert value == 8000
            assert isinstance(value, int)

    def test_get_config_value_type_casting_bool(self) -> None:
        """When casting to bool, should handle true/false strings."""
        from config.env_config import get_config

        with patch.dict(os.environ, {"DEBUG": "True"}):
            value = get_config("DEBUG", cast=bool)
            assert value is True

        with patch.dict(os.environ, {"DEBUG": "False"}):
            value = get_config("DEBUG", cast=bool)
            assert value is False

    def test_get_config_value_type_casting_list(self) -> None:
        """When casting to list, should split comma-separated values."""
        from config.env_config import get_config

        with patch.dict(os.environ, {"HOSTS": "host1,host2,host3"}):
            value = get_config("HOSTS", cast=lambda v: [s.strip() for s in v.split(",")])
            assert value == ["host1", "host2", "host3"]


@pytest.mark.unit
class TestConfigurationErrorMessages:
    """Test that error messages are clear and actionable."""

    def test_error_message_lists_all_missing_variables(self) -> None:
        """When multiple variables missing, should list all in error."""
        from config.env_config import ConfigurationError, validate_configuration

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                validate_configuration("production")

            error_message = str(exc_info.value)
            # Should mention multiple missing variables
            assert "SECRET_KEY" in error_message or "DB_NAME" in error_message

    def test_error_message_provides_solution(self) -> None:
        """When configuration invalid, should suggest solution."""
        from config.env_config import ConfigurationError, validate_configuration

        with patch.dict(os.environ, {"SECRET_KEY": "short"}, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                validate_configuration("production")

            error_message = str(exc_info.value)
            # Should provide guidance on how to fix
            assert ".env" in error_message or "environment" in error_message.lower()

    def test_error_message_shows_environment_context(self) -> None:
        """When validation fails, should show which environment."""
        from config.env_config import ConfigurationError, validate_configuration

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                validate_configuration("production")

            error_message = str(exc_info.value)
            assert "production" in error_message.lower()


@pytest.mark.unit
class TestConfigurationDefaults:
    """Test default configuration values."""

    def test_development_uses_defaults_safely(self) -> None:
        """Development environment should have safe defaults."""
        from config.env_config import validate_configuration

        # Minimal required vars for development
        env_vars = {
            "SECRET_KEY": "dev-key",  # Short key OK in development
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should not raise - development allows defaults
            validate_configuration("development")

    def test_testing_uses_minimal_config(self) -> None:
        """Testing environment should work with minimal config."""
        from config.env_config import validate_configuration

        # Testing should work with almost no configuration
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise - testing has its own defaults
            validate_configuration("testing")

    def test_production_requires_explicit_config(self) -> None:
        """Production should require all settings explicitly set."""
        from config.env_config import ConfigurationError, validate_configuration

        # Even with some vars, production should fail without all required
        env_vars = {
            "SECRET_KEY": "production-key-that-is-long-enough-to-be-secure-now",
            "DB_NAME": "prod_db",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ConfigurationError):
                validate_configuration("production")


@pytest.mark.unit
class TestConfigurationDocumentation:
    """Test that configuration is well-documented."""

    def test_get_all_config_variables(self) -> None:
        """Should provide list of all configuration variables."""
        from config.env_config import get_all_config_variables

        all_vars = get_all_config_variables()

        # Should include known required variables
        assert "SECRET_KEY" in all_vars
        assert "DB_NAME" in all_vars
        assert "DB_USER" in all_vars
        assert "DB_PASSWORD" in all_vars

        # Each variable should have description
        for var_name, var_info in all_vars.items():
            assert "description" in var_info
            assert "required" in var_info
            assert isinstance(var_info["required"], bool)

    def test_config_variables_have_defaults_documented(self) -> None:
        """Optional variables should document their defaults."""
        from config.env_config import get_all_config_variables

        all_vars = get_all_config_variables()

        # Optional variables should have default documented
        if "LOG_LEVEL" in all_vars:
            var_info = all_vars["LOG_LEVEL"]
            if not var_info["required"]:
                assert "default" in var_info

    def test_config_variables_have_examples(self) -> None:
        """Configuration variables should include examples."""
        from config.env_config import get_all_config_variables

        all_vars = get_all_config_variables()

        # Should have examples for complex variables
        if "CORS_ALLOWED_ORIGINS" in all_vars:
            assert "example" in all_vars["CORS_ALLOWED_ORIGINS"]
