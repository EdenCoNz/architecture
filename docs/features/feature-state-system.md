# Feature State Tracking System

## Overview

The feature state tracking system provides comprehensive lifecycle management for features from initial planning through deployment and archival. This system extends the basic timestamp tracking in `feature-log.json` to support a full state machine with transition history.

## State Definitions

### State: `planned`
**Description**: Feature has been identified and user stories are being created or have been created.

**Entry Criteria**:
- Feature request has been analyzed
- Feature ID has been assigned
- Feature directory structure has been created

**Typical Activities**:
- User stories are being written
- Technology stack is being researched
- Design decisions are being documented
- Dependencies are being identified

**Exit Criteria**:
- User stories have been created and reviewed
- Execution order has been defined
- Ready to begin implementation

**Next Valid States**: `in_progress`, `archived`

---

### State: `in_progress`
**Description**: Feature is actively being implemented by development agents.

**Entry Criteria**:
- User stories exist and are ready for implementation
- Implementation has been initiated (via /implement command)
- At least one story is being worked on

**Typical Activities**:
- User stories are being executed
- Code is being written and modified
- Tests are being created
- Documentation is being updated

**Exit Criteria**:
- All user stories have been completed
- Implementation log shows all stories as "completed"
- Feature log has been updated with userStoriesImplemented timestamp

**Next Valid States**: `testing`, `planned` (if blocked), `archived`

---

### State: `testing`
**Description**: Feature implementation is complete and undergoing testing and quality assurance.

**Entry Criteria**:
- All user stories have been implemented
- Implementation has been committed to git
- Feature is ready for validation

**Typical Activities**:
- Unit tests are being run
- Integration tests are being performed
- Manual testing is being conducted
- Bug fixes are being applied

**Exit Criteria**:
- All tests pass successfully
- Quality standards are met
- Feature is ready for code review

**Next Valid States**: `review`, `in_progress` (if issues found requiring rework), `archived`

---

### State: `review`
**Description**: Feature is undergoing code review and technical assessment.

**Entry Criteria**:
- All tests pass
- Code is committed to a feature branch
- Pull request has been created (if applicable)

**Typical Activities**:
- Code review is being conducted
- Design patterns are being validated
- Security review is being performed
- Performance assessment is being done

**Exit Criteria**:
- Code review is approved
- All review feedback has been addressed
- Ready for deployment

**Next Valid States**: `deployed`, `in_progress` (if changes requested), `archived`

---

### State: `deployed`
**Description**: Feature has been deployed to production or released.

**Entry Criteria**:
- Code review is complete and approved
- All quality gates have passed
- Deployment has been executed

**Typical Activities**:
- Feature is live in production
- Monitoring for issues
- Gathering user feedback
- Performance monitoring

**Exit Criteria**:
- Feature is stable in production
- Ready for summarization to reduce context

**Next Valid States**: `summarised`, `in_progress` (if production issues require hotfix), `archived`

---

### State: `summarised`
**Description**: Feature implementation has been summarized for efficient context loading.

**Entry Criteria**:
- Feature has been deployed and is stable
- Implementation logs exist and are complete
- Summarisation process has been run (via /summarise command)

**Typical Activities**:
- Implementation summary exists in implementation-log-summary.json
- Detailed implementation logs can be archived
- Context for future agents is reduced

**Exit Criteria**:
- Summary exists and is comprehensive
- Feature is considered complete

**Next Valid States**: `archived`

---

### State: `archived`
**Description**: Feature is no longer active and has been archived for historical reference.

**Entry Criteria**:
- Feature has been summarised (or explicitly marked for archival)
- Feature is no longer being actively maintained
- Feature may have been superseded or deprecated

**Typical Activities**:
- Feature exists only in historical records
- Documentation is preserved
- Code may be deprecated

**Exit Criteria**:
- N/A (terminal state)

**Next Valid States**: None (terminal state)

---

## State Transition Rules

### Allowed Transitions

The following state transitions are explicitly allowed:

```
planned → in_progress
planned → archived (if feature is cancelled before implementation)

in_progress → testing
in_progress → planned (if blocked and needs re-planning)
in_progress → archived (if feature is cancelled during implementation)

testing → review
testing → in_progress (if tests fail and rework is needed)
testing → archived (if feature is abandoned after testing)

review → deployed
review → in_progress (if review requests changes)
review → archived (if feature is rejected)

deployed → summarised
deployed → in_progress (if production issues require hotfix)
deployed → archived (if feature is rolled back)

summarised → archived
```

### Forbidden Transitions

The following transitions are NOT allowed and should be prevented:

- Any backward transition beyond one state (except to `archived`)
- Direct transition from `planned` to `deployed` (must go through implementation and testing)
- Transition from `archived` to any other state (terminal state)
- Any transition skipping `in_progress` when implementation is required

### Special Transition: `archived`

The `archived` state is special and can be reached from any other state:

- From `planned`: Feature is cancelled before implementation starts
- From `in_progress`: Feature is cancelled during development
- From `testing`: Feature is abandoned after testing reveals issues
- From `review`: Feature is rejected during review
- From `deployed`: Feature is rolled back or deprecated
- From `summarised`: Feature lifecycle is complete

## Feature Log Schema

### Extended Schema

The feature log schema has been extended with the following fields:

```json
{
  "features": [
    {
      "featureID": "string",
      "title": "string",
      "state": "planned|in_progress|testing|review|deployed|summarised|archived",
      "stateHistory": [
        {
          "state": "string",
          "timestamp": "ISO 8601 timestamp",
          "triggeredBy": "command|agent|manual",
          "notes": "optional context about the transition"
        }
      ],
      "createdAt": "ISO 8601 timestamp",
      "userStoriesCreated": "ISO 8601 timestamp or null",
      "userStoriesImplemented": "ISO 8601 timestamp or null",
      "isSummarised": "boolean",
      "summarisedAt": "ISO 8601 timestamp or null",
      "actions": []
    }
  ]
}
```

### Field Definitions

**state** (required)
- Type: enum string
- Valid values: `planned`, `in_progress`, `testing`, `review`, `deployed`, `summarised`, `archived`
- Default: `planned` (when feature is first created)
- Description: Current lifecycle state of the feature

**stateHistory** (required)
- Type: array of state transition objects
- Default: `[{"state": "planned", "timestamp": "{createdAt}", "triggeredBy": "command"}]`
- Description: Complete history of all state transitions for audit and tracking

**State Transition Object**:
- `state`: The state that was entered
- `timestamp`: When the transition occurred (ISO 8601 format)
- `triggeredBy`: What caused the transition (`command`, `agent`, `manual`)
- `notes`: Optional context about why the transition occurred

### Backward Compatibility

**Existing Fields Preserved**:
- `featureID`: No changes
- `title`: No changes
- `createdAt`: No changes
- `userStoriesCreated`: No changes (still used to track when user stories were created)
- `userStoriesImplemented`: No changes (still used to track when implementation completed)
- `isSummarised`: No changes (still used by /summarise command)
- `summarisedAt`: No changes (still used to track when summarization occurred)
- `actions`: No changes

**New Fields**:
- `state`: Added to track current lifecycle state
- `stateHistory`: Added to track complete transition history

**Backward Compatibility Strategy**:
Existing features without the `state` and `stateHistory` fields will have these fields inferred based on existing timestamp fields:

1. If `summarisedAt` is set → state is `summarised`
2. Else if `userStoriesImplemented` is set → state is `deployed` (assumed deployed if fully implemented)
3. Else if `userStoriesCreated` is set → state is `in_progress` (implementation assumed started)
4. Else → state is `planned`

The `stateHistory` will be retroactively constructed based on available timestamps.

## State Transition Triggers

### Automatic Transitions

The following commands automatically trigger state transitions:

**`/feature` command**:
- Creates feature with state `planned`
- Adds initial state history entry

**`/implement` command**:
- Transitions from `planned` → `in_progress` (when first story begins)
- Transitions from `in_progress` → `testing` (when all stories complete)
- Updates state history with transition details

