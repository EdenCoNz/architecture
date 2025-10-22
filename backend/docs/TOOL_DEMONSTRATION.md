# Code Quality Tools Demonstration

This document demonstrates the code quality tools in action with real examples.

## Table of Contents

1. [Black - Code Formatter](#black---code-formatter)
2. [isort - Import Sorter](#isort---import-sorter)
3. [Flake8 - Linter](#flake8---linter)
4. [mypy - Type Checker](#mypy---type-checker)
5. [pytest - Test Runner](#pytest---test-runner)
6. [Pre-commit Hooks](#pre-commit-hooks)

---

## Black - Code Formatter

### What Black Does

Black automatically formats your Python code to a consistent style. It handles:
- Line length (100 characters by default)
- Indentation
- Quotes (normalizes to double quotes)
- Whitespace
- Line breaks

### Example: Before and After

**Before Black** (inconsistent formatting):
```python
def calculate_total(items,tax_rate=0.08,discount=None):
  total=sum([item['price']for item in items])
  if discount:total=total-discount
  return total*(1+tax_rate)
```

**After Black** (consistent formatting):
```python
def calculate_total(items, tax_rate=0.08, discount=None):
    total = sum([item["price"] for item in items])
    if discount:
        total = total - discount
    return total * (1 + tax_rate)
```

### Running Black

```bash
# Check if files need formatting (doesn't modify)
black --check .

# Format all files
black .

# Format specific file
black apps/core/models.py

# Preview changes without modifying
black --diff apps/core/models.py
```

### Configuration

From `pyproject.toml`:
```toml
[tool.black]
line-length = 100          # Max characters per line
target-version = ['py312'] # Target Python 3.12
extend-exclude = '''
/(
  migrations  # Don't format Django migrations
)/
'''
```

**Rationale**:
- **100 characters**: Balances readability with screen space
- **Excludes migrations**: Django migrations shouldn't be manually edited
- **Python 3.12**: Uses modern Python syntax

---

## isort - Import Sorter

### What isort Does

isort organizes import statements into standardized groups:
1. Standard library imports (e.g., `os`, `sys`)
2. Third-party imports (e.g., `django`, `requests`)
3. Local application imports (e.g., `apps.core.models`)

### Example: Before and After

**Before isort** (random order):
```python
from apps.core.models import User
import os
from django.db import models
import sys
from rest_framework import serializers
from apps.utils.helpers import generate_uuid
from typing import Optional
```

**After isort** (organized):
```python
import os
import sys
from typing import Optional

from django.db import models
from rest_framework import serializers

from apps.core.models import User
from apps.utils.helpers import generate_uuid
```

### Running isort

```bash
# Check if imports need sorting (doesn't modify)
isort --check-only .

# Sort all imports
isort .

# Sort specific file
isort apps/core/models.py

# Preview changes
isort --diff apps/core/models.py
```

### Configuration

From `pyproject.toml`:
```toml
[tool.isort]
profile = "black"          # Compatible with Black
line_length = 100          # Match Black's line length
multi_line_output = 3      # Vertical hanging indent
skip_glob = ["*/migrations/*"]  # Skip migrations
```

---

## Flake8 - Linter

### What Flake8 Does

Flake8 checks your code for:
- **Style violations** (PEP 8 standards)
- **Programming errors** (undefined variables, syntax errors)
- **Complexity issues** (functions that are too complex)
- **Django-specific issues** (via flake8-django plugin)
- **Common bugs** (via flake8-bugbear plugin)

### Example: Common Issues

#### 1. Unused Import

**Code**:
```python
import os
import sys

def hello():
    print("Hello, World!")
```

**Flake8 Output**:
```
example.py:1:1: F401 'os' imported but unused
example.py:2:1: F401 'sys' imported but unused
```

**Fix**:
```python
# Remove unused imports
def hello():
    print("Hello, World!")
```

#### 2. Undefined Variable

**Code**:
```python
def calculate_total(items):
    total = sum(items)
    return totl  # Typo: should be 'total'
```

**Flake8 Output**:
```
example.py:3:12: F821 undefined name 'totl'
```

**Fix**:
```python
def calculate_total(items):
    total = sum(items)
    return total  # Fixed typo
```

#### 3. Line Too Long

**Code**:
```python
def process_data(data, option1=True, option2=False, option3=None, option4="default", option5=100):
    # This line exceeds 100 characters
    pass
```

**Flake8 Output**:
```
example.py:1:101: E501 line too long (108 > 100 characters)
```

**Fix** (Black auto-formats this):
```python
def process_data(
    data,
    option1=True,
    option2=False,
    option3=None,
    option4="default",
    option5=100,
):
    pass
```

#### 4. Complexity Warning

**Code**:
```python
def complex_function(a, b, c, d):
    if a:
        if b:
            if c:
                if d:
                    if a > b:
                        if c > d:
                            return True
    return False
```

**Flake8 Output**:
```
example.py:1:1: C901 'complex_function' is too complex (11)
```

**Fix** (refactor to reduce complexity):
```python
def complex_function(a, b, c, d):
    if not (a and b and c and d):
        return False
    return a > b and c > d
```

### Running Flake8

```bash
# Lint entire project
flake8

# Lint specific directory
flake8 apps/

# Lint specific file
flake8 apps/core/models.py

# Show statistics
flake8 --statistics
```

### Configuration

From `.flake8`:
```ini
[flake8]
max-line-length = 100      # Match Black
max-complexity = 10        # Warn if complexity > 10
extend-ignore = E203, W503 # Ignore Black conflicts
per-file-ignores =
    __init__.py:F401       # Allow unused imports in __init__.py
```

---

## mypy - Type Checker

### What mypy Does

mypy performs static type checking to catch type-related bugs before runtime:
- Verifies function arguments match expected types
- Ensures return types are correct
- Detects None/Optional misuse
- Catches attribute errors

### Example: Type Errors

#### 1. Missing Type Annotations

**Code**:
```python
def calculate_area(length, width):
    return length * width
```

**mypy Output**:
```
example.py:1: error: Function is missing a type annotation
```

**Fix**:
```python
def calculate_area(length: float, width: float) -> float:
    return length * width
```

#### 2. Type Mismatch

**Code**:
```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Calling with wrong type
greet(123)  # Should be string, not int
```

**mypy Output**:
```
example.py:5: error: Argument 1 to "greet" has incompatible type "int"; expected "str"
```

**Fix**:
```python
greet("John")  # Correct type
# or convert if needed
greet(str(123))
```

#### 3. None Handling

**Code**:
```python
def get_user_name(user_id: int) -> str:
    user = find_user(user_id)  # Returns User or None
    return user.name  # Error if user is None!
```

**mypy Output**:
```
example.py:3: error: Item "None" has no attribute "name"
```

**Fix**:
```python
from typing import Optional

def get_user_name(user_id: int) -> Optional[str]:
    user = find_user(user_id)
    if user is None:
        return None
    return user.name
```

#### 4. Return Type Mismatch

**Code**:
```python
def calculate_total(items: list[dict]) -> int:
    total = sum(item["price"] for item in items)
    return f"Total: ${total}"  # Returns str, not int!
```

**mypy Output**:
```
example.py:3: error: Incompatible return value type (got "str", expected "int")
```

**Fix**:
```python
def calculate_total(items: list[dict]) -> int:
    return sum(item["price"] for item in items)
```

### Running mypy

```bash
# Type check entire apps directory
mypy apps/

# Type check specific file
mypy apps/core/models.py

# Show error codes
mypy --show-error-codes apps/

# Generate coverage report
mypy --html-report mypy-report apps/
```

### Configuration

From `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.12"
disallow_untyped_defs = true   # Require type annotations
check_untyped_defs = true      # Check untyped functions
warn_unused_ignores = true     # Warn about unnecessary ignores
plugins = [
    "mypy_django_plugin.main",  # Django type support
    "mypy_drf_plugin.main"      # DRF type support
]
```

---

## pytest - Test Runner

### What pytest Does

pytest runs your tests and provides:
- Test discovery (finds all test_*.py files)
- Detailed failure output
- Code coverage reporting
- Test fixtures and markers
- Parallel test execution

### Example: Running Tests

#### Basic Test

**Code** (`tests/test_example.py`):
```python
import pytest

def test_addition():
    """Test basic addition."""
    assert 1 + 1 == 2

def test_string_operations():
    """Test string operations."""
    result = "hello".upper()
    assert result == "HELLO"

@pytest.mark.unit
def test_list_operations():
    """Test list operations."""
    items = [1, 2, 3]
    assert len(items) == 3
    assert sum(items) == 6
```

#### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_example.py

# Run specific test function
pytest tests/test_example.py::test_addition

# Run tests by marker
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests

# Run with coverage
pytest --cov=apps --cov-report=html

# Run in parallel (faster)
pytest -n auto
```

#### Test Output

**Success**:
```
========================= test session starts =========================
collected 3 items

tests/test_example.py::test_addition PASSED                     [ 33%]
tests/test_example.py::test_string_operations PASSED            [ 66%]
tests/test_example.py::test_list_operations PASSED              [100%]

========================== 3 passed in 0.12s ==========================
```

**Failure**:
```
========================= test session starts =========================
collected 1 items

tests/test_example.py::test_addition FAILED                     [100%]

============================== FAILURES ===============================
___________________________ test_addition ____________________________

    def test_addition():
        """Test basic addition."""
>       assert 1 + 1 == 3
E       assert 2 == 3

tests/test_example.py:5: AssertionError
======================= 1 failed in 0.15s ============================
```

### Configuration

From `pytest.ini`:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.testing
addopts =
    --verbose              # Detailed output
    --cov=apps            # Measure coverage
    --cov-report=html     # HTML coverage report
    --reuse-db            # Reuse database between runs
    --nomigrations        # Don't run migrations
markers =
    unit: Unit tests
    integration: Integration tests
    api: API endpoint tests
```

---

## Pre-commit Hooks

### What Pre-commit Does

Pre-commit automatically runs checks before each git commit:
1. Prevents commits with issues
2. Auto-fixes formatting problems
3. Ensures consistent code quality
4. Saves CI/CD time

### Hooks Configured

From `.pre-commit-config.yaml`:

| Hook | Purpose | Auto-fix |
|------|---------|----------|
| trailing-whitespace | Remove trailing spaces | Yes |
| end-of-file-fixer | Ensure newline at EOF | Yes |
| check-yaml | Validate YAML syntax | No |
| check-json | Validate JSON syntax | No |
| check-toml | Validate TOML syntax | No |
| check-merge-conflict | Detect merge conflicts | No |
| debug-statements | Find debug code (pdb) | No |
| black | Format Python code | Yes |
| isort | Sort imports | Yes |
| flake8 | Lint code | No |
| mypy | Type check | No |

### Example: Pre-commit in Action

#### Scenario: Committing Code with Issues

```bash
# Stage changes
git add apps/core/models.py

# Attempt to commit
git commit -m "Add user model"
```

**Pre-commit Output**:
```
Trim Trailing Whitespace...............................Passed
Fix End of Files.......................................Passed
Check Yaml.............................................Passed
Check JSON.............................................Passed
Check Toml.............................................Passed
Check for merge conflicts..............................Passed
Debug Statements (Python)..............................Passed
black..................................................Failed
- hook id: black
- files were modified by this hook

reformatted apps/core/models.py
All done! ✨ 🍰 ✨
1 file reformatted.

isort..................................................Failed
- hook id: isort
- files were modified by this hook

Fixing apps/core/models.py

flake8.................................................Passed
mypy...................................................Passed
```

**What Happened**:
1. ✅ Black auto-formatted the file
2. ✅ isort auto-sorted imports
3. ❌ Commit was blocked

**Next Steps**:
```bash
# Files were auto-fixed, re-stage them
git add apps/core/models.py

# Commit again
git commit -m "Add user model"
# This time it will pass!
```

#### Scenario: Type Error Detected

```bash
git add apps/api/views.py
git commit -m "Add API view"
```

**Pre-commit Output**:
```
... (other hooks pass)
mypy...................................................Failed
- hook id: mypy
- exit code: 1

apps/api/views.py:15: error: Function is missing a return type annotation
apps/api/views.py:18: error: Argument 1 has incompatible type "int"; expected "str"

Found 2 errors in 1 file (checked 1 source file)
```

**What Happened**:
- mypy found type errors
- Commit was blocked

**Fix**:
1. Add type annotations
2. Fix type mismatches
3. Re-commit

### Installing Hooks

```bash
# Install (one-time setup)
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Update hook versions
pre-commit autoupdate
```

---

## Complete Workflow Example

### TDD Workflow with Code Quality Tools

#### 1. Write a Failing Test (Red)

```python
# tests/unit/test_calculator.py
import pytest
from apps.utils.calculator import calculate_percentage

@pytest.mark.unit
def test_calculate_percentage():
    """Test percentage calculation."""
    result = calculate_percentage(50, 200)
    assert result == 25.0
```

**Run test**:
```bash
pytest tests/unit/test_calculator.py
# FAILS - module doesn't exist yet
```

#### 2. Write Code to Pass Test (Green)

```python
# apps/utils/calculator.py
def calculate_percentage(part: float, whole: float) -> float:
    """Calculate what percentage part is of whole."""
    if whole == 0:
        return 0.0
    return (part / whole) * 100
```

**Run test**:
```bash
pytest tests/unit/test_calculator.py
# PASSES - test passes
```

#### 3. Run Quality Checks (Refactor)

```bash
# Format code
make format

# Run all quality checks
make quality

# Output:
# ✓ Black formatting: Passed
# ✓ isort: Passed
# ✓ Flake8: Passed
# ✓ mypy: Passed
```

#### 4. Commit with Pre-commit Hooks

```bash
git add apps/utils/calculator.py tests/unit/test_calculator.py
git commit -m "Add percentage calculation utility"

# Pre-commit runs all hooks
# All hooks pass ✓
# Commit succeeds!
```

---

## Summary

### Tool Responsibilities

| Tool | When It Runs | Purpose | Auto-fix |
|------|-------------|---------|----------|
| **Black** | On save, pre-commit, manual | Code formatting | Yes |
| **isort** | On save, pre-commit, manual | Import sorting | Yes |
| **Flake8** | Pre-commit, manual | Linting | No |
| **mypy** | Pre-commit, manual | Type checking | No |
| **pytest** | Manual, CI/CD | Testing | N/A |

### Quality Workflow

```
Write Code
    ↓
Save (auto-format with Black/isort in editor)
    ↓
Run Tests (pytest)
    ↓
Run Quality Checks (make quality)
    ↓
Stage Changes (git add)
    ↓
Commit (git commit)
    ↓
Pre-commit Hooks Run
    ↓
[Pass] → Commit succeeds → Push
[Fail] → Fix issues → Re-commit
```

### Quick Commands

```bash
# One command to rule them all
make quality && make test

# If that passes, you're ready to commit!
git add .
git commit -m "Your message"
```

---

**Remember**: These tools are your friends! They catch bugs early and ensure consistent code quality across the team. 🚀
