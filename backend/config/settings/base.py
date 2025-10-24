"""
Django settings for backend project - Base settings.
All common settings shared across environments.
"""

from datetime import timedelta
from pathlib import Path

# Import configuration helpers
from config.env_config import get_config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Uses validated configuration from env_config module
SECRET_KEY = get_config(
    "SECRET_KEY", default="django-insecure-development-key-change-in-production"
)

# Application definition
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
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "django_redis",
]

LOCAL_APPS = [
    "apps.core",
    "apps.api",
    "apps.users",
    "apps.utils",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Static files
    "corsheaders.middleware.CorsMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",  # Security headers (Story #9)
    "apps.core.middleware.RequestLoggingMiddleware",  # Request logging
    "apps.core.middleware.PerformanceLoggingMiddleware",  # Performance monitoring
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_ratelimit.middleware.RatelimitMiddleware",  # Rate limiting (Story #3)
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_config("DB_NAME", default="backend_db"),
        "USER": get_config("DB_USER", default="postgres"),
        "PASSWORD": get_config("DB_PASSWORD", default="postgres"),
        "HOST": get_config("DB_HOST", default="localhost"),
        "PORT": get_config("DB_PORT", default="5432"),
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": 600,  # Connection pooling
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "users.User"

# REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Simple JWT Configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = get_config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
    cast=lambda v: [s.strip() for s in v.split(",")],
)
CORS_ALLOW_CREDENTIALS = True

# Cache Configuration (Redis)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": get_config("REDIS_URL", default="redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "backend",
        "TIMEOUT": 300,  # 5 minutes default
    }
}

# Session Configuration
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Celery Configuration
CELERY_BROKER_URL = get_config("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = get_config("CELERY_RESULT_BACKEND", default="redis://127.0.0.1:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# Email Configuration (to be configured in production)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Performance monitoring threshold (in milliseconds)
SLOW_REQUEST_THRESHOLD_MS = get_config("SLOW_REQUEST_THRESHOLD_MS", default=1000, cast=int)

# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} [{name}] {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "console_debug": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file_general": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "general.log",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "file_errors": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "errors.log",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "file_middleware": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "requests.log",
            "maxBytes": 1024 * 1024 * 20,  # 20MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        "file_exceptions": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "exceptions.log",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        # Django loggers
        "django": {
            "handlers": ["console", "file_general"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "file_errors"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console_debug"],
            "level": "DEBUG",
            "propagate": False,
        },
        # Application loggers
        "apps.middleware": {
            "handlers": ["console", "file_middleware"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.exceptions": {
            "handlers": ["console", "file_exceptions"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps.api": {
            "handlers": ["console", "file_general"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.core": {
            "handlers": ["console", "file_general"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.users": {
            "handlers": ["console", "file_general"],
            "level": "INFO",
            "propagate": False,
        },
        # Third-party loggers
        "celery": {
            "handlers": ["console", "file_general"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "file_general"],
        "level": "INFO",
    },
}

# API Documentation (drf-spectacular)
SPECTACULAR_SETTINGS = {
    "TITLE": "Backend API",
    "DESCRIPTION": (
        "Comprehensive API documentation for the backend application. "
        "This API provides endpoints for user authentication, health monitoring, "
        "and various application features. All endpoints follow RESTful principles "
        "and return JSON responses."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    # Format Settings - Default to JSON for better API compatibility
    "DEFAULT_GENERATOR_CLASS": "drf_spectacular.generators.SchemaGenerator",
    "SERVE_URLCONF": None,
    # API Information
    "CONTACT": {
        "name": "API Support",
        "email": "api-support@example.com",
    },
    "LICENSE": {
        "name": "MIT",
    },
    # Schema Generation Settings
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    # UI Settings
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "filter": True,
        "tagsSorter": "alpha",
        "operationsSorter": "alpha",
        "docExpansion": "none",
        "defaultModelsExpandDepth": 3,
        "defaultModelExpandDepth": 3,
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
    },
    # Security Schemes
    "SECURITY": [{"bearerAuth": []}],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": (
                    "JWT authentication. Obtain tokens via the /api/v1/auth/login/ endpoint. "
                    "Include the token in the Authorization header as: Bearer <token>"
                ),
            }
        }
    },
    # Schema Customization
    "ENUM_NAME_OVERRIDES": {},
    "POSTPROCESSING_HOOKS": [],
    "PREPROCESSING_HOOKS": [],
    # Tags and Grouping
    "TAGS": [
        {"name": "Health", "description": "Health check and system status endpoints"},
        {"name": "Authentication", "description": "User authentication and authorization"},
        {"name": "Users", "description": "User profile and account management"},
        {"name": "Configuration", "description": "Runtime configuration endpoints"},
    ],
    # Sorting and Display
    "SORT_OPERATIONS": True,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": None,
}

# Security Settings (Story #9 - Security Best Practices)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# CSRF Protection Settings
CSRF_COOKIE_SECURE = get_config("CSRF_COOKIE_SECURE", default=False, cast=bool)
CSRF_COOKIE_HTTPONLY = False  # Must be False for SPA to access
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = get_config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

# Session Security
SESSION_COOKIE_SECURE = get_config("SESSION_COOKIE_SECURE", default=False, cast=bool)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# Rate Limiting Configuration
RATELIMIT_ENABLE = get_config("RATELIMIT_ENABLE", default=True, cast=bool)
RATELIMIT_USE_CACHE = "default"
RATELIMIT_VIEW = "apps.core.middleware.ratelimit_view"

# Content Security Policy (CSP) is now handled by SecurityHeadersMiddleware
# Additional security headers are also handled by the middleware
