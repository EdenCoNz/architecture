# Development Environment Guide

**Feature #12 - Story 12.7: Development Environment Optimizations**

This guide explains how to use the optimized development environment for rapid iteration with live code reloading, debugging, and immediate dependency updates.

---

## Quick Start

```bash
# Start all services in development mode
./docker-dev.sh start

# View real-time logs from all services
./docker-dev.sh logs

# View logs for specific service
./docker-dev.sh logs backend
./docker-dev.sh logs frontend
```

Access the application:
- **Application**: http://localhost/ (unified entry point via nginx)
- **Frontend Dev Server**: http://localhost:5173 (direct access for debugging)
- **Backend API**: http://localhost:8000 (direct access for debugging)
- **Database**: localhost:5432 (for database tools like pgAdmin, DBeaver)
- **Redis**: localhost:6379 (for Redis clients like RedisInsight)

---

## Acceptance Criteria Implementation

### AC1: Frontend Hot Module Replacement (HMR)

**Given I modify frontend code, when I save the file, then the browser should automatically reload with my changes**

✅ **Implementation:**
- Vite dev server with optimized HMR configuration
- File watching with polling for Docker bind mounts
- WebSocket-based hot reload
- Source code bind-mounted to container

**How to use:**
1. Start the development environment: `./docker-dev.sh start`
2. Open http://localhost:5173 in your browser
3. Edit any file in `frontend/src/`
4. Save the file
5. Browser automatically updates within ~100ms

**Technical Details:**
- Vite config (`frontend/vite.config.ts`) enables:
  - `usePolling: true` - File watching for Docker bind mounts
  - `interval: 100` - Check for changes every 100ms
  - `host: 0.0.0.0` - Allow external connections from host
  - `hmr.clientPort: 5173` - WebSocket connection port

**Bind Mounts (compose.override.yml):**
```yaml
volumes:
  - ./frontend/src:/app/src
  - ./frontend/public:/app/public
  - ./frontend/index.html:/app/index.html
  - ./frontend/vite.config.ts:/app/vite.config.ts
  - frontend_node_modules:/app/node_modules
```

**Troubleshooting:**
- If HMR doesn't work, check browser console for WebSocket connection errors
- Ensure you're accessing via http://localhost:5173 (not the proxy port)
- Try `./docker-dev.sh restart frontend` to reset the dev server

---

### AC2: Backend Auto-reload

**Given I modify backend code, when I save the file, then the backend should restart automatically with my changes**

✅ **Implementation:**
- Django runserver with built-in auto-reload
- Enhanced with `watchdog` library for better file change detection
- Source code bind-mounted to container
- PYTHONUNBUFFERED=1 for immediate log output

**How to use:**
1. Start the development environment: `./docker-dev.sh start`
2. Edit any Python file in `backend/`
3. Save the file
4. Django automatically reloads within 1-2 seconds
5. Watch logs: `./docker-dev.sh logs backend`

**Technical Details:**
- Django's `runserver` command includes auto-reload by default
- `watchdog` library (added to dev requirements) provides enhanced file monitoring
- Bind mount ensures file changes are immediately visible to container

**Bind Mounts (compose.override.yml):**
```yaml
volumes:
  - ./backend:/app
  - /app/venv  # Prevent overriding virtual environment
  - ./backend/logs:/app/logs
```

**What triggers reload:**
- Python files (`.py`)
- Django templates (`.html`, `.txt`)
- Static files changes are reflected without reload

**Troubleshooting:**
- Check logs: `./docker-dev.sh logs backend`
- If reload doesn't work, restart manually: `./docker-dev.sh restart backend`
- Syntax errors will prevent reload - fix the error and save again

---

### AC3: Installing Dependencies Without Rebuild

**Given I install new dependencies, when they're added, then they should be available immediately without rebuilding**

✅ **Implementation:**
- Execute package install commands inside running containers
- Changes persist via bind mounts (package.json, requirements.txt)
- Next container restart will include the new dependencies

**Frontend Dependencies:**

