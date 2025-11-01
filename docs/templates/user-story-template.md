# Feature #{ID}: {Feature Title}

## Overview
{2-3 sentences describing the feature and its value to users}

## Missing Agents (if applicable)
- **{agent-name}**: {description of capabilities needed and why it would help}

---

## User Stories

### {#}. {Story Title}
{2-3 sentence description from user perspective}

**Acceptance Criteria**:
- {Testable user-observable behavior}
- {Another testable criterion}
- {Maximum 3-4 criteria}

**Agent**: {agent-name}
**Dependencies**: {none|story numbers}

---

## Execution Order

### Phase 1 (Parallel)
- Story #{X} (agent: {name})
- Story #{Y} (agent: {name})

### Phase 2 (Sequential)
- Story #{Z} (agent: {name}) - depends on Story #{X}

---

## Notes

### For Design Stories
Add this instruction to ui-ux-designer stories:

**Design Context**:
- Update docs/design-brief.md to incorporate design decisions for this feature
- If design-brief.md doesn't exist, create it using docs/design-brief-template.md
- Add a feature-specific section under the "## Features" heading
- Include component specifications, interaction patterns, and all UI states
- Ensure consistency with existing design system

### For API Contract Stories (Contract-First Development)

**When to Create an API Contract Story:**
- Feature has multiple API endpoints
- Feature requires parallel frontend-backend development
- Feature has complex request/response validation
- Integration risk is high

**API Contract Story Pattern:**

```markdown
### 0. Define API Contracts
As a developer, I want clear API specifications defined before implementation, so that frontend and backend can work in parallel without integration issues.

**Acceptance Criteria**:
- All API endpoints needed for this feature are specified
- Request/response schemas are defined with TypeScript types
- Validation rules are documented for all fields
- Error response formats are standardized
- Example request/response payloads are provided

**Agent**: api-contract-designer
**Dependencies**: Design stories complete
**Estimated Effort**: 1 day

**Output Files**:
- docs/features/{feature_id}/api-contract.md - Complete API specification
- docs/features/{feature_id}/api-types.ts - TypeScript interfaces (optional)
```

**Execution Order with API Contracts:**

```markdown
## Execution Order

### Phase 1: Design (Sequential)
- Story #1 (agent: ui-ux-designer)

### Phase 2: API Contract Definition (Sequential)
- Story #0 (agent: api-contract-designer) - depends on Story #1

### Phase 3: Parallel Implementation
**Parallel Block** (depends on Story #0):
- Story #2: Frontend Implementation (agent: frontend-developer)
- Story #3: Backend Implementation (agent: backend-developer)

### Phase 4: Integration & Testing (Sequential)
- Story #4 (agent: backend-developer) - depends on Story #2, #3
```

**Important Notes:**
- API contract story is typically numbered "0" as it comes before implementation
- Both frontend and backend stories must depend on the contract story
- Agents will automatically read api-contract.md when implementing (if it exists)
- Neither frontend nor backend should deviate from the contract without discussion

### Story Quality Guidelines
- Generic and implementation-agnostic (no frameworks, libraries, technologies)
- User-focused (describes WHAT users need, not HOW to build it)
- Atomic (1-3 days max, independently deployable)
- Testable (acceptance criteria are user-observable behaviors)
