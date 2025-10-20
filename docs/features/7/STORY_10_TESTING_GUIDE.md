# Story #10: Retry Detection Testing Guide

## Overview

This guide provides step-by-step instructions for testing the retry detection functionality added to the bug logger workflow in Story #10.

## Prerequisites

- Access to repository with write permissions
- Ability to trigger CI/CD workflows
- Ability to create and modify GitHub issues
- Feature branch with failing CI tests

## Test Scenarios

### Scenario 1: First Failure (No Retry)

**Objective:** Verify that the first occurrence of a failure is detected correctly and retry detection outputs are set to false.

**Steps:**

1. Create a new feature branch:
   ```bash
   git checkout -b feature/999-test-retry-detection
   ```

2. Introduce a failing test (e.g., in frontend):
   ```bash
   cd frontend
   # Add a failing test or lint error
   git add .
   git commit -m "Test: Introduce failing test for retry detection"
   git push origin feature/999-test-retry-detection
   ```

3. Create a pull request from the feature branch

4. Wait for CI to fail and bug logger to run

5. Navigate to the bug logger workflow run

6. Verify the workflow log shows:
   ```
   STEP 2: Checking for Closed Issues (Retry Detection)
   ========================================
   Found 0 closed issues with similar titles
   No closed issues found with similar titles

   Retry Detection:
     Is Retry: false
     Attempt Count: 1
   ```

7. Check the workflow summary shows:
   ```
   ### First Attempt

   This is the **first occurrence** of this failure (Attempt #1)
   ```

