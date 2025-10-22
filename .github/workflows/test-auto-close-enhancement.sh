#!/bin/bash

# Test script for auto-close-issue.yml bulk close enhancement
# This script validates the Python logic for extracting matching issues

set -e

echo "======================================================================"
echo "Testing Auto-Close Issue Bulk Enhancement"
echo "======================================================================"
echo ""

# Create test data matching the actual issue format
TEST_ISSUES='[
  {
    "number": 117,
    "body": "# Issue Log Template\n\n| Field | Value |\n|-------|-------|\n| title | Workflow Failure: Frontend CI/CD - Lint and Format Check - Run ESLint |\n| featureID | 5 |\n| featureName | feature/5-add-simple-button-that-says-hello-on-main-page |\n| jobName | Lint and Format Check |"
  },
  {
    "number": 118,
    "body": "# Issue Log Template\n\n| Field | Value |\n|-------|-------|\n| title | Workflow Failure: Frontend CI/CD - TypeScript Type Check |\n| featureID | 5 |\n| featureName | feature/5-add-simple-button-that-says-hello-on-main-page |\n| jobName | TypeScript Type Check |"
  },
  {
    "number": 119,
    "body": "# Issue Log Template\n\n| Field | Value |\n|-------|-------|\n| title | Workflow Failure: Frontend CI/CD - Unit Tests |\n| featureID | 5 |\n| featureName | feature/5-add-simple-button-that-says-hello-on-main-page |\n| jobName | Unit Tests |"
  },
  {
    "number": 120,
    "body": "# Issue Log Template\n\n| Field | Value |\n|-------|-------|\n| title | Different Feature |\n| featureID | 6 |\n| featureName | feature/6-different-feature |\n| jobName | Some Job |"
  },
  {
    "number": 121,
    "body": "Regular issue without metadata table"
  }
]'

echo "Test 1: Extract matching issues (featureID=5, featureName=feature/5-add-simple-button-that-says-hello-on-main-page, exclude=117)"
echo "Expected: 118, 119"
echo ""

# Create the Python script (same as in the workflow)
cat > /tmp/find_matching_issues.py << 'EOF'
import json
import sys
import re

data = json.loads(sys.stdin.read())
target_feature_id = sys.argv[1]
target_feature_name = sys.argv[2]
exclude_issue = sys.argv[3]

matching_issues = []

for issue in data:
    issue_number = str(issue.get('number', ''))
    issue_body = issue.get('body', '')

    if issue_number == exclude_issue:
        continue

    feature_id_match = re.search(r'\|\s*featureID\s*\|\s*([^|\s]+)', issue_body, re.IGNORECASE)
    feature_name_match = re.search(r'\|\s*featureName\s*\|\s*([^|\s]+)', issue_body, re.IGNORECASE)

    if feature_id_match and feature_name_match:
        issue_feature_id = feature_id_match.group(1).strip()
        issue_feature_name = feature_name_match.group(1).strip()

        if issue_feature_id == target_feature_id and issue_feature_name == target_feature_name:
            matching_issues.append(issue_number)

for issue in matching_issues:
    print(issue)
EOF

# Run test
RESULT=$(echo "$TEST_ISSUES" | python3 /tmp/find_matching_issues.py "5" "feature/5-add-simple-button-that-says-hello-on-main-page" "117")
echo "Result: $RESULT"
echo ""

# Validate result
EXPECTED_COUNT=2
ACTUAL_COUNT=$(echo "$RESULT" | wc -l)

if [ "$ACTUAL_COUNT" -eq "$EXPECTED_COUNT" ]; then
  echo "✓ Test 1 PASSED: Found $ACTUAL_COUNT matching issues"
else
  echo "✗ Test 1 FAILED: Expected $EXPECTED_COUNT issues, found $ACTUAL_COUNT"
  exit 1
fi

echo ""
echo "Test 2: Extract metadata from issue body"
echo "Expected: featureID=5, featureName=feature/5-add-simple-button-that-says-hello-on-main-page"
echo ""

ISSUE_BODY='| Field | Value |
|-------|-------|
| title | Workflow Failure |
| featureID | 5 |
| featureName | feature/5-add-simple-button-that-says-hello-on-main-page |
| jobName | Lint Check |'

FEATURE_ID=$(echo "$ISSUE_BODY" | grep -i '|[[:space:]]*featureID[[:space:]]*|' | sed 's/^.*|[[:space:]]*featureID[[:space:]]*|[[:space:]]*\([^|[:space:]]*\).*/\1/' | tr -d '[:space:]')
FEATURE_NAME=$(echo "$ISSUE_BODY" | grep -i '|[[:space:]]*featureName[[:space:]]*|' | sed 's/^.*|[[:space:]]*featureName[[:space:]]*|[[:space:]]*\([^|[:space:]]*\).*/\1/' | tr -d '[:space:]')

echo "Extracted featureID: $FEATURE_ID"
echo "Extracted featureName: $FEATURE_NAME"
echo ""

if [ "$FEATURE_ID" == "5" ] && [ "$FEATURE_NAME" == "feature/5-add-simple-button-that-says-hello-on-main-page" ]; then
  echo "✓ Test 2 PASSED: Metadata extraction successful"
else
  echo "✗ Test 2 FAILED: Metadata extraction failed"
  exit 1
fi

echo ""
echo "Test 3: Handle issue without metadata"
echo "Expected: Empty featureID and featureName"
echo ""

ISSUE_BODY_NO_META="This is a regular issue without metadata table"

FEATURE_ID=$(echo "$ISSUE_BODY_NO_META" | grep -i '|[[:space:]]*featureID[[:space:]]*|' | sed 's/^.*|[[:space:]]*featureID[[:space:]]*|[[:space:]]*\([^|[:space:]]*\).*/\1/' | tr -d '[:space:]')
FEATURE_NAME=$(echo "$ISSUE_BODY_NO_META" | grep -i '|[[:space:]]*featureName[[:space:]]*|' | sed 's/^.*|[[:space:]]*featureName[[:space:]]*|[[:space:]]*\([^|[:space:]]*\).*/\1/' | tr -d '[:space:]')

echo "Extracted featureID: '${FEATURE_ID:-empty}'"
echo "Extracted featureName: '${FEATURE_NAME:-empty}'"
echo ""

if [ -z "$FEATURE_ID" ] && [ -z "$FEATURE_NAME" ]; then
  echo "✓ Test 3 PASSED: Correctly handled missing metadata"
else
  echo "✗ Test 3 FAILED: Should have empty metadata"
  exit 1
fi

# Cleanup
rm -f /tmp/find_matching_issues.py

echo ""
echo "======================================================================"
echo "All Tests PASSED ✓"
echo "======================================================================"
echo ""
echo "The bulk close enhancement is ready for deployment!"
