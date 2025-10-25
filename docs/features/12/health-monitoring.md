# Service Health Monitoring Documentation (Story 12.9)

**Feature**: #12 - Unified Multi-Service Orchestration
**Story**: 12.9 - Service Health Monitoring
**Status**: Completed
**Date**: 2025-10-25

## Overview

This document describes the comprehensive health monitoring system implemented for all services in the application stack. The system provides real-time health status tracking, automatic service recovery, and operator notification for persistent failures.

## Features Implemented

### 1. Health Checks for All Services

All services have properly configured Docker health checks that verify service availability and functionality:

| Service | Health Check | Interval | Timeout | Retries | Start Period |
|---------|--------------|----------|---------|---------|--------------|
| **Database** (PostgreSQL) | `pg_isready` command | 5s | 3s | 5 | 15s |
| **Cache** (Redis) | `redis-cli ping` | 5s | 3s | 5 | 10s |
| **Backend** (Django) | HTTP GET `/api/v1/health/` | 15s | 5s | 3 | 45s |
| **Frontend** (React/Vite) | HTTP GET `http://localhost:5173` | 15s | 5s | 3 | 35s |
| **Reverse Proxy** (Nginx) | HTTP GET `/health` | 15s | 5s | 3 | 15s |

### 2. Automatic Service Restart

All services are configured with the `restart: unless-stopped` policy, which ensures:

- **Automatic recovery**: Services restart automatically when they fail
- **Dependency-aware restart**: Services with `depends_on` restart when dependencies fail
- **Manual control**: Services only stay stopped when explicitly stopped by operators

### 3. Health Monitoring Tools

#### Quick Status Check (docker-dev.sh)

The development helper script provides instant health status:

```bash
./docker-dev.sh status
```

**Output includes**:
- Service running status
- Health check status (healthy/starting/unhealthy)
- Application URLs
- Database and cache connection information

#### Comprehensive Health Validation (validate-health-checks.sh)

Validates all health checks are properly configured and functioning:

```bash
./scripts/validate-health-checks.sh          # Validate all services
./scripts/validate-health-checks.sh --backend # Backend only
./scripts/validate-health-checks.sh -v       # Verbose mode
```

**Checks performed**:
- ✅ Container running status
- ✅ Health check configuration presence
- ✅ Health endpoint accessibility
- ✅ Response structure validation
- ✅ Database connectivity verification
- ✅ Service dependency chain

#### Real-time Health Monitoring (monitor-services.sh)

Continuous monitoring for operators (NEW in Story 12.9):

```bash
./scripts/monitor-services.sh               # Continuous monitoring
./scripts/monitor-services.sh --once        # Single check
./scripts/monitor-services.sh --watch       # Watch mode (refresh UI)
./scripts/monitor-services.sh --alert       # Enable failure alerts
./scripts/monitor-services.sh --json        # JSON output
```

**Features**:
- Real-time health status display
- Service uptime tracking
- Container restart count
- Last health check timestamp
- Health status change detection
- Persistent failure alerting
- Structured logging

### 4. Notification System

The monitoring script includes a built-in notification system for persistent failures:

**Alert Triggers**:
- Service becomes unhealthy
- Service stops running
- Consecutive failure threshold reached (default: 3)
- Maximum restart attempts exceeded (default: 3)

**Notification Methods**:
- Console alerts (colored output)
- Log file (`logs/health-alerts.log`)
- Email notifications (optional, requires `mail` command)
- State tracking (`logs/health-state.json`)

**Configuration**:
```bash
# Enable alerts with email notification
./scripts/monitor-services.sh --alert --email admin@example.com
```

### 5. Health Check Endpoints

#### Backend Health Endpoints

The backend provides multiple health check endpoints:

1. **General Health**: `/api/v1/health/`
   - Checks: Database connectivity, Redis connectivity
   - Returns: Overall status, component statuses, timestamp
   - Usage: Primary health check endpoint

2. **Liveness Probe**: `/api/v1/health/live/`
   - Checks: Application is running and responsive
   - Returns: Simple status indicator
   - Usage: Kubernetes/orchestrator liveness probe

3. **Readiness Probe**: `/api/v1/health/ready/`
   - Checks: Application ready to accept traffic
   - Returns: Status with dependency checks
   - Usage: Kubernetes/orchestrator readiness probe

4. **Status Endpoint**: `/api/v1/status/`
   - Checks: Detailed system status
   - Returns: Service info, version, environment
   - Usage: Monitoring dashboards

#### Reverse Proxy Health Endpoints

The nginx reverse proxy provides health endpoints:

1. **Simple Health**: `/health`
   - Returns: 200 OK with "healthy" message
   - Usage: Load balancer health checks

2. **Proxy Status**: `/proxy-status`
   - Returns: JSON with proxy and upstream status
   - Usage: Detailed monitoring

