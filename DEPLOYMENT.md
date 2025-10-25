# Deployment Guide

This guide provides detailed instructions for deploying the application to different environments: local development, staging, and production.

## Table of Contents

- [Environment Overview](#environment-overview)
- [Local Development Deployment](#local-development-deployment)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Environment Configuration Reference](#environment-configuration-reference)
- [Security Checklist](#security-checklist)
- [Rollback Procedures](#rollback-procedures)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Environment Overview

The application supports three distinct environments, each with specific configurations and security requirements:

| Environment | Purpose | Entry Point | Security Level |
|-------------|---------|-------------|----------------|
| **Local** | Development and testing | http://localhost/ | Low (development) |
| **Staging** | Pre-production validation | https://staging.yourdomain.com | High (production-like) |
| **Production** | Live application | https://yourdomain.com | Maximum |

### Environment Characteristics

| Feature | Local | Staging | Production |
|---------|-------|---------|------------|
| **Image Source** | Local build | Registry | Registry (scanned) |
| **Port Exposure** | All services | Proxy only | Proxy only |
| **Debug Mode** | Enabled | Disabled | Disabled |
| **SSL/TLS** | Optional | Required | Required (HSTS) |
| **Resource Limits** | None | Moderate | Strict |
| **Hot Reload** | Yes | No | No |
| **Log Level** | DEBUG | INFO | WARNING |

---

## Local Development Deployment

### Prerequisites

- Docker Engine 23.0+
- Docker Compose v2.0+
- 4GB RAM minimum (8GB recommended)
- 20GB disk space

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd architecture

# Start all services
./docker-dev.sh start

# Wait for services to be healthy
./docker-dev.sh status

# Access application
open http://localhost/
```

### Custom Configuration (Optional)

Create `.env.local` to override defaults:

```bash
# Copy example file
cp .env.local.example .env.local

# Edit configuration
nano .env.local
```

**Example `.env.local`:**
```bash
# Ports
PROXY_PORT=80
BACKEND_PORT=8000
FRONTEND_PORT=5173
DB_PORT=5432
REDIS_PORT=6379

# Database
DB_NAME=backend_db
DB_USER=postgres
DB_PASSWORD=postgres

# Django
DEBUG=True
SECRET_KEY=development-secret-key-change-in-production
DJANGO_SETTINGS_MODULE=config.settings.development

# Frontend Runtime Config
FRONTEND_APP_NAME=Application (Local Dev)
FRONTEND_API_URL=http://localhost
FRONTEND_ENABLE_DEBUG=true
```

### Starting Services

```bash
# Start all services
./docker-dev.sh start

# Start specific services
docker compose up -d db redis backend

# Start with rebuild
./docker-dev.sh rebuild
```

### Stopping Services

```bash
# Stop all services (preserves data)
./docker-dev.sh stop

# Stop and remove containers (preserves data)
docker compose down

# Remove everything including data (DESTRUCTIVE)
./docker-dev.sh clean-all
```

### Development Workflow

```bash
# View logs
./docker-dev.sh logs

# Apply migrations
./docker-dev.sh backend-migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Access Django shell
./docker-dev.sh backend-shell

# Access database
./docker-dev.sh db-shell

# Install dependencies
./docker-dev.sh exec frontend npm install <package>
./docker-dev.sh exec backend pip install <package>
```

---

## Staging Deployment

Staging environment mirrors production configuration for pre-deployment testing.

### Prerequisites

- Server with Docker Engine 23.0+
- Docker Compose v2.0+
- Domain name configured (staging.yourdomain.com)
- SSL/TLS certificate
- 8GB RAM minimum
- 50GB disk space

### Initial Setup

#### 1. Prepare Server

```bash
# SSH to staging server
ssh user@staging-server

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

#### 2. Clone Repository

```bash
# Clone repository
git clone <repository-url>
cd architecture

# Checkout desired branch/tag
git checkout v1.0.0  # or main, staging, etc.
```

#### 3. Create Environment File

```bash
# Copy staging example
cp .env.staging.example .env.staging

# Edit environment file
nano .env.staging
```

#### 4. Configure Environment Variables

**Required variables to set** (replace all `CHANGE_ME` values):

```bash
# Environment
ENVIRONMENT=staging

# Domain
DOMAIN=staging.yourdomain.com
ALLOWED_HOSTS=staging.yourdomain.com

# Database (use strong passwords)
DB_NAME=backend_staging_db
DB_USER=postgres
DB_PASSWORD=<generate-with-openssl-rand>  # 32+ characters

# Redis (use strong password)
REDIS_PASSWORD=<generate-with-openssl-rand>  # 32+ characters
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/1

# Django
SECRET_KEY=<generate-with-python>  # 50+ characters
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.staging

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS
CORS_ALLOWED_ORIGINS=https://staging.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://staging.yourdomain.com

# Frontend Runtime Config
FRONTEND_APP_NAME=Application (Staging)
FRONTEND_API_URL=https://staging.yourdomain.com
FRONTEND_ENABLE_DEBUG=false
FRONTEND_ENABLE_ANALYTICS=false

# Email (configure SMTP)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<password>

# Monitoring (optional)
SENTRY_DSN=<sentry-dsn>
```

#### 5. Generate Secure Credentials

```bash
# Generate database and Redis passwords (32+ characters)
openssl rand -base64 32

# Generate Django SECRET_KEY (50+ characters)
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

#### 6. Setup SSL/TLS Certificates

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy certificates (obtain from Let's Encrypt or CA)
cp /path/to/fullchain.pem nginx/ssl/staging.yourdomain.com.crt
cp /path/to/privkey.pem nginx/ssl/staging.yourdomain.com.key

# Set permissions
chmod 600 nginx/ssl/*.key
chmod 644 nginx/ssl/*.crt
```

**Using Let's Encrypt (Certbot)**:
```bash
# Install certbot
sudo apt install certbot -y

# Obtain certificate (requires port 80 temporarily)
sudo certbot certonly --standalone -d staging.yourdomain.com

# Certificates will be in: /etc/letsencrypt/live/staging.yourdomain.com/

# Link to project
ln -s /etc/letsencrypt/live/staging.yourdomain.com/fullchain.pem nginx/ssl/staging.yourdomain.com.crt
ln -s /etc/letsencrypt/live/staging.yourdomain.com/privkey.pem nginx/ssl/staging.yourdomain.com.key
```

#### 7. Validate Configuration

```bash
# Validate environment configuration
./docker-env.sh staging validate

# Expected output:
# ✓ Environment file exists: .env.staging
# ✓ No CHANGE_ME placeholders found
# ✓ Docker Compose configuration valid
# ✓ All required variables set
```

#### 8. Pull Pre-Built Images

```bash
# Authenticate to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u <username> --password-stdin

# Pull images
./docker-env.sh staging pull

# Or build locally if images not available
docker compose -f docker-compose.yml -f compose.staging.yml build
```

#### 9. Start Services

```bash
# Start all services
./docker-env.sh staging start

# Monitor startup
./docker-env.sh staging logs -f

# Wait for all services to be healthy (2-3 minutes)
./docker-env.sh staging ps
```

#### 10. Initialize Database

```bash
# Apply migrations
./docker-env.sh staging exec backend python manage.py migrate

# Collect static files
./docker-env.sh staging exec backend python manage.py collectstatic --noinput

# Create superuser
./docker-env.sh staging exec backend python manage.py createsuperuser
```

#### 11. Verify Deployment

```bash
# Check service health
./docker-env.sh staging ps

# Test health endpoints
curl https://staging.yourdomain.com/health
curl https://staging.yourdomain.com/api/v1/health/

# Run validation suite
./scripts/validate-orchestration.sh

# Check Django deployment settings
./docker-env.sh staging exec backend python manage.py check --deploy
```

### Updating Staging

```bash
# SSH to staging server
ssh user@staging-server
cd architecture

# Pull latest code
git pull origin staging  # or specific tag

# Pull latest images
./docker-env.sh staging pull

# Stop services
./docker-env.sh staging stop

# Start with new images
./docker-env.sh staging start

# Apply migrations
./docker-env.sh staging exec backend python manage.py migrate

# Verify health
./docker-env.sh staging ps
```

---

## Production Deployment

Production deployment requires maximum security and reliability.

### Prerequisites

- Production server with Docker Engine 23.0+
- Docker Compose v2.0+
- Domain name configured (yourdomain.com)
- Valid SSL/TLS certificate
- 16GB RAM minimum (32GB recommended)
- 100GB disk space (SSD recommended)
- Backup solution configured
- Monitoring solution configured

### Pre-Deployment Checklist

Before deploying to production, ensure:

#### Security Requirements

- [ ] All credentials are highly secure (48+ character passwords)
- [ ] SSL/TLS certificates are valid and trusted
- [ ] HTTPS is enforced (no HTTP access)
- [ ] HSTS is enabled with preload
- [ ] Debug mode is disabled (DEBUG=False)
- [ ] SECRET_KEY is unique and never used elsewhere
- [ ] Database and Redis passwords are unique
- [ ] All environment variables reviewed for security

#### Infrastructure Requirements

- [ ] Server meets minimum requirements (16GB RAM, 100GB disk)
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] SSH key authentication configured (password auth disabled)
- [ ] Automated backups configured and tested
- [ ] Monitoring and alerting set up
- [ ] Log aggregation configured
- [ ] DNS records point to production server
- [ ] SSL certificates valid and auto-renewal configured

#### Application Requirements

- [ ] Images built and security scanned (Trivy)
- [ ] All tests passing in CI/CD
- [ ] Staging deployment successful
- [ ] Database migrations tested
- [ ] Rollback procedure documented and tested
- [ ] Performance testing completed
- [ ] Load testing completed

### Initial Production Deployment

#### 1. Prepare Server

```bash
# SSH to production server
ssh user@production-server

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Configure firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

#### 2. Clone Repository

```bash
# Clone repository
git clone <repository-url>
cd architecture

# Checkout production tag
git checkout v1.0.0  # Use specific version tag, not main
```

#### 3. Create Production Environment File

```bash
# Copy production example
cp .env.production.example .env.production

# Secure file permissions
chmod 600 .env.production

# Edit environment file
nano .env.production
```

#### 4. Configure Production Variables

**CRITICAL: Use highly secure credentials (48+ characters)**

```bash
# Environment
ENVIRONMENT=production

# Domain
DOMAIN=yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (highly secure passwords)
DB_NAME=backend_prod_db
DB_USER=postgres
DB_PASSWORD=<generate-48-chars>  # 48+ characters minimum

# Redis (highly secure password)
REDIS_PASSWORD=<generate-48-chars>  # 48+ characters minimum
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/1

# Django
SECRET_KEY=<generate-50-chars>  # 50+ characters minimum
DEBUG=False
LOG_LEVEL=WARNING
DJANGO_SETTINGS_MODULE=config.settings.production

# Security (HTTPS enforced)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend Runtime Config
FRONTEND_APP_NAME=Application
FRONTEND_API_URL=https://yourdomain.com
FRONTEND_ENABLE_DEBUG=false
FRONTEND_ENABLE_ANALYTICS=true
FRONTEND_ANALYTICS_ID=<google-analytics-id>

# Email (production SMTP)
EMAIL_HOST=smtp.production.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<password>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Monitoring (required for production)
SENTRY_DSN=<sentry-dsn>
SENTRY_ENVIRONMENT=production

# Database Tuning
POSTGRES_SHARED_BUFFERS=512MB
POSTGRES_EFFECTIVE_CACHE_SIZE=2GB
POSTGRES_MAX_CONNECTIONS=200
POSTGRES_WORK_MEM=4MB

# Redis Tuning
REDIS_MAXMEMORY=1gb

# Celery
CELERY_WORKER_CONCURRENCY=8
```

#### 5. Generate Highly Secure Credentials

```bash
# Generate database and Redis passwords (48+ characters)
openssl rand -base64 48

# Generate Django SECRET_KEY (50+ characters)
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Store credentials securely (use password manager)
```

#### 6. Setup Production SSL/TLS

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy production certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/yourdomain.com.crt
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/yourdomain.com.key

# Set secure permissions
sudo chown $USER:$USER nginx/ssl/*
chmod 600 nginx/ssl/*.key
chmod 644 nginx/ssl/*.crt
```

#### 7. Critical Validation

```bash
# Validate environment (CRITICAL STEP)
./docker-env.sh production validate

# Validate no CHANGE_ME placeholders
grep -r "CHANGE_ME" .env.production
# Should return nothing

# Validate Docker Compose configuration
docker compose -f docker-compose.yml -f compose.production.yml config --quiet

# Validate SSL certificates
openssl x509 -in nginx/ssl/yourdomain.com.crt -noout -dates
```

#### 8. Pull Security-Scanned Images

```bash
# Authenticate to registry
echo $GITHUB_TOKEN | docker login ghcr.io -u <username> --password-stdin

# Pull production images (must be security-scanned)
./docker-env.sh production pull

# Verify images
docker images | grep -E "backend|frontend"
```

#### 9. Backup Preparation

```bash
# Create backup directory
mkdir -p backups

# Test backup script
./docker-dev.sh backup-db

# Configure automated backups (cron)
crontab -e
# Add: 0 2 * * * /path/to/architecture/scripts/backup-daily.sh
```

#### 10. Start Production Services

```bash
# Start all services
./docker-env.sh production start

# Monitor startup closely
./docker-env.sh production logs -f

# Wait for all services to be healthy (3-5 minutes)
watch -n 5 './docker-env.sh production ps'
```

#### 11. Initialize Production Database

```bash
# Apply migrations
./docker-env.sh production exec backend python manage.py migrate

# Collect static files
./docker-env.sh production exec backend python manage.py collectstatic --noinput

# Create superuser (use secure password)
./docker-env.sh production exec backend python manage.py createsuperuser
```

#### 12. Comprehensive Verification

```bash
# 1. Check all services are healthy
./docker-env.sh production ps | grep "healthy"

# 2. Verify resource limits are in effect
docker inspect app-backend | grep -A 20 "Resources"

# 3. Verify non-root users
docker compose exec backend whoami   # Should be: django
docker compose exec frontend whoami  # Should be: nginx

# 4. Test HTTPS endpoints
curl -I https://yourdomain.com/health
curl -I https://yourdomain.com/api/v1/health/

# 5. Verify HTTPS redirect
curl -I http://yourdomain.com/  # Should redirect to HTTPS

# 6. Run comprehensive validation
./scripts/validate-orchestration.sh --verbose

# 7. Check Django deployment settings
./docker-env.sh production exec backend python manage.py check --deploy

# 8. Test application functionality
# - Create test user account
# - Test login/logout
# - Test key features
# - Verify email sending
# - Check Sentry error reporting
```

#### 13. Enable Monitoring

```bash
# Start monitoring service (if using monitor script)
nohup ./scripts/monitor-services.sh --alert --email ops@yourdomain.com &

# Configure external monitoring
# - Setup uptime monitoring (UptimeRobot, Pingdom)
# - Configure log aggregation (ELK, Datadog)
# - Setup APM (Sentry, New Relic)
# - Configure alerting (PagerDuty, Slack)
```

### Updating Production

**Follow blue-green deployment pattern for zero downtime:**

```bash
# 1. Backup current state
./docker-env.sh production exec backend python manage.py dumpdata > backups/pre-update-$(date +%Y%m%d).json
./docker-dev.sh backup-db

# 2. Pull latest code
git fetch --tags
git checkout v1.1.0  # New version

# 3. Pull new images
./docker-env.sh production pull

# 4. Run migrations in test mode (doesn't apply)
./docker-env.sh production exec backend python manage.py migrate --plan

# 5. Stop services
./docker-env.sh production stop

# 6. Start with new version
./docker-env.sh production start

# 7. Apply migrations
./docker-env.sh production exec backend python manage.py migrate

# 8. Collect static files
./docker-env.sh production exec backend python manage.py collectstatic --noinput

# 9. Verify health
./docker-env.sh production ps
./scripts/validate-orchestration.sh

# 10. Monitor for issues
./docker-env.sh production logs -f
```

---

## Environment Configuration Reference

### Local Development

**File**: `.env.local` (optional, has sensible defaults)

**Purpose**: Rapid development iteration

**Key Settings**:
- Debug mode: `Enabled`
- Hot reload: `Enabled`
- Port exposure: `All services`
- Resource limits: `None`
- Credentials: `Simple (postgres/postgres)`

### Staging

**File**: `.env.staging` (required)

**Purpose**: Pre-production testing

**Key Settings**:
- Debug mode: `Disabled`
- Hot reload: `Disabled`
- Port exposure: `Proxy only`
- Resource limits: `Moderate`
- Credentials: `Secure (32+ chars)`
- SSL/TLS: `Required`

### Production

**File**: `.env.production` (required)

**Purpose**: Live application

**Key Settings**:
- Debug mode: `Disabled`
- Hot reload: `Disabled`
- Port exposure: `Proxy only`
- Resource limits: `Strict`
- Credentials: `Highly secure (48+ chars)`
- SSL/TLS: `Required with HSTS`
- Logging: `WARNING level`
- Monitoring: `Required`

---

## Security Checklist

### Pre-Deployment Security Review

#### Application Security

- [ ] DEBUG=False in production and staging
- [ ] SECRET_KEY is unique and never reused
- [ ] All passwords are strong (48+ chars for production)
- [ ] No hardcoded credentials in code
- [ ] Environment files have secure permissions (600)
- [ ] ALLOWED_HOSTS configured correctly
- [ ] CORS_ALLOWED_ORIGINS limited to specific domains
- [ ] CSRF_TRUSTED_ORIGINS configured correctly

#### Network Security

- [ ] Only reverse proxy port exposed (80, 443)
- [ ] Database and Redis not accessible from internet
- [ ] Backend and Frontend only accessible via proxy
- [ ] Firewall configured (ufw or iptables)
- [ ] SSH key authentication enabled
- [ ] SSH password authentication disabled

#### SSL/TLS Security

- [ ] Valid SSL certificate installed
- [ ] Certificate auto-renewal configured
- [ ] HTTPS enforced (SECURE_SSL_REDIRECT=True)
- [ ] HSTS enabled with long max-age
- [ ] HSTS includeSubDomains enabled
- [ ] HSTS preload enabled (for production)
- [ ] HTTP redirects to HTTPS

#### Container Security

- [ ] All containers run as non-root users
- [ ] Images security scanned (Trivy, no HIGH/CRITICAL CVEs)
- [ ] Resource limits defined for all services
- [ ] No privileged containers
- [ ] No host paths mounted (except logs)
- [ ] Restart policy configured correctly

#### Data Security

- [ ] Database backups configured and tested
- [ ] Backup encryption enabled
- [ ] Backup retention policy defined
- [ ] Volume encryption considered (for sensitive data)
- [ ] Secrets management solution considered

#### Monitoring Security

- [ ] Logging configured and aggregated
- [ ] Sentry or error tracking configured
- [ ] Uptime monitoring configured
- [ ] Security scanning in CI/CD
- [ ] Alert recipients configured

---

## Rollback Procedures

### Quick Rollback (Staging/Production)

```bash
# 1. Stop current deployment
./docker-env.sh production down

# 2. Checkout previous version
git checkout v1.0.0  # Previous working version

# 3. Pull previous images (if available)
docker pull ghcr.io/<org>/backend:v1.0.0
docker pull ghcr.io/<org>/frontend:v1.0.0

# 4. Update .env to use previous images
echo "BACKEND_IMAGE=ghcr.io/<org>/backend:v1.0.0" >> .env.production
echo "FRONTEND_IMAGE=ghcr.io/<org>/frontend:v1.0.0" >> .env.production

# 5. Start services
./docker-env.sh production start

# 6. Verify health
./docker-env.sh production ps
```

### Database Rollback

```bash
# If database changes need to be reverted

# 1. Stop backend
./docker-env.sh production stop backend celery

# 2. Restore database backup
docker compose exec -T db psql -U postgres -d backend_prod_db < backups/pre-update-20251025.sql

# 3. Rollback migrations (if needed)
./docker-env.sh production exec backend python manage.py migrate <app_name> <previous_migration>

# 4. Start backend
./docker-env.sh production start backend celery

# 5. Verify
./docker-env.sh production ps
```

---

## Monitoring and Maintenance

### Health Monitoring

```bash
# Real-time monitoring
./scripts/monitor-services.sh --watch

# Enable alerts
./scripts/monitor-services.sh --alert --email ops@yourdomain.com

# JSON output for external tools
./scripts/monitor-services.sh --once --json
```

### Log Management

```bash
# View logs
./docker-env.sh production logs

# View logs for specific service
./docker-env.sh production logs backend

# Follow logs in real-time
./docker-env.sh production logs -f

# View logs with timestamps
docker compose logs -t backend
```

### Resource Monitoring

```bash
# Real-time resource usage
docker stats

# Service-specific stats
docker stats app-backend app-frontend app-db app-redis

# Check resource limits
docker inspect app-backend | grep -A 20 "Resources"
```

### Backup Management

```bash
# Manual backup
./docker-dev.sh backup-db

# Automated backups (setup cron)
crontab -e
# Daily at 2 AM: 0 2 * * * /path/to/scripts/backup-daily.sh
# Weekly on Sunday: 0 3 * * 0 /path/to/scripts/backup-weekly.sh

# Test backup restore (staging only!)
docker compose exec -T db psql -U postgres -d backend_db < backups/backup.sql
```

### Updates and Patching

```bash
# Update Docker images (monthly or as needed)
./docker-env.sh production pull
./docker-env.sh production restart

# Update system packages (monthly)
sudo apt update && sudo apt upgrade -y

# Update SSL certificates (automatic with certbot)
sudo certbot renew --dry-run

# Review and update dependencies (monthly)
# - backend/requirements/base.txt
# - frontend/package.json
```

---

## Summary

You now have comprehensive deployment guides for:

✅ **Local Development**: Quick setup for development with hot reload
✅ **Staging**: Production-like environment for testing
✅ **Production**: Secure, optimized deployment with monitoring

**Key Deployment Commands**:
```bash
# Local
./docker-dev.sh start

# Staging
./docker-env.sh staging start

# Production
./docker-env.sh production start
```

**Always remember**:
1. Validate configuration before deployment
2. Backup before making changes
3. Test in staging before production
4. Monitor after deployment
5. Have rollback plan ready

For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

For getting started, see [GETTING_STARTED.md](GETTING_STARTED.md).
