# Automated CI/CD Failure Resolution Flow - Complete Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture and Components](#architecture-and-components)
3. [Complete Workflow Diagram](#complete-workflow-diagram)
4. [Decision Trees](#decision-trees)
5. [Configuration and Setup](#configuration-and-setup)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Example Scenarios](#example-scenarios)
8. [Maintenance and Operations](#maintenance-and-operations)

---

## System Overview

### Purpose

The Automated CI/CD Failure Resolution Flow is a comprehensive system that automatically detects, logs, and manages CI/CD failures in GitHub Actions workflows. The system provides:

- Automatic detection and logging of CI/CD failures
- Intelligent duplicate detection to prevent noise
- Retry tracking for fix attempts
- Automated fix triggering and status management
- Complete issue lifecycle management

### Key Features

1. **Automatic Issue Creation**: Failed CI/CD jobs automatically create GitHub issues with detailed context
2. **Duplicate Detection**: Multi-stage detection prevents duplicate issues for the same failure
3. **Retry Tracking**: Tracks fix attempts and updates issue statuses accordingly
4. **Fix Automation**: Automatically triggers fix workflows for detected failures
5. **Issue Lifecycle Management**: Manages issue labels and status through the complete lifecycle
6. **Minimal Manual Intervention**: Designed to operate autonomously with minimal human oversight

### System Components

The system consists of 5 core workflows and 2 application workflows:

**Core Workflows:**
1. **bug-logger.yml** - Creates GitHub issues for CI/CD failures
2. **bug-resolver.yml** - Manages issue labels based on fix outcomes
3. **issue-event-listener.yml** - Detects CI failure issues and triggers automation
4. **fix-trigger.yml** - Adds automation markers to issues for manual fix execution
5. **DUPLICATE_DETECTION_FLOW.md** - Documentation for duplicate detection logic

**Application Workflows:**
6. **frontend-ci.yml** - Frontend CI/CD pipeline
7. **backend-ci.yml** - Backend CI/CD pipeline

---

## Architecture and Components

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CI/CD APPLICATION WORKFLOWS                     │
│                                                                     │
│  ┌──────────────────────┐         ┌──────────────────────┐        │
│  │  frontend-ci.yml     │         │  backend-ci.yml      │        │
│  │                      │         │                      │        │
│  │  Jobs:               │         │  Jobs:               │        │
│  │  - lint              │         │  - lint              │        │
│  │  - typecheck         │         │  - format            │        │
│  │  - build             │         │  - type-check        │        │
│  │  - security          │         │  - test              │        │
│  │  - docker            │         │  - security          │        │
│  │  - deployment-check  │         │  - build             │        │
│  │  - log-bugs          │         │  - deployment-check  │        │
│  └──────────┬───────────┘         └──────────┬───────────┘        │
│             │                                │                     │
│             │ on failure()                   │ on failure()        │
│             └────────────────┬───────────────┘                     │
└──────────────────────────────┼─────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BUG LOGGER WORKFLOW                            │
│                     (.github/workflows/bug-logger.yml)              │
│                                                                     │
│  Inputs:                                                            │
│  - job_results (JSON)                                               │
│  - branch_name                                                      │
│  - pr_number, pr_url, pr_author                                     │
│  - run_id                                                           │
│                                                                     │
│  Process:                                                           │
│  1. Extract feature/bug information from branch name                │
│  2. Parse job results and identify failures                         │
│  3. Fetch workflow logs for failed jobs                             │
│  4. Run duplicate and retry detection (multi-stage)                 │
│  5. Create GitHub issue (if not duplicate)                          │
│  6. Add commit identifier template to issue                         │
│  7. Call bug resolver if retry detected                             │
│                                                                     │
│  Outputs:                                                           │
│  - is_retry (true/false)                                            │
│  - retry_of_issue (issue number)                                    │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ├─────────────────────────────┐
                              │                             │
                              ▼                             ▼
┌───────────────────────────────────────┐   ┌──────────────────────────────┐
│    ISSUE EVENT LISTENER WORKFLOW      │   │   BUG RESOLVER WORKFLOW      │
│   (.github/workflows/                 │   │  (.github/workflows/         │
│    issue-event-listener.yml)          │   │   bug-resolver.yml)          │
│                                       │   │                              │
│  Trigger:                             │   │  Trigger:                    │
│  - issues.opened                      │   │  - workflow_call             │
│  - issues.labeled                     │   │                              │
│                                       │   │  Inputs:                     │
│  Process:                             │   │  - current_run_status        │
│  1. Detect ci-failure label           │   │  - previous_issue_number     │
│  2. Extract metadata from issue body  │   │  - action                    │
│  3. Validate metadata                 │   │                              │
│  4. Generate fix command context      │   │  Actions:                    │
│  5. Trigger repository_dispatch       │   │  - mark_previous_as_pending  │
│                                       │   │  - mark_as_resolved          │
│  Outputs:                             │   │  - log failure               │
│  - Triggers fix-trigger workflow      │   │                              │
└───────────────────┬───────────────────┘   └──────────────────────────────┘
                    │
                    │ repository_dispatch
                    │ (ci-failure-fix-trigger)
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FIX TRIGGER WORKFLOW                             │
│                (.github/workflows/fix-trigger.yml)                  │
│                                                                     │
│  Trigger:                                                           │
│  - repository_dispatch (ci-failure-fix-trigger)                     │
│                                                                     │
│  Process:                                                           │
│  1. Validate event payload                                          │
│  2. Add automated fix trigger comment to issue                      │
│  3. Add fix-queued label to issue                                   │
│  4. Provide manual execution instructions                           │
│                                                                     │
│  Output:                                                            │
│  - Issue ready for manual /fix command execution                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. CI/CD Failure
   ↓
2. bug-logger extracts failure context
   ↓
3. Duplicate Detection (3 stages)
   ├─→ Stage 1: Fetch latest issue with ci-failure label
   ├─→ Stage 2: Compare metadata (featureID, jobName, stepName, logLines)
   └─→ Stage 3: If duplicate → skip issue creation
   ↓
4. Retry Detection
   ├─→ Search closed issues with same feature/job/step
   ├─→ Check for pending-merge or fix-pending labels
   └─→ If retry → track attempt count
   ↓
5. Issue Creation (if not duplicate)
   ├─→ Create issue with detailed context
   ├─→ Add ci-failure label
   ├─→ Assign to PR author
   └─→ Add commit identifier template
   ↓
6. Bug Resolver Call (if retry)
   ├─→ Update previous issue status
   └─→ Add failure comment
   ↓
7. Issue Event Listener (on issue.opened)
   ├─→ Extract metadata from issue body
   ├─→ Validate metadata
   └─→ Trigger repository_dispatch
   ↓
8. Fix Trigger Workflow
   ├─→ Add fix-queued label
   ├─→ Add automated fix comment
   └─→ Ready for manual /fix execution
```

---

## Complete Workflow Diagram

### End-to-End Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                 DEVELOPER WORKFLOW                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Developer pushes │
                    │ to feature/*     │
                    │ branch (PR)      │
                    └────────┬─────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CI/CD WORKFLOWS                              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Frontend CI or Backend CI Workflow Executes              │  │
│  │                                                          │  │
│  │ Jobs run: lint, typecheck, build, test, security, etc.  │  │
│  └──────────────────┬──────────────────┬────────────────────┘  │
│                     │                  │                        │
│                     ▼                  ▼                        │
│              ┌──────────┐      ┌──────────────┐                │
│              │ SUCCESS  │      │   FAILURE    │                │
│              └──────────┘      └──────┬───────┘                │
│                   │                   │                        │
│                   │                   ▼                        │
│                   │         ┌──────────────────┐               │
│                   │         │  log-bugs job    │               │
│                   │         │  triggers        │               │
│                   │         └────────┬─────────┘               │
└───────────────────┼──────────────────┼─────────────────────────┘
                    │                  │
                    │                  ▼
                    │    ┌──────────────────────────────┐
                    │    │   BUG LOGGER WORKFLOW        │
                    │    │  (reusable workflow_call)    │
                    │    └──────────┬───────────────────┘
                    │               │
                    │               ▼
                    │    ┌──────────────────────────────┐
                    │    │ DUPLICATE DETECTION          │
                    │    │                              │
                    │    │ Stage 1: Fetch Latest Issue  │
                    │    │ Stage 2: Metadata Comparison │
                    │    │ Stage 3: (if needed)         │
                    │    │         Log Comparison       │
                    │    └──────────┬───────────────────┘
                    │               │
                    │       ┌───────┴────────┐
                    │       │                │
                    │       ▼                ▼
                    │  ┌─────────┐    ┌──────────────┐
                    │  │DUPLICATE│    │  NEW ISSUE   │
                    │  │DETECTED │    │  DETECTED    │
                    │  └────┬────┘    └──────┬───────┘
                    │       │                │
                    │       ▼                ▼
                    │  ┌─────────────────────────────┐
                    │  │ SKIP issue creation         │
                    │  │ Add PR comment with         │
                    │  │ duplicate reference         │
                    │  └─────────────────────────────┘
                    │                       │
                    │                       ▼
                    │            ┌──────────────────────┐
                    │            │ RETRY DETECTION      │
                    │            │                      │
                    │            │ Search closed issues │
                    │            │ with same context    │
                    │            └──────┬───────────────┘
                    │                   │
                    │          ┌────────┴────────┐
                    │          │                 │
                    │          ▼                 ▼
                    │   ┌────────────┐    ┌─────────────┐
                    │   │ IS RETRY   │    │ FIRST       │
                    │   │ (closed    │    │ ATTEMPT     │
                    │   │  issue     │    │             │
                    │   │  exists)   │    │             │
                    │   └─────┬──────┘    └─────┬───────┘
                    │         │                 │
                    │         ▼                 │
                    │   ┌──────────────────┐    │
                    │   │ CREATE NEW ISSUE │◄───┘
                    │   │                  │
                    │   │ - Add ci-failure │
                    │   │   label          │
                    │   │ - Assign to PR   │
                    │   │   author         │
                    │   │ - Add commit ID  │
                    │   │   template       │
                    │   └────────┬─────────┘
                    │            │
                    │            ├──────────────────────┐
                    │            │                      │
                    │            ▼                      ▼
                    │   ┌──────────────────┐   ┌──────────────────┐
                    │   │ IF RETRY:        │   │ ADD COMMENT      │
                    │   │ Call bug-resolver│   │ TO PR            │
                    │   │ workflow         │   └──────────────────┘
                    │   │                  │
                    │   │ Update previous  │
                    │   │ issue with       │
                    │   │ failure comment  │
                    │   └──────────────────┘
                    │            │
                    │            ▼
                    │   ┌──────────────────────────────┐
                    │   │ ISSUE CREATED WITH           │
                    │   │ ci-failure LABEL             │
                    │   └──────────┬───────────────────┘
                    │              │
                    │              ▼
                    │   ┌──────────────────────────────┐
                    │   │ ISSUE EVENT LISTENER         │
                    │   │                              │
                    │   │ Triggered by:                │
                    │   │ - issues.opened              │
                    │   │ - ci-failure label detected  │
                    │   └──────────┬───────────────────┘
                    │              │
                    │              ▼
                    │   ┌──────────────────────────────┐
                    │   │ EXTRACT METADATA             │
                    │   │                              │
                    │   │ - featureID                  │
                    │   │ - featureName                │
                    │   │ - jobName                    │
                    │   │ - stepName                   │
                    │   │ - branchName                 │
                    │   │ - PR URL, commit URL, etc.   │
                    │   └──────────┬───────────────────┘
                    │              │
                    │              ▼
                    │   ┌──────────────────────────────┐
                    │   │ VALIDATE METADATA            │
                    │   └──────────┬───────────────────┘
                    │              │
                    │       ┌──────┴──────┐
                    │       │             │
                    │       ▼             ▼
                    │  ┌─────────┐   ┌────────┐
                    │  │ INVALID │   │ VALID  │
                    │  │  SKIP   │   └───┬────┘
                    │  └─────────┘       │
                    │                    ▼
                    │         ┌──────────────────────┐
                    │         │ TRIGGER              │
                    │         │ repository_dispatch  │
                    │         │                      │
                    │         │ Event:               │
                    │         │ ci-failure-fix-      │
                    │         │ trigger              │
                    │         └──────────┬───────────┘
                    │                    │
                    │                    ▼
                    │         ┌──────────────────────┐
                    │         │ FIX TRIGGER WORKFLOW │
                    │         │                      │
                    │         │ 1. Validate payload  │
                    │         │ 2. Add fix-queued    │
                    │         │    label             │
                    │         │ 3. Add fix trigger   │
                    │         │    comment with      │
                    │         │    instructions      │
                    │         └──────────┬───────────┘
                    │                    │
                    │                    ▼
                    │         ┌──────────────────────┐
                    │         │ ISSUE READY FOR      │
                    │         │ MANUAL FIX           │
                    │         │                      │
                    │         │ Developer runs:      │
                    │         │ claude /fix gha      │
                    │         │                      │
                    │         │ OR                   │
                    │         │                      │
                    │         │ Manual investigation │
                    │         └──────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ CI/CD PASSES         │
         │ No issues created    │
         │ Workflow complete    │
         └──────────────────────┘
```

---

## Decision Trees

### 1. Bug Logger Decision Tree

```
START: CI/CD Failure Detected
│
├─→ Extract Feature Info from Branch Name
│   ├─→ feature/{id}-{name} → featureID = {id}
│   ├─→ bug/{id}-{name} → featureID = {id}
│   └─→ other → featureID = empty
│
├─→ Parse Job Results
│   ├─→ Find failed jobs
│   ├─→ Get first failed job
│   └─→ Extract failure count
│
├─→ Fetch Workflow Logs
│   ├─→ Get job ID for failed job
│   ├─→ Fetch full logs
│   ├─→ Extract failed step name
│   └─→ Extract last 50 lines (log excerpt)
│
├─→ DUPLICATE DETECTION (Multi-Stage)
│   │
│   ├─→ STAGE 1: Fetch Latest Open Issue with ci-failure Label
│   │   ├─→ No issues found → NOT DUPLICATE → CREATE ISSUE
│   │   └─→ Issues found → Proceed to Stage 2
│   │
│   ├─→ STAGE 2: Metadata Comparison
│   │   │   Compare: featureID, jobName, stepName, logLineNumbers
│   │   │
│   │   ├─→ All fields match → Proceed to Stage 3 (optional)
│   │   └─→ Any field differs → NOT DUPLICATE
│   │       ├─→ Mark old issue as fix-pending
│   │       └─→ CREATE ISSUE
│   │
│   └─→ STAGE 3: Deep Log Comparison (if metadata matches)
│       │
│       ├─→ Extract logs from previous issue body
│       │
│       ├─→ Run 3 Comparison Strategies:
│       │   ├─→ Strategy 1: Head/Tail Comparison
│       │   │   └─→ Both match → DUPLICATE
│       │   ├─→ Strategy 2: Hash Comparison
│       │   │   └─→ Exact match → DUPLICATE
│       │   └─→ Strategy 3: Similarity Analysis
│       │       └─→ ≥80% common lines → DUPLICATE
│       │
│       └─→ Decision:
│           ├─→ IS DUPLICATE → SKIP issue creation
│           │   └─→ Add PR comment with duplicate reference
│           └─→ NOT DUPLICATE → CREATE ISSUE
│
├─→ RETRY DETECTION (if creating new issue)
│   │
│   ├─→ Search Closed Issues
│   │   ├─→ Same featureID, jobName, stepName
│   │   └─→ Has pending-merge or fix-pending label
│   │
│   ├─→ Found matching closed issue?
│   │   ├─→ YES → IS RETRY
│   │   │   ├─→ Set is_retry = true
│   │   │   ├─→ Set retry_of_issue = {closed issue number}
│   │   │   └─→ Calculate attempt_count
│   │   └─→ NO → FIRST ATTEMPT
│   │       └─→ Set attempt_count = 1
│   │
│   └─→ Create attempt count summary
│
├─→ CREATE GITHUB ISSUE (if not duplicate)
│   ├─→ Generate issue title: [{branch}] {job} job failed
│   ├─→ Generate issue body from bug log template
│   ├─→ Assign to PR author (if available)
│   ├─→ Add ci-failure label (automatic)
│   └─→ Store issue URL and number
│
├─→ ADD COMMIT IDENTIFIER TEMPLATE
│   └─→ Post comment with commit message format
│
├─→ IF RETRY DETECTED
│   └─→ Call bug-resolver workflow
│       ├─→ Input: current_run_status = 'failure'
│       ├─→ Input: previous_issue_number = {retry_of_issue}
│       ├─→ Input: action = 'mark_as_resolved'
│       └─→ Bug resolver adds failure comment to previous issue
│
└─→ ADD PR COMMENT
    ├─→ If duplicate → Link to existing issue
    └─→ If new issue → Link to created issue

END
```

### 2. Issue Event Listener Decision Tree

```
START: GitHub Issue Event Detected
│
├─→ Check Event Type
│   ├─→ issues.opened → Continue
│   ├─→ issues.labeled → Continue
│   └─→ other → STOP (not relevant)
│
├─→ Check for ci-failure Label
│   ├─→ Label present → Continue
│   └─→ Label absent → STOP (not a CI failure issue)
│
├─→ Extract Metadata from Issue Body
│   ├─→ featureID (from table)
│   ├─→ featureName (from table)
│   ├─→ jobName (from table)
│   ├─→ stepName (from table)
│   ├─→ logLineNumbers (from table)
│   ├─→ PR URL (from table)
│   ├─→ commit URL (from table)
│   ├─→ run URL (from table)
│   └─→ branchName (from issue title)
│
├─→ Validate Metadata
│   │
│   ├─→ Required Fields Check:
│   │   ├─→ featureID present?
│   │   ├─→ jobName present?
│   │   └─→ branchName present?
│   │
│   ├─→ All required fields present?
│   │   ├─→ YES → is_valid = true → Continue
│   │   └─→ NO → is_valid = false
│   │       ├─→ Log validation errors
│   │       ├─→ Add warning to summary
│   │       └─→ STOP
│
├─→ Generate Fix Command Context
│   └─→ Create JSON structure with all metadata
│
├─→ Trigger repository_dispatch Event
│   ├─→ Event type: ci-failure-fix-trigger
│   ├─→ Payload: All metadata (issue number, featureID, branch, job, step, etc.)
│   └─→ Target: fix-trigger.yml workflow
│
└─→ Generate Summary
    ├─→ Event details
    ├─→ Metadata extraction status
    └─→ Fix trigger status

END
```

### 3. Fix Trigger Decision Tree

```
START: repository_dispatch Event Received
│
├─→ Validate Event Payload
│   │
│   ├─→ Check required fields:
│   │   ├─→ issue_number present?
│   │   ├─→ feature_id present?
│   │   └─→ branch_name present?
│   │
│   ├─→ All fields present?
│   │   ├─→ YES → is_valid = true → Continue
│   │   └─→ NO → is_valid = false
│   │       ├─→ Log error
│   │       ├─→ Add error to summary
│   │       └─→ STOP (exit 1)
│
├─→ Add Fix Trigger Comment to Issue
│   ├─→ Generate comment body with:
│   │   ├─→ Fix context table (featureID, branch, job, step)
│   │   ├─→ Next steps explanation
│   │   └─→ Manual execution command
│   └─→ Post comment using gh CLI
│
├─→ Add fix-queued Label to Issue
│   └─→ Label indicates issue is ready for /fix command
│
└─→ Generate Summary
    ├─→ If successful:
    │   ├─→ Issue link
    │   ├─→ Actions taken
    │   ├─→ Context table
    │   └─→ Manual execution instructions
    └─→ If failed:
        └─→ Error details and remediation

END
```

### 4. Bug Resolver Decision Tree

```
START: workflow_call Triggered
│
├─→ Validate Inputs
│   │
│   ├─→ current_run_status ∈ {success, failure}?
│   ├─→ previous_issue_number is number?
│   ├─→ action ∈ {mark_previous_as_pending, mark_as_resolved}?
│   │
│   ├─→ All valid?
│   │   ├─→ YES → Continue
│   │   └─→ NO → Log error and exit
│
├─→ Check if Issue Exists and is Open
│   │
│   ├─→ Fetch issue using gh CLI
│   │
│   ├─→ Issue exists and state == OPEN?
│   │   ├─→ YES → issue_exists = true → Continue
│   │   └─→ NO → issue_exists = false
│   │       ├─→ Log warning
│   │       └─→ Skip label updates
│
├─→ Determine Action Based on Inputs
│   │
│   ├─→ action == 'mark_previous_as_pending'?
│   │   ├─→ YES → Add fix-pending label
│   │   │   ├─→ Add label to issue
│   │   │   └─→ Add explanatory comment
│   │   └─→ NO → Continue
│   │
│   ├─→ action == 'mark_as_resolved' AND current_run_status == 'success'?
│   │   ├─→ YES → Add pending-merge label
│   │   │   ├─→ Add label to issue
│   │   │   └─→ Add success comment
│   │   └─→ NO → Continue
│   │
│   └─→ action == 'mark_as_resolved' AND current_run_status == 'failure'?
│       ├─→ YES → Log failure
│       │   └─→ Add failure comment to issue
│       └─→ NO → No action
│
└─→ Generate Summary
    ├─→ Input details
    ├─→ Action taken
    └─→ Issue link

END
```

### 5. Complete System Decision Flow

```
CI/CD Run
│
├─→ SUCCESS
│   └─→ END (no action)
│
└─→ FAILURE
    │
    ├─→ Bug Logger Triggered
    │   │
    │   ├─→ Duplicate Detection
    │   │   ├─→ IS DUPLICATE
    │   │   │   ├─→ Skip issue creation
    │   │   │   ├─→ Add PR comment
    │   │   │   └─→ END
    │   │   └─→ NOT DUPLICATE
    │   │       └─→ Continue
    │   │
    │   ├─→ Retry Detection
    │   │   ├─→ IS RETRY
    │   │   │   ├─→ Track attempt count
    │   │   │   └─→ Flag for bug resolver
    │   │   └─→ FIRST ATTEMPT
    │   │       └─→ Set attempt = 1
    │   │
    │   ├─→ Create Issue
    │   │   ├─→ Add ci-failure label
    │   │   ├─→ Assign to PR author
    │   │   ├─→ Add commit template
    │   │   └─→ Add PR comment
    │   │
    │   └─→ If IS RETRY
    │       └─→ Call Bug Resolver
    │           └─→ Update previous issue
    │
    ├─→ Issue Event Listener Triggered
    │   │
    │   ├─→ Extract Metadata
    │   │
    │   ├─→ Validate Metadata
    │   │   ├─→ INVALID → STOP
    │   │   └─→ VALID → Continue
    │   │
    │   └─→ Trigger Fix Workflow
    │
    └─→ Fix Trigger Workflow
        │
        ├─→ Validate Payload
        │   ├─→ INVALID → STOP
        │   └─→ VALID → Continue
        │
        ├─→ Add fix-queued label
        │
        ├─→ Add fix trigger comment
        │
        └─→ READY FOR MANUAL FIX
            │
            └─→ Developer Action Required:
                ├─→ Run: claude /fix gha
                └─→ OR Manual investigation

END
```

---

## Configuration and Setup

### Prerequisites

1. **Repository Requirements**:
   - GitHub repository with GitHub Actions enabled
   - Feature branch workflow (feature/* or bug/* branches)
   - Pull request workflow for feature branches

2. **Permissions**:
   - GitHub Actions must have permissions to:
     - Read repository contents
     - Write issues
     - Write checks
     - Read workflow runs
     - Trigger repository_dispatch events

3. **Labels**:
   The following labels must exist in the repository:
   - `ci-failure` - Applied to CI/CD failure issues
   - `fix-pending` - Applied when original issue may be resolved
   - `pending-merge` - Applied when fix is successful
   - `fix-queued` - Applied when issue is queued for automated fix

### Installation Steps

#### Step 1: Copy Workflow Files

Copy the following workflow files to `.github/workflows/`:

```
.github/workflows/
├── bug-logger.yml
├── bug-resolver.yml
├── issue-event-listener.yml
├── fix-trigger.yml
├── frontend-ci.yml (or your CI workflow)
└── backend-ci.yml (or your CI workflow)
```

#### Step 2: Create Required Labels

Create the required labels in your GitHub repository:

```bash
# Using GitHub CLI
gh label create "ci-failure" --description "CI/CD workflow failure" --color "d73a4a"
gh label create "fix-pending" --description "Fix is pending verification" --color "fbca04"
gh label create "pending-merge" --description "Fix is pending review and merge" --color "0e8a16"
gh label create "fix-queued" --description "Queued for automated fix attempt" --color "d4c5f9"
```

Or create them manually via the GitHub UI:
1. Go to repository → Issues → Labels
2. Click "New label"
3. Add each label with the corresponding description and color

#### Step 3: Configure CI/CD Workflows

Update your existing CI/CD workflows (e.g., frontend-ci.yml, backend-ci.yml) to call the bug-logger workflow on failure:

```yaml
jobs:
  # Your existing jobs (lint, test, build, etc.)
  lint:
    name: Lint Check
    # ... job configuration ...

  test:
    name: Test Suite
    # ... job configuration ...

  build:
    name: Build Application
    # ... job configuration ...

  # Add this job at the end
  log-bugs:
    name: Log Bug Report and Create Issue
    needs: [lint, test, build]  # List all jobs to monitor
    if: failure()  # Only run if any job fails
    uses: ./.github/workflows/bug-logger.yml
    with:
      job_results: ${{ toJSON(needs) }}
      branch_name: ${{ github.head_ref || github.ref_name }}
      pr_number: ${{ github.event.pull_request.number }}
      pr_url: ${{ github.event.pull_request.html_url }}
      pr_author: ${{ github.event.pull_request.user.login }}
      run_id: ${{ github.run_id }}
```

#### Step 4: Set Workflow Permissions

Ensure your workflows have the correct permissions. Add to the top of your CI workflows:

```yaml
permissions:
  contents: read
  checks: write
  actions: read  # Needed to fetch job logs
  issues: write  # Needed to create GitHub issues
```

#### Step 5: Verify Branch Naming Convention

The system relies on feature branch naming following this pattern:
- `feature/{id}-{description}` - e.g., `feature/7-dark-mode-toggle`
- `bug/{id}-{description}` - e.g., `bug/123-fix-login-error`

Ensure your team follows this convention for proper feature ID extraction.

#### Step 6: Test the Installation

Test the system by:

1. **Create a test feature branch**:
   ```bash
   git checkout -b feature/999-test-ci-failure-system
   ```

2. **Introduce a deliberate failure** in your code (e.g., failing test or lint error)

3. **Push to GitHub and create a PR**:
   ```bash
   git add .
   git commit -m "Test: Deliberate CI failure for system testing"
   git push -u origin feature/999-test-ci-failure-system
   ```

4. **Verify the workflow**:
   - Check that CI fails
   - Verify bug-logger workflow runs
   - Confirm GitHub issue is created with `ci-failure` label
   - Check that issue-event-listener triggers
   - Verify fix-trigger adds `fix-queued` label and comment
   - Clean up test branch and issue

### Configuration Options

#### Customizing Duplicate Detection

The duplicate detection logic is in `bug-logger.yml`. You can adjust the similarity threshold:

```yaml
# In bug-logger.yml, locate the similarity comparison
# Current threshold: 80%
# Adjust line ~290 to change threshold:
if [ "$SIMILARITY" -ge 80 ]; then
  # Change 80 to your desired percentage (e.g., 70, 90)
```

#### Customizing Issue Templates

The bug log template is in `bug-logger.yml` (lines 182-217). Customize the issue body format:

```yaml
cat > bug_log.md <<EOF
# Bug Log - CI/CD Failure

| Field | Value |
|-------|-------|
| title | [$BRANCH_NAME] $FAILED_JOB job failed |
# ... customize fields and format ...
EOF
```

#### Adjusting Timeout Values

Each workflow has a timeout. Adjust based on your needs:

```yaml
jobs:
  create-bug-issue:
    timeout-minutes: 5  # Increase if log fetching takes longer
```

### Maintenance

#### Regular Maintenance Tasks

1. **Label Cleanup**:
   - Periodically review and close old issues with `fix-pending` label
   - Archive or close resolved issues with `pending-merge` label

2. **Workflow Updates**:
   - Keep GitHub Actions versions up to date
   - Review workflow runs for any errors
   - Monitor workflow execution times

3. **Documentation Updates**:
   - Update this documentation when making system changes
   - Document any custom modifications

#### Monitoring

Monitor the system health:

```bash
# Check recent workflow runs
gh run list --workflow=bug-logger.yml --limit 20

# Check recent workflow runs for issue listener
gh run list --workflow=issue-event-listener.yml --limit 20

# Check recent workflow runs for fix trigger
gh run list --workflow=fix-trigger.yml --limit 20

# List open CI failure issues
gh issue list --label "ci-failure" --state open

# List issues waiting for fix
gh issue list --label "fix-queued" --state open
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Bug Logger Workflow Not Triggered

**Symptoms**:
- CI fails but no GitHub issue is created
- bug-logger workflow doesn't run

**Diagnosis**:
```bash
# Check if workflow file exists
ls -la .github/workflows/bug-logger.yml

# Check recent workflow runs
gh run list --workflow=bug-logger.yml --limit 5

# Check CI workflow configuration
cat .github/workflows/frontend-ci.yml | grep -A 10 "log-bugs"
```

**Solutions**:

1. **Missing log-bugs job**: Add the log-bugs job to your CI workflow
   ```yaml
   log-bugs:
     needs: [lint, test, build]
     if: failure()
     uses: ./.github/workflows/bug-logger.yml
     # ... with inputs ...
   ```

2. **Incorrect workflow path**: Verify the path in `uses:` points to `./.github/workflows/bug-logger.yml`

3. **Missing permissions**: Add required permissions to CI workflow:
   ```yaml
   permissions:
     contents: read
     issues: write
     actions: read
   ```

4. **Conditional not met**: Check that `if: failure()` condition is present and correct

#### Issue 2: Issue Created But No ci-failure Label

**Symptoms**:
- GitHub issue is created
- Issue lacks `ci-failure` label
- Issue event listener doesn't trigger

**Diagnosis**:
```bash
# Check if label exists in repository
gh label list | grep ci-failure

# Check issue details
gh issue view ISSUE_NUMBER --json labels
```

**Solutions**:

1. **Label doesn't exist**: Create the label
   ```bash
   gh label create "ci-failure" --description "CI/CD workflow failure" --color "d73a4a"
   ```

2. **Bug logger not adding label**: This is automatic - check bug-logger.yml line 489-494
   - The issue is created without explicit label parameter
   - GitHub automatically applies labels based on issue body content
   - Verify the issue body contains the metadata table

#### Issue 3: Duplicate Issues Being Created

**Symptoms**:
- Multiple issues for the same failure
- Duplicate detection not working

**Diagnosis**:
```bash
# Check duplicate detection step logs
gh run view RUN_ID --log | grep "Duplicate Detection"

# List open ci-failure issues
gh issue list --label "ci-failure" --state open --json number,title,body
```

**Solutions**:

1. **Check metadata consistency**: Ensure metadata fields are consistently formatted
   - Feature ID extraction
   - Job name formatting
   - Step name formatting

2. **Review log line number extraction**: Check that log line numbers are extracted correctly
   - Lines 140-154 in bug-logger.yml

3. **Test duplicate detection manually**:
   ```bash
   # Extract metadata from two issues and compare
   gh issue view ISSUE_1 --json body
   gh issue view ISSUE_2 --json body
   ```

4. **Check search query**: Verify GitHub search is finding existing issues
   - Line 258 in bug-logger.yml
   - Ensure title format is consistent

#### Issue 4: Issue Event Listener Not Triggering

**Symptoms**:
- Issue created with ci-failure label
- No fix-trigger comment added
- No fix-queued label added

**Diagnosis**:
```bash
# Check issue event listener runs
gh run list --workflow=issue-event-listener.yml --limit 10

# Check issue labels
gh issue view ISSUE_NUMBER --json labels

# Check workflow trigger events
cat .github/workflows/issue-event-listener.yml | grep -A 5 "on:"
```

**Solutions**:

1. **Workflow not enabled**: Check if workflow is active
   ```bash
   gh workflow list
   gh workflow enable issue-event-listener.yml
   ```

2. **Missing ci-failure label**: Verify label is present
   ```bash
   gh issue view ISSUE_NUMBER --json labels | jq '.labels[].name'
   ```

3. **Permissions issue**: Verify workflow has correct permissions
   ```yaml
   permissions:
     issues: read
     contents: read
     actions: write  # Required for repository_dispatch
   ```

4. **Event filter not matching**: Check the workflow filter (line 27):
   ```yaml
   if: contains(github.event.issue.labels.*.name, 'ci-failure')
   ```

#### Issue 5: Metadata Extraction Fails

**Symptoms**:
- Issue created but metadata validation fails
- Fix trigger workflow not run
- Validation errors in issue event listener summary

**Diagnosis**:
```bash
# View issue event listener logs
gh run view RUN_ID --log --job "Detect CI Failure Issue"

# Check issue body format
gh issue view ISSUE_NUMBER --json body | jq -r '.body'
```

**Solutions**:

1. **Malformed issue body**: Verify issue body follows expected format
   - Should contain markdown table with metadata fields
   - Example:
     ```markdown
     | Field | Value |
     |-------|-------|
     | featureID | 123 |
     | jobName | lint |
     | stepName | Run ESLint |
     ```

2. **Missing required fields**: Ensure all required fields are present:
   - featureID
   - jobName
   - branchName (in title)

3. **Regex extraction issue**: Check extraction patterns in issue-event-listener.yml lines 51-103

4. **Special characters**: Ensure field values don't contain characters that break regex
   - Pipes (`|`) in values
   - Newlines in values

#### Issue 6: Fix Trigger Workflow Fails

**Symptoms**:
- repository_dispatch triggered but workflow fails
- Validation errors in fix-trigger workflow

**Diagnosis**:
```bash
# View fix-trigger logs
gh run list --workflow=fix-trigger.yml --limit 5
gh run view RUN_ID --log
```

**Solutions**:

1. **Missing payload fields**: Verify repository_dispatch includes all required fields
   - Check issue-event-listener.yml lines 249-259

2. **Payload validation fails**: Check fix-trigger.yml lines 44-75
   - Ensure issue_number, feature_id, branch_name are present

3. **gh CLI authentication**: Verify GitHub token has correct scopes
   - The default `github.token` should work
   - Check permissions in workflow file

#### Issue 7: Bug Resolver Not Called on Retry

**Symptoms**:
- Retry detected in bug-logger
- Previous issue not updated
- No bug resolver workflow run

**Diagnosis**:
```bash
# Check bug-logger outputs
gh run view RUN_ID --log | grep "is_retry"

# Check for bug resolver workflow call
gh run view RUN_ID --log | grep "call-bug-resolver"

# Check bug resolver runs
gh run list --workflow=bug-resolver.yml --limit 10
```

**Solutions**:

1. **Output not set correctly**: Verify bug-logger sets outputs (lines 48-50, 423-425)

2. **Workflow call condition not met**: Check line 687:
   ```yaml
   if: needs.create-bug-issue.outputs.is_retry == 'true'
   ```

3. **Job dependency issue**: Verify `needs:` is correctly set (line 686)

4. **Workflow permissions**: Ensure bug-logger has permission to call reusable workflows

#### Issue 8: High Volume of Issues

**Symptoms**:
- Too many ci-failure issues created
- Noise overwhelming developers

**Diagnosis**:
```bash
# Count open ci-failure issues
gh issue list --label "ci-failure" --state open --json number | jq 'length'

# Group by failure type
gh issue list --label "ci-failure" --state open --json title | jq -r '.[].title' | sort | uniq -c
```

**Solutions**:

1. **Improve duplicate detection**: Lower similarity threshold
   - Edit bug-logger.yml line ~290
   - Change from 80% to 90% for stricter matching

2. **Batch close duplicate issues**:
   ```bash
   # List duplicates
   gh issue list --label "ci-failure" --state open --json number,title

   # Close duplicates (manual review recommended)
   gh issue close ISSUE_NUMBER --comment "Duplicate of #ORIGINAL_ISSUE"
   ```

3. **Auto-close after fix**: Enhance bug-resolver to close issues automatically when fix succeeds

4. **Add issue templates**: Create issue template to ensure consistent formatting

#### Issue 9: Permissions Errors

**Symptoms**:
- Workflow fails with "Permission denied" or "403 Forbidden"
- Cannot create issues, add labels, or trigger workflows

**Diagnosis**:
```bash
# Check workflow permissions
cat .github/workflows/bug-logger.yml | grep -A 10 "permissions:"

# Check repository settings
# Go to: Repository Settings → Actions → General → Workflow permissions
```

**Solutions**:

1. **Insufficient workflow permissions**: Add required permissions to workflow:
   ```yaml
   permissions:
     contents: read
     issues: write
     actions: read
     checks: write
   ```

2. **Repository-level restrictions**: Update repository settings:
   - Go to Settings → Actions → General
   - Set "Workflow permissions" to "Read and write permissions"
   - Enable "Allow GitHub Actions to create and approve pull requests"

3. **Fine-grained PAT issues**: If using fine-grained PAT, ensure it has:
   - Issues: Read and write
   - Contents: Read
   - Workflows: Read and write

#### Issue 10: Retry Detection Not Working

**Symptoms**:
- Fix attempted but retry not detected
- New issue created instead of tracking attempt count
- Previous issue not updated

**Diagnosis**:
```bash
# Check closed issues with same context
gh issue list --state closed --label "pending-merge" --json number,title,body

# Check bug-logger retry detection logs
gh run view RUN_ID --log | grep "Retry Detection"
```

**Solutions**:

1. **Closed issue missing labels**: Ensure previous issue has `pending-merge` or `fix-pending` label before closing

2. **Metadata mismatch**: Verify feature ID, job name, and step name match exactly
   - Feature ID must be identical
   - Job name comparison is case-sensitive
   - Step name comparison is case-sensitive

3. **Issue not closed**: Retry detection only searches closed issues
   - Ensure previous issue is closed before new failure occurs

4. **Search query issue**: Check lines 327-333 in bug-logger.yml
   - Verify search query finds closed issues

### Debugging Techniques

#### Enable Verbose Logging

Add debug logging to workflows:

```yaml
- name: Debug - Print all inputs
  run: |
    echo "=========================================="
    echo "DEBUG: All Inputs"
    echo "=========================================="
    echo "job_results: ${{ inputs.job_results }}"
    echo "branch_name: ${{ inputs.branch_name }}"
    echo "pr_number: ${{ inputs.pr_number }}"
    # ... print all inputs ...
```

#### Test Workflows Locally

Use `act` to test workflows locally:

```bash
# Install act
brew install act  # macOS
# or download from https://github.com/nektos/act

# Run workflow locally
act pull_request -W .github/workflows/frontend-ci.yml

# Run specific job
act -j log-bugs
```

#### Manual Workflow Dispatch

Test workflows manually:

```bash
# Trigger bug-logger manually (if workflow_dispatch added)
gh workflow run bug-logger.yml

# Trigger fix-trigger manually
gh workflow run fix-trigger.yml
```

#### Inspect Workflow Run Artifacts

Download and inspect workflow logs:

```bash
# List recent runs
gh run list --workflow=bug-logger.yml --limit 5

# Download logs for specific run
gh run view RUN_ID --log > workflow-logs.txt

# Download artifacts (if any)
gh run download RUN_ID
```

#### Check GitHub API Rate Limits

If workflows are failing intermittently:

```bash
# Check rate limit status
gh api rate_limit

# Check rate limit in workflow
- name: Check rate limit
  run: gh api rate_limit
  env:
    GH_TOKEN: ${{ github.token }}
```

### Getting Help

If you encounter issues not covered here:

1. **Review workflow run logs**: Check detailed logs in GitHub Actions UI
2. **Check existing issues**: Search repository issues for similar problems
3. **Enable debug logging**: Add debug steps to problematic workflows
4. **Test in isolation**: Create minimal reproduction case
5. **Contact maintainers**: Open an issue with full details:
   - Workflow run link
   - Error messages
   - Steps to reproduce
   - Expected vs actual behavior

---

## Example Scenarios

### Scenario 1: First-Time CI Failure

**Setup**:
- Feature branch: `feature/7-dark-mode-toggle`
- First push to branch
- Lint job fails due to code style issues
- No previous issues exist

**Expected Flow**:

1. **CI Pipeline Runs**:
   - Frontend CI workflow executes
   - Lint job fails at step "Run ESLint"
   - Other jobs may succeed or be skipped

2. **Bug Logger Executes**:
   - Triggered by `if: failure()` condition
   - Extracts feature ID: `7`
   - Extracts feature name: `dark-mode-toggle`
   - Identifies failed job: `lint`
   - Fetches logs for failed job
   - Extracts failed step: `Run ESLint`
   - Gets last 50 lines of logs

3. **Duplicate Detection**:
   - Stage 1: Searches for open issues with `ci-failure` label → None found
   - Result: NOT DUPLICATE
   - Skip reason: `no_existing_issues`
   - Action: Create new issue

4. **Retry Detection**:
   - Searches closed issues with same feature/job/step → None found
   - Result: FIRST ATTEMPT
   - Attempt count: 1
   - is_retry: false

5. **Issue Creation**:
   - Issue created with title: `[feature/7-dark-mode-toggle] lint job failed`
   - Issue body contains:
     - Metadata table (featureID: 7, jobName: lint, stepName: Run ESLint)
     - Log excerpt (last 50 lines)
     - Links to PR, commit, workflow run
   - Assigned to PR author
   - ci-failure label automatically applied

6. **Commit Identifier Template Added**:
   - Comment posted with commit message format example
   - Example: `Implementation of bug-github-issue-{number}-lint-job-failed`

7. **PR Comment Added**:
   - Comment posted to PR with link to created issue

8. **Issue Event Listener Triggers**:
   - Detects `issues.opened` event
   - Checks for `ci-failure` label → Present
   - Extracts all metadata from issue body
   - Validates metadata → All required fields present

9. **Fix Trigger Workflow Runs**:
   - Receives repository_dispatch event
   - Validates payload → All fields present
   - Adds `fix-queued` label to issue
   - Posts automation comment with:
     - Fix context
     - Next steps
     - Manual execution command: `claude /fix gha`

10. **Final State**:
    - Issue created: #N
    - Labels: `ci-failure`, `fix-queued`
    - Assignee: PR author
    - Comments: 2 (commit template + fix trigger)
    - Ready for developer action

**Workflow Runs Summary**:
```
1. frontend-ci.yml (Failed)
   └─→ log-bugs job → Calls bug-logger.yml
2. bug-logger.yml (Success)
   └─→ Created issue #N
3. issue-event-listener.yml (Success)
   └─→ Triggered repository_dispatch
4. fix-trigger.yml (Success)
   └─→ Added labels and comments
```

**Developer Actions**:
```bash
# Review the issue
gh issue view N

# Run automated fix (if using Claude CLI)
claude /fix gha

# OR manually fix the issue
# 1. Fix code style issues
# 2. Commit with proper format:
git commit -m "Implementation of bug-github-issue-N-lint-job-failed"
# 3. Push changes
git push
```

---

### Scenario 2: Duplicate Failure (Exact Same Issue)

**Setup**:
- Feature branch: `feature/7-dark-mode-toggle`
- Previous issue #42 exists for same failure
- Developer pushes another commit without fixing
- Same lint job fails with same error

**Expected Flow**:

1. **CI Pipeline Runs**:
   - Same as Scenario 1
   - Lint job fails again

2. **Bug Logger Executes**:
   - Extracts same context (featureID: 7, job: lint, step: Run ESLint)
   - Fetches logs (likely identical to previous failure)

3. **Duplicate Detection**:
   - Stage 1: Finds existing open issue #42 with `ci-failure` label
   - Stage 2: Compares metadata
     - featureID: 7 == 7 ✓
     - jobName: lint == lint ✓
     - stepName: Run ESLint == Run ESLint ✓
     - logLineNumbers: L100-L150 == L100-L150 ✓
   - All fields match → Proceed to Stage 3 (optional, may skip if confident)
   - Result: **DUPLICATE DETECTED**
   - Skip reason: `duplicate_detected`
   - Action: Skip issue creation

4. **Retry Detection**: Skipped (duplicate detected)

5. **Issue Creation**: Skipped

6. **Duplicate Handling**:
   - No new issue created
   - PR comment added: "CI/CD workflow failed. This failure is a duplicate of existing issue #42: [link]"

7. **Issue Event Listener**: Not triggered (no new issue)

8. **Fix Trigger**: Not run (no new issue)

9. **Final State**:
   - No new issue created
   - Existing issue #42 remains open
   - PR has comment linking to issue #42
   - Reduces noise and duplicate issues

**Workflow Runs Summary**:
```
1. frontend-ci.yml (Failed)
   └─→ log-bugs job → Calls bug-logger.yml
2. bug-logger.yml (Success)
   └─→ Skipped issue creation (duplicate)
   └─→ Added PR comment
```

**Developer Actions**:
```bash
# Review existing issue
gh issue view 42

# Fix the issue (same as Scenario 1)
# No new issue to track - use existing #42
```

---

### Scenario 3: Different Failure on Same Feature

**Setup**:
- Feature branch: `feature/7-dark-mode-toggle`
- Previous issue #42 exists (lint job failed)
- Developer fixes lint but introduces build error
- Build job now fails instead

**Expected Flow**:

1. **CI Pipeline Runs**:
   - Lint job succeeds (fix worked!)
   - Build job fails at step "Build application"

2. **Bug Logger Executes**:
   - Extracts feature ID: 7
   - Identifies failed job: `build` (different from previous)
   - Fetches logs for build job
   - Extracts failed step: `Build application`

3. **Duplicate Detection**:
   - Stage 1: Finds existing open issue #42
   - Stage 2: Compares metadata
     - featureID: 7 == 7 ✓
     - jobName: build != lint ✗ (MISMATCH)
   - Metadata differs → NOT DUPLICATE
   - Skip reason: `metadata_mismatch`
   - Action: Create new issue + Mark old issue as fix-pending

4. **Mark Old Issue as Fix-Pending**:
   - Adds `fix-pending` label to issue #42
   - Posts comment: "A new, different failure has been detected for the same feature/job/step combination. This suggests the original issue may have been resolved. This issue has been marked as `fix-pending` for verification."

5. **Retry Detection**:
   - Searches closed issues → None found
   - Result: FIRST ATTEMPT for build failure
   - Attempt count: 1

6. **Issue Creation**:
   - New issue #43 created: `[feature/7-dark-mode-toggle] build job failed`
   - Contains build failure context and logs

7. **Issue Event Listener & Fix Trigger**: Execute as in Scenario 1

8. **Final State**:
   - Issue #42: Open, labels: `ci-failure`, `fix-pending`
   - Issue #43: Open, labels: `ci-failure`, `fix-queued`
   - PR has two comments (one for each issue)
   - Developer can close #42 manually after verification

**Workflow Runs Summary**:
```
1. frontend-ci.yml (Failed - build job)
   └─→ log-bugs job → Calls bug-logger.yml
2. bug-logger.yml (Success)
   └─→ Marked issue #42 as fix-pending
   └─→ Created new issue #43
3. issue-event-listener.yml (Success)
   └─→ Triggered for issue #43
4. fix-trigger.yml (Success)
   └─→ Added labels to issue #43
```

**Developer Actions**:
```bash
# Review both issues
gh issue view 42  # Lint issue - likely fixed
gh issue view 43  # Build issue - new problem

# Close the old issue if verified fixed
gh issue close 42 --comment "Verified fixed - lint is now passing"

# Fix the new build issue
# ... fix code ...
git commit -m "Implementation of bug-github-issue-43-build-job-failed"
git push
```

---

### Scenario 4: Retry After Failed Fix Attempt

**Setup**:
- Feature branch: `feature/7-dark-mode-toggle`
- Issue #42 created for lint failure
- Developer attempted fix, marked issue as `pending-merge`
- Issue #42 closed after merge
- CI still fails (fix was incomplete)

**Expected Flow**:

1. **CI Pipeline Runs**:
   - Lint job fails again (same error or similar)

2. **Bug Logger Executes**:
   - Extracts context (featureID: 7, job: lint, step: Run ESLint)

3. **Duplicate Detection**:
   - Stage 1: Searches open issues → None found (issue #42 is closed)
   - Result: NOT DUPLICATE
   - Action: Create new issue

4. **Retry Detection**:
   - Searches closed issues with same feature/job/step → Finds issue #42
   - Checks labels on #42 → Has `pending-merge` label
   - Result: **IS RETRY**
   - retry_of_issue: 42
   - Attempt count: 2 (1 previous closed + 1 current)

5. **Issue Creation**:
   - New issue #44 created: `[feature/7-dark-mode-toggle] lint job failed`
   - Contains current failure context

6. **Bug Resolver Called**:
   - Triggered because is_retry = true
   - Inputs:
     - current_run_status: `failure` (we're in bug-logger, so CI failed)
     - previous_issue_number: 42
     - action: `mark_as_resolved`
   - Action: Since current_run_status is `failure`, adds comment to issue #42
   - Comment: "The automated fix attempt for this issue has failed. Manual investigation may be required. Check the workflow logs for details."
   - Note: No label added because fix failed

7. **Issue Event Listener & Fix Trigger**: Execute as in Scenario 1

8. **Final State**:
   - Issue #42: Closed, has failure comment from bug resolver
   - Issue #44: Open, labels: `ci-failure`, `fix-queued`
   - PR has comment linking to issue #44
   - Attempt count tracked in issue #44 metadata

**Workflow Runs Summary**:
```
1. frontend-ci.yml (Failed)
   └─→ log-bugs job → Calls bug-logger.yml
2. bug-logger.yml (Success)
   └─→ Created issue #44
   └─→ Called bug-resolver.yml
3. bug-resolver.yml (Success)
   └─→ Added failure comment to issue #42
4. issue-event-listener.yml (Success)
   └─→ Triggered for issue #44
5. fix-trigger.yml (Success)
   └─→ Added labels to issue #44
```

**Developer Actions**:
```bash
# Review new issue
gh issue view 44

# Check previous attempt
gh issue view 42  # See failure comment from bug resolver

# Investigate why fix didn't work
# - Review previous fix commit
# - Analyze current failure logs
# - Identify root cause

# Apply more comprehensive fix
# ... fix code ...
git commit -m "Implementation of bug-github-issue-44-lint-job-failed

Second attempt - previous fix was incomplete.
This fix addresses the root cause by [explanation]."
git push
```

---

### Scenario 5: Successful Fix After Retry

**Setup**:
- Following Scenario 4
- Issue #44 exists for failed retry
- Developer applies proper fix
- CI now passes

**Expected Flow**:

1. **CI Pipeline Runs**:
   - All jobs succeed
   - Lint job passes

2. **Bug Logger**: Not triggered (CI succeeded)

3. **Manual Developer Action**:
   - Developer closes issue #44 manually with comment about successful fix
   - OR uses automated tool to close issue

4. **Final State**:
   - Issue #42: Closed (first attempt, failed)
   - Issue #44: Closed (second attempt, successful)
   - Feature branch CI passing
   - Ready for PR review and merge

**Developer Actions**:
```bash
# Verify CI passes
gh run list --branch feature/7-dark-mode-toggle --limit 1

# Close the issue
gh issue close 44 --comment "Fix successful - CI is now passing.
Second attempt resolved the issue by addressing the root cause."

# Optional: Add pending-merge label for tracking
gh issue edit 44 --add-label "pending-merge"
```

---

### Scenario 6: Multiple Simultaneous Failures

**Setup**:
- Feature branch: `feature/7-dark-mode-toggle`
- First push with multiple issues
- Lint job fails (ESLint errors)
- Build job fails (TypeScript errors)
- Docker job fails (build context issues)

**Expected Flow**:

1. **CI Pipeline Runs**:
   - Lint job fails
   - Build job fails (or may be skipped if dependency on lint)
   - Docker job fails (or may be skipped)

2. **Bug Logger Executes**:
   - Identifies multiple failed jobs
   - Selects **first failed job** for issue creation (lint)
   - Creates single issue for lint failure
   - Note: Other failures are logged in job_results but not tracked separately

3. **Issue Creation**:
   - One issue created: `[feature/7-dark-mode-toggle] lint job failed`
   - Issue body notes "Number of failures: 3"
   - Only first failure gets detailed logging

4. **Limitation**: Only one issue created per CI run

5. **Developer Action Required**:
   - Fix first issue (lint)
   - Push fix
   - If other jobs still fail, new issues will be created

**Workflow Runs Summary**:
```
1. frontend-ci.yml (Failed - multiple jobs)
   └─→ log-bugs job → Calls bug-logger.yml
2. bug-logger.yml (Success)
   └─→ Created issue for first failure (lint)
```

**Developer Actions**:
```bash
# Fix first issue
# Fix lint errors

git commit -m "Implementation of bug-github-issue-N-lint-job-failed"
git push

# If other jobs still fail after lint fix:
# New issues will be created for remaining failures
# Process repeats for each failure
```

**System Design Note**:
This is intentional design to prevent issue spam. The system creates one issue per CI run for the first failure. After fixing that failure, subsequent failures surface one at a time.

---

## Maintenance and Operations

### Routine Maintenance

#### Weekly Tasks

1. **Review Open CI Failure Issues**:
   ```bash
   # List all open ci-failure issues
   gh issue list --label "ci-failure" --state open

   # Identify stale issues (open >7 days)
   gh issue list --label "ci-failure" --state open --json number,title,createdAt | \
     jq '.[] | select((.createdAt | fromdateiso8601) < (now - 604800))'
   ```

2. **Review Fix-Pending Issues**:
   ```bash
   # List issues marked as fix-pending
   gh issue list --label "fix-pending" --state open

   # Close if verified fixed
   gh issue close ISSUE_NUMBER --comment "Verified fixed - closing issue"
   ```

3. **Clean Up Fix-Queued Labels**:
   ```bash
   # List issues with fix-queued label
   gh issue list --label "fix-queued" --state open

   # Remove label if fix attempt completed or issue closed
   gh issue edit ISSUE_NUMBER --remove-label "fix-queued"
   ```

#### Monthly Tasks

1. **Review Duplicate Detection Effectiveness**:
   ```bash
   # Count duplicate skips in last 30 days
   gh run list --workflow=bug-logger.yml --limit 100 --json conclusion,createdAt | \
     jq 'map(select(.conclusion == "success" and (.createdAt | fromdateiso8601) > (now - 2592000))) | length'

   # Check workflow run logs for "duplicate_detected" messages
   # If too many duplicates are being created, adjust threshold
   ```

2. **Analyze Retry Patterns**:
   ```bash
   # Find issues with multiple retry attempts
   gh issue list --label "ci-failure" --state all --json number,title,body | \
     jq '.[] | select(.body | contains("Attempt #"))'

   # Identify recurring issues needing attention
   ```

3. **Review Workflow Performance**:
   ```bash
   # Check average execution time for bug-logger
   gh run list --workflow=bug-logger.yml --limit 50 --json timing | \
     jq '[.[].timing.run_duration_ms] | add / length / 1000'

   # If >2 minutes average, investigate performance issues
   ```

4. **Update Action Versions**:
   - Review GitHub Actions marketplace for updates
   - Update action versions in workflows:
     ```yaml
     # Example: Update checkout action
     - uses: actions/checkout@v4  # Check for v5, etc.
     ```
   - Test changes on feature branch before merging

#### Quarterly Tasks

1. **Security Audit**:
   - Review workflow permissions
   - Verify least privilege principle
   - Check for hardcoded secrets (none should exist)
   - Update GitHub Actions to latest versions

2. **Documentation Review**:
   - Update this documentation with any system changes
   - Add new troubleshooting scenarios discovered
   - Update configuration examples

3. **System Health Report**:
   ```bash
   # Generate report
   echo "=== CI/CD Failure Resolution System Health Report ==="
   echo ""
   echo "Issues Created (Last 90 Days):"
   gh issue list --label "ci-failure" --state all --json createdAt | \
     jq 'map(select((.createdAt | fromdateiso8601) > (now - 7776000))) | length'

   echo ""
   echo "Duplicate Detection Rate:"
   # Calculate from workflow logs

   echo ""
   echo "Retry Rate:"
   # Calculate retry attempts

   echo ""
   echo "Fix Success Rate:"
   # Calculate closed vs open issues
   ```

### Operational Procedures

#### Handling High Volume of Failures

If experiencing high volume of CI failures:

1. **Identify Root Cause**:
   ```bash
   # Group failures by job type
   gh issue list --label "ci-failure" --state open --json title | \
     jq -r '.[].title' | sed 's/.*] //' | sed 's/ job failed//' | sort | uniq -c
   ```

2. **Batch Fix Common Issues**:
   - If same failure across multiple features
   - Apply fix to main branch
   - Rebase feature branches

3. **Temporary Disable Automation** (if needed):
   ```bash
   # Disable issue-event-listener to prevent fix trigger spam
   gh workflow disable issue-event-listener.yml

   # Re-enable after fixes applied
   gh workflow enable issue-event-listener.yml
   ```

#### Emergency Procedures

**If System Creates Too Many Issues**:

1. **Immediate Action**:
   ```bash
   # Disable issue-event-listener
   gh workflow disable issue-event-listener.yml

   # Disable fix-trigger
   gh workflow disable fix-trigger.yml
   ```

2. **Clean Up**:
   ```bash
   # Bulk close duplicate issues (manual review recommended)
   gh issue list --label "ci-failure" --state open --limit 100 --json number | \
     jq -r '.[].number' | while read issue; do
       echo "Review issue #$issue"
       gh issue view $issue
       read -p "Close? (y/n) " confirm
       if [ "$confirm" = "y" ]; then
         gh issue close $issue --comment "Bulk cleanup - duplicate or resolved"
       fi
     done
   ```

3. **Root Cause Analysis**:
   - Check duplicate detection logic
   - Review metadata consistency
   - Test with sample data

4. **Fix and Re-enable**:
   - Apply fixes to workflows
   - Test thoroughly
   - Re-enable workflows
   ```bash
   gh workflow enable issue-event-listener.yml
   gh workflow enable fix-trigger.yml
   ```

**If Workflows Are Failing**:

1. **Check System Status**:
   ```bash
   # GitHub Actions status
   gh api https://www.githubstatus.com/api/v2/status.json

   # Check rate limits
   gh api rate_limit
   ```

2. **Review Recent Changes**:
   ```bash
   # Check recent commits to workflows
   git log --oneline -10 -- .github/workflows/
   ```

3. **Rollback if Needed**:
   ```bash
   # Revert workflow changes
   git revert COMMIT_HASH
   git push
   ```

### Monitoring and Alerts

#### Set Up Workflow Monitoring

Use GitHub Actions workflow monitoring:

1. **Workflow Status Badge**:
   Add to README.md:
   ```markdown
   ![Bug Logger Status](https://github.com/USER/REPO/actions/workflows/bug-logger.yml/badge.svg)
   ```

2. **Workflow Notifications**:
   - Configure GitHub notification settings
   - Set up email alerts for workflow failures

3. **Third-Party Monitoring** (optional):
   - Integrate with monitoring tools (Datadog, New Relic, etc.)
   - Set up custom dashboards

#### Metrics to Track

Key metrics for system health:

1. **Issue Volume**:
   - Total ci-failure issues per week
   - Trend over time

2. **Duplicate Detection Rate**:
   - % of failures that are duplicates
   - Target: >30% (indicates effective duplicate detection)

3. **Retry Rate**:
   - % of issues that are retries
   - High retry rate may indicate ineffective fixes

4. **Fix Success Rate**:
   - % of issues closed successfully
   - Target: >80%

5. **Time to Resolution**:
   - Average time from issue creation to closure
   - Track improvement over time

6. **Workflow Performance**:
   - Average execution time for each workflow
   - Identify performance degradation

### System Evolution

#### Future Enhancements

Potential improvements to the system:

1. **Automated Fix Application**:
   - Integrate with AI-powered fix generation
   - Automatically apply fixes and create PRs

2. **Enhanced Duplicate Detection**:
   - ML-based similarity detection
   - Semantic analysis of error messages

3. **Issue Prioritization**:
   - Automatic severity classification
   - Priority labels based on impact

4. **Metrics Dashboard**:
   - Real-time system health dashboard
   - Trends and analytics

5. **Auto-Close on Success**:
   - Automatically close issues when CI passes
   - Reduce manual cleanup

6. **Multi-Failure Tracking**:
   - Create separate issues for each failed job
   - Better tracking of complex failures

#### Contribution Guidelines

To contribute improvements:

1. **Fork and Branch**:
   ```bash
   git checkout -b feature/improve-duplicate-detection
   ```

2. **Test Thoroughly**:
   - Test on feature branch
   - Verify with real failures
   - Document testing process

3. **Update Documentation**:
   - Update this file with changes
   - Add new scenarios if applicable

4. **Create Pull Request**:
   - Clear description of changes
   - Link to related issues
   - Include testing evidence

---

## Appendix

### Workflow File Reference

Quick reference to all workflow files:

| Workflow File | Purpose | Trigger | Key Outputs |
|---------------|---------|---------|-------------|
| `bug-logger.yml` | Create GitHub issues for CI failures | `workflow_call` from CI workflows | `is_retry`, `retry_of_issue` |
| `bug-resolver.yml` | Manage issue labels based on fix outcomes | `workflow_call` from bug-logger | N/A (updates issues) |
| `issue-event-listener.yml` | Detect CI failure issues and trigger automation | `issues.opened`, `issues.labeled` | Triggers `repository_dispatch` |
| `fix-trigger.yml` | Add automation markers to issues | `repository_dispatch` | N/A (updates issues) |
| `frontend-ci.yml` | Frontend CI/CD pipeline | `pull_request`, `push` | N/A (runs tests) |
| `backend-ci.yml` | Backend CI/CD pipeline | `pull_request`, `push` | N/A (runs tests) |

### Label Reference

| Label | Color | Description | Applied By | Removed By |
|-------|-------|-------------|------------|------------|
| `ci-failure` | `#d73a4a` (red) | CI/CD workflow failure | bug-logger (automatic) | Manual (when issue resolved) |
| `fix-pending` | `#fbca04` (yellow) | Fix is pending verification | bug-logger, bug-resolver | Manual (after verification) |
| `pending-merge` | `#0e8a16` (green) | Fix is pending review and merge | bug-resolver | Manual (after merge) |
| `fix-queued` | `#d4c5f9` (purple) | Queued for automated fix attempt | fix-trigger | Manual (after fix attempt) |

### Issue Metadata Fields

Fields extracted from issue body:

| Field | Description | Example | Required |
|-------|-------------|---------|----------|
| `featureID` | Feature or bug ID from branch name | `7` | Yes |
| `featureName` | Feature description slug | `dark-mode-toggle` | No |
| `jobName` | Name of failed CI job | `lint` | Yes |
| `stepName` | Name of failed step within job | `Run ESLint` | Yes |
| `logLineNumbers` | Line range of log excerpt | `L100-L150` | Yes |
| `PRURL` | Pull request URL | `https://github.com/...` | No |
| `commitURL` | Commit URL | `https://github.com/...` | No |
| `runURL` | Workflow run URL | `https://github.com/...` | Yes |

### Common GitHub CLI Commands

Useful commands for managing the system:

```bash
# List workflows
gh workflow list

# View workflow runs
gh run list --workflow=bug-logger.yml --limit 10

# View specific run
gh run view RUN_ID

# View run logs
gh run view RUN_ID --log

# Download run logs
gh run view RUN_ID --log > logs.txt

# List issues
gh issue list --label "ci-failure"

# View issue
gh issue view ISSUE_NUMBER

# Edit issue
gh issue edit ISSUE_NUMBER --add-label "fix-pending"
gh issue edit ISSUE_NUMBER --remove-label "fix-queued"

# Close issue
gh issue close ISSUE_NUMBER --comment "Fixed"

# Create label
gh label create "ci-failure" --description "CI/CD failure" --color "d73a4a"

# List labels
gh label list

# Trigger workflow manually (if workflow_dispatch enabled)
gh workflow run WORKFLOW_NAME

# Check rate limit
gh api rate_limit
```

### Glossary

**Bug Logger**: Workflow that creates GitHub issues when CI/CD jobs fail

**Bug Resolver**: Workflow that manages issue labels based on fix attempt outcomes

**Duplicate Detection**: Multi-stage process to identify identical failures and prevent duplicate issues

**Retry Detection**: Process to identify when a fix attempt has failed and a new issue is needed

**Fix Trigger**: Workflow that prepares issues for automated fix attempts

**Issue Event Listener**: Workflow that monitors issue creation and triggers automation

**Metadata**: Structured information about a CI failure (feature ID, job name, step name, etc.)

**repository_dispatch**: GitHub event type used to trigger workflows programmatically

**workflow_call**: GitHub workflow trigger that allows workflows to be reused

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-10-20 | Initial comprehensive documentation | System |

---

**Document Status**: Complete
**Last Updated**: 2025-10-20
**System Version**: 1.0.0 (Stories #1-11 Complete, Story #12 In Progress)
