---
description: GitHub issue number containing the bug details
model: claude-sonnet-4-5
---

## Purpose

Automatically resolve GitHub issues by analyzing CI/CD failure logs, creating targeted fix stories, implementing solutions, and pushing fixes to the remote branch. This command orchestrates the entire bug fix workflow from issue detection through implementation and git operations.

## Variables

- `{{{ input }}}` - GitHub issue number to fix (optional - defaults to oldest open issue)
- Issue metadata extracted from GitHub issue body:
  - `featureID` - Feature ID the issue belongs to
  - `featureName` - Branch name for the feature
- User stories path: `docs/features/{featureID}/issues/{issue_number}/user-stories.md`
- Implementation log path: `docs/features/{featureID}/implementation-log.json`

## Instructions

- Follow the workflow steps in sequential order
- Do NOT stop after creating user stories - automatically proceed to implementation
- Do NOT ask the user for confirmation between steps
- Check available agents in .claude/agents/ to understand implementation capabilities
- Plan user stories based on available agents and issue requirements

## Workflow

### Step 1: Determine Issue to Fix

1. **Parse input parameter**:
   - Check if `{{{ input }}}` is provided and non-empty
   - If provided: Use the provided issue number
   - If not provided or empty: Query for oldest open issue

2. **Query oldest open issue** (only if no input provided):
   - Use `gh issue list --state open --json number,createdAt --limit 100` to get all open issues
   - Parse the JSON output to find the issue with the oldest `createdAt` timestamp
   - Extract the issue number from the oldest issue
   - If no open issues exist: STOP and inform user "No open issues found to fix"

3. **Store issue number**:
   - Store the determined issue number in a variable for use throughout the workflow
   - Display message: "Processing issue #{issue_number}"

### Step 2: Fetch Issue Details

1. **Retrieve full issue information**:
   - Use `gh issue view {issue_number} --json number,title,body` to get complete issue details
   - Parse the JSON response to extract `number`, `title`, and `body` fields
   - If issue doesn't exist: STOP and inform user "Issue #{issue_number} not found"

2. **Extract branch from issue body**:
   - Search for branch information in the issue body using these patterns (in order):
     1. Line matching `- **Branch**: {branch_name}`
     2. Line matching `**Branch**: {branch_name}`
     3. Line matching `Branch: {branch_name}`
   - Extract the branch name after the pattern (trim whitespace)
   - If no branch found with any pattern: STOP and display error "Issue #{issue_number} does not contain branch information. Expected branch field in issue body. Please add branch info to the issue."

3. **Determine feature information from branch**:
   - If branch starts with "feature/":
     - Set featureName = branch (e.g., "feature/5-hello-button")
     - Extract featureID from branch name: take characters after "feature/" and before first "-" or end of string
     - Examples:
       - "feature/7-initialise-backend-api" -> featureID = "7"
       - "feature/123-some-feature" -> featureID = "123"
       - "feature/5" -> featureID = "5"
   - If branch is "main" or doesn't start with "feature/":
     - Set featureName = "main"
     - Set featureID = "N/A"
     - STOP execution with message: "Issue #{issue_number} is for main branch. Cannot auto-fix infrastructure issues on main branch. Please fix manually."

4. **Extract error details**:
   - Parse the "## Failed Jobs and Steps" section from the issue body
   - For each failed job/step, extract:
     - Job name and step name (from section heading)
     - Error log excerpt (from code block)
   - Store all failed step information for use in Step 4
   - Display: "Found {count} failed job(s)/step(s) in issue"

### Step 3: Update Local Branch

1. **Get current branch**:
   - Run `git branch --show-current` to determine current branch
   - Store current branch name for reference

2. **Switch to feature branch if needed**:
   - Compare current branch with the extracted `featureName`
   - If already on correct branch: Display "Already on branch {featureName}"
   - If on different branch:
     - Run `git checkout {featureName}` to switch to the feature branch
     - If checkout fails: STOP and display error "Failed to checkout branch {featureName}. Error: {error_message}. Please ensure branch exists locally or fetch from remote."
     - If successful: Display "Switched to branch {featureName}"

