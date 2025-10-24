# Issue #189: Fix Docker Tag Generation for Feature Branches

## Overview
The CI/CD pipeline must generate valid Docker image tags regardless of branch naming conventions. Currently, feature branches with forward slashes in their names (e.g., `feature/9-docker-cicd-validation`) cause the container build and publish process to fail because Docker tags cannot contain forward slash characters. This prevents production containers from being built and published to the container registry, completely blocking the deployment pipeline for feature branches.

---

## User Stories

### 1. Valid Docker Tags for All Branch Names
As a developer working on a feature branch, I want the CI/CD pipeline to successfully build and publish container images regardless of my branch name, so that I can validate my containerized deployments in the automated pipeline without manual tag formatting.

**Acceptance Criteria**:
- Given I push code to a feature branch with slashes in the name (e.g., `feature/123-my-feature`), when the CI/CD pipeline runs, then Docker images should be built and tagged successfully
- Given the pipeline generates Docker tags, when the branch name contains special characters (slashes, underscores, dots), then the generated tags should only contain alphanumeric characters, hyphens, underscores, and dots
- Given the container build step completes, when I view the container registry, then I should see images tagged with sanitized branch names that are valid Docker tag formats
- Given multiple developers use different branch naming conventions, when their pipelines run, then all container builds should succeed with valid, deterministic tag names

**Agent**: devops-engineer
**Dependencies**: none

**Technical Reference**:
The current workflow generates tags like `prod-${BRANCH_NAME}` which creates invalid tags such as `prod-feature/9-docker-cicd-validation`. Docker tag format requirements: tags can only contain lowercase and uppercase letters, digits, underscores, periods, and hyphens (`[a-zA-Z0-9_.-]`). The tag portion cannot contain forward slashes.

Example problematic command from logs:
```
--tag ghcr.io/edenconz/backend:prod-feature/9-docker-cicd-validation
```

This should be transformed to a valid format such as:
```
--tag ghcr.io/edenconz/backend:prod-feature-9-docker-cicd-validation
```

Common transformation approach: Replace forward slashes with hyphens or underscores in branch names when generating Docker tags.

---

## Execution Order

### Phase 1 (Sequential)
- Story #1 (agent: devops-engineer) - Fix Docker tag generation in CI/CD workflows for both frontend and backend pipelines

---

## Notes

### Story Quality Validation
- Implementation-agnostic: Story does not specify how to sanitize tags (sed, bash parameter expansion, GitHub Actions expressions, etc.)
- User-focused: Describes what developers need (successful builds regardless of branch names) not implementation details
- Atomic: Single focused change to tag generation logic, estimated 1-2 hours
- Testable: Can be verified by pushing to a feature branch with slashes and confirming successful container builds

### Root Cause
The CI/CD workflow embeds branch names directly into Docker tags without sanitization, violating Docker's tag naming constraints when branches contain forward slashes.
