# DevOps Engineer Agent - Updated Context Loading Example

This example shows how to update the devops-engineer agent with intelligent context loading.

## Updated Context Loading Section

Replace the existing "Context Loading (CRITICAL)" section with:

```markdown
### Context Loading (CRITICAL)
**BEFORE starting any task, you MUST load relevant context using this priority system:**

#### Priority 1: Explicit Context (Highest Priority)
If the task prompt explicitly specifies context files, read ONLY those files:

**Example:**
```
Context: context/devops/github-actions.md

Task: Improve CI pipeline performance...
```
→ Read ONLY github-actions.md

#### Priority 2: Keyword-Based Context Loading (Recommended)
If no explicit context specified, analyze the task for keywords and load relevant context:

**Keyword Mapping for DevOps:**
- **GitHub Actions keywords**: "github actions", "workflow", "ci/cd", "pipeline", ".github/workflows", "ci", "cd", "automation"
  → Load: `context/devops/github-actions.md`

- **Docker keywords**: "docker", "dockerfile", "container", "containerize", "docker-compose", "image", "multi-stage"
  → Load: `context/devops/docker.md`

- **Both domains**: Task contains BOTH GitHub Actions AND Docker keywords
  → Load: Both `github-actions.md` AND `docker.md`

**How to implement:**
1. Read context index: `context/context-index.yml`
2. Analyze task description for keywords
3. Match keywords to context files using the index
4. Read all matching context files

**Examples:**
```
Task: "Add code coverage to CI pipeline"
Keywords: "ci", "pipeline"
Load: context/devops/github-actions.md

Task: "Build Docker images in GitHub Actions"
Keywords: "docker", "github actions"
Load: context/devops/github-actions.md + context/devops/docker.md

Task: "Optimize Dockerfile layers"
Keywords: "dockerfile", "layers"
Load: context/devops/docker.md
```

#### Priority 3: Default Context (Fallback)
If no specific context identified from keywords, read ALL files in DevOps context directory:

```bash
# Use Glob to find all DevOps context files
context/devops/**/*

# Read each file:
# - context/devops/github-actions.md
# - context/devops/docker.md
# - Any other future files in context/devops/
```

#### Priority 4: Secrets Documentation (Always)
**ALWAYS read the secrets documentation regardless of context strategy:**
- `.github/workflows/.env` - GitHub Actions secrets documentation
- Update this file when creating/modifying workflows that require secrets

### Context Application
After loading context:
1. Review and understand project-specific guidelines and best practices
2. Apply context knowledge to inform your approach and recommendations
3. Reference specific context files in your explanations
4. Ensure recommendations align with established patterns from context
5. Document which context informed your decisions

## Complete Updated Workflow

### 1. **Load Project Context** (using priority system)

**Implementation steps:**

a. **Check for Explicit Context**
```bash
# If task prompt contains "Context: path/to/file.md"
# Read ONLY that file
```

b. **Keyword-Based Loading**
```bash
# 1. Read the context index
Read: context/context-index.yml

# 2. Analyze task for keywords
Task: "Optimize Docker images in GitHub Actions workflow"
Keywords found: ["docker", "images", "github actions", "workflow"]

# 3. Match to context files
"docker" → context/devops/docker.md
"github actions" → context/devops/github-actions.md

# 4. Load matched files
Read: context/devops/docker.md
Read: context/devops/github-actions.md
```

c. **Fallback to Default**
```bash
# If no keywords matched or task is general
Use Glob: context/devops/**/*
Read all matching files
```

d. **Always Read Secrets**
```bash
# Regardless of above strategy
Read: .github/workflows/.env
```

### 2. **Understand Requirements**
- Ask clarifying questions about container/workflow requirements
- Understand application dependencies and runtime needs
- Clarify CI/CD pipeline requirements and environments
- Identify performance, security, and build time targets
- Reference loaded context for project-specific requirements

### 3. **Design Solution**
- Apply best practices from loaded context files
- Consider entire lifecycle: local development, testing, building, deployment
- Address container security, image size, build performance per context guidelines
- Design with patterns and conventions from context
- Plan for failure scenarios and rollback strategies

### 4. **Implement**
- Follow patterns and conventions from loaded context
- Deliver production-ready configurations
- Apply security best practices from context
- Use recommended patterns for error handling, logging, health checks
- Reference context files for implementation decisions

### 5. **Test and Validate**
- Validate YAML syntax (as specified in context)
- Test following strategies from context guidelines
- Verify security configurations per context standards
- Check performance targets from context requirements

### 6. **Document**
- Document decisions and how they align with context
- Reference specific context files that informed choices
- Explain any deviations from context guidelines
- Update `.github/workflows/.env` for secrets per context instructions

## Example Task Flows

### Example 1: GitHub Actions Only Task

**Task:** "Add code coverage reporting to our CI pipeline"

**Context Loading:**
```
1. Check explicit context: None specified
2. Analyze keywords: "code coverage", "CI pipeline"
   - "CI pipeline" matches github-actions keywords
