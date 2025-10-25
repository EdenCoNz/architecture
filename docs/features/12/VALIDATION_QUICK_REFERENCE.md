# Orchestration Validation - Quick Reference

**Feature**: #12 - Unified Multi-Service Orchestration
**Story**: 12.11 - Orchestration Testing and Validation

---

## Quick Start

```bash
# Start orchestration
./docker-dev.sh start

# Run validation
./docker-dev.sh validate

# Or use script directly
./scripts/validate-orchestration.sh
```

---

## Common Commands

### Basic Validation

```bash
# Full validation (recommended after startup)
./scripts/validate-orchestration.sh

# Quick validation (health checks only)
./scripts/validate-orchestration.sh --quick

# Verbose output (for troubleshooting)
./scripts/validate-orchestration.sh --verbose

# Via helper script
./docker-dev.sh validate
./docker-dev.sh validate --quick
./docker-dev.sh validate --verbose
```

### CI/CD Integration

```bash
# JSON output for automation
./scripts/validate-orchestration.sh --json

# Don't wait for services (check current state)
./scripts/validate-orchestration.sh --no-wait

# Custom wait timeout
./scripts/validate-orchestration.sh --max-wait 180
```

---

## What Gets Validated

### ✓ Service Health
- All 5 services running (db, redis, backend, frontend, proxy)
- Health check status for each service
- Container uptime and status

### ✓ Reverse Proxy Routing
- `/` → Frontend
- `/api/v1/health/` → Backend API
- `/admin/` → Django Admin
- `/health` → Proxy health check
- Static file serving

### ✓ Frontend-Backend Connectivity
- Backend API accessible through proxy
- API returns valid JSON responses
- CORS headers configured
- Frontend accessible through proxy
- WebSocket support (Vite HMR)

### ✓ Database Connectivity
- PostgreSQL accepts connections
- Backend can query database
- Redis responds to commands
- Health endpoint reports database status

### ✓ Environment Configuration
- Required environment variables set
- Frontend runtime config accessible
- Network isolation validated
- Service dependencies configured

### ✓ Security Headers
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Gzip compression

---

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | All validations passed | Continue with development/deployment |
| 1 | One or more validations failed | Check output for specific failures |
| 2 | Script error | Check arguments and environment |

---

## Troubleshooting

### Service Not Healthy

```bash
# Check which services are unhealthy
docker compose ps

# View logs for failing service
docker compose logs backend

# Check dependencies
./scripts/check-dependencies.sh --verbose

# Restart service
docker compose restart backend

# Re-validate
./docker-dev.sh validate
```

### Routing Issues

```bash
# Check nginx configuration
docker exec app-proxy nginx -t

# View proxy logs
docker compose logs proxy

# Test direct backend access
docker exec app-proxy wget -O- http://backend:8000/api/v1/health/

# Re-validate routing
./docker-dev.sh validate --verbose
```

### Database Connection Issues

```bash
# Check database health
docker exec app-db pg_isready -U postgres

# View backend logs
docker compose logs backend | grep -i database

# Test database connection from backend
docker exec app-backend python manage.py check --database default

# Re-validate
./docker-dev.sh validate --verbose
```

---

## Integration Points

### With Existing Scripts

```bash
# 1. Check service dependencies (foundational)
./scripts/check-dependencies.sh --verbose

# 2. Validate health check configurations
./scripts/validate-health-checks.sh

# 3. Comprehensive end-to-end validation (Story 12.11)
./scripts/validate-orchestration.sh --verbose
```

### Recommended Development Workflow

```bash
# Start development session
./docker-dev.sh start

# Validate everything is working
./docker-dev.sh validate

# Make code changes...

# Quick health check
./docker-dev.sh validate --quick

# If issues found
./docker-dev.sh validate --verbose
docker compose logs <service>

# Fix and re-validate
./docker-dev.sh validate
```

### CI/CD Pipeline Example

```bash
# In your CI/CD script
docker compose up -d
./scripts/validate-orchestration.sh --json > validation.json

# Check results
if [ "$(jq -r '.status' validation.json)" != "passed" ]; then
  echo "Validation failed!"
  jq '.failed_tests' validation.json
  exit 1
fi
```

---

## Performance

| Mode | Execution Time | Use Case |
|------|---------------|----------|
| Quick | 5-10 seconds | Regular health checks, CI/CD |
| Full | 15-30 seconds | After startup, troubleshooting |
| Full + Verbose | 20-40 seconds | Deep debugging |

---

## Key Files

| File | Purpose |
|------|---------|
| `/home/ed/Dev/architecture/scripts/validate-orchestration.sh` | Main validation script |
| `/home/ed/Dev/architecture/docs/features/12/STORY_12.11_VALIDATION.md` | Full documentation |
| `/home/ed/Dev/architecture/docker-dev.sh` | Helper script with validate command |
| `/home/ed/Dev/architecture/scripts/check-dependencies.sh` | Dependency health checks |
| `/home/ed/Dev/architecture/scripts/validate-health-checks.sh` | Health check config validation |

---

## Quick Tips

1. **Always validate after startup**
   ```bash
   ./docker-dev.sh start && ./docker-dev.sh validate
   ```

2. **Use quick mode for regular checks**
   ```bash
   ./docker-dev.sh validate --quick
   ```

3. **Use verbose mode when troubleshooting**
   ```bash
   ./docker-dev.sh validate --verbose
   ```

4. **Check JSON output structure for automation**
   ```bash
   ./scripts/validate-orchestration.sh --json | jq .
   ```

5. **Combine with logs for debugging**
   ```bash
   ./docker-dev.sh validate --verbose
   ./docker-dev.sh logs backend
   ```

---

## Common Issues

### Issue: "Timeout waiting for services"
**Solution**: Increase wait timeout
```bash
./scripts/validate-orchestration.sh --max-wait 300
```

### Issue: "Backend API is not accessible"
**Solution**: Check backend health and logs
```bash
docker compose ps backend
docker compose logs backend
docker exec app-backend curl http://localhost:8000/api/v1/health/
```

### Issue: "Database connection issue detected"
**Solution**: Verify database is healthy
```bash
docker exec app-db pg_isready -U postgres
docker compose restart backend
./docker-dev.sh validate
```

### Issue: "Route returns 502 Bad Gateway"
**Solution**: Check upstream service health
```bash
docker compose ps
docker compose logs proxy
docker compose restart proxy
```

---

## Getting Help

```bash
# Show validation script help
./scripts/validate-orchestration.sh --help

# Show docker-dev.sh help
./docker-dev.sh help

# View full documentation
cat docs/features/12/STORY_12.11_VALIDATION.md

# Check implementation log
cat docs/features/12/implementation-log.json | jq '.[] | select(.story == "12.11")'
```

---

## Related Documentation

- [Story 12.1 - Unified Orchestration](./STORY_12.1_COMPLETE.md)
- [Story 12.2 - Service Dependencies](./DEPENDENCY_MANAGEMENT.md)
- [Story 12.3 - Reverse Proxy](./STORY_12.3_REVERSE_PROXY_CONFIGURATION.md)
- [Story 12.11 - Full Validation Documentation](./STORY_12.11_VALIDATION.md)
- [Unified Orchestration Overview](./UNIFIED_ORCHESTRATION.md)

---

**Last Updated**: 2025-10-25
**Status**: ✅ Completed
