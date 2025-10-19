# CORS Configuration Documentation

## Overview

This document describes the Cross-Origin Resource Sharing (CORS) configuration for the backend API. CORS is configured to allow the frontend application to make requests to the backend API while maintaining security.

## Current Configuration

### Development Environment

**File**: `backend/src/backend/settings/development.py`

```python
# Permissive CORS for development - allows all origins
CORS_ALLOW_ALL_ORIGINS = True
```

**Purpose**: In development mode, CORS is configured to accept requests from any origin. This provides maximum flexibility during local development and allows developers to test the frontend from different ports or domains without CORS errors.

**Security Note**: This configuration should NEVER be used in production.

### Production Environment

**File**: `backend/src/backend/settings/production.py`

Production uses the base configuration which reads allowed origins from environment variables.

**File**: `backend/src/backend/settings/base.py`

```python
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
    cast=Csv(),
)

CORS_ALLOW_CREDENTIALS = True
```

**Purpose**: Production restricts CORS to specific trusted origins configured via environment variables.

### Environment Variables

**File**: `backend/.env.example`

```bash
# CORS Allowed Origins (comma-separated)
# Development: http://localhost:5173,http://127.0.0.1:5173
# Production: https://yourdomain.com
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## Allowed Origins

### Development Origins

The default development origins configured in the codebase:

- `http://localhost:5173` - Vite development server (localhost)
- `http://127.0.0.1:5173` - Vite development server (IP address)

**Why port 5173?** This is the default port for Vite, the build tool used by the frontend application.

### Production Origins

Production origins must be explicitly configured via the `CORS_ALLOWED_ORIGINS` environment variable. Examples:

- `https://app.example.com` - Production frontend domain
- `https://www.example.com` - Production website
- `https://staging.example.com` - Staging environment

**Important**: Always use HTTPS in production for security.

## CORS Settings Explained

### CORS_ALLOW_CREDENTIALS

```python
CORS_ALLOW_CREDENTIALS = True
```

**What it does**: Allows the frontend to send credentials (cookies, authorization headers, TLS client certificates) with cross-origin requests.

**Why it's needed**: Our application uses session-based authentication with cookies. Without this setting, browsers will block authentication cookies in cross-origin requests.

**Security implication**: When `CORS_ALLOW_CREDENTIALS` is `True`, you CANNOT use `CORS_ALLOW_ALL_ORIGINS = True` in production. You must specify exact allowed origins.

### CORS_ALLOWED_ORIGINS

**What it does**: Specifies which origins (protocol + domain + port) are allowed to make cross-origin requests to the backend.

