# Container Image Tagging Strategy

## Overview

This document describes the comprehensive container image tagging strategy implemented for the frontend application. The tagging strategy ensures that all container images are properly versioned, traceable, and identifiable across different environments and deployment scenarios.

## Tagging Strategy

### Tag Types

Our tagging strategy uses multiple tags per image to support different use cases:

1. **Commit-based tags**: Enable tracing images back to exact source code
2. **Branch-based tags**: Help identify which branch an image was built from
3. **Timestamp-based tags**: Provide chronological ordering of builds
4. **Version-based tags**: Support semantic versioning for releases
5. **Latest tags**: Mark the most recent stable images

All tags point to the same image digest, ensuring consistency and reproducibility.

### Development Container Tags

Development containers receive the following tags:

```
frontend:dev-<short-sha>                    # e.g., frontend:dev-cb2c01f
frontend:dev-<branch>                       # e.g., frontend:dev-feature-8-dockerize-frontend-and-backend
frontend:dev-<branch>-<short-sha>           # e.g., frontend:dev-feature-8-dockerize-frontend-and-backend-cb2c01f
frontend:dev-<timestamp>                    # e.g., frontend:dev-20251024-143052
frontend:latest-dev                         # Only for main branch builds
```

**Rationale**:
- `dev-<short-sha>`: Primary tag for commit traceability (7-character SHA)
- `dev-<branch>`: Identifies the latest build from a specific branch
- `dev-<branch>-<short-sha>`: Combines branch and commit for complete context
- `dev-<timestamp>`: Enables chronological sorting (format: YYYYMMDD-HHMMSS)
- `latest-dev`: Points to the latest main branch development build

### Production Container Tags

Production containers receive the following tags:

```
frontend:prod-<short-sha>                   # e.g., frontend:prod-cb2c01f
frontend:prod-<branch>                      # e.g., frontend:prod-main
frontend:prod-<branch>-<short-sha>          # e.g., frontend:prod-main-cb2c01f
frontend:prod-<timestamp>                   # e.g., frontend:prod-20251024-143052
frontend:prod-<version>-<short-sha>         # e.g., frontend:prod-1.0.0-cb2c01f
frontend:latest                             # Only for main branch builds
frontend:prod-latest                        # Only for main branch builds
frontend:<version>                          # Only for main branch builds (e.g., frontend:1.0.0)
```

**Rationale**:
- `prod-<short-sha>`: Primary tag for commit traceability
- `prod-<branch>`: Identifies the latest production build from a branch
- `prod-<branch>-<short-sha>`: Combines branch and commit for complete context
- `prod-<timestamp>`: Enables chronological sorting
- `prod-<version>-<short-sha>`: Links semantic version to specific commit
- `latest`: Standard Docker tag pointing to latest production release
- `prod-latest`: Explicit production latest tag
- `<version>`: Semantic version tag for releases (e.g., 1.0.0)

### Tag Sanitization

Branch names are sanitized for Docker tag compatibility:
- Forward slashes (`/`) are replaced with hyphens (`-`)
- Only alphanumeric characters, dots (`.`), underscores (`_`), and hyphens (`-`) are allowed
- Other characters are replaced with hyphens

Examples:
- `feature/tagging-strategy` → `feature-tagging-strategy`
- `bugfix/issue#123` → `bugfix-issue-123`

## Implementation

### GitHub Actions Workflow

The tagging strategy is implemented in `.github/workflows/frontend-ci.yml` using dedicated tag generation steps:

#### Development Container (Job: build-container-dev)

```yaml
- name: Generate image tags
  id: meta
  run: |
    # Extract branch name and sanitize for Docker tag format
    BRANCH_NAME="${{ github.ref_name }}"
    SANITIZED_BRANCH=$(echo "$BRANCH_NAME" | sed 's/\//-/g' | sed 's/[^a-zA-Z0-9._-]/-/g')

    # Extract short SHA (first 7 characters)
    SHORT_SHA="${{ github.sha }}"
    SHORT_SHA="${SHORT_SHA:0:7}"

    # Build timestamp for ordering
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)

    # Generate comprehensive tag list
    TAGS="frontend:dev-${SHORT_SHA}"
    TAGS="${TAGS},frontend:dev-${SANITIZED_BRANCH}"
    TAGS="${TAGS},frontend:dev-${SANITIZED_BRANCH}-${SHORT_SHA}"
    TAGS="${TAGS},frontend:dev-${TIMESTAMP}"

    # Add 'latest-dev' tag for main branch builds
    if [ "$BRANCH_NAME" = "main" ]; then
      TAGS="${TAGS},frontend:latest-dev"
    fi

    echo "tags=${TAGS}" >> $GITHUB_OUTPUT
    echo "short_sha=${SHORT_SHA}" >> $GITHUB_OUTPUT

- name: Build development container
  uses: docker/build-push-action@v5
  with:
    tags: ${{ steps.meta.outputs.tags }}
```

#### Production Container (Job: build-container-prod)

