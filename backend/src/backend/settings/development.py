"""
Development settings for backend project.

These settings are used during local development.
"""

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

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# ============================================================================
# Logging - More verbose in development
# ============================================================================

LOGGING["loggers"]["django.db.backends"] = {  # noqa: F405
    "handlers": ["console"],
    "level": "DEBUG",
    "propagate": False,
}
