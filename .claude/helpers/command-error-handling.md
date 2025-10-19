# Command-Level Error Handling System

## Purpose

This system provides comprehensive error handling for all slash commands in the architecture system. It wraps around the existing pre-flight validation system and provides structured error reporting, recovery suggestions, and graceful failure modes for all command operations.

## Design Principles

1. **Fail Gracefully**: Never crash - always provide actionable error messages
2. **Categorize Errors**: Use structured error types with specific error codes
3. **Provide Context**: Include what failed, why it failed, and what was attempted
4. **Suggest Recovery**: Always provide specific steps to resolve the issue
5. **Preserve State**: Ensure partial failures don't corrupt system state
6. **Log Everything**: Track all errors for debugging and metrics

## Error Categories and Codes

### Category 1: Environment Errors (ENV-XXX)

Errors related to the runtime environment and prerequisites.

**ENV-001: Git Repository Not Found**
- Trigger: `.git/` directory does not exist
- Impact: Cannot perform any git operations
- Recovery: Initialize git repository or navigate to correct directory

**ENV-002: Not a Git Repository**
- Trigger: Working directory is not inside a git repository
- Impact: Git commands will fail
- Recovery: Move to git repository or initialize one

**ENV-003: Detached HEAD State**
- Trigger: Repository is in detached HEAD state
- Impact: Commits may be lost, branch operations unavailable
- Recovery: Checkout a branch or create new branch from current state

**ENV-004: GitHub CLI Not Installed**
- Trigger: `gh` command not found in PATH
- Impact: Cannot interact with GitHub issues and PRs
- Recovery: Install GitHub CLI using package manager

**ENV-005: GitHub CLI Not Authenticated**
- Trigger: `gh auth status` shows not authenticated
- Impact: Cannot access GitHub repository data
- Recovery: Run `gh auth login` and authenticate

**ENV-006: GitHub Repository Not Connected**
- Trigger: No remote repository configured or connection fails
- Impact: Cannot fetch issues, create PRs, or sync with remote
- Recovery: Add remote origin or check network connection

**ENV-007: Python Not Available**
- Trigger: `python3` command not found
- Impact: Cannot validate JSON or run Python-based utilities
- Recovery: Install Python 3 or check PATH

### Category 2: File System Errors (FS-XXX)

Errors related to file and directory operations.

**FS-001: Required File Not Found**
- Trigger: Expected file does not exist at specified path
- Impact: Command cannot proceed without the file
- Recovery: Create the file or run prerequisite command

**FS-002: Required Directory Not Found**
- Trigger: Expected directory does not exist
- Impact: Cannot read or write files to directory
- Recovery: Create directory or run setup command

**FS-003: File Read Permission Denied**
- Trigger: Insufficient permissions to read file
- Impact: Cannot load configuration or data
- Recovery: Check file permissions or run as appropriate user

**FS-004: File Write Permission Denied**
- Trigger: Insufficient permissions to write file
- Impact: Cannot save changes or create new files
- Recovery: Check directory permissions or run as appropriate user

**FS-005: Invalid JSON Syntax**
- Trigger: JSON file contains syntax errors
- Impact: Cannot parse configuration or data
- Recovery: Fix JSON syntax errors at specified line/column

**FS-006: Invalid File Format**
- Trigger: File exists but has unexpected format
- Impact: Cannot parse or process file contents
- Recovery: Regenerate file or fix format issues

**FS-007: File System Full**
- Trigger: No space available to write files
- Impact: Cannot save changes
- Recovery: Free disk space or use different location

**FS-008: Path Too Long**
- Trigger: File path exceeds OS limits
- Impact: Cannot create or access file
- Recovery: Use shorter paths or reorganize directory structure

### Category 3: Data Validation Errors (DATA-XXX)

Errors related to data integrity and validation.

**DATA-001: Missing Required Field**
- Trigger: JSON object missing required property
- Impact: Cannot process incomplete data
- Recovery: Add missing field with valid value

**DATA-002: Invalid Field Type**
- Trigger: Field has wrong data type (e.g., string instead of number)
- Impact: Data processing will fail or produce incorrect results
- Recovery: Correct field to expected type

**DATA-003: Field Value Out of Range**
- Trigger: Numeric value exceeds allowed range
- Impact: May cause overflow or invalid state
- Recovery: Use value within allowed range

**DATA-004: Invalid Format**
- Trigger: Data doesn't match expected format (e.g., date, email, ID)
- Impact: Validation fails, processing cannot continue
- Recovery: Correct data to match expected format

