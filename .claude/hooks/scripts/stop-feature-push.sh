#!/bin/bash
# Stop hook script for /push command that creates a GitHub Pull Request
# This hook is triggered after a successful /push command to create a PR for the feature

# Source shared utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/hook-utils.sh"

# Initialize logging
init_hook_log "/tmp/stop-feature-push-PR-debug.log" "Feature Push PR"

# Read and validate transcript input
TRANSCRIPT_PATH=$(read_transcript_input)
validate_transcript "$TRANSCRIPT_PATH" || safe_exit

# Detect hook pattern
HOOK_PATTERN="Post Feature Push Create PR"
detect_hook_pattern "$TRANSCRIPT_PATH" "$HOOK_PATTERN" || safe_exit

# Extract JSON payload
PAYLOAD_JSON=$(extract_json_payload "$TRANSCRIPT_PATH" "$HOOK_PATTERN")
[ -n "$PAYLOAD_JSON" ] || safe_exit

# Parse required fields
FEATURE_ID=$(require_json_field "$PAYLOAD_JSON" "featureID" "feature ID") || safe_exit
FEATURE_TITLE=$(require_json_field "$PAYLOAD_JSON" "featureTitle" "feature title") || safe_exit
FEATURE_BRANCH=$(require_json_field "$PAYLOAD_JSON" "featureBranch" "feature branch") || safe_exit

# Check prerequisites
log_info "Checking prerequisites..."
check_command "gh" || safe_exit
check_command "git" || safe_exit
check_git_repo || safe_exit
log_info "Prerequisites validated"

# Verify we're on the expected feature branch
CURRENT_BRANCH=$(get_current_branch)
log_info "Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "$FEATURE_BRANCH" ]; then
    log_error "Warning: Current branch ($CURRENT_BRANCH) doesn't match expected feature branch ($FEATURE_BRANCH)"
    log_info "Proceeding with PR creation anyway..."
fi

# Verify the feature branch exists on remote
gh_branch_exists "$FEATURE_BRANCH" || safe_exit

# Read user stories file to extract PR body content
USER_STORIES_FILE="docs/features/${FEATURE_ID}/user-stories.md"
log_info "Reading user stories from: $USER_STORIES_FILE"

if [ ! -f "$USER_STORIES_FILE" ]; then
    log_error "Warning: User stories file not found at $USER_STORIES_FILE"
    log_info "Creating PR with minimal description"
    FEATURE_OVERVIEW="Feature implementation for feature #${FEATURE_ID}"
    USER_STORIES_LIST="- See docs/features/${FEATURE_ID}/ for details"
else
    # Extract overview section (between ## Overview and next ##)
    FEATURE_OVERVIEW=$(awk '/## Overview/,/^## / {if (!/^## /) print}' "$USER_STORIES_FILE" | sed '/^$/d' | head -n 10)

    # Extract user stories list (bullet points under ## User Stories)
    USER_STORIES_LIST=$(awk '/## User Stories/,/^## / {if (/^- /) print}' "$USER_STORIES_FILE" | head -n 20)

    log_info "Extracted overview (first 100 chars): ${FEATURE_OVERVIEW:0:100}..."
    log_info "Extracted user stories count: $(echo "$USER_STORIES_LIST" | wc -l)"
fi

# Construct PR title and body
PR_TITLE="Feature ${FEATURE_ID}: ${FEATURE_TITLE}"
log_info "PR title: $PR_TITLE"

PR_BODY=$(cat <<EOF
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
)

# Create pull request
PR_URL=$(gh_pr_create "$PR_TITLE" "$PR_BODY")

if [ $? -eq 0 ] && [ -n "$PR_URL" ]; then
    # Output success message to user
    echo "✅ Pull Request created successfully!" >&2
    echo "   URL: $PR_URL" >&2
else
    # Provide manual PR creation instructions
    log_error ""
    log_error "You can create the PR manually with:"
    log_error "  gh pr create --title '$PR_TITLE' --body 'See docs/features/${FEATURE_ID}/ for details'"
fi

finish_hook
safe_exit