**`/summarise` command**:
- Transitions from `deployed` → `summarised` (when feature is summarized)
- Updates state history with transition details

### Manual Transitions

Manual state transitions can be performed by directly editing `feature-log.json`:

1. Update the `state` field to the new state
2. Add a new entry to `stateHistory` with:
   - `state`: The new state
   - `timestamp`: Current timestamp in ISO 8601 format
   - `triggeredBy`: `manual`
   - `notes`: Explanation for the manual transition

### Validation

When updating feature state (automatically or manually):

1. Verify the transition is allowed per the transition rules
2. Ensure a state history entry is created for the transition
3. Validate timestamp is in ISO 8601 format
4. Ensure state history is in chronological order

## Usage Examples

### Example 1: New Feature Creation

When `/feature` creates a new feature:

```json
{
  "featureID": "5",
  "title": "Architecture System Improvements",
  "state": "planned",
  "stateHistory": [
    {
      "state": "planned",
      "timestamp": "2025-10-19T20:30:00Z",
      "triggeredBy": "command",
      "notes": "Feature created via /feature command"
    }
  ],
  "createdAt": "2025-10-19T20:30:00Z",
  "userStoriesCreated": "2025-10-19T20:30:00Z",
  "userStoriesImplemented": null,
  "isSummarised": false,
  "summarisedAt": null,
  "actions": []
}
```

### Example 2: Feature Implementation Started

When `/implement` begins implementation:

```json
{
  "featureID": "5",
  "title": "Architecture System Improvements",
  "state": "in_progress",
  "stateHistory": [
    {
      "state": "planned",
      "timestamp": "2025-10-19T20:30:00Z",
      "triggeredBy": "command",
      "notes": "Feature created via /feature command"
    },
    {
      "state": "in_progress",
      "timestamp": "2025-10-19T21:00:00Z",
      "triggeredBy": "command",
      "notes": "Implementation started via /implement command"
    }
  ],
  "createdAt": "2025-10-19T20:30:00Z",
  "userStoriesCreated": "2025-10-19T20:30:00Z",
  "userStoriesImplemented": null,
  "isSummarised": false,
  "summarisedAt": null,
  "actions": []
}
```

### Example 3: Feature Implementation Complete

When `/implement` completes all stories:

```json
{
  "featureID": "5",
  "title": "Architecture System Improvements",
  "state": "testing",
  "stateHistory": [
    {
      "state": "planned",
      "timestamp": "2025-10-19T20:30:00Z",
      "triggeredBy": "command",
      "notes": "Feature created via /feature command"
    },
    {
      "state": "in_progress",
      "timestamp": "2025-10-19T21:00:00Z",
      "triggeredBy": "command",
      "notes": "Implementation started via /implement command"
    },
    {
      "state": "testing",
      "timestamp": "2025-10-19T23:45:00Z",
      "triggeredBy": "command",
      "notes": "All user stories completed via /implement command"
    }
  ],
  "createdAt": "2025-10-19T20:30:00Z",
  "userStoriesCreated": "2025-10-19T20:30:00Z",
  "userStoriesImplemented": "2025-10-19T23:45:00Z",
  "isSummarised": false,
  "summarisedAt": null,
  "actions": []
}
```

### Example 4: Manual Transition to Review

User manually transitions feature to review after testing:

```json
{
  "featureID": "5",
  "title": "Architecture System Improvements",
  "state": "review",
  "stateHistory": [
    {
      "state": "planned",
      "timestamp": "2025-10-19T20:30:00Z",
      "triggeredBy": "command",
      "notes": "Feature created via /feature command"
    },
    {
      "state": "in_progress",
      "timestamp": "2025-10-19T21:00:00Z",
      "triggeredBy": "command",
      "notes": "Implementation started via /implement command"
    },
    {
      "state": "testing",
      "timestamp": "2025-10-19T23:45:00Z",
      "triggeredBy": "command",
      "notes": "All user stories completed via /implement command"
    },
    {
      "state": "review",
      "timestamp": "2025-10-20T10:00:00Z",
      "triggeredBy": "manual",
      "notes": "All tests passed, ready for code review"
    }
  ],
  "createdAt": "2025-10-19T20:30:00Z",
  "userStoriesCreated": "2025-10-19T20:30:00Z",
  "userStoriesImplemented": "2025-10-19T23:45:00Z",
  "isSummarised": false,
  "summarisedAt": null,
  "actions": []
}
```

