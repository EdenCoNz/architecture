# Atomicity Validation System

## Purpose
This helper provides comprehensive atomicity validation for user stories according to the validation system designed in Feature #5, Story #2. It validates stories across 5 dimensions: title complexity, acceptance criteria complexity, file impact estimation, time estimation, and technology-agnostic compliance.

## Usage
When validating user stories, apply each validation dimension below and calculate the composite atomicity score. Use the scoring thresholds to classify stories and provide actionable feedback.

---

## Validation Dimension 1: Title Complexity

### Rules

#### 1.1 Conjunction Detection
**Flag titles containing coordinating conjunctions that join distinct actions**

Patterns to detect:
- " and " (with spaces to avoid false positives like "understand")
- " or "
- " plus "

**Exceptions (allowed)**:
- "Create and Configure" (single cohesive action)
- "Build and Deploy" (when truly atomic)
- "Install and Setup" (when truly atomic)
- Technical phrases that represent single actions

**Scoring**: Each conjunction = +3 points

#### 1.2 Multiple Verb Detection
**Flag titles with 2+ primary action verbs**

Action verbs to detect:
- Create, Build, Implement, Design, Add, Update, Delete, Remove
- Configure, Setup, Initialize, Install
- Test, Validate, Verify
- Document, Write
- Deploy, Release
- Integrate, Connect
- Refactor, Optimize
- Research, Investigate, Analyze

**Scoring**: Each verb beyond the first = +4 points

#### 1.3 Scope Keywords
**Flag titles suggesting multiple concerns**

Keywords to detect:
- "including"
- "with"
- "containing"
- "covering"

**Scoring**: Each scope keyword = +2 points

#### 1.4 Title Length
**Flag overly complex titles**

Checks:
- Character count > 80 = +2 points
- Word count > 12 = +1 point
- Multiple clauses (comma-separated sections > 1) = clause_count × 2 points

### Title Complexity Score Calculation

```
title_complexity_score =
  (conjunction_count × 3) +
  (excess_verb_count × 4) +  // verbs beyond the first
  (scope_keyword_count × 2) +
  (character_count > 80 ? 2 : 0) +
  (word_count > 12 ? 1 : 0) +
  (clause_count > 1 ? clause_count × 2 : 0)
```

### Classification
- **0-2**: PASS (atomic)
- **3-5**: WARNING (potentially compound)
- **6+**: FAIL (definitely compound)

### Feedback Templates

**For FAIL (score 6+)**:
```
[FAIL] Title Complexity: Score {score}/6+
Issue: Title contains {issues_list}
→ Suggestion: Split into separate stories:
  1. "{first_action_extracted}"
  2. "{second_action_extracted}"
```

**For WARNING (score 3-5)**:
```
[WARNING] Title Complexity: Score {score}
Issue: {specific_issues}
→ Suggestion: Consider simplifying or reviewing if this represents multiple concerns
```

---

## Validation Dimension 2: Acceptance Criteria Complexity

### Rules

#### 2.1 Count Limits
- **1-2 criteria**: Ideal atomic story
- **3 criteria**: Acceptable if closely related
- **4 criteria**: Warning - at edge of atomicity
- **5+ criteria**: Fail - definitely needs splitting

**Scoring**:
- criteria_count > 4: (criteria_count - 4) × 3 points
- criteria_count === 4: +1 point

#### 2.2 Multi-Concern Criteria
**Flag criteria with "and" joining distinct outcomes**

Pattern: Criterion contains " and " joining separate testable outcomes

Example: "User can login AND password is hashed AND session persists"
→ Should be 3 separate criteria or 3 separate stories

**Scoring**: Each multi-concern criterion = +2 points

#### 2.3 Implementation-Heavy Criteria
**Flag criteria describing multiple implementation steps**

Heuristic: Criteria > 20 words with multiple clauses

Example: "System validates input, transforms data, stores in database, and sends confirmation email"

**Scoring**: Each implementation-heavy criterion = +2 points

#### 2.4 Cross-Concern Criteria
**Flag criteria spanning multiple system areas**

Keywords indicating cross-concern:
- "frontend" + "backend" in same criterion
- "database" + "API" in same criterion
- "UI" + "server" in same criterion
- Multiple layers mentioned together

