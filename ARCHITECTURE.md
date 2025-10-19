# Architecture System Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Design Principles](#design-principles)
3. [Agent Architecture](#agent-architecture)
4. [Command System](#command-system)
5. [Feature Lifecycle Management](#feature-lifecycle-management)
6. [Helper System](#helper-system)
7. [Integration Patterns](#integration-patterns)
8. [Data Flow and State Management](#data-flow-and-state-management)
9. [Quality and Validation](#quality-and-validation)
10. [Extension Points](#extension-points)

---

## System Overview

The Architecture System is an automated development workflow orchestration platform that transforms feature requests and bug reports into actionable, atomic user stories, then coordinates their implementation across specialized AI agents. The system provides comprehensive lifecycle management from initial planning through implementation, summarization, and archival.

### Key Components

- **Agents**: Specialized AI personas with domain expertise (product-owner, backend-developer, frontend-developer, devops-engineer, ui-ux-designer, meta-developer, research-specialist)
- **Commands**: Slash commands that orchestrate workflows (/feature, /implement, /fix, /summarise, /dashboard, /metrics, /commit, /rollback)
- **Helpers**: Validation systems, templates, error handling, state management, and utility functions
- **Feature Log**: Central registry tracking all features through their complete lifecycle
- **Implementation Logs**: Detailed records of story execution, file changes, and implementation progress

### Value Proposition

The system solves the challenge of maintaining consistent, high-quality development workflows by:

1. **Enforcing Atomicity**: Automatically validates and guides creation of small, independently deployable user stories
2. **Technology-Agnostic Planning**: Separates WHAT from HOW, letting specialized agents choose optimal implementations
3. **Automated Orchestration**: Handles parallel execution, dependency management, resume capability, and error handling
4. **State Tracking**: Comprehensive lifecycle state management with automatic transitions and validation
5. **Quality Assurance**: Multi-layer validation, pre-flight checks, atomicity scoring, and error handling
6. **Context Optimization**: Intelligent context caching and summarization reduce computational overhead

---

## Design Principles

### 1. Separation of Concerns

**Principle**: Each component has a single, well-defined responsibility.

**Application**:
- **Product Owner**: Plans features, creates user stories (WHAT to build)
- **Development Agents**: Implement stories with technical decisions (HOW to build)
- **Meta-Developer**: Builds and improves the system itself
- **Commands**: Orchestrate workflows, coordinate agents, manage state
- **Helpers**: Provide reusable validation, templates, and utilities

### 2. Technology-Agnostic Planning

**Principle**: User stories describe observable behaviors and outcomes, never specific technologies.

**Application**:
- Product owner creates stories without mentioning React, Django, PostgreSQL, etc.
- Development agents choose technologies based on project context and best practices
- Stories use generic terms: "build system" not "Vite", "server framework" not "Express.js"
- Acceptance criteria focus on behavior: "Users can authenticate" not "JWT token validation works"

### 3. Atomicity First

**Principle**: Stories must be small, focused, and independently deployable.

**Application**:
- Automated atomicity validation scores stories on 0-100 scale
- Stories scoring <70 flagged for splitting
- Validation checks: title complexity, criteria count, file impact, time estimation
- Product owner iteratively refines until all stories meet threshold

### 4. Fail-Safe Operations

**Principle**: Operations fail gracefully with clear error messages and recovery guidance.

**Application**:
- Comprehensive pre-flight validation before any destructive operations
- Structured error codes (ENV-001, FS-002, DEP-003, etc.) with remediation steps
- Checkpoint system creates automatic backups before major operations
- Resume capability allows continuation after interruptions

### 5. Observability

**Principle**: All operations trackable and debuggable.

**Application**:
- Implementation logs record every story execution with files modified, tools used, issues encountered
- State history preserves all feature transitions with timestamps and triggers
- Metrics system tracks completion time, velocity, and quality indicators
- Rollback history maintains audit trail of all system reversions

### 6. Extensibility

**Principle**: System designed for future additions without breaking existing functionality.

**Application**:
- Agent definitions are markdown files - easy to add new specialized agents
- Command structure standardized - new commands follow same patterns
- Helper system provides reusable validation and utilities
- Backward compatibility maintained for legacy features (automatic migration)

---

## Agent Architecture

### Agent Model

Agents are specialized AI personas defined in `.claude/agents/*.md` files. Each agent has:

- **Purpose**: Clear mission statement defining agent's role
- **Core Expertise**: Detailed breakdown of specialized capabilities
- **Best Practices**: Standards, anti-patterns, and guidelines
- **Workflow**: Step-by-step processes for completing tasks
- **Report Format**: Standardized output structure

### Agent Types

#### Planning Agent

**product-owner** (`.claude/agents/product-owner.md`)
- **Responsibility**: Transform feature requests into atomic, technology-agnostic user stories
- **Key Capabilities**:
  - Story decomposition using atomicity validation
  - CRUD operation splitting
  - Design-implementation separation
  - DevOps-development separation
  - Agent assignment based on available agents
  - Execution order optimization (parallel vs sequential)
  - Story template library usage
- **Integration**: Called by `/feature` and `/fix` commands

#### Development Agents

**backend-developer** (`.claude/agents/backend-developer.md`)
- **Responsibility**: Implement server-side application logic and APIs
- **Context**: Loads `context/backend/**/*` for best practices

**frontend-developer** (`.claude/agents/frontend-developer.md`)
- **Responsibility**: Implement client-side UI and user interactions
- **Context**: Loads `context/frontend/**/*` for best practices

**devops-engineer** (`.claude/agents/devops-engineer.md`)
- **Responsibility**: Docker, CI/CD, deployment automation, infrastructure
- **Context**: Loads `context/devops/**/*` for best practices

**ui-ux-designer** (`.claude/agents/ui-ux-designer.md`)
- **Responsibility**: Create wireframes, component specs, design systems
- **Updates**: `docs/design-brief.md` with design decisions

#### Meta-Development Agent

**meta-developer** (`.claude/agents/meta-developer.md`)
- **Responsibility**: Build and improve the architecture system itself (agents, commands, helpers)
- **Scope**: Works ON the system, not WITH the system
- **Expertise**: Agent design, command workflows, validation systems, documentation

#### Research Agent

**research-specialist** (`.claude/agents/research-specialist.md`)
- **Responsibility**: Technology evaluation, best practices research, solution analysis
- **Deliverables**: Research documents with trade-offs and recommendations

### Agent Interaction Patterns

#### Direct Agent Launch (Implementation)

```
/implement command
  → Reads user-stories.md
  → For each story in execution order:
    → Loads agent-specific context
    → Launches agent with story details
    → Agent executes story
    → Records in implementation-log.json
  → Updates feature state
```

#### Agent Handoff (Planning to Implementation)

```
/feature command
  → Launches product-owner agent
  → Product owner creates user stories
  → Assigns agents to each story
  → Defines execution order
  → If no missing agents:
    → Automatically launches /implement
    → /implement executes stories with assigned agents
```

#### Agent Context Loading

Agents receive context based on:
1. **Agent Type**: Default context directory (`context/backend/**/*` for backend-developer)
2. **Keywords**: Story title/description triggers additional context (`"Docker"` → `context/devops/docker.md`)
3. **Phase-Level Caching**: Context loaded once per execution phase, reused across all stories in phase

---

## Command System

### Command Structure

Commands are defined in `.claude/commands/*.md` files with standardized sections:

```markdown
---
description: Brief description
args: [optional arguments]
model: claude-sonnet-4-5
---

## Purpose
What this command does

## Variables
Input/output variables

## Instructions
How to execute command

## Error Handling
Error codes and recovery

## Workflow
Step-by-step execution

## Report
Output format
```

### Core Commands

#### /feature

**Purpose**: Transform feature request into user stories, create git branch, auto-implement if agents available

**Workflow**:
1. Pre-flight validation (git repo, agents directory, feature log)
2. Launch product-owner agent with feature request
3. Check for missing agents
4. If no missing agents:
   - Create git branch (`feature/{id}-{slug}`)
   - Commit planning files
   - Update feature state to "planned"
   - Auto-launch `/implement`
5. If missing agents: Report and wait for user to create agents

**State Transition**: null → planned

**Files Created**:
- `docs/features/{id}/user-stories.md`
- `docs/features/feature-log.json` (updated)

#### /implement

**Purpose**: Execute user stories in execution order with parallel/sequential support and resume capability

**Workflow**:
1. Pre-flight validation (git repo, feature log, user stories, git branch)
2. Load implementation log to identify completed stories
3. Parse execution order (phases, parallel vs sequential)
4. For each phase:
   - Filter completed vs pending stories
   - Load context once (phase-level caching)
   - Execute pending stories (skip completed)
   - Record implementations in log
5. Update feature state: planned → in_progress → deployed
6. Commit and push implementation

**State Transitions**:
- planned → in_progress (when first story starts)
- in_progress → deployed (when all stories complete)

**Resume Capability**: Automatically skips completed stories, resumes from next pending story

**Context Optimization**: Loads shared context files once per phase, caches for all stories in phase

#### /fix

**Purpose**: Process GitHub issues into bug fix user stories, then implement

**Workflow**:
1. Fetch GitHub Actions run logs or issue details
2. Extract error information
3. Launch product-owner to create bug fix stories
4. Create bug directory: `docs/features/{featureId}/bugs/{bugId}/`
5. Auto-implement bug fix stories

**Bug ID Format**: `github-issue-{number}` (e.g., `github-issue-37`)

#### /summarise

**Purpose**: Analyze implemented features, create concise summaries, reduce context for future agents

**Workflow**:
1. Pre-flight validation (git repo, feature log)
2. Identify unsummarised features (isSummarised: false)
3. For each unsummarised feature:
   - Read implementation-log.json
   - Read user-stories.md
   - Analyze completed vs partial vs blocked stories
   - Generate summary with key outcomes
4. Update implementation-log-summary.json
5. Update feature state: deployed → summarised

**State Transition**: deployed → summarised

**Context Reduction**: Typical 80-90% reduction in context size for future agents

#### /dashboard

**Purpose**: Display all features with current states, metrics, and progress indicators

**Output**:
- Features grouped by state
- Summary statistics (total, by state, completion rate)
- Key metrics per feature

#### /metrics

**Purpose**: Report performance indicators (story completion time, velocity, quality metrics)

**Metrics Tracked**:
- Story completion time by agent
- Feature implementation velocity
- Atomicity scores over time
- Error rates and recovery times

#### /commit

**Purpose**: Commit changes with standardized message format, optional push to remote

**Usage**:
- `/commit "message"` - Commit only
- `/commit "message" push` - Commit and push

**Integration**: Used by other commands for automated commits

#### /rollback

**Purpose**: Revert system state using checkpoints created before major operations

**Workflow**:
1. List available checkpoints
2. Show rollback preview (files affected, features impacted)
3. Create pre-rollback checkpoint (safety net)
4. Restore files from selected checkpoint
5. Validate restoration
6. Log rollback in rollback-history.json

**Checkpoint Triggers**: Automatic checkpoints before /feature, /implement, /fix, /summarise

### Command Orchestration

#### Sequential Execution

Commands execute steps one at a time when dependencies exist:

```
/feature
  → Pre-flight validation
  → Launch product-owner (wait for completion)
  → Check missing agents
  → Create git branch
  → Commit planning
  → Launch /implement (sequential dependency)
```

#### Parallel Execution

Commands launch multiple operations simultaneously when independent:

```
/implement Phase 2 (Parallel)
  → Story #3: backend-developer (parallel)
  → Story #4: frontend-developer (parallel)
  → Story #5: devops-engineer (parallel)
  → All three stories execute simultaneously
```

#### Error Handling

Comprehensive error handling with structured error codes:

**Error Categories**:
- **ENV**: Environment issues (ENV-001: not a git repo)
- **FS**: File system issues (FS-002: directory not found)
- **DEP**: Dependency issues (DEP-003: feature not found)
- **INPUT**: Input validation (INPUT-002: invalid bug ID format)
- **STATE**: State transition issues (STATE-004: invalid transition)
- **DATA**: Data integrity (DATA-005: corrupted JSON)
- **GIT**: Git operations (GIT-007: uncommitted changes)

**Error Message Format**:
```
Error: [Human-readable description]

Check: [What was being validated]
Status: [Current state]
Command: [Command that failed]

Remediation:
1. [Specific step to fix]
2. [Alternative approach]
3. [Recovery command]
```

---

## Feature Lifecycle Management

### Lifecycle States

Features progress through comprehensive states with automatic transitions:

```
      /feature          /implement        /implement       /summarise
null --------→ planned ----------→ in_progress -------→ deployed --------→ summarised --------→ archived
                 │                     │                    │                  │
                 │                     │                    │                  │
                 └─────────────────────┴────────────────────┴──────────────────┴─── (manual override)
```

#### State Definitions

**planned**
- Feature created, user stories written
- Entry: /feature command completes
- Indicators: userStoriesCreated set, userStoriesImplemented null

**in_progress**
- Implementation started, not all stories complete
- Entry: /implement starts executing first story
- Indicators: implementation-log.json exists with entries

**deployed**
- All stories completed and deployed
- Entry: /implement completes all stories
- Indicators: userStoriesImplemented set, all stories status: "completed"

**summarised**
- Implementation summarized for reduced context
- Entry: /summarise processes feature
- Indicators: isSummarised: true, summarisedAt set

**archived**
- Feature complete, historical reference only
- Entry: Manual state override
- Indicators: archivedAt set

### State Transition Rules

#### Automatic Transitions (enforced by commands)

```
planned → in_progress     (/implement starts)
in_progress → deployed    (/implement completes all stories)
deployed → summarised     (/summarise processes feature)
```

#### Manual Override Transitions (exceptional cases)

```
planned → archived        (feature cancelled)
in_progress → planned     (rollback scenario)
deployed → in_progress    (new stories added)
summarised → deployed     (re-implementation needed)
archived → deployed       (unarchive scenario)
```

#### Invalid Transitions (prevented)

```
planned → deployed        (must go through in_progress)
planned → summarised      (must implement first)
in_progress → summarised  (must complete first)
```

### State Tracking

#### State History

Each state transition recorded in `stateHistory` array:

```json
{
  "featureID": "5",
  "state": "in_progress",
  "stateHistory": [
    {
      "state": "planned",
      "timestamp": "2025-10-19T20:30:00Z",
      "triggeredBy": "/feature command completed",
      "notes": "Feature planning completed - user stories created"
    },
    {
      "state": "in_progress",
      "timestamp": "2025-10-19T21:00:00Z",
      "triggeredBy": "/implement command started",
      "notes": "Implementation started - executing first story"
    }
  ]
}
```

#### State Validation

Commands validate state transitions before execution:

```
/implement command:
  1. Read current feature state
  2. Check if planned → in_progress transition allowed
  3. If valid: Update state, append stateHistory
  4. If invalid: Display error, suggest valid transitions
  5. Proceed with implementation
```

### Feature Log Schema

Central registry at `docs/features/feature-log.json`:

```json
{
  "features": [
    {
      "featureID": "5",
      "title": "Architecture System Improvements",
      "createdAt": "2025-10-19T20:30:00Z",
      "userStoriesCreated": "2025-10-19T20:30:00Z",
      "userStoriesImplemented": "2025-10-19T23:00:00Z",
      "isSummarised": false,
      "summarisedAt": null,
      "state": "deployed",
      "stateHistory": [
        {
          "state": "planned",
          "timestamp": "2025-10-19T20:30:00Z",
          "triggeredBy": "/feature command completed",
          "notes": "Feature planning completed"
        },
        {
          "state": "in_progress",
          "timestamp": "2025-10-19T21:00:00Z",
          "triggeredBy": "/implement command started",
          "notes": "Implementation started"
        },
        {
          "state": "deployed",
          "timestamp": "2025-10-19T23:00:00Z",
          "triggeredBy": "/implement command completed",
          "notes": "All stories finished and deployed"
        }
      ],
      "actions": []
    }
  ]
}
```

### Implementation Log Schema

Detailed record at `docs/features/{id}/implementation-log.json`:

```json
[
  {
    "storyNumber": 1,
    "storyTitle": "Research Parallel Execution Patterns",
    "agent": "meta-developer",
    "status": "completed",
    "completedAt": "2025-10-19T21:15:00Z",
    "filesModified": ["docs/research/parallel-execution.md"],
    "filesCreated": ["docs/research/parallel-execution.md"],
    "actions": ["Created research document", "Analyzed 3 approaches"],
    "toolsUsed": ["Write", "WebSearch"],
    "issuesEncountered": [],
    "notes": "Recommended Task tool for parallel agent launching"
  }
]
```

---

## Helper System

Helpers provide reusable validation, templates, and utilities in `.claude/helpers/*.md`:

### Validation Helpers

#### atomicity-validation.md

**Purpose**: Validate user stories for atomicity violations

**Validation Dimensions**:
1. **Title Complexity**: Checks for "and", "or", multiple verbs, scope keywords
2. **Acceptance Criteria Count**: Limits to 3-4 criteria per story
3. **File Impact Estimation**: Estimates files touched based on CRUD operations
4. **Time Estimation**: Estimates days based on file count × complexity
5. **Technology References**: Scans for frameworks, libraries, tools

**Scoring**: 0-100 scale composite score

**Classification**:
- EXCELLENT (85-100): Ready to implement
- GOOD (70-84): Acceptable atomicity
- NEEDS_REVIEW (50-69): Consider splitting
- MUST_SPLIT (0-49): Too complex, must split

**Integration**: Product owner runs validation on all stories, iterates until all score >=70

#### pre-flight-validation.md

**Purpose**: Pre-execution validation for commands

**Checks**:
- Git repository exists (.git/ directory)
- Required directories exist (.claude/agents/, docs/features/)
- JSON files valid syntax
- Git working tree status (warn if uncommitted changes)
- Feature/bug dependencies satisfied

**Error Codes**: Standardized codes with remediation steps

#### state-validation.md

**Purpose**: Validate feature state transitions

**Validation**:
- Check current state
- Verify transition allowed (automatic or manual)
- Prevent invalid transitions
- Suggest valid transitions if invalid

#### file-operations-validation.md

**Purpose**: Validate file paths, data structure before writes

**Checks**:
- File paths exist and accessible
- Data structure matches expected schema
- JSON syntax valid before writing
- Git status clean before commits

### Template Helpers

#### story-templates.md

**Purpose**: Reusable templates for common story patterns

**Templates Available**:
- Create/Add Operations (Create New Entity, Initialize Component)
- Read/Display Operations (Display List, Display Details)
- Update/Edit Operations (Update Entity)
- Delete/Remove Operations (Delete Entity)
- Authentication (Login, Registration, Logout, Password Reset)
- API Endpoint (Create API Endpoint)
- Configuration (Configure Environment Settings)
- UI Component (Create UI Component)
- Service Layer (Create Service Layer)
- Design (Design UI Feature)

**Template Structure**:
```markdown
### Template: Create New {Entity}

**Title Format**: Create New {Entity}

**Description Template**:
Enable users to create new {entity} with required {attributes}.
The system should validate {validation requirements} and persist
{entity} for future retrieval.

**Acceptance Criteria**:
- Users can input all required {entity} attributes
- System validates {validation rules} before creation
- Successfully created {entity} is persisted and retrievable
- Clear feedback provided on creation success or validation errors

**Atomicity Score**: 97/100 (EXCELLENT)
**Estimated Files**: 2-3
**Estimated Time**: 1 day
```

**Usage**: Product owner selects template, customizes placeholders, adjusts criteria

### State Management Helpers

#### state-transition-system.md

**Purpose**: Define state transition logic and validation rules

**Content**:
- State definitions and entry conditions
- Allowed automatic transitions
- Allowed manual override transitions
- Invalid transitions
- State history format
- Backward compatibility migration

#### checkpoint-system.md

**Purpose**: Define checkpoint creation and rollback mechanisms

**Content**:
- Checkpoint storage structure
- Files to checkpoint per operation
- Checkpoint metadata schema
- Rollback workflow and preview
- Safety checks and validation
- Retention policy

### Error Handling Helpers

#### command-error-handling.md

**Purpose**: Standardized error codes, categories, message formats

**Error Categories**: ENV, FS, DEP, INPUT, STATE, DATA, GIT

**Message Format**: Error description, check status, remediation steps

#### error-code-mapping.md

**Purpose**: Map validation errors to error codes for consistent reporting

### Metrics and Tracking

#### metrics-tracker.md

**Purpose**: Define metrics collection and reporting

**Metrics**:
- Story completion time (by agent, by phase)
- Feature implementation velocity
- Atomicity scores over time
- Context loading time (caching effectiveness)
- Error rates and recovery times

---

## Integration Patterns

### Command-Agent Integration

```
Command (Orchestration)
  │
  ├─→ Pre-flight Validation (helpers)
  │
  ├─→ Create Checkpoint (helpers)
  │
  ├─→ Launch Agent (agent definition)
  │     │
  │     ├─→ Load Context (agent-specific + keywords)
  │     │
  │     ├─→ Execute Task (agent workflow)
  │     │
  │     └─→ Return Results
  │
  ├─→ Record Implementation (implementation-log.json)
  │
  ├─→ Update State (feature-log.json + validation)
  │
  └─→ Report (standardized output)
```

### Validation Integration

```
Product Owner Agent
  │
  ├─→ Generate Initial Stories
  │
  ├─→ Run Atomicity Validation (helpers/atomicity-validation.md)
  │     │
  │     ├─→ Score: Title Complexity
  │     ├─→ Score: Criteria Count
  │     ├─→ Score: File Impact
  │     ├─→ Score: Time Estimation
  │     └─→ Score: Technology References
  │     │
  │     └─→ Composite Score: 0-100
  │
  ├─→ Identify Stories to Refine (score < 70)
  │
  ├─→ Split/Refine Stories
  │
  ├─→ Re-validate (iterate until all >= 70)
  │
  └─→ Report (include validation summary)
```

### Context Caching Integration

```
/implement Command
  │
  ├─→ Parse Execution Order
  │
  ├─→ For Each Phase:
        │
        ├─→ Identify Pending Stories
        │
        ├─→ Analyze Context Requirements (once per phase)
        │     │
        │     ├─→ Collect agent types
        │     ├─→ Scan story keywords
        │     └─→ Build context file list
        │
        ├─→ Load All Context Files (once)
        │     │
        │     └─→ Cache in memory
        │
        ├─→ For Each Pending Story:
        │     │
        │     ├─→ Retrieve Cached Context
        │     │
        │     ├─→ Launch Agent (no re-reading files)
        │     │
        │     └─→ Record Implementation
        │
        └─→ Clear Cache (after phase completes)
```

### State Transition Integration

```
Command Execution
  │
  ├─→ Read Current State (feature-log.json)
  │
  ├─→ Validate Transition (helpers/state-validation.md)
  │     │
  │     ├─→ Check current state
  │     ├─→ Check if transition allowed
  │     ├─→ Return validation result
  │     │
  │     └─→ If invalid: Error + allowed transitions
  │
  ├─→ Execute Command Operations
  │
  ├─→ Update State (feature-log.json)
  │     │
  │     ├─→ Set new state
  │     └─→ Append stateHistory entry
  │
  └─→ Commit Changes
```

---

## Data Flow and State Management

### Feature Creation Flow

```
User: /feature "Build user authentication"
  │
  ├─→ /feature command
  │     │
  │     ├─→ Pre-flight validation
  │     ├─→ Launch product-owner agent
  │     │     │
  │     │     ├─→ Analyze feature request
  │     │     ├─→ Generate user stories
  │     │     ├─→ Run atomicity validation
  │     │     ├─→ Refine stories (iterate until all >= 70)
  │     │     ├─→ Assign agents
  │     │     ├─→ Define execution order
  │     │     └─→ Return: user-stories.md
  │     │
  │     ├─→ Write: docs/features/5/user-stories.md
  │     ├─→ Update: docs/features/feature-log.json
  │     │     └─→ Add feature entry, state: "planned"
  │     │
  │     ├─→ Create git branch: feature/5-build-user-authentication
  │     ├─→ Commit planning files
  │     │
  │     └─→ Auto-launch: /implement feature 5
```

### Implementation Flow

```
/implement feature 5
  │
  ├─→ Pre-flight validation
  ├─→ Create checkpoint
  ├─→ Read: docs/features/5/user-stories.md
  ├─→ Read: docs/features/5/implementation-log.json (if exists)
  ├─→ Identify completed stories
  │
  ├─→ Update state: planned → in_progress
  │
  ├─→ For Each Phase:
  │     │
  │     ├─→ Filter: completed vs pending stories
  │     ├─→ Load context once (phase-level caching)
  │     │
  │     ├─→ For Each Pending Story:
  │     │     │
  │     │     ├─→ Retrieve cached context
  │     │     ├─→ Launch agent (backend-developer, frontend-developer, etc.)
  │     │     │     │
  │     │     │     ├─→ Read story details
  │     │     │     ├─→ Execute implementation
  │     │     │     ├─→ Modify/create files
  │     │     │     └─→ Return: files changed, actions, notes
  │     │     │
  │     │     └─→ Record: implementation-log.json
  │     │           └─→ Append story entry
  │     │
  │     └─→ Clear cache
  │
  ├─→ Update state: in_progress → deployed
  ├─→ Update: feature-log.json
  │     └─→ Set userStoriesImplemented timestamp
  │
  ├─→ Commit implementation
  └─→ Push to remote
```

### Summarization Flow

```
/summarise
  │
  ├─→ Pre-flight validation
  ├─→ Create checkpoint
  ├─→ Read: docs/features/feature-log.json
  ├─→ Filter: unsummarised features (isSummarised: false)
  │
  ├─→ For Each Unsummarised Feature:
  │     │
  │     ├─→ Read: docs/features/{id}/implementation-log.json
  │     ├─→ Read: docs/features/{id}/user-stories.md
  │     │
  │     ├─→ Analyze:
  │     │     ├─→ Completed stories
  │     │     ├─→ Partial/blocked stories
  │     │     ├─→ Files modified
  │     │     ├─→ Technical decisions
  │     │     └─→ Issues encountered
  │     │
  │     └─→ Generate summary
  │           └─→ Append to: docs/features/implementation-log-summary.json
  │
  ├─→ Update state: deployed → summarised
  ├─→ Update: feature-log.json
  │     ├─→ Set isSummarised: true
  │     └─→ Set summarisedAt timestamp
  │
  └─→ Report: context reduction statistics
```

---

## Quality and Validation

### Multi-Layer Validation

#### Layer 1: Pre-Flight Validation (Command Level)

**Timing**: Before any command execution

**Checks**:
- Environment prerequisites (git repo, directories)
- File existence and syntax (JSON validation)
- Dependency satisfaction (features exist, user stories created)
- Git state (branch, uncommitted changes)

**Outcome**: BLOCKING errors stop execution, WARNINGS allow continuation

#### Layer 2: Atomicity Validation (Story Level)

**Timing**: During story creation by product-owner

**Checks**:
- Title complexity (conjunctions, multiple verbs, length)
- Acceptance criteria count (3-4 max)
- File impact estimation (1-5 files ideal)
- Time estimation (1-3 days max)
- Technology references (must be zero)

**Scoring**: Composite 0-100 score, must be >=70

**Outcome**: Stories scored <70 flagged for splitting, iterative refinement until all >=70

#### Layer 3: State Transition Validation (Feature Level)

**Timing**: Before updating feature state

**Checks**:
- Current state valid
- Transition allowed (automatic or manual)
- State history integrity

**Outcome**: Invalid transitions blocked with suggested valid transitions

#### Layer 4: File Operations Validation (Data Level)

**Timing**: Before writing files

**Checks**:
- File paths exist and accessible
- Data structure matches schema
- JSON syntax valid
- Git status appropriate

**Outcome**: Invalid operations prevented, files unchanged

### Quality Metrics

#### Story Quality Metrics

- **Atomicity Score**: 0-100 composite score
- **Average Criteria per Story**: Target 3-4
- **Average Estimated Files**: Target 2-3
- **Average Estimated Time**: Target 1-2 days
- **Technology-Agnostic Compliance**: Target 100%

#### Implementation Quality Metrics

- **Story Completion Rate**: Completed / Total stories
- **Average Completion Time**: Per story, per agent
- **Error Rate**: Stories with issues / Total stories
- **Resume Frequency**: Interrupted implementations / Total
- **Context Cache Hit Rate**: Cached reads / Total reads

#### System Health Metrics

- **Feature Velocity**: Features completed / Time period
- **State Distribution**: Features by state
- **Average Time in State**: Time from planned → deployed
- **Rollback Frequency**: Rollbacks / Total operations
- **Checkpoint Storage**: Total checkpoint size

---

## Extension Points

### Adding New Agents

1. **Create agent definition**: `.claude/agents/{agent-name}.md`
2. **Define sections**: Purpose, Core Expertise, Best Practices, Workflow, Report
3. **Register context directory**: Create `context/{agent-name}/` with best practices
4. **Update product-owner**: Add agent to available agents list
5. **Test with user story**: Assign story to new agent, verify execution

**Example Use Cases**:
- **database-administrator**: Schema migrations, query optimization
- **security-specialist**: Vulnerability assessments, penetration testing
- **qa-specialist**: Test planning, E2E scenarios, quality metrics
- **technical-writer**: User guides, API docs, tutorials

### Adding New Commands

1. **Create command file**: `.claude/commands/{command-name}.md`
2. **Define frontmatter**: description, args (optional), model
3. **Implement sections**: Purpose, Variables, Instructions, Error Handling, Workflow, Report
4. **Add pre-flight validation**: Use helpers/pre-flight-validation.md
5. **Add error handling**: Use helpers/command-error-handling.md error codes
6. **Create checkpoint**: Use helpers/checkpoint-system.md
7. **Update state**: Use helpers/state-validation.md if modifying features
8. **Test workflow**: Execute command, verify all steps, check error cases

**Example Use Cases**:
- **/archive**: Archive completed features, mark as historical
- **/migrate**: Migrate features between projects
- **/export**: Export feature data for external tools
- **/lint**: Validate all system files for integrity

### Adding New Helpers

1. **Create helper file**: `.claude/helpers/{helper-name}.md`
2. **Define purpose**: Clear description of helper's role
3. **Document usage**: How commands integrate helper
4. **Provide examples**: Concrete use cases
5. **Define schema**: If helper introduces data structures
6. **Update commands**: Integrate helper into relevant commands

**Example Use Cases**:
- **dependency-validation.md**: Validate story dependencies before execution
- **context-selection.md**: Smart context selection based on story analysis
- **notification-system.md**: Notify users of important events
- **integration-validation.md**: Validate integration with external systems

### Adding New Validation Rules

1. **Update atomicity-validation.md**: Add new validation dimension
2. **Define scoring**: How new dimension affects composite score
3. **Update product-owner**: Integrate new validation in workflow
4. **Add examples**: Show stories that pass/fail new validation
5. **Test validation**: Run on existing stories, verify scoring

**Example Use Cases**:
- **Complexity estimation**: Static analysis of story complexity
- **Dependency depth**: Check for deep dependency chains
- **Agent availability**: Validate assigned agents exist
- **Resource estimation**: Estimate compute/memory requirements

### Adding New State Transitions

1. **Update state-transition-system.md**: Define new state
2. **Define entry conditions**: When state is entered
3. **Define exit transitions**: Allowed next states
4. **Update feature-log schema**: Add state to allowed values
5. **Update commands**: Implement state transition logic
6. **Update state-validation.md**: Add validation rules

**Example Use Cases**:
- **testing**: Feature in QA testing phase
- **review**: Feature in code review
- **blocked**: Feature blocked by dependency
- **deprecated**: Feature superseded by newer feature

---

## Conclusion

The Architecture System provides a comprehensive, extensible platform for managing development workflows from planning through implementation to summarization. Key strengths include:

1. **Atomicity Enforcement**: Automated validation ensures small, deployable stories
2. **Technology-Agnostic Planning**: Clear separation of WHAT from HOW
3. **Automated Orchestration**: Parallel execution, resume capability, context optimization
4. **Comprehensive State Management**: Full lifecycle tracking with automatic transitions
5. **Multi-Layer Validation**: Quality assurance at every level
6. **Extensibility**: Easy to add agents, commands, helpers, validation rules

The system is designed for long-term maintainability and evolution, with backward compatibility, migration support, and clear extension points.

For more information:
- **README.md**: Quick start guide and project overview
- **AGENT_GUIDE.md**: Creating new specialized agents
- **COMMAND_GUIDE.md**: Creating new slash commands
- **docs/features/**: Feature documentation and implementation logs
- **.claude/agents/**: Agent definitions
- **.claude/commands/**: Command definitions
- **.claude/helpers/**: Validation systems and utilities
