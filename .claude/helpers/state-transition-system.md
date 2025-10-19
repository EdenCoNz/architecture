# Feature State Transition System

## Purpose

This document defines the comprehensive lifecycle state system for features and the automated state transition logic that updates feature states as commands execute. This system coordinates with Story #9 (state tracking extension) to provide automated state management.

## Feature Lifecycle States

Features progress through the following states during their lifecycle:

### 1. planned
**Definition**: Feature has been created and user stories have been planned but implementation has not started.

**Entry Conditions**:
- /feature command completes successfully
- User stories created and written to docs/features/{id}/user-stories.md
- Feature registered in feature-log.json

**Indicators**:
- userStoriesCreated is set (timestamp)
- userStoriesImplemented is null
- state field is "planned"

### 2. in_progress
**Definition**: Feature implementation has started but not all stories are completed yet.

**Entry Conditions**:
- /implement command starts execution
- At least one user story has been executed
- NOT all stories completed yet

**Indicators**:
- userStoriesCreated is set
- userStoriesImplemented is null
- implementation-log.json exists with at least one entry
- state field is "in_progress"

### 3. deployed
**Definition**: All user stories for the feature have been successfully completed and deployed.

**Entry Conditions**:
- /implement command completes successfully
- All user stories in execution order marked as completed
- userStoriesImplemented timestamp set

**Indicators**:
- userStoriesCreated is set
- userStoriesImplemented is set (timestamp)
- All stories in implementation-log.json have status "completed"
- state field is "deployed"

**Note**: The "deployed" state is used instead of "implemented" to align with the existing state system from Story #9.

### 4. summarised
**Definition**: Feature implementation has been analyzed and summarized to reduce context for future agents.

**Entry Conditions**:
- /summarise command processes the feature
- Summary added to implementation-log-summary.json
- isSummarised flag set to true

**Indicators**:
- userStoriesImplemented is set
- isSummarised is true
- summarisedAt is set (timestamp)
- state field is "summarised"

### 5. archived
**Definition**: Feature is complete and has been archived for historical reference only.

**Entry Conditions**:
- Manual state override (exceptional cases)
- Feature is old and no longer actively referenced

**Indicators**:
- All previous lifecycle timestamps set
- state field is "archived"
- archivedAt timestamp set

## State Transition Rules

### Allowed State Transitions

```
planned → in_progress     (when /implement starts)
planned → archived        (manual override only)

in_progress → implemented (when all stories completed)
in_progress → planned     (manual override - rollback scenario)

implemented → summarised  (when /summarise processes feature)
implemented → in_progress (manual override - new stories added)

summarised → archived     (manual state transition)
summarised → implemented  (manual override - re-implementation needed)

archived → implemented    (manual override - unarchive scenario)
```

### Invalid State Transitions (Prevented)

```
planned → implemented     (must go through in_progress)
planned → summarised      (must implement first)
in_progress → summarised  (must complete implementation)
in_progress → archived    (must complete first)
implemented → planned     (backward progression without override)
summarised → planned      (backward progression without override)
summarised → in_progress  (backward progression without override)
archived → any state      (requires explicit unarchive)
```

## State Transition Tracking

### state_history Array

Each state transition is recorded in a `state_history` array in the feature log entry:

```json
{
  "featureID": "5",
  "title": "Architecture System Improvements",
  "state": "in_progress",
  "createdAt": "2025-10-19T20:30:00Z",
  "userStoriesCreated": "2025-10-19T20:30:00Z",
  "userStoriesImplemented": null,
  "isSummarised": false,
  "summarisedAt": null,
  "state_history": [
    {
      "from_state": null,
      "to_state": "planned",
      "transitioned_at": "2025-10-19T20:30:00Z",
      "trigger": "/feature command completed",
      "automatic": true
    },
    {
      "from_state": "planned",
      "to_state": "in_progress",
      "transitioned_at": "2025-10-19T21:00:00Z",
      "trigger": "/implement command started",
      "automatic": true
    }
  ],
  "actions": []
}
```

### State History Entry Format

```json
{
  "from_state": "previous_state | null",
  "to_state": "new_state",
  "transitioned_at": "ISO 8601 timestamp",
  "trigger": "Description of what caused transition",
  "automatic": true | false,
  "notes": "Optional additional context"
}
```

## Backward Compatibility

### Migration Strategy

For existing features without state tracking:

1. **Read feature-log.json**: Load all existing features
2. **Infer current state**: Based on existing fields
   - If userStoriesCreated is null → state: "planned" (edge case, shouldn't happen)
   - If userStoriesImplemented is null → state: "planned"
   - If userStoriesImplemented is set AND isSummarised is false → state: "implemented"
   - If isSummarised is true → state: "summarised"
3. **Add state field**: Set inferred state
4. **Initialize state_history**: Create initial history entry showing inferred state
5. **Preserve all existing fields**: No data loss

### Example Migration

Before migration:
```json
{
  "featureID": "1",
  "title": "Initialize Frontend Web Application",
  "createdAt": "2025-10-15T00:00:00Z",
  "userStoriesCreated": "2025-10-15T00:00:00Z",
  "userStoriesImplemented": "2025-10-15T20:00:00Z",
  "isSummarised": true,
  "summarisedAt": "2025-10-15T20:15:00Z",
  "actions": []
}
```

After migration:
```json
{
  "featureID": "1",
  "title": "Initialize Frontend Web Application",
  "createdAt": "2025-10-15T00:00:00Z",
  "userStoriesCreated": "2025-10-15T00:00:00Z",
  "userStoriesImplemented": "2025-10-15T20:00:00Z",
  "isSummarised": true,
  "summarisedAt": "2025-10-15T20:15:00Z",
  "state": "summarised",
  "state_history": [
    {
      "from_state": null,
      "to_state": "summarised",
      "transitioned_at": "2025-10-15T20:15:00Z",
      "trigger": "Migrated from legacy format - inferred from isSummarised: true",
      "automatic": false,
      "notes": "Initial state inferred during system migration"
    }
  ],
  "actions": []
}
```

## Automatic State Transition Integration

### Command-Specific State Transitions

#### /feature Command

**Location**: .claude/commands/feature.md Step 3 (after creating git branch and committing)

**Transition**: null → planned

**Logic**:
1. Read feature-log.json
2. Find feature entry by featureID (newly created)
3. Add state field: "planned"
4. Add state_history entry:
   ```json
   {
     "from_state": null,
     "to_state": "planned",
     "transitioned_at": "{current ISO timestamp}",
     "trigger": "/feature command completed - user stories created",
     "automatic": true
   }
   ```
5. Write updated feature-log.json

#### /implement Command

**Location 1**: .claude/commands/implement.md Step 5 (when starting first story of feature)

**Transition**: planned → in_progress

**Logic**:
1. Before executing first pending story in Phase 1
2. Read feature-log.json
3. Find feature entry by featureID
4. Check current state:
   - If state is "planned": Transition to "in_progress"
   - If state is already "in_progress": No transition (resume scenario)
   - If state is "implemented": Add state_history note (re-implementation scenario)
5. Add state_history entry:
   ```json
   {
     "from_state": "planned",
     "to_state": "in_progress",
     "transitioned_at": "{current ISO timestamp}",
     "trigger": "/implement command started - executing first story",
     "automatic": true
   }
   ```
6. Write updated feature-log.json

**Location 2**: .claude/commands/implement.md Step 6 (after all stories completed)

**Transition**: in_progress → implemented

**Logic**:
1. After verifying all stories completed
2. Read feature-log.json (already being read for userStoriesImplemented update)
3. Find feature entry by featureID
4. Set state field: "implemented"
5. Add state_history entry:
   ```json
   {
     "from_state": "in_progress",
     "to_state": "implemented",
     "transitioned_at": "{current ISO timestamp}",
     "trigger": "/implement command completed - all stories finished",
     "automatic": true
   }
   ```
6. Write updated feature-log.json (combined with userStoriesImplemented update)

#### /summarise Command

**Location**: .claude/commands/summarise.md Step 5 (after creating summary)

**Transition**: implemented → summarised

**Logic**:
1. After adding summary to implementation-log-summary.json
2. Read feature-log.json (already being read for isSummarised update)
3. Find feature entry by featureID
4. Set state field: "summarised"
5. Add state_history entry:
   ```json
   {
     "from_state": "implemented",
     "to_state": "summarised",
     "transitioned_at": "{current ISO timestamp}",
     "trigger": "/summarise command completed - feature summarized",
     "automatic": true
   }
   ```
6. Write updated feature-log.json (combined with isSummarised and summarisedAt update)

## State Transition Validation

### Validation Function

```
function validateStateTransition(from_state, to_state, is_manual_override):
  # Allowed automatic transitions
  allowed_auto = {
    null: ["planned"],
    "planned": ["in_progress"],
    "in_progress": ["implemented"],
    "implemented": ["summarised"]
  }

  # Allowed manual override transitions
  allowed_manual = {
    "planned": ["archived"],
    "in_progress": ["planned"],
    "implemented": ["in_progress"],
    "summarised": ["archived", "implemented"],
    "archived": ["implemented"]
  }

  # Check if transition is allowed
  if is_manual_override:
    if from_state in allowed_manual and to_state in allowed_manual[from_state]:
      return {"valid": true, "message": "Manual state transition allowed"}
    else:
      return {
        "valid": false,
        "error": f"Invalid manual state transition from '{from_state}' to '{to_state}'",
        "allowed_from_current": allowed_manual.get(from_state, [])
      }
  else:
    if from_state in allowed_auto and to_state in allowed_auto[from_state]:
      return {"valid": true, "message": "Automatic state transition allowed"}
    else:
      return {
        "valid": false,
        "error": f"Invalid automatic state transition from '{from_state}' to '{to_state}'",
        "allowed_from_current": allowed_auto.get(from_state, []),
        "note": "Use manual override for non-standard transitions"
      }
```

### Error Message Format

When invalid transition detected:

```
Error: Invalid state transition

Current state: {from_state}
Requested state: {to_state}
Transition type: {automatic | manual}

This state transition is not allowed in the normal feature lifecycle.

Allowed transitions from '{from_state}':
  Automatic: {list of allowed automatic transitions}
  Manual: {list of allowed manual transitions}

Recommendation:
1. Verify the feature is in the expected state
2. Check feature-log.json for current state and history
3. Use manual state override if this is an exceptional case
4. Review state transition rules in .claude/helpers/state-transition-system.md
```

## Manual State Override Capability

### Override Command (Future Enhancement)

A dedicated command for manual state transitions:

```bash
/state-override feature {id} {new_state} "{reason}"
```

**Example**:
```bash
/state-override feature 5 archived "Feature superseded by Feature 10"
```

### Override Integration in Existing Commands

For now, manual overrides can be performed by:

1. **Direct JSON edit**: Edit feature-log.json manually
2. **Add state_history entry**: Document the manual override:
   ```json
   {
     "from_state": "implemented",
     "to_state": "in_progress",
     "transitioned_at": "2025-10-20T10:00:00Z",
     "trigger": "Manual override - new stories added to feature",
     "automatic": false,
     "notes": "Added 3 new stories for enhanced validation - re-opening implementation"
   }
   ```
3. **Update state field**: Set new state value
4. **Commit changes**: git commit with clear message explaining override

### Override Use Cases

1. **Re-opening implemented feature**: New stories added, need to re-implement
2. **Archiving incomplete feature**: Feature cancelled or deprioritized
3. **Unarchiving old feature**: Need to update archived feature
4. **Rollback scenario**: Implementation had issues, return to planned state

## State Query Helpers

### Get Current State

```
function getCurrentState(feature_id):
  feature_log = read_json("docs/features/feature-log.json")
  feature = find_by_id(feature_log.features, feature_id)

  if feature.state exists:
    return feature.state
  else:
    # Infer from legacy fields
    if feature.isSummarised:
      return "summarised"
    elif feature.userStoriesImplemented:
      return "implemented"
    else:
      return "planned"
```

### Get State History

```
function getStateHistory(feature_id):
  feature_log = read_json("docs/features/feature-log.json")
  feature = find_by_id(feature_log.features, feature_id)

  if feature.state_history exists:
    return feature.state_history
  else:
    # No history available - legacy entry
    return []
```

### Check If Transition Allowed

```
function isTransitionAllowed(feature_id, to_state, is_manual):
  current_state = getCurrentState(feature_id)
  validation = validateStateTransition(current_state, to_state, is_manual)
  return validation
```

## Integration Testing Checklist

- [ ] Feature creation (/feature) sets state to "planned"
- [ ] Implementation start (/implement first story) transitions planned → in_progress
- [ ] Implementation complete (/implement all stories) transitions in_progress → implemented
- [ ] Summarization (/summarise) transitions implemented → summarised
- [ ] Resume scenario maintains state correctly (in_progress remains in_progress)
- [ ] Re-implementation scenario records state_history note
- [ ] Invalid automatic transitions are prevented with clear errors
- [ ] State history preserves all transitions with timestamps
- [ ] Backward compatibility maintained for legacy features
- [ ] Manual state override capability documented and functional

## Future Enhancements

### State-Based Filtering

Commands could filter features by state:
```bash
/dashboard --state in_progress
/list-features --state implemented
```

### State-Based Metrics

Metrics system could track:
- Average time in each state
- State transition velocity
- Features stuck in states (potential blockers)
- State distribution over time

### State-Based Validation

Pre-flight validation could check state:
- /implement requires state: planned or in_progress
- /summarise requires state: implemented
- Warn if operating on unexpected state

### State Visualization

Dashboard could show state flow:
```
planned (5) → in_progress (3) → implemented (10) → summarised (8) → archived (2)
```

## Version History

- v1.0 (2025-10-19): Initial state transition system design for Story #10
- Coordinated with Story #9 for state tracking extension
