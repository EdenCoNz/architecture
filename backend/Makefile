# FastAPI Backend Makefile
# Convenient commands for development workflow

.PHONY: help install dev test lint format clean db-up db-down db-test migrate

# Default target
help:
	@echo "FastAPI Backend - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install all dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev              Start development server with hot reload"
	@echo "  make dev-debug        Start dev server with debug logging"
	@echo "  make shell            Start IPython shell with app context"
	@echo ""
	@echo "Database:"
	@echo "  make db-up            Start PostgreSQL and Redis (Docker)"
	@echo "  make db-down          Stop database services"
	@echo "  make db-test          Test database connection"
	@echo "  make db-reset         Reset database (WARNING: deletes all data)"
	@echo ""
	@echo "Migrations:"
	@echo "  make migrate          Run database migrations"
	@echo "  make migrate-test     Test migrations (check status)"
	@echo "  make migration MSG=   Create new migration"
	@echo "  make migration-down   Rollback last migration"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run linter (Ruff)"
	@echo "  make format           Format code with Black"
	@echo "  make type-check       Run type checker (mypy)"
	@echo "  make check            Run all code quality checks"
	@echo "  make pre-commit       Install pre-commit hooks"
	@echo "  make pre-commit-run   Run pre-commit on all files"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-cov         Run tests with coverage (HTML, XML, terminal)"
	@echo "  make test-cov-html    Run tests with coverage and open HTML report"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make test-e2e         Run end-to-end tests only"
	@echo "  make test-api         Run API tests only"
	@echo "  make test-database    Run database tests only"
	@echo "  make test-fast        Run fast tests (skip slow tests)"
	@echo "  make test-slow        Run slow tests only"
	@echo "  make test-failed      Re-run only failed tests"
	@echo "  make test-verbose     Run tests with verbose output"
	@echo "  make test-parallel    Run tests in parallel"
	@echo "  make test-debug       Run tests with debug output"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove cache and build files"
	@echo "  make clean-all        Deep clean (including venv)"
	@echo ""

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements/development.txt

install-prod:
	pip install -r requirements/production.txt

install-test:
	pip install -r requirements/test.txt

# Development
dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level info --reload-dir app --reload-dir main.py

dev-debug:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level debug --reload-dir app --reload-dir main.py

shell:
	ipython

# Database
db-up:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 5
	@echo "Database services started!"
	@echo "PostgreSQL: localhost:5432 (user: postgres, password: postgres)"
	@echo "Redis: localhost:6379"
	@echo ""
	@echo "Run 'make db-test' to verify connection"

db-down:
	docker-compose -f docker-compose.dev.yml down

db-stop:
	docker-compose -f docker-compose.dev.yml stop

db-logs:
	docker-compose -f docker-compose.dev.yml logs -f postgres

db-test:
	python scripts/test_db_connection.py

db-reset:
	@echo "WARNING: This will delete all data in the database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f docker-compose.dev.yml down -v; \
		docker-compose -f docker-compose.dev.yml up -d; \
		sleep 5; \
		echo "Database reset complete!"; \
	fi

# Migrations
migrate:
	alembic upgrade head

migrate-test:
	python scripts/test_migrations.py

migration:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: MSG parameter required. Usage: make migration MSG='your message'"; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(MSG)"

migration-down:
	alembic downgrade -1

migration-history:
	alembic history

migration-current:
	alembic current

# Code Quality
lint:
	ruff check .

format:
	black .

format-check:
	black --check .

type-check:
	mypy app/

check: format-check lint type-check
	@echo "All code quality checks passed!"

# Pre-commit hooks
pre-commit:
	pre-commit install
	@echo "Pre-commit hooks installed!"
	@echo "Hooks will run automatically on git commit"

pre-commit-run:
	pre-commit run --all-files

pre-commit-update:
	pre-commit autoupdate

# Testing
test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml

test-cov-html:
	pytest --cov=app --cov-report=html
	@echo "Opening coverage report..."
	@which xdg-open > /dev/null && xdg-open htmlcov/index.html || open htmlcov/index.html || echo "Please open htmlcov/index.html manually"

test-unit:
	pytest -m unit -v

test-integration:
	pytest -m integration -v

test-e2e:
	pytest -m e2e -v

test-api:
	pytest -m api -v

test-database:
	pytest -m database -v

test-fast:
	pytest -m "not slow" -v

test-slow:
	pytest -m slow -v

test-failed:
	pytest --lf -v

test-verbose:
	pytest -vv --tb=long

test-watch:
	pytest-watch

test-parallel:
	pytest -n auto

test-debug:
	pytest -vv --tb=long --log-cli-level=DEBUG -s

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cache and build files cleaned!"

clean-all: clean
	rm -rf venv/
	@echo "Complete cleanup done!"

# Docker
docker-build:
	docker build -t fastapi-backend .

docker-run:
	docker run -p 8000:8000 --env-file .env fastapi-backend

# Documentation
docs-serve:
	@echo "API Documentation available at:"
	@echo "  Swagger UI: http://localhost:8000/docs"
	@echo "  ReDoc: http://localhost:8000/redoc"
	@echo ""
	@echo "Starting development server..."
	@make dev

# Quick start for new developers
setup: install-dev db-up
	@echo ""
	@echo "Setup complete! Next steps:"
	@echo "  1. Copy .env.example to .env and configure"
	@echo "  2. Run 'make migrate' to set up database schema"
	@echo "  3. Run 'make dev' to start the development server"
	@echo "  4. Visit http://localhost:8000/docs for API documentation"
