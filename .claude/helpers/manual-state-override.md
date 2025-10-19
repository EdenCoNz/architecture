# Manual Feature State Override Guide

## Purpose

This guide explains how to manually override feature states for exceptional cases where automatic state transitions don't apply. Manual overrides should be used sparingly and only when necessary.

## When to Use Manual Override

Manual state overrides are appropriate in these scenarios:

### 1. Feature Cancellation
- **Scenario**: Feature is no longer needed or has been deprioritized
- **Transition**: planned → archived OR in_progress → archived
- **Reason**: Automatic transitions don't support direct archival from active states

### 2. Re-opening Completed Feature
- **Scenario**: New stories added to a completed feature
- **Transition**: implemented → in_progress
- **Reason**: Feature needs additional implementation work

### 3. Rollback to Planning
- **Scenario**: Implementation started but requirements changed significantly
- **Transition**: in_progress → planned
- **Reason**: Need to redesign and re-plan the feature

### 4. Unarchiving Old Feature
- **Scenario**: Archived feature needs to be reactivated
- **Transition**: archived → implemented OR archived → in_progress
- **Reason**: Feature became relevant again

### 5. State Correction
- **Scenario**: State was incorrectly set due to error or bug
- **Transition**: Any state → correct state
- **Reason**: Fix incorrect state tracking

### 6. Summary Re-generation
- **Scenario**: Need to regenerate summary for a feature
- **Transition**: summarised → implemented
- **Reason**: Summary needs updating or was incorrect

## Manual Override Procedure

### Step 1: Backup Current State

Before making any manual changes:

```bash
# Backup the feature log
cp docs/features/feature-log.json docs/features/feature-log.json.backup

# Record the current timestamp
date -u +"%Y-%m-%dT%H:%M:%SZ"
```

### Step 2: Edit Feature Log

1. Open `docs/features/feature-log.json` in a text editor
2. Find the feature entry by `featureID`
3. Note the current state value
4. Update the `state` field to the new desired state

### Step 3: Add State History Entry

Add a new entry to the `state_history` array documenting the manual override:

```json
{
  "from_state": "{previous_state}",
  "to_state": "{new_state}",
  "transitioned_at": "{current ISO 8601 timestamp}",
  "trigger": "{clear description of why override was needed}",
  "automatic": false,
  "notes": "{additional context about the manual override}"
}
```

**Important**: Set `automatic: false` to clearly mark this as a manual intervention.

### Step 4: Validate JSON Syntax

After editing, validate the JSON is still valid:

```bash
python3 -m json.tool docs/features/feature-log.json > /dev/null && echo "Valid JSON" || echo "Invalid JSON - fix errors"
```

If invalid, fix the syntax errors before proceeding.

### Step 5: Commit the Change

Commit the manual state override with a clear message:

```bash
git add docs/features/feature-log.json
git commit -m "Manual state override: Feature #{id} {from_state} → {to_state}

Reason: {explanation of why override was necessary}

This is a manual state transition to handle {exceptional scenario}.
Previous state: {from_state}
New state: {to_state}
Timestamp: {ISO 8601 timestamp}
"
```

### Step 6: Document in Feature Directory (Optional)

For significant overrides, create a note in the feature directory:

```bash
echo "Manual state override performed on {date}
From: {from_state}
To: {to_state}
Reason: {explanation}
Committed: {git commit hash}
" > docs/features/{id}/state-override-note.txt
```

## Complete Examples

### Example 1: Cancel Planned Feature

**Scenario**: Feature #7 was planned but business priorities changed.

**Manual Override**:
```json
{
  "featureID": "7",
  "title": "Advanced Reporting System",
  "state": "archived",
  "createdAt": "2025-10-18T10:00:00Z",
  "userStoriesCreated": "2025-10-18T10:30:00Z",
  "userStoriesImplemented": null,
  "isSummarised": false,
  "summarisedAt": null,
  "state_history": [
    {
      "from_state": null,
      "to_state": "planned",
      "transitioned_at": "2025-10-18T10:30:00Z",
      "trigger": "/feature command completed - user stories created",
      "automatic": true
    },
    {
      "from_state": "planned",
      "to_state": "archived",
      "transitioned_at": "2025-10-19T14:00:00Z",
      "trigger": "Manual override - feature cancelled due to business priority change",
      "automatic": false,
      "notes": "Feature deprioritized in favor of Feature #8. Stories preserved for future reference."
    }
  ],
  "actions": []
}
```

