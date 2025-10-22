# GitHub Actions Workflows

This directory contains automated workflows for the architecture repository.

## Available Workflows

### 🤖 Auto-Close Issue (Reusable Workflow)

**File**: `auto-close-issue.yml`

**Purpose**: Automatically closes GitHub issues when referenced in commit messages on successful CI/CD runs, with intelligent bulk-closing of related issues.

**Type**: Reusable workflow (called by other workflows like `frontend-ci.yml`)

#### Features

1. **Single Issue Closure**: Closes the issue referenced in commit messages (e.g., "Fix issue #117")
2. **Metadata Extraction**: Parses issue body for `featureID` and `featureName` metadata
3. **Bulk Issue Closure**: Automatically closes all other open issues with matching metadata
4. **Comprehensive Logging**: Detailed step summaries in GitHub Actions UI

#### How It Works

When a commit message contains "Fix issue #N" (case-insensitive) and all CI jobs succeed:

1. **Parse Commit Message**: Extracts issue number from commit message
2. **Validate Issue**: Checks if issue exists and is open
3. **Extract Metadata**: Parses issue body for metadata table:
   ```markdown
   | featureID | 5 |
   | featureName | feature/5-add-simple-button-that-says-hello-on-main-page |
   ```
4. **Close Initial Issue**: Closes the referenced issue with commit details
5. **Query Open Issues**: Fetches all other open issues
6. **Match and Close**: Closes all issues with matching `featureID` and `featureName`
7. **Report Summary**: Provides detailed summary of all closed issues

#### Usage Example

```yaml
jobs:
  auto-close:
    needs: [build, test, lint]  # Runs after all jobs succeed
    if: success() && github.ref == 'refs/heads/main'
    uses: ./.github/workflows/auto-close-issue.yml
    with:
      commit-message: ${{ github.event.head_commit.message }}
      repository: ${{ github.repository }}
      sha: ${{ github.sha }}
      workflow-name: 'Frontend CI/CD'
```

#### Edge Cases Handled

- **No Metadata**: If featureID is missing or "N/A", only closes the referenced issue
- **No Matches**: Reports "No additional issues found" if no other issues match
- **Partial Failures**: Continues closing issues even if some fail, reports failures
- **Already Closed**: Skips if the referenced issue is already closed
- **Non-existent Issue**: Gracefully handles if issue number doesn't exist

#### Example Scenarios

**Scenario 1: Multiple Related Failures**
- Issue #117: ESLint failure (featureID=5, featureName=feature/5-...)
- Issue #118: TypeScript failure (featureID=5, featureName=feature/5-...)
- Issue #119: Test failure (featureID=5, featureName=feature/5-...)

Commit message: "Fix issue #117"

Result: All three issues (#117, #118, #119) are closed with appropriate comments

**Scenario 2: No Metadata**
- Issue #50: Regular bug report (no metadata table)

Commit message: "Fix issue #50"

Result: Only issue #50 is closed, no bulk closing attempted

**Scenario 3: Different Features**
- Issue #117: Feature 5 failure
- Issue #120: Feature 6 failure

Commit message: "Fix issue #117"

Result: Only issue #117 is closed, issue #120 remains open

#### Permissions Required

```yaml
permissions:
  issues: write    # Close issues and add comments
  contents: read   # Access repository metadata
```

#### Testing

A test script is provided to validate the enhancement logic:

```bash
cd .github/workflows
./test-auto-close-enhancement.sh
```

The test validates:
- Metadata extraction from issue bodies
- JSON parsing and issue matching logic
- Handling of missing metadata
- Python script functionality

#### Step Summary Output

The workflow provides detailed output in GitHub Actions Step Summary:

```
## Auto-Close Issue Check

Commit message: Fix issue #117
Found issue reference: #117

Extracted metadata:
- featureID: 5
- featureName: feature/5-add-simple-button-that-says-hello-on-main-page

✅ Successfully closed issue #117

---

## Bulk Close Matching Issues

Searching for issues with matching metadata:
- featureID: 5
- featureName: feature/5-add-simple-button-that-says-hello-on-main-page

Found 2 additional issue(s) with matching metadata:

Closing issue #118...
  ✅ Successfully closed issue #118
Closing issue #119...
  ✅ Successfully closed issue #119

---

## Summary

- Initial issue closed: #117
- Additional issues closed: 2
Total issues closed: 3
```

#### Troubleshooting

**Issue not closing**
- Verify commit message contains "Fix issue #N" (case-insensitive)
- Check workflow has `issues: write` permission
- Ensure issue is open (not already closed)
- Verify workflow runs on successful job completion

**Bulk close not working**
- Confirm initial issue has valid metadata table
- Check featureID is not "N/A"
- Verify other issues have identical featureID and featureName
- Review Step Summary for detailed error messages

**Some issues fail to close**
- Check GitHub API rate limits
- Verify all issues are in OPEN state
- Review individual failure messages in Step Summary
- Check repository permissions

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
