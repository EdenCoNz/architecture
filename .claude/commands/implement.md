---
description: Implement feature by reading user stories and executing them in order
args:
  - name: id
    description: Feature ID to implement (reads from docs/features/{id}/user-stories.md)
    required: true
model: claude-sonnet-4-5
---

## Purpose

Execute user stories for a specific feature by launching appropriate agents in the correct order. This command reads the user stories file, processes the execution order, and coordinates implementation across multiple phases.

## Variables

- `$ID` - The feature ID number (e.g., "001" for Feature #001)
- User stories path: `docs/features/$ID/user-stories.md`
- Implementation log path: `docs/features/$ID/implementation-log.json`
- Feature log path: `docs/features/feature-log.json`

## Instructions

- Check if user-stories file exists before proceeding
- Skip stories that are already completed (found in implementation logs)
- Execute ALL user stories regardless of agent type
- Respect execution order: sequential phases run one-by-one, parallel phases run simultaneously
- Each agent MUST record their work in the implementation log
- Update feature log only when ALL stories are completed

## Workflow

### Step 1: Validate User Stories File

1. Check if user-stories file exists at `docs/features/$ID/user-stories.md`
2. If not found, respond with: "Error: No user stories found for Feature #$ID. Run /plan first."
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

For each agent, provide:

```
Feature ID: $ID

Implement the following user story from docs/features/$ID/user-stories.md:

[Story Title]
[Story Description]

Acceptance Criteria:
[List all acceptance criteria]

Execute this implementation following best practices and ensure all acceptance criteria are met.

IMPORTANT: After completing this user story, you MUST record your work in docs/features/$ID/implementation-log.json with:
- Story number and title
- Timestamp of completion
- All files created or modified
- All actions taken (tool calls, decisions made)
- Any issues encountered and how they were resolved
- Status (completed/partial/blocked)
- If the file already exists, append to it. If it doesn't exist, create it as a JSON array.

If this is a design story (ui-ux-designer agent) and you updated the design brief, also update docs/features/feature-log.json by appending to the "actions" array:
{"actionType": "design", "completedAt": "{YYYY-MM-DDTHH:mm:ssZ}", "designBriefUpdated": true}
```

### Step 5: Verify Completion and Update Feature Log

After all phases complete:

1. Verify all stories in the execution order have been completed by checking implementation-log.json
2. If ALL stories are completed:
   - Read the current feature-log.json file
   - Find the feature entry with matching featureID
   - Set `userStoriesImplemented` to current timestamp in ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ)
   - Ensure `isSummarised` is set to `false` (it should already be false from feature creation)
   - Write the updated feature-log.json file back

Note: The `isSummarised` property tracks whether this feature has been summarised by the /summarise command to reduce context for future agents.

## Report

Provide a comprehensive summary that includes:
- Total number of user stories processed
- Number of stories completed vs. skipped
- List of all agents launched and their status
- Any stories that failed or are blocked
- Confirmation of feature log update if all stories completed
- Implementation log location for detailed records
