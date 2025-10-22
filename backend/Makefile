# Makefile for common development tasks

.PHONY: help install verify check-db migrations migrate test coverage run shell clean format lint type-check quality pre-commit

help:
	@echo "Available commands:"
	@echo "  make install       - Install development dependencies"
	@echo "  make verify        - Verify development environment setup"
	@echo "  make check-db      - Check database connectivity"
	@echo "  make migrations    - Create database migrations"
	@echo "  make migrate       - Apply database migrations"
	@echo "  make test          - Run tests"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make run           - Run development server"
	@echo "  make shell         - Open Django shell"
	@echo "  make clean         - Remove Python cache files"
	@echo "  make format        - Format code with Black and isort"
	@echo "  make lint          - Run Flake8 linter"
	@echo "  make type-check    - Run mypy type checker"
	@echo "  make quality       - Run all quality checks"
	@echo "  make pre-commit    - Install pre-commit hooks"

install:
	pip install -r requirements/dev.txt

check-db:
	python manage.py check_database

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

test:
	pytest

coverage:
	pytest --cov=apps --cov-report=html --cov-report=term

run:
	python manage.py runserver

shell:
	python manage.py shell

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

format:
	black .
	isort .

lint:
	flake8

type-check:
	mypy apps/

quality: format lint type-check
	@echo "All quality checks passed!"

pre-commit:
	pre-commit install
	pre-commit run --all-files

verify:
	@echo "Running verification script..."
	@chmod +x scripts/verify_tools.sh
	@./scripts/verify_tools.sh
