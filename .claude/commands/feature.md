---
description: Transform a feature request into user stories
---

## Purpose

Transform a feature request into comprehensive user stories and automatically initiate implementation. This command orchestrates the entire process from feature analysis to implementation kickoff.

## Variables

- `{{{ input }}}` - The feature request describing the desired functionality for the web application

## Instructions

- Follow the workflow steps in sequential order
- Do NOT stop after creating user stories - automatically proceed to implementation
- Do NOT ask the user for confirmation between steps
- Check available agents in .claude/agents/ to understand implementation capabilities
- Plan user stories based on available agents and feature requirements

## Workflow

### Step 1: Pre-flight Checks

Before starting any feature work, verify that the environment is clean and ready:

1. **Check for active Pull Requests**:
   - Use gh pr list command to check for any open PRs in the repository
   - Parse the output to count the number of active PRs
   - If any active PRs exist: STOP execution and inform the user with message: "Cannot start new feature - there are {count} active Pull Request(s). Please merge or close existing PRs before starting a new feature."

2. **Check for active Issues**:
   - Use gh issue list command to check for any open issues in the repository
   - Parse the output to count the number of active issues
   - If any active issues exist: STOP execution and inform the user with message: "Cannot start new feature - there are {count} active issue(s). Please close existing issues before starting a new feature."

3. **Verify repository state**:
   - Run git status to verify the repository is in a clean state
   - If there are uncommitted changes: STOP execution and inform the user with message: "Cannot start new feature - repository has uncommitted changes. Please commit or stash changes before starting a new feature."

4. **Pre-flight check results**:
   - If ALL checks pass: Display "Pre-flight checks passed - ready to create feature" and CONTINUE to Step 2
   - If ANY check fails: STOP execution and display the failure message with clear instructions on how to resolve

### Step 2: Branch Setup

After pre-flight checks pass, set up the feature branch:

1. **Verify current branch**:
   - Run git branch --show-current to get the current branch name
   - If not on main branch: Run git checkout main to switch to main
   - Capture any errors during checkout

2. **Update main branch**:
   - Run git pull origin main to fetch and merge latest changes from remote
   - Verify pull success by checking the command exit code
   - If pull fails: STOP execution and inform the user with message: "Failed to update main branch. Error: {error_message}. Please resolve manually."

3. **Determine next feature ID**:
   - Read the feature-log.json file at docs/features/feature-log.json
   - Parse the JSON to extract all existing feature IDs from the features array
   - Handle both "id" and "featureID" field names (check both as the structure may vary)
   - Find the maximum feature ID currently in use
   - Calculate next feature ID as: max_id + 1
   - If feature-log.json doesn't exist or features array is empty, use 1 as the first feature ID
   - If JSON parsing fails: STOP execution and inform the user with message: "Failed to read feature-log.json. Error: {error_message}. Please verify file integrity."

4. **Generate feature branch name**:
   - Extract a description from the feature request input {{{ input }}}
   - Create a kebab-case description (lowercase, hyphens between words, max 50 chars)
   - Remove special characters and convert spaces to hyphens
   - Create branch name using format: `feature/{nextID}-{kebab-case-description}`
   - Example: For feature ID 5 and input "User Authentication System" -> `feature/5-user-authentication-system`

5. **Create feature branch**:
   - Run git checkout -b {branch_name} to create and switch to the feature branch
   - Verify branch creation by running git branch --show-current
   - If branch creation fails: STOP execution and inform the user with message: "Failed to create feature branch. Error: {error_message}. Please resolve manually."

6. **Branch setup confirmation**:
   - Display confirmation message: "Feature branch created: {branch_name} (Feature ID: {nextID})"
   - CONTINUE to Step 3

### Step 3: Launch Product Owner Agent

Use the Task tool to launch the product-owner agent with the following instructions:

First, check what agents are available in .claude/agents/ to understand what implementation capabilities exist.

Then, analyze this feature request for a web application and create comprehensive user stories:

{{{ input }}}

You MUST plan the user stories needed for this feature based on the available agents and feature requirements.

### Step 4: Extract Feature ID and Auto-Implement

After the product-owner agent completes and returns its output:

1. **Extract the feature ID**: Look in the agent's output for "Feature #XXX" or check the docs/features/ directory for the newly created feature folder
2. **Verify feature log entry**: Ensure the feature-log.json includes the new feature with `isSummarised: false`
3. **Automatically launch implementation**: Use the SlashCommand tool to execute: `/implement {feature_id}`
4. **Do not ask the user for confirmation** - automatically proceed with implementation

Note: All new features should have `isSummarised: false` by default, which allows the /summarise command to process them later.

### Step 5: Detect Implementation Completion

After the `/implement` command completes:

1. **Verify implementation completion**:
   - Read the user-stories.md file at `docs/features/{feature_id}/user-stories.md`
   - Parse the Execution Order section to count the total number of user stories
   - Read the implementation-log.json file at `docs/features/{feature_id}/implementation-log.json`
   - Count the number of stories with `status: "completed"` in the implementation log
   - Compare the counts to determine if all stories are completed

