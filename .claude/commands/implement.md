---
description: Implement feature or bug by reading user stories and executing them in order
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

Execute user stories for a specific feature or bug by launching appropriate agents in the correct order. This command reads the user stories file, processes the execution order, and coordinates implementation across multiple phases.

## Variables

- `$TYPE` - The type of implementation ("feature" or "bug")
- `$ID` - The feature or bug ID number (e.g., "001" for Feature #001 or Bug #001)
- User stories path (feature): `docs/features/$ID/user-stories.md`
- User stories path (bug): `docs/features/$FEATUREID/bugs/$ID/user-stories.md`
- Implementation log path (feature): `docs/features/$ID/implementation-log.json`
- Implementation log path (bug): `docs/features/$FEATUREID/bugs/$ID/implementation-log.json`
- Feature log path: `docs/features/feature-log.json`

## Instructions

- Check if user-stories file exists before proceeding
- Skip stories that are already completed (found in implementation logs)
- Execute ALL user stories regardless of agent type (ui-ux-designer, frontend-developer, backend-developer, devops-engineer, etc.)
- Respect execution order: sequential phases run one-by-one, parallel phases run simultaneously
- Launch agents directly with appropriate context for each story
- Record implementation in implementation log after each story
- Update feature log only when ALL stories are completed

## Error Handling

This command uses comprehensive error handling with specific error codes and recovery suggestions.

**Error Handling Reference**: See `.claude/helpers/command-error-handling.md` for complete error code documentation and `.claude/helpers/error-code-mapping.md` for validation error mapping.

**Common Errors**:
- ENV-001: Git repository not found → Initialize git or navigate to repository
- ENV-003: Detached HEAD state → Checkout a branch
- FS-001: User stories file not found → Run /feature command first
- FS-005: Invalid JSON in feature-log or implementation-log → Fix JSON syntax
- DEP-002: Feature not found → Create feature with /feature command
- DEP-003: User stories not created → Run /feature command
- INPUT-002: Invalid bug ID format → Use github-issue-{number} format
- STATE-004: Invalid state transition → Use valid transition path
- STATE-002: Feature already implemented → Re-run will resume from checkpoint (warning)

**Error Handling Strategy**:
- All validation errors (Step 0) use standardized error codes
- Path determination errors are BLOCKING - cannot proceed without valid paths
- Feature dependency errors are BLOCKING - must exist before implementation
- State transition errors are BLOCKING - prevents invalid state changes
- Already implemented is WARNING - resume capability handles this gracefully
- Invalid JSON in implementation log skips corrupt stories, continues with others

## Workflow

### Step 0: Pre-Flight Validation

Before executing any operations, run comprehensive validation checks to ensure prerequisites are met.

#### Step 0.0: Load Error Handling and Validation Systems

Read error handling system from .claude/helpers/command-error-handling.md to understand error codes, categories, and message formats.

Read error code mapping from .claude/helpers/error-code-mapping.md to map validation errors to error codes.

Read validation helper from .claude/helpers/pre-flight-validation.md to understand validation requirements and error message formats.

All validation errors in subsequent steps should include appropriate error codes from the error code mapping.

#### Step 0.1: Determine Paths Based on Type

1. If `$TYPE` is "feature":
   - Set base path to `docs/features/$ID`
   - Set user stories path to `docs/features/$ID/user-stories.md`
   - Set implementation log path to `docs/features/$ID/implementation-log.json`
2. If `$TYPE` is "bug":
   - The ID should be in the format "github-issue-{number}" (e.g., "github-issue-10")
   - Extract the feature ID from the user stories path (typically the bug user stories are at docs/features/{FEATUREID}/bugs/{ID}/user-stories.md)
   - Search for the user stories file by pattern: docs/features/*/bugs/$ID/user-stories.md
   - If found, use the parent feature directory as FEATUREID
   - Set base path to `docs/features/$FEATUREID/bugs/$ID`
   - Set user stories path to `docs/features/$FEATUREID/bugs/$ID/user-stories.md`
   - Set implementation log path to `docs/features/$FEATUREID/bugs/$ID/implementation-log.json`
3. If `$TYPE` is neither "feature" nor "bug":
   - Respond with: "Error: Type must be either 'feature' or 'bug'"
   - Stop execution

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
Command: /implement

Remediation:
1. Navigate to your git repository directory
2. Verify you are in the correct directory:
   pwd
3. This command requires a git repository to track implementation
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
Purpose: Tracks all features and their implementation status
Command: /implement

Remediation:
1. Ensure you are in the correct project directory
2. Run /feature command at least once to initialize the feature log
3. Features must be registered before implementation

Example:
  /feature "Initialize project structure"
```
- STOP execution immediately

Validate JSON syntax:
```bash
python3 -c "import json; json.load(open('docs/features/feature-log.json'))" 2>&1
```

If JSON validation fails:
- Display error message with specific JSON error and remediation steps (see pre-flight-validation.md)
- STOP execution immediately

#### Step 0.4: Validate User Stories File Exists

Check if user stories file exists at the determined path from Step 0.1:
```bash
test -f "{user_stories_path}" && echo "VALID" || echo "INVALID"
```

If output is "INVALID":
- Display error message:
```
Error: User stories file not found

File: {user_stories_path}
Purpose: Contains user stories for {type} #{id}
Command: /implement

Remediation:
1. Verify the {type} ID is correct
2. For features: Run /feature command to create user stories
3. For bugs: Run /fix command to process GitHub issue
4. Check that user stories were successfully created before running /implement

Example:
  /feature "Your feature description here"
  OR
  /fix gha
```
- STOP execution immediately

#### Step 0.5: Validate Feature Exists in Feature Log

Read feature-log.json and extract feature ID from user stories path.

Search for feature with matching featureID in feature-log.json.

If feature not found:
- Display error message:
```
Error: Feature not found in feature log

Dependency: Feature must be registered in feature log before implementation
Status: Feature #{feature_id} not found in docs/features/feature-log.json
Command: /implement

Remediation:
1. Verify the feature ID is correct
2. Check feature-log.json for available features:
   cat docs/features/feature-log.json | python3 -m json.tool
3. If feature should exist, run /feature command to create it:
   /feature "Your feature description"
4. Ensure feature-log.json contains an entry with featureID: "{feature_id}"
```
- STOP execution immediately

#### Step 0.6: Validate Bug ID Format (For Bugs Only)

If `$TYPE` is "bug":
- Validate id matches pattern "github-issue-{number}":
```bash
echo "{id}" | grep -E '^github-issue-[0-9]+$' && echo "VALID" || echo "INVALID"
```

If output is "INVALID":
- Display error message:
```
Error: Invalid bug ID format

Dependency: Bug ID must follow format 'github-issue-{number}'
Status: Received bug ID '{id}' which does not match expected pattern
Command: /implement

Remediation:
1. Use the correct bug ID format: github-issue-{number}
2. Find the GitHub issue number for this bug
3. Run the command again with correct format

Example:
  /implement bug github-issue-37
  (for GitHub issue #37)
```
- STOP execution immediately

#### Step 0.7: Validate Git Branch

Get current branch:
```bash
git rev-parse --abbrev-ref HEAD
```

Check if branch is appropriate for implementation:
- Valid branches: main, master, feature/*
- Invalid: Any other pattern or detached HEAD

If branch is "HEAD" (detached HEAD):
- Display error message:
```
Error: Repository is in detached HEAD state

Check: Git HEAD reference
Status: HEAD is detached
Command: /implement

Remediation:
1. Checkout a branch to reattach HEAD:
   git checkout main
   OR
   git checkout -b feature/{id}-{description}
2. If you want to keep changes, create a new branch first
```
- STOP execution immediately

If branch does not match expected pattern:
- Display warning message (allow execution to continue):
```
Warning: Unexpected branch name

Status: Current branch '{branch_name}' does not follow expected pattern
Expected: main, master, or feature/*
Command: /implement

Recommendation:
1. Feature implementations typically use feature branches:
   git checkout -b feature/{id}-{description}
2. You may continue on current branch at your own risk

You may continue, but using a feature branch is recommended.
```

Check if branch is behind remote:
```bash
git status -uno 2>&1 | grep "Your branch is behind"
```

If behind remote:
- Display warning message:
```
Warning: Branch is behind remote

Status: Your branch is behind the remote branch
Command: /implement

Recommendation:
1. Pull latest changes before implementing:
   git pull
2. Resolve any conflicts if they occur
3. Or continue at your own risk (may cause merge conflicts later)

You may continue, but pulling latest changes first is recommended.
```

#### Step 0.8: Check if Feature Already Fully Implemented (Warning)

Read feature-log.json and find the feature entry.

Check if userStoriesImplemented field is set (not null):

If userStoriesImplemented is set:
- Display warning message:
```
Warning: Feature may already be fully implemented

Status: Feature #{feature_id} has userStoriesImplemented timestamp set
Value: {userStoriesImplemented}
Command: /implement

Impact:
This feature was previously marked as fully implemented. Running /implement
again will re-execute user stories (using resume capability to skip completed ones).

Scenarios:
1. New stories added to feature - OK to continue
2. Re-implementing after partial failure - OK to continue
3. Feature already complete - Will skip all stories (no harm)

Recommendation:
1. Check implementation log to verify completion status:
   cat {implementation_log_path}
2. Review user stories to see what remains:
   cat {user_stories_path}

You may continue - resume capability will skip already completed stories.
```
- This is a WARNING - allow execution to continue

#### Step 0.9: Validate Implementation Log if Exists (Optional)

If implementation log exists at determined path from Step 0.1:
```bash
test -f "{implementation_log_path}" && echo "VALID" || echo "INVALID"
```

If file exists, validate JSON syntax:
```bash
python3 -c "import json; json.load(open('{implementation_log_path}'))" 2>&1
```

If JSON validation fails:
- Display error message:
```
Error: Implementation log contains invalid JSON

File: {implementation_log_path}
Purpose: Tracks implementation progress for {type} #{id}
Command: /implement

Remediation:
1. Open {implementation_log_path} in a text editor
2. Fix the JSON syntax error
3. Validate JSON using: python3 -m json.tool {implementation_log_path}
4. Or delete the file to start fresh (will re-execute all stories)
5. Implementation log should be an array of story entries

If unsure, you can delete the file and re-run /implement to start fresh.
```
- STOP execution immediately

#### Step 0.10: Validation Summary

If all validations pass:
- Output: "Pre-flight validation passed - proceeding with implementation"
- Display summary:
```
Validation Summary:
  ✓ Git repository validated
  ✓ Feature log validated
  ✓ User stories file found: {user_stories_path}
  ✓ Feature #{feature_id} registered in feature log
  {✓ Bug ID format validated (if bug)}
  ✓ Git branch validated: {branch_name}
  {⚠ Feature previously implemented (will resume from last checkpoint) (if applicable)}
  {✓ Implementation log validated (if exists)}

Proceeding with {type} #{id} implementation...
```
- Proceed to Step 1

If any critical validation failed:
- Execution has already been stopped
- User must remediate issues and re-run command

### Step 1: Validate User Stories File

1. Check if user-stories file exists at the determined path
2. If not found, respond with: "Error: No user stories found for $TYPE #$ID. Run /plan first."
3. If found, proceed to next step

### Step 2: Check for Existing Implementation Progress

1. Check if implementation-log.json exists at the determined path
2. If it exists:
   - Read and parse the implementation-log.json file
   - Extract all completed story numbers (where status is "completed")
   - Store the list of completed story numbers for later use
3. If it doesn't exist or is empty:
   - Proceed with no stories marked as completed
   - All stories will need to be executed

### Step 3: Parse Execution Order

1. Read the user-stories.md file
2. Parse the Execution Order section
3. Identify all phases and their execution mode (sequential/parallel)

### Step 4: Execute User Stories

For each phase in the execution order:

1. **Filter stories for this phase:**
   - Identify all stories in the current phase from the execution order
   - Check each story number against the list of completed stories from Step 2
   - Separate stories into two groups: completed (to skip) and pending (to execute)

2. **Provide resume feedback (if any stories are being skipped):**
   - If there are completed stories being skipped in this phase:
     - Output: "Skipping already completed stories in Phase X: Story #Y, Story #Z"
   - If all stories in this phase are completed:
     - Output: "Phase X already completed - skipping all stories"
     - Continue to next phase
   - If no stories are completed in this phase:
     - Output: "Starting Phase X - executing Story #A, Story #B" (list pending stories)
   - If some stories are completed and some are pending:
     - Output: "Resuming Phase X - skipping completed Story #Y, executing pending Story #A, Story #B"

3. **Load Phase Context Once (Performance Optimization):**
   - Record phase start timestamp for performance metrics
   - Analyze all pending stories in the current phase to identify required context files:
     - Collect unique agent types across all pending stories
     - Scan all pending story titles and descriptions for context keywords
     - Build a deduplicated list of context files needed for this phase
   - Read all identified context files ONCE at phase start
   - Cache the loaded content for reuse across all stories in this phase
   - Output: "Loaded [count] context files for Phase [X] ([story_count] pending stories): [list of file names]"

4. **Execute pending stories with cached context:**
   - For each pending (not completed) story in the phase:
   - Extract story details (title, description, acceptance criteria, agent, dependencies)
   - Retrieve relevant cached context for this story's agent type and keywords (no re-reading files)
   - Launch the agent with the story and the cached context
   - Record implementation in implementation-log.json

5. **Clean up after phase completes:**
   - Record phase end timestamp
   - Calculate phase duration (end - start)
   - Clear cached context to free memory before next phase
   - Log performance metrics:
     - Phase duration
     - Number of stories processed
     - Number of context files loaded once
     - Estimated time saved by caching (based on avoided redundant file reads)
   - Example output: "Phase 2 completed in 45.2s - processed 4 stories with 3 context files (estimated 12s saved by caching)"

#### Context Loading for Stories (Phase-Level Caching)

**Agent Default Context (always load for agent type):**
- ui-ux-designer → `context/design/**/*`
- frontend-developer → `context/frontend/**/*`
- backend-developer → `context/backend/**/*`
- devops-engineer → `context/devops/**/*`
- meta-developer → No default context (uses keyword-based context as needed)

**Keyword-Based Additional Context:**
Analyze story title and description for keywords:

- "Material UI" or "MUI" → `context/frontend/material-ui-best-practices.md`
- "React" or "component" → `context/frontend/react-typescript-best-practices-2024-2025.md`
- "Docker" or "container" → `context/devops/docker.md`
- "GitHub Actions" or "CI/CD" → `context/devops/github-actions.md`
- "Django" or "DRF" → `context/backend/django-drf-postgresql-best-practices.md`
- "testing" or "test" → `context/testing/**/*`

**Context Caching Strategy:**
- Context files are loaded ONCE per phase at phase start (before executing any stories)
- When multiple stories in a phase share the same agent type, default context is loaded only once
- Keyword-based context files identified across all phase stories are loaded once and cached
- Cached context content is reused for all stories in the phase (no redundant file reads)
- Cache is cleared between phases to manage memory usage
- Performance metrics track time saved by avoiding redundant file reads
- Example: Phase with 4 backend stories loads `context/backend/**/*` once, not 4 times - saving ~3x file read time

#### Execution Modes

6. For sequential phases:
   - Execute pending stories one by one in the specified order (skip completed ones)
   - Wait for each to complete before starting the next
7. For parallel phases:
   - Launch multiple pending agents simultaneously using the Task tool (skip completed ones)
   - Use multiple Task tool calls in a single message

**Example for Sequential Phase (with resume and context caching):**
```
For Phase 1 (Sequential) with stories 1, 2, 3:
- Check implementation log: Story #1 completed, Story #2 and #3 pending
- Output: "Resuming Phase 1 - skipping completed Story #1, executing pending Story #2, Story #3"
- Analyze stories 2 and 3 for context requirements
- Load context once: context/backend/**/* (shared by both stories)
- Output: "Loaded 2 context files for Phase 1 (2 pending stories): django-drf-postgresql-best-practices.md, testing/django-drf-testing-best-practices-2025.md"
- Execute story 2: Use cached context → Launch agent → Record in log
- Wait for completion
- Execute story 3: Use cached context → Launch agent → Record in log
- Clear cached context
- Output: "Phase 1 completed in 32.5s - processed 2 stories with 2 context files (estimated 8s saved by caching)"
```

**Example for Parallel Phase (with resume and context caching):**
```
For Phase 2 (Parallel) with stories 4, 5, 6:
- Check implementation log: Story #4 completed, Story #5 and #6 pending
- Output: "Resuming Phase 2 - skipping completed Story #4, executing pending Story #5, Story #6"
- Analyze stories 5 and 6 for context requirements
- Load context once: context/frontend/**/* (shared by both stories)
- Output: "Loaded 3 context files for Phase 2 (2 pending stories): react-typescript-best-practices-2024-2025.md, material-ui-best-practices.md, testing/frontend-testing-research-2025.md"
- Launch both pending agents simultaneously in one message using Task tool with cached context
- Record both in log after completion
- Clear cached context
- Output: "Phase 2 completed in 45.2s - processed 2 stories with 3 context files (estimated 10s saved by caching)"
```

**Example for Fully Completed Phase:**
```
For Phase 3 (Parallel) with stories 7, 8:
- Check implementation log: Story #7 and #8 both completed
- Output: "Phase 3 already completed - skipping all stories"
- Continue to next phase
```

#### Implementation Log Format

After each story completes, append to implementation-log.json:
```json
{
  "storyNumber": 1,
  "storyTitle": "Story title",
  "agent": "agent-type",
  "status": "completed|partial|blocked",
  "completedAt": "YYYY-MM-DDTHH:mm:ssZ",
  "filesModified": ["relative/path/to/file.ts"],
  "filesCreated": ["relative/path/to/newfile.ts"],
  "actions": ["Action description"],
  "toolsUsed": ["Write", "Edit"],
  "issuesEncountered": ["Issue description"],
  "notes": "Additional notes"
}
```

### Step 4: Handle Edge Cases and Provide Initial Feedback

After parsing execution order and before starting execution, analyze the situation:

1. **Count total stories and completed stories:**
   - Total stories: Count all stories across all phases in execution order
   - Completed stories: Count stories marked as "completed" in implementation-log.json
   - Pending stories: Total minus completed

2. **Determine execution scenario and provide feedback:**

   **Scenario A - All stories already completed:**
   - If completed stories equals total stories
   - Output: "All user stories for $TYPE #$ID have already been completed. Implementation log: [path]"
   - Skip to Step 6 (verify and update feature log) and Step 7 (commit and push)

   **Scenario B - No implementation log exists (fresh start):**
   - If implementation-log.json doesn't exist
   - Output: "Starting fresh implementation of $TYPE #$ID - executing all Y stories"
   - Initialize empty list of completed stories
   - Proceed with execution of all stories

   **Scenario C - Partial completion (resume scenario):**
   - If implementation-log.json exists with some (but not all) completed stories
   - Output: "Resuming implementation of $TYPE #$ID - X of Y stories completed, Z remaining"
   - List which stories are completed (by number and title)
   - Proceed with execution, skipping completed stories

   **Scenario D - Empty or invalid log file:**
   - If implementation-log.json exists but is empty or invalid JSON
   - Output warning: "Implementation log found but is empty or invalid - treating as fresh start"
   - Proceed as Scenario B (fresh start)

3. **Update feature state to "in_progress" (if starting fresh or resuming):**

   After determining execution scenario and before executing any stories:

   - **Only for features (not bugs)**: Update feature state if implementation is starting
   - Read the current feature-log.json file
   - Find the feature entry with matching featureID
   - Read the validation helper from .claude/helpers/state-validation.md to understand state transition rules
   - Check the current state field:
     - If state is "planned" (fresh start):
       - Validate transition: planned → in_progress (automatic)
       - If validation fails, display error and stop execution
       - If valid, proceed with transition to "in_progress"
     - If state is "in_progress" (resume scenario) → No state change, add note to stateHistory (skip validation)
     - If state is "deployed" (re-implementation) → Add note to stateHistory (skip validation)
     - If state field doesn't exist (legacy):
       - Infer state from existing fields (if isSummarised: "summarised", elif userStoriesImplemented: "deployed", else: "planned")
       - Add state: "in_progress" and initialize stateHistory (allow migration from any inferred state)

   - **For "planned" → "in_progress" transition (fresh start)**:
     - Set `state`: "in_progress"
     - Append to `stateHistory` array:
       ```json
       {
         "state": "in_progress",
         "timestamp": "{current ISO 8601 timestamp}",
         "triggeredBy": "/implement command started",
         "notes": "Implementation started - executing first story"
       }
       ```

   - **For "in_progress" resume scenario**:
     - Keep state as "in_progress"
     - Append to `stateHistory` array:
       ```json
       {
         "state": "in_progress",
         "timestamp": "{current ISO 8601 timestamp}",
         "triggeredBy": "/implement command resumed",
         "notes": "Resume scenario - continuing from story {next_story_number} ({completed_count} of {total_count} stories already completed)"
       }
       ```

   - **For "deployed" re-implementation scenario**:
     - Keep state as "deployed"
     - Append to `stateHistory` array:
       ```json
       {
         "state": "deployed",
         "timestamp": "{current ISO 8601 timestamp}",
         "triggeredBy": "/implement command re-running",
         "notes": "Re-implementation scenario - feature was previously completed"
       }
       ```

   - **For legacy features without state field**:
     - Add `state`: "in_progress"
     - Initialize `stateHistory` as array with initial entry:
       ```json
       {
         "state": "in_progress",
         "timestamp": "{current ISO 8601 timestamp}",
         "triggeredBy": "/implement command started",
         "notes": "State tracking initialized during implementation - migrated from legacy format"
       }
       ```

   - Write the updated feature-log.json file back
   - This automatic state transition tracks that implementation has started

### Step 5: Execute User Stories (Resume-Aware)

Execute user stories as defined in previous Step 4, which includes:
- Filtering completed vs pending stories per phase
- Providing phase-level resume feedback
- Executing only pending stories
- Recording implementations in log

### Step 6: Verify Completion and Update Feature Log

After all phases complete:

1. Verify all stories in the execution order have been completed by checking implementation-log.json
2. If ALL stories are completed:
   - Read the current feature-log.json file
   - Find the feature entry with matching featureID
   - Set `userStoriesImplemented` to current timestamp in ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ)
   - Ensure `isSummarised` is set to `false` (it should already be false from feature creation)
   - **Update feature state to "deployed"** (only for features, not bugs):
     - Read current state from feature entry
     - Validate transition: {current_state} → deployed (automatic)
     - If validation fails, display error message and stop execution (do not commit)
     - If valid, proceed with state transition:
     - Set `state`: "deployed"
     - Append to `stateHistory` array:
       ```json
       {
         "state": "deployed",
         "timestamp": "{current ISO 8601 timestamp}",
         "triggeredBy": "/implement command completed",
         "notes": "Implementation completed - all stories finished and deployed"
       }
       ```
     - This automatic state transition marks the feature as fully implemented and deployed
   - Write the updated feature-log.json file back

Note: The `isSummarised` property tracks whether this feature has been summarised by the /summarise command to reduce context for future agents.

### Step 7: Commit Implementation and Push

After all stories are completed and feature log is updated:

1. **Read implementation-log.json**: Extract all completed stories and files modified from the determined implementation log path
2. **Read feature-log.json**: Get the title for this feature/bug ID
3. **Determine issue number for bug fixes**:
   - If `$TYPE` is "bug" and `$ID` matches the pattern "github-issue-{number}":
     - Extract the issue number (e.g., "github-issue-123" → "123")
   - Otherwise, set issue number to null
4. **Create detailed commit message**: Use the following format:

   For bugs with GitHub issue:
   ```
   Implementation of {type}-{id}-{title}

   Completed user stories:
   - Story #{num}: {story-title}
   - Story #{num}: {story-title}

   Files modified:
   - {file1}
   - {file2}

   Fixes #{issue-number}
   ```

   For features or bugs without GitHub issue:
   ```
   Implementation of {type}-{id}-{title}

   Completed user stories:
   - Story #{num}: {story-title}
   - Story #{num}: {story-title}

   Files modified:
   - {file1}
   - {file2}
   ```

   Note: {type} should be lowercase ("feature" or "bug")
5. **Commit and push**: Use the SlashCommand tool to execute:
   ```
   /commit "{commit message}" push
   ```
   Note: Use `-u` flag in a separate git push command only if this is the first push to the remote branch

## Report

Provide a comprehensive summary that includes:
- Execution mode: Fresh start or Resume (with X of Y previously completed)
- Total number of user stories in execution order
- Number of stories completed in this run vs. skipped (already completed)
- List of all agents launched and their status
- Any stories that failed or are blocked
- Confirmation of feature log update if all stories completed
- Implementation log location for detailed records
- Confirmation of commit created and pushed to remote
- Current git branch name

## Resume Capability

The implement command automatically resumes from the last completed story when execution is interrupted:

**How Resume Works:**
1. At the start of execution, the command reads implementation-log.json
2. Any story marked as "completed" in the log is automatically skipped
3. Execution resumes from the first pending (not completed) story
4. Clear feedback is provided showing which stories are being skipped and where execution resumes

**Resume Scenarios:**

- **Fresh Start**: No implementation log exists - all stories will be executed
  - Output: "Starting fresh implementation of feature #5 - executing all 19 stories"

- **Partial Resume**: Some stories completed, some pending - resume from next pending story
  - Output: "Resuming implementation of feature #5 - 4 of 19 stories completed, 15 remaining"
  - Per-phase output: "Resuming Phase 2 - skipping completed Story #3, executing pending Story #4, Story #5"

- **All Completed**: All stories already completed - skip to verification and commit
  - Output: "All user stories for feature #5 have already been completed. Implementation log: docs/features/5/implementation-log.json"

**Resume Behavior by Execution Mode:**

- **Sequential Phases**: Completed stories are skipped, remaining stories execute in order
- **Parallel Phases**: Only pending stories are launched in parallel, completed stories are skipped

**Benefits:**
- Execution can be safely interrupted and resumed without redoing completed work
- No manual tracking needed - system automatically detects progress
- Works seamlessly with both sequential and parallel execution modes
- Prevents duplicate work and maintains consistency
