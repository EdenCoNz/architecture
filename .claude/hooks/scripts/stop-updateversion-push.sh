#!/bin/bash
# Stop hook script for /updateversion command that pushes version changes

# Debug log file
DEBUG_LOG="/tmp/stop-updateversion-push-debug.log"
echo "=== UpdateVersion Hook triggered at $(date) ===" >> "$DEBUG_LOG"
echo "Working directory: $(pwd)" >> "$DEBUG_LOG"

# Read JSON input from stdin and extract transcript_path
INPUT=$(cat)
echo "Received input: $INPUT" >> "$DEBUG_LOG"

TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path')
echo "Extracted transcript path: $TRANSCRIPT_PATH" >> "$DEBUG_LOG"

# Expand tilde in path
TRANSCRIPT_PATH="${TRANSCRIPT_PATH/#\~/$HOME}"
echo "Expanded transcript path: $TRANSCRIPT_PATH" >> "$DEBUG_LOG"

if [ -z "$TRANSCRIPT_PATH" ]; then
    echo "Error: Transcript path is empty" | tee -a "$DEBUG_LOG" >&2
    exit 0
fi

if [ ! -f "$TRANSCRIPT_PATH" ]; then
    echo "Error: Transcript file not found at: $TRANSCRIPT_PATH" | tee -a "$DEBUG_LOG" >&2
    exit 0
fi

echo "Transcript file exists, size: $(wc -c < "$TRANSCRIPT_PATH") bytes" >> "$DEBUG_LOG"

# Show first few lines of transcript for debugging
echo "First 3 lines of transcript:" >> "$DEBUG_LOG"
head -n 3 "$TRANSCRIPT_PATH" >> "$DEBUG_LOG" 2>&1

