"""
Django base settings for backend project.

This module contains settings that are common across all environments.
Environment-specific settings are in development.py, production.py, and test.py.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

from decouple import Csv, config

# ============================================================================
# Build paths inside the project like this: BASE_DIR / 'subdir'.
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# ============================================================================
# Security Settings
# ============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    "DJANGO_SECRET_KEY",
    default="django-insecure-change-this-in-production-12345678901234567890",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# ============================================================================
# Application definition
# ============================================================================

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
]

LOCAL_APPS: list[str] = [
    # Add your apps here
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ============================================================================
# Middleware
# ============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Serve static files
    "common.middleware.error_handling.ErrorHandlingMiddleware",  # Global error handling
    "common.middleware.request_logging.RequestLoggingMiddleware",  # Request logging
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # CORS headers
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

# ============================================================================
# Templates
# ============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# ============================================================================
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# ============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="backend_db"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="postgres"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": config("DB_CONN_MAX_AGE", default=60, cast=int),
    }
}

# ============================================================================
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ============================================================================
# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
# ============================================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# ============================================================================
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
# ============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise configuration for efficient static file serving
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ============================================================================
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
# ============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================================
# REST Framework Configuration
# https://www.django-rest-framework.org/api-guide/settings/
# ============================================================================

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}

# ============================================================================
# API Documentation with drf-spectacular
# https://drf-spectacular.readthedocs.io/
# ============================================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "Backend API",
    "DESCRIPTION": "Backend API service built with Django REST Framework",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
}

# ============================================================================
# CORS Configuration
# https://github.com/adamchainz/django-cors-headers
# ============================================================================

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
    cast=Csv(),
)

CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# Logging Configuration
# ============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
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
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": config("LOG_LEVEL", default="INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": config("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": config("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "common.middleware": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