3. **Pull latest changes**:
   - Run `git pull origin {featureName}` to fetch and merge latest changes from remote
   - If pull fails (e.g., branch doesn't exist on remote, conflicts):
     - Display warning but CONTINUE execution
     - Warning message: "Could not pull latest changes (branch may not exist on remote yet). Continuing with local branch."
   - If successful: Display "Branch updated with latest remote changes"

4. **Verify branch state**:
   - Run `git status` to check working tree status
   - If there are uncommitted changes:
     - Display warning: "Warning: Working tree has uncommitted changes. These will be included in the fix commit."
   - Display current branch and status summary

### Step 4: Launch Product Owner in FIX MODE

Use the Task tool to launch the product-owner agent with the following instructions:

```
You are operating in FIX MODE to create user stories for resolving GitHub Issue #{issue_number}.

First, check what agents are available in .claude/agents/ to understand what implementation capabilities exist.

Then, analyze the following CI/CD failure logs and create comprehensive user stories to fix the issues:

## Issue Details
- **Issue Number**: #{issue_number}
- **Issue Title**: {issue_title}
- **Feature ID**: {featureID}
- **Branch**: {featureName}

## Failed CI/CD Steps

{failed_steps_details}

## Your Task

Create 1-3 atomic user stories to fix these failures. Each story should:
- Address one specific failure or a closely related group of failures
- Be assigned to the appropriate agent (frontend-developer, backend-developer, devops-engineer, etc.)
- Have clear, testable acceptance criteria
- Focus on fixing the root cause, not just the symptom

## File Location Requirements

**CRITICAL**: You MUST save the user stories to the following location:
`docs/features/{featureID}/issues/{issue_number}/user-stories.md`

Create the directory structure if it doesn't exist.

## Feature Log Update

After creating the user stories file, you MUST also update `docs/features/feature-log.json`:
1. Find the feature entry with matching featureID
2. Add an issue entry if one doesn't exist for this issue number
3. Record that fix user stories have been created

Plan the user stories based on the available agents and the nature of the failures.
```

### Step 5: Verify User Stories Created

After product-owner agent completes:

1. **Check for user stories file**:
   - Verify file exists at `docs/features/{featureID}/issues/{issue_number}/user-stories.md`
   - If file doesn't exist: STOP and display error "Product owner failed to create user stories at expected location: docs/features/{featureID}/issues/{issue_number}/user-stories.md"

2. **Parse user stories**:
   - Read the user-stories.md file
   - Count the number of fix stories created (should be 1-3)
   - Parse the "Execution Order" section to understand the implementation phases
   - Extract story titles for reporting
   - Display: "Created {count} fix stories for issue #{issue_number}"

3. **Verify execution order exists**:
   - Confirm the user-stories.md file contains an "Execution Order" section
   - If missing: STOP and display error "User stories file is missing Execution Order section"

### Step 6: Call /implement Command in Fix Mode

1. **Invoke /implement with fix syntax**:
   - Use SlashCommand tool to execute: `/implement fix {issue_number}`
   - This will trigger the /implement command which handles fix scenarios
   - Wait for /implement to complete all user stories

2. **Monitor implementation completion**:
   - The /implement command will handle:
     - Reading fix user stories from the correct location
     - Executing all fix stories in the defined order
     - Updating implementation-log.json
     - Updating feature-log.json with implementation entry
   - Do not interfere with /implement execution

### Step 7: Verify Implementation Completion

After /implement completes:

1. **Read implementation log**:
   - Check `docs/features/{featureID}/implementation-log.json`
   - Verify all fix stories have status "completed"
   - Count completed vs total stories
   - If any stories are incomplete:
     - Display warning: "Warning: {incomplete_count}/{total} stories incomplete"
     - List incomplete stories with their status
     - Ask user if they want to continue with commit anyway or stop

2. **Report implementation status**:
   - Display: "Implementation complete: {completed}/{total} stories finished"
   - List all completed stories

### Step 8: Stage All Changes

After verifying implementation completion in Step 7:

1. **Check for changes**:
   - Run `git status --porcelain` to get list of modified/untracked files
   - Count the number of files with changes
   - If no changes detected: Display warning "No changes detected to commit" and SKIP to Step 11 (Close Issue)

2. **Stage all modified files**:
   - Use `git add .` to stage all modified and new files in the working directory
   - This ensures both modified files and new files are included in staging

3. **Verify staging success**:
   - Run `git status` to verify files were successfully staged
   - Check that "Changes to be committed" section shows all expected files
   - Count the number of staged files

4. **Handle staging failures**:
   - If git add fails:
     - Capture the error message from git add command
     - Display: "Git staging failed: {error_message}. Manual staging required."
     - Provide manual recovery instructions: "Manually run: git add . && git commit -m 'Fix issue #{issue_number}: {issue_title}' && git push"
     - STOP execution (cannot commit without staging)

5. **Report staging status**:
   - Display: "Staged {count} file(s) for commit"
   - List key files staged (user stories, implementation log, modified source files)

### Step 9: Create Fix Commit

After staging all changes in Step 8:

1. **Create commit with standardized message**:
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

2. **Capture and verify commit**:
   - Capture the commit hash from git commit output
   - Run `git log -1 --oneline` to verify the commit was created successfully
   - Store the commit hash for reporting

3. **Handle commit failures**:
   - CRITICAL: If git commit fails, implementation-log.json MUST remain unchanged
   - Capture the error message from git commit command
   - Provide manual recovery instructions based on failure type
   - Display: "Commit failed: {error_message}. Manual intervention required."
   - If commit succeeded: CONTINUE to Step 10
   - If commit failed: SKIP Step 10 and jump to Report (cannot push without commit)

4. **Report commit status**:
   - Display: "Commit created successfully"
   - Display commit hash
   - Display commit message preview

### Step 10: Push to Remote Branch

After creating the fix commit in Step 9 (SKIP this step if commit failed):

1. **Check remote tracking status**:
   - Run `git branch -vv` to check if the current branch has remote tracking configured
   - Parse the output to determine if the branch tracks a remote

2. **Push to remote repository**:
   - If branch has remote tracking: Use `git push` to push the commit
   - If branch has no remote tracking: Use `git push -u origin {featureName}` to create remote branch and set tracking

3. **Verify push success**:
   - Check the git push command exit code to verify success
   - Capture any error output if the push fails
   - Run `git status` to confirm the branch is up-to-date with remote

4. **Handle push failures**:
   - CRITICAL: If git push fails, implementation-log.json MUST remain unchanged
   - IMPORTANT: Commit already exists locally, so this is a PARTIAL SUCCESS scenario
   - Capture the error message from git push command
   - Provide manual recovery instructions: "Push failed: {error_message}. Commit exists locally ({commit_hash}). Retry with: git push"
   - Report PARTIAL SUCCESS: "Commit created locally but push failed"
   - If push succeeded: CONTINUE to Step 11
   - If push failed: SKIP Step 11 and jump to Report (cannot close issue without confirming remote has changes)

5. **Report push status**:
   - Display: "Changes pushed successfully to remote branch {featureName}"
   - Display remote tracking information

### Step 11: Close GitHub Issue

After successfully pushing changes in Step 10 (SKIP this step if push failed):

1. **Close the issue with comment**:
   - Use `gh issue close {issue_number} --comment "Fixed in commit {commit_hash}. All CI/CD failures have been resolved."`
   - Verify the issue was closed by checking the command exit code

2. **Handle close failures**:
   - If closing fails:
     - Capture the error message
     - Display warning: "Failed to close issue automatically: {error_message}"
     - Provide manual instructions: "Please close issue #{issue_number} manually at GitHub"
     - Mark as PARTIAL SUCCESS (fix complete but issue remains open)
     - Continue to Report

3. **Report issue closure**:
   - Display: "Issue #{issue_number} closed successfully"
   - Display the closing comment

## Report

Provide a comprehensive summary with the following sections:

### Issue Details
- Issue number processed
- Issue title
- Feature ID: {featureID}
- Branch name: {featureName}
- Number of failed steps found: {count}

### Branch Status
- Previous branch (if switched): {previous_branch}
- Feature branch checked out: {featureName}
- Pull status: (updated/skipped/failed)
- Working tree status: (clean/has changes)

### Fix Story Creation
- Number of fix stories created: {count}
- Story titles:
  1. {story_1_title}
  2. {story_2_title}
  etc.
- User stories file location: `docs/features/{featureID}/issues/{issue_number}/user-stories.md`

### Implementation Status
- Total fix stories: {count}
- Completed stories: {count}
- Incomplete stories (if any): {list with status}
- Implementation log location: `docs/features/{featureID}/implementation-log.json`

### Git Workflow Status

#### Staging
- Files staged: {count}
- Key files:
  - User stories
  - Implementation log
  - Modified source files (list key ones)
- Staging status: (success/failure)

#### Commit
- Commit hash: {hash}
- Commit message: "Fix issue #{issue_number}: {issue_title}"
- Commit status: (success/failure)

#### Push
- Push status: (success/failure)
- Remote tracking: (configured/newly configured)
- Branch name: {featureName}
- Error details (if any): {error_message}

#### Issue Closure
- Issue #{issue_number} status: (closed/failed to close)
- Closing comment: "Fixed in commit {commit_hash}"

### Overall Status
- If ALL steps successful: Display "✅ Fix workflow completed successfully. Issue #{issue_number} has been fixed, pushed to {featureName}, and closed."
- If partial success (commit but no push): Display "⚠️ Fix committed locally but push failed. Manual push required: git push"
- If partial success (pushed but issue not closed): Display "⚠️ Fix committed and pushed but failed to close issue. Please close issue #{issue_number} manually."
- If any major failures: Display error summary with recovery instructions

### Next Steps
- If fully successful: "The fix has been pushed to {featureName}. You can now test the changes or merge the pull request if one exists."
- If partial success: Provide specific manual recovery steps based on what failed

## Error Handling

### Common Failure Scenarios

1. **Issue not found or invalid**:
   - Provide clear error message
   - Suggest verifying issue number with `gh issue list`

2. **Missing branch information in issue**:
   - Display which fields are missing from issue body
   - Explain that auto-fix requires branch information in format: `- **Branch**: {branch}`
   - Suggest manual fix workflow

3. **Main branch infrastructure issues**:
   - Clearly state that main branch issues cannot be auto-fixed
   - Explain that infrastructure issues require manual investigation
   - Suggest involving DevOps engineer

4. **Branch checkout fails**:
   - Display git error message
   - Check if branch exists locally with `git branch --list {branch}`
   - Suggest fetching from remote: `git fetch origin {branch}:{branch}`
   - Provide recovery command: `git checkout {featureName}`

5. **Product owner fails to create stories**:
   - Check if file was created but in wrong location
   - Display expected vs actual file locations
   - List contents of `docs/features/{featureID}/issues/` directory
   - Suggest manual story creation

6. **Implementation incomplete**:
   - List which stories failed with their status
   - Provide path to implementation log for details
   - Ask user if they want to continue with partial fix or stop

7. **Git operations fail**:
   - Preserve all completed work (stories, implementation)
   - Provide exact manual recovery commands
   - Never lose implementation progress
   - Distinguish between staging, commit, and push failures

8. **Issue closure fails**:
   - Treat as minor failure (fix is complete)
   - Provide manual closure instructions
   - Include link to issue for convenience

## Self-Verification Checklist

Before finalizing, verify:

- [ ] Issue number determined (from input or oldest issue)
- [ ] Issue metadata successfully extracted (branch, featureID)
- [ ] Main branch infrastructure failures rejected with clear message
- [ ] Switched to correct feature branch
- [ ] Product owner created 1-3 fix stories (not more)
- [ ] User stories saved to correct location (docs/features/{featureID}/issues/{issue_number}/)
- [ ] /implement command invoked with correct syntax: `/implement fix {issue_number}`
- [ ] All fix stories completed (or user acknowledged partial completion)
- [ ] Changes staged successfully
- [ ] Changes committed with proper message format
- [ ] Changes pushed to remote (or failure documented with recovery steps)
- [ ] Issue closed on GitHub (or failure documented)
- [ ] Clear status and next steps provided to user
