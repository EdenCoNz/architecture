# Configuration Management Guide

This guide explains how to configure the backend API across different environments (development, testing, production).

## Table of Contents

- [Overview](#overview)
- [Environment Detection](#environment-detection)
- [Configuration Variables](#configuration-variables)
- [Adding New Configuration](#adding-new-configuration)
- [Validation and Error Messages](#validation-and-error-messages)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The backend API uses environment-based configuration management that:

- Loads settings from environment variables (via `.env` files)
- Validates configuration on startup with clear error messages
- Supports different configurations per environment (dev, test, prod)
- Never hardcodes sensitive values (passwords, API keys, secrets)
- Provides type casting and default values
- Documents all configuration options

### Key Features

1. **Environment Detection**: Automatically detects environment from `DJANGO_SETTINGS_MODULE`
2. **Validation**: Validates all required settings on startup
3. **Type Safety**: Supports type casting (int, bool, list, etc.)
4. **Clear Errors**: Provides actionable error messages when configuration is missing/invalid
5. **Documentation**: All variables documented with descriptions and examples
6. **Security**: Enforces secure configurations in production

## Environment Detection

The system automatically detects the environment from the `DJANGO_SETTINGS_MODULE` environment variable:

```bash
# Development (default)
export DJANGO_SETTINGS_MODULE=config.settings.development

# Testing
export DJANGO_SETTINGS_MODULE=config.settings.testing

# Staging
export DJANGO_SETTINGS_MODULE=config.settings.staging

# Production
export DJANGO_SETTINGS_MODULE=config.settings.production
```

If `DJANGO_SETTINGS_MODULE` is not set, it defaults to **development**.

### Supported Environments

| Environment | Purpose | Security Level | Configuration File |
|------------|---------|----------------|-------------------|
| Development | Local development | Low | `.env` |
| Testing | Automated tests | Minimal | Built-in |
| Staging | Pre-production testing | Production-like | `.env.staging` |
| Production | Live deployment | High | `.env.production` |

## Configuration Variables

All configuration variables are defined in `config/env_config.py` with full metadata.

### Required Variables (All Environments)

These variables must be set in development and production:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key for cryptographic signing | (generate using `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DB_NAME` | Database name | `backend_db` |
| `DB_USER` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | (secure password) |

**Production/Staging Requirements**:
- `SECRET_KEY` must be at least 50 characters
- `SECRET_KEY` cannot contain "django-insecure"
- `ALLOWED_HOSTS` must be set
- Strong database passwords required

### Optional Variables (With Defaults)

These variables have sensible defaults but can be customized:

#### Django Core

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DEBUG` | Enable debug mode | `True` (dev), `False` (prod) | `False` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` | `example.com,api.example.com` |

#### Database

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DB_HOST` | Database host | `localhost` | `db.example.com` |
| `DB_PORT` | Database port | `5432` | `5432` |

#### Redis Cache

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `REDIS_URL` | Redis connection URL | `redis://127.0.0.1:6379/1` | `redis://redis:6379/1` |

#### Celery

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CELERY_BROKER_URL` | Celery broker URL | `redis://127.0.0.1:6379/0` | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://127.0.0.1:6379/0` | `redis://redis:6379/0` |

#### CORS

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CORS_ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:3000,...` | `https://example.com` |

#### Email

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `EMAIL_HOST` | Email server host | `smtp.gmail.com` | `smtp.gmail.com` |
| `EMAIL_PORT` | Email server port | `587` | `587` |
| `EMAIL_HOST_USER` | Email username | (empty) | `user@example.com` |
| `EMAIL_HOST_PASSWORD` | Email password | (empty) | (secure password) |
| `DEFAULT_FROM_EMAIL` | Default from address | `noreply@example.com` | `noreply@example.com` |

#### Logging

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `WARNING`, `ERROR` |

#### JWT

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | Access token lifetime (minutes) | `15` | `30` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Refresh token lifetime (days) | `7` | `14` |

#### Security (Production)

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SECURE_SSL_REDIRECT` | Redirect HTTP to HTTPS | `False` | `True` |
| `SESSION_COOKIE_SECURE` | Secure session cookies | `False` | `True` |
| `CSRF_COOKIE_SECURE` | Secure CSRF cookies | `False` | `True` |

## Adding New Configuration

To add a new configuration variable:

### 1. Register in `config/env_config.py`

Add to the `CONFIG_VARIABLES` dictionary:

```python
CONFIG_VARIABLES = {
    # ... existing variables ...

    "YOUR_NEW_VARIABLE": {
        "description": "Description of what this variable does",
        "required": False,  # or True if always required
        "required_in": ["production"],  # List of environments where required
        "default": "default_value",  # Default if not set
        "example": "example_value",  # Example for documentation
        "sensitive": False,  # True if contains secrets
        "validation": lambda v, env: (
            # Validation logic (return tuple of bool and error message)
            len(v) > 0,
            "YOUR_NEW_VARIABLE cannot be empty"
        ),
        "production_validation": lambda v: (
            # Production-specific validation
            v.startswith("prod-"),
            "YOUR_NEW_VARIABLE must start with 'prod-' in production"
        ),
    },
}
```

### 2. Add to `.env.example`

Document the variable with an example:

```bash
# Your Feature
YOUR_NEW_VARIABLE=example_value
```

### 3. Use in Settings

Use the `get_config()` helper in your settings files:

```python
from config.env_config import get_config

# Simple usage
YOUR_SETTING = get_config('YOUR_NEW_VARIABLE', default='default')

# With type casting
YOUR_PORT = get_config('YOUR_PORT', default=8000, cast=int)

# Required variable
YOUR_REQUIRED = get_config('YOUR_REQUIRED', required=True)

# List (comma-separated)
YOUR_LIST = get_config(
    'YOUR_LIST',
    default='value1,value2',
    cast=lambda v: [s.strip() for s in v.split(',')]
)
```

### 4. Document in This File

Add the variable to the appropriate table in the [Configuration Variables](#configuration-variables) section.

### 5. Write Tests

Add tests in `tests/unit/test_config.py`:

```python
def test_your_new_variable_validation():
    """When YOUR_NEW_VARIABLE is invalid, should raise clear error."""
    from config.env_config import ConfigurationError, validate_configuration

    with patch.dict(os.environ, {"YOUR_NEW_VARIABLE": "invalid"}):
        with pytest.raises(ConfigurationError) as exc_info:
            validate_configuration("production")

        assert "YOUR_NEW_VARIABLE" in str(exc_info.value)
```

## Validation and Error Messages

### Startup Validation

Configuration is validated automatically on startup. To manually validate:

```python
from config.env_config import validate_configuration

# Validate current environment
validate_configuration()

# Validate specific environment
validate_configuration('production')
```

### Error Message Examples

When configuration is invalid, you'll see clear, actionable error messages:

```
Configuration validation failed for 'production' environment:

Missing required configuration variables:
  - SECRET_KEY: Django secret key for cryptographic signing
    Example: SECRET_KEY=your-secret-key-here-generate-using-python-secrets
  - ALLOWED_HOSTS: Comma-separated list of allowed hosts
    Example: ALLOWED_HOSTS=example.com,www.example.com,api.example.com

Invalid configuration values:
  - DB_PORT: DB_PORT must be a valid port number (1-65535)
  - LOG_LEVEL: LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL

Please update your .env file or environment variables and try again.
See docs/CONFIGURATION.md for detailed configuration documentation.
```

### Validation Rules

- **SECRET_KEY**:
  - Must be at least 50 characters in production
  - Cannot contain "django-insecure" in production

- **DB_PORT / EMAIL_PORT**:
  - Must be a valid integer between 1 and 65535

- **LOG_LEVEL**:
  - Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL

- **JWT Token Lifetimes**:
  - Must be positive integers

## Security Best Practices

### 1. Never Commit Secrets

- Never commit `.env` files to version control
- Use `.env.example` with placeholder values
- Add `.env` to `.gitignore`

### 2. Generate Strong SECRET_KEY

```bash
# Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3. Use Different Secrets Per Environment

- Development: Can use simple keys for convenience
- Testing: Uses minimal configuration
- Production: Must use strong, unique secrets

### 4. Rotate Secrets Regularly

- Rotate `SECRET_KEY` periodically (will invalidate sessions)
- Update database passwords regularly
- Rotate API keys and tokens

### 5. Limit Access

- Use environment-specific IAM roles
- Restrict who can view production secrets
- Use secret management services (AWS Secrets Manager, HashiCorp Vault)

### 6. Validate in Production

- Production validates all required settings on startup
- Server will not start with invalid configuration
- Errors are logged but sensitive values are not exposed

## Troubleshooting

### Missing Environment Variables

**Error**: `Required configuration variable 'SECRET_KEY' is not set`

**Solution**:
1. Copy `.env.example` to `.env`
2. Fill in required values
3. Source the environment: `source .env` or use `python-decouple`

### Invalid SECRET_KEY in Production

**Error**: `SECRET_KEY must be at least 50 characters in production`

**Solution**:
```bash
# Generate a new secure key
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Add to .env
echo "SECRET_KEY=<generated-key>" >> .env
```

### Invalid Port Number

**Error**: `DB_PORT must be a valid port number (1-65535)`

**Solution**:
```bash
# Ensure DB_PORT is a valid integer
DB_PORT=5432  # Not 'postgres' or other invalid value
```

### ALLOWED_HOSTS Not Set

**Error**: `Missing required configuration variables: ALLOWED_HOSTS`

**Solution**:
```bash
# Set your production domains
ALLOWED_HOSTS=example.com,www.example.com,api.example.com
```

### Configuration Not Loading

**Symptoms**: Application starts but uses wrong settings

**Solution**:
1. Check `DJANGO_SETTINGS_MODULE` is set correctly
2. Verify `.env` file is in the correct directory (backend/)
3. Check file permissions on `.env`
4. Ensure `python-decouple` is installed

### Testing Environment Issues

**Symptoms**: Tests fail due to missing configuration

**Solution**:
Testing environment has minimal requirements and uses in-memory databases. Most configuration is optional for tests.

```bash
# Set testing environment
export DJANGO_SETTINGS_MODULE=config.settings.testing

# Run tests
pytest
```

## Examples

### Development .env

```bash
SECRET_KEY=dev-key-not-for-production
DJANGO_SETTINGS_MODULE=config.settings.development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=backend_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

LOG_LEVEL=DEBUG
```

### Staging .env

```bash
SECRET_KEY=<50+ character secure key>
DJANGO_SETTINGS_MODULE=config.settings.staging
DEBUG=False
ALLOWED_HOSTS=staging.example.com,staging-api.example.com

DB_NAME=backend_staging
DB_USER=backend_staging_user
DB_PASSWORD=<secure password>
DB_HOST=db.staging.example.com
DB_PORT=5432

REDIS_URL=redis://redis.staging.example.com:6379/1
REDIS_PASSWORD=<secure password>
CELERY_BROKER_URL=redis://:password@redis.staging.example.com:6379/0
CELERY_RESULT_BACKEND=redis://:password@redis.staging.example.com:6379/0

CORS_ALLOWED_ORIGINS=https://staging.example.com

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<staging email>
EMAIL_HOST_PASSWORD=<password>
DEFAULT_FROM_EMAIL=noreply-staging@example.com

LOG_LEVEL=INFO

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Production .env

```bash
SECRET_KEY=<50+ character secure key from secrets manager>
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com,api.example.com

DB_NAME=backend_production
DB_USER=backend_user
DB_PASSWORD=<secure password from secrets manager>
DB_HOST=db.example.com
DB_PORT=5432

REDIS_URL=redis://redis.example.com:6379/1
REDIS_PASSWORD=<strong password from secrets manager>
CELERY_BROKER_URL=redis://:password@redis.example.com:6379/0
CELERY_RESULT_BACKEND=redis://:password@redis.example.com:6379/0

CORS_ALLOWED_ORIGINS=https://example.com,https://www.example.com

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<email from secrets manager>
EMAIL_HOST_PASSWORD=<password from secrets manager>
DEFAULT_FROM_EMAIL=noreply@example.com

LOG_LEVEL=WARNING

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Testing .env

```bash
DJANGO_SETTINGS_MODULE=config.settings.testing

# Testing uses in-memory databases and minimal configuration
# Most variables are optional
```

## Additional Resources

- [Django Settings Best Practices](https://docs.djangoproject.com/en/5.1/topics/settings/)
- [python-decouple Documentation](https://github.com/HBNetwork/python-decouple)
- [12-Factor App Configuration](https://12factor.net/config)
- [OWASP Configuration Management](https://owasp.org/www-project-proactive-controls/)

## Getting Help

If you encounter configuration issues:

1. Check this documentation first
2. Run `python manage.py check` to validate settings
3. Check the error messages - they include specific guidance
4. Review `.env.example` for all available variables
5. Check the implementation in `config/env_config.py`

For additional help, run:

```python
from config.env_config import print_configuration_help
print_configuration_help()
```

This will print all configuration variables with descriptions and examples.
