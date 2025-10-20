# Story #8 Testing Guide: Previous Issue Labeling Logic

## Overview

This guide provides comprehensive testing procedures for Story #8: Implement Previous Issue Labeling Logic in Bug Resolver.

## Test Status

✅ **Implementation Status**: Already implemented as part of Story #1
✅ **YAML Validation**: Passed
✅ **Code Review**: Passed
⏳ **Manual Testing**: Ready to execute

## Prerequisites

Before running tests, ensure:
1. You have an existing open GitHub issue to use for testing
2. The issue is in the same repository
3. You have permissions to modify issues (write access)
4. The bug-resolver workflow exists at `.github/workflows/bug-resolver.yml`

## Test Workflows

### Automated Test Workflow

**File**: `.github/workflows/test-story-8-previous-issue-labeling.yml`

This workflow provides automated testing of Story #8 functionality.

**How to Run**:
1. Navigate to Actions tab in GitHub
2. Select "Test Story #8 - Previous Issue Labeling Logic"
3. Click "Run workflow"
4. Enter an issue number to test
5. Click "Run workflow" button

**What It Tests**:
- ✅ Bug resolver accepts issue number input
- ✅ Bug resolver identifies and verifies issue exists
- ✅ `fix-pending` label is added to issue
- ✅ Explanatory comment is posted to issue
- ✅ All operations complete successfully

**Expected Results**:
- Workflow completes successfully (green checkmark)
- Issue receives `fix-pending` label
- Issue receives comment explaining the label
- Summary shows all acceptance criteria passed

## Manual Test Cases

### Test Case 1: Label Previous Issue as Fix-Pending (Primary Flow)

**Objective**: Verify the bug resolver correctly labels a previous issue when a new different failure is detected.

