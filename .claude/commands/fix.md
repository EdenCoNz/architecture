---
description: Fix a bug by analyzing GitHub issue and creating targeted user stories
args:
  - name: issue_number
    description: GitHub issue number containing the bug details
    required: true
model: claude-sonnet-4-5
---

## Purpose

Fix bugs efficiently by analyzing GitHub issues, creating targeted user stories for the fix, and automatically implementing them. This command bridges the gap between bug reports and implementation by leveraging the existing feature workflow infrastructure while optimizing for bug-fixing scenarios.

## Variables

- `$ISSUE_NUMBER` - The GitHub issue number to fix
- Issue details path: `docs/issues/{issue_number}/`
- Fix log path: `docs/issues/{issue_number}/fix-log.md`

## Instructions

- Parse GitHub issue to extract bug details
- Create minimal, focused user stories for the fix
- Use append-in-place logging to track fix progress
- Automatically implement fix using existing agents
- Do NOT create new feature branch (work on current branch)
- Do NOT run pre-flight checks (fixes can happen anytime)

## Workflow

### Step 1: Validate Issue Exists

1. **Fetch issue details from GitHub**:
   - Use `gh issue view $ISSUE_NUMBER --json number,title,body,state,labels` to fetch issue details
   - Parse the JSON output to extract: number, title, body, state, labels
   - If command fails or issue not found: STOP execution and inform user with message: "Error: Issue #$ISSUE_NUMBER not found. Please verify the issue number exists."

2. **Verify issue is open**:
   - Check that state is "OPEN"
   - If issue is already closed: ASK user if they want to proceed anyway using AskUserQuestion tool
   - If user says no: STOP execution
   - If user says yes: CONTINUE but note in log that issue was already closed

3. **Store issue details**:
   - Store title, body, labels for use in subsequent steps
   - Display brief confirmation: "Found issue #$ISSUE_NUMBER: {title}"

### Step 2: Parse Issue Details

1. **Extract structured information from issue body**:
   - Look for table with fields: title, featureID, featureName, jobName, stepName, logLineNumbers, PRURL, commitURL, runURL
   - Parse table format: `| Field | Value |` with `|-------|-------|` separator
   - Extract each field value by matching the field name in the first column
   - If table format not found: Use issue title and body as-is (handle generic bug reports)

2. **Determine issue type** (Hybrid Detection Approach):

   **A. Explicit Detection** (check for workflow-specific markers):
   - Check if issue body contains workflow failure table (| title | featureID | etc.)
   - Check if labels include "workflow-failure" or similar
   - Check if title starts with "Workflow Failure:"
   - If ANY of these match: Issue type is "workflow-failure"

   **B. Validation Detection** (check for test/lint/build failure markers):
   - Check if jobName contains: "test", "lint", "format", "build", "ci", "check"
   - Check if failed step log contains: "error", "failed", "✖", "problems", "exit code 1"
   - If workflow-failure AND validation markers present: Issue type is "validation-failure"

   **C. Fallback**:
   - If neither A nor B match: Issue type is "generic-bug"

3. **Extract failure context** (for validation-failure type):
   - Parse failed step log excerpt to identify:
     - Specific error messages (ESLint errors, test failures, build errors)
     - File paths mentioned in errors
     - Line numbers mentioned in errors
     - Error codes or categories (prettier/prettier, @typescript-eslint/no-unused-vars, etc.)
   - Create list of specific issues to fix (e.g., "Fix prettier formatting in Home.test.tsx lines 82, 96, 406, 448, 471")

4. **Store parsed data**:
   - Create docs/issues/{issue_number}/ directory if it doesn't exist
   - Store parsed issue data in memory for next steps
   - Report issue type and key details: "Issue type: {type}, Feature: #{featureID}, Affected files: {files}"

### Step 3: Create Fix Log (Append-in-Place)

1. **Initialize fix log file**:
   - Create docs/issues/{issue_number}/fix-log.md
   - Use append-in-place structure with clear delimiters for each attempt
   - Include issue metadata in header

