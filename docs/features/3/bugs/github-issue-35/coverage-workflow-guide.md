# Coverage Workflow Guide

**Feature:** #3 - Initialize Backend Project
**Bug Fix:** #github-issue-35 - Test job failed - test failures detected
**Document Version:** 1.0
**Last Updated:** 2025-10-19

## Overview

This guide explains how coverage reporting works in the backend CI/CD pipeline, when coverage data combination is needed, and how to maintain the workflow for different test execution scenarios.

## Table of Contents

1. [Coverage Collection Basics](#coverage-collection-basics)
2. [Single-Process vs Parallel Test Execution](#single-process-vs-parallel-test-execution)
3. [When Coverage Combine Is Needed](#when-coverage-combine-is-needed)
4. [Current Workflow Configuration](#current-workflow-configuration)
5. [How to Tell If Tests Run in Parallel](#how-to-tell-if-tests-run-in-parallel)
6. [Troubleshooting Coverage Issues](#troubleshooting-coverage-issues)
7. [Future Considerations](#future-considerations)

---

## Coverage Collection Basics

### What Is Coverage Data?

Coverage data tracks which lines of code were executed during test runs. The `coverage.py` library collects this data and stores it in files:

- **Single-process execution**: Creates `.coverage` file
- **Parallel execution**: Creates multiple `.coverage.<hostname>.<pid>.<random>` files

### Coverage Workflow Steps

The CI/CD pipeline processes coverage in these steps:

1. **Run tests**: Pytest executes tests with coverage plugin enabled
2. **Generate reports**: Coverage creates HTML, XML, and JSON reports
3. **Upload artifacts**: Reports are uploaded for later analysis
4. **Display summary**: Coverage statistics shown in GitHub Actions summary
5. **Check threshold**: Workflow fails if coverage is below 80%

---

## Single-Process vs Parallel Test Execution

### Single-Process Execution (Current Configuration)

**Command:** `make test` → `pytest`

**How it works:**
- All tests run in a single Python process sequentially
- Coverage collects data as tests execute
- Creates a single `.coverage` file
- **No coverage combine step needed**

**Pros:**
- Simpler execution model
- Easier debugging (sequential execution)
- No race condition risks
- Predictable test order

**Cons:**
- Slower execution (no parallelization)
- Doesn't utilize multiple CPU cores
- Longer CI/CD pipeline runs

**Coverage files created:**
```
backend/.coverage          # Single coverage data file
backend/htmlcov/           # HTML coverage report
backend/coverage.xml       # XML coverage report
backend/coverage.json      # JSON coverage report
```

### Parallel Execution (Available but Not Used)

**Command:** `make test-parallel` → `pytest -n auto`

**How it works:**
- Tests split across multiple Python processes (workers)
- Each worker creates its own coverage data file
- Multiple `.coverage.*` files are created
- **Coverage combine step IS needed** to merge files

**Pros:**
- Faster execution (uses multiple CPU cores)
- Reduces CI/CD pipeline time
- Better resource utilization

**Cons:**
- More complex execution model
- May expose race conditions in tests
- Harder to debug (parallel execution)
- Unpredictable test order

**Coverage files created:**
```
backend/.coverage.hostname.12345.abc123   # Worker 1 coverage data
backend/.coverage.hostname.12346.def456   # Worker 2 coverage data
backend/.coverage.hostname.12347.ghi789   # Worker 3 coverage data
backend/htmlcov/                          # HTML coverage report (after combine)
backend/coverage.xml                      # XML coverage report (after combine)
backend/coverage.json                     # JSON coverage report (after combine)
```

---

## When Coverage Combine Is Needed

### The `coverage combine` Command

**Purpose:** Merges multiple `.coverage.*` files into a single `.coverage` file

**When to use:**
- Tests run with `pytest -n <workers>` (parallel execution)
- Tests run with `pytest-xdist` plugin
- Coverage configuration has `parallel = true` AND tests actually run in parallel
- Multiple `.coverage.*` files exist after test execution

**When NOT to use:**
- Tests run with `pytest` (single-process)
- Only one `.coverage` file exists
- Tests are sequential (no parallel workers)

### Coverage Combine Error: "No data to combine"

This error occurs when:
- `coverage combine` is executed
- No `.coverage.*` files exist (only `.coverage` exists)
- Tests ran in single-process mode but workflow expects parallel files

**Solution:**
- Remove the `coverage combine` step from the workflow
- OR make the step conditional on parallel file existence
- OR change test execution to parallel mode

---

## Current Workflow Configuration

### Backend CI/CD Workflow

**File:** `.github/workflows/backend-ci.yml`

**Current Test Execution:**
```yaml
- name: Run tests with coverage
  run: make test    # Single-process execution
```

**Coverage Steps:**
```yaml
# Step 1: Run tests (creates .coverage file)
- name: Run tests with coverage
  run: make test

# Step 2: Upload coverage artifacts
- name: Upload coverage reports
  uses: actions/upload-artifact@v4
  with:
    name: backend-coverage-${{ github.sha }}
    path: |
      backend/htmlcov/
      backend/coverage.xml
      backend/coverage.json

# Step 3: Display coverage summary
- name: Coverage summary
  run: |
    echo "## Test Coverage Report" >> $GITHUB_STEP_SUMMARY
    poetry run coverage report >> $GITHUB_STEP_SUMMARY

# Step 4: Enforce 80% threshold
- name: Check coverage threshold
  run: |
    echo "Checking coverage threshold (minimum: 80%)"
    poetry run coverage report --fail-under=80
```

### Why Coverage Combine Was Removed

**Previous workflow** (from bug fix #github-issue-34):
```yaml
- name: Combine coverage data files
  run: poetry run coverage combine
```

This step was added in the fix for issue #34 but caused failures because:
1. Tests run in single-process mode (`make test`)
2. Only `.coverage` file is created
3. `coverage combine` expects `.coverage.*` files
4. Command fails with "No data to combine"

**Resolution:**
- Step was removed in Story #2 of bug fix #github-issue-35
- Workflow now works correctly with single-process test execution
- Coverage threshold check runs successfully

---

## How to Tell If Tests Run in Parallel

### Check 1: Workflow Test Command

**Location:** `.github/workflows/backend-ci.yml`

Look at the "Run tests with coverage" step:

```yaml
# Single-process execution
- name: Run tests with coverage
  run: make test

# Parallel execution (NOT currently used)
- name: Run tests with coverage
  run: make test-parallel
```

### Check 2: Makefile Test Target

**Location:** `backend/Makefile`

```makefile
# Single-process (current)
test:
	PYTHONPATH=src poetry run pytest

# Parallel (available but not used)
test-parallel:
	PYTHONPATH=src poetry run pytest -n auto
```

### Check 3: Pytest Configuration

**Location:** `backend/pyproject.toml`

Look for `-n` flag in pytest addopts:

```toml
[tool.pytest.ini_options]
addopts = [
    "--cov=src",
    # If no -n flag here, tests run in single-process
]
```

**Note:** The `-n` flag must be in the pytest command or addopts for parallel execution.

### Check 4: Coverage Files After Test Run

**Single-process execution creates:**
```bash
ls -la backend/.coverage*
# Output: backend/.coverage
```

**Parallel execution creates:**
```bash
ls -la backend/.coverage*
# Output:
# backend/.coverage.hostname.12345.abc123
# backend/.coverage.hostname.12346.def456
# backend/.coverage.hostname.12347.ghi789
```

### Check 5: Coverage Configuration

**Location:** `backend/pyproject.toml`

```toml
[tool.coverage.run]
parallel = true  # Enables parallel mode support
```

**Important:** `parallel = true` alone does NOT make tests run in parallel. Tests must be executed with `pytest -n <workers>` for parallel mode.

The `parallel = true` setting only tells coverage.py to:
- Create separate coverage files for each process (when tests run in parallel)
- Support multiprocess and threading concurrency tracking

---

## Troubleshooting Coverage Issues

### Issue 1: "No data to combine" Error

**Symptom:**
```
Error: No data to combine
Process completed with exit code 1
```

**Root Cause:**
- Workflow runs `coverage combine`
- Tests run in single-process mode
- Only `.coverage` file exists, no `.coverage.*` files

**Solution:**
- Remove `coverage combine` step from workflow
- OR make it conditional (see below)

**Conditional Coverage Combine:**
```yaml
- name: Combine coverage data files (if needed)
  run: |
    if ls .coverage.* 1> /dev/null 2>&1; then
      echo "Found parallel coverage files, combining..."
      poetry run coverage combine
    else
      echo "Single coverage file detected, skipping combine step"
    fi
```

### Issue 2: Coverage Threshold Check Fails

**Symptom:**
```
Error: Coverage is below 80%
```

**Root Cause:**
- Code coverage is actually below the 80% threshold
- OR coverage data file is missing/corrupted

**Solution:**
1. Check coverage report to see which files lack coverage:
   ```bash
   poetry run coverage report --show-missing
   ```
2. Add tests for uncovered code paths
3. OR adjust threshold if appropriate for the project stage

### Issue 3: Coverage Reports Not Generated

**Symptom:**
- Upload coverage artifacts step fails
- "No files found" error

**Root Cause:**
- Tests failed before coverage could be generated
- OR coverage plugin not enabled in pytest

**Solution:**
1. Ensure pytest-cov is installed:
   ```bash
   poetry show pytest-cov
   ```
2. Verify coverage options in pyproject.toml:
   ```toml
   [tool.pytest.ini_options]
   addopts = [
       "--cov=src",
       "--cov-report=html",
       "--cov-report=xml",
       "--cov-report=json",
   ]
   ```

### Issue 4: Coverage Data Mismatch

**Symptom:**
- Coverage shows 0% or incorrect percentages
- Coverage report shows wrong files

**Root Cause:**
- Coverage source path misconfigured
- Wrong files included/omitted

**Solution:**
1. Verify coverage source in pyproject.toml:
   ```toml
   [tool.coverage.run]
   source = ["src"]  # Should point to your source code directory
   ```
2. Check omit patterns to ensure test files are excluded:
   ```toml
   omit = [
       "*/tests/*",
       "*/test_*.py",
   ]
   ```

---

## Future Considerations

### Enabling Parallel Test Execution

If you need to enable parallel test execution for faster CI/CD runs:

**Step 1: Update workflow to use parallel tests**

File: `.github/workflows/backend-ci.yml`

```yaml
- name: Run tests with coverage
  run: make test-parallel  # Change from 'make test'
```

**Step 2: Add coverage combine step**

Add this step AFTER "Run tests with coverage":

```yaml
- name: Combine coverage data files
  run: |
    echo "Combining coverage data from parallel test workers..."
    poetry run coverage combine
    echo "Coverage data combined successfully"
```

**Step 3: Verify coverage configuration supports parallel mode**

File: `backend/pyproject.toml`

```toml
[tool.coverage.run]
parallel = true  # Should already be true
concurrency = ["thread", "multiprocessing"]  # Should already be set
```

**Step 4: Test the workflow**

1. Run tests locally with parallel execution:
   ```bash
   cd backend
   make test-parallel
   ls -la .coverage*  # Should see multiple .coverage.* files
   poetry run coverage combine
   poetry run coverage report
   ```

2. Push changes and verify CI/CD pipeline succeeds

### Conditional Coverage Combine (Recommended)

To support both single-process and parallel execution without workflow changes:

```yaml
- name: Combine coverage data files (if needed)
  run: |
    if ls .coverage.* 1> /dev/null 2>&1; then
      echo "Found parallel coverage files, combining..."
      poetry run coverage combine
      echo "Coverage data combined from multiple workers"
    else
      echo "Single coverage file detected, no combine needed"
    fi
```

This approach:
- Works with single-process tests (current)
- Works with parallel tests (future)
- No workflow changes needed when switching test modes
- Self-documenting through logging

### Monitoring Coverage Trends

Consider implementing coverage tracking over time:

1. **Upload coverage to external service:**
   - Codecov (https://codecov.io)
   - Coveralls (https://coveralls.io)
   - SonarQube

2. **Track coverage in artifacts:**
   - Store coverage.json for historical analysis
   - Compare coverage between PRs
   - Alert on coverage decreases

3. **Generate coverage badges:**
   - Add badge to README showing current coverage
   - Update badge automatically in CI/CD

---

## Summary

### Key Takeaways

1. **Current Configuration:**
   - Tests run in single-process mode (`make test`)
   - Creates single `.coverage` file
   - No `coverage combine` step needed
   - Coverage threshold check runs directly on `.coverage` file

2. **Coverage Combine Rule:**
   - ONLY needed when tests run in parallel mode
   - Required when multiple `.coverage.*` files exist
   - NOT needed for single-process test execution

3. **How to Verify Test Mode:**
   - Check workflow: `make test` (single) vs `make test-parallel` (parallel)
   - Check files: `.coverage` (single) vs `.coverage.*` (parallel)
   - Check pytest command: `pytest` (single) vs `pytest -n auto` (parallel)

4. **Future-Proofing:**
   - Use conditional `coverage combine` for flexibility
   - Document test execution mode in workflow comments
   - Test both single and parallel modes locally before deploying

### Workflow Maintenance Checklist

When modifying the coverage workflow:

- [ ] Understand current test execution mode (single vs parallel)
- [ ] Verify coverage files created match execution mode
- [ ] Add/remove `coverage combine` step based on execution mode
- [ ] Test workflow changes locally before pushing
- [ ] Document any changes to test execution mode
- [ ] Update this guide if workflow behavior changes
- [ ] Validate YAML syntax after making changes

---

## Related Documentation

- **Investigation Report:** `docs/features/3/bugs/github-issue-35/investigation-report.md`
- **User Stories:** `docs/features/3/bugs/github-issue-35/user-stories.md`
- **Backend CI Workflow:** `.github/workflows/backend-ci.yml`
- **Pytest Configuration:** `backend/pyproject.toml` (lines 153-182)
- **Coverage Configuration:** `backend/pyproject.toml` (lines 183-219)
- **Make Targets:** `backend/Makefile` (lines 57-85)

---

## Contact

For questions about this workflow or coverage configuration, refer to:
- DevOps Engineer Agent documentation
- GitHub Actions documentation: https://docs.github.com/en/actions
- Coverage.py documentation: https://coverage.readthedocs.io/
- Pytest-cov documentation: https://pytest-cov.readthedocs.io/
