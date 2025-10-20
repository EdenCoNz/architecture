# Dynamic Job Mapping Testing Plan

This document provides a comprehensive testing plan for the dynamic job mapping solution implemented to prevent job ID/name mismatch issues in the bug-logger workflow.

## Overview

The dynamic job mapping solution eliminates hardcoded job mappings and implements fail-fast error handling to prevent silent failures in bug logging. This testing plan validates all aspects of the implementation.

---

## Test Scenarios

### 1. Normal Operation Tests

#### Test 1.1: Backend CI Failure with Dynamic Mapping

**Objective:** Verify dynamic job mapping works correctly for backend CI failures.

**Pre-conditions:**
- Backend CI workflow has all jobs with valid `name:` fields
- All YAML files are syntactically correct

**Steps:**
1. Create a test branch: `test/dynamic-mapping-backend`
2. Introduce a lint failure in backend code:
   ```bash
   echo "import os" >> backend/src/backend/settings/production.py  # Unused import
   ```
3. Push changes and create PR
4. Wait for backend CI to fail on lint job
5. Verify bug-logger workflow runs

**Expected Results:**
- Bug-logger successfully extracts job mappings from backend-ci.yml
- Job matching works correctly:
  - Job ID: `lint`
  - Job Name: `Lint Check (Ruff)`
- GitHub issue is created with:
  - Correct job name in title
  - Complete log excerpt
  - All metadata fields populated
- No errors in bug-logger workflow logs

**Verification Commands:**
```bash
# Check workflow run logs
gh run list --workflow=bug-logger.yml --limit 1

# View detailed logs
gh run view <run-id> --log

# Check for error messages
gh run view <run-id> --log | grep "::error::"

# Verify issue was created
gh issue list --label bug --limit 1
```

---

#### Test 1.2: Frontend CI Failure with Dynamic Mapping

**Objective:** Verify dynamic job mapping works correctly for frontend CI failures.

**Pre-conditions:**
- Frontend CI workflow has all jobs with valid `name:` fields
- All YAML files are syntactically correct

**Steps:**
1. Create a test branch: `test/dynamic-mapping-frontend`
2. Introduce a lint failure in frontend code:
   ```bash
   echo "const unused = 1;" >> frontend/src/main.tsx  # Unused variable
   ```
3. Push changes and create PR
4. Wait for frontend CI to fail on lint job
5. Verify bug-logger workflow runs

**Expected Results:**
- Bug-logger successfully extracts job mappings from frontend-ci.yml
- Job matching works correctly:
  - Job ID: `lint`
  - Job Name: `Lint and Format Check`
- GitHub issue is created with complete details
- No errors in bug-logger workflow logs

---

### 2. Validation Tests

#### Test 2.1: PR Validation for Missing Job Name

**Objective:** Verify validation workflow catches missing job names in PRs.

**Pre-conditions:**
- Validation workflow is enabled
- Repository has valid workflow files

**Steps:**
1. Create a test branch: `test/validation-missing-name`
2. Modify backend-ci.yml to remove a job name:
   ```yaml
   jobs:
     lint:
       # name: Lint Check (Ruff)  # Comment out the name field
       runs-on: ubuntu-22.04
   ```
3. Commit and push
4. Create PR

**Expected Results:**
- Validation workflow fails
- PR check shows: "Job Mapping Validation Failed"
- PR comment is posted with:
  - Clear error message
  - List of jobs missing names
  - Instructions on how to fix
- PR cannot be merged until fixed

**Verification:**
```bash
# Check validation workflow status
gh pr checks

# View validation workflow logs
gh run view <run-id> --log | grep "Missing name"

# Check for PR comment
gh pr view <pr-number> --comments
```

---

#### Test 2.2: PR Validation for Duplicate Job Names

**Objective:** Verify validation workflow catches duplicate job names.

**Pre-conditions:**
- Validation workflow is enabled

**Steps:**
1. Create a test branch: `test/validation-duplicate-names`
2. Modify backend-ci.yml to create duplicate names:
   ```yaml
   jobs:
     lint:
       name: Quality Check
       runs-on: ubuntu-22.04
     format:
       name: Quality Check  # Duplicate name
       runs-on: ubuntu-22.04
   ```
3. Commit and push
4. Create PR

**Expected Results:**
- Validation workflow shows warning
- PR comment lists duplicate job names
- Clear guidance on making names unique

---

### 3. Error Handling Tests

#### Test 3.1: Missing Workflow File

**Objective:** Verify explicit failure when workflow file is not found.

**Pre-conditions:**
- Bug-logger workflow is functional

**Steps:**
1. Simulate a missing workflow file by renaming it temporarily:
   ```bash
   git mv .github/workflows/backend-ci.yml .github/workflows/backend-ci.yml.backup
   git commit -m "Test: Simulate missing workflow file"
   ```
2. Trigger a failure in another workflow that calls bug-logger
3. Observe bug-logger behavior

