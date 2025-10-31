# Feature 18: Command Logging Updates

**Created**: 2025-10-31
**Status**: Planning
**Dependencies**: Feature 17 (Logging Guidelines & Standards)

## Overview

Update the /implement command to enforce new logging standards and reduce verbosity in implementation logs by 50-65%. This feature shifts the logging paradigm from "log every action" to "log outcomes and decisions," referencing the comprehensive logging guidelines created in Feature 17.

## Business Value

- Immediate 50-65% reduction in new implementation log sizes
- Faster agent execution due to reduced logging overhead
- Improved log readability and maintainability
- Consistent logging approach across all future implementations
- Foundation for hierarchical log storage improvements

## User Stories

---

### Story 18.1: Update Logging Instructions in Implement Command

**As a** developer agent executing user stories
**I want** the /implement command to provide outcome-focused logging instructions
**So that** I create concise, valuable implementation logs instead of verbose process logs

**Description**:
The /implement command currently instructs agents to "record all actions taken" which leads to excessive verbosity. Update the command prompt to reference the new logging guidelines and emphasize outcome-focused logging (what was accomplished) over process logging (how it was done).

**Acceptance Criteria**:
- When an agent receives implementation instructions, the prompt should reference docs/guides/logging-guidelines.md
- When instructing agents on logging, the command should specify "log outcomes and decisions" rather than "log all actions"
- When agents complete work, they should be directed to the Quick Decision Matrix for determining what to log
- When agents write logs, they should distinguish between Essential (always log), Contextual (log if valuable), and Optional (generally skip) actions

**Agent**: meta-developer

---

### Story 18.2: Remove Verbose Action Logging Requirements

**As a** developer agent implementing features
**I want** clear guidance that routine operations don't need logging
**So that** I avoid cluttering logs with low-value entries about reading files or checking status

**Description**:
The current /implement command implies that all tool usage (Read, Edit, Bash) should be logged. Update the instructions to explicitly state that routine operations like reading files, checking status, or navigating code should NOT be logged unless they lead to discoveries or decisions.

**Acceptance Criteria**:
- When the command describes logging requirements, it should explicitly exclude routine Read operations from logging
- When describing what to log, it should state that checking status or validation that passes as expected should be skipped
- When agents perform exploratory searches that find nothing significant, they should not be required to log them
- When agents perform the same action repeatedly, only the outcome should be logged, not each individual repetition

**Agent**: meta-developer

---

### Story 18.3: Add Reference to Logging Guidelines

**As a** developer agent starting implementation work
**I want** a direct reference to the logging guidelines document
**So that** I can quickly understand logging standards without guessing

**Description**:
Add a prominent reference to the logging guidelines document (docs/guides/logging-guidelines.md) in the /implement command instructions. This should be placed early in the workflow so agents know the guidelines exist and where to find them.

**Acceptance Criteria**:
- When agents read the /implement command instructions, they should see a reference to docs/guides/logging-guidelines.md within the first few sections
- When the reference is provided, it should include a brief description of what the guidelines cover
- When agents are unsure about logging decisions, they should be reminded they can consult the guidelines
- When both FEATURE_MODE and FIX_MODE instructions are given, both should reference the logging guidelines

**Agent**: meta-developer

---

### Story 18.4: Update Implementation Log Format Instructions

**As a** developer agent recording work in implementation logs
**I want** clear structure for what an implementation log entry should contain
**So that** I create consistent, valuable log entries across all stories

**Description**:
Update the implementation log format instructions to align with the new logging guidelines. The format should emphasize recording outcomes (files changed, decisions made, issues resolved) rather than processes (individual tool calls, step-by-step actions).

**Acceptance Criteria**:
- When describing log entry structure, it should require story number, title, and timestamp
- When listing what to include, it should emphasize files created/modified/deleted as Essential logging
- When describing actions, it should focus on decisions made and issues encountered/resolved rather than individual tool calls
- When the status field is described, it should clearly define completed/partial/blocked states

**Agent**: meta-developer

---

### Story 18.5: Add Examples of Good vs Bad Logging

**As a** developer agent learning the new logging standards
**I want** concrete examples of appropriate vs inappropriate logging
**So that** I can quickly internalize what makes a good log entry

