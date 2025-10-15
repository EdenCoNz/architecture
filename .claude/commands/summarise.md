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

## Workflow

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
3. Add or update the following properties:
   - `isSummarised`: `true`
   - `summarisedAt`: Current timestamp in ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ)
4. Write the updated feature-log.json back

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
