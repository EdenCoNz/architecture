# Command Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Command Concept and Purpose](#command-concept-and-purpose)
3. [Command Structure and File Format](#command-structure-and-file-format)
4. [Command Definition Template](#command-definition-template)
5. [Workflow Patterns](#workflow-patterns)
6. [Error Handling Best Practices](#error-handling-best-practices)
7. [Integration with Helpers](#integration-with-helpers)
8. [Complete Examples](#complete-examples)
9. [Testing and Validation Strategies](#testing-and-validation-strategies)
10. [Best Practices and Anti-Patterns](#best-practices-and-anti-patterns)

---

## Introduction

Slash commands are the primary interface for automating complex development workflows in the architecture system. They orchestrate agents, manage state, validate prerequisites, and provide structured error handling. This guide provides comprehensive instructions for creating new slash commands that integrate seamlessly with the existing system.

**What are Slash Commands?**

Slash commands are markdown files in `.claude/commands/` that define automated workflows. When invoked (e.g., `/feature`, `/implement`), they expand into detailed instructions that guide the AI agent through a multi-step process with validation, error handling, and state management.

**Key Characteristics:**

- **Declarative**: Define what should happen, not how
- **Validated**: Comprehensive pre-flight checks before execution
- **Resilient**: Structured error handling with recovery suggestions
- **Stateful**: Track progress and enable resume capabilities
- **Composable**: Can invoke other commands and agents

---

## Command Concept and Purpose

### What Commands Should Do

Commands should automate **repeatable, multi-step workflows** that:

1. **Require validation** before execution (checking prerequisites)
2. **Modify system state** (feature logs, implementation logs, files)
3. **Orchestrate multiple operations** (agents, git, file operations)
4. **Need error recovery** (handling failures gracefully)
5. **Track progress** (maintaining state for resume capability)

### What Commands Should NOT Do

Commands should not be created for:

- **Single operations** (use agents directly instead)
- **Simple questions** (ask the AI directly)
- **One-off tasks** (not worth the overhead)
- **Application code** (commands are for the architecture system only)

### Command Design Questions

Before creating a command, ask:

1. **Is this workflow repeatable?** If not, use an agent directly
2. **Does it need validation?** If yes, a command is appropriate
3. **Does it modify state?** If yes, add state management
4. **Can it fail partially?** If yes, add checkpointing and resume
5. **Will users run it frequently?** If yes, optimize the UX

---

## Command Structure and File Format

### File Location

All command files must be located in:
```
.claude/commands/{command-name}.md
```

### YAML Frontmatter

Every command file must start with YAML frontmatter containing metadata:

```yaml
---
description: Brief description shown in command list
args:
  - name: arg_name
    description: What this argument is for
    required: true|false
model: claude-sonnet-4-5  # Optional: specific model to use
---
```

### Document Structure

After the frontmatter, commands follow this structure:

```markdown
## Purpose
Clear statement of what this command does and when to use it

## Variables
List of variables available in the command context

## Instructions
High-level instructions for the AI executing the command

## Error Handling
Reference to error handling system and common errors

## Workflow
Detailed step-by-step workflow with validation and execution

## Report
Expected output format and what to report to the user
```

### Sections Explained

**Purpose**: 1-3 sentences explaining what the command does and its use case.

**Variables**: Template variables that can be used throughout the command using `{{{ variable_name }}}` syntax.

**Instructions**: High-level rules and constraints (MUSTs and MUST NOTs).

**Error Handling**: Reference to `.claude/helpers/command-error-handling.md` and list of common errors with codes.

**Workflow**: The core of the command - detailed steps with substeps, validation checks, and execution logic.

**Report**: What to tell the user when the command completes (success or failure).

---

## Command Definition Template

Use this template as a starting point for new commands:

```markdown
---
description: Brief description of what this command does
args:
  - name: first_arg
    description: Description of first argument
    required: true
  - name: second_arg
    description: Description of second argument
    required: false
model: claude-sonnet-4-5
---

## Purpose

[1-3 sentences explaining what this command does and when to use it]

## Variables

- `{{{ args.first_arg }}}` - [Description of how this argument is used]
- `{{{ args.second_arg }}}` - [Description of optional argument]
- `$DERIVED_VAR` - [Description of variables computed during execution]

## Instructions

- MUST follow the workflow steps in sequential order
- MUST validate all prerequisites before execution
- MUST handle all errors using the error handling system
- MUST NOT skip validation steps
- MUST NOT proceed if critical validations fail

## Error Handling

This command uses comprehensive error handling with specific error codes and recovery suggestions.

**Error Handling Reference**: See `.claude/helpers/command-error-handling.md` for complete error code documentation and `.claude/helpers/error-code-mapping.md` for validation error mapping.

**Common Errors**:
- ENV-001: Git repository not found → Initialize git or navigate to repository
- FS-001: Required file not found → Run prerequisite command
- [Add command-specific errors]

**Error Handling Strategy**:
- All validation errors (Step 0) use standardized error codes
- [Describe which errors are blocking vs warnings]
- [Describe error recovery approach]

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
- Display error message with code ENV-001
- STOP execution immediately

[Add more validation steps as needed]

#### Step 0.X: Validation Summary

If all validations pass:
- Output: "Pre-flight validation passed - proceeding with [command name]"
- Proceed to Step 1

If any critical validation failed:
- Execution has already been stopped
- User must remediate issues and re-run command

### Step 1: [First Main Operation]

[Detailed instructions for first operation]

1. [Sub-step]
2. [Sub-step]
3. [Error handling for this step]

### Step 2: [Second Main Operation]

[Continue with workflow steps]

### Step N: Report

Provide a comprehensive summary that includes:
- [What was accomplished]
- [What files were modified]
- [Next steps for the user]
- [Any warnings or issues encountered]

## Report

Provide a summary that includes:
- [Key information about execution]
- [Files created or modified]
- [Status of operations]
- [Next steps or recommendations]
```

---

## Workflow Patterns

### Pattern 1: Sequential Execution

**When to Use**: Steps must execute in order, each depending on the previous step's completion.

**Implementation**:

```markdown
### Step 1: First Operation
Execute first task and capture output.

### Step 2: Use Output from Step 1
Use the output from Step 1 to perform second task.

### Step 3: Final Operation
Complete the workflow using results from previous steps.
```

**Example from /commit Command**:

```markdown
### Step 1: Stage all changes
Use the Bash tool to run `git add .` to stage all changes.

### Step 2: Create the commit
Use the Bash tool to run `git commit -m "{{{ args.message }}}"`.

### Step 3: Push to remote (conditional)
Check if `{{{ args.push }}}` is set to "push":
- If yes, run `git push`
- If no, skip this step

### Step 4: Verify the result
Run `git status` to confirm commit was created successfully.
```

### Pattern 2: Parallel Execution

**When to Use**: Multiple independent operations that can run simultaneously.

**Implementation**:

```markdown
### Step 1: Execute Multiple Operations in Parallel

Launch multiple operations simultaneously:

1. **Identify all independent operations** in this phase
2. **For parallel execution**:
   - Use multiple Task tool calls in a single message
   - Launch all agents simultaneously
   - Wait for all to complete before proceeding

Example:
```
For Phase 2 (Parallel) with stories 4, 5, 6:
- Launch backend-developer for Story #4
- Launch frontend-developer for Story #5
- Launch devops-engineer for Story #6
All launched in one message using multiple Task tool calls.
```
```

**Example from /implement Command**:

The `/implement` command uses parallel execution for stories in parallel phases:

```markdown
For parallel phases:
- Launch multiple pending agents simultaneously using the Task tool
- Use multiple Task tool calls in a single message
```

### Pattern 3: Conditional Execution

**When to Use**: Some steps should only run under certain conditions.

**Implementation**:

```markdown
### Step X: Conditional Operation

Check condition:
- If condition is true:
  - Execute operation A
  - Continue to next step
- If condition is false:
  - Skip operation A
  - Log why it was skipped
  - Continue to next step

### Step Y: Always Execute
This step runs regardless of condition in Step X.
```

**Example from /commit Command**:

```markdown
### Step 3: Push to remote (conditional)

Check if `{{{ args.push }}}` is set to "push":
- If yes, run `git push` to push the committed changes
- If no or empty, skip this step
```

### Pattern 4: State Management with Resume

**When to Use**: Long-running operations that may be interrupted and need to resume.

**Implementation**:

```markdown
### Step 1: Check for Existing Progress

1. Check if progress log exists at `{log_path}`
2. If it exists:
   - Read and parse the log
   - Extract all completed items
   - Store the list for later use
3. If it doesn't exist:
   - Proceed with no items marked as completed

### Step 2: Execute Operations with Resume Awareness

For each operation:
1. **Check if already completed**:
   - If completed: Skip and log "Skipping already completed: {item}"
   - If pending: Execute the operation
2. **Execute pending operation**:
   - Perform the operation
   - Record result in log immediately
3. **Continue to next operation**
```

**Example from /implement Command**:

```markdown
### Step 2: Check for Existing Implementation Progress

1. Check if implementation-log.json exists at the determined path
2. If it exists:
   - Read and parse the implementation-log.json file
   - Extract all completed story numbers (where status is "completed")
   - Store the list of completed story numbers for later use
3. If it doesn't exist or is empty:
   - Proceed with no stories marked as completed
   - All stories will need to be executed
```

### Pattern 5: Agent Orchestration

**When to Use**: Command needs to launch specialized agents for different tasks.

**Implementation**:

```markdown
### Step X: Launch Specialized Agent

1. **Determine appropriate agent** based on task requirements:
   - For backend work: backend-developer
   - For frontend work: frontend-developer
   - For DevOps work: devops-engineer
   - For design work: ui-ux-designer

2. **Prepare context for agent**:
   - Load relevant context files
   - Prepare instructions
   - Gather required parameters

3. **Launch agent using Task tool**:
   ```
   Use Task tool to launch {agent-name} with these instructions:

   [Detailed instructions for the agent]
   ```

4. **Wait for agent completion**:
   - Capture agent output
   - Extract relevant results
   - Record in progress log
```

**Example from /feature Command**:

```markdown
### Step 1: Launch Product Owner Agent

Use the Task tool to launch the product-owner agent with the following instructions:

First, check what agents are available in .claude/agents/ to understand implementation capabilities.

Then, analyze this feature request and create comprehensive user stories:

{{{ input }}}

You MUST plan the user stories needed for this feature based on available agents.
```

### Pattern 6: Validation with Error Recovery

**When to Use**: All commands - validation should always provide recovery paths.

**Implementation**:

```markdown
#### Step 0.X: Validate [Requirement]

Run validation check:
```bash
[validation command]
```

If validation fails:
- Display error message with error code:
```
ERROR: [Human-readable error title]

Code: [ERROR-CODE]
Category: [Error Category]
Command: /[command-name]

Details:
[What went wrong and why]

Context:
- Attempted operation: [what was being done]
- Expected: [what was expected]
- Actual: [what was found]

Impact:
[What this error prevents]

Recovery Steps:
1. [Specific step to fix]
2. [Alternative approach if applicable]
3. [How to verify fix]

For more information, see: .claude/helpers/command-error-handling.md ([ERROR-CODE])
```
- STOP execution immediately
```

**Example from /commit Command**:

```markdown
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

Recovery Steps:
1. Make changes to files before committing
2. Verify you are in the correct directory: pwd
3. Check git status to see current state
```
- STOP execution immediately
```

---

## Error Handling Best Practices

### Error Code System

All commands must use the standardized error code system defined in `.claude/helpers/command-error-handling.md`.

**Error Code Format**: `CATEGORY-XXX`

**Error Categories**:

- **ENV-XXX**: Environment errors (git, GitHub CLI, dependencies)
- **FS-XXX**: File system errors (missing files, permissions, invalid formats)
- **GIT-XXX**: Git operation errors (no changes, merge conflicts, push failures)
- **INPUT-XXX**: Input validation errors (missing arguments, invalid formats)
- **DEP-XXX**: Dependency errors (missing features, agents, prerequisites)
- **STATE-XXX**: State management errors (invalid transitions, corrupted state)
- **EXT-XXX**: External system errors (GitHub API, network, rate limits)
- **DATA-XXX**: Data integrity errors (corrupted logs, invalid references)

### Error Message Template

Every error message should follow this structure:

```
ERROR: [Human-readable title]

Code: [ERROR-CODE]
Category: [Error Category Name]
Command: /[command-name]

Details:
[Detailed explanation of what went wrong]

Context:
- [Relevant context item 1]
- [Relevant context item 2]

Impact:
[What this error prevents or breaks]

Recovery Steps:
1. [First specific remediation step]
2. [Second remediation step]
3. [Verification step]

For more information, see: .claude/helpers/command-error-handling.md ([ERROR-CODE])
```

### Blocking vs Non-Blocking Errors

**Blocking Errors** (execution MUST stop):
- Missing required files or directories
- Invalid JSON syntax in critical files
- Git repository not found
- Authentication failures
- Invalid state transitions

**Non-Blocking Warnings** (execution MAY continue):
- Uncommitted changes present
- Branch name doesn't follow convention
- Feature already implemented (resume handles this)
- No agents available (user informed)
- Sensitive files detected

**Implementation Pattern**:

```markdown
If [blocking condition]:
- Display error message with error code
- STOP execution immediately

If [warning condition]:
- Display warning message:
```
Warning: [Issue description]

Status: [Current state]
Impact: [What might happen]

Recommendation:
1. [Suggested action]
2. [Alternative]

You may continue, but [action] is recommended.
```
- This is a WARNING - allow execution to continue
```

### Error Handling Strategy Documentation

Every command should document its error handling strategy:

```markdown
## Error Handling

**Error Handling Strategy**:
- All validation errors (Step 0) use standardized error codes
- [Specific error type] errors are BLOCKING - [reason]
- [Specific error type] errors are NON-BLOCKING - [reason]
- [Special handling for specific scenarios]
```

**Example from /fix Command**:

```markdown
**Error Handling Strategy**:
- All validation errors (Step 0) use standardized error codes
- GitHub CLI errors are BLOCKING - must be resolved before proceeding
- GitHub API errors are BLOCKING - cannot fetch issues without API access
- No open issues is INFORMATIONAL - not an error, just no work to do
- Network errors include retry suggestions with backoff
```

---

## Integration with Helpers

Commands integrate with helper files in `.claude/helpers/` for reusable functionality.

### Pre-Flight Validation Helper

**File**: `.claude/helpers/pre-flight-validation.md`

**Purpose**: Standardized validation checks and error messages

**Integration Pattern**:

```markdown
#### Step 0.1: Load Error Handling and Validation Systems

Read error handling system from .claude/helpers/command-error-handling.md to understand error codes, categories, and message formats.

Read validation helper from .claude/helpers/pre-flight-validation.md to understand validation requirements and error message formats.

All validation errors in subsequent steps should include appropriate error codes.
```

### Error Code Mapping Helper

**File**: `.claude/helpers/error-code-mapping.md`

**Purpose**: Maps validation failures to specific error codes

**Integration Pattern**:

```markdown
#### Step 0.1: Load Error Handling and Validation Systems

Read error code mapping from .claude/helpers/error-code-mapping.md to map validation errors to error codes.
```

### State Validation Helper

**File**: `.claude/helpers/state-validation.md`

**Purpose**: Validates state transitions for features

**Integration Pattern**:

```markdown
#### Step X: Update Feature State

- Read the validation helper from .claude/helpers/state-validation.md to understand state transition rules
- Validate transition: [current_state] → [new_state]
- If validation fails, display error and stop execution
- If valid, proceed with state update
```

### Checkpoint System Helper

**File**: `.claude/helpers/checkpoint-system.md`

**Purpose**: Create checkpoints before major operations

**Integration Pattern** (future):

```markdown
#### Step 0: Create Checkpoint Before Operation

Use checkpoint system from .claude/helpers/checkpoint-system.md:
1. Create checkpoint with ID: checkpoint-{timestamp}-{operation}
2. Backup critical files
3. Record git state
4. Continue with operation
```

### Story Templates Helper

**File**: `.claude/helpers/story-templates.md`

**Purpose**: Templates for creating user stories

**Integration Pattern**:

```markdown
### Step X: Create User Stories

Reference story templates from .claude/helpers/story-templates.md for format and structure.
```

---

## Complete Examples

### Example 1: Simple Sequential Command (/commit)

**Use Case**: Stage changes and create git commit with optional push

**Key Features**:
- Sequential execution (stage → commit → push)
- Conditional step (push only if requested)
- Comprehensive validation
- Sensitive file detection (warning)

**Command Structure**:

```markdown
---
description: Stage all changes and create a git commit
args:
  - name: message
    description: The commit message
    required: true
  - name: push
    description: Optional - use "push" to push after committing
    required: false
model: claude-sonnet-4-5
---

## Purpose
Stage all changes and create a git commit with the provided message.
Optionally push changes to remote repository.

## Variables
- `{{{ args.message }}}` - The commit message
- `{{{ args.push }}}` - Optional "push" to push after commit

## Instructions
- MUST stage all changes using `git add .`
- MUST use provided message exactly as given
- MUST follow Git Safety Protocol
- MUST NOT skip hooks or use --no-verify

## Error Handling
References .claude/helpers/command-error-handling.md

Common errors:
- ENV-001: Git repository not found
- GIT-001: No changes to commit
- GIT-008: Invalid commit message

## Workflow

### Step 0: Pre-Flight Validation

#### Step 0.1: Load Validation Systems
[Load error handling and validation helpers]

#### Step 0.2: Validate Git Repository Exists
[Check for .git/ directory]

#### Step 0.3: Validate Working Directory Has Changes
[Check git status --porcelain]

#### Step 0.4: Validate Commit Message Provided
[Check message argument not empty]

#### Step 0.5: Check for Sensitive Files (Warning)
[Detect .env, credentials, etc. - non-blocking]

#### Step 0.6: Validation Summary
[Display summary and proceed or stop]

### Step 1: Stage all changes
Run `git add .`

### Step 2: Create the commit
Run `git commit -m "{{{ args.message }}}"`

### Step 3: Push to remote (conditional)
If `{{{ args.push }}}` equals "push":
- Run `git push`

### Step 4: Verify the result
Run `git status` to confirm success

## Report
- Confirmation that changes were staged
- Confirmation that commit was created
- Whether changes were pushed
- Current git status
```

**Key Lessons**:
- ✅ Clear, simple workflow for straightforward operation
- ✅ Conditional execution based on optional argument
- ✅ Non-blocking warning for sensitive files
- ✅ Verification step at the end

### Example 2: Complex Orchestration Command (/implement)

**Use Case**: Execute user stories by launching appropriate agents in correct order

**Key Features**:
- Resume capability (skip completed stories)
- Parallel and sequential execution modes
- Agent orchestration
- State management (feature log updates)
- Context caching for performance

**Command Structure** (simplified):

```markdown
---
description: Implement feature or bug by executing user stories in order
args:
  - name: type
    description: Type of implementation (feature or bug)
    required: true
  - name: id
    description: Feature or bug ID to implement
    required: true
model: claude-sonnet-4-5
---

## Purpose
Execute user stories for a feature or bug by launching appropriate agents
in the correct order with resume capability.

## Variables
- `$TYPE` - feature or bug
- `$ID` - Feature/bug ID
- Paths derived based on type

## Instructions
- Execute ALL user stories regardless of agent type
- Respect execution order (sequential/parallel phases)
- Skip completed stories (resume capability)
- Record implementation in logs

## Error Handling
[Reference to error handling system]
[List of common errors with codes]

## Workflow

### Step 0: Pre-Flight Validation

#### Step 0.0: Load Error Handling and Validation Systems
[Load helpers]

#### Step 0.1: Determine Paths Based on Type
- If type is "feature": Set paths to docs/features/{id}/
- If type is "bug": Search for bug path and extract feature ID

#### Step 0.2: Validate Git Repository Exists
[Standard validation]

#### Step 0.3: Validate Feature Log Exists
[Check and validate feature-log.json]

#### Step 0.4: Validate User Stories File Exists
[Check user-stories.md at determined path]

#### Step 0.5: Validate Feature Exists in Feature Log
[Ensure feature is registered]

#### Step 0.6: Validate Bug ID Format (For Bugs Only)
[Check github-issue-{number} format]

#### Step 0.7: Validate Git Branch
[Check not detached HEAD, warn if unusual branch]

#### Step 0.8: Check if Feature Already Fully Implemented (Warning)
[Non-blocking warning with resume explanation]

#### Step 0.9: Validate Implementation Log if Exists
[Optional validation of existing progress]

#### Step 0.10: Validation Summary
[Display summary and proceed]

### Step 1: Validate User Stories File
[Redundant check - already done in Step 0.4]

### Step 2: Check for Existing Implementation Progress
- Read implementation-log.json if exists
- Extract completed story numbers
- Store for later filtering

### Step 3: Parse Execution Order
- Read user-stories.md
- Parse execution order section
- Identify phases and execution modes

### Step 4: Execute User Stories
For each phase:
1. Filter stories: completed vs pending
2. Provide resume feedback
3. Load phase context once (performance optimization)
4. Execute pending stories with cached context
5. Record in implementation log
6. Clear cached context after phase

[Details on sequential vs parallel execution]

### Step 5: Update Feature State to "in_progress"
[State management for features]

### Step 6: Verify Completion and Update Feature Log
- Check all stories completed
- Update userStoriesImplemented timestamp
- Update state to "deployed"

### Step 7: Commit Implementation and Push
- Create detailed commit message
- Include "Fixes #{issue}" if bug
- Commit and push

## Report
- Execution mode (fresh/resume)
- Stories completed vs skipped
- Agents launched and status
- Feature log update confirmation
- Commit confirmation
```

**Key Lessons**:
- ✅ Complex path determination based on type argument
- ✅ Resume capability with implementation log tracking
- ✅ Phase-level context caching for performance
- ✅ State management with automatic transitions
- ✅ Agent orchestration with parallel/sequential modes
- ✅ Comprehensive validation with both blocking and non-blocking checks

### Example 3: Agent Coordination Command (/feature)

**Use Case**: Transform feature request into user stories and auto-implement

**Key Features**:
- Agent launch (product-owner)
- Missing agent detection (blocks auto-implementation)
- State management (planned → in_progress → deployed)
- Git branch creation
- Automatic progression to /implement

**Command Structure** (simplified):

```markdown
---
description: Transform a feature request into user stories
---

## Purpose
Transform feature request into user stories and automatically initiate
implementation if all required agents are available.

## Variables
- `{{{ input }}}` - The feature request

## Instructions
- Check available agents before planning
- If missing agents identified, STOP before implementation
- Only auto-implement if NO missing agents

## Error Handling
[Error handling reference]

## Workflow

### Step 0: Pre-Flight Validation

#### Step 0.1: Load Error Handling and Validation Systems
[Standard helper loading]

#### Step 0.2: Validate Git Repository Exists
[Standard git check]

#### Step 0.3: Validate Agents Directory Exists
[Check .claude/agents/ - blocking]

#### Step 0.4: Check for Available Agents (Warning)
[Warn if no agent files - non-blocking]

#### Step 0.5: Validate or Create Feature Log
[Check or create feature-log.json]

#### Step 0.6: Check Working Directory Status (Warning)
[Warn about uncommitted changes - non-blocking]

#### Step 0.7: Validation Summary
[Display summary]

### Step 1: Launch Product Owner Agent
Use Task tool to launch product-owner with feature request.
Product owner checks available agents and plans stories accordingly.

### Step 2: Check for Missing Agents
After product-owner completes:
- Look for "Missing Agents" section in output
- If missing agents found:
  - STOP - do NOT proceed to implementation
  - Report missing agents to user
  - Exit workflow

### Step 3: Create Git Branch and Commit Planning
Only if NO missing agents:
- Extract feature ID from output
- Create branch: feature/{id}-{slug}
- Commit planning files
- Update feature state to "planned"

### Step 4: Auto-Implement
Only if NO missing agents:
- Verify feature log entry
- Launch /implement command automatically
- Do not ask for confirmation

## Report

If missing agents:
- Feature ID created
- List of missing agents
- Implementation NOT initiated

If no missing agents:
- Feature ID created
- Git branch created
- Planning committed
- Implementation initiated
```

**Key Lessons**:
- ✅ Conditional workflow based on agent availability
- ✅ Agent coordination with product-owner
- ✅ Automatic progression to another command (/implement)
- ✅ Git branch management
- ✅ State transitions with validation

---

## Testing and Validation Strategies

### Pre-Deployment Testing

Before deploying a new command, test it thoroughly:

#### 1. Syntax Validation

**YAML Frontmatter Validation**:

```bash
# Extract and validate YAML frontmatter
python3 << 'EOF'
import yaml
with open('.claude/commands/your-command.md', 'r') as f:
    content = f.read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        frontmatter = parts[1]
        try:
            yaml.safe_load(frontmatter)
            print("✓ YAML frontmatter is valid")
        except yaml.YAMLError as e:
            print(f"✗ YAML error: {e}")
EOF
```

**Markdown Validation**:

```bash
# Check for common markdown issues
grep -n "###[^ ]" .claude/commands/your-command.md  # Missing space after ###
grep -n "\`\`\`[^ ]" .claude/commands/your-command.md  # Missing space after ```
```

#### 2. Validation Step Testing

Test each validation step independently:

**Test Happy Path** (all validations pass):

```bash
# Set up valid environment
git init  # If needed
mkdir -p .claude/agents
mkdir -p docs/features
echo '{"features": []}' > docs/features/feature-log.json

# Run command
/your-command [args]

# Verify: Should reach Step 1 (main execution)
```

**Test Each Failure Mode**:

```bash
# Test ENV-001: No git repository
cd /tmp/test-no-git
/your-command [args]
# Expected: Error message with ENV-001 code, execution stops

# Test FS-001: Missing required file
rm docs/features/feature-log.json
/your-command [args]
# Expected: Error message with FS-001 code, execution stops

# Continue for each validation check...
```

#### 3. Error Message Testing

Verify all error messages follow the standard format:

**Checklist**:
- ✅ Error code is present and correct (e.g., ENV-001)
- ✅ Category is correct (Environment Errors, File System Errors, etc.)
- ✅ Command name is correct (/your-command)
- ✅ Details explain what went wrong
- ✅ Context provides relevant information
- ✅ Impact explains consequences
- ✅ Recovery steps are specific and actionable
- ✅ Reference to error handling doc is present

#### 4. State Management Testing

If command modifies state, test state transitions:

**Test State Transitions**:

```bash
# Initial state
cat docs/features/feature-log.json | python3 -m json.tool

# Run command
/your-command [args]

# Verify state changed correctly
cat docs/features/feature-log.json | python3 -m json.tool
# Check: state field, stateHistory array, timestamps
```

**Test Invalid Transitions**:

```bash
# Manually set state to invalid starting state
# Run command
# Expected: State validation error, execution stops
```

#### 5. Resume Capability Testing

If command supports resume:

**Test Fresh Start**:

```bash
# No implementation log exists
/your-command [args]
# Verify: "Starting fresh implementation" message
# Verify: All items executed
```

**Test Resume from Checkpoint**:

```bash
# Create partial implementation log
echo '[{"storyNumber": 1, "status": "completed"}]' > implementation-log.json

# Run command again
/your-command [args]
# Verify: "Resuming implementation - 1 of 5 completed" message
# Verify: Story 1 skipped, stories 2-5 executed
```

**Test All Completed**:

```bash
# Create complete implementation log
# Run command
# Verify: "All stories already completed" message
# Verify: Skips to verification and commit
```

#### 6. Integration Testing

Test command integration with other commands and agents:

**Test Command Chaining**:

```bash
# If command calls another command
/your-command [args]
# Verify: Other command executed correctly
# Verify: Results passed between commands
```

**Test Agent Launch**:

```bash
# If command launches agents
/your-command [args]
# Verify: Correct agent launched
# Verify: Agent received correct context
# Verify: Agent output captured and used
```

### Testing Checklist

Before marking a command as complete:

**Pre-Flight Validation**:
- ✅ All required validations are present
- ✅ Validation Summary step displays correctly
- ✅ All error codes are correct and documented
- ✅ Blocking vs non-blocking errors are correctly classified

**Workflow Execution**:
- ✅ All workflow steps are numbered and ordered correctly
- ✅ Steps execute in the correct sequence
- ✅ Conditional steps work as intended
- ✅ Error handling at each step is comprehensive

**State Management**:
- ✅ State transitions are validated using state-validation.md
- ✅ stateHistory array is updated correctly
- ✅ Timestamps are in ISO 8601 format
- ✅ Invalid transitions are caught and prevented

**Error Handling**:
- ✅ All errors use standardized error codes
- ✅ Error messages follow the standard template
- ✅ Recovery steps are specific and actionable
- ✅ References to error handling docs are present

**Integration**:
- ✅ Helper files are loaded correctly
- ✅ Other commands are invoked correctly
- ✅ Agents receive correct context and instructions
- ✅ Git operations follow safety protocols

**Reporting**:
- ✅ Success report is comprehensive
- ✅ Failure report includes helpful information
- ✅ File paths are absolute, not relative
- ✅ Next steps are clearly communicated

**Documentation**:
- ✅ Purpose is clear and concise
- ✅ Variables are documented
- ✅ Instructions are comprehensive
- ✅ Examples are provided (if complex)
- ✅ Integration points are documented

---

## Best Practices and Anti-Patterns

### Best Practices

#### 1. Comprehensive Validation

**Do**: Validate everything before starting execution

```markdown
### Step 0: Pre-Flight Validation

#### Step 0.1: Load Error Handling Systems
#### Step 0.2: Validate Git Repository
#### Step 0.3: Validate Required Files
#### Step 0.4: Validate Dependencies
#### Step 0.X: Validation Summary
```

**Why**: Fail fast prevents partial execution and data corruption

#### 2. Structured Error Handling

**Do**: Use standardized error codes and messages

```markdown
If output is "INVALID":
- Display error message with error code ENV-001:
```
ERROR: Git repository not found

Code: ENV-001
Category: Environment Errors
Command: /your-command

Recovery Steps:
1. Initialize git: git init
2. Or navigate to repository: cd /path/to/repo
```
- STOP execution immediately
```

**Why**: Consistent error handling improves user experience and debugging

#### 3. State Validation

**Do**: Always validate state transitions

```markdown
- Read state validation from .claude/helpers/state-validation.md
- Validate transition: {current_state} → {new_state}
- If validation fails, display error and stop
- If valid, proceed with state update and add stateHistory entry
```

**Why**: Prevents invalid state transitions and maintains data integrity

#### 4. Resume Capability

**Do**: Implement resume for long-running operations

```markdown
### Step 2: Check for Existing Progress
- Read progress log if exists
- Extract completed items
- Skip completed items in execution
```

**Why**: Allows recovery from interruptions without redoing work

#### 5. Clear Reporting

**Do**: Provide comprehensive final reports

```markdown
## Report

Provide a summary that includes:
- What was accomplished
- Files created or modified with absolute paths
- Status of all operations
- Next steps for the user
- Any warnings or issues encountered
```

**Why**: Users need to understand what happened and what to do next

#### 6. Helper Integration

**Do**: Use helpers for common functionality

```markdown
#### Step 0.1: Load Error Handling and Validation Systems

Read error handling system from .claude/helpers/command-error-handling.md
Read validation helper from .claude/helpers/pre-flight-validation.md
```

**Why**: Consistency, maintainability, and avoiding duplication

### Anti-Patterns

#### 1. Missing Validation ❌

**Don't**: Skip validation steps

```markdown
### Step 1: Execute Operation
Run the operation immediately without checking prerequisites
```

**Why**: Leads to cryptic errors and partial failures

**Fix**: Always add Step 0: Pre-Flight Validation

#### 2. Inconsistent Error Handling ❌

**Don't**: Use ad-hoc error messages

```markdown
If file not found:
- Print "Error: File missing"
- Stop
```

**Why**: No context, no recovery guidance, no error code for tracking

**Fix**: Use standardized error code system with full error template

#### 3. Ignoring State Transitions ❌

**Don't**: Update state without validation

```markdown
### Step X: Update State
- Set state to "deployed"
- Write feature-log.json
```

**Why**: May create invalid state transitions, breaks state machine

**Fix**: Always validate transitions using state-validation.md

#### 4. No Resume Capability ❌

**Don't**: Restart from beginning on failure

```markdown
### Step 1: Execute All Items
For each item in list:
- Execute item
- (No checking if already completed)
```

**Why**: Wastes time and resources re-executing completed work

**Fix**: Add progress tracking and skip completed items

#### 5. Vague Reporting ❌

**Don't**: Provide minimal output

```markdown
## Report
"Operation completed successfully"
```

**Why**: Users don't know what happened or what to do next

**Fix**: Provide detailed summary with files, status, and next steps

#### 6. Hardcoded Values ❌

**Don't**: Hardcode paths or values

```markdown
### Step 1: Read File
Read file at: /home/user/project/docs/features/feature-log.json
```

**Why**: Breaks portability, fails in different environments

**Fix**: Use relative paths from project root or derive dynamically

#### 7. Skipping Helper Integration ❌

**Don't**: Duplicate helper functionality

```markdown
### Step 0.2: Validate Git Repository
Run: test -d ".git"
If fails, print custom error message
```

**Why**: Inconsistent with other commands, duplicates maintenance

**Fix**: Reference and use helpers: pre-flight-validation.md, error-code-mapping.md

#### 8. No Error Context ❌

**Don't**: Provide errors without context

```markdown
Error: Validation failed
```

**Why**: User doesn't know what failed, why, or how to fix it

**Fix**: Include what was validated, expected vs actual, and recovery steps

---

## Conclusion

Creating effective slash commands requires:

1. **Clear Purpose**: Know what the command should accomplish
2. **Comprehensive Validation**: Check all prerequisites before execution
3. **Structured Error Handling**: Use error codes and provide recovery guidance
4. **State Management**: Track state and validate transitions
5. **Resume Capability**: Allow interrupted operations to resume
6. **Helper Integration**: Use existing helpers for consistency
7. **Thorough Testing**: Validate syntax, logic, errors, and integration
8. **Clear Reporting**: Tell users what happened and what to do next

By following this guide, you'll create commands that are:
- **Reliable**: Validate before executing, handle errors gracefully
- **User-Friendly**: Clear messages, helpful errors, comprehensive reports
- **Maintainable**: Consistent patterns, helper integration, documented design
- **Resilient**: Resume capability, state management, error recovery

**Next Steps**:

1. Review existing commands in `.claude/commands/` for examples
2. Study helper files in `.claude/helpers/` for reusable functionality
3. Use the command template provided in this guide
4. Test thoroughly before deployment
5. Document any new patterns or helpers you create

For questions or improvements to this guide, consult the meta-developer agent or update this document directly.
