# Bug Fix User Stories: Test failure job failed - simulated test failure

**Bug ID:** 1
**Feature ID:** 2
**Severity:** Not specified
**Root Cause:** GitHub Actions API permission error when fetching job logs in the `log-bugs` job. Despite having `actions: read` permission declared, API calls to fetch job information fail with "insufficient permissions" error.

---

## Execution Order

### Phase 1 (Sequential)
- Story #1 (agent: devops-engineer) - Investigation

### Phase 2 (Sequential)
- Story #2 (agent: devops-engineer) - depends on Story #1

### Phase 3 (Sequential)
- Story #3 (agent: devops-engineer) - depends on Story #2

### Phase 4 (Parallel)
- Story #4 (agent: devops-engineer) - depends on Story #3
- Story #5 (agent: devops-engineer) - depends on Story #3

### Phase 5 (Sequential)
- Story #6 (agent: devops-engineer) - depends on Stories #4, #5

---

## User Stories

### 1. Investigate GitHub Actions API Permission Issue
Investigate why the `log-bugs` job cannot fetch job information via the GitHub API despite having `actions: read` permission. Analyze the workflow file permissions, token scopes, and API requirements. Determine if the issue is related to job-level permissions, workflow-level permissions, or GitHub API limitations when accessing logs from within the same workflow run.

Acceptance Criteria:
- Document current permission configuration in workflow file
- Test GitHub API calls manually to verify permission requirements
- Identify exact permission needed for fetching job logs and job information
- Document findings in investigation report with recommended solution

Agent: devops-engineer
Dependencies: none

---

### 2. Write Test for GitHub Actions Log Fetching with Proper Permissions
Create a test workflow or test job that validates the correct permissions are configured for fetching job logs via the GitHub API. This test should verify that API calls to `/repos/{owner}/{repo}/actions/runs/{run_id}/jobs` and `/repos/{owner}/{repo}/actions/jobs/{job_id}/logs` succeed.

Acceptance Criteria:
- Test workflow includes steps that fetch job information via GitHub API
- Test verifies API response is valid JSON with expected structure
- Test validates log fetching returns actual log content
- Test fails if permissions are insufficient

Agent: devops-engineer
Dependencies: Story #1

---

### 3. Fix GitHub Actions Workflow Permissions Configuration
Update the `.github/workflows/frontend-ci.yml` file with correct permissions based on investigation findings. Ensure the `log-bugs` job has all necessary permissions to fetch job information and logs via the GitHub API.

Acceptance Criteria:
- Workflow file updated with correct permissions for log-bugs job
- Permission changes follow principle of least privilege
- Permissions are documented with inline comments explaining why each is needed
- Test workflow from Story #2 passes with new permission configuration

Agent: devops-engineer
Dependencies: Story #2

---

### 4. Add Comprehensive Error Handling for API Calls
Enhance the "Fetch failed job logs" step in the `log-bugs` job with better error handling. Add validation checks for API responses, clear error messages when permissions fail, and fallback mechanisms when logs are unavailable.

Acceptance Criteria:
- API response validation checks added before processing JSON
- Clear error messages logged when API calls fail with permission errors
- Fallback mechanism provides meaningful bug report even when logs unavailable
- Error handling doesn't cause job to fail, allows bug logging to continue

Agent: devops-engineer
Dependencies: Story #3

---

### 5. Create Regression Test for Bug Logging Workflow
Create a regression test that validates the entire bug logging workflow end-to-end. This test should simulate a failing job and verify that the bug log entry is created correctly with proper job information and logs.

Acceptance Criteria:
- Test simulates job failure in a workflow
- Test verifies bug-log.json is updated with new bug entry
- Test validates markdown bug report file is created with correct content
- Test confirms job logs are fetched and included in bug report

Agent: devops-engineer
Dependencies: Story #3

---

### 6. Validate Fix and Update Bug Status
Run the fixed workflow to validate that job logs are now fetched successfully and bug reports are created with complete information. Update the bug-log.json to mark this bug as fixed.

Acceptance Criteria:
- Workflow runs successfully with test-failure job triggering log-bugs
- Bug report markdown file contains actual job logs (not permission error)
- Bug-log.json entry for bug #1 has isFixed: true and fixedDate set
- All GitHub Actions checks pass without permission errors

Agent: devops-engineer
Dependencies: Stories #4, #5

---

## Notes

### Technical Context
- The workflow is already using `permissions` at both workflow and job level
- Current permissions include `contents: write`, `pull-requests: write`, `checks: write`, `actions: read`
- The `gh` CLI is being used to make API calls with `${{ github.token }}`
- Error occurs specifically when fetching job information during workflow execution

### Potential Solutions to Investigate
1. GitHub Actions may require `actions: write` (not just `read`) to access logs from same workflow
2. Job-level permissions might need to be elevated beyond workflow-level permissions
3. The `GITHUB_TOKEN` might have limitations accessing logs while workflow is still running
4. API endpoint might require different authentication or token scope

### Related Files
- `.github/workflows/frontend-ci.yml` - Main workflow file to be fixed
- `docs/features/bug-log.json` - Bug tracking file
- `docs/features/2/bugs/1.md` - This bug's markdown report

### Follow-up Considerations
- Consider if this permission fix affects any security posture
- Document the permission requirements for future workflow development
- Update workflow comments to explain permission needs clearly
