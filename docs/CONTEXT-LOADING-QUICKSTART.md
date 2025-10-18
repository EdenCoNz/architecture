# Context Loading System - Quick Start Guide

## TL;DR

**Problem:** Agents load too much context, wasting tokens
**Solution:** Load only what's needed based on task keywords
**Result:** 30-40% token savings for specific tasks

## 5-Minute Overview

### How It Works

```
Task: "Add code coverage to CI pipeline"
         ↓
    Analyze keywords: ["code coverage", "ci pipeline"]
         ↓
    Look up in context-index.yml
         ↓
    Match: "ci pipeline" → github-actions.md
         ↓
    Load ONLY: context/devops/github-actions.md
         ↓
    Skip: docker.md (not needed)
         ↓
    Save: 25KB tokens (32% reduction)
```

### The Priority System

1. **Explicit Context** - Task says "Context: file.md" → Load ONLY that file
2. **Keywords** - Task contains "docker" → Load docker.md
3. **Default** - No match → Load ALL context/{agent}/**/*
4. **Always** - Some files ALWAYS load (e.g., .github/workflows/.env)

### What You Need

Already created:
- ✅ `context/context-index.yml` - Keyword mappings
- ✅ `context/README.md` - Documentation
- ✅ `docs/CONTEXT-LOADING-SYSTEM.md` - Full guide
- ✅ Templates and examples in `docs/templates/` and `docs/examples/`

To do:
- [ ] Update agent prompts (copy from templates)
- [ ] Update slash commands (optional, for optimization)
- [ ] Test with sample tasks

---

## Quick Implementation (30 Minutes)

### Step 1: Review Context Index (5 min)

Open `context/context-index.yml` and review the keyword mappings:

```yaml
# Example: GitHub Actions context
- path: context/devops/github-actions.md
  id: github-actions
  keywords:
    - github actions
    - workflow
    - ci/cd
    - pipeline
```

**Action:** Verify keywords match how tasks are typically phrased.

### Step 2: Update One Agent (10 min)

Pick an agent to update (recommend: `devops-engineer`).

Open `.claude/agents/devops-engineer.md` and find this section:

```markdown
### Context Loading (CRITICAL)
**BEFORE starting any task, you MUST:**
1. Read ALL files under the `context/devops/` directory
```

Replace with (from `docs/examples/devops-engineer-updated-example.md`):

```markdown
### Context Loading (CRITICAL)
**BEFORE starting any task, you MUST load relevant context using this priority system:**

#### Priority 1: Explicit Context (Highest Priority)
If the task prompt explicitly specifies context files, read ONLY those files.

#### Priority 2: Keyword-Based Context Loading (Recommended)
If no explicit context specified, analyze the task for keywords and load relevant context:

**Keyword Mapping for DevOps:**
- **GitHub Actions keywords**: "github actions", "workflow", "ci/cd", "pipeline"
  → Load: `context/devops/github-actions.md`

- **Docker keywords**: "docker", "dockerfile", "container", "containerize"
  → Load: `context/devops/docker.md`

- **Both domains**: Task contains BOTH sets of keywords
  → Load: Both files

**Implementation:**
1. Read context index: `context/context-index.yml`
2. Analyze task description for keywords
3. Match keywords to context files using the index
4. Read all matching context files

#### Priority 3: Default Context (Fallback)
If no specific context identified, read ALL files in DevOps context directory:
```bash
context/devops/**/*
```

#### Priority 4: Secrets Documentation (Always)
**ALWAYS read:** `.github/workflows/.env`
```

**Save the file.**

### Step 3: Test the Agent (10 min)

Test with sample tasks to verify context loading:

#### Test 1: GitHub Actions Only
```
Task: "Add code coverage reporting to CI pipeline"
Expected: Loads only github-actions.md
```

#### Test 2: Docker Only
```
Task: "Optimize Dockerfile for production"
Expected: Loads only docker.md
```

#### Test 3: Both
```
Task: "Build Docker images in GitHub Actions"
Expected: Loads both files
```

#### Test 4: Fallback
```
Task: "Review DevOps setup"
Expected: Loads all context/devops/**/*
```

**Verify:** Agent mentions which context files it loaded in its response.

### Step 4: Update Other Agents (5 min each)

Repeat Step 2 for:
- `backend-developer.md` (context/backend/)
- `frontend-developer.md` (context/frontend/)
- `ui-ux-designer.md` (context/design/)

Use templates in `docs/templates/agent-context-loading-template.md`.

---

## Common Patterns

### Pattern 1: Single Context File Needed

```
Scenario: "Improve GitHub Actions workflow performance"
Keywords: "github actions", "workflow"
Load: context/devops/github-actions.md
Skip: docker.md
Savings: 32%
```

### Pattern 2: Multiple Context Files Needed

```
Scenario: "Build and push Docker images in CI/CD pipeline"
Keywords: "docker", "ci/cd"
Load:
  - context/devops/github-actions.md
  - context/devops/docker.md
Skip: None (both needed)
Savings: 0%
```

### Pattern 3: Explicit Override

```
Scenario: Developer specifies exact context
Command: "Context: context/devops/docker.md\n\nOptimize Dockerfile"
Load: docker.md ONLY
Skip: Everything else (even if keywords match)
```

