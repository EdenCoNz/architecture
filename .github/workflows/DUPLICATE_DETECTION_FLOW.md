# Duplicate Detection Flow Diagram

## Quick Reference: Decision Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CI/CD Failure Detected                       │
│                  (feature/* branch PR fails)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Start Duplicate     │
                  │  Detection Process   │
                  └──────────┬───────────┘
                             │
                             ▼
        ╔════════════════════════════════════════════════╗
        ║  STAGE 1: Fetch Latest CI Failure Issue       ║
        ╚════════════════════════════════════════════════╝
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
            ┌────────────┐    ┌────────────────┐
            │ No issues  │    │ Issue found    │
            │ found      │    │ (with label    │
            │            │    │ "ci-failure")  │
            └─────┬──────┘    └────────┬───────┘
                  │                    │
                  │                    ▼
                  │     ╔════════════════════════════════════════╗
                  │     ║  STAGE 2: Preliminary Checks          ║
                  │     ║  (Fast Metadata Comparison)           ║
                  │     ╚════════════════════════════════════════╝
                  │                    │
                  │           ┌────────┴────────┐
                  │           │ Compare:        │
                  │           │ • Feature ID    │
                  │           │ • Job Name      │
                  │           │ • Step Name     │
                  │           └────────┬────────┘
                  │                    │
                  │           ┌────────┴────────┐
                  │           │                 │
                  │           ▼                 ▼
                  │   ┌────────────┐    ┌──────────────┐
                  │   │ Any field  │    │ All fields   │
                  │   │ differs    │    │ match        │
                  │   └─────┬──────┘    └──────┬───────┘
                  │         │                  │
                  │         │                  ▼
                  │         │   ╔════════════════════════════════════════╗
                  │         │   ║  STAGE 3: Deep Log Comparison         ║
                  │         │   ╚════════════════════════════════════════╝
                  │         │                  │
                  │         │          ┌───────┴───────┐
                  │         │          │ Extract logs  │
                  │         │          │ from previous │
                  │         │          │ issue body    │
                  │         │          └───────┬───────┘
                  │         │                  │
                  │         │          ┌───────┴───────────────────────┐
                  │         │          │ Run 3 Comparison Strategies:  │
                  │         │          │                               │
                  │         │          │ 1️⃣  Head/Tail Comparison      │
                  │         │          │    (first/last 10 lines)      │
                  │         │          │                               │
                  │         │          │ 2️⃣  Hash Comparison           │
                  │         │          │    (exact match detection)    │
                  │         │          │                               │
                  │         │          │ 3️⃣  Similarity Analysis       │
                  │         │          │    (% common lines)           │
                  │         │          └───────┬───────────────────────┘
                  │         │                  │
                  │         │                  ▼
                  │         │       ╔═══════════════════════════════════╗
                  │         │       ║  STAGE 4: Final Decision          ║
                  │         │       ╚═══════════════════════════════════╝
                  │         │                  │
                  │         │          ┌───────┴────────┐
                  │         │          │ Is duplicate?  │
                  │         │          │                │
                  │         │          │ • Exact match? │
                  │         │          │ • Head+tail?   │
                  │         │          │ • Similarity   │
                  │         │          │   ≥ 80%?       │
                  │         │          └───────┬────────┘
                  │         │                  │
                  │         │         ┌────────┴────────┐
                  │         │         │                 │
                  │         │         ▼                 ▼
                  │         │   ┌──────────┐     ┌───────────┐
                  │         │   │   YES    │     │    NO     │
                  │         │   │(Duplicate│     │ (New      │
                  │         │   │detected) │     │  issue)   │
                  │         │   └────┬─────┘     └─────┬─────┘
                  │         │        │                 │
                  ▼         ▼        ▼                 ▼
          ┌───────────────────────────┐       ┌──────────────────┐
          │  ⏭️  SKIP ISSUE CREATION  │       │  ✅ CREATE NEW   │
          │                           │       │     ISSUE        │
          │ • Log skip reason         │       │                  │
          │ • Reference existing      │       │ • Add label      │
          │   issue in summary        │       │   "ci-failure"   │
          │ • Show duplicate details  │       │ • Assign to      │
          └───────────────────────────┘       │   PR author      │
                                              │ • Link to PR     │
                                              └──────────────────┘
```

## Decision Criteria Summary

### Stage 1: Issue Lookup
- **Input:** Repository, ci-failure label
- **Output:** Latest open issue (or null)
- **Fast Path:** No issue → Create new issue immediately

### Stage 2: Metadata Comparison
- **Input:** featureID, jobName, stepName
- **Comparison:** Current vs. Previous
- **Fast Path:** Any mismatch → Create new issue immediately
- **Slow Path:** All match → Proceed to log comparison

### Stage 3: Log Similarity Detection

| Strategy | Method | Condition | Speed |
|----------|--------|-----------|-------|
| **1. Head/Tail** | Compare first/last 10 lines | Both match | ⚡ Fast |
| **2. Hash** | MD5 checksum comparison | Identical hash | ⚡⚡ Very Fast |
| **3. Similarity** | Count common unique lines | ≥80% match | ⚡ Fast |

### Stage 4: Final Decision

**Duplicate detected IF any of:**
- ✅ Exact hash match (Strategy 2)
- ✅ Head AND tail match (Strategy 1)
- ✅ Similarity ≥ 80% (Strategy 3)

**Otherwise:** Create new issue

## Performance Characteristics

```
┌────────────────────────────────────────────────────────┐
│           Typical Performance Profile                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  No existing issues:         < 1 second (fast path)   │
│  Metadata mismatch:          < 2 seconds (fast path)  │
│  Full log comparison:        3-5 seconds              │
│                                                        │
│  Most common path: Metadata mismatch (fast path)      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Example Execution Paths

### Path A: First Failure (Fastest)
```
Start → Fetch Latest Issue → No issues found → CREATE ISSUE
Time: <1s
Skip Reason: no_existing_issues
```

### Path B: Different Feature (Fast)
```
Start → Fetch Latest Issue → Found #42
      → Compare Metadata → Feature ID differs (2 vs 5)
      → CREATE ISSUE
Time: <2s
Skip Reason: metadata_mismatch
```

### Path C: Different Step (Fast)
```
Start → Fetch Latest Issue → Found #42
      → Compare Metadata → Job matches, Step differs
      → CREATE ISSUE
Time: <2s
Skip Reason: metadata_mismatch
```

### Path D: Exact Duplicate (Deep Check)
```
Start → Fetch Latest Issue → Found #42
      → Compare Metadata → All fields match
      → Extract Logs → Compare logs
      → Hash match: YES
      → SKIP ISSUE
Time: 3-5s
Skip Reason: duplicate_detected
```

### Path E: Similar But Different (Deep Check)
```
Start → Fetch Latest Issue → Found #42
      → Compare Metadata → All fields match
      → Extract Logs → Compare logs
      → Hash match: NO
      → Head/tail match: NO
      → Similarity: 45% (< 80%)
      → CREATE ISSUE
Time: 3-5s
Skip Reason: logs_differ
```

## Skip Reason Quick Reference

| Skip Reason | Stage | Path | Creates Issue? |
|-------------|-------|------|----------------|
| `no_existing_issues` | 1 | Fast | ✅ Yes |
| `metadata_mismatch` | 2 | Fast | ✅ Yes |
| `log_extraction_failed` | 3 | Deep | ✅ Yes (fail-safe) |
| `logs_differ` | 4 | Deep | ✅ Yes |
| `duplicate_detected` | 4 | Deep | ❌ No |

## Workflow Outputs

### Step Outputs (for subsequent steps)

```yaml
steps.duplicate-check.outputs.is_duplicate        # "true" or "false"
steps.duplicate-check.outputs.skip_reason         # One of the 5 reasons above
steps.duplicate-check.outputs.duplicate_issue_number  # Issue number (if duplicate)
steps.duplicate-check.outputs.is_retry            # "true" or "false"
steps.duplicate-check.outputs.retry_of_issue      # Previous issue number (if retry)
steps.duplicate-check.outputs.attempt_count       # Number of attempts for this failure
```

### Job Outputs (for subsequent jobs)

```yaml
jobs.create-bug-issue.outputs.is_retry            # "true" or "false"
jobs.create-bug-issue.outputs.retry_of_issue      # Previous issue number (if retry)
```

### Environment Variables

```yaml
env.ISSUE_URL  # URL of created issue (empty if skipped)
```

### Workflow Summary (GitHub UI)

Displays one of:
- ✅ Issue created (with detection details)
- ⏭️ Issue skipped (with duplicate reference)
- ⚠️ Warning (if something went wrong)

## Retry Detection and Bug Resolver Integration

### Overview

When a retry is detected (a fix was previously attempted but CI is still failing), the bug logger automatically calls the bug resolver workflow to update the previous issue's status.

### Retry Detection Criteria

A retry is detected when:
1. **No duplicate open issue exists** (this is a new issue)
2. **A closed issue exists** with matching:
   - Feature ID
   - Job Name
   - Step Name
3. **The closed issue was marked as resolved** (has `pending-merge` or `fix-pending` label)

### Automatic Bug Resolver Call

When a retry is detected, the bug logger:

1. **Creates a new issue** for the current failure
2. **Automatically calls** the bug resolver workflow with:
   - `current_run_status: 'failure'` (because we're in the bug logger, CI is failing)
   - `previous_issue_number: <retry_of_issue>` (the closed issue number)
   - `action: 'mark_as_resolved'` (to evaluate the fix outcome)

3. **Bug resolver updates the previous issue** based on the failure:
   - Adds a comment indicating the fix attempt failed
   - Does NOT add labels (since the current run is a failure)

### Integration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CI/CD Failure Detected                       │
│                  (Retry of previous fix attempt)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Bug Logger Workflow │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Retry Detection     │
                  │  (closed issue with  │
                  │   pending-merge)     │
                  └──────────┬───────────┘
                             │
                    is_retry=true
                             │
                             ▼
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
┌───────────────────┐                  ┌──────────────────────┐
│  Create New Issue │                  │  Call Bug Resolver   │
│  for Current      │                  │  Workflow            │
│  Failure          │                  │                      │
└───────────────────┘                  └──────────┬───────────┘
                                                  │
                                                  ▼
                                       ┌──────────────────────┐
                                       │  Update Previous     │
                                       │  Issue with Failure  │
                                       │  Comment             │
                                       └──────────────────────┘
```

### Example Scenario

1. **Initial Failure**: Issue #123 created for failing `lint` job
2. **Fix Attempted**: Developer commits fix, issue #123 marked `pending-merge`
3. **Issue Closed**: PR merged, issue #123 closed
4. **Retry Failure**: CI still fails on `lint` job
5. **Automatic Actions**:
   - New issue #124 created for current failure
   - Bug resolver called with `previous_issue_number: 123`
   - Issue #123 receives comment: "The automated fix attempt for this issue has failed. Manual investigation may be required."

### Benefits

- **Automatic tracking** of fix attempt outcomes
- **Clear history** of retry attempts in previous issues
- **No manual intervention** required to update issue statuses
- **Visibility** into whether fixes actually resolved the problem