# Check if the "Post UpdateVersion Push" pattern exists in the output with proper JSON structure
HAS_HOOK=$(jq -s -r '
  [.[] | select(.message.role == "assistant") | .message.content[]? | select(.type == "text") | .text]
  | last
  | if . != null and (. | test("## Post UpdateVersion Push\\s*\\n\\*\\*Payload\\*\\*:\\s*\\n\\{[\\s\\S]*?\\}")) then "true" else "false" end
' "$TRANSCRIPT_PATH" 2>>"$DEBUG_LOG")

echo "Has Post UpdateVersion Push hook: '$HAS_HOOK'" >> "$DEBUG_LOG"

# If no hook pattern found, exit early
if [ "$HAS_HOOK" != "true" ]; then
    echo "No Post UpdateVersion Push hook pattern found in output - exiting without action" >> "$DEBUG_LOG"
    echo "=== Hook completed (no action needed) ===" >> "$DEBUG_LOG"
    echo "" >> "$DEBUG_LOG"
    exit 0
fi

# Extract the JSON payload from the last assistant message
PAYLOAD_JSON=$(jq -s -r '
  [.[] | select(.message.role == "assistant") | .message.content[]? | select(.type == "text") | .text]
  | last
  | capture("## Post UpdateVersion Push\\s*\\n\\*\\*Payload\\*\\*:\\s*\\n(?<json>\\{[\\s\\S]*?\\})") // {}
  | .json // ""
' "$TRANSCRIPT_PATH" 2>>"$DEBUG_LOG")

echo "Extracted payload JSON: '$PAYLOAD_JSON'" >> "$DEBUG_LOG"

# Parse the version fields from the JSON payload
if [ -n "$PAYLOAD_JSON" ]; then
    FRONTEND_VERSION=$(echo "$PAYLOAD_JSON" | jq -r '.frontendVersion // empty' 2>>"$DEBUG_LOG")
    BACKEND_VERSION=$(echo "$PAYLOAD_JSON" | jq -r '.backendVersion // empty' 2>>"$DEBUG_LOG")

    echo "Extracted frontendVersion: '$FRONTEND_VERSION'" >> "$DEBUG_LOG"
    echo "Extracted backendVersion: '$BACKEND_VERSION'" >> "$DEBUG_LOG"

    # Validate versions exist and match
    if [ -z "$FRONTEND_VERSION" ] || [ "$FRONTEND_VERSION" = "null" ]; then
        echo "Error: No valid frontend version found in payload" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi

    if [ -z "$BACKEND_VERSION" ] || [ "$BACKEND_VERSION" = "null" ]; then
        echo "Error: No valid backend version found in payload" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi

    # Verify versions match
    if [ "$FRONTEND_VERSION" != "$BACKEND_VERSION" ]; then
        echo "Warning: Frontend and backend versions don't match" | tee -a "$DEBUG_LOG"
        echo "  Frontend: $FRONTEND_VERSION" | tee -a "$DEBUG_LOG"
        echo "  Backend: $BACKEND_VERSION" | tee -a "$DEBUG_LOG"
        # Continue with frontend version as primary
    fi

    NEW_VERSION="$FRONTEND_VERSION"
    echo "Using version: $NEW_VERSION" >> "$DEBUG_LOG"

    # Check prerequisites
    echo "Checking prerequisites..." >> "$DEBUG_LOG"

    if ! command -v git &> /dev/null; then
        echo "Error: git is not installed" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi

    # Verify we're in a git repository
    if ! git rev-parse --git-dir &> /dev/null; then
        echo "Error: Not in a git repository" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi

    echo "Prerequisites validated" >> "$DEBUG_LOG"

    # Get current branch
    CURRENT_BRANCH=$(git branch --show-current)
    echo "Current branch: $CURRENT_BRANCH" >> "$DEBUG_LOG"

    # Warn if on main/master but don't block
    if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
        echo "WARNING: Pushing to $CURRENT_BRANCH branch" | tee -a "$DEBUG_LOG"
    fi

    # Check if there are changes to commit
    if git diff --quiet && git diff --cached --quiet; then
        echo "No changes to commit - skipping git operations" >> "$DEBUG_LOG"
        echo "WARNING: No changes detected. Skipping commit and push." | tee -a "$DEBUG_LOG"
    else
        echo "Changes detected, proceeding with git operations..." >> "$DEBUG_LOG"

        # Stage all changes
        echo "Running: git add ." >> "$DEBUG_LOG"
        if ! git add . 2>>"$DEBUG_LOG"; then
            echo "Error: git add failed" | tee -a "$DEBUG_LOG" >&2
            exit 0
        fi
        echo "Successfully staged changes" >> "$DEBUG_LOG"

        # Commit with version message
        COMMIT_MSG="Version updated to ${NEW_VERSION}"
        echo "Running: git commit -m \"$COMMIT_MSG\"" >> "$DEBUG_LOG"
        if ! git commit -m "$COMMIT_MSG" 2>>"$DEBUG_LOG"; then
            echo "Error: git commit failed" | tee -a "$DEBUG_LOG" >&2
            exit 0
        fi
        echo "Successfully committed changes" >> "$DEBUG_LOG"

        # Push to remote
        echo "Running: git push" >> "$DEBUG_LOG"
        if ! git push 2>>"$DEBUG_LOG"; then
            echo "Error: git push failed - check credentials and network" | tee -a "$DEBUG_LOG" >&2
            echo "WARNING: Commit was created locally but not pushed" | tee -a "$DEBUG_LOG" >&2
            exit 0
        fi
        echo "Successfully pushed changes" >> "$DEBUG_LOG"

        echo "SUCCESS: All operations completed:" >> "$DEBUG_LOG"
        echo "  - Changes committed with message: $COMMIT_MSG" >> "$DEBUG_LOG"
        echo "  - Changes pushed to remote" >> "$DEBUG_LOG"
    fi
else
    echo "Warning: Post UpdateVersion Push pattern found but failed to extract JSON payload" >> "$DEBUG_LOG"
fi

echo "=== Hook completed ===" >> "$DEBUG_LOG"
echo "" >> "$DEBUG_LOG"

# Exit 0 to allow normal stoppage
exit 0
