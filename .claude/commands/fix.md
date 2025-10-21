---
description: GitHub issue number containing the bug details
args:
  - name: issue_number
    description: Optional issue number. If not provided, uses the oldest open issue
    required: false
model: claude-sonnet-4-5
---

## Purpose

Automatically resolve GitHub issues by analyzing failure logs, creating targeted fix stories, implementing solutions, and pushing fixes to the remote branch. This command orchestrates the entire bug fix workflow from issue detection through implementation.

## Variables

- `$ISSUE_NUMBER` - GitHub issue number to fix (optional - defaults to oldest open issue)
- Issue metadata extracted from GitHub issue body:
  - `featureID` - Feature ID the issue belongs to
  - `featureName` - Branch name for the feature
- User stories path: `docs/features/{featureID}/issues/{issue_number}/user-stories.md`
- Implementation log path: `docs/features/{featureID}/implementation-log.json`

## Instructions

- Follow the workflow steps in sequential order
- Extract metadata from GitHub issue body (feature ID, branch name, failed step logs)
- Launch product-owner agent in FIX MODE for targeted fix stories
- Automatically call /implement with fix context
- Commit and push changes after implementation
- Do NOT ask the user for confirmation between steps

## Workflow

### Step 1: Determine Issue to Fix

If issue number is provided via argument:
1. Use the provided issue number
2. Skip to Step 2

If NO issue number provided:
1. **Query oldest open issue**:
   - Use `gh issue list --state open --json number,createdAt --limit 100` to get all open issues
   - Parse the JSON output to find the issue with the oldest `createdAt` timestamp
   - Extract the issue number from the oldest issue
   - If no open issues exist: STOP and inform user "No open issues found to fix"

2. **Store issue number**:
   - Store the oldest issue number in a variable for use throughout the workflow
   - Display message: "Processing oldest open issue #{issue_number}"

### Step 2: Fetch Issue Details

1. **Retrieve full issue information**:
   - Use `gh issue view {issue_number} --json number,title,body` to get complete issue details
   - Parse the JSON response to extract `number`, `title`, and `body` fields
   - If issue doesn't exist: STOP and inform user "Issue #{issue_number} not found"

2. **Extract metadata from issue body**:
   - Parse the issue body to extract the table fields:
     - `featureID`: Look for `| featureID | {value} |` pattern
     - `featureName`: Look for `| featureName | {value} |` pattern
   - These fields are required - if either is missing or set to "N/A":
     - STOP execution
     - Display error: "Issue #{issue_number} is missing required metadata (featureID or featureName). This issue cannot be auto-fixed."
     - Suggest manual intervention

