"""
Test settings for backend project.

These settings are used when running tests.
"""

import os

# Set DEBUG environment variable before importing base settings
os.environ["DEBUG"] = "True"

from .base import *  # noqa: F401, F403, E402

# ============================================================================
# Security Settings - Override base settings for testing
# ============================================================================

# Ensure DEBUG is True for tests (override base setting)
DEBUG = True

SECRET_KEY = "test-secret-key-not-for-production"  # noqa: S105

# Override ALLOWED_HOSTS for tests
ALLOWED_HOSTS = ["*"]

# ============================================================================
# Database - Use SQLite for faster tests
# ============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# ============================================================================
# Password Hashing - Use faster hasher for tests
# ============================================================================

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# ============================================================================
# Email Backend - Use memory backend for tests
# ============================================================================

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ============================================================================
# Caching - Use local memory cache for tests
# ============================================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# ============================================================================
# Logging - Minimal logging during tests
# ============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # Allow pytest caplog to work
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
        },
        "common.middleware": {
            "handlers": ["console"],
            "level": "DEBUG",  # Allow all logs for testing
            "propagate": True,  # Allow caplog to capture
        },
    },
}

# ============================================================================
# REST Framework - Test optimizations
# ============================================================================

REST_FRAMEWORK["TEST_REQUEST_DEFAULT_FORMAT"] = "json"  # noqa: F405
