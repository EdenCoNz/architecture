---
description: Implement feature or fix by reading user stories and executing them in order
args:
  - name: mode
    description: Implementation mode - either "feature" or "fix"
    required: true
  - name: id
    description: Feature ID (for feature mode) or issue number (for fix mode)
    required: true
model: claude-sonnet-4-5
---

## Purpose

Execute user stories for either:
1. **Feature Mode**: Implement a feature by reading user stories from `docs/features/{id}/user-stories.md`
   - Usage: `/implement feature {feature_id}`
2. **Fix Mode**: Implement a bug fix by reading user stories from `docs/features/{featureID}/issues/{issue_number}/user-stories.md`
   - Usage: `/implement fix {issue_number}`

This command reads the user stories file, processes the execution order, and coordinates implementation across multiple phases.

## Variables

### Feature Mode Variables (when mode="feature")
- `$FEATURE_ID` - The feature ID number from the second argument (e.g., "5" for Feature #5)
- User stories path: `docs/features/$FEATURE_ID/user-stories.md`
- Implementation log path: `docs/features/$FEATURE_ID/implementation-log.json`
- Feature log path: `docs/features/feature-log.json`

### Fix Mode Variables (when mode="fix")
- `$ISSUE_NUMBER` - The GitHub issue number from the second argument
- `$FEATURE_ID` - The feature ID extracted from the issue user stories file path
- User stories path: `docs/features/{featureID}/issues/{issue_number}/user-stories.md`
- Implementation log path: `docs/features/{featureID}/implementation-log.json` (same as feature)
- Feature log path: `docs/features/feature-log.json` (updated with fix implementation type)

## Instructions

- First argument MUST be exactly "feature" or "fix" (case-sensitive)
- Second argument is the feature ID (for feature mode) or issue number (for fix mode)
- Check if user-stories file exists before proceeding
- Skip stories/fixes that are already completed (found in implementation logs)
- Execute ALL user stories regardless of agent type
- Respect execution order: sequential phases run one-by-one, parallel phases run simultaneously
- Each agent MUST record their work in the implementation log
- Update feature log when ALL stories are completed (both feature and fix modes)

## Workflow

### Step 0: Validate Arguments and Determine Execution Mode

1. **Validate argument count**:
   - Verify exactly 2 arguments are provided
   - If not: Display error with usage examples:
     ```
     Error: /implement requires exactly 2 arguments.

     Usage:
       /implement feature {feature_id}  - Implement feature stories
       /implement fix {issue_number}    - Implement fix stories

     Examples:
       /implement feature 5
       /implement fix 87
     ```

2. **Validate mode argument (first argument)**:
   - Check if first argument is exactly "feature" or "fix" (case-sensitive)
   - If not: Display error:
     ```
     Error: First argument must be either "feature" or "fix" (case-sensitive).

     Usage:
       /implement feature {feature_id}
       /implement fix {issue_number}

     Examples:
       /implement feature 5
       /implement fix 87
     ```

3. **Validate ID argument (second argument)**:
   - Verify second argument is numeric
   - If not: Display error:
     ```
     Error: Second argument must be a numeric ID.

     Usage:
       /implement feature {feature_id}  - where feature_id is numeric
       /implement fix {issue_number}    - where issue_number is numeric

     Examples:
       /implement feature 5
       /implement fix 87
     ```

4. **Set mode and variables**:
   - If mode is "feature":
     - Set execution mode to FEATURE_MODE
     - Set `$FEATURE_ID` to the second argument value
     - User stories path: `docs/features/{feature_id}/user-stories.md`
     - Implementation log path: `docs/features/{feature_id}/implementation-log.json`
   - If mode is "fix":
     - Set execution mode to FIX_MODE
     - Set `$ISSUE_NUMBER` to the second argument value
     - User stories path: `docs/features/{feature_id}/issues/{issue_id}/user-stories.md`
     - Implementation log path: `docs/features/{feature_id}/implementation-log.json`

5. **Display mode confirmation**:
   - **FEATURE_MODE**: "Running in FEATURE MODE for feature #{feature_id}"
   - **FIX_MODE**: "Running in FIX MODE for issue #{issue_number}"

### Step 1: Validate User Stories File

**For FEATURE_MODE**:
1. Check if user-stories file exists at `docs/features/{feature_id}/user-stories.md`
2. If not found, respond with: "Error: No user stories found for Feature #{feature_id}. Run /feature first."
3. If found, proceed to next step

**For FIX_MODE**:
1. Check if user-stories file exists at `docs/features/{feature_id}/issues/{issue_number}/user-stories.md`
2. If not found, respond with: "Error: No user stories found for Feature #{issue_id}. Run /fix first."
3. If found, proceed to next step

### Step 2: Parse Execution Order

1. Read the user-stories.md file
2. Parse the Execution Order section
3. Identify all phases and their execution mode (sequential/parallel)

### Step 3: Execute User Stories

For each phase in the execution order:

1. Skip stories that are already completed (check implementation-log.json)
2. Execute ALL stories in the phase regardless of agent type
3. For sequential phases:
   - Launch agents one by one in the specified order
   - Wait for each to complete before starting the next
4. For parallel phases:
   - Launch all agents in the phase simultaneously
   - Use multiple Task tool calls in a single message

### Step 4: Pass Story Context to Agents

```
Feature ID: {feature_id}

Implement the following user story from docs/features/{feature_id}/user-stories.md:

[Story Title]
[Story Description]

Acceptance Criteria:
[List all acceptance criteria]

Execute this implementation following best practices and ensure all acceptance criteria are met.

IMPORTANT: After completing this user story, you MUST record your work in docs/features/{feature_id}/implementation-log.json with:
- Story number and title
- Timestamp of completion
- All files created or modified
- All actions taken (tool calls, decisions made)
- Any issues encountered and how they were resolved
- Status (completed/partial/blocked)
- If the file already exists, append to it. If it doesn't exist, create it as a JSON array.

If this is a design story (ui-ux-designer agent) and you updated the design brief, also update docs/features/feature-log.json by appending to the "actions" array for the feature with matching featureID:
{"actionType": "design", "completedAt": "{YYYY-MM-DDTHH:mm:ssZ}", "designBriefUpdated": true}
```

### Step 5: Verify Completion and Update Feature Log

After all phases complete:

1. Verify all stories in the execution order have been completed by checking implementation-log.json

2. **Update feature-log.json for both FEATURE_MODE and FIX_MODE**:

   If ALL stories are completed:
   - Read the current `docs/features/feature-log.json` file
   - Find the feature entry with matching featureID
   - If it's an issue, find the issue entry under the existing feature (If fix mode) 
   - Append a new implementation entry to the feature's `implementations` array (create array if it doesn't exist)

   **For FEATURE_MODE**:
   - Add implementation entry with:
     ```json
     {
       "type": "feature",
       "timestamp": "{YYYY-MM-DDTHH:mm:ssZ}",
       "status": "completed",
       "implementationLog": "docs/features/{feature_id}/implementation-log.json"
     }
     ```
   - If this is the FIRST feature implementation for this feature:
     - Also set `userStoriesImplemented` to current timestamp (for backward compatibility)
     - Ensure `isSummarised` is set to `false`

   **For FIX_MODE**:
   - Add implementation entry with:
     ```json
     {
       "type": "fix",
       "timestamp": "{YYYY-MM-DDTHH:mm:ssZ}",
       "status": "completed",
       "implementationLog": "docs/features/{feature_id}/implementation-log.json"
     }
     ```

3. **Validation**:
   - Ensure the feature entry exists in feature-log.json before updating
   - If not found, display error: "Error: Feature #{feature_id} not found in feature-log.json"
   - Verify the JSON structure is valid before writing

Note: The `implementations` array provides a complete history of all work on the feature (both initial implementation and subsequent fixes). The `isSummarised` property tracks whether this feature has been summarised by the /summarise command to reduce context for future agents.

## Report

Provide a comprehensive summary that includes:

### Mode Information
- Execution mode (FEATURE_MODE or FIX_MODE)
- Feature ID
- Issue number (if FIX_MODE)

### Story Execution
- Total number of user stories processed
- Number of stories completed vs. skipped
- List of all agents launched and their status
- Any stories that failed or are blocked

### File Locations
- User stories file path
- Implementation log location
- Feature log location

### Feature Log Update
- Confirmation of feature log update if all stories completed
- Implementation type (feature or fix)
- Issue number (if FIX_MODE)
- Timestamp of completion

### Overall Status
- Clear indication of success or partial completion
- Next steps for user
