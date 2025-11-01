# Claude Code Hooks Documentation

This directory contains hook scripts that automatically execute after specific Claude Code commands complete.

## Overview

Hooks are configured in `.claude/settings.json` and trigger automatically when certain conditions are met in the Claude Code output. The hooks system uses JSON payloads embedded in the assistant's output to pass data to the hook scripts.

## Available Hooks

### 1. stop-push-and-close.sh

**Purpose**: Automatically commits, pushes, and closes GitHub issues after the `/fix` command completes.

**Trigger Pattern**: `## Post Fix Push and Close`

**Payload Structure**:
```json
{
    "issueID": "123",
    "runID": "optional-run-id"
}
```

**Actions**:
1. Stages all changes (`git add .`)
2. Commits with message: `Fix issue #{issueID}`
3. Pushes to remote repository
4. Closes the GitHub issue with a comment

**Prerequisites**:
- `git` command available
- `gh` (GitHub CLI) installed and authenticated
- Valid GitHub issue ID in payload

### 2. stop-updateversion-push.sh

**Purpose**: Automatically commits and pushes version changes after the `/updateversion` command completes.

**Trigger Pattern**: `## Post UpdateVersion Push`

**Payload Structure**:
```json
{
    "frontendVersion": "1.0.6",
    "backendVersion": "1.0.6"
}
```

**Actions**:
1. Validates that both frontend and backend versions are present
2. Stages all changes (`git add .`)
3. Commits with message: `Version updated to {version}`
4. Pushes to remote repository

**Prerequisites**:
- `git` command available
- Valid version strings in payload

**Version Handling**:
- Uses `frontendVersion` as the primary version
- Warns if frontend and backend versions don't match
- Continues with operation even if versions differ

### 3. stop-feature-push-PR.sh

**Purpose**: Automatically creates a GitHub Pull Request after the `/push` command completes successfully for a feature branch.

**Trigger Pattern**: `## Post Feature Push Create PR`

**Payload Structure**:
```json
{
    "featureID": "5",
    "featureTitle": "User Authentication System",
    "featureBranch": "feature/5-user-authentication-system"
}
```

**Actions**:
1. Validates that feature branch exists on remote
2. Reads user stories from `docs/features/{featureID}/user-stories.md`
3. Extracts feature overview and user stories list
4. Creates PR using `gh pr create` with standardized title format
5. PR body includes feature summary, user stories, and test plan

**Prerequisites**:
- `git` command available
- `gh` (GitHub CLI) installed and authenticated
- Feature branch pushed to remote repository
- User stories file exists at `docs/features/{featureID}/user-stories.md` (optional, will use minimal description if missing)

**PR Format**:
- Title: `Feature {featureID}: {featureTitle}`
- Body: Includes overview, user stories implemented, test plan checklist, and Claude Code attribution
- Target: Repository default branch (usually `main`)

**Error Handling**:
- Validates all required payload fields (featureID, featureTitle, featureBranch)
- Checks that feature branch exists on remote before creating PR
- Provides manual PR creation command if automatic creation fails
- Continues gracefully if user stories file is missing

## Hook Configuration

Hooks are registered in `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./.claude/hooks/scripts/stop-push-and-close.sh"
          },
          {
            "type": "command",
            "command": "./.claude/hooks/scripts/stop-updateversion-push.sh"
          },
          {
            "type": "command",
            "command": "./.claude/hooks/scripts/stop-feature-push-PR.sh"
          }
        ]
      }
    ]
  }
}
```

## How Hooks Work

1. **Trigger Detection**: When a command completes, Claude Code checks the assistant's output for specific patterns (e.g., `## Post UpdateVersion Push`)

2. **Payload Extraction**: The hook script uses `jq` to extract JSON payloads from the transcript

3. **Validation**: Each hook validates its prerequisites and required payload fields

4. **Execution**: If all validations pass, the hook performs its actions (commit, push, close issue, etc.)

5. **Logging**: All hook operations are logged to `/tmp/stop-{hookname}-debug.log`

## Adding New Hooks

To create a new hook:

1. **Create the script** in `.claude/hooks/scripts/`
   - Use the existing scripts as templates
   - Define a unique trigger pattern (e.g., `## Post MyCommand Action`)
   - Extract required payload fields using `jq`
   - Implement validation and error handling
   - Log all operations to debug log file

2. **Make it executable**:
   ```bash
   chmod +x .claude/hooks/scripts/my-new-hook.sh
   ```

3. **Register in settings.json**:
   ```json
   {
     "type": "command",
     "command": "./.claude/hooks/scripts/my-new-hook.sh"
   }
   ```

4. **Update command output**: Ensure the command includes the trigger pattern and payload in its output

## Debugging

Each hook writes detailed logs to `/tmp/stop-{hookname}-debug.log`. To debug hook execution:

```bash
# View updateversion hook logs
tail -f /tmp/stop-updateversion-push-debug.log

# View fix/push/close hook logs
tail -f /tmp/stop-hook-debug.log

# View feature PR creation hook logs
tail -f /tmp/stop-feature-push-PR-debug.log
```

Log entries include:
- Trigger timestamp
- Working directory
- Input received
- Transcript path and validation
- Pattern matching results
- Payload extraction
- All git operations
- Success/failure messages

## Error Handling

All hooks follow these principles:
- **Fail gracefully**: Never block command completion
- **Log errors**: All errors written to debug log
- **Early exit**: Exit with code 0 on validation failures
- **Clear messages**: User-facing errors written to stderr and log
- **Safe operations**: Warn on potentially dangerous operations (e.g., pushing to main)

## Security Considerations

- Hooks run with the same permissions as the user
- Git credentials must be properly configured
- GitHub CLI must be authenticated for issue operations
- All scripts validate inputs before executing commands
- No sensitive data should be logged (credentials, tokens, etc.)