**Scoring**: Each cross-concern criterion = +3 points

### Criteria Complexity Score Calculation

```
criteria_complexity_score =
  (criteria_count > 4 ? (criteria_count - 4) × 3 : 0) +
  (criteria_count === 4 ? 1 : 0) +
  (multi_concern_criteria_count × 2) +
  (implementation_heavy_count × 2) +
  (cross_concern_count × 3)
```

### Classification
- **0-2**: PASS (focused)
- **3-5**: WARNING (potentially unfocused)
- **6+**: FAIL (definitely needs splitting)

### Feedback Templates

**For FAIL (score 6+)**:
```
[FAIL] Acceptance Criteria: Score {score}/6+
Issues:
- {criteria_count} criteria detected (limit: 4)
- {multi_concern_count} criteria contain multiple distinct outcomes
→ Suggestion: Split story by criteria groupings or separate concerns
```

**For WARNING (score 3-5)**:
```
[WARNING] Acceptance Criteria: {criteria_count} criteria (approaching limit)
→ Suggestion: Review if criteria {numbers} could be separate story
```

---

## Validation Dimension 3: File Impact Estimation

### Heuristics for File Count Estimation

#### 3.1 CRUD Operation Detection
Count occurrences of CRUD verbs in title and description:
- Create, Build, Add: ~3 files (handler, validation, tests)
- Read, Get, Fetch, Retrieve: ~2 files (handler, tests)
- Update, Modify, Edit: ~3 files (handler, validation, tests)
- Delete, Remove: ~2 files (handler, tests)

**Base calculation**: CRUD_operations × 2.5 files average

#### 3.2 Component Keywords
UI component work suggests 2-3 files per component

Keywords: component, page, form, modal, dialog, layout, view, screen

**Calculation**: component_count × 2.5 files

#### 3.3 Infrastructure Keywords
Infrastructure work suggests 3-5 files

Keywords: setup, configure, initialize, install, scaffold

**Calculation**: infrastructure_detected ? 4 files : 0

#### 3.4 Multi-Layer Detection
Work spanning multiple layers increases file count

Detection:
- Frontend keywords (UI, component, page, client) + Backend keywords (server, API, database, endpoint)
- Frontend + Backend: multiply estimate by 1.5
- Database involvement: add 3 files
- API endpoints mentioned: add 2 files per endpoint

#### 3.5 Documentation Work
Documentation adds 1-2 files

Keywords: document, README, guide, docs, documentation

**Calculation**: documentation_work ? 1.5 : 0

### File Impact Score Calculation

```
estimated_file_count =
  (crud_operations × 2.5) +
  (component_count × 2.5) +
  (infrastructure_setup ? 4 : 0) +
  (base_estimate × multi_layer_multiplier) +  // 1.0, 1.5, or 2.0
  (database_work ? 3 : 0) +
  (api_endpoints × 2) +
  (documentation_work ? 1.5 : 0)

file_impact_score =
  (estimated_file_count <= 5 ? 0 : 0) +     // Ideal
  (estimated_file_count 6-8 ? 2 : 0) +      // Acceptable
  (estimated_file_count 9-12 ? 4 : 0) +     // Warning
  (estimated_file_count > 12 ? 6 : 0)       // Fail
```

### Classification
- **1-5 files**: PASS (ideal atomic scope)
- **6-8 files**: WARNING (acceptable but monitor)
- **9-12 files**: WARNING (consider splitting)
- **13+ files**: FAIL (definitely too large)

### Feedback Templates

**For FAIL (13+ files)**:
```
[FAIL] Estimated File Impact: ~{count} files
→ Suggestion: Split story by:
  - Layer (frontend/backend)
  - CRUD operation (separate Create, Read, Update, Delete)
  - Component (one story per major component)
  - Concern (separate business logic from UI)
```

**For WARNING (6-12 files)**:
```
[WARNING] Estimated File Impact: ~{count} files
→ Suggestion: Consider if story can be split into smaller vertical slices
```

---

## Validation Dimension 4: Time Estimation

### Time Estimation Algorithm

#### Base Time Calculation
```
base_time_days = estimated_file_count × 0.25
```
(Assumes 4 files per day average development pace)

#### Complexity Multipliers
Apply multiplier based on story type (detect from title/description):