2. **Write initial log header**:
   ```markdown
   # Fix Log: Issue #{issue_number}

   ## Issue Details
   - **Title**: {issue_title}
   - **Type**: {issue_type}
   - **State**: {issue_state}
   - **Opened**: {timestamp}
   - **Source**: https://github.com/{owner}/{repo}/issues/{issue_number}

   {Additional context based on issue type - featureID, PRURL, jobName, etc.}

   ---

   ## Fix Attempts

   {Attempts will be appended below with delimiters}
   ```

3. **Create first fix attempt entry**:
   ```markdown
   ### Attempt #1 - {timestamp}

   **Strategy**: {description of fix approach based on issue analysis}

   **User Stories Created**: {count}

   **Status**: In Progress

   {Details will be appended as fix progresses}

   ---
   ```

4. **Log creation confirmation**:
   - Display: "Fix log initialized at docs/issues/{issue_number}/fix-log.md"

### Step 4: Create Targeted User Stories

1. **Determine fix scope** based on issue type:

   **For validation-failure**:
   - Create ONE user story per category of error (e.g., "Fix ESLint prettier errors", "Fix unused variable warnings")
   - Focus on specific files and line numbers identified in Step 2
   - Keep stories atomic and focused on single error category

   **For workflow-failure** (non-validation):
   - Create ONE user story for the workflow issue
   - Focus on the specific job/step that failed

   **For generic-bug**:
   - Analyze issue description to create 1-3 focused user stories
   - Break down only if bug has clearly separable components

2. **Launch product-owner agent in FIX MODE**:

   Use the Task tool to launch the product-owner agent with special fix mode instructions:

   ```
   MODE: FIX

   You are operating in FIX MODE to address a specific bug/issue. This is different from feature development.

   IMPORTANT FIX MODE RULES:
   - Create MINIMAL user stories (1-3 maximum) focused solely on fixing this specific issue
   - Do NOT create comprehensive feature stories
   - Do NOT separate design from implementation unless absolutely necessary
   - Stories should be fix-focused, not feature-focused
   - Use issue details to create precise, targeted fixes

   Issue to fix:
   Issue #: {issue_number}
   Title: {issue_title}
   Type: {issue_type}

   {For validation-failure, include:}
   Affected Files: {file_list}
   Error Categories: {error_categories}
   Specific Errors:
   {detailed_error_list}

   {For workflow-failure, include:}
   Failed Job: {jobName}
   Failed Step: {stepName}
   Feature: #{featureID}

   {For generic-bug, include:}
   Bug Description:
   {issue_body}

   Create minimal, targeted user stories to fix this issue. Focus on:
   1. What needs to be fixed (be specific)
   2. How to verify the fix worked
   3. Assign to appropriate agent (frontend-developer, backend-developer, etc.)

   Output format: Create docs/issues/{issue_number}/user-stories.md with the same structure as feature user stories but optimized for fixes.
   ```

3. **Verify user stories created**:
   - Check that docs/issues/{issue_number}/user-stories.md was created
   - Verify stories are minimal and focused (ideally 1-3 stories)
   - If more than 5 stories created: WARN that this seems excessive for a bug fix

4. **Append to fix log**:
   ```markdown
   **User Stories**: docs/issues/{issue_number}/user-stories.md
   - Story 1: {title}
   - Story 2: {title}
   ...

   **Execution Plan**: {sequential/parallel phases}
   ```

### Step 5: Implement Fix

1. **Execute user stories** (similar to /implement but for fixes):

   For each user story in execution order:
   - Launch appropriate agent with story details
   - Provide fix context: "You are fixing Issue #{issue_number}: {title}"
   - Include reference to original issue details
   - Request implementation log in docs/issues/{issue_number}/implementation-log.json

2. **Monitor implementation progress**:
   - Track completion of each story
   - Append progress updates to fix log:
   ```markdown
   **Implementation Progress**:
   - [✓] Story 1: {title} - Completed at {timestamp}
   - [⧗] Story 2: {title} - In progress
   - [ ] Story 3: {title} - Pending
   ```

