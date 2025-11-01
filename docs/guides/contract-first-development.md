# Contract-First Development Guide

## Overview

Contract-First Development is a workflow that enables frontend and backend developers to work in parallel by defining API contracts before implementation. This approach reduces integration risks, speeds up development, and ensures both sides implement exactly the same interface.

## Benefits

### 1. Parallel Development
- Frontend and backend teams can work simultaneously
- No waiting for backend APIs to be ready
- No coordination bottlenecks during implementation

### 2. Reduced Integration Risk
- Both sides implement against the same specification
- Contract serves as single source of truth
- Mismatches are caught early through contract validation

### 3. Better Documentation
- API contracts serve as living documentation
- Examples are always up-to-date
- TypeScript types provide compile-time safety

### 4. Faster Development
- Expected time savings: 30-40% for features with significant API interactions
- Parallel execution reduces critical path
- Less rework from integration issues

## When to Use Contract-First Development

### Good Candidates
- Features with multiple API endpoints (3+)
- Features requiring parallel frontend-backend work
- Features with complex request/response validation
- Features where integration risk is high
- Features with multiple frontend consumers

### Poor Candidates
- Simple features with 1-2 trivial endpoints
- Features where API shape is highly uncertain
- Exploratory/prototype features
- Internal-only endpoints with no external consumers

## Workflow

### Step 1: Complete Design Phase

Before creating API contracts, ensure UI/UX design is complete:

```bash
# Design stories should be implemented first
/implement feature {id}
# This will run design stories (Phase 1)
```

The design brief should clearly specify:
- What data components need
- User interactions that trigger API calls
- State management requirements
- Error handling needs

### Step 2: Create API Contract Story

Add an API contract story to your user-stories.md:

```markdown
### Story 0: Define API Contracts
As a developer, I want clear API specifications defined before implementation,
so that frontend and backend can work in parallel without integration issues.

**Acceptance Criteria**:
- All API endpoints needed for this feature are specified
- Request/response schemas are defined with TypeScript types
- Validation rules are documented for all fields
- Error response formats are standardized
- Example request/response payloads are provided

**Agent**: api-contract-designer
**Dependencies**: Design stories complete (Story 1, 2, 3)
**Estimated Effort**: 1 day

**Output Files**:
- docs/features/{feature_id}/api-contract.md
- docs/features/{feature_id}/api-types.ts (optional)
```

### Step 3: Update Execution Order

Structure your execution order to support parallel implementation:

```markdown
## Execution Order

### Phase 1: Design (Sequential)
- Story #1: Design user interface (agent: ui-ux-designer)
- Story #2: Design data models (agent: ui-ux-designer)
- Story #3: Design user flows (agent: ui-ux-designer)

### Phase 2: API Contract Definition (Sequential)
- Story #0: Define API Contracts (agent: api-contract-designer)
  - Depends on: Story #1, #2, #3

### Phase 3: Parallel Implementation
**Parallel Block** (depends on Story #0):
- Story #4: Implement frontend UI (agent: frontend-developer)
- Story #5: Implement API endpoints (agent: backend-developer)

**Parallel Block** (depends on Story #4, #5):
- Story #6: Add form validation (agent: frontend-developer)
- Story #7: Add data persistence (agent: backend-developer)

### Phase 4: Integration & Polish (Sequential)
- Story #8: Integration testing (agent: backend-developer)
  - Depends on: All stories in Phase 3
```

### Step 4: Run Implementation

Execute the feature implementation:

```bash
/implement feature {id}
```

The `/implement` command will:
1. Execute design stories (Phase 1)
2. Execute API contract story (Phase 2)
   - Creates `docs/features/{id}/api-contract.md`
   - May create `docs/features/{id}/api-types.ts`
3. Execute parallel implementation (Phase 3)
   - Launches frontend-developer and backend-developer simultaneously
   - Both agents read the API contract
   - Both implement exactly to contract specifications
