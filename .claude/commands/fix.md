---
description: GitHub issue number containing the bug details
model: claude-sonnet-4-5
---

## Purpose

Automatically resolve GitHub issues: analyze CI/CD failures, create fix stories, implement solutions, and push changes. Fully autonomous workflow from issue detection to git operations.

## Key Variables

- `featureID` - Extracted from issue body
- `featureName` - Branch name from issue
- User stories: `docs/features/{featureID}/issues/{issue_number}/user-stories.md`
- Implementation log: `docs/features/{featureID}/implementation-log.json`

## Instructions

- **FIRST**: Clear context with /clear for optimal token efficiency
- Follow workflow steps sequentially without stopping
- Do NOT ask for confirmation between steps
- Check .claude/agents/ for available implementation capabilities
- Plan stories based on available agents and issue requirements

## Workflow

### Step 0: Clear Context

Execute /clear to reset conversation history and minimize token usage. If unavailable, continue anyway.

### Step 1: Determine Issue

- Run `gh issue list --state open --json number,createdAt --limit 100`
- If no issues: STOP with "No open issues found"
- Display: "Processing issue #{issue_number}"

### Step 2: Fetch Issue Details

1. **Get issue**: `gh issue view {issue_number} --json number,title,body`
   - If not found: STOP with "Issue #{issue_number} not found"

2. **Extract branch**: Search for patterns `- **Branch**:`, `**Branch**:`, or `Branch:`
   - If not found: STOP with "Issue missing branch information"

3. **Parse feature info**:
   - If branch = `feature/{id}-{name}`: Extract featureID from `{id}`
   - If branch = `main`: STOP with "Cannot auto-fix main branch infrastructure issues"

4. **Extract Job URLs**: Parse "## Failed Jobs and Steps" section
   - Look for `**JobURL**:` or `**Job URL**:` lines
   - Support formats: direct URL, next line, markdown link
   - Display: "Found {count} job(s) with URLs"
   - If no URLs but inline logs: Warn about old format

### Step 2.5: Fetch Error Logs

1. **Extract job IDs**: Parse `https://github.com/{owner}/{repo}/actions/runs/{run_id}/job/{job_id}`

2. **Fetch logs**: `gh api repos/{owner}/{repo}/actions/jobs/{job_id}/logs` for each job

3. **Parse errors**: Search for "Error:", "FAIL", "Exception", exit codes, test failures
   - Extract 5-10 lines of context around errors
   - Limit to ~50 lines per job
   - Remove ANSI codes

4. **Handle failures**:
   - Not authenticated: "Run 'gh auth login'"
   - Invalid URL: Warn and continue with other jobs
   - Rate limit: "Wait or use higher limit token"

5. **Report**: "Fetched logs from {success}/{total} job(s)" + list failures if any

### Step 2.6: Summarize Errors

Create non-technical summary for product owner:

1. **Analyze patterns**: Group errors (tests, build, linting, deployment, etc.), identify root causes
2. **Create summary**: For each group describe WHAT/WHY/WHERE in plain language, focus on business impact
3. **Format**:
   ```markdown
   ## Error Summary
   ### Overview
   - Total failures: {count}
   - Categories: {list}

   ### Breakdown
   #### {Category}
   - **What Failed**: {description}
   - **Why**: {root cause}
   - **Impact**: {business impact}
   - **Jobs**: {job names}
   ```
4. **Display** summary before proceeding
5. **Store** for product-owner agent (target: 200-500 words)

### Step 3: Update Local Branch

1. **Get current**: `git branch --show-current`
2. **Switch if needed**: `git checkout {featureName}` (STOP if fails)
3. **Pull**: `git pull origin {featureName}` (warn but continue if fails)
4. **Verify**: `git status` (warn if uncommitted changes exist)

### Step 4: Launch Product Owner in FIX MODE

Launch product-owner agent with:

```
FIX MODE: Create user stories for Issue #{issue_number}.

Check .claude/agents/ for available capabilities, then analyze:

Issue: #{issue_number} - {title} | Feature: {featureID} | Branch: {featureName}

{product_owner_summary}
{technical_error_details}

Create 1-3 atomic stories:
- One specific failure/group per story
- Assign to appropriate agent
- Clear acceptance criteria
- Fix root cause, not symptom

CRITICAL: Save to `docs/features/{featureID}/issues/{issue_number}/user-stories.md`
Update `docs/features/feature-log.json` with issue entry.
```

### Step 5: Verify User Stories

1. **Check file**: Verify `docs/features/{featureID}/issues/{issue_number}/user-stories.md` exists (STOP if not)
2. **Parse**: Read file, count stories (1-3), extract titles
3. **Verify**: Confirm "Execution Order" section exists (STOP if missing)
4. **Display**: "Created {count} fix stories for issue #{issue_number}"

### Step 6: Implement Fix

Execute `/implement fix {issue_number}` and wait for completion. Do not interfere with execution.

### Step 7: Verify Implementation

