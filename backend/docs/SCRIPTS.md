# Backend Development Scripts

This document provides comprehensive documentation for all development scripts available in the `backend/scripts/` directory.

## Table of Contents

- [Overview](#overview)
- [Script Index](#script-index)
- [Development Scripts](#development-scripts)
  - [dev.sh - Development Server](#devsh---development-server)
  - [prod.sh - Production Server](#prodsh---production-server)
  - [test.sh - Test Runner](#testsh---test-runner)
  - [seed.sh - Database Seeding](#seedsh---database-seeding)
  - [setup.sh - Environment Setup](#setupsh---environment-setup)
  - [verify_tools.sh - Code Quality Verification](#verify_toolssh---code-quality-verification)
- [Environment Variables](#environment-variables)
- [Common Workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)

---

## Overview

The backend project includes several shell scripts to streamline common development tasks. These scripts are located in `backend/scripts/` and provide convenient wrappers around Django management commands and common operations.

**Key Features:**
- Automatic virtual environment detection and activation
- Safety checks and validation
- Clear error messages and helpful output
- Support for various configuration options
- Production-ready deployment scripts

---

## Script Index

| Script | Purpose | Environment | Hot Reload |
|--------|---------|-------------|------------|
| `dev.sh` | Start development server | Development | ✓ Yes |
| `prod.sh` | Start production server | Production | ✗ No |
| `test.sh` | Run test suite | Testing | N/A |
| `seed.sh` | Seed database with test data | Development | N/A |
| `setup.sh` | Initial environment setup | Development | N/A |
| `verify_tools.sh` | Verify code quality tools | Development | N/A |

---

## Development Scripts

### dev.sh - Development Server

**Purpose:** Start the Django development server with hot reload enabled for rapid development.

**Usage:**
```bash
# Basic usage (default: localhost:8000)
./scripts/dev.sh

# Custom host and port
DEV_HOST=0.0.0.0 DEV_PORT=8080 ./scripts/dev.sh
```

**Features:**
- ✓ Automatic virtual environment detection and activation
- ✓ Database connectivity check
- ✓ Pending migration detection with interactive prompt
- ✓ Hot reload enabled - server restarts on code changes
- ✓ Useful URLs displayed (admin, API docs, health check)
- ✓ Graceful shutdown on Ctrl+C

**Environment Variables:**
- `DEV_HOST` - Server host (default: `127.0.0.1`)
- `DEV_PORT` - Server port (default: `8000`)
- `DJANGO_SETTINGS_MODULE` - Settings module (default: `config.settings.development`)

**What It Does:**
1. Checks for and activates virtual environment
2. Verifies `.env` file exists (creates from example if needed)
3. Tests database connectivity
4. Checks for pending migrations (offers to run them)
5. Starts Django development server with auto-reload

**Output Example:**
```
==================================================
Backend API - Development Server
==================================================

✓ Virtual environment activated
  Location: /path/to/venv

Configuration:
  Settings: config.settings.development
  Host: 127.0.0.1
  Port: 8000

✓ Database connection successful
✓ No pending migrations

==================================================
Starting Development Server
==================================================

Server URL: http://127.0.0.1:8000/
Admin URL: http://127.0.0.1:8000/admin/
API Docs: http://127.0.0.1:8000/api/docs/
Health Check: http://127.0.0.1:8000/api/health/

Hot reload is ENABLED - code changes will automatically restart the server

Press Ctrl+C to stop the server
==================================================
```

**Acceptance Criteria Met:**
- ✓ When I run the development script, I see the server start with hot reload enabled
- ✓ When I make code changes in development mode, I see the server restart automatically

---

### prod.sh - Production Server

**Purpose:** Start the production server using Gunicorn with production-optimized settings.

**Usage:**
```bash
# Basic usage (default: 0.0.0.0:8000)
./scripts/prod.sh

# Custom configuration
PROD_HOST=0.0.0.0 PROD_PORT=8080 GUNICORN_WORKERS=8 ./scripts/prod.sh
```

**Features:**
- ✓ Production readiness checks (SECRET_KEY, DEBUG, ALLOWED_HOSTS)
- ✓ Database connectivity verification
- ✓ Migration status check
- ✓ Django deployment checks (security settings)
- ✓ Static file collection
- ✓ Gunicorn with optimized worker settings
- ✓ No hot reload (production mode)

**Environment Variables:**
- `PROD_HOST` - Server host (default: `0.0.0.0`)
- `PROD_PORT` - Server port (default: `8000`)
- `GUNICORN_WORKERS` - Number of worker processes (default: `4`)
- `GUNICORN_TIMEOUT` - Request timeout in seconds (default: `30`)
- `GUNICORN_MAX_REQUESTS` - Max requests before worker restart (default: `1000`)
- `GUNICORN_MAX_REQUESTS_JITTER` - Jitter for max_requests (default: `100`)
- `DJANGO_SETTINGS_MODULE` - Settings module (default: `config.settings.production`)

**Production Readiness Checks:**
1. SECRET_KEY is secure (not "django-insecure", at least 50 characters)
2. DEBUG is False
3. ALLOWED_HOSTS is properly configured
4. Database connection is successful
5. All migrations are applied
6. Django deployment checks pass
7. Static files are collected

**What It Does:**
1. Checks for and activates virtual environment
2. Verifies `.env` file exists
3. Checks Gunicorn is installed
4. Runs comprehensive production readiness checks
5. Collects static files
6. Starts Gunicorn with production settings

**Output Example:**
```
==================================================
Backend API - Production Server
==================================================

✓ Virtual environment activated

Configuration:
  Settings: config.settings.production
  Host: 0.0.0.0
  Port: 8000
  Workers: 4
  Timeout: 30s
  Max Requests: 1000 (+/-100)

==================================================
Running Production Readiness Checks
==================================================

1. Checking SECRET_KEY security...
✓ SECRET_KEY is secure
2. Checking DEBUG setting...
✓ DEBUG is False
3. Checking ALLOWED_HOSTS...
✓ ALLOWED_HOSTS is configured
4. Checking database connection...
✓ Database connection successful
5. Checking migrations...
✓ All migrations applied
6. Running Django deployment checks...
✓ Deployment checks passed
7. Collecting static files...
✓ Static files collected

==================================================
✓ All production checks passed!
==================================================

Starting Production Server with Gunicorn
==================================================

Server URL: http://0.0.0.0:8000/

Note: Hot reload is DISABLED in production mode
      Restart the server to apply code changes

Press Ctrl+C to stop the server
==================================================
```

**Acceptance Criteria Met:**
- ✓ When I run the production script, I see the server start in optimized production mode

---

### test.sh - Test Runner

**Purpose:** Run tests with various options including coverage, parallel execution, and filtering.

**Usage:**
```bash
# Run all tests
./scripts/test.sh

# Run with coverage
./scripts/test.sh --coverage

# Run tests in parallel
./scripts/test.sh --parallel

# Run specific test type
./scripts/test.sh --type unit

# Run specific test file
./scripts/test.sh tests/unit/test_models.py

# Combined options
./scripts/test.sh -c -p -v  # Coverage + parallel + verbose

# Run tests with specific marker
./scripts/test.sh --marker slow

# Stop on first failure
./scripts/test.sh --fail-fast
```

**Options:**
- `-c, --coverage` - Run tests with coverage report
- `-p, --parallel` - Run tests in parallel (uses all CPU cores)
- `-v, --verbose` - Verbose output
- `-f, --fail-fast` - Stop on first failure
- `-k, --keep-db` - Keep test database between runs (faster)
- `-m, --marker MARKER` - Run tests with specific pytest marker
- `-t, --type TYPE` - Run specific test type (unit, integration, e2e, acceptance, all)
- `-h, --help` - Show help message

**Test Types:**
- `unit` - Unit tests (fast, isolated)
- `integration` - Integration tests (with database and services)
- `e2e` - End-to-end tests (full system tests)
- `acceptance` - Acceptance tests (user story verification)
- `slow` - Tests marked as slow
- `all` - All tests (default)

**What It Does:**
1. Checks for and activates virtual environment
2. Sets test settings module (`config.settings.testing`)
3. Verifies pytest is installed
4. Checks test database connectivity
5. Runs tests with specified options
6. Generates coverage reports (if enabled)

**Output Example:**
```
==================================================
Backend API - Test Runner
==================================================

Test Configuration:
  Settings: config.settings.testing
  Coverage: true
  Parallel: true
  Verbose: false
  Fail Fast: false
  Test Type: all

Running pre-test checks...
✓ pytest is available
✓ Test database connection successful

==================================================
Running Tests
==================================================

=================== test session starts ====================
platform linux -- Python 3.11.0, pytest-8.0.0
plugins: django-4.10.0, cov-5.0.0, xdist-3.5.0
collected 42 items

tests/unit/test_models.py ............          [ 28%]
tests/unit/test_views.py ................       [ 66%]
tests/integration/test_api.py ..............    [100%]

---------- coverage: platform linux, python 3.11 -----------
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
apps/api/views.py           45      2    96%   23-24
apps/core/models.py         38      0   100%
------------------------------------------------------
TOTAL                      325      8    98%

=================== 42 passed in 3.45s =====================

==================================================
✓ All tests passed!
==================================================

Coverage report saved to: htmlcov/index.html
View coverage: open htmlcov/index.html
```

---

### seed.sh - Database Seeding

**Purpose:** Seed the database with test data for development and testing.

**⚠ WARNING:** This script should NEVER be used in production! It only works when `DEBUG=True`.

**Usage:**
```bash
# Seed with default settings (10 users)
./scripts/seed.sh

# Seed with admin user
./scripts/seed.sh --admin

# Seed with custom number of users
./scripts/seed.sh --users 50

# Clear existing data and seed
./scripts/seed.sh --clear --admin

# Show help
./scripts/seed.sh --help
```

**Options:**
- `--clear` - Clear existing data before seeding (DANGEROUS!)
- `--admin` - Create admin user (admin@example.com / admin123)
- `--users NUM` - Number of test users to create (default: 10)
- `-h, --help` - Show help message

**Seeded Data:**
- **Test Users:**
  - Email: `testuser1@example.com`, `testuser2@example.com`, ...
  - Password: `password123`
- **Admin User** (if `--admin` flag used):
  - Email: `admin@example.com`
  - Password: `admin123`

**Safety Features:**
- ✓ Only works when DEBUG=True (production protection)
- ✓ Confirmation prompt for --clear operation
- ✓ Database connectivity check
- ✓ Migration status check with auto-run option

**What It Does:**
1. Checks for and activates virtual environment
2. Verifies DEBUG=True (safety check)
3. Checks database connectivity
4. Checks migration status (offers to run if needed)
5. Clears data if `--clear` flag used (with confirmation)
6. Creates admin user if `--admin` flag used
7. Creates specified number of test users
8. Displays summary of created data

**Output Example:**
```
==================================================
Backend API - Database Seeding
==================================================

Configuration:
  Settings: config.settings.development
  Clear existing data: false
  Create admin user: true
  Number of test users: 10

Running safety checks...
✓ Safety checks passed (DEBUG=True)
Checking database connection...
✓ Database connection successful
Checking migrations...
✓ All migrations applied

==================================================
Seeding Database
==================================================

======================================================================
Database Seeding Tool
======================================================================

Seeding database...

  ✓ Created admin user: admin@example.com
    Password: admin123
Creating 10 test users...
  ✓ Created 10 test users

======================================================================
✓ Database seeded successfully!
======================================================================

Database Summary:
  Total users: 11
  Admin users: 1
  Regular users: 10

Admin Credentials:
  Email: admin@example.com
  Password: admin123

==================================================
✓ Database seeded successfully!
==================================================

Admin Login:
  Email: admin@example.com
  Password: admin123

Test User Login:
  Email: testuser1@example.com (or testuser2, testuser3, ...)
  Password: password123
```

---

### setup.sh - Environment Setup

**Purpose:** Initial setup script for development environment.

**Usage:**
```bash
./scripts/setup.sh
```

**What It Does:**
1. Checks Python 3 is installed
2. Creates virtual environment if not exists
3. Activates virtual environment
4. Upgrades pip
5. Installs dependencies from requirements/dev.txt
6. Creates .env file from .env.example if not exists
7. Reminds about database and Redis setup

**Output Example:**
```
==================================================
Backend API - Development Setup
==================================================

Checking Python version...
Python 3.11.0

Virtual environment already exists.
Activating virtual environment...
Upgrading pip...
Installing dependencies...

✓ IMPORTANT: Edit .env file with your configuration!
   Generate a SECRET_KEY using: python -c "import secrets; print(secrets.token_urlsafe(50))"

Checking database connection...
Make sure PostgreSQL is running and configured in .env
Make sure Redis is running (redis-server)

==================================================
Setup complete!
==================================================

Next steps:
1. Edit .env with your configuration
2. Create database: createdb backend_db
3. Run migrations: python manage.py migrate
4. Create superuser: python manage.py createsuperuser
5. Run server: python manage.py runserver

Or use the Makefile:
  make migrate  - Apply migrations
  make run      - Start development server
  make test     - Run tests
```

---

### verify_tools.sh - Code Quality Verification

**Purpose:** Verify that all code quality tools are properly installed and configured.

**Usage:**
```bash
./scripts/verify_tools.sh
```

**What It Checks:**
1. Virtual environment is activated
2. Tool installation (Black, isort, Flake8, mypy, pytest, pre-commit)
3. Configuration files exist (.flake8, pyproject.toml, pytest.ini, etc.)
4. Tool functionality with test file
5. Pre-commit hooks installation
6. Project files formatting and linting status

**Output Example:**
```
==================================================
Code Quality Tools Verification Script
==================================================

✓ Virtual environment activated
  Location: /path/to/venv

==================================================
1. Checking Tool Installation
==================================================

Checking Black...
✓ Black installed
  Version: black, 24.0.0

Checking isort...
✓ isort installed
  Version: isort 5.13.0

[... more tools ...]

==================================================
2. Checking Configuration Files
==================================================

✓ pyproject.toml exists
✓ .flake8 exists
✓ pytest.ini exists
✓ .pre-commit-config.yaml exists
✓ .editorconfig exists

==================================================
3. Running Tool Verification Tests
==================================================

Testing Black (code formatter)...
✓ Black formatting successful

Testing isort (import sorter)...
✓ isort sorting successful

Testing Flake8 (linter)...
✓ Flake8 check passed

Testing mypy (type checker)...
✓ mypy check passed

==================================================
4. Checking Pre-commit Hooks
==================================================

✓ Pre-commit hooks installed
  Location: .git/hooks/pre-commit

✓ Pre-commit configuration valid

==================================================
Summary
==================================================

✓ All code quality tools are properly configured!

You can now:
  - Run 'make format' to format code
  - Run 'make lint' to check for issues
  - Run 'make type-check' to verify types
  - Run 'make quality' to run all checks
  - Run 'make pre-commit' to install hooks
```

---

## Environment Variables

### Development Server (dev.sh)

| Variable | Default | Description |
|----------|---------|-------------|
| `DEV_HOST` | `127.0.0.1` | Development server host |
| `DEV_PORT` | `8000` | Development server port |
| `DJANGO_SETTINGS_MODULE` | `config.settings.development` | Django settings module |

### Production Server (prod.sh)

| Variable | Default | Description |
|----------|---------|-------------|
| `PROD_HOST` | `0.0.0.0` | Production server host |
| `PROD_PORT` | `8000` | Production server port |
| `GUNICORN_WORKERS` | `4` | Number of Gunicorn workers |
| `GUNICORN_TIMEOUT` | `30` | Request timeout (seconds) |
| `GUNICORN_MAX_REQUESTS` | `1000` | Max requests before worker restart |
| `GUNICORN_MAX_REQUESTS_JITTER` | `100` | Jitter for max_requests |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` | Django settings module |

### Test Runner (test.sh)

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.testing` | Django settings module |

---

## Common Workflows

### Initial Setup

```bash
# 1. Clone repository and navigate to backend
cd backend/

# 2. Run setup script
./scripts/setup.sh

# 3. Edit .env file with your configuration
nano .env

# 4. Create database
createdb backend_db

# 5. Run migrations
python manage.py migrate

# 6. Seed database with test data
./scripts/seed.sh --admin

# 7. Start development server
./scripts/dev.sh
```

### Daily Development

```bash
# Start development server
./scripts/dev.sh

# In another terminal: run tests on file changes
./scripts/test.sh -c -p

# Seed fresh test data
./scripts/seed.sh --clear --admin --users 20

# Run code quality checks
make quality
```

### Running Tests

```bash
# Quick test run (all tests)
./scripts/test.sh

# Tests with coverage
./scripts/test.sh --coverage

# Fast parallel tests
./scripts/test.sh -p

# Unit tests only
./scripts/test.sh --type unit

# Integration tests with coverage
./scripts/test.sh --type integration --coverage

# Specific test file
./scripts/test.sh tests/unit/test_models.py

# Debug mode (verbose + fail fast)
./scripts/test.sh -v -f
```

### Production Deployment

```bash
# 1. Ensure production .env is configured
cat .env

# 2. Run production server
./scripts/prod.sh

# Server will perform all production readiness checks
# and start with Gunicorn if all checks pass
```

---

## Troubleshooting

### Virtual Environment Not Found

**Problem:**
```
Error: No virtual environment found!
```

**Solution:**
```bash
# Create virtual environment
python3 -m venv venv

# If python3-venv is not installed (Ubuntu/Debian)
sudo apt install python3-venv

# Then run setup script
./scripts/setup.sh
```

### Database Connection Failed

**Problem:**
```
✗ Database connection failed!
```

**Solution:**
```bash
# 1. Check PostgreSQL is running
sudo systemctl status postgresql

# 2. Check .env database configuration
cat .env | grep DB_

# 3. Create database if not exists
createdb backend_db

# 4. Test connection manually
psql -h localhost -U postgres -d backend_db
```

### Pending Migrations

**Problem:**
```
⚠ Pending migrations detected
```

**Solution:**
```bash
# Apply migrations
python manage.py migrate

# Or let the dev script do it
./scripts/dev.sh
# (answer 'y' when prompted)
```

### Gunicorn Not Installed

**Problem:**
```
Error: Gunicorn is not installed!
```

**Solution:**
```bash
# Install gunicorn (included in prod requirements)
pip install gunicorn

# Or reinstall all production requirements
pip install -r requirements/prod.txt
```

### Tests Failing

**Problem:**
Tests fail with database errors

**Solution:**
```bash
# 1. Check test database exists
# Django creates test database automatically

# 2. Run with fresh database
./scripts/test.sh  # (without --keep-db)

# 3. Check test settings
echo $DJANGO_SETTINGS_MODULE  # Should be config.settings.testing
```

### Hot Reload Not Working

**Problem:**
Code changes don't restart the development server

**Solution:**
```bash
# 1. Verify dev.sh is used (not prod.sh)
./scripts/dev.sh

# 2. Check file is in watched directory
# Django watches: apps/, config/, manage.py

# 3. Check for syntax errors in changed file
python -m py_compile your_file.py

# 4. Restart server manually if needed
# Ctrl+C and ./scripts/dev.sh
```

### Production Checks Failing

**Problem:**
```
✗ SECRET_KEY is not production-ready!
```

**Solution:**
```bash
# Generate secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Add to .env file
echo "SECRET_KEY=<generated-key>" >> .env
```

**Problem:**
```
✗ ALLOWED_HOSTS not properly configured!
```

**Solution:**
```bash
# Edit .env file
nano .env

# Add your domain(s)
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

---

## Acceptance Criteria Verification

### ✓ Acceptance Criteria Met

1. **Development Script with Hot Reload:**
   - ✓ When I run `./scripts/dev.sh`, the server starts with hot reload enabled
   - ✓ When I make code changes, the server restarts automatically

2. **Production Script:**
   - ✓ When I run `./scripts/prod.sh`, the server starts in optimized production mode
   - ✓ Production readiness checks ensure secure configuration
   - ✓ Gunicorn with production-optimized worker settings

3. **Clear Documentation:**
   - ✓ When I review available scripts, I see clear documentation of what each script does
   - ✓ Each script has --help option with usage examples
   - ✓ This SCRIPTS.md provides comprehensive documentation

4. **Additional Features:**
   - ✓ Test runner script with coverage and parallel options
   - ✓ Database seeding script for test data
   - ✓ Setup script for initial environment configuration
   - ✓ Code quality verification script

---

## Related Documentation

- [README.md](../README.md) - Main backend documentation
- [CONFIGURATION.md](CONFIGURATION.md) - Environment configuration guide
- [TESTING.md](TESTING.md) - Testing guide
- [.env.example](../.env.example) - Environment variables template

---

**Last Updated:** 2025-10-23
**Story:** #13 - Create Development Startup Scripts
**Feature:** #7 - Initialize Backend API