4. Execute integration stories (Phase 4)

### Step 5: Verify Integration

After parallel implementation completes:

1. **Review Implementation Logs**
   - Check `docs/features/{id}/implementation-log.json`
   - Verify both frontend and backend completed successfully
   - Look for any flagged contract issues

2. **Run Integration Tests**
   - Execute end-to-end tests
   - Verify frontend calls match backend implementation
   - Test error scenarios

3. **Contract Compliance Check**
   - Frontend: API calls use exact paths, methods, payloads from contract
   - Backend: Endpoints return exact response formats from contract
   - Both: Error handling matches contract specifications

## API Contract Structure

### Minimal Contract

At minimum, an API contract should include:

```markdown
# API Contract: Feature Name

## Endpoints

### 1. Endpoint Name
**Method:** POST
**Path:** `/api/v1/resource/`

#### Request
**Request Body:**
\`\`\`typescript
interface CreateResourceRequest {
  name: string;
  value: number;
}
\`\`\`

#### Response
**Success (201 Created):**
\`\`\`typescript
interface ResourceResponse {
  id: string;
  name: string;
  value: number;
  created_at: string;
}
\`\`\`

#### Validation Rules
- name: Required, max 255 chars
- value: Required, positive integer

#### Error Responses
**400 Bad Request:**
\`\`\`json
{
  "error": "Validation failed",
  "details": {
    "name": ["This field is required"]
  }
}
\`\`\`
```

### Comprehensive Contract

For complex features, include:
- Multiple endpoints with full specifications
- Shared TypeScript types
- Business logic validation rules
- Pagination/filtering patterns
- Authentication requirements
- Rate limiting details
- Integration examples
- Testing checklist

See `docs/templates/api-contract-template.md` for a complete example.

## Agent Behavior

### api-contract-designer Agent

**What it does:**
1. Reads user stories to understand API requirements
2. Reads design brief to understand data needs
3. Searches codebase for existing API patterns
4. Creates comprehensive API contract document
5. Optionally creates TypeScript types file

**Key decisions it makes:**
- Endpoint paths and HTTP methods
- Request/response schema design
- Validation rule specifications
- Error response formats
- TypeScript interface definitions

### frontend-developer Agent

**When API contract exists:**
1. **Reads contract first** before implementing
2. Uses contract as source of truth for:
   - API endpoint paths and methods
   - Request/response TypeScript types
   - Validation rules
   - Error response formats
3. **Implements exactly to spec** - no deviations
4. Validates implementation against contract
5. Flags any contract ambiguities immediately

**Mock data strategy:**
- Mock API responses match contract schemas exactly
- Use contract example payloads for testing
- Integration tests verify contract compliance

### backend-developer Agent

**When API contract exists:**
1. **Reads contract first** before implementing
2. Uses contract as source of truth for:
   - Endpoint paths and HTTP methods
   - Request/response data types
   - Validation rules
   - Status codes and error formats
3. **Implements exactly to spec** - no deviations
4. Validates requests according to contract rules
5. Returns responses in exact contract format
6. Flags if contract conflicts with data model

## File Organization

### Contract Files

```
docs/features/{feature_id}/
├── user-stories.md           # User stories including contract story
├── design-brief.md           # UI/UX design specifications
├── api-contract.md           # API contract specification (created by contract story)
├── api-types.ts              # TypeScript interfaces (optional, created by contract story)
├── implementation-log.json   # Implementation log (all stories)
└── implementation-summary.md # Human-readable summary
```

### Contract Ownership

**Read-Only During Implementation:**
- `api-contract.md` - Neither frontend nor backend modifies this
- `api-types.ts` - Generated from contract, not manually edited

**If Contract Needs Changes:**
1. Pause implementation
2. Update contract document
3. Notify both frontend and backend developers
4. Resume implementation with updated contract

## Common Patterns

### Pattern 1: Simple CRUD Feature

