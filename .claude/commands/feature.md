---
description: Transform a feature request into user stories
---

## Purpose

Transform a feature request into comprehensive user stories and automatically initiate implementation. This command orchestrates the entire process from feature analysis to implementation kickoff.

## Variables

- `{{{ input }}}` - The feature request describing the desired functionality for the web application

## Instructions

- You MUST follow the workflow steps in sequential order
- Do NOT stop after creating user stories - automatically proceed to implementation
- Do NOT ask the user for confirmation between steps
- Check available agents in .claude/agents/ to understand implementation capabilities
- Plan user stories based on available agents and feature requirements

## Workflow

### Step 1: Launch Product Owner Agent

Use the Task tool to launch the product-owner agent with the following instructions:

First, check what agents are available in .claude/agents/ to understand what implementation capabilities exist.

Then, analyze this feature request for a web application and create comprehensive user stories:

{{{ input }}}

You MUST plan the user stories needed for this feature based on the available agents and feature requirements.

### Step 2: Extract Feature ID and Auto-Implement

After the product-owner agent completes and returns its output:

1. **Extract the feature ID**: Look in the agent's output for "Feature #XXX" or check the docs/features/ directory for the newly created feature folder
2. **Verify feature log entry**: Ensure the feature-log.json includes the new feature with `isSummarised: false`
3. **Automatically launch implementation**: Use the SlashCommand tool to execute: `/implement {feature_id}`
4. **Do not ask the user for confirmation** - automatically proceed with implementation

Note: All new features should have `isSummarised: false` by default, which allows the /summarise command to process them later.

### Step 3: Detect Implementation Completion

After the `/implement` command completes:

1. **Verify implementation completion**:
   - Read the user-stories.md file at `docs/features/{feature_id}/user-stories.md`
   - Parse the Execution Order section to count the total number of user stories
   - Read the implementation-log.json file at `docs/features/{feature_id}/implementation-log.json`
   - Count the number of stories with `status: "completed"` in the implementation log
   - Compare the counts to determine if all stories are completed

2. **Retain feature ID for git operations**:
   - Store the feature ID in a variable for use in subsequent steps
   - The feature ID will be needed for git commit messages and PR creation in future enhancements

3. **Verify feature log update**:
   - Read the feature-log.json file
   - Find the feature entry with matching featureID
   - Confirm that `userStoriesImplemented` has been set to a timestamp (this should have been done by /implement)

Note: This step sets the foundation for automatic git workflow operations (commit, push, PR creation) that will be added in subsequent user stories.

### Step 4: Stage All Feature Changes

After verifying implementation completion in Step 3:

1. **Stage all modified files**:
   - Use git add to stage all modified files in the working directory
   - Use git add to stage all untracked files generated during implementation
   - This ensures both modified files and new files are included in staging

2. **Verify staging success**:
   - Run git status to verify files were successfully staged
   - Check that "Changes to be committed" section shows all expected files
   - Confirm no errors occurred during the staging process

