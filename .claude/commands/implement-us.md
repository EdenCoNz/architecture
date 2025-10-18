---
description: Implement a single user story with intelligent context loading
args:
  - name: type
    description: Type of implementation (feature or bug)
    required: true
  - name: id
    description: Feature or bug ID
    required: true
  - name: story_number
    description: User story number to implement
    required: true
model: claude-sonnet-4-5
---

## Purpose

Implement a single user story by:
1. Identifying the required agent from the story
2. Analyzing story keywords to determine context needs
3. Loading appropriate context files intelligently
4. Launching the agent with all necessary context

This command is designed to be called by `/implement` for each story, but can also be used independently.

## Variables

- `$TYPE` - The type of implementation ("feature" or "bug")
- `$ID` - The feature or bug ID number (e.g., "001" for Feature #001 or "github-issue-30" for Bug)
- `$STORY_NUMBER` - The story number to implement (e.g., "1", "5", "10")

## Instructions

Execute a single user story with intelligent context loading and agent orchestration.

## Workflow

### Step 0: Determine File Paths Based on Type

1. If `$TYPE` is "feature":
   - Set user stories path to `docs/features/$ID/user-stories.md`
   - Set implementation log path to `docs/features/$ID/implementation-log.json`
2. If `$TYPE` is "bug":
   - Search for user stories by pattern: `docs/features/*/bugs/$ID/user-stories.md`
   - If found, extract the feature ID from the path
   - Set user stories path to `docs/features/$FEATUREID/bugs/$ID/user-stories.md`
   - Set implementation log path to `docs/features/$FEATUREID/bugs/$ID/implementation-log.json`
3. If `$TYPE` is neither "feature" nor "bug":
   - Respond with: "Error: Type must be either 'feature' or 'bug'"
   - Stop execution

### Step 1: Validate and Read User Story

1. Check if user stories file exists at the determined path
2. If not found:
   - Respond with: "Error: No user stories found at {path}"
   - Stop execution
3. Read the user stories file
4. Parse and locate the specific story by `$STORY_NUMBER`
5. Extract from the story:
   - Story title
   - Story description
   - Acceptance criteria
   - Agent type (e.g., "Agent: frontend-developer")
   - Dependencies (if any)
6. If story not found:
   - Respond with: "Error: Story #$STORY_NUMBER not found in user stories"
   - Stop execution

### Step 2: Check if Story Already Completed

1. Check if implementation log exists at the determined path
2. If implementation log exists:
   - Read the log file
   - Check if story `$STORY_NUMBER` is already marked as completed
   - If completed:
     - Respond with: "Story #$STORY_NUMBER already completed. Skipping."
     - Stop execution
3. If not completed or log doesn't exist, proceed to next step

### Step 3: Analyze Story for Context Keywords

**Extract keywords from story title and description. Look for:**

**DevOps keywords:**
- "GitHub Actions", "workflow", "CI/CD", "pipeline", "continuous integration", "automation", ".github/workflows"
- "Docker", "Dockerfile", "container", "containerize", "docker-compose", "image", "multi-stage"

**Frontend keywords:**
- "React", "component", "hooks", "state management", "tsx"
- "Material UI", "MUI", "theme", "sx prop", "styled"

**Backend keywords:**
- "Django", "DRF", "REST Framework", "API", "MySQL", "database", "serializer", "viewset"

**Testing keywords:**
- "test", "testing", "Jest", "Vitest", "pytest", "React Testing Library", "e2e", "Cypress"

**Design keywords:**
- "design", "design system", "design brief", "UI/UX", "user flow", "wireframe", "mockup"

Store all matched keywords for the next step.

### Step 4: Load Agent Default Context

1. Read `context/context-index.yml`
2. Find the agent type in the `agent_defaults` section
3. For each context ID in the agent's defaults:
   - Look up the corresponding file path in the `context_files` section
   - Read the context file
   - Store the content
4. If agent has no defaults in context-index.yml:
   - Map agent to directory:
     - `ui-ux-designer` → `context/design/**/*`
     - `frontend-developer` → `context/frontend/**/*`
     - `backend-developer` → `context/backend/**/*`
     - `devops-engineer` → `context/devops/**/*`
   - Use Glob to find all files in the directory
   - Read all found files

### Step 5: Load Additional Context Based on Keywords

1. Read `context/context-index.yml`
2. For each context file in `context_files`:
   - Compare the matched keywords (from Step 3) with the file's `keywords` list
   - If there's a match AND the file is NOT already loaded in Step 4:
     - Read the context file
     - Add to the context collection
3. Apply `context_rules` from context-index.yml:
   - Check if story text matches any patterns in `context_rules`
   - If matched and context not already loaded:
     - Load the specified context files

**Example logic:**
- If keywords include "Material UI" AND "React":
  - Load both `material-ui` and `react-typescript` contexts
- If keywords include "Docker" AND "GitHub Actions":
  - Load both `docker` and `github-actions` contexts
- If keywords include "test" AND agent is frontend-developer:
  - Load `frontend-testing` context

### Step 6: Launch Agent with Loaded Context

Use the Task tool to launch the agent with the following prompt structure:

```
Context Files Loaded:
{list all loaded context file paths}

---

{full content of all loaded context files, separated by clear markers}

---

$TYPE ID: $ID
Story #$STORY_NUMBER

Implement the following user story from {user-stories-path}:

**{Story Title}**

{Story Description}

**Acceptance Criteria:**
{List all acceptance criteria as bullets}

**Dependencies:**
{List dependencies if any, or "None"}

---

IMPLEMENTATION INSTRUCTIONS:

1. Follow all best practices from the loaded context files above
2. Ensure all acceptance criteria are met
3. Write clean, maintainable, well-documented code
4. Include appropriate error handling
5. Follow the project's established patterns and conventions

CRITICAL - RECORD YOUR WORK:

After completing this user story, you MUST record your work in {implementation-log-path}:

If the file already exists, read it first, then append your entry. If it doesn't exist, create it as a JSON array with your entry.

**JSON Format:**
```json
{
  "storyNumber": $STORY_NUMBER,
  "storyTitle": "{Story Title}",
  "agent": "{agent-type}",
  "status": "completed|partial|blocked",
  "completedAt": "{YYYY-MM-DDTHH:mm:ssZ}",
  "filesModified": [
    "relative/path/to/file1.ts",
    "relative/path/to/file2.tsx"
  ],
  "filesCreated": [
    "relative/path/to/newfile.ts"
  ],
  "actions": [
    "Description of action 1",
    "Description of action 2"
  ],
  "toolsUsed": [
    "Write", "Edit", "Bash"
  ],
  "issuesEncountered": [
    "Description of any issues and how they were resolved"
  ],
  "notes": "Any additional notes about the implementation"
}
```

**IMPORTANT:**
- Use RELATIVE paths from project root (e.g., "frontend/src/App.tsx" NOT "/home/user/project/frontend/src/App.tsx")
- Set status to "completed" only if ALL acceptance criteria are met
- Set status to "partial" if some criteria are met but work is incomplete
- Set status to "blocked" if you cannot proceed due to dependencies or issues

**Special Instructions for ui-ux-designer:**

If you are the ui-ux-designer agent and you updated the design brief:
1. Record your work in the implementation log as described above
2. Also update `docs/features/feature-log.json`:
   - Read the current feature-log.json
   - Find the feature entry with matching featureID: "$ID"
   - Append to the "actions" array:
     ```json
     {
       "actionType": "design",
       "completedAt": "{YYYY-MM-DDTHH:mm:ssZ}",
       "designBriefUpdated": true
     }
     ```
   - Write the updated feature-log.json back

```

**Note:** Replace all placeholders with actual values before passing to the agent.

### Step 7: Report Completion

After the agent completes, provide a summary:

```
✓ Story #$STORY_NUMBER completed by {agent-type}

Story: {Story Title}

Context loaded:
- {context-file-1}
- {context-file-2}
...

Implementation recorded in: {implementation-log-path}

The agent has completed this user story. Check the implementation log for detailed information about files modified and actions taken.
```

If the agent reported any issues or the story is marked as "blocked" or "partial", include that information in the report.

## Examples

### Example 1: Implement Feature Story
```
/implement-us feature 1 5
```

This will:
1. Read story #5 from `docs/features/1/user-stories.md`
2. Identify the agent type
3. Analyze keywords
4. Load appropriate context
5. Launch agent with story details
6. Record implementation in `docs/features/1/implementation-log.json`

### Example 2: Implement Bug Fix Story
```
/implement-us bug github-issue-30 2
```

This will:
1. Find user stories at `docs/features/*/bugs/github-issue-30/user-stories.md`
2. Read story #2
3. Follow the same process as Example 1
4. Record implementation in the bug's implementation log

## Error Handling

**If story is blocked due to dependencies:**
- Report the blocking dependencies
- Mark story as "pending" in todo list
- Do not proceed with implementation

**If context files are missing:**
- Warn about missing context
- Proceed with available context
- Note the missing context in the implementation log

**If agent fails:**
- Report the failure
- Keep the story status as "pending" or "blocked"
- Include error details in report
