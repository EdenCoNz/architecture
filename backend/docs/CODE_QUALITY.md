# Code Quality Tools Guide

This document describes the code quality tools configured for the backend project, their purpose, configuration, and usage.

## Table of Contents

1. [Overview](#overview)
2. [Tool Descriptions](#tool-descriptions)
3. [Configuration Files](#configuration-files)
4. [Usage](#usage)
5. [Editor Integration](#editor-integration)
6. [Pre-commit Hooks](#pre-commit-hooks)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The backend project uses multiple code quality tools to ensure consistent, maintainable, and bug-free code:

- **Black**: Opinionated code formatter
- **isort**: Import statement organizer
- **Flake8**: Linter for style guide enforcement
- **mypy**: Static type checker
- **pytest**: Testing framework with coverage reporting
- **pre-commit**: Git hook framework for automated checks

### Why These Tools?

| Tool | Purpose | Benefit |
|------|---------|---------|
| Black | Code formatting | Eliminates style debates, ensures consistency |
| isort | Import sorting | Organized imports, reduces merge conflicts |
| Flake8 | Linting | Catches bugs, enforces PEP 8 standards |
| mypy | Type checking | Prevents type-related bugs, improves IDE support |
| pytest | Testing | Ensures code correctness, enables TDD workflow |
| pre-commit | Automation | Runs checks automatically before commits |

---

## Tool Descriptions

### Black - Code Formatter

**Purpose**: Automatically formats Python code to a consistent style.

**Key Features**:
- Line length: 100 characters
- Target: Python 3.12
- Excludes: migrations, virtual environments

**Philosophy**: "Any color you like, as long as it's black." Black removes formatting debates by enforcing a single style.

**Configuration**: `pyproject.toml`

```toml
[tool.black]
line-length = 100
target-version = ['py312']
```

### isort - Import Organizer

**Purpose**: Sorts and organizes import statements consistently.

**Key Features**:
- Compatible with Black (profile = "black")
- Groups imports: standard library, third-party, local
- Line length: 100 characters
- Excludes: migrations

**Configuration**: `pyproject.toml`

```toml
[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
```

### Flake8 - Linter

**Purpose**: Enforces PEP 8 style guide and catches common programming errors.

**Key Features**:
- Max line length: 100 characters
- Max complexity: 10 (warns about overly complex functions)
- Plugins: flake8-django, flake8-bugbear
- Ignores: E203, W503 (Black compatibility)

**What It Catches**:
- Unused imports
- Undefined variables
- Syntax errors
- Style violations
- Complexity issues
- Django-specific anti-patterns

**Configuration**: `.flake8`

```ini
[flake8]
max-line-length = 100
max-complexity = 10
extend-ignore = E203, W503
```

### mypy - Type Checker

**Purpose**: Static type checking to catch type-related bugs before runtime.

**Key Features**:
- Python version: 3.12
- Strict checking enabled (disallow_untyped_defs)
- Django plugin support
- DRF plugin support

**What It Catches**:
- Type mismatches
- Missing return types
- Incorrect function signatures
- Optional value misuse

**Configuration**: `pyproject.toml`

```toml
[tool.mypy]
python_version = "3.12"
disallow_untyped_defs = true
plugins = ["mypy_django_plugin.main", "mypy_drf_plugin.main"]
```

**Note**: mypy requires type annotations in function signatures:

```python
# Bad - no type annotations
def calculate_total(items):
    return sum(item.price for item in items)

# Good - with type annotations
def calculate_total(items: list[Item]) -> Decimal:
    return sum(item.price for item in items)
```

### pytest - Testing Framework

**Purpose**: Run tests with coverage reporting and detailed output.

**Key Features**:
- Coverage tracking with branch coverage
- Test discovery (test_*.py files)
- Database reuse for speed (--reuse-db)
- No migrations in tests (--nomigrations)
- HTML and terminal coverage reports

**Configuration**: `pytest.ini`

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.testing
addopts = --cov=apps --cov-report=html --cov-branch
```

**Coverage Configuration**: `pyproject.toml`

```toml
[tool.coverage.run]
source = ["apps"]
omit = ["*/migrations/*", "*/tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = ["pragma: no cover", "def __repr__", "if TYPE_CHECKING:"]
```

---

## Configuration Files

### `pyproject.toml`

Central configuration for Black, isort, mypy, and coverage. This is the modern Python standard for tool configuration.

**Location**: `/home/ed/Dev/architecture/backend/pyproject.toml`

**Contains**:
- [tool.black] - Black formatter settings
- [tool.isort] - Import sorting settings
- [tool.mypy] - Type checker settings
- [tool.django-stubs] - Django type stubs configuration
- [tool.coverage.run] - Coverage measurement settings
- [tool.coverage.report] - Coverage reporting settings

### `.flake8`

Flake8 configuration (uses INI format as it doesn't support pyproject.toml yet).

**Location**: `/home/ed/Dev/architecture/backend/.flake8`

**Contains**:
- Line length limits
- Excluded directories
- Ignored error codes
- Complexity thresholds
- Per-file overrides

### `pytest.ini`

Pytest and coverage configuration.

**Location**: `/home/ed/Dev/architecture/backend/pytest.ini`

**Contains**:
- Django settings module
- Test discovery patterns
- Default pytest arguments
- Test markers (unit, integration, e2e)
- Coverage settings

### `.pre-commit-config.yaml`

Pre-commit hook configuration for automated checks on git commit.

**Location**: `/home/ed/Dev/architecture/backend/.pre-commit-config.yaml`

**Contains**:
- Hook definitions for each tool
- Tool versions
- Additional dependencies
- Execution order

### `.editorconfig`

Editor configuration for consistent coding styles across different editors and IDEs.

**Location**: `/home/ed/Dev/architecture/backend/.editorconfig`

**Contains**:
- Character encoding (UTF-8)
- Line endings (LF)
- Indentation (4 spaces for Python)
- Max line length
- File-specific settings

---

## Usage

### Setup (One-time)

1. **Install system dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt install python3.12-venv

   # macOS
   # (Usually included with Python installation)
   ```

2. **Create virtual environment**:
   ```bash
   cd backend
   python3 -m venv venv
   ```

3. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

4. **Install development dependencies**:
   ```bash
   make install
   # or
   pip install -r requirements/dev.txt
   ```

5. **Install pre-commit hooks**:
   ```bash
   make pre-commit
   # or
   pre-commit install
   ```

### Daily Usage

#### Format Code

```bash
# Format all Python files with Black and isort
make format

# Or run individually
black .
isort .
```

**When to use**: Before committing code, or continuously in your editor.

#### Run Linter

```bash
# Run Flake8 linter
make lint

# Or directly
flake8
```

**When to use**: Before committing, or continuously in your editor. Fix all reported issues.

#### Type Checking

```bash
# Run mypy type checker
make type-check

# Or directly
mypy apps/
```

**When to use**: Before committing, especially when adding new functions or changing signatures.

#### Run Tests

```bash
# Run all tests with coverage
make test

# Run with detailed coverage report
make coverage

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m api          # API tests only

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test function
pytest tests/unit/test_models.py::TestUserModel::test_create_user
```

**When to use**: Continuously during development (TDD workflow), and before committing.

#### All Quality Checks

```bash
# Run format, lint, and type-check
make quality
```

**When to use**: Before committing, or before opening a pull request.

### Makefile Commands

The `Makefile` provides convenient shortcuts:

```bash
make help         # Show all available commands
make install      # Install dependencies
make format       # Format code (Black + isort)
make lint         # Run Flake8 linter
make type-check   # Run mypy type checker
make quality      # Run all quality checks
make test         # Run tests
make coverage     # Run tests with coverage report
make pre-commit   # Install and run pre-commit hooks
make clean        # Remove cache files
```

---

## Editor Integration

### VS Code

1. **Install extensions**:
   - Python (Microsoft)
   - Pylance
   - Black Formatter
   - isort
   - Flake8
   - mypy

2. **Configure settings** (`.vscode/settings.json`):

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Path": "flake8",
  "python.formatting.provider": "black",
  "python.formatting.blackPath": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.linting.mypyEnabled": true,
  "python.linting.mypyPath": "mypy"
}
```

3. **Select Python interpreter**: Choose the virtual environment Python (`venv/bin/python`).

### PyCharm / IntelliJ IDEA

1. **Configure Black**:
   - Preferences → Tools → Black
   - Enable "On save"
   - Set path to Black in venv

2. **Configure Flake8**:
   - Preferences → Tools → External Tools
   - Add Flake8 tool pointing to venv

3. **Configure mypy**:
   - Preferences → Tools → External Tools
   - Add mypy tool pointing to venv

4. **Enable EditorConfig**:
   - Preferences → Editor → Code Style
   - Enable EditorConfig support (usually enabled by default)

### Vim / Neovim

Use plugins like:
- ALE (Asynchronous Lint Engine)
- coc.nvim with coc-pyright
- vim-black
- vim-isort

Example ALE configuration:

```vim
let g:ale_linters = {
\   'python': ['flake8', 'mypy'],
\}
let g:ale_fixers = {
\   'python': ['black', 'isort'],
\}
let g:ale_fix_on_save = 1
```

---

## Pre-commit Hooks

Pre-commit hooks automatically run quality checks before each commit, preventing bad code from entering the repository.

### Installation

```bash
# Install hooks (one-time setup)
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

### What Runs on Commit

1. **pre-commit/pre-commit-hooks**:
   - trailing-whitespace: Removes trailing whitespace
   - end-of-file-fixer: Ensures files end with newline
   - check-yaml: Validates YAML syntax
   - check-json: Validates JSON syntax
   - check-toml: Validates TOML syntax
   - check-added-large-files: Prevents large files from being committed
   - check-merge-conflict: Detects merge conflict markers
   - debug-statements: Detects debug statements (pdb, ipdb)

2. **Black**: Formats Python code

3. **isort**: Sorts imports

4. **Flake8**: Lints code with django and bugbear plugins

5. **mypy**: Type checks code with Django and DRF stubs

### Workflow

1. **Make code changes**
2. **Stage changes**: `git add .`
3. **Commit**: `git commit -m "Your message"`
4. **Pre-commit runs automatically**:
   - If checks pass → commit succeeds
   - If checks fail → commit is blocked
5. **Fix issues** (often auto-fixed by Black/isort)
6. **Re-stage**: `git add .`
7. **Commit again**: `git commit -m "Your message"`

### Bypassing Hooks (Use Sparingly)

```bash
# Skip pre-commit hooks (not recommended)
git commit --no-verify -m "Emergency fix"
```

**When to bypass**: Only in emergencies. All code will be checked in CI/CD anyway.

### Updating Hooks

```bash
# Update hook versions
pre-commit autoupdate

# Clean and reinstall hooks
pre-commit clean
pre-commit install
```

---

## Troubleshooting

### "Black would reformat" Error

**Problem**: Black finds formatting issues.

**Solution**: Run `make format` or `black .` to auto-format, then commit again.

### "isort would reformat" Error

**Problem**: Imports are not sorted correctly.

**Solution**: Run `make format` or `isort .` to auto-sort, then commit again.

### Flake8 Errors

**Problem**: Flake8 reports style violations or bugs.

**Common errors**:
- F401: Module imported but unused → Remove unused import
- E501: Line too long → Break line or use Black to reformat
- E302: Expected 2 blank lines → Add blank lines
- F841: Local variable assigned but never used → Remove or use variable

**Solution**: Read the error message, fix the issue, then commit again.

### mypy Type Errors

**Problem**: Type annotations are missing or incorrect.

**Common errors**:
- Missing return type annotation
- Missing parameter type annotations
- Type mismatch (e.g., passing str where int expected)

**Solution**: Add type annotations to functions:

```python
# Before
def process_data(data):
    return data.upper()

# After
def process_data(data: str) -> str:
    return data.upper()
```

### Pre-commit Hook Fails

**Problem**: Pre-commit hook fails to run.

**Solutions**:
1. **Ensure virtual environment is activated**: `source venv/bin/activate`
2. **Reinstall hooks**: `pre-commit install`
3. **Update hooks**: `pre-commit autoupdate`
4. **Run manually to debug**: `pre-commit run --all-files`

### "No module named X" in mypy

**Problem**: mypy can't find Django or DRF types.

**Solution**: Install type stubs:

```bash
pip install django-stubs djangorestframework-stubs
```

### Virtual Environment Issues

**Problem**: Commands not found or wrong Python version.

**Solutions**:
1. **Activate virtual environment**: `source venv/bin/activate`
2. **Recreate if corrupted**:
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   make install
   ```

### Tests Fail Due to Missing Dependencies

**Problem**: pytest can't import modules.

**Solution**: Install development dependencies:

```bash
pip install -r requirements/dev.txt
```

---

## Best Practices

### 1. Run Quality Checks Before Committing

```bash
# Complete quality check
make quality

# If passing, commit
git add .
git commit -m "Your message"
```

### 2. Fix Issues Immediately

Don't ignore linter warnings or type errors. They often indicate real bugs or maintenance issues.

### 3. Use Type Annotations

Add type hints to all functions:

```python
from typing import Optional
from decimal import Decimal

def calculate_discount(
    price: Decimal,
    discount_percent: Optional[float] = None
) -> Decimal:
    if discount_percent is None:
        return price
    return price * (1 - discount_percent / 100)
```

### 4. Follow TDD Workflow

1. Write a failing test (Red)
2. Write code to pass the test (Green)
3. Run `make quality` to ensure code quality (Refactor)
4. Repeat

### 5. Keep Configuration Updated

Periodically update tool versions:

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Update requirements
pip list --outdated
```

### 6. Document Exceptions

If you need to disable a check, document why:

```python
# Ignore type checking for third-party library without stubs
from third_party import something  # type: ignore

# Ignore coverage for debugging code
def debug_helper():  # pragma: no cover
    pass
```

### 7. Review Coverage Reports

After running tests, check coverage:

```bash
make coverage
# Opens htmlcov/index.html in browser
```

Aim for >80% coverage, but focus on meaningful tests, not just coverage numbers.

---

## Configuration Justification

### Why Line Length 100?

- **Rationale**: Balance between readability and screen real estate
- **Standard**: Django uses 119, but 100 is more readable and works better with side-by-side diffs
- **Modern screens**: Can easily accommodate 100 characters
- **Compatibility**: Works well with GitHub's code view

### Why Strict mypy?

- **Rationale**: Type checking catches bugs early, improves IDE support
- **Configuration**: `disallow_untyped_defs = true` ensures all functions have type annotations
- **Benefit**: Prevents type-related runtime errors, especially with Django's complex types

### Why Pre-commit Hooks?

- **Rationale**: Automated enforcement is more reliable than manual checks
- **Benefit**: Catches issues before CI/CD, saves time
- **Developer experience**: Immediate feedback reduces context switching

### Why Separate Requirements Files?

- **Rationale**: Production doesn't need development/testing tools
- **Benefit**: Smaller production images, faster deployments, reduced attack surface
- **Organization**: Clear separation between base, dev, and prod dependencies

### Why Multiple Linters?

- **Black**: Formatting only, no logic checks
- **Flake8**: Style and logic checks, but no formatting
- **mypy**: Type checking only
- **Complementary**: Each tool has a specific purpose, together they provide comprehensive coverage

---

## Additional Resources

### Official Documentation

- **Black**: https://black.readthedocs.io/
- **isort**: https://pycqa.github.io/isort/
- **Flake8**: https://flake8.pycqa.org/
- **mypy**: https://mypy.readthedocs.io/
- **pytest**: https://docs.pytest.org/
- **pre-commit**: https://pre-commit.com/

### PEP Standards

- **PEP 8**: Style Guide for Python Code
- **PEP 484**: Type Hints
- **PEP 668**: Marking Python base environments as "externally managed"

### Django-Specific

- **Django Coding Style**: https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/
- **Django REST Framework Style**: https://www.django-rest-framework.org/topics/contributing/

---

## Summary

The code quality tools are configured to:

1. **Automate formatting** (Black, isort) - no manual formatting needed
2. **Catch bugs** (Flake8, mypy) - before they reach production
3. **Enforce standards** (Pre-commit hooks) - consistent code quality
4. **Enable TDD** (pytest) - test-first development workflow
5. **Provide feedback** (Coverage reports) - know what's tested

**Remember**: These tools are here to help, not hinder. They catch issues early and ensure code quality across the team.

For questions or issues, refer to this guide or the official documentation linked above.
