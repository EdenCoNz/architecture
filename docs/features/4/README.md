# Feature #4: Automated Issue Creation for Failed Workflow Jobs

## Implementation Status

### Completed Stories

#### Story #1: Detect Workflow Job Failures ✓
**Status**: Completed.
**Implementation Date**: 2025-10-21

The workflow failure detection system automatically monitors configured workflows and detects when any job fails or is cancelled.

**Key Files**:
- `/home/ed/Dev/architecture/.github/workflows/detect-workflow-failures.yml`

**How It Works**:
1. Uses `workflow_run` trigger to monitor completion of specified workflows
2. Only executes when a workflow concludes with 'failure' or 'cancelled' status
3. Fetches all jobs for the failed workflow run via GitHub REST API
4. Identifies each failed job independently, capturing:
   - Job name and ID
   - Job conclusion status
   - Start and completion timestamps
   - Failed step details (name, number, timing)
   - URLs to job and step logs
5. Generates comprehensive failure report in GITHUB_STEP_SUMMARY
6. Outputs structured data for use by subsequent automation

**Acceptance Criteria Met**:
- ✓ Detects job failures when they occur
- ✓ Does not trigger on successful workflows
- ✓ Detects multiple failures independently in a single workflow run

**Configuration**:

To monitor additional workflows, update the `workflows` array in `.github/workflows/detect-workflow-failures.yml`:

```yaml
on:
  workflow_run:
    workflows: ["Frontend CI/CD", "Backend CI/CD", "Other Workflow Name"]
    types: [completed]
```

**Testing**:

To test the failure detection:

1. Introduce a failure in a monitored workflow (e.g., Frontend CI/CD)
2. Push the change to trigger the workflow
3. Wait for the workflow to complete with failure status
4. The detect-workflow-failures workflow will automatically trigger
5. Review the workflow run to see the failure detection report

**Technical Details**:

- **Trigger**: `workflow_run` with `types: [completed]`
- **Conditional Execution**: Only runs when `conclusion == 'failure' || conclusion == 'cancelled'`
- **API Access**: Uses `gh api` CLI tool with GitHub token
- **Permissions**: Requires `contents: read` and `actions: read`
- **Timeout**: 5 minutes (sufficient for API calls and processing)
- **Runner**: ubuntu-22.04 (GitHub-hosted)

**Outputs**:

The workflow produces the following outputs (accessible via `steps.detect-failures.outputs`):
- `total_jobs`: Total number of jobs in the workflow run
- `failed_jobs`: Number of jobs that failed
- `cancelled_jobs`: Number of jobs that were cancelled
- `failed_job_names`: Comma-separated list of failed job names
- `failed_job_ids`: Comma-separated list of failed job IDs

**Future Integration**:

This workflow lays the foundation for subsequent stories:
- **Story #2**: Will use failure data to create local issue log files
- **Story #3**: Will trigger reusable workflow for issue creation
- **Story #4-6**: Will extract metadata, populate templates, and create GitHub issues

### Pending Stories

#### Story #2: Create Local Issue Log File from Template
**Status**: Not Started
**Dependencies**: Story #1 (Completed)

#### Story #3: Trigger Reusable Issue Creation Workflow
**Status**: Not Started
**Dependencies**: Story #2

#### Story #4: Extract Workflow Execution Metadata
**Status**: Not Started
**Dependencies**: Story #3

#### Story #5: Populate Issue Log Template with Metadata
**Status**: Not Started
**Dependencies**: Story #4

#### Story #6: Create Tracking Issue Automatically
**Status**: Not Started
**Dependencies**: Story #5

## Architecture

### Workflow Flow Diagram

```
┌─────────────────────────────────────┐
│  Monitored Workflow (e.g., CI/CD)  │
│         Runs and Completes          │
└──────────────┬──────────────────────┘
               │
               │ (workflow_run trigger)
               │
               ▼
┌─────────────────────────────────────┐
│   Detect Workflow Failures          │
│   (.github/workflows/               │
│    detect-workflow-failures.yml)    │
└──────────────┬──────────────────────┘
               │
               ├─► If conclusion == 'success' → Exit (no action)
               │
               └─► If conclusion == 'failure' or 'cancelled'
                   │
                   ▼
         ┌─────────────────────┐
         │  Fetch workflow     │
         │  run details        │
         └──────┬──────────────┘
                │
                ▼
         ┌─────────────────────┐
         │  Fetch all jobs     │
         │  via GitHub API     │
         └──────┬──────────────┘
                │
                ▼
         ┌─────────────────────┐
         │  Filter failed      │
         │  and cancelled jobs │
         └──────┬──────────────┘
                │
                ▼
         ┌─────────────────────┐
         │  Extract step       │
         │  failure details    │
         └──────┬──────────────┘
                │
                ▼
         ┌─────────────────────┐
         │  Generate failure   │
         │  detection report   │
         └─────────────────────┘
                │
                │ (Future: Story #2+)
                ▼
         ┌─────────────────────┐
         │  Create issue log   │
         │  and GitHub issue   │
         └─────────────────────┘
```

