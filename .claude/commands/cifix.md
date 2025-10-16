---
description: Analyze CI workflow failures and fix them using the appropriate agent
args:
  - name: logdetails
    description: CI log details or error information from the failing workflow
    required: true
model: claude-sonnet-4-5
---

## Purpose

This command analyzes GitHub Actions workflow failures, identifies the root cause, determines which specialized agent is best suited to fix the issue, and delegates the fix to that agent.

## Variables

- `{{{ logdetails }}}` - Contains CI log details, error messages, or failure information from the workflow

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

### Step 1: Locate Workflow Files

Use the Glob tool to find all GitHub Actions workflow files:
- Search for `.github/workflows/*.yml` and `.github/workflows/*.yaml`

### Step 2: Analyze the Workflow

Read the relevant workflow file(s) to understand:
- The workflow structure and jobs
- Which steps are configured
- What each job does (build, test, lint, deploy, etc.)

### Step 3: Parse the Log Details

Analyze the provided log details (`{{{ logdetails }}}`) to identify:
- Which job/step is failing
- The specific error messages
- The failure type (compilation error, test failure, configuration issue, etc.)

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