**DATA-005: Referential Integrity Violation**
- Trigger: Reference to non-existent entity (e.g., feature ID not in log)
- Impact: Cannot resolve dependency
- Recovery: Create referenced entity or fix reference

**DATA-006: Duplicate Entry**
- Trigger: Attempting to create entity that already exists
- Impact: May overwrite data or cause conflicts
- Recovery: Use existing entity or choose unique identifier

**DATA-007: Schema Validation Failed**
- Trigger: Data structure doesn't match expected schema
- Impact: Cannot safely process data
- Recovery: Update data to match schema or migrate schema

**DATA-008: Empty or Null Value**
- Trigger: Required field is null or empty string
- Impact: Cannot proceed with missing data
- Recovery: Provide valid value for required field

### Category 4: Git Operation Errors (GIT-XXX)

Errors specific to git operations.

**GIT-001: No Changes to Commit**
- Trigger: Working directory is clean, nothing to commit
- Impact: Commit command has nothing to do
- Recovery: Make changes before committing

**GIT-002: Merge Conflict Detected**
- Trigger: Git merge resulted in conflicts
- Impact: Cannot complete merge automatically
- Recovery: Resolve conflicts manually and complete merge

**GIT-003: Branch Already Exists**
- Trigger: Attempting to create branch that already exists
- Impact: Cannot create duplicate branch
- Recovery: Checkout existing branch or choose different name

**GIT-004: Branch Does Not Exist**
- Trigger: Reference to non-existent branch
- Impact: Cannot checkout or reference branch
- Recovery: Create branch or fix branch name

**GIT-005: Push Rejected**
- Trigger: Remote rejected push (e.g., behind remote, force push protection)
- Impact: Local commits not synchronized to remote
- Recovery: Pull latest changes, resolve conflicts, or use force push if appropriate

**GIT-006: Pull Failed**
- Trigger: Cannot pull from remote (conflicts, network, etc.)
- Impact: Local repository out of sync with remote
- Recovery: Resolve conflicts or check network connection

**GIT-007: Uncommitted Changes Blocking Operation**
- Trigger: Git operation requires clean working directory
- Impact: Cannot proceed with uncommitted changes
- Recovery: Commit or stash changes before operation

**GIT-008: Invalid Commit Message**
- Trigger: Commit message fails validation (empty, wrong format)
- Impact: Cannot create commit
- Recovery: Provide valid commit message

### Category 5: Dependency Errors (DEP-XXX)

Errors related to missing or invalid dependencies between operations.

**DEP-001: Prerequisite Command Not Run**
- Trigger: Required command must be executed first
- Impact: Missing data or configuration needed by current command
- Recovery: Run prerequisite command then retry

**DEP-002: Feature Not Found**
- Trigger: Referenced feature ID does not exist in feature log
- Impact: Cannot implement, summarize, or reference feature
- Recovery: Create feature or verify feature ID

**DEP-003: User Stories Not Created**
- Trigger: Feature exists but user stories not generated
- Impact: Cannot implement without user stories
- Recovery: Run feature planning to generate user stories

**DEP-004: Implementation Not Complete**
- Trigger: Attempting operation that requires completed implementation
- Impact: Operation may fail or produce incomplete results
- Recovery: Complete implementation first

**DEP-005: Circular Dependency Detected**
- Trigger: Story dependencies form a cycle
- Impact: Cannot determine valid execution order
- Recovery: Break circular dependency in story definitions

**DEP-006: Missing Agent Definition**
- Trigger: Story references agent that doesn't exist
- Impact: Cannot execute story without agent
- Recovery: Create agent definition or use different agent

**DEP-007: State Transition Invalid**
- Trigger: Attempting to transition to invalid state
- Impact: Feature state becomes inconsistent
- Recovery: Transition through valid intermediate states

**DEP-008: Resource Locked**
- Trigger: Another process has locked required resource
- Impact: Cannot proceed until lock is released
- Recovery: Wait for lock release or terminate blocking process

### Category 6: External Service Errors (EXT-XXX)

Errors from external services and APIs.

**EXT-001: GitHub API Rate Limit Exceeded**
- Trigger: Too many GitHub API requests in time window
- Impact: Cannot fetch issues or create PRs temporarily
- Recovery: Wait for rate limit reset or use authenticated requests

**EXT-002: GitHub API Authentication Failed**
- Trigger: GitHub API credentials invalid or expired
- Impact: Cannot access private repositories or authenticated endpoints
- Recovery: Re-authenticate with GitHub CLI