1. **Check feature-log.json** (optimized - small file ~400 lines):
   - Find feature entry → implementations array → issue_number match
   - Check `status` field: "completed" ✅ or "partial"/"blocked" ⚠️
   - Check `totalStories` count

2. **If partial/blocked**: Read `docs/features/{featureID}/issues/{issue_number}/implementation-log.json`
   - Count completed vs incomplete
   - List incomplete stories
   - Ask user to continue or stop

3. **Report**:
   - Completed: "✅ All {totalStories} fix stories finished"
   - Partial: "⚠️ {completed}/{total} stories finished"

CRITICAL: If all stories are completed from the report, run Step 8
### Step 8: Trigger Automated Push and Close

1. **Verify changes**: `git status --porcelain` to confirm there are changes to commit
2. **Output hook trigger**: Output the "Post Fix Push and Close" trigger pattern with issue number
   - The hook will automatically: commit changes, push to remote, and close the GitHub issue
   - If there are no changes, the hook will skip git operations and only close the issue
3. **Monitor**: The hook runs automatically after command completion

## Report

Provide comprehensive summary:

### Issue
- #{issue_number}: {title}
- Feature {featureID} | Branch: {featureName}
- Jobs found: {count} | URLs extracted: {count}

### Logs
- Fetched: {success}/{total}
- Failed (if any): {url} - {reason}
- Summary created | Categories: {list}

### Branch
- Checked out: {featureName}
- Pull: (updated/skipped/failed)
- Tree: (clean/has changes)

### Stories
- Created: {count} stories
- Titles: {list}
- Location: `docs/features/{featureID}/issues/{issue_number}/user-stories.md`

### Implementation
- Completed: {count}/{total}
- Incomplete (if any): {list with status}
- Log: `docs/features/{featureID}/implementation-log.json`

### Automation
- Hook trigger: (output/skipped)
- Hook will handle: git commit, git push, issue close
- Expected commit message: "Fix issue #{issue_number}"
- Changes ready: {count} files modified/added

### Status
- ✅ Success: "Issue #{issue_number} fixed, hook triggered to push and close"
- ⚠️ Partial: Specific recovery steps + retry command
- ❌ Failed: Error summary + recovery instructions

### Next
- Success: "Hook will push changes and close issue automatically. Monitor `/tmp/stop-hook-debug.log` for hook execution"
- Partial: Manual recovery steps

## Output

After completing Step 8 successfully (all fix stories implemented), output the hook trigger:

```
## Post Fix Push and Close
**Payload**:
{
  "issueID": "{issue_number}"
}
```

This triggers the stop-push-and-close hook which will automatically:
1. Stage all changes (`git add .`)
2. Commit with message: "Fix issue #{issue_number}"
3. Push to the remote repository
4. Close the GitHub issue with comment: "Automatically closed after fix was pushed"

**When to output**:
- ✅ Output trigger: All fix stories completed AND changes exist to commit
- ❌ Skip trigger: Implementation incomplete or no changes detected

**Note**: The hook handles all git operations. Do NOT call `/push` in Step 8 - let the hook handle it.

## Error Handling

| Scenario | Action |
|----------|--------|
| **Issue not found** | Error message + suggest `gh issue list` |
| **Missing branch** | Explain format requirement: `- **Branch**: {branch}` |
| **Missing Job URLs** | Check for old inline format, suggest update or STOP |
| **GH CLI not auth** | "Run 'gh auth login'" + STOP |
| **Partial log fetch** | Warn, list failures, ask user: continue or stop |
| **All logs fail** | List reasons, suggest checks (URL, access, rate limit) + STOP |
| **Empty logs** | Warn, continue with others, or error if all empty |
| **Main branch issue** | "Cannot auto-fix infrastructure" + suggest manual |
| **Checkout fails** | Show error + suggest `git fetch origin {branch}:{branch}` |
| **Stories not created** | Check location, show expected vs actual, suggest manual |
| **Incomplete impl** | List failed stories + ask continue or stop |
| **No changes to commit** | Skip hook trigger, suggest manual verification |
| **Hook fails** | Check `/tmp/stop-hook-debug.log` for details, provide manual git commands |

## Self-Verification Checklist

- [ ] Context cleared (/clear)
- [ ] Issue number determined
- [ ] Branch & featureID extracted
- [ ] Job URLs extracted
- [ ] Job IDs parsed
- [ ] GH CLI authenticated
- [ ] Logs fetched (or partial handled)
- [ ] Errors parsed from logs
- [ ] PO summary created (non-technical)
- [ ] Summary displayed to user
- [ ] Main branch rejected if detected
- [ ] Switched to feature branch
- [ ] 1-3 fix stories created
- [ ] Stories at correct location
- [ ] `/implement fix {issue_number}` invoked
- [ ] Implementation verified (completed or user acknowledged)
- [ ] Changes verified with `git status`
- [ ] Hook trigger output (if all stories completed and changes exist)
- [ ] Hook trigger format correct: "## Post Fix Push and Close" + JSON payload
- [ ] Hook will handle: git commit, push, issue close
- [ ] Status & next steps provided
- [ ] Error scenarios handled
