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

When metadata matches, the workflow performs detailed log analysis using **three strategies** with **intelligent normalization**:

#### Log Normalization: Semantic Duplicate Detection

Before comparison (in Strategies 2 and 3), logs are **normalized** to remove run-specific identifiers while preserving the underlying error pattern. This enables **semantic duplicate detection** rather than just literal comparison.

**What is Preserved:**
- Line numbers (format: `   1 | content`)
- Sequential order (no sorting during normalization)
- Error messages and codes
- Stack traces and file paths
- Command outputs

**What is Normalized (Replaced with Placeholders):**

| Pattern | Example | Replaced With | Regex Pattern |
|---------|---------|--------------|---------------|
| **UUIDs** | `f47ac10b-58cc-4372-a567-0e02b2c3d479` | `<UUID>` | `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` |
| **Git SHAs/Hashes** | `a3f5d8c9e2b1f4a6d7c8b9e0f1a2b3c4` | `<HASH>` | `\b[0-9a-f]{40}\b` |
| **Container IDs** | `f3d8a9b2c1e4` | `<CONTAINER_ID>` | `\b[0-9a-f]{12}\b` |
| **Process IDs** | `PID: 54321`, `process 98765` | `PID: <PID>` | `(PID\|pid\|process\|Process)\s*:?\s*[0-9]+` |
| **Build/Job Numbers** | `build #123`, `job 456` | `build <NUMBER>` | `(build\|job\|run)\s+#?[0-9]+` |
| **Temporary Paths** | `/tmp/gh-actions-abc123` | `/tmp/<TEMP>` | `/tmp/[a-zA-Z0-9_-]+` |
| **Durations** | `5.2s`, `120ms`, `3 minutes` | `<DURATION>s` | `[0-9]+(\.[0-9]+)?\s*(ms\|s\|sec\|seconds\|minutes\|min)` |
| **File Sizes** | `1.5MB`, `2048 bytes` | `<SIZE>MB` | `[0-9]+(\.[0-9]+)?\s*(B\|KB\|MB\|GB\|bytes)` |
| **Port Numbers** | `port 8080`, `PORT: 3000` | `port: <PORT>` | `(port\|PORT)[\s:]+[0-9]{2,5}` |
| **Memory Addresses** | `0x7fff5fbffb40` | `<ADDR>` | `0x[0-9a-f]+` |

**Normalization Function:**

```bash
normalize_log() {
  local input_file="$1"
  local output_file="$2"

  cat "$input_file" | \
    sed -E 's/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/<UUID>/g' | \
    sed -E 's/\b[0-9a-f]{40}\b/<HASH>/g' | \
    sed -E 's/\b[0-9a-f]{12}\b/<CONTAINER_ID>/g' | \
    sed -E 's/(PID|pid|process|Process)\s*:?\s*[0-9]+/\1: <PID>/g' | \
    sed -E 's/(build|job|run|Build|Job|Run)\s+#?[0-9]+/\1 <NUMBER>/g' | \
    sed -E 's|/tmp/[a-zA-Z0-9_-]+|/tmp/<TEMP>|g' | \
    sed -E 's|/var/tmp/[a-zA-Z0-9_-]+|/var/tmp/<TEMP>|g' | \
    sed -E 's/[0-9]+(\.[0-9]+)?\s*(ms|s|sec|seconds|minutes|min)\b/<DURATION>\2/g' | \
    sed -E 's/[0-9]+(\.[0-9]+)?\s*(B|KB|MB|GB|bytes)\b/<SIZE>\2/g' | \
    sed -E 's/(port|PORT|Port)[\s:]+[0-9]{2,5}\b/\1: <PORT>/g' | \
    sed -E 's/0x[0-9a-f]+/<ADDR>/g' > "$output_file"
}
```

**Example: Before vs After Normalization**

