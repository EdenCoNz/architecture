# Duplicate Issue Detection

## Overview

The Bug Logger workflow (`bug-logger.yml`) includes intelligent duplicate detection to prevent creating redundant GitHub issues for the same CI/CD failure. This feature saves time and reduces issue clutter by identifying when a failure is a duplicate of an existing issue.

This reusable workflow is called by CI/CD workflows (such as `frontend-ci.yml` and `backend-ci.yml`) when jobs fail.

## How It Works

The duplicate detection process runs in the `Check for duplicate issues` step and follows a **streamlined field-based comparison approach**:

### Stage 1: Search for Existing Open Issues

```bash
gh issue list \
  --repo "$REPO" \
  --state open \
  --search "\"$CURRENT_TITLE\" in:title" \
  --json number,title,body \
  --limit 10
```

- Queries GitHub for **open** issues with matching titles (same branch and job)
- If no existing issues are found → **Creates new issue immediately**
- If issues are found → **Proceeds to Stage 2**

### Stage 2: Field-Based Comparison

Extracts and compares metadata fields from each existing issue's body:

| Field | Description | Source |
|-------|-------------|--------|
| `title` | Issue title | `[branch] job_name job failed` |
| `featureID` | Feature/bug branch number | Extracted from `feature/{id}` or `bug/{id}` branch name |
| `jobName` | CI job that failed | e.g., "Build Application", "TypeScript Type Check" |
| `stepName` | Specific step that failed | e.g., "Run TypeScript type check", "Build application" |
| `logLineNumbers` | Log line range | e.g., "L100-L150" indicating the failure location in logs |

**Comparison Logic:**

```bash
if [ "$CURRENT_FEATURE_ID" = "$PREV_FEATURE_ID" ] && \
   [ "$CURRENT_JOB_NAME" = "$PREV_JOB_NAME" ] && \
   [ "$CURRENT_STEP_NAME" = "$PREV_STEP_NAME" ] && \
   [ "$CURRENT_LOG_LINES" = "$PREV_LOG_LINES" ]; then
  # ALL fields match → DUPLICATE
else
  # ANY field differs → NOT a duplicate
fi
```

**Result:**
- If **ALL** fields match → **Duplicate detected** (skip issue creation)
- If **ANY** field differs → **NOT a duplicate** (create new issue + mark old issue as fix-pending)

### Stage 3: Fix Tracking

