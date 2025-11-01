# GitHub Actions Failure Fix - Deploy to Staging

## Summary of the Issue

The **"Deploy to Staging"** job failed at the **"Verify staging deployment"** step with exit code 1.

**Root Causes Identified:**
1. Potential missing GitHub environment configuration
2. Missing or undefined SERVER_HOST secret
3. Bug in health check verification script (duplicate curl calls)

## Fixes Applied

### 1. Health Check Verification Script Improvements

**File**: `/home/ed/Dev/architecture/.github/workflows/unified-ci-cd.yml`

**Changes Made:**
1. Added validation to check if `SERVER_HOST` secret is defined (lines 786-791)
2. Fixed duplicate curl execution issue (lines 833-860)
3. Improved HTTP status code extraction using curl write-out format

### 2. Required Manual Actions

#### A. Configure GitHub Environments

**Go to**: https://github.com/EdenCoNz/architecture/settings/environments

**Create/Verify These Environments** (case-sensitive names):

1. **Staging** (with capital 'S')
   - Add environment URL: `https://staging.edenco.online`
   - Configure these secrets:
     - `SERVER_HOST` - Your staging server hostname/IP
     - `SERVER_USER` - SSH username for deployment
     - `DB_PASSWORD` - PostgreSQL password for staging
     - `REDIS_PASSWORD` - Redis password for staging
     - `SECRET_KEY` - Django secret key for staging

2. **Production** (with capital 'P')
   - Add environment URL: `https://yourdomain.com` (update as needed)
   - Configure same secrets as above but with production values

#### B. Verify Repository Secrets

**Go to**: https://github.com/EdenCoNz/architecture/settings/secrets/actions

**Ensure These Repository-Level Secrets Exist**:
- `TS_OAUTH_CLIENT_ID` - Tailscale OAuth client ID
- `TS_OAUTH_SECRET` - Tailscale OAuth secret
- `SSH_PRIVATE_KEY` - SSH private key for server access
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

## Testing the Fix

After configuring the environments and secrets:

1. **Trigger a new workflow run**:
   ```bash
   git add .github/workflows/unified-ci-cd.yml
   git commit -m "Fix: Improve staging deployment verification and handle undefined secrets"
   git push origin main
   ```

2. **Monitor the workflow**:
   - Go to: https://github.com/EdenCoNz/architecture/actions
   - Watch the "Unified CI/CD Pipeline" workflow
   - Check if the "Deploy to Staging" job passes

## Troubleshooting

If the deployment still fails after these fixes:

### 1. Check Environment Configuration
- Verify environment name is exactly "Staging" (capital S)
- Ensure all required secrets are configured in the environment
- Check that secrets have values (not empty)

### 2. Validate Tailscale Connection
- Ensure Tailscale OAuth credentials are valid
- Check if the CI runner can connect to your Tailscale network
- Verify the server is accessible via Tailscale

### 3. Check Server Configuration
- SSH into the server and verify Docker is running
- Check if port 80 is accessible
- Verify nginx is configured and running
- Check if the health endpoint `/api/v1/status/` is implemented

### 4. Review Detailed Logs
- Click on the failed job in GitHub Actions
- Expand the "Verify staging deployment" step
- Look for specific error messages about:
  - Missing secrets (will show "SERVER_HOST secret is not configured")
  - Connection failures (will show curl exit codes)
  - HTTP status codes (non-200 responses)

## Additional Recommendations

1. **Add Environment Protection Rules** (optional but recommended):
   - Go to environment settings
   - Add required reviewers for production deployments
   - Set deployment branches (e.g., only from main)

2. **Monitor Secret Expiration**:
   - Set reminders for SSH key rotation
   - Monitor Tailscale OAuth token expiration
   - Rotate database passwords periodically

3. **Test Locally First**:
   ```bash
   # Test the health endpoint manually
   curl -v http://your-staging-server/api/v1/status/
   ```

## Commit Message for the Fix

```
Fix: Improve staging deployment verification and handle undefined secrets

- Add validation for SERVER_HOST secret before attempting health check
- Fix duplicate curl execution in health check verification
- Improve HTTP status code extraction using curl write-out format
- Add better error messages for troubleshooting deployment failures

This resolves the exit code 1 error in the "Verify staging deployment" step
by properly handling cases where environment secrets may not be configured
and eliminating redundant network calls during health checks.
```
