---
description: Summarise implemented features to reduce context for future agents
model: claude-sonnet-4-5
---

## Purpose

Analyze implemented features and create concise summaries of what was actually accomplished versus what failed. This reduces context loading for future agents by consolidating implementation logs into digestible summaries while preserving critical information about successes and failures.

## Variables

- Feature log path: `docs/features/feature-log.json`
- Implementation log path: `docs/features/{id}/implementation-log.json`
- Summary path: `docs/features/implementation-log-summary.json`

## Instructions

- Process ONLY features that have NOT been summarised yet (isSummarised is false or missing)
- Skip features that don't have implementation logs
- Create objective summaries focused on actual outcomes, not intentions
- Preserve information about failures, blockers, and workarounds
- Update feature-log.json to mark features as summarised

## Error Handling

This command uses comprehensive error handling with specific error codes and recovery suggestions.

**Error Handling Reference**: See `.claude/helpers/command-error-handling.md` for complete error code documentation and `.claude/helpers/error-code-mapping.md` for validation error mapping.

**Common Errors**:
- ENV-001: Git repository not found → Initialize git or navigate to repository
- FS-001: Feature log not found → Run /feature command first
- FS-005: Invalid JSON in feature-log or implementation-logs → Fix JSON syntax
- STATE-003: Feature already summarized → Skip feature (informational)
- STATE-004: Invalid state transition → Fix state before summarizing
- DATA-005: Feature references don't exist → Verify feature IDs
- DEP-004: No unsummarised features → Informational, no work to do

**Error Handling Strategy**:
- All validation errors (Step 0) use standardized error codes
- No unsummarised features is INFORMATIONAL - not an error, just no work
- Invalid JSON in single feature's log is WARNING - skip that feature, process others
- Missing user stories file is WARNING - skip that feature, process others
- State transition errors stop processing for that feature only
- Feature log errors are BLOCKING - cannot proceed without valid feature log

## Workflow

### Step 0: Pre-Flight Validation

Before executing any operations, run comprehensive validation checks to ensure prerequisites are met.

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
Command: /summarise

Remediation:
1. Navigate to your git repository directory
2. Verify you are in the correct directory:
   pwd
3. This command requires a git repository to commit summaries
```
- STOP execution immediately

#### Step 0.3: Validate Feature Log Exists

Check if docs/features/feature-log.json exists:
```bash
test -f "docs/features/feature-log.json" && echo "VALID" || echo "INVALID"
```

If output is "INVALID":
- Display error message:
```
Error: Feature log not found

File: docs/features/feature-log.json
Purpose: Lists features to be summarised
Command: /summarise

Remediation:
1. Ensure you are in the correct project directory
2. Run /feature command at least once to initialize the feature log
3. Implement features before running /summarise

Example:
  /feature "Initialize project structure"
```
- STOP execution immediately

Validate JSON syntax:
```bash
python3 -c "import json; json.load(open('docs/features/feature-log.json'))" 2>&1
```

If JSON validation fails:
- Display error message with specific JSON error and remediation steps (see pre-flight-validation.md)
- STOP execution immediately

#### Step 0.4: Identify Unsummarised Features with Implementation Logs

Read feature-log.json and filter features where:
- `isSummarised` is `false` OR `isSummarised` property doesn't exist
- AND `userStoriesImplemented` is not null (feature has been implemented)

For each unsummarised feature, check if implementation log exists:
```bash
test -f "docs/features/{id}/implementation-log.json" && echo "VALID" || echo "INVALID"
```

Count the number of unsummarised features with valid implementation logs.

If count is 0:
- Display informational message:
```
No unsummarised features found

Status: All implemented features have already been summarised
Features in log: {total_count}
Already summarised: {summarised_count}
Not yet implemented: {not_implemented_count}
Command: /summarise

Information:
This is normal - there is no work to be done. The /summarise command only
processes features that:
1. Have been implemented (userStoriesImplemented is set)
2. Have NOT been summarised yet (isSummarised is false or missing)

Next Steps:
1. Implement new features using /implement command
2. Run /summarise again after features are implemented
3. Or manually set isSummarised: false for a feature to re-summarise it

Existing summaries can be found at:
  docs/features/implementation-log-summary.json
```
- STOP execution (no work to do, not an error)

#### Step 0.5: Validate Implementation Logs (For Each Unsummarised Feature)

For each unsummarised feature with implementation log:

Check if user-stories.md exists:
```bash
test -f "docs/features/{id}/user-stories.md" && echo "VALID" || echo "INVALID"
```

If user-stories.md missing:
- Display warning message:
```
Warning: User stories file missing for Feature #{id}

File: docs/features/{id}/user-stories.md
Status: Implementation log exists but user stories file not found
Impact: Cannot generate complete summary without original user stories

Recommendation:
1. This may indicate a file system issue
2. Skip this feature for now
3. Investigate why user stories file is missing

Skipping Feature #{id} - will continue with other features.
```
- Skip this feature (continue with others)

Validate implementation log JSON syntax:
```bash
python3 -c "import json; json.load(open('docs/features/{id}/implementation-log.json'))" 2>&1
```

If JSON validation fails:
- Display warning message:
```
Warning: Implementation log contains invalid JSON

File: docs/features/{id}/implementation-log.json
Status: JSON syntax error in implementation log
Impact: Cannot summarise Feature #{id}

Recommendation:
1. Fix JSON syntax error in implementation log
2. Or delete the file and re-run /implement
3. Skip this feature for now

