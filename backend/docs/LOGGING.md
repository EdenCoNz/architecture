# Request Logging and Error Handling

## Overview

The backend API implements comprehensive request logging and error handling to facilitate debugging, monitoring, and understanding API usage patterns. This system provides structured logging with different configurations for development and production environments.

## Features

### Request Logging
- **Automatic request tracking**: Every API request is logged with detailed information
- **Unique request IDs**: Each request gets a UUID for end-to-end tracking
- **Performance monitoring**: Response times are measured and logged
- **User tracking**: Authenticated user information is captured
- **Sensitive data sanitization**: Passwords, tokens, and other sensitive fields are automatically redacted

### Error Handling
- **Consistent error responses**: All errors follow the same response structure
- **Environment-aware detail exposure**: Detailed stack traces in development, generic messages in production
- **Comprehensive error logging**: All exceptions are logged with context
- **Request context preservation**: Error logs include request method, path, user, and request ID

### Structured Logging
- **Multiple log levels**: DEBUG, INFO, WARNING, ERROR
- **Separate log files**: Different files for requests, errors, exceptions, and general logs
- **Log rotation**: Automatic rotation based on file size with configurable retention
- **JSON formatting**: Production logs use JSON format for easy parsing and aggregation

## Log Files

All log files are stored in the `backend/logs/` directory:

| File | Content | Max Size | Backups |
|------|---------|----------|---------|
| `requests.log` | All HTTP requests with timing | 20MB (dev) / 100MB (prod) | 10 / 30 |
| `errors.log` | Error-level logs only | 10MB / 50MB | 5 / 20 |
| `exceptions.log` | API exceptions and warnings | 10MB / 50MB | 5 / 20 |
| `general.log` | General application logs | 10MB / 50MB | 5 / 20 |

## Request Log Format

Each request log entry includes:

```json
{
  "timestamp": "2025-10-23T12:34:56.789Z",
  "level": "INFO",
  "logger": "apps.middleware",
  "message": "GET /api/v1/users/ - Status: 200 - Duration: 45.23ms - User: john.doe",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "GET",
  "path": "/api/v1/users/",
  "status_code": 200,
  "response_time_ms": 45.23,
  "user_id": 123,
  "username": "john.doe",
  "query_params": {"page": "1", "limit": "20"},
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

## Error Response Format

All API errors return a consistent structure:

```json
{
  "error": true,
  "status_code": 400,
  "message": "Validation failed",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2025-10-23T12:34:56.789Z",
  "errors": {
    "email": ["This field is required."],
    "password": ["Password must be at least 8 characters."]
  }
}
```

### Development Mode
In development (`DEBUG=True`), error responses include additional debug information:

```json
{
  "error": true,
  "status_code": 500,
  "message": "An unexpected error occurred.",
  "request_id": "...",
  "timestamp": "...",
  "debug": {
    "exception_type": "DatabaseError",
    "exception_message": "Connection timeout",
    "traceback": "Traceback (most recent call last):\n..."
  }
}
```

### Production Mode
In production (`DEBUG=False`), error responses hide sensitive implementation details:

```json
{
  "error": true,
  "status_code": 500,
  "message": "An unexpected error occurred. Please try again later.",
  "request_id": "...",
  "timestamp": "..."
}
```

## Log Levels

### By Status Code
- **2xx (Success)**: `INFO` level
- **4xx (Client Error)**: `WARNING` level
- **5xx (Server Error)**: `ERROR` level

### By Environment
- **Development**: `DEBUG` and above
- **Production**: `WARNING` and above

## Performance Monitoring

### Slow Request Logging
Requests exceeding the threshold are automatically flagged:

- **Development**: 500ms threshold
- **Production**: 2000ms threshold

Slow requests are logged with:
```
SLOW REQUEST: GET /api/v1/heavy-operation/ took 1523.45ms (threshold: 1000ms)
```

### Configuration
Set the threshold via environment variable:
```bash
SLOW_REQUEST_THRESHOLD_MS=1000
```

## Sensitive Data Sanitization

The following fields are automatically redacted from logs:
- `password`
- `token`
- `secret`
- `api_key` / `apikey`
- `authorization` / `auth`
- `credentials`
- `csrf_token` / `csrfmiddlewaretoken`

Example:
```python
# Original request data:
{"username": "john", "password": "secret123"}

