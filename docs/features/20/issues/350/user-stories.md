# Issue #350: CI/CD Pipeline Failed - Deploy to Staging - Run #139

## Issue Summary
**Feature**: 20 - Basic Login Functionality
**Branch**: feature/20-basic-login
**Failure**: Deploy to Staging - HTTP Health Check
**Created**: 2025-11-02

### Problem Description
The staging deployment pipeline completes successfully (containers start and pass Docker health checks), but the HTTP health check fails to receive a "healthy" response from the backend API status endpoint after multiple retry attempts. The workflow verification step makes HTTP requests to `http://${SERVER_HOST}/api/v1/status/` but does not receive the expected healthy status response, causing the pipeline to fail and blocking E2E testing and production deployment.

### Root Cause Analysis
**Container Health vs HTTP Health**:
- Docker health checks pass (containers report as healthy)
- HTTP endpoint verification fails (no healthy response received)
- Issue occurs at the HTTP layer, not the container layer

**Potential Causes**:
1. Nginx routing misconfiguration preventing requests from reaching backend
2. Backend application not fully initialized despite Docker health check passing
3. CORS/CSRF settings blocking health endpoint requests
4. SSL/HTTPS redirect interfering with HTTP health check
5. Backend health endpoint responding with unexpected status or format

### Troubleshooting Context
From deployment logs:
- Containers are healthy but HTTP endpoint is not responding
- Check nginx routing configuration
- Check backend application logs for errors
- Verify CORS/CSRF settings allow the health endpoint

---

## User Stories

### Story #350.1: Investigate Backend Health Endpoint Response
**Agent**: devops-engineer
**Priority**: High
**Dependencies**: None

**Description**:
As a DevOps engineer, I need to investigate why the backend health endpoint is not responding correctly to HTTP requests in the staging environment, so that I can identify the root cause of the deployment health check failure.

**Acceptance Criteria**:
- When I connect to the staging server, I should be able to manually execute curl requests to `http://localhost/api/v1/status/` and see the actual HTTP response code
- When I review the backend container logs, I should see whether health endpoint requests are reaching the Django application
- When I check the nginx proxy logs, I should see HTTP request routing information for health endpoint requests
- When I inspect the nginx configuration, I should verify that `/api/v1/status/` requests are properly routed to the backend service
- When I review the backend CORS/CSRF settings in staging configuration, I should verify that health endpoints are accessible without authentication

**Technical Notes**:
- SSH to staging server and check: nginx access/error logs, backend application logs, container health status
- Verify nginx routing: location `/api/` block should proxy to backend upstream
- Check for SSL redirect issues: SECURE_SSL_REDIRECT setting may interfere with HTTP health checks
- Verify backend is listening on expected port (8000) and responding to internal health checks

---

### Story #350.2: Fix Health Endpoint Accessibility in Staging
**Agent**: backend-developer
**Priority**: High
**Dependencies**: Story #350.1 (must identify root cause first)

**Description**:
As a backend developer, I need to ensure the health endpoint is accessible and returns the correct response format in the staging environment, so that the CI/CD pipeline health check succeeds and deployments can complete.

**Acceptance Criteria**:
- When the backend application starts in staging, the health endpoint at `/api/v1/status/` should respond within 10 seconds of container being marked healthy
- When the health endpoint receives an HTTP request, it should return HTTP 200 status code with JSON body containing `"status": "healthy"`
- When CORS/CSRF protection is enabled, health endpoints should remain accessible without authentication or CSRF tokens
- When the backend is behind a reverse proxy, health endpoint responses should not be affected by security middleware (SSL redirect, CSRF, etc.)

**Technical Notes**:
- Health endpoint defined in `backend/apps/api/health_views.py` - StatusView class
- Endpoint uses `permission_classes = [AllowAny]` for unauthenticated access
- Check if SECURE_SSL_REDIRECT=True in staging is causing HTTP to HTTPS redirect for internal health checks
- Verify ALLOWED_HOSTS includes SERVER_HOST for staging requests
- Ensure health endpoint is excluded from rate limiting if applied

