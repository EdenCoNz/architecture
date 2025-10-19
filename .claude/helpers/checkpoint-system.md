# Checkpoint and Rollback System

## Purpose

The checkpoint and rollback system provides a safety net for major architecture operations by creating automated backups before destructive changes, enabling users to revert to previous states when something goes wrong or when they want to try a different approach.

## Design Principles

1. **Automatic Checkpoint Creation**: Checkpoints are created automatically before major operations, not requiring user intervention
2. **Lightweight Storage**: Checkpoints store only essential files, minimizing disk space usage
3. **Clear Rollback Preview**: Users see exactly what will be reverted before executing rollback
4. **Audit Trail**: All checkpoints and rollbacks are logged for history tracking
5. **Safe by Default**: Rollback operations require confirmation and won't overwrite uncommitted changes
6. **Time-Based Retention**: Old checkpoints can be automatically pruned to prevent disk bloat

## Checkpoint Storage

### Directory Structure

```
.checkpoints/
├── checkpoint-{timestamp}-{operation}/
│   ├── metadata.json              # Checkpoint metadata
│   ├── feature-log.json           # Backed up feature log
│   ├── feature-{id}/              # Feature-specific files
│   │   ├── user-stories.md
│   │   └── implementation-log.json
│   └── git-info.txt               # Git state information
├── checkpoint-{timestamp}-{operation}/
│   └── ...
└── rollback-history.json          # History of all rollbacks
```

### Checkpoint Location

Checkpoints are stored in `.checkpoints/` directory at project root. This directory is excluded from git via `.gitignore` as checkpoints are local safety nets, not version-controlled artifacts.

## What Gets Checkpointed

### Core Files (Always Checkpointed)

1. **Feature Log**: `docs/features/feature-log.json`
   - Central registry of all features
   - Tracks feature states and history
   - Critical for restoration

2. **User Stories**: `docs/features/{id}/user-stories.md`
   - Feature planning artifacts
   - Created by /feature command
   - Needed for feature rollback

3. **Implementation Logs**: `docs/features/{id}/implementation-log.json`
   - Implementation progress tracking
   - Created during /implement command
   - Needed for implementation rollback

4. **Git Information**: Current branch, commit hash, working tree status
   - Context about git state at checkpoint time
   - Not restored (informational only)

### Conditional Files (Context-Dependent)

1. **Bug Files**: `docs/features/{featureId}/bugs/{bugId}/*`
   - Only checkpointed when operating on bug fixes
   - User stories and implementation logs for bugs

2. **Metrics**: `docs/metrics/metrics.json`
   - Only checkpointed before /summarise (since it updates metrics)
   - Optional - regeneratable from logs

## When Checkpoints Are Created

### Automatic Checkpoint Triggers