Skipping Feature #{id} - will continue with other features.
```
- Skip this feature (continue with others)

#### Step 0.6: Validation Summary

If validation passes and unsummarised features found:
- Output: "Pre-flight validation passed - proceeding with summarisation"
- Display summary:
```
Validation Summary:
  ✓ Git repository validated
  ✓ Feature log validated
  ✓ {count} unsummarised features found with implementation logs
  ✓ Ready to generate summaries

Features to summarise:
  - Feature #{id}: {title}
  - Feature #{id}: {title}
  ...

Proceeding with summarisation...
```
- Proceed to Step 1

If no unsummarised features found:
- Execution stopped (no work to do)
- This is informational, not an error

If any critical validation failed:
- Execution has already been stopped
- User must remediate issues and re-run command

### Step 1: Validate Feature Log

1. Check if feature-log.json exists at `docs/features/feature-log.json`
2. If not found, respond with: "Error: No feature log found. Run /feature first to create features."
3. If found, proceed to next step

### Step 2: Identify Unsummarised Features

1. Read the feature-log.json file
2. Filter features where:
   - `isSummarised` is `false` OR
   - `isSummarised` property doesn't exist
3. For each unsummarised feature, check if implementation-log.json exists
4. Create a list of features ready for summarisation

### Step 3: Analyze Implementation Logs

For each unsummarised feature with an implementation log:

1. Read `docs/features/{id}/implementation-log.json`
2. Read `docs/features/{id}/user-stories.md` to understand original intent
3. Analyze what was completed vs what failed:
   - **Completed stories**: Stories with status "completed"
   - **Partial stories**: Stories with status "partial" (what was done, what wasn't)
   - **Blocked stories**: Stories with status "blocked" (why they were blocked)
   - **Missing stories**: Stories from user-stories.md not in implementation log
4. Extract key information:
   - Files created or modified
   - Major technical decisions made
   - Issues encountered and resolutions
   - Patterns or approaches used
   - Any deviations from original plan

### Step 4: Generate Summary

Create or update `docs/features/implementation-log-summary.json` with summaries for each feature. The JSON structure should be:

```json
{
  "summaries": [
    {
      "featureId": "{id}",
      "featureTitle": "{feature title from feature-log.json}",
      "summarisedAt": "{ISO 8601 timestamp}",
      "overview": "{2-3 sentence summary of what this feature was meant to accomplish}",
      "completedWork": {
        "storiesCompleted": {
          "count": 0,
          "total": 0,
          "stories": [
            {
              "storyNumber": 1,
              "title": "{story title}",
              "summary": "{one-line summary}"
            }
          ]
        },
        "filesModified": [
          {
            "path": "{file_path}",
            "description": "{brief description of changes}"
          }
        ],
        "keyTechnicalDecisions": [
          "{Decision and rationale}"
        ]
      },
      "incompleteWork": {
        "storiesNotCompleted": [
          {
            "storyNumber": 0,
            "title": "{story title}",
            "status": "{partial/blocked/not started}",
            "reason": "{why it wasn't completed}",
            "whatWasDone": "{if partial, what was accomplished}"
          }
        ],
        "knownIssues": [
          "{unresolved issues or technical debt}"
        ]
      },
      "implementationInsights": "{patterns, learnings, or important context}",
      "recommendations": [
        "{suggestions for future work}"
      ]
    }
  ],
  "metadata": {
    "lastUpdated": "{ISO 8601 timestamp}",
    "totalFeaturesSummarised": 0
  }
}
```

### Step 5: Update Feature Log

After creating the summary for each feature:

1. Read the current feature-log.json
2. Find each feature entry that was summarised
3. For each feature:
   - Read current state from feature entry
   - Validate transition: {current_state} → summarised (automatic)
   - If validation fails for this feature:
     - Display warning: "Feature #{id} cannot transition to summarised from state '{current_state}' - skipping"
     - Skip this feature (do not add to summary)
     - Continue with other features
   - If valid, proceed with updating this feature:
4. Add or update the following properties for each validated feature:
   - `isSummarised`: `true`
   - `summarisedAt`: Current timestamp in ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ)
   - **Update feature state to "summarised"**:
     - Set `state`: "summarised"
     - Append to `stateHistory` array:
       ```json
       {
         "state": "summarised",
         "timestamp": "{current ISO 8601 timestamp}",
         "triggeredBy": "/summarise command completed",
         "notes": "Feature summarized for reduced context loading"
       }
       ```
     - This automatic state transition marks the feature as summarized for reduced context loading
5. Write the updated feature-log.json back
6. If any features were skipped due to invalid state transitions:
   - List the skipped features with their current states
   - Provide guidance on how to fix state issues

### Step 6: Validate and Report

After processing all features:

1. Verify implementation-log-summary.json was created/updated successfully
2. Confirm feature-log.json was updated
3. List any features that couldn't be summarised and why

## Report

Provide a comprehensive summary that includes:

### Features Summarised: {count}

For each feature:
- **Feature #{id}**: {title}
  - Stories completed: {count}/{total}
  - Summary added to: `docs/features/implementation-log-summary.json`
  - Key outcome: {one sentence}

### Features Skipped: {count}

- **Feature #{id}**: {reason for skipping}

### Summary Statistics

- Total features in log: {count}
- Features already summarised: {count}
- Features newly summarised: {count}
- Features with incomplete implementations: {count}
- Total files modified across all features: {count}

### Context Reduction

- Original implementation logs: {total KB/lines}
- Summary JSON file: {total KB/lines}
- Context reduction: {percentage}%

### Next Steps

{Any recommendations for features that need attention or follow-up}