---

### Story #350.3: Update CI/CD Health Check Strategy
**Agent**: devops-engineer
**Priority**: Medium
**Dependencies**: Stories #350.1 and #350.2 (must fix underlying issues first)

**Description**:
As a DevOps engineer, I need to improve the health check verification strategy in the CI/CD pipeline to better handle staging deployment scenarios and provide clearer diagnostics when health checks fail, so that future deployment issues are easier to troubleshoot.

**Acceptance Criteria**:
- When containers become healthy, the health check script should wait an additional buffer period before starting HTTP verification attempts
- When HTTP health checks fail, the script should capture and display the full HTTP response body and headers for debugging
- When health check retries are exhausted, the script should provide specific diagnostic commands that can be run manually on the server
- When nginx or backend is misconfigured, the failure message should clearly indicate which layer (proxy vs backend) is failing

**Technical Notes**:
- Health check logic in `.github/workflows/unified-ci-cd.yml` (lines 892-1027)
- Current MAX_HTTP_RETRIES=6 with HTTP_RETRY_DELAY=10s (60 seconds total)
- Backend has start_period: 200s for migrations - may need additional grace period
- Consider adding intermediate check: nginx /health endpoint (verifies proxy layer separately from backend)
- Add curl verbose output capture for failed requests
- Include backend container logs in failure output (already present, verify adequacy)

---

## Execution Order

### Phase 1: Investigation (Sequential)
1. Story #350.1 - Investigate Backend Health Endpoint Response

### Phase 2: Fix Implementation (Sequential - depends on investigation findings)
2. Story #350.2 - Fix Health Endpoint Accessibility in Staging

### Phase 3: Process Improvement (Sequential - depends on fix being in place)
3. Story #350.3 - Update CI/CD Health Check Strategy

---

## Summary

**Total Stories**: 3
**Assigned Agents**:
- devops-engineer (Stories #350.1, #350.3)
- backend-developer (Story #350.2)

**Execution Phases**: 3
**Sequential Phases**: 3
**Parallel Phases**: 0

**Story Quality Validation**:
- ✅ All stories are implementation-agnostic
- ✅ All stories focus on WHAT, not HOW
- ✅ All acceptance criteria are user-observable
- ✅ No technical implementation details prescribed
- ✅ Stories work for ANY technology stack
- ✅ No separate API contract stories needed (backend-only fix)

**Atomicity Compliance**:
- ✅ Story #350.1: Investigation and root cause identification (1 day)
- ✅ Story #350.2: Fix backend health endpoint issues (1-2 days)
- ✅ Story #350.3: Improve health check robustness (1 day)
- ✅ All stories are independently deployable
- ✅ Each story delivers complete user-facing capability

---

## Additional Context

### Related Files
- `.github/workflows/unified-ci-cd.yml` - Deployment and health check workflow
- `backend/apps/api/health_views.py` - Health endpoint implementation
- `backend/apps/api/urls.py` - API URL routing (health endpoint at line 58)
- `nginx/nginx.production.conf` - Reverse proxy configuration
- `compose.staging.yml` - Staging environment configuration
- `backend/config/settings/staging.py` - Staging Django settings

### Recent Changes
Feature #20 (Basic Login Functionality) was recently implemented and may have introduced:
- New authentication middleware affecting health endpoints
- CORS/CSRF configuration changes
- SSL/security settings changes in staging environment

### Success Criteria
Deployment is successful when:
1. Containers pass Docker health checks (already working)
2. HTTP request to `/api/v1/status/` returns 200 OK
3. Response body contains JSON with `"status": "healthy"`
4. Health check succeeds within MAX_HTTP_RETRIES attempts
5. E2E testing pipeline stage can proceed