**Expected Results:**
- Bug-logger fails with explicit error message:
  ```
  ::error::FATAL: Workflow file not found: .github/workflows/backend-ci.yml

  This error indicates:
    1. Workflow file was moved or deleted
    2. Repository structure changed
    3. File path mapping is incorrect
  ```
- Workflow exits with code 1
- Error is visible in GitHub Actions UI
- No silent failure or undefined behavior

**Note:** This is a destructive test - restore the file immediately after:
```bash
git mv .github/workflows/backend-ci.yml.backup .github/workflows/backend-ci.yml
git commit -m "Restore workflow file"
```

---

#### Test 3.2: Job ID Not Found in Mapping

**Objective:** Verify explicit failure when job ID cannot be found.

**Pre-conditions:**
- Workflow files are intact

**Steps:**
1. Create a test branch: `test/missing-job-id`
2. Add a new job to backend-ci.yml WITHOUT a name field:
   ```yaml
   jobs:
     new-test-job:
       # Missing name field
       runs-on: ubuntu-22.04
       steps:
         - run: exit 1  # Force failure
   ```
3. Push changes and trigger workflow

**Expected Results:**
- Bug-logger fails with explicit error:
  ```
  ::error::FATAL: Could not find job name for failed job ID 'new-test-job'

  This indicates one of the following issues:
    1. Job ID 'new-test-job' does not exist in .github/workflows/backend-ci.yml
    2. Job ID mismatch between workflow file and job_results
    3. Dynamic extraction failed to capture this job

  Available job mappings in .github/workflows/backend-ci.yml:
    lint=Lint Check (Ruff)
    format=Format Check (Black)
    ...

  Failed job ID from job_results: new-test-job
  ```
- Debugging information is displayed
- Workflow exits with code 1

---

#### Test 3.3: Job Name Not Found in GitHub API

**Objective:** Verify explicit failure when job name doesn't match API response.

**Pre-conditions:**
- Workflow files are intact

**Steps:**
1. Create a test branch: `test/name-mismatch`
2. Modify backend-ci.yml job name to create a mismatch:
   ```yaml
   jobs:
     lint:
       name: "Lint Check (New Name)"  # Changed name
       runs-on: ubuntu-22.04
   ```
3. Introduce a lint failure
4. Push and trigger workflow

**Expected Results:**
- Bug-logger fails with explicit error:
  ```
  ::error::FATAL: Could not find job database ID for job name 'Lint Check (New Name)'

  This indicates one of the following issues:
    1. Job name mismatch between workflow file and GitHub API response
    2. GitHub API returned incomplete or unexpected data
    3. Job was skipped or didn't run

  Expected job name: Lint Check (New Name)
  Available jobs in API response:
    - Lint Check (Ruff)
    - Format Check (Black)
    ...
  ```
- Clear debugging steps provided
- Workflow exits with code 1

---

### 4. Multi-Workflow Tests

#### Test 4.1: Backend and Frontend Failures in Parallel

**Objective:** Verify both workflows can fail independently with correct job mapping.

**Steps:**
1. Create a test branch: `test/multi-workflow`
2. Introduce failures in both backend and frontend
3. Push changes and create PR
4. Wait for both CI workflows to fail

**Expected Results:**
- Two separate bug-logger runs
- Each extracts from correct workflow file:
  - Backend failure → backend-ci.yml
  - Frontend failure → frontend-ci.yml
- Two separate GitHub issues created
- No job mapping conflicts or confusion

---

#### Test 4.2: Unknown Workflow Name

**Objective:** Verify explicit failure for unregistered workflow names.

**Steps:**
1. Create a new workflow file: `.github/workflows/new-ci.yml`
2. Add jobs with failures
3. Configure it to call bug-logger
4. Don't add it to bug-logger's workflow name mapping

**Expected Results:**
- Bug-logger fails with explicit error:
  ```
  ::error::FATAL: Unknown workflow name: 'New CI'

  This error indicates one of the following:
    1. A new CI/CD workflow was added but not registered in bug-logger.yml
    2. Workflow name was changed without updating bug-logger.yml
    3. GitHub API returned unexpected workflow metadata

  Available workflow names:
    - Backend CI/CD
    - Frontend CI/CD

  To fix:
    1. If this is a new workflow, add case to WORKFLOW_FILE mapping
    2. If workflow was renamed, update the case statement
    3. Review .github/DEVOPS_GUIDELINES.md for workflow naming conventions
  ```

---

### 5. Integration Tests

#### Test 5.1: Complete Failure Resolution Cycle

**Objective:** Verify end-to-end workflow from failure to issue creation to resolution.

**Steps:**
1. Create a feature branch
2. Introduce a fixable lint error
3. Push and create PR
4. Wait for CI failure and bug issue creation
5. Fix the error
6. Push fix and verify CI passes
7. Verify bug resolver updates the issue

**Expected Results:**
- Dynamic job mapping works throughout entire cycle
- Issue created with correct job details
- Fix is properly logged
- Issue status updated correctly

