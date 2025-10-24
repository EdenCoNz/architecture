# Deployment Integration Examples

This document provides examples of how to integrate the reusable `deploy-to-ubuntu.yml` workflow into your frontend and backend CI/CD pipelines.

## Table of Contents

- [Overview](#overview)
- [Backend Deployment Integration](#backend-deployment-integration)
- [Frontend Deployment Integration](#frontend-deployment-integration)
- [Required Secrets](#required-secrets)
- [Testing the Integration](#testing-the-integration)
- [Troubleshooting](#troubleshooting)

## Overview

The `deploy-to-ubuntu.yml` reusable workflow handles deployment to an Ubuntu server via Tailscale VPN. It:

- Downloads Docker image artifacts from previous workflow jobs
- Establishes secure Tailscale VPN connection
- Transfers files to server via SSH
- Deploys using Docker Compose
- Verifies deployment health
- Provides detailed status reporting

## Backend Deployment Integration

### Step 1: Create Production Docker Compose File

Create `backend/docker-compose.production.yml`:

```yaml
services:
  backend:
    image: backend-prod:${IMAGE_TAG:-latest}
    container_name: backend-app
    restart: unless-stopped

    env_file:
      - .env.production

    environment:
      DJANGO_SETTINGS_MODULE: config.settings.production
      DEBUG: "False"

    ports:
      - "8000:8000"

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s

    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Step 2: Add Deployment Job to backend-ci.yml

Add this job to `.github/workflows/backend-ci.yml`:

```yaml
  # Job: Deploy Backend to Production (add after publish-backend-container-prod)
  deploy-backend-production:
    name: Deploy Backend to Production
    uses: ./.github/workflows/deploy-to-ubuntu.yml
    needs: [publish-backend-container-prod]
    # Only deploy on pushes to main branch (not on PRs)
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    with:
      # Service identification
      service_name: backend

      # Docker image configuration
      docker_image_artifact: backend-prod-container-${{ github.sha }}
      docker_image_file: backend-prod.tar
      image_name: backend-prod:${{ github.sha }}

      # Docker Compose configuration
      docker_compose_file: backend/docker-compose.production.yml
      container_name: backend-app

      # Deployment options
      remote_deploy_path: ~/deployments
      health_check_enabled: true
      health_check_retries: 15
      health_check_interval: 3

      # Optional: Enable Celery workers
      # compose_profiles: with-celery

    secrets: inherit

    permissions:
      contents: read
```

### Step 3: Update Job Dependencies

If you have other jobs that should run after deployment (like smoke tests), update their `needs` dependencies:

```yaml
  post-deployment-tests:
    name: Post-Deployment Smoke Tests
    needs: [deploy-backend-production]
    runs-on: ubuntu-latest
    # ... rest of job configuration
```

## Frontend Deployment Integration

### Step 1: Create Production Docker Compose File

Create `frontend/docker-compose.prod.yml`:

```yaml
services:
  frontend:
    image: frontend-prod:${IMAGE_TAG:-latest}
    container_name: frontend-app
    restart: unless-stopped

    environment:
      NODE_ENV: production
      # Runtime configuration loaded from backend API
      # No build-time env vars needed

    ports:
      - "3000:80"  # Nginx serves on port 80 inside container

    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:80/"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 20s

    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Step 2: Add Deployment Job to frontend-ci.yml

Add this job to `.github/workflows/frontend-ci.yml`:

```yaml
  # Job: Deploy Frontend to Production (add after publish-frontend-container-prod)
  deploy-frontend-production:
    name: Deploy Frontend to Production
    uses: ./.github/workflows/deploy-to-ubuntu.yml
    needs: [publish-frontend-container-prod]
    # Only deploy on pushes to main branch (not on PRs)
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    with:
      # Service identification
      service_name: frontend

      # Docker image configuration
      docker_image_artifact: frontend-prod-container-${{ github.sha }}
      docker_image_file: frontend-prod.tar
      image_name: frontend-prod:${{ github.sha }}

      # Docker Compose configuration
      docker_compose_file: frontend/docker-compose.prod.yml
      container_name: frontend-app

      # Deployment options
      remote_deploy_path: ~/deployments
      health_check_enabled: true
      health_check_retries: 10
      health_check_interval: 3

    secrets: inherit

    permissions:
      contents: read
```

## Multi-Service Deployment

If you want to deploy both frontend and backend together with shared services (PostgreSQL, Redis), create a unified compose file:

### unified-production-compose.yml

```yaml
services:
  # Database
  db:
    image: postgres:16-alpine
    container_name: prod-db
    restart: unless-stopped
    env_file:
      - .env.production
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - prod-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Cache
  redis:
    image: redis:7-alpine
    container_name: prod-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - prod-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Backend
  backend:
    image: backend-prod:${BACKEND_TAG:-latest}
    container_name: backend-app
    restart: unless-stopped
    env_file:
      - .env.production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    networks:
      - prod-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
      interval: 30s
      timeout: 3s
      retries: 3

  # Frontend
  frontend:
    image: frontend-prod:${FRONTEND_TAG:-latest}
    container_name: frontend-app
    restart: unless-stopped
    environment:
      BACKEND_URL: http://backend:8000
    depends_on:
      backend:
        condition: service_healthy
    ports:
      - "3000:80"
    networks:
      - prod-network
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:80/"]
      interval: 30s
      timeout: 3s
      retries: 3

networks:
  prod-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

## Required Secrets

Configure these secrets in GitHub repository settings (Settings → Secrets and variables → Actions):

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `TS_OAUTH_CLIENT_ID` | Tailscale OAuth client ID | `kxxxxx` |
| `TS_OAUTH_SECRET` | Tailscale OAuth secret | `tskey-client-kxxxxx` |
| `SSH_PRIVATE_KEY` | SSH private key (ED25519) | `-----BEGIN OPENSSH PRIVATE KEY-----\n...` |
| `SERVER_HOST` | Tailscale IP of Ubuntu server | `100.101.102.103` |
| `SERVER_USER` | SSH username | `ubuntu` or `deploy` |

See `.github/workflows/.env` for detailed instructions on creating each secret.

## Testing the Integration

### 1. Test SSH Connection Locally

Before pushing to GitHub, verify SSH connectivity:

```bash
# From your local machine (with Tailscale running)
ssh -i ~/.ssh/github_deploy_ed25519 ubuntu@100.x.x.x "echo 'SSH test successful'"
```

### 2. Test Docker Permissions

Verify the deployment user can run Docker without sudo:

```bash
ssh -i ~/.ssh/github_deploy_ed25519 ubuntu@100.x.x.x "docker ps"
```

If this fails, add the user to the docker group:

```bash
# On the Ubuntu server
sudo usermod -aG docker ubuntu
# Log out and back in for changes to take effect
```

### 3. Dry Run Deployment

Test the workflow with `workflow_dispatch` trigger:

1. Add to your workflow file (temporarily):

```yaml
on:
  workflow_dispatch:  # Add this for manual testing
  push:
    branches: [main]
```

2. Go to Actions tab in GitHub → Select your workflow → Click "Run workflow"
3. Monitor the execution and check the step summary for detailed logs

### 4. Verify Deployment on Server

After successful deployment, check container status on the server:

```bash
# On the Ubuntu server
cd ~/deployments/backend-deploy  # or frontend-deploy
docker compose ps
docker compose logs -f backend-app
docker stats backend-app
```

## Troubleshooting

### SSH Connection Fails

**Error**: "Could not scan SSH host keys"

**Solutions**:
1. Verify Tailscale is running on both GitHub Actions runner and server:
   ```bash
   tailscale status
   ```

2. Check SSH service on server:
   ```bash
   sudo systemctl status sshd
   ```

3. Verify SERVER_HOST secret is the Tailscale IP (not public IP):
   ```bash
   # On server
   tailscale ip -4
   ```

### Container Fails to Start

**Error**: "Container did not become healthy within the timeout period"

**Solutions**:
1. Check container logs on server:
   ```bash
   docker compose logs backend-app
   ```

2. Verify environment variables are set correctly:
   ```bash
   # Create .env.production on server if missing
   vim ~/deployments/backend-deploy/.env.production
   ```

3. Test container locally:
   ```bash
   # Pull the same image and test locally
   docker pull ghcr.io/yourorg/backend:prod-abc1234
   docker run --rm -it ghcr.io/yourorg/backend:prod-abc1234 /bin/bash
   ```

### Permission Denied

**Error**: "Permission denied" during Docker operations

**Solution**: Add deployment user to docker group:
```bash
sudo usermod -aG docker $USER
# Log out and back in
newgrp docker
```

### Image Not Found

**Error**: "Failed to load Docker image"

**Solutions**:
1. Verify artifact was uploaded in previous job:
   - Check workflow run → Artifacts section

2. Verify artifact name matches:
   ```yaml
   docker_image_artifact: backend-prod-container-${{ github.sha }}
   ```

3. Check artifact file exists:
   ```yaml
   docker_image_file: backend-prod.tar
   ```

### Tailscale Connection Issues

**Error**: "Ping failed" or "Server unreachable"

**Solutions**:
1. Verify Tailscale OAuth credentials are correct
2. Check server is online in Tailscale admin console
3. Verify firewall rules allow Tailscale traffic
4. Check server Tailscale status:
   ```bash
   sudo tailscale status
   sudo tailscale ping github-actions-runner
   ```

## Advanced Configuration

### Blue-Green Deployment

For zero-downtime deployments, modify the compose file to use multiple containers:

```yaml
services:
  backend-blue:
    image: backend-prod:blue
    # ... configuration

  backend-green:
    image: backend-prod:green
    # ... configuration

  nginx:
    image: nginx:alpine
    # Load balancer configuration
    depends_on:
      - backend-blue
      - backend-green
```

### Rollback Strategy

To enable easy rollback, tag images with version numbers:

```yaml
# In your workflow
docker tag backend-prod:${{ github.sha }} backend-prod:v1.2.3
docker tag backend-prod:${{ github.sha }} backend-prod:latest
```

Then on the server:

```bash
# Rollback to previous version
docker tag backend-prod:v1.2.2 backend-prod:latest
docker compose up -d
```

### Health Check Customization

Adjust health check parameters based on your application's startup time:

```yaml
with:
  health_check_enabled: true
  health_check_retries: 20      # More retries for slow-starting apps
  health_check_interval: 5      # Longer interval between checks
```

### Multiple Environments

Deploy to staging and production using different inputs:

```yaml
  deploy-staging:
    uses: ./.github/workflows/deploy-to-ubuntu.yml
    if: github.ref == 'refs/heads/develop'
    with:
      service_name: backend-staging
      remote_deploy_path: ~/deployments/staging
    secrets: inherit

  deploy-production:
    uses: ./.github/workflows/deploy-to-ubuntu.yml
    if: github.ref == 'refs/heads/main'
    with:
      service_name: backend-production
      remote_deploy_path: ~/deployments/production
    secrets: inherit
```

## Next Steps

1. Set up monitoring (Prometheus, Grafana) on the server
2. Configure log aggregation (ELK Stack, Loki)
3. Implement automated backups for volumes
4. Set up alerting for deployment failures
5. Create runbooks for common deployment issues

## Resources

- [Tailscale GitHub Action Documentation](https://github.com/tailscale/github-action)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitHub Actions Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- Project secrets documentation: `.github/workflows/.env`
