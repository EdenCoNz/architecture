# Backend API - FastAPI Application

Production-ready FastAPI backend with PostgreSQL, SQLAlchemy, Redis, and JWT authentication.

## Technology Stack

- **Framework**: FastAPI 0.115+
- **Language**: Python 3.12+
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 (async)
- **Cache/Sessions**: Redis 7.2
- **Authentication**: JWT (PyJWT + FastAPI Security)
- **Migrations**: Alembic
- **Testing**: pytest + httpx
- **Code Quality**: Black, Ruff, mypy

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (recommended for local development)
- OR PostgreSQL 16 + Redis 7.2 (if not using Docker)

### Installation

#### Option 1: Using Docker (Recommended)

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   # Development environment (includes all tools)
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Default .env works with Docker Compose - no changes needed!
   ```

4. **Start database services**:
   ```bash
   # Start PostgreSQL and Redis in Docker
   make db-up

   # Verify connection
   make db-test
   ```

5. **Run database migrations**:
   ```bash
   make migrate
   # Or: alembic upgrade head
   ```

6. **Start the development server**:
   ```bash
   # Using Make
   make dev

   # Or using uvicorn directly
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API**:
   - API: http://localhost:8000
   - Interactive API docs (Swagger): http://localhost:8000/docs
   - Alternative API docs (ReDoc): http://localhost:8000/redoc
   - Health check: http://localhost:8000/health

## Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed documentation.

```
backend/
├── app/                      # Application code
│   ├── api/                 # API endpoints
│   │   └── v1/             # API version 1
│   ├── core/               # Core functionality
│   │   └── config.py       # Settings and configuration
│   ├── models/             # SQLAlchemy database models
│   ├── schemas/            # Pydantic schemas
│   └── services/           # Business logic layer
├── alembic/                 # Database migrations
│   ├── versions/           # Migration files
│   └── env.py              # Alembic environment
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── requirements/            # Python dependencies
│   ├── base.txt            # Core dependencies
│   ├── development.txt     # Development tools
│   ├── production.txt      # Production dependencies
│   └── test.txt            # Testing dependencies
├── main.py                  # Application entry point
├── .env.example             # Environment variables template
├── pyproject.toml           # Python project configuration
└── alembic.ini              # Alembic configuration
```

## Database

### Connection Configuration

The application uses PostgreSQL with async SQLAlchemy. Connection pooling is configured automatically based on environment.

**Key Features:**
- Async database operations with `asyncpg`
- Automatic connection pooling
- Health checks on startup
- Transaction management with auto-commit/rollback

### Testing Database Connection

```bash
# Test database connection
make db-test
# Or: python scripts/test_db_connection.py
```

### Database Commands

```bash
# Start PostgreSQL + Redis (Docker)
make db-up

# Stop database services
make db-down

# View database logs
make db-logs

# Reset database (WARNING: deletes all data)
make db-reset
```

### Database Migrations

```bash
# Run all pending migrations
make migrate

# Test migration status
make migrate-test

# Create new migration (auto-generate from model changes)
make migration MSG="your migration message"

# Rollback last migration
make migration-down

# View migration history
make migration-history
```

For detailed migration documentation, see [docs/MIGRATIONS.md](docs/MIGRATIONS.md).

