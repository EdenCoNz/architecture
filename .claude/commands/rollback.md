---
description: Rollback system changes using checkpoints created before major operations
args:
  - name: checkpoint_id
    description: Checkpoint ID to restore (optional - if omitted, lists checkpoints)
    required: false
  - name: confirm
    description: Skip confirmation prompt (use --confirm flag)
    required: false
---

## Purpose

Restore the architecture system to a previous state using checkpoints created automatically before major operations (/feature, /implement, /summarise, /fix) or created manually. This command provides a safety net for undoing changes when something goes wrong or when you want to try a different approach.

## Variables

- `$CHECKPOINT_ID` - The checkpoint identifier to restore (format: checkpoint-{timestamp}-{operation})
- `$CONFIRM_FLAG` - Whether to skip confirmation (--confirm flag)

## Instructions

- List all available checkpoints if no checkpoint ID provided
- Show detailed preview of what will be restored before executing
- Require explicit confirmation unless --confirm flag is used
- Create pre-rollback checkpoint as safety net before restoration
- Restore files atomically where possible
- Validate restored files after rollback
- Log all rollbacks in rollback history
- Provide clear feedback about what was restored

## Workflow

### Step 0: Pre-Flight Validation

Before executing any operations, run comprehensive validation checks to ensure prerequisites are met.

#### Step 0.1: Load Validation System

Read the validation helper from .claude/helpers/pre-flight-validation.md to understand validation requirements and error message formats.

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
Command: /rollback

Remediation:
1. Navigate to your git repository directory
2. Verify you are in the correct directory:
   pwd
3. Rollback system requires git repository for context
```
- STOP execution immediately

#### Step 0.3: Validate Checkpoints Directory Exists

Check if .checkpoints/ directory exists:
```bash
test -d ".checkpoints" && echo "VALID" || echo "INVALID"
```

If output is "INVALID":
- Display informational message (not an error):
```
No checkpoints directory found

Status: .checkpoints/ directory does not exist
Command: /rollback

Information:
The checkpoint system has not been used yet. Checkpoints are created
automatically by these commands:
- /feature (before feature planning)
- /implement (before implementation)
- /summarise (before summarization)
- /fix (before bug processing)

You can also create manual checkpoints with:
  /checkpoint "description"

There are currently no checkpoints to rollback to.
```
- If listing checkpoints (no checkpoint ID provided): Exit gracefully
- If rolling back specific checkpoint: Continue to checkpoint existence validation

#### Step 0.4: Check for Available Checkpoints (If Listing)

If no checkpoint ID provided (listing mode), check if any checkpoints exist:
```bash
ls -1 .checkpoints/checkpoint-* 2>/dev/null | wc -l
```

If count is 0:
- Display informational message:
```
No checkpoints available

Status: .checkpoints/ directory exists but contains no checkpoints
Command: /rollback

Information:
Checkpoints are created automatically before major operations.
Run any of these commands to create checkpoints:
- /feature "feature description"
- /implement feature {id}
- /summarise
- /fix

You can also create manual checkpoints with:
  /checkpoint "description"
```
- Exit gracefully (this is expected state, not an error)

#### Step 0.5: Validation Summary

If all validations pass:
- Output: "Pre-flight validation passed - proceeding with rollback operation"
- Proceed to Step 1

If any critical validation failed:
- Execution has already been stopped
- User must remediate issues and re-run command

### Step 1: Parse Command Arguments

Parse the command arguments to determine operation mode:

1. **Check for checkpoint ID argument**:
   - If `$CHECKPOINT_ID` is empty or null: Set mode to "list"
   - If `$CHECKPOINT_ID` is provided: Set mode to "rollback"

2. **Check for confirm flag**:
   - If arguments contain "--confirm": Set confirm to true
   - Otherwise: Set confirm to false

3. **Validate checkpoint ID format** (if provided):
   - Expected format: `checkpoint-{timestamp}-{operation}`
   - Timestamp format: ISO 8601 format (e.g., 20251019T123045Z)
   - Operation: Any string (e.g., feature-planning, implement-5, summarise)
   - Validation regex: `^checkpoint-\d{8}T\d{6}Z-.+$`
   - If invalid format:
     - Display error message:
```
Error: Invalid checkpoint ID format

