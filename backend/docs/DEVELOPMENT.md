# Development Environment Guide

This document describes the development environment setup and tools available for backend development.

## Overview

The backend project is configured with comprehensive code quality tools, linting, formatting, type checking, and hot reload capabilities. All tools are configured to work together seamlessly and enforce consistent code quality across the team.

## Development Tools

### 1. Code Linting (Ruff)

**Purpose**: Fast Python linter that checks code for errors, style issues, and potential bugs.

**Configuration**: backend/pyproject.toml - `[tool.ruff]` section

**Features**:
- Checks for pycodestyle errors (E) and warnings (W)
- Pyflakes checks for common Python errors (F)
- Import sorting with isort (I)
- Bugbear checks for likely bugs (B)
- Comprehension improvements (C4)
- Modern Python upgrade suggestions (UP)
- Unused arguments detection (ARG)
- Code simplification suggestions (SIM)

**Usage**:
```bash
# Check code for linting issues
make lint

# Or directly with poetry
poetry run ruff check .

# Auto-fix issues where possible
poetry run ruff check --fix .

# Check specific files
poetry run ruff check src/backend/settings/
```

**Line Length**: 100 characters (matches Black)

**Exclusions**: migrations/, .venv/, venv/, .git/, __pycache__/

### 2. Code Formatting (Black)

**Purpose**: Automatic code formatter that ensures consistent code style.

**Configuration**: backend/pyproject.toml - `[tool.black]` section

**Features**:
- Consistent formatting across entire codebase
- No arguments over style
- Minimal diffs for code reviews
- Deterministic formatting

**Usage**:
```bash
# Format all code
make format

# Or directly with poetry
poetry run black .

# Check formatting without making changes
poetry run black --check .

# Format specific files
poetry run black src/backend/settings/
```

**Line Length**: 100 characters

**Target Version**: Python 3.12

**Exclusions**: migrations/, .venv/, venv/, .git/, .eggs/, .tox/, dist/, build/

### 3. Type Checking (MyPy)

**Purpose**: Static type checker that catches type errors before runtime.

**Configuration**: backend/pyproject.toml - `[tool.mypy]` section

**Features**:
- Strict type checking enabled
- Django plugin for Django-specific types
- DRF plugin for REST Framework types
- Comprehensive type checking rules

**Strict Checks Enabled**:
- `disallow_untyped_defs`: All functions must have type hints
- `disallow_incomplete_defs`: Functions must have complete type hints
- `check_untyped_defs`: Check function bodies without type hints
- `warn_return_any`: Warn when returning Any type
- `warn_unused_configs`: Warn about unused MyPy settings
- `warn_redundant_casts`: Warn about unnecessary casts
- `warn_unused_ignores`: Warn about unused type: ignore comments
- `warn_no_return`: Warn about missing return statements
- `strict_equality`: Strict equality checking
- `no_implicit_optional`: Disallow implicit Optional types

**Usage**:
```bash
# Run type checking
make type-check

# Or directly with poetry
PYTHONPATH=src poetry run mypy src

# Check specific files
PYTHONPATH=src poetry run mypy src/backend/settings/base.py
```

**Exclusions**: Tests have relaxed type checking requirements

### 4. Editor Configuration (.editorconfig)

**Purpose**: Ensures consistent coding styles across different editors and IDEs.

**Configuration**: backend/.editorconfig

**Settings**:

**All Files**:
- Charset: UTF-8
- End of line: LF (Unix-style)
- Insert final newline: true
- Trim trailing whitespace: true

**Python Files** (.py):
- Indent style: space
- Indent size: 4
- Max line length: 100

**TOML Files** (.toml):
- Indent style: space
- Indent size: 2

**YAML Files** (.yml, .yaml):
- Indent style: space
- Indent size: 2

**JSON Files** (.json):
- Indent style: space
- Indent size: 2

**Markdown Files** (.md):
- Trim trailing whitespace: false
- Max line length: off

**Makefiles**:
- Indent style: tab

**Supported Editors**:
- VS Code (native support)
- PyCharm/IntelliJ (native support)
- Sublime Text (with plugin)
- Vim (with plugin)
- Emacs (with plugin)

### 5. Hot Reload (Django Development Server)

**Purpose**: Automatically restarts the server when code changes are detected.

**Configuration**: backend/scripts/dev.py

**Features**:
- Automatic server restart on file changes
- Watches Python files for modifications
- Fast feedback loop during development
- No manual server restarts needed

**Usage**:
```bash
# Start development server with hot reload
make dev

# Or directly with poetry
poetry run dev

# Or with manage.py
PYTHONPATH=src poetry run python manage.py runserver 0.0.0.0:8000
```

**How It Works**:
- Django's runserver command has auto-reload enabled by default
- Monitors all .py files in the project
- Reloads when files are modified
- Uses watchdog for file system monitoring (if installed)
- Falls back to polling if watchdog not available

