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

3. **Report staging status**:
   - Count the number of files staged
   - List the key files that were staged (feature directory, modified command files, etc.)
   - Include staging confirmation in the final report

Note: This step prepares all changes for the commit operation that will be added in Story #3.

## Report

Provide a summary that includes:
- Feature ID that was created
- Number of user stories generated
- Confirmation that implementation has been initiated
- Implementation completion status (all stories completed vs. partial completion)
- Total stories completed vs. total stories
- Feature log update confirmation
- Git staging status (number of files staged, key files staged)
- Any issues encountered during the process
