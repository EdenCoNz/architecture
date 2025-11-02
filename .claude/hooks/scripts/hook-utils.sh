#!/bin/bash
# Shared utilities library for Claude Code hook scripts
# This library provides common functions used across all hook scripts to reduce
# code duplication and ensure consistent behavior.

# =============================================================================
# LOGGING UTILITIES
# =============================================================================

# Initialize hook logging with header
# Usage: init_hook_log "/tmp/my-hook-debug.log" "My Hook Name"
# Sets global DEBUG_LOG variable and writes initial header
init_hook_log() {
    local log_file="$1"
    local hook_name="$2"

    export DEBUG_LOG="$log_file"
    echo "=== ${hook_name} Hook triggered at $(date) ===" >> "$DEBUG_LOG"
    echo "Working directory: $(pwd)" >> "$DEBUG_LOG"
}

# Log informational message to debug log
# Usage: log_info "Message text"
log_info() {
    echo "$1" >> "$DEBUG_LOG"
}

# Log error to both debug log and stderr
# Usage: log_error "Error message"
log_error() {
    echo "$1" | tee -a "$DEBUG_LOG" >&2
}

# Log success message to debug log
# Usage: log_success "Success message"
log_success() {
    echo "SUCCESS: $1" >> "$DEBUG_LOG"
}

# =============================================================================
# INPUT HANDLING UTILITIES
# =============================================================================

# Read JSON input from stdin and extract transcript path
# Usage: TRANSCRIPT_PATH=$(read_transcript_input)
# Returns expanded transcript path or empty string on error
read_transcript_input() {
    local input
    input=$(cat)
    log_info "Received input: $input"

    local transcript_path
    transcript_path=$(echo "$input" | jq -r '.transcript_path')
    log_info "Extracted transcript path: $transcript_path"

    # Expand tilde in path
    transcript_path="${transcript_path/#\~/$HOME}"
    log_info "Expanded transcript path: $transcript_path"

    echo "$transcript_path"
}

# Validate transcript file exists and is readable
# Usage: validate_transcript "$TRANSCRIPT_PATH" || exit 0
# Returns 0 if valid, 1 if invalid (with error logged)
validate_transcript() {
    local transcript_path="$1"

    if [ -z "$transcript_path" ]; then
        log_error "Error: Transcript path is empty"
        return 1
    fi

    if [ ! -f "$transcript_path" ]; then
        log_error "Error: Transcript file not found at: $transcript_path"
        return 1
    fi

    log_info "Transcript file exists, size: $(wc -c < "$transcript_path") bytes"
    log_info "First 3 lines of transcript:"
    head -n 3 "$transcript_path" >> "$DEBUG_LOG" 2>&1

    return 0
}

# =============================================================================
# PATTERN DETECTION UTILITIES
# =============================================================================

