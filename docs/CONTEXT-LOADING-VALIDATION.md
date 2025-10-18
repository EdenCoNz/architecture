# Context Loading System - Validation Tests

This document provides test cases to validate the intelligent context loading system is working correctly.

## Test Setup

The system has been implemented with:
- ✅ Updated `devops-engineer.md` with priority-based context loading
- ✅ Updated `frontend-developer.md` with priority-based context loading
- ✅ Updated `backend-developer.md` with priority-based context loading
- ✅ Updated `ui-ux-designer.md` with priority-based context loading
- ✅ Updated `/implement` command with keyword-based context resolution
- ✅ Created `context/context-index.yml` with keyword mappings

## Validation Test Cases

### Test 1: DevOps - GitHub Actions Only

**Test Task:**
```
Task to devops-engineer: "Add code coverage reporting to our CI pipeline"
```

**Expected Behavior:**
1. Agent analyzes keywords: "code coverage", "CI pipeline"
2. Matches "CI pipeline" to github-actions context
3. Loads ONLY: `context/devops/github-actions.md`
4. Skips: `context/devops/docker.md`
5. Always loads: `.github/workflows/.env`

**Expected Token Savings:** ~32% (25KB saved by skipping docker.md)

**Validation:**
- [ ] Agent mentions loading github-actions.md
- [ ] Agent does NOT mention docker.md
- [ ] Response references GitHub Actions best practices
- [ ] No Docker-specific recommendations

---

### Test 2: DevOps - Docker Only

**Test Task:**
```
Task to devops-engineer: "Optimize our Dockerfile for production deployment"
```

**Expected Behavior:**
1. Agent analyzes keywords: "Dockerfile", "production deployment"
2. Matches "Dockerfile" to docker context
3. Loads ONLY: `context/devops/docker.md`
4. Skips: `context/devops/github-actions.md`

**Expected Token Savings:** ~68% (52KB saved by skipping github-actions.md)

**Validation:**
- [ ] Agent mentions loading docker.md
- [ ] Agent does NOT mention github-actions.md
- [ ] Response references Docker best practices (multi-stage builds, layer optimization, etc.)
- [ ] No GitHub Actions workflow recommendations

---

### Test 3: DevOps - Both Docker and GitHub Actions

**Test Task:**
```
Task to devops-engineer: "Build and push Docker images in our GitHub Actions workflow"
```

**Expected Behavior:**
1. Agent analyzes keywords: "Docker images", "GitHub Actions", "workflow"
2. Matches both "Docker" AND "GitHub Actions"
3. Loads BOTH:
   - `context/devops/github-actions.md`
   - `context/devops/docker.md`
4. Always loads: `.github/workflows/.env`

**Expected Token Savings:** 0% (both files needed)

**Validation:**
- [ ] Agent mentions loading both github-actions.md AND docker.md
- [ ] Response includes GitHub Actions workflow recommendations
- [ ] Response includes Docker image building best practices
- [ ] Integration of both contexts (e.g., Docker buildx in GitHub Actions)

---

### Test 4: DevOps - Explicit Context Override

**Test Task:**
```
Context: context/devops/docker.md

Task to devops-engineer: "Review our containerization strategy and suggest improvements"
```

**Expected Behavior:**
1. Agent detects explicit context specification
2. Loads ONLY: `context/devops/docker.md`
3. Skips: `context/devops/github-actions.md` (even though "strategy" is generic)
4. Ignores keyword matching (explicit takes priority)

**Expected Token Savings:** ~68%

**Validation:**
- [ ] Agent acknowledges explicit context
- [ ] Agent loads ONLY docker.md
- [ ] Response focuses on Docker/containerization
- [ ] No GitHub Actions recommendations

---

### Test 5: Frontend - Material UI Only

**Test Task:**
```
Task to frontend-developer: "Create a custom Material UI theme with dark mode support"
```

**Expected Behavior:**
1. Agent analyzes keywords: "Material UI", "theme", "dark mode"
2. Matches "Material UI" to material-ui context
3. Loads ONLY: `context/frontend/material-ui-best-practices.md`
4. Skips: `context/frontend/react-typescript-best-practices-2024-2025.md`