| Command | Checkpoint Name | Reason | Files Checkpointed |
|---------|----------------|--------|-------------------|
| `/feature` | `checkpoint-{timestamp}-feature-planning` | Before creating new feature | feature-log.json only (user stories don't exist yet) |
| `/implement` | `checkpoint-{timestamp}-implement-{id}` | Before starting implementation | feature-log.json, user-stories.md, implementation-log.json (if exists) |
| `/summarise` | `checkpoint-{timestamp}-summarise` | Before summarizing features | feature-log.json, all implementation logs for features being summarized |
| `/fix` | `checkpoint-{timestamp}-fix-{issue}` | Before processing GitHub issue | feature-log.json only (bug files don't exist yet) |

### Manual Checkpoint Creation

Users can create manual checkpoints via:
```
/checkpoint "description of why creating checkpoint"
```

This is useful before experimental changes or major manual edits to system files.

## Checkpoint Metadata Schema

Each checkpoint includes a `metadata.json` file:

```json
{
  "checkpointId": "checkpoint-20251019T123045Z-feature-planning",
  "createdAt": "2025-10-19T12:30:45Z",
  "operation": "feature-planning",
  "triggeredBy": "/feature command",
  "description": "Automatic checkpoint before feature planning",
  "gitState": {
    "branch": "main",
    "commitHash": "abc123def456",
    "workingTreeClean": true,
    "uncommittedFiles": []
  },
  "filesCheckpointed": [
    "docs/features/feature-log.json"
  ],
  "featureContext": {
    "featureId": null,
    "featureTitle": null,
    "operation": "create"
  },
  "systemState": {
    "totalFeatures": 5,
    "featuresInProgress": 1,
    "lastModified": "2025-10-19T12:00:00Z"
  }
}
```

## Rollback Operations

### Rollback Workflow

1. **List Available Checkpoints**: User runs `/rollback` to see all checkpoints
2. **Select Checkpoint**: User runs `/rollback {checkpoint-id}` to preview changes
3. **Preview Changes**: System shows exactly what will be reverted
4. **Confirm Rollback**: User confirms (or uses `--confirm` flag to skip)
5. **Execute Rollback**: System restores files from checkpoint
6. **Log Rollback**: Rollback recorded in rollback-history.json
7. **Report Results**: Summary of what was restored

### Rollback Preview

Before executing rollback, system shows:

```
Rollback Preview: checkpoint-20251019T123045Z-feature-planning
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHECKPOINT INFORMATION:
  Created: 2025-10-19 12:30:45 (2 hours ago)
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
  Working tree: 2 uncommitted changes

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

WARNING:
  ⚠ You have 2 uncommitted changes in your working tree
  ⚠ Consider committing or stashing before rollback
  ⚠ Feature #6 files will remain on disk but not tracked in feature log

ROLLBACK SCOPE:
  - This will restore 1 file
  - This will NOT affect git commits or branches
  - This will NOT delete files from disk (only updates feature log)

To execute this rollback, run:
  /rollback checkpoint-20251019T123045Z-feature-planning --confirm

To cancel, press Ctrl+C or just wait (no changes made yet)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Rollback Safety Checks

Before executing rollback, system validates:

1. **Checkpoint Exists**: Checkpoint ID is valid and files exist
2. **Working Tree**: Warns if uncommitted changes (doesn't block)
3. **File Integrity**: Checkpoint files are readable and valid
4. **No Concurrent Operations**: No other commands currently running (based on file locks)
5. **Git Repository**: Still a valid git repository
6. **Disk Space**: Sufficient space for restoration (unlikely issue but checked)

### Rollback Execution

1. **Create Pre-Rollback Backup**: Checkpoint current state before rollback
   - Ensures rollback can be undone if needed
   - Stored as `checkpoint-{timestamp}-pre-rollback-{original-checkpoint-id}`

2. **Restore Files**: Copy files from checkpoint to their original locations
   - Atomic operation where possible (write to temp, then move)
   - All-or-nothing restoration (if any file fails, rollback the rollback)

3. **Update Rollback History**: Record rollback in rollback-history.json

4. **Validate Restoration**: Check that files were restored correctly
   - JSON syntax validation for restored JSON files
   - File size and checksum comparison

5. **Report Success**: Show summary of what was restored

## Rollback History Tracking

All rollbacks are logged in `.checkpoints/rollback-history.json`:

```json
{
  "rollbacks": [
    {
      "rollbackId": "rollback-20251019T150000Z",
      "executedAt": "2025-10-19T15:00:00Z",
      "checkpointRestored": "checkpoint-20251019T123045Z-feature-planning",
      "triggeredBy": "manual",
      "reason": "User wanted to replan feature differently",
      "preRollbackCheckpoint": "checkpoint-20251019T145959Z-pre-rollback-checkpoint-20251019T123045Z-feature-planning",
      "filesRestored": [
        "docs/features/feature-log.json"
      ],
      "gitStateBeforeRollback": {
        "branch": "feature/5-architecture-improvements",
        "commitHash": "def789abc012",
        "workingTreeClean": false,
        "uncommittedFiles": ["file1.md", "file2.json"]
      },
      "gitStateAfterRollback": {
        "branch": "feature/5-architecture-improvements",
        "commitHash": "def789abc012",
        "workingTreeClean": false,
        "uncommittedFiles": ["file1.md", "file2.json", "docs/features/feature-log.json"]
      },
      "validationResults": {
        "featureLogValid": true,
        "jsonSyntaxValid": true,
        "filesIntact": true
      },
      "notes": "Successfully restored feature log to state before Feature #6 creation"
    }
  ]
}
```

## Checkpoint Cleanup and Retention

### Retention Policy

- **Recent Checkpoints** (< 7 days old): Always kept
- **Pre-Rollback Checkpoints**: Kept for 30 days (safety net)
- **Manual Checkpoints**: Kept for 90 days (user-initiated)
- **Automatic Checkpoints** (> 7 days old): Pruned based on rules:
  - Keep at most 1 checkpoint per day for days 7-30
  - Keep at most 1 checkpoint per week for weeks 5-12
  - Delete checkpoints older than 90 days

### Cleanup Command

Users can manually clean up checkpoints:
```
/rollback --cleanup
```

This shows checkpoints that would be deleted and asks for confirmation.

### Checkpoint Size Management

- Each checkpoint is typically 1-100 KB (text files only)
- Average project might have 20-50 checkpoints = 1-5 MB
- Cleanup prevents unbounded growth

## Common Rollback Scenarios

### Scenario 1: Undo Feature Planning

**Situation**: Created feature with /feature but user stories aren't right

**Solution**:
```bash
/rollback  # List checkpoints
/rollback checkpoint-20251019T123045Z-feature-planning
# Review preview
/rollback checkpoint-20251019T123045Z-feature-planning --confirm
```

**Result**: Feature removed from feature log, user stories directory remains but can be manually deleted

### Scenario 2: Undo Implementation Progress

**Situation**: Implementation went wrong, want to restart from beginning

**Solution**:
```bash
/rollback checkpoint-20251019T140000Z-implement-5
# Review preview showing implementation log will be cleared
/rollback checkpoint-20251019T140000Z-implement-5 --confirm
```

**Result**: Implementation log reset to checkpoint state, can re-run /implement to start fresh

### Scenario 3: Undo Summarization

**Situation**: Accidentally summarized features, want to restore full logs

**Solution**:
```bash
/rollback checkpoint-20251019T160000Z-summarise
# Review preview showing features will be unsummarised
/rollback checkpoint-20251019T160000Z-summarise --confirm
```

**Result**: Features marked as unsummarised, implementation logs restored

### Scenario 4: Undo Multiple Operations

**Situation**: Want to go back several operations

**Solution**:
```bash
/rollback  # List all checkpoints chronologically
# Find the checkpoint from before all the unwanted changes
/rollback checkpoint-20251019T120000Z-feature-planning --confirm
```

**Result**: System restored to state before all subsequent operations

### Scenario 5: Experiment Safely

**Situation**: Want to try something risky

**Solution**:
```bash
/checkpoint "Before trying experimental feature structure"
# Make experimental changes
# If it doesn't work:
/rollback checkpoint-20251019T180000Z-manual-checkpoint --confirm
```

**Result**: Clean restoration to pre-experiment state

## Integration with Commands

### /feature Command Integration

Add to /feature command workflow (after Step 0 Pre-Flight Validation):

**Step 0.8: Create Automatic Checkpoint**
- Create checkpoint before feature creation
- Checkpoint ID: `checkpoint-{timestamp}-feature-planning`
- Files checkpointed: `docs/features/feature-log.json`
- Log checkpoint creation
- Continue with normal workflow

### /implement Command Integration

Add to /implement command workflow (after Step 0 Pre-Flight Validation):

**Step 0.11: Create Automatic Checkpoint**
- Create checkpoint before implementation starts
- Checkpoint ID: `checkpoint-{timestamp}-implement-{featureId}`
- Files checkpointed: `docs/features/feature-log.json`, user-stories.md, implementation-log.json (if exists)
- For bugs: Include bug-specific files
- Log checkpoint creation
- Continue with normal workflow

### /summarise Command Integration

Add to /summarise command workflow (after Step 0 Pre-Flight Validation):

**Step 0.7: Create Automatic Checkpoint**
- Create checkpoint before summarization
- Checkpoint ID: `checkpoint-{timestamp}-summarise`
- Files checkpointed: `docs/features/feature-log.json`, all implementation logs being summarized
- Log checkpoint creation
- Continue with normal workflow

### /fix Command Integration

Add to /fix command workflow (after Step 0 Pre-Flight Validation):

**Step 0.9: Create Automatic Checkpoint**
- Create checkpoint before bug processing
- Checkpoint ID: `checkpoint-{timestamp}-fix-{issueNumber}`
- Files checkpointed: `docs/features/feature-log.json`
- Log checkpoint creation
- Continue with normal workflow

## Error Handling

### Checkpoint Creation Errors

| Error | Cause | Remediation |
|-------|-------|-------------|
| Disk full | Insufficient disk space | Free up space, checkpoint will be skipped with warning |
| Permission denied | No write access to .checkpoints/ | Fix permissions: `chmod u+w .checkpoints/` |
| File locked | Another operation in progress | Wait for other operation to complete |
| Invalid JSON | feature-log.json corrupted | Fix JSON before proceeding, no checkpoint created |

### Rollback Errors

| Error | Cause | Remediation |
|-------|-------|-------------|
| Checkpoint not found | Invalid checkpoint ID | List checkpoints with `/rollback`, verify ID |
| Corrupted checkpoint | Checkpoint files damaged | Use different checkpoint, or restore from git |
| File conflicts | Target files locked | Close other programs, ensure files aren't in use |
| Validation failed | Restored files invalid | Rollback was not completed, system unchanged |

## Best Practices

### When to Use Rollback

1. **After Mistakes**: Undo operations that went wrong
2. **Before Experiments**: Create manual checkpoint, try something, rollback if it doesn't work
3. **After Bad Planning**: Replan features with better structure
4. **After Implementation Issues**: Reset implementation and try different approach
5. **When Testing**: Create checkpoint, test changes, rollback to clean state

### When NOT to Use Rollback

1. **For Git Operations**: Use `git revert` or `git reset` for code changes
2. **For File System Cleanup**: Manually delete unwanted files
3. **For Correcting Small Typos**: Just edit the files directly
4. **After Commits**: Rollback doesn't undo git commits (by design)

### Rollback Workflow Tips

1. **Always Preview First**: Run rollback without --confirm to see what will change
2. **Check Git State**: Commit or stash changes before rollback
3. **Read Warnings**: Pay attention to what will be lost
4. **Create Manual Checkpoints**: Before risky operations
5. **Keep Rollback History**: Don't delete rollback-history.json (helps understand past decisions)
6. **Verify After Rollback**: Check that restored state is correct

## Technical Implementation Details

### Checkpoint Creation Algorithm

```python
def create_checkpoint(operation, context):
    # 1. Generate checkpoint ID
    timestamp = current_iso_timestamp()
    checkpoint_id = f"checkpoint-{timestamp}-{operation}"

    # 2. Create checkpoint directory
    checkpoint_dir = f".checkpoints/{checkpoint_id}"
    mkdir(checkpoint_dir)

    # 3. Collect files to checkpoint
    files = determine_files_to_checkpoint(operation, context)

    # 4. Copy files to checkpoint directory
    for file_path in files:
        relative_path = remove_root(file_path)
        dest_path = f"{checkpoint_dir}/{relative_path}"
        mkdir_recursive(dirname(dest_path))
        copy_file(file_path, dest_path)

    # 5. Capture git state
    git_info = {
        "branch": git("rev-parse --abbrev-ref HEAD"),
        "commitHash": git("rev-parse HEAD"),
        "workingTreeClean": git("status --porcelain") == "",
        "uncommittedFiles": git("status --porcelain").split("\n")
    }

    # 6. Create metadata
    metadata = {
        "checkpointId": checkpoint_id,
        "createdAt": timestamp,
        "operation": operation,
        "triggeredBy": context.triggered_by,
        "description": context.description,
        "gitState": git_info,
        "filesCheckpointed": files,
        "featureContext": context.feature_context,
        "systemState": get_system_state()
    }

    # 7. Write metadata
    write_json(f"{checkpoint_dir}/metadata.json", metadata)

    # 8. Write git info (human-readable)
    write_text(f"{checkpoint_dir}/git-info.txt", format_git_info(git_info))

    return checkpoint_id
```

### Rollback Execution Algorithm

```python
def execute_rollback(checkpoint_id, confirm=False):
    # 1. Load checkpoint metadata
    checkpoint_dir = f".checkpoints/{checkpoint_id}"
    metadata = read_json(f"{checkpoint_dir}/metadata.json")

    # 2. Safety checks
    validate_checkpoint_exists(checkpoint_id)
    validate_checkpoint_integrity(checkpoint_dir)
    git_status = check_git_status()

    # 3. Show preview
    preview = generate_rollback_preview(metadata, git_status)
    print(preview)

    # 4. Get confirmation
    if not confirm:
        response = input("Execute rollback? (yes/no): ")
        if response.lower() != "yes":
            print("Rollback cancelled")
            return

    # 5. Create pre-rollback checkpoint
    pre_rollback_id = create_checkpoint(
        f"pre-rollback-{checkpoint_id}",
        context={"reason": "Safety checkpoint before rollback"}
    )

    # 6. Restore files
    restored_files = []
    for file_path in metadata["filesCheckpointed"]:
        source = f"{checkpoint_dir}/{file_path}"
        dest = f"{file_path}"

        # Atomic restore: write to temp, then move
        temp_dest = f"{dest}.rollback-tmp"
        copy_file(source, temp_dest)
        move_file(temp_dest, dest)
        restored_files.append(dest)

    # 7. Validate restoration
    for file_path in restored_files:
        if file_path.endswith(".json"):
            validate_json_syntax(file_path)

    # 8. Log rollback
    log_rollback(checkpoint_id, pre_rollback_id, restored_files)

    # 9. Report success
    print(f"Successfully restored {len(restored_files)} files")
    print(f"Pre-rollback backup: {pre_rollback_id}")

    return True
```

## Future Enhancements

### Phase 1 (Story #15 - Current)
- Basic checkpoint creation before major operations
- Rollback command with preview and confirmation
- Rollback history tracking

### Phase 2 (Future Stories)
- Selective rollback (restore only specific files from checkpoint)
- Checkpoint diffing (show what changed between checkpoints)
- Checkpoint search and filtering
- Checkpoint export/import for sharing

### Phase 3 (Advanced Features)
- Automatic checkpoint pruning based on retention policy
- Checkpoint compression for older checkpoints
- Incremental checkpoints (only store changed files)
- Checkpoint verification and repair

## References

- Pre-flight validation system: `.claude/helpers/pre-flight-validation.md`
- Feature state tracking: `docs/features/feature-state-system.md`
- Command structure patterns: `.claude/commands/*.md`

## Version History

- v1.0.0 (2025-10-19): Initial checkpoint and rollback system design
