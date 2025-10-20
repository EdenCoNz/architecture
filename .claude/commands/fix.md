---
description: Process and fix bugs from GitHub issues
---

## Purpose

Fetch the oldest open issue from GitHub and create user stories using the product-owner agent to address CI/CD failures.

## Arguments

- `gha`: Required parameter to trigger GitHub issue processing

## Instructions

You MUST follow the workflow steps in sequential order. Do NOT ask the user for confirmation between steps - automatically proceed through all steps.

## Error Handling

This command uses comprehensive error handling with specific error codes and recovery suggestions.

**Error Handling Reference**: See `.claude/helpers/command-error-handling.md` for complete error code documentation and `.claude/helpers/error-code-mapping.md` for validation error mapping.

**Common Errors**:
- ENV-001: Git repository not found → Initialize git or navigate to repository
- ENV-004: GitHub CLI not installed → Install GitHub CLI
- ENV-005: GitHub CLI not authenticated → Run `gh auth login`
- ENV-006: GitHub repository not connected → Add remote origin
- FS-001: Feature log not found → Run /feature command first
- FS-005: Invalid JSON in feature-log → Fix JSON syntax errors
- EXT-001: GitHub API rate limit exceeded → Wait for reset or authenticate
- EXT-003: No open GitHub issues → Informational, no work to do
- EXT-004: GitHub network error → Check network connection

**Error Handling Strategy**:
- All validation errors (Step 0) use standardized error codes
- GitHub CLI errors are BLOCKING - must be resolved before proceeding
- GitHub API errors are BLOCKING - cannot fetch issues without API access
- No open issues is INFORMATIONAL - not an error, just no work to do
- Network errors include retry suggestions with backoff

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
Command: /fix

Remediation:
1. Navigate to your git repository directory
2. Verify you are in the correct directory:
   pwd
3. This command requires a git repository to track bug fixes
```
- STOP execution immediately

#### Step 0.3: Validate Feature Log Exists

Check if docs/features/feature-log.json exists:
```bash
test -f "docs/features/feature-log.json" && echo "VALID" || echo "INVALID"
```

If output is "INVALID":
- Display error message:
```
Error: Feature log not found

File: docs/features/feature-log.json
Purpose: Tracks features that bugs are associated with
Command: /fix

Remediation:
1. Ensure you are in the correct project directory
2. Run /feature command at least once to initialize the feature log
3. Bug fixes must be associated with existing features

Example:
  /feature "Initialize project structure"
```
- STOP execution immediately

If feature-log.json exists, validate JSON syntax:
```bash
python3 -c "import json; json.load(open('docs/features/feature-log.json'))" 2>&1
```

If JSON validation fails:
- Display error message with specific JSON error and remediation steps (see pre-flight-validation.md)
- STOP execution immediately

#### Step 0.4: Validate GitHub CLI Authentication

Check if gh command exists:
```bash
command -v gh >/dev/null 2>&1 && echo "VALID" || echo "INVALID"
```

If output is "INVALID":
- Display error message:
```
Error: GitHub CLI not installed

Check: GitHub CLI availability
Status: 'gh' command not found
Command: /fix

Remediation:
1. Install GitHub CLI:
   - macOS: brew install gh
   - Linux: See https://cli.github.com/manual/installation
   - Windows: See https://cli.github.com/manual/installation
2. Verify installation:
   command -v gh
```
- STOP execution immediately

Check GitHub CLI authentication status:
```bash
gh auth status 2>&1
```

Parse output to verify authentication. If not authenticated:
- Display error message:
```
Error: GitHub CLI not authenticated

Check: GitHub CLI authentication status
Status: Not logged into any GitHub hosts
Command: /fix

Remediation:
1. Authenticate with GitHub CLI:
   gh auth login
2. Follow the interactive prompts to authenticate
3. Verify authentication:
   gh auth status
4. Ensure you have appropriate repository access
```
- STOP execution immediately

#### Step 0.5: Validate GitHub Repository Connection

Test GitHub repository connection:
```bash
gh repo view 2>&1
```

If command fails:
- Display error message:
```
Error: Cannot connect to GitHub repository

Check: GitHub repository connection
Status: Failed to fetch repository information
Command: /fix

Remediation:
1. Verify you are in a GitHub-connected repository:
   git remote -v
2. If no remote exists, add one:
   git remote add origin https://github.com/username/repo.git
