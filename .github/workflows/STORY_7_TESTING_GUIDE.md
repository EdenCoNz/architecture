# Story #7 Testing Guide: Fix Command Trigger Integration

## Overview

This guide explains how to test the automated fix command trigger integration implemented in Story #7. The integration connects the issue-event-listener workflow to the fix-trigger workflow via `repository_dispatch` events.

## Architecture

```
CI Failure → Bug Logger → GitHub Issue Created → Issue Event Listener → repository_dispatch → Fix Trigger
                              ↓                           ↓                                      ↓
                      Labels: ci-failure         Validates metadata                   Adds: fix-queued
                                                 Triggers dispatch                    Posts comment
```

## Workflows Involved

1. **issue-event-listener.yml** (Modified in Story #7)
   - Listens for issue creation/labeling events
   - Filters for `ci-failure` labeled issues
   - Extracts metadata from issue body
   - Triggers `repository_dispatch` event with context

2. **fix-trigger.yml** (Created in Story #7)
   - Listens for `ci-failure-fix-trigger` repository_dispatch events
   - Validates event payload
   - Adds `fix-queued` label to issue
   - Posts comment with fix context and manual execution instructions

## Testing Methods

### Method 1: End-to-End Testing (Recommended)

This method tests the complete flow from CI failure to fix trigger.

**Prerequisites:**
- Push access to a feature branch
- GitHub Actions enabled

**Steps:**

1. **Create a feature branch with a deliberate CI failure:**
   ```bash
   git checkout -b feature/99-test-fix-trigger
   ```

2. **Introduce a lint error in frontend code:**
   ```bash
   # Example: Add intentional syntax error to frontend/src/App.tsx
   echo "const broken = " >> frontend/src/App.tsx
   git add frontend/src/App.tsx
   git commit -m "Test: Introduce lint error for fix trigger test"
   git push -u origin feature/99-test-fix-trigger
   ```

3. **Create a pull request:**
   - GitHub Actions will run frontend-ci.yml
   - Lint job will fail
   - Bug logger will create an issue with `ci-failure` label

4. **Monitor issue-event-listener workflow:**
   - Go to Actions tab → Issue Event Listener workflow
   - Verify workflow triggered by issue creation event
   - Check workflow logs for:
     - Metadata extraction success
     - `repository_dispatch` API call success
     - "Fix attempt triggered successfully" message

5. **Monitor fix-trigger workflow:**
   - Go to Actions tab → CI Failure Fix Trigger workflow
   - Verify workflow triggered by repository_dispatch
   - Check workflow logs for:
     - Payload validation success
     - Comment posted to issue
     - `fix-queued` label added

6. **Verify issue updates:**
   - Go to the created issue
   - Verify `fix-queued` label is present
   - Verify automated fix trigger comment is present
   - Verify comment includes:
     - Fix context table
     - Manual execution instructions
     - `/fix gha` command

7. **Clean up:**
   ```bash
   git checkout main
   git branch -D feature/99-test-fix-trigger
   git push origin --delete feature/99-test-fix-trigger
   # Close the test issue on GitHub
   ```

### Method 2: Manual Trigger Testing

This method tests only the fix-trigger workflow in isolation.

**Prerequisites:**
- GitHub CLI authenticated (`gh auth status`)
- An existing open issue (any issue)

**Steps:**

1. **Trigger repository_dispatch event manually:**
   ```bash
   gh api repos/OWNER/REPO/dispatches \
     --method POST \
     --field event_type="ci-failure-fix-trigger" \
     --field client_payload[issue_number]=123 \
     --field client_payload[issue_title]="Test Fix Trigger" \
     --field client_payload[issue_url]="https://github.com/OWNER/REPO/issues/123" \
     --field client_payload[feature_id]="99" \
     --field client_payload[feature_name]="test-feature" \
     --field client_payload[branch_name]="feature/99-test" \
     --field client_payload[job_name]="lint" \
     --field client_payload[step_name]="Run ESLint"
   ```

2. **Monitor fix-trigger workflow:**
   - Go to Actions tab → CI Failure Fix Trigger workflow
   - Verify workflow triggered within 30 seconds
   - Check workflow logs for success

3. **Verify issue updates:**
   - Check issue #123 (or your test issue)
   - Verify `fix-queued` label added
   - Verify comment posted

### Method 3: Issue Event Listener Testing Only

This method tests metadata extraction without triggering the fix workflow.

**Prerequisites:**
- An existing CI failure issue (created by bug-logger)

**Steps:**

1. **Trigger issue-event-listener by adding a label:**
   ```bash
   gh issue edit 123 --add-label "test-label"
   gh issue edit 123 --remove-label "test-label"
   ```

2. **Monitor issue-event-listener workflow:**
   - Go to Actions tab → Issue Event Listener workflow
   - Verify workflow triggered by label event
   - Check workflow logs for metadata extraction
   - Verify `repository_dispatch` API call in logs

## Expected Behavior

### Successful Flow

1. **Issue Event Listener Workflow:**
   - ✅ Triggered by issue creation with `ci-failure` label
   - ✅ Extracts all required metadata (feature ID, branch, job, step)
   - ✅ Validates metadata successfully
   - ✅ Calls repository_dispatch API successfully
   - ✅ Shows "Fix attempt triggered successfully" in logs
   - ✅ Summary shows "Automated fix attempt triggered"

2. **Fix Trigger Workflow:**
   - ✅ Triggered within 30 seconds of dispatch event
   - ✅ Validates payload successfully
   - ✅ Posts comment to issue with fix context
   - ✅ Adds `fix-queued` label to issue
   - ✅ Summary shows "Fix Trigger Successful"

3. **Issue State:**
   - ✅ Has `ci-failure` label (from bug-logger)
   - ✅ Has `fix-queued` label (from fix-trigger)
   - ✅ Has comment with fix context and manual execution instructions

### Failure Scenarios

#### Scenario 1: Metadata Validation Failure

**Cause:** Issue not created by bug-logger, missing required fields

**Expected:**
- Issue Event Listener workflow shows validation failure
- No `repository_dispatch` event triggered
- Fix Trigger workflow NOT triggered
- Issue does NOT get `fix-queued` label

#### Scenario 2: Payload Validation Failure

**Cause:** Invalid or incomplete repository_dispatch payload

**Expected:**
- Fix Trigger workflow triggered but fails validation
- No comment or label added to issue
- Workflow summary shows validation error

#### Scenario 3: GitHub API Failure

**Cause:** API rate limit, permissions issue, network error

**Expected:**
- Issue Event Listener or Fix Trigger workflow fails
- Error message in workflow logs
- Issue may not get updated

## Verification Checklist

Use this checklist to verify Story #7 acceptance criteria:

- [ ] Fix command automatically triggered when qualifying issue created
  - [ ] Issue with `ci-failure` label triggers issue-event-listener
  - [ ] Issue-event-listener triggers repository_dispatch event
  - [ ] Fix-trigger workflow is triggered by dispatch event

- [ ] Issue number passed correctly to fix command
  - [ ] Issue number extracted from issue event
  - [ ] Issue number included in repository_dispatch payload
  - [ ] Issue number used to post comment and add label
  - [ ] Comment includes correct issue context

- [ ] Fix attempt runs asynchronously without blocking issue creation
  - [ ] repository_dispatch creates asynchronous trigger
  - [ ] Issue Event Listener completes quickly (< 1 minute)
  - [ ] Fix Trigger runs independently
  - [ ] Issue creation workflow does not wait for fix completion

## Troubleshooting

### Fix Trigger Workflow Not Triggering

**Check:**
1. Issue Event Listener logs for repository_dispatch API call
2. GitHub Actions permissions (actions: write required)
3. repository_dispatch event type matches ("ci-failure-fix-trigger")
4. GitHub Actions tab shows Fix Trigger workflow exists

**Fix:**
- Verify GITHUB_TOKEN has actions: write permission
- Check workflow file is in .github/workflows/
- Ensure workflow is enabled in repository settings

### Comment Not Posted to Issue

**Check:**
1. Fix Trigger workflow logs for comment step
2. GitHub token permissions (issues: write required)
3. Issue number in payload is correct

**Fix:**
- Verify GITHUB_TOKEN has issues: write permission
- Check issue number is valid and issue exists
- Verify gh CLI authentication in workflow

### Label Not Added to Issue

**Check:**
1. Fix Trigger workflow logs for label step
2. Issue exists and is open
3. Label "fix-queued" is created in repository

**Fix:**
- Create "fix-queued" label in repository settings if missing
- Verify issue is open (not closed)
- Check GitHub token permissions

## Manual /fix Command Execution

After the fix-trigger workflow adds the `fix-queued` label, the `/fix` command can be executed manually:

```bash
# Navigate to repository
cd /path/to/architecture

# Execute fix command
# The /fix command will automatically:
# 1. Fetch the oldest open issue (the one with fix-queued label)
# 2. Parse the failure context
# 3. Create user stories
# 4. Implement the fix
# 5. Commit and push
# 6. Mark issue as fixed-pending-merge
claude /fix gha
```

The `/fix` command will process the oldest open issue, which should be the one marked with `fix-queued`.

## Next Steps After Testing

1. **Verify complete flow works end-to-end**
2. **Monitor for false positives** (issues incorrectly triggering fix)
3. **Verify /fix command** processes the queued issues correctly
4. **Test with multiple simultaneous failures** to ensure async behavior
5. **Document any edge cases** discovered during testing

## Integration with Future Stories

This Story #7 implementation integrates with:
- **Story #10**: Retry detection in bug logger
- **Story #11**: Bug resolver call from bug logger
- **Story #12**: Documentation updates

The fix-trigger workflow provides the foundation for automated fix attempts. Future stories will enhance retry detection and resolution tracking.