**EXT-003: GitHub Issue Not Found**
- Trigger: Referenced issue number doesn't exist
- Impact: Cannot process non-existent issue
- Recovery: Verify issue number or create issue

**EXT-004: GitHub Network Error**
- Trigger: Cannot connect to GitHub servers
- Impact: All GitHub operations will fail
- Recovery: Check network connection or wait for service restoration

**EXT-005: External Command Failed**
- Trigger: System command returned non-zero exit code
- Impact: Operation dependent on command cannot proceed
- Recovery: Check command output and fix underlying issue

**EXT-006: Service Unavailable**
- Trigger: External service is down or unreachable
- Impact: Operations requiring service will fail
- Recovery: Wait for service restoration or use alternative

**EXT-007: Timeout Exceeded**
- Trigger: Operation took longer than allowed timeout
- Impact: Operation aborted, may be incomplete
- Recovery: Retry with longer timeout or investigate performance issue

**EXT-008: API Response Invalid**
- Trigger: External API returned unexpected or malformed response
- Impact: Cannot parse or process response
- Recovery: Retry request or report API issue

### Category 7: User Input Errors (INPUT-XXX)

Errors from invalid user input or arguments.

**INPUT-001: Missing Required Argument**
- Trigger: Required command argument not provided
- Impact: Command cannot execute without argument
- Recovery: Provide required argument and retry

**INPUT-002: Invalid Argument Value**
- Trigger: Argument has invalid value or format
- Impact: Command will fail or produce unexpected results
- Recovery: Provide valid argument value

**INPUT-003: Conflicting Arguments**
- Trigger: Multiple arguments conflict with each other
- Impact: Ambiguous command intent
- Recovery: Use only compatible arguments

**INPUT-004: Argument Out of Range**
- Trigger: Numeric argument outside allowed range
- Impact: Operation will fail or produce invalid results
- Recovery: Use value within allowed range

**INPUT-005: Invalid Command Syntax**
- Trigger: Command used with incorrect syntax
- Impact: Parser cannot understand command
- Recovery: Check command documentation and use correct syntax

**INPUT-006: Unknown Flag or Option**
- Trigger: Unrecognized flag or option provided
- Impact: Command may ignore flag or fail
- Recovery: Remove unknown flag or check documentation

**INPUT-007: Message Too Short**
- Trigger: Required text input is too short (e.g., commit message)
- Impact: Input doesn't meet minimum requirements
- Recovery: Provide longer, more descriptive input

**INPUT-008: Message Too Long**
- Trigger: Input exceeds maximum allowed length
- Impact: May be truncated or rejected
- Recovery: Shorten input to within limits

### Category 8: State Consistency Errors (STATE-XXX)

Errors related to inconsistent or invalid system state.

**STATE-001: Feature Already Exists**
- Trigger: Attempting to create feature with duplicate ID
- Impact: Cannot create duplicate, may overwrite existing
- Recovery: Use existing feature or choose different ID

**STATE-002: Feature Already Implemented**
- Trigger: Attempting to re-implement completed feature
- Impact: May duplicate work or overwrite implementation
- Recovery: Check feature status or intentionally re-implement

**STATE-003: Feature Already Summarized**
- Trigger: Attempting to re-summarize already summarized feature
- Impact: May overwrite existing summary
- Recovery: Skip feature or force re-summarization

**STATE-004: Invalid State Transition**
- Trigger: Attempting invalid state change (e.g., planned → archived)
- Impact: State becomes inconsistent with lifecycle
- Recovery: Transition through valid intermediate states

**STATE-005: Inconsistent State Data**
- Trigger: State fields contradict each other
- Impact: Cannot determine actual state
- Recovery: Manually fix state data to be consistent

**STATE-006: Missing State History**
- Trigger: Feature missing stateHistory array
- Impact: Cannot track state transitions
- Recovery: Initialize stateHistory with current state

**STATE-007: State History Corruption**
- Trigger: State history has invalid or out-of-order entries
- Impact: Cannot reliably determine state timeline
- Recovery: Rebuild state history from timestamps

**STATE-008: Concurrent Modification Detected**
- Trigger: File modified externally during operation
- Impact: May overwrite external changes
- Recovery: Retry operation or merge changes manually

## Error Message Format

All errors must follow this standardized format for consistency:

