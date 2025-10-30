---
description: Transform a feature request into user stories
---

## Purpose

Transform a feature request into comprehensive user stories and automatically initiate implementation. This command orchestrates the entire process from feature analysis to implementation kickoff.

## Variables

- `{{{ input }}}` - The feature request describing the desired functionality for the web application

## Instructions

- FIRST: Clear the conversation context using /clear to ensure optimal token efficiency and clean starting state
- Follow the workflow steps in sequential order
- Do NOT stop after creating user stories - automatically proceed to implementation
- Do NOT ask the user for confirmation between steps
- Check available agents in .claude/agents/ to understand implementation capabilities
- Plan user stories based on available agents and feature requirements

## Context Management

This command automatically clears conversation context at the start because:
- The /feature workflow is fully autonomous and doesn't require prior conversation context
- Token efficiency is critical for this long-running workflow (creates branch, stories, implements features, commits)
- Clean context ensures predictable, consistent behavior across all feature executions
- Users who need to preserve context can manually run workflow steps instead of using /feature

## Workflow

### Step 0: Clear Conversation Context

**CRITICAL FIRST STEP**: Before any other operations, clear the conversation context to ensure optimal token efficiency.

1. **Execute /clear command**:
   - Run the /clear command to clear all previous conversation context
   - This ensures the feature workflow starts with minimal token usage
   - The /clear command is a built-in Claude Code command that resets conversation history

2. **Verify context cleared**:
   - After /clear executes, the conversation should have minimal context
   - Proceed immediately to Step 1

**Note**: If /clear is not available or fails, continue with the workflow but note increased token usage.

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

3. **Determine next feature ID and cache feature log data**:
   - Read the feature-log.json file at docs/features/feature-log.json
   - **IMPORTANT**: Store the entire parsed JSON in a variable for reuse in Steps 5 and 6
   - Parse the JSON to extract all existing feature IDs from the features array
   - Handle both "id" and "featureID" field names (check both as the structure may vary)
   - Find the maximum feature ID currently in use
   - Calculate next feature ID as: max_id + 1
   - If feature-log.json doesn't exist or features array is empty, use 1 as the first feature ID
   - If JSON parsing fails: STOP execution and inform the user with message: "Failed to read feature-log.json. Error: {error_message}. Please verify file integrity."
   - **Token Optimization**: By caching this data, you avoid re-reading the file in Steps 5 and 6

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
   - Re-read the feature-log.json file (it was updated by /implement in Step 4)
   - Find the feature entry with matching featureID
   - Confirm that `userStoriesImplemented` has been set to a timestamp (this should have been done by /implement)
   - **Cache this updated data** for use in Step 6 (avoids third read)

### Step 6: Cache Feature Metadata for Hooks

After verifying implementation completion in Step 5:

1. **Extract and cache feature metadata**:
   - Use the cached feature-log data from Step 5.3 (do NOT re-read the file)
   - Find the feature entry with matching featureID in the cached data
   - Extract the feature title for use in commit message and hooks
   - Store these values for use in the Report and Hook System:
     - `FeatureID`: The numeric feature ID
     - `FeatureBranch`: The current branch name (from git)
     - `IntendedCommitMessage`: "Feature {feature_id}: {feature_title}"
   - **Token Optimization**: Using cached data saves ~400 lines of JSON parsing
   - **Note**: Git operations (commit, push, PR) are now handled by the hook system in Step 8

2. **Prepare for hook execution**:
   - Verify all three variables are available and non-empty
   - These variables will be used by:
     - The Report section to display command outputs
     - The Hook System to execute the /push command automatically
   - Continue to Report section

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

### Overall Workflow Status
- If ALL steps completed successfully: Display success message with note that hooks will execute next
- If any steps failed: Display failure message with error details and manual recovery steps

### Command Output Variables
Display these variables in a clearly formatted section for use by hooks or other automation:

```
FeatureID: {feature_id}
FeatureBranch: {branch_name}
IntendedCommitMessage: Feature {feature_id}: {feature_title}
```

These variables are available for:
- Hook automation (configured in .claude/hooks.json)
- Manual reference for subsequent commands
- Integration with external tools

### Issues Encountered
- Any other issues encountered during the process

## Post-Execution Hook System

After completing the initial workflow report and only if implementation was successful (Steps 1-5 completed):

### Step 7: Check and Execute Hooks

1. **Read hook configuration**:
   - Read the hooks configuration file at `/home/ed/Dev/architecture/.claude/hooks.json`
   - If file doesn't exist or cannot be read: Skip hook execution (not an error, hooks are optional)
   - Parse the JSON to extract hook configuration

2. **Check if hooks are enabled globally**:
   - Check `configuration.disableAllHooks` in the hooks config
   - If `true`: Skip all hook execution
   - If `false`: Continue to feature-specific hooks

