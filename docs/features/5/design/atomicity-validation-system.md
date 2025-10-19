# Atomicity Validation System Design

## 1. Overview

### 1.1 Purpose
The Atomicity Validation System is designed to automatically detect violations of atomic user story principles during the product-owner workflow. It provides actionable feedback to help ensure stories are focused, independently deployable, and appropriately scoped before being presented to users.

### 1.2 Design Goals
- **Automated Detection**: Automatically identify compound titles, excessive acceptance criteria, and scope violations
- **Actionable Feedback**: Provide specific, implementable suggestions for splitting stories
- **Workflow Integration**: Seamlessly integrate into product-owner agent without disrupting workflow
- **Extensibility**: Support future validation rules and customization
- **Non-Blocking**: Provide warnings and suggestions rather than hard failures

### 1.3 Scope
This design covers validation rules, scoring algorithms, output formats, and integration points. It does not cover the implementation details (which will be Story #4) or the parallel execution system (Story #1).

---

## 2. Validation Rules

### 2.1 Title Complexity Analysis

#### 2.1.1 Compound Title Detection
**Purpose**: Identify titles containing multiple distinct actions or concerns

**Rules**:
1. **Conjunction Detection**: Flag titles containing coordinating conjunctions
   - Patterns: "and", "or", "plus"
   - Example violations:
     - "Create User Profile and Add Authentication" → Split into 2 stories
     - "Design Login Page or Registration Flow" → Split into 2 stories
   - Edge cases to allow:
     - "Create and Configure" (single cohesive action)
     - Technical phrases: "Build and Deploy", "Install and Setup" (when truly atomic)

2. **Multiple Verb Detection**: Flag titles with 2+ primary action verbs
   - Action verbs: Create, Build, Implement, Design, Add, Update, Delete, Configure, Setup, Test, Validate, etc.
   - Example violations:
     - "Create Database Schema, Implement Queries, Add Migrations" → Split into 3 stories
     - "Build Component, Style Layout, Add Tests" → Split into 3 stories
   - Edge cases to allow:
     - "Build and Test" (when test is acceptance criteria, not separate story)
     - "Create and Initialize" (single initialization process)

3. **Scope Keyword Detection**: Flag titles suggesting multiple concerns
   - Keywords: "including", "with", "containing", "covering"
   - Example violations:
     - "Setup Authentication including OAuth and JWT" → Split by auth method
     - "Create API with Endpoints and Documentation" → Split implementation and docs

#### 2.1.2 Title Length Analysis
**Purpose**: Detect overly complex titles that indicate multiple concerns

**Rules**:
1. **Character Count**: Warn if title > 80 characters (suggests excessive scope)
2. **Word Count**: Warn if title > 12 words (suggests complexity)
3. **Clause Count**: Flag titles with multiple clauses (comma-separated sections)

**Scoring**:
```
title_complexity_score =
  (conjunction_count * 3) +
  (excess_verb_count * 4) +  // verbs beyond the first
  (scope_keyword_count * 2) +
  (character_count > 80 ? 2 : 0) +
  (word_count > 12 ? 1 : 0) +
  (clause_count > 1 ? clause_count * 2 : 0)

Status:
- 0-2: PASS (atomic)
- 3-5: WARNING (potentially compound)
- 6+: FAIL (definitely compound)
```

---

### 2.2 Acceptance Criteria Analysis

#### 2.2.1 Count Limits
**Purpose**: Ensure stories remain focused and testable

**Rules**:
1. **Hard Limit**: Flag stories with > 4 acceptance criteria
2. **Warning Threshold**: Warn stories with exactly 4 criteria (at edge of atomicity)
3. **Grouping Detection**: Identify criteria that could be separate stories

**Rationale**:
- 1-2 criteria: Ideal atomic story
- 3 criteria: Acceptable if closely related
- 4 criteria: Edge case, review for splitting
- 5+ criteria: Definitely needs splitting

#### 2.2.2 Criteria Complexity Analysis
**Purpose**: Detect acceptance criteria that indicate separate concerns

**Rules**:
1. **Multi-Concern Criteria**: Flag criteria with "and" joining distinct outcomes
   - Example violation: "User can login AND password is hashed AND session persists"
   - Should be 3 separate criteria or 3 separate stories

2. **Implementation-Heavy Criteria**: Flag criteria describing multiple implementation steps
   - Pattern: Criteria > 20 words with multiple clauses
   - Example: "System validates input, transforms data, stores in database, and sends confirmation email"
   - Suggests multi-step workflow that should be broken down

3. **Cross-Concern Criteria**: Flag criteria spanning multiple system areas
   - Example: "Frontend displays data AND backend caches responses AND database indexes improve query speed"
   - Suggests stories should be split by layer or concern

**Scoring**:
```
criteria_complexity_score =
  (criteria_count > 4 ? (criteria_count - 4) * 3 : 0) +
  (criteria_count === 4 ? 1 : 0) +
  (multi_concern_criteria_count * 2) +
  (implementation_heavy_count * 2) +
  (cross_concern_count * 3)

Status:
- 0-2: PASS (focused)
- 3-5: WARNING (potentially unfocused)
- 6+: FAIL (definitely needs splitting)
```

---

### 2.3 Estimated Scope Scoring

#### 2.3.1 File Impact Estimation
**Purpose**: Predict number of files that will be touched based on story description

**Heuristics**:
1. **CRUD Operation Detection**: Each CRUD verb suggests 2-4 files (handler, test, type definitions, etc.)
   - Create: ~3 files (handler, validation, tests)
   - Read: ~2 files (handler, tests)
   - Update: ~3 files (handler, validation, tests)
   - Delete: ~2 files (handler, tests)

2. **Component Keywords**: UI component work suggests 2-3 files per component
   - Keywords: "component", "page", "form", "modal", "layout"
   - Multiplier: Count of component mentions

3. **Infrastructure Keywords**: Infrastructure work suggests 3-5 files
   - Keywords: "setup", "configure", "initialize", "install"
   - Base estimate: 3-5 files depending on scope words

4. **Multi-Layer Keywords**: Work spanning multiple layers suggests higher file count
   - Frontend + Backend: Multiply base estimate by 1.5
   - Database involvement: Add 2-3 files
   - API endpoints: Add 2 files per endpoint mentioned

5. **Documentation Keywords**: Documentation adds 1-2 files
   - Keywords: "document", "README", "guide", "docs"

**Scoring Algorithm**:
```
estimated_file_count =
  (crud_operations * 2.5) +  // Average files per CRUD op
  (component_count * 2.5) +   // Average files per component
  (infrastructure_setup ? 4 : 0) +
  (multi_layer_factor) +      // 0, 1.5x, or 2x based on layers
  (database_work ? 3 : 0) +
  (api_endpoints * 2) +
  (documentation_work ? 1.5 : 0)

file_impact_score =
  (estimated_file_count <= 5 ? 0 : 0) +    // Ideal
  (estimated_file_count 6-8 ? 2 : 0) +      // Acceptable
  (estimated_file_count 9-12 ? 4 : 0) +     // Warning
  (estimated_file_count > 12 ? 6 : 0)       // Fail

Status:
- 1-5 files: PASS (ideal atomic scope)
- 6-8 files: WARNING (acceptable but monitor)
- 9-12 files: WARNING (consider splitting)
- 13+ files: FAIL (definitely too large)
```

#### 2.3.2 Time Estimation
**Purpose**: Estimate implementation time based on story complexity

**Factors**:
1. **Base Time**: File count * 0.25 days (assumes 4 files per day average)
2. **Complexity Multipliers**:
   - Research story: 1.5x (uncertainty factor)
   - Design story: 1.2x (iteration factor)
   - Setup/Configuration: 1.3x (environment issues)
   - Testing story: 0.8x (usually focused)
   - Bug fix: 0.6x (targeted change)

3. **Technology Factors**:
   - New technology: +0.5 days (learning curve)
   - Integration work: +0.3 days per integration point
   - Complex business logic: +0.5 days

**Scoring Algorithm**:
```
estimated_days =
  (estimated_file_count * 0.25) *
  complexity_multiplier +
  technology_factor

time_score =
  (estimated_days <= 1 ? 0 : 0) +      // Ideal
  (estimated_days 1-2 ? 1 : 0) +        // Good
  (estimated_days 2-3 ? 3 : 0) +        // Warning
  (estimated_days > 3 ? 6 : 0)          // Fail

Status:
- 0-1 days: PASS (excellent atomic scope)
- 1-2 days: PASS (good atomic scope)
- 2-3 days: WARNING (at edge of atomicity)
- 3+ days: FAIL (too large, must split)
```

---

### 2.4 Dependency Analysis

#### 2.4.1 Dependency Complexity
**Purpose**: Detect stories with complex dependency chains

**Rules**:
1. **Dependency Count**: Flag stories depending on > 2 other stories
2. **Circular Dependencies**: Detect and flag circular dependency chains
3. **Deep Chains**: Warn if story is > 3 levels deep in dependency chain

**Rationale**: Stories with many dependencies or deep chains may indicate:
- Story is too large (depends on too much setup)
- Story decomposition could be improved
- Execution order complexity

---

### 2.5 Technology-Agnostic Validation

#### 2.5.1 Technology Reference Detection
**Purpose**: Enforce technology-agnostic story writing per product-owner requirements

**Rules**:
1. **Framework Detection**: Flag mentions of React, Vue, Angular, Express, NestJS, Django, etc.
2. **Library Detection**: Flag mentions of specific libraries (Axios, Lodash, Prisma, etc.)
3. **File Extension Detection**: Flag mentions of .ts, .js, .tsx, .json, .yml, etc.
4. **Tool Detection**: Flag mentions of npm, yarn, Docker, ESLint, Prettier, Jest, etc.
5. **Pattern Detection**: Flag architectural patterns (REST, GraphQL, microservices, MVC, etc.)

**Scanning Areas**:
- Title
- Description
- Acceptance criteria
- Agent assignment (only allowed in "Agent:" field)

**Exceptions**:
- Generic terms allowed: "framework", "library", "database", "server", "client"
- File paths in acceptance criteria (when testing specific file creation)
- Agent names in "Agent:" field

**Scoring**:
```
technology_reference_score =
  (framework_mentions * 3) +
  (library_mentions * 3) +
  (file_extension_mentions * 2) +
  (tool_mentions * 2) +
  (pattern_mentions * 2)

Status:
- 0: PASS (fully technology-agnostic)
- 1-3: WARNING (minor technology leakage)
- 4+: FAIL (violates technology-agnostic principle)
```

---

## 3. Composite Atomicity Score

### 3.1 Overall Scoring Algorithm

**Purpose**: Combine all validation dimensions into single atomicity score

**Formula**:
```
atomicity_score =
  title_complexity_score +
  criteria_complexity_score +
  file_impact_score +
  time_score +
  technology_reference_score

Weighted Total (0-100 scale):
weighted_score = 100 - (atomicity_score * 3)  // Lower score = better

Classification:
- 85-100: EXCELLENT (perfectly atomic)
- 70-84: GOOD (atomic, minor improvements possible)
- 50-69: WARNING (has atomicity issues, should review)
- 0-49: FAIL (not atomic, must split)
```

### 3.2 Story Classification

Based on composite score, classify stories:

1. **ATOMIC** (85-100): Story is well-scoped and atomic
   - No action required
   - Include in report as exemplar

2. **ACCEPTABLE** (70-84): Story is atomic but could be improved
   - Include minor suggestions
   - Continue with story as-is

3. **NEEDS REVIEW** (50-69): Story has atomicity concerns
   - Highlight specific issues
   - Provide splitting suggestions
   - Product owner should refine

4. **MUST SPLIT** (0-49): Story is clearly not atomic
   - Block story from being included
   - Provide detailed splitting guidance
   - Product owner must refactor

---

## 4. Validation Output Format

### 4.1 Per-Story Validation Report

For each story that fails validation, provide:

```markdown
### Story #{number}: {title}

Atomicity Score: {score}/100 - {classification}

Issues Detected:
- [FAIL] Title Complexity: Contains "and" joining 2 distinct actions
  → Suggestion: Split into "Story A: {first action}" and "Story B: {second action}"

- [WARNING] Acceptance Criteria: 4 criteria detected (at edge of atomicity)
  → Suggestion: Review if criteria 3-4 could be separate story

- [WARNING] Estimated Scope: ~9 files, ~2.5 days
  → Suggestion: Consider splitting by layer (frontend/backend) or by CRUD operation

Technology References:
- [FAIL] Description mentions "React" and "Express"
  → Required: Replace with "frontend framework" and "server framework"
- [FAIL] Criteria mentions ".tsx files"
  → Required: Replace with generic "component files"

Splitting Recommendations:
1. Story {number}A: {focused first part}
   - Criteria: {1-2 criteria from original}
   - Estimated: {files} files, {days} days

2. Story {number}B: {focused second part}
   - Criteria: {1-2 criteria from original}
   - Estimated: {files} files, {days} days
   - Dependencies: Story {number}A
```

### 4.2 Summary Validation Report

After validating all stories, provide summary:

```markdown
## Atomicity Validation Summary

Total Stories: {count}
- EXCELLENT (85-100): {count} stories
- GOOD (70-84): {count} stories
- NEEDS REVIEW (50-69): {count} stories
- MUST SPLIT (0-49): {count} stories

Average Atomicity Score: {score}/100

Stories Requiring Attention: {count}
- {story numbers with scores < 70}

Technology-Agnostic Compliance:
- Fully compliant: {count} stories
- Minor violations: {count} stories
- Major violations: {count} stories

Recommended Actions:
1. Split {count} stories that scored below 50
2. Review {count} stories that scored 50-69
3. Fix technology references in {count} stories

Estimated Impact:
- Original story count: {count}
- Recommended story count after splits: {count}
- Average stories per original: {ratio}
```

### 4.3 Actionable Feedback Format

For product-owner workflow integration, provide structured feedback:

```json
{
  "validationResults": [
    {
      "storyNumber": 1,
      "title": "Create User Profile and Add Authentication",
      "atomicityScore": 45,
      "classification": "MUST_SPLIT",
      "issues": [
        {
          "category": "title_complexity",
          "severity": "FAIL",
          "message": "Title contains 'and' joining 2 distinct actions",
          "suggestion": "Split into separate stories"
        },
        {
          "category": "estimated_scope",
          "severity": "WARNING",
          "message": "Estimated 13 files, 3.2 days",
          "suggestion": "Split by concern or layer"
        }
      ],
      "splittingRecommendations": [
        {
          "proposedTitle": "Create User Profile",
          "proposedCriteria": ["User can create profile", "Profile data persists"],
          "estimatedFiles": 6,
          "estimatedDays": 1.5
        },
        {
          "proposedTitle": "Add User Authentication",
          "proposedCriteria": ["User can login", "Session management works"],
          "estimatedFiles": 7,
          "estimatedDays": 1.7,
          "dependencies": ["Story 1A"]
        }
      ],
      "technologyViolations": [
        {
          "location": "description",
          "violation": "React",
          "suggestion": "Use 'frontend framework' instead"
        }
      ]
    }
  ],
  "summary": {
    "totalStories": 15,
    "excellent": 8,
    "good": 4,
    "needsReview": 2,
    "mustSplit": 1,
    "averageScore": 78,
    "technologicallyCompliant": 12
  }
}
```

---

## 5. Integration Points

### 5.1 Product-Owner Workflow Integration

Based on analysis of `/home/ed/Dev/architecture/.claude/agents/product-owner.md`, integrate at these points:

#### 5.1.1 Post-Story Creation (Step 8)
**Location**: After "Create Initial User Stories" in feature request workflow

**Integration**:
```
8. Create Initial User Stories
   - Break down feature based on feature request
   - Start with high-level story breakdown
   - CRITICAL REMINDER: Use ONLY generic, technology-agnostic language

8.5. RUN INITIAL VALIDATION (NEW STEP)
   - Apply atomicity validation to all stories
   - Generate validation report with scores
   - Identify stories that MUST_SPLIT or NEED_REVIEW
   - Use validation output to inform refinement decisions
```

#### 5.1.2 During Refinement (Step 9)
**Location**: Within "REFINE FOR ATOMICITY (CRITICAL)" step

**Integration**:
```
9. REFINE FOR ATOMICITY (CRITICAL)
   - START: Run atomicity validation on all stories
   - PRIORITIZE: Focus on stories marked MUST_SPLIT (score < 50)
   - Apply atomicity checks guided by validation results:
     ✂️ Title contains "and": Split into separate stories
     ✂️ More than 3-4 acceptance criteria: Split by criteria groupings
     ... [existing checks]
   - RE-VALIDATE: Run atomicity validation on refined stories
   - ITERATE: Continue until all stories score >= 70
   - Re-number stories and update dependencies after splitting
```

#### 5.1.3 Pre-Report Validation (Step 13)
**Location**: Before final validation and report

**Integration**:
```
13. Validate and Report
    - FINAL VALIDATION: Run atomicity validation one last time
    - Verify all stories score >= 70 (ACCEPTABLE or better)
    - Confirm design-implementation separation
    - Confirm DevOps-development separation
    - Check execution order makes sense
    - Validate agent assignments
    - INCLUDE: Add atomicity validation summary to report
```

### 5.2 Validation Function Interface

**Proposed Interface** (for implementation in Story #4):

```
validateStoryAtomicity(story: Story): ValidationResult

Input: Story object with {title, description, acceptanceCriteria[], dependencies}

Output: ValidationResult object with:
  - atomicityScore: number (0-100)
  - classification: "EXCELLENT" | "GOOD" | "NEEDS_REVIEW" | "MUST_SPLIT"
  - issues: Issue[] (category, severity, message, suggestion)
  - splittingRecommendations: Split[] (if score < 70)
  - technologyViolations: Violation[] (if any found)
  - estimatedFiles: number
  - estimatedDays: number
```

```
validateStorySet(stories: Story[]): SetValidationResult

Input: Array of Story objects

Output: SetValidationResult object with:
  - storyResults: ValidationResult[] (per-story results)
  - summary: {totalStories, excellent, good, needsReview, mustSplit, averageScore}
  - overallPass: boolean (all stories >= 70)
  - recommendedActions: string[] (actionable steps for product owner)
```

### 5.3 Command Integration

**Optional Enhancement**: Create standalone validation command

```
/validate-stories {featureID}

Description: Run atomicity validation on user stories for a feature

Workflow:
1. Read docs/features/{featureID}/user-stories.md
2. Parse all user stories
3. Run validateStorySet() on parsed stories
4. Generate detailed validation report
5. Output report to console and optionally save to docs/features/{featureID}/validation-report.md

Use Cases:
- Validate existing stories before implementation
- Re-validate after manual story editing
- Quality assurance check before committing stories
- Teaching tool for understanding atomicity principles
```

### 5.4 Reporting Integration

**Enhancement to Feature Planning Complete Report**:

Add new section after "Story Refinement Summary":

```markdown
## Atomicity Validation Summary
- Average atomicity score: {score}/100
- Stories by classification:
  - EXCELLENT (85-100): {count}
  - GOOD (70-84): {count}
  - NEEDS REVIEW (50-69): {count}
  - MUST SPLIT (0-49): {count}
- Technology-agnostic compliance: {pass/fail count}
- All stories meet atomicity threshold: ✅ Yes / ⚠️ {count} stories need review

Validation Statistics:
- Stories split during refinement: {count}
- Average estimated file count: {number}
- Average estimated time: {days} days
- Atomicity improvement: {before_score} → {after_score}
```

---

## 6. Validation Data Collection

### 6.1 Metrics to Track

For future system improvements, collect:

1. **Validation Metrics**:
   - Average atomicity score per feature
   - Distribution of classifications (EXCELLENT/GOOD/NEEDS REVIEW/MUST SPLIT)
   - Common violation patterns
   - Technology reference frequency by technology type

2. **Refinement Metrics**:
   - Number of splitting iterations needed
   - Average stories before/after refinement
   - Most common splitting triggers
   - Time spent in refinement loop

3. **Accuracy Metrics**:
   - Estimated vs actual file counts (post-implementation)
   - Estimated vs actual time (post-implementation)
   - False positive rate (stories flagged but actually atomic)
   - False negative rate (stories passed but should have split)

### 6.2 Feedback Loop

Use collected metrics to:
1. Tune scoring algorithm weights
2. Refine heuristics for file and time estimation
3. Update validation rules based on false positives/negatives
4. Create better splitting recommendation templates
5. Identify agent-specific patterns (e.g., backend stories tend to touch more files)

---

## 7. Extension Points

### 7.1 Future Validation Rules

System designed to easily add new rules:

1. **Domain-Specific Validations**:
   - Security-sensitive story detection
   - Performance-critical story identification
   - Database migration story validation

2. **Agent-Specific Rules**:
   - UI/UX designer stories: Validate design system references
   - DevOps stories: Validate deployment checklist items
   - Backend stories: Validate API contract references

3. **Custom Scoring Profiles**:
   - Strictness levels: Relaxed, Standard, Strict
   - Project-specific thresholds
   - Domain-specific weights (e.g., fintech might weight security validation higher)

### 7.2 Configuration Support

Future enhancement to support configuration file:

```json
{
  "atomicityValidation": {
    "enabled": true,
    "strictness": "standard",
    "thresholds": {
      "excellent": 85,
      "good": 70,
      "needsReview": 50
    },
    "rules": {
      "titleComplexity": {
        "enabled": true,
        "maxConjunctions": 0,
        "maxVerbs": 1,
        "maxCharacters": 80,
        "maxWords": 12
      },
      "acceptanceCriteria": {
        "enabled": true,
        "maxCount": 4,
        "warnAtCount": 4
      },
      "scopeEstimation": {
        "enabled": true,
        "maxFiles": 12,
        "maxDays": 3,
        "idealFiles": 5,
        "idealDays": 1.5
      },
      "technologyAgnostic": {
        "enabled": true,
        "strictMode": true
      }
    },
    "weights": {
      "titleComplexity": 1.0,
      "criteriaComplexity": 1.0,
      "fileImpact": 1.0,
      "timeEstimation": 1.0,
      "technologyReferences": 1.5
    }
  }
}
```

---

## 8. Implementation Considerations

### 8.1 Performance

**Requirements**:
- Validation should complete in < 1 second for typical feature (10-20 stories)
- Minimal memory footprint
- No external API calls (all processing local)

**Approach**:
- Use regex for pattern matching (fast)
- Cache keyword dictionaries at load time
- Process stories in parallel (if needed)
- Avoid expensive NLP operations

### 8.2 Maintainability

**Requirements**:
- Rules easily updatable without code changes
- New validation rules easy to add
- Clear separation of concerns

**Approach**:
- Rule-based architecture
- Each validation dimension in separate function
- Keyword dictionaries in separate data files
- Scoring formulas clearly documented

### 8.3 Testing Strategy

**Test Coverage**:
1. **Unit Tests**: Each validation rule independently
2. **Integration Tests**: Composite scoring with various story types
3. **Regression Tests**: Known good/bad stories from past features
4. **Edge Cases**: Boundary conditions, empty stories, malformed input

**Test Data**:
- Use Features 1-4 existing stories as test corpus
- Create synthetic stories for edge cases
- Maintain "golden set" of perfectly atomic stories
- Maintain "failure set" of clearly non-atomic stories

---

## 9. Success Criteria

This design is successful if:

1. **Validation Accuracy**:
   - 90%+ accuracy in flagging non-atomic stories (validated against Features 1-4)
   - <10% false positive rate

2. **Actionability**:
   - Product owner can understand and act on 100% of validation feedback
   - Splitting recommendations are implementable without additional research

3. **Workflow Integration**:
   - Validation adds <5% to total feature planning time
   - Reduces implementation issues by catching problems early

4. **Technology Compliance**:
   - 100% detection of framework/library/tool mentions
   - Clear guidance for technology-agnostic rewording

5. **Adoption**:
   - Used in 100% of new features after implementation
   - Reduces average atomicity score variance across features

---

## 10. Open Questions

1. **Threshold Calibration**: Should thresholds be stricter (e.g., 80 instead of 70 for GOOD)?
   - Recommendation: Start with 70, tune based on feedback

2. **Auto-Splitting**: Should system automatically split stories or just recommend?
   - Recommendation: Recommend only (Story #4), consider auto-split in future

3. **Validation Bypass**: Should there be a way to override validation for special cases?
   - Recommendation: Allow override with explicit justification in story notes

4. **Historical Analysis**: Should we retroactively validate Features 1-4?
   - Recommendation: Yes, use as calibration data and showcase

5. **Real-time Validation**: Should validation run during story writing or only after?
   - Recommendation: After initial creation, before final report (current design)

---

## 11. References

### 11.1 Product Owner Agent
- Location: `/home/ed/Dev/architecture/.claude/agents/product-owner.md`
- Key sections:
  - Atomicity Principles (lines 54-58)
  - Technology-Agnostic Story Writing (lines 62-106)
  - Atomicity-First Mindset (lines 108-116)
  - Workflow integration points (lines 154-427)

### 11.2 Example Features
- Feature 1: `/home/ed/Dev/architecture/docs/features/1/user-stories.md`
  - 10 stories, well-structured, good atomicity examples
- Feature 2: `/home/ed/Dev/architecture/docs/features/2/user-stories.md`
  - 7 stories, DevOps-focused, sequential execution
- Feature 5: `/home/ed/Dev/architecture/docs/features/5/user-stories.md`
  - 19 stories, meta-developer focus, complex execution order

### 11.3 Related Stories
- Story #1: Research Parallel Execution Patterns (informs execution complexity)
- Story #4: Implement Atomicity Validation (will implement this design)
- Story #8: Create Story Template Library (will use validation insights)

---

## Appendix A: Validation Rule Examples

### Example 1: Title Complexity

**Story**: "Create User Registration Form and Implement Email Verification"

**Analysis**:
- Conjunctions: "and" (1)
- Verbs: "Create" (1), "Implement" (2)
- Character count: 67 (OK)
- Word count: 8 (OK)

**Score**:
```
title_complexity_score = (1 * 3) + (1 * 4) + 0 + 0 + 0 + 0 = 7
Classification: FAIL (score 6+)
```

**Recommendation**: Split into:
1. "Create User Registration Form" (1 verb, no conjunctions)
2. "Implement Email Verification" (1 verb, depends on Story 1)

---

### Example 2: Acceptance Criteria

**Story**: "Setup Development Environment"

**Criteria**:
1. Development server starts successfully
2. Hot reload works when files change
3. ESLint and Prettier configured
4. TypeScript compilation successful
5. Tests run successfully

**Analysis**:
- Criteria count: 5 (exceeds 4)
- Multi-concern: Criteria 3 has "and" (ESLint AND Prettier)
- Implementation-heavy: None
- Cross-concern: Criteria span multiple tools

**Score**:
```
criteria_complexity_score = (1 * 3) + 0 + (1 * 2) + 0 + 0 = 5
Classification: WARNING (score 3-5)
```

**Recommendation**: Split into:
1. "Setup Development Server" (Criteria 1-2)
2. "Configure Code Quality Tools" (Criteria 3)
3. "Setup Build and Test Tools" (Criteria 4-5)

---

### Example 3: File Impact

**Story**: "Create User Authentication System"

**Description**: "Implement complete user authentication including registration, login, password hashing, session management, and JWT token generation. Add middleware for route protection and user role validation."

**Analysis**:
- CRUD operations: Create (registration), Read (login) = 2 ops × 2.5 = 5 files
- Multi-layer: Frontend + Backend = 1.5x multiplier
- API endpoints: registration, login, logout, refresh = 4 × 2 = 8 files
- Database work: User model, migrations = 3 files
- Infrastructure: Middleware = 2 files

**Calculation**:
```
base = 5 + 8 + 3 + 2 = 18 files
with_multiplier = 18 * 1.5 = 27 files
file_impact_score = 6 (13+ files)
```

**Estimated Time**: 27 files × 0.25 = 6.75 days × 1.3 (setup factor) = 8.8 days

**Score**:
```
file_impact_score = 6
time_score = 6 (> 3 days)
Classification: FAIL
```

**Recommendation**: Split into 6+ atomic stories:
1. Create User Registration (3 files, 0.8 days)
2. Implement Password Hashing (2 files, 0.5 days)
3. Create User Login (3 files, 0.8 days)
4. Implement Session Management (4 files, 1.2 days)
5. Add JWT Token Generation (3 files, 1 day)
6. Create Authentication Middleware (3 files, 1 day)
7. Add Role-based Access Control (4 files, 1.2 days)

---

### Example 4: Technology References

**Story**: "Create API Endpoints using Express.js"

**Description**: "Set up Express.js server with RESTful API endpoints. Use middleware for JSON parsing and CORS. Implement error handling with try-catch blocks."

**Criteria**:
1. Express server starts on port 3000
2. GET /api/users endpoint returns user list from PostgreSQL
3. POST endpoint validates with Joi schema
4. All endpoints have unit tests with Jest

**Analysis**:
- Framework mentions: "Express.js" (3 occurrences)
- Library mentions: "Joi" (1), "Jest" (1)
- Pattern mentions: "RESTful" (1), "middleware" (1)
- Tool mentions: "CORS" (1)

**Score**:
```
technology_reference_score = (3 * 3) + (2 * 3) + (2 * 2) + (1 * 2) = 21
Classification: FAIL (4+)
```

**Required Changes**:
- "Express.js" → "server framework"
- "RESTful API" → "API"
- "JSON parsing and CORS" → "request parsing and cross-origin support"
- "PostgreSQL" → "database"
- "Joi" → "validation library"
- "Jest" → "testing framework"

**Corrected Story**: "Create API Endpoints"

**Description**: "Set up server framework with API endpoints. Use request parsing and cross-origin support. Implement error handling."

**Criteria**:
1. Server starts and listens for requests
2. GET endpoint returns user list from database
3. POST endpoint validates input data
4. All endpoints have unit tests

---

## Appendix B: Scoring Calibration Data

Based on analysis of Features 1-4, expected score distributions:

### Feature 1 (10 stories)
| Story # | Title | Est. Score | Classification |
|---------|-------|------------|----------------|
| 1 | Research and Select Frontend Technology Stack | 88 | EXCELLENT |
| 2 | Initialize Frontend Project with Build Tooling | 82 | GOOD |
| 3 | Create Project Directory Structure | 90 | EXCELLENT |
| 4 | Design Foundation and Style System | 85 | EXCELLENT |
| 5 | Configure Development Environment | 75 | GOOD |
| 6 | Create Core Application Shell | 78 | GOOD |
| 7 | Implement Basic Routing Configuration | 80 | GOOD |
| 8 | Configure CI/CD Pipeline for Frontend | 76 | GOOD |
| 9 | Set Up Testing Infrastructure | 79 | GOOD |
| 10 | Create Frontend Documentation | 83 | GOOD |

**Average**: 81.6 (GOOD)

### Feature 2 (7 stories)
| Story # | Title | Est. Score | Classification |
|---------|-------|------------|----------------|
| 1 | Create Multi-Stage Dockerfile for Frontend | 72 | GOOD |
| 2 | Create Docker Ignore File | 92 | EXCELLENT |
| 3 | Create Docker Compose Configuration for Local Development | 68 | WARNING |
| 4 | Add Docker Build Scripts to Package.json | 85 | EXCELLENT |
| 5 | Create Development Dockerfile | 80 | GOOD |
| 6 | Integrate Docker Build into CI/CD Pipeline | 74 | GOOD |
| 7 | Create Docker Documentation | 86 | EXCELLENT |

**Average**: 79.6 (GOOD)

**Note**: Story 3 scores WARNING due to technology-specific references (Vite, port 5173, volume mounts, .env). This validates the need for technology-agnostic validation.

---

## Appendix C: Implementation Checklist

For Story #4 implementation, ensure:

- [ ] Title complexity validation function implemented
- [ ] Acceptance criteria validation function implemented
- [ ] File impact estimation algorithm implemented
- [ ] Time estimation algorithm implemented
- [ ] Technology reference detection implemented
- [ ] Composite scoring algorithm implemented
- [ ] Per-story validation report generation
- [ ] Summary validation report generation
- [ ] JSON output format implemented
- [ ] Integration with product-owner workflow (3 touch points)
- [ ] Validation function interface matches design
- [ ] Test coverage: title rules, criteria rules, scope estimation, technology detection
- [ ] Regression tests with Features 1-4 stories
- [ ] Documentation: validation rules, scoring formulas, integration guide
- [ ] Performance: < 1 second for 20 stories
- [ ] Configuration: Support basic threshold customization

---

**Document Version**: 1.0
**Created**: 2025-10-19
**Author**: Meta-Developer Agent
**Related Stories**: Feature #5, Story #2
**Status**: Design Complete, Ready for Implementation (Story #4)