```
ERROR: {Error Title}

Code: {ERROR-CODE}
Category: {Error Category}
Command: /{command-name}

Details:
{Detailed explanation of what went wrong and why}

Context:
{Relevant context about what was being attempted}
- Attempted operation: {operation description}
- Target: {file path, feature ID, etc.}
- Current state: {relevant state information}

Impact:
{What functionality is affected by this error}

Recovery Steps:
1. {First recovery step with specific command or action}
2. {Second recovery step if needed}
3. {Third recovery step if needed}

{If helpful: Example showing correct usage}

For more information, see: {link to documentation if applicable}
```

### Compact Error Format (for warnings)

For non-critical warnings that don't stop execution:

```
WARNING: {Warning Title}

Code: {WARNING-CODE}
Context: {What triggered the warning}
Impact: {What this might affect}

Recommendation:
{Suggested action to resolve warning}

{Execution will continue with warning acknowledged}
```

## Error Handling Workflow

Every command must implement error handling using this standard workflow:

### Step 1: Error Context Setup

At the beginning of each command, establish error context:

```markdown
## Error Context

Command: /{command-name}
Version: {command version if applicable}
Working Directory: {pwd}
Timestamp: {ISO 8601 timestamp}

This context is used in all error messages for debugging.
```

### Step 2: Try-Catch Wrapper

Wrap each major command section in conceptual try-catch logic:

```markdown
### Step X: {Operation Name}

**Error Handling Wrapper Start**

Attempt:
1. {Operation step 1}
2. {Operation step 2}
3. {Operation step 3}

On Success:
- Proceed to next step
- Log success if verbose mode

On Failure:
- Identify error type and category
- Generate structured error message
- Execute recovery suggestions if possible
- Log error details
- Decide: STOP execution or CONTINUE with degraded functionality
```

### Step 3: Error Detection

For each operation that can fail, explicitly check for errors:

```markdown
Check for errors:
- If {error condition 1}: Trigger {ERROR-CODE-1}
- If {error condition 2}: Trigger {ERROR-CODE-2}
- If {error condition 3}: Trigger {ERROR-CODE-3}

For each error:
1. Capture error details (exit code, error output, exception message)
2. Identify matching error code from this system
3. Generate error message using standard format
4. Determine if error is recoverable
```

### Step 4: Error Classification

Classify each detected error:

```markdown
Error Classification:
- **Critical**: Must stop execution immediately (data corruption risk)
- **Blocking**: Cannot proceed, but safe to stop (missing dependency)
- **Degraded**: Can continue with reduced functionality (warning)
- **Informational**: User should know, but not an error (empty result set)
```

### Step 5: Recovery Attempt

For recoverable errors, attempt automatic recovery:

```markdown
Recovery Attempt:
If error is {ERROR-CODE} and recoverable:
1. Attempt recovery action 1
2. If successful: Log recovery and continue
3. If failed: Try recovery action 2
4. If all recovery attempts fail: Display error and stop

Recovery actions by error type:
- FS-002 (Directory Not Found): Create directory automatically
- DATA-001 (Missing Field): Use default value if safe
- GIT-007 (Uncommitted Changes): Offer to commit or stash
```

### Step 6: Error Reporting

Display error to user with full context:

```markdown
Error Reporting:
1. Display error message using standard format
2. Include error code for reference
3. Provide specific recovery steps
4. Log error to error log if logging enabled
5. Update command execution status to "failed"
```

### Step 7: Graceful Shutdown

Ensure clean state even on error:

```markdown
Graceful Shutdown on Error:
1. Save any partial progress if safe
2. Release any locked resources
3. Restore state if transaction was started
4. Clean up temporary files
5. Log error details for debugging
6. Exit with appropriate status code
```

## Error Logging

All errors should be logged for debugging and metrics:

### Log Entry Format

```json
{
  "timestamp": "2025-10-19T14:35:22Z",
  "level": "ERROR",
  "errorCode": "FS-005",
  "category": "File System Errors",
  "command": "/implement",
  "message": "Invalid JSON Syntax",
  "details": {
    "file": "docs/features/feature-log.json",
    "line": 15,
    "column": 3,
    "jsonError": "Unexpected token '}'"
  },
  "context": {
    "operation": "Read feature log",
    "workingDirectory": "/home/ed/Dev/architecture",
    "user": "ed",
    "attemptedAction": "Parse feature log JSON"
  },
  "recovery": {
    "attempted": true,
    "actions": ["Validate JSON syntax"],
    "successful": false
  },
  "impact": "Command execution stopped",
  "resolutionStatus": "unresolved"
}
```

