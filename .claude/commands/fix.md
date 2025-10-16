---
description: Process and fix bugs from bug-log.json
---

## Purpose

Process bug reports from docs/features/bug-log.json, create user stories for unfixed bugs using the product-owner agent, and automatically commit and push the changes. This command orchestrates the entire bug fix planning workflow from identifying unfixed bugs to committing the user stories to the repository.

## Instructions

You MUST follow the workflow steps in sequential order. Do NOT ask the user for confirmation between steps - automatically proceed through all steps.

## Workflow

### Step 1: Read Bug Log

Read the bug log file:
- Path: docs/features/bug-log.json
- If the file doesn't exist, create it with an empty bugs array and report to the user that no bugs exist
- Parse the JSON structure

### Step 2: Identify Unfixed Bugs

Iterate through the bugs array and identify all bugs where `isFixed` is not set to `true` (this includes `false`, `null`, or missing values).

For each unfixed bug:
- Note the bug ID
- Note the featureID
- Note the featureName (branch name)
- Note the bug title
- Note the severity

### Step 3: Check and Switch to Feature Branch

For each unfixed bug, check if we're on the correct branch:

1. **Get current branch**:
```bash
git branch --show-current
```

2. **Check if current branch matches featureName**:
   - If current branch matches the bug's featureName, proceed to git pull
   - If current branch does NOT match, switch to the feature branch:
     ```bash
     git checkout {featureName}
     ```
   - If checkout fails (branch doesn't exist), report error and skip this bug

3. **Pull latest changes**:
```bash
git pull
```

If there are any conflicts or errors during pull, stop processing this bug and report to the user.

### Step 4: Read Bug Details

For each unfixed bug, read the bug details from the markdown file:

1. **Construct the bug details path**: docs/features/{featureID}/bugs/{bugID}.md
2. **Read the file**: Use the Read tool to get the complete bug details
3. **If file doesn't exist**: Report error and skip this bug

### Step 5: Process Each Unfixed Bug

For EACH unfixed bug identified, do the following sequentially:

1. **Launch Product Owner Agent**: Use the Task tool to launch the product-owner agent with these instructions:

```
Analyze this bug report and create comprehensive user stories to fix it:

Bug ID: {bug_id}
Feature ID: {featureID}
Title: {bug_title}
Severity: {bug_severity}
Details: {content from docs/features/{featureID}/bugs/{bugID}.md}

You MUST follow the "For Bug Fixes" workflow in your instructions. Create atomic user stories that address:
1. Investigation (if needed)
2. Implementation of the fix
3. Regression tests
4. Validation

Ensure all stories follow TDD methodology and are independently deployable.
```

2. **Wait for Agent Completion**: Wait for the product-owner agent to complete and return its output

3. **Update Bug Log**: Update the bug entry in docs/features/bug-log.json:
   - Set `isFixed` to `false` (it will be set to true after implementation)
   - Set `userStoriesCreated` to current ISO timestamp
   - Set `userStoriesPath` to the path created by the product-owner agent (typically docs/features/bug-{bugID}/user-stories.md)

### Step 6: Commit Changes

After ALL bugs have been processed:

1. **Stage Changes**: Stage all modified and new files:
   - docs/features/bug-log.json
   - Any new docs/features/bug-* directories created

2. **Create Commit**: Create a commit with the message format:
```
Fix planning for bugs: {comma-separated list of bug IDs}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

Example: "Fix planning for bugs: 1, 3, 5"

### Step 7: Push to Remote

Push the commit to the remote repository:

```bash
git push
```

If there are any errors during push, report them to the user.

## Report

Provide a summary that includes:
- Number of unfixed bugs found: {count}
- List of bug IDs processed: {list}
- User stories created for each bug
- Commit created: Yes/No
- Push successful: Yes/No
- Any errors or issues encountered

If no unfixed bugs were found, report: "No unfixed bugs found in bug-log.json"

## Error Handling

- If bug-log.json doesn't exist, create it with empty structure
- If bug-log.json is malformed, report the error and stop
- If git checkout fails (branch doesn't exist), skip that bug and continue with next
- If git pull fails, skip that bug and continue with next
- If bug details file (docs/features/{featureID}/bugs/{bugID}.md) doesn't exist, skip that bug and continue with next
- If product-owner agent fails, report which bug failed and continue with next bug
- If commit fails, report the error
- If push fails, report the error but note that changes are committed locally