- **Research story** (keywords: research, investigate, evaluate, analyze, spike): 1.5x
- **Design story** (keywords: design, mockup, wireframe, prototype): 1.2x
- **Setup/Configuration** (keywords: setup, configure, initialize, install): 1.3x
- **Testing story** (keywords: test, testing, E2E, integration test): 0.8x
- **Bug fix** (keywords: fix, bug, issue, resolve): 0.6x
- **Standard development**: 1.0x

#### Technology Factors
Add time for complexity factors:

- New technology mentioned: +0.5 days
- Integration work (keywords: integrate, connect, combine): +0.3 days
- Complex business logic (keywords: validation, calculation, workflow, algorithm): +0.5 days

### Time Score Calculation

```
estimated_days =
  (estimated_file_count × 0.25) ×
  complexity_multiplier +
  technology_factor

time_score =
  (estimated_days <= 1 ? 0 : 0) +       // Ideal
  (estimated_days 1-2 ? 1 : 0) +        // Good
  (estimated_days 2-3 ? 3 : 0) +        // Warning
  (estimated_days > 3 ? 6 : 0)          // Fail
```

### Classification
- **0-1 days**: PASS (excellent atomic scope)
- **1-2 days**: PASS (good atomic scope)
- **2-3 days**: WARNING (at edge of atomicity)
- **3+ days**: FAIL (too large, must split)

### Feedback Templates

**For FAIL (3+ days)**:
```
[FAIL] Estimated Time: ~{days} days
→ Suggestion: Story too large. Split into smaller stories of 1-2 days each
  - Consider vertical slicing (complete feature subset)
  - Or horizontal slicing (by layer or component)
```

**For WARNING (2-3 days)**:
```
[WARNING] Estimated Time: ~{days} days
→ Suggestion: Story at edge of atomicity. Consider splitting if possible
```

---

## Validation Dimension 5: Technology-Agnostic Compliance

### Technology Reference Detection

Scan title, description, and acceptance criteria for technology-specific references.

#### 5.1 Framework Detection
**Score**: +3 per mention

Frameworks to detect:
- Frontend: React, Vue, Angular, Svelte, Solid, Next.js, Nuxt, Gatsby, Remix
- Backend: Express, NestJS, Fastify, Koa, Django, Flask, FastAPI, Spring, Rails
- Full-stack: Meteor, Blitz

#### 5.2 Library Detection
**Score**: +3 per mention

Common libraries:
- HTTP: Axios, Fetch, Got, Superagent
- State: Redux, MobX, Zustand, Jotai, Recoil
- Forms: Formik, React Hook Form, Yup, Joi
- Data: Prisma, TypeORM, Sequelize, Mongoose, Drizzle
- Testing: Jest, Vitest, Mocha, Chai, Cypress, Playwright
- Utility: Lodash, Ramda, date-fns, Moment

#### 5.3 File Extension Detection
**Score**: +2 per mention

Extensions: .js, .ts, .tsx, .jsx, .py, .java, .go, .rs, .json, .yml, .yaml, .toml, .xml, .md, .css, .scss, .less

#### 5.4 Tool Detection
**Score**: +2 per mention

Tools:
- Package managers: npm, yarn, pnpm, pip, cargo, go mod
- Build tools: Webpack, Vite, Rollup, Parcel, esbuild, Turbopack
- Code quality: ESLint, Prettier, Biome, Stylelint
- Runtime: Node.js, Deno, Bun

#### 5.5 Architectural Pattern Detection
**Score**: +2 per mention

Patterns: REST, RESTful, GraphQL, gRPC, WebSocket, SSR, SSG, SPA, MVC, MVVM, Microservices, Monolith

#### 5.6 Language Detection
**Score**: +3 per mention

Languages: JavaScript, TypeScript, Python, Java, Go, Rust, C#, PHP, Ruby, Kotlin, Swift

### Exceptions (Allowed Terms)
These generic terms are allowed:
- "framework", "library", "database", "server", "client"
- "frontend", "backend", "API", "endpoint"
- "test", "build", "deploy"
- "configuration", "environment"
- File paths in acceptance criteria (when testing specific file creation)
- Agent names in "Agent:" field

### Technology Score Calculation