### Log Location

Error logs are written to `.claude/logs/error-log.json` (if logging is enabled).

Create log directory if it doesn't exist. Append new errors to existing log file.

## Common Error Scenarios and Handling

### Scenario 1: Missing Feature Log

**Context**: User runs `/implement feature 5` but feature-log.json doesn't exist.

**Error Code**: FS-001 (Required File Not Found)

**Error Message**:
```
ERROR: Feature log not found

Code: FS-001
Category: File System Errors
Command: /implement

Details:
Cannot find feature log at expected location. This file tracks all features
and their implementation status.

Context:
- Attempted operation: Read feature log for feature #5
- Target: docs/features/feature-log.json
- Current state: File does not exist

Impact:
Cannot proceed with implementation without feature log. Feature metadata
and dependencies cannot be resolved.

Recovery Steps:
1. Run /feature command to create your first feature:
   /feature "Your feature description"

2. This will automatically create feature-log.json

3. Then run /implement again:
   /implement feature 5

For more information, see: .claude/helpers/pre-flight-validation.md
```

**Action**: STOP execution

### Scenario 2: Invalid JSON in Implementation Log

**Context**: User runs `/summarise` but one feature's implementation log has syntax error.

**Error Code**: FS-005 (Invalid JSON Syntax)

**Error Message**:
```
WARNING: Invalid JSON in implementation log

Code: FS-005 (non-critical)
Context: Processing Feature #3 for summarization

Details:
Implementation log contains JSON syntax error at line 45, column 12.
Error: Unexpected token '}'

File: docs/features/3/implementation-log.json

Impact:
Feature #3 will be skipped during summarization. Other features will
continue to be processed normally.

Recommendation:
1. Validate JSON syntax:
   python3 -m json.tool docs/features/3/implementation-log.json

2. Fix the syntax error at line 45

3. Run /summarise again to include Feature #3

Execution will continue, skipping Feature #3.
```

**Action**: CONTINUE (skip feature, process others)

### Scenario 3: GitHub API Rate Limit

**Context**: User runs `/fix` but GitHub API rate limit is exceeded.

**Error Code**: EXT-001 (GitHub API Rate Limit Exceeded)

**Error Message**:
```
ERROR: GitHub API rate limit exceeded

Code: EXT-001
Category: External Service Errors
Command: /fix

Details:
GitHub API has rate limit of 60 requests/hour for unauthenticated requests
or 5000 requests/hour for authenticated requests. Rate limit has been
exceeded for current authentication level.

Context:
- Attempted operation: Fetch oldest open GitHub issue
- Target: GitHub API endpoint /repos/{owner}/{repo}/issues
- Current state: Rate limit exceeded
- Reset time: 2025-10-19T15:00:00Z (in 23 minutes)

Impact:
Cannot fetch GitHub issues until rate limit resets. All GitHub operations
will fail until reset time.

Recovery Steps:
1. Wait until rate limit resets at 2025-10-19T15:00:00Z

2. If using unauthenticated requests, authenticate for higher limit:
   gh auth login

3. For immediate access, use personal access token with higher limits

4. Retry command after rate limit reset:
   /fix

For more information, see: https://docs.github.com/en/rest/rate-limit
```

**Action**: STOP execution

### Scenario 4: State Transition Validation Failure

**Context**: User manually edited feature-log.json and created invalid state transition.

**Error Code**: STATE-004 (Invalid State Transition)

**Error Message**:
```
ERROR: Invalid state transition attempted

Code: STATE-004
Category: State Consistency Errors
Command: /implement

Details:
Feature #5 cannot transition from "deployed" to "in_progress". This violates
the feature state lifecycle rules.

Context:
- Attempted operation: Update feature state to "in_progress"
- Target: Feature #5 "Architecture System Improvements"
- Current state: deployed
- Requested state: in_progress
- Allowed transitions from "deployed": summarised, archived

Impact:
Cannot start implementation for feature that is already deployed. This
would create inconsistent state and potentially overwrite production code.

Recovery Steps:
1. If you want to re-implement this feature, first transition to valid state:
   - Read state transition system docs: .claude/helpers/state-transition-system.md
   - Use manual override if needed: .claude/helpers/manual-state-override.md

2. Or create a new feature for additional work:
   /feature "Enhancement to {existing feature}"

3. Or create a bug fix for the deployed feature:
   /fix (if GitHub issue exists)

Valid state transitions from "deployed":
- deployed → summarised (via /summarise command)
- deployed → archived (manual state override only)

For more information, see: .claude/helpers/state-validation.md
```

