---
description: Stage all changes and create a git commit
args:
  - name: message
    description: The commit message
    required: true
  - name: push
    description: Optional - use "push" to push changes after committing
    required: false
model: claude-sonnet-4-5
---

## Purpose

This command stages all changes in the working directory and creates a git commit with the provided message. Optionally, it can push the changes to the remote repository if "push" is specified as the second argument.

## Variables

- `{{{ args.message }}}` - The commit message to use for the git commit
- `{{{ args.push }}}` - Optional parameter - if set to "push", will push changes after committing

## Instructions

- MUST stage all changes using `git add .` before committing
- MUST use the provided message exactly as given
- MUST NOT modify or enhance the commit message
- MUST follow Git Safety Protocol from the Bash tool documentation
- MUST NOT skip hooks or use --no-verify unless explicitly requested
- MUST handle all errors using the error handling system from .claude/helpers/command-error-handling.md

## Error Handling

This command uses comprehensive error handling with specific error codes and recovery suggestions.

**Error Handling Reference**: See `.claude/helpers/command-error-handling.md` for complete error code documentation.

**Common Errors**:
- ENV-001: Git repository not found → Initialize git or navigate to correct directory
- ENV-003: Detached HEAD state → Checkout a branch before committing
- GIT-001: No changes to commit → Make changes before running commit command
- INPUT-001: Missing commit message → Provide commit message as first argument
- GIT-008: Invalid commit message → Provide non-empty commit message
- GIT-005: Push rejected by remote → Pull latest changes or resolve conflicts

**Error Handling Strategy**:
- All validation errors (Step 0) are BLOCKING - execution stops immediately
- Git operation errors are BLOCKING - cannot proceed without resolution
- Sensitive file warnings are NON-BLOCKING - user can choose to continue
- All errors display structured error messages with recovery steps

## Workflow

### Step 0: Pre-Flight Validation

Before executing any operations, run comprehensive validation checks to ensure prerequisites are met.

#### Step 0.1: Load Error Handling and Validation Systems

Read error handling system from .claude/helpers/command-error-handling.md to understand error codes, categories, and message formats.

Read validation helper from .claude/helpers/pre-flight-validation.md to understand validation requirements and error message formats.

#### Step 0.2: Validate Git Repository Exists

Run the following check to verify this is a git repository:
```bash
test -d ".git" && echo "VALID" || echo "INVALID"
```

If output is "INVALID":
- Display error message with error code ENV-001:
```
ERROR: Git repository not found

Code: ENV-001
Category: Environment Errors
Command: /commit

Details:
Cannot find .git/ directory in current working directory. Git operations
require a valid git repository.

Context:
- Attempted operation: Stage and commit changes
- Working directory: {current directory from pwd}
- Expected: .git/ directory to exist

Impact:
All git operations will fail. Cannot stage changes or create commits without
a git repository.

Recovery Steps:
1. If this is a new project, initialize git repository:
   git init

2. If repository exists elsewhere, navigate to it:
   cd /path/to/your/repository

3. Verify you are in the correct directory:
   pwd
   ls -la .git/

For more information, see: .claude/helpers/command-error-handling.md (ENV-001)
```
- STOP execution immediately

#### Step 0.3: Validate Working Directory Has Changes

Run git status to check for changes:
```bash
git status --porcelain
```

If output is empty (no changes):
- Display error message with error code GIT-001:
```
ERROR: No changes to commit

Code: GIT-001
Category: Git Operations
Command: /commit

Details:
Working tree is clean - no modifications, additions, or deletions detected.
Git commit requires changes to be staged.

Context:
- Attempted operation: Create git commit
- Working directory: {current directory}
- Git status: Clean (no changes)

Impact:
Cannot create empty commit. Commit operation has nothing to stage or commit.

Recovery Steps:
1. Make changes to files before committing:
   - Edit existing files
   - Create new files
   - Delete files

2. Verify you are in the correct directory:
   pwd

3. Check git status to see current state:
   git status

4. If changes exist but are in .gitignore, review .gitignore patterns

For more information, see: .claude/helpers/command-error-handling.md (GIT-001)
```
- STOP execution immediately

#### Step 0.4: Check for Detached HEAD State

Run the following check:
```bash
git rev-parse --abbrev-ref HEAD
```

If output is "HEAD":
- Display error message:
```
Error: Repository is in detached HEAD state

Check: Git HEAD reference
Status: HEAD is detached
Command: /commit

Remediation:
1. Checkout a branch to reattach HEAD:
   git checkout main
   OR
   git checkout -b feature/new-feature-name
2. If you want to keep changes, create a new branch first
```
- STOP execution immediately

#### Step 0.5: Validate Commit Message Provided

Check if commit message argument is provided and not empty:

If message is empty or not provided:
- Display error message:
```
Error: Commit message is required

Check: Commit message argument
Status: No commit message provided or message is empty
Command: /commit

Remediation:
1. Provide a commit message as the first argument
2. Use quotes if message contains spaces

Example:
  /commit "Add user authentication feature"
```
- STOP execution immediately

#### Step 0.6: Check for Sensitive Files (Warning)

Run git status to get list of files to be committed:
```bash
git status --porcelain
```

Check each file against sensitive file patterns:
- .env, .env.*
- *credentials*, *secrets*, *password*
- *.pem, *.key, *.p12
- config/database.yml, config/secrets.yml

If any sensitive files detected:
- Display warning message:
```
Warning: Attempting to commit potentially sensitive files

Status: Detected sensitive file(s) in staging area:
  - {list of sensitive files}

Impact:
These files may contain secrets, passwords, or API keys that should not be in version control.

Remediation:
1. Remove sensitive files from staging:
   git reset HEAD {files}
2. Add to .gitignore:
   echo "{pattern}" >> .gitignore
3. Store sensitive values in environment variables or secret management system

If you are certain these files should be committed, you may continue.
```
- This is a WARNING, not an error - allow execution to continue

#### Step 0.7: Validation Summary

If all validations pass:
- Output: "Pre-flight validation passed - proceeding with commit"
- Proceed to Step 1

If any validation failed:
- Execution has already been stopped
- User must remediate issues and re-run command

### Step 1: Stage all changes

Use the Bash tool to run `git add .` to stage all changes in the working directory.

### Step 2: Create the commit

Use the Bash tool to run `git commit -m "{{{ args.message }}}"` with the provided message.

Use a HEREDOC format to ensure proper formatting:
```
git commit -m "$(cat <<'EOF'
{{{ args.message }}}
EOF
)"
```

### Step 3: Push to remote (conditional)

Check if `{{{ args.push }}}` is set to "push":
- If yes, run `git push` to push the committed changes to the remote repository
- If no or empty, skip this step

### Step 4: Verify the result

Run `git status` to confirm the commit was created successfully and show the current state.

## Report

Report back to the user:
- Confirmation that changes were staged
- Confirmation that the commit was created
- The commit message used
- Whether changes were pushed (if push argument was provided)
- Current git status
