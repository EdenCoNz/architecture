#!/bin/bash
# Stop hook script for /push command that creates a GitHub Pull Request
# This hook is triggered after a successful /push command to create a PR for the feature

# Debug log file
DEBUG_LOG="/tmp/stop-feature-push-PR-debug.log"
echo "=== Feature Push PR Hook triggered at $(date) ===" >> "$DEBUG_LOG"
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

# Check if the "Post Feature Push Create PR" pattern exists in the output with proper JSON structure
# Supports both plain JSON and JSON wrapped in markdown code fences
HAS_HOOK=$(jq -s -r '
  [.[] | select(.message.role == "assistant") | .message.content[]? | select(.type == "text") | .text]
  | last
  | if . != null and (. | test("## Post Feature Push Create PR\\s*\\n\\*\\*Payload\\*\\*:\\s*\\n(```json\\s*\\n)?\\{[\\s\\S]*?\\}(\\s*\\n```)?")) then "true" else "false" end
' "$TRANSCRIPT_PATH" 2>>"$DEBUG_LOG")

echo "Has Post Feature Push Create PR hook: '$HAS_HOOK'" >> "$DEBUG_LOG"

# If no hook pattern found, exit early
if [ "$HAS_HOOK" != "true" ]; then
    echo "No Post Feature Push Create PR hook pattern found in output - exiting without action" >> "$DEBUG_LOG"
    echo "=== Hook completed (no action needed) ===" >> "$DEBUG_LOG"
    echo "" >> "$DEBUG_LOG"
    exit 0
fi

# Extract the JSON payload from the last assistant message
# Supports both plain JSON and JSON wrapped in markdown code fences
PAYLOAD_JSON=$(jq -s -r '
  [.[] | select(.message.role == "assistant") | .message.content[]? | select(.type == "text") | .text]
  | last
  | capture("## Post Feature Push Create PR\\s*\\n\\*\\*Payload\\*\\*:\\s*\\n(```json\\s*\\n)?(?<json>\\{[\\s\\S]*?\\})(\\s*\\n```)?") // {}
  | .json // ""
' "$TRANSCRIPT_PATH" 2>>"$DEBUG_LOG")

echo "Extracted payload JSON: '$PAYLOAD_JSON'" >> "$DEBUG_LOG"

# Parse the fields from the JSON payload
if [ -n "$PAYLOAD_JSON" ]; then
    FEATURE_ID=$(echo "$PAYLOAD_JSON" | jq -r '.featureID // empty' 2>>"$DEBUG_LOG")
    FEATURE_TITLE=$(echo "$PAYLOAD_JSON" | jq -r '.featureTitle // empty' 2>>"$DEBUG_LOG")
    FEATURE_BRANCH=$(echo "$PAYLOAD_JSON" | jq -r '.featureBranch // empty' 2>>"$DEBUG_LOG")

    echo "Extracted featureID: '$FEATURE_ID'" >> "$DEBUG_LOG"
    echo "Extracted featureTitle: '$FEATURE_TITLE'" >> "$DEBUG_LOG"
    echo "Extracted featureBranch: '$FEATURE_BRANCH'" >> "$DEBUG_LOG"

    # Validate required fields exist
    if [ -z "$FEATURE_ID" ] || [ "$FEATURE_ID" = "null" ]; then
        echo "Error: No valid feature ID found in payload" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi

    if [ -z "$FEATURE_TITLE" ] || [ "$FEATURE_TITLE" = "null" ]; then
        echo "Error: No valid feature title found in payload" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi

    if [ -z "$FEATURE_BRANCH" ] || [ "$FEATURE_BRANCH" = "null" ]; then
        echo "Error: No valid feature branch found in payload" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi

    # Check prerequisites
    echo "Checking prerequisites..." >> "$DEBUG_LOG"

    if ! command -v gh &> /dev/null; then
        echo "Error: gh (GitHub CLI) is not installed" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi

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

    # Verify we're on the expected feature branch
    CURRENT_BRANCH=$(git branch --show-current)
    echo "Current branch: $CURRENT_BRANCH" >> "$DEBUG_LOG"

    if [ "$CURRENT_BRANCH" != "$FEATURE_BRANCH" ]; then
        echo "Warning: Current branch ($CURRENT_BRANCH) doesn't match expected feature branch ($FEATURE_BRANCH)" | tee -a "$DEBUG_LOG"
        echo "Proceeding with PR creation anyway..." >> "$DEBUG_LOG"
    fi

    # Verify the feature branch exists on remote
    echo "Checking if feature branch exists on remote..." >> "$DEBUG_LOG"
    if ! git ls-remote --exit-code --heads origin "$FEATURE_BRANCH" &>>"$DEBUG_LOG"; then
        echo "Error: Feature branch '$FEATURE_BRANCH' not found on remote" | tee -a "$DEBUG_LOG" >&2
        echo "Push may have failed. Please verify with: git push -u origin $FEATURE_BRANCH" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi
    echo "Feature branch exists on remote" >> "$DEBUG_LOG"

    # Read user stories file to extract PR body content
    USER_STORIES_FILE="docs/features/${FEATURE_ID}/user-stories.md"
    echo "Reading user stories from: $USER_STORIES_FILE" >> "$DEBUG_LOG"

    if [ ! -f "$USER_STORIES_FILE" ]; then
        echo "Warning: User stories file not found at $USER_STORIES_FILE" | tee -a "$DEBUG_LOG"
        echo "Creating PR with minimal description" >> "$DEBUG_LOG"
        FEATURE_OVERVIEW="Feature implementation for feature #${FEATURE_ID}"
        USER_STORIES_LIST="- See docs/features/${FEATURE_ID}/ for details"
    else
        # Extract overview section (between ## Overview and next ##)
        FEATURE_OVERVIEW=$(awk '/## Overview/,/^## / {if (!/^## /) print}' "$USER_STORIES_FILE" | sed '/^$/d' | head -n 10)

        # Extract user stories list (bullet points under ## User Stories)
        USER_STORIES_LIST=$(awk '/## User Stories/,/^## / {if (/^- /) print}' "$USER_STORIES_FILE" | head -n 20)

        echo "Extracted overview (first 100 chars): ${FEATURE_OVERVIEW:0:100}..." >> "$DEBUG_LOG"
        echo "Extracted user stories count: $(echo "$USER_STORIES_LIST" | wc -l)" >> "$DEBUG_LOG"
    fi

    # Construct PR title
    PR_TITLE="Feature ${FEATURE_ID}: ${FEATURE_TITLE}"
    echo "PR title: $PR_TITLE" >> "$DEBUG_LOG"

    # Create PR using gh CLI with HEREDOC for body
    echo "Creating pull request..." >> "$DEBUG_LOG"

    PR_OUTPUT=$(gh pr create \
        --title "$PR_TITLE" \
        --body "$(cat <<EOF
## Summary

${FEATURE_OVERVIEW}

## User Stories Implemented

${USER_STORIES_LIST}

## Test Plan

- [ ] All user stories have been implemented
- [ ] Code has been tested locally
- [ ] No breaking changes introduced
- [ ] Documentation updated if needed

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" 2>&1)

    PR_EXIT_CODE=$?
    echo "gh pr create exit code: $PR_EXIT_CODE" >> "$DEBUG_LOG"
    echo "gh pr create output: $PR_OUTPUT" >> "$DEBUG_LOG"

    if [ $PR_EXIT_CODE -eq 0 ]; then
        # Extract PR URL from output
        PR_URL=$(echo "$PR_OUTPUT" | grep -o 'https://github.com[^ ]*')

        echo "SUCCESS: Pull request created successfully" >> "$DEBUG_LOG"
        echo "  - Title: $PR_TITLE" >> "$DEBUG_LOG"
        echo "  - URL: $PR_URL" >> "$DEBUG_LOG"

        # Output to user
        echo "✅ Pull Request created successfully!" >&2
        echo "   URL: $PR_URL" >&2
    else
        echo "ERROR: Failed to create pull request" | tee -a "$DEBUG_LOG" >&2
        echo "Error output: $PR_OUTPUT" | tee -a "$DEBUG_LOG" >&2
        echo "" | tee -a "$DEBUG_LOG" >&2
        echo "You can create the PR manually with:" | tee -a "$DEBUG_LOG" >&2
        echo "  gh pr create --title '$PR_TITLE' --body 'See docs/features/${FEATURE_ID}/ for details'" | tee -a "$DEBUG_LOG" >&2
        exit 0
    fi
else
    echo "Warning: Post Feature Push Create PR pattern found but failed to extract JSON payload" >> "$DEBUG_LOG"
fi

echo "=== Hook completed ===" >> "$DEBUG_LOG"
echo "" >> "$DEBUG_LOG"

# Exit 0 to allow normal stoppage
exit 0
