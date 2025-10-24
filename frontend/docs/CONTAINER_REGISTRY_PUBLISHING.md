# Container Registry Publishing

**Version**: 1.0.0
**Last Updated**: 2025-10-24
**Author**: DevOps Team

## Overview

This document describes the container registry integration and automated image publishing process for the frontend application. Images are published to GitHub Container Registry (GHCR) after passing all validation gates including functional testing, security scanning, and size optimization.

## Features

The container registry publishing system provides:

- **Automated Publishing**: Images automatically published after validation passes
- **Multi-Tag Strategy**: Multiple tags per image for different use cases
- **Security Gates**: Only validated images are published
- **Fork Protection**: Prevents publishing from forked repositories
- **Traceability**: Full traceability from commit to published image
- **GitHub Integration**: Native GHCR integration with GITHUB_TOKEN authentication

## Publishing Flow

### Build Pipeline

```
┌─────────────┐
│   Commit    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Build Container│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Functional Tests│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Security Scan │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Size Validation│
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│Publish to GHCR  │ ← Only if all validations pass
└─────────────────┘
```

### Validation Gates

Images are only published after passing **ALL** of the following validations:

1. **Container Build**: Image builds successfully
2. **Functional Tests**: Container starts and responds correctly
3. **Security Scan**: No critical/high vulnerabilities (configurable thresholds)
4. **Size Optimization**: Image size within acceptable limits

If any validation fails, the image is **not** published to the registry.

## Registry Configuration

### GitHub Container Registry (GHCR)

- **Registry URL**: `ghcr.io`
- **Image Namespace**: `ghcr.io/<owner>/<repo>/frontend`
- **Authentication**: GITHUB_TOKEN (automatic, no configuration required)
- **Permissions**: `packages: write` permission in workflow

### Image Naming Convention

#### Development Images

```
ghcr.io/<owner>/<repo>/frontend:dev-<short-sha>                    # Commit-based
ghcr.io/<owner>/<repo>/frontend:dev-<branch>                       # Branch-based
ghcr.io/<owner>/<repo>/frontend:dev-<branch>-<short-sha>           # Combined
ghcr.io/<owner>/<repo>/frontend:dev-<timestamp>                    # Time-based
ghcr.io/<owner>/<repo>/frontend:latest-dev                         # Latest (main only)
```

#### Production Images

```
ghcr.io/<owner>/<repo>/frontend:prod-<short-sha>                   # Commit-based
ghcr.io/<owner>/<repo>/frontend:prod-<branch>                      # Branch-based
ghcr.io/<owner>/<repo>/frontend:prod-<branch>-<short-sha>          # Combined
ghcr.io/<owner>/<repo>/frontend:prod-<timestamp>                   # Time-based
ghcr.io/<owner>/<repo>/frontend:prod-<version>-<short-sha>         # Version + commit
ghcr.io/<owner>/<repo>/frontend:latest                             # Latest (main only)
ghcr.io/<owner>/<repo>/frontend:prod-latest                        # Prod latest (main only)
ghcr.io/<owner>/<repo>/frontend:<version>                          # Semantic version (main only)
```

### Tag Examples

For commit `cb2c01f` on branch `feature/registry` with version `1.0.0`:

**Development:**
- `ghcr.io/edencnz/architecture/frontend:dev-cb2c01f`
- `ghcr.io/edencnz/architecture/frontend:dev-feature-registry`
- `ghcr.io/edencnz/architecture/frontend:dev-feature-registry-cb2c01f`
- `ghcr.io/edencnz/architecture/frontend:dev-20251024-120000`

**Production:**
- `ghcr.io/edencnz/architecture/frontend:prod-cb2c01f`
- `ghcr.io/edencnz/architecture/frontend:prod-feature-registry`
- `ghcr.io/edencnz/architecture/frontend:prod-feature-registry-cb2c01f`
- `ghcr.io/edencnz/architecture/frontend:prod-20251024-120000`
- `ghcr.io/edencnz/architecture/frontend:prod-1.0.0-cb2c01f`

**Main Branch Additional Tags:**
- `ghcr.io/edencnz/architecture/frontend:latest-dev` (development)
- `ghcr.io/edencnz/architecture/frontend:latest` (production)
- `ghcr.io/edencnz/architecture/frontend:prod-latest` (production)
- `ghcr.io/edencnz/architecture/frontend:1.0.0` (production)

## Publishing Conditions

### When Images Are Published

Images are published when:

1. ✅ **All validations pass** (functional tests, security scan, size check)
2. ✅ **Not a pull request from a fork** (security protection)
3. ✅ **Workflow has packages:write permission**

### When Images Are NOT Published

Images are **not** published when:

1. ❌ **Any validation fails** (tests, security, size)
2. ❌ **Pull request from a forked repository** (prevents malicious publishing)
3. ❌ **Build job fails** (image not created)

### Fork Protection

Pull requests from forks are protected from publishing to prevent:

- Malicious image injection
- Unauthorized registry access
- Supply chain attacks

Condition in workflow:
```yaml
if: |
  success() &&
  github.event_name != 'pull_request' ||
  (github.event_name == 'pull_request' && github.event.pull_request.head.repo.full_name == github.repository)
```