2. **Retain feature ID for git operations**:
   - Store the feature ID in a variable for use in subsequent steps
   - The feature ID will be needed for git commit messages and PR creation

3. **Verify feature log update**:
   - Read the feature-log.json file
   - Find the feature entry with matching featureID
   - Confirm that `userStoriesImplemented` has been set to a timestamp (this should have been done by /implement)

### Step 6: Stage All Feature Changes

After verifying implementation completion in Step 5:

1. **Stage all modified files**:
   - Use git add to stage all modified files in the working directory
   - Use git add to stage all untracked files generated during implementation
   - This ensures both modified files and new files are included in staging

2. **Verify staging success**:
   - Run git status to verify files were successfully staged
   - Check that "Changes to be committed" section shows all expected files

3. **Handle staging failures**:
   - CRITICAL: If git add fails, implementation-log.json MUST remain unchanged - all completed stories stay marked as completed
   - Capture the error message from git add command
   - Provide manual recovery instructions: "Git staging failed. Manually run: git add . && git commit -m 'Feature {feature_id}: {feature_title}' && git push && gh pr create"
   - CONTINUE to Step 7 (attempt commit anyway - files may already be staged from previous runs)

4. **Report staging status**:
   - Count the number of files staged
   - Include staging confirmation in the final report

### Step 7: Create Feature Commit

After staging all changes in Step 6:

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

4. **Handle commit failures**:
   - CRITICAL: If git commit fails, implementation-log.json MUST remain unchanged - all completed stories stay marked as completed
   - Capture the error message from git commit command
   - Provide manual recovery instructions based on failure type
   - If commit succeeded: CONTINUE to Step 8
   - If commit failed: SKIP Steps 8-9 and jump to Report (cannot push/PR without commit)

### Step 8: Push to Remote Branch

After creating the feature commit in Step 7 (SKIP this step if commit failed):

1. **Check remote tracking status**:
   - Run git branch -vv to check if the current branch has remote tracking configured
   - Parse the output to determine if the branch tracks a remote

2. **Push to remote repository**:
   - If branch has remote tracking: Use git push to push the commit
   - If branch has no remote tracking: Use git push -u origin {branch-name} to create remote branch and set tracking

3. **Verify push success**:
   - Check the git push command exit code to verify success
   - Capture any error output if the push fails
   - Run git status to confirm the branch is up-to-date with remote

4. **Handle push failures**:
   - CRITICAL: If git push fails, implementation-log.json MUST remain unchanged - all completed stories stay marked as completed
   - IMPORTANT: Commit already exists locally, so this is a PARTIAL SUCCESS scenario
   - Capture the error message from git push command
   - Provide manual recovery instructions: "Push failed. Commit exists locally (hash: {commit_hash}). Retry with: git push"
   - Report PARTIAL SUCCESS: "Commit created locally but push failed"
   - If push succeeded: CONTINUE to Step 9
   - If push failed: SKIP Step 9 and jump to Report (cannot create PR without remote branch)

### Step 9: Create Pull Request

After successfully pushing to the remote branch in Step 8 (SKIP this step if push failed):

1. **Extract feature summary for PR body**:
   - Read the user-stories.md file at `docs/features/{feature_id}/user-stories.md`
   - Extract the Overview section for the feature description
   - Parse the User Stories section to create a summary list of all implemented stories
   - Format the summary as a bulleted markdown list with story titles

2. **Create PR using gh CLI**:
   - Use gh pr create command with standardized title format: "Feature {feature_id}: {feature_title}"
   - Use a HEREDOC to construct the PR body with summary, user stories list, and Claude Code attribution
   - Ensure the PR targets the main branch (or repository default branch)

3. **Capture and verify PR creation**:
   - Capture the PR URL from the gh pr create output
   - Store the PR URL for inclusion in the final report

4. **Handle PR creation failures**:
   - CRITICAL: If gh pr create fails, implementation-log.json MUST remain unchanged - all completed stories stay marked as completed
   - IMPORTANT: Commit and push already succeeded, so this is a PARTIAL SUCCESS scenario
   - Capture the error message from gh pr create command
   - Provide manual recovery instructions: "PR creation failed. Create manually at GitHub or retry with: gh pr create --title 'Feature {feature_id}: {feature_title}'"
   - Report PARTIAL SUCCESS: "Commit created and pushed but PR creation failed"

## Report

Provide a comprehensive summary with the following sections:

### Pre-flight Checks
- Active PRs check status (pass/fail)
- Active issues check status (pass/fail)
- Repository state check status (pass/fail)
- Overall pre-flight status

### Branch Setup
- Previous branch (should be main)
- Main branch update status
- Next feature ID determined from feature-log.json
- Feature branch name (feature/{nextID}-{description})
- Branch creation status

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
- Key files staged
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
- Push errors with details (if any)

#### Pull Request
- PR URL (if successfully created)
- PR title
- PR creation status (success/failure)
- PR creation errors with details (if any)

### Overall Workflow Status
- If ALL steps completed successfully: Display success message
- If any git operations failed: Display partial success message with error details and manual recovery steps

### Issues Encountered
- Any other issues encountered during the process
