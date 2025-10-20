# Story #8 Flow Diagram: Previous Issue Labeling Logic

## Quick Reference

Story #8 implements the logic for marking previous issues as "fix-pending" when a new different failure is detected for the same feature.

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  New Different Failure Detected                  │
│              (Same feature/job, different error)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Caller Workflow     │
                  │  (Bug Logger or      │
                  │   Other Workflow)    │
                  └──────────┬───────────┘
                             │
                             │ Passes:
                             │ - previous_issue_number: "42"
                             │ - action: "mark_previous_as_pending"
                             │ - current_run_status: "failure"
                             │
                             ▼
          ┌─────────────────────────────────────────────┐
          │    Bug Resolver Workflow (Story #8 Logic)   │
          │    (.github/workflows/bug-resolver.yml)     │
          └────────────────────┬────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Validate Inputs     │
                  │  ✓ Issue # numeric   │
                  │  ✓ Action valid      │
                  │  ✓ Status valid      │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Check Issue Exists  │
                  │  via GitHub CLI      │
                  │  gh issue view #42   │
                  └──────────┬───────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
            ┌───────────┐     ┌──────────────┐
            │ Not Found │     │  Found and   │
            │ or Closed │     │     OPEN     │
            └─────┬─────┘     └──────┬───────┘
                  │                  │
                  │                  │
                  │                  ▼
                  │      ┌─────────────────────┐
                  │      │  Add Label:         │
                  │      │  "fix-pending"      │
                  │      │                     │
                  │      │  gh issue edit #42  │
                  │      │  --add-label        │
                  │      └──────────┬──────────┘
                  │                 │
                  │                 ▼
                  │      ┌─────────────────────┐
                  │      │  Add Comment:       │
                  │      │                     │
                  │      │  "A new, different  │
                  │      │  failure has been   │
                  │      │  detected..."       │
                  │      │                     │
                  │      │  gh issue comment   │
                  │      └──────────┬──────────┘
                  │                 │
                  ▼                 ▼
          ┌────────────────┐ ┌─────────────┐
          │  Log Warning   │ │  Success    │
          │  Skip Updates  │ │  Summary    │
          │  (Graceful)    │ │             │
          └────────┬───────┘ └──────┬──────┘
                   │                │
                   └────────┬───────┘
                            │
                            ▼
                  ┌──────────────────────┐
                  │  GitHub Actions      │
                  │  Step Summary        │
                  │  - Input details     │
                  │  - Action taken      │
                  │  - Issue link        │
                  └──────────────────────┘
```

## Decision Matrix

| Condition | Action | Result |
|-----------|--------|--------|
| ✅ Issue exists and open | Add label + comment | Previous issue marked as fix-pending |
| ❌ Issue not found | Log warning, skip | Graceful degradation, no error |
| ❌ Issue closed | Log warning, skip | Graceful degradation, no error |
| ❌ Invalid input | Fail validation | Early failure with clear error |

## Acceptance Criteria Flow

### AC1: Bug Resolver Identifies Previous Issue

```
┌──────────────────────┐
│  Input Parameter:    │
│  previous_issue_     │
│  number = "42"       │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Check if Issue      │
│  Exists Step         │
│                      │
│  gh issue view 42    │
│  --json state        │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Parse Response:     │
│  - number: 42        │
│  - state: "OPEN"     │
│  - title: "..."      │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Set Output:         │
│  issue_exists=true   │
└──────────────────────┘

✅ AC1 SATISFIED
```

### AC2: Appropriate Label Added

```
┌──────────────────────┐
│  Condition Check:    │
│  - issue_exists?     │
│  - action correct?   │
└─────────┬────────────┘
          │
          ▼ YES
┌──────────────────────┐
│  Execute:            │
│  gh issue edit 42    │
│  --add-label         │
│  "fix-pending"       │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  GitHub API:         │
│  Label added to      │
│  issue #42           │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Log Success:        │
│  "Label added to     │
│   issue #42"         │
└──────────────────────┘

✅ AC2 SATISFIED
```

### AC3: Comment Added to Explain Label Change

```
┌──────────────────────┐
│  Comment Body:       │
│  "A new, different   │
│  failure has been    │
│  detected for the    │
│  same feature/job/   │
│  step combination.   │
│  This suggests the   │
│  original issue may  │
│  have been resolved. │
│  This issue has been │
│  marked as           │
│  `fix-pending` for   │
│  verification."      │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Execute:            │
│  gh issue comment 42 │
│  --body "$COMMENT"   │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  GitHub API:         │
│  Comment posted to   │
│  issue #42           │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Log Success:        │
│  "Comment added to   │
│   issue #42"         │
└──────────────────────┘

✅ AC3 SATISFIED
```

## Integration Points

### Story #1 (Bug Resolver Workflow)
**Provides**: The reusable workflow implementation
**Status**: ✅ Implemented

```yaml
# Story #1 created this workflow
File: .github/workflows/bug-resolver.yml
Inputs:
  - current_run_status
  - previous_issue_number
  - action
```

### Story #8 (This Story)
**Extends**: Story #1 with specific logic
**Status**: ✅ Already implemented in Story #1

```yaml
# Story #8 logic is this specific code path
When: action == 'mark_previous_as_pending'
Then: Add fix-pending label + comment
```

### Story #11 (Integration)
**Will Use**: Story #8 logic via workflow_call
**Status**: ⏳ Pending implementation

```yaml
# Story #11 will call this workflow
jobs:
  handle-different-failure:
    uses: ./.github/workflows/bug-resolver.yml
    with:
      previous_issue_number: ${{ steps.detect.outputs.old_issue }}
      current_run_status: "failure"
      action: "mark_previous_as_pending"
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Error Scenarios Handled                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  Invalid Input       │
│  (Non-numeric issue) │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Validation Fails    │
│  Exit Code: 1        │
│  Message: Clear      │
└──────────────────────┘


┌──────────────────────┐
│  Issue Not Found     │
│  (404 from API)      │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Set Output:         │
│  issue_exists=false  │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Skip Label Steps    │
│  Log Warning         │
│  Exit Code: 0        │
└──────────────────────┘


┌──────────────────────┐
│  Issue Closed        │
│  (state != OPEN)     │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Set Output:         │
│  issue_exists=false  │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Skip Label Steps    │
│  Log Warning         │
│  Exit Code: 0        │
└──────────────────────┘
```

## Timeline: From Implementation to Integration

```
Story #1         Story #8         Story #9         Story #11
   │                │                │                │
   ▼                ▼                ▼                ▼
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Created │    │ Already │    │ Already │    │ Will    │
│ Bug     │───▶│Included │───▶│Included │───▶│ Call    │
│Resolver │    │ in #1   │    │ in #1   │    │Resolver │
│Workflow │    │         │    │         │    │         │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
    ✅             ✅             ✅              ⏳

Oct 20         Oct 20         Oct 20          Future
05:15          06:00          06:00
```

## Label States

```
┌─────────────────────────────────────────────────────────────────┐
│                     Issue Label Lifecycle                        │
└─────────────────────────────────────────────────────────────────┘

Initial State:
┌──────────────────────┐
│  Issue #42           │
│  Labels: ci-failure  │
│  State: OPEN         │
└──────────────────────┘

After Story #8 Logic:
┌──────────────────────┐
│  Issue #42           │
│  Labels:             │
│    - ci-failure      │
│    - fix-pending ✨  │ ← Added by Story #8
│  State: OPEN         │
│  Comments: +1 ✨     │ ← Added by Story #8
└──────────────────────┘

Explanation:
The "fix-pending" label indicates:
  • A different failure was detected for the same feature
  • The original issue may have been inadvertently fixed
  • Manual verification is recommended
  • The issue should be reviewed before closing
```

## Comment Format

```markdown
A new, different failure has been detected for the same
feature/job/step combination. This suggests the original
issue may have been resolved. This issue has been marked
as `fix-pending` for verification.
```

**Purpose**:
- Inform developers of status change
- Explain why the label was added
- Provide context for manual review
- Encourage verification of the fix

## Summary

Story #8 implements critical logic for the automated CI/CD failure resolution flow:

| Aspect | Details |
|--------|---------|
| **What** | Label previous issues when different failures detected |
| **Why** | Track potential inadvertent fixes automatically |
| **How** | GitHub CLI + workflow_call integration |
| **Status** | ✅ Already implemented in Story #1 |
| **Location** | `.github/workflows/bug-resolver.yml` lines 99-128 |
| **Trigger** | `action: "mark_previous_as_pending"` |
| **Label** | `fix-pending` |
| **Permission** | `issues: write` |
| **Security** | Minimal permissions, input validation |

**All acceptance criteria satisfied and production-ready.**
