# Story #10: Retry Detection Flow Diagram

## Overview

This diagram illustrates the retry detection logic added to the bug logger workflow in Story #10.

## Quick Reference: Retry Detection Decision Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CI/CD Failure Detected                       │
│                  (feature/* branch PR fails)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Bug Logger Workflow │
                  │  Extract failure     │
                  │  context             │
                  └──────────┬───────────┘
                             │
                             ▼
        ╔════════════════════════════════════════════════╗
        ║  STAGE 1: Open Issue Detection (Duplicates)   ║
        ╚════════════════════════════════════════════════╝
                             │
                  ┌──────────┴──────────┐
                  │ Search for OPEN     │
                  │ issues with         │
                  │ matching title      │
                  └──────────┬──────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
            ┌────────────┐    ┌──────────────┐
            │ No open    │    │ Open issue   │
            │ issues     │    │ found        │
            │ found      │    │              │
            └─────┬──────┘    └──────┬───────┘
                  │                  │
                  │           ┌──────┴──────┐
                  │           │ Compare:    │
                  │           │ • featureID │
                  │           │ • jobName   │
                  │           │ • stepName  │
                  │           │ • logLines  │
                  │           └──────┬──────┘
                  │                  │
                  │           ┌──────┴──────┐
                  │           │             │
                  │           ▼             ▼
                  │    ┌──────────┐  ┌──────────┐
                  │    │ All      │  │ Any      │
                  │    │ fields   │  │ field    │
                  │    │ match    │  │ differs  │
                  │    └────┬─────┘  └─────┬────┘
                  │         │              │
                  │         │              │ Different
                  │         │ DUPLICATE    │ failure
                  │         │              │
                  │         ▼              ▼
                  │  ┌──────────────┐  ┌─────────────┐
                  │  │ SKIP:        │  │ Mark old    │
                  │  │ - Issue      │  │ issue as    │
                  │  │   creation   │  │ fix-pending │
                  │  │ - Retry      │  └──────┬──────┘
                  │  │   detection  │         │
                  │  │              │         │
                  │  │ is_retry=F   │         │
                  │  │ attempt=1    │         │
                  │  └──────────────┘         │
                  │                           │
                  └───────────┬───────────────┘
                              │
                              ▼
        ╔════════════════════════════════════════════════╗
        ║  STAGE 2: Closed Issue Detection (Retry)      ║
        ╚════════════════════════════════════════════════╝
                              │
                   ┌──────────┴──────────┐
                   │ Search for CLOSED   │
                   │ issues with         │
                   │ matching title      │
                   └──────────┬──────────┘
                              │
                     ┌────────┴────────┐
                     │                 │
                     ▼                 ▼
             ┌────────────┐    ┌──────────────┐
             │ No closed  │    │ Closed       │
             │ issues     │    │ issues found │
             │ found      │    │              │
             └─────┬──────┘    └──────┬───────┘
                   │                  │
                   │           ┌──────┴──────┐
                   │           │ FOR EACH    │
                   │           │ closed      │
                   │           │ issue       │
                   │           └──────┬──────┘
                   │                  │
                   │           ┌──────┴───────┐
                   │           │ Compare:     │
                   │           │ • featureID  │
                   │           │ • jobName    │
                   │           │ • stepName   │
                   │           │ (NOT logs)   │
                   │           └──────┬───────┘
                   │                  │
                   │           ┌──────┴──────┐
                   │           │             │
                   │           ▼             ▼
                   │    ┌──────────┐  ┌──────────┐
                   │    │ Match    │  │ No match │
                   │    │ found    │  │          │
                   │    └────┬─────┘  └─────┬────┘
                   │         │              │
                   │         │              └──> Skip
                   │         │
                   │         ▼
                   │  ┌──────────────────────┐
                   │  │ Check issue labels   │
                   │  │ for:                 │
                   │  │ • pending-merge      │
                   │  │ • fix-pending        │
                   │  └──────────┬───────────┘
                   │             │
                   │      ┌──────┴──────┐
                   │      │             │
                   │      ▼             ▼
                   │  ┌────────┐   ┌─────────┐
                   │  │ Has    │   │ No      │
                   │  │ label  │   │ label   │
                   │  └───┬────┘   └────┬────┘
                   │      │             │
                   │      │ RETRY!      │ Not retry
                   │      │             │ (closed
                   │      │             │  but not
                   │      │             │  resolved)
                   │      │             │
                   │      ▼             ▼
                   │  ┌─────────────────────┐
                   │  │ Count all matching  │
                   │  │ closed issues       │
                   │  │                     │
                   │  │ attempt_count =     │
                   │  │   1 + count         │
                   │  └──────────┬──────────┘
                   │             │
                   │             ▼
                   │      ┌─────────────┐
                   │      │ is_retry=T  │
                   │      │ retry_of=#N │
                   │      │ attempt=N+1 │
                   │      └──────┬──────┘
                   │             │
                   ▼             ▼
            ┌──────────────────────┐
            │ is_retry=F           │
            │ retry_of=""          │
            │ attempt=1            │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Create New Issue     │
            │ with retry metadata  │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Outputs Available:   │
            │ • is_retry           │
            │ • retry_of_issue     │
            │ • attempt_count      │
            │                      │
            │ For Story #11:       │
            │ Bug Resolver Call    │
            └──────────────────────┘
```

## Decision Criteria Summary

### Stage 1: Open Issue Detection (Duplicate Detection)

**Input:** Open issues with matching title pattern

**Comparison:**
- Feature ID (must match)
- Job Name (must match)
- Step Name (must match)
- Log Line Numbers (must match)

**Outcomes:**
- **All match** → DUPLICATE detected, skip issue creation, skip retry detection
- **Any differs** → NOT duplicate, mark old issue as fix-pending, proceed to Stage 2
- **No issues** → Proceed to Stage 2

**Purpose:** Prevent creating multiple open issues for the same failure

---

### Stage 2: Closed Issue Detection (Retry Detection)

**Input:** Closed issues with matching title pattern

**Comparison:**
- Feature ID (must match)
- Job Name (must match)
- Step Name (must match)
- Log Line Numbers (IGNORED - can vary between retries)

**Additional Check:**
- Issue must have "pending-merge" OR "fix-pending" label

**Outcomes:**
- **Match + Has Label** → RETRY detected, count attempts, create issue with retry metadata
- **Match + No Label** → NOT retry (issue closed for other reasons), create issue as first attempt
- **No Match** → NOT retry, create issue as first attempt
- **No Closed Issues** → First attempt, create issue

**Purpose:** Detect when a fix was attempted but CI still failing

---

## Retry Detection Logic Table

| Open Issue | Closed Issue | Closed Issue Labels | Result | is_retry | attempt_count |
|------------|--------------|---------------------|--------|----------|---------------|
| None | None | N/A | First failure | false | 1 |
| None | Match, 1 issue | pending-merge | Retry attempt | true | 2 |
| None | Match, 2 issues | pending-merge | Multiple retries | true | 3 |
| None | Match, 1 issue | None | First failure | false | 1 |
| Match (exact) | N/A | N/A | Duplicate (skip) | false | 1 |
| Match (diff) | None | N/A | Different failure | false | 1 |

---

## Example Execution Paths

### Path A: First Failure (Fastest)

```
Start → Stage 1 → No open issues
      → Stage 2 → No closed issues
      → CREATE ISSUE (first attempt)
      → is_retry=false, attempt_count=1

Time: 3-5 seconds
```

### Path B: Exact Duplicate

```
Start → Stage 1 → Open issue found
      → Compare → All fields match
      → SKIP ISSUE CREATION (duplicate)
      → Skip Stage 2
      → is_retry=false, attempt_count=1

Time: 2-3 seconds (fast path)
```

### Path C: Retry After Fix

```
Start → Stage 1 → No open issues
      → Stage 2 → Closed issue found
      → Compare → Feature/Job/Step match
      → Check Labels → "pending-merge" found
      → RETRY DETECTED
      → CREATE ISSUE (retry attempt)
      → is_retry=true, retry_of_issue=42, attempt_count=2

Time: 5-7 seconds
```

### Path D: Different Failure (Same Feature)

```
Start → Stage 1 → Open issue found (old failure)
      → Compare → Job/Step differs
      → Mark old issue as "fix-pending"
      → Stage 2 → Closed issues found
      → Compare → Job/Step differs
      → NOT A RETRY
      → CREATE ISSUE (first attempt of new failure)
      → is_retry=false, attempt_count=1

Time: 5-7 seconds
```

### Path E: Multiple Retries

```
Start → Stage 1 → No open issues
      → Stage 2 → Multiple closed issues found
      → Issue #42 → Match, has "pending-merge"
      → Issue #43 → Match, has "pending-merge"
      → Count = 2 closed + 1 current = 3 attempts
      → RETRY DETECTED (3rd attempt)
      → CREATE ISSUE (retry attempt)
      → is_retry=true, retry_of_issue=43, attempt_count=3

Time: 6-8 seconds
```

---

## Performance Characteristics

```
┌────────────────────────────────────────────────────────┐
│           Typical Performance Profile                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  No existing issues:         3-5 seconds              │
│  Duplicate detected:         2-3 seconds (fast path)  │
│  Retry detected:             5-7 seconds              │
│  Different failure:          5-7 seconds              │
│  Multiple retries:           6-8 seconds              │
│                                                        │
│  Most common path: First failure (no retry)           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### API Calls

| Scenario | Open Issue Search | Closed Issue Search | Total |
|----------|-------------------|---------------------|-------|
| First failure | 1 | 1 | 2 |
| Duplicate | 1 | 0 (skipped) | 1 |
| Retry | 1 | 1 | 2 |
| Different failure | 1 | 1 | 2 |

---

## Workflow Outputs

### Step Outputs

Available to downstream workflows and steps:

```yaml
steps.check-duplicate.outputs.is_retry           # "true" or "false"
steps.check-duplicate.outputs.retry_of_issue     # Issue number or ""
steps.check-duplicate.outputs.attempt_count      # "1", "2", "3", etc.
steps.check-duplicate.outputs.is_duplicate       # "true" or "false" (existing)
steps.check-duplicate.outputs.duplicate_issue_number  # Issue number or "" (existing)
```

### Usage in Story #11

Story #11 will consume these outputs to call the bug-resolver workflow:

```yaml
- name: Call bug resolver for retry
  if: steps.check-duplicate.outputs.is_retry == 'true'
  uses: ./.github/workflows/bug-resolver.yml
  with:
    current_run_status: "failure"
    previous_issue_number: ${{ steps.check-duplicate.outputs.retry_of_issue }}
    action: "mark_as_resolved"
```

---

## Label Semantics

### Labels Used for Retry Detection

| Label | Meaning | Applied By | Retry Trigger? |
|-------|---------|------------|----------------|
| `ci-failure` | CI/CD job failed | Bug logger | ❌ No (all issues have this) |
| `pending-merge` | Fix succeeded, awaiting merge | Bug resolver (Story #9) | ✅ Yes |
| `fix-pending` | Original issue may be resolved | Bug logger / Bug resolver (Story #8) | ✅ Yes |

### Why These Labels?

**pending-merge:**
- Indicates fix attempt succeeded in CI
- Fix is ready for code review and merge
- If same failure occurs after merge, it's a retry (fix was incomplete)

**fix-pending:**
- Indicates different failure occurred, suggesting original fixed
- If issue later closed and same failure recurs, it's a retry
- Helps track issue resolution lifecycle

---

## Field Comparison Differences

### Stage 1 (Duplicate Detection)

Compares **ALL** fields including log lines:
- Feature ID ✓
- Job Name ✓
- Step Name ✓
- Log Line Numbers ✓

**Rationale:** Duplicates must be exact matches to avoid skipping distinct failures

### Stage 2 (Retry Detection)

Compares only **feature/job/step** (NOT log lines):
- Feature ID ✓
- Job Name ✓
- Step Name ✓
- Log Line Numbers ✗ (intentionally excluded)

**Rationale:** Same underlying issue can produce different error messages/line numbers after code changes

---

## Structured Logging Example

```
========================================
Starting Duplicate and Retry Detection
========================================

Current failure context:
  Title: [feature/6-dark-mode] lint job failed
  Feature ID: 6
  Job Name: lint
  Step Name: Run ESLint
  Log Lines: L1234-L1284

========================================
STEP 1: Checking for Open Issues (Duplicates)
========================================
Found 0 open issues with similar titles
No existing open issues found with similar titles

========================================
STEP 2: Checking for Closed Issues (Retry Detection)
========================================
Searching for closed issues with matching feature/job/step...
Found 1 closed issues with similar titles

Analyzing closed issues for retry detection...

Checking closed issue #42 (closed at: 2025-10-19T10:30:00Z)...
  Labels: ci-failure,pending-merge
  Feature ID: 6
  Job Name: lint
  Step Name: Run ESLint
  Result: MATCH - Same feature/job/step as current failure
  Status: This issue was marked as resolved/pending
  Action: RETRY DETECTED - This failure is a retry of issue #42

Matching closed issues: 42
Total attempts for this failure: 2 (including current attempt)

========================================
Detection Complete
========================================
Duplicate Detection:
  Is Duplicate: false

Retry Detection:
  Is Retry: true
  Retry of Issue: #42
  Attempt Count: 2
========================================
```

---

## Integration with Story #11

Story #11 will use retry detection outputs to automatically call the bug-resolver workflow:

```
┌─────────────────────────────────────────────┐
│  Bug Logger (Story #10)                     │
│  - Detects retry                            │
│  - Sets is_retry=true                       │
│  - Sets retry_of_issue=42                   │
│  - Creates new issue #43                    │
└────────────────┬────────────────────────────┘
                 │
                 │ if is_retry == true
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Bug Resolver (Story #11)                   │
│  - Called with previous_issue_number=42     │
│  - Action: mark_as_resolved                 │
│  - Status: failure                          │
│  - Adds comment to issue #42                │
└─────────────────────────────────────────────┘
```

---

## Summary

The retry detection flow:
1. **Always** checks for open duplicates first (Stage 1)
2. **Only if no duplicate** checks for closed issues (Stage 2)
3. **Requires resolution labels** to trigger retry detection
4. **Counts all matching closed issues** for attempt tracking
5. **Outputs retry state** for downstream workflows

This design ensures:
- ✅ Accurate retry detection
- ✅ No duplicate open issues created
- ✅ Clear attempt tracking
- ✅ Ready for Story #11 integration
- ✅ Efficient performance (fast paths for common cases)
