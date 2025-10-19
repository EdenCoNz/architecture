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
- Launch agents directly with appropriate context for each story
- Record implementation in implementation log after each story
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

### Step 3: Execute User Stories

For each phase in the execution order:

1. Skip stories that are already completed (check implementation-log.json)
2. For each story in the phase:
   - Extract story details (title, description, acceptance criteria, agent, dependencies)
   - Load appropriate context based on agent type and story keywords
   - Launch the agent with the story and context
   - Record implementation in implementation-log.json

#### Context Loading for Stories

**Agent Default Context (always load):**
- ui-ux-designer → `context/design/**/*`
- frontend-developer → `context/frontend/**/*`
- backend-developer → `context/backend/**/*`
- devops-engineer → `context/devops/**/*`

**Keyword-Based Additional Context:**
Analyze story title and description for keywords:

- "Material UI" or "MUI" → `context/frontend/material-ui-best-practices.md`
- "React" or "component" → `context/frontend/react-typescript-best-practices-2024-2025.md`
- "Docker" or "container" → `context/devops/docker.md`
- "GitHub Actions" or "CI/CD" → `context/devops/github-actions.md`
- "Django" or "DRF" → `context/backend/django-drf-mysql-best-practices.md`

#### Execution Modes

3. For sequential phases:
   - Execute stories one by one in the specified order
   - Wait for each to complete before starting the next
4. For parallel phases:
   - Launch multiple agents simultaneously using the Task tool
   - Use multiple Task tool calls in a single message

**Example for Sequential Phase:**
```
For Phase 1 (Sequential) with stories 1, 2, 3:
- Execute story 1: Load context → Launch agent → Record in log
- Wait for completion
- Execute story 2: Load context → Launch agent → Record in log
- Wait for completion
- Execute story 3: Load context → Launch agent → Record in log
```

**Example for Parallel Phase:**
```
For Phase 2 (Parallel) with stories 4, 5:
- Load context for both stories
- Launch both agents simultaneously in one message using Task tool
- Record both in log after completion
```

#### Implementation Log Format

After each story completes, append to implementation-log.json:
```json
{
  "storyNumber": 1,
  "storyTitle": "Story title",
  "agent": "agent-type",
  "status": "completed|partial|blocked",
  "completedAt": "YYYY-MM-DDTHH:mm:ssZ",
  "filesModified": ["relative/path/to/file.ts"],
  "filesCreated": ["relative/path/to/newfile.ts"],
  "actions": ["Action description"],
  "toolsUsed": ["Write", "Edit"],
  "issuesEncountered": ["Issue description"],
  "notes": "Additional notes"
}
```

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