**Action**: STOP execution

## Integration with Pre-Flight Validation

This error handling system wraps around and extends the existing pre-flight validation system:

### Pre-Flight Validation Integration

Pre-flight validation (Step 0 in all commands) performs upfront checks. This error handling system provides:

1. **Structured error codes** for all validation failures
2. **Consistent error message format** across all validations
3. **Recovery suggestions** for common validation failures
4. **Error logging** for validation failures
5. **Graceful degradation** for non-critical validation warnings

### Error Handling Layers

```
Layer 1: Pre-Flight Validation
  └─ Validates environment, files, dependencies
  └─ Uses error codes ENV-XXX, FS-XXX, DATA-XXX, DEP-XXX
  └─ Fails fast before any operations

Layer 2: Operation Error Handling
  └─ Wraps each command operation (git, file I/O, API calls)
  └─ Uses error codes GIT-XXX, FS-XXX, EXT-XXX
  └─ Attempts recovery where possible

Layer 3: State Consistency Validation
  └─ Validates state transitions and data consistency
  └─ Uses error codes STATE-XXX, DATA-XXX
  └─ Ensures system integrity

Layer 4: User Input Validation
  └─ Validates all user-provided arguments and data
  └─ Uses error codes INPUT-XXX
  └─ Provides helpful usage examples
```

## Command-Specific Error Handling

### /commit Command Errors

**Common Errors**:
- ENV-001: Git repository not found
- ENV-003: Detached HEAD state
- GIT-001: No changes to commit
- INPUT-001: Missing commit message
- GIT-005: Push rejected by remote
- GIT-008: Invalid commit message format

**Recovery Priority**:
1. Environment setup errors (ENV-XXX) - highest priority
2. Git state errors (GIT-XXX)
3. Input validation errors (INPUT-XXX)

### /feature Command Errors

**Common Errors**:
- ENV-001: Git repository not found
- FS-002: Agents directory not found
- FS-005: Invalid JSON in feature-log.json
- DEP-006: Missing agent definitions
- STATE-001: Feature already exists

**Recovery Priority**:
1. Environment and file system (ENV-XXX, FS-XXX)
2. Dependency validation (DEP-XXX)
3. State consistency (STATE-XXX)

### /implement Command Errors

**Common Errors**:
- FS-001: User stories file not found
- FS-005: Invalid JSON in feature-log or implementation-log
- DEP-002: Feature not found in feature log
- DEP-003: User stories not created
- STATE-004: Invalid state transition
- INPUT-002: Invalid feature/bug ID format

**Recovery Priority**:
1. File existence and format (FS-XXX)
2. Data dependencies (DEP-XXX, DATA-XXX)
3. State validation (STATE-XXX)

### /fix Command Errors

**Common Errors**:
- ENV-004: GitHub CLI not installed
- ENV-005: GitHub CLI not authenticated
- ENV-006: GitHub repository not connected
- EXT-001: GitHub API rate limit exceeded
- EXT-003: GitHub issue not found
- EXT-004: GitHub network error

**Recovery Priority**:
1. GitHub CLI setup (ENV-004, ENV-005)
2. GitHub connectivity (ENV-006, EXT-004)
3. GitHub API limits (EXT-001)
4. Issue validation (EXT-003)

### /summarise Command Errors

**Common Errors**:
- FS-001: Feature log not found
- FS-005: Invalid JSON in implementation logs
- STATE-003: Feature already summarized
- STATE-004: Invalid state transition
- DATA-005: Feature references don't exist

**Recovery Priority**:
1. Feature log validation (FS-XXX)
2. State validation (STATE-XXX)
3. Data integrity (DATA-XXX)

### /dashboard Command Errors

**Common Errors**:
- FS-001: Feature log not found
- FS-005: Invalid JSON in feature log
- INPUT-002: Invalid state filter value
- DATA-001: Missing required state fields

**Recovery Priority**:
1. Feature log validation (FS-XXX)
2. Input validation (INPUT-XXX)
3. Data validation (DATA-XXX) - non-critical, use defaults

### /metrics Command Errors

**Common Errors**:
- FS-001: Feature log or implementation logs not found
- FS-005: Invalid JSON in logs
- DATA-001: Missing required fields in story data
- DATA-004: Invalid timestamp format
- FS-004: Cannot write metrics cache