### Example 5: Feature Deployed and Summarised

Complete lifecycle through deployment and summarization:

```json
{
  "featureID": "5",
  "title": "Architecture System Improvements",
  "state": "summarised",
  "stateHistory": [
    {
      "state": "planned",
      "timestamp": "2025-10-19T20:30:00Z",
      "triggeredBy": "command",
      "notes": "Feature created via /feature command"
    },
    {
      "state": "in_progress",
      "timestamp": "2025-10-19T21:00:00Z",
      "triggeredBy": "command",
      "notes": "Implementation started via /implement command"
    },
    {
      "state": "testing",
      "timestamp": "2025-10-19T23:45:00Z",
      "triggeredBy": "command",
      "notes": "All user stories completed via /implement command"
    },
    {
      "state": "review",
      "timestamp": "2025-10-20T10:00:00Z",
      "triggeredBy": "manual",
      "notes": "All tests passed, ready for code review"
    },
    {
      "state": "deployed",
      "timestamp": "2025-10-20T14:00:00Z",
      "triggeredBy": "manual",
      "notes": "Code review approved and merged to main"
    },
    {
      "state": "summarised",
      "timestamp": "2025-10-20T15:00:00Z",
      "triggeredBy": "command",
      "notes": "Feature summarised via /summarise command"
    }
  ],
  "createdAt": "2025-10-19T20:30:00Z",
  "userStoriesCreated": "2025-10-19T20:30:00Z",
  "userStoriesImplemented": "2025-10-19T23:45:00Z",
  "isSummarised": true,
  "summarisedAt": "2025-10-20T15:00:00Z",
  "actions": []
}
```

## Migration Guide

### Migrating Existing Feature Log Entries

Existing features in `feature-log.json` need to be migrated to include the new `state` and `stateHistory` fields.

### Migration Strategy

**Option 1: Automatic Migration (Recommended)**

A migration script or command can automatically add the new fields based on existing timestamps:

1. Read current `feature-log.json`
2. For each feature missing `state` or `stateHistory`:
   - Infer current state based on existing fields
   - Construct state history from available timestamps
   - Add the new fields to the feature
3. Write updated `feature-log.json`

**Option 2: Manual Migration**

Manually edit `feature-log.json` to add the new fields to each feature.

### Automatic State Inference Rules

For features missing the `state` field:

```javascript
if (feature.summarisedAt !== null) {
  state = "summarised";
} else if (feature.userStoriesImplemented !== null) {
  state = "deployed"; // Assume deployed if fully implemented
} else if (feature.userStoriesCreated !== null) {
  state = "in_progress"; // Assume in progress if user stories exist
} else {
  state = "planned";
}
```

### Automatic State History Construction

For features missing the `stateHistory` field:

```javascript
stateHistory = [];

// Always start with planned state
if (feature.createdAt) {
  stateHistory.push({
    state: "planned",
    timestamp: feature.createdAt,
    triggeredBy: "command",
    notes: "Migrated from legacy feature log"
  });
}

// Add in_progress if user stories were created
if (feature.userStoriesCreated && feature.userStoriesCreated !== feature.createdAt) {
  stateHistory.push({
    state: "in_progress",
    timestamp: feature.userStoriesCreated,
    triggeredBy: "command",
    notes: "Migrated from legacy feature log"
  });
}

// Add testing/deployed if implementation completed
if (feature.userStoriesImplemented) {
  stateHistory.push({
    state: "deployed",
    timestamp: feature.userStoriesImplemented,
    triggeredBy: "command",
    notes: "Migrated from legacy feature log"
  });
}

// Add summarised if feature was summarised
if (feature.summarisedAt) {
  stateHistory.push({
    state: "summarised",
    timestamp: feature.summarisedAt,
    triggeredBy: "command",
    notes: "Migrated from legacy feature log"
  });
}
```