```bash
# Install a new npm package
./docker-dev.sh exec frontend npm install <package-name>

# Install from package.json changes
./docker-dev.sh exec frontend npm install

# Example: Install axios
./docker-dev.sh exec frontend npm install axios

# Verify installation
./docker-dev.sh exec frontend npm list axios
```

**Backend Dependencies:**

```bash
# Install a new Python package
./docker-dev.sh exec backend pip install <package-name>

# Install from requirements file changes
./docker-dev.sh exec backend pip install -r requirements/dev.txt

# Example: Install requests
./docker-dev.sh exec backend pip install requests

# Verify installation
./docker-dev.sh exec backend pip list | grep requests
```

**Persistence:**
- Frontend: `node_modules` is stored in named volume `frontend_node_modules`
- Backend: Packages installed to `/app/venv` (excluded from bind mount)
- Both persist across container restarts

**When to rebuild:**
You only need to rebuild containers if:
1. You modify the Dockerfile itself
2. You want to ensure a clean state
3. Dependencies conflict or become corrupted

```bash
# Rebuild specific service
./docker-dev.sh rebuild backend
./docker-dev.sh rebuild frontend

# Rebuild all services
./docker-dev.sh rebuild
```

**Best Practice:**
1. Add package to package.json or requirements.txt
2. Install using exec command above
3. Commit the package.json/requirements.txt changes
4. Other developers can install with: `./docker-dev.sh exec <service> <install-command>`

---

### AC4: Real-time Log Aggregation

**Given I view application logs, when I run the logs command, then I should see real-time output from all services**

✅ **Implementation:**
- Docker Compose native log aggregation
- Color-coded output per service
- Real-time streaming with timestamps
- JSON log driver with rotation

**View All Logs:**

```bash
# Real-time logs from all services
./docker-dev.sh logs

# Same as:
docker compose logs -f
```

**View Service-Specific Logs:**

```bash
# Backend logs only
./docker-dev.sh logs backend

# Frontend logs only
./docker-dev.sh logs frontend

# Database logs
./docker-dev.sh logs db

# Redis logs
./docker-dev.sh logs redis

# Nginx proxy logs
./docker-dev.sh logs proxy
```

**Advanced Log Viewing:**

```bash
# Show last 100 lines and follow
docker compose logs -f --tail=100

# View logs since specific time
docker compose logs --since 2024-10-25T10:00:00

# View logs for multiple services
docker compose logs -f backend frontend

# View logs without following (static output)
docker compose logs backend
```

**Log Output:**
- Each service has color-coded prefix
- Timestamps included
- stdout and stderr both captured
- Logs persisted to `/var/log/nginx/` for proxy service

**Log Rotation (configured in compose files):**
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

**Structured Logging:**
- Backend: Django logging configured to output structured logs
- Frontend: Vite dev server outputs formatted logs
- All services: PYTHONUNBUFFERED=1 ensures immediate output

---

## Development Workflow

### Starting Development

```bash
# 1. Start all services
./docker-dev.sh start

# 2. View logs to confirm all services are healthy
./docker-dev.sh logs

# 3. Open the application in your browser
open http://localhost/

# 4. Begin development - changes will auto-reload!
```

### Making Changes

**Frontend Changes:**
1. Edit files in `frontend/src/`
2. Save (Ctrl+S / Cmd+S)
3. Browser automatically reloads within 100ms
4. No rebuild needed

**Backend Changes:**
1. Edit files in `backend/`
2. Save (Ctrl+S / Cmd+S)
3. Django automatically reloads within 1-2 seconds
4. Watch logs: `./docker-dev.sh logs backend`
5. No rebuild needed

**Configuration Changes:**
- Edit `.env.local.example` and create `.env` if needed
- Restart services: `./docker-dev.sh restart`
- Changes take effect immediately

### Installing New Dependencies

**Frontend:**
```bash
# Install package
./docker-dev.sh exec frontend npm install <package>

# Update package.json manually, then:
./docker-dev.sh exec frontend npm install
```