```
technology_reference_score =
  (framework_mentions × 3) +
  (library_mentions × 3) +
  (file_extension_mentions × 2) +
  (tool_mentions × 2) +
  (pattern_mentions × 2) +
  (language_mentions × 3)
```

### Classification
- **0**: PASS (fully technology-agnostic)
- **1-3**: WARNING (minor technology leakage)
- **4+**: FAIL (violates technology-agnostic principle)

### Feedback Templates

**For FAIL (score 4+)**:
```
[FAIL] Technology References: {count} violations detected
Violations:
- {location}: "{technology}" → Replace with "{generic_term}"
- {location}: "{technology}" → Replace with "{generic_term}"

Required Action: Remove ALL technology-specific references. Focus on WHAT needs to be achieved, not HOW to implement it.
```

**For WARNING (score 1-3)**:
```
[WARNING] Technology References: Minor violations detected
- {location}: "{technology}" → Consider replacing with "{generic_term}"
```

### Generic Replacement Guide

| Technology-Specific | Generic Replacement |
|---------------------|---------------------|
| React, Vue, Angular | frontend framework, UI framework |
| Express, NestJS, Django | server framework, backend framework |
| PostgreSQL, MongoDB | database, data store |
| Jest, Vitest, Mocha | testing framework, test runner |
| ESLint, Prettier | code quality tools, linting tools |
| npm, yarn | package manager, dependency manager |
| Webpack, Vite | build tool, bundler |
| .ts, .tsx files | source files, component files |
| REST API, GraphQL | API, endpoints |
| TypeScript, JavaScript | programming language (or omit entirely) |

---

## Composite Atomicity Score

### Overall Score Calculation

```
atomicity_score =
  title_complexity_score +
  criteria_complexity_score +
  file_impact_score +
  time_score +
  technology_reference_score

weighted_score = 100 - (atomicity_score × 3)  // Lower atomicity_score = higher weighted_score

Note: If weighted_score < 0, set to 0
      If weighted_score > 100, set to 100
```

### Story Classification

Based on weighted_score (0-100):

- **85-100: EXCELLENT** ✅
  - Story is perfectly atomic
  - No action required
  - Include in report as exemplar

- **70-84: GOOD** ✅
  - Story is atomic but could be improved
  - Include minor suggestions
  - Continue with story as-is

- **50-69: NEEDS REVIEW** ⚠️
  - Story has atomicity concerns
  - Highlight specific issues
  - Provide splitting suggestions
  - Product owner should refine

- **0-49: MUST SPLIT** ❌
  - Story is clearly not atomic
  - Must be refactored before implementation
  - Provide detailed splitting guidance
  - Product owner must refactor

---

## Validation Output Format

### Per-Story Validation Report

```markdown
### Story #{number}: {title}

**Atomicity Score: {weighted_score}/100 - {classification}**

{If score < 85, show breakdown:}
Dimension Scores:
- Title Complexity: {score} ({status})
- Acceptance Criteria: {score} ({status})
- Estimated File Impact: ~{count} files ({score} points, {status})
- Estimated Time: ~{days} days ({score} points, {status})
- Technology References: {score} ({status})

{If any issues detected:}
Issues Detected:

{For each dimension with issues:}
- [{severity}] {Dimension}: {specific issue}
  → Suggestion: {actionable suggestion}

{If technology violations:}
Technology Violations:
- [{severity}] {location}: "{violation}" → Replace with "{suggestion}"

{If score < 70, provide splitting recommendations:}
Splitting Recommendations:
1. Story {number}A: {focused first part}
   - Criteria: {1-2 criteria from original}
   - Estimated: {files} files, {days} days

2. Story {number}B: {focused second part}
   - Criteria: {1-2 criteria from original}
   - Estimated: {files} files, {days} days
   - Dependencies: Story {number}A
```

### Summary Validation Report

