# Intelligent Context Loading System

## Executive Summary

This document describes a multi-layer context loading system that allows agents and commands to load **exactly the right context** for each task, reducing token usage and improving response quality.

### The Problem
- Current approach: All agents load ALL context from their directory
- Example: GitHub Actions task loads both `github-actions.md` (52KB) AND `docker.md` (25KB)
- Result: Wasted tokens, diluted focus, slower responses

### The Solution
- **4-Layer Priority System**: Explicit → Keywords → Default → Always
- **Central Index**: `context/context-index.yml` maps keywords to context files
- **Flexible**: Works for simple and complex scenarios
- **Token Efficient**: Load only what's needed (30-70% reduction in typical cases)

### Quick Example
```
Task: "Add code coverage to CI pipeline"

Old approach:
✗ Load: context/devops/github-actions.md (52KB)
✗ Load: context/devops/docker.md (25KB)
Total: 77KB

New approach:
✓ Load: context/devops/github-actions.md (52KB)
✗ Skip: context/devops/docker.md
Total: 52KB (32% reduction)
```

---

## Architecture Overview

### Directory Structure
```
context/
├── context-index.yml          # Central keyword→file mapping
├── README.md                  # System documentation
├── backend/
│   └── django-drf-mysql-best-practices.md
├── devops/
│   ├── docker.md
│   └── github-actions.md
├── frontend/
│   ├── react-typescript-best-practices-2024-2025.md
│   └── material-ui-best-practices.md
├── design/
└── testing/
    ├── frontend-testing-research-2025.md
    └── django-drf-testing-best-practices-2025.md
```

### Key Components

1. **Context Index** (`context/context-index.yml`)
   - Maps keywords to context files
   - Defines default context for each agent
   - Provides pattern-based rules for complex scenarios

2. **Agent Prompts** (`.claude/agents/*.md`)
   - Include priority-based context loading instructions
   - Reference the context index
   - Define agent-specific keyword mappings

3. **Slash Commands** (`.claude/commands/*.md`)
   - Can specify explicit context
   - Can leverage keyword matching
   - Can pass context to agents

---

## The 4-Layer Priority System

### Layer 1: Explicit Context (HIGHEST PRIORITY)
**When:** Task prompt explicitly specifies context files

**How:**
```markdown
Context: context/devops/github-actions.md

Task: Improve CI pipeline...
```

**Result:** Load ONLY the specified file(s), ignore all other context

**Use cases:**
- Slash commands with known requirements
- User-directed context override
- Testing specific scenarios

---

### Layer 2: Keyword-Based Context Loading (RECOMMENDED)
**When:** No explicit context, but task contains identifiable keywords

**How:**
1. Read `context/context-index.yml`
2. Analyze task description for keywords
3. Match keywords to context file IDs
4. Load all matching context files

**Example:**
```yaml
Task: "Build Docker images in GitHub Actions"

Keywords extracted: ["docker", "images", "github actions"]

Context index lookup:
- "docker" → context/devops/docker.md
- "github actions" → context/devops/github-actions.md

Load:
- context/devops/docker.md
- context/devops/github-actions.md
```

**Use cases:**
- Most routine tasks
- /implement command with user stories
- Ad-hoc agent invocations

---

### Layer 3: Default Context (FALLBACK)
**When:** No explicit context AND no keywords matched

**How:**
```bash
# Load all files in agent's default directory
Use Glob: context/{agent-type}/**/*
Read all matching files
```

**Example:**
```
Task: "Review our DevOps setup"
Keywords: Too general, no specific match
Fallback: Load ALL context/devops/**/*
```

**Use cases:**
- General/exploratory tasks
- Comprehensive reviews
- Uncertain requirements

---

### Layer 4: Always-Load Context (SPECIAL CASES)
**When:** Certain context is ALWAYS needed regardless of task

**Example for DevOps:**
```markdown
ALWAYS load:
- .github/workflows/.env (secrets documentation)

Regardless of whether task mentions secrets or not
```

**Use cases:**
- Critical project-specific files
- Security/compliance documentation
- Shared conventions

---

## Implementation Guide

### Step 1: Context Index (✅ Complete)

Already created: `context/context-index.yml`

Key sections:
```yaml
context_files:
  - path: context/devops/github-actions.md
    id: github-actions
    tags: [devops, ci-cd, workflows]
    keywords: [github actions, workflow, pipeline, ci/cd]
    agents: [devops-engineer]

agent_defaults:
  devops-engineer:
    - github-actions
    - docker

context_rules:
  - pattern: "github.actions.*(docker|container)"
    context_ids: [github-actions, docker]
```

### Step 2: Update Agent Prompts

Replace the "Context Loading" section in each agent:

**Before:**
```markdown
### Context Loading (CRITICAL)
**BEFORE starting any task, you MUST:**
1. Read ALL files under the `context/devops/` directory
```

**After:**
```markdown
### Context Loading (CRITICAL)
**BEFORE starting any task, you MUST load relevant context using this priority system:**

#### Priority 1: Explicit Context (Highest Priority)
If task prompt specifies context files, read ONLY those files

#### Priority 2: Keyword-Based Context Loading (Recommended)
If no explicit context:
1. Read context index: `context/context-index.yml`
2. Analyze task for keywords
3. Load matching context files

Common keywords for {AGENT}:
- "keyword1" → context/path/file1.md
- "keyword2" → context/path/file2.md

#### Priority 3: Default Context (Fallback)
If no keywords matched:
Use Glob: context/{agent-directory}/**/*
```

See `docs/examples/devops-engineer-updated-example.md` for complete example.

### Step 3: Update Slash Commands (Gradual)

#### High-Priority Commands to Update:

1. **`/implement`** - Most important
   ```markdown
   For each user story:
   1. Parse story keywords (e.g., "Material UI", "Docker", "GitHub Actions")
   2. Consult context/context-index.yml
   3. Load matching context files
   4. Pass explicit context to agent:
      ```
      Context: context/devops/github-actions.md

      Story #4: Set up CI pipeline
      [Story details...]
      ```
   ```

2. **`/fix`** - Bug fixes
   ```markdown
   1. Read bug report from docs/features/*/bugs/*/bug-report.json
   2. Analyze bug type and affected components
   3. Load relevant context based on keywords
   4. Pass to agent with explicit context
   ```

3. **Custom workflow commands** (e.g., `/improve-ci`, `/optimize-docker`)
   ```markdown
   # Explicit context - we know what's needed
   Read: context/devops/github-actions.md
   Launch devops-engineer with loaded context
   ```

### Step 4: Test and Validate

#### Test Scenarios:

1. **Explicit Context Test**
   ```
   Command: /improve-ci
   Expected: Loads only github-actions.md
   Token savings: ~25KB (docker.md skipped)
   ```

2. **Keyword Matching Test**
   ```
   Task: "Build and push Docker images in CI"
   Expected: Loads both github-actions.md + docker.md
   Token savings: None (both needed)
   ```

3. **Fallback Test**
   ```
   Task: "Review DevOps practices"
   Expected: Loads all context/devops/**/*
   Token savings: None (comprehensive task)
   ```

4. **Agent Invocation Test**
   ```
   Task to devops-engineer: "Add caching to workflows"
   Expected: Keyword match → github-actions.md only
   Token savings: ~25KB
   ```

#### Validation Checklist:
- [ ] Context index YAML is valid
- [ ] Agent prompts reference correct directories
- [ ] Commands pass explicit context to agents
- [ ] Fallback to default context works
- [ ] Token usage reduced for specific tasks
- [ ] No context missed for complex tasks

---

## Real-World Examples

### Example 1: /implement Command (Multi-Agent)

**Scenario:** Implementing Feature #2 with user stories involving multiple agents

**User Stories:**
1. Story #1: UI/UX Designer - Design dashboard layout (Material UI)
2. Story #2: Frontend - Implement dashboard components (React + Material UI)
3. Story #3: Backend - Create API endpoints (Django DRF)
4. Story #4: DevOps - Set up CI pipeline (GitHub Actions)
5. Story #5: DevOps - Containerize application (Docker + GitHub Actions)

**Context Loading per Story:**

```markdown
Story #1 (ui-ux-designer):
- Keywords: "dashboard", "material ui"
- Context: context/frontend/material-ui-best-practices.md
- Token usage: ~15KB

Story #2 (frontend-developer):
- Keywords: "dashboard components", "react", "material ui"
- Context:
  - context/frontend/react-typescript-best-practices-2024-2025.md
  - context/frontend/material-ui-best-practices.md
- Token usage: ~40KB

Story #3 (backend-developer):
- Keywords: "api endpoints", "django"
- Context: context/backend/django-drf-mysql-best-practices.md
- Token usage: ~35KB

Story #4 (devops-engineer):
- Keywords: "ci pipeline", "github actions"
- Context: context/devops/github-actions.md
- Always: .github/workflows/.env
- Token usage: ~52KB

Story #5 (devops-engineer):
- Keywords: "containerize", "docker", "github actions"
- Context:
  - context/devops/docker.md
  - context/devops/github-actions.md
- Always: .github/workflows/.env
- Token usage: ~77KB

Total context loaded: ~219KB
Old approach (load all): ~350KB
Savings: ~131KB (37% reduction)
```

### Example 2: Specialized DevOps Tasks