**Port**: 8000 (default)

**Host**: 0.0.0.0 (accessible from all network interfaces)

**Disable Hot Reload** (not recommended for development):
```bash
python manage.py runserver --noreload
```

## Makefile Commands

The project includes a Makefile with convenient commands for all development tools:

```bash
make help          # Show all available commands
make install       # Install dependencies
make dev          # Run development server with hot reload
make test         # Run tests with coverage
make test-watch   # Run tests in watch mode
make lint         # Run linting (Ruff)
make format       # Format code (Black + Ruff)
make type-check   # Run type checking (MyPy)
make migrate      # Run database migrations
make migrations   # Create new migrations
make shell        # Open Django shell
make superuser    # Create superuser
make clean        # Clean build artifacts
```

## Development Workflow

### 1. Initial Setup

```bash
# Install dependencies
make install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
make migrate

# Create superuser (optional)
make superuser
```

### 2. Daily Development

```bash
# Start development server
make dev

# In another terminal, run tests in watch mode
make test-watch
```

### 3. Before Committing

```bash
# Format code
make format

# Run linting
make lint

# Run type checking
make type-check

# Run tests
make test
```

### 4. Recommended Editor Setup

**VS Code**:
- Install Python extension
- Install EditorConfig extension
- Install Ruff extension
- Configure settings.json:
  ```json
  {
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
  ```

**PyCharm**:
- Enable EditorConfig support (built-in)
- Configure Black as external tool or use plugin
- Install Ruff plugin
- Configure MyPy as external tool
- Enable "Reformat code" on commit

## Continuous Integration

All development tools are integrated into the CI/CD pipeline:

1. **Linting**: Fails if code doesn't pass Ruff checks
2. **Formatting**: Fails if code isn't formatted with Black
3. **Type Checking**: Fails if MyPy finds type errors
4. **Tests**: Fails if tests don't pass or coverage is too low

## Troubleshooting

### Linting Errors

If you see linting errors:

```bash
# Auto-fix what can be fixed
make format

# Check remaining issues
make lint

# Fix remaining issues manually
```

### Type Checking Errors

If MyPy reports errors:

1. Add type hints to functions
2. Use type: ignore comments for false positives (sparingly)
3. Check Django stubs are installed: `poetry show django-stubs`

### Hot Reload Not Working

If hot reload isn't working:

1. Check that you're using `make dev` or `runserver` command
2. Ensure --noreload flag is not set
3. Try installing watchdog: `poetry add watchdog --dev`
4. Check file permissions on project directory

### Performance Issues

If development server is slow:

1. Install watchdog for faster file monitoring: `poetry add watchdog --dev`
2. Exclude unnecessary directories from linting: check pyproject.toml
3. Run tests in parallel: `pytest -n auto`

## Code Quality Standards

### Line Length

- Maximum line length: 100 characters
- Configured in Black, Ruff, and EditorConfig
- Enforced by linting and formatting tools

### Import Sorting

- Imports automatically sorted by Ruff (isort rules)
- Order: standard library, third-party, first-party
- Blank line between import groups

### Type Hints

- All functions must have type hints (enforced by MyPy)
- Use modern type hint syntax (Python 3.12+)
- Prefer built-in types over typing module when possible
- Use `list[str]` instead of `List[str]`, `dict[str, int]` instead of `Dict[str, int]`

### Docstrings

- Use docstrings for all public functions, classes, and modules
- Follow Google or NumPy docstring format
- Include parameter types and return types in docstrings

### Test Coverage

- Minimum test coverage: 80%
- Critical business logic: 100% coverage
- Tests in tests/ directory
- Use pytest fixtures and marks

## Additional Tools

### Testing Framework

- **pytest**: Testing framework
- **pytest-django**: Django integration for pytest
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **factory-boy**: Test data generation

### Debugging

- **django-debug-toolbar**: Development debugging panel
- **ipython**: Enhanced Python shell

### API Documentation

- **drf-spectacular**: OpenAPI schema generation
- Swagger UI at `/api/docs/`
- ReDoc at `/api/redoc/`

## Best Practices

1. **Always format before committing**: `make format`
2. **Run linting locally**: `make lint`
3. **Keep type hints up to date**: `make type-check`
4. **Run tests frequently**: `make test-watch`
5. **Use hot reload during development**: `make dev`
6. **Review linting errors carefully**: Don't blindly ignore them
7. **Write tests first (TDD)**: Red-Green-Refactor cycle
8. **Keep test coverage high**: Aim for 80%+ coverage

## Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Black Documentation](https://black.readthedocs.io/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [EditorConfig Documentation](https://editorconfig.org/)
- [Django Development Server](https://docs.djangoproject.com/en/5.1/ref/django-admin/#runserver)
- [Pytest Documentation](https://docs.pytest.org/)
