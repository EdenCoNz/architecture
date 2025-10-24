# Backend API

A production-ready Django REST Framework API with PostgreSQL, Redis caching, JWT authentication, comprehensive testing infrastructure, and enterprise-grade security features.

## Table of Contents

- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Docker Development Setup](#docker-development-setup)
- [Installation](#installation)
- [Quick Start Scripts](#quick-start-scripts)
- [Architecture](#architecture)
- [Development Workflow](#development-workflow)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Contributing](#contributing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Technology Stack

### Core Technologies

- **Framework**: Django 5.1+ with Django REST Framework 3.15+
- **Language**: Python 3.12+
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Task Queue**: Celery with Redis broker
- **Testing**: pytest with pytest-django
- **API Documentation**: drf-spectacular (OpenAPI 3.0)
- **Code Quality**: Black, Flake8, isort, mypy
- **Password Hashing**: Argon2 (industry standard)

## Project Structure

```
backend/
├── apps/                      # Django applications
│   ├── api/                   # API endpoints, views, serializers
│   ├── core/                  # Core models and utilities
│   ├── users/                 # User management
│   └── utils/                 # Helper functions
├── config/                    # Django settings and configuration
│   ├── settings/              # Environment-specific settings
│   │   ├── base.py           # Common settings
│   │   ├── development.py    # Development settings
│   │   ├── production.py     # Production settings
│   │   └── testing.py        # Test settings
│   ├── asgi.py               # ASGI configuration
│   ├── wsgi.py               # WSGI configuration
│   └── urls.py               # Main URL configuration
├── docs/                      # Documentation
├── logs/                      # Application logs
├── media/                     # User-uploaded files
├── requirements/              # Python dependencies
│   ├── base.txt              # Core dependencies
│   ├── dev.txt               # Development dependencies
│   └── prod.txt              # Production dependencies
├── static/                    # Static files
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── manage.py                  # Django management script
├── pytest.ini                 # Pytest configuration
├── pyproject.toml            # Python project metadata
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.12+**: [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 15+**: [Download PostgreSQL](https://www.postgresql.org/download/)
- **Redis 7+**: [Download Redis](https://redis.io/download/)
- **python3-venv**: Required for virtual environments

### Installing python3-venv (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.12-venv
```

### Installing python3-venv (macOS)

python3-venv is included with Python on macOS. No additional installation needed.

## Docker Development Setup

The easiest way to get started is using Docker containers. This eliminates the need to install PostgreSQL, Redis, and other dependencies on your machine.

### Prerequisites for Docker

- **Docker Engine 23.0+**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose V2**: Usually included with Docker Desktop

### Quick Start with Docker

```bash
# Navigate to backend directory
cd backend/

# Start all services (PostgreSQL, Redis, Backend)
./docker-dev.sh start

# View logs
./docker-dev.sh logs

# The API will be available at http://localhost:8000
```

### Common Docker Commands

```bash
# Start services
./docker-dev.sh start

# Stop services
./docker-dev.sh stop

# Run database migrations
./docker-dev.sh migrate

# Run tests
./docker-dev.sh test

# Open shell in container
./docker-dev.sh shell

# View service status
./docker-dev.sh status

# Show all commands
./docker-dev.sh help
```

### Docker Benefits

- **No local dependencies**: PostgreSQL and Redis run in containers
- **Consistent environment**: Same setup across all developers
- **Isolated**: Won't conflict with other projects
- **Hot reload**: Code changes are automatically detected
- **Data persistence**: Database data survives container restarts

For detailed Docker documentation, see [DOCKER.md](DOCKER.md).

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd architecture/backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# For development
pip install -r requirements/dev.txt

# For production
pip install -r requirements/prod.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# At minimum, update:
# - SECRET_KEY (generate using: python -c "import secrets; print(secrets.token_urlsafe(50))")
# - Database credentials
# - Redis URL
```

### 5. Set Up Database

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE backend_db;
CREATE USER backend_user WITH PASSWORD 'your_password';
ALTER ROLE backend_user SET client_encoding TO 'utf8';
ALTER ROLE backend_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE backend_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE backend_db TO backend_user;
\q

# Verify database connectivity
make check-db
# Or: python manage.py check_database

# Run migrations
python manage.py migrate
```

See [Database Documentation](docs/DATABASE.md) for comprehensive database setup, configuration, and troubleshooting.

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## Quick Start Scripts

The backend provides convenient shell scripts for common development tasks. All scripts are located in the `scripts/` directory and handle environment setup automatically.

### Development Server

Start the development server with hot reload:

```bash
# Using the script (recommended - includes checks and setup)
./scripts/dev.sh

# Or using Make
make run

# Or directly
python manage.py runserver
```

**Features**:
- Automatically activates virtual environment if found
- Checks database connectivity
- Prompts to run pending migrations
- Displays useful URLs (API docs, admin, health checks)
- Hot reload enabled - code changes automatically restart server

**Environment Variables**:
- `DEV_HOST`: Server host (default: 127.0.0.1)
- `DEV_PORT`: Server port (default: 8000)
- `DJANGO_SETTINGS_MODULE`: Settings module (default: config.settings.development)

### Production Server

Start the production server with Gunicorn:

```bash
# Using the script (includes production readiness checks)
./scripts/prod.sh
```

**Features**:
- Validates SECRET_KEY is production-ready (50+ characters, no "django-insecure")
- Verifies DEBUG is False
- Checks ALLOWED_HOSTS is configured
- Runs database connectivity test
- Ensures all migrations are applied
- Executes Django deployment checks
- Collects static files
- Starts Gunicorn with optimized settings

**Environment Variables**:
- `PROD_HOST`: Server host (default: 0.0.0.0)
- `PROD_PORT`: Server port (default: 8000)
- `GUNICORN_WORKERS`: Number of workers (default: 4)
- `GUNICORN_TIMEOUT`: Request timeout (default: 30s)
- `GUNICORN_MAX_REQUESTS`: Max requests before worker restart (default: 1000)

**Gunicorn Configuration**:
- Worker class: sync
- Max requests jitter: 100 (prevents thundering herd)
- Worker temp directory: /dev/shm (for better performance)
- Logging: access and error logs to stdout

### Running Tests

Execute tests with various options:

```bash
# Run all tests
./scripts/test.sh

# Run with coverage report
./scripts/test.sh --coverage

# Run tests in parallel (faster)
./scripts/test.sh --parallel

# Run specific test type
./scripts/test.sh --type unit
./scripts/test.sh --type integration

# Run with specific marker
./scripts/test.sh --marker slow

# Run specific test file
./scripts/test.sh tests/unit/test_models.py

# Combined options
./scripts/test.sh --coverage --parallel --verbose
```

**Options**:
- `-c, --coverage`: Generate coverage report (HTML + XML + terminal)
- `-p, --parallel`: Run tests in parallel using all CPU cores
- `-v, --verbose`: Verbose output
- `-f, --fail-fast`: Stop on first failure
- `-k, --keep-db`: Reuse test database (faster for repeated runs)
- `-m, --marker`: Run tests with specific pytest marker
- `-t, --type`: Run specific test type (unit, integration, e2e, acceptance, all)
- `-h, --help`: Show help message

### Database Seeding

Populate database with test data for development:

```bash
# Seed with default data (10 users)
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

**Created Users**:
- Test users: `testuser1@example.com`, `testuser2@example.com`, etc.
  - Password: `password123`
- Admin user (with --admin flag): `admin@example.com`
  - Password: `admin123`

**Safety Features**:
- Only works when DEBUG=True (prevents accidental production use)
- Requires confirmation for data clearing
- Checks database connectivity before seeding
- Prompts to run migrations if pending

**Note**: This script should NEVER be used in production!

## Architecture

### Design Philosophy

The backend API is built following these core principles:

1. **Separation of Concerns**: Clear boundaries between layers (views, serializers, models, business logic)
2. **Security First**: Security considerations integrated at every level
3. **Testability**: All components designed with testing in mind
4. **Scalability**: Architecture supports horizontal scaling
5. **Maintainability**: Clean code, comprehensive documentation, consistent patterns

### Architecture Decisions

#### Why Django REST Framework?

**Decision**: Use Django REST Framework over alternatives (FastAPI, Flask-RESTful, Express.js)

**Rationale**:
- **Production-Proven**: Battle-tested at scale (Instagram, Pinterest, Mozilla, NASA)
- **Batteries Included**: Authentication, permissions, serialization, validation built-in
- **ORM Excellence**: Django ORM provides powerful, database-agnostic queries
- **Security Features**: CSRF protection, XSS prevention, SQL injection protection out of the box
- **Admin Interface**: Built-in admin panel for data management
- **Ecosystem Maturity**: Extensive third-party packages and community support
- **Testing Infrastructure**: Comprehensive testing tools included
- **Documentation**: Automatic API documentation with minimal configuration

**Trade-offs**:
- Slightly higher overhead than FastAPI (async-first frameworks)
- More opinionated than Flask (faster development, less flexibility)
- Larger framework size (but includes more features)

#### Why PostgreSQL?

**Decision**: Use PostgreSQL as the primary database over MySQL, MongoDB, or others

**Rationale**:
- **Advanced Features**: JSONB, full-text search, arrays, range types, PostGIS
- **ACID Compliance**: Strong data integrity guarantees
- **Performance**: Excellent query optimization and indexing
- **Django Integration**: First-class ORM support with all features
- **Scalability**: Proven at massive scale with proper configuration
- **Open Source**: No licensing costs, active community
- **JSON Support**: JSONB provides document store capabilities when needed

**Trade-offs**:
- More complex setup than SQLite
- Requires separate service (not embedded)
- Higher resource usage than simpler databases

#### Why JWT Authentication?

**Decision**: Use JWT tokens over session-based authentication

**Rationale**:
- **Stateless Design**: No server-side session storage required
- **Horizontal Scaling**: Tokens work across multiple servers without shared state
- **Mobile-Friendly**: Ideal for mobile apps and SPAs
- **Microservices**: Easy to share authentication across services
- **Industry Standard**: RFC 7519 specification, widely supported
- **Decentralized**: Verification doesn't require database queries

**Implementation Details**:
- Access tokens: 15-minute expiration (reduces exposure window)
- Refresh tokens: 7-day expiration with rotation
- Token blacklist: Secure logout by blacklisting refresh tokens
- Argon2 password hashing: Industry-standard, resistant to GPU attacks

**Trade-offs**:
- Cannot immediately revoke access tokens (must wait for expiration)
- Slightly larger request size (token in headers)
- Requires token blacklist storage for logout

#### Layered Architecture

**1. Presentation Layer** (`apps/api/`)
- Views and ViewSets
- Request/response handling
- API endpoint definitions
- Input validation

**2. Serialization Layer** (`apps/*/serializers.py`)
- Data transformation
- Validation logic
- Field-level permissions
- Nested object handling

**3. Business Logic Layer** (`apps/*/models.py`, `apps/core/`)
- Domain models
- Business rules
- Data integrity constraints
- Model methods

**4. Data Access Layer** (Django ORM)
- Database queries
- Transactions
- Connection pooling
- Query optimization

**5. Cross-Cutting Concerns** (`apps/core/middleware.py`, `apps/core/exceptions.py`)
- Authentication/Authorization
- Logging and monitoring
- Error handling
- Performance tracking

### Security Architecture

#### Defense in Depth

Multiple layers of security controls:

1. **Network Layer**: HTTPS enforcement, CORS configuration
2. **Application Layer**: Input validation, output encoding, CSRF protection
3. **Authentication Layer**: JWT tokens, password hashing, rate limiting
4. **Authorization Layer**: Permission classes, object-level permissions
5. **Data Layer**: SQL injection prevention, query parameterization

#### Security Features

- **Password Security**: Argon2 hashing (memory-hard, GPU-resistant)
- **Token Management**: Short-lived access tokens, refresh token rotation
- **Input Validation**: DRF serializers, custom validators
- **Rate Limiting**: Configurable per-endpoint throttling
- **CORS/CSRF**: Proper origin validation, CSRF tokens
- **Security Headers**: XSS protection, content type sniffing prevention, frame options
- **Sensitive Data Sanitization**: Automatic redaction in logs

See [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md) for authentication details.

### Data Persistence Architecture

#### Connection Management

- **Connection Pooling**: Reuses database connections (10-minute lifetime)
- **Atomic Requests**: Automatic transaction wrapping per request
- **Health Monitoring**: Database connectivity checks with graceful degradation
- **Error Handling**: Clear error messages for common database issues

#### Migration Strategy

- **Version Control**: All schema changes tracked in migrations
- **Forward-Only**: Migrations designed for safe forward progression
- **Zero-Downtime**: Backward-compatible changes for production deployments
- **Data Integrity**: Transactions ensure consistency during migrations

See [docs/DATABASE.md](docs/DATABASE.md) for complete database documentation.

### Logging and Monitoring Architecture

#### Structured Logging

- **Request Tracking**: Unique request IDs for end-to-end tracing
- **Performance Monitoring**: Response time tracking, slow request alerts
- **Error Aggregation**: Structured error logs with context
- **Sensitive Data Protection**: Automatic redaction of passwords, tokens

#### Log Levels by Environment

- **Development**: DEBUG level, SQL queries, verbose console output
- **Production**: WARNING level, JSON format, log aggregation ready

See [docs/LOGGING.md](docs/LOGGING.md) for logging configuration.

### Testing Architecture

#### Test-Driven Development (TDD)

This project follows strict TDD principles:

1. **Write Tests First**: Tests define the desired behavior before implementation
2. **Red-Green-Refactor**: Fail → Pass → Improve cycle
3. **High Coverage**: Maintain >80% code coverage
4. **Multiple Test Levels**: Unit, integration, E2E, acceptance tests

#### Test Pyramid

```
         /\
        /  \  E2E (few)
       /    \
      /      \ Integration (some)
     /        \
    /          \ Unit (many)
   /____________\
```

- **Unit Tests**: Fast, isolated, mock dependencies (majority of tests)
- **Integration Tests**: Test component interactions, real database
- **E2E Tests**: Complete workflows, simulate real user behavior
- **Acceptance Tests**: Validate user story acceptance criteria

See [tests/README.md](tests/README.md) for comprehensive testing guide.

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e          # End-to-end tests only

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest tests/unit/test_example.py

# Run in parallel (faster)
pytest -n auto
```

### Code Quality

This project uses automated code quality tools to ensure consistent, maintainable code. All tools are pre-configured and ready to use.

**Automated Tools**:
- 🎨 **Black**: Code formatter (100-char line length)
- 📦 **isort**: Import sorter (Black-compatible)
- 🔍 **Flake8**: Linter with Django and bugbear plugins
- 🔐 **mypy**: Static type checker with Django stubs
- 🪝 **pre-commit**: Git hooks for automatic checks

**Quick Commands**:
```bash
# Format code (Black + isort)
make format

# Run linter
make lint

# Type checking
make type-check

# Run all quality checks
make quality

# Verify tools are installed correctly
make verify
```

**Manual Commands**:
```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check linting with Flake8
flake8

# Type checking with mypy
mypy apps/
```

**Comprehensive Documentation**:
- 📚 **[Code Quality Guide](docs/CODE_QUALITY.md)**: Complete guide to all tools, configurations, and best practices
- 🎯 **[Tool Demonstrations](docs/TOOL_DEMONSTRATION.md)**: Examples showing each tool in action with real code
- ⚙️ **[Development Setup](docs/DEVELOPMENT_SETUP.md)**: Step-by-step environment setup and troubleshooting

### Pre-commit Hooks

Pre-commit hooks automatically run quality checks before each commit, preventing bad code from entering the repository.

```bash
# Install pre-commit hooks (one-time setup)
make pre-commit
# Or: pre-commit install

# Run manually on all files
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

**What runs on commit**:
1. ✅ Trailing whitespace removal
2. ✅ File ending fixes
3. ✅ YAML/JSON/TOML validation
4. ✅ Merge conflict detection
5. ✅ Debug statement detection
6. 🎨 Black formatting (auto-fix)
7. 📦 isort sorting (auto-fix)
8. 🔍 Flake8 linting
9. 🔐 mypy type checking

If any check fails, the commit is blocked. Auto-fixable issues (Black, isort) are fixed automatically - just re-stage and commit again.

### Database Management

```bash
# Check database connectivity
make check-db
python manage.py check_database
python manage.py check_database --wait 30  # Wait up to 30s

# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Rollback migration
python manage.py migrate <app_name> <migration_name>

# Show migrations status
python manage.py showmigrations

# Create database backup
pg_dump backend_db > backup.sql

# Restore database
psql backend_db < backup.sql
```

**Database Features**:
- PostgreSQL 15+ with JSONB support
- Connection pooling (10-minute connection reuse)
- Atomic requests (automatic transaction wrapping)
- Health monitoring with performance metrics
- Graceful degradation on connection failure
- Clear error messages for troubleshooting

See [Database Documentation](docs/DATABASE.md) for:
- Complete configuration guide
- Connection management best practices
- Health check utilities
- Error handling and troubleshooting
- Performance optimization tips
- Production deployment checklist

### Django Shell

```bash
# Open Django shell
python manage.py shell

# Open Django shell with IPython
python manage.py shell_plus  # requires django-extensions
```

## API Documentation

Once the server is running, access the API documentation at:

- **Swagger UI**: http://localhost:8000/api/v1/docs/
- **ReDoc**: http://localhost:8000/api/v1/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/v1/schema/

## Environment Variables

Key environment variables (see `.env.example` for complete list):

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (required) |
| `DEBUG` | Enable debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed host names | `localhost` |
| `DB_NAME` | Database name | `backend_db` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | (required) |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `REDIS_URL` | Redis connection URL | `redis://127.0.0.1:6379/1` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

## Testing

### Testing Philosophy

This project follows Test-Driven Development (TDD) principles:

1. **Write tests first** before implementing features
2. **Red-Green-Refactor** cycle:
   - Red: Write failing test that defines expected behavior
   - Green: Write minimal code to pass the test
   - Refactor: Improve code while keeping tests green
3. **High coverage**: Maintain >80% code coverage
4. **Test organization**: Unit, integration, E2E, and acceptance tests

### Running Tests

```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e          # End-to-end tests only
pytest -m acceptance   # Acceptance tests only

# Run with coverage
pytest --cov=apps --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_user_model.py

# Run tests in parallel (faster)
pytest -n auto

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Verbose output
pytest -vv
```

### Test Organization

```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_user_model.py
│   ├── test_serializers.py
│   └── test_validators.py
├── integration/             # Integration tests (component interactions)
│   ├── test_auth_endpoints.py
│   └── test_database_integration.py
├── e2e/                     # End-to-end tests (complete workflows)
│   └── test_user_journey.py
├── acceptance/              # Acceptance tests (user story validation)
│   ├── test_story_4_acceptance.py
│   └── test_story_6_authentication.py
├── factories.py             # Factory Boy factories for test data
├── utils.py                 # Test utilities and helpers
└── conftest.py              # Shared pytest fixtures
```

### Writing Tests

#### Test Structure (Arrange-Act-Assert)

```python
import pytest
from tests.factories import UserFactory
from rest_framework.test import APIClient

@pytest.mark.unit
@pytest.mark.django_db
def test_user_registration():
    # Arrange: Set up test data
    client = APIClient()
    user_data = {
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'password_confirm': 'SecurePass123!'
    }

    # Act: Perform the action
    response = client.post('/api/v1/auth/register/', user_data)

    # Assert: Verify the results
    assert response.status_code == 201
    assert response.data['email'] == user_data['email']
    assert 'password' not in response.data  # Password not exposed
```

#### Using Factories

```python
from tests.factories import UserFactory

# Create a user
user = UserFactory()

# Create with custom attributes
admin = UserFactory(is_staff=True, is_superuser=True)

# Create multiple users
users = UserFactory.create_batch(5)

# Build without saving to database (faster)
user = UserFactory.build()
```

#### Testing API Endpoints

```python
from tests.utils import APITestHelper

@pytest.mark.integration
@pytest.mark.django_db
def test_authenticated_endpoint():
    # Setup
    user = UserFactory()
    client = APIClient()
    helper = APITestHelper(client)

    # Authenticate
    access_token, _ = helper.authenticate(user)

    # Make authenticated request
    response = helper.get('/api/v1/users/me/')

    # Assert
    helper.assert_success(response)
    assert response.data['email'] == user.email
```

### Test Coverage

**Target Coverage**: >80% overall

```bash
# Generate coverage report
pytest --cov=apps --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html

# Fail if coverage below threshold
pytest --cov=apps --cov-fail-under=80
```

### Test Best Practices

1. **Use descriptive test names** that explain what is being tested
   ```python
   def test_user_cannot_access_another_users_profile():
       ...
   ```

2. **One assertion per test** when possible (or related assertions)
   ```python
   def test_user_registration_creates_user():
       response = register_user()
       assert response.status_code == 201
       assert User.objects.filter(email=data['email']).exists()
   ```

3. **Test both success and failure cases**
   ```python
   def test_login_with_valid_credentials_succeeds():
       ...

   def test_login_with_invalid_credentials_fails():
       ...
   ```

4. **Keep tests independent** - each test should be able to run in isolation
   ```python
   # Good - creates its own data
   def test_example():
       user = UserFactory()
       # test logic

   # Bad - depends on external state
   def test_example():
       user = User.objects.get(id=1)  # Assumes user exists
   ```

5. **Mock external dependencies**
   ```python
   from unittest.mock import patch

   @patch('apps.services.external_api.call')
   def test_external_service(mock_call):
       mock_call.return_value = {'status': 'success'}
       # test logic
   ```

### Continuous Integration

All tests run automatically on:
- Pull request creation
- Commits to main branch
- Daily scheduled runs

**CI Pipeline Checks**:
- All tests pass
- Code coverage >80%
- Code quality (Black, Flake8, isort, mypy)
- Security checks
- Documentation builds

See [tests/README.md](tests/README.md) for comprehensive testing documentation.

## Architecture Decisions

### Why Django REST Framework?
- Production-proven at scale (Instagram, Pinterest, NASA)
- Comprehensive security features built-in
- Excellent testing infrastructure
- Rich ecosystem and community support
- Batteries-included philosophy reduces boilerplate

### Why PostgreSQL?
- Advanced features (JSONB, full-text search, arrays)
- Strong ACID compliance for data integrity
- First-class Django ORM integration
- Proven scalability

### Why JWT Authentication?
- Stateless design enables horizontal scaling
- Excellent mobile and SPA support
- Industry standard (RFC 7519)
- No session storage required

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Configure `SECRET_KEY` with strong random value
- [ ] Set `ALLOWED_HOSTS` to production domains
- [ ] Configure production database credentials
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure email backend for notifications
- [ ] Set up Sentry or error tracking
- [ ] Configure static file serving (Whitenoise/CDN)
- [ ] Set up database backups
- [ ] Configure log aggregation
- [ ] Enable rate limiting
- [ ] Review security headers

### Production Server

```bash
# Install production dependencies
pip install -r requirements/prod.txt

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## Troubleshooting

### Virtual Environment Issues

**Error**: `The virtual environment was not created successfully because ensurepip is not available`

**Solution**: Install python3-venv:
```bash
sudo apt install python3.12-venv
```

### Database Connection Issues

**Error**: `FATAL: password authentication failed for user`

**Solution**: Check database credentials in `.env` file and ensure PostgreSQL is running.

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'apps'`

**Solution**: Ensure virtual environment is activated and dependencies are installed.

## Contributing

We welcome contributions! Please follow these guidelines to maintain code quality and consistency.

### Development Setup for Contributors

1. **Fork and Clone**
   ```bash
   git clone <your-fork-url>
   cd architecture/backend
   ```

2. **Set Up Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements/dev.txt
   ```

3. **Configure Pre-commit Hooks**
   ```bash
   pre-commit install
   # Or: make pre-commit
   ```

4. **Set Up Database**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   python manage.py migrate
   ```

5. **Verify Setup**
   ```bash
   make verify
   pytest
   ```

### Coding Standards

#### Python Style Guide

We follow PEP 8 with these specific conventions:

- **Line Length**: 100 characters (configured in Black)
- **Quotes**: Use double quotes for strings (Black default)
- **Imports**: Sorted with isort (Black-compatible profile)
- **Type Hints**: Required for public functions and methods
- **Docstrings**: Required for all public modules, classes, and functions

#### Code Quality Tools

All code must pass these checks before merging:

1. **Black** (automatic formatting)
   ```bash
   black .
   ```

2. **isort** (import sorting)
   ```bash
   isort .
   ```

3. **Flake8** (linting)
   ```bash
   flake8
   ```

4. **mypy** (type checking)
   ```bash
   mypy apps/
   ```

5. **Run all checks**
   ```bash
   make quality
   ```

**Configuration Files**:
- `pyproject.toml`: Black and isort configuration
- `setup.cfg`: Flake8 and mypy configuration
- `.pre-commit-config.yaml`: Pre-commit hook configuration

### Test-Driven Development (TDD)

All code changes MUST follow TDD:

1. **Red**: Write a failing test first
   ```python
   def test_user_can_update_profile():
       """Test that authenticated users can update their profile."""
       # Arrange
       user = UserFactory()
       client = APIClient()
       client.force_authenticate(user=user)

       # Act
       response = client.patch('/api/v1/users/me/', {'first_name': 'Updated'})

       # Assert
       assert response.status_code == 200
       assert response.data['first_name'] == 'Updated'
   ```

2. **Green**: Write minimal code to pass the test
   ```python
   class UserProfileView(APIView):
       permission_classes = [IsAuthenticated]

       def patch(self, request):
           serializer = UserSerializer(request.user, data=request.data, partial=True)
           serializer.is_valid(raise_exception=True)
           serializer.save()
           return Response(serializer.data)
   ```

3. **Refactor**: Improve code while keeping tests green
   ```python
   class UserProfileView(generics.RetrieveUpdateAPIView):
       permission_classes = [IsAuthenticated]
       serializer_class = UserSerializer

       def get_object(self):
           return self.request.user
   ```

### Testing Requirements

- **Coverage**: Maintain >80% code coverage
  ```bash
  pytest --cov=apps --cov-fail-under=80
  ```

- **Test Types**: Include unit, integration, and acceptance tests
- **Naming**: Use descriptive test names that explain the behavior
- **Independence**: Each test should be independent and idempotent
- **Fixtures**: Use factories for test data (see `tests/factories.py`)

See [tests/README.md](tests/README.md) for comprehensive testing guidelines.

### API Design Conventions

#### RESTful Principles

- Use standard HTTP methods: GET, POST, PUT, PATCH, DELETE
- Use plural resource names: `/api/v1/users/`, not `/api/v1/user/`
- Use nested routes sparingly: `/api/v1/users/{id}/posts/`
- Return appropriate status codes (200, 201, 204, 400, 401, 403, 404, 500)

#### Request/Response Format

**Successful Response**:
```json
{
  "id": 123,
  "email": "user@example.com",
  "created_at": "2025-10-23T12:00:00Z"
}
```

**Error Response**:
```json
{
  "error": true,
  "status_code": 400,
  "message": "Validation failed",
  "request_id": "uuid",
  "timestamp": "2025-10-23T12:00:00Z",
  "errors": {
    "email": ["This field is required."]
  }
}
```

#### Versioning

- API version in URL: `/api/v1/`, `/api/v2/`
- Maintain backward compatibility within major versions
- Deprecate endpoints gracefully with warnings

#### Documentation

- Document all endpoints with `@extend_schema` decorator
- Include request/response examples
- Specify authentication requirements
- List possible error responses

Example:
```python
from drf_spectacular.utils import extend_schema, OpenApiResponse

class UserViewSet(viewsets.ModelViewSet):
    @extend_schema(
        summary="List all users",
        description="Returns a paginated list of all users.",
        responses={
            200: UserSerializer(many=True),
            401: OpenApiResponse(description="Authentication required"),
        },
        tags=['Users']
    )
    def list(self, request):
        ...
```

### Git Workflow

#### Branch Naming

- Feature: `feature/description` or `feature/story-number`
- Bug fix: `fix/description` or `fix/issue-number`
- Hotfix: `hotfix/description`
- Documentation: `docs/description`

#### Commit Messages

Follow the Conventional Commits specification:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(auth): add password reset functionality

Implement password reset flow with email verification.
Closes #123

fix(api): correct user serializer validation

The email field was not properly validating unique constraints.

test(users): add tests for user registration

docs(readme): update installation instructions
```

#### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Write Tests First** (TDD)
   ```bash
   # Write failing test
   pytest tests/unit/test_my_feature.py  # Should fail
   ```

3. **Implement Feature**
   ```bash
   # Write code to pass the test
   pytest tests/unit/test_my_feature.py  # Should pass
   ```

4. **Run All Quality Checks**
   ```bash
   make quality      # Code quality
   pytest           # All tests
   pytest --cov     # Coverage check
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat(module): add new feature"
   # Pre-commit hooks will run automatically
   ```

6. **Push and Create PR**
   ```bash
   git push origin feature/my-feature
   # Create pull request on GitHub
   ```

7. **PR Requirements**:
   - All CI checks must pass
   - Code review approval required
   - Coverage must not decrease
   - Documentation updated if needed

### Code Review Guidelines

**For Authors**:
- Keep PRs focused and reasonably sized (<500 lines)
- Write clear PR descriptions explaining the changes
- Link related issues
- Respond promptly to review feedback
- Update tests and documentation

**For Reviewers**:
- Review within 24 hours
- Be constructive and respectful
- Focus on logic, security, and maintainability
- Check test coverage and quality
- Verify documentation is updated

### Documentation Standards

#### When to Update Documentation

Update documentation when:
- Adding new features or endpoints
- Changing API behavior
- Modifying configuration options
- Adding dependencies
- Changing architecture

#### Documentation Files

- `README.md`: Getting started, overview, quick reference
- `docs/CONFIGURATION.md`: Environment variables and settings
- `docs/DATABASE.md`: Database setup and management
- `docs/AUTHENTICATION.md`: Authentication system details
- `docs/API_DOCUMENTATION.md`: API documentation guide
- `docs/LOGGING.md`: Logging and monitoring
- `tests/README.md`: Testing guide

#### Docstring Format

Use Google-style docstrings:

```python
def calculate_total(items: List[Item], tax_rate: float = 0.0) -> Decimal:
    """Calculate total price including tax.

    Args:
        items: List of items to calculate total for
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)

    Returns:
        Total price including tax

    Raises:
        ValueError: If tax_rate is negative

    Example:
        >>> items = [Item(price=10.00), Item(price=20.00)]
        >>> calculate_total(items, tax_rate=0.08)
        Decimal('32.40')
    """
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")

    subtotal = sum(item.price for item in items)
    return subtotal * (1 + tax_rate)
```

### Security Guidelines

#### Never Commit

- Passwords or API keys
- `.env` files (use `.env.example` instead)
- Private keys or certificates
- Database dumps with real data
- Personal information

#### Security Checklist

- [ ] Input validation on all user inputs
- [ ] Output encoding to prevent XSS
- [ ] Parameterized queries (Django ORM does this automatically)
- [ ] Authentication on protected endpoints
- [ ] Authorization checks for resource access
- [ ] Rate limiting on public endpoints
- [ ] HTTPS in production
- [ ] Secure password hashing (Argon2)
- [ ] CSRF protection enabled
- [ ] Security headers configured

### Performance Guidelines

- Use `select_related()` and `prefetch_related()` for N+1 queries
- Add database indexes for frequently queried fields
- Cache expensive computations
- Use pagination for list endpoints
- Optimize serializers (use `fields` or `exclude`)
- Profile slow endpoints with Django Debug Toolbar

### Common Pitfalls to Avoid

1. **Not Following TDD**: Always write tests first
2. **Ignoring Pre-commit Hooks**: Fix issues, don't skip hooks
3. **Large Commits**: Break work into smaller, logical commits
4. **Missing Tests**: Every feature needs tests
5. **Hardcoding Values**: Use environment variables
6. **Exposing Sensitive Data**: Sanitize logs and error messages
7. **N+1 Queries**: Use `select_related()` and `prefetch_related()`
8. **Missing Documentation**: Update docs with code changes

### Getting Help

- **Documentation**: Check `docs/` directory first
- **Tests**: Look at existing tests for patterns
- **Issues**: Search existing issues before creating new ones
- **Questions**: Create a discussion or ask in team chat

### Recognition

Contributors are recognized in:
- Git commit history
- Release notes
- GitHub contributors page

Thank you for contributing to making this project better!

## Support

For questions or issues:
1. Check the documentation
2. Review existing tests for examples
3. Open an issue on the repository

## License

[Your License Here]

## Next Steps

- [ ] Story #3: Configure development environment and code quality tools
- [ ] Story #4: Establish data persistence layer
- [ ] Story #5: Implement health check endpoints
- [ ] Story #6: Configure JWT authentication system
- [ ] Story #7: Implement request logging and error handling
- [ ] Story #8: Create comprehensive API documentation
- [ ] Story #9: Implement security best practices
- [ ] Story #10: Configure environment-based settings
- [ ] Story #11: Set up testing infrastructure
- [ ] Story #12: Configure CI/CD pipeline
