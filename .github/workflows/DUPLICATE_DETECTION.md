# Duplicate Issue Detection

## Overview

The Frontend CI/CD workflow (`frontend-ci.yml`) includes intelligent duplicate detection to prevent creating redundant GitHub issues for the same CI/CD failure. This feature saves time and reduces issue clutter by identifying when a failure is a duplicate of an existing issue.

## How It Works

The duplicate detection process runs in the `Check for duplicate issues` step and follows a **multi-stage progressive approach**:

### Stage 1: Fetch Latest CI Failure Issue

```bash
gh issue list \
  --repo "$REPO" \
  --label "ci-failure" \
  --state open \
  --limit 1
```

- Queries GitHub for the most recent **open** issue with the `ci-failure` label
- If no existing issues are found → **Creates new issue immediately**
- If an issue is found → **Proceeds to Stage 2**

### Stage 2: Preliminary Checks (Fast Comparison)

Extracts and compares metadata fields from the latest issue's body:

| Field | Description | Source |
|-------|-------------|--------|
| `featureID` | Feature branch number | Extracted from `feature/{id}` branch name |
| `jobName` | CI job that failed | e.g., "Build Application", "Docker Build" |
| `stepName` | Specific step that failed | e.g., "Run TypeScript type check" |

**Comparison Logic:**

```bash
if [ "$FEATURE_ID" != "$PREV_FEATURE_ID" ]; then
  # Different feature → NOT a duplicate
elif [ "$FAILED_JOB" != "$PREV_JOB_NAME" ]; then
  # Different job → NOT a duplicate
elif [ "$FAILED_STEP" != "$PREV_STEP_NAME" ]; then
  # Different step → NOT a duplicate
else
  # All metadata matches → Proceed to Stage 3
fi
```

**Result:**
- If **any** field differs → **Creates new issue immediately** (fast path)
- If **all** fields match → **Proceeds to Stage 3** (deep comparison)

### Stage 3: Deep Log Comparison

When metadata matches, the workflow performs detailed log analysis using **three strategies**:

#### Strategy 1: Head/Tail Comparison

Compares the first 10 and last 10 lines of logs:

```bash
head -10 prev_log.txt > prev_log_head.txt
tail -10 prev_log.txt > prev_log_tail.txt
head -10 current_log.txt > current_log_head.txt
tail -10 current_log.txt > current_log_tail.txt

diff -q prev_log_head.txt current_log_head.txt  # Check first 10 lines
diff -q prev_log_tail.txt current_log_tail.txt  # Check last 10 lines
```

**Why this works:**
- Catches identical error patterns (same start and end)
- Ignores minor timing/timestamp differences in the middle
- Fast and effective for most duplicate scenarios

#### Strategy 2: Hash Comparison (Exact Match)

Computes MD5 hashes of the complete logs:

```bash
PREV_HASH=$(md5sum prev_log.txt | cut -d' ' -f1)
CURRENT_HASH=$(md5sum current_log.txt | cut -d' ' -f1)
```

**Why this works:**
- Detects **100% identical logs**
- Most reliable indicator of exact duplicate failure
- Extremely fast (hash computation is efficient)

#### Strategy 3: Line-by-Line Similarity Analysis

Calculates the percentage of shared content between logs:

```bash
# Normalize logs (remove line numbers, sort lines)
sed 's/^[[:space:]]*[0-9]*[[:space:]]*|[[:space:]]*//' prev_log.txt | sort > prev_log_normalized.txt
sed 's/^[[:space:]]*[0-9]*[[:space:]]*|[[:space:]]*//' current_log.txt | sort > current_log_normalized.txt

# Count total unique lines in both logs
TOTAL_UNIQUE_LINES=$(cat prev_log_normalized.txt current_log_normalized.txt | sort -u | wc -l)

# Count common lines between logs
COMMON_LINES=$(comm -12 prev_log_normalized.txt current_log_normalized.txt | wc -l)

# Calculate similarity percentage
SIMILARITY_PCT=$((COMMON_LINES * 100 / TOTAL_UNIQUE_LINES))
```

**Why this works:**
- Handles logs with minor variations (timestamps, PIDs, etc.)
- Provides a **similarity score** (0-100%)
- Catches duplicate failures even when logs aren't byte-for-byte identical

### Stage 4: Final Duplicate Decision

A failure is considered a **duplicate** if **ANY** of these conditions are met:

1. **Exact match**: Hash comparison shows 100% identical logs
2. **Head/tail match**: Both first AND last 10 lines match exactly
3. **High similarity**: Similarity score ≥ 80%

