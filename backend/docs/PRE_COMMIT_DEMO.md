# Pre-Commit Hooks Demonstration

This document demonstrates how pre-commit hooks prevent code quality violations from being committed.

## Setup

After setting up the pre-commit hooks:

```bash
# Install dependencies (includes pre-commit)
poetry install

# Install git hooks
poetry run pre-commit install
```

## What Gets Prevented

### 1. Ruff UP038 Violations - isinstance() with Tuple Syntax

**Code with violation:**
```python
# backend/tests/integration/test_cors_configuration.py
def test_example():
    value = "test"
    if isinstance(value, (str, int)):  # ❌ UP038 violation
        print("Valid")
```

**Pre-commit output:**
```
Lint with Ruff...........................................................Failed
- hook id: ruff
- exit code: 1

backend/tests/integration/test_cors_configuration.py:10:8: UP038 [*] Use `X | Y` in `isinstance` call instead of `(X, Y)`
   |
10 |     if isinstance(value, (str, int)):
   |        ^^^^^^^^^^^^^^^^^^^^^^^^^^ UP038
   |
   = help: Convert to `X | Y`

Found 1 error.
```

**How to fix:**
```python
# Correct code
def test_example():
    value = "test"
    if isinstance(value, str | int):  # ✅ Correct
        print("Valid")
```

### 2. Black Formatting Violations

**Code with formatting issues:**
```python
# backend/src/apps/users/models.py
def create_user(username,email,password):  # ❌ Missing spaces
    return User.objects.create(username=username,email=email,password=password)
```

**Pre-commit output:**
```
Format code with Black....................................................Failed
- hook id: black
- files were modified by this hook

reformatted backend/src/apps/users/models.py

All done! ✨ 🍰 ✨
1 file reformatted.
```

**Auto-fixed code:**
```python
# backend/src/apps/users/models.py
def create_user(username, email, password):  # ✅ Properly formatted
    return User.objects.create(username=username, email=email, password=password)
```

### 3. Old-Style Type Hints

**Code with old-style syntax:**
```python
from typing import List, Dict, Optional

def process_data(items: List[str]) -> Dict[str, int]:  # ❌ Old style
    return {item: len(item) for item in items}

def get_user(user_id: int) -> Optional[User]:  # ❌ Old style
    return User.objects.filter(id=user_id).first()
```

**Pre-commit output:**
```
Lint with Ruff...........................................................Failed
- hook id: ruff
- exit code: 1

backend/src/apps/users/service.py:3:26: UP006 [*] Use `list` instead of `List` for type annotation
backend/src/apps/users/service.py:3:41: UP006 [*] Use `dict` instead of `Dict` for type annotation
backend/src/apps/users/service.py:6:30: UP007 [*] Use `X | Y` for union type annotations

Found 3 errors.
[*] 3 fixable with the `--fix` option.
```

**How to fix:**
```python
def process_data(items: list[str]) -> dict[str, int]:  # ✅ Modern syntax
    return {item: len(item) for item in items}

def get_user(user_id: int) -> User | None:  # ✅ Modern syntax
    return User.objects.filter(id=user_id).first()
```

### 4. Missing Type Hints

**Code without type hints:**
```python
def calculate_total(items):  # ❌ No type hints
    return sum(item.price for item in items)
```

**Pre-commit output:**
```
Type check with MyPy......................................................Failed
- hook id: mypy
- exit code: 1

backend/src/apps/orders/service.py:10: error: Function is missing a type annotation for one or more arguments  [no-untyped-def]
backend/src/apps/orders/service.py:10: error: Function is missing a return type annotation  [no-untyped-def]

Found 2 errors in 1 file (checked 1 source file)
```

**How to fix:**
```python
from decimal import Decimal

def calculate_total(items: list[Item]) -> Decimal:  # ✅ Type hints added
    return sum(item.price for item in items)
```

### 5. Security Issues

**Code with potential security risk:**
```python
# ❌ Private key accidentally committed
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"
```

**Pre-commit output:**
```
Detect private keys......................................................Failed
- hook id: detect-private-key
- exit code: 1

backend/.env:3:AWS_SECRET_KEY
```

This prevents accidentally committing secrets to the repository.

### 6. Large Files

**Attempting to commit a large file:**
```bash
# ❌ Committing a 2MB database dump
git add database_dump.sql
git commit -m "Add database"
```

**Pre-commit output:**
```
Check for large files....................................................Failed
- hook id: check-added-large-files
- exit code: 1

database_dump.sql (2048 KB) exceeds 1000 KB.
```

### 7. Trailing Whitespace

**Code with trailing whitespace:**
```python
def example():    # ❌ Trailing spaces
    return "test"
```

**Pre-commit output:**
```
Remove trailing whitespace...............................................Failed
- hook id: trailing-whitespace
- exit code: 1
- files were modified by this hook

Fixing backend/src/apps/users/views.py
```

**Auto-fixed:** Trailing whitespace is automatically removed.

## Complete Workflow Example

### Scenario: Developer makes changes with violations

```bash
# Developer writes code with quality issues
$ vim backend/tests/integration/test_cors_configuration.py

# Attempts to commit
$ git add backend/tests/integration/test_cors_configuration.py
$ git commit -m "Add CORS test"
```

### Pre-commit hooks run automatically

