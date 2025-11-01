#!/bin/bash
# Stop hook script that parses the ## Stop section from Claude's output

# Debug log file
DEBUG_LOG="/tmp/stop-hook-debug.log"
echo "=== Hook triggered at $(date) ===" >> "$DEBUG_LOG"
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

# First check if the "Post Fix Push and Close" pattern exists in the output with proper JSON structure
HAS_HOOK=$(jq -s -r '
  [.[] | select(.message.role == "assistant") | .message.content[]? | select(.type == "text") | .text]
  | last
  | if . != null and (. | test("## Post Fix Push and Close\\s*\\n\\*\\*Payload\\*\\*:\\s*\\n\\{[\\s\\S]*?\\}")) then "true" else "false" end
' "$TRANSCRIPT_PATH" 2>>"$DEBUG_LOG")

echo "Has Post Fix Push and Close hook: '$HAS_HOOK'" >> "$DEBUG_LOG"

# If no hook pattern found, exit early
if [ "$HAS_HOOK" != "true" ]; then
    echo "No Post Fix Push and Close hook pattern found in output - exiting without action" >> "$DEBUG_LOG"
    echo "=== Hook completed (no action needed) ===" >> "$DEBUG_LOG"
    echo "" >> "$DEBUG_LOG"
    exit 0
fi

# Extract the JSON payload from the last assistant message
PAYLOAD_JSON=$(jq -s -r '
  [.[] | select(.message.role == "assistant") | .message.content[]? | select(.type == "text") | .text]
  | last
  | capture("## Post Fix Push and Close\\s*\\n\\*\\*Payload\\*\\*:\\s*\\n(?<json>\\{[\\s\\S]*?\\})") // {}
  | .json // ""
' "$TRANSCRIPT_PATH" 2>>"$DEBUG_LOG")

echo "Extracted payload JSON: '$PAYLOAD_JSON'" >> "$DEBUG_LOG"

# Parse the individual fields from the JSON payload
if [ -n "$PAYLOAD_JSON" ]; then
    ISSUE_ID=$(echo "$PAYLOAD_JSON" | jq -r '.issueID // empty' 2>>"$DEBUG_LOG")
    RUN_ID=$(echo "$PAYLOAD_JSON" | jq -r '.runID // empty' 2>>"$DEBUG_LOG")

    echo "Extracted issueID: '$ISSUE_ID'" >> "$DEBUG_LOG"
    echo "Extracted runID: '$RUN_ID'" >> "$DEBUG_LOG"

    # Validate ISSUE_ID exists
    if [ -z "$ISSUE_ID" ] || [ "$ISSUE_ID" = "null" ]; then
        echo "Error: No valid issue ID found in payload" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi

    # Check prerequisites
    echo "Checking prerequisites..." >> "$DEBUG_LOG"

    if ! command -v git &> /dev/null; then
        echo "Error: git is not installed" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi

    if ! command -v gh &> /dev/null; then
        echo "Error: gh (GitHub CLI) is not installed" | tee -a "$DEBUG_LOG" >&2
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

        # Commit with issue reference
        COMMIT_MSG="Fix issue #${ISSUE_ID}"
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
    fi

    # Verify issue exists before trying to close it
    echo "Checking if issue #$ISSUE_ID exists..." >> "$DEBUG_LOG"
    if ! gh issue view "$ISSUE_ID" &>>"$DEBUG_LOG"; then
        echo "Error: Issue #$ISSUE_ID not found or not accessible" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi

    # Close the issue
    echo "Closing issue #$ISSUE_ID..." >> "$DEBUG_LOG"
    if ! gh issue close "$ISSUE_ID" --comment "Automatically closed after fix was pushed" 2>>"$DEBUG_LOG"; then
        echo "Error: Failed to close issue #$ISSUE_ID" | tee -a "$DEBUG_LOG" >&2
        echo "WARNING: Changes were pushed but issue was not closed" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi

    echo "SUCCESS: All operations completed:" >> "$DEBUG_LOG"
    echo "  - Changes committed with message: $COMMIT_MSG" >> "$DEBUG_LOG"
    echo "  - Changes pushed to remote" >> "$DEBUG_LOG"
    echo "  - Issue #$ISSUE_ID closed" >> "$DEBUG_LOG"
else
    echo "Warning: Post Fix Push and Close pattern found but failed to extract JSON payload" >> "$DEBUG_LOG"
fi

echo "=== Hook completed ===" >> "$DEBUG_LOG"
echo "" >> "$DEBUG_LOG"

# Exit 0 to allow normal stoppage
exit 0
