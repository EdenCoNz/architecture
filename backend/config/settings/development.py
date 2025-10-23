"""
Django settings for backend project - Development environment.
"""

from typing import Any

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Development-specific apps
INSTALLED_APPS += [
    "debug_toolbar",
    "django_extensions",
]

# Development-specific middleware
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

# Django Debug Toolbar Configuration
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# More verbose logging in development
LOGGING["root"]["level"] = "DEBUG"  # type: ignore[index]

# Log SQL queries in development
LOGGING["loggers"]["django.db.backends"]["level"] = "DEBUG"  # type: ignore[index]

# More detailed request logging
LOGGING["loggers"]["apps.middleware"]["level"] = "DEBUG"  # type: ignore[index]

# Lower threshold for slow request warnings in development
SLOW_REQUEST_THRESHOLD_MS = 500

# Disable SSL redirect in development
SECURE_SSL_REDIRECT = False

# Email backend for development (console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Static files - use default storage in development
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
