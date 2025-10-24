---
description: Commit message for the changes to be committed and pushed
model: claude-sonnet-4-5
---

## Purpose

Stage all changes, commit them with a provided message, and push to the remote repository. This command streamlines the git workflow by executing three sequential operations: `git add .`, `git commit`, and `git push`.

## Variables

- `{{{ input }}}` - The commit message to use for the commit
- Current branch - Automatically detected from git
- Remote tracking - Automatically configured if not already set

## Instructions

- Execute git operations sequentially (add, commit, push)
- Use standardized commit message format with Claude Code footer
- Handle errors gracefully at each stage
- Verify each operation succeeds before proceeding to the next
- Configure remote tracking automatically if needed

## Workflow

### Step 1: Validate Commit Message

1. **Check message argument**:
   - Verify `{{{ input }}}` is provided and non-empty
   - Trim whitespace from the message
   - If empty or not provided: STOP and display error:
     ```
     Error: Commit message is required.

     Usage:
       /push "Your commit message here"

     Example:
       /push "Add new feature to improve user authentication"
     ```

2. **Store commit message**:
   - Store the trimmed message for use in Step 3
   - Display: "Preparing to commit with message: {message}"

### Step 2: Stage All Changes

1. **Check for changes**:
   - Run `git status --porcelain` to get list of modified/untracked files
   - Parse the output to count files with changes
   - If no changes detected:
     - Display: "No changes detected to commit"
     - STOP execution (nothing to stage or commit)

2. **Stage all files**:
   - Run `git add .` to stage all modified and new files in the working directory
   - This ensures both modified files and new files are included in staging
   - Capture any error output from the command

3. **Verify staging success**:
   - Run `git status` to verify files were successfully staged
   - Check that "Changes to be committed" section shows files
   - Count the number of staged files for reporting

4. **Handle staging failures**:
   - If git add fails:
     - Capture the error message
     - Display: "Git staging failed: {error_message}"
     - Provide manual recovery: "Please manually run: git add . && git commit -m 'message' && git push"
     - STOP execution (cannot proceed without successful staging)

5. **Report staging status**:
   - Display: "Staged {count} file(s) for commit"

### Step 3: Create Commit

1. **Get current branch**:
   - Run `git branch --show-current` to determine current branch
   - Store branch name for reporting and push operation

2. **Create commit with standardized format**:
   - Commit message format: User's message + Claude Code footer
   - Use git commit with HEREDOC format for proper formatting:
     ```bash
     git commit -m "$(cat <<'EOF'
     {user_message}

     🤖 Generated with [Claude Code](https://claude.com/claude-code)

     Co-Authored-By: Claude <noreply@anthropic.com>
     EOF
     )"
     ```
   - Replace {user_message} with the actual message from Step 1

3. **Verify commit success**:
   - Capture the commit hash from git commit output
   - Run `git log -1 --oneline` to verify the commit was created
   - Store the commit hash for reporting

4. **Handle commit failures with intelligent auto-fix**:
   - If git commit fails:
     - Capture the full error output (stdout and stderr)
     - Display: "Commit failed"
     - Analyze the failure type:
       - **Hook failures** (pre-commit, commit-msg, etc.):
         - Apply the "Hook Failure Resolution" workflow (see dedicated section below)
         - Automatically analyze, fix, and retry commit up to 2 times
         - Display progress: "🔍 Analyzing commit hook failure..."
         - Launch appropriate agent (backend-developer, frontend-developer, or devops-engineer)
         - Agent fixes the issues automatically
         - Retry commit after fixes are applied
         - If successful after auto-fix: Display "✅ Commit successful after auto-fix!" and continue
         - If retry limit reached: Display error and STOP execution
       - **Empty commit** (no changes staged):
         - Display: "No changes to commit after staging"
         - Suggest checking .gitignore rules or git status
         - STOP execution (nothing to commit)
       - **Git configuration issues** (missing user.name or user.email):
         - Display: "Git user.name or user.email not configured"
         - Provide configuration commands:
           ```
           git config user.name "Your Name"
           git config user.email "your.email@example.com"
           ```
         - STOP execution (requires manual config)
       - **Other failures**:
         - Display the error message
         - Provide appropriate manual recovery instructions
         - STOP execution

5. **Report commit status**:
   - Display: "Commit created successfully: {commit_hash}"
   - Display the first line of the commit message
   - If auto-fix was used: Display summary of issues fixed and number of retry attempts

### Step 4: Push to Remote

1. **Check remote tracking status**:
   - Run `git branch -vv` to check if current branch has remote tracking
   - Parse output to determine if branch tracks a remote
   - Store remote tracking information

