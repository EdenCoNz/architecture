# Fix for Issue #160: Backend CI/CD Dependency Resolution Failure

## Overview
The backend development pipeline is completely blocked due to a Python package dependency conflict. All CI/CD jobs (tests, type checking, and linting) fail during the dependency installation phase because the package manager cannot find compatible versions of type stub packages that work together with Django 5.1+ and Django REST Framework 3.15+. This prevents any code from being tested, validated, or merged, blocking all development work on the backend API feature.

## Issue Context
- **Issue Number**: #160
- **Feature ID**: 7 (Initialize Backend API)
- **Branch**: feature/7-initialise-backend-api
- **Impact**: Complete development blockage - no code can be tested or validated
- **Root Cause**: Overly broad version constraints on django-stubs and djangorestframework-stubs packages cause pip to enter a resolution loop when trying to find compatible versions with Django 5.1+ and DRF 3.15+

---

## User Stories

### 1. Resolve Development Dependency Conflicts

As a backend developer, I want all development dependencies to install successfully so that I can run tests, type checks, and code quality tools on my local machine and in CI/CD pipelines without dependency resolution failures.

**Acceptance Criteria**:
- Given I run the dependency installation command with the development requirements file, when the installation process completes, then all packages should install successfully without version conflict errors or resolution loops
- Given the CI/CD pipeline runs any job (tests, type check, or linting), when it reaches the dependency installation step, then the installation should complete in under 2 minutes without errors
- Given I have installed all development dependencies, when I run the type checker tool, then it should execute successfully and analyze the codebase without missing stub packages or compatibility warnings

**Technical Reference**:
The issue is in backend/requirements/dev.txt at lines 18-19. The current version constraints for django-stubs and djangorestframework-stubs are too broad and incompatible with Django 5.1+ and djangorestframework 3.15+ specified in base.txt. The version ranges need to be narrowed to specific compatible versions that work with the current Django and DRF versions.

**Agent**: backend-developer
**Dependencies**: none

---

## Execution Order

### Phase 1 (Single Story)
- Story #1 (agent: backend-developer)

---

## Notes

### Story Quality Guidelines
- Generic and implementation-agnostic (no frameworks, libraries, technologies)
- User-focused (describes WHAT users need, not HOW to build it)
- Atomic (1-3 days max, independently deployable)
- Testable (acceptance criteria are user-observable behaviors)

### Technical Context for Implementation
This fix requires updating the version constraints in backend/requirements/dev.txt to use compatible versions of the type stub packages. The acceptance criteria focus on observable outcomes (successful installation, fast completion, working tools) rather than prescribing specific version numbers, allowing the backend-developer agent to research and select the appropriate compatible versions.
