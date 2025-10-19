---
description: Display feature dashboard with states and metrics
---

## Purpose

Display a comprehensive dashboard view of all features showing their current lifecycle states, key metrics, and progress indicators. The dashboard provides an easy-to-scan overview of the entire project's feature portfolio organized by state for quick status assessment.

## Variables

- `{{{ input }}}` - Optional filter parameter: state name (planned, in_progress, testing, review, deployed, summarised, archived) or "all" (default)

## Instructions

You MUST follow the workflow steps in sequential order.

## Error Handling

This command uses comprehensive error handling with specific error codes and recovery suggestions.

**Error Handling Reference**: See `.claude/helpers/command-error-handling.md` for complete error code documentation and `.claude/helpers/error-code-mapping.md` for validation error mapping.

**Common Errors**:
- ENV-001: Git repository not found → Initialize git or navigate to repository
- FS-001: Feature log not found → Run /feature command first
- FS-005: Invalid JSON in feature-log → Fix JSON syntax errors
- INPUT-002: Invalid state filter value → Use valid state name or "all"
- DATA-001: Missing state fields → Use backward compatibility defaults

**Error Handling Strategy**:
- All validation errors (Step 0) use standardized error codes
- Feature log errors are BLOCKING - cannot display dashboard without feature log
- Invalid state filter is BLOCKING - must provide valid filter
- Missing state fields is NON-BLOCKING - use backward compatibility inference
- Empty feature log displays helpful message (not an error)

## Workflow

### Step 0: Pre-Flight Validation

Before displaying the dashboard, validate that required files exist and are accessible.

#### Step 0.1: Load Error Handling and Validation Systems

Read error handling system from .claude/helpers/command-error-handling.md to understand error codes, categories, and message formats.

Read error code mapping from .claude/helpers/error-code-mapping.md to map validation errors to error codes.

Read validation helper from .claude/helpers/pre-flight-validation.md to understand validation requirements and error message formats.

All validation errors in subsequent steps should include appropriate error codes from the error code mapping.

#### Step 0.2: Validate Git Repository Exists

Run the following check to verify this is a git repository:
```bash
test -d ".git" && echo "VALID" || echo "INVALID"
```

If output is "INVALID":
- Display error message:
```
Error: Not a git repository

Check: Git repository existence
Status: No .git/ directory found in current working directory
Command: /dashboard

Remediation:
1. Navigate to your git repository directory
2. If this is a new project, initialize git:
   git init
3. Verify you are in the correct directory:
   pwd
```
- STOP execution immediately

#### Step 0.3: Validate Feature Log Exists

Check if docs/features/feature-log.json exists:
```bash
test -f "docs/features/feature-log.json" && echo "VALID" || echo "INVALID"
```

If "INVALID":
- Display error message:
```
Error: Feature log not found

Check: docs/features/feature-log.json existence
Status: File does not exist
Command: /dashboard

Remediation:
1. Ensure you are in the correct project directory
2. Feature log is created automatically by /feature command
3. If this is a new project, create your first feature:
   /feature "Your feature description"
4. Expected location: docs/features/feature-log.json
```
- STOP execution immediately

#### Step 0.4: Validate Feature Log JSON Syntax

Validate the feature log has valid JSON syntax:
```bash
python3 -c "import json; json.load(open('docs/features/feature-log.json'))" 2>&1
```

If validation fails:
- Display error message:
```
Error: Feature log contains invalid JSON

File: docs/features/feature-log.json
Purpose: Tracks all features and their implementation status
Command: /dashboard

Remediation:
1. Open docs/features/feature-log.json in a text editor
2. Fix the JSON syntax error
3. Validate JSON using: python3 -m json.tool docs/features/feature-log.json
4. Ensure the file follows the feature log schema
```
- STOP execution immediately

#### Step 0.5: Validation Summary

If all validations pass:
- Output: "Pre-flight validation passed - loading dashboard"
- Proceed to Step 1

### Step 1: Parse Input Filter

Parse the input parameter to determine which features to display:

1. **If input is empty or "all"**: Display all features (no filtering)
2. **If input is a valid state name**: Filter to show only features in that state
   - Valid states: `planned`, `in_progress`, `testing`, `review`, `deployed`, `summarised`, `archived`
