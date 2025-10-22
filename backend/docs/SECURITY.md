# Security Best Practices - Feature #7, Story #9

## Overview

This document describes the comprehensive security features implemented in Story #9 to protect the API from common vulnerabilities and attacks. All implementations follow OWASP best practices and industry standards.

## Acceptance Criteria - ALL MET ✓

### 1. Security Headers ✓
**Acceptance Criteria**: When I inspect HTTP responses, I should see security headers configured appropriately.

**Implementation**: `SecurityHeadersMiddleware` adds the following headers to ALL responses:

- **X-Content-Type-Options**: `nosniff` - Prevents MIME type sniffing
- **X-Frame-Options**: `DENY` - Prevents clickjacking attacks
- **X-XSS-Protection**: `1; mode=block` - Enables browser XSS filtering
- **Strict-Transport-Security**: `max-age=31536000; includeSubDomains` - Enforces HTTPS for 1 year
- **Content-Security-Policy**: Comprehensive CSP with strict directives
- **Referrer-Policy**: `strict-origin-when-cross-origin` - Controls referrer information
- **Permissions-Policy**: Restricts camera, microphone, geolocation, and other browser features

**Location**: `/home/ed/Dev/architecture/backend/apps/core/middleware.py`

### 2. Input Validation & Sanitization ✓
**Acceptance Criteria**: When I send malformed or malicious input, I should see it rejected with appropriate error messages.

**Implementation**: Comprehensive validation utilities in `apps/utils/validators.py`:

#### XSS Protection
- `sanitize_html()` - Escapes HTML entities and removes dangerous patterns
- `detect_xss()` - Detects script tags, event handlers, and javascript: protocols

#### SQL Injection Prevention
- `detect_sql_injection()` - Detects UNION, OR 1=1, DROP TABLE, SQL comments
- `sanitize_sql_input()` - Removes dangerous SQL keywords and characters

#### Path Traversal Prevention
- `detect_path_traversal()` - Detects ../, encoded variants, backslash attempts
- `sanitize_filename()` - Safely sanitizes filenames, removes path separators

#### Format Validation
- `validate_email()` - RFC-compliant email validation with XSS checks
- `validate_username()` - Alphanumeric + underscore/hyphen, 3-150 chars
- `validate_url()` - Blocks javascript:, data:, file: protocols
- `sanitize_json_input()` - Recursively sanitizes JSON objects

**Location**: `/home/ed/Dev/architecture/backend/apps/utils/validators.py`

### 3. Rate Limiting ✓
**Acceptance Criteria**: When I make excessive requests, I should encounter rate limiting.

**Implementation**: Using `django-ratelimit` package with the following limits:

- **User Registration**: 5 registrations per hour per IP address
- **User Login**: 10 login attempts per minute per IP address
- **Password Change**: 5 password changes per hour per user

**Configuration**:
- `RATELIMIT_ENABLE` - Can be disabled in test environments
- `RATELIMIT_USE_CACHE` - Uses Redis cache for distributed rate limiting
- Returns HTTP 429 (Too Many Requests) when limits exceeded

**Location**: `/home/ed/Dev/architecture/backend/apps/users/views.py`

### 4. CORS & CSRF Protection ✓
**Acceptance Criteria**: When I attempt cross-origin requests from unauthorized domains, I should see them blocked.

**Implementation**:

#### CORS Configuration
- **Development**: Allows `localhost:3000` and `127.0.0.1:3000`
- **Production**: Explicit origins only (configured via `CORS_ALLOWED_ORIGINS`)
- **Always**: `CORS_ALLOW_ALL_ORIGINS = False` in production
- **Always**: `CORS_ALLOW_CREDENTIALS = True` for cookie support

#### CSRF Protection
- `CSRF_COOKIE_SECURE` - Set to True in production (HTTPS only)
- `CSRF_COOKIE_HTTPONLY` - False (allows JavaScript access for SPA)
- `CSRF_COOKIE_SAMESITE` - 'Lax' (balance between security and usability)
- `CSRF_TRUSTED_ORIGINS` - Configurable list of trusted domains

