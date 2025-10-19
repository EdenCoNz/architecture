# Code Quality Guide

This document describes the code quality tools, standards, and automated checks used in this project.

## Table of Contents

- [Overview](#overview)
- [Pre-Commit Hooks](#pre-commit-hooks)
- [Code Quality Tools](#code-quality-tools)
- [Modern Python Syntax Requirements](#modern-python-syntax-requirements)
- [Running Quality Checks](#running-quality-checks)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## Overview

This project enforces strict code quality standards using automated tools:

- **Black**: Code formatting (line length: 100)
- **Ruff**: Fast Python linter with pyupgrade rules
- **MyPy**: Static type checking
- **Pre-commit**: Automated pre-commit hooks

All code must pass these checks before being committed or merged.

## Pre-Commit Hooks

Pre-commit hooks automatically run quality checks before each commit, catching issues early in the development process.

### Initial Setup

```bash
# Install pre-commit dependency (already in pyproject.toml)
poetry install

# Install git hooks (one-time setup)
poetry run pre-commit install
```

### What Gets Checked

Pre-commit hooks run these checks automatically:

1. **Black** - Code formatting
2. **Ruff** - Linting and import sorting
3. **MyPy** - Type checking (excluding tests)
4. **Trailing whitespace** - Remove trailing whitespace
5. **End-of-file fixer** - Ensure files end with newline
6. **YAML/JSON/TOML validation** - Syntax checking
7. **Large files check** - Prevent committing large files (>1MB)
8. **Merge conflict detection** - Prevent committing merge conflicts
9. **Private key detection** - Prevent committing secrets
10. **Python-specific checks** - Prevent common Python mistakes

### Manual Execution

Run pre-commit hooks manually:

```bash
# Run all hooks on all files
poetry run pre-commit run --all-files

# Run specific hook
poetry run pre-commit run black --all-files
poetry run pre-commit run ruff --all-files
poetry run pre-commit run mypy --all-files

# Run hooks on specific files
poetry run pre-commit run --files src/apps/users/models.py

# Update hooks to latest versions
poetry run pre-commit autoupdate
```

### Bypassing Hooks (Not Recommended)

If you need to bypass pre-commit hooks temporarily (e.g., work-in-progress commit):

```bash
git commit --no-verify -m "WIP: work in progress"
```

**Warning**: Never bypass hooks for code intended to be merged. CI/CD will fail if quality checks don't pass.

## Code Quality Tools

### Black - Code Formatting

Black automatically formats Python code with consistent style.

**Configuration** (`pyproject.toml`):
- Line length: 100 characters
- Target: Python 3.12
- Excludes: migrations, venv, build artifacts

**Usage**:
```bash
# Format all code
make format
# or
poetry run black .

# Check formatting without changing files
poetry run black --check .

# Format specific file
poetry run black src/apps/users/models.py
```

### Ruff - Linting

Ruff is a fast Python linter that replaces Flake8, isort, and pyupgrade.

**Enabled Rules**:
- `E` - pycodestyle errors
- `W` - pycodestyle warnings
- `F` - pyflakes
- `I` - isort (import sorting)
- `B` - flake8-bugbear
- `C4` - flake8-comprehensions
- `UP` - pyupgrade (modern Python syntax)
- `ARG` - flake8-unused-arguments
- `SIM` - flake8-simplify

**Usage**:
```bash
# Run linting
make lint
# or
poetry run ruff check .

# Auto-fix issues
poetry run ruff check --fix .

# Check specific file
poetry run ruff check src/apps/users/models.py
```

### MyPy - Type Checking

MyPy performs static type analysis to catch type-related errors.

**Configuration**:
- Strict type checking enabled
- Django and DRF stubs installed
- Tests excluded from strict checking
- Migrations ignored

**Usage**:
```bash
# Run type checking
make type-check
# or
PYTHONPATH=src poetry run mypy src

# Check specific file
PYTHONPATH=src poetry run mypy src/apps/users/models.py
```

## Modern Python Syntax Requirements

This project targets **Python 3.12+** and requires modern syntax.

### Type Hints - Use Built-in Types

**Correct** (Python 3.12+):
```python
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

def get_user(user_id: int) -> User | None:
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
```

**Incorrect** (Old style - will fail Ruff checks):
```python
from typing import List, Dict, Optional

def process_items(items: List[str]) -> Dict[str, int]:  # ❌ Use list[str]
    return {item: len(item) for item in items}

def get_user(user_id: int) -> Optional[User]:  # ❌ Use User | None
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
```

### Union Types - Use `|` Operator

**Correct**:
```python
def parse_value(value: str | int | None) -> str:
    if value is None:
        return "empty"
    return str(value)
```

**Incorrect**:
```python
from typing import Union, Optional

def parse_value(value: Union[str, int, None]) -> str:  # ❌ Use str | int | None
    if value is None:
        return "empty"
    return str(value)
```

### isinstance() - Use `|` Operator (UP038)

**Correct**:
```python
if isinstance(value, int | str):
    print(f"Value: {value}")

if isinstance(obj, dict | list | tuple):
    process_collection(obj)
```

**Incorrect**:
```python
if isinstance(value, (int, str)):  # ❌ UP038 violation - use int | str
    print(f"Value: {value}")

if isinstance(obj, (dict, list, tuple)):  # ❌ UP038 violation
    process_collection(obj)
```

### Why These Requirements?

1. **Readability**: Modern syntax is clearer and more concise
2. **Consistency**: Python 3.12+ best practices
3. **Type Safety**: Better static analysis with `|` operator
4. **Future-Proof**: Aligns with Python's direction
5. **Automated Enforcement**: Tools automatically check compliance

### Ruff Rule UP038

Ruff's UP038 rule specifically checks for old-style isinstance syntax:

```
UP038: Use `X | Y` in `isinstance` call instead of `(X, Y)`
```

This rule caught the violations fixed in GitHub Issue #37:
```python
# Before (violations):
isinstance(value, (str, int))
isinstance(result, (list, dict))

# After (compliant):
isinstance(value, str | int)
isinstance(result, list | dict)
```

## Running Quality Checks

### Individual Tools

```bash
# Format code with Black
make format

# Run Ruff linting
make lint

# Run MyPy type checking
make type-check

# Run tests
make test
```

### All Checks at Once

```bash
# Using make commands
make format && make lint && make type-check && make test

# Using pre-commit (faster, parallel execution)
poetry run pre-commit run --all-files
```

### Recommended Workflow

1. **During Development** - Pre-commit hooks run automatically on commit
2. **Before Push** - Run `make format && make lint && make type-check && make test`
3. **In CI/CD** - Automated checks on every PR

## CI/CD Integration

All quality checks run automatically in GitHub Actions CI/CD pipeline.

### Pipeline Jobs

1. **Lint Check** - Ruff linting (`make lint`)
2. **Format Check** - Black formatting (`black --check`)
3. **Type Check** - MyPy type checking (`make type-check`)
4. **Test Suite** - Pytest with 80% coverage requirement

### Required Status Checks

Before merging to `main`, all checks must pass:

- ✅ Lint Check (Ruff)
- ✅ Format Check (Black)
- ✅ Type Check (MyPy)
- ✅ Test Suite (≥80% coverage)
- ✅ Build Verification

### Workflow File

See `.github/workflows/backend-ci.yml` for complete pipeline configuration.

## Troubleshooting

### Pre-commit Hook Failures

**Problem**: Pre-commit hooks fail on commit

**Solution**:
```bash
# Run hooks manually to see detailed errors
poetry run pre-commit run --all-files

# Fix specific issues
poetry run black .           # Format code
poetry run ruff check --fix . # Fix linting issues

# Commit again after fixes
git add .
git commit -m "Your message"
```

### Ruff UP038 Violations

**Problem**: `UP038 [*] Use X | Y in isinstance call instead of (X, Y)`

**Solution**: Replace tuple syntax with `|` operator:
```python
# Before
isinstance(value, (str, int))

# After
isinstance(value, str | int)
```

### Black Formatting Conflicts

**Problem**: Black wants to format code differently than you wrote it

**Solution**: Let Black format the code automatically:
```bash
poetry run black .
```

Black's formatting is non-negotiable - it ensures consistency across the codebase.

### MyPy Type Errors

**Problem**: MyPy reports type errors

**Common Solutions**:

1. Add type hints:
```python
# Before
def process(data):
    return data.upper()

# After
def process(data: str) -> str:
    return data.upper()
```

2. Use `| None` for optional values:
```python
# Before
def get_user(user_id: int):  # Missing return type
    return User.objects.filter(id=user_id).first()

# After
def get_user(user_id: int) -> User | None:
    return User.objects.filter(id=user_id).first()
```

3. Use type comments for complex types:
```python
from typing import TypedDict

class UserData(TypedDict):
    name: str
    email: str
    age: int

def create_user(data: UserData) -> User:
    return User.objects.create(**data)
```

### Skipping Specific Checks

**For specific lines** (use sparingly):
```python
# Disable Ruff check for one line
value = do_something()  # noqa: E501

# Disable MyPy check for one line
result = unsafe_operation()  # type: ignore[arg-type]
```

**For entire files** (configured in `pyproject.toml`):
```toml
[tool.ruff.lint.per-file-ignores]
"test_*.py" = ["ARG001", "ARG002"]  # Unused arguments ok in tests
```

### Pre-commit Hook Updates

Keep hooks updated to latest versions:

```bash
# Update all hooks
poetry run pre-commit autoupdate

# Update specific hook
poetry run pre-commit autoupdate --repo https://github.com/psf/black
```

### Clean Installation

If hooks are misbehaving, reinstall them:

```bash
# Uninstall hooks
poetry run pre-commit uninstall

# Reinstall hooks
poetry run pre-commit install

# Clear cache
poetry run pre-commit clean

# Run all hooks
poetry run pre-commit run --all-files
```

## Best Practices

### 1. Install Pre-commit Hooks Early

Set up pre-commit hooks immediately after cloning:
```bash
poetry install
poetry run pre-commit install
```

### 2. Run Checks Before Pushing

Always run quality checks before pushing:
```bash
make format && make lint && make type-check && make test
```

### 3. Fix Issues Incrementally

Don't accumulate quality violations. Fix them as you go.

### 4. Use IDE Integration

Configure your IDE to run Black, Ruff, and MyPy automatically:

- **VS Code**: Install Python extension, configure formatOnSave
- **PyCharm**: Enable Black as formatter, Ruff as linter
- **Vim/Neovim**: Use ALE or coc.nvim with Black, Ruff, MyPy

### 5. Review Pre-commit Output

When pre-commit hooks fail, read the output carefully:
```
Black....................................................................Failed
- hook id: black
- files were modified by this hook

reformatted src/apps/users/models.py
```

The hook tells you exactly what was modified and why.

### 6. Keep Configuration Updated

Review and update quality tool configuration periodically:
- Update pre-commit hook versions
- Review new Ruff rules
- Adjust coverage thresholds
- Update Python version targets

## Additional Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Python 3.12 Type Hints](https://docs.python.org/3.12/library/typing.html)
- [PEP 604 - Union Operator](https://peps.python.org/pep-0604/)

## Summary

Code quality in this project is enforced through:

1. **Pre-commit hooks** - Automatic checks before every commit
2. **CI/CD pipeline** - Automated checks on every PR
3. **Modern Python syntax** - Python 3.12+ with `|` operator
4. **Comprehensive tooling** - Black, Ruff, MyPy working together
5. **Documentation** - Clear guidelines and examples

By following these standards, we maintain a high-quality, consistent, and maintainable codebase.
