---
description: Process and fix bugs from GitHub issues
---

## Purpose

Fetch the oldest open issue from GitHub and create user stories using the product-owner agent to address CI/CD failures.

## Arguments

- `gha`: Required parameter to trigger GitHub issue processing

## Instructions

You MUST follow the workflow steps in sequential order. Do NOT ask the user for confirmation between steps - automatically proceed through all steps.

## Workflow

### Step 1: Fetch Oldest GitHub Issue

Use the Bash tool to get the oldest open issue from the GitHub repository:

```bash
gh issue list --state open --json number,title,body,createdAt,labels --limit 100 | python3 -c "import json, sys; issues = json.load(sys.stdin); oldest = min(issues, key=lambda x: x['createdAt']) if issues else None; print(json.dumps(oldest, indent=2)) if oldest else print('{}')"
```

This command:
- Lists all open issues
- Sorts by creation date using Python (oldest first)
- Returns the first (oldest) issue
- Does not require jq to be installed

If no issues are found, report to the user and stop.

Parse the JSON output to extract:
- Issue number
- Issue title
- Issue body
- Labels (if any)
- Creation date

### Step 2: Parse Issue Template Data

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

### Step 3: Launch Product Owner Agent

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

### Step 4: Implement User Stories

After creating the user stories, automatically implement them:

Use the SlashCommand tool to execute:
```
/implement bug github-issue-{issue_number}
```

This will:
- Read the user stories created by the product-owner
- Execute all stories in the defined execution order
- Launch appropriate specialized agents for each story
- Record implementation progress in implementation-log.json
- Commit and push changes when complete

Wait for the implementation to complete.

### Step 5: Close GitHub Issue

If all user stories were successfully implemented:

1. Use the Bash tool to close the GitHub issue:
   ```bash
   gh issue close {issue_number} --comment "Fixed in commit {commit_url}. All user stories completed and tested."
   ```

If implementation was partial or blocked, skip this step and report the status.

### Step 6: Report

Provide a comprehensive summary that includes:
- GitHub issue number and title
- Feature ID associated
- User stories path created
- Number of user stories implemented
- Implementation status (completed/partial/blocked)
- GitHub issue status (closed/still open)
- Any errors or issues encountered

## Error Handling

- If gh command fails, ensure GitHub CLI is installed and authenticated
- If feature ID cannot be determined from GitHub issue, ask user
- If product-owner agent fails, report which issue failed and stop
- If /implement command fails, report error with details and do not close GitHub issue
- If implementation is partial or blocked, do not close GitHub issue