This ensures:
- Non-PR events (push, manual trigger) can publish
- PRs from same repository can publish
- PRs from forks **cannot** publish

## Using Published Images

### Pull from Registry

#### Authenticate with GHCR

```bash
# Login using GitHub Personal Access Token (PAT)
echo $GITHUB_TOKEN | docker login ghcr.io -u <username> --password-stdin

# For GitHub Actions workflows (automatic)
- name: Log in to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

#### Pull Images

```bash
# Pull by commit SHA (most reproducible)
docker pull ghcr.io/edencnz/architecture/frontend:dev-cb2c01f

# Pull by branch
docker pull ghcr.io/edencnz/architecture/frontend:dev-main

# Pull latest development (main branch only)
docker pull ghcr.io/edencnz/architecture/frontend:latest-dev

# Pull production by version + commit
docker pull ghcr.io/edencnz/architecture/frontend:prod-1.0.0-cb2c01f

# Pull production latest (main branch only)
docker pull ghcr.io/edencnz/architecture/frontend:latest
```

### Run Containers

#### Development Container

```bash
# Run with default settings
docker run -p 5173:5173 ghcr.io/edencnz/architecture/frontend:dev-cb2c01f

# Run with environment variables
docker run -p 5173:5173 \
  -e VITE_API_URL=http://localhost:8000 \
  ghcr.io/edencnz/architecture/frontend:dev-cb2c01f

# Run with volume mount for live code changes
docker run -p 5173:5173 \
  -v $(pwd)/src:/app/src \
  ghcr.io/edencnz/architecture/frontend:dev-cb2c01f
```

#### Production Container

```bash
# Run production container
docker run -p 80:80 ghcr.io/edencnz/architecture/frontend:latest

# Run with custom port
docker run -p 8080:80 ghcr.io/edencnz/architecture/frontend:prod-1.0.0-cb2c01f

# Run with environment-specific configuration
docker run -p 80:80 \
  -e VITE_API_URL=https://api.production.com \
  -e VITE_APP_NAME="Production App" \
  ghcr.io/edencnz/architecture/frontend:latest
```

### Docker Compose Integration

```yaml
version: '3.8'

services:
  frontend:
    image: ghcr.io/edencnz/architecture/frontend:latest
    ports:
      - "80:80"
    environment:
      VITE_API_URL: https://api.production.com
      VITE_APP_NAME: Production Application
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

## CI/CD Integration

### Workflow Jobs

The publishing process is integrated into the GitHub Actions workflow with two separate publishing jobs:

**Job 8: publish-container-dev**
- Runs after: `build-container-dev` and `security-scan-dev`
- Publishes development images after validation
- Tags include dev prefix

**Job 10: publish-container-prod**
- Runs after: `build-container-prod` and `security-scan-prod`
- Publishes production images after validation
- Tags include prod prefix and version information

### Publish Job Workflow

Each publishing job performs the following steps:

1. **Checkout code**
2. **Set up Docker Buildx** (for efficient caching)
3. **Generate image tags** (multiple tags per image)
4. **Log in to GHCR** (using GITHUB_TOKEN)
5. **Build and push** (leverages existing caches)
6. **Verify published image** (display digest and tags)

### GitHub Actions Outputs

After publishing, the workflow provides comprehensive information in GitHub Step Summary:

- Registry and image name
- All published tags
- Image digest (SHA256)
- Pull command examples
- Image metadata (commit, branch, version, workflow run)
- Security and quality gate status

## Image Verification

### Verify Image Digest

Images are immutable and identified by SHA256 digest:

```bash
# Inspect image digest
docker inspect ghcr.io/edencnz/architecture/frontend:latest \
  --format='{{index .RepoDigests 0}}'

# Pull by digest (most secure)
docker pull ghcr.io/edencnz/architecture/frontend@sha256:abc123...
```

### Verify Image Metadata

Check image labels and metadata:

```bash
# View image labels
docker inspect ghcr.io/edencnz/architecture/frontend:latest \
  --format='{{json .Config.Labels}}' | jq

# Check creation date
docker inspect ghcr.io/edencnz/architecture/frontend:latest \
  --format='{{.Created}}'

# View image history
docker history ghcr.io/edencnz/architecture/frontend:latest
```

### Verify Security Scan Results

Security scan results are available in:

1. **GitHub Security Tab**: Code scanning alerts for container vulnerabilities
2. **Workflow Artifacts**: SARIF and JSON scan reports (30-day retention)
3. **GitHub Step Summary**: Vulnerability summary with threshold evaluation

## Image Traceability

### From Image to Source

Every published image can be traced back to its source:

1. **Image Tag**: Contains commit SHA (e.g., `dev-cb2c01f`)
2. **Workflow Run**: Link provided in GitHub Step Summary
3. **GitHub Security Tab**: SARIF uploads linked to specific commits
4. **Artifacts**: Scan results and size analysis reports

### Example Traceability Workflow

