# Django Production Security Best Practices

## Critical Production Settings

### 1. Debug and Environment

```python
# settings/production.py
DEBUG = False  # NEVER True in production
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')  # Specific domains only

# Example .env
# ALLOWED_HOSTS=example.com,www.example.com,api.example.com
```

**Why**: `DEBUG=True` exposes environment variables, database queries, and stack traces to attackers.

### 2. Secret Key Management

```python
# NEVER hardcode secrets
SECRET_KEY = env('DJANGO_SECRET_KEY')  # From environment variable

# Generate strong secret key
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

**Tools for Secret Management**:
- **django-environ**: Load from .env files
- **docker secrets**: For Docker/Swarm
- **AWS Secrets Manager/Parameter Store**: For AWS
- **HashiCorp Vault**: Enterprise solution
- **django-encrypted-secrets**: Encrypted secrets in repo

### 3. HTTPS and Security Headers

```python
# Force HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'

# Additional security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### 4. CORS Configuration

```python
# Install django-cors-headers
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... other middleware
]

# Production CORS - restrictive by default
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
# Example: CORS_ALLOWED_ORIGINS=https://app.example.com,https://www.example.com

# For development only
# CORS_ALLOW_ALL_ORIGINS = True  # NEVER in production

# Fine-grained control
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.example\.com$",
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

## CSRF Protection

### 1. Built-in CSRF Middleware

```python
# Enabled by default
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',  # Should be here
    # ...
]
```

### 2. CSRF with DRF

```python
# For session-based auth (same-origin requests)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# CSRF exempt for JWT/Token auth (different origin)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# Custom CSRF for specific views
from django.views.decorators.csrf import csrf_exempt, csrf_protect

@csrf_exempt  # Use sparingly
def api_view(request):
    pass
```

### 3. CSRF Token in Frontend

```javascript
// Fetch CSRF token
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Include in fetch request
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
});
```

## Authentication Security

### 1. JWT Best Practices

```python
from datetime import timedelta

SIMPLE_JWT = {
    # Short-lived access tokens
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),

    # Token rotation
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    # Security
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': env('JWT_SECRET_KEY'),

    # Token claims
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Install token blacklist
INSTALLED_APPS += ['rest_framework_simplejwt.token_blacklist']
```

**Security Rules**:
- Always use HTTPS with JWT
- Keep access tokens short-lived (5-15 minutes)
- Store refresh tokens securely (httpOnly cookies or secure storage)
- Implement token blacklist for logout
- Rotate tokens on refresh

### 2. Password Security

```python
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}  # Stronger than default 8
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Argon2 password hasher (strongest)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

### 3. OAuth2 Integration

```python
# Use django-oauth-toolkit for OAuth2 provider
INSTALLED_APPS += ['oauth2_provider']

OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 600,
    'REFRESH_TOKEN_EXPIRE_SECONDS': 86400,
    'ROTATE_REFRESH_TOKEN': True,
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
    },
}

# For social auth (Google, GitHub, etc.)
# Use django-allauth or social-auth-app-django
```

## API Security

### 1. Rate Limiting (Essential)

```python
# Redis-backed throttling for production
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',      # Unauthenticated
        'user': '10000/day',     # Authenticated
    }
}
```

**Custom throttling for sensitive endpoints**:
```python
from rest_framework.throttling import UserRateThrottle

class LoginRateThrottle(UserRateThrottle):
    rate = '5/hour'  # Prevent brute force

class PasswordResetThrottle(UserRateThrottle):
    rate = '3/hour'

class SignupRateThrottle(AnonRateThrottle):
    rate = '10/day'
```

### 2. Input Validation and Sanitization

