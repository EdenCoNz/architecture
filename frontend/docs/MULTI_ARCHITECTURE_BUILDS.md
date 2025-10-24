# Multi-Architecture Container Builds

## Overview

The CI/CD pipeline builds container images for multiple processor architectures, enabling containers to run on different deployment targets without compatibility issues. This is achieved using Docker Buildx and manifest lists, which allow a single image tag to reference multiple architecture-specific variants.

## Supported Architectures

The pipeline supports building for the following architectures:

- **linux/amd64** (x86_64): Intel/AMD 64-bit processors - primary architecture for most cloud environments
- **linux/arm64** (aarch64): ARM 64-bit processors - used by Apple Silicon Macs, AWS Graviton instances, and other ARM-based servers

## Build Strategy

### Branch-Based Build Configuration

To optimize CI time and resources, the pipeline uses a conditional build strategy:

| Branch Type | Architectures Built | Rationale |
|-------------|-------------------|-----------|
| **main branch** | amd64 + arm64 (multi-arch) | Production-ready images need broad compatibility |
| **Feature branches** | amd64 only (single-arch) | Faster CI runs for development/testing |

### Why This Strategy?

1. **Reduced CI Time**: Building for multiple architectures can increase build time by 50-100%. Feature branches build single-arch to provide fast feedback.
2. **Production Readiness**: Main branch builds include all architectures for deployment flexibility.
3. **Testing Efficiency**: Functional tests and security scans run on amd64 builds, which covers the primary deployment architecture.
4. **Cost Optimization**: Reduced build minutes for feature branches lowers CI costs.

## Implementation Details

### Build Job Architecture Detection

Each container build job includes a "Determine build platforms" step that conditionally sets the target platforms:

```bash
if [ "${{ github.ref_name }}" = "main" ]; then
  PLATFORMS="linux/amd64,linux/arm64"
  ARCH_LABEL="Multi-architecture (amd64, arm64)"
else
  PLATFORMS="linux/amd64"
  ARCH_LABEL="Single architecture (amd64)"
fi
```

### Build Jobs (Testing Phase)

**Purpose**: Build and test images for validation

- **Platform**: Always `linux/amd64`
- **Output**: Docker tar file for local testing
- **Why amd64 only**: Docker export (`type=docker,dest=...`) only works with single-platform builds. We need to export the image for functional testing and security scanning.

**Jobs**:
- `build-container-dev`: Builds development container for amd64
- `build-container-prod`: Builds production container for amd64

### Publishing Jobs (Multi-Architecture)

**Purpose**: Build and publish validated images to registry

- **Platform**: Conditional based on branch (`linux/amd64` for features, `linux/amd64,linux/arm64` for main)
- **Output**: Pushed to GitHub Container Registry
- **Manifest**: Creates multi-architecture manifest list on main branch

**Jobs**:
- `publish-container-dev`: Publishes development images
- `publish-container-prod`: Publishes production images

### How It Works

1. **Build Phase** (amd64 only):
   ```yaml
   platforms: linux/amd64
   outputs: type=docker,dest=/tmp/frontend-dev.tar
   ```
   - Builds single-architecture image
   - Exports as tar file
   - Runs functional tests
   - Runs security scans
   - Validates image size

2. **Publishing Phase** (conditional multi-arch):
   ```yaml
   platforms: ${{ steps.platforms.outputs.platforms }}
   push: true
   ```
   - Rebuilds with configured platforms
   - Leverages existing caches for fast rebuild
   - Pushes to registry with manifest list
   - Verifies all architectures present

## Manifest Lists

When multi-architecture images are published, Docker creates a **manifest list** (also called a **fat manifest**). This is a special image manifest that contains references to architecture-specific images.

### Manifest List Structure

```
ghcr.io/owner/repo/frontend:prod-cb2c01f
├─ Manifest List (digest: sha256:abc123...)
   ├─ linux/amd64 image (digest: sha256:def456...)
   └─ linux/arm64 image (digest: sha256:789ghi...)
```

### How Manifest Lists Work

When you pull an image:
```bash
docker pull ghcr.io/owner/repo/frontend:prod-cb2c01f
```

Docker automatically:
1. Fetches the manifest list
2. Identifies your platform architecture
3. Pulls only the matching architecture variant

### Platform Selection

Docker automatically selects the correct architecture based on your system. You can override this:

```bash
# Pull specific architecture
docker pull --platform linux/amd64 ghcr.io/owner/repo/frontend:prod-cb2c01f
docker pull --platform linux/arm64 ghcr.io/owner/repo/frontend:prod-cb2c01f

# Run specific architecture (useful for testing cross-platform)
docker run --platform linux/arm64 ghcr.io/owner/repo/frontend:prod-cb2c01f
```

## Manifest Inspection and Verification

### Viewing Manifest Information

The CI pipeline automatically inspects and verifies manifests after publishing:

```bash
# Inspect manifest using docker buildx imagetools
docker buildx imagetools inspect ghcr.io/owner/repo/frontend:prod-cb2c01f
```

Output shows:
- Manifest digest
- Media type (manifest list vs single image)
- All architecture variants with their digests
- Image sizes for each architecture

