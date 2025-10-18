---
description: Process and fix bugs from bug-log.json [bugid] or GitHub [gha]
---

## Purpose

Process bug reports from either docs/features/bug-log.json or GitHub issues. When "gha" parameter is provided, fetch the oldest open issue from GitHub and create user stories using the product-owner agent. Otherwise, process bugs from bug-log.json as usual.

## Arguments

- `bugid` (optional): The ID of a specific bug to process from bug-log.json
- `gha` (optional): When set to "gha", fetches the oldest open issue from GitHub repository

## Instructions

You MUST follow the workflow steps in sequential order. Do NOT ask the user for confirmation between steps - automatically proceed through all steps.

## Workflow

### Step 0: Determine Mode

Check the first argument:
- If argument is "gha": Follow the GitHub Issues Workflow (Steps A1-A5)
- If argument is a number or not provided: Follow the Bug Log Workflow (Steps B1-B7)

---

## GitHub Issues Workflow (when parameter is "gha")

### Step A1: Fetch Oldest GitHub Issue

Use the Bash tool to get the oldest open issue from the GitHub repository:

```bash
gh issue list --state open --json number,title,body,createdAt,labels --limit 100 | jq 'sort_by(.createdAt) | .[0]'
```

This command:
- Lists all open issues
- Sorts by creation date (oldest first)
- Returns the first (oldest) issue

If no issues are found, report to the user and stop.

Parse the JSON output to extract:
- Issue number
- Issue title
- Issue body
- Labels (if any)
- Creation date

### Step A2: Parse Issue Template Data

The issue body follows the bug-log-template structure from docs/templates/bug-log-template.md.

Parse the issue body to extract:
- title (from the table)
- featureID (from the table)
- featureName (from the table)
- jobName (from the table)
- stepName (from the table)
- PRURL (from the table)
- commitURL (from the table)
- runURL (from the table)
- Failed Step Log Excerpt (from the section below the table)

If any required fields (title, featureID, featureName) are missing, report error and stop.

### Step A3: Launch Product Owner Agent

Use the Task tool to launch the product-owner agent with these instructions:

```
Analyze this GitHub Actions CI/CD failure and create comprehensive user stories to fix it:

Feature ID: {featureID}
Feature Name: {featureName}
GitHub Issue: #{issue_number}
Title: {title}

## CI/CD Context
- Job Name: {jobName}
- Step Name: {stepName}
- PR URL: {PRURL}
- Commit URL: {commitURL}
- Run URL: {runURL}

## Failed Step Log
{Failed Step Log Excerpt}

You MUST follow the "For Bug Fixes" workflow in your instructions. Create atomic user stories that address:
1. Investigation of the CI/CD failure
2. Root cause analysis
3. Implementation of the fix
4. Regression tests to prevent similar failures
5. Validation that the fix resolves the issue

Ensure all stories follow TDD methodology and are independently deployable.

Write the user stories to: docs/features/{featureID}/bugs/github-issue-{issue_number}/user-stories.md
```

Wait for the agent to complete and return its output.

### Step A4: Report

Provide a summary that includes:
- GitHub issue number and title
- Feature ID associated
- User stories path created
- Any errors or issues encountered

---

## Bug Log Workflow (when parameter is bugid or not provided)

### Step B1: Pull Latest Changes (Conditional)

**If bugid argument is provided**:
- Skip this step entirely
- Assume the current branch has the latest changes
- Proceed directly to Step B2

**If bugid argument is NOT provided**:
Pull the latest changes from the current branch:

```bash
git pull
```

If there are any conflicts or errors during pull, report to the user and stop.

### Step B2: Read Bug Log

Read the bug log file:
- Path: docs/features/bug-log.json
- If the file doesn't exist, create it with an empty bugs array
- Parse the JSON structure

### Step B3: Identify Unfixed Bugs

**If bugid argument is provided**:
- Find the specific bug with matching ID
- If the bug doesn't exist, report error and stop
- If the bug's isFixed is already true, report that the bug is already fixed and stop
- Proceed with only this bug

**If bugid argument is NOT provided**:
- Identify all bugs where isFixed is not set to true

For each unfixed bug, note:
- Bug ID
- featureID
- featureName (branch name)
- Bug title
- Severity

### Step B4: Check and Switch to Feature Branch (Conditional)

**If bugid argument is provided**:
- Skip this step entirely
- Assume we're already on the correct branch

**If bugid argument is NOT provided**:
For each unfixed bug, check if we're on the correct branch and switch if needed.

### Step B5: Read Bug Details

For each unfixed bug, read from: docs/features/{featureID}/bugs/{bugID}.md

### Step B6: Process Each Unfixed Bug

For EACH unfixed bug:

1. Launch Product Owner Agent with bug details
2. Wait for completion
3. Update bug entry in bug-log.json
4. Implement user stories using: `/implement bug {bugID}`

### Step B7: Commit and Push Changes

After ALL bugs processed:

```
/commit "Fix planning for bugs: {comma-separated list of bug IDs}" push
```

---

## Error Handling

- If gh command fails, ensure GitHub CLI is installed and authenticated
- If bug-log.json doesn't exist, create it with empty structure
- If feature ID cannot be determined from GitHub issue, ask user
- If product-owner agent fails, report which bug/issue failed
- If commit/push fails, report the error
