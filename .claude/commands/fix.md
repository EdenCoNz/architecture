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

4. **Extract Job URLs from issue**:
   - Parse the "## Failed Jobs and Steps" section from the issue body
   - For each failed job/step section, extract:
     - Job name and step name (from section heading like "### 1. {failed_job} - {failed step}")
     - Job URL (from line matching `**JobURL**:` or `**Job URL**:` followed by the URL)
   - Store all Job URLs in an array for processing in Step 2.5
   - Handle multiple URL formats:
     - Direct URL on same line: `**JobURL**: https://github.com/...`
     - URL on next line after label
     - Markdown link format: `**JobURL**: [View Job](https://github.com/...)`
   - Display: "Found {count} failed job(s)/step(s) with Job URLs in issue"
   - If no Job URLs found but error logs exist inline: Display warning "Issue uses old format with inline logs. Consider updating to new format with Job URLs."

### Step 2.5: Fetch Error Logs from Job URLs

1. **Extract job IDs from URLs**:
   - For each Job URL collected in Step 2.4, extract the job ID
   - Job URLs typically have format: `https://github.com/{owner}/{repo}/actions/runs/{run_id}/job/{job_id}`
   - Parse the URL to extract the job_id (numeric identifier at the end)
   - Store mapping of job_id to job/step name for reference

2. **Fetch logs using GitHub CLI**:
   - For each job_id, use gh CLI to fetch the job logs:
     - Command: `gh api repos/{owner}/{repo}/actions/jobs/{job_id}/logs`
     - The logs are returned as plain text with ANSI color codes
   - Store the raw logs temporarily for parsing

3. **Parse error information from logs**:
   - Search for error indicators in the logs:
     - Lines containing "Error:", "error:", "ERROR", "FAIL", "Failed", "Exception"
     - Exit code indicators (e.g., "Process exited with code")
     - Test failure summaries
     - Build failure messages
   - Extract context around errors (5-10 lines before and after error line)
   - Remove ANSI color codes and excessive whitespace
   - Limit extracted error context to ~50 lines per job to keep it manageable

4. **Handle fetch failures gracefully**:
   - If gh CLI is not authenticated: Display error "GitHub CLI not authenticated. Run 'gh auth login' to authenticate."
   - If job URL is invalid or inaccessible: Display warning "Could not fetch logs for job {job_id}. URL may be invalid or you may lack access permissions."
   - If API rate limit exceeded: Display error "GitHub API rate limit exceeded. Wait before retrying or use a token with higher limits."
   - For any failed fetches: Continue with other jobs and note which jobs failed
   - Store successfully fetched error logs with their associated job/step names

5. **Report fetch status**:
   - Display: "Successfully fetched logs from {success_count}/{total_count} job(s)"
   - If any fetches failed: List which job URLs failed and why
   - Prepare error data structure for Step 2.6

### Step 2.6: Summarize Errors for Product Owner

This step creates a clear, non-technical summary of errors that a product owner can understand.

1. **Analyze error patterns**:
   - Group similar errors together (e.g., multiple test failures, build errors, linting issues)
   - Identify root causes vs symptoms:
     - Syntax errors in code
     - Missing dependencies
     - Test failures (unit, integration, e2e)
     - Build/compilation failures
     - Deployment/infrastructure issues
     - Environment/configuration issues
   - Count occurrences of each error type

2. **Create product owner summary**:
   - For each error group, create a plain-language summary:
     - WHAT failed: "3 unit tests are failing in the authentication module"
     - WHY it failed: "The tests expect a user ID field that no longer exists in the database schema"
     - WHERE it failed: "Backend API tests in the login component"
   - Avoid technical jargon where possible
   - Focus on business impact, not stack traces
   - Use bullet points for clarity

3. **Format the summary**:
   - Structure the summary as markdown with clear sections:
     ```markdown
     ## Error Summary for Product Owner

     ### Overview
     - Total failures: {count}
     - Failure categories: {list}

     ### Detailed Breakdown

     #### 1. {Error Category Name}
     - **What Failed**: {plain language description}
     - **Why It Failed**: {root cause in simple terms}
     - **Impact**: {business/user impact}
     - **Jobs Affected**: {job names}

     #### 2. {Another Error Category}
     ...

     ### Technical Details
     {Condensed error logs for developer reference}
     ```

4. **Display summary to user**:
   - Present the product owner summary before proceeding to fix
   - This allows human oversight of what will be fixed
   - Display: "Error Summary:"
   - Print the formatted summary
   - Display: "Proceeding with fix user story creation..."