3. **Check feature command hooks**:
   - Navigate to `hooks.feature` in the configuration
   - Check if `hooks.feature.enabled` is `true`
   - If `false`: Skip feature hooks execution
   - If `true`: Continue to process onComplete hooks

4. **Process onComplete hooks**:
   - Iterate through `hooks.feature.onComplete` array
   - For each hook entry:
     - Check if the hook's `enabled` field is `true`
     - If `false`: Skip this hook
     - If `true`: Continue processing this hook

5. **Validate hook conditions**:
   - Check if hook has a `condition` object
   - If `condition.requireAllVariables` exists:
     - Verify all required variables are available (FeatureID, FeatureBranch, IntendedCommitMessage)
     - If any variable is missing: Skip this hook and log warning
     - If all variables present: Continue to execute hook

6. **Prepare hook command**:
   - Extract `command` field (e.g., "/push")
   - Extract `arguments` object
   - Replace variable placeholders with actual values:
     - Replace `{{FeatureID}}` with the actual feature ID
     - Replace `{{FeatureBranch}}` with the actual branch name
     - Replace `{{IntendedCommitMessage}}` with "Feature {feature_id}: {feature_title}"
   - Construct the final command string with replaced arguments

7. **Execute hook command**:
   - If `configuration.verbose` is `true`:
     - Display: "Executing hook: {command} with arguments: {replaced_arguments}"
     - Display hook description if available
   - Use SlashCommand tool to execute the hook command
   - Example: `SlashCommand("/push", "Feature 5: User Authentication System")`

8. **Handle hook execution results**:
   - If hook executes successfully: Display success message
   - If hook fails:
     - Check `configuration.failOnHookError`:
       - If `true`: Display error and note that hook failed (workflow already completed successfully)
       - If `false`: Display warning but continue (hook failures don't affect main workflow status)
   - Display completion message for all hooks processed

9. **Hook execution summary**:
   - Display: "Hook execution complete. Executed {count} hook(s)."
   - If no hooks were executed: Display: "No hooks configured or enabled for this command."

**Important Notes**:
- Hooks execute after implementation completes but before PR creation
- Hook failures do not affect the success status of the main /feature workflow
- Hooks are optional - missing hook configuration file is not an error
- Hook execution is logged for debugging and transparency
- Users can disable hooks globally, per-command, or per-hook
- If hooks fail, PR creation in Step 8 will be skipped

### Step 8: Create Pull Request

After hook execution completes (or if hooks were skipped), and only if the /push hook succeeded:

1. **Verify push was successful**:
   - Check that the /push command (executed by hook in Step 7) completed successfully
   - Verify the feature branch exists on the remote repository
   - If push failed or was skipped: SKIP PR creation and note in final report

2. **Extract feature summary for PR body**:
   - Read the user-stories.md file at `docs/features/{feature_id}/user-stories.md`
   - Extract the Overview section for the feature description
   - Parse the User Stories section to create a summary list of all implemented stories
   - Format the summary as a bulleted markdown list with story titles

3. **Create PR using gh CLI**:
   - Use gh pr create command with standardized title format: "Feature {feature_id}: {feature_title}"
   - Use a HEREDOC to construct the PR body with summary, user stories list, and Claude Code attribution
   - Ensure the PR targets the main branch (or repository default branch)

4. **Capture and verify PR creation**:
   - Capture the PR URL from the gh pr create output
   - Store the PR URL for inclusion in the final report

5. **Handle PR creation failures**:
   - CRITICAL: If gh pr create fails, implementation-log.json MUST remain unchanged - all completed stories stay marked as completed
   - IMPORTANT: Commit and push already succeeded (via hook), so this is a PARTIAL SUCCESS scenario
   - Capture the error message from gh pr create command
   - Provide manual recovery instructions: "PR creation failed. Create manually at GitHub or retry with: gh pr create --title 'Feature {feature_id}: {feature_title}'"
   - Report PARTIAL SUCCESS: "Commit created and pushed but PR creation failed"

6. **PR creation summary**:
   - If successful: Display PR URL and success message
   - If failed: Display error and manual recovery steps
   - Continue to Final Report

## Final Report

After all steps complete (including hooks and PR creation), provide a final comprehensive summary:

### Hook Execution Results
- Hooks enabled: (yes/no)
- Hooks executed: {count}
- /push hook status: (success/failure/skipped)
- Commit hash (if /push succeeded): {hash}
- Push status (if /push succeeded): (success/failure)

### Pull Request Results
- PR creation status: (success/failure/skipped)
- PR URL (if successful): {url}
- PR title (if successful): "Feature {feature_id}: {feature_title}"
- Error details (if failed): {error_message}

### Complete Workflow Summary
- Overall status: (fully successful/partial success/failed)
- If fully successful: "Feature {feature_id} created, implemented, committed, pushed, and PR created successfully!"
- If partial success: Explain what succeeded and what failed, with recovery steps
- If failed: Explain what failed and provide detailed recovery instructions