## Usage Scenarios

### Scenario 1: Check Service Health Status

**Operator wants to see if all services are healthy**

```bash
# Quick check
./docker-dev.sh status

# Detailed validation
./scripts/validate-health-checks.sh

# Real-time monitoring
./scripts/monitor-services.sh --once
```

### Scenario 2: Monitor Services Continuously

**Operator wants to monitor services during deployment**

```bash
# Watch mode with visual refresh
./scripts/monitor-services.sh --watch --interval 5
```

**Output**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Service Health Monitor - 2025-10-25 22:30:00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ db            healthy         Uptime: 2h 15m       Restarts: 0   Last: 22:29:55
✅ redis         healthy         Uptime: 2h 15m       Restarts: 0   Last: 22:29:56
✅ backend       healthy         Uptime: 2h 10m       Restarts: 0   Last: 22:29:50
✅ frontend      healthy         Uptime: 2h 10m       Restarts: 0   Last: 22:29:52
✅ proxy         healthy         Uptime: 2h 10m       Restarts: 0   Last: 22:29:54

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ All services are healthy

Refreshing in 5s... (Press Ctrl+C to stop)
```

### Scenario 3: Detect and Alert on Failures

**Operator wants to be notified when services fail**

```bash
# Enable alert mode
./scripts/monitor-services.sh --alert

# With email notifications
./scripts/monitor-services.sh --alert --email ops@example.com
```

**When a service becomes unhealthy**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  ALERT: Service Health Issue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service:   backend
Status:    unhealthy
Time:      2025-10-25T22:35:00Z
Message:   Health check output: Connection refused
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Scenario 4: Investigate Persistent Failures

**Backend service repeatedly fails and reaches restart limit**

```bash
# Check alert log
cat logs/health-alerts.log

# View state file for failure counts
cat logs/health-state.json
```

**Alert when persistent failure detected**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  ALERT: Service Health Issue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service:   backend
Status:    PERSISTENT_FAILURE
Time:      2025-10-25T22:40:00Z
Message:   Service has failed 3 consecutive health checks and reached maximum
           restart attempts (3/3). Manual intervention required.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Manual intervention steps**:
1. Check service logs: `docker compose logs backend --tail=100`
2. Inspect container: `docker inspect app-backend`
3. Check dependencies: `./scripts/validate-health-checks.sh`
4. Review recent changes: `git log --oneline -10`
5. Restart manually: `docker compose restart backend`

### Scenario 5: Integration with External Monitoring

**Operator wants to integrate with monitoring systems (Prometheus, Datadog, etc.)**

```bash
# JSON output for programmatic consumption
./scripts/monitor-services.sh --once --json
```

**Output**:
```json
{
  "timestamp": "2025-10-25T22:30:00Z",
  "services": [
    {
      "service": "db",
      "health": "healthy",
      "uptime": "2h 15m",
      "restart_count": 0,
      "last_check": "2025-10-25T22:29:55Z",
      "health_output": "accepting connections",
      "consecutive_failures": 0
    },
    {
      "service": "backend",
      "health": "healthy",
      "uptime": "2h 10m",
      "restart_count": 0,
      "last_check": "2025-10-25T22:29:50Z",
      "health_output": "{\"status\":\"healthy\",\"database\":\"connected\"}",
      "consecutive_failures": 0
    }
  ]
}
```

## Troubleshooting

### Service Shows as Unhealthy

**Symptoms**: Service appears unhealthy in health checks

**Diagnosis**:
```bash
# Check service logs
docker compose logs <service-name> --tail=100

# Inspect health check details
docker inspect --format='{{json .State.Health}}' app-<service-name> | jq

# Run validation
./scripts/validate-health-checks.sh --<service-name> -v
```

**Common causes**:
1. **Database/Redis not ready**: Wait for dependencies to be healthy first
2. **Port conflict**: Check if another service is using the port
3. **Configuration error**: Review service environment variables
4. **Resource constraints**: Check Docker resource limits
5. **Network issues**: Verify Docker network connectivity

### Service Restart Loop

**Symptoms**: Service continuously restarts

**Diagnosis**:
```bash
# Check restart count
docker compose ps

# View recent logs across restarts
docker compose logs <service-name> --tail=500

# Check for resource issues
docker stats app-<service-name>
```

**Common causes**:
1. **Missing dependencies**: Check `depends_on` configuration
2. **Configuration errors**: Validate environment variables
3. **Resource exhaustion**: Increase memory/CPU limits
4. **Application bugs**: Review application startup logs
5. **Failed migrations**: Check database migration status

### Health Check Fails but Service Works

**Symptoms**: Health check reports unhealthy but service functions normally

**Diagnosis**:
```bash
# Test health endpoint manually
curl -v http://localhost:8000/api/v1/health/  # Backend
curl -v http://localhost:5173                  # Frontend
curl -v http://localhost/health                # Proxy

