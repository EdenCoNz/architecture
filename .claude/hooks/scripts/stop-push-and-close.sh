#!/bin/bash
# Stop hook script that commits changes, pushes to git, and closes GitHub issues
# This hook is triggered by the /fix command after a bug fix is completed

# Source shared utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/hook-utils.sh"

# Initialize logging
init_hook_log "/tmp/stop-hook-debug.log" "Fix Push and Close"

# Read and validate transcript input
TRANSCRIPT_PATH=$(read_transcript_input)
validate_transcript "$TRANSCRIPT_PATH" || safe_exit

# Detect hook pattern
HOOK_PATTERN="Post Fix Push and Close"
detect_hook_pattern "$TRANSCRIPT_PATH" "$HOOK_PATTERN" || safe_exit

# Extract JSON payload
PAYLOAD_JSON=$(extract_json_payload "$TRANSCRIPT_PATH" "$HOOK_PATTERN")
[ -n "$PAYLOAD_JSON" ] || safe_exit

# Parse required fields
ISSUE_ID=$(require_json_field "$PAYLOAD_JSON" "issueID" "issue ID") || safe_exit

# Parse optional fields
RUN_ID=$(parse_json_field "$PAYLOAD_JSON" "runID")

# Check prerequisites
log_info "Checking prerequisites..."
check_command "git" || safe_exit
check_command "gh" || safe_exit
check_git_repo || safe_exit
log_info "Prerequisites validated"

# Get and validate current branch
CURRENT_BRANCH=$(get_current_branch)
log_info "Current branch: $CURRENT_BRANCH"
warn_main_branch "$CURRENT_BRANCH"

# Execute git workflow
COMMIT_MSG="Fix issue #${ISSUE_ID}"
git_workflow "$COMMIT_MSG" || safe_exit

# Verify issue exists and close it
gh_issue_exists "$ISSUE_ID" || safe_exit
gh_issue_close "$ISSUE_ID" "Automatically closed after fix was pushed" || safe_exit

# Finish with success message
SUCCESS_MSG="All operations completed:
  - Changes committed with message: $COMMIT_MSG
  - Changes pushed to remote
  - Issue #$ISSUE_ID closed"
finish_hook "$SUCCESS_MSG"

safe_exit
