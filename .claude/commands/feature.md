---
description: Transform a feature request into user stories
---

## Purpose

Transform a feature request into comprehensive user stories and automatically initiate implementation if all required agents are available. This command orchestrates the entire process from feature analysis to implementation kickoff, with built-in validation to ensure necessary agents exist before proceeding.

## Variables

- `{{{ input }}}` - The feature request describing the desired functionality for the web application

## Instructions

- You MUST follow the workflow steps in sequential order
- Check available agents in .claude/agents/ to understand implementation capabilities
- Plan user stories based on available agents and feature requirements
- If missing agents are identified by product-owner, STOP and do NOT proceed to implementation
- Only automatically proceed to implementation if NO missing agents are found
- Do NOT ask the user for confirmation between steps (unless missing agents are found)

## Workflow

### Step 1: Launch Product Owner Agent

Use the Task tool to launch the product-owner agent with the following instructions:

First, check what agents are available in .claude/agents/ to understand what implementation capabilities exist.

Then, analyze this feature request for a web application and create comprehensive user stories:

{{{ input }}}

You MUST plan the user stories needed for this feature based on the available agents and feature requirements.

### Step 2: Check for Missing Agents

After the product-owner agent completes and returns its output:

1. **Check for missing agents**: Look in the agent's output for a "Missing Agents" section
2. **If missing agents are identified**:
   - STOP and do NOT proceed with implementation
   - Report the missing agents to the user
   - Ask the user to create the necessary agents before proceeding
   - Exit the workflow here

### Step 3: Create Git Branch and Commit Planning

Only proceed with this step if NO missing agents were identified:

1. **Extract the feature ID**: Look in the agent's output for "Feature #XXX" or check the docs/features/ directory for the newly created feature folder
2. **Read feature-log.json**: Extract the feature ID and title for the new feature
3. **Create feature description slug**: Convert the title to a URL-friendly slug (lowercase, replace spaces with hyphens, remove special characters)
4. **Create git branch**: Use Bash tool to create and checkout a new branch with format: `feature/{id}-{slug}`
   - Example: If feature ID is 3 and title is "User Authentication System", branch should be `feature/3-user-authentication-system`
5. **Commit planning files**: Use the SlashCommand tool to execute:
   ```
   /commit "Planning of {id}-{feature-description}"
   ```
   where {feature-description} is the original title from feature-log.json
   - Example: `/commit "Planning of 3-User Authentication System"`

### Step 4: Auto-Implement

Only proceed with this step if NO missing agents were identified:

1. **Verify feature log entry**: Ensure the feature-log.json includes the new feature with `isSummarised: false`
2. **Automatically launch implementation**: Use the SlashCommand tool to execute: `/implement feature {feature_id}`
3. **Do not ask the user for confirmation** - automatically proceed with implementation

Note: All new features should have `isSummarised: false` by default, which allows the /summarise command to process them later.

## Report

### If Missing Agents Were Identified

Provide a summary that includes:
- Feature ID that was created
- Number of user stories generated
- List of missing agents identified
- Clear instruction that implementation has NOT been initiated
- Request for user to create missing agents before proceeding

### If No Missing Agents

Provide a summary that includes:
- Feature ID that was created
- Git branch created and current branch
- Planning commit created
- Number of user stories generated
- Confirmation that implementation has been initiated
- Any issues encountered during the process