### Data Flow

**Step 1: Workflow Completion**
- Monitored workflow completes (any conclusion)
- GitHub triggers workflow_run event

**Step 2: Failure Detection**
- Check workflow conclusion
- If not failure/cancelled, exit
- If failure/cancelled, proceed to fetch details

**Step 3: Job Fetching**
- API call: `GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs`
- Returns JSON with all jobs and their steps

**Step 4: Failure Identification**
- Filter jobs where `conclusion == "failure"`
- Filter jobs where `conclusion == "cancelled"`
- Extract job metadata (name, ID, timestamps, URLs)

**Step 5: Step Analysis**
- For each failed job, identify failed steps
- Extract step metadata (name, number, timestamps)

**Step 6: Output Generation**
- Store structured data in GITHUB_OUTPUT
- Generate human-readable report in GITHUB_STEP_SUMMARY
- Make data available for subsequent steps/workflows

## Best Practices Implemented

### Security
- **Minimal Permissions**: Only requests `contents: read` and `actions: read`
- **No Secret Exposure**: Uses GITHUB_TOKEN (automatic, scoped token)
- **Read-Only Operations**: Only reads workflow data, never modifies repository

### Performance
- **Conditional Execution**: Only runs when needed (failures/cancellations)
- **Timeout Protection**: 5-minute timeout prevents runaway jobs
- **Efficient API Usage**: Single API call fetches all job data

### Reliability
- **Structured Output**: Uses GITHUB_OUTPUT for reliable data passing
- **Error Handling**: Uses `if: always()` for cleanup steps
- **Comprehensive Logging**: Detailed GITHUB_STEP_SUMMARY for debugging

### Maintainability
- **Well-Documented**: Inline comments explain each step
- **Modular Design**: Each step has single responsibility
- **Extensible**: Easy to add new workflows to monitor
- **Standard Tools**: Uses `gh api` (available on all GitHub runners)

### GitHub Actions Best Practices
- **Explicit Versioning**: Uses `@v4` for actions (not `@latest`)
- **Timeout Configuration**: Prevents resource waste
- **Structured Data**: JSON processing with `jq` for reliability
- **Summary Output**: Uses GITHUB_STEP_SUMMARY for visibility

## Monitoring and Observability

### Viewing Failure Detection Results

1. **GitHub Actions UI**:
   - Navigate to Actions tab in repository
   - Find "Detect Workflow Failures" workflow runs
   - Click on a run to view the failure detection report

2. **Step Summary**:
   - Each run includes a comprehensive summary showing:
     - Workflow name and run number
     - Total, failed, and cancelled job counts
     - Detailed breakdown of each failed job
     - Failed step information within each job

3. **Workflow Outputs**:
   - Access programmatically via GitHub API
   - Available as step outputs for workflow extensions

### Debugging

If failure detection is not working as expected:

1. **Check Workflow Trigger**:
   - Verify the monitored workflow name matches exactly
   - Confirm the workflow is completing (not still running)

2. **Check Permissions**:
   - Verify `actions: read` permission is granted
   - Check repository settings haven't restricted API access

3. **Review API Responses**:
   - Enable `ACTIONS_STEP_DEBUG` secret for verbose logging
   - Check the "Fetch workflow jobs" step output

4. **Validate Conclusion Status**:
   - Confirm workflow is actually failing (not just steps with continue-on-error)
   - Check that the conclusion is 'failure' or 'cancelled', not 'success'

## Dependencies

### Required Permissions
- `contents: read` - For checking out repository code
- `actions: read` - For accessing workflow run and job details via API

### Runtime Dependencies
- `gh` CLI tool (pre-installed on GitHub runners)
- `jq` JSON processor (pre-installed on GitHub runners)
- GitHub REST API availability

### No Additional Secrets Required
Uses `GITHUB_TOKEN` which is automatically provided to workflows.

## Future Enhancements

### Story #2-6 Integration
The current implementation provides the foundation for:
- Creating local issue log files from template
- Triggering reusable issue creation workflow
- Extracting complete workflow execution metadata
- Populating issue templates with failure data
- Automatically creating GitHub issues for tracking

### Potential Future Improvements
- **Notification Integration**: Send Slack/email alerts on critical failures
- **Failure Trend Analysis**: Track failure patterns over time
- **Automatic Retry**: Trigger workflow re-runs for transient failures
- **Failure Categorization**: Classify failures by type (test, build, deployment)
- **Custom Filtering**: Ignore known/expected failures based on patterns
- **Multi-Repository Support**: Monitor workflows across organization

## References

- GitHub Actions Documentation: [Workflow Run Events](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#workflow_run)
- GitHub REST API: [Actions Endpoints](https://docs.github.com/en/rest/actions)
- Project Context: `/home/ed/Dev/architecture/context/devops/github-actions.md`
- User Stories: `/home/ed/Dev/architecture/docs/features/4/user-stories.md`
