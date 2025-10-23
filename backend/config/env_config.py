"""
Environment-based configuration management.

This module provides centralized configuration management with validation,
type casting, and clear error messages. It ensures the API behaves
appropriately across development, testing, and production environments.

Usage:
    from config.env_config import get_config, validate_configuration

    # Get configuration value with type casting
    db_port = get_config('DB_PORT', default=5432, cast=int)

    # Validate all configuration on startup
    validate_configuration()
"""

import os
import sys
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from decouple import config

T = TypeVar("T")


class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""

    pass


# Configuration variable registry with metadata
CONFIG_VARIABLES: Dict[str, Dict[str, Any]] = {
    # Django Core Settings
    "SECRET_KEY": {
        "description": "Django secret key for cryptographic signing",
        "required": True,
        "required_in": ["development", "production"],
        "example": "your-secret-key-here-generate-using-python-secrets",
        "validation": lambda v, env: (
            len(v) >= 50 if env == "production" else len(v) > 0,
            "SECRET_KEY must be at least 50 characters in production",
        ),
        "production_validation": lambda v: (
            "django-insecure" not in v.lower(),
            "SECRET_KEY cannot contain 'django-insecure' in production",
        ),
    },
    "DEBUG": {
        "description": "Enable debug mode (should be False in production)",
        "required": False,
        "default": "True",
        "example": "False",
    },
    "ALLOWED_HOSTS": {
        "description": "Comma-separated list of allowed hosts",
        "required": False,
        "required_in": ["production"],
        "default": "localhost,127.0.0.1",
        "example": "example.com,www.example.com,api.example.com",
    },
    # Database Settings
    "DB_NAME": {
        "description": "Database name",
        "required": True,
        "required_in": ["development", "production"],
        "default": "backend_db",
        "example": "backend_db",
    },
    "DB_USER": {
        "description": "Database username",
        "required": True,
        "required_in": ["development", "production"],
        "default": "postgres",
        "example": "postgres",
    },
    "DB_PASSWORD": {
        "description": "Database password",
        "required": True,
        "required_in": ["development", "production"],
        "default": "postgres",
        "example": "secure_password",
        "sensitive": True,
    },
    "DB_HOST": {
        "description": "Database host",
        "required": False,
        "default": "localhost",
        "example": "localhost",
    },
    "DB_PORT": {
        "description": "Database port",
        "required": False,
        "default": "5432",
        "example": "5432",
        "validation": lambda v, env: (
            v.isdigit() and 1 <= int(v) <= 65535,
            "DB_PORT must be a valid port number (1-65535)",
        ),
    },
    # Redis Settings
    "REDIS_URL": {
        "description": "Redis connection URL",
        "required": False,
        "default": "redis://127.0.0.1:6379/1",
        "example": "redis://localhost:6379/1",
    },
    # Celery Settings
    "CELERY_BROKER_URL": {
        "description": "Celery broker URL",
        "required": False,
        "default": "redis://127.0.0.1:6379/0",
        "example": "redis://localhost:6379/0",
    },
    "CELERY_RESULT_BACKEND": {
        "description": "Celery result backend URL",
        "required": False,
        "default": "redis://127.0.0.1:6379/0",
        "example": "redis://localhost:6379/0",
    },
    # CORS Settings
    "CORS_ALLOWED_ORIGINS": {
        "description": "Comma-separated list of allowed CORS origins",
        "required": False,
        "default": "http://localhost:3000,http://127.0.0.1:3000",
        "example": "http://localhost:3000,https://example.com",
    },
    # Email Settings
    "EMAIL_HOST": {
        "description": "Email server host",
        "required": False,
        "required_in": [],
        "default": "smtp.gmail.com",
        "example": "smtp.gmail.com",
    },
    "EMAIL_PORT": {
        "description": "Email server port",
        "required": False,
        "default": "587",
        "example": "587",
        "validation": lambda v, env: (
            v.isdigit() and 1 <= int(v) <= 65535,
            "EMAIL_PORT must be a valid port number (1-65535)",
        ),
    },
    "EMAIL_HOST_USER": {
        "description": "Email server username",
        "required": False,
        "default": "",
        "example": "your-email@example.com",
    },
    "EMAIL_HOST_PASSWORD": {
        "description": "Email server password",
        "required": False,
        "default": "",
        "example": "your-email-password",
        "sensitive": True,
    },
    "DEFAULT_FROM_EMAIL": {
        "description": "Default from email address",
        "required": False,
        "default": "noreply@example.com",
        "example": "noreply@example.com",
    },
    # Logging Settings
    "LOG_LEVEL": {
        "description": "Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        "required": False,
        "default": "INFO",
        "example": "INFO",
        "validation": lambda v, env: (
            v.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL",
        ),
    },
    # JWT Settings
    "JWT_ACCESS_TOKEN_LIFETIME_MINUTES": {
        "description": "JWT access token lifetime in minutes",
        "required": False,
        "default": "15",
        "example": "15",
        "validation": lambda v, env: (
            v.isdigit() and int(v) > 0,
            "JWT_ACCESS_TOKEN_LIFETIME_MINUTES must be a positive integer",
        ),
    },
    "JWT_REFRESH_TOKEN_LIFETIME_DAYS": {
        "description": "JWT refresh token lifetime in days",
        "required": False,
        "default": "7",
        "example": "7",
        "validation": lambda v, env: (
            v.isdigit() and int(v) > 0,
            "JWT_REFRESH_TOKEN_LIFETIME_DAYS must be a positive integer",
        ),
    },
    # Security Settings (Production)
    "SECURE_SSL_REDIRECT": {
        "description": "Redirect all HTTP requests to HTTPS",
        "required": False,
        "default": "False",
        "example": "True",
    },
    "SESSION_COOKIE_SECURE": {
        "description": "Use secure cookies (HTTPS only)",
        "required": False,
        "default": "False",
        "example": "True",
    },
    "CSRF_COOKIE_SECURE": {
        "description": "Use secure CSRF cookies (HTTPS only)",
        "required": False,
        "default": "False",
        "example": "True",
    },
}


