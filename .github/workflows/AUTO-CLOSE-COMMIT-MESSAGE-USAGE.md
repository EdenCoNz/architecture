# Auto-Close Issues from Commit Messages - Usage Guide

## Overview

The Backend CI/CD workflow now automatically closes GitHub issues when commit messages contain the pattern `fix issue #<number>`. This feature runs **regardless of whether the CI workflow succeeds or fails**, ensuring issues are closed based on the developer's intent expressed in the commit message.

## How It Works

### Workflow Integration

The `auto-close-issue-from-commit` job in `backend-ci.yml`:
- Runs with `if: always()` to execute regardless of previous job outcomes
- Extracts issue numbers from commit messages using pattern matching
- Validates that issues exist and are open
- Closes issues with informative comments that differ based on CI status
- Provides comprehensive GitHub Step Summary with closure details

### Pattern Matching

The workflow uses **case-insensitive** pattern matching to detect issue references:

**Supported Patterns:**
- `fix issue #<number>`
- `Fix issue #<number>`
- `fixes issue #<number>`
- `fixed issue #<number>`

**Important Notes:**
- Pattern matching is case-insensitive (FIX, fix, Fix all work)
- Space between "issue" and "#" is required
- Multiple issues can be referenced in a single commit message
- Pattern must match exactly: `fix issue #` (other patterns like `closes #` are NOT supported)

## Usage Examples

### Single Issue

```bash
git commit -m "fix issue #123"
```
**Result:** Closes issue #123

### Multiple Issues

```bash
git commit -m "fix issue #123 and fix issue #456"
```
**Result:** Closes both issue #123 and #456

### With Description

```bash
git commit -m "Implement user authentication - fixes issue #789"
```
**Result:** Closes issue #789

### Case Variations

All of these work:
```bash
git commit -m "fix issue #100"      # lowercase
git commit -m "Fix issue #200"      # capitalized
git commit -m "FIX ISSUE #300"      # uppercase
git commit -m "fixes issue #400"    # plural
git commit -m "fixed issue #500"    # past tense
```

### Multi-line Commit Messages

```bash
git commit -m "Major refactor of authentication system

This commit fixes issue #42 by implementing new JWT tokens.
Also fixes issue #43 with better error handling."
```
**Result:** Closes both issue #42 and #43

## CI Status Messages

The workflow adds different comments to closed issues based on the CI workflow status:

### When CI Succeeds

```markdown
Automatically closed by commit abc123def - Backend CI/CD workflow completed successfully.

**Run URL**: https://github.com/org/repo/actions/runs/12345
**Workflow**: Backend CI/CD
**Status**: ✅ All checks passed
```

### When CI Fails

```markdown
Automatically closed by commit abc123def - Backend CI/CD workflow completed (some checks may have failed).

**Run URL**: https://github.com/org/repo/actions/runs/12345
**Workflow**: Backend CI/CD
**Status**: ⚠️ Some checks failed (see run for details)
```

## GitHub Step Summary

The workflow provides detailed information in the GitHub Actions Step Summary:

**Commit Message Analysis:**
- Shows the commit message being analyzed
- Lists all detected issue references
- Shows the pattern being used

**Closing Issues:**
- Lists each issue being processed
- Shows CI status (success/failure)
- Indicates whether each issue was closed, already closed, or doesn't exist

**Summary:**
- Total issues processed
- Successfully closed count
- Failed/Skipped count

## Edge Cases and Validation

### Issue Validation

The workflow performs validation before closing:

1. **Issue Exists:** Checks if the issue number is valid
   - If not found: Logs warning, doesn't fail the workflow

2. **Issue is Open:** Checks if the issue is already closed
   - If already closed: Logs info message, skips closing

3. **Permissions:** Ensures GITHUB_TOKEN has `issues: write` permission
   - Permission is granted in the workflow configuration

### Multiple References

When the same issue is referenced multiple times:
```bash
git commit -m "fix issue #123 and also fix issue #123"
```
**Result:** Issue #123 is closed once (duplicates are handled by `sort -u`)

### Pattern Matching Tests

**These patterns WORK:**
- `fix issue #123` ✅
- `Fix issue #456` ✅
- `fixes issue #789` ✅
- `fixed issue #999` ✅
- `FIX ISSUE #555` ✅