# Check if a hook trigger pattern exists in the transcript
# Usage: detect_hook_pattern "$TRANSCRIPT_PATH" "Post Fix Push and Close" || exit 0
# Supports both plain JSON and markdown-fenced JSON
# Returns 0 if pattern found, 1 if not found
detect_hook_pattern() {
    local transcript_path="$1"
    local pattern_name="$2"

    # Escape special regex characters in pattern name
    local escaped_pattern
    escaped_pattern=$(echo "$pattern_name" | sed 's/[][\/.^$*]/\\&/g')

    local has_hook
    has_hook=$(jq -s -r --arg pattern "$escaped_pattern" '
      [.[] | select(.message.role == "assistant") | .message.content[]? | select(.type == "text") | .text]
      | last
      | if . != null and (. | test("## " + $pattern + "\\s*\\n\\*\\*Payload\\*\\*:\\s*\\n(```json\\s*\\n)?\\{[\\s\\S]*?\\}(\\s*\\n```)?")) then "true" else "false" end
    ' "$transcript_path" 2>>"$DEBUG_LOG")

    log_info "Has '$pattern_name' hook: '$has_hook'"

    if [ "$has_hook" != "true" ]; then
        log_info "No '$pattern_name' hook pattern found in output - exiting without action"
        log_info "=== Hook completed (no action needed) ==="
        echo "" >> "$DEBUG_LOG"
        return 1
    fi

    return 0
}

# Extract JSON payload from hook pattern in transcript
# Usage: PAYLOAD=$(extract_json_payload "$TRANSCRIPT_PATH" "Post Fix Push and Close")
# Supports both plain JSON and markdown-fenced JSON
# Returns JSON string or empty string if not found
extract_json_payload() {
    local transcript_path="$1"
    local pattern_name="$2"

    # Escape special regex characters in pattern name
    local escaped_pattern
    escaped_pattern=$(echo "$pattern_name" | sed 's/[][\/.^$*]/\\&/g')

    local payload_json
    payload_json=$(jq -s -r --arg pattern "$escaped_pattern" '
      [.[] | select(.message.role == "assistant") | .message.content[]? | select(.type == "text") | .text]
      | last
      | capture("## " + $pattern + "\\s*\\n\\*\\*Payload\\*\\*:\\s*\\n(```json\\s*\\n)?(?<json>\\{[\\s\\S]*?\\})(\\s*\\n```)?") // {}
      | .json // ""
    ' "$transcript_path" 2>>"$DEBUG_LOG")

    log_info "Extracted payload JSON: '$payload_json'"

    if [ -z "$payload_json" ]; then
        log_error "Warning: '$pattern_name' pattern found but failed to extract JSON payload"
    fi

    echo "$payload_json"
}

# =============================================================================
# JSON PAYLOAD PARSING UTILITIES
# =============================================================================

# Parse a single field from JSON payload
# Usage: VALUE=$(parse_json_field "$PAYLOAD_JSON" "fieldName")
# Returns field value or empty string if not found/null
parse_json_field() {
    local payload_json="$1"
    local field_name="$2"

    local value
    value=$(echo "$payload_json" | jq -r ".${field_name} // empty" 2>>"$DEBUG_LOG")

    log_info "Extracted ${field_name}: '$value'"

    echo "$value"
}

# Parse and validate a required field from JSON payload
# Usage: VALUE=$(require_json_field "$PAYLOAD_JSON" "fieldName" "Field Display Name") || exit 0
# Returns field value or exits with error if missing/null
require_json_field() {
    local payload_json="$1"
    local field_name="$2"
    local display_name="$3"

    local value
    value=$(parse_json_field "$payload_json" "$field_name")

    if [ -z "$value" ] || [ "$value" = "null" ]; then
        log_error "Error: No valid $display_name found in payload"
        return 1
    fi

    echo "$value"
}

# =============================================================================
# PREREQUISITES CHECKING UTILITIES
# =============================================================================

# Check if a command exists
# Usage: check_command "git" || exit 0
# Returns 0 if command exists, 1 with error logged if not
check_command() {
    local cmd="$1"

    if ! command -v "$cmd" &> /dev/null; then
        log_error "Error: $cmd is not installed"
        return 1
    fi

    return 0
}

# Check if we're in a git repository
# Usage: check_git_repo || exit 0
# Returns 0 if in git repo, 1 with error logged if not
check_git_repo() {
    if ! git rev-parse --git-dir &> /dev/null; then
        log_error "Error: Not in a git repository"
        return 1
    fi

    return 0
}

# Get current git branch name
# Usage: BRANCH=$(get_current_branch)
# Returns branch name
get_current_branch() {
    git branch --show-current
}

# Warn if on main or master branch (but don't block)
# Usage: warn_main_branch "$CURRENT_BRANCH"
warn_main_branch() {
    local branch="$1"

    if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
        log_error "WARNING: Pushing to $branch branch"
    fi
}

# =============================================================================
# GIT OPERATIONS UTILITIES
# =============================================================================

# Check if there are uncommitted changes
# Usage: if has_uncommitted_changes; then ... fi
# Returns 0 if changes exist, 1 if working directory is clean
has_uncommitted_changes() {
    if git diff --quiet && git diff --cached --quiet; then
        log_info "No changes to commit - skipping git operations"
        log_error "WARNING: No changes detected. Skipping commit and push."
        return 1
    fi

    log_info "Changes detected, proceeding with git operations..."
    return 0
}

# Stage all changes in working directory
# Usage: git_add_all || exit 0
# Returns 0 on success, 1 on failure (with error logged)
git_add_all() {
    log_info "Running: git add ."

    if ! git add . 2>>"$DEBUG_LOG"; then
        log_error "Error: git add failed"
        return 1
    fi

    log_info "Successfully staged changes"
    return 0
}

# Commit staged changes with message
# Usage: git_commit "Fix issue #123" || exit 0
# Returns 0 on success, 1 on failure (with error logged)
git_commit() {
    local commit_msg="$1"

    log_info "Running: git commit -m \"$commit_msg\""

    if ! git commit -m "$commit_msg" 2>>"$DEBUG_LOG"; then
        log_error "Error: git commit failed"
        return 1
    fi

    log_info "Successfully committed changes"
    return 0
}

# Push commits to remote
# Usage: git_push || exit 0
# Returns 0 on success, 1 on failure (with error logged)
git_push() {
    log_info "Running: git push"

    if ! git push 2>>"$DEBUG_LOG"; then
        log_error "Error: git push failed - check credentials and network"
        log_error "WARNING: Commit was created locally but not pushed"
        return 1
    fi

    log_info "Successfully pushed changes"
    return 0
}

# Execute complete git workflow: add, commit, push
# Usage: git_workflow "Commit message" || exit 0
# Returns 0 on success, 1 on failure at any step
git_workflow() {
    local commit_msg="$1"

    if ! has_uncommitted_changes; then
        return 0
    fi

    git_add_all || return 1
    git_commit "$commit_msg" || return 1
    git_push || return 1

    return 0
}

# =============================================================================
# GITHUB OPERATIONS UTILITIES
# =============================================================================

# Check if a GitHub issue exists
# Usage: gh_issue_exists "123" || exit 0
# Returns 0 if issue exists, 1 if not (with error logged)
gh_issue_exists() {
    local issue_id="$1"

    log_info "Checking if issue #$issue_id exists..."

    if ! gh issue view "$issue_id" &>>"$DEBUG_LOG"; then
        log_error "Error: Issue #$issue_id not found or not accessible"
        return 1
    fi

    return 0
}

# Close a GitHub issue with comment
# Usage: gh_issue_close "123" "Comment text" || exit 0
# Returns 0 on success, 1 on failure (with error logged)
gh_issue_close() {
    local issue_id="$1"
    local comment="$2"

    log_info "Closing issue #$issue_id..."

    if ! gh issue close "$issue_id" --comment "$comment" 2>>"$DEBUG_LOG"; then
        log_error "Error: Failed to close issue #$issue_id"
        log_error "WARNING: Changes were pushed but issue was not closed"
        return 1
    fi

    log_info "Successfully closed issue #$issue_id"
    return 0
}

# Check if a git branch exists on remote
# Usage: gh_branch_exists "feature/my-branch" || exit 0
# Returns 0 if branch exists on remote, 1 if not (with error logged)
gh_branch_exists() {
    local branch_name="$1"

    log_info "Checking if branch exists on remote..."

    if ! git ls-remote --exit-code --heads origin "$branch_name" &>>"$DEBUG_LOG"; then
        log_error "Error: Branch '$branch_name' not found on remote"
        log_error "Push may have failed. Please verify with: git push -u origin $branch_name"
        return 1
    fi

    log_info "Branch exists on remote"
    return 0
}

# Create a GitHub pull request
# Usage: PR_URL=$(gh_pr_create "Title" "Body content") || exit 0
# Returns PR URL on success, empty on failure (with error logged)
gh_pr_create() {
    local pr_title="$1"
    local pr_body="$2"

    log_info "Creating pull request..."
    log_info "PR title: $pr_title"

    local pr_output
    pr_output=$(gh pr create --title "$pr_title" --body "$pr_body" 2>&1)
    local pr_exit_code=$?

    log_info "gh pr create exit code: $pr_exit_code"
    log_info "gh pr create output: $pr_output"

    if [ $pr_exit_code -eq 0 ]; then
        local pr_url
        pr_url=$(echo "$pr_output" | grep -o 'https://github.com[^ ]*')

        log_success "Pull request created successfully"
        log_info "  - Title: $pr_title"
        log_info "  - URL: $pr_url"

        echo "$pr_url"
        return 0
    else
        log_error "ERROR: Failed to create pull request"
        log_error "Error output: $pr_output"
        return 1
    fi
}

# =============================================================================
# CLEANUP UTILITIES
# =============================================================================

# Finish hook execution with success message
# Usage: finish_hook "Changes committed and pushed"
finish_hook() {
    local success_msg="$1"

    if [ -n "$success_msg" ]; then
        log_success "$success_msg"
    fi

    log_info "=== Hook completed ==="
    echo "" >> "$DEBUG_LOG"
}

# =============================================================================
# HELPER UTILITIES
# =============================================================================

# Safe exit that always returns 0 (never blocks Claude Code)
# Usage: safe_exit
safe_exit() {
    exit 0
}
