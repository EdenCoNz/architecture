# Docker Setup for React Frontend

This project implements Docker best practices for 2024-2025, including:
- ✅ Multi-stage builds for minimal production images
- ✅ Non-root user execution for security
- ✅ BuildKit cache optimization
- ✅ Separate development and production configurations
- ✅ Health checks and resource limits
- ✅ Structured logging with rotation

## Quick Start

### Development Mode

```bash
# Start development server with hot reload
docker compose up

# Access the app at http://localhost:5173
```

The development mode features:
- Live code reloading via bind mounts
- Full development dependencies
- Vite dev server with HMR
- No restart on failure

### Production Mode

```bash
# Build and start production container
docker compose -f compose.yaml -f compose.production.yaml up -d

# Access the app at http://localhost:80
```

The production mode features:
- Nginx web server serving optimized static files
- Minimal Alpine-based image (~50MB)
- Non-root user execution
- Health checks and auto-restart
- Gzip compression and caching headers

## Docker Commands

### Build Commands

```bash
# Build development image
docker compose build

# Build production image
docker build -t react-frontend:latest --target production .

# Build with BuildKit cache
DOCKER_BUILDKIT=1 docker build -t react-frontend:latest .
```

### Run Commands

```bash
# Start development containers
docker compose up

# Start in background (detached)
docker compose up -d

# Stop containers
docker compose down

# View logs
docker compose logs -f frontend

# Rebuild and restart
docker compose up --build
```

### Maintenance Commands

```bash
# Check container health
docker compose ps

# Inspect container
docker inspect react-frontend

# Execute command in running container
docker compose exec frontend sh

# Remove all stopped containers
docker compose down -v

# Prune unused images and containers
docker system prune -a
```

## Architecture

### Multi-Stage Dockerfile

The Dockerfile uses four stages:

1. **base**: Common stage with all dependencies
2. **development**: Vite dev server with hot reload
3. **builder**: Builds production-optimized bundle
4. **production**: Nginx serving static files

### File Structure

```
frontend/
├── Dockerfile                      # Multi-stage build configuration
├── .dockerignore                   # Files excluded from build context
├── nginx.conf                      # Nginx configuration for production
├── compose.yaml                    # Base Docker Compose configuration
├── compose.override.yaml           # Development overrides (auto-loaded)
├── compose.production.yaml         # Production overrides
└── DOCKER.md                       # This file
```

## Security Features

### Non-Root User Execution

Both development and production containers run as user `nodejs` (UID 1001):

```dockerfile
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
USER nodejs
```

### Minimal Base Images

- Development: `node:20-alpine` (~180MB)
- Production: `nginx:1.27-alpine` (~40MB) + built assets

### Health Checks

Production container includes health checks:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1
```

Health endpoint is available at: `http://localhost:8080/health`

## Performance Optimizations

### BuildKit Cache Mounts

The Dockerfile uses cache mounts to persist npm cache:

```dockerfile
RUN --mount=type=cache,target=/root/.npm \
    npm install && \
    npm cache clean --force
```

### Layer Ordering

Layers are ordered from least to most frequently changing:
1. Base image
2. Package dependencies (package.json)
3. Application source code

### Nginx Optimization

Production nginx configuration includes:
- Gzip compression for text assets
- 1-year cache for static assets
- Security headers (X-Frame-Options, X-Content-Type-Options)
- React Router support (SPA routing)

## Resource Limits

### Development

- CPU: 1 core limit, 0.25 core reserved
- Memory: 512MB limit, 128MB reserved

### Production

- CPU: 2 cores limit, 0.5 core reserved
- Memory: 1GB limit, 256MB reserved

Adjust in compose files under `deploy.resources`.

## Logging

Logs are configured with rotation:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

View logs:
```bash
# All logs
docker compose logs

# Follow logs in real-time
docker compose logs -f

# Specific service
docker compose logs frontend

# Last 100 lines
docker compose logs --tail=100
```

## Troubleshooting

### Port Already in Use

If port 5173 (dev) or 8080/80 (prod) is in use:

```bash
# Check what's using the port
lsof -i :5173

# Change port in compose.yaml
ports:
  - "3000:5173"  # Map to different host port
```

### Permission Errors

If you encounter permission errors with bind mounts:

```bash
# Ensure proper ownership
sudo chown -R $USER:$USER .

# Or run with current user
docker compose run --user $(id -u):$(id -g) frontend npm install
```

### Build Cache Issues

If build cache causes issues:

```bash
# Build without cache
docker compose build --no-cache

# Remove all build cache
docker builder prune -a
```

### Container Won't Start

Check logs for errors:

```bash
# View container logs
docker compose logs frontend

# Check container health
docker compose ps

# Inspect container
docker inspect react-frontend
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build production image
        uses: docker/build-push-action@v5
        with:
          context: .
          target: production
          tags: react-frontend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Best Practices Applied

✅ **Security**
- Non-root user execution
- Minimal Alpine base images
- No secrets in image layers
- Security headers in nginx

✅ **Performance**
- Multi-stage builds (70% size reduction)
- BuildKit cache mounts
- Layer ordering optimization
- Gzip compression

✅ **Reliability**
- Health checks with auto-restart
- Resource limits
- Structured logging with rotation
- Proper error handling

✅ **Development Experience**
- Hot reload with bind mounts
- Fast rebuilds with cache
- Environment-specific configs
- Easy local testing

## References

- [Docker Official Documentation](https://docs.docker.com/)
- [Vite Docker Guide](https://vitejs.dev/guide/docker.html)
- [nginx Docker Hub](https://hub.docker.com/_/nginx)
- [Docker Best Practices 2024-2025](../context/devops/docker.md)