3. **Extract failed step log excerpt**:
   - Parse the issue body to find the "## Failed Step Log Excerpt" section
   - Extract everything between the markdown code fence (```) after this header
   - This log excerpt will be passed to the product-owner agent for analysis
   - If log excerpt is missing: Continue anyway (product owner will work with title/description)

4. **Validate extracted data**:
   - Confirm featureID is numeric
   - Confirm featureName starts with "feature/"
   - Display extracted metadata:
     ```
     Issue #{issue_number}: {title}
     Feature ID: {featureID}
     Branch: {featureName}
     Log excerpt length: {char_count} characters
     ```

### Step 3: Update Local Branch

1. **Get current branch**:
   - Run `git branch --show-current` to determine current branch
   - Store current branch name for reference

2. **Switch to feature branch if needed**:
   - Compare current branch with the extracted `featureName`
   - If already on correct branch: Display "Already on branch {featureName}"
   - If on different branch:
     - Run `git checkout {featureName}` to switch to the feature branch
     - If checkout fails: STOP and display error "Failed to checkout branch {featureName}. Error: {error_message}"
     - If successful: Display "Switched to branch {featureName}"

3. **Pull latest changes**:
   - Run `git pull origin {featureName}` to fetch and merge latest changes from remote
   - If pull fails (e.g., branch doesn't exist on remote, conflicts):
     - Display warning but CONTINUE execution
     - Warning message: "Could not pull latest changes (branch may not exist on remote yet). Continuing with local branch."
   - If successful: Display "Branch updated with latest remote changes"

4. **Verify branch state**:
   - Run `git status` to check working tree status
   - Display current branch and status summary

### Step 4: Launch Product Owner in FIX MODE

Use the Task tool to launch the product-owner agent with FIX MODE instructions:

```
MODE: FIX

You are operating in FIX MODE. Create MINIMAL, targeted user stories (1-3 maximum) to fix the following issue.

Issue Details:
- Issue Number: #{issue_number}
- Issue Title: {title}
- Feature ID: {featureID}
- Branch: {featureName}

Failed Step Log Excerpt:
```
{log_excerpt}
```

Analyze the failure and create 1-3 focused fix stories. Save to: docs/features/{featureID}/issues/{issue_number}/user-stories.md

Do NOT update feature-log.json (this is a fix, not a new feature).
```

Important notes for Task tool invocation:
- Replace all placeholders with actual values extracted from the issue
- Include the complete log excerpt in the instructions
- Ensure the file path uses the correct featureID and issue_number
- Wait for the product-owner agent to complete before proceeding

### Step 5: Verify User Stories Created

After product-owner agent completes:

1. **Check for user stories file**:
   - Verify file exists at `docs/features/{featureID}/issues/{issue_number}/user-stories.md`
   - If file doesn't exist: STOP and display error "Product owner failed to create user stories at expected location"

2. **Parse user stories**:
   - Read the user-stories.md file
   - Count the number of fix stories created (should be 1-3)
   - Extract story titles for reporting
   - Display: "Created {count} fix stories for issue #{issue_number}"

### Step 6: Call /implement Command in Fix Mode

1. **Invoke /implement with fix syntax**:
   - Use SlashCommand tool to execute: `/implement fix {issue_number}`
   - This will trigger the updated /implement command which handles fix scenarios
   - Wait for /implement to complete all user stories

2. **Monitor implementation completion**:
   - The /implement command will handle:
     - Reading fix user stories from the correct location
     - Executing all fix stories
     - Updating implementation-log.json
   - Do not interfere with /implement execution

### Step 7: Verify Implementation Completion

After /implement completes:

1. **Read implementation log**:
   - Check `docs/features/{featureID}/implementation-log.json`
   - Verify all fix stories have status "completed"
   - Count completed vs total stories
   - If any stories are incomplete:
     - Display warning: "Some fix stories incomplete - review implementation log"
     - List incomplete stories
     - Ask user if they want to continue with commit/push anyway

2. **Report implementation status**:
   - Display: "Implementation complete: {completed}/{total} stories finished"

### Step 8: Commit Changes

1. **Stage all changes**:
   - Run `git add .` to stage all modified and new files
   - Verify staging with `git status`
   - Count number of files staged
   - If no files staged: Display warning "No changes to commit" and SKIP to Step 10 (no commit needed)

2. **Create commit with standardized message**:
   - Commit message format: "Fix issue #{issue_number}: {issue_title}"
   - Use git commit with HEREDOC format:
     ```bash
     git commit -m "$(cat <<'EOF'
     Fix issue #{issue_number}: {issue_title}

     🤖 Generated with [Claude Code](https://claude.com/claude-code)

     Co-Authored-By: Claude <noreply@anthropic.com>
     EOF
     )"
     ```
   - Replace {issue_number} and {issue_title} with actual values

3. **Verify commit creation**:
   - Capture commit hash from git commit output
   - Run `git log -1` to verify commit was created
   - If commit fails:
     - Capture error message
     - Display: "Commit failed: {error}. Manual intervention required."
     - SKIP Steps 9-10 and jump to Report

4. **Report commit status**:
   - Display: "Commit created: {commit_hash}"
   - Display commit message preview

### Step 9: Push to Remote

1. **Check remote tracking**:
   - Run `git branch -vv` to check if branch has remote tracking
   - Parse output to determine tracking status

2. **Push changes to remote**:
   - If branch has remote tracking: Use `git push`
   - If no remote tracking: Use `git push -u origin {featureName}` to create remote branch and set tracking
   - Monitor push output for success/failure

3. **Handle push failures**:
   - If push fails:
     - Capture error message
     - Display: "Push failed: {error}. Commit exists locally ({commit_hash}). Retry with: git push"
     - Mark as PARTIAL SUCCESS (commit created but not pushed)
     - Continue to Step 10

4. **Verify push success**:
   - Run `git status` to confirm branch is up-to-date with remote
   - Display: "Changes pushed to remote branch {featureName}"

### Step 10: Close GitHub Issue (Optional Enhancement)

After successful push:

1. **Add comment to issue**:
   - Use `gh issue comment {issue_number} --body "Fix implemented and pushed to branch {featureName}. Commit: {commit_hash}"`
   - This provides traceability between issue and fix

2. **Optionally close issue**:
   - If you want to auto-close issues after fix, use: `gh issue close {issue_number} --comment "Fixed in commit {commit_hash}"`
   - Otherwise, leave issue open for manual verification/closing
   - **Recommended**: Leave open for now to allow manual verification

Note: For this initial implementation, we'll ADD COMMENT but LEAVE ISSUE OPEN for manual verification.

## Report

Provide a comprehensive summary with the following sections:

### Issue Details
- Issue number processed
- Issue title
- Feature ID and branch name extracted
- Log excerpt character count

### Branch Status
- Previous branch (if switched)
- Feature branch checked out
- Pull status (updated/skipped/failed)
- Working tree status

### Fix Story Creation
- Number of fix stories created (should be 1-3)
- Story titles
- User stories file location

### Implementation Status
- Total fix stories: {count}
- Completed stories: {count}
- Incomplete stories (if any): {list}
- Implementation log location

### Git Workflow Status

#### Staging
- Files staged: {count}
- Staging status (success/failure)

#### Commit
- Commit hash (if created)
- Commit message
- Commit status (success/failure)

#### Push
- Push status (success/failure)
- Remote tracking status
- Branch name
- Error details (if any)

### Overall Status
- If ALL steps successful: Display "Fix workflow completed successfully. Issue #{issue_number} has been fixed and pushed to {featureName}."
- If partial success (commit but no push): Display "Fix committed locally but push failed. Manual push required."
- If any major failures: Display error summary with recovery instructions

### Next Steps
- Remind user that issue #{issue_number} is still OPEN for manual verification
- Suggest running tests to verify fix
- Recommend creating/updating PR if needed

## Error Handling

### Common Failure Scenarios

1. **Issue not found or invalid**:
   - Provide clear error message
   - Suggest verifying issue number with `gh issue list`

2. **Missing metadata in issue**:
   - Display which fields are missing
   - Explain that auto-fix requires featureID and featureName
   - Suggest manual fix workflow

3. **Branch checkout fails**:
   - Display git error message
   - Suggest manual branch operations
   - Provide recovery command: `git checkout {featureName}`

4. **Product owner fails to create stories**:
   - Check if file was created but in wrong location
   - Display expected vs actual file locations
   - Suggest manual story creation

5. **Implementation incomplete**:
   - List which stories failed
   - Provide path to implementation log for details
   - Ask user if they want to continue with partial fix

6. **Git operations fail**:
   - Preserve all completed work (stories, implementation)
   - Provide exact manual recovery commands
   - Never lose implementation progress

## Self-Verification Checklist

Before finalizing, verify:

- [ ] Issue metadata successfully extracted (featureID, featureName)
- [ ] Switched to correct feature branch
- [ ] Product owner created 1-3 fix stories (not more)
- [ ] User stories saved to correct location (docs/features/{featureID}/issues/{issue_number}/)
- [ ] /implement command invoked with correct fix syntax
- [ ] All fix stories completed (or partial completion acknowledged)
- [ ] Changes committed with proper message format
- [ ] Changes pushed to remote (or failure documented)
- [ ] Issue commented with fix details
- [ ] Issue left open for manual verification
- [ ] Clear next steps provided to user