3. **Handle implementation failures**:
   - If any story fails or is blocked: Append failure details to fix log
   - Ask user if they want to: (a) Continue with remaining stories, (b) Stop and review, (c) Create new fix attempt
   - Log decision in fix log

### Step 6: Verify Fix

1. **For validation-failure issues**:
   - Read the implementation log to identify files that were modified
   - Determine appropriate validation command based on original failure:
     - If jobName contains "lint": Run `npm run lint` (or equivalent)
     - If jobName contains "test": Run `npm run test` (or equivalent)
     - If jobName contains "build": Run `npm run build` (or equivalent)
     - If jobName contains "format": Run `npm run format:check` (or equivalent)
   - Execute validation command in appropriate directory (e.g., frontend/)
   - Capture command output and exit code

2. **Analyze validation results**:
   - If exit code is 0: Validation passed ✓
   - If exit code is non-zero: Validation failed ✗
   - Parse output to identify remaining issues (if any)
   - Compare original errors with current errors to determine progress

3. **Append validation results to fix log**:
   ```markdown
   **Validation Results**:
   - Command: {validation_command}
   - Exit Code: {exit_code}
   - Status: {Passed/Failed}

   {If failed, include:}
   Remaining Issues:
   - {error_1}
   - {error_2}
   ...

   Progress: {X/Y errors fixed}
   ```

4. **For non-validation issues**:
   - Skip automated validation
   - Append note: "Manual verification required - no automated validation available"
   - Provide testing instructions based on issue type

### Step 7: Finalize Fix Attempt

1. **Update fix log with final status**:
   ```markdown
   **Final Status**: {Success/Partial Success/Failed}

   {If Success:}
   All issues resolved. Ready for commit.

   {If Partial Success:}
   Progress made: {X/Y} issues resolved
   Remaining issues: {list}
   Recommendation: {Create Attempt #2 / Manual intervention needed / etc.}

   {If Failed:}
   Fix did not resolve issues
   Errors: {list}
   Recommendation: {Analyze root cause / Different approach needed / etc.}
   ```

2. **Determine next steps** based on validation results:

   **If validation passed OR no validation available**:
   - CONTINUE to Step 8 (Commit & Close)

   **If validation failed but progress made**:
   - Ask user: "Validation failed but {X/Y} issues were fixed. Options: (a) Commit partial fix, (b) Create Attempt #2 to fix remaining issues, (c) Stop and review manually"
   - If user chooses (a): CONTINUE to Step 8 with partial fix note
   - If user chooses (b): JUMP back to Step 4 with new attempt number, append to fix log
   - If user chooses (c): STOP execution, provide fix log location

   **If validation failed with no progress**:
   - STOP execution, do not commit
   - Inform user: "Fix did not resolve issues. Review fix log at docs/issues/{issue_number}/fix-log.md for details."

3. **Append completion timestamp**:
   ```markdown
   **Completed**: {timestamp}

   ---
   ```

### Step 8: Commit Fix and Close Issue

1. **Stage all modified files**:
   - Use `git add .` to stage all changes
   - Verify staging with `git status`
   - Include fix log, user stories, implementation log, and code changes

2. **Create fix commit**:
   - Use standardized commit message format:
   ```
   Fix: Issue #{issue_number} - {issue_title}

   {Brief description of what was fixed}

   Fixes #{issue_number}

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```
   - Use HEREDOC for proper formatting
   - The "Fixes #{issue_number}" line will automatically close the issue when pushed

3. **Verify commit**:
   - Run `git log -1` to confirm commit created
   - Store commit hash for reporting

4. **Handle commit failures**:
   - If commit fails: Capture error message
   - Append to fix log: "Commit failed: {error}"
   - Provide manual recovery instructions
   - Do NOT attempt to close issue if commit failed

5. **Push to remote** (if commit succeeded):
   - Check if current branch has remote tracking: `git branch -vv`
   - Push using `git push` or `git push -u origin {branch}` if needed
   - Verify push success

