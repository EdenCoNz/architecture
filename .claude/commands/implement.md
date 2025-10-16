---
description: Implement feature or bug by reading user stories and executing them in order
args:
  - name: type
    description: Type of implementation (feature or bug)
    required: true
  - name: id
    description: Feature or bug ID to implement
    required: true
model: claude-sonnet-4-5
---

## Purpose

Execute user stories for a specific feature or bug by launching appropriate agents in the correct order. This command reads the user stories file, processes the execution order, and coordinates implementation across multiple phases.

## Variables

- `$TYPE` - The type of implementation ("feature" or "bug")
- `$ID` - The feature or bug ID number (e.g., "001" for Feature #001 or Bug #001)
- User stories path (feature): `docs/features/$ID/user-stories.md`
- User stories path (bug): `docs/features/bugs/$ID/user-stories.md`
- Implementation log path (feature): `docs/features/$ID/implementation-log.json`
- Implementation log path (bug): `docs/features/bugs/$ID/implementation-log.json`
- Feature log path: `docs/features/feature-log.json`

## Instructions

- Check if user-stories file exists before proceeding
- Skip stories that are already completed (found in implementation logs)
- Execute ALL user stories regardless of agent type (ui-ux-designer, frontend-developer, backend-developer, devops-engineer, etc.)
- Respect execution order: sequential phases run one-by-one, parallel phases run simultaneously
- Each agent MUST record their work in the implementation log
- Update feature log only when ALL stories are completed

## Workflow

### Step 0: Determine Paths Based on Type

1. If `$TYPE` is "feature":
   - Set base path to `docs/features/$ID`
   - Set user stories path to `docs/features/$ID/user-stories.md`
   - Set implementation log path to `docs/features/$ID/implementation-log.json`
2. If `$TYPE` is "bug":
   - Set base path to `docs/features/bugs/$ID`
   - Set user stories path to `docs/features/bugs/$ID/user-stories.md`
   - Set implementation log path to `docs/features/bugs/$ID/implementation-log.json`
3. If `$TYPE` is neither "feature" nor "bug":
   - Respond with: "Error: Type must be either 'feature' or 'bug'"
   - Stop execution

### Step 1: Validate User Stories File

1. Check if user-stories file exists at the determined path
2. If not found, respond with: "Error: No user stories found for $TYPE #$ID. Run /plan first."
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

For each agent (regardless of type), provide:

```
$TYPE ID: $ID

Implement the following user story from {user-stories-path}:

[Story Title]
[Story Description]

Acceptance Criteria:
[List all acceptance criteria]

Execute this implementation following best practices and ensure all acceptance criteria are met.

IMPORTANT: After completing this user story, you MUST:

1. Record your work in {implementation-log-path}:
   - Story number and title
   - Timestamp of completion
   - All files created or modified (use RELATIVE paths from project root, e.g., "frontend/src/App.tsx" NOT "/home/user/project/frontend/src/App.tsx")
   - All actions taken (tool calls, decisions made)
   - Any issues encountered and how they were resolved
   - Status (completed/partial/blocked)
   - If the file already exists, append to it. If it doesn't exist, create it as a JSON array.

2. If this is a design story (ui-ux-designer agent) and you updated the design brief:
   - Update docs/features/feature-log.json
   - Find the feature entry with matching featureID
   - Append to the "actions" array:
     ```json
     {
       "actionType": "design",
       "completedAt": "{YYYY-MM-DDTHH:mm:ssZ}",
       "designBriefUpdated": true
     }
     ```
```

Note: Replace {user-stories-path} and {implementation-log-path} with the actual paths determined in Step 0.

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

### Step 6: Commit Implementation and Push

After all stories are completed and feature log is updated:

1. **Read implementation-log.json**: Extract all completed stories and files modified from the determined implementation log path
2. **Read feature-log.json**: Get the title for this feature/bug ID
3. **Create detailed commit message**: Use the following format:
   ```
   Implementation of {type}-{id}-{title}

   Completed user stories:
   - Story #{num}: {story-title}
   - Story #{num}: {story-title}

   Files modified:
   - {file1}
   - {file2}

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```
   Note: {type} should be lowercase ("feature" or "bug")
4. **Stage and commit**: Use Bash tool to:
   - Stage all modified files
   - Create commit with the detailed message using HEREDOC format
5. **Push to remote**: Use Bash tool to push the current branch to remote with `-u` flag

## Report

Provide a comprehensive summary that includes:
- Total number of user stories processed
- Number of stories completed vs. skipped
- List of all agents launched and their status
- Any stories that failed or are blocked
- Confirmation of feature log update if all stories completed
- Implementation log location for detailed records
- Confirmation of commit created and pushed to remote
- Current git branch name