**Expected Token Savings:** ~63% (25KB saved)

**Validation:**
- [ ] Agent mentions loading material-ui-best-practices.md
- [ ] Agent does NOT mention react-typescript context
- [ ] Response includes MUI theming recommendations (createTheme, palette, etc.)
- [ ] References Material Design 3 principles

---

### Test 6: Frontend - React Architecture

**Test Task:**
```
Task to frontend-developer: "Design the state management architecture for our React application using Redux Toolkit"
```

**Expected Behavior:**
1. Agent analyzes keywords: "state management", "React", "Redux Toolkit"
2. Matches "React" and "state management" to react-typescript context
3. Loads ONLY: `context/frontend/react-typescript-best-practices-2024-2025.md`
4. Skips: `context/frontend/material-ui-best-practices.md`

**Expected Token Savings:** ~38% (15KB saved)

**Validation:**
- [ ] Agent mentions loading react-typescript-best-practices.md
- [ ] Agent does NOT mention material-ui context
- [ ] Response includes Redux Toolkit recommendations
- [ ] State management patterns discussed
- [ ] No MUI-specific component recommendations

---

### Test 7: Frontend - Both React and Material UI

**Test Task:**
```
Task to frontend-developer: "Build a responsive dashboard using React components and Material UI design system"
```

**Expected Behavior:**
1. Agent analyzes keywords: "React components", "Material UI", "dashboard"
2. Matches BOTH "React" AND "Material UI"
3. Loads BOTH:
   - `context/frontend/react-typescript-best-practices-2024-2025.md`
   - `context/frontend/material-ui-best-practices.md`

**Expected Token Savings:** 0% (both needed)

**Validation:**
- [ ] Agent mentions loading both context files
- [ ] Response includes React component architecture
- [ ] Response includes Material UI component selection
- [ ] Integration of both (e.g., React hooks with MUI components)

---

### Test 8: Backend - Django API

**Test Task:**
```
Task to backend-developer: "Create REST API endpoints for user management using Django REST Framework"
```

**Expected Behavior:**
1. Agent analyzes keywords: "REST API", "Django REST Framework", "user management"
2. Matches to django-drf context
3. Loads: `context/backend/django-drf-mysql-best-practices.md`

**Expected Token Savings:** 0% (only one backend context file currently)

**Validation:**
- [ ] Agent mentions loading django-drf context
- [ ] Response includes DRF serializers, viewsets
- [ ] MySQL database considerations
- [ ] API best practices from context

---

### Test 9: UI/UX Designer - Material UI Components

**Test Task:**
```
Task to ui-ux-designer: "Design the component library and theming strategy for our application using Material UI"
```

**Expected Behavior:**
1. Agent analyzes keywords: "component library", "Material UI", "theming"
2. Matches "Material UI" to material-ui context
3. Loads: `context/frontend/material-ui-best-practices.md`
4. Always checks: `docs/design-brief.md` (if exists)

**Validation:**
- [ ] Agent mentions loading material-ui context
- [ ] Agent checks for existing design-brief.md
- [ ] Response includes MUI component selection guidance
- [ ] MUI theming strategy (createTheme, design tokens)
- [ ] Updates design-brief.md with decisions

---

### Test 10: /implement Command - Multi-Agent Story

**Test Scenario:**
Create a user story file with multiple stories requiring different contexts:

```markdown
# User Stories

## Story 1: Design Dashboard Layout (ui-ux-designer)
Design a Material UI-based dashboard layout...

## Story 2: Implement React Components (frontend-developer)
Build React components for the dashboard using Material UI and Redux...

## Story 3: Create API Endpoints (backend-developer)
Create Django REST Framework API endpoints...

## Story 4: Set up CI/CD Pipeline (devops-engineer)
Configure GitHub Actions workflow for automated testing and deployment...
```

