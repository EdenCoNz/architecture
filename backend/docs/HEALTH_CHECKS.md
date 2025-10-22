# Health Check and Status Endpoints

## Overview

The API provides comprehensive health check and status endpoints for monitoring system health, diagnosing issues, and integrating with orchestration platforms like Kubernetes.

**Story #5**: Implement Health Check and Status Endpoints

## Endpoints

### Health Check: `GET /api/v1/health/`

Basic health check endpoint that reports overall system health.

**Purpose**: Quick health check for load balancers and monitoring systems

**Response Codes**:
- `200 OK` - Service is healthy and operational
- `503 Service Unavailable` - Service is unhealthy (e.g., database down)

**Response Format**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-23T18:30:00.000Z",
  "database": {
    "status": "connected",
    "response_time_ms": 15.5,
    "engine": "django.db.backends.postgresql"
  }
}
```

**Unhealthy Response**:
```json
{
  "status": "unhealthy",
  "timestamp": "2025-10-23T18:30:00.000Z",
  "database": {
    "status": "disconnected",
    "error": "Could not connect to database server at localhost:5432",
    "engine": "django.db.backends.postgresql"
  }
}
```

**Fields**:
- `status`: Overall health status (`healthy`, `degraded`, or `unhealthy`)
- `timestamp`: ISO 8601 timestamp of the health check
- `database.status`: Database connection status (`connected` or `disconnected`)
- `database.response_time_ms`: Database query response time in milliseconds
- `database.error`: Error message if database is unavailable (optional)
- `database.engine`: Database engine being used

---

### Status: `GET /api/v1/status/`

Detailed status endpoint with comprehensive system information.

**Purpose**: Detailed system information for troubleshooting and monitoring dashboards

**Response Code**:
- `200 OK` - Always returns 200 (even if unhealthy) to allow troubleshooting

**Response Format**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-23T18:30:00.000Z",
  "version": "1.0.0",
  "api_version": "v1",
  "environment": "production",
  "uptime_seconds": 3600.5,
  "memory": {
    "used_mb": 256.5,
    "percent": 12.5
  },
  "database": {
    "status": "connected",
    "response_time_ms": 15.5,
    "engine": "django.db.backends.postgresql"
  }
}
```

**Fields**:
- `status`: Overall health status
- `timestamp`: ISO 8601 timestamp
- `version`: Application version
- `api_version`: API version (v1, v2, etc.)
- `environment`: Current environment (development, production, testing)
- `uptime_seconds`: Server uptime in seconds since start
- `memory.used_mb`: Memory usage in megabytes
- `memory.percent`: Memory usage as percentage
- `database.*`: Database health information (same as health endpoint)

---

### Readiness Probe: `GET /api/v1/health/ready/`

Kubernetes readiness probe endpoint.

**Purpose**: Indicates whether the service is ready to accept traffic

**Response Codes**:
- `200 OK` - Service is ready to accept traffic
- `503 Service Unavailable` - Service is not ready (dependencies unavailable)

**Response Format**:
```json
{
  "ready": true,
  "timestamp": "2025-10-23T18:30:00.000Z"
}
```

