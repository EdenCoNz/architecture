# Test Failure Notifications

## Overview

This document describes the comprehensive test failure notification system implemented for end-to-end, integration, and performance tests. The system ensures that developers are promptly notified of test failures with detailed diagnostic information to enable rapid issue resolution.

## Notification Channels

### 1. GitHub Native Notifications (Default - Always Enabled)

#### GitHub Issues (Main Branch Failures)

**When**: Tests fail on the `main` branch
**How**: Automated via `detect-workflow-failures.yml` workflow

**What's Included**:
- Workflow name and run number
- Branch and commit SHA
- List of failed jobs and steps
- Direct links to workflow run and logs
- Automatic issue labeling with `workflow-failure`
- Auto-closure when tests pass again

**Example Issue Format**:
```markdown
# Workflow Failure Report

## Workflow Information
- **Workflow Name**: End-to-End Tests
- **Run ID**: 1234567890
- **Branch**: main
- **Commit**: abc1234
- **Run URL**: [View on GitHub](...)

## Summary
This workflow run failed with 2 job/step failure(s).

## Failed Jobs and Steps

### 1. E2E Test Execution - Run E2E tests
**Job URL**: https://github.com/.../jobs/...
```

#### Pull Request Comments (PR Branch Failures)

**When**: Tests fail on pull request branches
**How**: Automated inline comments on PRs

**What's Included**:
- Test execution summary with pass/fail metrics
- Detailed list of failed tests (up to 10)
- Error messages and file locations
- Links to all test artifacts (screenshots, videos, traces, logs)
- Step-by-step debugging instructions
- Links to relevant documentation

**Example PR Comment**:
```markdown
## ❌ E2E Test Results

**Suite:** All E2E tests
**Overall Status:** ❌ FAILED
**Branch:** `feature/123`
**Commit:** `abc1234`

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Tests | 50 | 100% |
| ✅ Passed | 48 | 96.0% |
| ❌ Failed | 2 | 4.0% |
| ⏭️ Skipped | 0 | 0.0% |

### ⚠️ Test Failures Detected

#### 🔍 Failure Analysis

**Failed Tests:**

1. **User Login Flow - should redirect to dashboard after successful login**
   - **File:** `testing/e2e/specs/auth/login.spec.ts`
   - **Error:** Expected URL to be "http://localhost/dashboard" but got "http://localhost/login"

2. **Onboarding Form - should save assessment data**
   - **File:** `testing/e2e/specs/onboarding/assessment.spec.ts`
   - **Error:** Timeout 30000ms exceeded waiting for API response

#### 📊 Available Test Artifacts

- **📄 HTML Test Report** - Detailed test execution report
- **📸 Screenshots** - Visual snapshots at point of failure (artifact: `e2e-test-failures-abc1234`)
- **🎥 Video Recordings** - Full test execution videos (artifact: `e2e-test-failures-abc1234`)
- **🔍 Trace Files** - Playwright traces for step-by-step debugging (artifact: `e2e-test-failures-abc1234`)
- **📋 Service Logs** - Backend/frontend/database logs (artifact: `service-logs-abc1234`)

#### 🛠️ Debugging Steps

1. Download the test artifacts from the workflow run
2. Review screenshots and videos to see visual state at failure
3. Open trace files in Playwright Trace Viewer
4. Check service logs for backend/API errors
5. Review the HTML report for detailed error messages and stack traces
```

#### GitHub Job Summaries

**When**: After every test run (success or failure)
**How**: Automatically generated in workflow summary

**What's Included**:
- Test execution metrics
- Detailed failure information with error messages
- Links to artifacts
- Service health status
- Build information (branch, commit, trigger)

### 2. Email Notifications (Optional)

Email notifications can be configured for critical test failures using GitHub Actions secrets and third-party email services.

#### Setup with SendGrid

1. **Create SendGrid Account**
   - Sign up at https://sendgrid.com/
   - Create an API key with "Mail Send" permissions

2. **Add GitHub Secrets**
   ```
   Repository Settings → Secrets and variables → Actions → New repository secret

   Name: SENDGRID_API_KEY
   Value: <your-sendgrid-api-key>

   Name: NOTIFICATION_EMAIL
   Value: team@example.com
   ```