```
Remove trailing whitespace...............................................Passed
Ensure files end with newline............................................Passed
Validate YAML files......................................................Passed
Validate JSON files......................................................Passed
Check for large files....................................................Passed
Check for merge conflicts................................................Passed
Detect private keys......................................................Passed
Fix mixed line endings...................................................Passed
Format code with Black...................................................Passed
Lint with Ruff..........................................................Failed
- hook id: ruff
- exit code: 1

backend/tests/integration/test_cors_configuration.py:142:16: UP038 [*] Use `X | Y` in `isinstance` call instead of `(X, Y)`
backend/tests/integration/test_cors_configuration.py:156:16: UP038 [*] Use `X | Y` in `isinstance` call instead of `(X, Y)`

Found 2 errors.
[*] 2 fixable with the `--fix` option.
```

### Developer fixes the issues

```bash
# Fix the violations manually or use ruff --fix
$ ruff check --fix backend/tests/integration/test_cors_configuration.py

# Try committing again
$ git add backend/tests/integration/test_cors_configuration.py
$ git commit -m "Add CORS test"
```

### All checks pass

```
Remove trailing whitespace...............................................Passed
Ensure files end with newline............................................Passed
Validate YAML files......................................................Passed
Validate JSON files......................................................Passed
Check for large files....................................................Passed
Check for merge conflicts................................................Passed
Detect private keys......................................................Passed
Fix mixed line endings...................................................Passed
Format code with Black...................................................Passed
Lint with Ruff..........................................................Passed
Format imports with Ruff.................................................Passed
Type check with MyPy.....................................................Passed

[main abc1234] Add CORS test
 1 file changed, 50 insertions(+)
```

## Manual Execution

Run hooks manually without committing:

```bash
# Run all hooks on all files
poetry run pre-commit run --all-files

# Run specific hook on all files
poetry run pre-commit run black --all-files
poetry run pre-commit run ruff --all-files
poetry run pre-commit run mypy --all-files

# Run hooks on specific files
poetry run pre-commit run --files backend/tests/integration/test_cors_configuration.py
```

## Auto-Fix Capabilities

Some hooks automatically fix issues:

| Hook | Auto-Fix | Manual Fix Required |
|------|----------|-------------------|
| Black | ✅ Yes | No - auto-formats |
| Ruff (with --fix) | ✅ Yes | Some rules require manual fix |
| Ruff format | ✅ Yes | No - auto-formats imports |
| MyPy | ❌ No | Yes - add type hints manually |
| Trailing whitespace | ✅ Yes | No - auto-removes |
| End-of-file fixer | ✅ Yes | No - auto-adds newline |
| Mixed line endings | ✅ Yes | No - auto-fixes to LF |

## Benefits

### 1. Catch Issues Early
- Problems caught before commit, not in CI/CD
- Faster feedback loop
- Less context switching

### 2. Enforce Standards Automatically
- No manual checking required
- Consistent code quality
- Team-wide standards

### 3. Prevent CI/CD Failures
- Local checks match CI/CD checks
- Fewer failed pipeline runs
- Faster merge times

### 4. Learn Best Practices
- Clear error messages
- Auto-fix shows correct syntax
- Educational feedback

### 5. Reduce Code Review Time
- Automated checks handled by tools
- Reviewers focus on logic, not style
- Faster review cycles

## Skipping Hooks (Emergency Only)

In rare cases, you may need to bypass hooks:

```bash
# Skip hooks for one commit (not recommended)
git commit --no-verify -m "WIP: emergency fix"
```

**Warning**: CI/CD will still fail if quality checks don't pass. Only use for:
- Emergency hotfixes (will fix in follow-up commit)
- Work-in-progress commits on feature branches
- Temporary debugging commits

Never use `--no-verify` for code intended to be merged to main.

## Updating Hooks

Keep pre-commit hooks up to date:

```bash
# Update all hooks to latest versions
poetry run pre-commit autoupdate

# Review changes in .pre-commit-config.yaml
git diff .pre-commit-config.yaml

# Test updated hooks
poetry run pre-commit run --all-files

# Commit updated configuration
git add .pre-commit-config.yaml
git commit -m "Update pre-commit hooks"
```

## Troubleshooting

### Hooks fail after installation

**Problem**: Pre-commit hooks fail immediately after installation

**Solution**: Run hooks manually to see detailed errors:
```bash
poetry run pre-commit run --all-files
```

Fix any issues in existing code before committing new changes.

### Hook versions out of date

**Problem**: Hook versions don't match tool versions in pyproject.toml

**Solution**: Update hook versions:
```bash
poetry run pre-commit autoupdate
```

### Hooks run too slowly

**Problem**: Pre-commit hooks take too long

**Solutions**:
1. Run hooks only on changed files (default behavior)
2. Disable MyPy hook for faster commits (not recommended)
3. Use `--no-verify` sparingly for WIP commits

### Clean installation

**Problem**: Hooks are behaving incorrectly

**Solution**: Reinstall hooks:
```bash
poetry run pre-commit clean
poetry run pre-commit uninstall
poetry run pre-commit install
poetry run pre-commit run --all-files
```

## Summary

Pre-commit hooks provide:

✅ **Automatic quality checks** - Run before every commit
✅ **Immediate feedback** - Catch issues in seconds, not minutes
✅ **Auto-fix capabilities** - Many issues fixed automatically
✅ **CI/CD alignment** - Local checks match pipeline checks
✅ **Team consistency** - Everyone uses the same standards

Install once, benefit forever:
```bash
poetry install
poetry run pre-commit install
```

From then on, every commit is automatically checked for quality!
