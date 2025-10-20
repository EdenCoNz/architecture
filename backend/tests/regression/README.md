# Code Quality Regression Tests

This directory contains automated regression tests that validate code quality standards across the backend codebase. These tests are designed to prevent code quality issues from being merged into the codebase.

## Overview

The code quality regression test suite was created in response to **GitHub Issue #47**, where unused imports were passing through code review and into CI/CD. These tests ensure that common code quality violations are automatically detected.

## Test Files

### test_code_quality.py

Comprehensive test suite covering:

1. **Unused Imports Detection** - Detects imports that are declared but never used
2. **Black Formatting Compliance** - Validates code follows Black formatting standards
3. **Ruff Code Quality Checks** - Comprehensive linting for common issues
4. **Configuration Validation** - Ensures quality tools are properly configured
5. **Original Bug Regression** - Specific tests ensuring the original issue cannot recur

## Running the Tests

### Run all code quality regression tests:
```bash
cd backend
make test -k regression
# or
pytest tests/regression/test_code_quality.py
```

### Run specific test categories:
```bash
# Test only unused imports detection
pytest tests/regression/test_code_quality.py::TestUnusedImportsDetection -v

# Test only Black formatting
pytest tests/regression/test_code_quality.py::TestBlackFormattingCompliance -v

# Test only Ruff checks
pytest tests/regression/test_code_quality.py::TestRuffCodeQualityChecks -v

# Test original bug regression
pytest tests/regression/test_code_quality.py::TestOriginalBugRegression -v
```

## Test Coverage

### TestUnusedImportsDetection
- AST-based analysis of unused imports
- Detection of `from X import Y` unused imports
- Star import detection (`from X import *`)
- Full source code scanning using Ruff F401 rule

### TestBlackFormattingCompliance
- Black formatter availability check
- Configuration validation
- Source file formatting compliance
- Line length consistency between Black and Ruff

### TestRuffCodeQualityChecks
- Undefined variable detection (F821)
- Syntax error detection (E999)
- Import ordering validation (I001)
- Unused variable detection (F841)
- Mutable default argument detection (B006)
- Comprehensive quality check with all configured rules

### TestCodeQualityConfiguration
- pyproject.toml existence and structure
- Ruff rule configuration validation
- pytest marker configuration
- Coverage exclusion rules

### TestOriginalBugRegression
- Verifies unused imports are detected in CI
- Validates CI pipeline includes lint step
- Confirms developer tools (make format) are available

## Integration with CI/CD

These tests run automatically as part of the test suite:
- Executed via `make test` in CI pipeline
- Fail the build if code quality violations are detected
- Provide actionable error messages with file locations and line numbers

## Fixing Code Quality Issues

When tests fail, use the following commands to fix issues:

```bash
# Auto-fix formatting and import ordering
make format

# View detailed linting errors
make lint

# Run type checking
make type-check
```

## Test Markers

The regression tests use the `@pytest.mark.regression` marker:

```bash
# Run only regression tests
pytest -m regression

# Run all tests except regression tests
pytest -m "not regression"
```

## Technical Implementation

### AST Analysis
The tests use Python's `ast` module to parse and analyze source code for unused imports, providing a robust detection mechanism that understands Python syntax.

### Subprocess Integration
Tests invoke Ruff and Black via subprocess to leverage their full capabilities:
- JSON output parsing for structured error reporting
- Exit code checking for pass/fail status
- Integration with project configuration in pyproject.toml

### Error Reporting
When violations are detected, tests provide:
- Count of violations by type
- File path and line number for each issue
- Violation description and suggested fix
- Commands to resolve the issues

## Best Practices

1. **Run tests before committing**: Use `make test` or `pytest tests/regression/`
2. **Fix formatting first**: Run `make format` to auto-fix many issues
3. **Check linting**: Run `make lint` to see all code quality issues
4. **Keep tests fast**: These tests are designed to run quickly (<15 seconds)
5. **Update tests when rules change**: Modify tests if Ruff/Black configurations change

## Related Documentation

- Main testing guide: `context/testing/django-drf-testing-best-practices-2025.md`
- Backend best practices: `context/backend/django-drf-postgresql-best-practices.md`
- Original bug report: GitHub Issue #47

## Maintenance

When adding new code quality rules:
1. Update the appropriate test class in `test_code_quality.py`
2. Add test methods for new rule categories
3. Update this README with new test descriptions
4. Ensure tests provide clear error messages

## Contact

For questions or issues with code quality tests, refer to the project's contribution guidelines or open an issue on GitHub.