```markdown
## Atomicity Validation Summary

**Overall Statistics:**
- Total Stories Validated: {count}
- Average Atomicity Score: {score}/100

**Classification Distribution:**
- ✅ EXCELLENT (85-100): {count} stories {if count > 0: - #{story_numbers}}
- ✅ GOOD (70-84): {count} stories {if count > 0: - #{story_numbers}}
- ⚠️ NEEDS REVIEW (50-69): {count} stories {if count > 0: - #{story_numbers}}
- ❌ MUST SPLIT (0-49): {count} stories {if count > 0: - #{story_numbers}}

**Technology-Agnostic Compliance:**
- Fully compliant: {count} stories
- Minor violations: {count} stories
- Major violations: {count} stories

**Recommended Actions:**
{if mustSplit > 0:}
1. ❌ CRITICAL: Split {count} stories that scored below 50
{if needsReview > 0:}
2. ⚠️ IMPORTANT: Review {count} stories that scored 50-69
{if technology violations:}
3. Fix technology references in {count} stories

**Estimated Impact:**
- Average estimated files per story: {number}
- Average estimated time per story: {days} days
- Stories requiring immediate attention: {count}

{If refinement was done:}
**Refinement Progress:**
- Stories before refinement: {count}
- Stories after refinement: {count}
- Atomicity score improvement: {before_avg} → {after_avg}
```

---

## Validation Workflow Integration

### When to Run Validation

1. **After Initial Story Creation** (Step 8.5 in product-owner workflow)
   - Run validation on all newly created stories
   - Identify stories that MUST_SPLIT or NEED_REVIEW
   - Use results to prioritize refinement efforts

2. **During Refinement** (Step 9 in product-owner workflow)
   - Re-run validation after each refinement iteration
   - Focus on stories with score < 70
   - Continue until all stories score >= 70

3. **Before Final Report** (Step 13 in product-owner workflow)
   - Final validation pass on all stories
   - Verify all stories score >= 70
   - Include summary in final report

### Validation Process

For each story:
1. **Extract story components**: title, description, acceptance criteria
2. **Run each validation dimension**: calculate individual scores
3. **Calculate composite score**: sum dimension scores, convert to weighted score
4. **Classify story**: EXCELLENT, GOOD, NEEDS_REVIEW, or MUST_SPLIT
5. **Generate feedback**: dimension-specific issues and suggestions
6. **Provide splitting guidance**: if score < 70, recommend how to split

After validating all stories:
1. **Generate summary report**: statistics and distribution
2. **Identify priority actions**: which stories need immediate attention
3. **Calculate metrics**: averages, compliance rates
4. **Track refinement**: if validation run multiple times, show improvement

---

## Quick Reference: Validation Checklist

Use this checklist when validating stories:

### Title Validation
- [ ] Count conjunctions ("and", "or", "plus")
- [ ] Count action verbs (should be 1)
- [ ] Check for scope keywords ("including", "with", "containing")
- [ ] Check length (≤80 chars, ≤12 words)
- [ ] Check for multiple clauses

### Acceptance Criteria Validation
- [ ] Count criteria (should be ≤4)
- [ ] Check for multi-concern criteria (contains "and" joining distinct outcomes)
- [ ] Check for implementation-heavy criteria (>20 words with multiple clauses)
- [ ] Check for cross-concern criteria (spans multiple layers)

### Scope Validation
- [ ] Estimate file count based on CRUD, components, layers
- [ ] Estimate time based on files × 0.25 × complexity multiplier
- [ ] Verify file count ≤ 12
- [ ] Verify time ≤ 3 days

### Technology Validation
- [ ] Scan for framework names
- [ ] Scan for library names
- [ ] Scan for file extensions
- [ ] Scan for tool names
- [ ] Scan for architectural patterns
- [ ] Scan for programming languages
- [ ] Verify 0 violations (or provide generic replacements)

### Final Check
- [ ] Calculate composite atomicity score
- [ ] Classify story (EXCELLENT/GOOD/NEEDS_REVIEW/MUST_SPLIT)
- [ ] Generate actionable feedback
- [ ] Provide splitting recommendations if needed

---

## Example Validation Outputs

### Example 1: EXCELLENT Story (Score: 92/100)

**Story #5: Create User Registration Form**

**Atomicity Score: 92/100 - EXCELLENT ✅**

No issues detected. Story is perfectly atomic.

---

### Example 2: NEEDS REVIEW Story (Score: 58/100)

**Story #3: Setup Development Environment**

**Atomicity Score: 58/100 - NEEDS REVIEW ⚠️**