2. **Push to remote repository**:
   - If branch has remote tracking:
     - Use `git push` to push the commit to the tracked remote
   - If branch has no remote tracking:
     - Use `git push -u origin {branch_name}` to create remote branch and set up tracking
     - This configures the branch to track origin/{branch_name} for future pushes

3. **Verify push success**:
   - Check the git push command exit code
   - Capture any error output if push fails
   - Run `git status` to confirm branch is up-to-date with remote

4. **Handle push failures**:
   - If git push fails:
     - Capture the error message
     - Display: "Push failed: {error_message}"
     - Common failure reasons:
       - Remote branch diverged (need to pull first)
       - No write access to remote repository
       - Network connectivity issues
       - Remote branch protected by branch protection rules
     - Provide recovery guidance based on error:
       - For diverged branches: "Pull latest changes with 'git pull' and resolve conflicts, then retry push"
       - For permission issues: "Verify you have write access to the repository"
       - For protected branches: "Create a pull request instead of pushing directly"
     - Note: Commit exists locally ({commit_hash}), so this is a PARTIAL SUCCESS
     - User can retry push manually with: `git push`

5. **Report push status**:
   - If successful: Display "Changes pushed successfully to {remote}/{branch_name}"
   - Display remote tracking information
   - Display the commit that was pushed

## Report

Provide a comprehensive summary with the following sections:

### Execution Summary
- Commit message used: "{user_message}"
- Branch: {branch_name}
- Files staged: {count}
- Commit hash: {commit_hash}
- Push status: (success/failure)
- Remote: {remote_name}/{branch_name}

### Git Operations Status

#### Staging
- Status: (success/failure)
- Files staged: {count}
- Key files staged (list main ones if notable)

#### Commit
- Status: (success/failure)
- Commit hash: {commit_hash}
- Commit message (first line): {message}

#### Push
- Status: (success/failure)
- Remote tracking: (already configured/newly configured)
- Remote branch: {remote}/{branch}
- Error details (if failed): {error_message}

### Overall Status
- If ALL steps successful:
  - Display: "✅ Successfully committed and pushed changes to {remote}/{branch}"
- If partial success (commit but no push):
  - Display: "⚠️ Changes committed locally ({commit_hash}) but push failed. Retry with: git push"
- If any step failed:
  - Display which step failed and the error message
  - Provide manual recovery instructions

### Next Steps
- If fully successful: "Your changes are now on the remote repository. You can create a pull request if needed."
- If partial success: Provide specific manual steps to complete the push
- If failed: Provide recovery steps based on which stage failed

## Error Handling

### Common Failure Scenarios

1. **Missing commit message**:
   - Display clear error with usage example
   - Explain that commit message is required

2. **No changes to commit**:
   - Display: "No changes detected. Nothing to commit."
   - Suggest using `git status` to verify working directory state

3. **Staging failures**:
   - Display git error message
   - Common causes: File permission issues, .gitignore conflicts
   - Suggest manual staging with specific files

4. **Commit failures**:
   - Pre-commit hook failures:
     - Display hook output
     - Explain what needs to be fixed
     - Suggest using `--no-verify` flag only if appropriate
   - Empty commit after staging:
     - Display: "No changes to commit after staging"
     - Suggest checking .gitignore rules
   - Missing git configuration:
     - Display: "Git user.name or user.email not configured"
     - Provide configuration commands:
       ```
       git config user.name "Your Name"
       git config user.email "your.email@example.com"
       ```

5. **Push failures**:
   - Branch diverged:
     - Explain that remote has changes not present locally
     - Suggest: `git pull --rebase` or `git pull` then retry push
   - No remote configured:
     - Should be handled automatically with `git push -u origin {branch}`
     - If still fails, suggest checking remote configuration with `git remote -v`
   - Permission denied:
     - Display: "No write access to remote repository"
     - Suggest verifying repository permissions and authentication
   - Protected branch:
     - Display: "Cannot push to protected branch {branch}"
     - Suggest creating a feature branch and pull request instead
   - Network issues:
     - Display: "Network error during push"
     - Suggest checking internet connection and retrying

6. **Branch tracking issues**:
   - If automatic tracking setup fails:
     - Provide manual command: `git push --set-upstream origin {branch}`
     - Explain that this sets up tracking for future pushes

## Hook Failure Resolution

When a commit hook fails (pre-commit, pre-push, etc.), automatically analyze the failure, identify the best agent to fix it, and implement the fix.

### Failure Detection and Analysis

1. **Capture hook failure output**:
   - When `git commit` exits with non-zero code, capture the full error output
   - Parse the output to identify which hook failed (pre-commit, commit-msg, etc.)
   - Extract specific error messages and file references

