#!/bin/bash
set -e

# Test script for duplicate detection logic
# This script tests the Python duplicate detection code independently

echo "Testing duplicate detection logic..."

# Create test Python script
cat > /tmp/test_check_duplicates.py << 'PYTHON_SCRIPT_EOF'
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

# Test Case 1: Exact duplicate should be detected
echo ""
echo "Test 1: Exact duplicate detection"
echo "=================================="

# Create mock issue data with exact match
MOCK_ISSUES=$(cat <<EOF
[
  {
    "number": 123,
    "title": "Workflow Failure: Frontend CI/CD - Lint and Format Check - Run ESLint",
    "body": "# Issue Log Template\n\n| Field | Value |\n|-------|-------|\n| title | Workflow Failure: Frontend CI/CD - Lint and Format Check - Run ESLint |\n| featureID | 5 |\n| featureName | feature/5-add-simple-button-that-says-hello-on-main-page |\n| jobName | Lint and Format Check |\n| stepName | Run ESLint |\n| logLineNumbers | See workflow run URL for complete logs |"
  }
]
EOF
)

export CURRENT_TITLE="Workflow Failure: Frontend CI/CD - Lint and Format Check - Run ESLint"
export CURRENT_FEATURE_ID="5"
export CURRENT_FEATURE_NAME="feature/5-add-simple-button-that-says-hello-on-main-page"
export CURRENT_JOB_NAME="Lint and Format Check"
export CURRENT_STEP_NAME="Run ESLint"
export CURRENT_LOG_LINE_NUMBERS="See workflow run URL for complete logs"

if echo "$MOCK_ISSUES" | python3 /tmp/test_check_duplicates.py 2>&1 | grep -q "Duplicate issue found: #123"; then
    echo "✓ PASS: Exact duplicate was correctly detected"
else
    echo "✗ FAIL: Exact duplicate was not detected"
    exit 1
fi

# Test Case 2: Different branch should NOT be detected as duplicate
echo ""
echo "Test 2: Different branch (no duplicate)"
echo "========================================"

MOCK_ISSUES=$(cat <<EOF
[
  {
    "number": 456,
    "title": "Workflow Failure: Frontend CI/CD - Lint and Format Check - Run ESLint",
    "body": "# Issue Log Template\n\n| Field | Value |\n|-------|-------|\n| title | Workflow Failure: Frontend CI/CD - Lint and Format Check - Run ESLint |\n| featureID | 6 |\n| featureName | feature/6-different-feature |\n| jobName | Lint and Format Check |\n| stepName | Run ESLint |\n| logLineNumbers | See workflow run URL for complete logs |"
  }
]
EOF
)

if echo "$MOCK_ISSUES" | python3 /tmp/test_check_duplicates.py 2>&1 | grep -q "No duplicate issues found"; then
    echo "✓ PASS: Different branch correctly not detected as duplicate"
else
    echo "✗ FAIL: Different branch was incorrectly detected as duplicate"
    exit 1
fi

# Test Case 3: Different step name should NOT be detected as duplicate
echo ""
echo "Test 3: Different step name (no duplicate)"
echo "==========================================="

MOCK_ISSUES=$(cat <<EOF
[
  {
    "number": 789,
    "title": "Workflow Failure: Frontend CI/CD - Lint and Format Check - Run ESLint",
    "body": "# Issue Log Template\n\n| Field | Value |\n|-------|-------|\n| title | Workflow Failure: Frontend CI/CD - Lint and Format Check - Run ESLint |\n| featureID | 5 |\n| featureName | feature/5-add-simple-button-that-says-hello-on-main-page |\n| jobName | Lint and Format Check |\n| stepName | Different Step |\n| logLineNumbers | See workflow run URL for complete logs |"
  }
]
EOF
)

if echo "$MOCK_ISSUES" | python3 /tmp/test_check_duplicates.py 2>&1 | grep -q "No duplicate issues found"; then
    echo "✓ PASS: Different step name correctly not detected as duplicate"
else
    echo "✗ FAIL: Different step name was incorrectly detected as duplicate"
    exit 1
fi

# Test Case 4: Empty issue list should NOT find duplicates
echo ""
echo "Test 4: Empty issue list (no duplicates)"
echo "========================================="

MOCK_ISSUES="[]"

if echo "$MOCK_ISSUES" | python3 /tmp/test_check_duplicates.py 2>&1 | grep -q "No duplicate issues found"; then
    echo "✓ PASS: Empty issue list correctly handled"
else
    echo "✗ FAIL: Empty issue list was not handled correctly"
    exit 1
fi

# Test Case 5: Multiple issues, one matching
echo ""
echo "Test 5: Multiple issues with one exact match"
echo "============================================="

MOCK_ISSUES=$(cat <<EOF
[
  {
    "number": 100,
    "title": "Different Issue",
    "body": "# Issue Log Template\n\n| Field | Value |\n|-------|-------|\n| title | Different Issue |\n| featureID | 1 |\n| featureName | feature/1-other |\n| jobName | Other Job |\n| stepName | Other Step |\n| logLineNumbers | Lines 1-10 |"
  },
  {
    "number": 200,
    "title": "Workflow Failure: Frontend CI/CD - Lint and Format Check - Run ESLint",
    "body": "# Issue Log Template\n\n| Field | Value |\n|-------|-------|\n| title | Workflow Failure: Frontend CI/CD - Lint and Format Check - Run ESLint |\n| featureID | 5 |\n| featureName | feature/5-add-simple-button-that-says-hello-on-main-page |\n| jobName | Lint and Format Check |\n| stepName | Run ESLint |\n| logLineNumbers | See workflow run URL for complete logs |"
  },
  {
    "number": 300,
    "title": "Another Different Issue",
    "body": "# Issue Log Template\n\n| Field | Value |\n|-------|-------|\n| title | Another Different Issue |\n| featureID | 2 |\n| featureName | feature/2-another |\n| jobName | Another Job |\n| stepName | Another Step |\n| logLineNumbers | Lines 20-30 |"
  }
]
EOF
)

if echo "$MOCK_ISSUES" | python3 /tmp/test_check_duplicates.py 2>&1 | grep -q "Duplicate issue found: #200"; then
    echo "✓ PASS: Correct duplicate found among multiple issues"
else
    echo "✗ FAIL: Failed to find correct duplicate among multiple issues"
    exit 1
fi

echo ""
echo "=================================="
echo "All tests passed successfully! ✓"
echo "=================================="
echo ""

# Clean up
rm -f /tmp/test_check_duplicates.py

exit 0
