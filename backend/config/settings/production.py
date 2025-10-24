"""
Django settings for backend project - Production environment.
Enhanced with Story #9 security best practices.
"""

from typing import Any

from config.env_config import get_config

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = get_config(
    "ALLOWED_HOSTS", default="", cast=lambda v: [s.strip() for s in v.split(",") if s.strip()]
)

# Production-specific apps
INSTALLED_APPS += [
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
]

# Security Settings (Story #9)
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [
    r"^api/v1/health/$",  # Health check endpoint (Story #188)
    r"^api/v1/health/ready/$",  # Readiness probe endpoint
    r"^api/v1/health/live/$",  # Liveness probe endpoint
]
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# CORS Configuration for Production (Story #9)
# Override development defaults with strict production settings
CORS_ALLOWED_ORIGINS = get_config(
    "CORS_ALLOWED_ORIGINS",
    default="",  # Must be explicitly set in production
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)
CORS_ALLOW_ALL_ORIGINS = False  # Never allow all origins in production
CORS_ALLOW_CREDENTIALS = True

# Ensure CORS_ALLOWED_ORIGINS is not empty in production
if not CORS_ALLOWED_ORIGINS:
    import warnings

    warnings.warn(
        "CORS_ALLOWED_ORIGINS is empty in production. "
        "Set the CORS_ALLOWED_ORIGINS environment variable."
    )

# CSRF Configuration for Production (Story #9)
CSRF_TRUSTED_ORIGINS = get_config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

# Rate Limiting in Production (Story #9)
RATELIMIT_ENABLE = True  # Always enabled in production

# Static files - use WhiteNoise for production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Production logging optimizations
# Type ignore needed because LOGGING is imported via * and seen as object by mypy
LOGGING["root"]["level"] = "WARNING"  # type: ignore[index]

# Use JSON formatter for production logs (better for log aggregation)
LOGGING["handlers"]["file_general"]["formatter"] = "json"  # type: ignore[index]
LOGGING["handlers"]["file_errors"]["formatter"] = "json"  # type: ignore[index]
LOGGING["handlers"]["file_middleware"]["formatter"] = "json"  # type: ignore[index]
LOGGING["handlers"]["file_exceptions"]["formatter"] = "json"  # type: ignore[index]

# Increase log file sizes and retention in production
LOGGING["handlers"]["file_general"]["maxBytes"] = 1024 * 1024 * 50  # type: ignore[index]  # 50MB
LOGGING["handlers"]["file_general"]["backupCount"] = 20  # type: ignore[index]

LOGGING["handlers"]["file_errors"]["maxBytes"] = 1024 * 1024 * 50  # type: ignore[index]  # 50MB
LOGGING["handlers"]["file_errors"]["backupCount"] = 20  # type: ignore[index]

# type: ignore[index]  # 100MB
LOGGING["handlers"]["file_middleware"]["maxBytes"] = 1024 * 1024 * 100
# type: ignore[index]
LOGGING["handlers"]["file_middleware"]["backupCount"] = 30

# Only log errors and above to console in production
LOGGING["handlers"]["console"]["level"] = "ERROR"  # type: ignore[index]

# Higher threshold for slow requests in production
SLOW_REQUEST_THRESHOLD_MS = 2000

# Email Configuration (configure with real SMTP in production)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = get_config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = get_config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = get_config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = get_config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = get_config("DEFAULT_FROM_EMAIL", default="noreply@example.com")

# Database connection pooling and optimization
DATABASES["default"]["CONN_MAX_AGE"] = 600  # type: ignore[index]
DATABASES["default"]["OPTIONS"] = {  # type: ignore[assignment,index]
    "connect_timeout": 10,
}

# Celery - use more workers in production
CELERY_WORKER_CONCURRENCY = 4

# Cache - longer timeouts in production
CACHES["default"]["TIMEOUT"] = 900  # 15 minutes  # type: ignore[index]
