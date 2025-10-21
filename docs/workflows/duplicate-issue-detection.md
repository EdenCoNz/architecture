# Duplicate Issue Detection

## Overview

The create-issue-from-log workflow includes automatic duplicate detection to prevent creating multiple issues for the same failure. This feature intelligently identifies when a workflow failure has already been reported and labels the existing issue instead of creating a duplicate.

## How It Works

### Detection Flow

1. **Metadata Extraction**: After populating the issue template, the workflow extracts all relevant metadata fields from the log file
2. **Query Open Issues**: Retrieves all open issues in the repository (up to 100 most recent)
3. **Field-by-Field Comparison**: Compares the following fields between the current failure and existing issues:
   - `title`
   - `featureID`
   - `featureName`
   - `jobName`
   - `stepName`
   - `logLineNumbers`
4. **Branch Filtering**: First filters issues by the same source branch (featureName) for efficiency
5. **Exact Match Detection**: If ALL fields match exactly, the issue is considered a duplicate
6. **Label and Skip**: When a duplicate is found:
   - The existing issue is labeled with "attempted"
   - No new issue is created
   - The workflow summary reports the duplicate detection

### Workflow Location

The duplicate detection is implemented between these steps in `/home/ed/Dev/architecture/.github/workflows/create-issue-from-log.yml`:

- **After**: Step "Populate issue log template with metadata" (line 267-343)
- **Before**: Step "Create tracking issue" (line 513-548)

This placement ensures:
- All metadata has been extracted and is available for comparison
- We can skip issue creation if a duplicate is found
- The workflow completes successfully in both scenarios

## Fields Checked

All of the following fields must match for an issue to be considered a duplicate:

| Field | Description | Example Value |
|-------|-------------|---------------|
| `title` | Issue title derived from workflow/job/step names | "Workflow Failure: Frontend CI/CD - Lint and Format Check - Run ESLint" |
| `featureID` | Feature ID extracted from branch name | "5" |
| `featureName` | Full branch name | "feature/5-add-simple-button-that-says-hello-on-main-page" |
| `jobName` | Name of the failed job | "Lint and Format Check" |
| `stepName` | Name of the failed step | "Run ESLint" |
| `logLineNumbers` | Range and count of log lines in the excerpt (NOT error line numbers) | "Lines 120-170 (error at line 145)" or "Lines 200-250 (last 50 lines, no clear error pattern)" |

### Why All Fields?

The duplicate detection requires ALL fields to match for these reasons:

- **Same failure context**: Ensures we're detecting the exact same failure scenario
- **Same branch**: Different branches may have different root causes
- **Same job/step**: Different steps failing indicate different problems
- **Precision over recall**: Better to create a duplicate than miss a unique failure

## Behavior

### When a Duplicate is Found

1. **No New Issue**: The workflow skips the "Create tracking issue" step
2. **Label Applied**: The existing issue is labeled with "attempted" to indicate another occurrence
3. **Summary Updated**: The workflow summary clearly indicates duplicate detection
4. **Graceful Completion**: The workflow completes successfully (not as a failure)

Example summary output:
```
⚠️ Duplicate issue detected - no new issue created

- Existing Issue: #76
- Issue URL: https://github.com/EdenCoNz/architecture/issues/76
- Action Taken: Added 'attempted' label to existing issue
- Log File: issue-logs/issue-log-run-12345-job-67890-step-1.md
- Workflow Run: https://github.com/EdenCoNz/architecture/actions/runs/12345

> This failure appears to be the same as an existing open issue.
> The existing issue has been labeled with 'attempted' to indicate another occurrence.
```

### When No Duplicate is Found

1. **New Issue Created**: The workflow proceeds normally to create a new tracking issue
2. **Standard Labels**: No "attempted" label is added (only present on duplicates)
3. **Summary Updated**: The workflow summary shows successful issue creation

Example summary output:
```
✓ Tracking issue created successfully

- Issue URL: https://github.com/EdenCoNz/architecture/issues/77
- Issue Number: #77
- Log File: issue-logs/issue-log-run-12345-job-67890-step-1.md
- Workflow Run: https://github.com/EdenCoNz/architecture/actions/runs/12345
```

## Error Handling

The duplicate detection includes robust error handling:

1. **Python Script Failures**: If the duplicate check script fails unexpectedly, the workflow defaults to creating a new issue (fail-safe behavior)
2. **Labeling Failures**: If adding the "attempted" label fails, a warning is logged but the workflow continues
3. **API Rate Limits**: The gh CLI respects GitHub API rate limits automatically
4. **Empty Issue Lists**: Correctly handles repositories with no open issues

## Implementation Details

### Technology Stack

- **Shell Script**: Bash for workflow step orchestration
- **Python 3**: For JSON parsing and field comparison logic
- **gh CLI**: For querying issues and adding labels
- **GitHub Actions**: Conditional step execution (`if:` conditions)

### Python Script

The duplicate detection uses a standalone Python script written to `/tmp/check_duplicates.py` at runtime. Key features:

- **Environment Variables**: Metadata passed via environment variables for safety
- **Regex Parsing**: Extracts fields from issue body using regex patterns
- **Exit Codes**: Returns 0 for duplicate found, 1 for no duplicate (standard Unix convention)
- **Stderr Output**: Outputs match results to stderr for reliable parsing

### Conditional Execution

The workflow uses GitHub Actions conditional execution:

```yaml
- name: Create tracking issue
  if: steps.check-duplicates.outputs.create_issue == 'true'
```

This ensures the issue creation step only runs when no duplicate is found.

## Testing

A comprehensive test suite is available at `/home/ed/Dev/architecture/.github/workflows/test-duplicate-detection.sh`.

### Test Coverage

The test suite validates:

1. **Exact Duplicate Detection**: Verifies exact matches are correctly identified
2. **Different Branch**: Ensures issues from different branches are not considered duplicates
3. **Different Step**: Ensures different failing steps are not considered duplicates
4. **Empty Issue List**: Handles repositories with no open issues
5. **Multiple Issues**: Correctly identifies the matching issue among multiple candidates

### Running Tests

```bash
cd /home/ed/Dev/architecture
chmod +x .github/workflows/test-duplicate-detection.sh
./.github/workflows/test-duplicate-detection.sh
```

Expected output:
```
Testing duplicate detection logic...

Test 1: Exact duplicate detection
==================================
✓ PASS: Exact duplicate was correctly detected

Test 2: Different branch (no duplicate)
========================================
✓ PASS: Different branch correctly not detected as duplicate

Test 3: Different step name (no duplicate)
===========================================
✓ PASS: Different step name correctly not detected as duplicate

Test 4: Empty issue list (no duplicates)
=========================================
✓ PASS: Empty issue list correctly handled

Test 5: Multiple issues with one exact match
=============================================
✓ PASS: Correct duplicate found among multiple issues

==================================
All tests passed successfully! ✓
==================================
```

## Performance Considerations

### Query Limits

- **Open Issues Retrieved**: Limited to 100 most recent open issues
- **Rationale**: Most projects don't have 100+ open workflow failure issues. If they do, older issues should likely be closed
- **Optimization**: Issues are filtered by branch first, reducing comparison overhead

### Time Complexity

- **Issue Query**: O(1) - single API call with limit
- **Field Extraction**: O(n) where n = number of open issues (max 100)
- **Total Runtime**: Typically < 2 seconds for < 100 issues

### Memory Usage

- **Issue JSON**: Stored in memory temporarily
- **Python Script**: Written to `/tmp/check_duplicates.py` (< 2KB)
- **Total Memory**: Minimal impact on runner resources

## Maintenance

### Updating Field Definitions

To add or remove fields from duplicate detection:

1. **Update Extraction**: Modify the grep commands in "Check for duplicate issues" step (lines 356-361)
2. **Update Environment**: Add/remove export statements for Python script (lines 460-465)
3. **Update Python Logic**: Modify the comparison logic in Python script (lines 434-441)
4. **Update Tests**: Add test cases for the new field in test-duplicate-detection.sh
5. **Update Documentation**: Update this document and the field table above

### Label Customization

To change the "attempted" label:

1. **Update Label Name**: Change `--add-label "attempted"` in "Label duplicate issue" step (line 501)
2. **Create Label**: Ensure the label exists in your repository (Settings → Labels)
3. **Update Documentation**: Update this document with the new label name

## Troubleshooting

### Duplicate Not Detected

**Problem**: Two identical failures created separate issues

**Diagnosis**:
1. Check if ALL fields match exactly (including whitespace)
2. Verify the existing issue is still OPEN (closed issues are not checked)
3. Check if issue count exceeds 100 (older issues may not be retrieved)

**Solution**:
- Manually close one issue and label the other with "attempted"
- Review field extraction logic if whitespace mismatches are common

### False Positive Detection

**Problem**: Different failures incorrectly detected as duplicates

**Diagnosis**:
1. Review the fields being compared - are they specific enough?
2. Check if `logLineNumbers` is always the same or varies based on log context
   - Note: `logLineNumbers` represents the range of lines extracted (e.g., "Lines 120-170"), not the specific error line
   - Different log excerpts may have different ranges but represent the same underlying failure

**Solution**:
- Consider adding more specific fields (e.g., error message hash)
- Review if the log extraction logic is consistently identifying the same failure context

### Label Not Applied

**Problem**: Duplicate detected but "attempted" label not added

**Diagnosis**:
1. Check workflow permissions (`issues: write` required)
2. Verify the label exists in the repository
3. Check GitHub API rate limits

**Solution**:
- Add label manually to the issue
- Check workflow run logs for specific error messages
- Ensure proper permissions in workflow YAML

## Security Considerations

### Input Validation

- **Field Extraction**: Uses simple grep/sed to avoid command injection
- **Python Script**: Uses environment variables instead of direct string interpolation
- **Issue Bodies**: Parsed as JSON and regex - no shell execution of user content

### Permissions

Required workflow permissions:
```yaml
permissions:
  contents: read
  issues: write
  actions: read
```

- **issues: write**: Required to add "attempted" label
- **contents: read**: Required to checkout repository
- **actions: read**: Required to download artifacts

### API Token

- Uses default `GITHUB_TOKEN` with scoped permissions
- Token automatically expires after workflow run
- No long-lived credentials required

## Future Enhancements

### Potential Improvements

1. **Fuzzy Matching**: Allow minor differences in log line numbers
2. **Time-based Filtering**: Only compare issues created within last N days
3. **Auto-close on Fix**: Automatically close duplicates when original is closed as fixed
4. **Duplicate Count**: Track number of times an issue has been attempted
5. **Smart Deduplication**: Use ML/heuristics for more intelligent matching

### Known Limitations

1. **Closed Issues**: Only checks open issues (by design)
2. **100 Issue Limit**: Only checks most recent 100 open issues
3. **Exact Match Only**: No fuzzy matching or similarity scoring
4. **Single Label**: Only adds one label ("attempted")

## References

- **Workflow File**: `/home/ed/Dev/architecture/.github/workflows/create-issue-from-log.yml`
- **Test Suite**: `/home/ed/Dev/architecture/.github/workflows/test-duplicate-detection.sh`
- **Issue Template**: `/home/ed/Dev/architecture/docs/templates/issue-log-template.md`
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **gh CLI Docs**: https://cli.github.com/manual/
