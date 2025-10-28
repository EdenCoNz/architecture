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

### Story Quality Guidelines
- Generic and implementation-agnostic (no frameworks, libraries, technologies)
- User-focused (describes WHAT users need, not HOW to build it)
- Atomic (1-3 days max, independently deployable)
- Testable (acceptance criteria are user-observable behaviors)