2. **Classify the failure type** by analyzing error patterns:

   **Python/Django Backend Issues** (use backend-developer agent):
   - Linting errors: `flake8`, `pylint`, `ruff` errors
   - Type checking errors: `mypy`, `pyright` errors
   - Test failures: `pytest`, unittest failures
   - Import errors: Missing or circular imports
   - Code quality: Complexity warnings, security issues
   - Patterns to match:
     - "E501 line too long"
     - "F401 imported but unused"
     - "error: " (mypy errors)
     - "FAILED" (pytest failures)
     - ".py:" (Python file references)

   **Frontend Issues** (use frontend-developer agent):
   - JavaScript/TypeScript errors: ESLint, TSC errors
   - React/Vue component issues
   - Patterns to match:
     - ".ts:", ".tsx:", ".js:", ".jsx:"
     - "ESLint"
     - "TypeScript"

   **DevOps/Infrastructure Issues** (use devops-engineer agent):
   - Dockerfile lint errors: hadolint
   - GitHub Actions workflow errors
   - Docker Compose validation errors
   - Patterns to match:
     - "Dockerfile"
     - ".github/workflows/"
     - "docker-compose"
     - "hadolint"

   **Configuration/Documentation Issues** (handle directly, no agent):
   - YAML/JSON syntax errors
   - Markdown formatting
   - .env.example validation
   - Can be fixed with simple edits

3. **Determine if auto-fix is appropriate**:
   - ✅ Auto-fix for: Linting errors, formatting issues, type errors, import cleanup
   - ✅ Auto-fix for: Test failures caused by code changes (update tests)
   - ❌ Skip auto-fix for: Git configuration issues (user.name, user.email)
   - ❌ Skip auto-fix for: Empty commits (no changes to commit)
   - ❌ Skip auto-fix for: Merge conflicts or complex issues requiring user decision

### Auto-Fix Workflow

**Initialize retry tracking**:
- Set `max_retry_attempts = 2` (avoid infinite loops)
- Set `current_attempt = 0`
- Store original commit message for retry

**When commit hook fails**:

1. **Analyze and categorize**:
   - Parse error output to determine failure type
   - Identify affected files from error messages
   - Determine appropriate agent (backend-developer, frontend-developer, or devops-engineer)

2. **Display analysis**:
   ```
   🔍 Analyzing commit hook failure...

   Hook: pre-commit
   Failure type: Python linting errors (flake8)
   Affected files:
     - backend/apps/users/models.py (line too long)
     - backend/apps/core/database.py (unused import)

   ⚙️ Attempting automatic fix using backend-developer agent...
   ```

3. **Parse and deduplicate errors (Token Optimization)**:
   - Extract unique error patterns from the full error output
   - Group duplicate errors by type and file
   - Create a condensed error summary:
     - "E501 line too long (3 occurrences in backend/apps/users/models.py)"
     - "F401 unused import (2 occurrences across 2 files)"
   - Limit to ~20 lines of unique errors instead of passing 100+ lines of repetitive output
   - Keep just enough context for the agent to understand and fix the issues

4. **Launch appropriate agent**:
   - Use the Task tool with the appropriate subagent_type
   - Provide condensed context:
     ```
     A pre-commit hook failed while attempting to commit code.

     Error Summary (deduplicated):
     {condensed_error_summary}

     Affected Files:
     {list_of_affected_files}

     Your task:
     1. Fix all identified issues in the affected files
     2. Ensure the fixes maintain code functionality and don't break tests
     3. Verify the fixes resolve all the errors mentioned

     After fixing, I will automatically retry the commit.
     ```
   - Agents to use based on issue type:
     - `backend-developer`: Python/Django code, tests, type errors
     - `frontend-developer`: JS/TS/React code, frontend tests
     - `devops-engineer`: Docker, CI/CD, infrastructure configs
   - **Token Optimization**: Condensed summary reduces agent context by 70-90% while preserving all necessary information

5. **Wait for agent completion**:
   - Agent will fix the issues and report back
   - Display: "✅ Agent completed fixes"

6. **Verify fixes were applied**:
   - Run `git status` to see which files were modified
   - Run `git diff` to review the changes made by the agent
   - Display summary: "Modified {count} file(s): {file_list}"

7. **Retry commit**:
   - Increment `current_attempt`
   - If `current_attempt > max_retry_attempts`:
     - Display: "❌ Auto-fix retry limit reached. Manual intervention required."
     - Display the remaining errors
     - STOP execution
   - Otherwise:
     - Display: "🔄 Retrying commit (attempt {current_attempt}/{max_retry_attempts})..."
     - Re-run the commit command with the same message
     - If commit succeeds:
       - Display: "✅ Commit successful after auto-fix!"
       - Continue to Step 4 (Push to Remote)
     - If commit fails again:
       - Repeat from step 1 (re-analyze the new failure)