When a new issue is created (meaning the fields don't match), this indicates the failure has changed, suggesting the previous issue may have been fixed:

**Fix Tracking Logic:**

```bash
if issue_exists && fields_differ; then
  # Mark the old issue with "fix-pending" label
  gh issue edit $OLD_ISSUE --add-label "fix-pending"

  # Add explanatory comment
  gh issue comment $OLD_ISSUE \
    --body "A new, different failure has been detected. This suggests the original issue may have been resolved."
fi
```

**What This Means:**
- When log line numbers change, it usually means the failure is occurring at a different point in the workflow
- This suggests the original failure was resolved, but a new issue has emerged
- The `fix-pending` label helps track issues that may have been inadvertently fixed

## Duplicate Detection Decision Tree

```
Start: CI/CD Job Fails
         |
         v
[Search for open issues with matching title]
         |
         +---> No issues found? --> CREATE NEW ISSUE
         |
         v
[Found existing open issue(s)]
         |
         v
[Extract fields from each issue:]
  - featureID
  - jobName
  - stepName
  - logLineNumbers
         |
         v
[Compare ALL fields]
         |
         +---> ALL fields match? --> DUPLICATE DETECTED
         |                            - Skip issue creation
         |                            - Reference existing issue
         |
         v
[ANY field differs]
         |
         v
CREATE NEW ISSUE
  +---> Mark old issue as "fix-pending"
         (suggests previous issue was fixed)
```

## Key Design Decisions

### Why Log Line Numbers?

Log line numbers provide a precise indicator of where in the workflow the failure occurred:

- **Same line numbers** = Same failure point = Likely the same issue
- **Different line numbers** = Different failure point = Likely a different issue (or the same issue manifesting differently)

This is more reliable than comparing log content because:
1. Log content can vary slightly between runs (timestamps, PIDs, etc.)
2. Line numbers are stable and directly indicate the failure location
3. Simpler and faster than deep log content analysis

### Why Compare ALL Fields?

All five fields must match for a duplicate to be detected:

- **Title**: Ensures same branch and job
- **Feature ID**: Ensures same feature/bug being worked on
- **Job Name**: Ensures same CI/CD job failed
- **Step Name**: Ensures same step within the job failed
- **Log Line Numbers**: Ensures failure occurred at the same location

If ANY field differs, it's considered a new issue because it represents a meaningfully different failure.

## Output and Logging

### Console Output Format

The duplicate detection step produces **clear, structured console output**:

```
==========================================
Starting Duplicate Detection
==========================================

Current failure context:
  Title: [feature/6-dark-mode] Build Application job failed
  Feature ID: 6
  Job Name: Build Application
  Step Name: Build application
  Log Lines: L100-L150

Searching for existing open issues...
Found 1 open issues with similar titles

Analyzing existing issues for duplicates...

Checking issue #42...
  Previous issue context:
    Feature ID: 6
    Job Name: Build Application
    Step Name: Build application
    Log Lines: L100-L150
  Result: DUPLICATE DETECTED (all fields match)

==========================================
Duplicate Detection Complete
  Is Duplicate: true
  Duplicate Issue: #42
==========================================
```

**Alternative: When fields differ (new issue created with fix tracking):**

```
==========================================
Starting Duplicate Detection
==========================================

Current failure context:
  Title: [feature/6-dark-mode] Build Application job failed
  Feature ID: 6
  Job Name: Build Application
  Step Name: Build application
  Log Lines: L200-L250

Searching for existing open issues...
Found 1 open issues with similar titles

Analyzing existing issues for duplicates...

Checking issue #42...
  Previous issue context:
    Feature ID: 6
    Job Name: Build Application
    Step Name: Build application
    Log Lines: L100-L150
  Result: NOT a duplicate (fields differ)
  Action: Will mark issue #42 as fix-pending (different failure detected)

==========================================
Duplicate Detection Complete
  Is Duplicate: false
  Old Issue to Mark: #42
==========================================
```

### Workflow Summary Output

The workflow summary (visible in the GitHub Actions UI) shows:

**When duplicate is detected:**
```markdown
## Bug Logging Summary

### Duplicate Issue Detected

This failure is a duplicate of existing issue [#42](https://github.com/owner/repo/issues/42)

**No new issue was created.**

### Duplicate Detection Details
- Feature ID: 6
- Job Name: Build Application
- Step Name: Build application
- Log Line Numbers: L100-L150

All fields matched the existing issue, indicating this is the same failure.

A comment has been added to PR #15
```

**When new issue is created (with fix tracking):**
```markdown
## Bug Logging Summary

### New Issue Created

A GitHub issue has been created for the CI/CD failure:

- Issue: https://github.com/owner/repo/issues/43
- Branch: feature/6-dark-mode
- Failed Job: Build Application
- Failed Step: Build application
- Log Lines: L200-L250

### Fix Tracking

Issue [#42](https://github.com/owner/repo/issues/42) has been marked as `fix-pending` because this represents a different failure, suggesting the previous issue may have been resolved.

A comment has been added to PR #15
```

**When new issue is created (no old issue):**
```markdown
## Bug Logging Summary

### New Issue Created

A GitHub issue has been created for the CI/CD failure:

- Issue: https://github.com/owner/repo/issues/43
- Branch: feature/6-dark-mode
- Failed Job: Build Application
- Failed Step: Build application
- Log Lines: L100-L150

A comment has been added to PR #15
```

## Benefits

### 1. Reduces Issue Clutter
- Prevents multiple issues for the same recurring failure
- Makes issue tracking more manageable
- Easier to identify unique failures vs. recurring ones

### 2. Fast and Simple
- **Field-based comparison** is extremely fast (no log parsing required)
- Simple string matching on structured metadata
- No complex algorithms or normalization needed

### 3. Accurate Duplicate Detection
- **Five-field comparison** provides high accuracy
- Log line numbers provide precise failure location matching
- All fields must match to be considered a duplicate (no false positives)

### 4. Automatic Fix Tracking
- **fix-pending label** automatically marks potentially resolved issues
- Helps identify when an issue may have been inadvertently fixed
- Provides visibility into issue resolution patterns

### 5. Clear Logging
- Detailed console output shows decision-making process
- Easy to debug false positives/negatives
- Workflow summary provides high-level overview

## Configuration

### Adjusting Search Limit

The workflow searches for the last 10 open issues with matching titles:

```bash
gh issue list \
  --state open \
  --search "\"$CURRENT_TITLE\" in:title" \
  --limit 10
```

**To adjust:**
- Increase `--limit 10` to check more historical issues
- Decrease to improve performance (only check most recent issues)

**Recommendations:**
- **10** (default): Good balance for most projects
- **20-30**: Use if you have high issue creation rate
- **5**: Use if you want faster duplicate detection with fewer comparisons

## Edge Cases and Limitations

### Edge Case 1: Multiple Simultaneous Failures

**Scenario:** Two PRs fail at the same time with identical errors

**Behavior:**
- First workflow creates issue
- Second workflow detects duplicate and skips
- Both workflows reference the same issue

**Limitation:** If both workflows run **exactly** simultaneously, there's a small race condition window where both might create issues.

### Edge Case 2: Field Extraction Failure

**Scenario:** Previous issue exists but fields cannot be extracted (malformed issue body)

**Behavior:**
- Workflow logs warning: "Could not extract fields from previous issue"
- Creates new issue (fail-safe: better to create a duplicate than miss a new issue)

### Edge Case 3: First Failure on Feature Branch

**Scenario:** First time a feature branch fails CI

**Behavior:**
- No existing open issues found with matching title
- Immediately creates new issue (fast path)

### Edge Case 4: Different Failures on Same Feature

**Scenario:** Feature #6 fails on "Build" job, then later fails on "Docker" job

**Behavior:**
- Job name differs
- Creates separate issue for each failure
- First issue is NOT marked as fix-pending (different job = clearly different issue)

### Edge Case 5: Same Failure, Different Log Lines

**Scenario:** Feature #6 fails on "Build" job at line 100, then later at line 200

**Behavior:**
- Log line numbers differ
- Creates new issue for the new failure location
- Marks old issue as fix-pending (suggests the original failure was resolved, but a new issue emerged)

## Troubleshooting

### Issue: Too many duplicate issues are being created

**Possible causes:**
- Fields are extracting incorrectly (regex patterns not matching issue body format)
- Issue title format changed
- Manual edits to issue body breaking field extraction

**Solutions:**
1. Verify bug-log-template.md format matches field extraction patterns in bug-logger.yml
2. Check workflow logs for field extraction warnings
3. Ensure issue body uses the correct table format with pipe-separated fields

### Issue: Legitimate new issues are being skipped as duplicates

**Possible causes:**
- Log line numbers are not changing between failures (extraction logic issue)
- Step name extraction is failing (always returns same value)

**Solutions:**
1. Review log line number extraction logic in fetch-logs step
2. Verify step name extraction from job JSON
3. Check that failed step is correctly identified

### Issue: Old issues are being marked fix-pending incorrectly

**Possible causes:**
- Log line numbers are changing frequently (unstable extraction)
- Multiple issues open with same title

**Solutions:**
1. Review log line extraction logic (should be stable for same failure)
2. Increase search limit to check more issues
3. Consider closing old resolved issues to reduce false positives

## Security Considerations

### Permissions Required

```yaml
permissions:
  contents: read   # Read repository content
  issues: write    # Create, edit, and label issues
  actions: read    # Fetch job logs and job information
```

### Token Usage

The workflow uses the default `GITHUB_TOKEN`:

```yaml
env:
  GH_TOKEN: ${{ github.token }}
```

**Security notes:**
- Token is automatically provided by GitHub Actions
- Token has repository-scoped permissions only
- Token expires after workflow completes
- No need to configure additional secrets

### Data Privacy

**What data is compared:**
- Issue metadata (feature ID, job name, step name, log line numbers)
- All data stays within GitHub (not sent to external services)

**What data is stored:**
- Temporary files created during workflow execution
- Files are automatically cleaned up by GitHub Actions runner
- No persistent storage beyond the workflow run

## Related Files

- **Workflow:** `.github/workflows/bug-logger.yml`
- **Bug Template:** `docs/templates/bug-log-template.md`
- **This Documentation:** `.github/workflows/DUPLICATE_DETECTION.md`

## Future Enhancements

Potential improvements to duplicate detection:

### 1. Smarter Log Line Extraction

Improve log line number extraction to be more precise:
- Extract actual line numbers from GitHub Actions log format
- Calculate line numbers relative to step start/end
- Handle multi-line errors more accurately

### 2. Automatic Issue Closing

When a fix-pending issue is validated as resolved:
- Automatically close the issue after verification period
- Add comment with resolution details

### 3. Duplicate Detection Across Branches

Detect duplicates across **different feature branches** if the error is identical (e.g., infrastructure failure affecting multiple branches).

### 4. Time-Based Deduplication

Only consider issues from the **last N days** as potential duplicates, automatically creating new issues for old recurring failures.

### 5. Label-Based Filtering

Support filtering by additional labels (e.g., only check issues with specific severity or component labels).

---

**Documentation Version:** 2.0 (Field-Based Duplicate Detection)
**Last Updated:** 2025-10-20