3. **Add Email Notification Step to Workflow**

   Add this step to `.github/workflows/e2e-tests.yml` after test execution:

   ```yaml
   - name: Send email notification on failure
     if: failure() && github.ref == 'refs/heads/main'
     uses: dawidd6/action-send-mail@v3
     with:
       server_address: smtp.sendgrid.net
       server_port: 587
       secure: true
       username: apikey
       password: ${{ secrets.SENDGRID_API_KEY }}
       subject: "❌ E2E Tests Failed - ${{ github.repository }}"
       to: ${{ secrets.NOTIFICATION_EMAIL }}
       from: "GitHub Actions <noreply@github.com>"
       body: |
         E2E tests failed on branch: ${{ github.ref_name }}

         Workflow: ${{ github.workflow }}
         Run: ${{ github.run_number }}
         Commit: ${{ github.sha }}

         Failed Tests: ${{ steps.test_summary.outputs.failed }}
         Total Tests: ${{ steps.test_summary.outputs.total }}

         View full results:
         https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}

         Download test artifacts (screenshots, videos, logs) from the workflow run.
   ```

#### Setup with Gmail SMTP

1. **Create App Password** (if using Gmail)
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Generate an app password for "GitHub Actions"

2. **Add GitHub Secrets**
   ```
   Name: GMAIL_USERNAME
   Value: your-email@gmail.com

   Name: GMAIL_PASSWORD
   Value: <your-app-password>

   Name: NOTIFICATION_EMAIL
   Value: team@example.com
   ```

3. **Add Email Notification Step**
   ```yaml
   - name: Send email notification on failure
     if: failure() && github.ref == 'refs/heads/main'
     uses: dawidd6/action-send-mail@v3
     with:
       server_address: smtp.gmail.com
       server_port: 587
       secure: true
       username: ${{ secrets.GMAIL_USERNAME }}
       password: ${{ secrets.GMAIL_PASSWORD }}
       subject: "❌ Tests Failed - ${{ github.repository }}"
       to: ${{ secrets.NOTIFICATION_EMAIL }}
       from: ${{ secrets.GMAIL_USERNAME }}
       body: |
         Test failures detected in ${{ github.workflow }}

         Branch: ${{ github.ref_name }}
         Commit: ${{ github.sha }}
         Failed: ${{ steps.test_summary.outputs.failed }} tests

         View details: https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}
   ```

### 3. Slack Notifications (Optional)

Slack notifications provide real-time alerts to development teams.

#### Setup with Slack Webhook

1. **Create Slack Webhook**
   - Go to Slack → Apps → Incoming Webhooks
   - Create a new webhook for your channel (e.g., `#test-failures`)
   - Copy the webhook URL

