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

## Error Handling

This command uses comprehensive error handling with specific error codes and recovery suggestions.

**Error Handling Reference**: See `.claude/helpers/command-error-handling.md` for complete error code documentation and `.claude/helpers/error-code-mapping.md` for validation error mapping.

**Common Errors**:
- ENV-001: Git repository not found → Initialize git or navigate to repository
- FS-002: Agents directory not found → Create .claude/agents/ directory
- FS-005: Invalid JSON in feature-log → Fix JSON syntax errors
- DEP-006: No agents available → Create agent definitions (warning)
- GIT-007: Uncommitted changes → Commit or stash changes (warning)
- STATE-001: Feature already exists → Use existing feature (warning)

**Error Handling Strategy**:
- All validation errors (Step 0) use standardized error codes
- Missing agents directory is BLOCKING - cannot plan without agents
- No agent files is WARNING - user can proceed but should create agents
- Uncommitted changes is WARNING - user can proceed but should commit first
- Feature creation errors stop execution to prevent duplicates

## Workflow

### Step 0: Pre-Flight Validation

Before executing any operations, run comprehensive validation checks to ensure prerequisites are met.

#### Step 0.1: Load Error Handling and Validation Systems

Read error handling system from .claude/helpers/command-error-handling.md to understand error codes, categories, and message formats.

Read error code mapping from .claude/helpers/error-code-mapping.md to map validation errors to error codes.

Read validation helper from .claude/helpers/pre-flight-validation.md to understand validation requirements and error message formats.

All validation errors in subsequent steps should include appropriate error codes from the error code mapping.

#### Step 0.2: Validate Git Repository Exists

Run the following check to verify this is a git repository:
```bash
test -d ".git" && echo "VALID" || echo "INVALID"
```

If output is "INVALID":
- Display error message:
```
Error: Not a git repository

Check: Git repository existence
Status: No .git/ directory found in current working directory
Command: /feature

Remediation:
1. Navigate to your git repository directory
2. If this is a new project, initialize git:
   git init
3. Verify you are in the correct directory:
   pwd
```
- STOP execution immediately

#### Step 0.3: Validate Agents Directory Exists

Check if .claude/agents/ directory exists:
```bash
test -d ".claude/agents" && echo "VALID" || echo "INVALID"
```

If output is "INVALID":
- Display error message:
```
Error: Agents directory not found

Check: .claude/agents/ directory existence
Status: Directory does not exist
Command: /feature

Remediation:
1. Ensure you are in the correct project directory
2. Verify the architecture system is properly set up
3. Check that .claude/agents/ directory exists with agent definitions
4. Expected structure:
   .claude/
   └── agents/
       ├── product-owner.md
       ├── backend-developer.md
       ├── frontend-developer.md
       └── ...
```
- STOP execution immediately

#### Step 0.4: Check for Available Agents (Warning)

Check if agents directory has any agent files:
```bash
ls -1 .claude/agents/*.md 2>/dev/null | wc -l
```

If count is 0:
- Display warning message:
```
Warning: No agent definitions found

Status: .claude/agents/ directory exists but contains no agent files
Impact: Product owner will identify missing agents but cannot auto-implement

Recommendation:
1. Create agent definition files in .claude/agents/
2. Review docs/templates/ for agent templates
3. Common agents needed:
   - backend-developer.md
   - frontend-developer.md
   - devops-engineer.md
   - ui-ux-designer.md

You may continue, but implementation will require creating agents first.
```
- This is a WARNING - allow execution to continue

#### Step 0.5: Validate or Create Feature Log

Check if docs/features/ directory exists:
```bash
test -d "docs/features" && echo "VALID" || echo "INVALID"
```

If "INVALID":
- Create the directory:
```bash
mkdir -p docs/features
```

Check if docs/features/feature-log.json exists:
```bash
test -f "docs/features/feature-log.json" && echo "VALID" || echo "INVALID"
```

If "INVALID":
- Create initial feature-log.json:
```json
{
  "features": []
}
```

If feature-log.json exists, validate JSON syntax:
```bash
python3 -c "import json; json.load(open('docs/features/feature-log.json'))" 2>&1
```

If JSON validation fails:
- Display error message:
```
Error: Feature log contains invalid JSON

File: docs/features/feature-log.json
Purpose: Tracks all features and their implementation status
Command: /feature

Remediation:
1. Open docs/features/feature-log.json in a text editor
2. Fix the JSON syntax error
3. Validate JSON using: python3 -m json.tool docs/features/feature-log.json
4. Ensure the file follows this schema:
   {
     "features": [
       {
         "featureID": "1",
         "title": "Feature Title",
         "createdAt": "2025-10-19T00:00:00Z",
         "userStoriesCreated": "2025-10-19T00:00:00Z",
         "userStoriesImplemented": null,
         "isSummarised": false,
         "summarisedAt": null,
         "actions": []
       }
     ]
   }
```
- STOP execution immediately

#### Step 0.6: Check Working Directory Status (Warning)

Run git status to check for uncommitted changes:
```bash
git status --porcelain
```

If output is not empty (changes exist):
- Display warning message:
```
Warning: Working directory is not clean

Status: Uncommitted changes detected in working directory
Impact: Feature planning will create new files and git branch

Recommendation:
1. Commit current changes before planning new feature:
   git add .
   git commit -m "Your commit message"
2. Or stash changes:
   git stash
3. Or continue at your own risk (changes may conflict)

You may continue, but committing current work first is recommended.
```
- This is a WARNING - allow execution to continue

#### Step 0.7: Validation Summary

If all validations pass:
- Output: "Pre-flight validation passed - proceeding with feature planning"
- Proceed to Step 1

If any critical validation failed:
- Execution has already been stopped
- User must remediate issues and re-run command

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
6. **Update feature state to "planned"**: After successful commit:
   - Read the current feature-log.json file
   - Find the feature entry with the newly created featureID
   - Add or update the following fields:
     - `state`: "planned"
     - `stateHistory`: Initialize as array if doesn't exist, then append:
       ```json
       {
         "state": "planned",
         "timestamp": "{current ISO 8601 timestamp}",
         "triggeredBy": "/feature command completed",
         "notes": "Feature planning completed - user stories created"
       }
       ```
   - Write the updated feature-log.json file back
   - This automatic state transition marks the feature as planned and ready for implementation

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