# Check health check configuration
docker inspect app-<service-name> | grep -A 10 Healthcheck
```

**Common causes**:
1. **Timeout too short**: Increase health check timeout
2. **Wrong endpoint**: Verify health check URL is correct
3. **Network isolation**: Ensure health check can reach endpoint
4. **Dependency check failing**: Check backend dependencies (DB, Redis)

### Alert Fatigue (Too Many Alerts)

**Symptoms**: Receiving alerts for transient issues

**Solutions**:
```bash
# Adjust failure threshold (default: 3)
FAILURE_THRESHOLD=5 ./scripts/monitor-services.sh --alert

# Increase check interval
./scripts/monitor-services.sh --alert --interval 30

# Filter logs for critical alerts only
grep "PERSISTENT_FAILURE" logs/health-alerts.log
```

## Best Practices

### 1. Regular Monitoring

- **Development**: Use `./docker-dev.sh status` before starting work
- **Deployment**: Use `./scripts/monitor-services.sh --watch` during deployments
- **Production**: Integrate JSON output with external monitoring systems

### 2. Health Check Design

- **Keep it fast**: Health checks should complete in < 3 seconds
- **Check dependencies**: Backend checks DB and Redis connectivity
- **Use appropriate intervals**: Balance between responsiveness and overhead
- **Set start periods**: Give services time to initialize before health checks

### 3. Alert Management

- **Use alert mode in production**: Always enable `--alert` for production monitoring
- **Configure email notifications**: Set up proper email recipients
- **Review alert logs regularly**: Check `logs/health-alerts.log` weekly
- **Tune thresholds**: Adjust failure thresholds based on service reliability

### 4. Incident Response

- **Check logs first**: Always start with `docker compose logs <service>`
- **Verify dependencies**: Use `./scripts/validate-health-checks.sh`
- **Review recent changes**: Check git history and deployments
- **Document resolution**: Update troubleshooting guide with new issues

## Configuration Reference

### Docker Compose Health Check Format

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
  interval: 15s      # How often to run health check
  timeout: 5s        # Max time for health check to complete
  retries: 3         # Number of consecutive failures before unhealthy
  start_period: 45s  # Grace period before health checks count as failures
```

### Restart Policy Options

```yaml
restart: unless-stopped  # Default for all services (recommended)
# restart: always        # Alternative: restart even if manually stopped
# restart: on-failure    # Alternative: only restart on non-zero exit
# restart: no            # Alternative: never restart automatically
```

### Monitor Script Environment Variables

```bash
# Failure detection
FAILURE_THRESHOLD=3       # Consecutive failures before alert (default: 3)
MAX_RESTART_ATTEMPTS=3    # Max restarts before manual intervention (default: 3)

# Check interval
WATCH_INTERVAL=5          # Seconds between checks in watch mode (default: 5)

# Notification
NOTIFICATION_EMAIL=""     # Email address for alerts (default: none)
```

## Files and Locations

### Scripts

- `/scripts/monitor-services.sh` - Real-time health monitoring (Story 12.9)
- `/scripts/validate-health-checks.sh` - Health check validation
- `/docker-dev.sh` - Development helper with status command

### Configuration

- `/docker-compose.yml` - Service health check definitions
- `/backend/Dockerfile` - Backend health check implementation
- `/frontend/Dockerfile` - Frontend health check implementation
- `/nginx/nginx.conf` - Reverse proxy health endpoints

### Logs and State

- `/logs/health-monitoring.log` - Continuous monitoring log
- `/logs/health-alerts.log` - Alert notifications
- `/logs/health-state.json` - Current health state tracking

## Related Documentation

- [Docker Compose Configuration](../../docker-compose.yml)
- [Service Dependency Management](./service-dependencies.md)
- [Backend Health Endpoints](../../backend/docs/api/health.md)
- [Deployment Guide](./deployment.md)

## Future Enhancements

Potential improvements for health monitoring (beyond Story 12.9 scope):

1. **Metrics Collection**: Integrate with Prometheus for historical metrics
2. **Dashboard**: Web-based health monitoring dashboard
3. **Advanced Alerting**: Integration with PagerDuty, Slack, etc.
4. **Predictive Monitoring**: ML-based anomaly detection
5. **Distributed Tracing**: OpenTelemetry integration
6. **Auto-scaling**: Trigger scaling based on health metrics

## Summary

Story 12.9 implements a comprehensive health monitoring system that:

✅ Monitors health of all services (db, redis, backend, frontend, proxy)
✅ Automatically restarts unhealthy services
✅ Alerts operators when restart attempts are exhausted
✅ Provides last health check result and timestamp
✅ Offers multiple monitoring tools for different use cases
✅ Includes detailed troubleshooting guidance

All acceptance criteria for Story 12.9 have been met.
