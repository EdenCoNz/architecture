# Docker Guide: Frontend Application

**Last Updated**: 2025-10-15
**Version**: 1.0.0
**Maintainer**: DevOps Team

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
  - [Multi-Stage Build Design](#multi-stage-build-design)
  - [Development vs Production](#development-vs-production)
  - [Network Architecture](#network-architecture)
- [Build Instructions](#build-instructions)
  - [Development Build](#development-build)
  - [Production Build](#production-build)
  - [Build Performance](#build-performance)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Volume Mounts](#volume-mounts)
  - [Networking](#networking)
- [Production Deployment](#production-deployment)
  - [Security Best Practices](#security-best-practices)
  - [Resource Management](#resource-management)
  - [Monitoring and Health Checks](#monitoring-and-health-checks)
  - [Deployment Checklist](#deployment-checklist)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debugging Techniques](#debugging-techniques)
  - [Performance Issues](#performance-issues)
- [Advanced Topics](#advanced-topics)
  - [Multi-Platform Builds](#multi-platform-builds)
  - [Image Optimization](#image-optimization)
  - [CI/CD Integration](#cicd-integration)

---

## Overview

This guide provides comprehensive documentation for using Docker with the React frontend application. The Docker setup is designed for both local development and production deployment, following modern DevOps best practices including:

- **Multi-stage builds** for minimal production images
- **Non-root user execution** for enhanced security
- **Hot module replacement** in development environments
- **BuildKit optimizations** for faster builds
- **Health checks** for monitoring and orchestration
- **Comprehensive security headers** and configurations

### Key Features

| Feature | Development | Production |
|---------|-------------|------------|
| Base Image | Node 20 Alpine | nginx:alpine |
| Image Size | ~350MB | ~54MB |
| User | nodejs (UID 1001) | nginx-app (UID 1001) |
| Port | 5173 | 8080 |
| Hot Reload | Yes (via volumes) | No |
| Health Check | Vite dev server | nginx /health endpoint |
| Build Time | ~60s (first), ~20s (cached) | ~120s (first), ~35s (cached) |

---

## Architecture

### Multi-Stage Build Design

The production Dockerfile uses a multi-stage build strategy to separate build-time dependencies from runtime, resulting in minimal final images.

#### Stage 1: Build Stage (Node 20 Alpine)

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build
```

**Purpose**: Compile TypeScript, bundle JavaScript/CSS, optimize assets

**Includes**:
- Node.js 20 runtime
- All development dependencies (TypeScript, Vite, ESLint)
- Build tools and compilers
- Source code and configuration

**Output**: Optimized production bundle in `dist/` directory

#### Stage 2: Production Stage (nginx:alpine)

```dockerfile
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
RUN addgroup -g 1001 -S nginx-app && \
    adduser -S nginx-app -u 1001 -G nginx-app && \
    chown -R nginx-app:nginx-app /usr/share/nginx/html && \
    # ... additional permission setup
USER nginx-app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget --spider http://localhost:8080/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
```

**Purpose**: Serve static files with minimal attack surface

**Includes**:
- nginx:alpine base (~52MB)
- Compiled static assets only
- Custom nginx configuration
- Non-root user setup

**Excludes**:
- Node.js runtime
- Build tools
- Development dependencies
- Source code

**Result**: 54MB final image (vs 350MB if single-stage)

### Development vs Production

#### Development Environment (Dockerfile.dev)

**Design Goals**:
- Fast feedback loop with hot module replacement
- Debugging capabilities
- Development tools included
- Matches production security model

**Architecture**:
```
┌─────────────────────────────────────────┐
│ Docker Container (Node 20 Alpine)       │
│                                         │
│ ┌───────────────────────────────────┐  │
│ │ Vite Dev Server (Port 5173)       │  │
│ │ - HMR via WebSocket               │  │
│ │ - Source Maps enabled             │  │
│ │ - Hot Reload active               │  │
│ └───────────────────────────────────┘  │
│                                         │
│ Volume Mounts (read-only):              │
│ - /app/src       ← Host: frontend/src  │
│ - /app/public    ← Host: frontend/public│
│ - /app/*.config  ← Host: frontend/*.config│
│                                         │
│ Container-Only:                         │
│ - /app/node_modules (not mounted)      │
│                                         │
│ User: nodejs (UID 1001)                │
└─────────────────────────────────────────┘
```

**Key Features**:
- Volume mounts for live code updates
- Vite dev server with `--host 0.0.0.0` for external access
- All development dependencies included
- Git and wget tools for debugging
- Health check on Vite dev server endpoint

#### Production Environment (Dockerfile)

**Design Goals**:
- Minimal image size
- Maximum security
- Optimal performance
- Scalability

**Architecture**:
```
┌─────────────────────────────────────────┐
│ Docker Container (nginx:alpine)         │
│                                         │
│ ┌───────────────────────────────────┐  │
│ │ nginx (Port 8080)                 │  │
│ │ - Gzip compression                │  │
│ │ - Security headers                │  │
│ │ - SPA routing fallback            │  │
│ │ - Static asset caching            │  │
│ └───────────────────────────────────┘  │
│                                         │
│ Static Files:                           │
│ /usr/share/nginx/html/                  │
│ ├── index.html                          │
│ ├── assets/                             │
│ │   ├── index-[hash].js (366KB)        │
│ │   └── index-[hash].css (2KB)         │
│ └── vite.svg                            │
│                                         │
│ User: nginx-app (UID 1001)             │
│ Health: /health endpoint               │
└─────────────────────────────────────────┘
```

**Key Features**:
- No source code or build tools
- Only compiled static assets
- nginx optimized for SPA serving
- Security headers (CSP, X-Frame-Options, etc.)
- Caching strategies for performance

### Network Architecture

#### Development Network (docker-compose)

```
┌──────────────────────────────────────────────────┐
│ Docker Network: architecture-network (bridge)    │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ Container: architecture-frontend-dev       │ │
│  │ Hostname: frontend                         │ │
│  │ Internal IP: 172.x.x.x (dynamic)          │ │
│  │                                            │ │
│  │ Exposed Ports:                             │ │
│  │   5173:5173 → Vite dev server             │ │
│  │                                            │ │
│  │ Environment:                               │ │
│  │   - NODE_ENV=development                   │ │
│  │   - VITE_HOST=0.0.0.0                     │ │
│  │   - VITE_PORT=5173                        │ │
│  │   - VITE_API_BASE_URL (from .env)         │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  Future Services:                                │
│  - Backend API (port 3000)                      │
│  - Database (port 5432)                         │
│  - Redis cache (port 6379)                      │
└──────────────────────────────────────────────────┘
        │
        │ Port Mapping
        ↓
   Host: localhost:5173
```

**Network Features**:
- Custom bridge network for service isolation
- DNS resolution between containers (access via service name)
- Automatic network creation and teardown
- No external dependencies in development

#### Production Network

Production deployment networking depends on your orchestration platform (Kubernetes, Docker Swarm, cloud services). Key considerations:

- **Load Balancing**: Use external load balancer (nginx, ALB, Cloud Load Balancer)
- **Service Discovery**: Leverage platform DNS (Kubernetes Services, Docker Swarm DNS)
- **TLS Termination**: Handle at load balancer or ingress controller level
- **Port Exposure**: Map container port 8080 to load balancer backend

---

## Build Instructions

### Development Build

#### Using Docker Compose (Recommended)

1. **Navigate to project root**:
   ```bash
   cd /path/to/architecture
   ```

2. **Copy environment template** (first time only):
   ```bash
   cp .env.example .env
   # Edit .env to customize settings
   ```

3. **Build images**:
   ```bash
   docker compose build
   ```

   Output:
   ```
   [+] Building 65.3s (13/13) FINISHED
   => [frontend internal] load build context
   => [frontend builder 1/6] FROM node:20-alpine
   => [frontend builder 2/6] WORKDIR /app
   => [frontend builder 3/6] COPY package*.json ./
   => [frontend builder 4/6] RUN npm ci
   => [frontend builder 5/6] COPY . .
   => [frontend] exporting to image
   ```

4. **Start development server**:
   ```bash
   docker compose up
   ```

   Access application at: http://localhost:5173

#### Using npm Scripts (Alternative)

From the `frontend/` directory:

```bash
# Build images
npm run docker:build

# Start containers
npm run docker:run

# Stop containers
npm run docker:stop
```

#### Manual Docker Build

```bash
cd frontend
docker build -f Dockerfile.dev -t frontend-dev:latest .
docker run -p 5173:5173 \
  -v $(pwd)/src:/app/src:ro \
  -v $(pwd)/public:/app/public:ro \
  -v $(pwd)/vite.config.ts:/app/vite.config.ts:ro \
  --name frontend-dev \
  frontend-dev:latest
```

### Production Build

#### Using Docker Build

```bash
cd frontend

# Build production image
docker build -t frontend:latest .

# Run production container
docker run -d \
  --name frontend-prod \
  -p 8080:8080 \
  frontend:latest

# Verify health
curl http://localhost:8080/health
# Expected output: healthy

# Test application
curl -I http://localhost:8080/
# Expected: HTTP/1.1 200 OK
```

#### Using BuildKit Cache Mounts (Faster Builds)

```bash
# Enable BuildKit (default in Docker 23.0+)
export DOCKER_BUILDKIT=1

# Build with cache optimization
docker build \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  -t frontend:latest \
  .

# First build: ~120 seconds
# Subsequent builds with cache: ~35 seconds
```

#### Multi-Platform Build

```bash
# Set up buildx
docker buildx create --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t myregistry/frontend:latest \
  --push \
  .
```

### Build Performance

#### Build Time Metrics

| Build Type | First Build | Cached Build | Cache Hit Ratio |
|------------|-------------|--------------|-----------------|
| Development | ~65s | ~20s | 70-80% |
| Production | ~120s | ~35s | 60-70% |
| CI/CD (GitHub Actions) | ~180s | ~60s | 80-90% |

#### Optimization Techniques

1. **Layer Caching Optimization**:
   ```dockerfile
   # Good: Package files copied first (change less frequently)
   COPY package.json package-lock.json ./
   RUN npm ci
   # Source code copied last (changes frequently)
   COPY . .
   ```

2. **BuildKit Cache Mounts**:
   ```dockerfile
   RUN --mount=type=cache,target=/root/.npm \
       npm ci
   # npm cache persists across builds
   ```

3. **Multi-Stage Build Benefits**:
   - Build stage: 350MB (includes all devDependencies)
   - Production stage: Only 54MB (366KB JS + 2KB CSS + nginx)
   - Savings: 296MB (84% reduction)

4. **.dockerignore Effectiveness**:
   - Without .dockerignore: 189.30 MB, 57,326 files
   - With .dockerignore: 0.23 MB, 38 files
   - Reduction: 99.9% size, 52% faster builds

---

## Configuration

### Environment Variables

#### Frontend Application Variables

All variables prefixed with `VITE_` are exposed to the browser client.

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NODE_ENV` | Environment mode | `development` | No |
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:3000` | Yes |
| `VITE_HOST` | Vite dev server host | `0.0.0.0` | No |
| `VITE_PORT` | Vite dev server port | `5173` | No |

#### Setting Environment Variables

**Method 1: .env File** (Recommended for local development)

```bash
# Create .env file at project root
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:3000
NODE_ENV=development
VITE_HOST=0.0.0.0
VITE_PORT=5173
EOF
```

**Method 2: docker-compose.yml**

```yaml
services:
  frontend:
    environment:
      - NODE_ENV=production
      - VITE_API_BASE_URL=https://api.production.com
```

**Method 3: Docker Run Command**

```bash
docker run -e VITE_API_BASE_URL=https://api.example.com frontend:latest
```

**Method 4: Build-Time Arguments**

```dockerfile
ARG API_BASE_URL=http://localhost:3000
ENV VITE_API_BASE_URL=$API_BASE_URL
```

```bash
docker build --build-arg API_BASE_URL=https://api.prod.com -t frontend:latest .
```

#### Security Considerations

- **Never commit .env files** with sensitive data to version control
- **Use secret management** for production (Docker secrets, Kubernetes secrets, AWS Secrets Manager)
- **VITE_ prefix exposure**: All `VITE_*` variables are embedded in JavaScript bundle and visible to users
- **Avoid sensitive data** in VITE_ variables (API keys, tokens, passwords)

### Volume Mounts

Volume mounts enable live code updates in development without rebuilding images.

#### Development Volume Strategy

```yaml
volumes:
  # Source code (read-only for security)
  - ./frontend/src:/app/src:ro
  - ./frontend/public:/app/public:ro

  # Configuration files (read-only)
  - ./frontend/index.html:/app/index.html:ro
  - ./frontend/vite.config.ts:/app/vite.config.ts:ro
  - ./frontend/tsconfig.json:/app/tsconfig.json:ro
  - ./frontend/tsconfig.app.json:/app/tsconfig.app.json:ro
  - ./frontend/tsconfig.node.json:/app/tsconfig.node.json:ro

  # Exclude node_modules (use container's version)
  - /app/node_modules
```

#### Volume Mount Best Practices

1. **Use read-only mounts** (`:ro`) for source code to prevent accidental modification
2. **Exclude node_modules** to avoid platform-specific binary conflicts
3. **Mount configuration files** needed for Vite HMR to work correctly
4. **Avoid mounting .git** directory for security and performance

#### Production Volumes

Production containers should **not** use bind mounts for source code. Use named volumes only for:

- **Persistent data**: User uploads, logs, cache
- **Shared configuration**: Between multiple container instances
- **Log aggregation**: Centralized logging to host

Example production volume:
```yaml
services:
  frontend:
    image: frontend:latest
    volumes:
      - nginx-logs:/var/log/nginx  # Named volume for logs

volumes:
  nginx-logs:
    driver: local
```

### Networking

#### Port Mappings

**Development**:
- Container Port: 5173 (Vite dev server)
- Host Port: 5173
- Mapping: `5173:5173`
- Protocol: HTTP with WebSocket (for HMR)

**Production**:
- Container Port: 8080 (nginx, non-privileged)
- Host Port: 80 or 443 (via reverse proxy)
- Mapping: `80:8080` or load balancer → 8080
- Protocol: HTTP (TLS at load balancer)

#### Network Modes

**Bridge Network** (Default, Recommended):
```yaml
networks:
  architecture-network:
    driver: bridge
```

Benefits:
- Service isolation
- DNS resolution between containers
- Controlled exposure to host

**Host Network** (Not Recommended):
```yaml
network_mode: host
```

Use cases:
- High-performance networking requirements
- Avoiding NAT overhead

Drawbacks:
- No container isolation
- Port conflicts with host services
- Security risks

#### Service Discovery

In docker-compose, services can communicate using service names:

```yaml
services:
  frontend:
    # Frontend can access backend at http://backend:3000
  backend:
    # Backend service
```

Example API call from frontend:
```typescript
// In docker-compose environment
const API_URL = process.env.VITE_API_BASE_URL || 'http://backend:3000';
```

---

## Production Deployment

### Security Best Practices

#### 1. Non-Root User Execution

**Why**: Running as root gives container processes unnecessary privileges. Compromised containers can escalate to host root.

**Implementation** (Dockerfile):
```dockerfile
# Create non-root user
RUN addgroup -g 1001 -S nginx-app && \
    adduser -S nginx-app -u 1001 -G nginx-app

# Set file ownership
RUN chown -R nginx-app:nginx-app /usr/share/nginx/html && \
    chown -R nginx-app:nginx-app /var/cache/nginx && \
    chown -R nginx-app:nginx-app /var/log/nginx

# Switch to non-root user
USER nginx-app
```

**Verification**:
```bash
docker run --rm frontend:latest id
# Output: uid=1001(nginx-app) gid=1001(nginx-app)
```

#### 2. Minimal Base Images

**Current**: `nginx:alpine` (52.8MB)

**Benefits**:
- Reduced attack surface (fewer packages = fewer vulnerabilities)
- Smaller image size (faster deployment)
- Lower storage and bandwidth costs

**Alternatives**:
- `nginx:alpine` (52MB) - Current choice
- `nginx:stable` (142MB) - Full Debian base
- Distroless nginx (custom build, ~40MB) - No shell or package manager

#### 3. Security Headers

Configured in `nginx.conf`:

```nginx
# Prevent clickjacking attacks
add_header X-Frame-Options "SAMEORIGIN" always;

# Prevent MIME type sniffing
add_header X-Content-Type-Options "nosniff" always;

# Enable XSS protection
add_header X-XSS-Protection "1; mode=block" always;

# Control referrer information
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self';" always;
```

**Customize CSP** based on your application's needs (external APIs, CDNs, analytics).

#### 4. Vulnerability Scanning

**Recommended Tools**:

1. **Trivy** (Fast, comprehensive):
   ```bash
   docker run aquasec/trivy image frontend:latest
   ```

2. **Grype** (Accurate, SBOM-first):
   ```bash
   grype frontend:latest
   ```

3. **Docker Scout** (Native to Docker):
   ```bash
   docker scout cves frontend:latest
   ```

**CI/CD Integration**:
```yaml
- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: frontend:latest
    severity: HIGH,CRITICAL
    exit-code: 1  # Fail build on vulnerabilities
```

#### 5. Read-Only Root Filesystem

**Implementation**:
```bash
docker run --read-only --tmpfs /var/cache/nginx --tmpfs /var/run frontend:latest
```

**Benefits**:
- Prevents malware from persisting changes
- Protects against file-based attacks

**Considerations**:
- nginx needs write access to `/var/cache/nginx` and `/var/run`
- Use tmpfs mounts for temporary writable paths

#### 6. Secrets Management

**Bad Practice**:
```dockerfile
ENV API_KEY="secret-key-123"  # Visible in image history
RUN echo "password" > /app/credentials  # Persists in layer
```

**Good Practice**:

**Docker Secrets** (Swarm/Kubernetes):
```bash
echo "my-secret-token" | docker secret create api_key -
docker service create --secret api_key frontend:latest
```

**Environment Variables at Runtime**:
```bash
docker run -e API_KEY=$(vault read -field=value secret/api_key) frontend:latest
```

**External Secret Managers**:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Google Secret Manager

### Resource Management

#### CPU and Memory Limits

**Why**: Prevent resource exhaustion, ensure fair resource allocation, improve scheduling.

**docker-compose.yml**:
```yaml
services:
  frontend:
    deploy:
      resources:
        limits:
          cpus: '1.0'      # Max 1 CPU core
          memory: 512M     # Max 512MB RAM
        reservations:
          cpus: '0.5'      # Guaranteed 0.5 CPU
          memory: 256M     # Guaranteed 256MB RAM
```

**Docker Run**:
```bash
docker run \
  --cpus="1.0" \
  --memory="512m" \
  --memory-reservation="256m" \
  frontend:latest
```

#### Recommended Limits

| Environment | CPU | Memory | Rationale |
|-------------|-----|--------|-----------|
| Development | 1.0 | 512MB | Matches typical laptop constraints |
| Production (Single) | 0.5 | 256MB | nginx is lightweight, static files |
| Production (Load Balanced) | 0.25 | 128MB | Horizontal scaling preferred |
| CI/CD | 2.0 | 1GB | Faster builds |

#### Monitoring Resource Usage

```bash
# Real-time stats
docker stats frontend

# Output:
CONTAINER ID   NAME       CPU %     MEM USAGE / LIMIT   MEM %     NET I/O
abc123         frontend   0.10%     45MiB / 512MiB     8.79%     1.2kB / 850B
```

### Monitoring and Health Checks

#### Health Check Configuration

**Dockerfile**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1
```

**Parameters**:
- `--interval=30s`: Check every 30 seconds
- `--timeout=3s`: Fail if check takes >3 seconds
- `--start-period=5s`: Grace period during container startup
- `--retries=3`: Mark unhealthy after 3 consecutive failures

**Health Check Endpoint** (`nginx.conf`):
```nginx
location /health {
    access_log off;
    return 200 "healthy\n";
    add_header Content-Type text/plain;
}
```

#### Monitoring Health Status

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' frontend
# Output: healthy | unhealthy | starting

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' frontend
```

#### Docker Compose Health Checks

```yaml
services:
  frontend:
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

#### Orchestrator Integration

**Kubernetes Liveness Probe**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 30
```

**Docker Swarm Health Check**:
```bash
docker service create \
  --name frontend \
  --health-cmd "wget --spider http://localhost:8080/health" \
  --health-interval 30s \
  frontend:latest
```

#### Application-Level Monitoring

**Structured Logging** (nginx):
```nginx
log_format json_combined escape=json
  '{'
    '"time":"$time_iso8601",'
    '"remote_addr":"$remote_addr",'
    '"request":"$request",'
    '"status":"$status",'
    '"bytes_sent":"$bytes_sent",'
    '"request_time":"$request_time",'
    '"http_user_agent":"$http_user_agent"'
  '}';

access_log /var/log/nginx/access.log json_combined;
```

**Log Aggregation**:
```yaml
services:
  frontend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Metrics Collection**:
- Prometheus nginx exporter
- Datadog agent
- CloudWatch Container Insights
- Grafana dashboard

### Deployment Checklist

Before deploying to production, verify:

#### Pre-Deployment Checks

- [ ] **Image built successfully** with production Dockerfile
- [ ] **Image size optimized** (<60MB for frontend)
- [ ] **Vulnerability scan passed** (no HIGH/CRITICAL vulnerabilities)
- [ ] **Non-root user configured** (UID 1001)
- [ ] **Health check endpoint working** (returns 200 OK)
- [ ] **Environment variables configured** for production
- [ ] **Secrets externalized** (not hardcoded in image)
- [ ] **Resource limits set** (CPU, memory)
- [ ] **Logging configured** (driver, rotation policy)
- [ ] **Monitoring enabled** (health checks, metrics)

#### Security Checks

- [ ] **Security headers configured** (CSP, X-Frame-Options, etc.)
- [ ] **TLS/HTTPS enabled** (at load balancer or ingress)
- [ ] **No sensitive data in image layers** (docker history check)
- [ ] **Base image up to date** (recent nginx:alpine)
- [ ] **Port 8080 used** (non-privileged port)
- [ ] **File permissions correct** (owned by nginx-app)

#### Testing Checks

- [ ] **Application loads correctly** (curl http://localhost:8080/)
- [ ] **SPA routing works** (curl http://localhost:8080/some-route → index.html)
- [ ] **Static assets served** (JS/CSS bundles load)
- [ ] **Gzip compression enabled** (check response headers)
- [ ] **Cache headers present** (static assets cached 1 year)
- [ ] **Health check passes** (curl http://localhost:8080/health)
- [ ] **Container restarts on failure** (restart policy configured)

#### Performance Checks

- [ ] **Build time acceptable** (<2 minutes with cache)
- [ ] **Image layers optimized** (minimal layers, good caching)
- [ ] **BuildKit cache working** (subsequent builds faster)
- [ ] **.dockerignore effective** (build context <1MB)
- [ ] **Startup time fast** (<10 seconds)
- [ ] **Memory usage reasonable** (<256MB)

---

## Troubleshooting

### Common Issues

#### Issue 1: Port Already in Use

**Symptoms**:
```bash
Error: bind: address already in use
```

**Diagnosis**:
```bash
# Find process using port 5173
lsof -i:5173

# Or for port 8080
lsof -i:8080
```

**Solutions**:

**Option 1: Stop conflicting process**
```bash
# Kill process by PID
kill -9 <PID>

# Or kill by port
lsof -ti:5173 | xargs kill -9
```

**Option 2: Use different port**
```bash
# Docker Compose
docker compose up
# Edit docker-compose.yml: ports: "5174:5173"

# Docker Run
docker run -p 5174:5173 frontend-dev:latest
```

**Option 3: Stop Docker container**
```bash
docker compose down
# Or
docker stop frontend-test && docker rm frontend-test
```

#### Issue 2: Changes Not Reflecting in Browser

**Symptoms**:
- Code changes in editor not appearing in browser
- Old version of app still running

**Diagnosis**:
```bash
# Check if volumes mounted correctly
docker inspect frontend | grep Mounts -A 20

# Check container logs
docker compose logs -f frontend
```

**Solutions**:

**Option 1: Restart container**
```bash
docker compose restart frontend
```

**Option 2: Rebuild image** (if Dockerfile changed)
```bash
docker compose up --build
```

**Option 3: Clear browser cache**
```
Ctrl+Shift+R (hard reload)
```

**Option 4: Verify volume mounts**
```yaml
# Ensure in docker-compose.yml:
volumes:
  - ./frontend/src:/app/src:ro  # Check path is correct
```

**Option 5: Check Vite HMR** (Development)
```bash
# HMR requires WebSocket connection
# Check browser console for WebSocket errors
```

#### Issue 3: Container Fails to Start

**Symptoms**:
```bash
docker compose up
# Container exits immediately
```

**Diagnosis**:
```bash
# View container logs
docker compose logs frontend

# Check container status
docker compose ps

# Inspect container
docker inspect frontend
```

**Common Causes and Solutions**:

**Cause 1: Missing dependencies**
```bash
# Rebuild with no cache
docker compose build --no-cache
```

**Cause 2: Permission errors**
```bash
# Check file permissions
ls -la frontend/

# Fix if needed
chmod -R 755 frontend/src
```

**Cause 3: Syntax error in Dockerfile**
```bash
# Validate Dockerfile
docker build -f frontend/Dockerfile.dev --no-cache .
# Look for error in build output
```

**Cause 4: Invalid nginx config** (Production)
```bash
# Test nginx config
docker run --rm -v $(pwd)/frontend/nginx.conf:/etc/nginx/conf.d/default.conf nginx:alpine nginx -t
```

#### Issue 4: Health Check Failing

**Symptoms**:
```bash
docker inspect frontend | grep Health -A 10
# Status: unhealthy
```

**Diagnosis**:
```bash
# Check health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' frontend

# Manually test health endpoint
docker exec frontend wget --spider http://localhost:8080/health
```

**Solutions**:

**Option 1: Increase start period**
```dockerfile
HEALTHCHECK --start-period=30s  # Increase from 5s
```

**Option 2: Adjust timeout**
```dockerfile
HEALTHCHECK --timeout=10s  # Increase from 3s
```

**Option 3: Check nginx running**
```bash
docker exec frontend ps aux | grep nginx
```

**Option 4: Verify port binding**
```bash
docker exec frontend netstat -tuln | grep 8080
```

#### Issue 5: Image Size Too Large

**Symptoms**:
```bash
docker images frontend:latest
# SIZE: 200MB+
```

**Diagnosis**:
```bash
# Analyze image layers
docker history frontend:latest

# Check what's taking space
docker run --rm frontend:latest du -sh /* 2>/dev/null | sort -h
```

**Solutions**:

**Option 1: Verify multi-stage build**
```dockerfile
# Ensure production stage doesn't copy from wrong stage
COPY --from=builder /app/dist /usr/share/nginx/html  # Only dist
```

**Option 2: Check .dockerignore**
```bash
# Ensure node_modules excluded
cat frontend/.dockerignore | grep node_modules
```

**Option 3: Remove development dependencies** (Production)
```dockerfile
# In builder stage
RUN npm ci --only=production  # Only if not needed for build
```

**Option 4: Clean npm cache** (if not using cache mounts)
```dockerfile
RUN npm ci && npm cache clean --force
```

### Debugging Techniques

#### 1. Interactive Shell Access

**Development Container**:
```bash
# Access running container
docker exec -it frontend sh

# Or start container with shell
docker run -it --rm frontend-dev:latest sh
```

**Production Container**:
```bash
# Production uses minimal image, may not have shell
# Use debug image if needed
docker run -it --rm --entrypoint sh frontend:latest
```

#### 2. Log Analysis

**View Logs**:
```bash
# Follow logs in real-time
docker compose logs -f frontend

# Last 100 lines
docker compose logs --tail=100 frontend

# Specific time range
docker compose logs --since="2025-10-15T10:00:00" frontend
```

**nginx Access Logs** (Production):
```bash
docker exec frontend cat /var/log/nginx/access.log
```

**nginx Error Logs**:
```bash
docker exec frontend cat /var/log/nginx/error.log
```

#### 3. Network Debugging

**Test Connectivity**:
```bash
# From host to container
curl http://localhost:5173/

# From container to external
docker exec frontend wget -O- http://example.com

# Between containers (in docker-compose)
docker exec frontend wget -O- http://backend:3000/health
```

**Check Listening Ports**:
```bash
docker exec frontend netstat -tuln
```

**Inspect Network**:
```bash
docker network inspect architecture-network
```

#### 4. Build Debugging

**Enable BuildKit Debug**:
```bash
DOCKER_BUILDKIT=1 docker build --progress=plain --no-cache .
```

**Check Build Context**:
```bash
# See what's being sent to Docker daemon
docker build -t test . 2>&1 | grep "Sending build context"
```

**Verify .dockerignore**:
```bash
tar -czh . | tar -tz | wc -l  # With .dockerignore
tar -czh --exclude-ignore=.dockerignore . | tar -tz | wc -l  # Without
```

### Performance Issues

#### Issue: Slow Build Times

**Diagnosis**:
```bash
# Time the build
time docker build -t frontend:latest .
```

**Solutions**:

1. **Enable BuildKit** (if not already):
   ```bash
   export DOCKER_BUILDKIT=1
   ```

2. **Use cache mounts**:
   ```dockerfile
   RUN --mount=type=cache,target=/root/.npm npm ci
   ```

3. **Optimize layer order**:
   ```dockerfile
   # Copy package files first (change less often)
   COPY package*.json ./
   RUN npm ci
   # Source code last (changes frequently)
   COPY . .
   ```

4. **Verify .dockerignore**:
   ```bash
   # Should exclude node_modules, .git, dist, etc.
   cat .dockerignore
   ```

#### Issue: Slow Container Startup

**Diagnosis**:
```bash
# Measure startup time
time docker run --rm frontend:latest echo "Started"
```

**Solutions**:

1. **Reduce image size** (fewer layers to extract)
2. **Use Alpine base images** (faster extraction)
3. **Optimize HEALTHCHECK start-period**:
   ```dockerfile
   HEALTHCHECK --start-period=5s  # Reduce if app starts faster
   ```

#### Issue: High Memory Usage

**Diagnosis**:
```bash
docker stats frontend
```

**Solutions**:

1. **Set memory limits**:
   ```bash
   docker run --memory="256m" frontend:latest
   ```

2. **Check for memory leaks** (Development):
   ```bash
   # Monitor over time
   watch -n 5 'docker stats --no-stream frontend'
   ```

3. **Reduce Vite cache size** (Development):
   ```typescript
   // vite.config.ts
   export default defineConfig({
     cacheDir: '/tmp/vite-cache'
   })
   ```

---

## Advanced Topics

### Multi-Platform Builds

Build images for multiple CPU architectures (AMD64, ARM64).

**Setup buildx**:
```bash
docker buildx create --name multiplatform --use
docker buildx inspect --bootstrap
```

**Build for multiple platforms**:
```bash
cd frontend

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t myregistry/frontend:latest \
  --push \
  .
```

**Use in CI/CD**:
```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build multi-platform image
  uses: docker/build-push-action@v5
  with:
    context: ./frontend
    platforms: linux/amd64,linux/arm64
    push: true
    tags: myregistry/frontend:latest
```

**Benefits**:
- Support ARM-based servers (AWS Graviton, Raspberry Pi)
- Apple Silicon Macs (M1/M2)
- Cloud cost savings (ARM instances cheaper)

### Image Optimization

#### Current Metrics

- **Production Image**: 53.5MB (target: <50MB)
- **Base nginx:alpine**: 52.8MB
- **Application Overhead**: 0.7MB

#### Further Optimization Opportunities

1. **Distroless nginx** (custom build):
   - Remove shell and package manager
   - Potential size: ~40MB
   - Trade-off: Harder to debug

2. **Compress JavaScript bundles**:
   ```typescript
   // vite.config.ts
   import viteCompression from 'vite-plugin-compression';

   export default defineConfig({
     plugins: [
       react(),
       viteCompression({ algorithm: 'brotli' })
     ]
   });
   ```

3. **Tree-shaking optimization**:
   - Ensure proper ES module imports
   - Avoid default imports from large libraries
   - Example: `import { Button } from '@mui/material'` (not `import Button from '@mui/material/Button'`)

4. **Code splitting**:
   ```typescript
   // Lazy load routes
   const Dashboard = lazy(() => import('./pages/Dashboard'));
   ```

5. **Pre-compression** (nginx serves .gz files directly):
   ```dockerfile
   RUN find /usr/share/nginx/html -type f \( -name '*.js' -o -name '*.css' \) -exec gzip -k {} \;
   ```

### CI/CD Integration

Our CI/CD workflow (`.github/workflows/frontend-ci.yml`) includes Docker build and testing.

#### Current Workflow

1. **Lint and Type Check** (parallel)
2. **Build Application** (after lint/typecheck)
3. **Security Audit** (parallel with docker)
4. **Docker Build and Test**:
   - Build image with GitHub Actions cache
   - Tag with commit SHA and latest
   - Start container
   - Test health endpoint (30s timeout)
   - Test application root (HTML verification)
   - Capture logs on failure
5. **Deployment Check** (after all jobs)

#### GitHub Actions Cache

**Configuration**:
```yaml
- name: Build Docker image
  uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Benefits**:
- 10GB cache storage per repository
- 50-70% faster builds on cache hits
- Automatic cache invalidation
- Scoped to workflow branch

**Performance Metrics**:
- First build: ~180s
- Cached build: ~60s
- Time savings: ~120s (67% faster)

#### Registry Push (Future)

To push images to a container registry:

```yaml
- name: Log in to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_TOKEN }}

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: ./frontend
    push: true
    tags: |
      myregistry/frontend:${{ github.sha }}
      myregistry/frontend:latest
    cache-from: type=registry,ref=myregistry/frontend:cache
    cache-to: type=registry,ref=myregistry/frontend:cache,mode=max
```

**Required Secrets**:
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_TOKEN`: Docker Hub access token
- Or `GHCR_TOKEN` for GitHub Container Registry

---

## Summary

This guide covers comprehensive Docker usage for the React frontend application, from local development to production deployment. Key takeaways:

- **Multi-stage builds** reduce production image size by 84% (350MB → 54MB)
- **Non-root execution** enhances security in both development and production
- **Volume mounts** enable hot module replacement in development
- **BuildKit optimizations** speed up builds by 52%
- **Health checks** enable monitoring and orchestration
- **Security headers** protect against common web vulnerabilities
- **Comprehensive CI/CD integration** ensures images are tested before deployment

For questions or issues, consult the [Troubleshooting](#troubleshooting) section or contact the DevOps team.

**Version**: 1.0.0
**Last Updated**: 2025-10-15
**Next Review**: 2025-12-15
