# Environment-Specific Configuration (Story 12.4)

## Overview

The application supports three distinct environments (local, staging, production) using a single set of Docker Compose files with environment-specific overrides. This approach ensures consistency across environments while allowing necessary customizations.

**Key Achievement**: Same orchestration configuration works across all environments with environment-specific overrides.

## Architecture

### File Structure

```
architecture/
├── docker-compose.yml              # Base configuration (common across all environments)
├── compose.override.yml            # Local development overrides (auto-loaded)
├── compose.staging.yml             # Staging environment overrides
├── compose.production.yml          # Production environment overrides
├── .env.local.example              # Local environment variables template
├── .env.staging.example            # Staging environment variables template
├── .env.production.example         # Production environment variables template
└── docker-env.sh                   # Environment management helper script
```

### Configuration Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    docker-compose.yml                       │
│              (Base - Common Configuration)                   │
│  - Service definitions                                       │
│  - Network configuration                                     │
│  - Volume definitions                                        │
│  - Default health checks                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
                     Environment Layer
                            ↓
┌────────────────┬────────────────────┬─────────────────────┐
│  Local Dev     │      Staging       │     Production      │
│ compose.       │  compose.staging.  │  compose.production.│
│ override.yml   │      yml           │      yml            │
├────────────────┼────────────────────┼─────────────────────┤
│ - Bind mounts  │ - Named volumes    │ - Named volumes     │
│ - Debug ports  │ - No port exposure │ - No port exposure  │
│ - Hot reload   │ - Pre-built images │ - Pre-built images  │
│ - No limits    │ - Moderate limits  │ - Strict limits     │
│ - Dev tools    │ - HTTPS support    │ - HTTPS required    │
└────────────────┴────────────────────┴─────────────────────┘
                            ↓
                    Environment Variables
                            ↓