```diff
# Before normalization (Run 1):
   1 | Error in build abc123: Module not found
   2 | Process ID: 54321
   3 | Docker container: f3d8a9b2c1e4
   4 | Duration: 5.2s
   5 | Port 8080 already in use

# After normalization (Run 1):
   1 | Error in build <NUMBER>: Module not found
   2 | Process ID: <PID>
   3 | Docker container: <CONTAINER_ID>
   4 | Duration: <DURATION>s
   5 | Port <PORT> already in use

# Before normalization (Run 2):
   1 | Error in build def456: Module not found
   2 | Process ID: 98765
   3 | Docker container: a1b2c3d4e5f6
   4 | Duration: 4.8s
   5 | Port 8080 already in use

# After normalization (Run 2):
   1 | Error in build <NUMBER>: Module not found
   2 | Process ID: <PID>
   3 | Docker container: <CONTAINER_ID>
   4 | Duration: <DURATION>s
   5 | Port <PORT> already in use

# Result: Both runs normalize to IDENTICAL content → Duplicate detected ✓
```

#### Strategy 1: Exact Match (No Normalization)

Computes MD5 hashes of the **original** logs (before normalization):

```bash
PREV_HASH=$(md5sum prev_log.txt | cut -d' ' -f1)
CURRENT_HASH=$(md5sum current_log.txt | cut -d' ' -f1)
```

**Why this works:**
- Detects **100% identical logs** (byte-for-byte match)
- Most reliable indicator of exact duplicate failure
- Extremely fast (hash computation is efficient)
- **No normalization needed** - catches perfect duplicates immediately

#### Strategy 2: Head/Tail Comparison (With Normalization)

Compares the first 10 and last 10 lines of **normalized** logs:

```bash
# Normalize logs
normalize_log "prev_log.txt" "prev_log_normalized_full.txt"
normalize_log "current_log.txt" "current_log_normalized_full.txt"

# Extract head and tail
head -10 prev_log_normalized_full.txt > prev_log_head.txt
tail -10 prev_log_normalized_full.txt > prev_log_tail.txt
head -10 current_log_normalized_full.txt > current_log_head.txt
tail -10 current_log_normalized_full.txt > current_log_tail.txt

# Compare using diff
diff -q prev_log_head.txt current_log_head.txt  # Check first 10 lines
diff -q prev_log_tail.txt current_log_tail.txt  # Check last 10 lines
```

**Why this works:**
- Catches **semantic duplicates** with different run-specific IDs
- Ignores timing/timestamp/PID differences
- Fast and effective for most duplicate scenarios
- **Normalization enables semantic comparison** instead of literal comparison

#### Strategy 3: Line-by-Line Similarity Analysis (With Normalization)

Calculates the percentage of shared content between **normalized** logs:

```bash
# Use normalized logs from Strategy 2
cp prev_log_normalized_full.txt prev_log_normalized.txt
cp current_log_normalized_full.txt current_log_normalized.txt

# Count total unique lines in both logs
TOTAL_UNIQUE_LINES=$(cat prev_log_normalized.txt current_log_normalized.txt | sort -u | wc -l)

# Count common lines between logs
COMMON_LINES=$(comm -12 <(sort prev_log_normalized.txt) <(sort current_log_normalized.txt) | wc -l)

# Calculate similarity percentage
SIMILARITY_PCT=$((COMMON_LINES * 100 / TOTAL_UNIQUE_LINES))
```

**Why this works:**
- Handles logs with minor variations after normalization
- Provides a **similarity score** (0-100%)
- Catches duplicate failures even when logs have different run-specific data
- **Normalization removes noise** to focus on the actual error pattern

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

Strategy 1: Exact match comparison (no normalization)...
  Previous log hash: a3f5d8c9e2b1f4a6
  Current log hash:  d7e8f9a0b1c2d3e4
  ❌ Logs differ (proceeding to normalization)

Strategy 2: Comparing first and last 10 lines (with normalization)...
  Normalizing logs (removing run-specific identifiers)...
  ✅ Normalization complete
  ✅ First 10 lines match (after normalization)
  ✅ Last 10 lines match (after normalization)

Strategy 3: Line-by-line similarity analysis (with normalization)...
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

## Tuning the Detection System

### Tuning the Similarity Threshold

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

### Tuning the Normalization Patterns

The normalization function can be customized to match your specific CI/CD environment:

#### Adding New Normalization Patterns

If your logs contain other run-specific identifiers, add them to the `normalize_log()` function:

```bash
normalize_log() {
  local input_file="$1"
  local output_file="$2"

  cat "$input_file" | \
    # ... existing patterns ...
    sed -E 's/0x[0-9a-f]+/<ADDR>/g' | \
    # Add your custom pattern here:
    sed -E 's/your-pattern-here/<YOUR_PLACEHOLDER>/g' > "$output_file"
}
```