def get_environment() -> str:
    """
    Detect the current environment from DJANGO_SETTINGS_MODULE.

    Returns:
        Environment name: 'development', 'production', or 'testing'

    Examples:
        >>> os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'
        >>> get_environment()
        'production'
    """
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.development")

    if "production" in settings_module:
        return "production"
    elif "testing" in settings_module or "test" in settings_module:
        return "testing"
    else:
        return "development"


def get_config(
    key: str,
    default: Optional[Any] = None,
    cast: Optional[Callable[[str], T]] = None,
    required: bool = False,
) -> Union[str, T, None]:
    """
    Get configuration value from environment with optional type casting.

    Args:
        key: Environment variable name
        default: Default value if not set (None if not provided)
        cast: Function to cast the value (e.g., int, bool)
        required: If True, raises error when variable not set

    Returns:
        Configuration value (cast to specified type if cast provided)

    Raises:
        ConfigurationError: If required variable is missing

    Examples:
        >>> get_config('DB_PORT', default=5432, cast=int)
        5432
        >>> get_config('DEBUG', default=False, cast=bool)
        True
    """
    try:
        if cast:
            result: T = config(key, default=default, cast=cast)  # type: ignore[assignment]
            return result
        value: str = config(key, default=default)  # type: ignore[assignment]
        return value
    except Exception as e:
        if required:
            raise ConfigurationError(
                f"Required configuration variable '{key}' is not set. "
                f"Please set it in your .env file or environment variables. "
                f"Error: {str(e)}"
            ) from e
        if default is not None:
            return default
        raise


