# Development Environment Setup Guide

This guide walks you through setting up the complete development environment for the backend API.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1. **Python 3.12+**
   ```bash
   python3 --version  # Should be 3.12 or higher
   ```

2. **python3-venv** (Ubuntu/Debian)
   ```bash
   sudo apt install python3.12-venv
   ```

3. **PostgreSQL 15+** (for database)
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib

   # macOS
   brew install postgresql@15

   # Verify installation
   psql --version
   ```

4. **Redis 7+** (for caching and Celery)
   ```bash
   # Ubuntu/Debian
   sudo apt install redis-server

   # macOS
   brew install redis

   # Verify installation
   redis-cli --version
   ```

5. **Git** (for version control)
   ```bash
   git --version
   ```

## Step-by-Step Setup

### 1. Clone the Repository

```bash
cd /path/to/your/projects
git clone <repository-url>
cd architecture/backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show venv path)
which python
```

**Important**: Always activate the virtual environment before working on the project!

### 3. Install Dependencies

```bash
# Install development dependencies (includes all tools)
make install

# Or manually:
pip install -r requirements/dev.txt
```

This installs:
- **Framework**: Django, Django REST Framework
- **Database**: psycopg2 (PostgreSQL adapter)
- **Cache**: Redis client
- **Auth**: JWT authentication
- **Testing**: pytest, pytest-django, factory-boy
- **Code Quality**: Black, isort, Flake8, mypy
- **Development**: django-debug-toolbar, ipython

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Minimum required settings**:
```env
# Django
DJANGO_SETTINGS_MODULE=config.settings.development
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/architecture_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Allowed Hosts
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Generate a secure SECRET_KEY**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Set Up Database

```bash
# Start PostgreSQL service
sudo systemctl start postgresql  # Ubuntu/Debian
brew services start postgresql@15  # macOS

# Create database
sudo -u postgres psql
CREATE DATABASE architecture_dev;
CREATE USER architecture_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE architecture_dev TO architecture_user;
\q

# Update DATABASE_URL in .env with your credentials

# Run migrations
make migrate
# Or: python manage.py migrate
```

### 6. Set Up Redis

```bash
# Start Redis service
sudo systemctl start redis  # Ubuntu/Debian
brew services start redis  # macOS

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### 7. Install Pre-commit Hooks

```bash
# Install pre-commit hooks (runs quality checks on commit)
make pre-commit

# Or manually:
pre-commit install
```

### 8. Verify Installation

```bash
# Run verification script
./scripts/verify_tools.sh

# Or manually verify:
make quality  # Runs format, lint, type-check
make test     # Runs all tests
```

If all checks pass, your environment is set up correctly! 🎉

### 9. Start Development Server

```bash
# Run development server
make run

# Or manually:
python manage.py runserver

# Server will be available at: http://localhost:8000
# API documentation at: http://localhost:8000/api/docs/
```

## Quick Reference

### Daily Workflow

```bash
# 1. Activate virtual environment (every new terminal session)
source venv/bin/activate

# 2. Start services
sudo systemctl start postgresql redis  # Linux
brew services start postgresql@15 redis  # macOS

# 3. Run development server
make run
```

### Common Commands

```bash
# Code Quality
make format       # Format code with Black and isort
make lint         # Run Flake8 linter
make type-check   # Run mypy type checker
make quality      # Run all quality checks

# Testing
make test         # Run all tests
make coverage     # Run tests with coverage report
pytest -m unit    # Run only unit tests

# Database
make migrations   # Create migrations
make migrate      # Apply migrations
make shell        # Open Django shell

# Cleanup
make clean        # Remove cache files

# Help
make help         # Show all available commands
```

### Virtual Environment Management

```bash
# Activate
source venv/bin/activate

# Deactivate
deactivate

# Recreate (if corrupted)
rm -rf venv
python3 -m venv venv
source venv/bin/activate
make install
```

## Troubleshooting

### Issue: "ensurepip is not available"

**Error**:
```
The virtual environment was not created successfully because ensurepip is not available.
```

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install python3.12-venv

# Then recreate virtual environment
rm -rf venv
python3 -m venv venv
```

### Issue: "No module named pip"

**Error**:
```
/usr/bin/python3: No module named pip
```

**Solution**: This is expected on modern Debian/Ubuntu systems. You must use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Issue: Database Connection Error

**Error**:
```
django.db.utils.OperationalError: could not connect to server
```

**Solution**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start if not running
sudo systemctl start postgresql

# Check connection details in .env
# Ensure DATABASE_URL matches your PostgreSQL setup
```

### Issue: Redis Connection Error

**Error**:
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solution**:
```bash
# Check if Redis is running
sudo systemctl status redis

# Start if not running
sudo systemctl start redis

# Test connection
redis-cli ping  # Should return PONG
```

### Issue: Pre-commit Hooks Fail

**Error**: Pre-commit hooks fail on git commit

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Run checks manually to see detailed errors
pre-commit run --all-files

# Fix issues (often auto-fixed by Black/isort)
make format

# Reinstall hooks if needed
pre-commit clean
pre-commit install
```

### Issue: Import Errors in Tests

**Error**:
```
ImportError: No module named 'django'
```

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
make install

# Verify installation
pip list | grep -i django
```

### Issue: Permission Errors

**Error**: Permission denied when creating database or running commands

**Solution**:
```bash
# For PostgreSQL
sudo -u postgres psql  # Run psql as postgres user

# For file permissions
sudo chown -R $USER:$USER .  # Change ownership to current user
```

## Editor Setup

See [CODE_QUALITY.md](CODE_QUALITY.md#editor-integration) for detailed editor configuration:

- VS Code
- PyCharm / IntelliJ IDEA
- Vim / Neovim

## Next Steps

After setup is complete:

1. **Read Documentation**:
   - [CODE_QUALITY.md](CODE_QUALITY.md) - Code quality tools guide
   - [README.md](../README.md) - Project overview and architecture
   - API documentation at http://localhost:8000/api/docs/

2. **Explore the Codebase**:
   - `apps/` - Django applications
   - `config/` - Project configuration
   - `tests/` - Test suite

3. **Run Tests**:
   ```bash
   make test
   make coverage  # View coverage report in htmlcov/index.html
   ```

4. **Start Developing**:
   - Follow TDD workflow (write tests first)
   - Run `make quality` before committing
   - Pre-commit hooks will enforce code quality

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [pytest Documentation](https://docs.pytest.org/)

## Getting Help

- Check the [troubleshooting section](#troubleshooting) above
- Review [CODE_QUALITY.md](CODE_QUALITY.md) for tool-specific issues
- Check project README for architecture and design decisions
- Ask team members or create an issue in the repository

---

**Happy coding!** 🚀