**Backend:**
```bash
# Install package
./docker-dev.sh exec backend pip install <package>

# Update requirements/dev.txt, then:
./docker-dev.sh exec backend pip install -r requirements/dev.txt
```

### Running Migrations

```bash
# Create new migrations
./docker-dev.sh backend-makemigrations

# Apply migrations
./docker-dev.sh backend-migrate

# Or manually:
./docker-dev.sh exec backend python manage.py makemigrations
./docker-dev.sh exec backend python manage.py migrate
```

### Debugging

**Backend Shell (Django):**
```bash
# Open Django shell
./docker-dev.sh backend-shell

# Or:
./docker-dev.sh exec backend python manage.py shell
```

**Frontend Shell:**
```bash
# Open shell in frontend container
./docker-dev.sh frontend-shell

# Or:
./docker-dev.sh shell frontend
```

**Database Shell:**
```bash
# Open PostgreSQL shell
./docker-dev.sh db-shell

# Or:
./docker-dev.sh exec db psql -U postgres -d backend_db
```

**Redis CLI:**
```bash
# Open Redis CLI
./docker-dev.sh redis-cli

# Or:
./docker-dev.sh exec redis redis-cli
```

### Stopping Development

```bash
# Stop all services (preserves data)
./docker-dev.sh stop

# Stop and remove containers (preserves data)
docker compose down

# Stop and remove containers + volumes (DESTRUCTIVE - removes data)
./docker-dev.sh clean
```

---

## Performance Optimization

### File Watching Performance

The development environment is optimized for file watching in Docker:

**Frontend (Vite):**
- Polling interval: 100ms (configurable in `vite.config.ts`)
- Immediate HMR updates via WebSocket
- Only changed modules are reloaded

**Backend (Django):**
- Django's built-in autoreload with watchdog enhancement
- Typically 1-2 second reload time
- Full process restart on code changes

### Build Cache

The development environment uses Docker BuildKit cache:

```bash
# Build with cache
docker compose build

# Build without cache (fresh build)
docker compose build --no-cache

# Or using helper script
./docker-dev.sh rebuild
```

### Volume Performance

Named volumes are used for better performance:
- `frontend_node_modules` - Faster than bind mount
- `postgres_data` - Database persistence
- `redis_data` - Cache persistence

---

## Troubleshooting

### HMR Not Working (Frontend)

**Symptoms:** Changes to frontend code don't reload the browser

**Solutions:**
1. Check WebSocket connection in browser console
2. Ensure accessing via http://localhost:5173 (not proxy port)
3. Restart frontend service: `./docker-dev.sh restart frontend`
4. Check Vite config: `cat frontend/vite.config.ts`
5. Verify polling is enabled: `usePolling: true`

### Backend Not Auto-reloading

**Symptoms:** Changes to Python code don't restart Django

**Solutions:**
1. Check logs for errors: `./docker-dev.sh logs backend`
2. Verify file is mounted: `./docker-dev.sh exec backend ls -la /app/`
3. Restart backend service: `./docker-dev.sh restart backend`
4. Check for syntax errors in Python code
5. Verify watchdog is installed: `./docker-dev.sh exec backend pip list | grep watchdog`

### Dependencies Not Available

**Symptoms:** Import errors after installing packages

**Solutions:**
1. Verify installation: `./docker-dev.sh exec <service> <package-manager> list`
2. Restart service to load new packages: `./docker-dev.sh restart <service>`
3. Check bind mounts aren't overriding installations
4. Rebuild if needed: `./docker-dev.sh rebuild <service>`

### Slow File Watching

**Symptoms:** Changes take several seconds to trigger reload

**Solutions:**
1. Adjust polling interval in `vite.config.ts` (lower = faster, more CPU)
2. Reduce number of watched files with `.dockerignore`
3. Ensure Docker has adequate resources (Docker Desktop settings)
4. Consider using native Docker on Linux (faster than Docker Desktop on Mac/Windows)

### Logs Not Showing

**Symptoms:** `./docker-dev.sh logs` shows no output