### Migration Example

**Before Migration:**

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

**After Migration:**

```json
{
  "featureID": "1",
  "title": "Initialize Frontend Web Application",
  "state": "summarised",
  "stateHistory": [
    {
      "state": "planned",
      "timestamp": "2025-10-15T00:00:00Z",
      "triggeredBy": "command",
      "notes": "Migrated from legacy feature log"
    },
    {
      "state": "deployed",
      "timestamp": "2025-10-15T20:00:00Z",
      "triggeredBy": "command",
      "notes": "Migrated from legacy feature log"
    },
    {
      "state": "summarised",
      "timestamp": "2025-10-15T20:15:00Z",
      "triggeredBy": "command",
      "notes": "Migrated from legacy feature log"
    }
  ],
  "createdAt": "2025-10-15T00:00:00Z",
  "userStoriesCreated": "2025-10-15T00:00:00Z",
  "userStoriesImplemented": "2025-10-15T20:00:00Z",
  "isSummarised": true,
  "summarisedAt": "2025-10-15T20:15:00Z",
  "actions": []
}
```

### Migration Validation

After migration, validate that:

1. All features have a `state` field with a valid state value
2. All features have a `stateHistory` array with at least one entry
3. State history is in chronological order (earliest first)
4. Current `state` matches the last entry in `stateHistory`
5. All existing fields are preserved unchanged
6. JSON syntax is valid

### Rollback Strategy

If migration needs to be rolled back:

1. The `state` and `stateHistory` fields can be removed from all features
2. All other fields remain unchanged
3. The system will continue to work with the legacy schema
4. Commands will function as before (they will need to be updated to handle both schemas)

## Best Practices

### When to Transition States

**planned → in_progress**:
- When `/implement` command is executed and first story begins

**in_progress → testing**:
- When all user stories are completed
- Implementation log shows all stories as "completed"

**testing → review**:
- When all tests pass successfully
- Feature is ready for code review
- Pull request has been created

**review → deployed**:
- When code review is approved
- Changes have been merged to main/production branch
- Feature is live in production

**deployed → summarised**:
- When `/summarise` command is executed
- Feature is stable in production
- Implementation details have been condensed

**any → archived**:
- When feature is cancelled, deprecated, or no longer active
- When feature lifecycle is complete

### State History Best Practices

1. Always add timestamp when transitioning states
2. Include meaningful notes for manual transitions
3. Preserve complete history (never delete state history entries)
4. Keep state history in chronological order
5. Use consistent timestamp format (ISO 8601)

### Querying by State

To find features in a specific state:

```javascript
const featuresInProgress = featureLog.features.filter(f => f.state === "in_progress");
const featuresReadyForReview = featureLog.features.filter(f => f.state === "review");
```

To find features that transitioned recently:

```javascript
const recentlyDeployed = featureLog.features.filter(f => {
  const deployedEntry = f.stateHistory.find(h => h.state === "deployed");
  if (!deployedEntry) return false;
  const deployedDate = new Date(deployedEntry.timestamp);
  const daysSinceDeployment = (Date.now() - deployedDate) / (1000 * 60 * 60 * 24);
  return daysSinceDeployment <= 7; // Deployed in last 7 days
});
```

## Future Enhancements

Potential future enhancements to the state system:

1. **Automated State Transitions**: Commands automatically transition states based on completion criteria
2. **State Transition Validation**: Built-in validation to prevent invalid state transitions
3. **State-Based Reporting**: Dashboard showing features by current state
4. **State Transition Webhooks**: Trigger external actions when states change
5. **State Metrics**: Track average time spent in each state
6. **Custom States**: Allow projects to define additional states beyond the core set
7. **State Dependencies**: Define dependencies between features based on states
8. **Automated Archival**: Automatically archive features after a certain period in "summarised" state