```yaml
- name: Generate image tags
  id: meta
  run: |
    # Extract branch name and sanitize
    BRANCH_NAME="${{ github.ref_name }}"
    SANITIZED_BRANCH=$(echo "$BRANCH_NAME" | sed 's/\//-/g' | sed 's/[^a-zA-Z0-9._-]/-/g')

    # Extract short SHA
    SHORT_SHA="${{ github.sha }}"
    SHORT_SHA="${SHORT_SHA:0:7}"

    # Build timestamp
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)

    # Version (currently hardcoded, will be extracted from package.json)
    VERSION="1.0.0"

    # Generate comprehensive tag list
    TAGS="frontend:prod-${SHORT_SHA}"
    TAGS="${TAGS},frontend:prod-${SANITIZED_BRANCH}"
    TAGS="${TAGS},frontend:prod-${SANITIZED_BRANCH}-${SHORT_SHA}"
    TAGS="${TAGS},frontend:prod-${TIMESTAMP}"
    TAGS="${TAGS},frontend:prod-${VERSION}-${SHORT_SHA}"

    # Add 'latest' tags for main branch builds
    if [ "$BRANCH_NAME" = "main" ]; then
      TAGS="${TAGS},frontend:latest"
      TAGS="${TAGS},frontend:prod-latest"
      TAGS="${TAGS},frontend:${VERSION}"
    fi

    echo "tags=${TAGS}" >> $GITHUB_OUTPUT
    echo "version=${VERSION}" >> $GITHUB_OUTPUT

- name: Build production container
  uses: docker/build-push-action@v5
  with:
    tags: ${{ steps.meta.outputs.tags }}
```

### Tag Visibility

All generated tags are displayed in the GitHub Actions Step Summary for easy verification:

```markdown
## Container Image Tags

The following tags will be applied to the production container image:

```
frontend:prod-cb2c01f
frontend:prod-feature-8-dockerize-frontend-and-backend
frontend:prod-feature-8-dockerize-frontend-and-backend-cb2c01f
frontend:prod-20251024-143052
frontend:prod-1.0.0-cb2c01f
```

**Commit**: cb2c01fb1234567890abcdef1234567890abcdef
**Short SHA**: cb2c01f
**Branch**: feature/8-dockerize-frontend-and-backend
**Sanitized Branch**: feature-8-dockerize-frontend-and-backend
**Timestamp**: 20251024-143052
**Version**: 1.0.0
```

## Usage Examples

### Finding Images

#### By Commit SHA

To find the image built from a specific commit:

```bash
# Using full SHA
docker pull frontend:prod-cb2c01f

# This works for both development and production
docker pull frontend:dev-cb2c01f
docker pull frontend:prod-cb2c01f
```

#### By Branch Name

To find the latest image from a specific branch:

```bash
# Latest development image from main branch
docker pull frontend:dev-main

# Latest development image from feature branch
docker pull frontend:dev-feature-8-dockerize-frontend-and-backend

# Latest production image from main branch
docker pull frontend:prod-main
```

#### By Version

To find a specific version (production only):

```bash
# Specific version
docker pull frontend:1.0.0

# Version with commit traceability
docker pull frontend:prod-1.0.0-cb2c01f
```

#### Latest Production Image

To pull the latest production image:

```bash
# Standard Docker latest tag
docker pull frontend:latest

# Explicit production latest
docker pull frontend:prod-latest
```

### Tracing Images to Source Code

Given an image tag, you can trace it back to the source code:

1. **From commit-based tag** (`frontend:prod-cb2c01f`):
   ```bash
   # The short SHA is in the tag
   git show cb2c01f
   ```

2. **From branch-commit tag** (`frontend:prod-main-cb2c01f`):
   ```bash
   # You know both the branch and commit
   git log main --oneline | grep cb2c01f
   ```

3. **From image metadata**:
   ```bash
   # Inspect image labels (future enhancement)
   docker inspect frontend:latest | jq '.[0].Config.Labels'
   ```

### Verifying Tag Consistency

All tags for the same build point to the same image digest:

```bash
# Get digest for each tag
docker inspect frontend:prod-cb2c01f -f '{{.Id}}'
docker inspect frontend:prod-main -f '{{.Id}}'
docker inspect frontend:latest -f '{{.Id}}'

# All should return the same digest SHA256
```

## Tag Lifecycle

### Feature Branch Workflow

1. **Push to feature branch** → Creates feature-specific tags:
   - `frontend:dev-feature-X-abc1234`
   - `frontend:prod-feature-X-abc1234`

2. **Merge to main** → Creates/updates main branch tags:
   - `frontend:dev-main`
   - `frontend:prod-main`
   - `frontend:latest`
   - `frontend:latest-dev`
   - `frontend:1.0.0`

3. **Deploy to production** → Pull using appropriate tag:
   - Development: `frontend:latest-dev`
   - Staging: `frontend:prod-main`
   - Production: `frontend:latest` or `frontend:1.0.0`

### Tag Retention