---

#### Test 5.2: Multiple Failures in Same Job

**Objective:** Verify bug-logger handles multiple failures in the same job correctly.

**Steps:**
1. Create a test branch
2. Introduce multiple lint errors
3. Push and wait for failure
4. Fix one error and push
5. Wait for second failure

**Expected Results:**
- First failure creates issue with dynamic mapping
- Second failure is recognized as retry or new failure
- Job mapping works consistently across retries

---

### 6. Performance Tests

#### Test 6.1: Large Workflow File Parsing

**Objective:** Verify dynamic extraction performs well with large workflow files.

**Pre-conditions:**
- Workflow file with 20+ jobs

**Steps:**
1. Add multiple test jobs to workflow file (all with names)
2. Trigger a failure
3. Measure bug-logger execution time

**Expected Results:**
- Job mapping extraction completes in < 5 seconds
- No timeout errors
- Correct job matched despite large file

**Measurement:**
```bash
# Check workflow timing
gh run view <run-id> --log | grep "Step.*Dynamic Job Mapping"
```

---

## Regression Prevention

### Automated Safeguards

1. **PR Validation** (`.github/workflows/validate-job-mappings.yml`)
   - Runs on every PR modifying workflow files
   - Catches missing/duplicate names before merge
   - Prevents introduction of job mapping bugs

2. **YAML Syntax Validation**
   - All workflow files validated in CI
   - Syntax errors caught before deployment

3. **Documentation**
   - `.github/DEVOPS_GUIDELINES.md` provides clear guidelines
   - Inline comments explain dynamic extraction
   - Error messages reference troubleshooting steps

### Manual Checks

Before merging workflow changes:

```bash
# 1. Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/backend-ci.yml')); print('✓ Valid')"

# 2. Check for missing job names
yq eval '.jobs | to_entries | .[] | select(.value.name == null) | .key' .github/workflows/backend-ci.yml

# 3. Check for duplicate job names
yq eval '.jobs | to_entries | .[].value.name' .github/workflows/backend-ci.yml | sort | uniq -d

# 4. Test dynamic extraction
yq eval '.jobs | to_entries | .[] | .key + "=" + .value.name' .github/workflows/backend-ci.yml
```

---

## Test Execution Checklist

- [ ] Test 1.1: Backend CI failure with dynamic mapping
- [ ] Test 1.2: Frontend CI failure with dynamic mapping
- [ ] Test 2.1: PR validation for missing job name
- [ ] Test 2.2: PR validation for duplicate job names
- [ ] Test 3.1: Missing workflow file error handling
- [ ] Test 3.2: Job ID not found in mapping
- [ ] Test 3.3: Job name not found in GitHub API
- [ ] Test 4.1: Backend and frontend failures in parallel
- [ ] Test 4.2: Unknown workflow name
- [ ] Test 5.1: Complete failure resolution cycle
- [ ] Test 5.2: Multiple failures in same job
- [ ] Test 6.1: Large workflow file parsing

---

## Success Criteria

All tests must pass with the following outcomes:

1. **No Silent Failures:** All error conditions produce explicit failures with detailed error messages
2. **Correct Job Matching:** Failed jobs are always matched correctly to their workflow definitions
3. **Complete Bug Reports:** GitHub issues contain all required information with correct job details
4. **Fast Execution:** Dynamic extraction completes in < 5 seconds even with large workflows
5. **Clear Error Messages:** All error messages provide:
   - What went wrong
   - Why it might have happened
   - How to debug and fix

---

## Rollback Plan

If critical issues are discovered:

1. **Immediate Rollback:**
   ```bash
   # Revert to previous version
   git revert <commit-sha>
   git push
   ```

2. **Restore Hardcoded Mapping (Temporary):**
   - Edit `.github/workflows/bug-logger.yml`
   - Restore hardcoded `JOB_ID_TO_NAME_MAP`
   - Remove dynamic extraction code
   - Push emergency fix

3. **Disable Validation (if blocking PRs):**
   - Rename validation workflow file
   - Create issue to track re-enablement
   - Fix validation issues
   - Re-enable when ready

---

## Maintenance

### After Adding New Workflows

1. Add workflow name to bug-logger.yml case statement
2. Ensure all jobs have `name:` fields
3. Run validation workflow manually
4. Test with intentional failure

### After Renaming Workflows

1. Update bug-logger.yml workflow name mapping
2. Update DEVOPS_GUIDELINES.md
3. Run full test suite

### Quarterly Review

- Review error logs for any silent failures
- Check if error messages are helpful
- Update documentation based on team feedback
- Optimize job mapping extraction if needed

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-20
**Author:** DevOps Team
**Related Documents:**
- `.github/DEVOPS_GUIDELINES.md`
- `.github/workflows/JOB_MATCHING_FIX.md`
- `.github/workflows/bug-logger.yml`
- `.github/workflows/validate-job-mappings.yml`