Provided: {checkpoint_id}
Expected format: checkpoint-{timestamp}-{operation}
Example: checkpoint-20251019T123045Z-feature-planning

To see available checkpoints, run:
  /rollback
```
     - STOP execution immediately

4. **Continue to appropriate step**:
   - If mode is "list": Go to Step 2
   - If mode is "rollback": Go to Step 3

### Step 2: List Available Checkpoints

If no checkpoint ID provided, list all available checkpoints in reverse chronological order (newest first):

#### Step 2.1: Discover Checkpoints

1. List all checkpoint directories:
   ```bash
   ls -1 .checkpoints/checkpoint-* 2>/dev/null
   ```

2. For each checkpoint directory:
   - Read metadata.json file
   - Extract: checkpointId, createdAt, operation, triggeredBy, description, filesCheckpointed
   - Calculate age: current timestamp - createdAt (in hours and days)

3. Sort checkpoints by createdAt in descending order (newest first)

#### Step 2.2: Display Checkpoint List

Format the checkpoint list as a clear, scannable table:

```
Available Checkpoints
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID: checkpoint-20251019T150000Z-implement-5
Created: 2025-10-19 15:00:00 (2 hours ago)
Operation: implement-5
Triggered by: /implement command
Description: Automatic checkpoint before implementing Feature #5
Files backed up: 3 files (feature-log.json, user-stories.md, implementation-log.json)

───────────────────────────────────────────────────────────────────────────────────────

ID: checkpoint-20251019T123045Z-feature-planning
Created: 2025-10-19 12:30:45 (5 hours ago)
Operation: feature-planning
Triggered by: /feature command
Description: Automatic checkpoint before feature planning
Files backed up: 1 file (feature-log.json)

───────────────────────────────────────────────────────────────────────────────────────

ID: checkpoint-20251019T100000Z-summarise
Created: 2025-10-19 10:00:00 (8 hours ago)
Operation: summarise
Triggered by: /summarise command
Description: Automatic checkpoint before summarizing features
Files backed up: 5 files (feature-log.json, 4 implementation logs)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total: 3 checkpoints available

To rollback to a checkpoint:
  /rollback {checkpoint-id}

To see preview before rollback:
  /rollback {checkpoint-id}
  (then confirm or cancel)

To rollback without confirmation prompt:
  /rollback {checkpoint-id} --confirm
  (use with caution - no preview)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Step 2.3: Exit

After listing checkpoints, exit gracefully (no further action needed).

### Step 3: Load Checkpoint Metadata

Load the metadata for the specified checkpoint:

1. **Validate checkpoint directory exists**:
   ```bash
   test -d ".checkpoints/$CHECKPOINT_ID" && echo "VALID" || echo "INVALID"
   ```

   If "INVALID":
   - Display error message:
```
Error: Checkpoint not found

Checkpoint ID: {checkpoint_id}
Expected location: .checkpoints/{checkpoint_id}
Status: Directory does not exist

To see available checkpoints, run:
  /rollback

Remediation:
1. Verify the checkpoint ID is correct (check for typos)
2. List available checkpoints with /rollback
3. Use an existing checkpoint ID from the list
```
   - STOP execution immediately

2. **Validate metadata.json exists**:
   ```bash
   test -f ".checkpoints/$CHECKPOINT_ID/metadata.json" && echo "VALID" || echo "INVALID"
   ```

   If "INVALID":
   - Display error message:
```
Error: Checkpoint metadata missing

Checkpoint ID: {checkpoint_id}
Expected file: .checkpoints/{checkpoint_id}/metadata.json
Status: File does not exist

This checkpoint appears to be corrupted or incomplete.

Remediation:
1. Try a different checkpoint
2. List available checkpoints: /rollback
3. If checkpoint is important, check .checkpoints/ directory manually
```
   - STOP execution immediately

3. **Read and parse metadata.json**:
   ```bash
   python3 -c "import json; json.load(open('.checkpoints/$CHECKPOINT_ID/metadata.json'))"
   ```

   If parsing fails (invalid JSON):
   - Display error message:
```
Error: Checkpoint metadata corrupted

Checkpoint ID: {checkpoint_id}
File: .checkpoints/{checkpoint_id}/metadata.json
Status: Invalid JSON format

This checkpoint cannot be used for rollback.

Remediation:
1. Try a different checkpoint: /rollback
2. If this checkpoint is important, inspect the metadata file manually
```
   - STOP execution immediately

4. **Extract metadata fields**:
   - checkpointId
   - createdAt
   - operation
   - triggeredBy
   - description
   - gitState (branch, commitHash, workingTreeClean, uncommittedFiles)
   - filesCheckpointed (array of file paths)
   - featureContext (featureId, featureTitle, operation)
   - systemState (totalFeatures, featuresInProgress, lastModified)

5. **Validate checkpointed files exist**:
   - For each file in filesCheckpointed array:
     - Check if file exists in checkpoint directory
     - If any file missing:
       - Display error message:
```
Error: Checkpoint files missing

Checkpoint ID: {checkpoint_id}
Missing file: {file_path}
Status: Checkpoint is incomplete

This checkpoint cannot be used for rollback because it's missing required files.

Remediation:
1. Try a different checkpoint: /rollback
2. List available checkpoints to find complete one
```
       - STOP execution immediately

6. **Continue to preview generation** (Step 4)

### Step 4: Generate Rollback Preview

Generate a comprehensive preview showing exactly what will be restored:

#### Step 4.1: Capture Current System State

1. **Read current feature log**:
   - Parse docs/features/feature-log.json
   - Count total features
   - Identify features by state
   - Determine last modified timestamp

2. **Capture current git state**:
   ```bash
   git rev-parse --abbrev-ref HEAD  # Current branch
   git rev-parse HEAD                # Current commit
   git status --porcelain            # Working tree status
   ```

3. **Read current versions of checkpointed files**:
   - For each file in metadata.filesCheckpointed:
     - Read current file content
     - Calculate file size and last modified time
     - For JSON files: Count features/entries
     - For markdown files: Count lines

#### Step 4.2: Compare Checkpoint vs Current State

For each file being restored:

1. **Feature Log Comparison** (if docs/features/feature-log.json in checkpoint):
   - Current feature count vs checkpoint feature count
   - Identify features that will be removed (in current but not in checkpoint)
   - Identify features that will be restored (in checkpoint but not in current)
   - List features with state changes

2. **User Stories Comparison** (if user-stories.md in checkpoint):
   - Current line count vs checkpoint line count
   - Note: Detailed diff not shown (too verbose), just indicate change

3. **Implementation Log Comparison** (if implementation-log.json in checkpoint):
   - Current story count vs checkpoint story count
   - Identify stories that will be removed
   - Calculate progress loss (stories that were completed but will be rolled back)

#### Step 4.3: Analyze Impact

Calculate the impact of rollback:

1. **Features Affected**:
   - Features that will be removed
   - Features that will be restored
   - Features with state changes
   - Features with implementation progress loss