5. **Store summary for product owner agent**:
   - Save the formatted summary to pass to product-owner agent in Step 4
   - This gives the agent clear context for creating fix stories
   - The summary should be comprehensive but concise (target: 200-500 words)

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

Then, analyze the following error summary and create comprehensive user stories to fix the issues:

## Issue Details
- **Issue Number**: #{issue_number}
- **Issue Title**: {issue_title}
- **Feature ID**: {featureID}
- **Branch**: {featureName}

## Error Summary

{product_owner_summary}

## Technical Error Details

The following technical details were extracted from the CI/CD job logs for developer reference:

{technical_error_details}

## Your Task

Create 1-3 atomic user stories to fix these failures. Each story should:
- Address one specific failure or a closely related group of failures
- Be assigned to the appropriate agent (frontend-developer, backend-developer, devops-engineer, etc.)
- Have clear, testable acceptance criteria
- Focus on fixing the root cause, not just the symptom
- Use the product owner summary to understand WHAT and WHY, and the technical details to understand HOW

## File Location Requirements

**CRITICAL**: You MUST save the user stories to the following location:
`docs/features/{featureID}/issues/{issue_number}/user-stories.md`

Create the directory structure if it doesn't exist.

## Feature Log Update

After creating the user stories file, you MUST also update `docs/features/feature-log.json`:
1. Find the feature entry with matching featureID
2. Add an issue entry if one doesn't exist for this issue number
3. Record that fix user stories have been created

Plan the user stories based on the available agents and the nature of the failures. Use the product owner summary to communicate the business context, and reference the technical details as needed for implementation guidance.
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

### Step 8: Commit and Push Changes

After verifying implementation completion in Step 7:

1. **Check for changes**:
   - Run `git status --porcelain` to get list of modified/untracked files
   - Count the number of files with changes
   - If no changes detected: Display warning "No changes detected to commit" and SKIP to Step 9 (Close Issue)

2. **Use /push command to stage, commit, and push**:
   - Use SlashCommand tool to execute: `/push "Fix issue #{issue_number}: {issue_title}"`
   - The /push command will automatically:
     - Stage all changes with `git add .`
     - Create a commit with the provided message (including Claude Code footer)
     - Push to remote (configuring tracking if needed)
   - Wait for /push to complete

3. **Monitor /push completion**:
   - The /push command handles all git operations automatically
   - It will report staging, commit, and push status
   - Capture the commit hash and push status from /push output

4. **Handle /push failures**:
   - CRITICAL: If /push fails, implementation-log.json MUST remain unchanged
   - The /push command provides detailed error reporting for:
     - Staging failures
     - Commit failures
     - Push failures (partial success if commit succeeded)
   - Follow the recovery instructions provided by /push
   - If /push succeeded: CONTINUE to Step 9
   - If /push failed: SKIP Step 9 and jump to Report (cannot close issue without confirming remote has changes)

## Report

Provide a comprehensive summary with the following sections:

### Issue Details
- Issue number processed
- Issue title
- Feature ID: {featureID}
- Branch name: {featureName}
- Number of failed jobs found: {count}
- Job URLs extracted: {count}

### Error Log Fetch Status
- Job logs fetched: {success_count}/{total_count}
- Failed fetches (if any):
  - Job URL: {url}
  - Reason: {error_reason}
- Error summary created: (yes/no)
- Error categories identified: {list of categories}

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

#### /push Command Execution
- Commit hash: {hash}
- Commit message: "Fix issue #{issue_number}: {issue_title}"
- Files staged: {count}
- Key files:
  - User stories
  - Implementation log
  - Modified source files (list key ones)
- Push status: (success/failure)
- Remote tracking: (configured/newly configured)
- Branch name: {featureName}
- Overall /push status: (success/partial success/failure)
- Error details (if any): {error_message}

#### Issue Closure
- Issue #{issue_number} status: (closed/failed to close)
- Closing comment: "Fixed in commit {commit_hash}"

### Overall Status
- If ALL steps successful: Display "✅ Fix workflow completed successfully. Issue #{issue_number} has been fixed, pushed to {featureName}, and closed."
- If partial success (commit but no push): Display "⚠️ Fix committed locally but push failed. Retry with: `/push \"Fix issue #{issue_number}: {issue_title}\"`"
- If partial success (pushed but issue not closed): Display "⚠️ Fix committed and pushed but failed to close issue. Please close issue #{issue_number} manually."
- If any major failures: Display error summary with recovery instructions