**Usage in Kubernetes**:
```yaml
readinessProbe:
  httpGet:
    path: /api/v1/health/ready/
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

### Liveness Probe: `GET /api/v1/health/live/`

Kubernetes liveness probe endpoint.

**Purpose**: Indicates whether the service is alive and should remain running

**Response Code**:
- `200 OK` - Service is alive (always returns 200 if server is running)

**Response Format**:
```json
{
  "alive": true,
  "timestamp": "2025-10-23T18:30:00.000Z"
}
```

**Important**: This endpoint does NOT check database or other dependencies. It only indicates that the server process is running. If this endpoint fails to respond, Kubernetes will restart the pod.

**Usage in Kubernetes**:
```yaml
livenessProbe:
  httpGet:
    path: /api/v1/health/live/
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 30
```

---

## Acceptance Criteria Validation

### ✓ Criterion 1: Server Operational Status
**Requirement**: When I send a request to the health endpoint, I should receive a response indicating the server is operational.

**Validation**:
- `GET /api/v1/health/` returns `200 OK` when healthy
- Response includes `status: "healthy"` field
- Database connectivity is verified and reported

### ✓ Criterion 2: Degraded Status Reporting
**Requirement**: When the data store is unavailable, I should see the health endpoint report degraded status.

**Validation**:
- Health endpoint returns `503 Service Unavailable` when database is down
- Response includes `status: "unhealthy"` field
- Database error details are included in response
- Endpoint remains accessible even when database is unavailable

### ✓ Criterion 3: Version and Uptime Statistics
**Requirement**: When I query the status endpoint, I should see version information and uptime statistics.

**Validation**:
- `GET /api/v1/status/` includes `version` field
- Response includes `api_version` field
- Response includes `uptime_seconds` field
- Response includes `memory` usage statistics
- Response includes `environment` information

### ✓ Criterion 4: Machine-Readable Response
**Requirement**: When monitoring systems query the health endpoint, they should receive a machine-readable response.

**Validation**:
- All responses use `application/json` content type
- Consistent structure across all health endpoints
- Standardized status values (`healthy`, `degraded`, `unhealthy`)
- ISO 8601 timestamps for easy parsing
- No authentication required for monitoring access

---

## Features

### 1. Database Connectivity Monitoring
All health check endpoints (except liveness) verify database connectivity:
- Executes simple query (`SELECT 1`) to verify connection
- Measures response time in milliseconds
- Reports connection status and errors
- Uses `DatabaseHealthCheck` from Story #4

### 2. Memory Usage Tracking
Status endpoint includes real-time memory usage:
- Memory used in megabytes
- Memory usage as percentage
- Uses `psutil` library for accurate measurements

### 3. Uptime Statistics
Status endpoint tracks server uptime:
- Seconds since server start
- Useful for understanding restart frequency
- Helps diagnose stability issues

### 4. Version Information
Status endpoint provides version details:
- Application version (`1.0.0`)
- API version (`v1`)
- Environment (development, production, testing)
- Helps verify correct deployment

### 5. Security
All health check endpoints:
- Do NOT expose database passwords or credentials
- Do NOT require authentication (accessible to monitoring systems)
- Provide minimal error details (no stack traces)
- Use structured, predictable responses

### 6. Kubernetes Integration
Dedicated endpoints for Kubernetes orchestration:
- **Readiness Probe**: Controls traffic routing (checks dependencies)
- **Liveness Probe**: Controls pod restarts (no dependency checks)

---

## Usage Examples

### cURL

**Health Check**:
```bash
curl -i http://localhost:8000/api/v1/health/
```

**Status**:
```bash
curl -i http://localhost:8000/api/v1/status/
```

**Readiness**:
```bash
curl -i http://localhost:8000/api/v1/health/ready/
```

**Liveness**:
```bash
curl -i http://localhost:8000/api/v1/health/live/
```

### Python

```python
import requests

# Health check
response = requests.get('http://localhost:8000/api/v1/health/')
if response.status_code == 200:
    print("Service is healthy")
    data = response.json()
    print(f"Database response time: {data['database']['response_time_ms']}ms")
else:
    print("Service is unhealthy")

# Status check
response = requests.get('http://localhost:8000/api/v1/status/')
data = response.json()
print(f"Version: {data['version']}")
print(f"Uptime: {data['uptime_seconds']} seconds")
print(f"Memory usage: {data['memory']['used_mb']} MB")
```

### JavaScript

```javascript
// Health check
fetch('http://localhost:8000/api/v1/health/')
  .then(response => response.json())
  .then(data => {
    console.log('Status:', data.status);
    console.log('Database:', data.database.status);
  });

// Status check
fetch('http://localhost:8000/api/v1/status/')
  .then(response => response.json())
  .then(data => {
    console.log('Version:', data.version);
    console.log('Uptime:', data.uptime_seconds, 'seconds');
    console.log('Memory:', data.memory.used_mb, 'MB');
  });
```

---

## Monitoring Integration

### Load Balancer Health Checks

**AWS Application Load Balancer (ALB)**:
```yaml
HealthCheckPath: /api/v1/health/
HealthCheckIntervalSeconds: 30
HealthCheckTimeoutSeconds: 5
HealthyThresholdCount: 2
UnhealthyThresholdCount: 3
Matcher:
  HttpCode: 200