┌────────────────┬────────────────────┬─────────────────────┐
│  .env.local    │   .env.staging     │  .env.production    │
│  (optional)    │   (required)       │  (required)         │
├────────────────┼────────────────────┼─────────────────────┤
│ - Simple pass  │ - Secure passwords │ - Highly secure     │
│ - Debug=True   │ - Debug=False      │ - Debug=False       │
│ - Dev domains  │ - Staging domains  │ - Production domains│
└────────────────┴────────────────────┴─────────────────────┘
```

## Environment Comparison

### High-Level Differences

| Aspect | Local | Staging | Production |
|--------|-------|---------|------------|
| **Purpose** | Development | Pre-production testing | Live production |
| **Images** | Built locally | Registry (pre-built) | Registry (security-scanned) |
| **Ports** | All exposed | Only proxy | Only proxy |
| **Volumes** | Bind mounts | Named volumes | Named volumes (persistent) |
| **Debug** | Enabled | Disabled | Disabled |
| **Logging** | Verbose | Enhanced | Minimal |
| **Resources** | Unlimited | Moderate limits | Strict limits |
| **Security** | Relaxed | Production-like | Maximum |
| **HTTPS** | Optional | Required | Required |
| **Restart** | unless-stopped | always | always |

### Service Configuration Comparison

#### Backend Service

| Configuration | Local | Staging | Production |
|--------------|-------|---------|------------|
| **Image Source** | Build from `./backend` | `ghcr.io/.../backend:staging` | `ghcr.io/.../backend:latest` |
| **Target Stage** | `development` | `production` | `production` |
| **Debug Mode** | `True` | `False` | `False` |
| **Log Level** | `DEBUG` | `INFO` | `WARNING` |
| **Port Exposure** | `8000:8000` | None | None |
| **Bind Mounts** | Full source code | Logs only | Logs only |
| **CPU Limit** | Unlimited | 2 CPUs | 4 CPUs |
| **Memory Limit** | Unlimited | 2GB | 4GB |
| **Gunicorn Workers** | 2 | 4 | 8 |
| **Hot Reload** | Enabled | Disabled | Disabled |

#### Frontend Service

| Configuration | Local | Staging | Production |
|--------------|-------|---------|------------|
| **Image Source** | Build from `./frontend` | `ghcr.io/.../frontend:staging` | `ghcr.io/.../frontend:latest` |
| **Target Stage** | `development` | `production` | `production` |
| **Node Env** | `development` | `production` | `production` |
| **Port Exposure** | `5173:5173` | None | None |
| **Bind Mounts** | Full source code | None | None |
| **CPU Limit** | Unlimited | 1 CPU | 2 CPUs |
| **Memory Limit** | Unlimited | 1GB | 2GB |
| **HMR** | Enabled | Disabled | Disabled |
| **Source Maps** | Full | None | None |

#### Database Service

| Configuration | Local | Staging | Production |
|--------------|-------|---------|------------|
| **Image** | `postgres:15-alpine` | `postgres:15-alpine` | `postgres:15-alpine` |
| **Port Exposure** | `5432:5432` | None | None |
| **Database Name** | `backend_db` | `backend_staging_db` | `backend_prod_db` |
| **Password** | `postgres` | Secure (32+ chars) | Highly secure (48+ chars) |
| **Shared Buffers** | 128MB | 256MB | 512MB |
| **Max Connections** | 50 | 100 | 200 |
| **CPU Limit** | 2 CPUs | 2 CPUs | 4 CPUs |
| **Memory Limit** | 1GB | 1GB | 2GB |
| **Volume** | `app-postgres-data` | `app-staging-postgres-data` | `app-production-postgres-data` |

#### Redis Service

| Configuration | Local | Staging | Production |
|--------------|-------|---------|------------|
| **Image** | `redis:7-alpine` | `redis:7-alpine` | `redis:7-alpine` |
| **Port Exposure** | `6379:6379` | None | None |
| **Password** | None | Required (32+ chars) | Required (48+ chars) |
| **Max Memory** | 256MB | 512MB | 1GB |
| **Persistence** | Yes (appendonly) | Yes (enhanced) | Yes (optimized) |
| **CPU Limit** | 0.5 CPUs | 1 CPU | 2 CPUs |
| **Memory Limit** | 256MB | 512MB | 1GB |

#### Proxy Service (Nginx)

| Configuration | Local | Staging | Production |
|--------------|-------|---------|------------|
| **Image** | `nginx:1.27-alpine` | `nginx:1.27-alpine` | `nginx:1.27-alpine` |
| **Config File** | `nginx.conf` | `nginx.staging.conf` | `nginx.production.conf` |
| **HTTP Port** | `80:80` | `80:80` | `80:80` (→ HTTPS) |
| **HTTPS Port** | None | `443:443` | `443:443` |
| **SSL/TLS** | Not required | Required | Required (HSTS) |
| **CPU Limit** | 0.5 CPUs | 1 CPU | 2 CPUs |
| **Memory Limit** | 256MB | 512MB | 1GB |

### Environment Variables Comparison

#### Core Variables

| Variable | Local | Staging | Production |
|----------|-------|---------|------------|
| **ENVIRONMENT** | `local` | `staging` | `production` |
| **DEBUG** | `True` | `False` | `False` |
| **LOG_LEVEL** | `DEBUG` | `INFO` | `WARNING` |
| **SECRET_KEY** | Simple (insecure) | Secure (50+ chars) | Highly secure (50+ chars) |
| **ALLOWED_HOSTS** | `localhost,127.0.0.1` | `staging.yourdomain.com` | `yourdomain.com` |

#### Security Variables

| Variable | Local | Staging | Production |
|----------|-------|---------|------------|
| **SECURE_SSL_REDIRECT** | `False` | `True` | `True` |
| **SESSION_COOKIE_SECURE** | `False` | `True` | `True` |
| **CSRF_COOKIE_SECURE** | `False` | `True` | `True` |
| **SECURE_HSTS_SECONDS** | N/A | N/A | `31536000` |
| **SECURE_HSTS_PRELOAD** | N/A | N/A | `True` |

#### Frontend Runtime Config

| Variable | Local | Staging | Production |
|----------|-------|---------|------------|
| **FRONTEND_API_URL** | `http://localhost` | `https://staging.yourdomain.com` | `https://yourdomain.com` |
| **FRONTEND_API_ENABLE_LOGGING** | `true` | `true` | `false` |
| **FRONTEND_APP_NAME** | `Application (Local Dev)` | `Application (Staging)` | `Application` |
| **FRONTEND_ENABLE_DEBUG** | `true` | `false` | `false` |
| **FRONTEND_ENABLE_ANALYTICS** | `false` | `false` | `true` |