```bash
if [ "$EXACT_MATCH" = true ]; then
  IS_DUPLICATE=true
elif [ "$HEAD_MATCH" = true ] && [ "$TAIL_MATCH" = true ]; then
  IS_DUPLICATE=true
elif [ "$SIMILARITY_PCT" -ge 80 ]; then
  IS_DUPLICATE=true
else
  IS_DUPLICATE=false
fi
```

**Result:**
- **Duplicate detected** → **Skip issue creation**, reference existing issue
- **Not a duplicate** → **Create new issue**

## Output and Logging

### Console Output Format

The duplicate detection step produces **clear, structured console output**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting Duplicate Detection Process
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current Failure Context:
  Feature ID:   2
  Job Name:     Build Application
  Step Name:    Build application

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1: Fetching Latest CI Failure Issue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Found latest issue: #42

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 2: Preliminary Checks (Fast Comparison)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Previous Issue #42 Context:
  Feature ID:   '2'
  Job Name:     'Build Application'
  Step Name:    'Build application'

Comparing metadata fields...
✅ Feature ID matches: 2
✅ Job name matches: 'Build Application'
✅ Step name matches: 'Build application'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Preliminary Checks Result: PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  Metadata matches - proceeding to log comparison

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 3: Deep Log Comparison
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Extracting log excerpt from issue #42...
Previous log excerpt: 156 lines
Current log excerpt:  156 lines

Analyzing log similarity...

Strategy 1: Comparing first and last 10 lines...
  ✅ First 10 lines match
  ✅ Last 10 lines match

Strategy 2: Hash comparison (exact match)...
  Previous log hash: a3f5d8c9e2b1f4a6
  Current log hash:  a3f5d8c9e2b1f4a6
  ✅ Logs are identical (exact match)

Strategy 3: Line-by-line similarity analysis...
  Total unique lines: 156
  Common lines:       156
  Similarity:         100%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Final Duplicate Decision
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Decision Criteria:
  - Exact match:           true
  - Head/tail match:       Head=true, Tail=true
  - Similarity threshold:  100% (threshold: 80%)

🔍 Duplicate detected: Exact log match

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏭️  SKIPPING ISSUE CREATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This failure is a duplicate of existing issue #42
Existing issue URL: https://github.com/owner/repo/issues/42
```

### Workflow Summary Output

The workflow summary (visible in the GitHub Actions UI) shows:

**When duplicate is detected:**
```markdown
## Bug Tracking Summary

⏭️  **Issue Creation Skipped** - Duplicate detected

