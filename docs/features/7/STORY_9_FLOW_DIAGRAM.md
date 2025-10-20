# Story #9: Success Labeling Logic - Flow Diagram

## Overview

This document provides visual representations of the success labeling logic flow implemented in Story #9. The diagrams illustrate how the bug resolver detects successful fix completion and applies the pending-merge label.

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Story #9: Success Labeling                   │
│                  (Already Implemented in Story #1)              │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Fix Attempt         │
                  │  Completes           │
                  │  (Success or Fail)   │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Caller Invokes      │
                  │  Bug Resolver        │
                  │  Workflow            │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Input Parameters:   │
                  │  - issue_number: 42  │
                  │  - status: success   │
                  │  - action: resolved  │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Bug Resolver        │
                  │  Processes Request   │
                  └──────────┬───────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
            ┌───────────┐     ┌──────────────┐
            │  Success  │     │   Failure    │
            │   Path    │     │    Path      │
            └─────┬─────┘     └──────┬───────┘
                  │                  │
                  ▼                  ▼
        ┌──────────────────┐  ┌─────────────┐
        │ Apply Label:     │  │ Add Comment:│
        │ "pending-merge"  │  │ "Fix failed"│
        └──────┬───────────┘  └─────────────┘
               │
               ▼
        ┌──────────────────┐
        │ Add Comment:     │
        │ "Fix succeeded,  │
        │  pending merge"  │
        └──────┬───────────┘
               │
               ▼
        ┌──────────────────┐
        │ Issue Ready for  │
        │ Code Review      │
        └──────────────────┘
```

## Detailed Workflow Execution

```
┌──────────────────────────────────────────────────────────────────┐
│                  Bug Resolver Workflow Execution                 │
│              (.github/workflows/bug-resolver.yml)                │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Job: resolve-issue  │
                  │  Runner: ubuntu-22   │
                  │  Timeout: 5 min      │
                  └──────────┬───────────┘
                             │
                             ▼
        ╔════════════════════════════════════════════╗
        ║  STEP 1: Validate Inputs                   ║
        ╚════════════════════════════════════════════╝
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Validate:            │
                  │ ✓ current_run_status │
                  │   = "success" or     │
                  │     "failure"        │
                  │ ✓ issue_number       │
                  │   is numeric         │
                  │ ✓ action = valid     │
                  │   option             │
                  └──────────┬───────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
             [Valid]▼                 ▼[Invalid]
        ┌─────────────┐       ┌──────────────┐
        │  Continue   │       │  Exit with   │
        │  Workflow   │       │  Error Code  │
        └──────┬──────┘       └──────────────┘
               │
               ▼
        ╔════════════════════════════════════════════╗
        ║  STEP 2: Check if Issue Exists             ║
        ╚════════════════════════════════════════════╝
               │
               ▼
        ┌─────────────────────┐
        │ GitHub CLI:         │
        │ gh issue view $NUM  │
        │ --json state,labels │
        └──────────┬──────────┘
                   │
          ┌────────┴────────┐
          │                 │
   [Found]▼                 ▼[Not Found]
┌──────────────┐    ┌───────────────────┐
│ Parse State  │    │ Set:              │
│ from JSON    │    │ issue_exists=false│
└──────┬───────┘    └──────┬────────────┘
       │                   │
       ▼                   │
  [OPEN State]             │
       │                   │
       ▼                   ▼
┌──────────────┐    ┌──────────────────┐
│ Set:         │    │ Log Warning:     │
│issue_exists= │    │ "Issue not found"│
│    true      │    │ Skip to Summary  │
└──────┬───────┘    └──────────────────┘
       │
       ▼
╔════════════════════════════════════════════╗
║  STEP 3: Determine Action Path             ║
╚════════════════════════════════════════════╝
       │
       ▼
┌──────────────────────┐
│ Check conditions:    │
│                      │
│ IF issue_exists AND  │
│    action = resolved │
│    status = success  │
│ THEN: Success Path   │
│                      │
│ IF issue_exists AND  │
│    action = resolved │
│    status = failure  │
│ THEN: Failure Path   │
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
[Success]     [Failure]
    │             │
    ▼             ▼
╔═══════════════════════════════════════════╗
║  STEP 4a: Success Path                    ║
║  (Story #9 Implementation)                ║
╚═══════════════════════════════════════════╝
    │
    ▼
┌─────────────────────┐
│ Log:                │
│ "Marking Issue #N   │
│  as resolved"       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ GitHub CLI:         │
│ gh issue edit $NUM  │
│ --add-label         │
│ "pending-merge"     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Log:                │
│ "Label added"       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Create Comment:     │
│ "The fix attempt    │
│  for this issue has │
│  completed          │
│  successfully..."   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ GitHub CLI:         │
│ gh issue comment    │
│ $NUM --body "..."   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Log:                │
│ "Successfully       │
│  marked issue as    │
│  pending merge"     │
└──────────┬──────────┘
           │
           │           ╔═══════════════════════════════╗
           │           ║  STEP 4b: Failure Path        ║
           │           ╚═══════════════════════════════╝
           │                       │
           │                       ▼
           │           ┌─────────────────────┐
           │           │ Log:                │
           │           │ "Fix Attempt Failed"│
           │           └──────────┬──────────┘
           │                      │
           │                      ▼
           │           ┌─────────────────────┐
           │           │ Create Comment:     │
           │           │ "The automated fix  │
           │           │  attempt failed..." │
           │           └──────────┬──────────┘
           │                      │
           │                      ▼
           │           ┌─────────────────────┐
           │           │ GitHub CLI:         │
           │           │ gh issue comment    │
           │           └──────────┬──────────┘
           │                      │
           └──────────┬───────────┘
                      │
                      ▼
        ╔════════════════════════════════════════════╗
        ║  STEP 5: Generate Summary                  ║
        ╚════════════════════════════════════════════╝
                      │
                      ▼
           ┌─────────────────────┐
           │ Create:             │
           │ $GITHUB_STEP_SUMMARY│
           └──────────┬──────────┘
                      │
                      ▼
           ┌─────────────────────┐
           │ Include:            │
           │ - Input details     │
           │ - Action taken      │
           │ - Issue link        │
           │ - Success/failure   │
           └──────────┬──────────┘
                      │
                      ▼
           ┌─────────────────────┐
           │ Workflow Complete   │
           │ ✅ Success          │
           └─────────────────────┘
```

## Decision Tree

```
                     START
                       │
                       ▼
              ┌────────────────┐
              │ Inputs Valid?  │
              └────────┬───────┘
                       │
              ┌────────┴────────┐
              │                 │
           [No]▼                ▼[Yes]
        ┌──────────┐    ┌──────────────┐
        │  EXIT 1  │    │ Check Issue  │
        │  Error   │    │   Exists     │
        └──────────┘    └──────┬───────┘
                               │
                      ┌────────┴────────┐
                      │                 │
                   [No]▼                ▼[Yes]
              ┌──────────────┐  ┌──────────────┐
              │ Log Warning  │  │ Issue State? │
              │ Skip Updates │  └──────┬───────┘
              └──────────────┘         │
                                  ┌────┴────┐
                                  │         │
                             [OPEN]▼         ▼[CLOSED]
                          ┌──────────┐  ┌──────────┐
                          │  Action  │  │   Skip   │
                          │   Type?  │  │ Updates  │
                          └────┬─────┘  └──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
            [mark_as_resolved]  [mark_previous_as_pending]
                    │                     │
                    ▼                     ▼
             ┌──────────┐         ┌──────────────┐
             │  Status? │         │ Story #8     │
             └────┬─────┘         │ Logic        │
                  │               └──────────────┘
         ┌────────┴────────┐
         │                 │
    [success]▼             ▼[failure]
  ┌──────────────┐  ┌──────────────┐
  │ STORY #9:    │  │ Add Failure  │
  │              │  │ Comment Only │
  │ Add Label:   │  │              │
  │ pending-merge│  │ No Label     │
  │              │  │ Changes      │
  │ Add Comment: │  └──────────────┘
  │ "Success,    │
  │  pending     │
  │  merge"      │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │   Generate   │
  │   Summary    │
  └──────┬───────┘
         │
         ▼
      SUCCESS
```

## Integration Flow with Fix Command

```
┌──────────────────────────────────────────────────────────────────┐
│         Complete Automated Resolution Flow (Story #7)            │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  CI/CD Job Fails     │
                  │  (frontend-ci.yml,   │
                  │   backend-ci.yml)    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Bug Logger Creates  │
                  │  GitHub Issue with   │
                  │  ci-failure label    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Issue Event         │
                  │  Listener Detects    │
                  │  New CI Failure      │
                  │  (Story #5)          │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Fix Command         │
                  │  Triggered           │
                  │  (Story #7)          │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Fix Attempt         │
                  │  Executes            │
                  │  (Claude Agent)      │
                  └──────────┬───────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
             [Success]▼               ▼[Failure]
        ┌─────────────────┐   ┌──────────────────┐
        │ Fix PR Created  │   │ Fix Attempt      │
        │ Tests Pass      │   │ Failed           │
        └──────┬──────────┘   └──────┬───────────┘
               │                     │
               ▼                     ▼
    ╔══════════════════════╗  ┌──────────────────┐
    ║  STORY #9:           ║  │ Bug Resolver:    │
    ║  Bug Resolver Called ║  │ Log Failure      │
    ║                      ║  │ Add Comment      │
    ║  Inputs:             ║  │ (No Label)       │
    ║  - issue: 42         ║  └──────────────────┘
    ║  - status: success   ║
    ║  - action: resolved  ║
    ╚══════════════════════╝
               │
               ▼
        ┌──────────────────┐
        │ Add Label:       │
        │ "pending-merge"  │
        └──────┬───────────┘
               │
               ▼
        ┌──────────────────┐
        │ Add Comment:     │
        │ "Fix succeeded"  │
        └──────┬───────────┘
               │
               ▼
        ┌──────────────────┐
        │ Developer        │
        │ Reviews PR       │
        └──────┬───────────┘
               │
               ▼
        ┌──────────────────┐
        │ PR Merged        │
        │ Issue Closed     │
        └──────────────────┘
```

## State Transitions

```
Issue Lifecycle with Story #9:

┌──────────────┐
│ Issue Created│
│ Label:       │
│ - ci-failure │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Fix Attempt  │
│ In Progress  │
└──────┬───────┘
       │
       │
┌──────┴──────┐
│             │
▼             ▼
┌─────────────────────┐    ┌──────────────────┐
│ Fix Succeeded       │    │ Fix Failed       │
│                     │    │                  │
│ Story #9 Applies:   │    │ No Label Change  │
│ ┌─────────────────┐ │    │ ┌──────────────┐ │
│ │ pending-merge   │ │    │ │ ci-failure   │ │
│ └─────────────────┘ │    │ └──────────────┘ │
│                     │    │                  │
│ "Fix ready for      │    │ "Fix failed,     │
│  review and merge"  │    │  manual review   │
│                     │    │  needed"         │
└──────┬──────────────┘    └──────────────────┘
       │
       ▼
┌──────────────┐
│ Code Review  │
│ & Testing    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PR Merged    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Issue Closed │
│ (Manually)   │
└──────────────┘
```

## Label State Machine

```
┌─────────────────────────────────────────────────────────────────┐
│                    Label State Machine                          │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │  Issue Open  │
                    │  No Labels   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
              ┌─────│ ci-failure   │────┐
              │     └──────────────┘    │
              │                         │
    [New Different]               [Fix Attempt]
     [Failure]                      [Triggered]
              │                         │
              ▼                         ▼
    ┌──────────────┐           ┌──────────────┐
    │ fix-pending  │           │  Processing  │
    │ (Story #8)   │           └──────┬───────┘
    └──────────────┘                  │
                              ┌───────┴────────┐
                              │                │
                         [Success]        [Failure]
                              │                │
                              ▼                ▼
                    ┌──────────────┐   ┌──────────────┐
                    │pending-merge │   │ ci-failure   │
                    │ (Story #9)   │   │ (unchanged)  │
                    └──────┬───────┘   └──────────────┘
                           │
                      [PR Merged]
                           │
                           ▼
                    ┌──────────────┐
                    │Issue Closed  │
                    │(All labels   │
                    │ preserved)   │
                    └──────────────┘
```

## Timing Diagram

```
Timeline: Fix Attempt to Label Application

Time  Event
────────────────────────────────────────────────────────────────
T+0s  │ Fix attempt completes successfully
      │
T+1s  │ Fix command workflow calls bug-resolver
      │ Inputs: status=success, action=mark_as_resolved
      │
T+2s  │ Bug resolver: Input validation
      │ ✓ All inputs valid
      │
T+3s  │ Bug resolver: Check issue exists
      │ gh issue view 42 --json state,labels
      │
T+5s  │ Issue found, state=OPEN
      │ Set issue_exists=true
      │
T+6s  │ Evaluate conditions:
      │ ✓ issue_exists == true
      │ ✓ action == mark_as_resolved
      │ ✓ status == success
      │ → Execute success path (Story #9)
      │
T+8s  │ Add pending-merge label
      │ gh issue edit 42 --add-label "pending-merge"
      │
T+10s │ Label applied successfully
      │
T+12s │ Add success comment
      │ gh issue comment 42 --body "..."
      │
T+15s │ Comment added successfully
      │
T+16s │ Generate GitHub Actions summary
      │
T+18s │ Workflow complete ✅
      │
T+20s │ Developer receives notification
      │ "Issue #42 labeled: pending-merge"
────────────────────────────────────────────────────────────────
Total Duration: ~20 seconds
```

## Error Handling Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    Error Handling Paths                          │
└──────────────────────────────────────────────────────────────────┘

                         START
                           │
                           ▼
                  ┌────────────────┐
                  │ Validate Input │
                  └────────┬───────┘
                           │
                    ┌──────┴──────┐
                    │             │
              [Invalid]▼           ▼[Valid]
            ┌────────────┐   ┌─────────┐
            │ LOG ERROR  │   │Continue │
            │ EXIT 1     │   └────┬────┘
            └────────────┘        │
                                  ▼
                          ┌───────────────┐
                          │ Check Issue   │
                          └───────┬───────┘
                                  │
                          ┌───────┴───────┐
                          │               │
                    [Not Found]▼           ▼[Found]
                  ┌──────────────┐   ┌─────────┐
                  │ LOG WARNING  │   │Continue │
                  │ Skip Updates │   └────┬────┘
                  │ EXIT 0       │        │
                  └──────────────┘        ▼
                                  ┌───────────────┐
                                  │ Issue State?  │
                                  └───────┬───────┘
                                          │
                                  ┌───────┴───────┐
                                  │               │
                            [CLOSED]▼             ▼[OPEN]
                          ┌──────────────┐   ┌─────────┐
                          │ LOG WARNING  │   │Continue │
                          │ Skip Updates │   └────┬────┘
                          │ EXIT 0       │        │
                          └──────────────┘        ▼
                                          ┌───────────────┐
                                          │ gh issue edit │
                                          └───────┬───────┘
                                                  │
                                          ┌───────┴───────┐
                                          │               │
                                    [Error]▼              ▼[Success]
                                  ┌──────────┐    ┌──────────┐
                                  │ Retry 3x │    │ Continue │
                                  └────┬─────┘    └────┬─────┘
                                       │               │
                                  [All Failed]          ▼
                                       │         ┌──────────────┐
                                       │         │gh issue      │
                                       │         │comment       │
                                       │         └──────┬───────┘
                                       │                │
                                       │         ┌──────┴──────┐
                                       │         │             │
                                       │   [Error]▼            ▼[Success]
                                       │   ┌──────────┐  ┌─────────┐
                                       │   │ Retry 3x │  │ Success │
                                       │   └────┬─────┘  └─────────┘
                                       │        │
                                       │   [All Failed]
                                       │        │
                                       ▼        ▼
                                  ┌──────────────────┐
                                  │ LOG ERROR        │
                                  │ Workflow Failed  │
                                  │ Manual Review    │
                                  │ Required         │
                                  └──────────────────┘
```

## Comparison: Story #8 vs Story #9

```
┌──────────────────────────────────────────────────────────────────┐
│          Story #8 vs Story #9 Execution Paths                    │
└──────────────────────────────────────────────────────────────────┘

                         START
                           │
                           ▼
                  ┌────────────────┐
                  │  Bug Resolver  │
                  │  Workflow      │
                  └────────┬───────┘
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
          ┌─────────────────┐   ┌──────────────────┐
          │ Story #8        │   │ Story #9         │
          │ fix-pending     │   │ pending-merge    │
          └─────────────────┘   └──────────────────┘
          │                     │
          │ Trigger:            │ Trigger:
          │ - action: mark_     │ - action: mark_
          │   previous_as_      │   as_resolved
          │   pending           │ - status: success
          │                     │
          ▼                     ▼
          ┌─────────────────┐   ┌──────────────────┐
          │ Scenario:       │   │ Scenario:        │
          │ New different   │   │ Fix attempt      │
          │ failure         │   │ succeeded        │
          │ detected        │   │                  │
          └─────────┬───────┘   └──────┬───────────┘
                    │                  │
                    ▼                  ▼
          ┌─────────────────┐   ┌──────────────────┐
          │ Label Added:    │   │ Label Added:     │
          │ "fix-pending"   │   │ "pending-merge"  │
          └─────────┬───────┘   └──────┬───────────┘
                    │                  │
                    ▼                  ▼
          ┌─────────────────┐   ┌──────────────────┐
          │ Comment:        │   │ Comment:         │
          │ "Different      │   │ "Fix succeeded,  │
          │  failure        │   │  pending merge"  │
          │  detected..."   │   │                  │
          └─────────┬───────┘   └──────┬───────────┘
                    │                  │
                    ▼                  ▼
          ┌─────────────────┐   ┌──────────────────┐
          │ Next Action:    │   │ Next Action:     │
          │ Verify fix      │   │ Code review      │
          │ worked          │   │ & merge PR       │
          └─────────────────┘   └──────────────────┘
```

## Summary

These flow diagrams illustrate:

1. **High-Level Flow**: Overall success labeling process
2. **Detailed Workflow**: Step-by-step execution in bug-resolver.yml
3. **Decision Tree**: Logic flow for determining actions
4. **Integration Flow**: How Story #9 fits into complete resolution flow
5. **State Transitions**: Issue label lifecycle
6. **Label State Machine**: All possible label states and transitions
7. **Timing Diagram**: Expected execution timeline
8. **Error Handling**: How errors are detected and handled
9. **Comparison**: Differences between Story #8 and Story #9

All diagrams represent the implementation in `.github/workflows/bug-resolver.yml` lines 130-160 (Story #9 success labeling logic).