3. **If input is not a valid state**: Display error message and list valid states

Valid state values:
- `planned` - Features in planning phase with user stories created
- `in_progress` - Features actively being implemented
- `testing` - Features completed and undergoing testing
- `review` - Features in code review
- `deployed` - Features deployed to production
- `summarised` - Features with implementation summarized
- `archived` - Features archived or deprecated

### Step 2: Load Feature Log

Read the feature log from `docs/features/feature-log.json` and parse the JSON.

Handle the following cases:
- **Empty feature log** (no features): Display message "No features found. Create your first feature with /feature command."
- **Missing state fields**: If a feature is missing `state` or `stateHistory` fields, infer the state using backward compatibility rules from the feature state system documentation

Backward compatibility state inference:
```javascript
if (feature.summarisedAt !== null) {
  state = "summarised";
} else if (feature.userStoriesImplemented !== null) {
  state = "deployed";
} else if (feature.userStoriesCreated !== null) {
  state = "in_progress";
} else {
  state = "planned";
}
```

### Step 3: Calculate Dashboard Metrics

For all features (before filtering), calculate:

1. **Total feature count**: Total number of features in the log
2. **Features by state**: Count of features in each lifecycle state
3. **Completion rate**: Percentage of features that are deployed or summarised (completed states)
   - Formula: `(deployed + summarised + archived) / total * 100`
4. **Active features**: Count of features in active development (in_progress + testing + review)
5. **Average time in current state**: For features with stateHistory, calculate days since last state transition

### Step 4: Apply Filter

If a specific state filter was provided in input:
1. Filter the features array to only include features where `state` matches the filter value
2. If filtered list is empty, display: "No features found in state '{state}'"

### Step 5: Group Features by State

Group the features (filtered or all) into state-based buckets for organized display:

State display order:
1. `in_progress` - Show first (most actionable)
2. `testing` - Show second (ready for QA)
3. `review` - Show third (ready for deployment)
4. `planned` - Show fourth (ready to start)
5. `deployed` - Show fifth (recently completed)
6. `summarised` - Show sixth (archived)
7. `archived` - Show last (historical)

For each state group, sort features by most recent state transition (most recent first).

### Step 6: Format and Display Dashboard

Display the dashboard using the following format:

```
================================================================================
                           FEATURE DASHBOARD
================================================================================

SUMMARY
-----------------------------------------------------------------------
Total Features:        {total_count}
Active Development:    {in_progress + testing + review} features
Completion Rate:       {completion_percentage}% ({completed_count}/{total_count})

Features by State:
  - In Progress:       {count}
  - Testing:           {count}
  - Review:            {count}
  - Planned:           {count}
  - Deployed:          {count}
  - Summarised:        {count}
  - Archived:          {count}

{if filter applied: "Filtered by: {state}"}

================================================================================

{For each state group with features:}

{STATE_NAME_UPPERCASE} ({count})
-----------------------------------------------------------------------
{For each feature in state:}
  [{feature_id}] {title}
  Created:     {created_date}
  State Since: {days_in_state} days ago ({last_transition_date})
  {if state == "in_progress" && userStoriesCreated: "User Stories: Created"}
  {if state == "deployed" && userStoriesImplemented: "Implemented: " + date}
  {if state == "summarised": "Summarised: " + date}
  {if stateHistory.length > 1: "Previous States: " + state_names_in_order}
  ---
{end for each feature}

{end for each state group}

================================================================================
                              END OF DASHBOARD
================================================================================
```

### Step 6.1: State Section Headers

Use the following header formats for each state:

- **IN PROGRESS**: Use for `in_progress` state
- **TESTING**: Use for `testing` state
- **IN REVIEW**: Use for `review` state
- **PLANNED**: Use for `planned` state
- **DEPLOYED**: Use for `deployed` state
- **SUMMARISED**: Use for `summarised` state
- **ARCHIVED**: Use for `archived` state

### Step 6.2: Feature Detail Formatting

For each feature, display:

**Required fields:**
- Feature ID and title on first line: `[{id}] {title}`
- Creation date: `Created: {YYYY-MM-DD}` (convert ISO timestamp to readable date)
- Time in current state: `State Since: {X} days ago ({YYYY-MM-DD})`

