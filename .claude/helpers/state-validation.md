# Feature State Validation Helper

## Purpose

This helper provides validation logic for feature state transitions to ensure features follow the proper lifecycle and prevent invalid state changes.

## Validation Function

### validateStateTransition

Validates whether a state transition is allowed based on current state and transition type (automatic or manual).

**Input Parameters**:
- `from_state`: Current state of the feature (string or null)
- `to_state`: Target state for the transition (string)
- `is_manual_override`: Boolean indicating if this is a manual override (default: false)

**Returns**: Object with validation result
```json
{
  "valid": true/false,
  "message": "Success or error message",
  "allowed_from_current": ["array", "of", "allowed", "states"]
}
```

## Allowed State Transitions

### Automatic Transitions (is_manual_override = false)

These transitions happen automatically when commands complete:

```
null → "planned"           (/feature creates feature)
"planned" → "in_progress"  (/implement starts)
"in_progress" → "deployed"     (/implement completes all stories)
"deployed" → "summarised"      (/summarise processes feature)
```

### Manual Override Transitions (is_manual_override = true)

These transitions require explicit manual intervention:

```
"planned" → "archived"         (Feature cancelled/deprioritized)
"in_progress" → "planned"      (Rollback to planning)
"deployed" → "in_progress"     (New stories added, re-opening)
"summarised" → "archived"      (Archiving old feature)
"summarised" → "deployed"      (Re-implementation needed)
"archived" → "deployed"        (Unarchive scenario)
```

## Validation Logic

```python
def validate_state_transition(from_state, to_state, is_manual_override=False):
    # Allowed automatic transitions
    allowed_auto = {
        None: ["planned"],
        "planned": ["in_progress"],
        "in_progress": ["deployed"],
        "deployed": ["summarised"]
    }

    # Allowed manual override transitions
    allowed_manual = {
        "planned": ["archived"],
        "in_progress": ["planned"],
        "deployed": ["in_progress"],
        "summarised": ["archived", "deployed"],
        "archived": ["deployed"]
    }

    # Check if transition is allowed
    if is_manual_override:
        if from_state in allowed_manual and to_state in allowed_manual[from_state]:
            return {
                "valid": True,
                "message": f"Manual state transition from '{from_state}' to '{to_state}' is allowed"
            }
        else:
            allowed = allowed_manual.get(from_state, [])
            return {
                "valid": False,
                "message": f"Invalid manual state transition from '{from_state}' to '{to_state}'",
                "allowed_from_current": allowed
            }
    else:
        if from_state in allowed_auto and to_state in allowed_auto[from_state]:
            return {
                "valid": True,
                "message": f"Automatic state transition from '{from_state}' to '{to_state}' is allowed"
            }
        else:
            allowed = allowed_auto.get(from_state, [])
            return {
                "valid": False,
                "message": f"Invalid automatic state transition from '{from_state}' to '{to_state}'",
                "allowed_from_current": allowed,
                "note": "Use manual override for non-standard transitions"
            }
```

## Error Message Format

When validation fails in a command, display this error:

```
Error: Invalid state transition

Current state: {from_state}
Requested state: {to_state}
Transition type: {automatic | manual}

This state transition is not allowed in the normal feature lifecycle.

Allowed automatic transitions from '{from_state}':
  - {state1}
  - {state2}

Allowed manual override transitions from '{from_state}':
  - {state1}
  - {state2}

Recommendation:
1. Verify the feature is in the expected state:
   python3 -c "import json; f=json.load(open('docs/features/feature-log.json')); print([x for x in f['features'] if x['featureID']=='{feature_id}'][0]['state'])"
2. Check state history for this feature in feature-log.json
3. Review valid state transitions in .claude/helpers/state-transition-system.md
4. For exceptional cases, use manual state override (edit feature-log.json directly)

The command has been stopped to prevent invalid state transition.
```

## Integration in Commands

### /feature Command (Step 3, Sub-step 6)

Before transitioning to "planned":

