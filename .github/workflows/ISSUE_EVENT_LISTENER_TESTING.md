# Issue Event Listener Workflow - Testing Guide

**Feature #7, Story #5**: Issue Event Listener Workflow Testing Documentation

## Overview

This document provides comprehensive testing instructions for the Issue Event Listener workflow, which detects CI failure issues and extracts metadata for automated fix attempts.

## Workflow Details

- **File**: `.github/workflows/issue-event-listener.yml`
- **Triggers**:
  - Issues opened
  - Issues labeled
- **Filter**: Only processes issues with the `ci-failure` label
- **Purpose**: Extract metadata from CI failure issues to enable automated fix attempts

## Prerequisites

Before testing:

1. The workflow must be merged to the repository's default branch (or testing branch)
2. You need write access to create issues and labels
3. GitHub CLI (`gh`) installed for some testing methods (optional)

## Testing Methods

### Method 1: Create a Test CI Failure Issue (Recommended)

This method simulates what the bug-logger workflow creates.

#### Step 1: Create the Test Issue

Create a new issue with the following content:

**Title:**
```
[feature/123-test-feature] lint job failed
```

**Body:**
```markdown
# Bug Log - CI/CD Failure

| Field | Value |
|-------|-------|
| title | [feature/123-test-feature] lint job failed |
| featureID | 123 |
| featureName | test-feature |
| jobName | lint |
| stepName | Run ESLint |
| logLineNumbers | L100-L150 |
| PRURL | https://github.com/yourorg/yourrepo/pull/1 |
| commitURL | https://github.com/yourorg/yourrepo/commit/abc123 |
| runURL | https://github.com/yourorg/yourrepo/actions/runs/123456 |

## Failed Step Log Excerpt

The following shows the failed step's output (lines L100-L150).

```
Error: ESLint found 5 errors
  /src/app.js:10:5 - error: 'console' is not defined
  /src/app.js:25:8 - error: Missing semicolon
```

## How to Fix

1. Review the failure logs above
2. Fix the ESLint errors in your branch
3. Push changes to trigger a new CI/CD run
```

**Labels:**
- Add the `ci-failure` label when creating the issue

#### Step 2: Verify Workflow Execution

1. Go to Actions tab
2. Look for "Issue Event Listener - CI Failure Detection" workflow run
3. Click on the run to view details

#### Step 3: Validate Expected Behavior

The workflow should:
- ✅ Detect the issue with `ci-failure` label
- ✅ Extract all metadata correctly:
  - Feature ID: `123`
  - Feature Name: `test-feature`
  - Branch Name: `feature/123-test-feature`
  - Job Name: `lint`
  - Step Name: `Run ESLint`
  - Log Lines: `L100-L150`
- ✅ Pass validation
- ✅ Generate fix context JSON
- ✅ Show success summary

### Method 2: Test Label Addition Trigger

Test the workflow's response to label changes.

#### Step 1: Create Issue Without Label

Create an issue (any content) WITHOUT the `ci-failure` label.

**Expected Behavior**: Workflow does NOT run (no matching label).

#### Step 2: Add the ci-failure Label

Add the `ci-failure` label to the issue.

**Expected Behavior**: Workflow triggers and processes the issue.

### Method 3: Test Validation Failure

Test the workflow's handling of malformed issues.

#### Step 1: Create Incomplete Issue

Create an issue with the `ci-failure` label but missing required fields:

**Title:**
```
Test issue without proper format
```

**Body:**
```markdown
This is a test issue without the metadata table.
```

**Labels:**
- `ci-failure`

#### Step 2: Verify Validation Failure

The workflow should:
- ✅ Trigger on the issue
- ✅ Fail metadata extraction
- ⚠️  Show validation errors in summary
- ✅ Provide actionable error messages

### Method 4: Using GitHub CLI (Advanced)

Create a test issue programmatically:

```bash
gh issue create \
  --title "[feature/456-cli-test] build job failed" \
  --body "$(cat <<'EOF'
# Bug Log - CI/CD Failure

| Field | Value |
|-------|-------|
| title | [feature/456-cli-test] build job failed |
| featureID | 456 |
| featureName | cli-test |
| jobName | build |
| stepName | Run npm build |
| logLineNumbers | L200-L250 |
| PRURL | https://github.com/yourorg/yourrepo/pull/2 |
| commitURL | https://github.com/yourorg/yourrepo/commit/def456 |
| runURL | https://github.com/yourorg/yourrepo/actions/runs/789012 |

## Failed Step Log Excerpt

Build failed with exit code 1.
EOF
)" \
  --label "ci-failure"
```

## Verification Checklist

After each test, verify the following in the workflow run summary:

### Success Case Checklist

