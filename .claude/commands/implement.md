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
- User stories path (bug): `docs/features/$FEATUREID/bugs/$ID/user-stories.md`
- Implementation log path (feature): `docs/features/$ID/implementation-log.json`
- Implementation log path (bug): `docs/features/$FEATUREID/bugs/$ID/implementation-log.json`
- Feature log path: `docs/features/feature-log.json`

## Instructions

- Check if user-stories file exists before proceeding
- Skip stories that are already completed (found in implementation logs)
- Execute ALL user stories regardless of agent type (ui-ux-designer, frontend-developer, backend-developer, devops-engineer, etc.)
- Respect execution order: sequential phases run one-by-one, parallel phases run simultaneously
- **IMPORTANT**: Call /implement-us for each story (it handles context loading and agent orchestration)
- Each story will be implemented by /implement-us which records work in implementation log
- Update feature log only when ALL stories are completed

## Workflow

### Step 0: Determine Paths Based on Type

1. If `$TYPE` is "feature":
   - Set base path to `docs/features/$ID`
   - Set user stories path to `docs/features/$ID/user-stories.md`
   - Set implementation log path to `docs/features/$ID/implementation-log.json`
2. If `$TYPE` is "bug":
   - The ID should be in the format "github-issue-{number}" (e.g., "github-issue-10")
   - Extract the feature ID from the user stories path (typically the bug user stories are at docs/features/{FEATUREID}/bugs/{ID}/user-stories.md)
   - Search for the user stories file by pattern: docs/features/*/bugs/$ID/user-stories.md
   - If found, use the parent feature directory as FEATUREID
   - Set base path to `docs/features/$FEATUREID/bugs/$ID`
   - Set user stories path to `docs/features/$FEATUREID/bugs/$ID/user-stories.md`
   - Set implementation log path to `docs/features/$FEATUREID/bugs/$ID/implementation-log.json`
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

### Step 3: Execute User Stories Using /implement-us

For each phase in the execution order:

1. Skip stories that are already completed (check implementation-log.json)
2. Execute ALL stories in the phase using the `/implement-us` command
3. For sequential phases:
   - Call `/implement-us $TYPE $ID {story-number}` one by one in the specified order
   - Wait for each to complete before starting the next
4. For parallel phases:
   - Call `/implement-us $TYPE $ID {story-number}` for all stories simultaneously
   - Use multiple SlashCommand tool calls in a single message

**Example for Sequential Phase:**
```
For Phase 1 (Sequential) with stories 1, 2, 3:
- Call: /implement-us feature 1 1
- Wait for completion
- Call: /implement-us feature 1 2
- Wait for completion
- Call: /implement-us feature 1 3
```

**Example for Parallel Phase:**
```
For Phase 2 (Parallel) with stories 4, 5:
- Call both simultaneously in one message:
  - /implement-us feature 1 4
  - /implement-us feature 1 5
```

**Note:** The `/implement-us` command handles:
- Story parsing and validation
- Agent identification
- Context loading (agent defaults + keyword-based)
- Agent orchestration
- Implementation log recording

### Step 4: Verify Completion and Update Feature Log

After all phases complete:

1. Verify all stories in the execution order have been completed by checking implementation-log.json
2. If ALL stories are completed:
   - Read the current feature-log.json file
   - Find the feature entry with matching featureID
   - Set `userStoriesImplemented` to current timestamp in ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ)
   - Ensure `isSummarised` is set to `false` (it should already be false from feature creation)
   - Write the updated feature-log.json file back

Note: The `isSummarised` property tracks whether this feature has been summarised by the /summarise command to reduce context for future agents.

### Step 5: Commit Implementation and Push

After all stories are completed and feature log is updated:

1. **Read implementation-log.json**: Extract all completed stories and files modified from the determined implementation log path
2. **Read feature-log.json**: Get the title for this feature/bug ID
3. **Determine issue number for bug fixes**:
   - If `$TYPE` is "bug" and `$ID` matches the pattern "github-issue-{number}":
     - Extract the issue number (e.g., "github-issue-123" → "123")
   - Otherwise, set issue number to null
4. **Create detailed commit message**: Use the following format:

   For bugs with GitHub issue:
   ```
   Implementation of {type}-{id}-{title}

   Completed user stories:
   - Story #{num}: {story-title}
   - Story #{num}: {story-title}

   Files modified:
   - {file1}
   - {file2}

   Fixes #{issue-number}
   ```

   For features or bugs without GitHub issue:
   ```
   Implementation of {type}-{id}-{title}

   Completed user stories:
   - Story #{num}: {story-title}
   - Story #{num}: {story-title}

   Files modified:
   - {file1}
   - {file2}
   ```

   Note: {type} should be lowercase ("feature" or "bug")
5. **Commit and push**: Use the SlashCommand tool to execute:
   ```
   /commit "{commit message}" push
   ```
   Note: Use `-u` flag in a separate git push command only if this is the first push to the remote branch

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