Tags are applied during the build process but not automatically cleaned up. When implementing Story 9.8 (Container Registry Integration), consider:

1. **Retention policies**:
   - Keep all tags for main branch builds indefinitely
   - Keep feature branch tags for 30-90 days
   - Clean up old timestamp-based tags after 90 days

2. **Image pruning**:
   - Remove untagged images (dangling images)
   - Remove images not referenced by any tags

## Best Practices

### For Developers

1. **Use commit-based tags for debugging**:
   ```bash
   docker run frontend:dev-abc1234
   ```

2. **Use branch tags for local testing**:
   ```bash
   docker run frontend:dev-feature-my-feature
   ```

3. **Never rely on `latest` in production**:
   - Use semantic version tags: `frontend:1.0.0`
   - Or commit-based tags: `frontend:prod-abc1234`

### For DevOps Engineers

1. **Tag immutability**:
   - Commit-based tags are immutable (never overwritten)
   - Branch-based tags are mutable (updated with each build)
   - `latest` tags are mutable (updated with each main build)

2. **Deployment strategies**:
   - **Development**: Use `latest-dev` for continuous deployment
   - **Staging**: Use `prod-main` for testing latest changes
   - **Production**: Use semantic version tags for releases

3. **Rollback capability**:
   - Always tag production deployments with semantic versions
   - Keep commit-based tags for quick rollback to any commit
   - Document deployed versions in deployment logs

### For CI/CD Pipelines

1. **When building locally**:
   ```bash
   # Use timestamp for unique local builds
   docker build -t frontend:local-$(date +%Y%m%d-%H%M%S) .
   ```

2. **When publishing to registry** (Story 9.8):
   ```bash
   # Push all tags to ensure registry has complete history
   docker push --all-tags frontend
   ```

3. **When deploying**:
   ```bash
   # Use specific version tags, never 'latest'
   docker pull frontend:1.0.0
   docker run frontend:1.0.0
   ```

## Future Enhancements

### Semantic Version Extraction

Currently, the version is hardcoded (`1.0.0`). Future enhancement will extract version from `package.json`:

```yaml
- name: Extract version from package.json
  id: version
  run: |
    VERSION=$(jq -r '.version' frontend/package.json)
    echo "version=${VERSION}" >> $GITHUB_OUTPUT
```

### Image Labels

Add OCI-compliant labels to images for better traceability:

```dockerfile
LABEL org.opencontainers.image.created="${BUILD_TIMESTAMP}"
LABEL org.opencontainers.image.revision="${GITHUB_SHA}"
LABEL org.opencontainers.image.source="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.ref.name="${GITHUB_REF_NAME}"
```

### Git Tag Integration

For releases, create Git tags that match semantic versions:

```bash
# When releasing version 1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# CI detects git tag and creates matching image tag
docker tag frontend:prod-abc1234 frontend:1.0.0
```

## Troubleshooting

### Tag Not Found

**Problem**: `docker pull frontend:dev-feature-X` fails with "tag not found"

**Solutions**:
1. Verify the branch name was sanitized correctly:
   ```bash
   # feature/X becomes feature-X
   echo "feature/X" | sed 's/\//-/g'
   ```

2. Check if the build completed successfully in GitHub Actions

3. Verify the tag was generated in the workflow logs

### Multiple Tags for Same Image

**Problem**: Why does my image have so many tags?

**Answer**: This is intentional. All tags point to the same image digest, consuming no additional storage. Multiple tags enable different use cases:
- Developers use commit tags for debugging
- CI/CD uses branch tags for automated testing
- Deployments use version tags for stability

### Wrong Image Version

**Problem**: Pulled `frontend:latest` but got wrong version

**Solution**:
1. Don't use `latest` in production
2. Use semantic version tags: `frontend:1.0.0`
3. Verify the image digest matches expected commit:
   ```bash
   docker inspect frontend:1.0.0 -f '{{.Config.Labels}}'
   ```

## Related Documentation

- [Container Build Caching](CONTAINER_BUILD_CACHING.md) - Build performance optimization
- [Container Security Scanning](CONTAINER_SECURITY_SCANNING.md) - Vulnerability scanning
- [Container Testing](CONTAINER_TESTING.md) - Functional testing
- [Image Size Optimization](IMAGE_SIZE_OPTIMIZATION.md) - Size validation

## References

- [Docker Tagging Best Practices](https://docs.docker.com/engine/reference/commandline/tag/)
- [OCI Image Spec](https://github.com/opencontainers/image-spec/blob/main/annotations.md)
- [Semantic Versioning](https://semver.org/)
- [GitHub Actions Context Variables](https://docs.github.com/en/actions/learn-github-actions/contexts)

## Version History

- **2025-10-24**: Initial implementation (Story 9.9)
  - Commit-based tagging with short SHA (7 characters)
  - Branch-based tagging with sanitization
  - Timestamp-based tagging for chronological ordering
  - Version-based tagging for production images
  - Latest tags for main branch builds
  - Comprehensive tag visibility in CI/CD