```

**NGINX Upstream Health Checks**:
```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;

    # Health check
    check interval=3000 rise=2 fall=5 timeout=1000 type=http;
    check_http_send "GET /api/v1/health/ HTTP/1.0\r\n\r\n";
    check_http_expect_alive http_2xx;
}
```

### Kubernetes Probes

**Deployment YAML**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-backend
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: backend:latest
        ports:
        - containerPort: 8000

        # Readiness probe - controls traffic routing
        readinessProbe:
          httpGet:
            path: /api/v1/health/ready/
            port: 8000
            scheme: HTTP
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3

        # Liveness probe - controls pod restarts
        livenessProbe:
          httpGet:
            path: /api/v1/health/live/
            port: 8000
            scheme: HTTP
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3
```

### Prometheus Monitoring

**Metrics Scraping**:
```yaml
scrape_configs:
  - job_name: 'api-backend-health'
    scrape_interval: 30s
    metrics_path: /api/v1/status/
    static_configs:
      - targets: ['localhost:8000']
```

**Alert Rules**:
```yaml
groups:
  - name: backend-health
    rules:
      - alert: BackendUnhealthy
        expr: backend_health_status != 1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Backend service is unhealthy"
          description: "Backend has been unhealthy for 5 minutes"

      - alert: DatabaseSlowResponse
        expr: backend_database_response_time_ms > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database response time is slow"
          description: "Database response time > 1 second"
```

### Datadog Integration

```python
from datadog import statsd

# Monitor health check
response = requests.get('http://localhost:8000/api/v1/status/')
data = response.json()

# Send metrics to Datadog
statsd.gauge('backend.uptime', data['uptime_seconds'])
statsd.gauge('backend.memory.used_mb', data['memory']['used_mb'])
statsd.gauge('backend.memory.percent', data['memory']['percent'])
statsd.gauge('backend.database.response_time_ms',
             data['database']['response_time_ms'])

# Send health status
if data['status'] == 'healthy':
    statsd.gauge('backend.health', 1)
else:
    statsd.gauge('backend.health', 0)
```

---

## Testing

### Run All Health Check Tests

```bash
# Unit tests
pytest tests/unit/test_health_endpoints.py -v

# Integration tests
pytest tests/integration/test_health_endpoints_integration.py -v

# Acceptance tests (validate user story criteria)
pytest tests/acceptance/test_story_5_acceptance.py -v

# All health check tests
pytest -k "health" -v

# With coverage
pytest tests/unit/test_health_endpoints.py \
       tests/integration/test_health_endpoints_integration.py \
       tests/acceptance/test_story_5_acceptance.py \
       --cov=apps.api.health_views --cov-report=html
```

### Manual Testing