```markdown
1. Get current state (should be null for new feature)
2. Validate transition: validateStateTransition(null, "planned", false)
3. If not valid:
   - Display error message
   - Stop execution
4. If valid:
   - Proceed with state transition
```

### /implement Command (Step 4, Sub-step 3)

Before transitioning to "in_progress":

```markdown
1. Read feature-log.json and get current state
2. Validate transition:
   - If state is "planned": validateStateTransition("planned", "in_progress", false)
   - If state is null (legacy): validateStateTransition(null, "in_progress", false) - allowed as migration
   - If state is "in_progress": Skip validation (resume scenario, no transition)
   - If state is "implemented": Skip validation (re-implementation scenario, history note only)
3. If validation fails:
   - Display error message
   - Stop execution
4. If valid or skip:
   - Proceed with state transition or history note
```

Before transitioning to "implemented" (Step 6):

```markdown
1. Read feature-log.json and get current state
2. Validate transition: validateStateTransition(current_state, "implemented", false)
3. If not valid:
   - Display error message
   - Stop execution (do not commit implementation)
4. If valid:
   - Proceed with state transition
```

### /summarise Command (Step 5)

Before transitioning to "summarised":

```markdown
1. Read feature-log.json and get current state for each feature
2. For each feature being summarised:
   - Validate transition: validateStateTransition(current_state, "summarised", false)
   - If not valid:
     - Display warning for this specific feature
     - Skip this feature (do not summarise)
     - Continue with other features
   - If valid:
     - Proceed with state transition for this feature
3. Report any features skipped due to invalid state
```

## Special Cases

### Legacy Features Without State Field

When encountering a feature without a `state` field:

1. Infer the current state based on existing fields:
   ```python
   if feature.get("isSummarised"):
       current_state = "summarised"
   elif feature.get("userStoriesImplemented"):
       current_state = "implemented"
   else:
       current_state = "planned"
   ```

2. Allow transitions from inferred state
3. Initialize `state` and `state_history` fields during first transition

### Resume Scenarios (No Transition)

When /implement resumes an in_progress feature:
- No state transition occurs ("in_progress" → "in_progress")
- Skip validation since state isn't changing
- Add history note documenting the resume

### Re-implementation Scenarios (No Transition)

When /implement re-runs on an implemented feature:
- No state transition occurs ("implemented" → "implemented")
- Skip validation since state isn't changing
- Add history note documenting the re-run

## Validation Testing

### Test Cases

1. **Valid automatic transition**:
   - from_state: "planned", to_state: "in_progress", manual: false
   - Expected: valid = true

2. **Invalid automatic transition**:
   - from_state: "planned", to_state: "implemented", manual: false
   - Expected: valid = false, allowed = ["in_progress"]

3. **Valid manual override**:
   - from_state: "implemented", to_state: "in_progress", manual: true
   - Expected: valid = true

4. **Invalid manual override**:
   - from_state: "summarised", to_state: "planned", manual: true
   - Expected: valid = false, allowed = ["archived", "implemented"]

5. **Legacy feature (null state)**:
   - from_state: null, to_state: "planned", manual: false
   - Expected: valid = true

### Manual Testing Procedure

1. Create test feature with /feature command
2. Verify state is "planned" in feature-log.json
3. Try to manually set state to "implemented" (should be rejected by validation when /implement runs)
4. Start /implement to transition to "in_progress"
5. Complete /implement to transition to "implemented"
6. Run /summarise to transition to "summarised"
7. Check state_history shows all transitions

## Quick Reference

### Automatic Transition Rules
- New feature → planned
- Start implementation → in_progress
- Complete implementation → implemented
- Summarize feature → summarised

### When Validation Fails
1. Check current state in feature-log.json
2. Review state_history for transition history
3. Verify command is appropriate for current state
4. Use manual override only for exceptional cases

### Bypass Validation (Manual Override)
1. Edit feature-log.json directly
2. Update state field
3. Add state_history entry with automatic: false
4. Commit changes with clear explanation

## Version History

- v1.0 (2025-10-19): Initial state validation helper for Story #10
