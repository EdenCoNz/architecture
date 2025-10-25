# Story 12.7: Development Environment - Quick Reference

**One-page reference for rapid development iteration**

---

## Start Development

```bash
./docker-dev.sh start          # Start all services
./docker-dev.sh status         # Check health status
./docker-dev.sh logs           # View all logs in real-time
```

**Access Points:**
- Application: http://localhost/
- Frontend (direct): http://localhost:5173
- Backend (direct): http://localhost:8000
- Database: localhost:5432
- Redis: localhost:6379

---

## Make Code Changes

### Frontend Changes (Auto HMR)

```bash
# Edit any file in frontend/src/
# Save file (Ctrl+S / Cmd+S)
# Browser updates automatically in ~100ms
```

**What's configured:**
- ✅ Hot Module Replacement (HMR)
- ✅ File watching with polling (100ms interval)
- ✅ WebSocket-based updates
- ✅ Preserves application state

### Backend Changes (Auto Reload)

```bash
# Edit any .py file in backend/
# Save file (Ctrl+S / Cmd+S)
# Django restarts automatically in 1-2s
```

**What's configured:**
- ✅ Django runserver auto-reload
- ✅ Enhanced with watchdog library
- ✅ Immediate log output (PYTHONUNBUFFERED=1)
- ✅ Monitors .py, .html, .txt files

---

## Install Dependencies

### Frontend (npm)

```bash
# Install specific package
./docker-dev.sh exec frontend npm install <package-name>

# Install from package.json
./docker-dev.sh exec frontend npm install

# Example
./docker-dev.sh exec frontend npm install axios
```

### Backend (pip)

```bash
# Install specific package
./docker-dev.sh exec backend pip install <package-name>

# Install from requirements
./docker-dev.sh exec backend pip install -r requirements/dev.txt

# Example
./docker-dev.sh exec backend pip install requests
```

**No rebuild needed!** Packages available immediately.

---

## View Logs

```bash
# All services (real-time)
./docker-dev.sh logs

# Specific service
./docker-dev.sh logs backend
./docker-dev.sh logs frontend
./docker-dev.sh logs db
./docker-dev.sh logs redis
./docker-dev.sh logs proxy

# Last N lines
docker compose logs --tail=50 backend

# Since timestamp
docker compose logs --since 5m

# Multiple services
docker compose logs -f backend frontend
```

---

## Common Commands

```bash
# Service management
./docker-dev.sh start          # Start all services
./docker-dev.sh stop           # Stop all services
./docker-dev.sh restart        # Restart all services
./docker-dev.sh ps             # Show running services
./docker-dev.sh status         # Detailed status with URLs

# Rebuild (when Dockerfile changes)
./docker-dev.sh rebuild        # Rebuild all
./docker-dev.sh rebuild backend   # Rebuild specific service

# Shell access
./docker-dev.sh backend-shell  # Django shell
./docker-dev.sh frontend-shell # Frontend container shell
./docker-dev.sh db-shell       # PostgreSQL shell
./docker-dev.sh redis-cli      # Redis CLI

# Database operations
./docker-dev.sh backend-migrate          # Apply migrations
./docker-dev.sh backend-makemigrations   # Create migrations

# Data management
./docker-dev.sh backup         # Backup all data
./docker-dev.sh backup-db      # Backup database only
./docker-dev.sh volumes        # Show volume info
./docker-dev.sh clean          # Remove containers (preserve data)
./docker-dev.sh clean-all      # Remove everything (DESTRUCTIVE)
```

---

## Typical Development Session

```bash
# 1. Start environment
./docker-dev.sh start

# 2. Wait for services to be healthy
./docker-dev.sh status

# 3. Open logs in separate terminal
./docker-dev.sh logs

# 4. Open application in browser
open http://localhost:5173

# 5. Edit code
# - Save files → Auto-reload happens
# - No manual restart needed

# 6. Install new dependencies if needed
./docker-dev.sh exec frontend npm install <package>
./docker-dev.sh exec backend pip install <package>

# 7. Run migrations if needed
./docker-dev.sh backend-migrate

# 8. Stop when done
./docker-dev.sh stop
```

---

## Troubleshooting

### HMR Not Working (Frontend)

```bash
# Check WebSocket connection in browser console
# Should see: "[vite] connected"

# Restart frontend service
./docker-dev.sh restart frontend

# Check logs for errors
./docker-dev.sh logs frontend
```

### Backend Not Reloading

```bash
# Check logs for syntax errors
./docker-dev.sh logs backend

# Verify file is mounted
./docker-dev.sh exec backend ls -la /app/

# Restart backend service
./docker-dev.sh restart backend
```

### Dependency Not Available

```bash
# Verify installation
./docker-dev.sh exec frontend npm list <package>
./docker-dev.sh exec backend pip list | grep <package>

# Restart service
./docker-dev.sh restart <service>

# If still not working, rebuild
./docker-dev.sh rebuild <service>
```

### Slow Performance

```bash
# Check resource usage
docker stats

# Ensure Docker has adequate resources
# Docker Desktop → Settings → Resources
# Recommended: 4GB RAM, 2+ CPUs

# Check logs for errors
./docker-dev.sh logs
```

---

## Performance Expectations

| Operation | Expected Time |
|-----------|--------------|
| Frontend HMR | <100ms |
| Backend auto-reload | 1-2 seconds |
| Install npm package | 10-30 seconds |
| Install pip package | 5-15 seconds |
| Service restart | 5-15 seconds |
| Full rebuild | 2-5 minutes |

---

## File Locations

```
Project Root
├── frontend/
│   ├── src/                # Edit files here → HMR
│   ├── vite.config.ts     # Vite configuration
│   └── package.json       # Frontend dependencies
├── backend/
│   ├── **/*.py            # Edit files here → Auto-reload
│   └── requirements/      # Backend dependencies
│       ├── base.txt
│       ├── dev.txt        # Includes watchdog
│       └── prod.txt
├── docker-compose.yml     # Base configuration
├── compose.override.yml   # Development overrides
├── docker-dev.sh          # Helper script
└── DEVELOPMENT_ENVIRONMENT.md  # Full guide
```

---

## Key Features

### ✅ Acceptance Criteria Met

1. **Frontend HMR**: Changes reload browser automatically in <100ms
2. **Backend Auto-reload**: Django restarts automatically in 1-2s
3. **Dependency Installation**: No rebuild needed, use exec commands
4. **Log Aggregation**: Real-time logs from all services with color coding

### 🚀 Technical Implementation

- **Frontend**: Vite with polling-based file watching (Docker-optimized)
- **Backend**: Django runserver + watchdog library
- **Volumes**: Bind mounts for code, named volumes for dependencies
- **Logs**: Docker Compose native aggregation with JSON driver

---

## Environment Variables

Create `.env` file from `.env.local.example`:

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
```

---

## Need More Help?

- Full guide: `DEVELOPMENT_ENVIRONMENT.md`
- Testing guide: `docs/features/12/story-12.7-testing-guide.md`
- Helper script help: `./docker-dev.sh help`
- Docker Compose docs: `docker compose --help`

---

**Pro Tips:**

- Keep logs running in a separate terminal for visibility
- Use `./docker-dev.sh status` to check service health
- Install dependencies via exec, not by rebuilding containers
- Use named volumes for better performance
- Monitor resource usage with `docker stats`