**Prerequisites**:
- An open GitHub issue (e.g., #42)
- Issue should NOT already have `fix-pending` label

**Steps**:
1. Run the automated test workflow with the issue number
2. Observe workflow execution in Actions tab
3. Navigate to the issue
4. Verify label was added
5. Verify comment was posted

**Expected Results**:
- ✅ Workflow completes successfully
- ✅ Issue has `fix-pending` label
- ✅ Issue has comment: "A new, different failure has been detected for the same feature/job/step combination. This suggests the original issue may have been resolved. This issue has been marked as `fix-pending` for verification."
- ✅ No errors in workflow logs

**Acceptance Criteria Mapping**:
- ✅ AC1: Bug resolver identifies previous issue from provided issue number
- ✅ AC2: Appropriate label added to previous issue indicating status change
- ✅ AC3: Comment added to previous issue explaining the label change

---

### Test Case 2: Handle Non-Existent Issue (Error Case)

**Objective**: Verify the bug resolver gracefully handles non-existent issues.

**Prerequisites**:
- A non-existent issue number (e.g., 999999)

**Steps**:
1. Create a test workflow or use workflow_dispatch:
   ```yaml
   uses: ./.github/workflows/bug-resolver.yml
   with:
     current_run_status: "failure"
     previous_issue_number: "999999"
     action: "mark_previous_as_pending"
   ```
2. Run the workflow
3. Observe execution

**Expected Results**:
- ✅ Workflow completes successfully (does not fail)
- ✅ Warning logged: "Issue #999999 not found or not open"
- ✅ No errors thrown
- ✅ Graceful degradation

**Acceptance Criteria Mapping**:
- ✅ AC1: Bug resolver attempts to identify issue (fails gracefully)

---

### Test Case 3: Handle Closed Issue (Edge Case)

**Objective**: Verify the bug resolver skips labeling when the issue is closed.

**Prerequisites**:
- A closed GitHub issue

**Steps**:
1. Run bug resolver workflow with closed issue number
2. Observe execution
3. Verify no labels or comments added

**Expected Results**:
- ✅ Workflow completes successfully
- ✅ Warning logged: "Issue #X is not open (state: CLOSED), skipping label update"
- ✅ No labels added to closed issue
- ✅ No comments added to closed issue

**Acceptance Criteria Mapping**:
- ✅ AC1: Bug resolver identifies issue and checks state

---

### Test Case 4: Input Validation (Security Test)

**Objective**: Verify input validation prevents invalid data.

**Test 4a: Invalid Issue Number (Non-Numeric)**

**Steps**:
```yaml
uses: ./.github/workflows/bug-resolver.yml
with:
  current_run_status: "failure"
  previous_issue_number: "invalid-number"
  action: "mark_previous_as_pending"
```

**Expected Results**:
- ✅ Workflow fails with validation error
- ✅ Error message: "Invalid previous_issue_number. Must be a number"

**Test 4b: Invalid Action**

**Steps**:
```yaml
uses: ./.github/workflows/bug-resolver.yml
with:
  current_run_status: "failure"
  previous_issue_number: "42"
  action: "invalid_action"
```

**Expected Results**:
- ✅ Workflow fails with validation error
- ✅ Error message: "Invalid action. Must be 'mark_previous_as_pending' or 'mark_as_resolved'"

**Test 4c: Invalid Run Status**

**Steps**:
```yaml
uses: ./.github/workflows/bug-resolver.yml
with:
  current_run_status: "invalid_status"
  previous_issue_number: "42"
  action: "mark_previous_as_pending"
```

**Expected Results**:
- ✅ Workflow fails with validation error
- ✅ Error message: "Invalid current_run_status. Must be 'success' or 'failure'"

---

### Test Case 5: Idempotency Test

**Objective**: Verify the workflow can be run multiple times on the same issue without errors.

**Prerequisites**:
- An open issue that already has `fix-pending` label

**Steps**:
1. Run bug resolver workflow on issue that already has the label
2. Verify workflow completes successfully
3. Check that duplicate labels are not added
4. Check that duplicate comments may be added (expected behavior)

**Expected Results**:
- ✅ Workflow completes successfully
- ✅ Only one `fix-pending` label exists (GitHub prevents duplicates)
- ✅ New comment is added (each run adds a comment)
- ✅ No errors occur

---

### Test Case 6: Integration Test with Bug Logger

**Objective**: Verify Story #8 works correctly when called from bug logger.

**Prerequisites**:
- Bug logger workflow integrated with bug resolver (Story #11)
- A feature branch with failing CI

**Steps**:
1. Create a feature branch (e.g., `feature/123-test`)
2. Push a commit that causes CI failure
3. Wait for bug logger to create issue (Issue A)
4. Fix the issue but introduce a different failure
5. Push the fix commit
6. Observe bug logger behavior

**Expected Results**:
- ✅ Bug logger creates new issue (Issue B) for different failure
- ✅ Bug logger calls bug resolver for Issue A
- ✅ Issue A receives `fix-pending` label
- ✅ Issue A receives explanatory comment
- ✅ Issue B is created as new issue

**Note**: This test requires Story #11 implementation.

---

## Test Data Requirements

### Recommended Test Issues

Create test issues with the following characteristics:

**Test Issue 1: Clean Open Issue**
- Status: Open
- Labels: None (or only `ci-failure`)
- Purpose: Primary test case

**Test Issue 2: Issue with Existing Labels**
- Status: Open
- Labels: `ci-failure`, `bug`
- Purpose: Verify label addition doesn't conflict

**Test Issue 3: Closed Issue**
- Status: Closed
- Purpose: Verify graceful handling of closed issues

## Verification Checklist

After running tests, verify the following:

### Workflow Execution
- [ ] Workflow completes without errors
- [ ] All steps execute in correct order
- [ ] Input validation passes
- [ ] Issue existence check passes
- [ ] Label addition succeeds
- [ ] Comment posting succeeds

### Issue Modifications
- [ ] `fix-pending` label added to issue
- [ ] Label color/description matches repository standards
- [ ] Comment posted with correct text
- [ ] Comment author is github-actions[bot]
- [ ] Issue remains open (not closed)

### Error Handling
- [ ] Invalid inputs cause workflow to fail gracefully
- [ ] Non-existent issues log warnings but don't fail
- [ ] Closed issues are skipped appropriately
- [ ] Clear error messages in all failure scenarios

### Acceptance Criteria
- [ ] AC1: Bug resolver identifies previous issue from provided issue number
- [ ] AC2: Appropriate label added to previous issue indicating status change
- [ ] AC3: Comment added to previous issue explaining the label change

### Security
- [ ] Workflow uses minimal permissions (contents: read, issues: write)
- [ ] No sensitive data exposed in logs
- [ ] Input validation prevents injection attacks
- [ ] Uses default GITHUB_TOKEN (no additional secrets)

### Observability
- [ ] Structured logs provide clear execution flow
- [ ] GitHub Actions summary shows results
- [ ] Direct link to modified issue in summary
- [ ] All steps have clear descriptions

## Troubleshooting

### Issue: Workflow Fails with "Permission Denied"

**Cause**: Insufficient repository permissions

**Solution**:
- Ensure workflow has `issues: write` permission
- Check repository settings → Actions → General → Workflow permissions
- Set to "Read and write permissions"

### Issue: Label Not Added

**Cause**: Multiple possible causes

**Solutions**:
1. Verify issue is open (not closed)
2. Check workflow logs for error messages
3. Verify `action` input is `"mark_previous_as_pending"`
4. Ensure GitHub token has issues:write permission

### Issue: Comment Not Posted

**Cause**: GitHub API rate limiting or permissions

**Solutions**:
1. Check workflow logs for API errors
2. Verify GitHub token is valid
3. Wait if rate limited (rare in GitHub Actions)

### Issue: Test Workflow Not Found

**Cause**: Workflow file not committed to repository

**Solution**:
- Ensure `.github/workflows/test-story-8-previous-issue-labeling.yml` is committed
- Push changes to repository
- Refresh Actions tab

## Performance Benchmarks

Expected execution times:

| Step | Expected Duration |
|------|------------------|
| Input Validation | < 5 seconds |
| Issue Existence Check | < 10 seconds |
| Label Addition | < 5 seconds |
| Comment Posting | < 5 seconds |
| **Total Workflow** | **< 30 seconds** |

Timeout set to 5 minutes for safety margin.

## Test Results Template

Use this template to document test results:

```markdown
## Story #8 Test Results

**Date**: YYYY-MM-DD
**Tester**: Your Name
**Environment**: GitHub Actions

### Test Case 1: Label Previous Issue as Fix-Pending
- Status: ✅ PASS / ❌ FAIL
- Issue Number: #___
- Notes: ___

### Test Case 2: Handle Non-Existent Issue
- Status: ✅ PASS / ❌ FAIL
- Notes: ___

### Test Case 3: Handle Closed Issue
- Status: ✅ PASS / ❌ FAIL
- Issue Number: #___
- Notes: ___

### Test Case 4: Input Validation
- Status: ✅ PASS / ❌ FAIL
- Notes: ___

### Test Case 5: Idempotency Test
- Status: ✅ PASS / ❌ FAIL
- Issue Number: #___
- Notes: ___

### Acceptance Criteria
- [ ] AC1: Bug resolver identifies previous issue from provided issue number
- [ ] AC2: Appropriate label added to previous issue indicating status change
- [ ] AC3: Comment added to previous issue explaining the label change

### Overall Result
- [ ] All tests passed
- [ ] Some tests failed (details above)
- [ ] Ready for production
```

## Next Steps After Testing

Once all tests pass:

1. ✅ Mark Story #8 as fully tested
2. ✅ Document any issues found
3. ✅ Proceed to Story #9 testing (Success Labeling Logic)
4. ✅ Prepare for Story #11 integration testing

## Conclusion

This testing guide ensures comprehensive validation of Story #8 acceptance criteria. The automated test workflow provides quick verification, while manual test cases cover edge cases and error scenarios.

**Ready for Production**: Once all tests pass, Story #8 implementation is production-ready and can be integrated with downstream workflows (Story #11).