**Format**: List or tuple of fully-qualified origin URLs
- Include protocol (http:// or https://)
- Include port if non-standard (e.g., :5173 for development)
- Do NOT include trailing slashes

**Examples**:
```python
# Development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Production
CORS_ALLOWED_ORIGINS = [
    "https://app.example.com",
    "https://www.example.com",
]
```

## Security Headers

The CORS configuration works in conjunction with other security headers configured in the backend:

### Production Security Headers

**File**: `backend/src/backend/settings/production.py`

```python
# SSL/HTTPS Enforcement
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie Security
SESSION_COOKIE_SECURE = True  # Only send session cookies over HTTPS
CSRF_COOKIE_SECURE = True     # Only send CSRF cookies over HTTPS

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
```

**What these do**:

- **SECURE_SSL_REDIRECT**: Redirects all HTTP requests to HTTPS
- **SECURE_HSTS_SECONDS**: Tells browsers to only connect via HTTPS for 1 year
- **SESSION_COOKIE_SECURE**: Prevents session cookies from being sent over HTTP
- **CSRF_COOKIE_SECURE**: Prevents CSRF tokens from being sent over HTTP
- **SECURE_CONTENT_TYPE_NOSNIFF**: Prevents browsers from MIME-sniffing responses
- **X_FRAME_OPTIONS**: Prevents the site from being embedded in iframes (clickjacking protection)

## CORS Response Headers

When a request is made from an allowed origin, the backend includes these CORS headers in the response:

```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: content-type, authorization
```

### Preflight Requests

For complex requests (POST, PUT, DELETE, or custom headers), browsers send a preflight OPTIONS request first. The backend automatically handles these preflight requests and returns appropriate CORS headers.

**Example preflight request**:
```http
OPTIONS /api/users/ HTTP/1.1
Origin: http://localhost:5173
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type, authorization
```

**Example preflight response**:
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: content-type, authorization
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400
```

## Middleware Configuration

CORS is implemented using the `django-cors-headers` package. The middleware must be positioned correctly in the middleware stack:

**File**: `backend/src/backend/settings/base.py`

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "common.middleware.error_handling.ErrorHandlingMiddleware",
    "common.middleware.request_logging.RequestLoggingMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # Must be after SessionMiddleware
    "django.middleware.common.CommonMiddleware",  # Must be after CorsMiddleware
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

**Important**: `CorsMiddleware` must be placed:
- **After** `SessionMiddleware` (to handle session cookies)
- **Before** `CommonMiddleware` (to process CORS before other common middleware)

## Testing CORS Configuration

The CORS configuration is thoroughly tested in `backend/tests/integration/test_cors_configuration.py`.

### Running CORS Tests

```bash
# Run all CORS tests
cd backend
make test-integration

# Or specifically CORS tests
poetry run pytest tests/integration/test_cors_configuration.py -v
```

### Test Coverage

The test suite verifies:

1. **Middleware Configuration**
   - CORS middleware is installed
   - Middleware is in correct position
   - Credentials support is enabled

2. **CORS Headers**
   - Headers are present on API requests
   - Credentials are allowed
   - Preflight requests work correctly
   - Allowed origins receive correct headers
   - Disallowed origins are blocked

3. **Security Headers**
   - Security headers are included in responses
   - Content-Type is set correctly
   - Production cookie settings are secure

4. **Environment Configuration**
   - Development is permissive for ease of use
   - Production is restrictive for security
   - Environment variables work correctly

5. **Authentication Integration**
   - CORS works with session authentication
   - Headers persist across redirects

## Configuration for Different Environments

### Local Development

**Setup**:
1. Copy `.env.example` to `.env`
2. Ensure `DJANGO_SETTINGS_MODULE=backend.settings.development`
3. No need to modify `CORS_ALLOWED_ORIGINS` - development mode allows all origins

**Verification**:
```bash
# Start backend
cd backend
make dev

# In browser console (from frontend at http://localhost:5173)
fetch('http://localhost:8000/health/')
  .then(r => r.json())
  .then(console.log)
// Should work without CORS errors
```

### Staging Environment

**Setup**:
1. Set `DJANGO_SETTINGS_MODULE=backend.settings.production`
2. Set `CORS_ALLOWED_ORIGINS=https://staging-frontend.example.com`
3. Ensure all security settings are enabled

**Environment Variables**:
```bash
DJANGO_SETTINGS_MODULE=backend.settings.production
CORS_ALLOWED_ORIGINS=https://staging-frontend.example.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Production Environment

**Setup**:
1. Set `DJANGO_SETTINGS_MODULE=backend.settings.production`
2. Set `CORS_ALLOWED_ORIGINS` to your production frontend domain(s)
3. Enable all security settings
4. Use HTTPS only

**Environment Variables**:
```bash
DJANGO_SETTINGS_MODULE=backend.settings.production
CORS_ALLOWED_ORIGINS=https://app.example.com,https://www.example.com
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**Production Checklist**:
- [ ] Use HTTPS only (no HTTP)
- [ ] Set specific allowed origins (no wildcards)
- [ ] Enable `SESSION_COOKIE_SECURE`
- [ ] Enable `CSRF_COOKIE_SECURE`
- [ ] Enable `SECURE_SSL_REDIRECT`
- [ ] Set `SECURE_HSTS_SECONDS` to at least 31536000 (1 year)
- [ ] Verify CORS headers in browser developer tools

## Troubleshooting

### Common CORS Errors

#### Error: "No 'Access-Control-Allow-Origin' header present"

**Cause**: The origin making the request is not in `CORS_ALLOWED_ORIGINS`.

**Solution**:
1. Check the origin in the browser error message
2. Add the origin to `CORS_ALLOWED_ORIGINS` environment variable
3. Restart the backend server

**Example**:
```bash
# If frontend is at https://new-domain.com
CORS_ALLOWED_ORIGINS=https://new-domain.com
```

#### Error: "Credentials flag is 'true', but 'Access-Control-Allow-Credentials' header is ''"

**Cause**: Frontend is sending credentials but backend doesn't allow them.

**Solution**: Verify `CORS_ALLOW_CREDENTIALS = True` is set in settings.

#### Error: "The 'Access-Control-Allow-Origin' header contains multiple values"

**Cause**: Multiple middleware or configurations are adding CORS headers.

**Solution**:
1. Check that `CorsMiddleware` is only added once
2. Verify no custom middleware is adding CORS headers
3. Check reverse proxy (nginx, etc.) isn't adding CORS headers

### Debugging CORS Issues

**1. Check Backend Logs**:
```bash
# Backend logs show incoming requests with origin
INFO Request: method=GET path=/health/ ip=127.0.0.1 origin=http://localhost:5173
```

**2. Check Browser Developer Tools**:
- Open Network tab
- Look for preflight OPTIONS request
- Check response headers for `Access-Control-*` headers
- Verify request headers include `Origin`

**3. Test with curl**:
```bash
# Test CORS headers
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: content-type" \
     -X OPTIONS \
     http://localhost:8000/health/ \
     -v
```

**4. Verify Environment Variables**:
```bash
# Check loaded environment
cd backend
poetry run python manage.py shell
>>> from django.conf import settings
>>> print(settings.CORS_ALLOWED_ORIGINS)
>>> print(settings.CORS_ALLOW_CREDENTIALS)
```

## References

- [django-cors-headers Documentation](https://github.com/adamchainz/django-cors-headers)
- [MDN: Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Django Security Settings](https://docs.djangoproject.com/en/5.1/topics/security/)
- [OWASP: CORS Security](https://owasp.org/www-community/attacks/CORS_OriginHeaderScrutiny)

## Summary

The backend CORS configuration:

1. **Development**: Allows all origins for ease of development (`CORS_ALLOW_ALL_ORIGINS = True`)
2. **Production**: Restricts to specific origins via environment variable (`CORS_ALLOWED_ORIGINS`)
3. **Credentials**: Enabled to support session-based authentication (`CORS_ALLOW_CREDENTIALS = True`)
4. **Security**: Includes comprehensive security headers for production deployments
5. **Testing**: Thoroughly tested with 17 integration tests covering all scenarios
6. **Flexibility**: Configurable via environment variables for different deployment environments

The configuration follows Django REST Framework and django-cors-headers best practices, providing both developer convenience and production security.