### Next Steps
- If fully successful: "The fix has been pushed to {featureName}. You can now test the changes or merge the pull request if one exists."
- If partial success: Provide specific manual recovery steps based on what failed (follow /push command's error guidance)

## Error Handling

### Common Failure Scenarios

1. **Issue not found or invalid**:
   - Provide clear error message
   - Suggest verifying issue number with `gh issue list`

2. **Missing branch information in issue**:
   - Display which fields are missing from issue body
   - Explain that auto-fix requires branch information in format: `- **Branch**: {branch}`
   - Suggest manual fix workflow

3. **Missing Job URLs in issue**:
   - Display error: "Issue #{issue_number} does not contain Job URLs in the expected format"
   - Check if issue uses old format with inline error logs
   - If old format detected: Suggest updating issue with Job URLs or proceeding with inline logs (fallback mode)
   - If neither Job URLs nor inline logs found: STOP and display "Cannot proceed without error information. Please add Job URLs to the issue."

4. **GitHub CLI authentication failure**:
   - Display error: "GitHub CLI is not authenticated. Cannot fetch job logs."
   - Provide authentication instructions: "Run 'gh auth login' to authenticate with GitHub"
   - Suggest alternative: "Or manually add error logs to the issue in the old format"
   - STOP execution (cannot fetch logs without authentication)

5. **Job log fetch failures**:
   - If some jobs succeed but others fail:
     - Display warning: "Failed to fetch logs from {failed_count}/{total_count} job(s)"
     - List which job URLs failed and the reason (invalid URL, access denied, rate limit, etc.)
     - Ask user: "Continue with partial error information, or stop to investigate failed fetches?"
     - If user chooses continue: Proceed with available error logs
     - If user chooses stop: STOP execution
   - If all jobs fail:
     - Display error: "Could not fetch logs from any job URLs"
     - List all failures with reasons
     - Suggest checking: Job URL format, repository access permissions, API rate limits
     - STOP execution (cannot create fix without any error information)

6. **Empty or unparseable job logs**:
   - Display warning: "Job logs for {job_id} contain no recognizable error patterns"
   - Include the job URL for manual inspection
   - Continue with other jobs if available
   - If all logs are empty: Display error "No error information found in any job logs. Manual investigation required."

7. **Main branch infrastructure issues**:
   - Clearly state that main branch issues cannot be auto-fixed
   - Explain that infrastructure issues require manual investigation
   - Suggest involving DevOps engineer

8. **Branch checkout fails**:
   - Display git error message
   - Check if branch exists locally with `git branch --list {branch}`
   - Suggest fetching from remote: `git fetch origin {branch}:{branch}`
   - Provide recovery command: `git checkout {featureName}`

9. **Product owner fails to create stories**:
   - Check if file was created but in wrong location
   - Display expected vs actual file locations
   - List contents of `docs/features/{featureID}/issues/` directory
   - Suggest manual story creation

10. **Implementation incomplete**:
    - List which stories failed with their status
    - Provide path to implementation log for details
    - Ask user if they want to continue with partial fix or stop

11. **Git operations fail**:
    - Preserve all completed work (stories, implementation)
    - The /push command provides detailed error reporting and recovery instructions
    - Never lose implementation progress
    - Follow the specific recovery steps provided by /push command output

12. **Issue closure fails**:
    - Treat as minor failure (fix is complete)
    - Provide manual closure instructions
    - Include link to issue for convenience

## Self-Verification Checklist

Before finalizing, verify:

- [ ] Issue number determined (from input or oldest issue)
- [ ] Issue metadata successfully extracted (branch, featureID)
- [ ] Job URLs extracted from issue (or fallback to inline logs with warning)
- [ ] Job IDs parsed from Job URLs correctly
- [ ] GitHub CLI authentication verified before fetching logs
- [ ] Job logs fetched successfully (or partial fetch handled gracefully)
- [ ] Error information parsed from logs (error patterns identified)
- [ ] Product owner error summary created (non-technical, business-focused)
- [ ] Error summary displayed to user before proceeding
- [ ] Main branch infrastructure failures rejected with clear message
- [ ] Switched to correct feature branch
- [ ] Product owner created 1-3 fix stories (not more)
- [ ] User stories saved to correct location (docs/features/{featureID}/issues/{issue_number}/)
- [ ] /implement command invoked with correct syntax: `/implement fix {issue_number}`
- [ ] All fix stories completed (or user acknowledged partial completion)
- [ ] /push command invoked with correct message format
- [ ] /push command completed successfully (or failure documented with recovery steps)
- [ ] Issue closed on GitHub (or failure documented)
- [ ] Clear status and next steps provided to user
- [ ] All error scenarios properly handled (auth, fetch failures, empty logs, etc.)