#### Task A: GitHub Actions Only
```
Task: "Add code coverage reporting to CI"
Keywords: "code coverage", "ci"
Load: github-actions.md (52KB)
Skip: docker.md (25KB)
Savings: 32%
```

#### Task B: Docker Only
```
Task: "Optimize Dockerfile for production"
Keywords: "dockerfile", "optimize"
Load: docker.md (25KB)
Skip: github-actions.md (52KB)
Savings: 68%
```

#### Task C: Both Needed
```
Task: "Build multi-stage Docker images in GitHub Actions"
Keywords: "multi-stage", "docker", "github actions"
Load: github-actions.md (52KB) + docker.md (25KB)
Skip: None
Savings: 0% (both needed)
```

### Example 3: Frontend Development

#### Task A: Material UI Specific
```
Task: "Create custom MUI theme with dark mode"
Keywords: "mui theme", "dark mode"
Load: material-ui-best-practices.md (15KB)
Skip: react-typescript-best-practices-2024-2025.md (25KB)
Savings: 63%
```

#### Task B: React Architecture
```
Task: "Design state management architecture for dashboard"
Keywords: "state management", "react", "architecture"
Load: react-typescript-best-practices-2024-2025.md (25KB)
Skip: material-ui-best-practices.md (15KB)
Savings: 38%
```

#### Task C: Full Frontend Implementation
```
Task: "Build responsive dashboard with Material UI and Redux"
Keywords: "dashboard", "material ui", "redux", "react"
Load: Both files (40KB total)
Skip: None
Savings: 0% (both needed)
```

---

## Benefits Analysis

### Token Efficiency

| Scenario | Old Approach | New Approach | Savings |
|----------|-------------|--------------|---------|
| GitHub Actions only | 77KB | 52KB | 32% |
| Docker only | 77KB | 25KB | 68% |
| Both needed | 77KB | 77KB | 0% |
| Material UI only | 40KB | 15KB | 63% |
| React only | 40KB | 25KB | 38% |
| Backend API | 35KB | 35KB | 0% |

**Average savings across typical tasks: 30-40%**

### Response Quality

1. **Focused Context**
   - Agent gets exactly what it needs
   - Less noise, more signal
   - Better pattern matching

2. **Relevant Recommendations**
   - Solutions align with loaded context
   - Fewer irrelevant suggestions
   - More project-specific guidance

3. **Faster Responses**
   - Less context to process
   - Quicker to relevant information
   - Reduced latency

### Maintainability

1. **Central Index**
   - Single source of truth for keyword mappings
   - Easy to update when adding context
   - No need to update individual agents

2. **Scalable**
   - Add new context files without changing agent prompts
   - Update keyword mappings in one place
   - Handles project growth gracefully

3. **Backward Compatible**
   - Fallback to "load all" still works
   - Gradual migration possible
   - No breaking changes

### Developer Experience

1. **Explicit Control**
   - Can override with explicit context
   - Useful for testing and debugging
   - Clear what context is loaded

2. **Automatic Intelligence**
   - Keyword matching handles most cases
   - No need to specify context manually
   - Works intuitively

3. **Transparency**
   - Agents document which context they used
   - Easy to understand decisions
   - Reproducible results

---

## Migration Strategy

### Phase 1: Foundation (Week 1) ✅ COMPLETE
- [x] Create context/context-index.yml
- [x] Create context/README.md
- [x] Create docs/templates/agent-context-loading-template.md
- [x] Create docs/templates/command-context-loading-example.md
- [x] Create docs/examples/devops-engineer-updated-example.md

### Phase 2: Update Agents (Week 2)
- [ ] Update devops-engineer.md with priority-based context loading
- [ ] Update frontend-developer.md with priority-based context loading
- [ ] Update backend-developer.md with priority-based context loading
- [ ] Update ui-ux-designer.md with priority-based context loading
- [ ] Test each agent with sample tasks

### Phase 3: Update High-Priority Commands (Week 3)
- [ ] Update /implement command with keyword-based context resolution
- [ ] Update /fix command with context loading
- [ ] Create /improve-ci command with explicit context
- [ ] Create /optimize-docker command with explicit context
- [ ] Test commands end-to-end

### Phase 4: Optimize and Iterate (Ongoing)
- [ ] Monitor context loading patterns
- [ ] Refine keyword mappings based on usage
- [ ] Split large context files if needed (e.g., separate docker-compose from docker)
- [ ] Add new context files as project grows
- [ ] Update context-index.yml with new mappings

---

## Best Practices

### For Context Files
1. **Keep Files Focused**
   - One topic per file (e.g., separate github-actions.md and docker.md)
   - Makes selective loading more effective
   - Easier to maintain

2. **Comprehensive Keywords**
   - Include common terms, abbreviations, variations
   - Think about how tasks will be phrased
   - Update context-index.yml when adding new patterns