2. **Data Loss Assessment**:
   - User stories that will be removed (directories that exist but won't be tracked)
   - Implementation progress that will be lost (stories completed but rolled back)
   - State transitions that will be undone

3. **Git Impact**:
   - Warn if working tree is not clean (uncommitted changes)
   - Note that rollback does NOT affect git commits or branches
   - Note that files may become uncommitted changes after rollback

#### Step 4.4: Format Preview

Display comprehensive preview with all information:

```
Rollback Preview: {checkpoint_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHECKPOINT INFORMATION:
  Created: {checkpoint_created_at} ({time_ago})
  Operation: {operation}
  Triggered by: {triggered_by}
  Description: {description}

GIT STATE AT CHECKPOINT:
  Branch: {checkpoint_git_branch}
  Commit: {checkpoint_git_commit}
  Working tree: {checkpoint_working_tree_status}

CURRENT GIT STATE:
  Branch: {current_git_branch}
  Commit: {current_git_commit}
  Working tree: {current_working_tree_status}
  {Uncommitted files: X files} (if not clean)

FILES THAT WILL BE RESTORED:
  ✓ docs/features/feature-log.json
    - Current: {current_feature_count} features (last modified: {current_last_modified})
    - Checkpoint: {checkpoint_feature_count} features (last modified: {checkpoint_last_modified})
    - Changes: {difference_description}

  {Additional files listed similarly}

FEATURES AFFECTED:
  {List of features that will be removed, restored, or changed}
  - Feature #{id} "{title}" will be {removed/restored/changed}
    - Created: {created_at}
    - State: {state}
    - User stories: {YES/NO} (will be {lost/restored})
    - Implementation log: {YES/NO} (will be {lost/restored})

{If no features affected: "No features will be affected by this rollback"}

WARNINGS:
  {If working tree not clean:}
  ⚠ You have {count} uncommitted changes in your working tree
  ⚠ Consider committing or stashing before rollback
  ⚠ Rollback may create additional uncommitted changes

  {If features will be removed:}
  ⚠ Feature directories will remain on disk but not tracked in feature log
  ⚠ You may want to manually delete: docs/features/{id}/

  {If implementation progress will be lost:}
  ⚠ This will undo {count} completed stories
  ⚠ You will need to re-implement these stories

ROLLBACK SCOPE:
  - This will restore {count} file(s)
  - This will NOT affect git commits or branches
  - This will NOT delete files from disk (only updates tracked files)
  - A pre-rollback checkpoint will be created automatically

To execute this rollback, run:
  /rollback {checkpoint_id} --confirm

To cancel, just wait or run any other command (no changes made yet)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

5. **Continue to confirmation** (Step 5)

### Step 5: Handle Confirmation

Handle user confirmation before executing rollback:

#### Step 5.1: Check Confirm Flag

1. **If --confirm flag is set**:
   - Skip confirmation prompt
   - Log that rollback was executed with --confirm flag
   - Continue to Step 6 (Create Pre-Rollback Checkpoint)

2. **If --confirm flag NOT set**:
   - Continue to confirmation prompt (Step 5.2)

#### Step 5.2: Display Confirmation Prompt

After showing preview (Step 4), display confirmation prompt:

```
⚠ CONFIRMATION REQUIRED ⚠

This rollback will restore {count} file(s) from checkpoint created {time_ago}.

Type 'yes' to execute rollback (with pre-rollback safety checkpoint)
Type 'no' to cancel (no changes will be made)

Execute rollback? (yes/no):
```

#### Step 5.3: Wait for User Response

1. **Wait for user input** (timeout after 60 seconds)

2. **If user types "yes"** (case-insensitive):
   - Output: "Executing rollback..."
   - Continue to Step 6 (Create Pre-Rollback Checkpoint)

3. **If user types "no"** (case-insensitive):
   - Output: "Rollback cancelled - no changes made"
   - Exit gracefully

4. **If user types anything else or timeout**:
   - Output: "Invalid response or timeout - rollback cancelled"
   - Exit gracefully

### Step 6: Create Pre-Rollback Checkpoint

Before executing rollback, create a safety checkpoint of the current state:

1. **Generate pre-rollback checkpoint ID**:
   - Format: `checkpoint-{current_timestamp}-pre-rollback-{original_checkpoint_id}`
   - Example: `checkpoint-20251019T174530Z-pre-rollback-checkpoint-20251019T123045Z-feature-planning`

2. **Create checkpoint directory**:
   ```bash
   mkdir -p .checkpoints/{pre_rollback_checkpoint_id}
   ```

3. **Copy current versions of files that will be restored**:
   - For each file in original checkpoint's filesCheckpointed array:
     - If file exists currently:
       - Copy to pre-rollback checkpoint directory
       - Preserve directory structure
     - If file doesn't exist currently:
       - Note in metadata that file didn't exist

4. **Capture current git state**:
   - Branch, commit hash, working tree status
   - List of uncommitted files

5. **Create pre-rollback metadata**:
   ```json
   {
     "checkpointId": "{pre_rollback_checkpoint_id}",
     "createdAt": "{current_timestamp}",
     "operation": "pre-rollback",
     "triggeredBy": "automatic (before rollback)",
     "description": "Safety checkpoint before rollback to {original_checkpoint_id}",
     "gitState": { /* current git state */ },
     "filesCheckpointed": [ /* files being backed up */ ],
     "rollbackContext": {
       "originalCheckpoint": "{original_checkpoint_id}",
       "rollbackReason": "User-initiated rollback"
     },
     "systemState": { /* current system state */ }
   }
   ```

6. **Write metadata and git info files**

7. **Validate pre-rollback checkpoint creation**:
   - Verify all files copied successfully
   - Verify metadata written correctly
   - If validation fails:
     - Display error message:
```
Error: Failed to create pre-rollback checkpoint

Status: Could not backup current state before rollback
Impact: Rollback aborted for safety

Remediation:
1. Check disk space: df -h
2. Check .checkpoints/ directory permissions
3. Ensure no file locks on feature-log.json
4. Try rollback again
```
     - STOP execution immediately (rollback NOT executed)

8. **Output success message**:
   ```
   ✓ Created pre-rollback checkpoint: {pre_rollback_checkpoint_id}
   ```

9. **Continue to Step 7** (Execute Rollback)

### Step 7: Execute Rollback

Restore files from the checkpoint:

#### Step 7.1: Prepare Restoration

1. **Create temporary directory for atomic restoration**:
   ```bash
   mkdir -p .checkpoints/.tmp-rollback-{timestamp}
   ```

2. **For each file in checkpoint's filesCheckpointed array**:
   - Copy file from checkpoint to temporary directory
   - Preserve directory structure

3. **Validate copied files**:
   - For JSON files: Validate JSON syntax
   - Check file sizes are reasonable (not empty, not corrupted)
   - If any validation fails:
     - Clean up temporary directory
     - Display error message:
```
Error: Checkpoint file validation failed

File: {file_path}
Issue: {validation_error}
Status: Rollback aborted

The checkpoint appears to be corrupted. Your system state is unchanged.

Remediation:
1. Try a different checkpoint: /rollback
2. Restore from git if needed
3. Contact support if checkpoint is critical
```
     - STOP execution immediately

#### Step 7.2: Execute Atomic Restoration

For each file being restored:

1. **Atomic file replacement**:
   ```bash
   # Write to temp file in target directory
   cp .checkpoints/.tmp-rollback-{timestamp}/{file_path} {file_path}.rollback-tmp

   # Atomic move (replaces existing file)
   mv {file_path}.rollback-tmp {file_path}
   ```

2. **Track restored files** for reporting

3. **If any restoration fails**:
   - Immediately stop further restorations
   - Attempt to restore from pre-rollback checkpoint
   - Display error message:
```
Error: File restoration failed

File: {file_path}
Status: Partial rollback occurred

Attempting to restore from pre-rollback checkpoint...
{Result of restoration attempt}

Remediation:
1. Check current state: cat docs/features/feature-log.json | python3 -m json.tool
2. If corrupted, restore from: .checkpoints/{pre_rollback_checkpoint_id}
3. Contact support if needed
```
   - STOP execution

#### Step 7.3: Clean Up

1. **Remove temporary directory**:
   ```bash
   rm -rf .checkpoints/.tmp-rollback-{timestamp}
   ```

2. **Validate all restored files**:
   - For each restored file:
     - If JSON: Validate syntax
     - Check file exists and is readable
     - If any validation fails:
       - Display warning (not error, rollback already executed):
```
Warning: Restored file may have issues

File: {file_path}
Issue: {validation_issue}
Status: File was restored but validation flagged potential problem

Recommended actions:
1. Manually inspect the file: cat {file_path}
2. Validate JSON syntax: python3 -m json.tool {file_path}
3. If corrupted, restore from pre-rollback: .checkpoints/{pre_rollback_checkpoint_id}
```

3. **Continue to Step 8** (Log Rollback)

### Step 8: Log Rollback in History

Record the rollback in rollback history for audit trail:

1. **Read existing rollback history** (if exists):
   ```bash
   if [ -f .checkpoints/rollback-history.json ]; then
     cat .checkpoints/rollback-history.json
   fi
   ```

2. **If rollback-history.json doesn't exist, create initial structure**:
   ```json
   {
     "rollbacks": []
   }
   ```

3. **Create rollback entry**:
   ```json
   {
     "rollbackId": "rollback-{current_timestamp}",
     "executedAt": "{current_timestamp}",
     "checkpointRestored": "{checkpoint_id}",
     "triggeredBy": "manual",
     "reason": "User-initiated rollback via /rollback command",
     "preRollbackCheckpoint": "{pre_rollback_checkpoint_id}",
     "filesRestored": [ /* array of restored file paths */ ],
     "gitStateBeforeRollback": {
       "branch": "{current_branch}",
       "commitHash": "{current_commit}",
       "workingTreeClean": {true/false},
       "uncommittedFiles": [ /* list of uncommitted files before rollback */ ]
     },
     "gitStateAfterRollback": {
       "branch": "{current_branch}",  // Same as before (rollback doesn't change branch)
       "commitHash": "{current_commit}",  // Same as before
       "workingTreeClean": {true/false},  // May change if restored files differ
       "uncommittedFiles": [ /* list of uncommitted files after rollback */ ]
     },
     "validationResults": {
       "featureLogValid": {true/false},
       "jsonSyntaxValid": {true/false},
       "filesIntact": {true/false}
     },
     "notes": "{summary of what was rolled back}"
   }
   ```

4. **Append rollback entry to history**:
   - Read current rollback-history.json
   - Add new entry to rollbacks array
   - Write updated rollback-history.json

5. **Validate history file written correctly**:
   ```bash
   python3 -c "import json; json.load(open('.checkpoints/rollback-history.json'))"
   ```

   - If validation fails:
     - Display warning (not error - rollback already completed):
```
Warning: Failed to update rollback history

Status: Rollback was successful but history log failed to update
Impact: No audit trail of this rollback

The rollback was completed successfully. You may want to manually
document this rollback for your records.
```

6. **Continue to Step 9** (Report Results)

### Step 9: Report Rollback Results

Provide comprehensive report of rollback execution:

```
Rollback Completed Successfully
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ROLLBACK SUMMARY:
  Checkpoint restored: {checkpoint_id}
  Operation: {operation}
  Created: {checkpoint_created_at} ({time_ago})

FILES RESTORED:
  ✓ docs/features/feature-log.json
  {Additional files if any}

  Total: {count} file(s) restored

SYSTEM STATE:
  Before: {previous_feature_count} features ({previous_state_distribution})
  After: {current_feature_count} features ({current_state_distribution})

FEATURES AFFECTED:
  {List of features removed, restored, or changed}
  - Feature #{id} "{title}": {removed/restored/changed}

GIT STATUS:
  Branch: {current_branch} (unchanged)
  Commit: {current_commit} (unchanged)
  Working tree: {clean/dirty}
  {Uncommitted changes: X files} (if dirty)

SAFETY CHECKPOINT:
  Pre-rollback backup: {pre_rollback_checkpoint_id}
  Location: .checkpoints/{pre_rollback_checkpoint_id}

  To undo this rollback (restore to pre-rollback state):
    /rollback {pre_rollback_checkpoint_id}

NEXT STEPS:
  {If working tree dirty:}
  - Review uncommitted changes: git status
  - Commit changes: git add . && git commit -m "After rollback to {checkpoint_id}"

  {If features were removed:}
  - Manually delete feature directories if needed: rm -rf docs/features/{id}

  {If implementation was rolled back:}
  - Re-run implementation: /implement feature {id}

ROLLBACK HISTORY:
  This rollback has been logged in: .checkpoints/rollback-history.json
  Rollback ID: rollback-{timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Report

Provide a summary that includes:
- Operation mode (list or rollback)
- If listing: Number of checkpoints available
- If rolling back: Checkpoint ID restored, files restored count, features affected
- Pre-rollback safety checkpoint created (if rollback executed)
- Validation results for restored files
- Git status before and after rollback
- Next steps and recommendations
- Location of rollback history log

## Examples

### Example 1: List Available Checkpoints

**Command**: `/rollback`

**Output**:
```
Available Checkpoints
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID: checkpoint-20251019T150000Z-implement-5
Created: 2025-10-19 15:00:00 (2 hours ago)
Operation: implement-5
Triggered by: /implement command
Description: Automatic checkpoint before implementing Feature #5
Files backed up: 3 files (feature-log.json, user-stories.md, implementation-log.json)

───────────────────────────────────────────────────────────────────────────────────────

ID: checkpoint-20251019T123045Z-feature-planning
Created: 2025-10-19 12:30:45 (5 hours ago)
Operation: feature-planning
Triggered by: /feature command
Description: Automatic checkpoint before feature planning
Files backed up: 1 file (feature-log.json)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total: 2 checkpoints available

To rollback to a checkpoint:
  /rollback {checkpoint-id}
```

### Example 2: Preview Rollback (No Confirmation)

**Command**: `/rollback checkpoint-20251019T123045Z-feature-planning`

**Output**:
```
Rollback Preview: checkpoint-20251019T123045Z-feature-planning
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHECKPOINT INFORMATION:
  Created: 2025-10-19 12:30:45 (5 hours ago)
  Operation: feature-planning
  Triggered by: /feature command
  Description: Automatic checkpoint before feature planning

GIT STATE AT CHECKPOINT:
  Branch: main
  Commit: abc123def456
  Working tree: clean

CURRENT GIT STATE:
  Branch: feature/5-architecture-improvements
  Commit: def789abc012
  Working tree: dirty
  Uncommitted files: 2 files

FILES THAT WILL BE RESTORED:
  ✓ docs/features/feature-log.json
    - Current: 6 features (last modified: 2025-10-19 14:30:00)
    - Checkpoint: 5 features (last modified: 2025-10-19 12:00:00)
    - Changes: 1 feature will be removed

FEATURES AFFECTED:
  - Feature #6 "New Feature Title" will be removed
    - Created: 2025-10-19 14:15:00
    - State: planned
    - User stories: YES (will be lost)
    - Implementation log: NO

WARNINGS:
  ⚠ You have 2 uncommitted changes in your working tree
  ⚠ Consider committing or stashing before rollback
  ⚠ Feature #6 directory will remain on disk but not tracked in feature log

ROLLBACK SCOPE:
  - This will restore 1 file
  - This will NOT affect git commits or branches
  - This will NOT delete files from disk (only updates feature log)
  - A pre-rollback checkpoint will be created automatically

To execute this rollback, run:
  /rollback checkpoint-20251019T123045Z-feature-planning --confirm

To cancel, just wait or run any other command (no changes made yet)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠ CONFIRMATION REQUIRED ⚠

This rollback will restore 1 file(s) from checkpoint created 5 hours ago.

Type 'yes' to execute rollback (with pre-rollback safety checkpoint)
Type 'no' to cancel (no changes will be made)

Execute rollback? (yes/no): no

Rollback cancelled - no changes made
```

### Example 3: Execute Rollback with Confirmation

**Command**: `/rollback checkpoint-20251019T123045Z-feature-planning --confirm`

**Output**:
```
Pre-flight validation passed - proceeding with rollback operation

✓ Created pre-rollback checkpoint: checkpoint-20251019T174530Z-pre-rollback-checkpoint-20251019T123045Z-feature-planning

Executing rollback...
✓ Restored docs/features/feature-log.json

Rollback Completed Successfully
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ROLLBACK SUMMARY:
  Checkpoint restored: checkpoint-20251019T123045Z-feature-planning
  Operation: feature-planning
  Created: 2025-10-19 12:30:45 (5 hours ago)

FILES RESTORED:
  ✓ docs/features/feature-log.json

  Total: 1 file(s) restored

SYSTEM STATE:
  Before: 6 features (5 deployed, 1 planned)
  After: 5 features (5 deployed)

FEATURES AFFECTED:
  - Feature #6 "New Feature Title": removed

GIT STATUS:
  Branch: feature/5-architecture-improvements (unchanged)
  Commit: def789abc012 (unchanged)
  Working tree: dirty
  Uncommitted changes: 3 files (2 previous + 1 from rollback)

SAFETY CHECKPOINT:
  Pre-rollback backup: checkpoint-20251019T174530Z-pre-rollback-checkpoint-20251019T123045Z-feature-planning
  Location: .checkpoints/checkpoint-20251019T174530Z-pre-rollback-checkpoint-20251019T123045Z-feature-planning

  To undo this rollback (restore to pre-rollback state):
    /rollback checkpoint-20251019T174530Z-pre-rollback-checkpoint-20251019T123045Z-feature-planning

NEXT STEPS:
  - Review uncommitted changes: git status
  - Commit changes: git add . && git commit -m "After rollback to checkpoint-20251019T123045Z-feature-planning"
  - Manually delete feature directory if needed: rm -rf docs/features/6

ROLLBACK HISTORY:
  This rollback has been logged in: .checkpoints/rollback-history.json
  Rollback ID: rollback-20251019T174530Z

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Example 4: No Checkpoints Available

**Command**: `/rollback`

**Output**:
```
No checkpoints available

Status: .checkpoints/ directory exists but contains no checkpoints
Command: /rollback

Information:
Checkpoints are created automatically before major operations.
Run any of these commands to create checkpoints:
- /feature "feature description"
- /implement feature {id}
- /summarise
- /fix

You can also create manual checkpoints with:
  /checkpoint "description"
```

### Example 5: Checkpoint Not Found Error

**Command**: `/rollback checkpoint-20251019T999999Z-nonexistent`

**Output**:
```
Error: Checkpoint not found

Checkpoint ID: checkpoint-20251019T999999Z-nonexistent
Expected location: .checkpoints/checkpoint-20251019T999999Z-nonexistent
Status: Directory does not exist

To see available checkpoints, run:
  /rollback

Remediation:
1. Verify the checkpoint ID is correct (check for typos)
2. List available checkpoints with /rollback
3. Use an existing checkpoint ID from the list
```

## Best Practices

### When to Use Rollback

1. **After Mistakes**: Feature planning went wrong, want to replan differently
2. **Implementation Issues**: Implementation created problems, want to reset and retry
3. **Experimental Changes**: Tried something that didn't work, restore to clean state
4. **Accidental Operations**: Ran wrong command, undo the changes
5. **Testing**: Create checkpoint, test changes, rollback to clean state

### When NOT to Use Rollback

1. **For Git Commits**: Use `git revert` or `git reset` for code changes
2. **For File Deletions**: Rollback doesn't restore deleted files from disk
3. **For Bug Fixes**: Fix issues directly rather than rolling back
4. **For Minor Edits**: Just edit files directly for small changes

### Rollback Safety Tips

1. **Always Preview First**: Run without --confirm to see what will change
2. **Check Git State**: Commit or stash uncommitted changes before rollback
3. **Review Warnings**: Pay attention to what data will be lost
4. **Use Pre-Rollback Checkpoint**: You can undo the rollback if needed
5. **Manual Cleanup**: Delete feature directories manually if needed

### Understanding Rollback Scope

- **What Rollback DOES**: Restores tracked files (feature-log.json, user-stories.md, implementation-log.json)
- **What Rollback DOESN'T DO**:
  - Doesn't affect git commits or branches
  - Doesn't delete files or directories from disk
  - Doesn't modify source code or application files
  - Doesn't affect .checkpoints/ directory itself

## Notes

- Rollback is a file restoration operation, not a version control operation
- Git state (commits, branches) is never modified by rollback
- Files on disk (feature directories) are not deleted, only tracking is updated
- Pre-rollback checkpoint ensures rollback can be undone
- Rollback history provides audit trail of all rollbacks
- Checkpoints should be created by commands automatically, not manually (unless testing)
- Rollback works offline (no network required)
- Multiple rollbacks can be chained (rollback a rollback)

## Integration with Commands

This rollback command integrates with checkpoint creation in:
- `/feature` - Creates checkpoint before feature planning
- `/implement` - Creates checkpoint before implementation
- `/summarise` - Creates checkpoint before summarization
- `/fix` - Creates checkpoint before bug processing

Each command should call checkpoint creation helper (documented in .claude/helpers/checkpoint-system.md) before making changes.

## References

- Checkpoint system design: `.claude/helpers/checkpoint-system.md`
- Pre-flight validation: `.claude/helpers/pre-flight-validation.md`
- Feature state tracking: `docs/features/feature-state-system.md`
