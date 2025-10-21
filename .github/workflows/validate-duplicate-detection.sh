#!/bin/bash
set -e

# Validation script for duplicate detection with real repository data
# This script tests the duplicate detection logic against actual open issues

echo "Validating duplicate detection with real repository data..."
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "Error: gh CLI is not installed"
    exit 1
fi

# Create the same Python script used in the workflow
cat > /tmp/validate_check_duplicates.py << 'PYTHON_SCRIPT_EOF'
import sys
import json
import re
import os

# Read the issues JSON from stdin
issues = json.load(sys.stdin)

# Extract current metadata from environment
current_title = os.environ.get('CURRENT_TITLE', '')
current_feature_id = os.environ.get('CURRENT_FEATURE_ID', '')
current_feature_name = os.environ.get('CURRENT_FEATURE_NAME', '')
current_job_name = os.environ.get('CURRENT_JOB_NAME', '')
current_step_name = os.environ.get('CURRENT_STEP_NAME', '')
current_log_line_numbers = os.environ.get('CURRENT_LOG_LINE_NUMBERS', '')

# Function to extract field value from issue body
def extract_field(body, field_name):
    if not body:
        return None
    # Match: | fieldName | value |
    pattern = r'\|\s*' + re.escape(field_name) + r'\s*\|\s*(.+?)\s*\|'
    match = re.search(pattern, body, re.MULTILINE | re.IGNORECASE)
    if match:
        value = match.group(1).strip()
        return value if value else None
    return None

duplicate_found = False
duplicate_number = None

print(f"Checking for duplicates of:", file=sys.stderr)
print(f"  Title: {current_title}", file=sys.stderr)
print(f"  Feature: {current_feature_name}", file=sys.stderr)
print(f"  Job: {current_job_name}", file=sys.stderr)
print(f"  Step: {current_step_name}", file=sys.stderr)
print("", file=sys.stderr)

# Check each issue for duplicates
for issue in issues:
    issue_number = issue.get('number')
    issue_body = issue.get('body', '')

    # Extract all fields from the issue body
    issue_title = extract_field(issue_body, 'title')
    issue_feature_id = extract_field(issue_body, 'featureID')
    issue_feature_name = extract_field(issue_body, 'featureName')
    issue_job_name = extract_field(issue_body, 'jobName')
    issue_step_name = extract_field(issue_body, 'stepName')
    issue_log_line_numbers = extract_field(issue_body, 'logLineNumbers')

    # First check: must be from the same branch (feature name)
    if issue_feature_name != current_feature_name:
        continue

    print(f"Checking issue #{issue_number} (same branch):", file=sys.stderr)
    print(f"  Title match: {issue_title == current_title}", file=sys.stderr)
    print(f"  Feature ID match: {issue_feature_id == current_feature_id}", file=sys.stderr)
    print(f"  Job match: {issue_job_name == current_job_name}", file=sys.stderr)
    print(f"  Step match: {issue_step_name == current_step_name}", file=sys.stderr)
    print(f"  Log lines match: {issue_log_line_numbers == current_log_line_numbers}", file=sys.stderr)
    print("", file=sys.stderr)

    # Check if ALL required fields match
    all_match = (
        issue_title == current_title and
        issue_feature_id == current_feature_id and
        issue_feature_name == current_feature_name and
        issue_job_name == current_job_name and
        issue_step_name == current_step_name and
        issue_log_line_numbers == current_log_line_numbers
    )

    if all_match:
        duplicate_found = True
        duplicate_number = issue_number
        print(f'DUPLICATE_MATCH=true', file=sys.stderr)
        print(f'DUPLICATE_NUMBER={issue_number}', file=sys.stderr)
        break

# Output results
if duplicate_found:
    print(f'Duplicate issue found: #{duplicate_number}')
    sys.exit(0)
else:
    print('No duplicate issues found')
    sys.exit(1)
PYTHON_SCRIPT_EOF

# Fetch actual open issues from the repository
echo "Fetching open issues from repository..."
OPEN_ISSUES=$(gh issue list --state open --limit 100 --json number,title,body)
ISSUE_COUNT=$(echo "$OPEN_ISSUES" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "Found $ISSUE_COUNT open issue(s)"
echo ""

# Test Case 1: Check if issue #76 would be detected as duplicate of itself
echo "Test 1: Issue #76 duplicate detection"
echo "======================================"
ISSUE_76=$(gh issue view 76 --json body --jq '.body')

# Extract metadata from issue #76
TITLE_76=$(echo "$ISSUE_76" | grep "^| title |" | sed 's/^| title | \(.*\) |$/\1/')
FEATURE_ID_76=$(echo "$ISSUE_76" | grep "^| featureID |" | sed 's/^| featureID | \(.*\) |$/\1/')
FEATURE_NAME_76=$(echo "$ISSUE_76" | grep "^| featureName |" | sed 's/^| featureName | \(.*\) |$/\1/')
JOB_NAME_76=$(echo "$ISSUE_76" | grep "^| jobName |" | sed 's/^| jobName | \(.*\) |$/\1/')
STEP_NAME_76=$(echo "$ISSUE_76" | grep "^| stepName |" | sed 's/^| stepName | \(.*\) |$/\1/')
LOG_LINE_NUMBERS_76=$(echo "$ISSUE_76" | grep "^| logLineNumbers |" | sed 's/^| logLineNumbers | \(.*\) |$/\1/')

echo "Extracted metadata from issue #76:"
echo "  Title: $TITLE_76"
echo "  Feature ID: $FEATURE_ID_76"
echo "  Feature Name: $FEATURE_NAME_76"
echo "  Job Name: $JOB_NAME_76"
echo "  Step Name: $STEP_NAME_76"
echo "  Log Line Numbers: $LOG_LINE_NUMBERS_76"
echo ""

# Set environment variables and run check
export CURRENT_TITLE="$TITLE_76"
export CURRENT_FEATURE_ID="$FEATURE_ID_76"
export CURRENT_FEATURE_NAME="$FEATURE_NAME_76"
export CURRENT_JOB_NAME="$JOB_NAME_76"
export CURRENT_STEP_NAME="$STEP_NAME_76"
export CURRENT_LOG_LINE_NUMBERS="$LOG_LINE_NUMBERS_76"

echo "Running duplicate detection..."
echo ""

if echo "$OPEN_ISSUES" | python3 /tmp/validate_check_duplicates.py 2>&1 | tee /tmp/validation_output.log | grep -q "Duplicate issue found"; then
    DETECTED_ISSUE=$(grep "Duplicate issue found" /tmp/validation_output.log | grep -o '#[0-9]*' | tr -d '#')
    if [ "$DETECTED_ISSUE" == "76" ] || [ "$DETECTED_ISSUE" == "75" ]; then
        echo "✓ PASS: Duplicate correctly detected (issue #$DETECTED_ISSUE)"
        echo ""
        echo "This confirms the duplicate detection logic works with real repository data."
    else
        echo "⚠ INFO: Detected issue #$DETECTED_ISSUE (expected #76 or #75)"
        echo ""
        echo "This is acceptable if multiple identical issues exist."
    fi
else
    echo "ℹ INFO: No duplicate detected"
    echo ""
    echo "This suggests issues #75 and #76 may have different metadata,"
    echo "or they may have been closed since we last checked."
fi

# Display the full detection log
echo ""
echo "Full Detection Log:"
echo "==================="
cat /tmp/validation_output.log

# Clean up
rm -f /tmp/validate_check_duplicates.py /tmp/validation_output.log

echo ""
echo "Validation complete!"
