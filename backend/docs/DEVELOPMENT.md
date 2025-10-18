# Development Environment Guide

This guide covers all development tools and workflows configured for the FastAPI backend project.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Code Formatting](#code-formatting)
3. [Linting](#linting)
4. [Type Checking](#type-checking)
5. [Pre-commit Hooks](#pre-commit-hooks)
6. [Hot Reload](#hot-reload)
7. [Editor Configuration](#editor-configuration)
8. [Development Workflow](#development-workflow)

---

## Quick Start

### First Time Setup

```bash
# Install development dependencies
make install-dev

# Set up pre-commit hooks
make pre-commit

# Start database services
make db-up

# Run migrations
make migrate

# Start development server with hot reload
make dev
```

### Daily Development

```bash
# Start development server
make dev

# Run tests
make test

# Run code quality checks
make check
```

---

## Code Formatting

We use **Black** as our code formatter with the following configuration:

### Configuration (`pyproject.toml`)

```toml
[tool.black]
line-length = 88
target-version = ['py312']
```

### Usage

```bash
# Format all Python files
make format

# Check formatting without making changes
make format-check
```

### Black Features

- **Line length**: 88 characters (Black's default)
- **Python version**: 3.12+
- **Automatic**: Runs on git commit via pre-commit hooks
- **Consistent**: Everyone uses the same formatting rules

### Example

Before Black:
```python
def very_long_function_name(arg1, arg2, arg3, arg4, arg5):
    return {"key1": arg1, "key2": arg2, "key3": arg3, "key4": arg4}
```

After Black:
```python
def very_long_function_name(
    arg1, arg2, arg3, arg4, arg5
):
    return {
        "key1": arg1,
        "key2": arg2,
        "key3": arg3,
        "key4": arg4,
    }
```

---

## Linting

We use **Ruff** as our linter - a fast Python linter written in Rust.

### Configuration (`pyproject.toml`)

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "C",  # flake8-comprehensions
    "B",  # flake8-bugbear
    "UP", # pyupgrade
]
```

### Usage

```bash
# Run linter
make lint

# Run linter with auto-fix
ruff check . --fix
```

### What Ruff Checks

- **Code errors**: Syntax errors, undefined names, unused imports
- **Code style**: PEP 8 compliance, naming conventions
- **Import sorting**: Automatic import organization (replaces isort)
- **Code improvements**: Suggests modern Python patterns
- **Bug detection**: Common mistakes and anti-patterns

### Example Fixes

```python
# Before (Ruff will fix)
import os
import sys
from typing import Dict, List
import json

# After (imports sorted and organized)
import json
import os
import sys
from typing import Dict, List
```

---

## Type Checking

We use **mypy** for static type checking with strict configuration.

### Configuration (`pyproject.toml`)

```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true
plugins = ["pydantic.mypy"]
```

### Usage

```bash
# Run type checker
make type-check

# Type check specific file
mypy app/api/v1/endpoints/users.py
```

### Type Hints Best Practices

```python
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# ✓ Good: All parameters and return types annotated
def get_user_by_email(
    email: str,
    db: AsyncSession
) -> Optional[User]:
    """Retrieve user by email address."""
    return await db.query(User).filter(User.email == email).first()

# ✗ Bad: Missing type hints
def get_user_by_email(email, db):
    return db.query(User).filter(User.email == email).first()

# ✓ Good: Pydantic models are fully typed
class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: Optional[str] = None

# ✓ Good: Async functions with type hints
async def create_user(
    user_data: UserCreate,
    db: AsyncSession
) -> User:
    """Create a new user."""
    user = User(**user_data.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

### Pydantic Plugin

The Pydantic plugin for mypy provides:
- Better type inference for Pydantic models
- Validation of model fields
- Type checking for model methods

---

## Pre-commit Hooks

Pre-commit hooks automatically run code quality checks before each commit.

### Installation

```bash
# Install hooks
make pre-commit

# This will run checks on every git commit
```

### What Runs on Commit

1. **File checks**: trailing whitespace, end-of-file, large files
2. **Black**: Code formatting
3. **Ruff**: Linting with auto-fix
4. **mypy**: Type checking
5. **Bandit**: Security vulnerability scanning
6. **YAML/JSON/TOML**: Configuration file validation

### Manual Execution

```bash
# Run all hooks on all files
make pre-commit-run

# Run specific hook
pre-commit run black --all-files

# Skip hooks for a commit (use sparingly!)
git commit --no-verify -m "message"

# Update hook versions
make pre-commit-update
```

### Configuration (`.pre-commit-config.yaml`)

The configuration includes:
- Black 24.8.0
- Ruff 0.6.8
- mypy 1.11.2
- Bandit 1.7.9 (security)
- Standard pre-commit hooks

### Troubleshooting

If pre-commit fails:

```bash
# See what failed
git status

# Fix issues manually
make format
make lint

# Or let pre-commit auto-fix
pre-commit run --all-files

# Then try committing again
git add .
git commit -m "message"
```

---

## Hot Reload

The development server uses **Uvicorn** with automatic reload enabled.

### Usage

```bash
# Start server with hot reload (production log level)
make dev

# Start server with debug logging
make dev-debug
```

### Configuration

```bash
# Development server command
uvicorn main:app \
  --reload \                    # Enable hot reload
  --host 0.0.0.0 \             # Listen on all interfaces
  --port 8000 \                # Port 8000
  --log-level info \           # Log level
  --reload-dir app \           # Watch app directory
  --reload-dir main.py         # Watch main.py file
```

### What Gets Reloaded

When you save changes to any of these files, the server automatically restarts:
- `main.py`
- `app/**/*.py` (all Python files in app directory)
- Configuration changes in `.env` (requires manual restart)

### Hot Reload in Action

```bash
$ make dev
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.

# You edit app/api/v1/endpoints/users.py
INFO:     Detected file change in 'app/api/v1/endpoints/users.py'
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Performance Note

Hot reload watches file system changes. In large projects:
- Only watch directories that contain code (`--reload-dir`)
- Exclude directories with many files (already configured)
- Consider using `--reload-exclude` for specific patterns

---

## Editor Configuration

We use **EditorConfig** for consistent editor settings across all IDEs.

### Configuration (`.editorconfig`)

```ini
# Python files
[*.py]
indent_style = space
indent_size = 4
max_line_length = 88

# YAML files
[*.{yml,yaml}]
indent_style = space
indent_size = 2

# All files
[*]
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
charset = utf-8
```

### Supported Editors

EditorConfig is supported by:
- **VS Code**: Install "EditorConfig for VS Code" extension
- **PyCharm/IntelliJ**: Built-in support
- **Sublime Text**: Install "EditorConfig" package
- **Vim**: Install "editorconfig-vim" plugin
- **Emacs**: Install "editorconfig-emacs" package

### VS Code Setup

Recommended extensions for VS Code:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "editorconfig.editorconfig",
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml"
  ]
}
```

Recommended settings (`.vscode/settings.json`):

```json
{
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true
}
```

---

## Development Workflow

### Complete Development Cycle

```bash
# 1. Pull latest changes
git pull origin main

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Start development environment
make db-up
make dev

# 4. Write code with hot reload
# Edit files, server auto-restarts

# 5. Write tests (TDD approach)
pytest tests/test_my_feature.py -v

# 6. Run all tests
make test

# 7. Check code quality
make check

# 8. Commit changes (pre-commit runs automatically)
git add .
git commit -m "Add my feature"

# 9. Push and create PR
git push origin feature/my-feature
```

### Code Quality Checklist

Before pushing code, ensure:

- [ ] All tests pass: `make test`
- [ ] Code is formatted: `make format`
- [ ] No linting errors: `make lint`
- [ ] Type checking passes: `make type-check`
- [ ] Pre-commit hooks pass: `make pre-commit-run`

Run all checks at once:

```bash
make check
```

### Continuous Integration

Our CI pipeline runs the same checks:

1. Install dependencies
2. Run linting (Ruff)
3. Run formatting check (Black)
4. Run type checking (mypy)
5. Run security scanning (Bandit)
6. Run tests with coverage
7. Upload coverage report

If CI fails, the same commands that work locally will fix the issues.

---

## Tips and Best Practices

### 1. Use Make Commands

All common tasks have Makefile shortcuts:

```bash
make help  # See all available commands
```

### 2. Keep Dependencies Updated

```bash
# Update pre-commit hooks
make pre-commit-update

# Update Python dependencies
pip install --upgrade -r requirements/development.txt
```

### 3. Run Tests Often

```bash
# Quick test during development
pytest tests/test_my_feature.py -v

# Run all tests before commit
make test

# Run with coverage
make test-cov
```

### 4. Use IPython Shell

```bash
# Start interactive shell with app context
make shell

# Import and test your code
>>> from app.models.user import User
>>> from app.core.database import AsyncSessionLocal
```

### 5. Debug with ipdb

Add breakpoint to your code:

```python
import ipdb; ipdb.set_trace()
```

When code hits this line, you get an interactive debugger.

### 6. Monitor Logs

```bash
# Development server logs
make dev

# Database logs
make db-logs

# Test with verbose output
pytest -v -s
```

---

## Troubleshooting

### Pre-commit Hooks Not Running

```bash
# Reinstall hooks
pre-commit uninstall
make pre-commit
```

### Type Checking Errors

```bash
# Run mypy on specific file
mypy app/api/v1/endpoints/users.py

# Common fixes:
# - Add type hints to function parameters
# - Import types from typing module
# - Use Optional[T] for nullable values
# - Use List[T], Dict[K, V] for collections
```

### Hot Reload Not Working

```bash
# Check if uvicorn is running
ps aux | grep uvicorn

# Restart development server
Ctrl+C
make dev
```

### Formatting Conflicts

If Black and your editor disagree:

```bash
# Use Black's formatting (it's the source of truth)
make format

# Configure your editor to use Black
# See Editor Configuration section
```

---

## Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [EditorConfig Documentation](https://editorconfig.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
