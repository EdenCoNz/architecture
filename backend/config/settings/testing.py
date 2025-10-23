"""
Django settings for backend project - Testing environment.
"""

import os

from .base import *

# Use PostgreSQL for acceptance tests, SQLite for unit tests (based on environment variable)
# This allows fast unit tests while still testing PostgreSQL functionality in acceptance tests
USE_POSTGRES_FOR_TESTS = os.environ.get("USE_POSTGRES_FOR_TESTS", "false").lower() == "true"

if USE_POSTGRES_FOR_TESTS:
    # Use PostgreSQL for acceptance tests that verify database-specific functionality
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": get_config("DB_NAME", default="backend_test_db"),
            "USER": get_config("DB_USER", default="postgres"),
            "PASSWORD": get_config("DB_PASSWORD", default="postgres"),
            "HOST": get_config("DB_HOST", default="localhost"),
            "PORT": get_config("DB_PORT", default="5432"),
            "ATOMIC_REQUESTS": True,
            "CONN_MAX_AGE": 600,  # Connection pooling
            "TEST": {
                "NAME": "test_backend_db",  # Use a separate test database
            },
        }
    }
else:
    # Use in-memory SQLite for faster unit tests
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "ATOMIC_REQUESTS": True,
            # SQLite doesn't support CONN_MAX_AGE in the same way, but we set it for compatibility
            "CONN_MAX_AGE": 600,
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