8. Verify the created issue exists and note its number (e.g., #99)

**Expected Results:**
- ✅ New issue created
- ✅ `is_retry` output = `false`
- ✅ `retry_of_issue` output = empty string
- ✅ `attempt_count` output = `1`
- ✅ Summary shows "First Attempt"

---

### Scenario 2: Retry After Successful Fix

**Objective:** Verify that a retry is detected when a fix was attempted and merged but CI still fails.

**Steps:**

1. Using the issue from Scenario 1 (e.g., #99):

2. Add the "pending-merge" label to the issue:
   ```bash
   gh issue edit 99 --add-label "pending-merge" --repo <owner>/<repo>
   ```

3. Close the issue:
   ```bash
   gh issue close 99 --repo <owner>/<repo>
   ```

4. Push another commit that still fails CI:
   ```bash
   # Make a change that doesn't fix the issue
   git commit --allow-empty -m "Test: Attempt fix (still failing)"
   git push origin feature/999-test-retry-detection
   ```

5. Wait for CI to fail and bug logger to run

6. Navigate to the bug logger workflow run

7. Verify the workflow log shows:
   ```
   STEP 2: Checking for Closed Issues (Retry Detection)
   ========================================
   Found 1 closed issues with similar titles

   Checking closed issue #99...
     Labels: ci-failure,pending-merge
     Result: MATCH - Same feature/job/step as current failure
     Status: This issue was marked as resolved/pending
     Action: RETRY DETECTED - This failure is a retry of issue #99

   Matching closed issues: 99
   Total attempts for this failure: 2 (including current attempt)

   Retry Detection:
     Is Retry: true
     Retry of Issue: #99
     Attempt Count: 2
   ```

8. Check the workflow summary shows:
   ```
   ### Retry Detection

   This is a **retry attempt** for a previously resolved issue.

   - Previous Issue: [#99](...) (closed)
   - Attempt Count: **2**

   A fix was previously attempted and merged, but the CI is still failing.
   ```

9. Verify a new issue was created (e.g., #100)

**Expected Results:**
- ✅ New issue created for the retry
- ✅ `is_retry` output = `true`
- ✅ `retry_of_issue` output = `"99"`
- ✅ `attempt_count` output = `2`
- ✅ Summary shows "Retry Detection" section
- ✅ Link to previous issue (#99) displayed

---

### Scenario 3: Multiple Retries

**Objective:** Verify that attempt count increments correctly across multiple retry attempts.

**Steps:**

1. Using the new issue from Scenario 2 (e.g., #100):

2. Add "pending-merge" label and close it:
   ```bash
   gh issue edit 100 --add-label "pending-merge" --repo <owner>/<repo>
   gh issue close 100 --repo <owner>/<repo>
   ```

3. Push another failing commit:
   ```bash
   git commit --allow-empty -m "Test: Second retry attempt"
   git push origin feature/999-test-retry-detection
   ```

4. Wait for CI to fail and bug logger to run

5. Verify the workflow log shows:
   ```
   Matching closed issues: 100,99
   Total attempts for this failure: 3 (including current attempt)

   Retry Detection:
     Is Retry: true
     Retry of Issue: #100
     Attempt Count: 3
   ```

6. Check the workflow summary shows attempt count of **3**

**Expected Results:**
- ✅ New issue created for third attempt
- ✅ `is_retry` output = `true`
- ✅ `retry_of_issue` output = `"100"` (most recent closed issue)
- ✅ `attempt_count` output = `3`
- ✅ Summary shows correct attempt count

---

### Scenario 4: Duplicate Detection (No Retry Check)

**Objective:** Verify that retry detection is skipped when a duplicate open issue is found.

**Steps:**

1. Ensure an open issue exists from previous scenarios (e.g., #101)

2. Push another commit with the exact same failure:
   ```bash
   git commit --allow-empty -m "Test: Trigger same failure"
   git push origin feature/999-test-retry-detection
   ```

3. Wait for CI to fail and bug logger to run

4. Verify the workflow log shows:
   ```
   STEP 1: Checking for Open Issues (Duplicates)
   ========================================
   Found 1 open issues with similar titles

   Checking issue #101...
     Result: DUPLICATE DETECTED (all fields match)

   STEP 2: Checking for Closed Issues (Retry Detection)
   ========================================
   Skipping retry detection (duplicate issue detected)

   Detection Complete
   ========================================
   Duplicate Detection:
     Is Duplicate: true
     Duplicate Issue: #101

   Retry Detection:
     Is Retry: false
     Attempt Count: 1
   ```

5. Verify no new issue was created

**Expected Results:**
- ✅ No new issue created (duplicate detected)
- ✅ `is_duplicate` output = `true`
- ✅ `is_retry` output = `false` (retry check skipped)
- ✅ `attempt_count` output = `1`
- ✅ Summary shows "Duplicate Issue Detected"

---

### Scenario 5: Different Failure (Not a Retry)

**Objective:** Verify that retry detection correctly identifies when a failure is different from previous failures.

**Steps:**

1. Using the same feature branch, introduce a failure in a different job:

2. For example, if previous failures were in the "lint" job, introduce a failure in the "typecheck" job:
   ```bash
   # Modify code to fail type checking instead of linting
   git add .
   git commit -m "Test: Different failure in typecheck job"
   git push origin feature/999-test-retry-detection
   ```

3. Wait for CI to fail in the new job

4. Verify the workflow log shows:
   ```
   STEP 2: Checking for Closed Issues (Retry Detection)
   ========================================

   Checking closed issue #99...
     Result: No match (different feature/job/step)

   Retry Detection:
     Is Retry: false
     Attempt Count: 1
   ```

5. Verify a new issue was created without retry detection

6. Verify the old open issue from the "lint" job gets marked with "fix-pending" label

**Expected Results:**
- ✅ New issue created for different failure
- ✅ `is_retry` output = `false`
- ✅ `attempt_count` output = `1`
- ✅ Old issue marked as "fix-pending"
- ✅ Summary shows "First Attempt"

---

### Scenario 6: Closed Issue Without Resolution Labels

**Objective:** Verify that closed issues without resolution labels are not considered for retry detection.

**Steps:**

1. Create a new feature branch:
   ```bash
   git checkout -b feature/998-test-no-labels
   ```

2. Introduce a failure and create an issue (e.g., #102)

3. Close the issue WITHOUT adding "pending-merge" or "fix-pending" labels:
   ```bash
   gh issue close 102 --repo <owner>/<repo>
   # Do NOT add resolution labels
   ```

4. Push another failing commit:
   ```bash
   git commit --allow-empty -m "Test: Trigger same failure after close"
   git push origin feature/998-test-no-labels
   ```

5. Verify the workflow log shows:
   ```
   Checking closed issue #102...
     Labels: ci-failure
     Status: This issue was closed without resolution labels

   Retry Detection:
     Is Retry: false
     Attempt Count: 1
   ```

**Expected Results:**
- ✅ New issue created
- ✅ `is_retry` output = `false` (no resolution labels on closed issue)
- ✅ `attempt_count` output = `1`
- ✅ Summary shows "First Attempt"

---

## Output Validation

### Checking Workflow Outputs

To verify workflow outputs are set correctly:

1. Navigate to the bug logger workflow run
2. Click on the "Create Bug Issue" job
3. Expand the "Check for duplicate issues and retry detection" step
4. Look for the output lines:
   ```
   is_retry=true
   retry_of_issue=42
   attempt_count=2
   ```

### Checking Summary Display

1. Navigate to the workflow run summary page
2. Look for the "Bug Logging Summary" section
3. Verify the retry detection information is displayed correctly

### Checking Issue Creation

1. Navigate to the repository issues page
2. Filter for issues with "ci-failure" label
3. Verify the correct issues were created/skipped based on retry detection

## Cleanup

After testing is complete:

1. Close all test issues:
   ```bash
   gh issue close 99 100 101 102 --repo <owner>/<repo>
   ```

2. Delete test branches:
   ```bash
   git branch -D feature/999-test-retry-detection
   git branch -D feature/998-test-no-labels
   git push origin --delete feature/999-test-retry-detection
   git push origin --delete feature/998-test-no-labels
   ```

3. Close any test pull requests

## Troubleshooting

### Issue: Retry detection not working

**Symptoms:**
- `is_retry` always returns `false`
- Closed issues not being found

**Solutions:**
1. Verify closed issue has "pending-merge" or "fix-pending" label
2. Check that feature ID, job name, and step name match exactly
3. Ensure issue title format matches: `[branch-name] job-name job failed`
4. Review workflow logs for detailed matching information

### Issue: Attempt count incorrect

**Symptoms:**
- Attempt count doesn't increment
- Attempt count higher than expected

**Solutions:**
1. Check how many closed issues exist with matching feature/job/step
2. Verify closed issues are being counted correctly in workflow log
3. Look for the "Matching closed issues" line in logs

### Issue: Duplicate detection interfering with retry detection

**Symptoms:**
- Retry detection always skipped
- Open duplicate issue found

**Solutions:**
1. Close or delete the open duplicate issue
2. Ensure log line numbers differ between attempts (natural variation)
3. Review Stage 1 output in workflow logs

## Expected Test Results Summary

| Scenario | is_duplicate | is_retry | retry_of_issue | attempt_count | New Issue Created |
|----------|--------------|----------|----------------|---------------|-------------------|
| 1. First Failure | false | false | "" | 1 | ✅ Yes |
| 2. Retry After Fix | false | true | "99" | 2 | ✅ Yes |
| 3. Multiple Retries | false | true | "100" | 3 | ✅ Yes |
| 4. Duplicate | true | false | "" | 1 | ❌ No |
| 5. Different Failure | false | false | "" | 1 | ✅ Yes |
| 6. Closed No Labels | false | false | "" | 1 | ✅ Yes |

## Integration Testing for Story #11

Once Story #11 is implemented, verify these outputs are consumed correctly:

1. When `is_retry=true`, bug-resolver workflow should be called
2. `retry_of_issue` should be passed as `previous_issue_number`
3. Appropriate action should be determined based on retry state
4. Labels should be applied to the retry issue

## Reporting Issues

If you encounter unexpected behavior during testing:

1. Capture the workflow run URL
2. Note the step where the issue occurs
3. Include relevant log excerpts
4. Describe expected vs actual behavior
5. Report to the development team with details

## Success Criteria

Testing is successful when:
- ✅ All 6 scenarios pass with expected results
- ✅ Workflow outputs are set correctly
- ✅ Summary displays retry information
- ✅ No errors in workflow execution
- ✅ Backward compatibility maintained (existing features work)
