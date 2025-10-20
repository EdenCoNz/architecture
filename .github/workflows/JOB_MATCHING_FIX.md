# Bug-Logger Job Matching Fix

## Problem Description

The bug-logger workflow was failing to identify failed jobs correctly due to a mismatch between job identifiers:

- **Job IDs (YAML keys)**: `lint`, `format`, `type-check`, `test`, `security`, `build`, `deployment-check`
- **Job Names (display names)**: `Lint Check (Ruff)`, `Format Check (Black)`, `Type Check (MyPy)`, etc.

### Root Cause

1. The `job_results` input to bug-logger contains job IDs (YAML keys like "lint")
2. The GitHub Actions API returns job names (display names like "Lint Check (Ruff)")
3. The workflow was trying to match job IDs against job names using `contains()`, which failed

### Example of Failure

```bash
FAILED_JOB_NAME="lint"  # From job_results (job ID)
# Tries to match "lint" against "Lint Check (Ruff)" - FAILS!
JOB_ID=$(cat workflow_jobs.json | jq -r ".jobs[] | select(.name | contains(\"$FAILED_JOB_NAME\")) | .databaseId")
```

## Solution

Implemented a mapping-based approach with fallback matching:

### 1. Job ID to Name Mapping

Created a declarative mapping in the bug-logger workflow:

```bash
declare -A JOB_ID_TO_NAME_MAP=(
  ["lint"]="Lint Check (Ruff)"
  ["format"]="Format Check (Black)"
  ["type-check"]="Type Check (MyPy)"
  ["test"]="Test Suite (Pytest)"
  ["security"]="Security Audit"
  ["build"]="Build Verification"
  ["deployment-check"]="Deployment Readiness Check"
)
```

### 2. Matching Logic

1. **Map job ID to name**: Convert the job ID (e.g., "lint") to the display name (e.g., "Lint Check (Ruff)")
2. **Exact match**: Use `jq` to match the exact job name in the API response
3. **Fallback match**: If exact match fails, use case-insensitive partial matching

```bash
# Exact match
JOB_ID=$(cat workflow_jobs.json | jq -r ".jobs[] | select(.name == \"$FAILED_JOB_NAME\") | .databaseId")

# Fallback: case-insensitive partial match
if [ -z "$JOB_ID" ]; then
  JOB_ID=$(cat workflow_jobs.json | jq -r ".jobs[] | select(.name | ascii_downcase | contains(\"$FAILED_JOB_ID\" | ascii_downcase)) | .databaseId")
fi
```

### 3. Improved Debugging

Added comprehensive logging:
- Shows the job ID being searched
- Displays all available jobs in the workflow
- Logs the mapping result
- Shows the final database ID

## Files Modified

- `.github/workflows/bug-logger.yml` (lines 109-159)

## Testing Strategy

To test the fix:

1. Trigger a CI failure (e.g., introduce a linting error)
2. Verify the bug-logger workflow runs
3. Check the workflow logs for:
   - "Looking for job with ID: lint"
   - "Mapped job ID 'lint' to job name 'Lint Check (Ruff)'"
   - "Failed job database ID: [number]"
4. Verify a GitHub issue is created with correct job information

## Maintenance

**Important**: If you add or rename jobs in `backend-ci.yml`, you MUST update the mapping in `bug-logger.yml`:

1. Add new job ID to the `JOB_ID_TO_NAME_MAP` array
2. Ensure the job name matches exactly (including parentheses and capitalization)

Example:
```bash
# If you add a new job to backend-ci.yml:
new-job:
  name: New Job (Tool)

# Add to bug-logger.yml mapping:
["new-job"]="New Job (Tool)"
```

## Why This Approach?

### Alternative Approaches Considered

1. **Use job IDs everywhere**: Not possible - GitHub API doesn't expose YAML job IDs
2. **Change backend-ci.yml to use simple names**: Would lose descriptive job names in UI
3. **Reverse engineer job IDs from names**: Fragile and unreliable

### Selected Approach Benefits

- **Reliable**: Explicit mapping eliminates guesswork
- **Maintainable**: Clear documentation and simple to update
- **Debuggable**: Comprehensive logging shows exactly what's happening
- **Robust**: Fallback matching handles edge cases
- **Clear**: Code is self-documenting with comments

## Related Issues

This fix addresses the issue where the bug-logger would fail with:
```
Looking for job: lint
Available jobs in workflow:
- Lint Check (Ruff)
- Format Check (Black)
...
Failed job ID: [empty]
```

Now it correctly maps:
```
Looking for job with ID: lint
Mapped job ID 'lint' to job name 'Lint Check (Ruff)'
Failed job database ID: 12345678
```
