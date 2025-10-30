# Athlete Performance App - Agent Primer

## Project Overview
Full-stack MVP for sport-specific training programs with injury prevention focus. Target sports: Football & Cricket.

## Stack
- **Frontend**: React 19.1 + TypeScript + Vite + MUI 7.3 + Redux Toolkit
- **Backend**: Django 4.x + DRF + PostgreSQL 15 + Redis + Celery
- **Infra**: Docker Compose (multi-env) + Nginx proxy + GitHub Actions CI/CD

## Architecture
```
/                       # Root configs, docker-compose files, docs
├── backend/           # Django API (2.3MB)
├── frontend/          # React SPA (375MB with node_modules)
├── testing/           # Playwright E2E + Locust perf tests
├── nginx/             # Reverse proxy config
├── docs/              # Documentation
│   └── features/      # 16 completed features with implementation logs
├── archive/           # Obsolete files (safely ignorable)
└── scripts/           # Helper scripts for validation/monitoring
```

## Key Endpoints
- Frontend: `http://localhost` (dev) or configured domain
- Backend API: `/api/`
- Django Admin: `/admin/`
- Static/Media: `/static/`, `/media/`

## Environments
- **dev**: Local development with hot reload
- **staging**: Production-like testing
- **production**: Live environment
- **test**: CI/CD testing

## Docker Services
1. **db**: PostgreSQL database
2. **redis**: Cache & queues
3. **backend**: Django API
4. **frontend**: React app
5. **proxy**: Nginx reverse proxy
6. **celery**: Background tasks (optional)

## Current State
- Branch: `bau/meta-improvements`
- Main branch: `main`
- 16 features completed and documented
- Active development ongoing

## Critical Configuration Issues (Need Fixing)
1. **Django settings path**: Wrong in test env - should be `config.settings.testing` not `backend.settings.test`
2. **Frontend API URLs**: Some configs use direct backend URL instead of proxy
3. **CORS configuration**: Test environment needs alignment

## Project Commands
### Development
```bash
docker-compose up                    # Start all services
docker-compose -f docker-compose.yml -f compose.override.yml up  # Dev mode
docker-compose -f docker-compose.yml -f compose.staging.yml up   # Staging
docker-compose -f docker-compose.yml -f compose.production.yml up # Production
```

### Testing
```bash
cd testing && npm test               # Run E2E tests
cd backend && python manage.py test  # Run backend tests
cd frontend && npm test              # Run frontend tests
```

## Key Files
- `docker-compose.yml` - Base orchestration
- `compose.*.yml` - Environment overlays
- `.env*` files - Environment configs (15 files across project)
- `docs/features/` - Feature documentation
- `docs/CONFIGURATION_DISCREPANCIES.md` - Known issues

## Feature Implementation Pattern
Features are tracked in `/docs/features/` with:
- User stories in markdown
- Implementation logs in JSON
- Architecture diagrams
- Configuration details

## Notes for Agents
- Use `/docs/features/` for feature history
- Check `CONFIGURATION_DISCREPANCIES.md` for known issues
- Frontend uses unified proxy (`http://localhost`) not direct backend
- Test environment has critical config issues that need fixing
- Archive folder contains obsolete files - can be ignored
- Git history preserves all changes - no need for backup files