### Resource Limits Comparison

#### Total Stack Resources

| Resource | Local | Staging | Production |
|----------|-------|---------|------------|
| **Total CPU Limit** | Unlimited | ~12 CPUs | ~20 CPUs |
| **Total CPU Reserved** | Unlimited | ~6 CPUs | ~10 CPUs |
| **Total Memory Limit** | Unlimited | ~8GB | ~14GB |
| **Total Memory Reserved** | Unlimited | ~4GB | ~7GB |

#### Per-Service Breakdown

**Local Development** (No Limits):
- All services can use host resources freely
- Good for development but may impact host performance

**Staging** (Moderate Limits):
- Database: 2 CPUs / 1GB memory
- Redis: 1 CPU / 512MB memory
- Backend: 2 CPUs / 2GB memory
- Frontend: 1 CPU / 1GB memory
- Proxy: 1 CPU / 512MB memory
- Celery: 2 CPUs / 1GB memory

**Production** (Strict Limits):
- Database: 4 CPUs / 2GB memory
- Redis: 2 CPUs / 1GB memory
- Backend: 4 CPUs / 4GB memory
- Frontend: 2 CPUs / 2GB memory
- Proxy: 2 CPUs / 1GB memory
- Celery: 4 CPUs / 2GB memory

## Usage Guide

### Setup

#### 1. Create Environment Files

```bash
# Local development (optional - has sensible defaults)
cp .env.local.example .env.local
# Edit .env.local if needed

# Staging (required)
cp .env.staging.example .env.staging
# Edit .env.staging - replace all CHANGE_ME values

# Production (required)
cp .env.production.example .env.production
# Edit .env.production - replace all CHANGE_ME values with HIGHLY SECURE credentials
```

#### 2. Generate Secure Passwords

```bash
# For staging/production databases and Redis
openssl rand -base64 32

# For production (even stronger)
openssl rand -base64 48

# For Django SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Using the Helper Script

#### Local Development

```bash
# Start local environment (uses compose.override.yml automatically)
./docker-env.sh local start

# View logs
./docker-env.sh local logs

# Stop services
./docker-env.sh local stop

# Restart
./docker-env.sh local restart

# Validate configuration
./docker-env.sh local validate

# Execute command in backend
./docker-env.sh local exec backend python manage.py migrate
```

#### Staging Environment

```bash
# Validate staging configuration first
./docker-env.sh staging validate

# Pull pre-built images
./docker-env.sh staging pull

# Start staging environment
./docker-env.sh staging start

# View logs for specific service
./docker-env.sh staging logs backend

# Stop staging
./docker-env.sh staging stop
```

#### Production Environment

```bash
# Validate production configuration (CRITICAL STEP)
./docker-env.sh production validate

# Pull security-scanned images
./docker-env.sh production pull

# Start production environment
./docker-env.sh production start

# Monitor logs
./docker-env.sh production logs

# Check service status
./docker-env.sh production ps
```

### Using Docker Compose Directly

If you prefer using Docker Compose directly:

```bash
# Local (uses docker-compose.yml + compose.override.yml automatically)
docker compose up -d
docker compose down