```bash
# Start development server
python manage.py runserver

# Test health endpoint
curl http://localhost:8000/api/v1/health/ | jq

# Test status endpoint
curl http://localhost:8000/api/v1/status/ | jq

# Test readiness endpoint
curl http://localhost:8000/api/v1/health/ready/ | jq

# Test liveness endpoint
curl http://localhost:8000/api/v1/health/live/ | jq
```

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────┐
│              Health Check Endpoints                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌──────────────┐               │
│  │HealthCheckView│  │  StatusView  │               │
│  │              │  │              │               │
│  │ GET /health/ │  │ GET /status/ │               │
│  └──────┬───────┘  └──────┬───────┘               │
│         │                  │                        │
│         └──────────┬───────┘                        │
│                    │                                │
│         ┌──────────▼──────────┐                    │
│         │ DatabaseHealthCheck │ (Story #4)         │
│         │                     │                    │
│         │ - check()          │                    │
│         │ - measure timing   │                    │
│         │ - format errors    │                    │
│         └──────────┬──────────┘                    │
│                    │                                │
│         ┌──────────▼──────────┐                    │
│         │   PostgreSQL DB     │                    │
│         │                     │                    │
│         │   SELECT 1          │                    │
│         └─────────────────────┘                    │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐               │
│  │ReadinessView │  │ LivenessView │               │
│  │              │  │              │               │
│  │ GET /ready/  │  │ GET /live/   │               │
│  └──────────────┘  └──────────────┘               │
│      (checks DB)      (no checks)                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Dependencies

- **Story #4**: `DatabaseHealthCheck` class provides database health monitoring
- **psutil**: System and process utilities for memory usage
- **Django REST Framework**: API views and responses
- **drf-spectacular**: OpenAPI documentation

---

## Best Practices

### 1. Monitor Health Check Endpoints
- Set up automated monitoring of `/api/v1/health/`
- Alert on 503 responses or slow response times
- Track database response time trends

### 2. Use Appropriate Probes
- **Load Balancers**: Use `/api/v1/health/`
- **Kubernetes Readiness**: Use `/api/v1/health/ready/`
- **Kubernetes Liveness**: Use `/api/v1/health/live/`
- **Monitoring Dashboards**: Use `/api/v1/status/`

### 3. Set Reasonable Timeouts
- Health checks should complete in < 5 seconds
- Liveness checks should complete in < 1 second
- Set appropriate timeout values in your monitoring configuration

### 4. Don't Restart on Temporary Failures
- Use `failureThreshold` > 1 in Kubernetes probes
- Avoid restarting pods for transient database issues
- Use readiness probe to stop traffic, not liveness

### 5. Monitor Response Times
- Track database response time over time
- Alert on sustained slow responses (> 1 second)
- Investigate spikes in response time

---

## Troubleshooting

### Health Endpoint Returns 503

**Symptom**: `GET /api/v1/health/` returns 503 Service Unavailable

**Possible Causes**:
1. Database is down or unreachable
2. Database credentials are incorrect
3. Network connectivity issues

**Diagnosis**:
```bash
# Check detailed status
curl http://localhost:8000/api/v1/status/ | jq

# Check database directly
python manage.py check_database

# Check database logs
docker logs postgres-container
```

**Solutions**:
- Verify database is running: `docker ps` or `systemctl status postgresql`
- Check database credentials in `.env` file
- Verify network connectivity to database host
- Check database logs for errors

### Slow Response Times

**Symptom**: Health check takes > 1 second to respond

**Possible Causes**:
1. Database queries are slow
2. Database connection pool exhausted
3. Network latency to database

**Diagnosis**:
```bash
# Check database response time
curl http://localhost:8000/api/v1/status/ | jq .database.response_time_ms

# Check database with management command
python manage.py check_database --verbose
```

**Solutions**:
- Optimize database queries
- Increase database connection pool size (CONN_MAX_AGE)
- Check database server resources (CPU, memory, disk)
- Verify network latency to database

### Kubernetes Pod Keeps Restarting

**Symptom**: Pod restarts frequently

**Possible Causes**:
1. Liveness probe failing
2. Application crashes
3. Out of memory

**Diagnosis**:
```bash
# Check pod status
kubectl get pods

# Check pod events
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name> --previous
```

**Solutions**:
- Increase `initialDelaySeconds` for liveness probe
- Increase `periodSeconds` to reduce check frequency
- Fix application errors causing crashes
- Increase pod memory limits

### Status Endpoint Shows Unhealthy but Service Works

**Symptom**: `/api/v1/status/` shows `status: "unhealthy"` but API endpoints work

**Explanation**: Status endpoint always returns 200 OK (even when unhealthy) to allow troubleshooting. Check the `status` field in the response body, not the HTTP status code.

**Action**: Check the `database` section of the response for details on what's unhealthy.

---

## Related Documentation

- [Database Health Checks](./DATABASE.md) - Story #4 database connectivity
- [Logging and Error Handling](./LOGGING.md) - Story #7 logging infrastructure
- [API Documentation](http://localhost:8000/api/v1/docs/) - OpenAPI/Swagger UI
- [Configuration Guide](./CONFIGURATION.md) - Environment configuration

---

## References

- [Kubernetes Liveness and Readiness Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Health Check Best Practices](https://microservices.io/patterns/observability/health-check-api.html)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [ISO 8601 Date Format](https://en.wikipedia.org/wiki/ISO_8601)