**Recovery Priority**:
1. Log file validation (FS-XXX)
2. Data validation (DATA-XXX) - skip invalid stories
3. Cache write errors (FS-004) - warning only, continue

## Error Recovery Strategies

### Automatic Recovery

Some errors can be automatically recovered:

**FS-002: Directory Not Found**
- Recovery: Create directory using `mkdir -p {path}`
- Safe: Yes, if directory is for writing new files
- Example: Creating `docs/metrics/` directory

**DATA-001: Missing Field with Default Value**
- Recovery: Use default value from schema
- Safe: Yes, if field has documented default
- Example: `isSummarised: false` if missing

**GIT-007: Uncommitted Changes** (warning only)
- Recovery: Display warning, allow user to decide
- Safe: Yes, user makes decision
- Example: Running /feature with uncommitted changes

### Manual Recovery Required

Some errors require user intervention:

**FS-005: Invalid JSON Syntax**
- Recovery: User must fix JSON manually
- Why: Cannot auto-fix without risking data loss
- Guidance: Provide line number and specific error

**STATE-004: Invalid State Transition**
- Recovery: User must use valid transition path
- Why: State machine rules enforce consistency
- Guidance: Show valid transitions from current state

**EXT-001: GitHub API Rate Limit**
- Recovery: User must wait or authenticate
- Why: External service limitation
- Guidance: Show reset time and authentication options

### Graceful Degradation

Some errors allow continuing with reduced functionality:

**Multiple Features with One Invalid** (in /summarise)
- Strategy: Skip invalid feature, process others
- Report: Warning for skipped feature
- Result: Partial success better than total failure

**Missing Context Files** (in /implement)
- Strategy: Warn but continue implementation
- Report: Note which context files are missing
- Result: Story executes without optimal context

**Cache Write Failure** (in /metrics)
- Strategy: Generate metrics but don't cache
- Report: Warning about re-calculation on next run
- Result: Metrics still displayed, just slower next time

## Testing Error Handling

### Error Injection for Testing

To test error handling, create these test scenarios:

**Test ENV-001: Missing Git Repository**
```bash
cd /tmp/not-a-git-repo
/implement feature 5
# Expected: ENV-001 error with recovery steps
```

**Test FS-005: Invalid JSON**
```bash
echo "invalid json {]}" > docs/features/feature-log.json
/feature "Test feature"
# Expected: FS-005 error with syntax details
```

**Test GIT-001: No Changes to Commit**
```bash
# Ensure working directory is clean
git add .
git commit -m "Clean state"
/commit "Test message"
# Expected: GIT-001 error
```

**Test DEP-002: Feature Not Found**
```bash
/implement feature 999
# Expected: DEP-002 error with feature creation guidance
```

**Test STATE-004: Invalid State Transition**
```bash
# Manually edit feature-log.json to set state to "deployed"
/implement feature 5
# Expected: STATE-004 error with valid transitions
```

### Error Handling Test Checklist

For each command, verify:
- [ ] All error codes are documented
- [ ] Error messages follow standard format
- [ ] Recovery steps are specific and actionable
- [ ] Critical errors stop execution safely
- [ ] Warnings allow continuation with acknowledgment
- [ ] Partial failures are handled gracefully
- [ ] State is not corrupted on error
- [ ] Error context includes relevant details

## Best Practices

### For Command Developers

1. **Fail Fast**: Check for errors at the earliest possible point
2. **Be Specific**: Use specific error codes, not generic errors
3. **Provide Context**: Include file paths, line numbers, command output
4. **Suggest Solutions**: Always provide recovery steps
5. **Preserve State**: Never leave system in invalid state
6. **Log Everything**: Log all errors for debugging
7. **Test Errors**: Test error paths as thoroughly as success paths
8. **Document Errors**: Document all possible errors for command

### For Users

1. **Read Error Messages**: Full error message contains important context
2. **Note Error Codes**: Error code helps find documentation
3. **Follow Recovery Steps**: Steps are ordered by likelihood of success
4. **Check Prerequisites**: Many errors are missing prerequisites
5. **Verify State**: Check feature state and git status before operations
6. **Report Bugs**: If error message is unclear, report for improvement

## Error Code Quick Reference

