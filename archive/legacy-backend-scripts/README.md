# Legacy Backend Scripts

This directory contains backend development scripts that were used before the Docker-based development workflow was implemented.

## Archived Date
October 31, 2025

## Reason for Archival
These scripts were replaced by the Docker Compose orchestration system (Feature #15) which provides:
- Unified development environment across all services
- Consistent configuration management
- Simplified dependency management
- Container-based isolation
- Unified entry point via `docker-dev.sh`

## Archived Scripts

### dev.sh
**Purpose:** Start Django development server with hot reload
**Replaced by:** `docker-dev.sh start` (runs backend in Docker container)

### prod.sh
**Purpose:** Start production server with Gunicorn
**Replaced by:** Docker Compose production configuration

### test.sh
**Purpose:** Run test suite with various options
**Replaced by:** `docker compose exec backend pytest` or `backend/Makefile` test targets

### seed.sh
**Purpose:** Seed database with test data
**Replaced by:** Django management commands via Docker: `docker compose exec backend python manage.py seed_database`

### setup.sh
**Purpose:** Initial environment setup
**Replaced by:** Docker Compose handles all setup automatically

## Active Scripts

The following script remains active in `backend/scripts/`:
- **verify_tools.sh** - Used by Makefile to verify code quality tools (still relevant for local development)

## Current Development Workflow

For current development practices, please refer to:
- `/docker-dev.sh` - Main entry point for Docker-based development
- `/backend/Makefile` - Common development tasks
- `/docs/features/15/` - Docker orchestration documentation
- `/backend/README.md` - Backend documentation (updated for Docker workflow)

## If You Need These Scripts

These scripts are preserved here for:
1. Historical reference
2. Non-Docker development scenarios (if needed)
3. Understanding the pre-Docker development workflow

To use these scripts:
1. Set up a local Python virtual environment
2. Install dependencies from `backend/requirements/dev.txt`
3. Configure local PostgreSQL and Redis instances
4. Copy scripts from this archive to `backend/scripts/`

However, we strongly recommend using the Docker-based workflow instead.