6. **Close issue on GitHub** (if push succeeded):
   - The commit message "Fixes #{issue_number}" will auto-close when merged to main
   - If on main branch: Issue will close immediately after push
   - If on feature branch: Issue will close when PR is merged
   - Add comment to issue with fix details:
   ```
   gh issue comment {issue_number} --body "Fixed in commit {commit_hash}

   Fix details: docs/issues/{issue_number}/fix-log.md"
   ```

7. **Handle failures gracefully**:
   - If push fails: Provide manual recovery instructions, do not attempt issue close
   - If issue comment fails: Continue (non-critical), note in report
   - Append all outcomes to fix log

## Report

Provide a comprehensive summary with the following sections:

### Issue Details
- Issue number and title
- Issue type (workflow-failure/validation-failure/generic-bug)
- Issue state (open/closed)
- Feature association (if applicable)
- Source URL

### Issue Analysis
- Parsed information (featureID, affected files, error categories, etc.)
- Number of specific errors identified
- Fix strategy determined

### User Stories Created
- Number of stories created
- Story titles and assigned agents
- Execution plan (sequential/parallel phases)
- User stories location: docs/issues/{issue_number}/user-stories.md

### Implementation Status
- Number of stories completed vs. total
- Agents launched and their status
- Any failures or blocked stories
- Implementation log location: docs/issues/{issue_number}/implementation-log.json

### Validation Results (if applicable)
- Validation command executed
- Validation status (passed/failed/skipped)
- Original error count vs. remaining error count
- Specific errors fixed
- Remaining issues (if any)

### Fix Attempt Summary
- Attempt number
- Final status (Success/Partial Success/Failed)
- Timestamp range (started - completed)
- Files modified
- Fix log location: docs/issues/{issue_number}/fix-log.md

### Git Workflow Status

#### Commit
- Commit hash (if successful)
- Commit message
- Files committed
- Commit errors (if any)

#### Push
- Push status (success/failure)
- Branch name
- Push errors (if any)

#### Issue Status
- Issue closed automatically (yes/no)
- Issue comment added (yes/no)
- Manual steps needed (if any)

### Overall Status
- If ALL steps successful: "Issue #{issue_number} fixed and closed successfully"
- If partial success: "Issue #{issue_number} partially fixed - {details}"
- If failed: "Fix attempt failed - {details}"

### Next Steps
- If successful: "Issue resolved. Changes committed and pushed."
- If partial: "Review remaining issues in fix log. Consider creating Attempt #2."
- If failed: "Review fix log for details. Manual intervention may be needed."

### Fix Log Location
- Full path to fix log for detailed records and debugging

## Edge Cases

### Multiple Fix Attempts
- Each attempt appends to fix-log.md with clear delimiters
- Attempt numbers increment: Attempt #1, Attempt #2, etc.
- Each attempt includes: strategy, user stories, implementation progress, validation results, final status
- Previous attempts remain visible for historical context

### Validation Not Applicable
- For generic bugs without automated validation: Skip Step 6, proceed to commit
- Note in fix log: "Manual verification required"
- Provide testing instructions in fix log based on issue description

### Issue Already Closed
- Ask user if they want to proceed (may be reopening/additional fix)
- If yes: Continue normally but note in fix log
- If no: STOP execution

### No Errors Found in Validation
- If validation passes before fix attempt: Inform user "Issue may already be resolved"
- Ask user: "Validation passes but issue is still open. Options: (a) Close issue, (b) Investigate further, (c) Cancel"
- Handle based on user choice

### Commit Message Magic Words
- "Fixes #{issue_number}" auto-closes issue when merged to default branch
- "Closes #{issue_number}" is equivalent
- "Resolves #{issue_number}" is equivalent
- Other keywords that work: "Fix", "Close", "Resolve" (with #number)

### Working on Feature Branch
- Fix committed to current branch (typically feature branch)
- Issue will auto-close when PR is merged to main (due to "Fixes #" in commit message)
- Note in report: "Issue will close when PR is merged"

### Multiple Issues in Same Attempt
- This command handles ONE issue at a time
- If multiple related issues: User should run /fix multiple times or manually combine
- Each issue gets its own fix log and user stories
