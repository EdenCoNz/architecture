# Backend Server - Quick Start Guide

## Prerequisites
- Python 3.12+
- PostgreSQL 14+
- Poetry (Python package manager)

## Initial Setup

1. **Install Dependencies**
   ```bash
   poetry install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Run Database Migrations**
   ```bash
   make migrate
   ```

4. **Start Development Server**
   ```bash
   make dev
   ```

The server will start on `http://localhost:8000`

## Quick Verification

### Health Check
```bash
curl http://localhost:8000/health/
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-19T12:00:00.000000Z",
  "service": "backend-api"
}
```

### API Documentation
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

## Development Commands

```bash
# Run tests
make test

# Run linting
make lint

# Format code
make format

# Type checking
make type-check

# Django shell
make shell

# Create superuser
make superuser

# Create migrations
make migrations

# Run migrations
make migrate
```

## Features Implemented

### ✅ Health Check Endpoint
- URL: `/health/`
- Public access (no authentication)
- Returns server status

### ✅ Request Logging
- Logs all incoming requests
- Includes method, path, IP, status, duration
- Configured in middleware

### ✅ Global Error Handling
- Catches all exceptions
- Returns JSON formatted errors
- Different handlers for different error types

## Project Structure

```
backend/
├── src/
│   ├── backend/          # Django project settings
│   ├── common/           # Common utilities, middleware, views
│   ├── core/             # Core business logic
│   └── apps/             # Feature-specific apps
├── tests/                # Test suite
├── docs/                 # Documentation
├── static/               # Static files
└── templates/            # HTML templates
```

## Common Issues

### Poetry Not Found
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

### Database Connection Error
- Check PostgreSQL is running
- Verify credentials in `.env`
- Ensure database exists: `createdb backend_db`

### Module Not Found
- Ensure dependencies are installed: `poetry install`
- Check PYTHONPATH: `export PYTHONPATH=src`

## Next Steps

1. Read the detailed documentation in `docs/SERVER_SETUP.md`
2. Review the API documentation at `/api/docs/`
3. Run the test suite: `make test`
4. Start building your API endpoints

## Getting Help

- Documentation: `backend/docs/`
- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/

## Development Workflow

1. Create a new branch for your feature
2. Write tests first (TDD approach)
3. Implement the feature
4. Run tests: `make test`
5. Format code: `make format`
6. Run linting: `make lint`
7. Commit and push changes

Happy coding!
