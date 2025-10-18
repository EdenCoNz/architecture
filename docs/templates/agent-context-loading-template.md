# Agent Context Loading Template

This template demonstrates how to implement intelligent context loading in agent prompts.

## Template Structure

```markdown
---
name: agent-name
description: Agent description
model: sonnet
---

# Agent Name

## Purpose
[Agent purpose and expertise]

## Core Expertise
[List of core competencies]

## Best Practices

### Context Loading (CRITICAL)
**BEFORE starting any task, you MUST load relevant context using this priority system:**

#### Priority 1: Explicit Context (Highest Priority)
If the task prompt explicitly specifies context files, read ONLY those files:
```
Example task prompt:
"Context: context/devops/github-actions.md

Improve the CI pipeline..."
```

#### Priority 2: Keyword-Based Context Loading (Recommended)
If no explicit context is specified, analyze the task for keywords and load relevant context:

1. Read the context index: `context/context-index.yml`
2. Analyze the task description for relevant keywords
3. Match keywords to context files using the index
4. Read all matching context files

**Common keyword patterns for {AGENT_TYPE}:**
- Keyword A → context/path/file1.md
- Keyword B → context/path/file2.md
- Keywords A + B → both files

**How to determine keywords:**
```bash
# Use Grep to search for relevant patterns in the task description
# Then consult context-index.yml for matching context files
```

#### Priority 3: Default Context (Fallback)
If no specific context is identified, read ALL files in your default directory:
```bash
# Use Glob to find all context files
context/{agent-directory}/**/*

# Read each file
```

#### Priority 4: Cross-Domain Context (Optional)
If task spans multiple domains (e.g., Docker + GitHub Actions), load context from multiple directories:
```bash
# Example: DevOps task involving both Docker and CI/CD
- context/devops/docker.md
- context/devops/github-actions.md
```

### Context Application
After loading context:
1. Review and understand project-specific guidelines
2. Apply best practices from context to your approach
3. Reference context files in your explanations
4. Ensure recommendations align with established patterns

## Workflow

1. **Load Project Context** (using priority system above)
   - Determine which context loading strategy to use
   - Load relevant context files
   - Understand project-specific requirements

2. **Understand Requirements**
   [Rest of agent workflow...]
```

## Real-World Examples

### Example 1: GitHub Actions Task
```markdown
User: "Add code coverage reporting to our CI pipeline"

Agent Analysis:
- Keywords: "CI pipeline", "code coverage"
- Context index lookup: "ci", "pipeline" → github-actions
- Load: context/devops/github-actions.md
- Skip: context/devops/docker.md (not needed)
```

### Example 2: Docker + GitHub Actions Task
```markdown
User: "Build and push Docker images in GitHub Actions workflow"

Agent Analysis:
- Keywords: "Docker images", "GitHub Actions", "workflow"
- Context index lookup: "docker", "github actions" → github-actions, docker
- Load:
  - context/devops/github-actions.md
  - context/devops/docker.md
```

### Example 3: Explicit Context Override
```markdown
User: "Context: context/devops/docker.md

Optimize our Dockerfile for production"

Agent Analysis:
- Explicit context specified
- Load ONLY: context/devops/docker.md
- Skip: All other context files
```

### Example 4: Fallback to Default
```markdown
User: "Help me improve our DevOps practices"

Agent Analysis:
- Keywords: Generic "DevOps" (no specific topic)
- No explicit context
- Fallback to default: Load ALL context/devops/**/*
```

## Implementation in Agent Files

### Step 1: Add Context Loading Section
Replace the existing "Context Loading" section in your agent files with the priority-based approach.

### Step 2: Document Default Context
Clearly specify what context files belong to each agent by default.

### Step 3: Add Keyword Examples
Provide examples of common keywords that map to specific context files for that agent.

### Step 4: Cross-Reference Context Index
Mention that agents should consult `context/context-index.yml` for authoritative keyword mappings.

## Benefits of This Approach

1. **Efficiency**: Load only what's needed for the task
2. **Flexibility**: Supports explicit, selective, and default loading
3. **Scalability**: Grows well as context increases
4. **Backward Compatible**: Fallback to loading all context still works
5. **Maintainable**: Central index makes it easy to update mappings
6. **Clear**: Explicit priority system reduces ambiguity

## Maintenance

When adding new context:
1. Add the file to appropriate context directory
2. Update context-index.yml with keywords and tags
3. Agent prompts automatically benefit from the new context
4. No need to update individual agent files
