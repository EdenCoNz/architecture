# Server Setup and Configuration

This document describes the basic server application setup including health check endpoint, request logging, and error handling.

## Overview

The backend server is built with Django 5.1 and Django REST Framework. It includes:

1. **Health Check Endpoint**: Public endpoint for monitoring server status
2. **Request Logging Middleware**: Logs all incoming HTTP requests
3. **Error Handling Middleware**: Catches and formats exceptions consistently

## Health Check Endpoint

### Endpoint
- **URL**: `/health/`
- **Method**: `GET`
- **Authentication**: Not required (public endpoint)

### Response Format
```json
{
  "status": "healthy",
  "timestamp": "2025-10-19T12:00:00.000000Z",
  "service": "backend-api",
  "version": "0.1.0",
  "database": "connected",
  "debug_mode": false
}
```

### Status Codes
- `200 OK`: Server is healthy
- `503 Service Unavailable`: Server is unhealthy (e.g., database connection failed)

### Use Cases
- Load balancer health checks
- Monitoring systems (Prometheus, Datadog, etc.)
- Container orchestration (Kubernetes, Docker Swarm)
- CI/CD pipeline health verification

### Implementation
- **View**: `backend/src/common/views/health.py`
- **Service**: `backend/src/core/services/health.py` (if database checks are implemented)
- **URL Configuration**: `backend/src/backend/urls.py`

## Request Logging Middleware

### Purpose
Logs all incoming HTTP requests with relevant information for debugging and monitoring.

### Logged Information
- HTTP method (GET, POST, PUT, DELETE, etc.)
- Request path
- Client IP address (handles X-Forwarded-For for proxied requests)
- User agent
- Response status code
- Request processing duration (in milliseconds)

### Example Log Output
```
INFO Request: method=GET path=/api/users/ ip=192.168.1.100 status=200 duration=45.23ms user_agent=Mozilla/5.0
```

### Configuration
- **Middleware**: `common.middleware.request_logging.RequestLoggingMiddleware`
- **Log Level**: INFO
- **Excluded Paths**: `/health/`, `/favicon.ico` (to reduce log noise)

### Implementation
- **File**: `backend/src/common/middleware/request_logging.py`
- **Logger**: `common.middleware`

## Error Handling Middleware

### Purpose
Catches exceptions raised during request processing and returns properly formatted JSON error responses.

### Handled Exceptions

#### 1. HTTP 404 Not Found
```json
{
  "error": "Not Found",
  "message": "The requested resource was not found",
  "path": "/api/invalid/"
}
```

#### 2. Authentication Errors (401)
```json
{
  "error": "Not Authenticated",
  "message": "Authentication credentials were not provided",
  "path": "/api/protected/"
}
```

#### 3. Permission Denied (403)
```json
{
  "error": "Permission Denied",
  "message": "You do not have permission to access this resource",
  "path": "/api/admin/"
}
```

#### 4. Validation Errors (400)
```json
{
  "error": "Validation Error",
  "message": "The request contains invalid data",
  "errors": {
    "email": ["This field is required"],
    "age": ["Must be a positive integer"]
  },
  "path": "/api/users/"
}
```

#### 5. Internal Server Error (500)
**Production Mode** (DEBUG=False):
```json
{
  "error": "Internal Server Error",
  "message": "An internal server error occurred. Please try again later.",
  "path": "/api/users/"
}
```

**Debug Mode** (DEBUG=True):
```json
{
  "error": "Internal Server Error",
  "message": "Specific error message",
  "exception_type": "ValueError",
  "path": "/api/users/",
  "traceback": ["...full traceback..."]
}
```

### Security Features
- Hides sensitive error details in production
- Includes detailed error information in debug mode for development
- Logs all exceptions with full stack traces

### Implementation
- **File**: `backend/src/common/middleware/error_handling.py`
- **Logger**: `common.middleware`

## Middleware Order

The middleware is configured in the following order (important for correct behavior):

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "common.middleware.error_handling.ErrorHandlingMiddleware",  # Catch errors early
    "common.middleware.request_logging.RequestLoggingMiddleware",  # Log requests
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

### Order Rationale
1. **Error Handling First**: Catches all exceptions from subsequent middleware
2. **Request Logging Second**: Logs requests after error handling is in place
3. **Django Core Middleware**: Standard Django middleware stack

## Logging Configuration

### Log Levels
- **Development**: INFO level
- **Production**: WARNING level (configurable via `LOG_LEVEL` env var)

### Log Format
```
{levelname} {asctime} {module} {process:d} {thread:d} {message}
```

### Environment Variables
- `LOG_LEVEL`: Overall log level (default: INFO)
- `DJANGO_LOG_LEVEL`: Django-specific log level (default: INFO)

### Loggers
- `common.middleware`: Custom middleware logging
- `django`: Django framework logging
- `django.server`: Django development server logging

## Testing

### Running Tests
```bash
# Run all tests
make test

# Run specific test files
PYTHONPATH=src poetry run pytest tests/integration/test_health_check.py -v
PYTHONPATH=src poetry run pytest tests/unit/middleware/test_request_logging.py -v
PYTHONPATH=src poetry run pytest tests/unit/middleware/test_error_handling.py -v
```

### Test Coverage
- Unit tests for middleware functionality
- Integration tests for health check endpoint
- Integration tests for server startup and configuration

### Test Files
- `tests/integration/test_health_check.py`: Health check endpoint tests
- `tests/unit/middleware/test_request_logging.py`: Request logging tests
- `tests/unit/middleware/test_error_handling.py`: Error handling tests
- `tests/integration/test_server_startup.py`: Server configuration tests

## Starting the Server

### Development Server
```bash
# Using make
make dev

# Using manage.py directly
PYTHONPATH=src python manage.py runserver 0.0.0.0:8000
```

### Production Server
```bash
make prod
```

### Environment Setup
1. Copy environment file:
   ```bash
   cp .env.example .env
   ```

2. Update database credentials in `.env`:
   ```
   DB_NAME=backend_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. Run migrations:
   ```bash
   make migrate
   ```

4. Start server:
   ```bash
   make dev
   ```

## Verification

### Health Check
```bash
# Test health check endpoint
curl http://localhost:8000/health/

# Expected response:
# {"status":"healthy","timestamp":"2025-10-19T12:00:00Z","service":"backend-api",...}
```

### Request Logging
Check server logs after making requests - you should see log entries like:
```
INFO Request: method=GET path=/health/ ip=127.0.0.1 status=200 duration=5.23ms user_agent=curl/7.68.0
```

### Error Handling
```bash
# Test 404 error
curl http://localhost:8000/api/invalid/

# Expected response:
# {"error":"Not Found","message":"The requested resource was not found","path":"/api/invalid/"}
```

## Next Steps

1. Add database health check to health endpoint
2. Add metrics endpoint for Prometheus
3. Add request correlation IDs for distributed tracing
4. Add rate limiting middleware
5. Add authentication middleware
6. Add API versioning

## File Structure

```
backend/
├── src/
│   ├── backend/
│   │   ├── settings/
│   │   │   └── base.py          # Middleware configuration
│   │   └── urls.py              # Health check URL
│   └── common/
│       ├── middleware/
│       │   ├── __init__.py
│       │   ├── request_logging.py
│       │   └── error_handling.py
│       └── views/
│           ├── __init__.py
│           └── health.py
└── tests/
    ├── integration/
    │   ├── test_health_check.py
    │   └── test_server_startup.py
    └── unit/
        └── middleware/
            ├── test_request_logging.py
            └── test_error_handling.py
```