### Architecture Verification

The CI pipeline verifies that all expected architectures are present:

**For main branch builds**:
- ✅ Verifies both linux/amd64 and linux/arm64 are present
- ❌ Fails if any expected architecture is missing

**For feature branch builds**:
- ℹ️ Confirms single architecture (linux/amd64)
- Notes this is expected behavior

### Verification Script Logic

```bash
# Get raw manifest JSON
MANIFEST_JSON=$(docker buildx imagetools inspect --raw "$IMAGE")

# Check if multi-arch manifest list
if echo "$MANIFEST_JSON" | jq -e '.manifests' > /dev/null 2>&1; then
  # Extract all architectures
  ARCHS=$(echo "$MANIFEST_JSON" | jq -r '.manifests[].platform | "\(.os)/\(.architecture)"')

  # Verify expected architectures present
  # Fails build if missing
else
  # Single architecture image
  ARCH=$(echo "$MANIFEST_JSON" | jq -r '.os + "/" + .architecture')
fi
```

## CI/CD Integration

### Workflow Jobs

The multi-architecture feature is integrated into these jobs:

**Development Container**:
1. `build-container-dev`: Builds amd64 for testing
2. `security-scan-dev`: Scans amd64 image
3. `publish-container-dev`: Publishes multi-arch (main) or single-arch (features)

**Production Container**:
1. `build-container-prod`: Builds amd64 for testing
2. `security-scan-prod`: Scans amd64 image
3. `publish-container-prod`: Publishes multi-arch (main) or single-arch (features)

### Build Time Impact

Expected build times:

| Build Type | Single Architecture (amd64) | Multi-Architecture (amd64 + arm64) |
|------------|----------------------------|-----------------------------------|
| Development | 30-60 seconds | 60-120 seconds |
| Production | 1-2 minutes | 2-4 minutes |

**Cache Effectiveness**:
- First multi-arch build: ~2x single-arch build time
- Subsequent builds: Minimal overhead due to layer caching
- Cross-architecture layer reuse: Most layers are shared between amd64 and arm64

### GitHub Actions Output

The CI pipeline provides detailed output in GitHub Step Summary:

**Build Architectures Section**:
```
Branch: main
Platforms: linux/amd64,linux/arm64
Description: Multi-architecture (amd64, arm64)

Note: Multi-architecture builds (amd64 + arm64) run only on main branch.
Feature branches build for amd64 only to reduce CI time.
```

**Manifest Inspection Section**:
```
Manifest Type: Multi-architecture list
Architectures: linux/amd64, linux/arm64
Variant Count: 2

✅ amd64 architecture present
✅ arm64 architecture present
```

## Using Multi-Architecture Images

### Automatic Platform Selection

Docker automatically selects the correct architecture:

```bash
# On x86_64/amd64 machine
docker pull ghcr.io/owner/repo/frontend:latest
# Automatically pulls amd64 variant

# On Apple Silicon Mac (arm64)
docker pull ghcr.io/owner/repo/frontend:latest
# Automatically pulls arm64 variant
```

### Explicit Platform Selection

For testing or specific requirements:

```bash
# Pull specific architecture
docker pull --platform linux/amd64 ghcr.io/owner/repo/frontend:latest
docker pull --platform linux/arm64 ghcr.io/owner/repo/frontend:latest

# Run specific architecture
docker run --platform linux/amd64 ghcr.io/owner/repo/frontend:latest
docker run --platform linux/arm64 ghcr.io/owner/repo/frontend:latest

# Build for specific platform locally
docker build --platform linux/amd64 -t frontend:dev .
docker build --platform linux/arm64 -t frontend:dev .
```

### Docker Compose

Specify platform in docker-compose.yml if needed:

```yaml
services:
  frontend:
    image: ghcr.io/owner/repo/frontend:latest
    platform: linux/amd64  # Optional: force specific architecture
```

## Local Development

### Building Multi-Architecture Images Locally

Developers can build multi-architecture images locally using Docker Buildx:

```bash
# Ensure buildx is enabled
docker buildx version

# Create builder instance (one-time setup)
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap

# Build for multiple architectures
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --target development \
  -t frontend:dev \
  ./frontend

# Build and push to registry (requires login)
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --target production \
  --push \
  -t ghcr.io/owner/repo/frontend:test \
  ./frontend
```

### Testing Cross-Platform Images

```bash
# Test arm64 image on amd64 machine (using QEMU emulation)
docker run --platform linux/arm64 -p 5173:5173 frontend:dev

# Note: Emulation is slower than native execution
# Best used for smoke tests, not performance testing
```

## Deployment Considerations

### Cloud Platforms

**AWS**:
- EC2 x86 instances: Use linux/amd64
- EC2 Graviton instances: Use linux/arm64 (better price/performance)
- Fargate/ECS: Supports both architectures

**Google Cloud**:
- Standard VMs: linux/amd64
- Tau T2A instances: linux/arm64

**Azure**:
- Standard VMs: linux/amd64
- Ampere Altra ARM VMs: linux/arm64

**Docker automatically selects the correct architecture when deploying to these platforms.**