```bash
# 1. Pull image
docker pull ghcr.io/edencnz/architecture/frontend:dev-cb2c01f

# 2. Inspect to get commit SHA
docker inspect ghcr.io/edencnz/architecture/frontend:dev-cb2c01f \
  --format='{{.Config.Labels}}'

# 3. View commit in GitHub
# Navigate to: https://github.com/<owner>/<repo>/commit/cb2c01f

# 4. View workflow run that built the image
# Link available in GitHub Step Summary of the build
```

## Security Best Practices

### Registry Access Control

1. **Use Fine-Grained Personal Access Tokens (PAT)**
   - Grant only `read:packages` permission for pulling
   - Grant `write:packages` only when necessary
   - Set expiration dates and rotate regularly

2. **Protect GITHUB_TOKEN**
   - Never log or expose in workflow outputs
   - Use only in authenticated steps
   - Automatic scoping to repository

3. **Image Signing** (Future Enhancement)
   - Consider implementing Sigstore/cosign for image signing
   - Verify signatures before deployment
   - Integrate signature verification in deployment pipelines

### Vulnerability Management

1. **Automated Scanning**
   - All images scanned with Trivy before publishing
   - SARIF results uploaded to GitHub Security tab
   - Configurable severity thresholds

2. **Threshold Configuration**
   - Development: Max 5 critical, 10 high vulnerabilities
   - Production: 0 critical, max 5 high vulnerabilities
   - Adjust thresholds in workflow file as needed

3. **Remediation Workflow**
   - Review vulnerabilities in GitHub Security tab
   - Update dependencies or base images
   - Rebuild and re-scan images
   - Track remediation progress over time

### Supply Chain Security

1. **Immutable Tags**
   - Use commit SHA tags for reproducibility
   - Never rely on `latest` tag in production
   - Pull by digest for maximum security

2. **Fork Protection**
   - Prevent publishing from forks
   - Review external contributions carefully
   - Require approval for dependency updates

3. **Audit Trail**
   - All publishes logged in workflow runs
   - GitHub audit log tracks registry access
   - SARIF uploads provide vulnerability history

## Troubleshooting

### Publishing Failures

**Issue**: Image not published after successful build

**Possible Causes:**
1. ❌ Validation failed (check functional tests, security scan, size check)
2. ❌ Pull request from fork (expected behavior for security)
3. ❌ Missing `packages: write` permission
4. ❌ GHCR authentication failed

**Resolution:**
- Review workflow logs for specific failure
- Check GitHub Step Summary for validation results
- Verify workflow permissions in YAML file
- Ensure GITHUB_TOKEN has correct permissions

### Authentication Errors

**Issue**: `unauthorized: authentication required`

**Resolution:**
```bash
# Re-authenticate with GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u <username> --password-stdin

# Verify token has correct permissions
# For PAT: read:packages (pull) or write:packages (push)
```

### Image Not Found

**Issue**: `Error: manifest unknown`

**Resolution:**
1. Verify image name is lowercase: `ghcr.io/edencnz/architecture/frontend`
2. Check tag exists in registry (not all branches publish to `latest`)
3. Ensure image was successfully published (check workflow logs)
4. Verify you have read access to the repository/package

### Large Image Push Failures

**Issue**: Image push times out or fails

**Resolution:**
1. Image too large - review size optimization (run `analyze-image-size.sh`)
2. Network issues - retry workflow
3. Layer count exceeds limits - consolidate RUN commands in Dockerfile
4. Registry storage quota - clean up old images

## Maintenance

### Cleaning Up Old Images

#### Manual Cleanup (GitHub UI)

1. Navigate to repository → Packages
2. Select frontend package
3. Click on "Package settings"
4. Delete old/unused versions

#### Automated Cleanup (Future Enhancement)

Consider implementing automated cleanup policies:

- Retain images from main branch indefinitely
- Delete feature branch images after 30 days
- Keep last 10 images per branch
- Remove images when branch is deleted

### Updating Image Tags

**Never modify existing tags** - tags should be immutable for reliability.

Instead:
1. Create new tags for corrected images
2. Update deployments to use new tags
3. Leave old tags for audit/rollback purposes

### Monitoring Registry Usage

Check registry usage regularly:

1. **Storage Quota**: Monitor package storage in GitHub settings
2. **Pull Statistics**: Review package download statistics
3. **Vulnerability Trends**: Track security scan results over time
4. **Build Performance**: Monitor image build and push times

## Reference Documentation

### Related Documents

- [Container Build Caching](./CONTAINER_BUILD_CACHING.md) - Build performance optimization
- [Container Security Scanning](./CONTAINER_SECURITY_SCANNING.md) - Vulnerability scanning details
- [Container Image Tagging](./CONTAINER_IMAGE_TAGGING.md) - Tagging strategy documentation
- [Container Testing](./CONTAINER_TESTING.md) - Functional testing approach

### External References

- [GitHub Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Docker Login Action](https://github.com/docker/login-action)
- [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)

## Version History

| Version | Date       | Changes                                    |
|---------|------------|--------------------------------------------|
| 1.0.0   | 2025-10-24 | Initial documentation for registry publishing |

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review workflow logs in GitHub Actions
3. Consult related documentation
4. Open an issue in the repository