# Logged as:
{"username": "john", "password": "***REDACTED***"}
```

## Request ID Tracking

Every request receives a unique UUID stored in:
1. Request object: `request.request_id`
2. Log entries: `extra.request_id`
3. Response header: `X-Request-ID`

Use this ID to trace a request through logs:
```bash
# Search logs for a specific request
grep "a1b2c3d4-e5f6-7890-abcd-ef1234567890" logs/*.log
```

## Custom Middleware

### RequestLoggingMiddleware
Primary middleware that logs all requests with detailed information.

**Features:**
- Automatic timing measurement
- User identification
- Query parameter capture
- IP address extraction
- Sensitive data sanitization

### PerformanceLoggingMiddleware
Monitors and logs slow requests exceeding the configured threshold.

**Configuration:**
```python
# In settings
SLOW_REQUEST_THRESHOLD_MS = 1000
```

### HealthCheckLoggingExemptionMiddleware
Skips logging for health check endpoints to prevent log spam from monitoring tools.

**Exempt paths:**
- `/health/`
- `/health/ready/`
- `/health/live/`
- `/api/v1/health/`

## Exception Handler

### Custom Exception Handler
Located at `apps.core.exceptions.custom_exception_handler`

**Features:**
- Converts Django exceptions to DRF exceptions
- Provides consistent error response format
- Logs with appropriate level based on severity
- Includes request context in logs
- Sanitizes sensitive data

### Custom Exception Classes

#### ServiceUnavailableException
```python
from apps.core.exceptions import ServiceUnavailableException

raise ServiceUnavailableException('Database is temporarily unavailable')
```
Returns HTTP 503 with appropriate message.

#### RateLimitExceededException
```python
from apps.core.exceptions import RateLimitExceededException

raise RateLimitExceededException('API rate limit exceeded')
```
Returns HTTP 429 with appropriate message.

## Configuration

### Environment Variables

```bash
# Slow request threshold (milliseconds)
SLOW_REQUEST_THRESHOLD_MS=1000
```

### Settings Files

#### Base Settings (`config/settings/base.py`)
- Core logging configuration
- Handler and formatter definitions
- Logger hierarchy setup

#### Development Settings (`config/settings/development.py`)
- DEBUG level logging
- SQL query logging
- Lower slow request threshold
- Verbose console output

#### Production Settings (`config/settings/production.py`)
- WARNING level logging
- JSON formatted logs
- Higher slow request threshold
- Larger log files with more backups

## Usage Examples

### Logging in Views
```python
import logging

logger = logging.getLogger('apps.api')

class UserViewSet(viewsets.ModelViewSet):
    def list(self, request):
        logger.info('Fetching user list')
        try:
            users = User.objects.all()
            return Response(UserSerializer(users, many=True).data)
        except Exception as e:
            logger.error(f'Failed to fetch users: {e}', exc_info=True)
            raise
```

### Raising Custom Exceptions
```python
from apps.core.exceptions import ServiceUnavailableException

def check_external_service():
    if not service_available():
        raise ServiceUnavailableException('External API is down')
```

### Accessing Request ID
```python
def my_view(request):
    request_id = request.request_id
    logger.info(f'Processing request {request_id}')
```

## Monitoring and Analysis

### Viewing Logs
```bash
# Tail request logs
tail -f logs/requests.log

# View recent errors
tail -50 logs/errors.log

# Search for specific request
grep "request_id" logs/*.log

# Count errors by type
grep "ERROR" logs/errors.log | cut -d' ' -f4 | sort | uniq -c
```

### Log Analysis Tools
For production, consider using:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Datadog**
- **CloudWatch** (AWS)
- **Stackdriver** (GCP)

The JSON log format in production is optimized for these tools.

## Testing

Run logging tests:
```bash
# All logging tests
pytest tests/test_middleware.py tests/test_exception_handler.py -v

# Specific test
pytest tests/test_middleware.py::RequestLoggingMiddlewareTestCase::test_middleware_logs_request_with_basic_info -v
```

## Best Practices

1. **Use appropriate log levels**:
   - DEBUG: Detailed diagnostic information
   - INFO: General informational messages
   - WARNING: Warning messages for potentially harmful situations
   - ERROR: Error events that might still allow the application to continue

2. **Include context**: Always provide relevant context in log messages
   ```python
   logger.error(f'Failed to process order {order_id} for user {user_id}', exc_info=True)
   ```

3. **Don't log sensitive data**: The middleware sanitizes common fields, but be cautious in manual logging

4. **Use structured logging**: Include extra context as dictionary
   ```python
   logger.info('User login', extra={'user_id': user.id, 'ip': request.META.get('REMOTE_ADDR')})
   ```

5. **Log exceptions properly**: Use `exc_info=True` for stack traces
   ```python
   try:
       risky_operation()
   except Exception as e:
       logger.error('Operation failed', exc_info=True)
   ```

## Troubleshooting

### Logs not appearing
1. Check `DEBUG` setting matches environment
2. Verify log directory exists and is writable: `mkdir -p logs`
3. Check logger name matches configuration
4. Verify log level is appropriate

### Too many logs
1. Increase log level (INFO → WARNING → ERROR)
2. Add paths to `HealthCheckLoggingExemptionMiddleware`
3. Adjust slow request threshold

### Disk space issues
1. Decrease `maxBytes` in handlers
2. Reduce `backupCount`
3. Set up log rotation with system tools (logrotate)
4. Archive old logs to external storage

## Future Enhancements

Potential improvements for future iterations:
1. Integration with external log aggregation services
2. Real-time alerting for critical errors
3. Automated log analysis and anomaly detection
4. Performance metrics dashboard
5. Request correlation across microservices
6. Log sampling for high-traffic endpoints
