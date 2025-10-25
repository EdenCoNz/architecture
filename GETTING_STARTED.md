# Getting Started with Unified Multi-Service Orchestration

**Welcome to the application!** This guide will help you get the complete application stack running locally within minutes, and understand how to deploy it to different environments.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [First Time Setup](#first-time-setup)
- [Common Commands](#common-commands)
- [Understanding the Stack](#understanding-the-stack)
- [Development Workflow](#development-workflow)
- [Environment Configuration](#environment-configuration)
- [Deploying to Staging/Production](#deploying-to-stagingproduction)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## Quick Start

**Get the application running in 3 commands:**

```bash
# 1. Start all services
./docker-dev.sh start

# 2. Wait for services to be healthy (1-2 minutes)
./docker-dev.sh status

# 3. Open application in your browser
open http://localhost/
```

**That's it!** The complete application stack is now running with:
- Frontend (React/Vite SPA)
- Backend (Django REST API)
- Database (PostgreSQL)
- Cache (Redis)
- Reverse Proxy (Nginx)

---

## Prerequisites

Before starting, ensure you have the following installed:

### Required Software

| Software | Minimum Version | Purpose |
|----------|----------------|---------|
| **Docker Engine** | 23.0+ | Container runtime |
| **Docker Compose** | v2.0+ | Multi-container orchestration |
| **Git** | 2.0+ | Version control |

### System Requirements

- **CPU**: 2+ cores (4+ recommended)
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 20GB free space
- **OS**: Linux, macOS, or Windows with WSL2

### Verify Installation

```bash
# Check Docker version
docker --version
# Expected: Docker version 23.0 or higher

# Check Docker Compose version
docker compose version
# Expected: Docker Compose version v2.0 or higher

# Verify Docker is running
docker ps
# Should show running containers or empty list (no errors)
```

### Docker Desktop Configuration (if applicable)

If using Docker Desktop, ensure adequate resources are allocated:

1. Open Docker Desktop → Settings → Resources
2. Set minimum resources:
   - **CPUs**: 2 cores minimum (4 recommended)
   - **Memory**: 4GB minimum (8GB recommended)
   - **Disk**: 20GB minimum
3. Click "Apply & Restart"

---

## First Time Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd architecture
```

### 2. Create Environment Files (Optional)

The application works out-of-the-box with sensible defaults. Create custom environment files only if you need to override defaults:

```bash
# Local development (optional - has good defaults)
cp .env.local.example .env.local
# Edit .env.local if needed (ports, database credentials, etc.)
```

**Note**: For staging and production environments, see [Environment Configuration](#environment-configuration) section.

### 3. Start the Application

```bash
# Start all services
./docker-dev.sh start

# Output:
# [+] Running 6/6
#  ✔ Container app-db          Healthy
#  ✔ Container app-redis        Healthy
#  ✔ Container app-backend      Healthy
#  ✔ Container app-frontend     Healthy
#  ✔ Container app-proxy        Healthy
#  ✔ Container app-celery       Started (optional)
```

### 4. Verify Everything is Running

```bash
# Check service health
./docker-dev.sh status

# Output:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   Service Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✅ db            healthy
# ✅ redis         healthy
# ✅ backend       healthy
# ✅ frontend      healthy
# ✅ proxy         healthy
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   Access Points (Unified Entry Point)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Application:  http://localhost/
# API:          http://localhost/api/
# Admin:        http://localhost/admin/
# Health:       http://localhost/health
```

### 5. Access the Application

Open your browser and navigate to:
- **Application**: http://localhost/
- **API Documentation**: http://localhost/api/
- **Django Admin**: http://localhost/admin/

---

## Common Commands

### Service Management

```bash
# Start all services
./docker-dev.sh start

# Stop all services (preserves data)
./docker-dev.sh stop

# Restart all services
./docker-dev.sh restart

# View service status
./docker-dev.sh status

# View service details
./docker-dev.sh ps
```

### Viewing Logs

```bash
# View logs from all services (real-time)
./docker-dev.sh logs

# View logs from specific service
./docker-dev.sh logs backend
./docker-dev.sh logs frontend
./docker-dev.sh logs db

# View last N lines of logs
docker compose logs --tail=50 backend

# View logs since timestamp
docker compose logs --since 5m
```

### Rebuilding Services

```bash
# Rebuild all services (when Dockerfile changes)
./docker-dev.sh rebuild

# Rebuild specific service
./docker-dev.sh rebuild backend
./docker-dev.sh rebuild frontend

# Clean rebuild (no cache)
docker compose build --no-cache
./docker-dev.sh start
```

### Shell Access

```bash
# Django shell (Python REPL with Django context)
./docker-dev.sh backend-shell

# Frontend container shell
./docker-dev.sh frontend-shell

# PostgreSQL shell
./docker-dev.sh db-shell

# Redis CLI
./docker-dev.sh redis-cli

# General container shell access
docker compose exec <service-name> /bin/bash
```

### Database Operations

```bash
# Apply database migrations
./docker-dev.sh backend-migrate

# Create new migrations
./docker-dev.sh backend-makemigrations

# Create Django superuser
docker compose exec backend python manage.py createsuperuser

# Access database directly
docker compose exec db psql -U postgres -d backend_db
```

### Data Management

```bash
# View volume information
./docker-dev.sh volumes

# Backup database
./docker-dev.sh backup-db

# Backup all data
./docker-dev.sh backup

# Clean containers (preserves data)
./docker-dev.sh clean

# Clean everything (DESTRUCTIVE - removes all data)
./docker-dev.sh clean-all
```

---

## Understanding the Stack

### Service Architecture

The application uses a **unified multi-service orchestration** approach with a reverse proxy as the single entry point:

```
┌─────────────────────────────────────────────────────────────┐
│  Browser → http://localhost/                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Reverse Proxy (Nginx) - Port 80                            │
│  - Routes traffic based on URL path                          │
│  - UNIFIED ENTRY POINT for the entire stack                 │
└────┬────────────────────────────────────────────────────┬───┘
     │                                                     │
     │  /                                                  │  /api/*, /admin/*, /media/*
     │  /@vite/*, /ws                                      │
     ▼                                                     ▼
┌─────────────────────────┐              ┌──────────────────────────┐
│  Frontend               │              │  Backend                 │
│  React/Vite SPA         │              │  Django REST API         │
│  Port 5173 (internal)   │              │  Port 8000 (internal)    │
└─────────────────────────┘              └─────────┬────────────────┘
                                                   │
                                   ┌───────────────┴────────────────┐
                                   │                                 │
                                   ▼                                 ▼
                       ┌─────────────────────┐      ┌─────────────────────┐
                       │  PostgreSQL         │      │  Redis              │
                       │  Port 5432          │      │  Port 6379          │
                       │  (internal)         │      │  (internal)         │
                       └─────────────────────┘      └─────────────────────┘
```

### Services Explained

| Service | Purpose | Internal Port | Access |
|---------|---------|---------------|--------|
| **Reverse Proxy (Nginx)** | Unified entry point, routes traffic | 80 | http://localhost/ |
| **Frontend (React/Vite)** | User interface | 5173 | Via proxy at `/` |
| **Backend (Django)** | REST API, business logic | 8000 | Via proxy at `/api/` |
| **Database (PostgreSQL)** | Data persistence | 5432 | Backend only |
| **Cache (Redis)** | Caching, session storage, task queue | 6379 | Backend only |
| **Celery (Optional)** | Background task processing | N/A | Not exposed |

### URL Routing

The reverse proxy routes requests based on URL paths:

| URL Path | Destination | Purpose |
|----------|------------|---------|
| `/` | Frontend | React SPA application |
| `/api/*` | Backend | REST API endpoints |
| `/admin/*` | Backend | Django admin interface |
| `/static/*` | Backend | Django static files (CSS, JS) |
| `/media/*` | Backend | User-uploaded media files |
| `/health` | Proxy | Reverse proxy health check |
| `/@vite/*` | Frontend | Vite development assets |
| `/ws` | Frontend | WebSocket for hot module replacement |

### Network Architecture

**Security Model**:
- All services communicate via private Docker network (`app-network`)
- Only the reverse proxy exposes port 80 to the host
- Database and Redis are completely isolated from external access
- Backend and Frontend are only accessible through the reverse proxy

**Benefits**:
- Single entry point simplifies access
- No CORS issues (same-origin policy satisfied)
- Enhanced security through network isolation
- Simplified firewall rules (only port 80/443 needed)

### Data Persistence

Data persists across container restarts using named Docker volumes:

| Volume | Content | Persistence |
|--------|---------|-------------|
| `app-postgres-data` | Database records | Permanent |
| `app-redis-data` | Cache data | Permanent |
| `app-backend-media` | User uploads | Permanent |
| `app-backend-static` | Static files | Permanent |
| `app-frontend-node-modules` | Node.js dependencies | Temporary* |
| `app-proxy-logs` | Nginx logs | Permanent |

*Temporary volumes can be safely removed and rebuilt.

---

## Development Workflow

### Typical Development Session

```bash
# 1. Start environment
./docker-dev.sh start

# 2. Wait for services to be healthy (check with status)
./docker-dev.sh status

# 3. Open logs in separate terminal (optional)
./docker-dev.sh logs

# 4. Open application in browser
open http://localhost/

# 5. Make code changes
#    - Frontend: Edit files in frontend/src/ → Hot Module Replacement (~100ms)
#    - Backend: Edit .py files → Auto-reload (1-2 seconds)

# 6. Install new dependencies if needed
./docker-dev.sh exec frontend npm install <package>
./docker-dev.sh exec backend pip install <package>

# 7. Run database migrations if needed
./docker-dev.sh backend-migrate

# 8. Stop environment when done
./docker-dev.sh stop
```

### Live Code Reloading

**Frontend (React/Vite)**:
- Changes to files in `frontend/src/` automatically reload the browser
- Hot Module Replacement (HMR) preserves application state
- Reload time: ~100ms

**Backend (Django)**:
- Changes to `.py` files automatically restart the Django server
- Uses watchdog library for enhanced file watching
- Reload time: 1-2 seconds

**No rebuilding required!** Just edit and save files.

### Installing Dependencies

Dependencies can be installed without rebuilding containers:

```bash
# Frontend (npm)
./docker-dev.sh exec frontend npm install axios
./docker-dev.sh exec frontend npm install -D @types/react

# Backend (pip)
./docker-dev.sh exec backend pip install requests
./docker-dev.sh exec backend pip install django-extensions

# Dependencies are available immediately
```

**Persisting dependencies**:
- Frontend: Update `frontend/package.json`
- Backend: Update `backend/requirements/dev.txt` or `backend/requirements/base.txt`

### Running Tests

```bash
# Frontend tests
docker compose exec frontend npm test
docker compose exec frontend npm run test:coverage

# Backend tests
docker compose exec backend python manage.py test
docker compose exec backend pytest
docker compose exec backend pytest --cov

# Linting
docker compose exec frontend npm run lint
docker compose exec backend flake8
docker compose exec backend black --check .
```

### Database Migrations

```bash
# Create new migrations
./docker-dev.sh backend-makemigrations

# Apply migrations
./docker-dev.sh backend-migrate

# Show migration status
docker compose exec backend python manage.py showmigrations

# Rollback migration
docker compose exec backend python manage.py migrate <app_name> <migration_name>
```

---

## Environment Configuration

The application supports three environments: **local**, **staging**, and **production**.

### Local Development

**Default behavior** - Works out-of-the-box with sensible defaults.

```bash
# Uses docker-compose.yml + compose.override.yml automatically
./docker-dev.sh start

# Or using Docker Compose directly
docker compose up -d
```

**Characteristics**:
- All ports exposed for debugging
- Bind mounts for live code reloading
- Development dependencies included
- Debug mode enabled
- Simple credentials (postgres/postgres)
- No resource limits

### Staging Environment

**Pre-production testing environment** - Mirrors production configuration.

#### Setup

```bash
# 1. Create staging environment file
cp .env.staging.example .env.staging

# 2. Edit .env.staging - Replace all CHANGE_ME values
nano .env.staging

# 3. Validate configuration
./docker-env.sh staging validate

# 4. Pull pre-built images (if available)
./docker-env.sh staging pull

# 5. Start staging environment
./docker-env.sh staging start

# 6. Monitor startup
./docker-env.sh staging logs -f
```

**Characteristics**:
- Uses pre-built production images
- Only reverse proxy port exposed
- Moderate resource limits
- HTTPS support
- Secure credentials required
- Production-like security settings

### Production Environment

**Live production deployment** - Maximum security and performance.

#### Setup

```bash
# 1. Create production environment file
cp .env.production.example .env.production

# 2. Edit .env.production - Use highly secure credentials
nano .env.production

# 3. CRITICAL: Validate configuration
./docker-env.sh production validate

# 4. Pull security-scanned images
./docker-env.sh production pull

# 5. Start production environment
./docker-env.sh production start

# 6. Verify deployment
./docker-env.sh production ps
./scripts/validate-orchestration.sh
```

**Characteristics**:
- Uses security-scanned production images
- Only reverse proxy port exposed
- Strict resource limits
- HTTPS enforced
- Highly secure credentials required (48+ characters)
- All security features enabled
- Minimal logging (WARNING level)

### Environment Comparison

| Feature | Local | Staging | Production |
|---------|-------|---------|------------|
| **Port Exposure** | All services | Proxy only | Proxy only |
| **Code Mounting** | Bind mounts | None | None |
| **Hot Reload** | Enabled | Disabled | Disabled |
| **Debug Mode** | Enabled | Disabled | Disabled |
| **Resource Limits** | None | Moderate | Strict |
| **SSL/TLS** | Optional | Required | Required (enforced) |
| **Credentials** | Simple | Secure | Highly secure |
| **Image Source** | Local build | Registry | Registry (scanned) |

---

## Deploying to Staging/Production

### Pre-Deployment Checklist

Before deploying to staging or production, ensure:

#### Required Steps

- [ ] Environment file created (`.env.staging` or `.env.production`)
- [ ] All `CHANGE_ME` placeholders replaced with real values
- [ ] Database password is strong (32+ characters for staging, 48+ for production)
- [ ] Redis password is strong (32+ characters for staging, 48+ for production)
- [ ] SECRET_KEY is unique and strong (50+ characters)
- [ ] ALLOWED_HOSTS configured with correct domain(s)
- [ ] SSL/TLS certificates in place (`nginx/ssl/`)
- [ ] Configuration validated: `./docker-env.sh <env> validate`

#### Production-Specific

- [ ] All passwords are highly secure (48+ characters minimum)
- [ ] HTTPS enforced (SECURE_SSL_REDIRECT=True)
- [ ] Debug mode disabled (DEBUG=False)
- [ ] HSTS enabled with preload
- [ ] Log level set to WARNING or ERROR
- [ ] Backup strategy defined and tested
- [ ] Monitoring and alerting configured
- [ ] Django deployment check passed

### Generating Secure Credentials

```bash
# Database and Redis passwords (staging)
openssl rand -base64 32

# Database and Redis passwords (production)
openssl rand -base64 48

# Django SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Deployment Process

#### 1. Initial Deployment

```bash
# Set environment (staging or production)
ENVIRONMENT=production  # or staging

# Validate configuration
./docker-env.sh $ENVIRONMENT validate

# Pull pre-built images
./docker-env.sh $ENVIRONMENT pull

# Start services
./docker-env.sh $ENVIRONMENT start

# Wait for services to be healthy
./docker-env.sh $ENVIRONMENT ps

# Run database migrations
./docker-env.sh $ENVIRONMENT exec backend python manage.py migrate

# Collect static files
./docker-env.sh $ENVIRONMENT exec backend python manage.py collectstatic --noinput

# Create superuser (if needed)
./docker-env.sh $ENVIRONMENT exec backend python manage.py createsuperuser

# Validate deployment
./scripts/validate-orchestration.sh
```

#### 2. Updating Deployment

```bash
# Set environment
ENVIRONMENT=production  # or staging

# Pull latest images
./docker-env.sh $ENVIRONMENT pull

# Stop services
./docker-env.sh $ENVIRONMENT stop

# Start with new images
./docker-env.sh $ENVIRONMENT start

# Run migrations
./docker-env.sh $ENVIRONMENT exec backend python manage.py migrate

# Verify health
./docker-env.sh $ENVIRONMENT ps
```

#### 3. Rollback Procedure

```bash
# Set environment
ENVIRONMENT=production  # or staging

# Stop current deployment
./docker-env.sh $ENVIRONMENT down

# Pull previous image version
docker pull ghcr.io/<org>/backend:previous-tag
docker pull ghcr.io/<org>/frontend:previous-tag

# Update image tags in .env file
echo "BACKEND_IMAGE=ghcr.io/<org>/backend:previous-tag" >> .env.$ENVIRONMENT
echo "FRONTEND_IMAGE=ghcr.io/<org>/frontend:previous-tag" >> .env.$ENVIRONMENT

# Start services
./docker-env.sh $ENVIRONMENT start

# Verify health
./docker-env.sh $ENVIRONMENT ps
```

### Post-Deployment Verification

```bash
# Check all services are healthy
./docker-env.sh $ENVIRONMENT ps | grep "healthy"

# Verify resource limits are in effect
docker inspect app-backend | grep -A 10 "Resources"

# Verify non-root users
docker compose exec backend whoami   # Should be: django
docker compose exec frontend whoami  # Should be: nginx

# Test application endpoints
curl https://yourdomain.com/health
curl https://yourdomain.com/api/v1/health/

# Run comprehensive validation
./scripts/validate-orchestration.sh

# Check Django deployment settings
./docker-env.sh $ENVIRONMENT exec backend python manage.py check --deploy
```

---

## Common Tasks

### Creating a Django Superuser

```bash
# Interactive prompt
docker compose exec backend python manage.py createsuperuser

# Non-interactive (for automation)
docker compose exec backend python manage.py createsuperuser \
  --username admin \
  --email admin@example.com \
  --noinput
```

### Database Backup and Restore

```bash
# Backup database
./docker-dev.sh backup-db
# Creates: backups/db_backup_YYYYMMDD_HHMMSS.sql

# Restore database
docker compose exec -T db psql -U postgres -d backend_db < backups/db_backup_20251025_120000.sql
```

### Viewing Service Resource Usage

```bash
# Real-time resource monitoring
docker stats

# Service-specific stats
docker stats app-backend app-frontend app-db app-redis

# View resource limits
docker inspect app-backend | grep -A 20 "Resources"
```

### Clearing Redis Cache

```bash
# Flush all Redis data
./docker-dev.sh redis-cli
> FLUSHALL
> exit

# Or in one command
docker compose exec redis redis-cli FLUSHALL
```

### Rebuilding Frontend Node Modules

```bash
# If node_modules get corrupted
docker compose down
docker volume rm app-frontend-node-modules
./docker-dev.sh rebuild frontend
./docker-dev.sh start
```

### Running One-Off Commands

```bash
# Run Django management command
docker compose exec backend python manage.py <command>

# Run npm command
docker compose exec frontend npm run <script>

# Run arbitrary shell command
docker compose exec backend /bin/bash -c "echo 'Hello from backend'"
```

---

## Troubleshooting

For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Quick Fixes

#### Services Won't Start

```bash
# Check what went wrong
./docker-dev.sh logs

# Try rebuilding
./docker-dev.sh rebuild
./docker-dev.sh start
```

#### Can't Access Application

```bash
# Verify proxy is running
curl http://localhost/health

# Check backend health
curl http://localhost/api/v1/health/

# Check service status
./docker-dev.sh status
```

#### Port Already in Use

```bash
# Find what's using port 80
sudo netstat -tlnp | grep :80

# Use different port
export PROXY_PORT=8080
./docker-dev.sh start

# Access application on new port
open http://localhost:8080/
```

#### Database Connection Issues

```bash
# Check database is ready
docker compose exec db pg_isready -U postgres

# Check backend can connect
docker compose exec backend python manage.py check_database

# View database logs
docker compose logs db
```

#### Out of Disk Space

```bash
# Clean up unused Docker resources
docker system prune -a --volumes

# Remove old images
docker image prune -a

# Remove unused volumes
docker volume prune
```

---

## Next Steps

### Documentation Resources

- **Full Troubleshooting Guide**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Environment Configuration**: [docs/features/12/ENVIRONMENT_CONFIG.md](docs/features/12/ENVIRONMENT_CONFIG.md)
- **Development Environment Details**: [docs/features/12/story-12.7-quick-reference.md](docs/features/12/story-12.7-quick-reference.md)
- **Production Optimizations**: [docs/features/12/production-optimizations.md](docs/features/12/production-optimizations.md)
- **Health Monitoring**: [docs/features/12/health-monitoring.md](docs/features/12/health-monitoring.md)
- **Service Architecture**: [docs/features/12/ARCHITECTURE_DIAGRAM.md](docs/features/12/ARCHITECTURE_DIAGRAM.md)

### Learning More

**Understanding the Architecture**:
- [Unified Orchestration Overview](docs/features/12/UNIFIED_ORCHESTRATION.md)
- [Service Dependencies](docs/features/12/DEPENDENCY_MANAGEMENT.md)
- [Reverse Proxy Configuration](docs/features/12/STORY_12.3_REVERSE_PROXY_CONFIGURATION.md)
- [Data Persistence](docs/features/12/DATA_PERSISTENCE.md)

**Development Topics**:
- [Development Workflow Guide](docs/features/12/story-12.7-testing-guide.md)
- [Runtime Configuration](RUNTIME_CONFIG_IMPLEMENTATION.md)
- [Docker Best Practices](context/devops/docker.md)

**Operations Topics**:
- [Validation Scripts](docs/features/12/STORY_12.11_VALIDATION.md)
- [Service Isolation](docs/features/12/SERVICE_ISOLATION.md)
- [Health Monitoring](docs/features/12/health-monitoring.md)

### Getting Help

**Common Issues**:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first
2. Review service logs: `./docker-dev.sh logs <service>`
3. Validate orchestration: `./scripts/validate-orchestration.sh`
4. Check GitHub issues for similar problems

**Community Support**:
- Create an issue in the GitHub repository
- Include output from `./docker-dev.sh status` and relevant logs
- Specify your environment (local/staging/production)

---

## Summary

You now know how to:

✅ Start the complete application stack with a single command
✅ Access all services through the unified entry point (http://localhost/)
✅ View logs and monitor service health
✅ Make code changes with live reloading
✅ Install dependencies without rebuilding containers
✅ Deploy to staging and production environments
✅ Troubleshoot common issues
✅ Find detailed documentation for advanced topics

**Key Commands to Remember**:
```bash
./docker-dev.sh start     # Start everything
./docker-dev.sh status    # Check health
./docker-dev.sh logs      # View logs
./docker-dev.sh stop      # Stop everything
```

**Need help?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or create an issue on GitHub.

Happy developing! 🚀
