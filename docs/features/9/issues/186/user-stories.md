# Fix User Stories: Issue #186 - Docker Tag Mismatch in Frontend CI/CD Verification

## Issue Context

**Issue Number**: #186
**Issue Title**: Workflow Run #193 Failed: Frontend CI/CD (0 failure(s))
**Feature ID**: 9
**Branch**: feature/9-docker-cicd-validation

**Problem Summary**: The Frontend CI/CD workflow builds Docker images with environment-specific tags (staging- for feature branches, prod- for main branch) but the image verification step hardcodes a prod- prefix when attempting to inspect the published image. This causes verification to fail on feature branches even though the images were successfully built and published with correct staging- tags.

**Root Cause**: The workflow has two metadata generation steps with different tagging strategies, and the verification step references the wrong tag variable, causing a mismatch between what was published and what is being verified.

---

## Story 186.1: Align Image Verification with Environment-Based Tagging

**Story ID**: Story-186.1
**Assigned Agent**: devops-engineer
**Execution Phase**: 1 (Sequential)

### Description

As a DevOps engineer, I need the CI/CD pipeline verification step to use the correct environment-based image tags so that the workflow can successfully verify published images regardless of whether they were built from feature branches or main branch.

The current implementation publishes images with environment-aware tags (staging- prefix for feature branches, prod- prefix for main branch) but attempts to verify using a hardcoded prod- prefix. This causes verification failures on feature branches even when images are successfully published.

**Business Context**: The verification step is critical for ensuring that published container images are accessible in the registry and contain all expected platform architectures. When verification fails due to tag mismatches, it blocks the CI/CD pipeline from completing successfully, preventing valid deployments from being validated and creating false negatives in the build status.

**Technical Reference**:
- The publish metadata step (around line 737 in frontend-ci.yml) correctly generates environment-based tags stored in `steps.meta.outputs.env_prefix`
- The verification step (line 831) hardcodes `prod-` instead of using the dynamic `env_prefix` output
- Error logs show image published as `staging-f6521ff` but verification attempts to inspect `prod-f6521ff`

### Acceptance Criteria

**AC1**: Environment-Aware Tag Selection
- Given the workflow is running on a feature branch
- When the verification step inspects the published image
- Then it should use the staging- prefixed tag that matches the published image tag
- And the verification should complete successfully

**AC2**: Main Branch Verification
- Given the workflow is running on the main branch
- When the verification step inspects the published image
- Then it should use the prod- prefixed tag that matches the published image tag
- And the verification should complete successfully

**AC3**: Tag Variable Consistency
- Given the publish step generates environment-based tags
- When the verification step constructs the image reference
- Then it should use the same env_prefix output variable that was used during publishing
- And the tag format should exactly match between publish and verification steps

**AC4**: Verification Success Confirmation
- Given the verification step successfully locates the published image
- When it inspects the image manifest
- Then it should display manifest details including all platform architectures
- And the workflow should mark the verification step as passed

### Dependencies

- Requires publish metadata step outputs to be accessible to verification step
- Verification step must run after image publication completes

### Implementation Notes

The verification step should reference `${{ steps.meta.outputs.env_prefix }}` instead of hardcoding "prod-" to construct the PRIMARY_TAG variable. This ensures the verification uses the same environment-based prefix that was applied during image publication.

---

## Execution Plan

### Phase 1: Sequential Execution
- **Story-186.1** (devops-engineer): Fix tag mismatch in verification step

**Total Stories**: 1
**Estimated Effort**: 1-2 days

---

## Summary

This issue involves a single atomic fix to align the image verification logic with the environment-based tagging strategy already implemented in the publish step. By using the correct tag prefix variable, the verification step will successfully locate and inspect published images regardless of the branch environment.

**Story Breakdown Rationale**: This is a single, focused issue affecting one specific workflow step. The fix involves updating a single variable reference to use the environment-based prefix instead of a hardcoded value. It does not require multiple stories as it addresses one root cause with one solution.