**Expected Behavior:**
1. `/implement` analyzes each story for keywords
2. Story 1 → Passes `context/frontend/material-ui-best-practices.md` to ui-ux-designer
3. Story 2 → Passes BOTH frontend context files to frontend-developer
4. Story 3 → Passes `context/backend/django-drf-mysql-best-practices.md` to backend-developer
5. Story 4 → Passes `context/devops/github-actions.md` to devops-engineer

**Validation:**
- [ ] Each agent receives appropriate context
- [ ] No unnecessary context loaded
- [ ] Agents reference their loaded context in responses
- [ ] Implementation log shows context-informed decisions

---

## Validation Checklist

### System-Level Validation
- [ ] `context/context-index.yml` is valid YAML
- [ ] All agent files have "Context Loading (CRITICAL)" section
- [ ] All agents reference priority system (1-4)
- [ ] `/implement` command includes Step 4 for context determination
- [ ] Keyword mappings in context-index.yml are comprehensive

### Agent-Level Validation
- [ ] devops-engineer.md updated with priority system
- [ ] frontend-developer.md updated with priority system
- [ ] backend-developer.md updated with priority system
- [ ] ui-ux-designer.md updated with priority system

### Functional Validation (Run Tests 1-10 Above)
- [ ] Test 1: GitHub Actions only - PASSED
- [ ] Test 2: Docker only - PASSED
- [ ] Test 3: Both GitHub Actions and Docker - PASSED
- [ ] Test 4: Explicit context override - PASSED
- [ ] Test 5: Material UI only - PASSED
- [ ] Test 6: React architecture - PASSED
- [ ] Test 7: Both React and Material UI - PASSED
- [ ] Test 8: Django API - PASSED
- [ ] Test 9: UI/UX with Material UI - PASSED
- [ ] Test 10: /implement with multiple agents - PASSED

### Performance Validation
- [ ] Measure token usage for specific tasks (compare old vs new)
- [ ] Verify 30-40% token savings for single-context tasks
- [ ] Confirm no context is missed for multi-context tasks
- [ ] Response quality maintained or improved

---

## Test Results Template

Use this template to record test results:

```markdown
### Test X: [Test Name]

**Date:** YYYY-MM-DD
**Task:** [Exact task given to agent]

**Expected Context:**
- Load: [expected files]
- Skip: [expected skipped files]

**Actual Behavior:**
- Context loaded: [actual files loaded]
- Context skipped: [actual files skipped]

**Agent Response:**
[Summary of agent response]

**Validation:**
- [ ] Correct context loaded: YES/NO
- [ ] Unnecessary context skipped: YES/NO
- [ ] Response quality: GOOD/FAIR/POOR
- [ ] Context references in response: YES/NO
- [ ] Token savings achieved: X%

**Result:** PASS/FAIL

**Notes:**
[Any observations, issues, or improvements needed]
```

---

## Success Criteria

The context loading system is validated when:

1. **Correctness**: All agents load the right context based on keywords
2. **Efficiency**: Single-context tasks achieve 30-40% token savings
3. **Completeness**: Multi-context tasks load all required context
4. **Override**: Explicit context specification works correctly
5. **Fallback**: Generic tasks fall back to loading all context
6. **Quality**: Response quality maintained or improved
7. **Integration**: `/implement` command passes correct context to agents

---

## Next Steps After Validation

Once all tests pass:
1. Document any issues or edge cases discovered
2. Refine keyword mappings in `context-index.yml` if needed
3. Update agent prompts if patterns emerge
4. Create additional context files if gaps identified
5. Monitor real-world usage and iterate

---

## Troubleshooting Common Issues

### Issue: Agent loads wrong context
- Check keyword mappings in context-index.yml
- Verify task contains expected keywords
- Consider adding more keyword variations

### Issue: Agent loads too much context
- Use explicit context override for that task
- Refine keyword matching to be more specific
- Split large context files into smaller, focused files

### Issue: Agent misses needed context
- Add missing keywords to context-index.yml
- Use broader keyword patterns
- Temporarily fall back to default context loading

### Issue: Inconsistent behavior
- Standardize task phrasing
- Make keywords case-insensitive
- Add pattern-based rules to context-index.yml
