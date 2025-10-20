# Automated CI/CD Failure Resolution - Quick Reference

This is a quick reference guide for developers using the automated CI/CD failure resolution system. For comprehensive documentation, see [AUTOMATED_CI_CD_FAILURE_RESOLUTION.md](./AUTOMATED_CI_CD_FAILURE_RESOLUTION.md).

---

## What Happens When CI Fails?

```
1. CI job fails
   ↓
2. GitHub issue created automatically
   ↓
3. Issue labeled with 'ci-failure'
   ↓
4. Automation comment added to issue
   ↓
5. Issue labeled with 'fix-queued'
   ↓
6. Ready for developer action
```

---

## Quick Actions

### View Your CI Failure Issues

```bash
# List your open CI failure issues
gh issue list --label "ci-failure" --state open --assignee @me

# View specific issue
gh issue view ISSUE_NUMBER
```

### Run Automated Fix

```bash
# Automatic fix attempt (if using Claude CLI)
claude /fix gha
```

### Manual Fix

```bash
# 1. Fix the code
# 2. Commit with proper format (see commit template in issue)
git commit -m "Implementation of bug-github-issue-NUMBER-short-description"

# 3. Push changes
git push

# 4. CI runs again
# 5. If successful, close the issue
gh issue close ISSUE_NUMBER --comment "Fixed - CI now passing"
```

---

## Issue Labels Explained

| Label | Meaning | Action Required |
|-------|---------|-----------------|
| `ci-failure` | CI job failed | Fix the code |
| `fix-queued` | Ready for automated fix | Run `/fix` or manually fix |
| `fix-pending` | Original issue may be resolved | Verify if actually fixed |
| `pending-merge` | Fix successful, awaiting merge | Review and merge PR |

---

## Understanding the Issue

Each CI failure issue contains:

1. **Metadata Table**: Feature ID, job name, step name, log lines
2. **Log Excerpt**: Last 50 lines of failed job logs
3. **Links**: PR, commit, workflow run
4. **Commit Template**: Example commit message format
5. **Fix Instructions**: How to run automated fix

**Example Issue Body**:
```markdown
# Bug Log - CI/CD Failure

| Field | Value |
|-------|-------|
| featureID | 7 |
| jobName | lint |
| stepName | Run ESLint |
| logLineNumbers | L100-L150 |

## Failed Step Log Excerpt
[Last 50 lines of logs]

## How to Fix
[Instructions]
```

---

## Common Scenarios

### Scenario 1: First Failure

**Situation**: You push code and CI fails for the first time

**What Happens**:
- Issue created with `ci-failure` label
- Issue assigned to you
- Automation comment added
- `fix-queued` label added

**What You Do**:
1. Review the issue
2. Fix the code
3. Commit with proper format (see issue comment)
4. Push changes
5. If CI passes, close the issue

### Scenario 2: Duplicate Failure

**Situation**: You push again without fixing, same failure occurs

**What Happens**:
- NO new issue created (duplicate detected)
- PR comment links to existing issue
- Reduces noise

**What You Do**:
- Fix the original issue (same as Scenario 1)

### Scenario 3: Different Failure

**Situation**: You fix the lint issue but introduce a build error

**What Happens**:
- New issue created for build failure
- Old lint issue marked `fix-pending` (may be resolved)
- Two separate issues to track

**What You Do**:
1. Verify old issue is actually fixed
2. Close old issue if verified
3. Fix new issue

### Scenario 4: Fix Attempt Failed

**Situation**: You attempted a fix, merged it, but CI still fails

