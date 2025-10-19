# Pre-Flight Validation System

## Purpose

This validation system provides comprehensive pre-flight checks for all slash commands in the architecture system. It ensures prerequisites are met before executing potentially destructive operations, providing clear error messages with specific remediation steps when validation fails.

## Design Principles

1. **Fail Fast**: Validate everything before starting execution
2. **Clear Errors**: Provide specific, actionable error messages
3. **Remediation Guidance**: Always tell users exactly how to fix issues
4. **Reusable Components**: Modular validation functions for common checks
5. **Non-Blocking**: Some validations can be warnings instead of hard failures

## Validation Categories

### 1. File Existence Validation

Verify required files exist before attempting operations.

#### Required Files by Command

**All Commands (Universal):**
- `.git/` directory (to verify git repository)

**/feature Command:**
- `docs/features/feature-log.json` (created automatically if missing)
- `.claude/agents/` directory (contains available agents)

**/implement Command:**
- `docs/features/{id}/user-stories.md` (feature) OR `docs/features/*/bugs/{id}/user-stories.md` (bug)
- `docs/features/feature-log.json` (for tracking implementation completion)

**/fix Command:**
- `.github/` directory (for GitHub integration)
- `docs/features/feature-log.json` (for tracking bugs)

**/summarise Command:**
- `docs/features/feature-log.json` (for finding features to summarise)
- `docs/features/{id}/implementation-log.json` (for each feature to summarise)

**/commit Command:**
- Working directory changes (verified via `git status`)

#### Validation Workflow

```
For each required file:
  1. Check if file exists at expected path
  2. If file is a JSON file, validate JSON syntax
  3. If validation fails:
     - Provide specific error message
     - Explain what the file is for
     - Provide remediation steps
     - Stop execution
```

#### Error Message Format

```
Error: Required file not found

File: {file_path}
Purpose: {what this file is for}
Command: /{command_name}

Remediation:
{specific steps to create or fix the file}

Example:
{example command or file content if applicable}
```

#### Example Error Messages

**Missing user-stories.md:**
```
Error: User stories file not found

File: docs/features/5/user-stories.md
Purpose: Contains user stories for Feature #5
Command: /implement

Remediation:
1. Verify the feature ID is correct
2. Run /feature command to create user stories for this feature
3. Ensure user stories were successfully created before running /implement

Example:
  /feature "Your feature description here"
```

**Missing feature-log.json:**
```
Error: Feature log file not found

File: docs/features/feature-log.json
Purpose: Tracks all features and their implementation status
Command: /implement

Remediation:
1. Ensure you are in the correct project directory
2. Run /feature command at least once to initialize the feature log
3. Verify the docs/features/ directory exists

Example:
  /feature "Initialize project structure"
```

**Invalid JSON in feature-log.json:**
```
Error: Feature log file contains invalid JSON

File: docs/features/feature-log.json
Purpose: Tracks all features and their implementation status
Command: /implement
JSON Error: Unexpected token '}' at line 15, column 3

Remediation:
1. Open docs/features/feature-log.json in a text editor
2. Fix the JSON syntax error at the indicated line
3. Validate JSON using a tool like jsonlint.com
4. Ensure the file follows the expected schema

Expected Schema:
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

### 2. Git Repository State Validation

Verify git repository is in a safe state before operations that modify files or create commits.

#### Git State Checks

**For /commit Command:**
- ✅ Git repository exists (`.git/` directory)
- ✅ Working directory has changes to commit (`git status` shows modifications)
- ✅ Not in detached HEAD state
- ⚠️ Warning if there are uncommitted changes to critical files (.env, credentials, etc.)

**For /feature Command:**
- ✅ Git repository exists
- ⚠️ Warning if working directory is not clean (suggest committing first)
- ✅ Can create new branch

**For /implement Command:**
- ✅ Git repository exists
- ✅ On correct feature branch (feature/{id}-* or main/master)
- ⚠️ Warning if branch is behind remote

**For /fix Command:**
- ✅ Git repository exists
- ✅ GitHub CLI authenticated (`gh auth status`)

#### Validation Workflow

```
1. Check .git/ directory exists
   - If not: Error "Not a git repository"

