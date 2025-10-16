# Automated Permission Test Documentation

**Bug ID:** 2
**User Story:** #2 - Write Automated Test for Job Log Fetching Permissions
**Created:** 2025-10-17
**Test Workflow:** `.github/workflows/test-permissions.yml`

## Overview

This automated test validates that GitHub Actions workflows can successfully fetch job logs with the correct permissions configuration. The test specifically validates the fix for Bug #2, which requires `actions: read` permission to access the GitHub Actions API.

## Purpose

The test workflow ensures that:

1. The GitHub CLI can access the `/repos/{owner}/{repo}/actions/runs/{run_id}/jobs` endpoint
2. API responses contain valid JSON with a `jobs` array (not error messages)
3. Job log retrieval returns actual log content (not permission errors)
4. The workflow fails explicitly with clear error messages when permissions are insufficient

## Test Scenarios

The workflow supports two test scenarios via `workflow_dispatch` inputs:

### Scenario 1: Positive Test - WITH actions:read Permission

**Purpose:** Validate that API access succeeds when `actions: read` permission is present

**Configuration:**
```yaml
permissions:
  contents: read
  actions: read  # REQUIRED for API access
```

**Expected Result:** ✅ All API calls succeed and return valid data

**What it tests:**
- API call to jobs endpoint returns HTTP 200
- Response contains valid JSON with `jobs` array
- Job ID can be extracted from response
- Logs endpoint returns actual log content (not JSON error)
- Log content is substantial (>10 bytes)

### Scenario 2: Negative Test - WITHOUT actions:read Permission

**Purpose:** Validate that API access fails when `actions: read` permission is missing

**Configuration:**
```yaml
permissions:
  contents: read
  # actions: read is MISSING - should cause failure
```

**Expected Result:** ✅ API calls fail with permission denied error

**What it tests:**
- API call to jobs endpoint fails (HTTP 403 or similar)
- Error response indicates insufficient permissions
- Test correctly identifies the expected failure

## How to Run the Test

### Via GitHub Actions UI

1. Navigate to the repository on GitHub
2. Go to **Actions** tab
3. Select **Test GitHub Actions Permissions** workflow from the left sidebar
4. Click **Run workflow** button
5. Select test scenario from dropdown:
   - **test-with-actions-read** - Positive test (should pass)
   - **test-without-actions-read** - Negative test (should pass by failing correctly)
6. Click **Run workflow**
7. Wait for workflow to complete
8. Review test results in the job summary

### Via GitHub CLI

```bash
# Run positive test (with actions:read permission)
gh workflow run test-permissions.yml \
  -f test-scenario=test-with-actions-read

# Run negative test (without actions:read permission)
gh workflow run test-permissions.yml \
  -f test-scenario=test-without-actions-read

# View workflow run status
gh run list --workflow=test-permissions.yml --limit=5

# View specific run
gh run view <run-id>
```

### Via REST API

```bash
# Trigger positive test
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/{owner}/{repo}/actions/workflows/test-permissions.yml/dispatches \
  -d '{"ref":"main","inputs":{"test-scenario":"test-with-actions-read"}}'

# Trigger negative test
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/{owner}/{repo}/actions/workflows/test-permissions.yml/dispatches \
  -d '{"ref":"main","inputs":{"test-scenario":"test-without-actions-read"}}'
```

## Understanding Test Results

### Successful Positive Test (test-with-actions-read)

**Job Summary:**
```
✅ Permission Test PASSED

Test Results:
- ✅ GitHub CLI can access /repos/{owner}/{repo}/actions/runs/{run_id}/jobs endpoint
- ✅ API response contains valid JSON with jobs array
- ✅ Job log retrieval returns actual log content (not error messages)
- ✅ Permissions are sufficient for bug logging workflow

Configuration Tested:
permissions:
  contents: read
  actions: read  # REQUIRED for API access
```

**What this means:**
- The `actions: read` permission is working correctly
- API calls succeed and return valid data
- The bug logging workflow will be able to fetch job logs

### Successful Negative Test (test-without-actions-read)

**Job Summary:**
```
✅ Negative Test PASSED

Test Results:
- ✅ API call correctly failed without actions: read permission
- ✅ Error message indicates insufficient permissions

Configuration Tested:
permissions:
  contents: read
  # actions: read is MISSING

Conclusion:
This test confirms that actions: read permission is REQUIRED
for the log-bugs job to function correctly.
```

**What this means:**
- The test correctly validates that `actions: read` is required
- Without this permission, API calls fail as expected
- The fix for Bug #2 is necessary

### Test Failure Scenarios

#### Positive Test Fails

If the positive test fails, possible causes:

1. **GitHub API Rate Limiting**
   - Wait a few minutes and retry
   - Check rate limit: `gh api rate_limit`

2. **Network Connectivity Issues**
   - Check GitHub status: https://www.githubstatus.com/
   - Retry the workflow

3. **Workflow Run Not Yet Available**
   - Logs may not be immediately available after job completion
   - This is rare but can happen with API delays