**These patterns DO NOT WORK:**
- `closes #123` ❌ (wrong keyword)
- `fix #123` ❌ (missing "issue" keyword)
- `fix issue#123` ❌ (missing space before #)
- `resolve issue #123` ❌ (wrong keyword)

## Troubleshooting

### Issues Not Closing

**Check the following:**

1. **Commit Message Pattern:**
   - Ensure you're using `fix issue #<number>` exactly
   - Check for typos in "issue" or "fix"
   - Verify there's a space before the # symbol

2. **Issue Number:**
   - Confirm the issue number exists in the repository
   - Verify the issue is open (already closed issues are skipped)

3. **Workflow Execution:**
   - Check the GitHub Actions run logs
   - Look at the "Auto-Close Issue from Commit Message" job
   - Review the GitHub Step Summary for detailed information

4. **Permissions:**
   - Ensure `issues: write` permission is granted
   - Check organization/repository settings for restrictions

### Debugging

To see detailed information about what the workflow detected:

1. Go to **Actions** tab in GitHub
2. Find the workflow run for your commit
3. Click on "Auto-Close Issue from Commit Message" job
4. Check the **Summary** tab for detailed output

The summary will show:
- Exact commit message analyzed
- Issues detected (or "No issue references found")
- Status of each issue closure attempt
- Final summary with counts

## Best Practices

### When to Use This Feature

**Good Use Cases:**
- Closing issues fixed by a specific commit
- Closing multiple related issues at once
- Automating issue closure during development

**When NOT to Use:**
- If you want to manually verify the fix first
- If the issue requires additional discussion before closing
- If closing the issue depends on deployment/release

### Commit Message Style

**Recommended:**
```bash
# Clear and specific
git commit -m "Add email validation - fixes issue #42"

# Multiple issues with context
git commit -m "Refactor authentication module

- Fix issue #100: JWT token expiration
- Fix issue #101: Password reset flow"
```

**Not Recommended:**
```bash
# Too vague
git commit -m "fix stuff - fix issue #42"

# Unclear what was fixed
git commit -m "fix issue #42"  # No description of the fix
```

### Workflow Integration

The auto-close feature integrates with your development workflow:

1. **Create Issue:** Describe the bug or feature
2. **Create Branch:** Work on the fix
3. **Commit with Pattern:** Use `fix issue #N` in commit message
4. **Push/PR:** Push to remote or create PR
5. **Auto-Close:** Workflow automatically closes the issue
6. **Verify:** Check issue for closure comment with CI status

## Configuration

### Permissions

The workflow requires these permissions (already configured):

```yaml
permissions:
  issues: write     # Required to close issues
  contents: read    # Required to read commit messages
```

### Job Settings

The job is configured with:

```yaml
if: always()         # Runs regardless of previous job status
timeout-minutes: 5   # Prevents hanging
```

### Customization

To modify the behavior:

1. **Change Pattern:** Edit the regex in `Extract issue numbers from commit message` step
2. **Modify Comments:** Edit the `CLOSE_COMMENT` messages in `Close referenced issues` step
3. **Add Labels:** Extend the `gh issue close` command to add labels

## Frequently Asked Questions

### Q: Will issues be closed if the CI fails?
**A:** Yes! The job runs with `if: always()`, so issues are closed regardless of CI status. The closure comment will indicate if some checks failed.

### Q: Can I use other keywords like "closes" or "resolves"?
**A:** No, currently only `fix/fixes/fixed issue #N` patterns are supported. This is intentional to maintain consistency.

### Q: What if I reference an issue that doesn't exist?
**A:** The workflow validates issue existence. Non-existent issues are logged in the summary but don't cause the workflow to fail.

### Q: Can I reopen an issue after it's auto-closed?
**A:** Yes, you can manually reopen any issue through the GitHub UI. The auto-close feature only closes issues, it doesn't prevent reopening.

### Q: Does this work for Pull Request commits?
**A:** Yes, the workflow handles both push events and pull request events. The commit message is fetched appropriately for each event type.

### Q: How many issues can I reference in one commit?
**A:** There's no hard limit. The workflow extracts all matching patterns and processes them. Practically, it's best to keep it reasonable (1-5 issues per commit).

## Examples from Real Scenarios

### Scenario 1: Bug Fix

```bash
# Issue #42: Login fails with special characters in password

git commit -m "Sanitize password input - fixes issue #42

Added proper escaping for special characters in authentication flow."
```

**Workflow Action:**
- ✅ Closes issue #42
- 💬 Adds comment with CI status and run URL
- 📊 Updates GitHub Step Summary with closure details

### Scenario 2: Multiple Related Fixes

```bash
# Issues #100, #101: Auth module problems

git commit -m "Refactor authentication module

- fix issue #100: JWT token validation
- fix issue #101: Session timeout handling"
```

**Workflow Action:**
- ✅ Closes issue #100
- ✅ Closes issue #101
- 💬 Adds individual comments to each issue
- 📊 Summary shows 2 issues closed

### Scenario 3: Failed CI

```bash
git commit -m "Attempt fix for rate limiting - fix issue #50"
# Commit has syntax error, CI fails
```

**Workflow Action:**
- ✅ Still closes issue #50 (because of if: always())
- ⚠️ Closure comment indicates CI failures
- 💬 Provides link to failed CI run for review
- 🔄 Issue can be reopened if fix is insufficient

## Technical Details

### Regex Pattern

```bash
grep -iEo 'fix(es|ed)? issue #[0-9]+'
```

**Breakdown:**
- `-i`: Case-insensitive matching
- `-E`: Extended regex
- `-o`: Only matching part
- `fix(es|ed)?`: Matches "fix", "fixes", or "fixed"
- ` issue #`: Literal space, "issue", space, and "#"
- `[0-9]+`: One or more digits

### Issue Number Extraction

```bash
grep -oE '[0-9]+' | sort -u
```

**Breakdown:**
- `grep -oE '[0-9]+'`: Extract just the numbers
- `sort -u`: Sort and remove duplicates

### GitHub CLI Commands

**Check issue state:**
```bash
gh issue view "$ISSUE_NUMBER" --json state --jq '.state'
```

**Close issue with comment:**
```bash
gh issue close "$ISSUE_NUMBER" \
  --repo "$REPOSITORY" \
  --comment "$CLOSE_COMMENT"
```

## Conclusion

The auto-close feature streamlines issue management by automatically closing issues referenced in commit messages. It runs regardless of CI status, provides detailed feedback, and integrates seamlessly with your existing workflow.

For questions or issues with this feature, check the workflow logs in GitHub Actions or review this documentation.

**File Location:**
- Workflow: `/home/ed/Dev/architecture/.github/workflows/backend-ci.yml`
- Job Name: `auto-close-issue-from-commit`
- Documentation: `/home/ed/Dev/architecture/.github/workflows/.env`