**Solutions:**
1. Verify services are running: `./docker-dev.sh ps`
2. Check specific service: `./docker-dev.sh logs backend`
3. Restart services: `./docker-dev.sh restart`
4. Check log configuration in docker-compose.yml

### Port Conflicts

**Symptoms:** Services fail to start with "port already in use" errors

**Solutions:**
1. Check which process is using the port:
   ```bash
   # Linux/Mac
   lsof -i :5173
   lsof -i :8000

   # Windows
   netstat -ano | findstr :5173
   ```
2. Stop conflicting process or change port in `.env`
3. Use different ports in `.env`:
   ```
   FRONTEND_PORT=5174
   BACKEND_PORT=8001
   ```

---

## Environment Variables

Development environment variables are configured in:
- `.env` (create from `.env.local.example`)
- `compose.override.yml` (development overrides)

**Key Variables:**

```bash
# Service Ports
FRONTEND_PORT=5173
BACKEND_PORT=8000
PROXY_PORT=80
DB_PORT=5432

# Database
DB_NAME=backend_db
DB_USER=postgres
DB_PASSWORD=postgres

# Django
DJANGO_SETTINGS_MODULE=config.settings.development
DEBUG=True
LOG_LEVEL=DEBUG
```

---

## Best Practices

### Do's

✅ Use `./docker-dev.sh` commands for common operations
✅ Keep services running while developing
✅ Install dependencies via `exec` commands
✅ Commit package.json and requirements.txt changes
✅ Use bind mounts for code, named volumes for dependencies
✅ Watch logs to understand what's happening
✅ Use health checks to verify services are ready

### Don'ts

❌ Don't rebuild containers for every change
❌ Don't modify files inside containers (changes will be lost)
❌ Don't commit `.env` files (use `.env.example`)
❌ Don't use `docker` commands directly (use `docker compose` or helper script)
❌ Don't run production containers in development
❌ Don't forget to stop services when done

---

## Advanced Topics

### Using Debuggers

**Backend (ipdb):**
```python
# Add breakpoint in your code
import ipdb; ipdb.set_trace()

# Attach to container
./docker-dev.sh exec backend python manage.py runserver 0.0.0.0:8000
```

**Frontend (Browser DevTools):**
- Source maps enabled by default
- Use Chrome/Firefox DevTools
- Set breakpoints in original TypeScript code

### Custom Django Management Commands

```bash
# Run custom management command
./docker-dev.sh exec backend python manage.py <command>

# Examples:
./docker-dev.sh exec backend python manage.py createsuperuser
./docker-dev.sh exec backend python manage.py shell
./docker-dev.sh exec backend python manage.py test
```

### Testing in Development

```bash
# Backend tests
./docker-dev.sh exec backend pytest

# Frontend tests
./docker-dev.sh exec frontend npm test

# With coverage
./docker-dev.sh exec backend pytest --cov
./docker-dev.sh exec frontend npm run test:coverage
```

### Database Operations

```bash
# Backup database
./docker-dev.sh backup-db

# Restore database
./docker-dev.sh restore <backup-file>

# Access database directly
./docker-dev.sh db-shell

# Run SQL file
./docker-dev.sh exec db psql -U postgres -d backend_db -f /path/to/file.sql
```

---

## Summary

The development environment is optimized for rapid iteration:

1. **Frontend HMR**: Changes reload automatically in ~100ms
2. **Backend Auto-reload**: Django restarts automatically in 1-2s
3. **Dependency Management**: Install packages without rebuilding containers
4. **Log Aggregation**: Real-time logs from all services with color coding
5. **Debugging Tools**: Shell access, debuggers, and database tools
6. **Performance**: Optimized file watching and caching

For more information:
- Docker Compose file: `docker-compose.yml`
- Development overrides: `compose.override.yml`
- Helper script: `./docker-dev.sh` (run `./docker-dev.sh help`)
- Frontend config: `frontend/vite.config.ts`
- Backend requirements: `backend/requirements/dev.txt`