# Staging (explicit files)
docker compose -f docker-compose.yml -f compose.staging.yml --env-file .env.staging up -d
docker compose -f docker-compose.yml -f compose.staging.yml --env-file .env.staging down

# Production (explicit files)
docker compose -f docker-compose.yml -f compose.production.yml --env-file .env.production up -d
docker compose -f docker-compose.yml -f compose.production.yml --env-file .env.production down
```

## Configuration Validation

### Pre-Deployment Checklist

#### All Environments

- [ ] Base `docker-compose.yml` exists and is valid YAML
- [ ] Environment-specific override file exists
- [ ] Environment variables file exists (staging/production)
- [ ] `docker compose config` validates successfully
- [ ] All required services defined
- [ ] Health checks configured for all services
- [ ] Networks properly configured

#### Staging/Production Specific

- [ ] All `CHANGE_ME` placeholders replaced
- [ ] Database password is strong (32+ characters)
- [ ] Redis password is strong (32+ characters)
- [ ] SECRET_KEY is unique and strong (50+ characters)
- [ ] ALLOWED_HOSTS configured with correct domains
- [ ] CORS_ALLOWED_ORIGINS configured correctly
- [ ] CSRF_TRUSTED_ORIGINS configured correctly
- [ ] SSL certificates in place
- [ ] Email service configured
- [ ] Sentry DSN configured (recommended)
- [ ] Backup strategy defined

#### Production Specific

- [ ] All passwords are highly secure (48+ characters minimum)
- [ ] HTTPS enforced (SECURE_SSL_REDIRECT=True)
- [ ] HSTS enabled with preload
- [ ] Debug mode disabled (DEBUG=False)
- [ ] Log level set to WARNING or ERROR
- [ ] Resource limits appropriate for expected load
- [ ] Backup automation configured
- [ ] Monitoring and alerting set up
- [ ] Django deployment check passed: `python manage.py check --deploy`

### Validation Commands

```bash
# Validate environment configuration
./docker-env.sh <environment> validate

# Show merged configuration
./docker-env.sh <environment> config

# Check for common issues
docker compose -f docker-compose.yml -f compose.<environment>.yml config --quiet

# Test Django deployment readiness (production)
./docker-env.sh production exec backend python manage.py check --deploy
```

## Switching Between Environments

### On Same Host

To switch environments on the same host, you need to stop one environment before starting another (they may share port 80):

```bash
# Stop current environment
./docker-env.sh <current-env> down

# Start new environment
./docker-env.sh <new-env> start
```

### Multiple Environments Simultaneously

To run multiple environments on the same host, you need to change exposed ports. Modify the `.env.<environment>` file:

```bash
# .env.staging
PROXY_PORT=8080  # Change from 80

# .env.production
PROXY_PORT=9080  # Change from 80
```

Then both can run simultaneously:
- Local: http://localhost/
- Staging: http://localhost:8080/
- Production: http://localhost:9080/

## Troubleshooting

### Common Issues

#### 1. "Environment file contains CHANGE_ME placeholders"

**Solution**: Edit the environment file and replace all `CHANGE_ME` values with actual credentials.

```bash
# Generate secure values
openssl rand -base64 32  # For passwords
python3 -c "import secrets; print(secrets.token_urlsafe(50))"  # For SECRET_KEY
```

#### 2. "Environment file not found"

**Solution**: Create the environment file from the example:

```bash
cp .env.staging.example .env.staging
# Edit .env.staging
```

#### 3. "Port already in use"

**Solution**: Either stop the conflicting service or change the port in the environment file:

```bash
# Change PROXY_PORT in .env.<environment>
PROXY_PORT=8080
```

#### 4. "Configuration validation failed"

**Solution**: Check Docker Compose syntax:

```bash
./docker-env.sh <environment> config
# Review error messages
```

#### 5. "Cannot connect to database"

**Solution**: Check database service is healthy and credentials are correct:

```bash
./docker-env.sh <environment> ps
./docker-env.sh <environment> logs db
```

#### 6. "Frontend cannot reach backend API"

**Solution**: Verify CORS and runtime configuration:

```bash
# Check backend environment variables
./docker-env.sh <environment> exec backend env | grep FRONTEND

