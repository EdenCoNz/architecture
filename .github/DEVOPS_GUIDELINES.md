# DevOps Engineering Guidelines

This document provides essential guidelines for maintaining and modifying GitHub Actions workflows and Docker configurations in this repository. These guidelines ensure reliability, maintainability, and prevent common failure modes.

**Target Audience:** DevOps engineers, CI/CD maintainers, and contributors modifying workflow files.

---

## Table of Contents

- [Core Principles](#core-principles)
- [GitHub Actions Job Naming Convention](#github-actions-job-naming-convention)
- [Dynamic Job Mapping Architecture](#dynamic-job-mapping-architecture)
- [Error Handling Best Practices](#error-handling-best-practices)
- [Workflow Validation](#workflow-validation)
- [Docker Best Practices](#docker-best-practices)
- [Adding New Workflows](#adding-new-workflows)
- [Modifying Existing Workflows](#modifying-existing-workflows)
- [Troubleshooting Guide](#troubleshooting-guide)
- [Related Documentation](#related-documentation)

---

## Core Principles

### 1. Fail Fast, Fail Loud

**Problem:** Silent failures hide bugs and create debugging nightmares.

**Solution:** Every critical path must validate inputs and fail explicitly with detailed error messages.

```bash
# ❌ BAD: Silent failure
if [ -z "$JOB_ID" ]; then
  echo "Warning: Job ID not found"
  JOB_ID="unknown"
fi

# ✅ GOOD: Explicit failure with context
if [ -z "$JOB_ID" ] || [ "$JOB_ID" = "null" ]; then
  echo "::error::FATAL: Could not find job ID for failed job '$FAILED_JOB_ID'"
  echo "Available jobs:"
  jq -r '.jobs[] | "  - \(.name)"' workflow_jobs.json
  echo ""
  echo "Debugging steps:"
  echo "  1. Verify job exists in workflow file"
  echo "  2. Check job has 'name:' field defined"
  exit 1
fi
```

### 2. Single Source of Truth

**Problem:** Duplicating data across files leads to synchronization issues.

**Solution:** Extract data dynamically from authoritative sources.

```bash
# ❌ BAD: Hardcoded mapping that gets out of sync
declare -A JOB_ID_TO_NAME_MAP=(
  ["lint"]="Lint Check (Ruff)"
  ["format"]="Format Check (Black)"
)

# ✅ GOOD: Dynamic extraction from workflow file
yq eval '.jobs | to_entries | .[] | .key + "=" + .value.name' backend-ci.yml > job_mapping.txt
```

### 3. Automated Validation

**Problem:** Manual checks are error-prone and often skipped.

**Solution:** Use automated validation in PRs to catch issues before merge.

- Workflow: `.github/workflows/validate-job-mappings.yml`
- Validates all CI/CD workflows on every PR
- Fails PRs that don't follow conventions

---

## GitHub Actions Job Naming Convention

### Requirement: All Jobs Must Have Explicit Names

**Every job in a CI/CD workflow MUST have a `name:` field.**

#### Why This Matters

The bug-logger workflow dynamically extracts job mappings from workflow files at runtime. Without explicit job names, the job matching logic fails and bug reports become incomplete or incorrect.

#### Correct Format

```yaml
jobs:
  lint:                          # ← Job ID (YAML key)
    name: Lint Check (Ruff)      # ← Job Name (REQUIRED!)
    runs-on: ubuntu-22.04
    steps:
      - name: Run linting
        run: make lint
```

#### Common Mistakes

```yaml
# ❌ MISTAKE 1: Missing name field
jobs:
  lint:
    runs-on: ubuntu-22.04
    steps:
      - run: make lint

# ❌ MISTAKE 2: Empty or null name
jobs:
  lint:
    name: ""
    runs-on: ubuntu-22.04

# ❌ MISTAKE 3: Duplicate names across jobs
jobs:
  lint-backend:
    name: Lint Check    # ← Duplicate!
  lint-frontend:
    name: Lint Check    # ← Duplicate!
```

### Job Naming Best Practices

1. **Be Descriptive**: Include the tool or purpose
   - Good: `Lint Check (Ruff)`, `Test Suite (Pytest)`, `Type Check (MyPy)`
   - Bad: `Lint`, `Test`, `Check`

2. **Be Unique**: No duplicate names within a workflow
   - Each job must have a distinct name for reliable matching

3. **Be Consistent**: Follow existing patterns in the codebase
   - Review existing workflows before adding new jobs

4. **Be Explicit**: Always include `name:` field
   - Don't rely on GitHub's auto-generated names

### Validation

Run validation before committing workflow changes:

```bash
# Manual validation
yq eval '.jobs | to_entries | .[] | select(.value.name == null or .value.name == "") | .key' backend-ci.yml

# Automated validation runs on all PRs
# See: .github/workflows/validate-job-mappings.yml
```

---

## Dynamic Job Mapping Architecture

### How It Works

1. **Bug Detection**: A CI/CD job fails
2. **Log Extraction**: Bug-logger workflow is triggered
3. **Dynamic Mapping**: Workflow extracts job mapping from source workflow file
4. **Job Matching**: Uses mapping to find failed job details from GitHub API
5. **Issue Creation**: Creates GitHub issue with complete failure context

### Implementation

The bug-logger workflow uses `yq` to dynamically extract job mappings:

```bash
# Extract job ID to name mapping from workflow file
WORKFLOW_FILE=".github/workflows/backend-ci.yml"
yq eval '.jobs | to_entries | .[] | .key + "=" + .value.name' "$WORKFLOW_FILE" > job_mapping.txt

# Build associative array
declare -A JOB_ID_TO_NAME_MAP
while IFS='=' read -r JOB_ID JOB_NAME; do
  JOB_ID_TO_NAME_MAP[$JOB_ID]="$JOB_NAME"
done < job_mapping.txt

# Look up job name
FAILED_JOB_NAME="${JOB_ID_TO_NAME_MAP[$FAILED_JOB_ID]}"
```

### Benefits

- **Single Source of Truth**: Workflow file is the authoritative source
- **Zero Maintenance**: Adding/renaming jobs automatically updates mapping
- **Fail-Fast**: Missing job names cause explicit failures, not silent bugs
- **Self-Documenting**: Code clearly shows where data comes from

### Determining Source Workflow

The bug-logger must detect which workflow triggered it (backend-ci.yml vs frontend-ci.yml):

```bash
# Detect source workflow from run ID
WORKFLOW_NAME=$(gh run view ${{ inputs.run_id }} --json workflowName --jq '.workflowName')

case "$WORKFLOW_NAME" in
  "Backend CI/CD")
    WORKFLOW_FILE=".github/workflows/backend-ci.yml"
    ;;
  "Frontend CI/CD")
    WORKFLOW_FILE=".github/workflows/frontend-ci.yml"
    ;;
  *)
    echo "::error::Unknown workflow: $WORKFLOW_NAME"
    exit 1
    ;;
esac
```

---

## Error Handling Best Practices

### Explicit Validation and Failure

Every critical path should validate inputs and fail explicitly:

```bash
# 1. Validate input exists
if [ -z "$WORKFLOW_FILE" ]; then
  echo "::error::FATAL: Workflow file path not set"
  exit 1
fi

# 2. Validate file exists
if [ ! -f "$WORKFLOW_FILE" ]; then
  echo "::error::FATAL: Workflow file not found: $WORKFLOW_FILE"
  exit 1
fi

# 3. Validate extraction succeeded
if [ -z "$JOB_NAME" ] || [ "$JOB_NAME" = "null" ]; then
  echo "::error::FATAL: Could not extract job name for job ID '$JOB_ID'"
  echo "This indicates one of the following:"
  echo "  1. Job ID '$JOB_ID' does not exist in $WORKFLOW_FILE"
  echo "  2. Job is missing required 'name:' field"
  echo "  3. YAML parsing failed"
  exit 1
fi

# 4. Validate GitHub API response
if [ -z "$JOB_DATABASE_ID" ] || [ "$JOB_DATABASE_ID" = "null" ]; then
  echo "::error::FATAL: Could not find job database ID for job '$JOB_NAME'"
  echo "Available jobs in workflow run:"
  jq -r '.jobs[] | "  - \(.name) (ID: \(.databaseId))"' workflow_jobs.json
  exit 1
fi
```

### Error Message Guidelines

1. **Use ::error:: prefix**: Makes errors visible in GitHub Actions UI
2. **Explain what failed**: Don't just say "error", explain what went wrong
3. **Explain why it might have failed**: List possible root causes
4. **Provide debugging steps**: Help the reader fix the issue
5. **Show context**: Display relevant data (available jobs, expected values)

---

## Workflow Validation

### Automated Validation Workflow

File: `.github/workflows/validate-job-mappings.yml`

**Runs on:**
- Pull requests modifying CI/CD workflow files
- Pushes to main branch
- Manual dispatch

**Validates:**
- All jobs have explicit `name:` fields
- No duplicate job names within a workflow
- Job names are not empty or null

**Failure Mode:**
- Fails the PR if validation fails
- Posts comment on PR with specific issues
- Provides clear remediation steps

### Manual Validation

Before committing workflow changes:

```bash
# Check for missing job names
yq eval '.jobs | to_entries | .[] | select(.value.name == null or .value.name == "") | "Missing name: " + .key' .github/workflows/backend-ci.yml

# Check for duplicate job names
yq eval '.jobs | to_entries | .[].value.name' .github/workflows/backend-ci.yml | sort | uniq -d

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/backend-ci.yml')); print('✓ Valid YAML')"
```

---

## Docker Best Practices

### Dockerfile Requirements

1. **Multi-stage builds**: Minimize final image size
2. **Non-root user**: Run containers as non-root for security
3. **Health checks**: Include HEALTHCHECK instruction
4. **Layer optimization**: Order layers from least to most frequently changing

### Container Security

1. **Minimal base images**: Use Alpine or distroless images
2. **Vulnerability scanning**: Integrate Trivy or similar in CI/CD
3. **No secrets in images**: Use secrets managers, not environment variables
4. **SHA pinning**: Pin base image versions by digest

### Docker Compose

1. **Version control**: Always specify compose file version
2. **Environment files**: Use .env files for configuration
3. **Volume management**: Use named volumes, not bind mounts in production
4. **Resource limits**: Set memory and CPU limits

---

## Adding New Workflows

### Checklist

- [ ] **Choose descriptive workflow name**: `name: My Workflow Name`
- [ ] **Set minimal permissions**: Follow principle of least privilege
- [ ] **All jobs have explicit names**: Every job must have `name:` field
- [ ] **Job names are unique**: No duplicates within workflow
- [ ] **Job names are descriptive**: Include tool/purpose (e.g., "Lint Check (ESLint)")
- [ ] **Add timeout-minutes**: Prevent runaway jobs
- [ ] **Use concurrency control**: Prevent redundant runs
- [ ] **Implement caching**: Speed up runs (dependencies, build artifacts)
- [ ] **Add error handling**: Explicit failures with detailed messages
- [ ] **Include summary output**: Use `$GITHUB_STEP_SUMMARY`
- [ ] **Validate YAML syntax**: Run `python3 -c "import yaml; yaml.safe_load(open('file.yml'))"`
- [ ] **Test locally if possible**: Use `act` for local testing
- [ ] **Update .github/workflows/.env**: Document any required secrets

### Template

```yaml
name: My New CI/CD Workflow

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  checks: write

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  my-job:
    name: My Descriptive Job Name  # ← Required!
    runs-on: ubuntu-22.04
    timeout-minutes: 10

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run my task
        run: |
          echo "Task implementation"

      - name: Generate summary
        if: always()
        run: |
          echo "## Task Summary" >> $GITHUB_STEP_SUMMARY
          echo "✅ Task completed" >> $GITHUB_STEP_SUMMARY
```

---

## Modifying Existing Workflows

### Pre-Modification Checklist

- [ ] **Read workflow completely**: Understand all jobs and dependencies
- [ ] **Check job dependencies**: Understand `needs:` relationships
- [ ] **Review reusable workflows**: Check if workflow is called by others
- [ ] **Identify secrets usage**: Understand required secrets
- [ ] **Check for dynamic references**: Look for job IDs referenced elsewhere

### Post-Modification Checklist

- [ ] **Maintain job name fields**: Don't remove or change `name:` fields without updating callers
- [ ] **Preserve job IDs**: Changing job IDs breaks dependencies and references
- [ ] **Update job mappings**: If adding jobs, ensure they have `name:` fields
- [ ] **Validate YAML syntax**: Run syntax validation
- [ ] **Test changes**: Use feature branch and verify workflow runs
- [ ] **Update documentation**: Update `.github/workflows/.env` if secrets change

### Safe Renaming Pattern

To rename a job safely:

```yaml
# OLD (don't change job ID immediately)
jobs:
  old-job-id:
    name: New Descriptive Name  # ← Change name first
    runs-on: ubuntu-22.04

# After confirming no references exist, change job ID in separate commit:
jobs:
  new-job-id:
    name: New Descriptive Name
    runs-on: ubuntu-22.04
```

---

## Troubleshooting Guide

### Issue: Bug-logger reports "Could not find job ID"

**Symptoms:**
- Bug-logger workflow fails with "Could not find job ID for failed job 'X'"
- Bug reports are incomplete or missing

**Root Causes:**
1. Job is missing `name:` field in workflow file
2. Job ID doesn't match what's in the workflow file
3. Workflow file parsing failed

**Solution:**
```bash
# 1. Check job exists and has name field
yq eval '.jobs.YOUR_JOB_ID' .github/workflows/backend-ci.yml

# 2. Verify name field is not empty
yq eval '.jobs.YOUR_JOB_ID.name' .github/workflows/backend-ci.yml

# 3. Check for parsing errors
yq eval '.jobs' .github/workflows/backend-ci.yml
```

### Issue: Validation workflow fails on PR

**Symptoms:**
- PR check fails with "Job Mapping Validation Failed"
- Comment on PR lists missing or duplicate names

**Solution:**

1. **Missing name field:**
   ```yaml
   # Add explicit name field to job
   jobs:
     my-job:
       name: My Descriptive Job Name  # ← Add this
       runs-on: ubuntu-22.04
   ```

2. **Duplicate name:**
   ```yaml
   # Make each job name unique
   jobs:
     lint-backend:
       name: Backend Lint Check  # ← Make unique
     lint-frontend:
       name: Frontend Lint Check  # ← Make unique
   ```

### Issue: Dynamic job mapping not working

**Symptoms:**
- Bug-logger can't match failed jobs
- Falls back to using job ID instead of name

**Debugging:**
```bash
# Test yq extraction manually
yq eval '.jobs | to_entries | .[] | .key + "=" + .value.name' .github/workflows/backend-ci.yml

# Expected output:
# lint=Lint Check (Ruff)
# format=Format Check (Black)
# test=Test Suite (Pytest)

# If output is empty or has "null", jobs are missing name fields
```

---

## Related Documentation

- **Bug-Logger Architecture**: `.github/workflows/bug-logger.yml`
- **Backend CI/CD**: `.github/workflows/backend-ci.yml`
- **Frontend CI/CD**: `.github/workflows/frontend-ci.yml`
- **Validation Workflow**: `.github/workflows/validate-job-mappings.yml`
- **Secrets Documentation**: `.github/workflows/.env`
- **Docker Guidelines**: `frontend/Dockerfile`, `backend/Dockerfile` (when available)
- **Job Matching Fix History**: `.github/workflows/JOB_MATCHING_FIX.md`

---

## Quick Reference Commands

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('workflow.yml')); print('✓ Valid')"

# Check for missing job names
yq eval '.jobs | to_entries | .[] | select(.value.name == null) | .key' workflow.yml

# Check for duplicate job names
yq eval '.jobs | to_entries | .[].value.name' workflow.yml | sort | uniq -d

# Extract job mappings
yq eval '.jobs | to_entries | .[] | .key + "=" + .value.name' workflow.yml

# Test workflow locally (requires act)
act -j job-name --secret-file .env

# List all jobs in workflow
yq eval '.jobs | keys | .[]' workflow.yml

# Validate all workflows at once
for f in .github/workflows/*.yml; do
  echo "Validating $f..."
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "✓" || echo "✗ FAILED"
done
```

---

## Maintenance Schedule

- **Weekly**: Review workflow run times and optimize slow jobs
- **Monthly**: Review and rotate secrets
- **Quarterly**: Update action versions (dependabot or manual)
- **Ad-hoc**: After any workflow failures, review and improve error handling

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check workflow run logs**: GitHub Actions provides detailed logs
2. **Review related documentation**: See "Related Documentation" section
3. **Search existing issues**: Check if problem is already reported
4. **Ask for help**: Tag @devops team in PR or issue

---

**Last Updated:** 2025-10-20
**Maintained By:** DevOps Team
**Version:** 1.0.0