**Commit Message**:
```
Manual state override: Feature #7 planned → archived

Reason: Feature cancelled due to business priority change

Feature "Advanced Reporting System" has been deprioritized in favor of
Feature #8 (Real-time Analytics). User stories are preserved in
docs/features/7/ for future reference if priorities change again.

This is a manual state transition to archive a planned feature.
Previous state: planned
New state: archived
Timestamp: 2025-10-19T14:00:00Z
```

### Example 2: Re-open Implemented Feature

**Scenario**: Feature #5 was implemented but new stories were added.

**Manual Override**:
```json
{
  "featureID": "5",
  "title": "Architecture System Improvements",
  "state": "in_progress",
  "createdAt": "2025-10-19T20:30:00Z",
  "userStoriesCreated": "2025-10-19T20:30:00Z",
  "userStoriesImplemented": "2025-10-19T23:00:00Z",
  "isSummarised": false,
  "summarisedAt": null,
  "state_history": [
    {
      "from_state": null,
      "to_state": "planned",
      "transitioned_at": "2025-10-19T20:30:00Z",
      "trigger": "/feature command completed - user stories created",
      "automatic": true
    },
    {
      "from_state": "planned",
      "to_state": "in_progress",
      "transitioned_at": "2025-10-19T21:00:00Z",
      "trigger": "/implement command started - executing first story",
      "automatic": true
    },
    {
      "from_state": "in_progress",
      "to_state": "implemented",
      "transitioned_at": "2025-10-19T23:00:00Z",
      "trigger": "/implement command completed - all stories finished",
      "automatic": true
    },
    {
      "from_state": "implemented",
      "to_state": "in_progress",
      "transitioned_at": "2025-10-20T09:00:00Z",
      "trigger": "Manual override - 3 new stories added for enhanced validation",
      "automatic": false,
      "notes": "Added Stories #20-22 for additional validation capabilities. Re-opening feature for implementation."
    }
  ],
  "actions": []
}
```

**Commit Message**:
```
Manual state override: Feature #5 implemented → in_progress

Reason: New stories added for enhanced validation

Feature "Architecture System Improvements" was completed but additional
requirements were identified. Added 3 new stories (#20-22) for enhanced
validation capabilities. Re-opening feature to implement new stories.

This is a manual state transition to re-open a completed feature.
Previous state: implemented
New state: in_progress
Timestamp: 2025-10-20T09:00:00Z

Note: userStoriesImplemented timestamp preserved to track original completion.
```

### Example 3: Correct Erroneous State

**Scenario**: Feature #6 state was incorrectly set to "summarised" but it was never summarized.

**Manual Override**:
```json
{
  "featureID": "6",
  "title": "User Authentication",
  "state": "implemented",
  "createdAt": "2025-10-17T10:00:00Z",
  "userStoriesCreated": "2025-10-17T10:30:00Z",
  "userStoriesImplemented": "2025-10-17T15:00:00Z",
  "isSummarised": false,
  "summarisedAt": null,
  "state_history": [
    {
      "from_state": null,
      "to_state": "planned",
      "transitioned_at": "2025-10-17T10:30:00Z",
      "trigger": "/feature command completed - user stories created",
      "automatic": true
    },
    {
      "from_state": "planned",
      "to_state": "in_progress",
      "transitioned_at": "2025-10-17T11:00:00Z",
      "trigger": "/implement command started - executing first story",
      "automatic": true
    },
    {
      "from_state": "in_progress",
      "to_state": "implemented",
      "transitioned_at": "2025-10-17T15:00:00Z",
      "trigger": "/implement command completed - all stories finished",
      "automatic": true
    },
    {
      "from_state": "implemented",
      "to_state": "summarised",
      "transitioned_at": "2025-10-17T16:00:00Z",
      "trigger": "INCORRECT - state was erroneously set",
      "automatic": false,
      "notes": "This transition was incorrect - feature was never actually summarized"
    },
    {
      "from_state": "summarised",
      "to_state": "implemented",
      "transitioned_at": "2025-10-19T10:00:00Z",
      "trigger": "Manual override - correcting erroneous state",
      "automatic": false,
      "notes": "State was incorrectly set to 'summarised' but feature was never actually summarized. isSummarised flag is false and no entry in implementation-log-summary.json. Correcting state back to 'implemented'."
    }
  ],
  "actions": []
}
```