2. **Add GitHub Secret**
   ```
   Repository Settings → Secrets and variables → Actions → New repository secret

   Name: SLACK_WEBHOOK_URL
   Value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

3. **Add Slack Notification Step to Workflow**

   Add this step to `.github/workflows/e2e-tests.yml`:

   ```yaml
   - name: Send Slack notification on failure
     if: failure()
     uses: slackapi/slack-github-action@v1.25.0
     with:
       webhook-type: incoming-webhook
       webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
       payload: |
         {
           "text": "❌ E2E Tests Failed",
           "blocks": [
             {
               "type": "header",
               "text": {
                 "type": "plain_text",
                 "text": "❌ E2E Tests Failed"
               }
             },
             {
               "type": "section",
               "fields": [
                 {
                   "type": "mrkdwn",
                   "text": "*Repository:*\n${{ github.repository }}"
                 },
                 {
                   "type": "mrkdwn",
                   "text": "*Branch:*\n${{ github.ref_name }}"
                 },
                 {
                   "type": "mrkdwn",
                   "text": "*Workflow:*\n${{ github.workflow }}"
                 },
                 {
                   "type": "mrkdwn",
                   "text": "*Commit:*\n${{ github.sha }}"
                 },
                 {
                   "type": "mrkdwn",
                   "text": "*Failed Tests:*\n${{ steps.test_summary.outputs.failed }}/${{ steps.test_summary.outputs.total }}"
                 }
               ]
             },
             {
               "type": "actions",
               "elements": [
                 {
                   "type": "button",
                   "text": {
                     "type": "plain_text",
                     "text": "View Workflow Run"
                   },
                   "url": "https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}"
                 }
               ]
             }
           ]
         }
   ```

#### Setup with Slack Bot Token

For more advanced notifications with thread replies and reactions:

1. **Create Slack App**
   - Go to https://api.slack.com/apps
   - Create a new app for your workspace
   - Add OAuth scopes: `chat:write`, `files:write`
   - Install app to workspace
   - Copy the Bot Token

2. **Add GitHub Secret**
   ```
   Name: SLACK_BOT_TOKEN
   Value: xoxb-your-bot-token

   Name: SLACK_CHANNEL_ID
   Value: C01234567 (your channel ID)
   ```

3. **Add Advanced Slack Notification**
   ```yaml
   - name: Send detailed Slack notification
     if: failure()
     uses: slackapi/slack-github-action@v1.25.0
     env:
       SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
     with:
       channel-id: ${{ secrets.SLACK_CHANNEL_ID }}
       payload: |
         {
           "text": "E2E Test Failures Detected",
           "attachments": [
             {
               "color": "danger",
               "title": "${{ github.workflow }} Failed",
               "title_link": "https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}",
               "fields": [
                 {
                   "title": "Repository",
                   "value": "${{ github.repository }}",
                   "short": true
                 },
                 {
                   "title": "Branch",
                   "value": "${{ github.ref_name }}",
                   "short": true
                 },
                 {
                   "title": "Failed Tests",
                   "value": "${{ steps.test_summary.outputs.failed }}",
                   "short": true
                 },
                 {
                   "title": "Total Tests",
                   "value": "${{ steps.test_summary.outputs.total }}",
                   "short": true
                 }
               ],
               "footer": "GitHub Actions",
               "footer_icon": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
               "ts": ${{ github.event.repository.updated_at }}
             }
           ]
         }
   ```

### 4. Microsoft Teams Notifications (Optional)

#### Setup with Teams Webhook

1. **Create Teams Webhook**
   - In Teams, go to your channel → Connectors → Incoming Webhook
   - Configure webhook and copy the URL

2. **Add GitHub Secret**
   ```
   Name: TEAMS_WEBHOOK_URL
   Value: https://outlook.office.com/webhook/YOUR-WEBHOOK-URL
   ```

3. **Add Teams Notification Step**
   ```yaml
   - name: Send Teams notification on failure
     if: failure()
     run: |
       curl -H 'Content-Type: application/json' \
         -d '{
           "@type": "MessageCard",
           "@context": "https://schema.org/extensions",
           "summary": "E2E Tests Failed",
           "themeColor": "ff0000",
           "title": "❌ E2E Tests Failed",
           "sections": [{
             "facts": [
               {"name": "Repository", "value": "${{ github.repository }}"},
               {"name": "Branch", "value": "${{ github.ref_name }}"},
               {"name": "Workflow", "value": "${{ github.workflow }}"},
               {"name": "Failed Tests", "value": "${{ steps.test_summary.outputs.failed }}/${{ steps.test_summary.outputs.total }}"}
             ]
           }],
           "potentialAction": [{
             "@type": "OpenUri",
             "name": "View Workflow Run",
             "targets": [{
               "os": "default",
               "uri": "https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}"
             }]
           }]
         }' \
         ${{ secrets.TEAMS_WEBHOOK_URL }}
   ```

## Notification Content

### What Information is Included

All notification channels provide:

1. **Test Execution Summary**
   - Total tests run
   - Number of passed/failed/skipped tests
   - Pass rate percentage
   - Overall status (PASSED/FAILED)

2. **Failure Details**
   - List of failed test names
   - Error messages
   - File locations and line numbers
   - Stack traces (in detailed reports)

3. **Artifact Links**
   - HTML test reports
   - Screenshots (visual state at failure)
   - Video recordings (full test execution)
   - Trace files (step-by-step debugging)
   - Service logs (backend/frontend/database)

4. **Debugging Information**
   - Direct links to workflow run
   - Links to logs
   - Step-by-step debugging instructions
   - Links to relevant documentation

5. **Context**
   - Repository name
   - Branch name
   - Commit SHA
   - Workflow name and run number
   - Trigger event (push, PR, manual)

### Accessing Test Artifacts

#### From GitHub UI

1. Navigate to Actions tab in repository
2. Click on the failed workflow run
3. Scroll to "Artifacts" section at bottom
4. Download artifact ZIP files:
   - `e2e-test-results-<sha>` - HTML reports and JSON data
   - `e2e-test-failures-<sha>` - Screenshots, videos, traces
   - `service-logs-<sha>` - Service logs (if tests failed)

#### From Notification Links

All PR comments and GitHub Summaries include direct links to:
- Workflow run page
- Workflow logs
- Individual job logs

#### Viewing Playwright Traces

1. Download trace files from artifacts
2. Visit https://trace.playwright.dev/
3. Drag and drop trace file to viewer
4. Explore step-by-step test execution with:
   - DOM snapshots
   - Network requests
   - Console logs
   - Screenshots at each step
   - Action timings

## Notification Filtering

### Conditional Notifications

You can configure notifications to only trigger under specific conditions:

#### Only on Main Branch
```yaml
if: failure() && github.ref == 'refs/heads/main'
```

#### Only on PR Branches
```yaml
if: failure() && github.event_name == 'pull_request'
```

#### Only on Scheduled Runs
```yaml
if: failure() && github.event_name == 'schedule'
```

#### Only for Specific Test Suites
```yaml
if: failure() && steps.test_suite.outputs.suite == 'critical'
```

#### Based on Failure Threshold
```yaml
if: failure() && steps.test_summary.outputs.failed >= 5
```

## Troubleshooting Notifications

### Notifications Not Received

**GitHub Issues/PR Comments:**
- Verify workflow has `issues: write` and `pull-requests: write` permissions
- Check workflow run completed successfully (notifications run even if tests fail)
- Verify `detect-workflow-failures.yml` is enabled

**Email Notifications:**
- Verify email secrets are configured correctly
- Check spam/junk folders
- Review workflow logs for email sending errors
- Test SMTP credentials independently

**Slack Notifications:**
- Verify webhook URL is correct and active
- Check Slack app has required permissions
- Review workflow logs for HTTP errors
- Test webhook with curl command

### Missing Artifact Links

- Verify artifact upload steps ran successfully
- Check artifact retention period hasn't expired (default 30 days for test results)
- Ensure workflow has `actions: read` permission for artifact access

### Incomplete Failure Details

- Verify test framework is generating JSON reports
- Check `jq` parsing commands in workflow
- Review test execution logs for output format issues
- Ensure test results are written to expected file paths

## Best Practices

1. **Use Multiple Channels**: Combine GitHub native notifications with one external channel (email or Slack)

2. **Filter Appropriately**: Only send critical alerts to email/Slack; use PR comments for all test runs

3. **Test Notifications**: Trigger a deliberate test failure to verify notification system works

4. **Secure Secrets**: Use GitHub Secrets for all API keys and tokens; never commit them to code

5. **Monitor Notification Volume**: If failures are frequent, consider fixing root causes rather than silencing alerts

6. **Include Context**: Ensure notifications provide enough information to diagnose issues without opening GitHub

7. **Maintain Artifacts**: Keep test artifacts (screenshots, logs) for at least 30 days for post-mortem analysis

8. **Document Custom Notifications**: If adding custom notification logic, document in this file

## Security Considerations

1. **Webhook URLs**: Treat webhook URLs as secrets; rotate them periodically
2. **API Keys**: Use restricted API keys with minimum required permissions
3. **Sensitive Data**: Avoid including passwords, tokens, or PII in notifications
4. **Public Repositories**: Be cautious with artifact visibility in public repos
5. **Rate Limits**: Respect notification service rate limits to avoid blocking

## Related Documentation

- [E2E Testing Guide](../testing/e2e/README.md)
- [Performance Testing Guide](../testing/performance/README.md)
- [GitHub Actions Workflows](../../.github/workflows/README.md)
- [CI/CD Pipeline Documentation](../devops/cicd-pipeline.md)
- [Troubleshooting Test Failures](../testing/README.md#troubleshooting)

## Maintenance

This notification system should be reviewed quarterly to ensure:
- All notification channels are functioning
- Secrets/credentials are rotated
- Notification content remains relevant
- New test types are covered

Last Updated: 2025-10-26