def validate_configuration(environment: Optional[str] = None) -> None:
    """
    Validate all configuration variables for the current environment.

    Checks that:
    - All required variables are set
    - All variables pass their validation rules
    - Production has secure configurations
    - Variable types are correct

    Args:
        environment: Environment to validate for (auto-detected if None)

    Raises:
        ConfigurationError: If configuration is invalid with detailed message

    Examples:
        >>> validate_configuration('production')  # Validates production config
        >>> validate_configuration()  # Auto-detects environment and validates
    """
    if environment is None:
        environment = get_environment()

    missing_vars: list[str] = []
    invalid_vars: list[tuple[str, str]] = []

    # Special handling for testing environment - minimal requirements
    if environment == "testing":
        # Testing environment uses in-memory databases and has minimal requirements
        return

    # Check each registered configuration variable
    for var_name, var_config in CONFIG_VARIABLES.items():
        # Determine if required for this environment
        is_required = var_config.get("required", False)
        required_in = var_config.get("required_in", [])

        if environment in required_in:
            is_required = True

        # Get value from environment
        value = os.environ.get(var_name)

        # Check if required variable is missing
        if is_required and not value:
            # For development, use default if available
            if environment == "development" and "default" in var_config:
                continue
            missing_vars.append(var_name)
            continue

        # Skip validation if value not set and not required
        if not value:
            continue

        # Run validation function if provided
        if "validation" in var_config:
            is_valid, error_message = var_config["validation"](value, environment)
            if not is_valid:
                invalid_vars.append((var_name, error_message))

        # Run production-specific validation
        if environment == "production" and "production_validation" in var_config:
            is_valid, error_message = var_config["production_validation"](value)
            if not is_valid:
                invalid_vars.append((var_name, error_message))

    # Production-specific checks
    if environment == "production":
        allowed_hosts = os.environ.get("ALLOWED_HOSTS", "")
        if not allowed_hosts:
            missing_vars.append("ALLOWED_HOSTS")

    # Build error message if there are issues
    if missing_vars or invalid_vars:
        error_parts = [f"\nConfiguration validation failed for '{environment}' environment:\n"]

        if missing_vars:
            error_parts.append("Missing required configuration variables:")
            for var in missing_vars:
                var_info = CONFIG_VARIABLES.get(var, {})
                desc = var_info.get("description", "No description")
                example = var_info.get("example", "")
                error_parts.append(f"  - {var}: {desc}")
                if example:
                    error_parts.append(f"    Example: {var}={example}")

        if invalid_vars:
            error_parts.append("\nInvalid configuration values:")
            for var, message in invalid_vars:
                error_parts.append(f"  - {var}: {message}")

        error_parts.append("\nPlease update your .env file or environment variables and try again.")
        error_parts.append("See docs/CONFIGURATION.md for detailed configuration documentation.")

        raise ConfigurationError("\n".join(error_parts))


def get_all_config_variables() -> Dict[str, Dict[str, Any]]:
    """
    Get all registered configuration variables with their metadata.

    Returns:
        Dictionary of all configuration variables with metadata

    Examples:
        >>> vars = get_all_config_variables()
        >>> 'SECRET_KEY' in vars
        True
        >>> vars['SECRET_KEY']['description']
        'Django secret key for cryptographic signing'
    """
    return CONFIG_VARIABLES.copy()


def print_configuration_help() -> None:
    """
    Print helpful information about all configuration variables.

    Useful for documentation and troubleshooting.
    """
    print("\n=== Configuration Variables ===\n")

    for var_name, var_config in sorted(CONFIG_VARIABLES.items()):
        required = var_config.get("required", False)
        required_in = var_config.get("required_in", [])
        default = var_config.get("default", "")
        description = var_config.get("description", "No description")
        example = var_config.get("example", "")
        sensitive = var_config.get("sensitive", False)

        print(f"{var_name}")
        print(f"  Description: {description}")

        if required or required_in:
            req_str = "Required"
            if required_in:
                req_str += f" in {', '.join(required_in)}"
            print(f"  {req_str}")
        else:
            print("  Optional")

        if default:
            if sensitive:
                print(f"  Default: (sensitive - not shown)")
            else:
                print(f"  Default: {default}")

        if example and not sensitive:
            print(f"  Example: {example}")

        print()


def check_configuration_on_startup() -> None:
    """
    Check configuration on application startup.

    This should be called early in the application lifecycle to catch
    configuration errors before the application starts handling requests.

    Prints validation results and exits if configuration is invalid.
    """
    environment = get_environment()

    print(f"\nValidating configuration for '{environment}' environment...")

    try:
        validate_configuration(environment)
        print(f"✓ Configuration validation passed for '{environment}' environment\n")
    except ConfigurationError as e:
        print(f"\n✗ Configuration validation failed:\n{str(e)}\n", file=sys.stderr)
        sys.exit(1)