3. **Handle staging failures** (Error Handling - Story #7):
   - CRITICAL: If git add fails, implementation-log.json MUST remain unchanged - all completed stories stay marked as completed
   - Capture the error message from git add command (stderr output)
   - Log the staging failure details for reporting
   - Provide clear manual recovery instructions in the report:
     - "Git staging failed with error: {error_message}"
     - "To manually complete the workflow, run these commands:"
     - "  git add ."
     - "  git commit -m 'Feature {feature_id}: {feature_title}'"
     - "  git push"
     - "  gh pr create --title 'Feature {feature_id}: {feature_title}' --body-file {path_to_pr_body}"
   - CONTINUE to Step 5 (attempt commit anyway - files may already be staged from previous runs)
   - Mark staging as FAILED in workflow status tracking

4. **Report staging status**:
   - Count the number of files staged (or 0 if staging failed)
   - List the key files that were staged (feature directory, modified command files, etc.)
   - If staging failed, include the error message and manual recovery steps in the report
   - Include staging confirmation in the final report

Note: This step prepares all changes for the commit operation. Error handling ensures user stories remain marked as completed even if git operations fail (Story #7 requirement).

### Step 5: Create Feature Commit

After staging all changes in Step 4:

1. **Read feature title**:
   - Read the feature-log.json file
   - Find the feature entry with matching featureID
   - Extract the feature title for use in the commit message

2. **Create commit with standardized message**:
   - Use git commit to create a commit with the message format: "Feature {feature_id}: {feature_title}"
   - Use a HEREDOC to ensure proper formatting of multi-line commit messages
   - Include the Claude Code attribution footer in the commit message

3. **Capture and verify commit**:
   - Capture the commit hash from the git commit output
   - Run git log -1 to verify the commit was created successfully
   - Store the commit hash for reporting
   - Confirm the commit message follows the correct format

4. **Handle commit failures** (Error Handling - Story #7):
   - CRITICAL: If git commit fails, implementation-log.json MUST remain unchanged - all completed stories stay marked as completed
   - Common failure scenarios:
     - No changes to commit (working directory clean) - this is acceptable, report as "no changes needed"
     - Commit hook failures (pre-commit checks failed) - capture hook error output
     - Git configuration issues (user.name/user.email not set) - provide configuration guidance
   - Capture the error message from git commit command (stderr output)
   - Log the commit failure details for reporting
   - Provide clear manual recovery instructions based on failure type:
     - For "nothing to commit" errors: "No changes to commit - feature files may already be committed"
     - For hook failures: "Commit hooks failed with: {error_message}. Fix the issues and run: git commit -m 'Feature {feature_id}: {feature_title}'"
     - For config errors: "Git config error: {error_message}. Set up git with: git config user.name 'Your Name' && git config user.email 'your@email.com'"
   - If commit succeeded but verification fails, treat as SUCCESS (commit hash captured is sufficient)
   - CONTINUE to Step 6 if commit succeeded (even if no new commit was created because nothing changed)
   - SKIP Steps 6-7 and jump to Report if commit failed (cannot push/PR without commit)
   - Mark commit as FAILED in workflow status tracking

Note: This step creates a permanent record of the feature implementation. Error handling ensures graceful degradation - implementation log stays intact, and clear recovery guidance is provided (Story #7 requirement).

### Step 6: Push to Remote Branch

After creating the feature commit in Step 5 (SKIP this step if commit failed):

1. **Check remote tracking status**:
   - Run git branch -vv to check if the current branch has remote tracking configured
   - Parse the output to determine if the branch tracks a remote (e.g., [origin/branch-name])
   - This determines whether to use git push or git push -u

2. **Push to remote repository**:
   - If branch has remote tracking: Use git push to push the commit
   - If branch has no remote tracking: Use git push -u origin {branch-name} to create remote branch and set tracking
   - The -u flag (--set-upstream) creates the remote branch and establishes tracking relationship

3. **Verify push success**:
   - Check the git push command exit code to verify success
   - Capture any error output if the push fails
   - Run git status to confirm the branch is up-to-date with remote
   - Report push success or failure with detailed error information

4. **Handle push failures** (Error Handling - Story #7):
   - CRITICAL: If git push fails, implementation-log.json MUST remain unchanged - all completed stories stay marked as completed
   - IMPORTANT: Commit already exists locally, so this is a PARTIAL SUCCESS scenario
   - Common failure scenarios:
     - Network connectivity issues - temporary failure, retry usually works
     - Authentication failures (SSH key, token expired) - need credential refresh
     - Remote branch conflicts (forced update on remote) - need pull and merge
     - Protected branch rules (no direct push to main/master) - need feature branch
     - Large file rejections (file size limits) - need Git LFS or file cleanup
   - Capture the error message from git push command (stderr output)
   - Log the push failure details for reporting
   - Provide clear manual recovery instructions based on failure type:
     - For network errors: "Push failed due to network error: {error_message}. Retry with: git push"
     - For auth errors: "Push failed due to authentication: {error_message}. Check credentials and retry: git push"
     - For conflict errors: "Push failed due to conflicts: {error_message}. Pull changes first: git pull --rebase && git push"
     - For protected branch: "Cannot push to protected branch. Create PR manually from current branch"
     - For large files: "Push rejected due to large files: {error_message}. Use Git LFS or reduce file size"
   - Report PARTIAL SUCCESS: "Commit created locally (hash: {commit_hash}) but push failed"
   - CONTINUE to Step 7 if push succeeded (PR can only be created if remote branch exists)
   - SKIP Step 7 and jump to Report if push failed (cannot create PR without remote branch)
   - Mark push as FAILED in workflow status tracking
   - Include commit hash in report so user knows the work is saved locally

Note: This step ensures the feature commit is backed up to the remote repository. Error handling provides graceful degradation for partial success scenarios where commit succeeded but push failed (Story #7 requirement).

### Step 7: Create Pull Request

After successfully pushing to the remote branch in Step 6 (SKIP this step if push failed):

1. **Extract feature summary for PR body**:
   - Read the user-stories.md file at `docs/features/{feature_id}/user-stories.md`
   - Extract the Overview section (lines 3-5 typically) for the feature description
   - Parse the User Stories section to create a summary list of all implemented stories
   - Format the summary as a bulleted markdown list with story titles

2. **Create PR using gh CLI**:
   - Use gh pr create command with standardized title format: "Feature {feature_id}: {feature_title}"
   - Use a HEREDOC to construct the PR body with the following format:
     - Summary section with feature overview
     - User Stories section with bulleted list of implemented stories
     - Claude Code attribution footer
   - Ensure the PR targets the main branch (or repository default branch)

3. **Capture and verify PR creation**:
   - Capture the PR URL from the gh pr create output
   - Store the PR URL for inclusion in the final report
   - If gh CLI is not configured or PR creation fails, capture the error and report it
   - Provide clear guidance on manual PR creation if automated creation fails

4. **Handle PR creation failures** (Error Handling - Story #7):
   - CRITICAL: If gh pr create fails, implementation-log.json MUST remain unchanged - all completed stories stay marked as completed
   - IMPORTANT: Commit and push already succeeded, so this is a PARTIAL SUCCESS scenario
   - Common failure scenarios:
     - gh CLI not installed - need to install GitHub CLI
     - gh CLI not authenticated - need to run gh auth login
     - Insufficient permissions (no repo access) - need proper GitHub token scopes
     - PR already exists for branch - duplicate PR attempt
     - Base branch doesn't exist - invalid target branch
     - Network connectivity issues - temporary failure
   - Capture the error message from gh pr create command (stderr output)
   - Log the PR creation failure details for reporting
   - Provide clear manual recovery instructions based on failure type:
     - For gh not found: "GitHub CLI not installed. Install from https://cli.github.com/ and run: gh pr create --title 'Feature {feature_id}: {feature_title}'"
     - For auth errors: "GitHub CLI not authenticated: {error_message}. Run: gh auth login, then: gh pr create --title 'Feature {feature_id}: {feature_title}'"
     - For permission errors: "Insufficient GitHub permissions: {error_message}. Check token scopes and retry: gh pr create --title 'Feature {feature_id}: {feature_title}'"
     - For duplicate PR: "PR already exists for this branch: {error_message}. View existing PR or close it before creating new one"
     - For network errors: "PR creation failed due to network: {error_message}. Retry with: gh pr create --title 'Feature {feature_id}: {feature_title}'"
     - For any error, also provide GitHub web UI option: "Alternatively, create PR manually at: https://github.com/{owner}/{repo}/compare/{branch}"
   - Report PARTIAL SUCCESS: "Commit created and pushed (hash: {commit_hash}) but PR creation failed"
   - Mark PR creation as FAILED in workflow status tracking
   - Include commit hash and branch name in report so user can create PR manually

Note: This step completes the automated git workflow. Error handling provides graceful degradation for partial success scenarios where commit and push succeeded but PR creation failed (Story #7 requirement).

## Report

Provide a comprehensive summary with the following sections:

### Feature Creation
- Feature ID that was created
- Number of user stories generated
- Feature title

### Implementation Status
- Confirmation that implementation has been initiated
- Implementation completion status (all stories completed vs. partial completion)
- Total stories completed vs. total stories
- Feature log update confirmation

### Git Workflow Status

#### Staging
- Number of files staged
- Key files staged (feature directory, modified command files, etc.)
- Staging errors (if any)

#### Commit
- Commit hash
- Commit message
- Branch name
- Commit errors (if any)

#### Push
- Push status (success/failure)
- Branch name
- Remote tracking status
- Push errors with details (if any occurred - include error message, suggested resolution)

#### Pull Request
- PR URL (if successfully created)
- PR title
- PR creation status (success/failure)
- PR creation errors with details (if any occurred - include error message, suggested resolution)

### Overall Workflow Status
- If ALL steps completed successfully (stories implemented, committed, pushed, PR created):
  - Display success message: "All workflow steps completed successfully: user stories implemented, changes committed, pushed to remote, and pull request created."
- If any git operations failed:
  - Display partial success message indicating which steps succeeded and which failed
  - List all error details with suggested manual steps to complete the workflow

### Issues Encountered
- Any other issues encountered during the process (non-git related)
