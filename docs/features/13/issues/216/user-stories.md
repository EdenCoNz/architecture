# Fix User Stories - Issue #216: CI/CD Pipeline Failed - Missing Frontend Test Script

**Feature ID**: 13
**Issue Number**: 216
**Branch**: feature/13-end-to-end-testing
**Created**: 2025-10-26

## Issue Summary

The CI/CD pipeline is failing because it's attempting to run a frontend test script (`npm run test:unit`) that doesn't exist in the frontend's package.json file. The available test scripts are `test:ui` and `test:run`, but the workflow is configured to use a different script name.

## User Stories

### Story-216.1: Align CI/CD Test Script with Frontend Configuration

**Priority**: Critical
**Assigned Agent**: devops-engineer
**Estimated Effort**: 1 day

**As a** developer
**I want** the CI/CD pipeline to execute frontend tests using the correct test script
**So that** automated testing can run successfully and code quality checks pass

**Description**:
The CI/CD workflow is configured to run frontend unit tests using `npm run test:unit`, but this script doesn't exist in the frontend application's package.json file. The frontend uses `test:run` for running tests in CI mode (non-interactive). The workflow configuration needs to be updated to use the correct script name that actually exists in the frontend project.

**Acceptance Criteria**:
- Given the CI/CD workflow executes the frontend testing step, when it runs the test command, then it should use `npm run test:run` instead of `npm run test:unit`
- Given the workflow file is updated, when I review the frontend testing configuration in `.github/workflows/unified-ci-cd.yml`, then the test command should match a script that exists in `frontend/package.json`
- Given the workflow runs with the corrected script name, when frontend tests execute in the pipeline, then they should complete successfully without "Missing script" errors
- Given the fix is applied, when I commit changes and push to the branch, then the CI/CD pipeline should progress past the frontend testing step

**Technical Context**:
The workflow file `.github/workflows/unified-ci-cd.yml` at line 198 contains:
```bash
docker compose run --rm frontend npm run test:unit
```

This should be changed to use `test:run` which exists in the frontend/package.json file and is designed for CI/CD execution (runs tests once and exits, unlike `test:ui` which launches an interactive UI).

**Definition of Done**:
- [ ] Workflow file updated to use correct test script name
- [ ] CI/CD pipeline successfully executes frontend tests
- [ ] No "Missing script" errors in pipeline logs
- [ ] Change is committed and pushed to the feature branch

---

## Execution Order

### Sequential Execution

**Phase 1: Fix Workflow Configuration**
- Story-216.1 (devops-engineer) - Update CI/CD workflow to use correct test script

---

## Story Summary

- **Total Stories**: 1
- **Assigned Agents**:
  - devops-engineer: 1 story
- **Execution Phases**: 1
- **Sequential Phases**: 1
- **Parallel Phases**: 0

---

## Atomicity & Quality Validation

### Atomicity Compliance
- Story delivers ONE complete capability (fix CI/CD test script mismatch)
- Can be completed in less than 1 day
- Has exactly 4 acceptance criteria
- Title is clear and singular

### Generic & Implementation-Agnostic Compliance
- Story focuses on WHAT needs to be fixed (script name alignment)
- Describes the user-observable outcome (tests run successfully)
- Uses domain language appropriate for CI/CD
- Technical context provided separately for implementer reference

### User-Focused Validation
- Written from developer perspective (CI/CD user)
- Explains WHY the fix is needed (enable automated testing)
- Acceptance criteria describe observable outcomes
- Clear success conditions defined

---

## Notes

This is a simple configuration mismatch issue that requires a one-line change to the CI/CD workflow file. The frontend application uses Vitest as its testing framework, which provides multiple test execution modes:
- `test:ui` - Interactive UI mode (not suitable for CI/CD)
- `test:run` - Single run mode (suitable for CI/CD)
- `test:coverage` - Run with coverage reporting

The workflow should use `test:run` for standard CI/CD test execution.