2. Run `git status --porcelain` to check working tree state
   - Parse output to identify:
     - Modified files
     - Untracked files
     - Deleted files
     - Renamed files

3. Run `git rev-parse --abbrev-ref HEAD` to get current branch
   - Check if in detached HEAD state
   - Validate branch name matches expected pattern for command

4. Run `git status -uno` to check if branch is behind remote
   - Parse for "Your branch is behind" message
   - Provide warning if behind remote

5. For /fix command: Run `gh auth status`
   - Verify GitHub CLI is authenticated
   - Check for appropriate scopes
```

#### Error Message Format

```
Error: Git repository validation failed

Check: {what was being validated}
Status: {what was found}
Command: /{command_name}

Remediation:
{specific steps to fix the issue}
```

#### Example Error Messages

**Not a git repository:**
```
Error: Not a git repository

Check: Git repository existence
Status: No .git/ directory found in current working directory
Command: /commit

Remediation:
1. Navigate to your git repository directory
2. If this is a new project, initialize git:
   git init
3. Verify you are in the correct directory:
   pwd
```

**Detached HEAD state:**
```
Error: Repository is in detached HEAD state

Check: Git HEAD reference
Status: HEAD is detached at commit abc1234
Command: /implement

Remediation:
1. Checkout a branch to reattach HEAD:
   git checkout main
   OR
   git checkout feature/5-your-feature
2. If you want to keep changes, create a new branch:
   git checkout -b feature/new-feature-name
```

**No changes to commit:**
```
Error: No changes to commit

Check: Working directory modifications
Status: Working tree is clean (no modifications, additions, or deletions)
Command: /commit

Remediation:
1. Make changes to files before committing
2. Verify you are in the correct directory
3. Check git status to see current state:
   git status
```

**GitHub CLI not authenticated:**
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

### 3. Dependency Validation

Verify dependencies between operations are met before execution.

#### Dependency Checks by Command

**/feature Command:**
- ⚠️ Warning if .claude/agents/ directory is empty (no agents available for implementation)

**/implement Command:**
- ✅ User stories exist for the specified feature/bug
- ✅ Feature exists in feature-log.json
- ✅ For bug: GitHub issue number format is valid (github-issue-{number})
- ⚠️ Warning if feature already fully implemented (userStoriesImplemented is set)

**/fix Command:**
- ✅ GitHub repository connection is working (`gh repo view`)
- ✅ Open issues exist on GitHub

**/summarise Command:**
- ✅ At least one feature with implementation-log.json exists
- ✅ At least one unsummarised feature exists (isSummarised: false)
- ⚠️ Warning if all features already summarised

**/commit Command:**
- ✅ Commit message is provided and not empty
- ⚠️ Warning if committing sensitive files (.env, credentials, secrets, etc.)

#### Validation Workflow

```
1. For each dependency requirement:
   - Read necessary files/data
   - Check dependency condition
   - If hard requirement (✅) fails:
     - Provide specific error message
     - Explain the dependency
     - Provide remediation steps
     - Stop execution
   - If soft requirement (⚠️) fails:
     - Provide warning message
     - Explain potential issue
     - Allow execution to continue
```

#### Error Message Format

```
Error: Dependency validation failed

Dependency: {what dependency is required}
Status: {what was found}
Command: /{command_name}

Remediation:
{specific steps to meet the dependency}

Example:
{example command or workflow if applicable}
```

#### Example Error Messages

**Feature not in feature log:**
```
Error: Feature not found in feature log

Dependency: Feature must be registered in feature log before implementation
Status: Feature #8 not found in docs/features/feature-log.json
Command: /implement

Remediation:
1. Verify the feature ID is correct
2. Check feature-log.json for available features
3. If feature should exist, run /feature command to create it:
   /feature "Your feature description"
4. Ensure feature-log.json contains an entry with featureID: "8"
```

**No unsummarised features:**
```
Warning: All features already summarised

Dependency: At least one feature with isSummarised: false
Status: All 5 features have isSummarised: true
Command: /summarise

Impact:
No work to be done - all features have already been summarised.