### Agent Selection Logic

```
function select_agent(error_output):
    # Check for Python/Backend patterns
    if contains(error_output, [".py:", "flake8", "mypy", "pytest", "E501", "F401"]):
        return "backend-developer"

    # Check for Frontend patterns
    if contains(error_output, [".ts:", ".tsx:", ".js:", ".jsx:", "ESLint", "TypeScript"]):
        return "frontend-developer"

    # Check for DevOps patterns
    if contains(error_output, ["Dockerfile", ".github/workflows", "hadolint"]):
        return "devops-engineer"

    # Default: try backend-developer for general fixes
    return "backend-developer"
```

### Example Scenarios

**Scenario 1: Flake8 linting errors**
```
Error output:
backend/apps/users/models.py:45:80: E501 line too long (95 > 79 characters)
backend/apps/core/database.py:10:1: F401 'time' imported but unused

Analysis:
- Failure type: Python linting (flake8)
- Agent: backend-developer
- Task: Fix line length and remove unused import

Action:
1. Launch backend-developer agent with error context
2. Agent fixes both issues
3. Retry commit
4. Commit succeeds
```

**Scenario 2: MyPy type errors**
```
Error output:
backend/apps/users/serializers.py:23: error: Incompatible return type

Analysis:
- Failure type: Python type checking (mypy)
- Agent: backend-developer
- Task: Fix type annotation

Action:
1. Launch backend-developer agent with error context
2. Agent fixes type annotation
3. Retry commit
4. Commit succeeds
```

**Scenario 3: Multiple hook failures (requires retry)**
```
First attempt:
- Flake8 errors → Fixed by backend-developer → Retry
Second attempt:
- MyPy errors (revealed after flake8 fix) → Fixed by backend-developer → Retry
Third attempt:
- Commit succeeds
```

**Scenario 4: Retry limit reached**
```
After 2 retries, hooks still failing:
- Display clear error message
- Show remaining issues
- Provide manual recovery instructions
- STOP execution
```

### Error Messages and User Communication

**When auto-fix is attempted**:
```
🔍 Commit hook failed. Analyzing failure...

Hook: pre-commit
Issues found:
  • 3 flake8 linting errors
  • 2 files affected

⚙️ Launching backend-developer agent to fix issues automatically...
[Agent output...]
✅ Fixes applied

🔄 Retrying commit...
✅ Commit successful!
```

**When auto-fix fails after retries**:
```
❌ Commit failed after 2 auto-fix attempts

Remaining issues:
{error_output}

Manual intervention required. To fix:
1. Review the errors above
2. Fix the issues in the affected files
3. Run: git commit -m "your message"

Or bypass hooks (use with caution):
  git commit --no-verify -m "your message"
```

**When auto-fix is not applicable**:
```
❌ Commit failed: {error_reason}

This issue requires manual intervention:
{specific_instructions_based_on_error}
```

## Self-Verification Checklist

Before finalizing, verify:

- [ ] Commit message validated (non-empty)
- [ ] No changes check performed (avoid empty commits)
- [ ] All files staged successfully with `git add .`
- [ ] Commit created with proper message format
- [ ] Claude Code footer added to commit message
- [ ] Current branch determined correctly
- [ ] Remote tracking status checked
- [ ] Push executed (with -u flag if needed for new remote branches)
- [ ] Each step verified before proceeding to next
- [ ] All errors captured and reported clearly
- [ ] Manual recovery instructions provided for each failure type
- [ ] Partial success scenarios handled (commit without push)
- [ ] Clear status and next steps provided to user

### Hook Failure Resolution Checklist

If commit hooks fail:

- [ ] Full error output captured (stdout and stderr)
- [ ] Hook failure type identified (pre-commit, commit-msg, etc.)
- [ ] Error patterns analyzed to determine issue category (linting, type errors, tests, etc.)
- [ ] Affected files extracted from error messages
- [ ] Appropriate agent selected based on error patterns:
  - [ ] backend-developer for Python/Django issues
  - [ ] frontend-developer for JS/TS/React issues
  - [ ] devops-engineer for Docker/CI/CD issues
- [ ] Agent launched with comprehensive error context
- [ ] Agent fixes verified (git status and git diff checked)
- [ ] Commit retry attempted with same message
- [ ] Retry attempt counter tracked (max 2 attempts)
- [ ] Success message displayed if auto-fix resolves issues
- [ ] Clear error message if retry limit reached
- [ ] User notified of what was fixed and how many attempts were made
