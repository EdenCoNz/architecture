"""
Production settings for backend project.

These settings are used in production deployment.
"""

from typing import Any, cast

from .base import *  # noqa: F401, F403

# ============================================================================
# Security Settings
# ============================================================================

DEBUG = False

# Security middleware settings
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)  # noqa: F405
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# ============================================================================
# CORS Configuration - Restrictive in production
# ============================================================================

# CORS_ALLOWED_ORIGINS is defined in base.py from environment variable

# ============================================================================
# Email Configuration
# ============================================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")  # noqa: F405
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)  # noqa: F405
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)  # noqa: F405
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")  # noqa: F405
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")  # noqa: F405
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@example.com")  # noqa: F405

# ============================================================================
# Caching Configuration
# ============================================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6379/1"),  # noqa: F405
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "backend",
    }
}

# ============================================================================
# Session Configuration
# ============================================================================

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ============================================================================
# REST Framework - Production optimizations
# ============================================================================

# Cast REST_FRAMEWORK to help MyPy with type inference
_rest_framework = cast(dict[str, Any], REST_FRAMEWORK)  # noqa: F405

# Remove browsable API in production
_rest_framework["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
]

# Add throttling in production
_rest_framework["DEFAULT_THROTTLE_CLASSES"] = [
    "rest_framework.throttling.AnonRateThrottle",
    "rest_framework.throttling.UserRateThrottle",
]

_rest_framework["DEFAULT_THROTTLE_RATES"] = {
    "anon": config("THROTTLE_ANON", default="100/hour"),  # noqa: F405
    "user": config("THROTTLE_USER", default="1000/hour"),  # noqa: F405
}

# ============================================================================
# Logging - Production logging configuration
# ============================================================================

# Cast LOGGING to help MyPy with type inference
_logging = cast(dict[str, Any], LOGGING)  # noqa: F405

_logging["handlers"]["file"] = {
    "class": "logging.handlers.RotatingFileHandler",
    "filename": BASE_DIR / "logs" / "django.log",  # noqa: F405
    "maxBytes": 1024 * 1024 * 15,  # 15MB
    "backupCount": 10,
    "formatter": "verbose",
}

_logging["root"]["handlers"] = ["console", "file"]

_logging["loggers"]["django"]["handlers"] = ["console", "file"]
_logging["loggers"]["django.server"]["handlers"] = ["console", "file"]