### Kubernetes

Kubernetes automatically schedules pods on nodes matching the image architecture:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  template:
    spec:
      containers:
      - name: frontend
        image: ghcr.io/owner/repo/frontend:latest
        # Kubernetes uses image manifest to match node architecture
```

You can also use node selectors if needed:

```yaml
spec:
  nodeSelector:
    kubernetes.io/arch: amd64  # or arm64
```

## Troubleshooting

### Common Issues

#### Issue: "exec format error"

**Cause**: Trying to run image built for different architecture

**Solution**:
```bash
# Check image architecture
docker inspect ghcr.io/owner/repo/frontend:latest | jq '.[0].Architecture'

# Specify correct platform
docker run --platform linux/amd64 ghcr.io/owner/repo/frontend:latest
```

#### Issue: Slow builds for arm64

**Cause**: Building arm64 images on amd64 hardware uses QEMU emulation

**Solution**:
- This is expected and normal
- Leverage CI/CD caching (most layers cached after first build)
- Consider native arm64 runners for production builds (future enhancement)

#### Issue: Missing architecture in manifest

**Cause**: Build job failed for one architecture

**Solution**:
- Check CI logs for specific architecture build failure
- Verify Dockerfile compatibility with both architectures
- Check for architecture-specific dependencies

### Verification Commands

```bash
# Check if image is multi-arch
docker buildx imagetools inspect ghcr.io/owner/repo/frontend:latest

# View manifest list JSON
docker buildx imagetools inspect --raw ghcr.io/owner/repo/frontend:latest | jq .

# List all architecture variants
docker buildx imagetools inspect --raw ghcr.io/owner/repo/frontend:latest | \
  jq -r '.manifests[].platform | "\(.os)/\(.architecture)"'

# Get digest for specific architecture
docker buildx imagetools inspect --raw ghcr.io/owner/repo/frontend:latest | \
  jq -r '.manifests[] | select(.platform.architecture=="arm64") | .digest'
```

## Performance Considerations

### Build Performance

**Cache Effectiveness**:
- Most Dockerfile layers are architecture-independent (metadata, instructions)
- Only binary layers differ (Node.js binaries, npm packages with native modules)
- BuildKit shares common layers between architectures

**Build Time Breakdown**:
```
Single-arch (amd64):        100% (baseline)
Multi-arch (amd64 + arm64): 150-200% (first build)
Multi-arch (cached):        110-120% (subsequent builds)
```

### Runtime Performance

**Architecture-Specific Performance**:
- **amd64**: Mature, well-optimized, broad compatibility
- **arm64**: Better power efficiency, competitive performance, cost-effective (AWS Graviton, Apple Silicon)

**No performance overhead** from multi-architecture images - Docker pulls only the variant matching your platform.

## Future Enhancements

Potential improvements for multi-architecture builds:

1. **Native ARM64 Runners**:
   - Use ARM64 GitHub Actions runners for faster arm64 builds
   - Eliminates QEMU emulation overhead

2. **Additional Architectures**:
   - `linux/arm/v7` (32-bit ARM) for IoT/embedded devices
   - Platform-specific optimizations

3. **Architecture-Specific Optimizations**:
   - Compiler flags optimized for each architecture
   - Architecture-specific base images

4. **Conditional Architecture Builds**:
   - Build arm64 only when Dockerfile changes
   - Skip unchanged architectures to save time

5. **Multi-Architecture Testing**:
   - Run functional tests on both architectures
   - Catch architecture-specific bugs

## Best Practices

### For Developers

1. **Test Locally**: Build and test multi-arch images before pushing
2. **Use Caching**: Leverage Buildx cache for fast rebuilds
3. **Architecture Awareness**: Be mindful of architecture-specific dependencies
4. **Specify Platforms**: Use `--platform` flag when needed for clarity

### For DevOps Engineers

1. **Monitor Build Times**: Track multi-arch build performance
2. **Optimize Dockerfiles**: Order layers to maximize cache reuse
3. **Verify Manifests**: Always inspect manifests after publishing
4. **Document Architecture**: Clearly document which architectures are supported

### For CI/CD Pipelines

1. **Conditional Builds**: Use branch-based logic to optimize CI time
2. **Validate All Architectures**: Verify manifest lists contain expected variants
3. **Fail Fast**: Exit immediately if expected architecture missing
4. **Clear Reporting**: Display architecture information in build summaries

## Related Documentation

- [Container Image Tagging Strategy](/home/ed/Dev/architecture/frontend/docs/CONTAINER_IMAGE_TAGGING.md) - Tag naming conventions
- [Container Registry Publishing](/home/ed/Dev/architecture/frontend/docs/CONTAINER_REGISTRY_PUBLISHING.md) - Publishing workflow
- [Container Build Caching](/home/ed/Dev/architecture/frontend/docs/CONTAINER_BUILD_CACHING.md) - Caching strategies
- [Docker Buildx Documentation](https://docs.docker.com/buildx/working-with-buildx/) - Official Buildx guide
- [OCI Image Manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md) - Manifest specification

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-24 | Initial implementation of multi-architecture builds |
