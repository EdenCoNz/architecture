# Issue #187: Backend Production Container Health Endpoint Test Failure

## Issue Overview

**Issue Number**: #187
**Issue Title**: Workflow Run #64 Failed: Backend CI/CD (0 failure(s))
**Feature ID**: 9
**Branch**: feature/9-docker-cicd-validation
**Created**: 2025-10-25

## Problem Summary

The backend production container functional testing job is failing during the API health endpoint verification step. The container starts successfully, database connectivity is confirmed, and the Docker health check mechanism is configured correctly, but when the CI/CD workflow tests the health endpoint via curl, it receives a non-200 HTTP response code.

### Business Impact

- CI/CD pipeline is blocked, preventing code from being merged
- Production container cannot be verified as deployment-ready
- Development velocity is impacted as features cannot progress through the pipeline
- Confidence in containerized deployment artifacts is reduced

### Root Cause Analysis

The failure occurs due to a timing issue in the test workflow:

1. Container starts and begins initialization (entrypoint runs migrations, collectstatic, etc.)
2. Workflow waits for Docker's built-in health check to pass
3. However, the API health endpoint test runs immediately after the Docker health check passes
4. There may be a brief window where the Docker health check passes but the Gunicorn server is not yet fully bound to port 8000
5. The curl request arrives during this window and fails

Alternative possibilities:
- URL path mismatch (unlikely, as code shows `/api/v1/health/` exists)
- ALLOWED_HOSTS rejection (unlikely, as localhost is configured)
- Application crash between health check and test (would show in subsequent tests)

---

## User Stories

### Story 187.1: Improve API Health Endpoint Test Reliability

**Title**: Improve API Health Endpoint Test Reliability
**Assigned Agent**: devops-engineer
**Story Points**: 2
**Priority**: High

**Description**:
As a DevOps engineer, I want the CI/CD pipeline to reliably verify the backend production container's health endpoint, so that I can confidently determine when the container is ready to serve traffic and avoid false failures due to timing issues.

**Acceptance Criteria**:
- Given the production container starts, when the health endpoint test runs, then it should implement retry logic to handle brief unavailability windows
- Given the API takes time to become ready, when the test executes, then it should wait for a successful response within a reasonable timeout period (30-60 seconds)
- Given the health endpoint returns non-200 status codes, when retrying, then the test should log each attempt's HTTP status code for debugging
- Given the test exhausts all retries without success, when it fails, then it should display the final HTTP status code, response body, and container logs to aid troubleshooting
- Given the health endpoint responds with HTTP 200, when the test succeeds, then it should report the successful status code and response time

**Dependencies**: None

**Notes**:
- Implement retry logic similar to the Docker health check verification step (which already uses retries)
- Consider using a progressive backoff strategy: check immediately, then every 3 seconds
- Maximum retry period should align with Docker health check start-period (60 seconds)
- This improves test reliability without changing application code
- Should follow the same pattern as "Verify container health" step which successfully waits for Docker health checks

**Technical Context** (for implementation):
The test currently runs a single curl command at line 894 of backend-ci.yml:
```bash
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/health/ || echo "000")
```

This needs to be wrapped in a retry loop similar to lines 830-852 which successfully wait for Docker health checks to pass.

---

## Execution Order

### Phase 1 (Sequential - Test Reliability Fix)
- Story 187.1: Improve API Health Endpoint Test Reliability

---

## Story Quality Validation

### Atomicity Compliance
- All stories deliver one complete user-facing capability
- Single story addresses the specific failure point
- Estimated at 2 story points (1-2 days completion time)
- No compound requirements - focused solely on test reliability

### Generic Compliance
- No specific testing tools mandated (can use curl, wget, or other HTTP clients)
- No specific retry mechanism prescribed (can implement various backoff strategies)
- Focus on WHAT needs to be achieved (reliable health check verification)
- Not HOW to implement it (implementation details left to agent)
- Works with any container orchestration or CI/CD platform

### User-Focused
- Written from DevOps engineer perspective (the user of CI/CD pipelines)
- Uses "As a... I want... So that..." format
- Acceptance criteria use "Given... When... Then..." patterns
- Describes observable outcomes (test passes reliably, logs show status)
- Focus on user problem: avoiding false failures and gaining confidence

---

## Summary

**Total Stories**: 1
**Total Story Points**: 2
**Assigned Agents**:
- devops-engineer: 1 story

**Fix Strategy**:
This is a test infrastructure issue, not an application code issue. The backend application and health endpoint are working correctly - the problem is that the CI/CD test doesn't wait long enough for the API to be ready. By adding retry logic with appropriate timeout, we ensure the test accurately reflects whether the container is healthy, eliminating false failures from timing race conditions.

**Success Criteria**:
- Health endpoint test passes consistently when container is healthy
- Test provides clear diagnostic information when actual failures occur
- No false failures due to timing issues
- CI/CD pipeline can reliably validate production containers

**Validation Approach**:
After implementation, verify by:
1. Running the CI/CD pipeline multiple times to confirm consistent passing
2. Checking that the test logs show retry attempts when needed
3. Confirming the test completes within expected time bounds
4. Verifying container logs are captured when genuine failures occur