3. Verify GitHub CLI can access the repository:
   gh repo view
4. Check your GitHub permissions for this repository
```
- STOP execution immediately

#### Step 0.6: Check for Open GitHub Issues (Warning)

Check if there are any open issues:
```bash
gh issue list --state open --limit 1 --json number
```

If output shows no issues (empty array []):
- Display warning message:
  ```
  Warning: No open GitHub issues found

  Status: No open issues in the repository
  Impact: /fix command processes oldest open issue
  Command: /fix

  Information:
  The /fix command is designed to process GitHub Actions CI/CD failures
  reported as GitHub issues.

  Next Steps:
  1. If you expect open issues, verify:
     - You are in the correct repository
     - Issues exist at: gh issue list --state open
  2. If no issues exist, this is normal - no bugs to fix
  3. Run /fix again when GitHub Actions creates failure issues

  This is informational only - no action needed if no issues exist.
  ```
  - STOP execution (no work to do, but not an error)

#### Step 0.7: Validate GitHub Integration Setup

Check if .github/ directory exists:
```bash
test -d ".github" && echo "VALID" || echo "INVALID"
```

If output is "INVALID":
- Display warning message:
```
Warning: GitHub integration directory not found

Status: .github/ directory does not exist
Impact: GitHub Actions workflows may not be configured
Command: /fix

Recommendation:
1. This command processes CI/CD failures from GitHub Actions
2. Ensure .github/workflows/ directory exists with workflow files
3. Verify GitHub Actions are enabled for this repository

You may continue, but the /fix command is most useful with GitHub Actions configured.
```
- This is a WARNING - allow execution to continue

#### Step 0.8: Validation Summary

If all validations pass:
- Output: "Pre-flight validation passed - proceeding to fetch oldest GitHub issue"
- Proceed to Step 1

If any critical validation failed:
- Execution has already been stopped
- User must remediate issues and re-run command

If no open issues found:
- Execution stopped (no work to do)
- This is informational, not an error

### Step 1: Fetch Oldest GitHub Issue

Use the Bash tool to get the oldest open issue:

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

### Step 5: Verify Issue Auto-Close

After implementation completes, verify that the commit message includes the correct issue reference for auto-closing.

**Verification Steps:**

1. Get the latest commit message from the implementation:
```bash
git log -1 --format='%B'
```

2. Check if the commit message contains "Fixes #{issue_number}":
```bash
git log -1 --format='%B' | grep -q "Fixes #${issue_number}" && echo "VALID" || echo "INVALID"
```

3. If output is "INVALID":
   - Display warning message:
   ```
   Warning: Commit message missing issue reference

   Expected: Commit message should include "Fixes #{issue_number}"
   Status: Issue reference not found in latest commit
   Impact: GitHub issue will not auto-close when PR is merged

   Commit message format should be:
   Implementation of bug-github-issue-{issue_number}-{title}

   Completed user stories:
   - Story #1: {title}

   Files modified:
   - {files}

   Fixes #{issue_number}

   This typically indicates /implement command did not follow the expected format.
   The issue can still be manually closed after PR merge.
   ```
   - Note this in the final report

4. If output is "VALID":
   - Confirm that the commit message includes "Fixes #{issue_number}"
   - The GitHub issue will automatically close when the commit is merged to the default branch (main/master)

Report to the user:
- Confirm that the commit message includes "Fixes #{issue_number}" (or warn if missing)
- Explain that the issue will auto-close upon merge to main/master (if reference found)
- If implementation was partial or blocked, note that the issue will remain open

### Step 6: Report

Provide a comprehensive summary that includes:
- GitHub issue number and title
- Feature ID associated
- User stories path created
- Number of user stories implemented
- Implementation status (completed/partial/blocked)
- Commit message verification status:
  - If verified: "Commit message includes 'Fixes #{issue_number}' - issue will auto-close on merge"
  - If not verified: "Warning: Commit message missing 'Fixes #{issue_number}' reference - manual close required"
- Note that issue will auto-close when PR is merged to main/master (if Fixes reference found)
- Any errors or issues encountered

## Error Handling

- If gh command fails, ensure GitHub CLI is installed and authenticated
- If feature ID cannot be determined from GitHub issue, ask user
- If product-owner agent fails, report which issue failed and stop
- If /implement command fails, report error with details and do not close GitHub issue
- If implementation is partial or blocked, do not close GitHub issue
