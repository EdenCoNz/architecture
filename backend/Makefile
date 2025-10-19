# ============================================================================
# Makefile for Backend Development
# ============================================================================

.PHONY: help install dev prod test lint format clean migrate shell

# Default target
help:
	@echo "Backend Development Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install         - Install dependencies with Poetry"
	@echo "  make dev             - Run development server"
	@echo "  make prod            - Run production server (Gunicorn)"
	@echo "  make shell           - Open Django shell"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run all tests with coverage"
	@echo "  make test-watch      - Run tests in watch mode (TDD workflow)"
	@echo "  make test-fast       - Run tests with minimal output (no coverage)"
	@echo "  make test-unit       - Run only unit tests"
	@echo "  make test-integration - Run only integration tests"
	@echo "  make test-parallel   - Run tests in parallel (faster)"
	@echo "  make test-smoke      - Run smoke tests (critical functionality)"
	@echo "  make coverage        - Open coverage report in browser"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            - Run linting (Ruff)"
	@echo "  make format          - Format code (Black + Ruff)"
	@echo "  make type-check      - Run type checking (MyPy)"
	@echo ""
	@echo "Database:"
	@echo "  make migrate         - Run database migrations"
	@echo "  make migrations      - Create new migrations"
	@echo "  make superuser       - Create Django superuser"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           - Remove build artifacts and cache files"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	poetry install

# Development server
dev:
	@echo "Starting development server..."
	PYTHONPATH=src poetry run python manage.py runserver 0.0.0.0:8000

# Production server
prod:
	@echo "Starting production server..."
	poetry run python scripts/prod.py

# Run tests
test:
	@echo "Running tests with coverage..."
	PYTHONPATH=src poetry run pytest

# Run tests in watch mode (TDD workflow)
test-watch:
	@echo "Running tests in watch mode for TDD..."
	@echo "Tests will re-run automatically when files change"
	PYTHONPATH=src poetry run ptw -- --testmon

# Run tests with minimal output (fast feedback)
test-fast:
	@echo "Running tests with minimal output..."
	PYTHONPATH=src poetry run pytest --quiet --no-cov --tb=line

# Run only unit tests
test-unit:
	@echo "Running unit tests..."
	PYTHONPATH=src poetry run pytest -m unit

# Run only integration tests
test-integration:
	@echo "Running integration tests..."
	PYTHONPATH=src poetry run pytest -m integration

# Run parallel tests (faster)
test-parallel:
	@echo "Running tests in parallel..."
	PYTHONPATH=src poetry run pytest -n auto

# Run smoke tests (critical functionality)
test-smoke:
	@echo "Running smoke tests..."
	PYTHONPATH=src poetry run pytest -m smoke

# Show test coverage report
coverage:
	@echo "Generating coverage report..."
	@echo "Opening coverage report in browser..."
	@python -m webbrowser htmlcov/index.html 2>/dev/null || open htmlcov/index.html 2>/dev/null || xdg-open htmlcov/index.html 2>/dev/null || echo "Coverage report available at htmlcov/index.html"

# Linting
lint:
	@echo "Running linting checks..."
	poetry run ruff check .

# Format code
format:
	@echo "Formatting code..."
	poetry run black .
	poetry run ruff check --fix .

# Type checking
type-check:
	@echo "Running type checks..."
	PYTHONPATH=src poetry run mypy src

# Run migrations
migrate:
	@echo "Running migrations..."
	PYTHONPATH=src poetry run python manage.py migrate

# Create migrations
migrations:
	@echo "Creating migrations..."
	PYTHONPATH=src poetry run python manage.py makemigrations

# Django shell
shell:
	@echo "Opening Django shell..."
	PYTHONPATH=src poetry run python manage.py shell

# Create superuser
superuser:
	@echo "Creating superuser..."
	PYTHONPATH=src poetry run python manage.py createsuperuser

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage
	rm -f coverage.xml
	@echo "Clean complete!"