4. **Permission Configuration Error**
   - Verify the workflow file has correct permissions block
   - Check repository settings for workflow permissions

#### Negative Test Fails

If the negative test fails (API call succeeds when it shouldn't):

1. **Test Configuration Error**
   - Verify the permissions block is correctly missing `actions: read`
   - Check for workflow-level permissions that might override

2. **GitHub API Behavior Change**
   - GitHub may have changed permission requirements
   - Review GitHub Actions documentation for updates

## Test Workflow Structure

```
test-permissions.yml
├── trigger-failure (always fails)
│   └── Simulates a failed job to test log fetching
├── test-with-actions-read (runs if scenario selected)
│   ├── Test API access to jobs endpoint
│   ├── Test API access to job logs endpoint
│   └── Generate test summary
└── test-without-actions-read (runs if scenario selected)
    ├── Test API access WITHOUT permission (expect failure)
    ├── Validate error message
    └── Generate test summary
```

## Integration with Bug Fix Workflow

This test workflow validates the fix that will be applied in **User Story #3: Update Workflow Permissions Configuration**.

**Before Fix (Current State):**
```yaml
# .github/workflows/frontend-ci.yml
log-bugs:
  permissions:
    contents: write
    # actions: read is MISSING - causes API failures
```

**After Fix (User Story #3):**
```yaml
# .github/workflows/frontend-ci.yml
log-bugs:
  permissions:
    contents: write
    actions: read  # ADDED - enables API access
```

## Maintenance

### When to Run This Test

- **Before applying the permission fix** - Validates the negative case
- **After applying the permission fix** - Validates the positive case
- **After any changes to workflow permissions** - Regression testing
- **When debugging permission issues** - Diagnostic tool
- **As part of CI/CD validation** - Automated regression testing

### Updating the Test

If GitHub API endpoints or permission requirements change:

1. Update API endpoint URLs in test workflow
2. Update expected HTTP status codes
3. Update permission configurations in test scenarios
4. Update this documentation with new findings
5. Validate YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/test-permissions.yml'))"`

## Troubleshooting

### Common Issues

**Issue:** Test workflow doesn't appear in Actions UI
**Solution:** Ensure workflow file is committed to `.github/workflows/` directory

**Issue:** Cannot trigger workflow manually
**Solution:** Verify workflow has `workflow_dispatch` trigger and you have repository permissions

**Issue:** API calls return 404
**Solution:** Wait a few seconds after workflow starts - run/job data may not be immediately available

**Issue:** Logs endpoint returns empty content
**Solution:** This can happen if logs aren't fully flushed - the test handles this gracefully

## Security Considerations

### Principle of Least Privilege

The test workflow demonstrates the principle of least privilege:

- **Positive test** - Only grants `contents: read` and `actions: read` (minimum required)
- **Negative test** - Only grants `contents: read` (deliberately missing `actions: read`)

### Token Security

- Test workflow uses `GITHUB_TOKEN` (automatic token)
- Token is automatically scoped to the repository
- Token is revoked when workflow completes
- No long-lived credentials are stored

### Audit Trail

All test runs are logged in GitHub Actions:
- View run history: Actions tab → Test GitHub Actions Permissions
- Each run shows which scenario was tested
- Step logs show exact API calls made
- Results are preserved for audit purposes

## References

- **Investigation Report:** `docs/features/bugs/2/investigation-report.md`
- **User Stories:** `docs/features/bugs/2/user-stories.md`
- **GitHub API Documentation:** https://docs.github.com/en/rest/actions
- **GitHub Actions Permissions:** https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication

## Acceptance Criteria Validation

### Story #2 Acceptance Criteria

✅ **Test workflow verifies gh CLI can access /repos/{owner}/{repo}/actions/runs/{run_id}/jobs endpoint**
- Implemented in `test-with-actions-read` job, step "Test API access to jobs endpoint"
- Uses curl with GitHub API to validate access
- Checks HTTP status code and response structure

✅ **Test validates API response contains valid JSON with jobs array**
- Implemented with `jq -e '.jobs'` validation
- Ensures response is valid JSON (not error message)
- Verifies `jobs` array exists in response

✅ **Test confirms job log retrieval returns actual log content (not error messages)**
- Implemented in `test-with-actions-read` job, step "Test API access to job logs endpoint"
- Validates logs are not JSON error responses
- Checks log size to ensure substantial content
- Verifies logs are plain text (not JSON)

✅ **Test fails explicitly if permissions are insufficient with clear error message**
- Implemented in both test scenarios
- Positive test fails with clear HTTP error codes
- Negative test validates expected failure occurs
- GitHub step summaries provide clear pass/fail indicators
- Error messages indicate root cause (missing permissions)

## Next Steps

After Story #2 completion:

1. **User Story #3** - Apply the permission fix to `.github/workflows/frontend-ci.yml`
2. **User Story #4** - Enhance error handling in log fetching logic
3. **User Story #5** - Create end-to-end regression test for bug logging workflow
4. **User Story #6** - Validate complete bug fix and update bug status