**Location**:
- `/home/ed/Dev/architecture/backend/config/settings/base.py`
- `/home/ed/Dev/architecture/backend/config/settings/production.py`

## Security Features Summary

### 1. HTTP Security Headers (OWASP Compliant)
- Implemented via `SecurityHeadersMiddleware`
- 7 comprehensive security headers on every response
- CSP relaxed in DEBUG mode for development tools
- HSTS with 1-year max-age for production

### 2. Input Validation & Sanitization
- 10 validation/sanitization functions
- Protection against: XSS, SQL Injection, Path Traversal
- Email, Username, URL, Filename validation
- Recursive JSON sanitization

### 3. Rate Limiting (Brute Force Protection)
- IP-based limiting for anonymous users
- User-based limiting for authenticated users
- Configurable limits per endpoint
- Uses Redis for distributed systems

### 4. CORS & CSRF Protection
- Strict origin policies
- Configurable per environment
- Secure cookie configuration
- Preflight request handling

### 5. Session Security
- `SESSION_COOKIE_SECURE` - HTTPS only in production
- `SESSION_COOKIE_HTTPONLY` - True (prevents JavaScript access)
- `SESSION_COOKIE_SAMESITE` - 'Lax' (CSRF protection)

## Test Coverage

### Unit Tests (81 tests)
- `test_security_headers.py` - 13 tests for HTTP headers
- `test_input_validation.py` - 38 tests for validators
- `test_rate_limiting.py` - 11 tests for rate limiting
- `test_cors_csrf_protection.py` - 19 tests for CORS/CSRF

### Acceptance Tests (16 tests)
- `test_story_9_security.py` - Tests for all 4 acceptance criteria

**Total**: 97 comprehensive security tests

## Configuration

### Environment Variables

Add to `.env` file (see `.env.example` for reference):

```bash
# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# CSRF Configuration
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Cookie Security (Set to True in production with HTTPS)
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False

# Rate Limiting
RATELIMIT_ENABLE=True
```

### Production Configuration

In production, ensure:

1. **HTTPS Enforcement**:
   ```python
   SECURE_SSL_REDIRECT = True
   CSRF_COOKIE_SECURE = True
   SESSION_COOKIE_SECURE = True
   ```

2. **Explicit CORS Origins**:
   ```bash
   CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

3. **CSRF Trusted Origins**:
   ```bash
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

4. **Rate Limiting Enabled**:
   ```python
   RATELIMIT_ENABLE = True  # Always True in production
   ```

## Usage Examples

### Using Input Validators

```python
from apps.utils.validators import (
    validate_email,
    sanitize_html,
    detect_sql_injection,
    sanitize_json_input
)

# Email validation
if not validate_email(user_email):
    return {"error": "Invalid email format"}

# HTML sanitization
safe_bio = sanitize_html(user_bio)

# SQL injection detection
if detect_sql_injection(search_query):
    return {"error": "Invalid search query"}

# JSON sanitization
clean_data = sanitize_json_input(request_data)
```

### Testing Security Headers

```python
from rest_framework.test import APIClient

client = APIClient()
response = client.get('/api/v1/health/')

assert 'X-Content-Type-Options' in response
assert 'Strict-Transport-Security' in response
assert 'Content-Security-Policy' in response
```

## Security Checklist for Production