Dimension Scores:
- Title Complexity: 0 (PASS)
- Acceptance Criteria: 5 (WARNING) - 5 criteria detected
- Estimated File Impact: ~7 files (2 points, WARNING)
- Estimated Time: ~2.2 days (3 points, WARNING)
- Technology References: 0 (PASS)

Issues Detected:

- [WARNING] Acceptance Criteria: 5 criteria detected (limit: 4)
  → Suggestion: Split story by criteria groupings. Consider separating tool setup from server setup.

- [WARNING] Estimated File Impact: ~7 files
  → Suggestion: Consider splitting by concern (development server vs. code quality tools vs. build tools)

- [WARNING] Estimated Time: ~2.2 days
  → Suggestion: Story at edge of atomicity. Consider splitting for better focus.

Splitting Recommendations:
1. Story 3A: Setup Development Server
   - Criteria: Development server starts successfully, Hot reload works
   - Estimated: 3 files, 0.8 days

2. Story 3B: Configure Code Quality Tools
   - Criteria: Linting and formatting configured
   - Estimated: 2 files, 0.5 days

3. Story 3C: Setup Build and Test Tools
   - Criteria: Build process successful, Tests run successfully
   - Estimated: 2 files, 0.6 days

---

### Example 3: MUST SPLIT Story (Score: 35/100)

**Story #8: Create User Authentication System**

**Atomicity Score: 35/100 - MUST SPLIT ❌**

Dimension Scores:
- Title Complexity: 0 (PASS)
- Acceptance Criteria: 6 (FAIL) - 6 criteria detected
- Estimated File Impact: ~18 files (6 points, FAIL)
- Estimated Time: ~5.5 days (6 points, FAIL)
- Technology References: 3 (WARNING)

Issues Detected:

- [FAIL] Acceptance Criteria: 6 criteria detected (limit: 4)
  → Suggestion: Split story by criteria groupings. Consider separate stories for registration, login, and session management.

- [FAIL] Estimated File Impact: ~18 files
  → Suggestion: Split story by:
    - CRUD operation (registration, login, logout)
    - Concern (password hashing, session management, JWT tokens)
    - Layer (frontend auth UI, backend auth API)

- [FAIL] Estimated Time: ~5.5 days
  → Suggestion: Story too large. Split into smaller stories of 1-2 days each

Technology Violations:
- [WARNING] Description: "JWT" → Replace with "authentication tokens"
- [WARNING] Criteria: "session cookies" → Replace with "session storage"

Splitting Recommendations:
1. Story 8A: Create User Registration
   - Criteria: Users can register with credentials, Registration data validates and persists
   - Estimated: 4 files, 1.2 days

2. Story 8B: Implement Password Security
   - Criteria: Passwords are securely stored, Password strength validated
   - Estimated: 2 files, 0.6 days
   - Dependencies: Story 8A

3. Story 8C: Create User Login
   - Criteria: Users can login with credentials, Invalid credentials rejected
   - Estimated: 3 files, 0.9 days
   - Dependencies: Story 8A, 8B

4. Story 8D: Implement Session Management
   - Criteria: User sessions persist across requests, Sessions expire appropriately
   - Estimated: 3 files, 1.0 days
   - Dependencies: Story 8C

5. Story 8E: Add Authentication Token Generation
   - Criteria: Authenticated users receive tokens, Tokens validate user identity
   - Estimated: 3 files, 0.9 days
   - Dependencies: Story 8C

6. Story 8F: Create Authentication Middleware
   - Criteria: Protected routes require authentication, Unauthorized access blocked
   - Estimated: 3 files, 0.9 days
   - Dependencies: Story 8E

---

## Notes for Implementation

### Performance Considerations
- Validation should complete in < 1 second for 20 stories
- Use simple pattern matching (indexOf, includes, regex) for detection
- Avoid complex NLP or external API calls
- Process stories sequentially (parallel processing not needed for small sets)

### Maintainability
- Rules are defined declaratively in this document
- Easy to update keyword lists and scoring weights
- Each validation dimension is independent
- Clear separation between detection, scoring, and reporting

### Future Enhancements
- Configuration file support for custom thresholds
- Historical metric tracking for accuracy tuning
- Auto-splitting capability (currently recommendation-only)
- Domain-specific validation rules
- Agent-specific validation profiles