Next Steps:
1. Review docs/features/implementation-log-summary.json for existing summaries
2. Implement new features and run /summarise again
3. Manually set isSummarised: false for a feature to re-summarise it
```

**Invalid bug ID format:**
```
Error: Invalid bug ID format

Dependency: Bug ID must follow format 'github-issue-{number}'
Status: Received bug ID 'bug-10' which does not match expected pattern
Command: /implement

Remediation:
1. Use the correct bug ID format: github-issue-{number}
2. Find the GitHub issue number for this bug
3. Run the command again with correct format

Example:
  /implement bug github-issue-37
  (for GitHub issue #37)
```

**Committing sensitive files:**
```
Warning: Attempting to commit potentially sensitive files

Dependency: No sensitive files should be committed to repository
Status: Detected sensitive file(s) in staging area:
  - .env
  - backend/credentials.json

Impact:
These files may contain secrets, passwords, or API keys that should not be in version control.

Remediation:
1. Remove sensitive files from staging:
   git reset HEAD .env backend/credentials.json
2. Add to .gitignore:
   echo ".env" >> .gitignore
   echo "credentials.json" >> .gitignore
3. Store sensitive values in environment variables or secret management system
4. Commit .gitignore changes:
   git add .gitignore
   git commit -m "Add sensitive files to gitignore"

If you are certain these files should be committed, you may override this warning.
```

## Validation Helper Functions

### File Validation Functions

```markdown
## Validate File Exists

Input:
- file_path: Absolute path to file
- purpose: Description of what file is for
- command: Name of command requiring file

Process:
1. Use Bash tool to check file existence:
   test -f "{file_path}" && echo "EXISTS" || echo "NOT_FOUND"
2. If NOT_FOUND:
   - Generate error message using template
   - Return validation failure

Output:
- validation_result: "pass" | "fail"
- error_message: Error message if validation fails (null otherwise)

Example:
validateFileExists(
  file_path="/home/ed/Dev/architecture/docs/features/5/user-stories.md",
  purpose="Contains user stories for Feature #5",
  command="implement"
)
→ { validation_result: "fail", error_message: "Error: User stories file not found..." }
```

```markdown
## Validate JSON File

Input:
- file_path: Absolute path to JSON file
- purpose: Description of what file is for
- command: Name of command requiring file
- schema_description: Optional description of expected schema

Process:
1. Validate file exists using validateFileExists
2. Use Python/jq to validate JSON syntax:
   python3 -m json.tool "{file_path}" > /dev/null 2>&1
3. If validation fails:
   - Capture JSON error message
   - Generate error message with line number
   - Return validation failure

Output:
- validation_result: "pass" | "fail"
- error_message: Error message if validation fails (null otherwise)
- json_data: Parsed JSON if validation succeeds (null otherwise)

Example:
validateJSONFile(
  file_path="/home/ed/Dev/architecture/docs/features/feature-log.json",
  purpose="Tracks all features and their implementation status",
  command="implement",
  schema_description="{features: [...]}"
)
→ { validation_result: "pass", error_message: null, json_data: {...} }
```

### Git Validation Functions

```markdown
## Validate Git Repository

Input:
- command: Name of command requiring git repository

Process:
1. Check .git/ directory exists:
   test -d ".git" && echo "EXISTS" || echo "NOT_FOUND"
2. If NOT_FOUND:
   - Generate error message
   - Return validation failure

Output:
- validation_result: "pass" | "fail"
- error_message: Error message if validation fails (null otherwise)

Example:
validateGitRepository(command="commit")
→ { validation_result: "pass", error_message: null }
```

```markdown
## Validate Working Tree State

Input:
- command: Name of command requiring clean/dirty working tree
- require_changes: Boolean - true if changes required, false if clean tree required

Process:
1. Run git status:
   git status --porcelain
2. Parse output to detect changes
3. If require_changes=true and no changes:
   - Generate error message
   - Return validation failure
4. If require_changes=false and changes exist:
   - Generate warning message
   - Return validation warning

Output:
- validation_result: "pass" | "warning" | "fail"
- message: Error or warning message if applicable (null otherwise)
- changes: Array of changed files with status

Example:
validateWorkingTreeState(command="commit", require_changes=true)
→ { validation_result: "pass", message: null, changes: [{status: "M", file: "src/app.ts"}] }
```

```markdown
## Validate Git Branch

Input:
- command: Name of command requiring specific branch
- expected_pattern: Regex pattern for expected branch name (optional)

Process:
1. Get current branch:
   git rev-parse --abbrev-ref HEAD
2. Check for detached HEAD state
3. If expected_pattern provided:
   - Validate branch name matches pattern
4. Check if branch is behind remote:
   git status -uno | grep "Your branch is behind"

Output:
- validation_result: "pass" | "warning" | "fail"
- message: Error or warning message if applicable
- current_branch: Current branch name
- is_behind_remote: Boolean

Example:
validateGitBranch(command="implement", expected_pattern="^(main|master|feature/.+)$")
→ { validation_result: "pass", message: null, current_branch: "feature/5-improvements", is_behind_remote: false }
```

```markdown
## Validate GitHub CLI

Input:
- command: Name of command requiring GitHub CLI

Process:
1. Check gh command exists:
   command -v gh > /dev/null 2>&1
2. Check authentication status:
   gh auth status
3. Parse output for login state
4. If not authenticated or gh not found:
   - Generate error message
   - Return validation failure

Output:
- validation_result: "pass" | "fail"
- error_message: Error message if validation fails (null otherwise)
- authenticated_user: GitHub username if authenticated (null otherwise)

Example:
validateGitHubCLI(command="fix")
→ { validation_result: "pass", error_message: null, authenticated_user: "octocat" }
```

### Dependency Validation Functions

```markdown
## Validate Feature Exists

Input:
- feature_id: Feature ID to validate
- command: Name of command requiring feature
- feature_log_path: Path to feature-log.json (default: docs/features/feature-log.json)

Process:
1. Validate feature-log.json exists and is valid JSON
2. Read feature-log.json
3. Search for feature with matching featureID
4. If not found:
   - Generate error message
   - Return validation failure

Output:
- validation_result: "pass" | "fail"
- error_message: Error message if validation fails (null otherwise)
- feature_data: Feature object if found (null otherwise)

Example:
validateFeatureExists(feature_id="5", command="implement")
→ { validation_result: "pass", error_message: null, feature_data: {...} }
```

```markdown
## Validate User Stories Exist

Input:
- type: "feature" | "bug"
- id: Feature or bug ID
- command: Name of command requiring user stories

Process:
1. Determine user stories path based on type:
   - Feature: docs/features/{id}/user-stories.md
   - Bug: Search for docs/features/*/bugs/{id}/user-stories.md
2. Validate file exists
3. If not found:
   - Generate error message with remediation
   - Return validation failure

Output:
- validation_result: "pass" | "fail"
- error_message: Error message if validation fails (null otherwise)
- user_stories_path: Path to user stories file if found (null otherwise)

Example:
validateUserStoriesExist(type="feature", id="5", command="implement")
→ { validation_result: "pass", error_message: null, user_stories_path: "docs/features/5/user-stories.md" }
```

```markdown
## Validate Sensitive Files

Input:
- files: Array of file paths being committed
- command: Name of command (typically "commit")

Process:
1. Define sensitive file patterns:
   - .env, .env.*
   - *credentials*, *secrets*, *password*
   - *.pem, *.key, *.p12
   - config/database.yml, config/secrets.yml
2. Check each file against patterns
3. If sensitive files found:
   - Generate warning message
   - Return validation warning

Output:
- validation_result: "pass" | "warning"
- message: Warning message if sensitive files detected (null otherwise)
- sensitive_files: Array of detected sensitive files

Example:
validateSensitiveFiles(files=["src/app.ts", ".env", "README.md"], command="commit")
→ { validation_result: "warning", message: "Warning: Attempting to commit...", sensitive_files: [".env"] }
```

## Integration Guide for Commands

### Standard Pre-Flight Validation Workflow

Every command should follow this standard workflow:

```
## Pre-Flight Validation

Before executing any operations, run comprehensive validation checks:

### Step 0.1: Load Validation System

Read the validation helper from .claude/helpers/pre-flight-validation.md to access all validation functions.

### Step 0.2: Run File Existence Checks

Validate all required files exist:
- {list specific files for this command}

Use validateFileExists() for regular files.
Use validateJSONFile() for JSON files (includes syntax validation).

If any file validation fails:
- Display error message with remediation steps
- STOP execution immediately
- Do NOT proceed to subsequent steps

### Step 0.3: Run Git State Checks

Validate git repository state:
- {list specific git checks for this command}

Use validateGitRepository() to check .git/ exists.
Use validateWorkingTreeState() to check for required/unwanted changes.
Use validateGitBranch() to validate current branch.
Use validateGitHubCLI() to validate GitHub authentication (if needed).

If any critical git validation fails:
- Display error message with remediation steps
- STOP execution immediately

If warnings are generated:
- Display warning messages
- Continue execution (user can choose to abort)

### Step 0.4: Run Dependency Checks

Validate all dependencies are met:
- {list specific dependencies for this command}

Use validateFeatureExists() to check feature registration.
Use validateUserStoriesExist() to check user stories.
Use validateSensitiveFiles() to check for sensitive files (if applicable).

If any critical dependency validation fails:
- Display error message with remediation steps
- STOP execution immediately

If warnings are generated:
- Display warning messages
- Allow user to decide whether to continue

### Step 0.5: Validation Summary

If all validations pass:
- Output: "Pre-flight validation passed - proceeding with {command} command"
- Proceed to Step 1 of normal workflow

If any validation failed:
- All error messages have been displayed
- Execution has been stopped
- User must remediate issues and re-run command
```

### Command-Specific Validation Requirements

**/commit Command:**
```markdown
## Pre-Flight Validation for /commit

Step 0.2 - File Existence Checks:
- None required (git repository is the only requirement)

Step 0.3 - Git State Checks:
- validateGitRepository() → Must pass
- validateWorkingTreeState(require_changes=true) → Must pass
- validateGitBranch() with check for detached HEAD → Must pass
- Check current branch name → Warning if on main/master

Step 0.4 - Dependency Checks:
- Validate commit message is provided and not empty → Must pass
- Get list of files to commit (git status --porcelain)
- validateSensitiveFiles(files) → Warning if sensitive files detected

Step 0.5 - Validation Summary:
- If validation passes, proceed to Step 1: Stage all changes
```

**/feature Command:**
```markdown
## Pre-Flight Validation for /feature

Step 0.2 - File Existence Checks:
- Check .claude/agents/ directory exists → Must pass
- Check docs/features/ directory exists → Create if missing (not an error)
- Check docs/features/feature-log.json exists → Create if missing (not an error)
- If feature-log.json exists: validateJSONFile() → Must pass

Step 0.3 - Git State Checks:
- validateGitRepository() → Must pass
- validateWorkingTreeState(require_changes=false) → Warning if dirty

Step 0.4 - Dependency Checks:
- Check .claude/agents/ directory is not empty → Warning if empty
- Read available agents for missing agent detection

Step 0.5 - Validation Summary:
- If validation passes, proceed to Step 1: Launch Product Owner Agent
```

**/implement Command:**
```markdown
## Pre-Flight Validation for /implement

Step 0.1 - Determine Paths Based on Type:
- Parse type ("feature" or "bug") and id from arguments
- Determine user stories path and implementation log path
- Store paths for use in subsequent validation steps

Step 0.2 - File Existence Checks:
- validateJSONFile(docs/features/feature-log.json) → Must pass
- Validate user stories file exists at determined path → Must pass
- If implementation log exists: validateJSONFile() → Must pass

Step 0.3 - Git State Checks:
- validateGitRepository() → Must pass
- validateGitBranch(expected_pattern="^(main|master|feature/.+)$") → Must pass
- Check if branch behind remote → Warning if behind

Step 0.4 - Dependency Checks:
- Extract feature ID from user stories path
- validateFeatureExists(feature_id) → Must pass
- If type is "bug": validate id matches "github-issue-{number}" pattern → Must pass
- Check if feature already fully implemented → Warning if userStoriesImplemented is set
- Check if context files exist in context/ directory → Warning if missing expected context

Step 0.5 - Validation Summary:
- If validation passes, proceed to Step 1: Validate User Stories File (existing workflow)
- Note: Step 1 is redundant after pre-flight validation but retained for backwards compatibility
```

**/fix Command:**
```markdown
## Pre-Flight Validation for /fix

Step 0.2 - File Existence Checks:
- validateJSONFile(docs/features/feature-log.json) → Must pass
- Check .github/ directory exists → Must pass (indicates GitHub integration)

Step 0.3 - Git State Checks:
- validateGitRepository() → Must pass
- validateGitHubCLI() → Must pass

Step 0.4 - Dependency Checks:
- Test GitHub repository connection: gh repo view → Must pass
- Check for open issues: gh issue list --state open --limit 1 → Warning if none

Step 0.5 - Validation Summary:
- If validation passes, proceed to Step 1: Fetch Oldest GitHub Issue
```

**/summarise Command:**
```markdown
## Pre-Flight Validation for /summarise

Step 0.2 - File Existence Checks:
- validateJSONFile(docs/features/feature-log.json) → Must pass

Step 0.3 - Git State Checks:
- validateGitRepository() → Must pass (for final commit)

Step 0.4 - Dependency Checks:
- Read feature-log.json
- Check for features with implementation logs:
  - For each feature with userStoriesImplemented set:
    - Check if docs/features/{id}/implementation-log.json exists
    - Validate JSON if exists
- Count unsummarised features (isSummarised: false or missing) with implementation logs
- If zero unsummarised features found → Warning and exit early (no work to do)

Step 0.5 - Validation Summary:
- If validation passes and unsummarised features found, proceed to Step 1: Validate Feature Log
- If zero unsummarised features: display warning and exit (not an error, just no work)
```

## Validation Output Format

All validation functions should use consistent output format for easy parsing and clear user feedback.

### Success Output

```
✓ Pre-flight validation passed

Checks performed:
- File existence: 3 files validated
- Git repository: Repository clean and ready
- Dependencies: All requirements met

Proceeding with /{command} command...
```

### Failure Output

```
✗ Pre-flight validation failed

The following issues must be resolved before proceeding:

1. Error: User stories file not found
   File: docs/features/5/user-stories.md
   Purpose: Contains user stories for Feature #5

   Remediation:
   - Verify the feature ID is correct
   - Run /feature command to create user stories

2. Error: Feature not found in feature log
   Dependency: Feature must be registered before implementation

   Remediation:
   - Check feature-log.json for available features
   - Run /feature command to create the feature

Execution stopped. Please resolve the above issues and try again.
```

### Warning Output

```
⚠ Pre-flight validation warnings

The following non-critical issues were detected:

1. Warning: Working directory is not clean
   Status: 3 modified files, 1 untracked file

   Impact: Changes may conflict with command operations

   Recommendation:
   - Commit or stash changes before proceeding
   - Or continue at your own risk

2. Warning: All features already summarised
   Status: 5 of 5 features have isSummarised: true

   Impact: No work to be done by /summarise command

   Recommendation:
   - Review existing summaries
   - Implement new features before running /summarise

Continue with /{command} command? (Warnings can be ignored)
```

## Testing Pre-Flight Validation

### Manual Testing Checklist

For each command, test the following scenarios:

**File Existence Validation:**
- ✅ All required files exist (should pass)
- ❌ One required file missing (should fail with specific error)
- ❌ JSON file has syntax error (should fail with line number)

**Git State Validation:**
- ✅ Valid git repository (should pass)
- ❌ Not a git repository (should fail)
- ❌ Detached HEAD state (should fail for most commands)
- ⚠️ Working directory dirty (should warn for /feature)
- ⚠️ Working directory clean (should fail for /commit)

**Dependency Validation:**
- ✅ All dependencies met (should pass)
- ❌ Feature not in feature log (should fail for /implement)
- ❌ Invalid bug ID format (should fail for /implement bug)
- ⚠️ No unsummarised features (should warn and exit for /summarise)
- ⚠️ Sensitive files in staging (should warn for /commit)

### Automated Testing

Consider creating test cases for common validation scenarios:

```bash
# Test: Missing user stories file
rm docs/features/5/user-stories.md
/implement feature 5
# Expected: Error with remediation steps

# Test: Invalid JSON
echo "invalid json" > docs/features/feature-log.json
/implement feature 5
# Expected: JSON syntax error with line number

# Test: Not authenticated with GitHub
gh auth logout
/fix gha
# Expected: GitHub CLI authentication error

# Test: No changes to commit
git checkout .
/commit "test message"
# Expected: No changes to commit error

# Test: Detached HEAD
git checkout HEAD~1
/implement feature 5
# Expected: Detached HEAD error
```

## Maintenance and Evolution

### Adding New Validations

When adding new validation checks:

1. **Define the validation requirement clearly**
   - What is being validated?
   - Is it a hard requirement (fail) or soft requirement (warning)?
   - Which commands need this validation?

2. **Create validation function**
   - Add to appropriate category in this document
   - Follow standard output format
   - Include clear error messages and remediation steps

3. **Update command integration**
   - Add validation to Step 0.X in command workflow
   - Test validation in isolation
   - Test validation integrated with full command workflow

4. **Document the validation**
   - Add to validation helper functions section
   - Include examples and expected outputs
   - Update integration guide for affected commands

### Validation Performance

Validation should be fast (< 1 second for all checks) to avoid slowing down command execution.

**Performance Guidelines:**
- Use bash commands over heavy tools when possible
- Cache validation results within a command execution when same check needed multiple times
- Avoid unnecessary file reads (validate once per file)
- Run validations in parallel when checks are independent

**Performance Optimization:**
```
Instead of:
  validateFileExists(file1)
  validateFileExists(file2)
  validateFileExists(file3)

Use parallel checks:
  test -f "file1" && echo "file1:OK" || echo "file1:FAIL"
  test -f "file2" && echo "file2:OK" || echo "file2:FAIL"
  test -f "file3" && echo "file3:OK" || echo "file3:FAIL"
```

## Quick Reference

### Validation Checklist by Command

| Command | File Checks | Git Checks | Dependency Checks |
|---------|-------------|------------|-------------------|
| /commit | None | Repository, Changes required, Not detached HEAD | Commit message provided, No sensitive files |
| /feature | Agents dir, Feature log JSON | Repository, Clean working tree (warning) | Agents available (warning) |
| /implement | User stories, Feature log JSON | Repository, Correct branch | Feature exists, Valid bug ID format |
| /fix | Feature log JSON, .github dir | Repository, GitHub CLI auth | GitHub connection, Open issues exist |
| /summarise | Feature log JSON | Repository | Unsummarised features exist |

### Error vs Warning

**Use Error (fail validation) when:**
- Missing required file that command cannot create
- Invalid JSON in critical configuration file
- Git repository doesn't exist
- Required dependency is not met
- Operation would fail if continued

**Use Warning (continue with caution) when:**
- Working directory state is suboptimal but not blocking
- Recommended files missing but command can proceed
- Optional optimization opportunity missed
- User should be aware but can make informed decision to continue

### Common Validation Patterns

**Pattern 1: Validate JSON File with Schema**
```
1. Check file exists
2. Validate JSON syntax with python3 -m json.tool
3. Parse JSON and check for required fields
4. Validate data types and value ranges
```

**Pattern 2: Validate Git Repository State**
```
1. Check .git/ directory exists
2. Run git status --porcelain to get working tree state
3. Parse output to categorize changes
4. Check for specific conditions based on command requirements
```

**Pattern 3: Validate External Tool Availability**
```
1. Check command exists with command -v {tool}
2. Run tool-specific health check command
3. Parse output to verify tool is properly configured
4. Provide remediation if tool missing or misconfigured
```

## Conclusion

This pre-flight validation system provides comprehensive, reusable validation components that can be integrated into all slash commands. By validating prerequisites before execution, we catch issues early, provide clear error messages, and guide users to successful command execution.

**Key Benefits:**
- **Fail Fast**: Issues caught before any destructive operations
- **Clear Guidance**: Specific remediation steps for every error
- **Reusable Components**: Modular validation functions
- **Consistent Experience**: Same validation patterns across all commands
- **Maintainable**: Easy to add new validations as system evolves