- [ ] Set `CSRF_COOKIE_SECURE=True`
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Configure `CORS_ALLOWED_ORIGINS` with production domains
- [ ] Configure `CSRF_TRUSTED_ORIGINS` with production domains
- [ ] Verify `RATELIMIT_ENABLE=True`
- [ ] Test security headers with tools like [Security Headers](https://securityheaders.com/)
- [ ] Run security audit with `python manage.py check --deploy`
- [ ] Review CSP policy and adjust for your frontend needs
- [ ] Monitor rate limiting logs for potential attacks
- [ ] Set up alerts for unusual authentication patterns

## Dependencies

- **django-ratelimit** (>=4.1,<5.0) - Rate limiting functionality

## Files Modified

1. `/home/ed/Dev/architecture/backend/apps/core/middleware.py` - Added SecurityHeadersMiddleware
2. `/home/ed/Dev/architecture/backend/apps/users/views.py` - Added rate limiting decorators
3. `/home/ed/Dev/architecture/backend/config/settings/base.py` - Security configurations
4. `/home/ed/Dev/architecture/backend/config/settings/production.py` - Production hardening
5. `/home/ed/Dev/architecture/backend/.env.example` - Security environment variables

## Files Created

1. `/home/ed/Dev/architecture/backend/apps/utils/validators.py` - Validation utilities
2. `/home/ed/Dev/architecture/backend/tests/unit/test_security_headers.py`
3. `/home/ed/Dev/architecture/backend/tests/unit/test_input_validation.py`
4. `/home/ed/Dev/architecture/backend/tests/unit/test_rate_limiting.py`
5. `/home/ed/Dev/architecture/backend/tests/unit/test_cors_csrf_protection.py`
6. `/home/ed/Dev/architecture/backend/tests/acceptance/test_story_9_security.py`

## Best Practices Followed

1. **Defense in Depth**: Multiple layers of security controls
2. **Fail Secure**: Default to restrictive policies
3. **Least Privilege**: Minimal permissions by default
4. **Security by Design**: Security considered from the start
5. **Clear Error Messages**: Helpful without exposing system details
6. **Test-Driven Development**: 97 tests written before implementation
7. **Environment-Based Configuration**: Different security for dev/prod
8. **OWASP Compliance**: Following OWASP security guidelines

## Common Vulnerabilities Addressed

| Vulnerability | Protection Mechanism |
|--------------|---------------------|
| XSS (Cross-Site Scripting) | Input sanitization, CSP, X-XSS-Protection |
| SQL Injection | Input validation, parameterized queries (Django ORM) |
| CSRF (Cross-Site Request Forgery) | CSRF tokens, SameSite cookies |
| Clickjacking | X-Frame-Options: DENY |
| MIME Sniffing | X-Content-Type-Options: nosniff |
| Man-in-the-Middle | HSTS, Secure cookies |
| Brute Force Attacks | Rate limiting on authentication |
| Path Traversal | Filename sanitization, path validation |
| Information Disclosure | Referrer-Policy, error handling |
| Unauthorized CORS | Strict origin policies |

## Monitoring & Logging

Security events are logged via Django's logging framework:

- **Rate Limiting**: Logged when limits are exceeded
- **Authentication Failures**: Logged with IP address
- **Invalid Input**: Validation errors logged (without exposing data)
- **Security Headers**: Applied to all responses (visible in response logs)

Check logs in:
- `logs/requests.log` - Request logs with security context
- `logs/exceptions.log` - Security exceptions and violations

## Future Enhancements

Potential future security improvements:

1. IP allowlist/blocklist for admin endpoints
2. Anomaly detection for authentication patterns
3. Two-factor authentication (2FA)
4. API key management for third-party integrations
5. Web Application Firewall (WAF) integration
6. Security scanning in CI/CD pipeline
7. Automated penetration testing
8. Content Security Policy reporting endpoint

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Documentation](https://docs.djangoproject.com/en/5.1/topics/security/)
- [Django REST Framework Security](https://www.django-rest-framework.org/topics/security/)
- [Security Headers Reference](https://securityheaders.com/)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)

---

**Implementation Date**: 2025-10-23
**Story**: Feature #7, Story #9
**Status**: ✅ Complete - All acceptance criteria met
**Production Ready**: ✅ Yes
**Tests**: 97 comprehensive tests
