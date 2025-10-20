# GitHub Actions Workflows

This directory contains automated workflows for the architecture repository.

## Documentation

- **Automated CI/CD Failure Resolution**: [AUTOMATED_CI_CD_FAILURE_RESOLUTION.md](./AUTOMATED_CI_CD_FAILURE_RESOLUTION.md) - Complete system documentation
- **Quick Reference**: [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Quick start guide for developers
- **Duplicate Detection**: [DUPLICATE_DETECTION_FLOW.md](./DUPLICATE_DETECTION_FLOW.md) - Duplicate detection flow details

## Available Workflows

### 🤖 Automated CI/CD Failure Resolution System

**Purpose**: Automatically detects, logs, and manages CI/CD failures in GitHub Actions workflows.

**Core Workflows**:
- `bug-logger.yml` - Creates GitHub issues for CI/CD failures
- `bug-resolver.yml` - Manages issue labels based on fix outcomes
- `issue-event-listener.yml` - Detects CI failure issues and triggers automation
- `fix-trigger.yml` - Adds automation markers to issues for manual fix execution

**Application Workflows**:
- `frontend-ci.yml` - Frontend CI/CD pipeline with failure logging
- `backend-ci.yml` - Backend CI/CD pipeline with failure logging

**Features**:
- Automatic issue creation when CI jobs fail
- Intelligent duplicate detection to prevent noise
- Retry tracking for fix attempts
- Automated fix triggering and status management
- Complete issue lifecycle management

**Getting Started**:
- For developers: See [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- For system details: See [AUTOMATED_CI_CD_FAILURE_RESOLUTION.md](./AUTOMATED_CI_CD_FAILURE_RESOLUTION.md)

**Quick Start**:
```bash
# View your CI failure issues
gh issue list --label "ci-failure" --state open --assignee @me

# Run automated fix (if using Claude CLI)
claude /fix gha

# Or manually fix and commit
git commit -m "Implementation of bug-github-issue-NUMBER-description"
```

---

### 🔄 Sync to Proform Repository

**File**: `sync-to-proform.yml`

**Purpose**: Syncs the `.claude` and `context` folders to the [EdenCoNz/proform](https://github.com/EdenCoNz/proform) repository.

**Trigger**: Manual only (workflow_dispatch)

#### Setup Instructions

Before running this workflow for the first time, you must configure authentication:

##### 1. Create a Personal Access Token (PAT)

Choose one of the following options:

**Option A: Fine-Grained PAT (Recommended)**

1. Go to [GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens](https://github.com/settings/tokens?type=beta)
2. Click "Generate new token"
3. Configure:
   - **Token name**: `Architecture to Proform Sync`
   - **Expiration**: Choose an appropriate duration (90 days recommended)
   - **Repository access**: Only select repositories → `EdenCoNz/proform`
   - **Repository permissions**:
     - Contents: **Read and write** (required for push)
4. Click "Generate token"
5. **Copy the token immediately** (you won't be able to see it again)

**Option B: Classic PAT**

1. Go to [GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Configure:
   - **Note**: `Architecture to Proform Sync`
   - **Expiration**: Choose an appropriate duration
   - **Scopes**: Select `repo` (Full control of private repositories)
4. Click "Generate token"
5. **Copy the token immediately**

##### 2. Add Secret to Repository

1. Navigate to this repository's settings: [Settings → Secrets and variables → Actions](../../settings/secrets/actions)
2. Click "New repository secret"
3. Configure:
   - **Name**: `TARGET_REPO_PAT`
   - **Value**: Paste the token you copied
4. Click "Add secret"

#### How to Run the Workflow

##### Option 1: Via GitHub UI (Recommended)

1. Go to the [Actions tab](../../actions)
2. Click "Sync to Proform Repository" in the left sidebar
3. Click "Run workflow" button
4. Choose options:
   - **Branch**: `main` (or your current branch)
   - **Dry run**: Check this to test without pushing changes
5. Click "Run workflow"

##### Option 2: Via GitHub CLI

```bash
# Standard sync
gh workflow run sync-to-proform.yml

# Dry run (test without pushing)
gh workflow run sync-to-proform.yml -f dry_run=true
```

#### What Gets Synced

The workflow syncs these folders to the target repository:

- **`.claude/`** - Claude AI commands, agents, and configurations
- **`context/`** - Project context and documentation

The sync operation:
1. ✅ Performs a clean sync (removes old files, adds new ones)
2. ✅ Commits changes with detailed commit message
3. ✅ Includes source commit SHA for traceability
4. ✅ Pushes to the `main` branch of the target repository

#### Dry Run Mode

Use dry run mode to test the workflow without actually pushing changes:

- The workflow will clone the target repository
- It will create commits locally
- It will show what would be pushed
- It will **NOT** push to the target repository

This is useful for:
- Testing the workflow after setup
- Verifying what changes will be synced
- Troubleshooting issues

#### Monitoring

After running the workflow:

1. Click on the workflow run in the Actions tab
2. View the detailed logs for each step
3. Check the "Summary" step for operation results
4. Verify changes in the [target repository](https://github.com/EdenCoNz/proform)

#### Security Considerations

✅ **Best Practices Implemented**:

- Manual trigger only (no automatic execution)
- Explicit least-privilege permissions
- PAT scoped to specific repository (fine-grained)
- No hardcoded credentials
- Comprehensive validation before pushing
- Timeout limits to prevent runaway jobs

⚠️ **Security Notes**:

- The PAT is stored as an encrypted secret
- Only repository administrators can add/modify secrets
- The token is never exposed in logs
- Consider rotating the PAT every 90 days

#### Troubleshooting

**Error: "TARGET_REPO_PAT secret not found"**
- Solution: Follow setup instructions above to create and add the secret

**Error: "Authentication failed"**
- Solution: Verify the PAT is valid and has correct permissions
- Solution: Regenerate the PAT and update the secret

**Error: "Permission denied"**
- Solution: Ensure the PAT has "Contents: Write" permission for the target repository
- Solution: Verify you have write access to EdenCoNz/proform

**Error: "Folder not found"**
- Solution: Ensure `.claude` and `context` folders exist in the source repository

**No changes detected**
- Info: The folders are already in sync - this is expected behavior

#### Maintenance

**PAT Expiration**:
- Set a calendar reminder before your PAT expires
- Regenerate and update the secret before expiration
- Consider using 90-day expiration for security

**Workflow Updates**:
- The workflow follows GitHub Actions best practices
- Action versions are pinned to specific SHAs for security
- Review and update action versions quarterly

#### Support

For issues or questions:
1. Check the workflow run logs in the Actions tab
2. Review the troubleshooting section above
3. Contact the repository maintainers

---

**Last Updated**: 2025-10-15
**Workflow Version**: 1.0.0
