# Slash Command Context Loading Examples

This document demonstrates how to integrate intelligent context loading into slash commands.

## Pattern 1: Explicit Context Pre-loading

**Use when:** The command always needs specific context files

```markdown
---
description: Improve GitHub Actions CI/CD pipeline
model: claude-sonnet-4-5
---

## Step 1: Load Context

Read the following context files BEFORE starting:
- context/devops/github-actions.md

## Step 2: Execute Task

Launch the devops-engineer agent with the following prompt:

```
Context loaded: context/devops/github-actions.md

Task: Analyze and improve the GitHub Actions workflows in .github/workflows/

Focus on:
- Performance optimization
- Cost reduction
- Security best practices
- Caching strategies

Provide specific recommendations and implementation code.
```
```

## Pattern 2: Conditional Context Loading

**Use when:** Context depends on command arguments

```markdown
---
description: Optimize Docker configuration
args:
  - name: scope
    description: Optimization scope (dockerfile, compose, or both)
    required: true
model: claude-sonnet-4-5
---

## Step 1: Determine Context

Based on $SCOPE argument:
- If "dockerfile": Load context/devops/docker.md (Dockerfile sections)
- If "compose": Load context/devops/docker.md (Docker Compose sections)
- If "both": Load entire context/devops/docker.md

## Step 2: Execute Task

Launch devops-engineer agent with loaded context...
```

## Pattern 3: Multi-Domain Context

**Use when:** Command spans multiple expertise areas

```markdown
---
description: Set up full CI/CD pipeline with containerization
model: claude-sonnet-4-5
---

## Step 1: Load Multi-Domain Context

Read the following context files:
- context/devops/github-actions.md (for CI/CD workflows)
- context/devops/docker.md (for containerization)

## Step 2: Execute Task

Launch devops-engineer agent with comprehensive context:

```
Context loaded:
- context/devops/github-actions.md
- context/devops/docker.md

Task: Design and implement a complete CI/CD pipeline that:
1. Builds Docker images on every commit
2. Runs tests in containers
3. Pushes images to registry on main branch
4. Implements security scanning

Deliver production-ready configuration.
```
```

## Pattern 4: Dynamic Context Resolution

**Use when:** Context should be determined by analyzing the current state

```markdown
---
description: Fix CI/CD issues
model: claude-sonnet-4-5
---

## Step 1: Analyze Current State

1. Check if .github/workflows/ exists
2. Check if Dockerfile exists
3. Check if docker-compose.yml exists

## Step 2: Load Relevant Context

Based on findings:
- If workflows exist: Load context/devops/github-actions.md
- If Dockerfile exists: Load context/devops/docker.md
- If both exist: Load both context files

## Step 3: Execute Task

Launch devops-engineer with dynamically loaded context...
```

## Pattern 5: Context Passthrough from Main Command

**Use when:** Implementing nested commands (like /implement)

```markdown
---
description: Implement feature or bug by reading user stories
args:
  - name: type
    description: Type of implementation (feature or bug)
    required: true
  - name: id
    description: Feature or bug ID
    required: true
model: claude-sonnet-4-5
---

## Step 1: Read User Stories

Read the user stories file from docs/features/$ID/user-stories.md

## Step 2: Determine Required Context

For each user story, analyze which agent is needed:
- ui-ux-designer → No additional context (uses design brief)
- frontend-developer → Check story keywords for context:
  - Contains "Material UI" / "MUI" → context/frontend/material-ui-best-practices.md
  - Contains "React" / "Component" → context/frontend/react-typescript-best-practices-2024-2025.md
- backend-developer → context/backend/django-drf-mysql-best-practices.md
- devops-engineer → Check story keywords:
  - Contains "GitHub Actions" / "CI" → context/devops/github-actions.md
  - Contains "Docker" / "Container" → context/devops/docker.md

## Step 3: Pass Context to Agents

When launching each agent, include explicit context in the task prompt:

```
Context: context/devops/github-actions.md

User Story #3: Set up automated testing in CI pipeline

[Full story details...]

Implement this user story following best practices from the loaded context.
```
```

## Pattern 6: Context Index Query

**Use when:** Need programmatic context resolution

```markdown
---
description: Smart context loader example
model: claude-sonnet-4-5
---

## Step 1: Read Context Index

Read context/context-index.yml to get keyword mappings

## Step 2: Analyze Task Keywords

Extract keywords from the task description:
```python
import re

task = "Optimize Docker images in GitHub Actions"
keywords = ["docker", "github actions", "optimize"]
```

## Step 3: Match Keywords to Context

Look up keywords in context-index.yml:
- "docker" → context/devops/docker.md
- "github actions" → context/devops/github-actions.md

## Step 4: Load Matched Context

Read the matched context files before proceeding...
```

## Best Practices for Commands

### 1. Be Explicit When Possible
If you know exactly what context is needed, specify it explicitly:
```markdown
Read: context/devops/github-actions.md
```

### 2. Use Context Index for Complex Scenarios
For multi-domain or ambiguous tasks, reference the context index:
```markdown
Consult context/context-index.yml to determine required context based on task keywords
```

### 3. Document Context Decisions
Explain why specific context is loaded:
```markdown
## Context Rationale
- github-actions.md: Needed for workflow best practices
- docker.md: Needed for multi-stage build optimization
```

### 4. Support Context Overrides
Allow users to override context if needed:
```markdown
---
args:
  - name: context
    description: Optional context files to load (comma-separated)
    required: false
---

If $CONTEXT is provided, load those files
Otherwise, use default context loading logic
```

### 5. Minimize Context When Possible
Only load what's needed to reduce token usage:
```markdown
# Good: Specific context for specific task
Load: context/devops/docker.md (for Dockerfile optimization)

# Avoid: Loading everything when only one file is needed
Load: context/devops/**/* (when only working on Docker)
```

## Integration with /implement Command

The `/implement` command is a perfect use case for intelligent context loading:

```markdown
### Step 3: Execute User Stories (UPDATED)

For each user story, determine context before launching agent:

1. **Parse Story Keywords**
   - Extract technology keywords (e.g., "Material UI", "Docker", "GitHub Actions")
   - Extract task type (e.g., "testing", "deployment", "UI")

2. **Resolve Context Files**
   - Use context/context-index.yml keyword mappings
   - Match story keywords to context file IDs
   - Build list of context files to load

3. **Launch Agent with Context**
   ```
   Context:
   - context/devops/github-actions.md
   - context/devops/docker.md

   Feature ID: 2
   Story #4: Build and deploy Docker images in CI

   [Story details...]

   Implement following best practices from loaded context.
   ```

4. **Fallback for Unclear Context**
   - If keywords don't match context index, load agent's default context
   - Allows agent to determine what's needed
```

## Summary

| Pattern | When to Use | Example |
|---------|-------------|---------|
| Explicit Pre-loading | Known context requirements | CI improvement command → github-actions.md |
| Conditional Loading | Context depends on args | Docker command with scope arg |
| Multi-Domain | Spans multiple areas | Full-stack feature implementation |
| Dynamic Resolution | Analyze project first | Fix command that checks current state |
| Context Passthrough | Nested commands | /implement passing context to agents |
| Index Query | Complex keyword matching | Smart loader analyzing task description |

**General Recommendation:**
- Start with **Explicit Pre-loading** for simple commands
- Use **Context Index Query** for complex/multi-step commands like /implement
- Always provide context explicitly to agents in task prompts
- Let agents fallback to default context if needed