**Description**:
Include 2-3 examples in the /implement command showing the difference between verbose process logging (bad) and concise outcome logging (good). These examples should be brief and directly applicable to common implementation scenarios.

**Acceptance Criteria**:
- When the command provides examples, it should show at least one "bad" example of over-logging routine actions
- When good examples are shown, they should demonstrate logging file changes and decisions without logging every read/search
- When examples are provided, they should be realistic scenarios agents commonly encounter
- When comparing good vs bad, the difference in value and verbosity should be immediately obvious

**Agent**: meta-developer

---

### Story 18.6: Update Feature Mode Logging Instructions

**As a** developer agent implementing a new feature
**I want** specific instructions for logging feature implementation work
**So that** I create feature logs that focus on what was built and key decisions

**Description**:
Update the FEATURE_MODE section of the /implement command to incorporate the new logging guidelines. Feature implementations tend to be more exploratory and involve more decisions, so the instructions should guide agents to log discoveries and architectural choices while skipping routine operations.

**Acceptance Criteria**:
- When FEATURE_MODE instructions are provided, they should reference the logging guidelines
- When describing what to log, they should emphasize configuration changes, dependency additions, and architectural decisions
- When agents create new files, they should be instructed to log what was created and why, not the process of creation
- When agents encounter and resolve issues, they should log the issue and solution, not the debugging process

**Agent**: meta-developer

---

### Story 18.7: Update Fix Mode Logging Instructions

**As a** developer agent fixing a bug
**I want** specific instructions for logging bug fix work
**So that** I create fix logs that focus on root cause, solution, and verification

**Description**:
Update the FIX_MODE section of the /implement command to incorporate the new logging guidelines. Bug fixes require logging the root cause investigation and solution, but should skip the trial-and-error debugging process unless it reveals important insights.

**Acceptance Criteria**:
- When FIX_MODE instructions are provided, they should reference the logging guidelines
- When describing what to log, they should emphasize root cause findings and the implemented solution
- When agents try multiple approaches, only the successful approach should be logged unless failed attempts provide valuable insights
- When verification passes as expected, agents should not be required to log every validation step

**Agent**: meta-developer

---

### Story 18.8: Add Logging Decision Flowchart Reference

**As a** developer agent deciding whether to log an action
**I want** a quick decision framework to use during implementation
**So that** I can make fast, consistent logging decisions without interrupting my workflow

**Description**:
Add a reference to the Quick Decision Matrix from the logging guidelines, or include a condensed version directly in the /implement command. This should help agents make 3-5 second decisions about whether to log an action.

**Acceptance Criteria**:
- When agents need to decide whether to log something, they should see a quick reference decision framework
- When the framework is presented, it should cover the most common scenarios (file changes, discoveries, routine operations)
- When agents are unsure, the framework should default to "when in doubt, ask: did this CHANGE something or DISCOVER something?"
- When routine operations are performed, the framework should clearly indicate these should be skipped

**Agent**: meta-developer

---

### Story 18.9: Update Step 4 Context Passing

**As a** developer agent receiving story context from the /implement command
**I want** logging instructions to be concise and clear in the story handoff
**So that** I understand logging expectations without excessive documentation

**Description**:
The "Step 4: Pass Story Context to Agents" section currently has lengthy logging instructions. Simplify this section to provide a concise reminder that references the full guidelines, rather than repeating all logging rules inline.

**Acceptance Criteria**:
- When story context is passed to agents, logging instructions should be no more than 5-7 bullet points
- When the instructions reference logging, they should point to the guidelines document for full details
- When listing what to log, it should use summary language like "file changes, configuration updates, and key decisions"
- When both FEATURE_MODE and FIX_MODE contexts are defined, they should have consistent logging instruction formatting

**Agent**: meta-developer

---

### Story 18.10: Validate Updated Command Produces Concise Logs

**As a** system architect
**I want** to verify that the updated /implement command leads to more concise logs
**So that** the changes achieve the 50-65% reduction goal

**Description**:
Create a brief validation plan or checklist that can be used to verify the updated command achieves the desired reduction in log verbosity. This should include comparing the length of logs produced before and after the update, and checking that logs still contain all essential information.