**Commit Message**:
```
Manual state override: Feature #6 summarised → implemented (correction)

Reason: Correcting erroneous state from previous error

Feature "User Authentication" state was incorrectly set to "summarised"
but the feature was never actually summarized (isSummarised: false, no
entry in implementation-log-summary.json). Correcting state back to
"implemented" to reflect actual status.

This is a manual state transition to fix incorrect state tracking.
Previous state: summarised (incorrect)
Corrected state: implemented
Timestamp: 2025-10-19T10:00:00Z
```

## Allowed Manual Transitions

Reference table of valid manual override transitions:

| From State   | To State     | Use Case |
|--------------|--------------|----------|
| planned      | archived     | Cancel planned feature |
| in_progress  | planned      | Rollback to planning phase |
| in_progress  | archived     | Cancel in-progress feature |
| implemented  | in_progress  | Re-open for new stories |
| summarised   | archived     | Archive old feature |
| summarised   | implemented  | Re-generate summary |
| archived     | implemented  | Unarchive feature |
| any          | any          | State correction (exceptional) |

## Safety Checklist

Before performing manual state override:

- [ ] I have backed up feature-log.json
- [ ] I have a clear reason for the manual override
- [ ] I have verified this cannot be handled by normal command flow
- [ ] I have noted the current state and timestamp
- [ ] I will add a complete state_history entry with automatic: false
- [ ] I will validate JSON syntax after editing
- [ ] I will commit with a clear explanation
- [ ] I will document the reason in commit message and state_history notes

## Troubleshooting

### JSON Syntax Error After Edit

**Problem**: feature-log.json has syntax error after manual edit.

**Solution**:
1. Restore from backup: `cp docs/features/feature-log.json.backup docs/features/feature-log.json`
2. Use a JSON-aware editor (VS Code, vim with syntax highlighting)
3. Validate JSON frequently during editing
4. Check for missing commas, quotes, brackets

### State History Array Not Found

**Problem**: Feature entry doesn't have `state_history` array.

**Solution**:
1. Add `state_history` field as empty array: `"state_history": []`
2. Then add your manual override entry to the array
3. This typically happens with legacy features migrated from old format

### Cannot Determine Current State

**Problem**: Unsure what current state should be.

**Solution**:
1. Check existing fields:
   - If `isSummarised: true` → current state is "summarised"
   - If `userStoriesImplemented` is set AND `isSummarised: false` → current state is "implemented"
   - If `userStoriesCreated` is set AND `userStoriesImplemented` is null → current state could be "planned" or "in_progress"
2. Check implementation-log.json:
   - If implementation log exists with entries → state is "in_progress" or "implemented"
   - If no implementation log → state is "planned"

### Unsure if Manual Override is Needed

**Problem**: Not sure if this situation requires manual override.

**Solution**:
1. Check if normal command flow can handle it:
   - New stories for completed feature → Need manual override (implemented → in_progress)
   - Resume interrupted implementation → No override needed (automatic resume)
   - Cancel planned feature → Need manual override (planned → archived)
2. When in doubt, ask: "Can a command transition this state automatically?"
3. If no, manual override is needed

## Best Practices

### Do's
- ✅ Always backup before manual edits
- ✅ Use clear, descriptive trigger messages
- ✅ Include detailed notes explaining context
- ✅ Commit immediately after override
- ✅ Validate JSON after every edit
- ✅ Document exceptional scenarios
- ✅ Set automatic: false for manual overrides

### Don'ts
- ❌ Don't manually override without documenting reason
- ❌ Don't skip state_history entry
- ❌ Don't use manual override for normal workflow
- ❌ Don't forget to commit changes
- ❌ Don't set automatic: true for manual overrides
- ❌ Don't edit feature-log.json while commands are running

## Future Enhancement: /state-override Command

A dedicated command for manual state transitions is planned for future enhancement:

```bash
/state-override feature {id} {new_state} "{reason}"
```

This command will:
- Validate the transition is allowed as manual override
- Automatically create state_history entry
- Update feature-log.json with proper formatting
- Commit the change with appropriate message
- Handle JSON editing safely

Until implemented, use the manual procedure documented above.

## Questions and Support

If unsure about manual state override:
1. Review allowed transitions table
2. Check if command automation can handle it
3. Consult .claude/helpers/state-transition-system.md
4. Review .claude/helpers/state-validation.md
5. Create backup before proceeding

## Version History

- v1.0 (2025-10-19): Initial manual state override guide for Story #10