### Using Database in Code

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Example endpoint using database dependency injection."""
    from sqlalchemy import select
    from app.models import User

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user
    # Transaction automatically committed or rolled back
```

**See [docs/DATABASE.md](docs/DATABASE.md) for comprehensive database documentation.**

## Development

### Running Tests

Comprehensive test suite using pytest, httpx, and async testing patterns.

#### Quick Test Commands

```bash
# Run all tests
make test
# Or: pytest

# Run tests with coverage report
make test-cov
# Or: pytest --cov

# Run tests and open HTML coverage report
make test-cov-html
```

#### Test Types

```bash
# Run unit tests only (fast, isolated)
make test-unit

# Run integration tests (with database)
make test-integration

# Run end-to-end tests (complete workflows)
make test-e2e

# Run API endpoint tests
make test-api

# Run database tests
make test-database
```

#### Advanced Testing

```bash
# Run fast tests only (skip slow tests)
make test-fast

# Re-run only failed tests
make test-failed

# Run tests in parallel (requires pytest-xdist)
make test-parallel

# Run tests with debug output
make test-debug

# Run specific test file
pytest tests/test_health.py

# Run specific test function
pytest tests/test_health.py::TestHealthCheckEndpoint::test_health_check_returns_200_when_healthy

# Run tests matching pattern
pytest -k "health"
```

#### Test Configuration

Tests are configured to use:
- **SQLite in-memory** by default (fast, isolated)
- **PostgreSQL test database** for integration testing (set `TEST_DATABASE_URL` in `.env.test`)
- **Coverage target**: 80%+ (enforced)
- **Automatic database cleanup** after each test

For detailed testing documentation, see [docs/TESTING.md](docs/TESTING.md).

### Code Quality

```bash
# Format code with Black
black .

# Lint with Ruff
ruff check .

# Type check with mypy
mypy app/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current migration
alembic current

# Show migration history
alembic history
```

## API Documentation

The API is automatically documented using OpenAPI/Swagger:

- **Swagger UI** (interactive): http://localhost:8000/docs
- **ReDoc** (clean docs): http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

**See [docs/API.md](docs/API.md) for comprehensive API documentation** including:
- Authentication flow (JWT tokens)
- Request/Response format and examples
- Error handling patterns
- Rate limiting policies
- Available endpoints with examples
- Testing APIs with cURL, httpx, and Postman
- OpenAPI schema usage and client SDK generation

## Environment Variables

Key environment variables (see `.env.example` for full list):

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment (development/staging/production) | `development` |
| `DEBUG` | Enable debug mode | `false` |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://...` |
| `DATABASE_POOL_SIZE` | Connection pool size | `20` (prod), `5` (dev) |
| `DATABASE_MAX_OVERFLOW` | Extra connections beyond pool | `0` (prod), `10` (dev) |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT secret key (min 32 chars) | *required* |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3000` |

## Configuration

The application uses Pydantic Settings for type-safe configuration management:

- Settings defined in `app/core/config.py`
- Loads from environment variables or `.env` file
- Validation and type checking built-in
- Access via `from app.core import settings`

### Development vs Production

Different configurations are automatically applied based on `ENVIRONMENT` variable:

| Setting | Development | Production |
|---------|-------------|------------|
| Debug Mode | Enabled | Disabled |
| API Docs | Enabled (`/docs`) | Disabled |
| Database Pool Size | 5 | 50 |
| Max Overflow | 10 | 20 |
| CORS Origins | `*` (permissive) | Restricted list |
| Logging Format | Human-readable | JSON (structured) |
| Password Hashing | Faster (fewer rounds) | Slower (more rounds) |

## Testing Strategy

The testing infrastructure follows modern 2025 best practices with pytest, httpx, and FastAPI testing patterns.

### Test Pyramid

```
           /\
          /E2E\        End-to-End (few, slow, high value)
         /------\
        /  INT   \      Integration (medium, moderate speed)
       /----------\
      /    UNIT    \    Unit (many, fast, low-level)
     /--------------\
```

### Test Types

- **Unit Tests** (`tests/unit/`): Test individual functions, classes, and models in isolation
  - Fast execution (< 1 second per test)
  - No external dependencies (database, APIs)
  - Mock external services
  - Example: Model methods, utility functions, validation logic

- **Integration Tests** (`tests/integration/`): Test multiple components working together
  - Moderate speed (1-5 seconds per test)
  - Use test database (SQLite in-memory or PostgreSQL)
  - Test API endpoints, database operations, authentication
  - Example: API endpoint + database + serialization

- **End-to-End Tests** (`tests/e2e/`): Test complete user workflows
  - Slower execution (5-30 seconds per test)
  - Full application stack
  - Test realistic scenarios
  - Example: User registration → login → create resource → logout

### Coverage Goals

- **Minimum**: 80% (enforced by CI/CD with `--cov-fail-under=80`)
- **Target**: 90% for critical business logic
- **Focus Areas**: Authentication, authorization, data validation, business logic
- **Excluded**: Auto-generated code, migrations, third-party integrations

### Test Database

**Default: SQLite in-memory**
- Fast, isolated tests
- Perfect for unit and integration tests
- No setup required

**Optional: PostgreSQL test database**
```bash
# Set in .env.test
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app_test
```

### Running Tests

See [Development → Running Tests](#running-tests) section above or [docs/TESTING.md](docs/TESTING.md) for comprehensive testing guide.

### Continuous Integration

All tests run automatically on:
- Every push to main/develop branches
- Every pull request
- Enforces 80%+ coverage
- Tests must pass before merge

## Production Deployment

### Using Docker

```bash
# Build Docker image
docker build -t backend-api .

# Run container
docker run -p 8000:8000 --env-file .env backend-api
```

### Using Docker Compose

```bash
# Start all services (API, PostgreSQL, Redis)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Manual Deployment

1. Install dependencies: `pip install -r requirements/production.txt`
2. Set `ENVIRONMENT=production` in `.env`
3. Set `DEBUG=false`
4. Configure secure `SECRET_KEY` (32+ characters)
5. Run migrations: `alembic upgrade head`
6. Start with Gunicorn: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000`

### Production Checklist

- [ ] `DEBUG=false` in environment
- [ ] Strong `SECRET_KEY` set (32+ characters)
- [ ] Database connection pooling configured
- [ ] Redis connection established
- [ ] HTTPS enabled (use reverse proxy like nginx)
- [ ] CORS origins restricted to production domains
- [ ] Error tracking configured (Sentry)
- [ ] Logging configured with appropriate levels
- [ ] Database backups automated
- [ ] Health check endpoint monitored
- [ ] Rate limiting enabled

## Security

- Passwords hashed with bcrypt
- JWT tokens for authentication
- CORS configured for allowed origins
- SQL injection prevention via SQLAlchemy parameterized queries
- Input validation via Pydantic schemas
- HTTPS enforced in production
- Secrets managed via environment variables

## Performance

- Async SQLAlchemy for non-blocking database operations
- Redis caching for expensive queries
- Connection pooling for database connections
- Uvicorn ASGI server for high concurrency
- Expected performance: 1,000-3,000 requests/second per instance

## Monitoring

- Health check endpoint: `/health`
- Application logs with configurable levels
- Error tracking with Sentry (optional)
- Database connection monitoring
- Redis connection monitoring

## Documentation Index

All comprehensive documentation is organized in the `docs/` directory:

| Document | Purpose |
|----------|---------|
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Complete directory structure and architecture |
| [docs/DATABASE.md](docs/DATABASE.md) | Database configuration, pooling, and best practices |
| [docs/MIGRATIONS.md](docs/MIGRATIONS.md) | Database migration workflow and commands |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Development tools, code quality, and workflow |
| [docs/TESTING.md](docs/TESTING.md) | Testing infrastructure, patterns, and best practices |
| [docs/API.md](docs/API.md) | API documentation, endpoints, and usage examples |

## Troubleshooting

### Common Issues

**Issue**: Database connection failed

**Solution**:
```bash
# Ensure PostgreSQL is running
make db-up

# Test connection
make db-test

# Check .env configuration
cat .env | grep DATABASE_URL
```

**Issue**: Tests failing with "database is locked"

**Solution**: SQLite in-memory uses `StaticPool` configured in `tests/conftest.py`. If issues persist, use PostgreSQL test database in `.env.test`.

**Issue**: Hot reload not working

**Solution**:
```bash
# Restart development server
Ctrl+C
make dev

# Check if uvicorn is watching correct directories
# Should watch: app/, main.py
```

**Issue**: Pre-commit hooks failing

**Solution**:
```bash
# Run formatting and linting
make format
make lint

# Or let pre-commit auto-fix
pre-commit run --all-files

# Then commit again
git add .
git commit -m "message"
```

**Issue**: Import errors in tests

**Solution**:
```bash
# Ensure you're in virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

## Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes following code style (Black, Ruff)
3. Write tests (TDD approach preferred)
4. Run quality checks: `make check`
5. Commit changes (pre-commit hooks run automatically)
6. Push and create pull request

### Code Quality Standards

All code must pass:
- ✓ Black formatting (`make format`)
- ✓ Ruff linting (`make lint`)
- ✓ mypy type checking (`make type-check`)
- ✓ Bandit security scanning (runs in CI)
- ✓ Tests with 80%+ coverage (`make test-cov`)

### Pull Request Checklist

- [ ] Tests written and passing
- [ ] Code formatted with Black
- [ ] No linting errors (Ruff)
- [ ] Type hints added (mypy passing)
- [ ] Documentation updated
- [ ] Migration created (if schema changes)
- [ ] Changelog updated (if applicable)

## License

[Your License Here]

## Support

For issues and questions:

1. Check the [Documentation Index](#documentation-index) above
2. Review [docs/DATABASE.md](docs/DATABASE.md) for database issues
3. Review [docs/TESTING.md](docs/TESTING.md) for testing issues
4. Review [docs/API.md](docs/API.md) for API questions
5. Check application logs in `logs/` directory (production)
6. Contact the development team