**Acceptance Criteria**:
- When the validation plan is created, it should define how to measure log verbosity (e.g., line count, entry count)
- When comparing before/after, it should identify what should be present in new logs and what should be absent
- When essential information is checked, it should verify file changes, decisions, and issue resolutions are still captured
- When optional information is checked, it should verify routine operations and repetitive actions are omitted

**Agent**: meta-developer

---

## Execution Order

All stories are assigned to the **meta-developer** agent and should be executed sequentially to ensure coherent updates to the /implement command:

### Phase 1: Sequential (Stories 18.1-18.3) - Foundation
1. Story 18.1: Update Logging Instructions in Implement Command
2. Story 18.2: Remove Verbose Action Logging Requirements
3. Story 18.3: Add Reference to Logging Guidelines

### Phase 2: Sequential (Stories 18.4-18.5) - Structure
4. Story 18.4: Update Implementation Log Format Instructions
5. Story 18.5: Add Examples of Good vs Bad Logging

### Phase 3: Sequential (Stories 18.6-18.7) - Mode-Specific Updates
6. Story 18.6: Update Feature Mode Logging Instructions
7. Story 18.7: Update Fix Mode Logging Instructions

### Phase 4: Sequential (Stories 18.8-18.10) - Refinement
8. Story 18.8: Add Logging Decision Flowchart Reference
9. Story 18.9: Update Step 4 Context Passing
10. Story 18.10: Validate Updated Command Produces Concise Logs

**Total Phases**: 4
**Parallel Phases**: 0
**Sequential Phases**: 4

---

## Notes

### Implementation Approach
- All changes are to a single file (.claude/commands/implement.md)
- Changes should maintain backward compatibility with existing features
- The updated command should work seamlessly with Feature 17's logging guidelines
- No schema changes are required for feature-log.json (already supports summary/detail separation)

### Migration Strategy
- Existing logs do NOT need to be updated (changes apply to future implementations only)
- Agents that have already internalized verbose logging patterns will automatically adapt to new instructions
- First few features after this update should be monitored to ensure agents follow new guidelines

### Success Metrics
- New implementation logs should average 50-65% fewer lines than equivalent logs pre-update
- Essential information (file changes, decisions, issues) should remain present in all logs
- Agent execution time should decrease due to reduced logging overhead
- Log readability scores (subjective assessment) should improve

### Dependencies
- Feature 17 (Logging Guidelines & Standards) must be merged to main branch
- docs/guides/logging-guidelines.md must be accessible at that path
- All agents should have updated prompts referencing logging guidelines (completed in Feature 17)

---

## Story Refinement Summary

- **Initial stories created**: 10
- **Stories after atomicity refinement**: 10
- **Stories split**: 0 (all stories were atomic from the start)
- **Average acceptance criteria per story**: 4.0

All stories meet atomicity requirements:
- Each delivers ONE complete capability (updating a specific section of the command)
- Each can be completed in < 1 day
- Each has 4 acceptance criteria
- No compound titles or multiple verbs

---

## Story Quality Validation

- All stories are implementation-agnostic
- All stories focus on WHAT (update instructions), not HOW (technical implementation)
- All acceptance criteria describe what users see/experience in the command output
- No technical implementation details present
- Stories work regardless of how the meta-developer agent chooses to implement them

---

## Self-Verification Checklist

### Generic & Implementation-Agnostic
- [x] NO frameworks, libraries, or technologies mentioned
- [x] NO architecture patterns or code structure
- [x] Story works with ANY technology stack

### User-Focused
- [x] Title describes user capability
- [x] Description explains WHAT users need
- [x] Uses domain language, not technical jargon

### Acceptance Criteria
- [x] All criteria describe what users SEE, DO, or EXPERIENCE
- [x] Uses "Given... When... Then..." patterns (in "When... then..." format)
- [x] NO technical validation details

### Atomic
- [x] Delivers ONE complete capability
- [x] Can be completed in < 1 day
- [x] Has 4 criteria per story
- [x] Title doesn't contain "and"

### Red Flags - None Present
- Framework/library mentions
- "API", "endpoint", "database", "cache", "middleware"
- Code structure descriptions
- Technical jargon
- Tech stack-specific requirements

**Final Verification**: "Could a developer implement this using a completely different approach?" **YES** - All stories describe desired outcomes in the command's instructions, not how to technically achieve them.