### Pattern 4: Default Fallback

```
Scenario: "Review our DevOps practices"
Keywords: Too general, no specific match
Load: ALL context/devops/**/*
Skip: None
Savings: 0% (comprehensive task needs all context)
```

---

## Keyword Cheat Sheet

### DevOps Agent Keywords

| Topic | Keywords | Context File |
|-------|----------|--------------|
| GitHub Actions | "github actions", "workflow", "ci/cd", "pipeline", ".github/workflows" | github-actions.md |
| Docker | "docker", "dockerfile", "container", "image", "compose" | docker.md |
| Both | Contains BOTH sets of keywords above | Both files |

### Frontend Agent Keywords

| Topic | Keywords | Context File |
|-------|----------|--------------|
| React/TypeScript | "react", "typescript", "component", "hooks", "tsx" | react-typescript-best-practices-2024-2025.md |
| Material UI | "material ui", "mui", "theme", "sx prop", "styled" | material-ui-best-practices.md |
| Both | React component + Material UI | Both files |

### Backend Agent Keywords

| Topic | Keywords | Context File |
|-------|----------|--------------|
| Django/DRF | "django", "drf", "rest framework", "api", "serializer" | django-drf-mysql-best-practices.md |

### Testing Keywords

| Topic | Keywords | Context File |
|-------|----------|--------------|
| Frontend Testing | "jest", "react testing library", "e2e", "cypress" | frontend-testing-research-2025.md |
| Backend Testing | "pytest", "django test", "api test" | django-drf-testing-best-practices-2025.md |

---

## Updating the /implement Command

The `/implement` command benefits most from intelligent context loading.

### Current Flow
```
/implement feature 2
  → Read user-stories.md
  → For each story: Launch agent
  → Agent loads ALL context for its type
```

### Improved Flow
```
/implement feature 2
  → Read user-stories.md
  → For each story:
      → Parse story keywords
      → Determine required context
      → Launch agent with explicit context
```

### Example Update

In `.claude/commands/implement.md`, update Step 4:

**Before:**
```markdown
### Step 4: Pass Story Context to Agents

For each agent, provide:
```
{Story details}
```
```

**After:**
```markdown
### Step 4: Determine and Pass Context

For each story:

1. **Analyze Story Keywords**
   - Extract technology keywords from story title and description
   - Examples: "Material UI", "Docker", "GitHub Actions", "React", "Django"

2. **Determine Required Context**
   Consult context/context-index.yml to map keywords to context files:
   - "Material UI" → context/frontend/material-ui-best-practices.md
   - "Docker" → context/devops/docker.md
   - "GitHub Actions" → context/devops/github-actions.md
   - "React" → context/frontend/react-typescript-best-practices-2024-2025.md
   - "Django" → context/backend/django-drf-mysql-best-practices.md

3. **Pass Explicit Context to Agent**
   ```
   Context: context/devops/github-actions.md

   Feature ID: 2
   Story #4: Set up CI pipeline

   {Story details}

   Implement following best practices from loaded context.
   ```

If no specific keywords found, let agent use default context loading.
```

---

## Verification Checklist

After implementing, verify:

- [ ] Context index YAML is valid (no syntax errors)
- [ ] Agent prompts mention priority system
- [ ] Test tasks with single context file load correctly
- [ ] Test tasks with multiple context files load all needed files
- [ ] Test explicit context override works
- [ ] Test fallback to default context works
- [ ] Commands reference context loading approach
- [ ] Token usage reduced for specific tasks (check in conversation)

---

## Troubleshooting

### Agent loads too much context
**Fix:** Add more specific keywords to context-index.yml for that task type

### Agent loads too little context
**Fix:** Add missing keywords or use explicit context override

### Keywords don't match
**Fix:** Update context-index.yml with variations and common phrases

### Context loading unpredictable
**Fix:** Use explicit context specification in commands for consistency

---

## Next Steps

1. ✅ Read this quick start guide
2. ⏭️ Review `context/context-index.yml` (verify keywords)
3. ⏭️ Update `devops-engineer.md` agent (10 min)
4. ⏭️ Test with sample tasks (10 min)
5. ⏭️ Update other agents (5 min each)
6. ⏭️ Optionally update `/implement` command (15 min)
7. ✅ Start using the system!

---

## Resources

- **Full Guide:** `docs/CONTEXT-LOADING-SYSTEM.md`
- **Agent Template:** `docs/templates/agent-context-loading-template.md`
- **Command Examples:** `docs/templates/command-context-loading-example.md`
- **DevOps Example:** `docs/examples/devops-engineer-updated-example.md`
- **Context Index:** `context/context-index.yml`
- **System Docs:** `context/README.md`

---

## Key Takeaways

1. **Priority System**: Explicit → Keywords → Default → Always
2. **Token Savings**: 30-40% for specific tasks
3. **Central Index**: Update `context-index.yml` to add new mappings
4. **Backward Compatible**: Fallback ensures nothing breaks
5. **Gradual Migration**: Update agents one at a time
6. **Test Thoroughly**: Verify context loading with sample tasks

**Questions?** Review `docs/CONTEXT-LOADING-SYSTEM.md` for comprehensive details.