```python
from rest_framework import serializers
from django.core.validators import EmailValidator, URLValidator

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[EmailValidator()],
        required=True
    )
    website = serializers.URLField(
        validators=[URLValidator()],
        required=False,
        allow_blank=True
    )

    def validate_username(self, value):
        # Custom validation
        if len(value) < 3:
            raise serializers.ValidationError("Username too short")
        # Sanitize input
        return value.strip().lower()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'website']
        read_only_fields = ['id']
```

### 3. SQL Injection Prevention

Django's ORM prevents SQL injection by default. **Avoid**:

```python
# DANGEROUS - Never do this
User.objects.raw(f"SELECT * FROM users WHERE username = '{username}'")

# SAFE - Use parameterized queries
User.objects.raw("SELECT * FROM users WHERE username = %s", [username])

# BEST - Use ORM
User.objects.filter(username=username)
```

### 4. XSS Prevention

```python
# Django templates auto-escape by default
# {{ user_input }}  <- Safe, auto-escaped

# To mark safe (use carefully)
from django.utils.safestring import mark_safe
content = mark_safe(sanitized_html)

# DRF JSON responses are not vulnerable to XSS
# But validate/sanitize HTML input
from bleach import clean

class ArticleSerializer(serializers.ModelSerializer):
    def validate_content(self, value):
        # Strip dangerous HTML
        allowed_tags = ['p', 'br', 'strong', 'em', 'a']
        return clean(value, tags=allowed_tags, strip=True)
```

## Permissions and Authorization

### 1. Restrictive Defaults

```python
# Global restrictive default
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Open up specific endpoints
class PublicArticleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Article.objects.filter(published=True)
```

### 2. Object-Level Permissions

```python
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only for owner
        return obj.owner == request.user

class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
```

### 3. Role-Based Access Control (RBAC)

```python
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

# Use django-guardian for object-level permissions
# or implement custom user groups/roles
```

## Database Security

### 1. Database Credentials

```python
# Use environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

# Separate read-only user for reports
DATABASES['readonly'] = {
    # ... same config but different USER
    'USER': env('DB_READONLY_USER'),
}
```

### 2. Connection Security

```python
# SSL connection to database
DATABASES = {
    'default': {
        # ...
        'OPTIONS': {
            'sslmode': 'require',
            'sslrootcert': '/path/to/ca-cert',
        }
    }
}
```

## Logging and Monitoring

### 1. Security Logging

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/security.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
```

### 2. Failed Authentication Monitoring

```python
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
import logging

logger = logging.getLogger('security')

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    logger.warning(
        f'Failed login attempt for {credentials.get("username")} '
        f'from {request.META.get("REMOTE_ADDR")}'
    )
```

### 3. Sentry Integration

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=env('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,  # Don't send user data
    environment=env('ENVIRONMENT', default='production'),
)
```

## Security Checklist

- [ ] `DEBUG = False` in production
- [ ] `ALLOWED_HOSTS` configured with specific domains
- [ ] `SECRET_KEY` from environment variables, not hardcoded
- [ ] HTTPS enforced (`SECURE_SSL_REDIRECT = True`)
- [ ] HSTS enabled with long duration
- [ ] Secure cookies (`SESSION_COOKIE_SECURE = True`)
- [ ] CORS configured restrictively
- [ ] CSRF protection enabled and tested
- [ ] Rate limiting on all APIs (Redis-backed)
- [ ] Strong password validation
- [ ] Argon2 password hasher
- [ ] Short-lived JWT tokens (if using JWT)
- [ ] Token blacklist implemented
- [ ] Input validation on all serializers
- [ ] Parameterized queries (no raw SQL with f-strings)
- [ ] Restrictive default permissions
- [ ] Object-level permissions where needed
- [ ] Database credentials in environment variables
- [ ] SSL connection to database
- [ ] Security logging configured
- [ ] Sentry or error monitoring enabled
- [ ] Regular security audits (`python manage.py check --deploy`)
- [ ] Dependency vulnerability scanning (safety, snyk)
- [ ] `.env` files in `.gitignore`
- [ ] No sensitive data in version control
