"""
Development settings for backend project.

These settings are used during local development.
"""

from typing import Any, cast

from .base import *  # noqa: F401, F403

# ============================================================================
# Security Settings
# ============================================================================

DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ["*"]

# ============================================================================
# CORS Configuration - Permissive for development
# ============================================================================

CORS_ALLOW_ALL_ORIGINS = True

# ============================================================================
# Development Tools
# ============================================================================

# Add Django Debug Toolbar in development
INSTALLED_APPS += [  # noqa: F405
    "debug_toolbar",
]

MIDDLEWARE = [  # noqa: F405
    "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE  # noqa: F405

# Show toolbar for all IPs in development
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# ============================================================================
# Database - Use SQLite for quick local development
# ============================================================================

# Uncomment to use SQLite instead of PostgreSQL in development
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
#     }
# }

# ============================================================================
# Email Backend - Use console backend in development
# ============================================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ============================================================================
# REST Framework - Add browsable API in development
# ============================================================================

# Cast REST_FRAMEWORK to help MyPy with type inference
_rest_framework = cast(dict[str, Any], REST_FRAMEWORK)  # noqa: F405

_rest_framework["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# ============================================================================
# Logging - More verbose in development
# ============================================================================

# Cast LOGGING to help MyPy with type inference
_logging = cast(dict[str, Any], LOGGING)  # noqa: F405

_logging["loggers"]["django.db.backends"] = {
    "handlers": ["console"],
    "level": "DEBUG",
    "propagate": False,
}