**What Happens**:
- New issue created for current failure
- Old issue updated with failure comment
- Attempt count tracked (Attempt #2, #3, etc.)

**What You Do**:
1. Review both issues (old and new)
2. Investigate why previous fix didn't work
3. Apply more comprehensive fix

---

## Troubleshooting

### Issue Not Created

**Check**:
```bash
# View recent workflow runs
gh run list --workflow=bug-logger.yml --limit 5

# View specific run logs
gh run view RUN_ID --log
```

**Common Causes**:
- CI workflow not configured to call bug-logger
- Permissions issue
- Workflow disabled

### No Automation Comment

**Check**:
```bash
# View issue event listener runs
gh run list --workflow=issue-event-listener.yml --limit 5

# Check if ci-failure label exists
gh label list | grep ci-failure
```

**Common Causes**:
- ci-failure label missing
- Issue event listener not triggered
- Metadata validation failed

### Multiple Issues for Same Failure

**Check**:
```bash
# List open issues
gh issue list --label "ci-failure" --state open

# Check duplicate detection logs
gh run view RUN_ID --log | grep "Duplicate Detection"
```

**Common Causes**:
- Metadata fields differ slightly
- Log line numbers changing
- Feature ID not extracted correctly

---

## Best Practices

### Commit Messages

Always use the commit identifier template provided in the issue:

```bash
# Format
git commit -m "Implementation of bug-github-issue-{NUMBER}-{description}"

# Example
git commit -m "Implementation of bug-github-issue-42-lint-job-failed"
```

### Closing Issues

When CI passes after fix:

```bash
# Close with explanation
gh issue close ISSUE_NUMBER --comment "Fixed in commit COMMIT_SHA - CI now passing"

# Optional: Add pending-merge label
gh issue edit ISSUE_NUMBER --add-label "pending-merge"
```

### Reviewing Fix Attempts

Before applying a fix:
1. Read the full issue description
2. Review the log excerpt
3. Click the workflow run link for full logs
4. Understand the root cause
5. Apply comprehensive fix (not just symptom)

### Multiple Failures

If multiple jobs fail, only the first failure gets an issue. After fixing it:
1. Push the fix
2. CI runs again
3. If other jobs still fail, new issues will be created
4. Fix one issue at a time

---

## Getting Help

### Documentation

- **Full Documentation**: [AUTOMATED_CI_CD_FAILURE_RESOLUTION.md](./AUTOMATED_CI_CD_FAILURE_RESOLUTION.md)
- **Duplicate Detection**: [DUPLICATE_DETECTION_FLOW.md](./DUPLICATE_DETECTION_FLOW.md)
- **Workflow Files**: `.github/workflows/`

### Commands Reference

```bash
# List workflows
gh workflow list

# View workflow runs
gh run list --workflow=WORKFLOW_NAME --limit 10

# View specific run
gh run view RUN_ID --log

# List issues
gh issue list --label "ci-failure"

# View issue
gh issue view ISSUE_NUMBER

# Close issue
gh issue close ISSUE_NUMBER --comment "Fixed"

# Edit issue labels
gh issue edit ISSUE_NUMBER --add-label "pending-merge"
gh issue edit ISSUE_NUMBER --remove-label "fix-queued"
```

### Support

If you encounter issues:
1. Check workflow run logs
2. Review troubleshooting section above
3. Check full documentation
4. Contact DevOps team or repository maintainers

---

## System Workflow Overview

```
Developer Push
    ↓
CI/CD Runs
    ↓
    ├─→ Success → Done
    │
    └─→ Failure
        ↓
    Bug Logger
        ↓
    Duplicate Check
        ↓
        ├─→ Duplicate → Skip issue, comment on PR
        │
        └─→ New Issue
            ↓
        Create Issue
            ↓
        Issue Event Listener
            ↓
        Fix Trigger
            ↓
        Ready for Fix
            ↓
        Developer Action:
        - Run: claude /fix gha
        - OR manually fix
```

---

## Frequently Asked Questions

**Q: Why wasn't an issue created for my CI failure?**
A: Check if a duplicate exists, review bug-logger workflow logs, verify CI workflow is configured correctly.

**Q: Can I disable the automation for a specific PR?**
A: Not currently. The automation runs for all feature/* branches with CI failures.

**Q: How do I know if my fix worked?**
A: Push your changes, wait for CI to run, check if all jobs pass. If they do, close the issue.

**Q: What if I get multiple issues for the same failure?**
A: This shouldn't happen due to duplicate detection. If it does, report it as a bug - there may be an issue with metadata consistency.

**Q: Can I manually trigger the fix workflow?**
A: The fix-trigger workflow adds a comment with instructions. Use `claude /fix gha` in your development environment or fix manually.

**Q: How long are issues kept open?**
A: Issues remain open until you close them. It's your responsibility to close issues once CI passes.

**Q: What happens if I close an issue but CI still fails?**
A: A new issue will be created, and it will be marked as a retry (Attempt #2, etc.).

---

**Last Updated**: 2025-10-20
**Version**: 1.0.0

For comprehensive documentation, see [AUTOMATED_CI_CD_FAILURE_RESOLUTION.md](./AUTOMATED_CI_CD_FAILURE_RESOLUTION.md)
