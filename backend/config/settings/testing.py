"""
Django settings for backend project - Testing environment.
"""

import os

from .base import *

# Testing is not production - enable debug features for better test output
DEBUG = True

# Allow all hosts in testing (required for test client)
ALLOWED_HOSTS = ["*"]

# Use PostgreSQL for CI/integration tests, SQLite for local unit tests
# CI sets USE_POSTGRES_FOR_TESTS=true to test with real PostgreSQL
# Local development can use fast SQLite tests by default
USE_POSTGRES_FOR_TESTS = os.environ.get("USE_POSTGRES_FOR_TESTS", "false").lower() == "true"

if USE_POSTGRES_FOR_TESTS:
    # Use PostgreSQL for CI and integration tests
    # Reads credentials from environment variables set by CI:
    # - DB_NAME: Database name (e.g., test_backend_db)
    # - DB_USER: Database user (e.g., test_user in CI, not root)
    # - DB_PASSWORD: Database password (e.g., test_password)
    # - DB_HOST: Database host (defaults to localhost)
    # - DB_PORT: Database port (defaults to 5432)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": get_config("DB_NAME", default="test_backend_db"),
            "USER": get_config("DB_USER", default="test_user"),
            "PASSWORD": get_config("DB_PASSWORD", default="test_password"),
            "HOST": get_config("DB_HOST", default="localhost"),
            "PORT": get_config("DB_PORT", default="5432"),
            "ATOMIC_REQUESTS": True,  # Each test runs in a transaction
            "CONN_MAX_AGE": 0,  # Disable connection pooling for test isolation
            # No custom OPTIONS needed - Django manages transaction isolation automatically
            "TEST": {  # type: ignore[dict-item]
                # Django will create test_<DB_NAME> automatically
                # Ensure test database has a predictable name
                "NAME": get_config("TEST_DB_NAME", default=None),
                # Preserve test database between runs when --reuse-db is used
                "SERIALIZE": False,  # Faster tests - no need to serialize data
                # Use template database for faster test database creation
                "TEMPLATE": "template0",
                "CHARSET": "UTF8",
            },
        }
    }
else:
    # Use in-memory SQLite for faster local unit tests
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "ATOMIC_REQUESTS": True,  # Each test runs in a transaction
            "CONN_MAX_AGE": 0,  # Disable connection pooling for test isolation
            "TEST": {  # type: ignore[dict-item]
                "NAME": ":memory:",  # Ensure in-memory database for each test worker
                "SERIALIZE": False,  # Faster tests
            },
        }
    }

# Use simple password hasher for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


# Disable migrations for tests (use --create-db to enable)
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


# MIGRATION_MODULES = DisableMigrations()

# Use in-memory cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Disable Celery in tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable throttling in tests
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []

# Disable rate limiting in tests (django-ratelimit)
RATELIMIT_ENABLE = False

# Simpler logging in tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "CRITICAL",
    },
}

# Force DEBUG=True for testing (must be at end to override any imports)
DEBUG = True

# CSRF_COOKIE_SECURE should be True in production (DEBUG=False)
# For testing purposes, we set it to True even though DEBUG=True
# to ensure production settings are validated correctly
CSRF_COOKIE_SECURE = True
