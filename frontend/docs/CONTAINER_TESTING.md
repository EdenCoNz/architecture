# Frontend Container Functional Testing

This document describes the comprehensive functional testing approach for frontend Docker containers.

## Overview

The frontend container functional testing validates that built Docker images work correctly in a containerized environment. This ensures that runtime issues are caught before deployment and that containers serve the application properly.

## Test Coverage

The functional tests verify the following aspects:

### 1. Container Startup
- Container starts successfully
- No immediate crashes or failures
- Proper initialization of services

### 2. Container Health
- Container maintains running state
- Health checks pass (for production containers)
- No critical errors in startup logs

### 3. Application Endpoints
- Root endpoint (`/`) responds with HTTP 200
- HTML content is served correctly
- Application bootstrap is successful

### 4. Content Verification
- HTML structure is valid (DOCTYPE, root element)
- JavaScript bundles are referenced
- React application initializes properly

### 5. Static Assets
- Static files are accessible
- Asset delivery works correctly
- File serving is functional

### 6. Security Headers (Production only)
- X-Frame-Options header present
- X-Content-Type-Options header present
- X-XSS-Protection header present

### 7. Health Endpoint (Production only)
- `/health` endpoint responds with HTTP 200
- Health check mechanism works

### 8. Container Logs
- No critical errors in logs
- Clean startup without exceptions
- Proper logging configuration

### 9. Resource Usage
- Container CPU and memory usage within acceptable limits
- No resource leaks detected

## Test Script

The functional tests are implemented in `test-container-functional.sh`:

```bash
./test-container-functional.sh <container-image> <container-port> [test-port]
```

### Arguments

- **container-image**: The Docker image to test (e.g., `frontend:prod-abc123`)
- **container-port**: Internal container port (80 for production, 5173 for development)
- **test-port**: Optional external port to bind (default: 8080 for prod, 5173 for dev)

### Examples

```bash
# Test production container
./test-container-functional.sh frontend:prod-abc123 80 8080

# Test development container
./test-container-functional.sh frontend:dev-abc123 5173

# Test production container on custom port
./test-container-functional.sh frontend:prod-latest 80 9000
```

### Exit Codes

- **0**: All tests passed
- **1**: Container startup failed
- **2**: Health check failed
- **3**: Application endpoint failed
- **4**: Content verification failed
- **5**: Critical functionality failed

## CI/CD Integration

The functional tests are integrated into the GitHub Actions CI/CD pipeline in two jobs:

### Development Container Testing

Job: `build-container-dev`

```yaml
- name: Run comprehensive functional tests
  run: |
    cd frontend
    chmod +x test-container-functional.sh
    ./test-container-functional.sh frontend:dev-${{ github.sha }} 5173
```

**Tests executed:**
- Container startup
- Container running state
- Application endpoint accessibility
- Content verification
- Container logs analysis
- Resource usage monitoring

### Production Container Testing

Job: `build-container-prod`

```yaml
- name: Run comprehensive functional tests
  run: |
    cd frontend
    chmod +x test-container-functional.sh
    ./test-container-functional.sh frontend:prod-${{ github.sha }} 80 8080
```

**Tests executed:**
- Container startup
- Container health status
- Health endpoint verification
- Application endpoint accessibility
- Content verification
- Static asset delivery
- Security headers validation
- Container logs analysis
- Resource usage monitoring

## Local Testing

To test containers locally before pushing:

### Build and Test Production Container

```bash
# Build production container
docker build --target production \
  --build-arg VITE_API_URL=https://api.example.com \
  -t frontend:prod-local .

# Run functional tests
./test-container-functional.sh frontend:prod-local 80 8080
```

### Build and Test Development Container

```bash
# Build development container
docker build --target development -t frontend:dev-local .

# Run functional tests
./test-container-functional.sh frontend:dev-local 5173
```

## Test Output

The test script provides detailed output with color-coded results:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend Container Functional Testing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Configuration:
  Image:          frontend:prod-abc123
  Container Port: 80
  Test Port:      8080
  Startup Wait:   15s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test 1: Container Startup
─────────────────────────────────────────────────────────────────────────
[INFO] Starting container...
[SUCCESS] Container started: abc123def456

Test 2: Container Running State
─────────────────────────────────────────────────────────────────────────
[INFO] Waiting 15s for container to initialize...
[SUCCESS] Container is running

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Container Image: frontend:prod-abc123
  Container ID:    abc123def456

  Tests Passed:    10
  Tests Failed:    0

[SUCCESS] All functional tests passed!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Troubleshooting

### Test Failures

If tests fail, the script provides detailed error messages and container logs:

```bash
[ERROR] Application endpoint failed after 5 attempts (HTTP 000)

Container logs:
...
```

### Common Issues

**Port already in use:**
```bash
# Use a different test port
./test-container-functional.sh frontend:prod-local 80 9000
```

**Container fails to start:**
- Check Docker daemon is running
- Verify image exists: `docker images`
- Check build logs for errors
- Review Dockerfile configuration

**Health check fails:**
- Verify health endpoint is configured correctly
- Check nginx configuration in Dockerfile
- Ensure health check timeout is sufficient

**Content verification fails:**
- Verify build completed successfully
- Check static files are in correct location
- Review nginx server configuration

## Best Practices

1. **Run tests locally before pushing** to catch issues early
2. **Review test output** to understand failures
3. **Check container logs** when tests fail for root cause
4. **Test both development and production containers** for consistency
5. **Validate security headers** in production builds
6. **Monitor resource usage** to prevent excessive consumption

## References

- [Docker Documentation](https://docs.docker.com/)
- [Frontend Dockerfile](/home/ed/Dev/architecture/frontend/Dockerfile)
- [GitHub Actions Workflow](/.github/workflows/frontend-ci.yml)
- [Container Development Guide](/home/ed/Dev/architecture/frontend/DOCKER.md)