**Conditional fields (only if relevant):**
- For `in_progress`: Show if user stories created
- For `deployed`: Show implementation completion date
- For `summarised`: Show summarization date
- For all: Show previous states if feature has transitioned (from stateHistory)

**State history display:**
If feature has more than one state in stateHistory, show previous states:
```
Previous States: planned (2 days) -> in_progress (5 days) -> testing (1 day)
```

Calculate time spent in each state by comparing timestamps between consecutive state history entries.

### Step 6.3: Date and Time Formatting

Convert ISO 8601 timestamps to readable formats:

- **For dates**: `YYYY-MM-DD` format (e.g., "2025-10-19")
- **For time calculations**: Calculate days between timestamps
  - Formula: `Math.floor((current_date - timestamp_date) / (1000 * 60 * 60 * 24))`
  - Display: `{X} days ago`
  - Handle edge cases: "today", "1 day ago", "2 days ago"

### Step 6.4: Completion Rate Calculation

Completion rate considers features in terminal or production states:

**Completed states:**
- `deployed` - Feature is in production
- `summarised` - Feature is completed and summarized
- `archived` - Feature lifecycle complete

Formula:
```
completion_rate = (deployed_count + summarised_count + archived_count) / total_features * 100
```

Round to 1 decimal place for display.

### Step 7: Handle Edge Cases

Handle the following edge cases gracefully:

1. **No features in any state**: Display message explaining how to create first feature
2. **Filter returns no results**: Show which filter was applied and suggest using "all"
3. **Missing state fields**: Use backward compatibility inference and show note
4. **Empty stateHistory**: Use createdAt as state transition timestamp
5. **Invalid dates**: Display "Unknown" for any unparseable timestamps
6. **Negative time calculations**: Display "today" if timestamp is in future or same day

### Step 8: Provide Action Recommendations

At the end of the dashboard, provide actionable recommendations based on the current state distribution:

**Recommendations section:**
```
RECOMMENDED ACTIONS
-----------------------------------------------------------------------
{Generate 1-3 recommendations based on state distribution:}

- If features in "planned": "Start implementation with /implement feature {id}"
- If features in "testing": "Run tests and transition to review state"
- If features in "review": "Complete code review and transition to deployed"
- If features in "deployed": "Consider running /summarise to reduce context"
- If no active features: "Create a new feature with /feature command"
- If many in_progress: "Focus on completing current features before starting new ones"
```

Generate recommendations dynamically based on the actual state distribution.

## Report

After displaying the dashboard, provide:

1. **Summary line**: "Dashboard displayed: {filtered_count} of {total_count} features shown"
2. **Filter applied**: If filter was used, show which state was filtered
3. **Top priority actions**: Highlight 1-2 most urgent actions from recommendations
4. **Data freshness**: Show when feature log was last modified

## Examples

### Example 1: Display All Features

```
Input: /dashboard

Output:
================================================================================
                           FEATURE DASHBOARD
================================================================================

SUMMARY
-----------------------------------------------------------------------
Total Features:        5
Active Development:    1 features
Completion Rate:       60.0% (3/5)

Features by State:
  - In Progress:       1
  - Testing:           0
  - Review:            0
  - Planned:           0
  - Deployed:          3
  - Summarised:        1
  - Archived:          0

================================================================================

IN PROGRESS (1)
-----------------------------------------------------------------------
  [5] Architecture System Improvements
  Created:     2025-10-19
  State Since: 0 days ago (2025-10-19)
  User Stories: Created
  ---

DEPLOYED (3)
-----------------------------------------------------------------------
  [4] Connect Frontend and Backend with Test Page
  Created:     2025-10-19
  State Since: 0 days ago (2025-10-19)
  Implemented: 2025-10-19
  ---
  [3] Initialize Backend Project
  Created:     2025-10-19
  State Since: 0 days ago (2025-10-19)
  Implemented: 2025-10-19
  ---
  [2] Dockerize Frontend Application
  Created:     2025-10-15
  State Since: 4 days ago (2025-10-15)
  Implemented: 2025-10-15
  Previous States: planned (0 days)
  ---

SUMMARISED (1)
-----------------------------------------------------------------------
  [1] Initialize Frontend Web Application
  Created:     2025-10-15
  State Since: 4 days ago (2025-10-15)
  Summarised:  2025-10-15
  Previous States: planned (0 days) -> deployed (0 days)
  ---

================================================================================
                              END OF DASHBOARD
================================================================================

RECOMMENDED ACTIONS
-----------------------------------------------------------------------
- Continue implementation of Feature #5 with /implement feature 5
- Consider summarising deployed features (3) with /summarise to reduce context

Dashboard displayed: 5 of 5 features shown
```