| Code | Category | Severity | Description |
|------|----------|----------|-------------|
| ENV-001 | Environment | Critical | Git repository not found |
| ENV-002 | Environment | Critical | Not a git repository |
| ENV-003 | Environment | Blocking | Detached HEAD state |
| ENV-004 | Environment | Critical | GitHub CLI not installed |
| ENV-005 | Environment | Blocking | GitHub CLI not authenticated |
| ENV-006 | Environment | Blocking | GitHub repository not connected |
| ENV-007 | Environment | Critical | Python not available |
| FS-001 | File System | Blocking | Required file not found |
| FS-002 | File System | Recoverable | Required directory not found |
| FS-003 | File System | Blocking | File read permission denied |
| FS-004 | File System | Warning | File write permission denied |
| FS-005 | File System | Blocking | Invalid JSON syntax |
| FS-006 | File System | Blocking | Invalid file format |
| FS-007 | File System | Critical | File system full |
| FS-008 | File System | Blocking | Path too long |
| DATA-001 | Data Validation | Blocking | Missing required field |
| DATA-002 | Data Validation | Blocking | Invalid field type |
| DATA-003 | Data Validation | Blocking | Field value out of range |
| DATA-004 | Data Validation | Blocking | Invalid format |
| DATA-005 | Data Validation | Blocking | Referential integrity violation |
| DATA-006 | Data Validation | Warning | Duplicate entry |
| DATA-007 | Data Validation | Blocking | Schema validation failed |
| DATA-008 | Data Validation | Blocking | Empty or null value |
| GIT-001 | Git Operations | Informational | No changes to commit |
| GIT-002 | Git Operations | Blocking | Merge conflict detected |
| GIT-003 | Git Operations | Warning | Branch already exists |
| GIT-004 | Git Operations | Blocking | Branch does not exist |
| GIT-005 | Git Operations | Blocking | Push rejected |
| GIT-006 | Git Operations | Blocking | Pull failed |
| GIT-007 | Git Operations | Warning | Uncommitted changes blocking operation |
| GIT-008 | Git Operations | Blocking | Invalid commit message |
| DEP-001 | Dependencies | Blocking | Prerequisite command not run |
| DEP-002 | Dependencies | Blocking | Feature not found |
| DEP-003 | Dependencies | Blocking | User stories not created |
| DEP-004 | Dependencies | Blocking | Implementation not complete |
| DEP-005 | Dependencies | Critical | Circular dependency detected |
| DEP-006 | Dependencies | Blocking | Missing agent definition |
| DEP-007 | Dependencies | Blocking | State transition invalid |
| DEP-008 | Dependencies | Warning | Resource locked |
| EXT-001 | External Services | Blocking | GitHub API rate limit exceeded |
| EXT-002 | External Services | Blocking | GitHub API authentication failed |
| EXT-003 | External Services | Blocking | GitHub issue not found |
| EXT-004 | External Services | Blocking | GitHub network error |
| EXT-005 | External Services | Blocking | External command failed |
| EXT-006 | External Services | Blocking | Service unavailable |
| EXT-007 | External Services | Warning | Timeout exceeded |
| EXT-008 | External Services | Warning | API response invalid |
| INPUT-001 | User Input | Blocking | Missing required argument |
| INPUT-002 | User Input | Blocking | Invalid argument value |
| INPUT-003 | User Input | Blocking | Conflicting arguments |
| INPUT-004 | User Input | Blocking | Argument out of range |
| INPUT-005 | User Input | Blocking | Invalid command syntax |
| INPUT-006 | User Input | Warning | Unknown flag or option |
| INPUT-007 | User Input | Blocking | Message too short |
| INPUT-008 | User Input | Warning | Message too long |
| STATE-001 | State Consistency | Warning | Feature already exists |
| STATE-002 | State Consistency | Warning | Feature already implemented |
| STATE-003 | State Consistency | Warning | Feature already summarized |
| STATE-004 | State Consistency | Blocking | Invalid state transition |
| STATE-005 | State Consistency | Critical | Inconsistent state data |
| STATE-006 | State Consistency | Warning | Missing state history |
| STATE-007 | State Consistency | Critical | State history corruption |
| STATE-008 | State Consistency | Warning | Concurrent modification detected |

## Severity Levels

- **Critical**: System integrity at risk, immediate stop required
- **Blocking**: Cannot proceed, must be fixed before retrying
- **Warning**: Can continue but with potential issues
- **Informational**: No error, just information for user
- **Recoverable**: Can be automatically fixed

## Version History

- v1.0.0 (2025-10-19): Initial error handling system
  - 8 error categories with 64 error codes
  - Standardized error message format
  - Error logging support
  - Integration with pre-flight validation
  - Recovery strategies for common errors
