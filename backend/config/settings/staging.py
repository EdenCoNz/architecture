"""
Django settings for backend project - Staging environment.
Staging should closely match production to catch issues before production deployment.
"""

from typing import Any

from config.env_config import get_config

from .base import *

# Debug mode should be False in staging to match production
DEBUG = get_config("DEBUG", default=False, cast=bool)

# Allowed hosts - must be configured for staging domain
ALLOWED_HOSTS = get_config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

# Staging-specific apps (same as production)
INSTALLED_APPS += [
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
]

# Security Settings
# Note: SECURE_SSL_REDIRECT intentionally set to False in staging to allow both HTTP and HTTPS
# Production should always set this to True
SECURE_SSL_REDIRECT = get_config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = get_config("SESSION_COOKIE_SECURE", default=True, cast=bool)
CSRF_COOKIE_SECURE = get_config("CSRF_COOKIE_SECURE", default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Silence security.W008 warning if SSL redirect is disabled in staging
# This is intentional to allow both HTTP and HTTPS for testing
if not SECURE_SSL_REDIRECT:
    SILENCED_SYSTEM_CHECKS = ["security.W008"]

# CORS Configuration for Staging
# Override development defaults with strict staging settings
CORS_ALLOWED_ORIGINS = get_config(
    "CORS_ALLOWED_ORIGINS",
    default="",  # Must be explicitly set in staging
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)
CORS_ALLOW_ALL_ORIGINS = False  # Never allow all origins in staging
CORS_ALLOW_CREDENTIALS = True

# Ensure CORS_ALLOWED_ORIGINS is not empty in staging
if not CORS_ALLOWED_ORIGINS:
    import warnings

    warnings.warn(
        "CORS_ALLOWED_ORIGINS is empty in staging. "
        "Set the CORS_ALLOWED_ORIGINS environment variable."
    )

# CSRF Configuration for Staging
CSRF_TRUSTED_ORIGINS = get_config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

# Rate Limiting in Staging (always enabled to match production)
RATELIMIT_ENABLE = True

# Static files - use WhiteNoise for staging (same as production)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Staging logging configuration
# More verbose than production but less than development
# Type ignore needed because LOGGING is imported via * and seen as object by mypy
LOGGING["root"]["level"] = "INFO"  # type: ignore[index]

# Use JSON formatter for staging logs (better for log aggregation)
LOGGING["handlers"]["file_general"]["formatter"] = "json"  # type: ignore[index]
LOGGING["handlers"]["file_errors"]["formatter"] = "json"  # type: ignore[index]
LOGGING["handlers"]["file_middleware"]["formatter"] = "json"  # type: ignore[index]
LOGGING["handlers"]["file_exceptions"]["formatter"] = "json"  # type: ignore[index]

# Increase log file sizes and retention in staging
LOGGING["handlers"]["file_general"]["maxBytes"] = 1024 * 1024 * 50  # type: ignore[index]  # 50MB
LOGGING["handlers"]["file_general"]["backupCount"] = 15  # type: ignore[index]

LOGGING["handlers"]["file_errors"]["maxBytes"] = 1024 * 1024 * 50  # type: ignore[index]  # 50MB
LOGGING["handlers"]["file_errors"]["backupCount"] = 15  # type: ignore[index]

LOGGING["handlers"]["file_middleware"]["maxBytes"] = (
    1024 * 1024 * 100  # type: ignore[index]  # 100MB
)
LOGGING["handlers"]["file_middleware"]["backupCount"] = 20  # type: ignore[index]

# Log warnings and above to console in staging
LOGGING["handlers"]["console"]["level"] = "WARNING"  # type: ignore[index]

# Staging threshold for slow requests (same as production)
SLOW_REQUEST_THRESHOLD_MS = get_config("SLOW_REQUEST_THRESHOLD_MS", default=2000, cast=int)

# Email Configuration for Staging
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = get_config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = get_config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = get_config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = get_config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = get_config("DEFAULT_FROM_EMAIL", default="noreply-staging@example.com")

# Database connection pooling and optimization (match production)
DATABASES["default"]["CONN_MAX_AGE"] = 600  # type: ignore[index]
DATABASES["default"]["OPTIONS"] = {  # type: ignore[assignment,index]
    "connect_timeout": 10,
}

# Celery - use multiple workers in staging (same as production)
CELERY_WORKER_CONCURRENCY = get_config("CELERY_WORKER_CONCURRENCY", default=4, cast=int)

# Cache - longer timeouts in staging (match production)
CACHES["default"]["TIMEOUT"] = 900  # 15 minutes  # type: ignore[index]

# Optional: Sentry for error tracking in staging
# Uncomment and configure if using Sentry
# if get_config("SENTRY_DSN", default=""):
#     import sentry_sdk
#     from sentry_sdk.integrations.django import DjangoIntegration
#
#     sentry_sdk.init(
#         dsn=get_config("SENTRY_DSN"),
#         integrations=[DjangoIntegration()],
#         environment="staging",
#         traces_sample_rate=get_config("SENTRY_TRACES_SAMPLE_RATE", default=0.1, cast=float),
#         send_default_pii=False,
#     )