### Example 2: Filter by State

```
Input: /dashboard in_progress

Output:
================================================================================
                           FEATURE DASHBOARD
================================================================================

SUMMARY
-----------------------------------------------------------------------
Total Features:        5
Active Development:    1 features
Completion Rate:       60.0% (3/5)

Features by State:
  - In Progress:       1
  - Testing:           0
  - Review:            0
  - Planned:           0
  - Deployed:          3
  - Summarised:        1
  - Archived:          0

Filtered by: in_progress

================================================================================

IN PROGRESS (1)
-----------------------------------------------------------------------
  [5] Architecture System Improvements
  Created:     2025-10-19
  State Since: 0 days ago (2025-10-19)
  User Stories: Created
  ---

================================================================================
                              END OF DASHBOARD
================================================================================

RECOMMENDED ACTIONS
-----------------------------------------------------------------------
- Continue implementation of Feature #5 with /implement feature 5

Dashboard displayed: 1 of 5 features shown (filtered by: in_progress)
```

### Example 3: No Features Found

```
Input: /dashboard

Output:
No features found. Create your first feature with /feature command.

Examples:
  /feature "Initialize Frontend Application"
  /feature "Add User Authentication"
  /feature "Create Dashboard UI"
```

### Example 4: Empty Filter Results

```
Input: /dashboard archived

Output:
================================================================================
                           FEATURE DASHBOARD
================================================================================

SUMMARY
-----------------------------------------------------------------------
Total Features:        5
Active Development:    1 features
Completion Rate:       60.0% (3/5)

Features by State:
  - In Progress:       1
  - Testing:           0
  - Review:            0
  - Planned:           0
  - Deployed:          3
  - Summarised:        1
  - Archived:          0

Filtered by: archived

================================================================================

No features found in state 'archived'

Try /dashboard all to see all features, or use one of these states:
  - in_progress (1 feature)
  - deployed (3 features)
  - summarised (1 feature)

================================================================================
                              END OF DASHBOARD
================================================================================

Dashboard displayed: 0 of 5 features shown (filtered by: archived)
```

## Best Practices

### Dashboard Usage

1. **Regular monitoring**: Run `/dashboard` regularly to monitor project status
2. **Filter for focus**: Use state filters to focus on specific workflow stages
3. **Track completion**: Monitor completion rate to assess project progress
4. **Identify bottlenecks**: Look for states with many features (potential bottlenecks)
5. **Follow recommendations**: Act on the recommended actions provided

### State Filtering

Use filters to focus on specific workflow stages:
- `planned` - See features ready to implement
- `in_progress` - See active implementation work
- `testing` - See features ready for QA
- `review` - See features ready for deployment
- `deployed` - See recently deployed features
- `summarised` - See completed and summarized features
- `archived` - See historical features

### Interpreting Metrics

**Completion Rate:**
- High (>80%): Most features completed, ready for new work
- Medium (50-80%): Balanced portfolio with active and completed work
- Low (<50%): Many active features, consider focusing on completion

**Active Development:**
- High count: Risk of too much parallel work
- Low count: Opportunity to start new features
- Zero: No active work, create or resume features

**Time in State:**
- Long time in `in_progress`: May indicate blocked work
- Long time in `testing`: May indicate QA bottleneck
- Long time in `review`: May indicate review bottleneck
- Long time in `deployed`: Consider summarising

## Notes

- Dashboard reads feature-log.json but does not modify it
- All timestamp calculations use current date/time for accuracy
- State inference supports features without explicit state field (backward compatibility)
- Previous states display shows complete state history with time in each state
- Recommendations are generated dynamically based on current state distribution
- Dashboard is read-only and safe to run at any time