**Example: Normalize Kubernetes Pod Names**

```bash
# Pattern: my-app-7f6d8c9b-xyz12
sed -E 's/[a-z0-9-]+-[0-9a-f]{8,10}-[a-z0-9]{5}\b/<K8S_POD>/g'
```

**Example: Normalize AWS Request IDs**

```bash
# Pattern: req-a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6
sed -E 's/req-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/<AWS_REQ_ID>/g'
```

**Example: Normalize NPM Package Versions**

```bash
# Pattern: package@1.2.3 or package@^1.2.3
sed -E 's/(@)[0-9]+\.[0-9]+\.[0-9]+/\1<VERSION>/g'
```

#### Removing or Modifying Patterns

If a normalization pattern is too aggressive (causing false positives), you can:

1. **Remove the pattern entirely:**
   - Comment out or delete the specific `sed` line

2. **Make the pattern more specific:**
   - Add word boundaries: `\b[0-9a-f]{40}\b` instead of `[0-9a-f]{40}`
   - Add context: `container[- ]?[0-9a-f]{12}` instead of `[0-9a-f]{12}`

3. **Make the pattern less aggressive:**
   - Increase minimum length: `[0-9a-f]{16}` instead of `[0-9a-f]{12}`
   - Require prefix: `0x[0-9a-f]{8}` instead of `[0-9a-f]{8}`

#### Testing Normalization Patterns

To test if normalization is working correctly:

1. **View normalized logs in workflow output:**
   ```bash
   # Add this after normalization in the workflow
   echo "=== Normalized Previous Log (first 20 lines) ==="
   head -20 prev_log_normalized_full.txt
   echo ""
   echo "=== Normalized Current Log (first 20 lines) ==="
   head -20 current_log_normalized_full.txt
   ```

2. **Test patterns locally:**
   ```bash
   # Create test input
   echo "Error in build abc123: Module not found" > test.txt

   # Apply normalization
   sed -E 's/(build|job|run)\s+#?[0-9]+/\1 <NUMBER>/g' test.txt

   # Expected output: "Error in build <NUMBER>: Module not found"
   ```

3. **Check for over-normalization:**
   - If different errors are being marked as duplicates incorrectly
   - Review the normalized logs to see if too much information is being removed
   - Make patterns more specific to preserve distinguishing details

#### Common Patterns Library

Here are additional patterns you might want to add:

```bash
# Timestamps (ISO 8601)
sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?Z?/<TIMESTAMP>/g'

# IP Addresses (IPv4)
sed -E 's/\b([0-9]{1,3}\.){3}[0-9]{1,3}\b/<IP>/g'

# URLs (full or partial)
sed -E 's|https?://[a-zA-Z0-9._/-]+|<URL>|g'

# Email Addresses
sed -E 's/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/<EMAIL>/g'

# JWT Tokens (simplified)
sed -E 's/eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+/<JWT>/g'

# Semantic Versions
sed -E 's/\b([0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?)\b/<SEMVER>/g'

# Date (YYYY-MM-DD)
sed -E 's/\b[0-9]{4}-[0-9]{2}-[0-9]{2}\b/<DATE>/g'

# Time (HH:MM:SS)
sed -E 's/\b[0-9]{2}:[0-9]{2}:[0-9]{2}\b/<TIME>/g'

# Line numbers in stack traces (e.g., "at file.js:123:45")
sed -E 's/:[0-9]+:[0-9]+\b/:LINE:COL/g'
```

#### Performance Considerations

- Each `sed` command adds overhead to the normalization process
- The current implementation uses **piped sed commands** for readability
- For better performance with many patterns, consider:
  ```bash
  # Single sed with multiple expressions (faster)
  sed -E -e 's/pattern1/<P1>/g' \
         -e 's/pattern2/<P2>/g' \
         -e 's/pattern3/<P3>/g'
  ```

#### Validation After Tuning

After modifying normalization patterns:

1. **Check that duplicates are still detected:**
   - Trigger the same failure twice
   - Verify duplicate detection works correctly

2. **Check that different issues are not conflated:**
   - Trigger two different failures on the same feature
   - Verify both create separate issues

3. **Review workflow logs:**
   - Examine the "Analyzing log similarity" section
   - Verify similarity percentages make sense
   - Look for unexpected matches or misses

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
