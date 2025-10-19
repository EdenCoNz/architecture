# Backend API

Production-ready backend API service built with Django 5.1 and Django REST Framework.

## Overview

This backend API provides a scalable, maintainable foundation for web applications with:

- **Modern Python Stack**: Django 5.1, Django REST Framework, Python 3.12+
- **Database Support**: PostgreSQL (production), SQLite (development)
- **Code Quality**: Black, Ruff, MyPy with strict type checking
- **Testing**: Comprehensive test suite with pytest (80%+ coverage required)
- **API Documentation**: Auto-generated with drf-spectacular (Swagger/ReDoc)
- **CI/CD**: GitHub Actions with automated quality checks
- **Developer Experience**: Hot reload, watch mode testing, pre-configured tooling

## Quick Links

- [Quick Start Guide](docs/QUICK_START.md) - Get up and running in 5 minutes
- [Development Guide](docs/DEVELOPMENT.md) - Development tools and workflow
- [Testing Guide](docs/TESTING.md) - Testing approach and best practices
- [Architecture](ARCHITECTURE.md) - Project structure and design patterns
- [Contributing](CONTRIBUTING.md) - Contribution guidelines
- [Coding Conventions](CODING_CONVENTIONS.md) - Code style and standards
- [CI/CD Pipeline](docs/CICD.md) - Continuous integration documentation
- [API Documentation](docs/API_ENDPOINTS.md) - Available API endpoints

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Available Commands](#available-commands)
- [Development](#development)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Documentation](#documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Prerequisites

- **Python**: 3.12 or higher
- **Poetry**: For dependency management (install from [python-poetry.org](https://python-poetry.org/))
- **PostgreSQL**: For production (optional for development)
- **Git**: For version control

## Quick Start

### Installation

1. Install dependencies:

```bash
make install
# or
poetry install
```

2. Copy environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run database migrations:

```bash
make migrate
# or
PYTHONPATH=src poetry run python manage.py migrate
```

4. Create a superuser (optional):

```bash
make superuser
# or
PYTHONPATH=src poetry run python manage.py createsuperuser
```

5. Set up pre-commit hooks (recommended):

```bash
poetry run pre-commit install
```

Pre-commit hooks automatically run code quality checks (Black, Ruff, MyPy) before each commit, preventing common issues from being committed.

### Development

Run the development server:

```bash
make dev
# or
PYTHONPATH=src poetry run python manage.py runserver 0.0.0.0:8000
```

The API will be available at http://localhost:8000

API documentation available at:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

## Available Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make dev          # Run development server
make prod         # Run production server
make test         # Run tests with coverage
make test-watch   # Run tests in watch mode
make lint         # Run linting
make format       # Format code
make type-check   # Run type checking
make migrate      # Run database migrations
make migrations   # Create new migrations
make shell        # Open Django shell
make superuser    # Create superuser
make clean        # Clean build artifacts
```

## Project Structure

The project follows a scalable, feature-based architecture with clear separation of concerns:

```
backend/
├── src/                        # Source code
│   ├── backend/                # Main Django project configuration
│   │   ├── settings/           # Environment-specific settings
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # Common settings
│   │   │   ├── development.py  # Development settings
│   │   │   ├── production.py   # Production settings
│   │   │   └── test.py         # Test settings
│   │   ├── __init__.py
│   │   ├── asgi.py             # ASGI application
│   │   ├── wsgi.py             # WSGI application
│   │   └── urls.py             # Root URL configuration
│   │
│   ├── apps/                   # Feature-based Django applications
│   │   └── <app_name>/         # Individual app (e.g., users, products)
│   │       ├── __init__.py
│   │       ├── apps.py         # App configuration
│   │       ├── models.py       # Database models
│   │       ├── views.py        # View logic
│   │       ├── serializers.py  # DRF serializers
│   │       ├── urls.py         # URL routing
│   │       ├── admin.py        # Admin interface
│   │       ├── managers.py     # Custom model managers
│   │       ├── signals.py      # Django signals
│   │       ├── tasks.py        # Background tasks
│   │       ├── migrations/     # Database migrations
│   │       └── tests/          # App-specific tests
│   │
│   ├── common/                 # Shared utilities and helpers
│   │   ├── middleware/         # Custom middleware
│   │   ├── utils/              # Utility functions
│   │   ├── validators/         # Custom validators
│   │   ├── exceptions/         # Custom exceptions
│   │   ├── mixins/             # Reusable mixins
│   │   ├── serializers/        # Base serializers
│   │   ├── permissions/        # Custom permissions
│   │   └── decorators/         # Custom decorators
│   │
│   └── core/                   # Core business logic
│       ├── models/             # Abstract base models
│       ├── services/           # Business logic services
│       └── repositories/       # Data access layer
│
├── tests/                      # Test suite (mirrors src structure)
│   ├── unit/                   # Unit tests
│   │   ├── apps/               # App unit tests
│   │   ├── common/             # Common utilities tests
│   │   └── core/               # Core services tests
│   ├── integration/            # Integration tests
│   │   ├── api/                # API endpoint tests
│   │   └── database/           # Database integration tests
│   ├── e2e/                    # End-to-end tests
│   ├── fixtures/               # Test fixtures and factories
│   ├── conftest.py             # Pytest configuration
│   └── test_*.py               # Top-level tests
│
├── scripts/                    # Utility scripts
│   ├── dev.py                  # Development server
│   └── prod.py                 # Production server
│
├── static/                     # Static files (CSS, JS, images)
├── templates/                  # Django templates
├── logs/                       # Application logs
├── media/                      # User-uploaded files
├── staticfiles/                # Collected static files (production)
│
├── pyproject.toml              # Poetry dependencies
├── Makefile                    # Development commands
├── manage.py                   # Django management script
├── .env.example                # Environment variables template
└── README.md                   # Project documentation
```

### Architecture Overview

#### Source Code Organization (`src/`)

**backend/** - Django project configuration
- Contains settings, WSGI/ASGI configurations, and root URL routing
- Settings are split by environment (base, development, production, test)

**apps/** - Feature-based applications
- Each app is self-contained and focused on a specific domain
- Apps follow Django's standard structure with models, views, serializers, etc.
- Apps should be loosely coupled and communicate through well-defined interfaces

**common/** - Shared utilities
- Reusable code used across multiple apps
- Middleware, validators, permissions, and other cross-cutting concerns
- Utilities should be generic and not tied to specific business logic

**core/** - Business logic layer
- Abstract models providing common fields/behaviors
- Service layer implementing business logic and orchestration
- Repository pattern for complex database queries and data access

#### Test Organization (`tests/`)

**unit/** - Fast, isolated tests
- Test individual components in isolation
- Mock external dependencies
- Mirror the src/ structure for easy navigation

**integration/** - Component interaction tests
- Test how components work together
- Verify database operations and API endpoints
- Use real database connections (test database)

**e2e/** - End-to-end workflow tests
- Test complete user journeys
- Verify critical business processes
- Run separately from unit/integration tests

**fixtures/** - Test data and factories
- Reusable test data generators
- Model factories for creating test instances
- JSON fixtures for complex scenarios

### Design Principles

1. **Separation of Concerns**: Clear boundaries between routing, business logic, and data access
2. **Feature-Based Organization**: Apps organized by domain/feature for scalability
3. **Testability**: Test structure mirrors source for easy test discovery and maintenance
4. **Reusability**: Common functionality in `common/` package, avoiding duplication
5. **Layered Architecture**:
   - Views/Serializers (Presentation)
   - Services (Business Logic)
   - Repositories (Data Access)
   - Models (Data Structure)

### Adding New Features

When adding a new feature:

1. Create a new app in `src/apps/<feature_name>/`
2. Define models, views, serializers, and URLs
3. Add business logic to `core/services/` if shared across apps
4. Create corresponding tests in `tests/unit/apps/<feature_name>/`
5. Add integration tests in `tests/integration/api/`
6. Register the app in `backend.settings.base.LOCAL_APPS`

## Testing

The project includes a comprehensive testing infrastructure with unit tests, integration tests, and TDD workflow support.

### Quick Testing Commands

```bash
# Run all tests with coverage
make test

# Run tests in watch mode (TDD workflow)
make test-watch

# Run tests with minimal output (fast feedback)
make test-fast

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Run tests in parallel (faster)
make test-parallel

# Run smoke tests (critical functionality)
make test-smoke

# View coverage report in browser
make coverage
```

### Run Specific Tests

```bash
# Run specific test file
PYTHONPATH=src poetry run pytest tests/test_configuration.py

# Run specific test class
PYTHONPATH=src poetry run pytest tests/unit/core/test_health_service.py::TestHealthCheckService

# Run tests matching a pattern
PYTHONPATH=src poetry run pytest -k "health"
```

### Test Categories

Tests are organized by type using pytest markers:
- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Integration tests with database/API
- `@pytest.mark.smoke` - Critical functionality tests
- `@pytest.mark.slow` - Tests that take >1 second

### Coverage Reports

```bash
# Generate HTML coverage report
PYTHONPATH=src poetry run pytest --cov-report=html

# Open coverage report in browser
make coverage
```

Coverage reports are generated in multiple formats:
- HTML: `htmlcov/index.html` (interactive)
- XML: `coverage.xml` (CI/CD integration)
- JSON: `coverage.json` (programmatic access)

The project enforces a minimum coverage threshold of **80%**.

For detailed testing documentation, see [docs/TESTING.md](docs/TESTING.md)

## Code Quality

Format code:

```bash
make format
```

Run linting:

```bash
make lint
```

Run type checking:

```bash
make type-check
```

## Configuration

The project uses environment variables for configuration. See `.env.example` for available options.

### Settings Modules

- `backend.settings.base` - Common settings for all environments
- `backend.settings.development` - Development-specific settings
- `backend.settings.production` - Production-specific settings
- `backend.settings.test` - Test-specific settings

Set `DJANGO_SETTINGS_MODULE` environment variable to use a specific settings module.

## Production Deployment

1. Set environment variables:

```bash
export DJANGO_SETTINGS_MODULE=backend.settings.production
export DJANGO_SECRET_KEY=your-secret-key
export DEBUG=False
export ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
# ... other production settings
```

2. Run production server:

```bash
make prod
# or
poetry run python scripts/prod.py
```

The production server uses Gunicorn with multiple workers.

## Development Tools

- **Black**: Code formatting (auto-formats on `make format`)
- **Ruff**: Fast Python linter (runs on `make lint`)
- **MyPy**: Static type checking (runs on `make type-check`)
- **Pytest**: Testing framework (runs on `make test`)
- **Django Debug Toolbar**: Development debugging
- **Hot Reload**: Automatic server restart on file changes

For detailed information about development tools, workflow, and best practices, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

## API Documentation

API documentation is automatically generated using drf-spectacular:

- Interactive Swagger UI: `/api/docs/`
- ReDoc documentation: `/api/redoc/`
- OpenAPI schema: `/api/schema/`

## CI/CD Pipeline

The backend includes automated Continuous Integration and Continuous Deployment (CI/CD) pipeline using GitHub Actions.

### Pipeline Features

- **Automated Quality Checks**: Linting, formatting, type checking
- **Comprehensive Testing**: Full test suite with coverage reporting (≥80% required)
- **Build Verification**: Production build validation and Django deployment checks
- **Security Scanning**: Dependency vulnerability scanning
- **Intelligent Caching**: Fast workflow execution with Poetry dependency caching
- **Automatic Bug Reporting**: GitHub issues created automatically on CI failures

### Pipeline Jobs

The CI/CD pipeline runs these jobs on every pull request:

1. **Lint Check** - Ruff code quality validation
2. **Format Check** - Black code formatting verification
3. **Type Check** - MyPy static type analysis
4. **Security Audit** - Dependency vulnerability scanning
5. **Test Suite** - Pytest with coverage reporting
6. **Build Verification** - Production build validation

### Required Status Checks

Before merging a PR to `main`, these checks must pass:

✅ Lint Check (Ruff)
✅ Format Check (Black)
✅ Type Check (MyPy)
✅ Test Suite (≥80% coverage)
✅ Build Verification

### Local Pre-Push Validation

Run these commands before pushing to avoid CI failures:

```bash
make lint          # Check code quality
make format        # Auto-format code
make type-check    # Verify type hints
make test          # Run tests with coverage
```

**Automated Pre-Commit Checks:**

Install pre-commit hooks to automatically run these checks before every commit:

```bash
# Install hooks (one-time setup)
poetry run pre-commit install

# Manually run all hooks on all files
poetry run pre-commit run --all-files
```

Pre-commit hooks will prevent commits with code quality violations, ensuring your code always passes CI/CD checks.

For detailed CI/CD documentation, see [docs/CICD.md](docs/CICD.md)

## Contributing

We welcome contributions! Please follow these steps:

1. **Read the guidelines**:
   - [Contributing Guide](CONTRIBUTING.md) - Contribution process and guidelines
   - [Coding Conventions](CODING_CONVENTIONS.md) - Code style and standards

2. **Set up your environment**:
   ```bash
   make install
   make migrate
   make test
   ```

3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Follow TDD workflow**:
   ```bash
   make test-watch  # Run tests in watch mode
   ```

5. **Run quality checks before committing**:
   ```bash
   make format
   make lint
   make type-check
   make test
   ```

6. **Submit a pull request** with a clear description

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## Documentation

### For New Developers

Start here to get familiar with the project:

1. [Quick Start Guide](docs/QUICK_START.md) - 5-minute setup
2. [Architecture Overview](ARCHITECTURE.md) - Project structure and design
3. [Development Guide](docs/DEVELOPMENT.md) - Tools and workflow
4. [Coding Conventions](CODING_CONVENTIONS.md) - Code standards

### For Contributors

Reference these when contributing:

- [Contributing Guide](CONTRIBUTING.md) - Contribution process
- [Testing Guide](docs/TESTING.md) - Writing and running tests
- [CI/CD Documentation](docs/CICD.md) - Pipeline and deployment

### API Documentation

- [API Endpoints](docs/API_ENDPOINTS.md) - Available endpoints
- Interactive Swagger UI: http://localhost:8000/api/docs/
- ReDoc Documentation: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

### Additional Resources

- [Server Setup](docs/SERVER_SETUP.md) - Health checks and middleware
- [Project Architecture](ARCHITECTURE.md) - Detailed architecture
- [.env.example](.env.example) - Environment variables reference

## Project Resources

### External Documentation

- [Django 5.1 Documentation](https://docs.djangoproject.com/en/5.1/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [pytest Documentation](https://docs.pytest.org/)

### Development Tools

- [Black Code Formatter](https://black.readthedocs.io/)
- [Ruff Linter](https://docs.astral.sh/ruff/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)

## Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=src
# Or use make commands which handle this automatically
make dev
```

**Port Already in Use**:
```bash
# Check what's using port 8000
lsof -i :8000
# Use a different port
python manage.py runserver 8080
```

**Tests Failing**:
```bash
# Clean and retry
make clean
make test
```

**Database Issues**:
```bash
# Reset database
rm db.sqlite3
make migrate
```

For more troubleshooting help, see:
- [Development Guide](docs/DEVELOPMENT.md#troubleshooting)
- [Testing Guide](docs/TESTING.md#troubleshooting)
- [Quick Start Guide](docs/QUICK_START.md#troubleshooting)

## Getting Help

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Search or create [GitHub Issues](../../issues)
- **Discussions**: Ask questions in [GitHub Discussions](../../discussions)
- **Code Review**: Request review in your pull request

## License

Copyright (c) 2024 Architecture Team

## Acknowledgments

Built with:
- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Poetry](https://python-poetry.org/)
- [pytest](https://pytest.org/)

And many other excellent open-source projects.
