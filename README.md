# Architecture Development System

A sophisticated development automation system powered by specialized AI agents, slash commands, and workflow orchestration. This system transforms feature requests into atomic user stories and coordinates implementation across multiple specialized agents, enabling efficient, consistent, and high-quality software development.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Core Concepts](#core-concepts)
- [Available Commands](#available-commands)
- [Agent Ecosystem](#agent-ecosystem)
- [Development Workflow](#development-workflow)
- [Feature Lifecycle](#feature-lifecycle)
- [Contributing](#contributing)
- [Documentation](#documentation)

## Overview

### What is This System?

The Architecture Development System is an intelligent development automation platform that:

- **Breaks down complex features** into atomic, independently deployable user stories
- **Coordinates specialized AI agents** (backend, frontend, DevOps, UI/UX, etc.) to implement features
- **Enforces best practices** through automated validation, atomicity checks, and quality gates
- **Manages the complete feature lifecycle** from planning through deployment and summarization
- **Provides comprehensive tracking** via feature logs, implementation logs, and metrics

### Why Use This System?

**For Teams:**
- Consistent development patterns across all features
- Clear separation of concerns with specialized agents
- Automated quality checks and validation
- Comprehensive audit trail of all changes
- Reduced cognitive load through structured workflows

**For Developers:**
- Focus on implementation, not process management
- Clear, atomic user stories with testable acceptance criteria
- Automated orchestration of complex multi-step workflows
- Resume capability for interrupted work
- Built-in error handling and recovery

**For Product Owners:**
- Technology-agnostic user stories that focus on business value
- Automated atomicity validation ensures stories are implementable
- Clear execution order with parallel and sequential phases
- Visibility into feature progress and implementation status

## Key Features

### Intelligent Story Decomposition
- Breaks down features into atomic user stories (1-5 files, 1-3 days max)
- Automated atomicity validation with scoring system (0-100 scale)
- Story templates for common patterns (CRUD, auth, API, UI)
- Technology-agnostic language enforced throughout

### Specialized Agent Architecture
- **Product Owner**: Transforms feature requests into user stories
- **Backend Developer**: Implements server-side application code
- **Frontend Developer**: Implements client-side application code
- **DevOps Engineer**: Handles Docker, CI/CD, deployment automation
- **UI/UX Designer**: Creates design specifications and component specs
- **Meta-Developer**: Improves the development system itself
- **Research Specialist**: Evaluates technologies and best practices

### Workflow Automation
- Parallel execution for independent stories
- Sequential execution for dependent stories
- Context caching optimization (loads shared context once per phase)
- Resume capability (continues from last completed story)
- Pre-flight validation checks before execution
- Comprehensive error handling with recovery suggestions

### Quality & Validation
- Atomicity validation (title complexity, criteria count, file impact, time estimation)
- Technology-agnostic compliance checking
- Pre-flight validation for all commands
- Git status verification before destructive operations
- JSON schema validation for configuration files
- File operations validation layer

### Feature Lifecycle Management
- State tracking: planned → in_progress → deployed → summarised → archived
- Automated state transitions based on command completion
- State history with timestamps and audit trail
- Feature dashboard for at-a-glance status
- Metrics tracking for velocity and performance

### Developer Experience
- Slash commands for common operations (/feature, /implement, /fix, /commit)
- Clear error messages with remediation steps
- Checkpoint and rollback capabilities
- Implementation logs with detailed audit trail
- Performance metrics and optimization tracking

## Quick Start

### Prerequisites

- Git repository initialized
- Python 3.x (for JSON validation)
- Access to Claude AI (Claude Code CLI)

### Installation

1. Clone or initialize your project with the architecture system:

```bash
git clone <your-repo>
cd <your-repo>
```

2. Verify the architecture system structure exists:

```bash
ls -la .claude/
# Should show:
# .claude/agents/        - Specialized agent definitions
# .claude/commands/      - Slash command definitions
# .claude/helpers/       - Helper systems and utilities
```

3. Initialize the feature tracking system (if not already present):

```bash
mkdir -p docs/features
echo '{"features": []}' > docs/features/feature-log.json
```

### Your First Feature

1. **Plan a feature** by transforming a request into user stories:

```bash
/feature "Create a user authentication system"
```

This will:
- Generate a unique feature ID
- Create atomic user stories with acceptance criteria
- Validate stories for atomicity and compliance
- Create a git branch (e.g., `feature/5-user-authentication-system`)
- Commit planning files
- Automatically start implementation if all agents are available

2. **Monitor progress** with the dashboard:

```bash
/dashboard
```

3. **Review implementation** in the logs:

```bash
cat docs/features/5/implementation-log.json
```

4. **Create a pull request** when ready:

```bash
gh pr create --title "Feature #5: User Authentication System" --body "..."
```

### Basic Usage Examples

**Fix a bug from GitHub issue:**
```bash
/fix gha
# Analyzes GitHub Actions failures and creates user stories
```

**Implement a specific feature:**
```bash
/implement feature 5
# Executes all user stories for Feature #5
```

**Commit changes:**
```bash
/commit "Add user authentication endpoints"
# Or with automatic push:
/commit "Add user authentication endpoints" push
```

**View metrics:**
```bash
/metrics
# Shows completion time, velocity, quality metrics
```

**Summarise completed features:**
```bash
/summarise
# Reduces context for future agents
```

## Architecture

### System Design Principles

1. **Separation of Concerns**: Each agent has a single, well-defined responsibility
2. **Atomicity First**: User stories must be small, focused, and independently deployable
3. **Technology Agnostic**: Stories describe WHAT, not HOW (agents decide implementation)
4. **Fail-Safe**: Graceful error handling with clear recovery paths
5. **Observability**: All operations tracked, logged, and auditable
6. **Extensibility**: Easy to add new agents, commands, and workflows

### High-Level Architecture

```
User Request
    ↓
Slash Command (/feature, /implement, /fix)
    ↓
Product Owner Agent
    ├─ Analyzes request
    ├─ Creates atomic user stories
    ├─ Validates atomicity
    └─ Assigns stories to agents
    ↓
Execution Orchestrator
    ├─ Parses execution order
    ├─ Loads context once per phase
    ├─ Launches agents (parallel/sequential)
    └─ Tracks progress in logs
    ↓
Specialized Agents
    ├─ Backend Developer
    ├─ Frontend Developer
    ├─ DevOps Engineer
    ├─ UI/UX Designer
    └─ Meta-Developer
    ↓
Implementation Logs + Git Commits
    ↓
Feature Complete → Deployed State
```

### Directory Structure

```
.claude/
├── agents/                      # Specialized agent definitions
│   ├── product-owner.md        # Feature → user stories transformation
│   ├── backend-developer.md    # Server-side implementation
│   ├── frontend-developer.md   # Client-side implementation
│   ├── devops-engineer.md      # Docker, CI/CD, deployment
│   ├── ui-ux-designer.md       # Design specs and components
│   ├── meta-developer.md       # System improvements
│   └── research-specialist.md  # Technology evaluation
├── commands/                    # Slash command workflows
│   ├── feature.md              # Plan new feature
│   ├── implement.md            # Execute user stories
│   ├── fix.md                  # Fix bugs from GitHub issues
│   ├── commit.md               # Commit with standard format
│   ├── summarise.md            # Reduce context for future agents
│   ├── dashboard.md            # View all features and states
│   ├── metrics.md              # Show performance metrics
│   └── rollback.md             # Revert system changes
└── helpers/                     # Utility systems
    ├── atomicity-validation.md  # Story atomicity scoring
    ├── story-templates.md       # Reusable story patterns
    ├── state-validation.md      # Feature state transitions
    ├── pre-flight-validation.md # Command prerequisites
    ├── command-error-handling.md # Error codes and recovery
    └── metrics-tracker.md       # Performance tracking

docs/
└── features/
    ├── feature-log.json         # All features and their states
    ├── implementation-log-summary.json  # Summarised context
    └── {featureID}/
        ├── user-stories.md      # Atomic user stories
        ├── implementation-log.json  # Detailed implementation log
        └── bugs/
            └── {bugID}/
                ├── user-stories.md
                └── implementation-log.json
```

## Core Concepts

### User Stories

**Atomic User Stories** are the fundamental unit of work in this system. Each story must:

- Touch **1-5 files** ideally
- Take **1-3 days maximum** to complete
- Have **3-4 acceptance criteria** maximum
- Be **independently deployable**
- Use **technology-agnostic language**
- Have **testable acceptance criteria**

Example of a good user story:

```
### Create User Profile

Enable users to create a personal profile by providing their name,
email, and bio. The system validates input, stores the profile,
and provides confirmation of successful creation.

Acceptance Criteria:
- Users can provide name, email, and bio for their profile
- System validates email format and displays clear error messages
- Successfully created profile is persisted and retrievable

Agent: backend-developer
Dependencies: none

**Important**: This story describes WHAT needs to be achieved using
generic, technology-agnostic language. ALL implementation details
(technology choices, frameworks, libraries, tools, file formats,
patterns, architecture) MUST be decided by the assigned development
agent based on project context and best practices.
```

### Agents

**Agents** are specialized AI personas with specific capabilities and responsibilities. Each agent:

- Has a **clear, focused purpose**
- Follows **documented best practices**
- Uses **appropriate context files** for their domain
- Produces **implementation logs** for audit trail
- Works **autonomously** within their scope

### Commands

**Commands** are slash-based workflows that orchestrate complex operations:

- `/feature` - Transform feature request into user stories
- `/implement` - Execute user stories in correct order
- `/fix` - Process GitHub issues and create bug fix stories
- `/commit` - Standardized git commit with co-authoring
- `/dashboard` - View all features and their current states
- `/metrics` - Show performance and quality metrics
- `/summarise` - Reduce context for future agents
- `/rollback` - Revert system changes using checkpoints

### Feature States

Features progress through defined lifecycle states:

1. **planned** - User stories created, ready for implementation
2. **in_progress** - Implementation started, some stories completed
3. **deployed** - All stories completed, feature implemented
4. **summarised** - Implementation details condensed for context efficiency
5. **archived** - Feature archived for long-term storage

State transitions are automatic based on command completion and validated to prevent invalid progressions.

### Execution Order

User stories are organized into **phases** with execution modes:

- **Parallel phases**: All stories execute simultaneously
- **Sequential phases**: Stories execute one-by-one

Example execution order:

```
Phase 1 (Parallel)
- Story #1 (agent: backend-developer)
- Story #2 (agent: frontend-developer)

Phase 2 (Sequential)
- Story #3 (agent: backend-developer) - depends on Story #1

Phase 3 (Parallel)
- Story #4 (agent: devops-engineer)
- Story #5 (agent: ui-ux-designer)
```

## Available Commands

### /feature

Transform a feature request into atomic user stories and automatically start implementation.

```bash
/feature "Add user profile management"
```

**What it does:**
1. Analyzes feature request with available agents
2. Creates atomic, technology-agnostic user stories
3. Validates stories for atomicity (scoring 0-100)
4. Assigns stories to appropriate agents
5. Creates execution order (parallel/sequential phases)
6. Creates git branch (e.g., `feature/5-user-profile-management`)
7. Commits planning files
8. Automatically starts implementation if no missing agents

### /implement

Execute user stories for a feature or bug fix in the correct order.

```bash
/implement feature 5
/implement bug github-issue-37
```

**What it does:**
1. Validates prerequisites (git repo, feature exists, user stories exist)
2. Checks for existing progress (resume capability)
3. Loads context once per phase (optimization)
4. Executes stories respecting parallel/sequential phases
5. Skips already completed stories (resume from checkpoint)
6. Records implementation in logs
7. Updates feature state to "deployed" when complete
8. Creates commit with all changes

**Resume capability:** If interrupted, re-run the same command to continue from the last completed story.

### /fix

Process GitHub issues and create bug fix user stories.

```bash
/fix gha
# Analyzes GitHub Actions failures

/fix {github-issue-number}
# Processes specific GitHub issue
```

**What it does:**
1. Fetches GitHub issue details
2. Analyzes root cause and impact
3. Creates atomic bug fix user stories
4. Validates stories for atomicity
5. Assigns to appropriate agents
6. Automatically starts implementation

### /commit

Create standardized git commit with co-authoring attribution.

```bash
/commit "Add user authentication endpoints"
/commit "Add user authentication endpoints" push
```

**What it does:**
1. Stages all changes
2. Creates commit with standard format
3. Adds co-authoring attribution to Claude
4. Optionally pushes to remote

**Commit message format:**
```
Add user authentication endpoints

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
```

### /dashboard

Display all features with current states and progress indicators.

```bash
/dashboard
```

**What it shows:**
- All features grouped by state
- Creation date, completion date, progress
- Summary statistics (total features, completion rate)
- Features needing attention

### /metrics

Show performance metrics and quality indicators.

```bash
/metrics
```

**What it shows:**
- Story completion time by agent
- Feature velocity (features/week)
- Atomicity score trends
- Quality metrics

### /summarise

Reduce context for future agents by condensing implementation details.

```bash
/summarise
```

**What it does:**
1. Finds features with `isSummarised: false`
2. Extracts key implementation details
3. Creates condensed summary
4. Updates feature log with `isSummarised: true`
5. Reduces token usage for future agent context

### /rollback

Revert system changes using checkpoints.

```bash
/rollback
```

**What it does:**
1. Lists available checkpoints
2. Shows what will be reverted
3. Restores system state from checkpoint
4. Tracks rollback in history

## Agent Ecosystem

### Product Owner

**Purpose**: Transform feature requests and bug reports into atomic user stories

**Key Responsibilities:**
- Analyze requirements and identify scope
- Create technology-agnostic user stories
- Validate stories for atomicity (scoring system)
- Assign stories to appropriate agents
- Create optimal execution order
- Update feature log with metadata

**Output:** User stories file, feature log entry

### Backend Developer

**Purpose**: Implement server-side application code

**Key Responsibilities:**
- Build API endpoints and business logic
- Implement data models and persistence
- Write backend tests (unit, integration)
- Follow TDD methodology
- Use project context (Django, DRF, PostgreSQL)

**Output:** Python code, tests, implementation log

### Frontend Developer

**Purpose**: Implement client-side application code

**Key Responsibilities:**
- Build UI components and pages
- Implement state management and routing
- Write frontend tests (unit, integration, E2E)
- Follow TDD methodology
- Use project context (React, TypeScript, Material-UI)

**Output:** TypeScript/JSX code, tests, implementation log

### DevOps Engineer

**Purpose**: Handle infrastructure, containerization, and CI/CD

**Key Responsibilities:**
- Create and maintain Dockerfiles
- Build docker-compose configurations
- Design CI/CD pipelines (GitHub Actions)
- Implement deployment automation
- Set up security scanning and vulnerability management

**Output:** Docker files, workflows, deployment scripts

### UI/UX Designer

**Purpose**: Create design specifications and component specs

**Key Responsibilities:**
- Design user interfaces and interactions
- Create component specifications
- Define visual design system
- Update design brief with feature designs
- Ensure accessibility compliance

**Output:** Design brief updates, component specs, wireframes

### Meta-Developer

**Purpose**: Improve the development system itself

**Key Responsibilities:**
- Create and modify agents
- Build and enhance slash commands
- Improve workflow automation
- Build validation and quality systems
- Create documentation and guides

**Output:** Agent files, command files, helper files, documentation

### Research Specialist

**Purpose**: Evaluate technologies and research best practices

**Key Responsibilities:**
- Research technology options
- Evaluate frameworks and libraries
- Document best practices
- Create technology comparison reports
- Recommend solutions with rationale

**Output:** Research documents, technology evaluations

## Development Workflow

### Standard Feature Development Flow

1. **Request a Feature**
   ```bash
   /feature "Add user notification system"
   ```

2. **System Plans the Feature**
   - Creates atomic user stories
   - Validates atomicity
   - Assigns to agents
   - Creates git branch
   - Commits planning

3. **Implementation Begins Automatically**
   - Executes stories in order
   - Respects parallel/sequential phases
   - Loads context once per phase
   - Records progress in logs

4. **Monitor Progress**
   ```bash
   /dashboard
   # or check implementation log
   cat docs/features/6/implementation-log.json
   ```

5. **Implementation Completes**
   - All stories executed
   - Feature state → "deployed"
   - Commit created automatically
   - Changes pushed to remote

6. **Create Pull Request**
   ```bash
   gh pr create --title "Feature #6: User Notification System" \
     --body "Implements user notification system with email and in-app notifications"
   ```

7. **After Merge, Summarise**
   ```bash
   /summarise
   # Reduces context for future agents
   ```

### Bug Fix Workflow

1. **GitHub Issue Created**
   - Issue reported: #42 "Login fails with invalid credentials"

2. **Process the Issue**
   ```bash
   /fix 42
   ```

3. **System Creates Fix Stories**
   - Analyzes root cause
   - Creates atomic bug fix stories
   - Assigns to appropriate agent
   - Starts implementation

4. **Implementation & Testing**
   - Bug fix implemented
   - Regression tests added
   - Validation performed

5. **Commit References Issue**
   ```
   Implementation of bug-github-issue-42-Login fails with invalid credentials

   Completed user stories:
   - Story #1: Fix authentication validation
   - Story #2: Add regression tests

   Files modified:
   - backend/authentication/views.py
   - backend/tests/test_authentication.py

   Fixes #42
   ```

### Resume from Interruption

If implementation is interrupted, simply re-run the command:

```bash
/implement feature 6
```

The system will:
- Check implementation log
- Identify completed stories
- Skip completed work
- Resume from next pending story
- Provide clear feedback on what was skipped

## Feature Lifecycle

### State Transitions

```
[New Request]
    ↓
/feature command
    ↓
[planned] ━━━━━━━━━━━━━━━━━→ State created: user stories ready
    ↓
/implement starts
    ↓
[in_progress] ━━━━━━━━━━━→ State updated: implementation started
    ↓
All stories complete
    ↓
[deployed] ━━━━━━━━━━━━━→ State updated: feature implemented
    ↓
/summarise command
    ↓
[summarised] ━━━━━━━━━━→ State updated: context reduced
    ↓
Archive (manual)
    ↓
[archived] ━━━━━━━━━━━→ State updated: long-term storage
```

### State History

Each state transition is recorded with:
- State name
- Timestamp (ISO 8601)
- Triggered by (command or manual)
- Notes (context about the transition)

Example state history:

```json
{
  "state": "deployed",
  "stateHistory": [
    {
      "state": "planned",
      "timestamp": "2025-10-19T10:00:00Z",
      "triggeredBy": "/feature command completed",
      "notes": "Feature planning completed - user stories created"
    },
    {
      "state": "in_progress",
      "timestamp": "2025-10-19T10:05:00Z",
      "triggeredBy": "/implement command started",
      "notes": "Implementation started - executing first story"
    },
    {
      "state": "deployed",
      "timestamp": "2025-10-19T12:30:00Z",
      "triggeredBy": "/implement command completed",
      "notes": "Implementation completed - all stories finished and deployed"
    }
  ]
}
```

## Contributing

### Adding New Agents

Create a new agent file in `.claude/agents/{agent-name}.md`:

```markdown
---
name: agent-name
description: Brief description of agent purpose
model: sonnet
---

# Agent Name

## Purpose
Clear statement of what this agent does

## Core Expertise
- Area 1
- Area 2

## Best Practices
- Practice 1
- Practice 2

## Workflow
1. Step 1
2. Step 2

## Report / Response
Expected output format
```

See `AGENT_GUIDE.md` (if available) for comprehensive instructions.

### Adding New Commands

Create a new command file in `.claude/commands/{command-name}.md`:

```markdown
---
description: Brief description of what this command does
---

## Purpose
Detailed explanation of command purpose

## Variables
- `{{{ input }}}` - Description of input

## Instructions
Step-by-step workflow

## Error Handling
Error codes and recovery

## Workflow
### Step 1: ...
### Step 2: ...

## Report
Expected output format
```

See `COMMAND_GUIDE.md` (if available) for comprehensive instructions.

### Adding New Story Templates

Add templates to `.claude/helpers/story-templates.md`:

```markdown
### Template: {Template Name}

**Title Format:** `{Action} {Entity}`

**Description:**
```
Template description with placeholders
```

**Acceptance Criteria:**
```
- Criterion 1 with {placeholder}
- Criterion 2 with {placeholder}
```

**Usage Example:**
```
Concrete example of the template in use
```
```

### Improving Validation Systems

Validation helpers are in `.claude/helpers/`:

- `atomicity-validation.md` - Story atomicity scoring
- `state-validation.md` - Feature state transitions
- `pre-flight-validation.md` - Command prerequisites
- `file-operations-validation.md` - File operation safety

Improvements to these systems should maintain backward compatibility and include comprehensive testing examples.

## Documentation

### Available Documentation

- `README.md` - This file, project overview and quick start
- `ARCHITECTURE.md` - Detailed system architecture (if available)
- `AGENT_GUIDE.md` - Guide for creating new agents (if available)
- `COMMAND_GUIDE.md` - Guide for creating new commands (if available)

### Context Files

Agent-specific context files are in `context/`:

- `context/backend/` - Django, DRF, PostgreSQL best practices
- `context/frontend/` - React, TypeScript, Material-UI best practices
- `context/devops/` - Docker, CI/CD, deployment guides
- `context/testing/` - Testing frameworks and strategies
- `context/design/` - Design system and UI patterns

### Implementation Logs

Detailed logs for each feature are in `docs/features/{featureID}/`:

- `user-stories.md` - All user stories with execution order
- `implementation-log.json` - Detailed implementation audit trail
- `design/` - Design artifacts and specifications
- `research/` - Research documents and technology evaluations

### Feature Log

The feature log (`docs/features/feature-log.json`) tracks all features with:

- Feature ID and title
- Creation and completion timestamps
- Current state and state history
- Summarisation status
- Custom actions (design updates, etc.)

## Best Practices

### For Product Owners
- Use story templates for common patterns
- Run atomicity validation before finalizing stories
- Keep stories focused and independently deployable
- Use technology-agnostic language throughout
- Leverage execution order for optimal parallelization

### For Developers
- Read the full user story including acceptance criteria
- Follow TDD methodology (tests first)
- Use provided context files for project patterns
- Record detailed implementation logs
- Update design brief for UI changes

### For System Maintainers
- Keep agent definitions focused and clear
- Document all command workflows thoroughly
- Maintain backward compatibility in validation systems
- Test commands with edge cases before deployment
- Update documentation when making system changes

## Troubleshooting

### Common Issues

**Issue: Pre-flight validation fails**
- Check error message for specific validation failure
- Remediate as suggested in error output
- Re-run command after fixing issues

**Issue: Missing agents identified**
- Create the missing agent definitions
- Re-run /feature command to proceed with implementation

**Issue: Implementation interrupted**
- Re-run `/implement feature {id}` to resume
- System automatically skips completed stories

**Issue: Invalid JSON in feature log**
- Use `python3 -m json.tool docs/features/feature-log.json` to validate
- Fix JSON syntax errors
- Ensure proper schema structure

**Issue: Git conflicts**
- Resolve conflicts manually
- Re-run command after resolution

### Getting Help

1. Check command output for specific error codes
2. Review error handling documentation in `.claude/helpers/command-error-handling.md`
3. Check pre-flight validation guide in `.claude/helpers/pre-flight-validation.md`
4. Review implementation logs for detailed audit trail
5. Consult agent guides for agent-specific questions

## License

Specify your license here.

## Acknowledgments

Powered by Claude AI and built with Claude Code CLI.

---

Generated with Claude Code