```markdown
## Execution Order

### Phase 1: Design (Sequential)
- Story #1: Design UI (ui-ux-designer)

### Phase 2: API Contract (Sequential)
- Story #0: Define API Contract (api-contract-designer)

### Phase 3: Parallel Implementation
**Parallel Block**:
- Story #2: Frontend CRUD UI (frontend-developer)
- Story #3: Backend CRUD API (backend-developer)
```

**Time Savings:** ~25% (1 day saved on 4-day feature)

### Pattern 2: Multi-Step Form with Validation

```markdown
## Execution Order

### Phase 1: Design (Sequential)
- Story #1: Design form UI (ui-ux-designer)
- Story #2: Design validation rules (ui-ux-designer)

### Phase 2: API Contract (Sequential)
- Story #0: Define API Contract (api-contract-designer)

### Phase 3: Parallel Implementation - Core
**Parallel Block**:
- Story #3: Form components (frontend-developer)
- Story #4: Validation endpoints (backend-developer)

### Phase 4: Parallel Implementation - Enhancement
**Parallel Block**:
- Story #5: Client-side validation (frontend-developer)
- Story #6: Data persistence (backend-developer)
```

**Time Savings:** ~35% (2-3 days saved on 8-day feature)

### Pattern 3: Dashboard with Multiple Data Sources

```markdown
## Execution Order

### Phase 1: Design (Sequential)
- Story #1: Dashboard layout (ui-ux-designer)

### Phase 2: API Contract (Sequential)
- Story #0: Define API Contract (api-contract-designer)

### Phase 3: Parallel Implementation - Data Endpoints
**Parallel Block**:
- Story #2: Dashboard components (frontend-developer)
- Story #3: Data aggregation endpoints (backend-developer)

### Phase 4: Parallel Implementation - Features
**Parallel Block**:
- Story #4: Filtering UI (frontend-developer)
- Story #5: Filtering logic (backend-developer)
- Story #6: Export UI (frontend-developer)
- Story #7: Export generation (backend-developer)
```

**Time Savings:** ~40% (3-4 days saved on 10-day feature)

## Troubleshooting

### Issue: Contract is Ambiguous

**Symptoms:**
- Agent flags contract as unclear
- Frontend and backend interpret differently
- Integration tests fail

**Resolution:**
1. Review the specific ambiguity
2. Update api-contract.md with clarification
3. Add more examples if needed
4. Notify both frontend and backend
5. Resume implementation

### Issue: Contract Conflicts with Data Model

**Symptoms:**
- Backend agent flags contract as not implementable
- Data model constraints prevent contract compliance
- Business logic conflicts with contract

**Resolution:**
1. Evaluate if data model can be adjusted
2. If not, update api-contract.md to match data model reality
3. Notify frontend developer of changes
4. Update TypeScript types if needed
5. Resume implementation

### Issue: Contract Lacks Detail

**Symptoms:**
- Agent requests more information
- Multiple valid interpretations exist
- Missing validation rules or error scenarios

**Resolution:**
1. Enhance api-contract.md with missing details
2. Add specific validation rules
3. Document error scenarios
4. Provide more example payloads
5. Resume implementation

### Issue: Frontend and Backend Out of Sync

**Symptoms:**
- Integration tests fail
- API calls return unexpected errors
- Response parsing fails

**Resolution:**
1. Compare implementations to contract
2. Identify which side deviated
3. Fix the deviation to match contract
4. Add contract compliance tests
5. Re-run integration tests

## Best Practices

### 1. Start with Design
Always complete UI/UX design before creating API contracts. The design drives data requirements.

### 2. Keep Contracts Simple
Start with minimal contracts. Add complexity only when needed. Over-specification can be as bad as under-specification.

### 3. Use TypeScript Types
Generate TypeScript interfaces from contracts. This provides compile-time safety and catches deviations early.

### 4. Provide Examples
Always include example request/response payloads. Examples clarify ambiguities better than descriptions.

