#!/bin/bash
# Stop hook script for /updateversion command that commits and pushes version changes
# This hook is triggered after the /updateversion command updates package.json files

# Source shared utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/hook-utils.sh"

# Initialize logging
init_hook_log "/tmp/stop-updateversion-push-debug.log" "UpdateVersion"

# Read and validate transcript input
TRANSCRIPT_PATH=$(read_transcript_input)
validate_transcript "$TRANSCRIPT_PATH" || safe_exit

# Detect hook pattern
HOOK_PATTERN="Post UpdateVersion Push"
detect_hook_pattern "$TRANSCRIPT_PATH" "$HOOK_PATTERN" || safe_exit

# Extract JSON payload
PAYLOAD_JSON=$(extract_json_payload "$TRANSCRIPT_PATH" "$HOOK_PATTERN")
[ -n "$PAYLOAD_JSON" ] || safe_exit

# Parse required fields
FRONTEND_VERSION=$(require_json_field "$PAYLOAD_JSON" "frontendVersion" "frontend version") || safe_exit
BACKEND_VERSION=$(require_json_field "$PAYLOAD_JSON" "backendVersion" "backend version") || safe_exit

# Verify versions match
if [ "$FRONTEND_VERSION" != "$BACKEND_VERSION" ]; then
    log_error "Warning: Frontend and backend versions don't match"
    log_error "  Frontend: $FRONTEND_VERSION"
    log_error "  Backend: $BACKEND_VERSION"
    # Continue with frontend version as primary
fi

NEW_VERSION="$FRONTEND_VERSION"
log_info "Using version: $NEW_VERSION"

# Check prerequisites
log_info "Checking prerequisites..."
check_command "git" || safe_exit
check_git_repo || safe_exit
log_info "Prerequisites validated"

# Get and validate current branch
CURRENT_BRANCH=$(get_current_branch)
log_info "Current branch: $CURRENT_BRANCH"
warn_main_branch "$CURRENT_BRANCH"

# Execute git workflow
COMMIT_MSG="Version updated to ${NEW_VERSION}"
git_workflow "$COMMIT_MSG" || safe_exit

# Finish with success message
SUCCESS_MSG="All operations completed:
  - Changes committed with message: $COMMIT_MSG
  - Changes pushed to remote"
finish_hook "$SUCCESS_MSG"

safe_exit
