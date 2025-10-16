# GitHub Actions Token Permissions Investigation Report

**Bug ID:** 2
**Investigation Date:** 2025-10-17
**Investigator:** DevOps Engineer (AI Agent)

## Executive Summary

The `log-bugs` job in `.github/workflows/frontend-ci.yml` fails to fetch job logs from the GitHub API with an "insufficient permissions" error. This investigation identifies the root cause and documents the minimum required permissions to resolve the issue.

## Current Configuration Analysis

### Workflow-Level Permissions

**Location:** `.github/workflows/frontend-ci.yml` (lines 10-14)

```yaml
permissions:
  contents: write  # Needed for log-bugs job to commit changes
  pull-requests: write
  checks: write
  actions: read  # Needed to fetch job logs and job information
```

### Job-Level Permissions (log-bugs job)

**Location:** `.github/workflows/frontend-ci.yml` (lines 358-360)

```yaml
permissions:
  contents: write
```

## Root Cause Analysis

### The Permission Inheritance Problem

**CRITICAL FINDING:** When a job defines explicit `permissions`, it **completely overrides** workflow-level permissions rather than merging with them. The `log-bugs` job only has `contents: write` permission at the job level, which means it **lost** the `actions: read` permission declared at the workflow level.

### GitHub Actions Permission Model

From the GitHub Actions documentation:

1. **Default Behavior (No explicit permissions):** Jobs inherit workflow-level permissions
2. **Job-Level Permissions Defined:** Job permissions **replace** (not merge with) workflow-level permissions
3. **Required Permission for API Access:** The `actions: read` permission is required to:
   - Access `/repos/{owner}/{repo}/actions/runs/{run_id}/jobs` endpoint
   - Access `/repos/{owner}/{repo}/actions/jobs/{job_id}/logs` endpoint
   - Fetch job information and logs from the same workflow run

### Evidence from Bug Report

The bug report (`docs/features/2/bugs/2.md`) shows:

```
## Failed Step
API Error - Permission Denied

## Raw Logs
API Error: Unable to fetch job information due to insufficient permissions
```

This confirms the API call at line 478 in the workflow fails due to missing `actions: read` permission.

## API Endpoints Investigation

### Endpoints Used by log-bugs Job

**1. Jobs List Endpoint** (line 478)
```bash
gh api "/repos/$REPO/actions/runs/$RUN_ID/jobs"
```
- **Purpose:** Fetch list of jobs in the workflow run
- **Required Permission:** `actions: read`
- **Returns:** JSON array of job objects with names, IDs, and status

**2. Job Logs Endpoint** (line 539)
```bash
gh api "/repos/$REPO/actions/jobs/$JOB_ID/logs"
```
- **Purpose:** Download raw logs for a specific job
- **Required Permission:** `actions: read`
- **Returns:** Plain text log output

### Permission Requirements from GitHub API Documentation

According to GitHub's REST API documentation for Actions:

- **GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs**
  - Required permission: `actions: read`
  - Scope: Repository-level access to workflow run information

- **GET /repos/{owner}/{repo}/actions/jobs/{job_id}/logs**
  - Required permission: `actions: read`
  - Scope: Repository-level access to job logs

## Testing Different Permission Combinations

### Test Case 1: Current Configuration (FAILS)

```yaml
# Workflow level
permissions:
  contents: write
  pull-requests: write
  checks: write
  actions: read

# Job level (log-bugs)
permissions:
  contents: write
```

**Result:** ❌ FAILS - Job loses `actions: read` permission
**Error:** "API Error: Unable to fetch job information due to insufficient permissions"

### Test Case 2: Add actions: read to Job Level (SHOULD SUCCEED)

```yaml
# Workflow level
permissions:
  contents: write
  pull-requests: write
  checks: write
  actions: read

# Job level (log-bugs)
permissions:
  contents: write
  actions: read  # ADD THIS
```

**Expected Result:** ✅ SUCCESS - Job has both required permissions
**Rationale:** Explicit job-level permissions include both `contents: write` (for committing) and `actions: read` (for API access)

### Test Case 3: Remove Job-Level Permissions (SHOULD SUCCEED)

```yaml
# Workflow level
permissions:
  contents: write
  pull-requests: write
  checks: write
  actions: read

# Job level (log-bugs)
# Remove permissions block entirely - inherit from workflow level
```

**Expected Result:** ✅ SUCCESS - Job inherits all workflow-level permissions
**Rationale:** Without explicit job permissions, the job inherits workflow-level permissions
**Trade-off:** Job gets more permissions than minimally required (pull-requests: write, checks: write)

### Test Case 4: Minimal Job-Level Permissions (RECOMMENDED)

```yaml
# Workflow level
permissions:
  pull-requests: write
  checks: write
  # Remove actions: read from here if only log-bugs needs it

# Job level (log-bugs)
permissions:
  contents: write  # Required for git commit/push
  actions: read    # Required for API access to jobs and logs
```

**Expected Result:** ✅ SUCCESS with least privilege principle
**Rationale:** Each job has only the permissions it needs
**Security Benefit:** Other jobs don't get unnecessary `contents: write` or `actions: read`

## Minimum Required Permissions

### For log-bugs Job Specifically

The `log-bugs` job requires exactly **TWO** permissions:

1. **`contents: write`** - Required for:
   - Git checkout with write access
   - Creating/modifying `docs/features/bug-log.json`
   - Creating markdown bug report files
   - Committing changes to the branch
   - Pushing commits to the remote repository