- [ ] Workflow triggered on issue event
- [ ] `ci-failure` label detected correctly
- [ ] Feature ID extracted correctly
- [ ] Feature name extracted correctly
- [ ] Branch name extracted from title
- [ ] Job name extracted correctly
- [ ] Step name extracted correctly
- [ ] Log line numbers extracted correctly
- [ ] PR URL extracted correctly
- [ ] Commit URL extracted correctly
- [ ] Run URL extracted correctly
- [ ] Validation passed
- [ ] Fix context JSON generated
- [ ] Summary shows all extracted fields
- [ ] No errors in workflow logs

### Failure Case Checklist (Validation Test)

- [ ] Workflow triggered on issue event
- [ ] Metadata extraction attempted
- [ ] Validation failed with clear error messages
- [ ] Summary shows validation errors
- [ ] Workflow marked as completed (not failed)
- [ ] Error messages are actionable

## Expected Workflow Outputs

### Successful Extraction

The workflow summary should display:

```
## Issue Event Listener Summary

### Event Details
- **Event Type**: issues
- **Action**: opened (or labeled)
- **Issue**: #X
- **Title**: [feature/123-test-feature] lint job failed

### ✅ Metadata Extraction Successful

| Field | Value |
|-------|-------|
| Feature ID | 123 |
| Feature Name | test-feature |
| Branch Name | feature/123-test-feature |
| Job Name | lint |
| Step Name | Run ESLint |
| Log Lines | L100-L150 |

**Status**: Ready for automated fix attempt (Story #7)
```

### Failed Validation

The workflow summary should display:

```
## Issue Event Listener Summary

### Event Details
- **Event Type**: issues
- **Action**: opened
- **Issue**: #X
- **Title**: Test issue without proper format

### ⚠️  Metadata Validation Failed

**Issues Detected**:
- Feature ID is missing
- Job name is missing
- Branch name is missing

**Action Required**: Manual review needed. The issue may not have been created by the bug-logger workflow.
```

## Integration Testing

Once Story #7 is implemented, test the full integration:

1. Create a CI failure issue (using Method 1)
2. Verify this workflow extracts metadata
3. Verify Story #7 workflow receives the metadata
4. Verify fix command is triggered with correct context

## Debugging Tips

### Workflow Doesn't Trigger

**Possible Causes:**
- Issue doesn't have `ci-failure` label
- Workflow file not on default branch
- Permissions issue

**Solutions:**
1. Verify label is present: `gh issue view <number> --json labels`
2. Check workflow exists: `gh workflow list`
3. Check workflow runs: `gh run list --workflow=issue-event-listener.yml`

### Metadata Extraction Fails

**Possible Causes:**
- Issue body format doesn't match expected table structure
- Missing required fields in issue body
- Incorrect regex patterns

**Solutions:**
1. Compare issue body to expected format in this guide
2. Review workflow logs for specific extraction errors
3. Check for special characters that might break parsing

### Validation Fails

**Possible Causes:**
- Issue not created by bug-logger workflow
- Manual issue creation with wrong format
- Missing critical metadata fields

**Solutions:**
1. Use the exact format from Method 1 in this guide
2. Ensure all required fields are present in the issue body
3. Check for whitespace or formatting issues

## Clean Up

After testing:

1. Close or delete test issues
2. Remove test labels if no longer needed
3. Review workflow run history to confirm expected behavior

## Security Considerations

- The workflow only has read permissions (issues: read, contents: read)
- No secrets are used or required
- Uses default GITHUB_TOKEN with minimal permissions
- No external API calls or data transmission
- All processing happens within GitHub Actions environment

## Performance Expectations

- **Trigger latency**: < 5 seconds after issue creation/labeling
- **Execution time**: 10-30 seconds for complete workflow
- **Metadata extraction**: < 5 seconds
- **Validation**: < 1 second

## Known Limitations

1. **Label Requirement**: Issues MUST have the `ci-failure` label to trigger the workflow
2. **Format Dependency**: Issue body must follow the exact table format used by bug-logger
3. **Single Issue Processing**: Workflow processes one issue per trigger
4. **Regex Parsing**: Extraction relies on specific regex patterns; format changes may break parsing

## Next Steps

After successful testing:

1. Verify workflow works with real CI failures from bug-logger
2. Proceed to Story #7: Integrate fix command trigger
3. Test full automated resolution flow end-to-end

## Support

For issues or questions:
1. Review workflow run logs in Actions tab
2. Check this testing guide for common scenarios
3. Verify issue format matches expected structure
4. Contact repository maintainers

---

**Last Updated**: 2025-10-20
**Story**: Feature #7, Story #5
**Workflow Version**: 1.0.0
