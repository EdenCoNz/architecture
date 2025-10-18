---
description: Call any agent with optional context loading
args:
  - name: agent
    description: Agent type to call
    required: true
  - name: prompt
    description: The task or prompt to pass to the agent
    required: true
  - name: context
    description: Optional specific context file to load from context/ folder
    required: false
---

## Purpose

Launch any available agent with intelligent context loading. This command provides a flexible way to invoke agents with either selective context (if specified) or default context based on the agent type.

## Variables

- `$AGENT` - The agent type to call (must be one of the valid agents)
- `$PROMPT` - The task or prompt to pass to the agent
- `$CONTEXT` - Optional context file path relative to context/ folder (e.g., "devops/docker.md")

## Valid Agents

The following agents are available:
- `ui-ux-designer` - UI/UX design work, design systems, user flows
- `frontend-developer` - Frontend architecture, React/TypeScript, testing strategies
- `backend-developer` - Backend development, APIs, database design
- `devops-engineer` - Docker, GitHub Actions, CI/CD pipelines
- `product-owner` - Transform feature requests into user stories
- `research-specialist` - Research technical topics and best practices

## Instructions

Follow these steps to validate the agent and load the appropriate context before launching.

## Workflow

### Step 1: Validate Agent Type

1. Check if `$AGENT` matches one of the valid agent types listed above
2. If `$AGENT` is not valid:
   - Respond with: "Error: Invalid agent type '$AGENT'. Valid agents are: ui-ux-designer, frontend-developer, backend-developer, devops-engineer, product-owner, research-specialist"
   - Stop execution
3. If valid, proceed to next step

### Step 2: Determine Context to Load

**If `$CONTEXT` is provided:**

1. Check if the context file exists at `context/$CONTEXT`
2. If file does not exist:
   - Respond with: "Error: Context file 'context/$CONTEXT' not found"
   - Stop execution
3. If file exists:
   - Read the specified context file: `context/$CONTEXT`
   - Store the content for passing to the agent
   - Continue to Step 3

**If `$CONTEXT` is NOT provided (default behavior):**

1. Read `context/context-index.yml` to find the agent's default context
2. Look up the agent in the `agent_defaults` section
3. For each context ID in the agent's defaults:
   - Find the corresponding `path` in the `context_files` section
   - Read each context file
   - Store all content for passing to the agent
4. If agent has no defaults in context-index.yml:
   - Use Glob to find all files in the agent's context directory: `context/{domain}/**/*`
     - ui-ux-designer → `context/design/**/*`
     - frontend-developer → `context/frontend/**/*`
     - backend-developer → `context/backend/**/*`
     - devops-engineer → `context/devops/**/*`
   - Read all found files
5. Continue to Step 3

### Step 3: Launch Agent with Context

Use the Task tool to launch the specified agent with the following prompt structure:

```
Context Loading:
{loaded-context-content}

---

$PROMPT
```

Where:
- `{loaded-context-content}` is the content from all loaded context files (from Step 2)
- `$PROMPT` is the user's task/request for the agent

## Report

Provide a brief summary that includes:
- Agent type launched
- Context files loaded (list all paths)
- Confirmation that agent is running
- Brief description of what the agent will do based on the user's input

## Examples

### Example 1: Call devops-engineer with default context
```
/callagent devops-engineer "Optimize our GitHub Actions workflow"
```
This will:
- Load context/devops/github-actions.md and context/devops/docker.md (agent defaults)
- Launch devops-engineer agent with the task: "Optimize our GitHub Actions workflow"

### Example 2: Call frontend-developer with specific context
```
/callagent frontend-developer "Review Dockerfile for frontend build" devops/docker.md
```
This will:
- Load only context/devops/docker.md (specified context)
- Launch frontend-developer agent with the task: "Review Dockerfile for frontend build"

### Example 3: Call ui-ux-designer with default context
```
/callagent ui-ux-designer "Design a dashboard for analytics"
```
This will:
- Load context/frontend/material-ui-best-practices.md (agent default)
- Launch ui-ux-designer agent with the task: "Design a dashboard for analytics"