3. Load: context/devops/github-actions.md
4. Skip: context/devops/docker.md (not needed)
5. Always load: .github/workflows/.env
```

**Implementation:**
```yaml
# Uses patterns from github-actions.md
name: CI Pipeline

on: [push, pull_request]

jobs:
  test-with-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tests with coverage
        run: |
          npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}  # Documented in .github/workflows/.env
```

**Documentation:**
```markdown
Context used: context/devops/github-actions.md

Implementation follows GitHub Actions best practices:
- Uses SHA-pinned actions (from context security guidelines)
- Implements proper caching (from context performance guidelines)
- Uses recommended coverage tools (from context testing section)

Secret added to .github/workflows/.env:
- CODECOV_TOKEN: For uploading coverage reports
```

### Example 2: Docker + GitHub Actions Task

**Task:** "Build and push Docker images in GitHub Actions with multi-stage builds"

**Context Loading:**
```
1. Check explicit context: None specified
2. Analyze keywords: "docker images", "github actions", "multi-stage builds"
   - "docker" matches docker keywords
   - "github actions" matches github-actions keywords
   - "multi-stage" matches docker keywords
3. Load:
   - context/devops/github-actions.md
   - context/devops/docker.md
4. Always load: .github/workflows/.env
```

**Implementation:**
Uses patterns from BOTH context files:
- Multi-stage Dockerfile (from docker.md)
- GitHub Actions workflow with Docker buildx (from github-actions.md)
- Security scanning (from both contexts)
- Optimal caching strategies (from both contexts)

### Example 3: Explicit Context Override

**Task:**
```
Context: context/devops/docker.md

Optimize our Dockerfile for production deployments.
```

**Context Loading:**
```
1. Explicit context specified: context/devops/docker.md
2. Load ONLY: context/devops/docker.md
3. Skip: context/devops/github-actions.md (even though we have workflows)
4. Skip: Keyword analysis (explicit context takes precedence)
5. Always load: .github/workflows/.env (if working with secrets)
```

### Example 4: General DevOps Task

**Task:** "Review our DevOps practices and suggest improvements"

**Context Loading:**
```
1. Check explicit context: None specified
2. Analyze keywords: "devops practices" (too general)
   - No specific keyword matches
3. Fallback to default: Load ALL context/devops/**/*
   - context/devops/github-actions.md
   - context/devops/docker.md
4. Always load: .github/workflows/.env
```

**Result:** Comprehensive review using all DevOps context

## Benefits of This Approach

1. **Token Efficiency**
   - GitHub Actions-only task: ~50K tokens saved by skipping docker.md
   - Docker-only task: ~25K tokens saved by skipping github-actions.md

2. **Focused Context**
   - Agent gets exactly the information needed
   - Reduces noise and improves response quality

3. **Flexibility**
   - Explicit context for precise control
   - Keyword matching for convenience
   - Fallback for comprehensive coverage

4. **Maintainability**
   - Central context index (context-index.yml)
   - Agent prompt doesn't need updates when adding context
   - Easy to add new context files

5. **Backward Compatible**
   - Fallback to "load all" still works
   - Existing commands continue to function
   - Gradual migration possible

## Migration Path

### Phase 1: Add Context Index (Done)
- Created context/context-index.yml
- Documented keyword mappings

### Phase 2: Update Agent Prompts
- Replace "Context Loading" section with priority-based approach
- Keep default behavior as fallback

### Phase 3: Update Slash Commands (Gradual)
- Start with high-value commands (/implement, etc.)
- Add explicit context specifications
- Test and iterate

### Phase 4: Optimize (Ongoing)
- Monitor which contexts are frequently loaded together
- Refine keyword mappings based on usage
- Split large context files if needed
- Add new context files as project grows
```

## Implementation Checklist

To update devops-engineer.md:

- [ ] Replace lines 51-60 (Context Loading section) with Priority-based approach
- [ ] Update Workflow section (line 116-123) to reference priority system
- [ ] Add examples of keyword matching in Best Practices
- [ ] Test with sample tasks to verify context loading works
- [ ] Document context decisions in reports

## Testing the Updated Agent

Test cases to validate:

1. **Test Explicit Context**
   ```
   Task prompt: "Context: context/devops/github-actions.md\nImprove CI"
   Expected: Load ONLY github-actions.md
   ```

2. **Test Keyword Matching**
   ```
   Task: "Optimize Docker images"
   Expected: Load docker.md only
   ```

3. **Test Multi-Domain**
   ```
   Task: "Build Docker images in GitHub Actions"
   Expected: Load both github-actions.md and docker.md
   ```

4. **Test Fallback**
   ```
   Task: "Review DevOps setup"
   Expected: Load all context/devops/**/*
   ```

5. **Test Secrets**
   ```
   Any task involving workflows
   Expected: Always load .github/workflows/.env
   ```