# Check CORS settings
./docker-env.sh <environment> exec backend env | grep CORS
```

## Best Practices

### General

1. **Always validate before deploying**: Run `./docker-env.sh <env> validate` before starting services
2. **Use the helper script**: It includes validation and best practices
3. **Keep base configuration DRY**: Common settings in `docker-compose.yml`, environment-specific in override files
4. **Version control override files**: Commit all `compose.*.yml` files but NOT `.env.*` files
5. **Document environment differences**: Update this file when adding environment-specific features

### Local Development

1. **Use bind mounts**: Enable live code reloading for rapid development
2. **Expose all ports**: Access services directly for debugging
3. **Keep it simple**: Use simple credentials, no SSL, minimal security
4. **Don't limit resources**: Let services use what they need

### Staging

1. **Mirror production**: Configuration should be as close to production as possible
2. **Use pre-built images**: Test the same images that will go to production
3. **Enable enhanced logging**: More verbose than production for debugging
4. **Moderate security**: Use real SSL certificates, secure passwords, but allow more access for testing
5. **Separate credentials**: Never use production credentials in staging

### Production

1. **Security first**: All security features enabled, HTTPS required, strong passwords
2. **Use registry images**: Never build in production, always use pre-built, scanned images
3. **Strict resource limits**: Prevent resource exhaustion
4. **Minimal logging**: INFO or WARNING level to reduce I/O
5. **Zero trust**: No direct service access, everything through reverse proxy
6. **Backup everything**: Automated backups with tested restore procedures
7. **Monitor actively**: Application performance monitoring, alerting, error tracking
8. **Test in staging first**: All changes validated in staging before production

## Related Documentation

- [Story 12.1 - Unified Orchestration](./UNIFIED_ORCHESTRATION.md)
- [Story 12.2 - Service Dependencies](./SERVICE_DEPENDENCIES.md)
- [Story 12.3 - Reverse Proxy Configuration](./REVERSE_PROXY.md)
- [Runtime Configuration Guide](../../RUNTIME_CONFIG_IMPLEMENTATION.md)
- [Docker Best Practices](../../context/devops/docker.md)

## Success Criteria

Story 12.4 acceptance criteria verification:

✅ **AC1 - Environment-specific configuration loading**
- Each environment loads its appropriate configuration (ports, URLs, resource limits)
- Verified through `docker compose config` showing correct merged configuration
- Environment variables control all environment-specific behavior

✅ **AC2 - Environment switching**
- Services use correct configuration without modifying orchestration files
- Switching achieved via `./docker-env.sh <environment> <command>`
- Same base `docker-compose.yml` used across all environments

✅ **AC3 - Clear environment differences**
- Comprehensive comparison table documents all differences
- Environment variables clearly separated by environment
- Configuration changes visible via `./docker-env.sh <env> config`

✅ **AC4 - Consistent environment structure**
- All environments follow same structure and naming patterns
- New environments can be created by copying and modifying existing override files
- Validation ensures consistency across environments

## Conclusion

The environment-specific configuration system provides:

1. **Consistency**: Same orchestration files work across all environments
2. **Flexibility**: Environment-specific customizations via override files
3. **Security**: Different security postures for different environments
4. **Simplicity**: Single command to deploy to any environment
5. **Validation**: Built-in checks prevent misconfiguration
6. **Documentation**: Clear understanding of environment differences

This implementation satisfies all acceptance criteria for Story 12.4 and provides a solid foundation for managing the application across the development lifecycle.
