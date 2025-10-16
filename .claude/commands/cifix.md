---
description: Analyze CI workflow failures and fix them using the appropriate agent
args:
  - name: workflow.yml
    description: The GitHub Actions workflow file name (e.g., frontend-ci.yml)
    required: true
  - name: job
    description: The job name that is failing in the workflow
    required: true
  - name: step
    description: The specific step within the job that is failing
    required: true
  - name: logdetail
    description: CI log details or error information from the failing step
    required: true
model: claude-sonnet-4-5
---

## Purpose

This command analyzes GitHub Actions workflow failures, identifies the root cause, determines which specialized agent is best suited to fix the issue, and delegates the fix to that agent.

## Variables

- `{{{ workflow.yml }}}` - The workflow file name (e.g., frontend-ci.yml)
- `{{{ job }}}` - The job name that is failing
- `{{{ step }}}` - The specific step within the job that is failing
- `{{{ logdetail }}}` - Contains CI log details, error messages, or failure information from the failing step

## Instructions

- MUST analyze the workflow files to understand the CI pipeline structure
- MUST identify which step/job is failing based on the log details
- MUST determine the root cause of the failure (build errors, test failures, linting issues, deployment problems, etc.)
- MUST select the most appropriate agent based on the failure type:
  - `backend-developer` - For API errors, database issues, server-side test failures
  - `frontend-developer` - For UI build errors, frontend test failures, component issues
  - `devops-engineer` - For Docker issues, CI/CD pipeline configuration, deployment failures
  - `general-purpose` - For other issues or when multiple areas are involved
- MUST NOT make assumptions - verify the actual workflow configuration first
- MUST provide clear context to the selected agent about what needs to be fixed

## Workflow

### Step 1: Read the Workflow File

Read the specified workflow file at `.github/workflows/{{{ workflow.yml }}}` to understand:
- The workflow structure and jobs
- The specific job `{{{ job }}}` configuration
- The failing step `{{{ step }}}` and what it does

### Step 2: Analyze the Failure Context

Using the provided parameters:
- Workflow file: `{{{ workflow.yml }}}`
- Failing job: `{{{ job }}}`
- Failing step: `{{{ step }}}`
- Log details: `{{{ logdetail }}}`

Understand the complete context of what is failing and why.

### Step 3: Parse the Log Details

Analyze the provided log details (`{{{ logdetail }}}`) to identify:
- The specific error messages
- The failure type (compilation error, test failure, configuration issue, etc.)
- Any relevant stack traces or diagnostic information

### Step 4: Identify Root Cause

Determine the category of the failure:
- **Build/Compilation errors** - Code doesn't compile or build
- **Test failures** - Unit tests, integration tests, or E2E tests failing
- **Linting/Code quality** - ESLint, TypeScript, or other linter failures
- **Docker/Container issues** - Docker build or container runtime problems
- **Deployment failures** - Issues deploying to production/staging
- **Pipeline configuration** - Workflow YAML syntax or configuration errors

### Step 5: Select the Appropriate Agent

Based on the root cause, select the best agent:
- **Backend issues** (API tests, server errors, database) → `backend-developer`
- **Frontend issues** (UI tests, build errors, component problems) → `frontend-developer`
- **Infrastructure/DevOps** (Docker, CI/CD config, deployment) → `devops-engineer`
- **Mixed or unclear** → `general-purpose`

### Step 6: Delegate to Agent

Use the Task tool to launch the selected agent with:
- Clear description of the failing step/job
- Relevant error messages from the logs
- Context about what needs to be fixed
- Instruction to fix the issue

## Report

After delegating to the agent, inform the user:
1. Which workflow and job/step is failing
2. The identified root cause of the failure
3. Which agent was selected and why
4. Summary of what the agent will work on