### 5. Document Validation Rules Explicitly
Don't assume. State every validation rule clearly:
- Required vs optional
- Min/max lengths
- Patterns/formats
- Business logic constraints

### 6. Standardize Error Formats
Use consistent error response format across all endpoints. Define it once in the contract.

### 7. Version Your Contracts
Track contract changes in a changelog. Note breaking changes explicitly.

### 8. Test Contract Compliance
Both frontend and backend should test against the contract examples. Integration tests should verify compliance.

### 9. Don't Deviate
If contract needs changes, update the contract first. Don't implement workarounds.

### 10. Review Together
Have frontend and backend review the contract together before implementation starts.

## Metrics

Track these metrics to measure contract-first development effectiveness:

### Development Time
- Time from design complete to feature ready
- Compare with vs without contracts
- Expected improvement: 30-40% for suitable features

### Integration Issues
- Number of integration bugs found
- Number of contract deviations
- Expected reduction: 60-80%

### Rework Time
- Time spent fixing integration issues
- Time spent resolving API mismatches
- Expected reduction: 70-90%

### Developer Satisfaction
- Parallel vs sequential workflow preference
- Contract clarity ratings
- Coordination overhead perception

## Advanced Topics

### Pagination Contracts

```typescript
interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Usage
interface UsersListResponse extends PaginatedResponse<UserResponse> {}
```

### Nested Resources

```
GET  /api/v1/users/{user_id}/
GET  /api/v1/users/{user_id}/assessments/
POST /api/v1/users/{user_id}/assessments/
GET  /api/v1/users/{user_id}/assessments/{assessment_id}/
```

### Partial Updates (PATCH)

```typescript
// All fields optional for PATCH
interface UpdateUserRequest {
  name?: string;
  email?: string;
  role?: UserRole;
}

// Response returns full object
interface UserResponse {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  updated_at: string;
}
```

### Batch Operations

```typescript
interface BatchCreateRequest {
  items: CreateItemRequest[];
}

interface BatchCreateResponse {
  created: ItemResponse[];
  failed: Array<{
    index: number;
    error: string;
  }>;
}
```

## Migration Guide

### Adding Contracts to Existing Features

If you want to add contract-first development to an existing feature:

1. **Document existing APIs**
   - Create api-contract.md from current implementation
   - Extract schemas from code
   - Document current validation rules

2. **Generate TypeScript types**
   - Create api-types.ts from contract
   - Update frontend to use types

3. **Add contract tests**
   - Test frontend calls against contract
   - Test backend responses against contract

4. **Future changes use contract-first**
   - New endpoints get added to contract first
   - Changes update contract before implementation

## Examples

### Example 1: User Profile API Contract

See: `docs/templates/api-contract-template.md`

### Example 2: Assessment Equipment Feature

A complete example showing contract-first development for a multi-endpoint feature with parallel frontend-backend implementation.

**User Stories Structure:**
```markdown
### Story 0: Define API Contracts
- Agent: api-contract-designer
- Output: api-contract.md with 3 endpoints

### Story 1: Equipment Selection UI
- Agent: frontend-developer
- Reads: api-contract.md

### Story 2: Equipment Validation API
- Agent: backend-developer
- Reads: api-contract.md
```

**Outcome:**
- Both agents implemented in parallel
- Zero integration issues
- 35% time savings vs sequential approach

## Summary

Contract-First Development with parallel execution offers significant benefits:

**Pros:**
- 30-40% faster development for suitable features
- Reduced integration risk
- Better documentation
- Type safety
- Parallel execution

**Cons:**
- Additional upfront planning
- Requires discipline to follow contracts
- Not suitable for all features

**Best For:**
- Features with 3+ API endpoints
- Features requiring parallel work
- Features with complex validation
- High integration risk scenarios

**Use the workflow when these conditions are met, and you'll see significant improvements in development speed and quality.**
