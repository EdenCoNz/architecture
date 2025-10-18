---
description: Process and fix bugs from bug-log.json [bugid]
---

## Purpose

Process bug reports from docs/features/bug-log.json, create user stories for unfixed bugs using the product-owner agent, and automatically commit and push the changes. This command orchestrates the entire bug fix planning workflow from identifying unfixed bugs to committing the user stories to the repository.

## Arguments

- `bugid` (optional): The ID of a specific bug to process. If provided, only that bug will be processed and git pull will be skipped (assuming you already have the latest changes).

## Instructions

You MUST follow the workflow steps in sequential order. Do NOT ask the user for confirmation between steps - automatically proceed through all steps.

## Workflow

### Step 1: Pull Latest Changes (Conditional)

**If bugid argument is provided**:
- Skip this step entirely
- Assume the current branch has the latest changes
- Proceed directly to Step 2

**If bugid argument is NOT provided**:
Pull the latest changes from the current branch to ensure we have the most up-to-date bug-log.json:

```bash
git pull
```

If there are any conflicts or errors during pull, report to the user and stop.

### Step 2: Read Bug Log

Read the bug log file:
- Path: docs/features/bug-log.json
- If the file doesn't exist, create it with an empty bugs array and report to the user that no bugs exist
- Parse the JSON structure

### Step 3: Identify Unfixed Bugs

**If bugid argument is provided**:
- Find the specific bug with matching ID in the bugs array
- If the bug doesn't exist, report error and stop
- If the bug's `isFixed` is already `true`, report that the bug is already fixed and stop
- Proceed with only this bug

**If bugid argument is NOT provided**:
- Iterate through the bugs array and identify all bugs where `isFixed` is not set to `true` (this includes `false`, `null`, or missing values)

For each unfixed bug:
- Note the bug ID
- Note the featureID
- Note the featureName (branch name)
- Note the bug title
- Note the severity

### Step 4: Check and Switch to Feature Branch (Conditional)

**If bugid argument is provided**:
- Skip this step entirely
- Assume we're already on the correct branch
- Proceed directly to Step 5

**If bugid argument is NOT provided**:
For each unfixed bug, check if we're on the correct branch:

1. **Get current branch**:
```bash
git branch --show-current
```

2. **Check if current branch matches featureName**:
   - If current branch matches the bug's featureName, continue to next bug
   - If current branch does NOT match, switch to the feature branch:
     ```bash
     git checkout {featureName}
     ```
   - If checkout fails (branch doesn't exist), report error and skip this bug

3. **Pull latest changes after switching**:
```bash
git pull
```

If there are any conflicts or errors during pull, stop processing this bug and report to the user.

### Step 5: Read Bug Details

For each unfixed bug, read the bug details from the markdown file:

1. **Construct the bug details path**: docs/features/{featureID}/bugs/{bugID}.md
2. **Read the file**: Use the Read tool to get the complete bug details
3. **If file doesn't exist**: Report error and skip this bug

### Step 6: Process Each Unfixed Bug

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
   - Set `userStoriesPath` to the path created by the product-owner agent (typically docs/features/{featureID}/bugs/{bugID}/user-stories.md)

4. **Implement User Stories**: After user stories are created for the bug, automatically call the implement command:
   ```
   /implement bug {bugID}
   ```

   This will:
   - Implement the user stories created for this bug
   - Run tests and builds as specified in the implement workflow
   - Commit and push the implementation changes

   Wait for the implement command to complete before proceeding to the next bug.

### Step 7: Commit and Push Changes

After ALL bugs have been processed, use the SlashCommand tool to execute:

```
/commit "Fix planning for bugs: {comma-separated list of bug IDs}" push
```

Example: `/commit "Fix planning for bugs: 1, 3, 5" push`

If there are any errors during commit or push, report them to the user.

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