2. **`actions: read`** - Required for:
   - Accessing GitHub Actions API endpoints
   - Fetching job information from current workflow run
   - Downloading job logs for failed jobs
   - Reading workflow run metadata

### Verification of Other Permission Needs

**NOT REQUIRED for log-bugs:**
- `pull-requests: write` - Not used by this job (no PR comments or modifications)
- `checks: write` - Not used by this job (no check runs created)
- `issues: write` - Not used by this job (no issue creation)
- `deployments: write` - Not used by this job (no deployments)

## Recommended Solution

### Option 1: Explicit Job-Level Permissions (RECOMMENDED)

**Pros:**
- Follows principle of least privilege
- Each job has only what it needs
- Clear and explicit permissions per job
- Better security posture

**Cons:**
- Requires explicit permission block for each job that needs non-default permissions
- More verbose configuration

**Implementation:**
```yaml
permissions:
  contents: write
  actions: read
```

Add this to the `log-bugs` job at line 358 in `.github/workflows/frontend-ci.yml`.

### Option 2: Remove Job-Level Permissions Block

**Pros:**
- Simpler configuration
- Job inherits from workflow level
- Less repetition

**Cons:**
- Job gets more permissions than it needs (pull-requests: write, checks: write)
- Violates principle of least privilege
- Less secure

**Implementation:**
Remove lines 358-360 from `.github/workflows/frontend-ci.yml`.

## Security Considerations

### Principle of Least Privilege

The recommended solution (Option 1) follows the principle of least privilege by granting each job only the permissions it requires to function. This limits the potential impact if:
- A job is compromised
- A third-party action in the job is malicious
- A bug causes unintended API calls

### Token Scope Limitations

The `GITHUB_TOKEN` has built-in limitations even with explicit permissions:
- Cannot access resources outside the repository
- Automatically revoked when workflow completes
- Scoped to the specific workflow run
- Cannot be used for authentication to external services

### Permission Audit Trail

GitHub provides audit logs for all API calls made with `GITHUB_TOKEN`, allowing tracking of:
- Which jobs accessed which endpoints
- When permissions were used
- What modifications were made to repository content

## Implementation Validation Plan

### Step 1: Apply Permission Fix

Add `actions: read` to the `log-bugs` job permissions block.

### Step 2: Trigger Test Workflow

Push changes to a feature branch to trigger the `test-failure` job, which will cause `log-bugs` to execute.

### Step 3: Verify API Access

Check the workflow logs for the "Fetch failed job logs" step (line 464-569) to confirm:
- ✅ API call to jobs endpoint succeeds
- ✅ Job ID is correctly extracted
- ✅ Logs are successfully downloaded
- ✅ No "Permission Denied" errors appear

### Step 4: Verify Bug Report Content

Check the generated bug report markdown file contains:
- ✅ Actual job logs (not error messages)
- ✅ Failed step name (not "API Error - Permission Denied")
- ✅ Complete log output with timestamps

### Step 5: Security Validation

Verify other jobs in the workflow cannot:
- ❌ Commit to the repository (should fail - no `contents: write`)
- ❌ Access actions API (should fail - no `actions: read`)

This confirms permissions are properly scoped per job.

## Documentation Updates Required

### Files to Update

1. **`.github/workflows/frontend-ci.yml`** - Add `actions: read` permission to log-bugs job
2. **`.github/workflows/.env`** - Document the permission requirements (lines 59-79)
3. **This investigation report** - Archive as reference documentation

### Inline Comments to Add

Add explanatory comments to the workflow file:

```yaml
permissions:
  contents: write  # Required: commit bug reports and update bug-log.json
  actions: read    # Required: fetch job information and logs via GitHub API
```

## Conclusion

### Summary of Findings

1. **Root Cause:** Job-level `permissions` block overrides workflow-level permissions, causing loss of `actions: read`
2. **Minimum Required Permissions:** `contents: write` + `actions: read`
3. **Recommended Fix:** Add `actions: read` to job-level permissions block
4. **Security Impact:** Minimal - follows least privilege principle
5. **Testing Required:** Yes - validate API access and log fetching in test workflow run

### Next Steps

1. ✅ Investigation complete - documented findings
2. ⏭️ Create automated test for job log fetching permissions (User Story #2)
3. ⏭️ Update workflow permissions configuration (User Story #3)
4. ⏭️ Enhance API error handling (User Story #4)
5. ⏭️ Create end-to-end regression test (User Story #5)
6. ⏭️ Validate fix and update bug status (User Story #6)

## References

- [GitHub Docs - Workflow Syntax: permissions](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#permissions)
- [GitHub Docs - REST API Actions Endpoints](https://docs.github.com/en/rest/actions/workflow-runs)
- [GitHub Docs - Automatic token authentication](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication)
- [GitHub Actions Best Practices - Security Hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)

## Appendix: Permission Matrix

| Permission | Workflow Level | log-bugs Job Level (Current) | log-bugs Job Level (Required) |
|------------|---------------|------------------------------|-------------------------------|
| `contents: write` | ✅ | ✅ | ✅ REQUIRED |
| `pull-requests: write` | ✅ | ❌ (lost) | ❌ Not needed |
| `checks: write` | ✅ | ❌ (lost) | ❌ Not needed |
| `actions: read` | ✅ | ❌ (lost) | ✅ REQUIRED |

**Legend:**
- ✅ REQUIRED - Permission must be present for job to function
- ✅ - Permission is present
- ❌ - Permission is absent
- ❌ Not needed - Permission is not required by this job
