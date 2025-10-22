# CI/CD Workflow Pattern Standard

This document defines the standard pattern that all CI/CD workflows in this repository must follow. It ensures consistency, maintainability, and proper integration with our automated issue tracking and workflow monitoring systems.

## Table of Contents

- [Overview](#overview)
- [Standard Workflow Structure](#standard-workflow-structure)
- [Required Jobs](#required-jobs)
- [Downstream Workflow Integration](#downstream-workflow-integration)
- [Permissions](#permissions)
- [Conditions and Filters](#conditions-and-filters)
- [Template for New Workflows](#template-for-new-workflows)
- [Examples](#examples)

## Overview

All CI/CD workflows in this repository follow a consistent pattern that includes:

1. **Core Pipeline Jobs**: Technology-specific validation, testing, and building
2. **Deployment Readiness**: Verification that code is ready for production
3. **Commit Message Extraction**: Capturing commit metadata for downstream workflows
4. **Auto-Close Issue Integration**: Automatically closing GitHub issues when fixes pass all checks
5. **Workflow Failure Detection**: Inline failure reporting and external workflow monitoring

This pattern enables:
- Automatic issue closure when fixes are validated
- Comprehensive failure detection and reporting
- Consistent behavior across all pipelines
- Easy addition of new pipelines (mobile, infrastructure, etc.)

## Standard Workflow Structure

All CI/CD workflows must follow this job sequence:

```yaml
jobs:
  # ===================================================================
  # SECTION 1: Core Pipeline Jobs (Technology-Specific)
  # ===================================================================
  # Jobs 1-N: Validation, testing, security, and building
  # Examples: lint, typecheck, test, security, build

  # ===================================================================
  # SECTION 2: Deployment Readiness (Production Pipelines Only)
  # ===================================================================
  # Optional: deployment-check job (only for main branch pushes)

  # ===================================================================
  # SECTION 3: Commit Message Extraction
  # ===================================================================
  # REQUIRED: get-commit-message job

  # ===================================================================
  # SECTION 4: Auto-Close Issue Integration
  # ===================================================================
  # REQUIRED: auto-close-issue job (calls reusable workflow)

  # ===================================================================
  # SECTION 5: Inline Failure Detection
  # ===================================================================
  # REQUIRED: detect-workflow-failures job
```

## Required Jobs

### 1. Core Pipeline Jobs

These jobs are technology-specific and include validation, testing, security checks, and building. The exact jobs depend on the technology stack:

**Frontend (Node.js/TypeScript)**:
- `lint`: ESLint and Prettier checks
- `typecheck`: TypeScript type checking
- `test`: Unit tests with coverage
- `build`: Production build
- `security`: npm audit

**Backend (Python/Django)**:
- `lint`: Black, isort, Flake8 checks
- `typecheck`: mypy type checking
- `test`: pytest with coverage (includes service containers)
- `security`: Safety and Bandit scans
- `build`: Django build verification (collectstatic, check --deploy)

**Common Requirements**:
- Run conditionally: `if: github.event_name != 'pull_request' || startsWith(github.head_ref, 'feature/')`
- Set timeouts: `timeout-minutes: 10-15`
- Use appropriate runners: `runs-on: ubuntu-22.04`
- Generate job summaries: Use `$GITHUB_STEP_SUMMARY`
- Upload artifacts: Coverage reports, test results, security scans

### 2. Deployment Readiness Check (Optional)

**Job Name**: `deployment-check`

**Purpose**: Verify all checks passed and artifacts are production-ready

**Condition**: Only run on main branch pushes
```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

**Dependencies**: All core pipeline jobs
```yaml
needs: [lint, typecheck, test, security, build]
```

**Example**:
```yaml
deployment-check:
  name: Deployment Readiness Check
  runs-on: ubuntu-22.04
  timeout-minutes: 5
  needs: [lint, typecheck, test, security, build]
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'

  steps:
    - name: Verify deployment readiness
      run: |
        echo "## Deployment Readiness" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "✅ All checks passed" >> $GITHUB_STEP_SUMMARY
        echo "🚀 Ready for deployment to production" >> $GITHUB_STEP_SUMMARY
```

### 3. Get Commit Message (REQUIRED)

**Job Name**: `get-commit-message`

**Purpose**: Extract commit message and SHA for downstream workflows (especially auto-close-issue)

**Condition**: Run on pushes to main/feature branches OR pull requests
```yaml
if: |
  (github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/feature/'))) ||
  github.event_name == 'pull_request'
```

**Outputs**:
- `commit-message`: Full commit message
- `commit-sha`: Commit SHA

**Template**:
```yaml
get-commit-message:
  runs-on: ubuntu-latest
  if: |
    (github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/feature/'))) ||
    github.event_name == 'pull_request'
  outputs:
    commit-message: ${{ steps.get-message.outputs.message }}
    commit-sha: ${{ steps.get-message.outputs.sha }}
  steps:
    - name: Get commit message
      id: get-message
      env:
        GH_TOKEN: ${{ github.token }}
      run: |
        if [ "${{ github.event_name }}" = "pull_request" ]; then
          # For PR events, fetch the latest commit message
          SHA="${{ github.event.pull_request.head.sha }}"
          MESSAGE=$(gh api repos/${{ github.repository }}/commits/${SHA} --jq '.commit.message')
          echo "sha=${SHA}" >> $GITHUB_OUTPUT
          echo "message<<EOF" >> $GITHUB_OUTPUT
          echo "${MESSAGE}" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
        else
          # For push events, use the head commit
          echo "sha=${{ github.sha }}" >> $GITHUB_OUTPUT
          echo "message<<EOF" >> $GITHUB_OUTPUT
          echo "${{ github.event.head_commit.message }}" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
        fi
```

### 4. Auto-Close Issue (REQUIRED)

**Job Name**: `auto-close-issue`

**Purpose**: Automatically close GitHub issues when a commit with "Fix issue #N" passes all checks

**Dependencies**:
- All core pipeline jobs (to ensure everything passed)
- `get-commit-message` job (to get commit metadata)

**Condition**: Same as get-commit-message
```yaml
if: |
  (github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/feature/'))) ||
  github.event_name == 'pull_request'
```

**Permissions**:
```yaml
permissions:
  issues: write
  contents: read
  pull-requests: write
```

**Template**:
```yaml
auto-close-issue:
  needs: [lint, typecheck, test, security, build, get-commit-message]
  if: |
    (github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/feature/'))) ||
    github.event_name == 'pull_request'
  uses: ./.github/workflows/auto-close-issue.yml
  with:
    commit-message: ${{ needs.get-commit-message.outputs.commit-message }}
    repository: ${{ github.repository }}
    sha: ${{ needs.get-commit-message.outputs.commit-sha }}
    workflow-name: 'REPLACE_WITH_WORKFLOW_NAME'  # e.g., 'Frontend CI/CD', 'Backend CI/CD'
  permissions:
    issues: write
    contents: read
    pull-requests: write
```

**Important Notes**:
- **Must depend on ALL core pipeline jobs** to ensure they all pass before closing issues
- Update the `needs` array to include all your core pipeline jobs
- Replace `workflow-name` with your actual workflow name (e.g., 'Mobile CI/CD', 'Infrastructure CI/CD')

### 5. Detect Workflow Failures (REQUIRED)

**Job Name**: `detect-workflow-failures`

**Purpose**: Provide inline failure reporting in the workflow summary

**Condition**: Only run on failure or cancellation
```yaml
if: failure() || cancelled()
```

**Template**:
```yaml
detect-workflow-failures:
  name: Detect Workflow Failures
  runs-on: ubuntu-22.04
  timeout-minutes: 5
  if: failure() || cancelled()

  steps:
    - name: Report workflow failure
      run: |
        echo "## Workflow Issue Detected" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY

        if [ "${{ job.status }}" == "cancelled" ]; then
          echo "⚠️ Workflow was cancelled." >> $GITHUB_STEP_SUMMARY
        else
          echo "❌ One or more jobs in this workflow have failed." >> $GITHUB_STEP_SUMMARY
        fi

        echo "" >> $GITHUB_STEP_SUMMARY
        echo "Please check the job logs above for details." >> $GITHUB_STEP_SUMMARY
```

**Note**: This job provides immediate feedback. The external `detect-workflow-failures.yml` workflow provides more detailed analysis and triggers issue creation.

## Downstream Workflow Integration

### External Workflow: detect-workflow-failures.yml

This workflow runs **after** your CI/CD workflow completes and provides:
- Detailed failure analysis
- Failed job and step identification
- Automatic issue creation from failures

**How it works**:
1. Monitors all workflows listed in its `workflow_run.workflows` trigger
2. Runs only when those workflows have failures or are cancelled
3. Analyzes all failed jobs and steps
4. Creates issue log files for each failure
5. Triggers independent issue creation workflows

**Adding Your Workflow to Monitoring**:

To enable automatic failure detection for your new workflow, add it to the `workflows` array in `.github/workflows/detect-workflow-failures.yml`:

```yaml
on:
  workflow_run:
    workflows: ["Frontend CI/CD", "Backend CI/CD", "YOUR_WORKFLOW_NAME"]
    types: [completed]
```

**Current Monitored Workflows**:
- Frontend CI/CD
- Backend CI/CD

## Permissions

### Workflow-Level Permissions

All CI/CD workflows must use **least privilege** permissions:

```yaml
permissions:
  contents: read        # Read repository contents
  pull-requests: write  # Comment on PRs (coverage reports, etc.)
  checks: write         # Create check runs
  issues: write         # Required for auto-close-issue integration
```

**Backend-specific** (if using security scanning):
```yaml
permissions:
  contents: read
  pull-requests: write
  checks: write
  issues: write
  security-events: write  # For uploading security scan results
```

### Job-Level Permissions

The `auto-close-issue` job requires specific permissions:
```yaml
permissions:
  issues: write
  contents: read
  pull-requests: write
```

## Conditions and Filters

### Feature Branch Filter

All core pipeline jobs should use this condition to run only on feature branches (for PRs) or always (for pushes/manual triggers):

```yaml
if: github.event_name != 'pull_request' || startsWith(github.head_ref, 'feature/')
```

**Why?**: This prevents workflows from running on non-feature PRs while still allowing manual triggers and direct pushes.

### Path Filters

Use path filters to trigger workflows only when relevant files change:

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci.yml'
  pull_request:
    branches: [main]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci.yml'
```

**Pattern**:
- Include the component directory (e.g., `frontend/**`, `backend/**`, `mobile/**`)
- Include the workflow file itself (e.g., `.github/workflows/frontend-ci.yml`)

### Concurrency

Prevent concurrent runs for the same branch/PR:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Template for New Workflows

Use this template when creating a new CI/CD workflow:

```yaml
name: YOUR_COMPONENT CI/CD

# Trigger on pull requests from feature branches and pushes to main branch
on:
  push:
    branches: [main]
    paths:
      - 'YOUR_COMPONENT/**'
      - '.github/workflows/YOUR_COMPONENT-ci.yml'
  pull_request:
    branches: [main]
    paths:
      - 'YOUR_COMPONENT/**'
      - '.github/workflows/YOUR_COMPONENT-ci.yml'
  workflow_dispatch:  # Allow manual triggering

# Explicit permissions (least privilege)
permissions:
  contents: read
  pull-requests: write
  checks: write
  issues: write

# Prevent concurrent runs for same branch/PR
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # ===================================================================
  # SECTION 1: Core Pipeline Jobs (Technology-Specific)
  # ===================================================================

  # Job 1: Lint and Format Check
  lint:
    name: Lint and Format Check
    runs-on: ubuntu-22.04
    timeout-minutes: 10
    if: github.event_name != 'pull_request' || startsWith(github.head_ref, 'feature/')

    defaults:
      run:
        working-directory: ./YOUR_COMPONENT

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Add your technology-specific lint steps here
      # Examples: ESLint, Prettier, Black, isort, Flake8, etc.

  # Job 2: Type Check
  typecheck:
    name: Type Check
    runs-on: ubuntu-22.04
    timeout-minutes: 10
    if: github.event_name != 'pull_request' || startsWith(github.head_ref, 'feature/')

    defaults:
      run:
        working-directory: ./YOUR_COMPONENT

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Add your technology-specific type checking steps here
      # Examples: tsc, mypy, etc.

  # Job 3: Tests with Coverage
  test:
    name: Tests with Coverage
    runs-on: ubuntu-22.04
    timeout-minutes: 15
    if: github.event_name != 'pull_request' || startsWith(github.head_ref, 'feature/')

    defaults:
      run:
        working-directory: ./YOUR_COMPONENT

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Add your technology-specific test steps here
      # Examples: npm test, pytest, etc.

      - name: Upload coverage reports
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report-${{ github.sha }}
          path: YOUR_COMPONENT/coverage/
          retention-days: 30
          if-no-files-found: error

  # Job 4: Security Audit
  security:
    name: Security Audit
    runs-on: ubuntu-22.04
    timeout-minutes: 10
    if: github.event_name != 'pull_request' || startsWith(github.head_ref, 'feature/')

    defaults:
      run:
        working-directory: ./YOUR_COMPONENT

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Add your technology-specific security scanning steps here
      # Examples: npm audit, safety, bandit, etc.

  # Job 5: Build
  build:
    name: Build Application
    runs-on: ubuntu-22.04
    timeout-minutes: 15
    needs: [lint, typecheck, test, security]
    if: github.event_name != 'pull_request' || startsWith(github.head_ref, 'feature/')

    defaults:
      run:
        working-directory: ./YOUR_COMPONENT

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Add your technology-specific build steps here
      # Examples: npm run build, python manage.py collectstatic, etc.

  # ===================================================================
  # SECTION 2: Deployment Readiness (Production Pipelines Only)
  # ===================================================================

  deployment-check:
    name: Deployment Readiness Check
    runs-on: ubuntu-22.04
    timeout-minutes: 5
    needs: [lint, typecheck, test, security, build]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - name: Verify deployment readiness
        run: |
          echo "## Deployment Readiness" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "✅ All checks passed" >> $GITHUB_STEP_SUMMARY
          echo "🚀 Ready for deployment to production" >> $GITHUB_STEP_SUMMARY

  # ===================================================================
  # SECTION 3: Commit Message Extraction
  # ===================================================================

  get-commit-message:
    runs-on: ubuntu-latest
    if: |
      (github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/feature/'))) ||
      github.event_name == 'pull_request'
    outputs:
      commit-message: ${{ steps.get-message.outputs.message }}
      commit-sha: ${{ steps.get-message.outputs.sha }}
    steps:
      - name: Get commit message
        id: get-message
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            # For PR events, fetch the latest commit message
            SHA="${{ github.event.pull_request.head.sha }}"
            MESSAGE=$(gh api repos/${{ github.repository }}/commits/${SHA} --jq '.commit.message')
            echo "sha=${SHA}" >> $GITHUB_OUTPUT
            echo "message<<EOF" >> $GITHUB_OUTPUT
            echo "${MESSAGE}" >> $GITHUB_OUTPUT
            echo "EOF" >> $GITHUB_OUTPUT
          else
            # For push events, use the head commit
            echo "sha=${{ github.sha }}" >> $GITHUB_OUTPUT
            echo "message<<EOF" >> $GITHUB_OUTPUT
            echo "${{ github.event.head_commit.message }}" >> $GITHUB_OUTPUT
            echo "EOF" >> $GITHUB_OUTPUT
          fi

  # ===================================================================
  # SECTION 4: Auto-Close Issue Integration
  # ===================================================================

  auto-close-issue:
    needs: [lint, typecheck, test, security, build, get-commit-message]
    if: |
      (github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/feature/'))) ||
      github.event_name == 'pull_request'
    uses: ./.github/workflows/auto-close-issue.yml
    with:
      commit-message: ${{ needs.get-commit-message.outputs.commit-message }}
      repository: ${{ github.repository }}
      sha: ${{ needs.get-commit-message.outputs.commit-sha }}
      workflow-name: 'YOUR_COMPONENT CI/CD'
    permissions:
      issues: write
      contents: read
      pull-requests: write

  # ===================================================================
  # SECTION 5: Inline Failure Detection
  # ===================================================================

  detect-workflow-failures:
    name: Detect Workflow Failures
    runs-on: ubuntu-22.04
    timeout-minutes: 5
    if: failure() || cancelled()

    steps:
      - name: Report workflow failure
        run: |
          echo "## Workflow Issue Detected" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY

          if [ "${{ job.status }}" == "cancelled" ]; then
            echo "⚠️ Workflow was cancelled." >> $GITHUB_STEP_SUMMARY
          else
            echo "❌ One or more jobs in this workflow have failed." >> $GITHUB_STEP_SUMMARY
          fi

          echo "" >> $GITHUB_STEP_SUMMARY
          echo "Please check the job logs above for details." >> $GITHUB_STEP_SUMMARY
```

### Checklist for New Workflows

After creating a new workflow, complete these steps:

- [ ] Replace all `YOUR_COMPONENT` placeholders with actual component name
- [ ] Update `workflow-name` in auto-close-issue job
- [ ] Update path filters in trigger section
- [ ] Implement technology-specific steps (lint, typecheck, test, security, build)
- [ ] Update `needs` array in `auto-close-issue` job to include all core pipeline jobs
- [ ] Add workflow to `.github/workflows/detect-workflow-failures.yml` monitoring list
- [ ] Validate YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/YOUR_WORKFLOW.yml')); print('✓ YAML valid')"`
- [ ] Test with a feature branch PR
- [ ] Verify auto-close-issue integration works
- [ ] Verify failure detection works

## Examples

### Frontend CI/CD Workflow

Location: `.github/workflows/frontend-ci.yml`

**Core Jobs**:
1. `lint`: ESLint and Prettier
2. `typecheck`: TypeScript type checking
3. `test`: Jest with coverage
4. `build`: Vite production build
5. `security`: npm audit

**Integration Jobs**:
- `deployment-check`: Verify production readiness
- `get-commit-message`: Extract commit metadata
- `auto-close-issue`: Close issues on successful fixes
- `detect-workflow-failures`: Inline failure reporting

### Backend CI/CD Workflow

Location: `.github/workflows/backend-ci.yml`

**Core Jobs**:
1. `lint`: Black, isort, Flake8
2. `typecheck`: mypy type checking
3. `test`: pytest with coverage (PostgreSQL + Redis services)
4. `security`: Safety and Bandit scans
5. `build`: Django build verification

**Integration Jobs**:
- `deployment-check`: Verify production readiness
- `get-commit-message`: Extract commit metadata
- `auto-close-issue`: Close issues on successful fixes
- `detect-workflow-failures`: Inline failure reporting

## Key Principles

1. **Consistency**: All workflows follow the same structure and integration pattern
2. **Modularity**: Core pipeline jobs are technology-specific; integration jobs are standardized
3. **Reusability**: Common functionality (auto-close-issue) is extracted into reusable workflows
4. **Observability**: Rich summaries, artifact uploads, and failure detection
5. **Security**: Least privilege permissions, explicit permission grants
6. **Reliability**: Timeouts, concurrency control, proper conditions

## Future Enhancements

When adding new components (mobile, infrastructure, etc.):

1. Copy the template from this document
2. Customize the core pipeline jobs for your technology
3. Keep the integration jobs (get-commit-message, auto-close-issue, detect-workflow-failures) identical
4. Add your workflow to the detect-workflow-failures.yml monitoring list
5. Update this documentation with your workflow as an example

## Troubleshooting

### Auto-Close Issue Not Working

**Symptoms**: Issues are not being closed even though all jobs pass

**Checklist**:
- [ ] Verify commit message contains "Fix issue #N" pattern (case-insensitive)
- [ ] Check that `auto-close-issue` job has `needs` dependencies on ALL core pipeline jobs
- [ ] Verify workflow has `issues: write` permission
- [ ] Check that the issue exists and is open
- [ ] Review `auto-close-issue` job logs for errors

### Failure Detection Not Triggering

**Symptoms**: detect-workflow-failures.yml not running after failures

**Checklist**:
- [ ] Verify your workflow name is listed in detect-workflow-failures.yml `workflows` array
- [ ] Check that the workflow actually failed (not just skipped jobs)
- [ ] Verify detect-workflow-failures.yml has correct permissions
- [ ] Review GitHub Actions logs for the monitor workflow

### Jobs Not Running on PRs

**Symptoms**: Jobs skip on pull requests

**Checklist**:
- [ ] Verify PR is from a feature branch (branch name starts with `feature/`)
- [ ] Check path filters match changed files
- [ ] Review job conditions: `if: github.event_name != 'pull_request' || startsWith(github.head_ref, 'feature/')`

## Additional Resources

- [Frontend CI/CD Workflow](.github/workflows/frontend-ci.yml)
- [Backend CI/CD Workflow](.github/workflows/backend-ci.yml)
- [Auto-Close Issue Reusable Workflow](.github/workflows/auto-close-issue.yml)
- [Detect Workflow Failures Workflow](.github/workflows/detect-workflow-failures.yml)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows Documentation](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