This failure is a duplicate of existing issue [#42](https://github.com/owner/repo/issues/42)

### Duplicate Detection Details
- **Metadata Match**: Feature ID, Job Name, and Step Name all matched
- **Log Comparison**: Logs are substantially similar (see workflow logs for details)
- **Reason**: `duplicate_detected`

### Failure Information
- **Feature**: feature/2-test (#2)
- **Failed Job**: Build Application
- **Failed Step**: Build application
- **PR**: #15
```

**When new issue is created:**
```markdown
## Bug Tracking Summary

✅ **GitHub Issue Created**: https://github.com/owner/repo/issues/43
✅ **Bug log generated** from template

### Duplicate Detection
- **Check Performed**: Yes
- **Result**: Not a duplicate (new issue created)
- **Reason**: `logs_differ`

### Failure Information
- **Feature**: feature/2-test (#2)
- **Failed Job**: Build Application
- **Failed Step**: Build application
- **PR**: #15
```

## Skip Reasons

The workflow outputs different `skip_reason` values to explain why a decision was made:

| Skip Reason | Meaning | Action Taken |
|------------|---------|--------------|
| `no_existing_issues` | No open ci-failure issues found | **Create new issue** |
| `metadata_mismatch` | Feature ID, Job Name, or Step Name differs | **Create new issue** |
| `log_extraction_failed` | Could not extract log from previous issue | **Create new issue** |
| `logs_differ` | Logs are significantly different | **Create new issue** |
| `duplicate_detected` | Logs are substantially similar | **Skip issue creation** |

## Benefits

### 1. Reduces Issue Clutter
- Prevents multiple issues for the same recurring failure
- Makes issue tracking more manageable
- Easier to identify unique failures vs. recurring ones

### 2. Fast Performance
- **Preliminary checks** (metadata comparison) avoid expensive log analysis when possible
- Only performs deep log comparison when metadata matches
- Uses efficient algorithms (hash comparison, line counting)

### 3. Comprehensive Detection
- **Three complementary strategies** catch duplicates in different scenarios:
  - Exact matches (hash comparison)
  - Similar errors (head/tail comparison)
  - Partial matches (similarity percentage)

### 4. Clear Logging
- Detailed console output shows decision-making process
- Easy to debug false positives/negatives
- Workflow summary provides high-level overview

### 5. Automatic Label Management
- Creates `ci-failure` label if it doesn't exist
- All CI failure issues are automatically labeled for easy filtering
- Labels are used to query for latest issue

## Tuning the Detection Threshold

The similarity threshold is currently set to **80%**. You can adjust this in the workflow:

```bash
# Current threshold
elif [ "$SIMILARITY_PCT" -ge 80 ]; then

# More strict (fewer duplicates detected, more issues created)
elif [ "$SIMILARITY_PCT" -ge 90 ]; then

# More lenient (more duplicates detected, fewer issues created)
elif [ "$SIMILARITY_PCT" -ge 70 ]; then
```

**Recommendations:**
- **80%** (default): Good balance for most projects
- **90%**: Use if you want to be conservative (prefer creating issues)
- **70%**: Use if you have very noisy CI failures and want aggressive deduplication

## Edge Cases and Limitations

### Edge Case 1: Multiple Simultaneous Failures

**Scenario:** Two PRs fail at the same time with identical errors

**Behavior:**
- First workflow creates issue
- Second workflow detects duplicate and skips
- Both workflows reference the same issue

**Limitation:** If both workflows run **exactly** simultaneously, there's a small race condition window where both might create issues.

### Edge Case 2: Log Extraction Failure

**Scenario:** Previous issue exists but log excerpt cannot be extracted (malformed issue body)

**Behavior:**
- Workflow logs warning: "Could not extract log excerpt from previous issue"
- Creates new issue (fail-safe: better to create a duplicate than miss a new issue)
- Sets `skip_reason=log_extraction_failed`

### Edge Case 3: First Failure on Feature Branch

**Scenario:** First time a feature branch fails CI

**Behavior:**
- No existing ci-failure issues found
- Immediately creates new issue (fast path)
- Sets `skip_reason=no_existing_issues`

### Edge Case 4: Different Failures on Same Feature

**Scenario:** Feature #2 fails on "Build" job, then later fails on "Docker" job

**Behavior:**
- Metadata differs (different job name)
- Creates separate issue for each failure
- Sets `skip_reason=metadata_mismatch`

## Troubleshooting

### Issue: Too many duplicates are being created

**Possible causes:**
- Similarity threshold is too high (>80%)
- Logs have high variance (timestamps, random IDs, etc.)
- Metadata fields are not matching correctly

**Solutions:**
1. Lower similarity threshold to 70%
2. Improve log normalization (remove more variable content)
3. Check metadata extraction regex patterns

### Issue: Legitimate new issues are being skipped

**Possible causes:**
- Similarity threshold is too low (<80%)
- Different errors produce similar logs
- Hash comparison is too strict

**Solutions:**
1. Raise similarity threshold to 90%
2. Review log comparison strategies
3. Add additional metadata fields for comparison

### Issue: Log extraction fails

**Possible causes:**
- Issue template format changed
- Manual edits to issue body
- Different template version

**Solutions:**
1. Verify issue template format in `docs/templates/bug-log-template.md`
2. Ensure "## Failed Step Log Excerpt" section exists
3. Check that code blocks use triple backticks correctly

## Security Considerations

### Permissions Required

```yaml
permissions:
  contents: read   # Read repository content
  issues: write    # Create and label issues
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
- Issue metadata (feature ID, job name, step name)
- Log excerpts from failed CI steps
- All data stays within GitHub (not sent to external services)

**What data is stored:**
- Temporary log files created during comparison
- Files are automatically cleaned up by GitHub Actions runner
- No persistent storage beyond the workflow run

## Future Enhancements

Potential improvements to duplicate detection:

### 1. Multi-Issue Comparison
Currently compares against **only the latest** ci-failure issue. Could be enhanced to check the **last N issues** (e.g., last 5) to catch duplicates even if other issues were created in between.

### 2. Machine Learning Similarity
Use more sophisticated similarity algorithms:
- Levenshtein distance for log comparison
- TF-IDF vectorization for log content
- Cosine similarity for semantic comparison

### 3. Auto-Close Duplicates
When a duplicate is detected, automatically add a comment to the existing issue linking to the new failure run, rather than creating a new issue.

### 4. Duplicate Detection Across Branches
Detect duplicates across **different feature branches** if the error is identical (e.g., infrastructure failure affecting multiple branches).

### 5. Time-Based Deduplication
Only consider issues from the **last N days** as potential duplicates, automatically creating new issues for old recurring failures.

## Related Files

- **Workflow:** `.github/workflows/frontend-ci.yml`
- **Bug Template:** `docs/templates/bug-log-template.md`
- **Secrets Documentation:** `.github/workflows/.env`
- **This Documentation:** `.github/workflows/DUPLICATE_DETECTION.md`
