# Bug Fix User Stories: Test failure job failed - simulated test failure

**Bug ID:** 2
**Feature ID:** 2
**Severity:** High
**Root Cause:** GitHub Actions API permission error when fetching job logs in the `log-bugs` job. The workflow has `actions: read` permission declared, but API calls to fetch job information fail with "insufficient permissions" error. This prevents proper bug reporting and logging in the CI/CD pipeline.

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

### 1. Investigate GitHub Actions Token Permission Requirements
Investigate the exact GitHub Actions token permissions required to fetch job information and logs via the GitHub API. Test various permission configurations to determine the minimal set of permissions needed for the `log-bugs` job to successfully retrieve job details and log content from the same workflow run.

Acceptance Criteria:
- Document current permission configuration in .github/workflows/frontend-ci.yml
- Test GitHub API calls with different permission combinations
- Identify the minimum required permissions for fetching job logs
- Create investigation report documenting findings with specific permission requirements

Agent: devops-engineer
Dependencies: none

---

### 2. Write Automated Test for Job Log Fetching Permissions
Create an automated test that validates the GitHub Actions workflow can successfully fetch job logs with the correct permissions. The test should verify API access to job information and log content, ensuring the bug logging workflow functions correctly.

Acceptance Criteria:
- Test workflow verifies gh CLI can access /repos/{owner}/{repo}/actions/runs/{run_id}/jobs endpoint
- Test validates API response contains valid JSON with jobs array
- Test confirms job log retrieval returns actual log content (not error messages)
- Test fails explicitly if permissions are insufficient with clear error message

Agent: devops-engineer
Dependencies: Story #1

---

### 3. Update Workflow Permissions Configuration
Update the `.github/workflows/frontend-ci.yml` file with the correct permissions based on investigation findings from Story #1. Apply the principle of least privilege while ensuring the `log-bugs` job has sufficient permissions to fetch job information and logs.

Acceptance Criteria:
- Workflow file updated with minimum required permissions for log-bugs job
- Permissions include inline comments explaining why each permission is needed
- Changes follow GitHub Actions security best practices
- Automated test from Story #2 passes with new permission configuration

Agent: devops-engineer
Dependencies: Story #2

---

### 4. Enhance API Error Handling in Log Fetching Logic
Improve error handling in the "Fetch failed job logs" step of the `log-bugs` job. Add comprehensive validation, clear error messages, and graceful fallbacks when API calls fail or permissions are insufficient.

Acceptance Criteria:
- API response validation checks added before processing JSON responses
- Clear, actionable error messages logged when API permission errors occur
- Fallback mechanism creates meaningful bug report even when logs unavailable
- Error handling prevents job failure while still logging the bug

Agent: devops-engineer
Dependencies: Story #3

---

### 5. Create End-to-End Regression Test for Bug Logging Workflow
Create a comprehensive regression test that validates the complete bug logging workflow from test failure through bug report creation. The test should simulate a failing job and verify all steps of the bug logging process execute correctly.

Acceptance Criteria:
- Test simulates job failure and triggers log-bugs job
- Test verifies bug-log.json is updated with correct bug entry structure
- Test validates markdown bug report file is created at correct path with expected content
- Test confirms job logs are fetched and included in bug report (not permission errors)

Agent: devops-engineer
Dependencies: Story #3

---

### 6. Validate Bug Fix and Update Bug Status
Execute the fixed workflow to validate that job logs are now successfully fetched and bug reports contain complete information. Mark Bug #2 as fixed in the bug log after confirming the workflow operates correctly.

Acceptance Criteria:
- Workflow runs successfully with test-failure job properly triggering log-bugs
- Generated bug report markdown file contains actual job logs (not API permission errors)
- Bug-log.json entry for bug #2 updated with isFixed: true and current fixedDate
- All GitHub Actions CI/CD checks pass without permission-related errors

Agent: devops-engineer
Dependencies: Stories #4, #5

---

## Notes

### Technical Context
- Current workflow declares permissions at workflow level: `contents: write`, `pull-requests: write`, `checks: write`, `actions: read`
- The `log-bugs` job has job-level permissions: `contents: write`
- GitHub CLI (`gh`) is used to make API calls with `${{ github.token }}`
- Error occurs when calling `/repos/{owner}/{repo}/actions/runs/{run_id}/jobs` endpoint
- API returns "insufficient permissions" despite `actions: read` being declared

### Root Cause Analysis
The issue likely stems from one or more of the following:
1. GitHub Actions may require `actions: write` (not just `read`) to access logs from the same workflow run
2. Job-level permissions may be overriding workflow-level permissions, removing necessary scopes
3. The `GITHUB_TOKEN` has limitations accessing certain APIs while the workflow is still executing
4. Specific API endpoints may require additional permissions beyond `actions: read`

### Potential Solutions to Validate
1. Add `actions: write` permission to log-bugs job
2. Remove job-level permissions block to inherit workflow-level permissions
3. Add explicit `actions: read` to job-level permissions alongside `contents: write`
4. Use alternative API endpoints that may have different permission requirements
5. Investigate if logs need to be fetched after workflow completion rather than during execution

### Files to Modify
- `.github/workflows/frontend-ci.yml` - Primary workflow file requiring permission fixes
- `docs/features/bug-log.json` - Bug tracking file to be updated when fix is validated
- `docs/features/2/bugs/2.md` - Current bug report with API permission error

### Security Considerations
- Follow principle of least privilege when adding permissions
- Document all permission changes with clear rationale
- Ensure added permissions don't introduce security risks
- Consider impact on other jobs in the workflow

### Success Criteria
The bug is fixed when:
1. Bug logging workflow successfully fetches and includes actual job logs in bug reports
2. No API permission errors appear in bug report markdown files
3. All automated tests pass validating the bug logging functionality
4. Changes are documented and follow GitHub Actions best practices