3. **Regular Updates**
   - Keep context current with latest best practices
   - Update when technologies evolve
   - Document changes in context files

### For Agents
1. **Reference Loaded Context**
   - Mention which context files informed decisions
   - Cite specific sections when relevant
   - Explain alignment with context guidelines

2. **Document Exceptions**
   - If deviating from context, explain why
   - Provide rationale for exceptions
   - Update context if pattern becomes common

3. **Validate Context Completeness**
   - Ensure loaded context is sufficient for task
   - Request additional context if needed
   - Fallback to default if uncertain

### For Commands
1. **Be Explicit When Possible**
   - Specify exact context files for known scenarios
   - Reduces ambiguity and token usage
   - Improves predictability

2. **Use Keywords for Flexibility**
   - Allow dynamic context resolution for variable tasks
   - Leverage context-index.yml mappings
   - Better for multi-step workflows

3. **Document Context Decisions**
   - Explain why specific context is loaded
   - Help users understand the system
   - Aid debugging and optimization

---

## Troubleshooting

### Issue: Agent loads wrong context
**Symptoms:** Agent references irrelevant context or misses needed context

**Solutions:**
1. Check keyword mappings in context-index.yml
2. Add missing keywords for the task type
3. Use explicit context override for that specific task
4. Update agent's keyword documentation

### Issue: Too much context loaded
**Symptoms:** High token usage, slow responses

**Solutions:**
1. Use explicit context instead of default fallback
2. Split large context files into smaller, focused files
3. Refine keyword matching to be more specific
4. Review context-rules in context-index.yml

### Issue: Too little context loaded
**Symptoms:** Agent lacks necessary information, makes uninformed decisions

**Solutions:**
1. Add missing keywords to context-index.yml
2. Use broader keyword patterns
3. Temporarily use default context loading (load all)
4. Add cross-references between context files

### Issue: Context loading inconsistent
**Symptoms:** Different results for similar tasks

**Solutions:**
1. Standardize keyword usage in task descriptions
2. Make keyword matching case-insensitive
3. Add pattern-based rules to context-index.yml
4. Document expected keywords for common tasks

---

## Metrics and Success Criteria

### Token Efficiency
- **Target:** 30-40% reduction in context token usage for specific tasks
- **Measure:** Compare token usage old vs. new approach
- **Success:** Achieve target without missing required context

### Response Quality
- **Target:** Maintain or improve response relevance
- **Measure:** User feedback, task completion success rate
- **Success:** No decrease in quality, improved focus

### Developer Productivity
- **Target:** Reduce time to load and process context
- **Measure:** Response time, iterations needed
- **Success:** Faster responses, fewer clarification rounds

### Maintainability
- **Target:** Easier to add new context files
- **Measure:** Time to add new context, number of files to update
- **Success:** Add context by only updating context-index.yml

---

## Future Enhancements

### Short Term
1. **Context Caching**
   - Cache frequently-loaded context combinations
   - Reduce redundant file reads
   - Improve performance

2. **Context Validation**
   - Verify all keywords in index are used
   - Check for missing keywords
   - Suggest new mappings

3. **Usage Analytics**
   - Track which context is loaded for which tasks
   - Identify optimization opportunities
   - Refine keyword mappings

### Medium Term
1. **Smart Context Splitting**
   - Automatically split large context files
   - Organize by subtopics
   - Improve granularity

2. **Context Dependencies**
   - Define dependencies between context files
   - Auto-load related context
   - Ensure completeness

3. **Multi-Project Context**
   - Share common context across projects
   - Project-specific overrides
   - Reusable context library

### Long Term
1. **AI-Powered Context Resolution**
   - Use LLM to analyze task and determine context
   - Learn from usage patterns
   - Adaptive keyword matching

2. **Context Versioning**
   - Track context changes over time
   - Associate context versions with features
   - Support rollback

3. **Context Composition**
   - Compose context from multiple sources
   - Merge, override, extend patterns
   - Dynamic context generation

---

## Conclusion

The intelligent context loading system provides:

✅ **Token Efficiency**: 30-40% reduction for specific tasks
✅ **Better Focus**: Load only what's needed
✅ **Flexibility**: Explicit, keyword-based, and default strategies
✅ **Maintainability**: Central index, easy updates
✅ **Scalability**: Grows with project complexity
✅ **Backward Compatible**: Gradual migration, no breaking changes

**Next Steps:**
1. Review this document and examples
2. Test the system with sample tasks
3. Update agents one by one (start with devops-engineer)
4. Update high-priority commands (/implement, /fix)
5. Monitor usage and refine keyword mappings

**Questions or issues?**
- Review examples in docs/examples/
- Check templates in docs/templates/
- Consult context/README.md
- Update context-index.yml as needed
