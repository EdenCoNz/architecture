# Quick Start - Deploy to Ubuntu Server

Fast-track guide to set up automated deployments in 15 minutes.

## Prerequisites Checklist

- [ ] Ubuntu server running (20.04 LTS or newer)
- [ ] Docker and Docker Compose installed on server
- [ ] Tailscale account created
- [ ] GitHub repository admin access

## 5-Minute Server Setup

```bash
# 1. Install Docker (on Ubuntu server)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Install Docker Compose
sudo apt-get install docker-compose-plugin

# 3. Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker  # or log out and back in

# 4. Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# 5. Get Tailscale IP (save this!)
tailscale ip -4
# Example output: 100.101.102.103
```

## 3-Minute SSH Key Setup

```bash
# On your local machine

# 1. Generate SSH key
ssh-keygen -t ed25519 -f ~/.ssh/github_deploy_ed25519 -N ""

# 2. Copy to server (replace USER and IP)
ssh-copy-id -i ~/.ssh/github_deploy_ed25519.pub USER@100.x.x.x

# 3. Test connection
ssh -i ~/.ssh/github_deploy_ed25519 USER@100.x.x.x "echo 'Success!'"

# 4. Display private key (copy this for GitHub)
cat ~/.ssh/github_deploy_ed25519
```

## 2-Minute Tailscale OAuth Setup

1. Visit: https://login.tailscale.com/admin/settings/oauth
2. Click "Generate OAuth client"
3. Settings:
   - Description: `GitHub Actions`
   - Tags: `tag:ci`
   - Scopes: `devices:write`
4. Copy **both** Client ID and Secret

## 3-Minute GitHub Secrets Setup

Go to: `GitHub Repo → Settings → Secrets and variables → Actions`

Add these 5 secrets:

| Name | Value |
|------|-------|
| `TS_OAUTH_CLIENT_ID` | From Tailscale OAuth client |
| `TS_OAUTH_SECRET` | From Tailscale OAuth client |
| `SSH_PRIVATE_KEY` | Output of `cat ~/.ssh/github_deploy_ed25519` |
| `SERVER_HOST` | Output of `tailscale ip -4` on server |
| `SERVER_USER` | Your SSH username (e.g., `ubuntu`) |

## 2-Minute Workflow Integration

### Backend Deployment

Add to `.github/workflows/backend-ci.yml`:

```yaml
  deploy:
    uses: ./.github/workflows/deploy-to-ubuntu.yml
    needs: [build-backend-prod-container]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    with:
      service_name: backend
      docker_image_artifact: backend-prod-container-${{ github.sha }}
      docker_image_file: backend-prod.tar
      docker_compose_file: backend/docker-compose.production.yml
      container_name: backend-app
      image_name: backend-prod
    secrets: inherit
```

### Frontend Deployment

Add to `.github/workflows/frontend-ci.yml`:

```yaml
  deploy:
    uses: ./.github/workflows/deploy-to-ubuntu.yml
    needs: [build-frontend-prod-container]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    with:
      service_name: frontend
      docker_image_artifact: frontend-prod-container-${{ github.sha }}
      docker_image_file: frontend-prod.tar
      docker_compose_file: frontend/docker-compose.prod.yml
      container_name: frontend-app
      image_name: frontend-prod
    secrets: inherit
```

## Test It!

```bash
# 1. Commit and push to a feature branch
git checkout -b test-deployment
git add .
git commit -m "Test: Add deployment workflow"
git push origin test-deployment

# 2. Create PR to main and merge

# 3. Check GitHub Actions tab for deployment status

# 4. On server, verify deployment
ssh USER@100.x.x.x
cd ~/deployments/backend-deploy  # or frontend-deploy
docker compose ps
docker compose logs -f
```

## Quick Troubleshooting

**Deployment fails at "Connect to Tailscale"**
```bash
# On server, check Tailscale status
tailscale status
sudo systemctl restart tailscaled
```

**Deployment fails at "SSH connection"**
```bash
# Verify SSH key is correct
ssh -i ~/.ssh/github_deploy_ed25519 USER@100.x.x.x
# Should connect without password
```

**Deployment fails at "Docker operations"**
```bash
# On server, verify docker group membership
groups $USER
# Should include 'docker'

# If not, add and re-login
sudo usermod -aG docker $USER
```

**Container won't start**
```bash
# On server, check logs
cd ~/deployments/SERVICE-deploy
docker compose logs --tail 100

# Check if image loaded
docker images | grep prod
```

## What's Next?

1. ✅ You now have automated deployments!
2. 📚 Read `DEPLOYMENT_SETUP_GUIDE.md` for detailed configuration
3. 📖 Check `DEPLOYMENT_INTEGRATION_EXAMPLES.md` for advanced usage
4. 🔐 Review `.github/workflows/.env` for security best practices
5. 📊 Set up monitoring (Prometheus, Grafana)
6. 💾 Configure automated backups

## Folder Structure on Server

After first deployment:

```
~/deployments/
├── backend-deploy/
│   ├── docker-compose.yml
│   ├── .env.production
│   └── backend-prod.tar (removed after load)
└── frontend-deploy/
    ├── docker-compose.yml
    └── frontend-prod.tar (removed after load)
```

## Useful Commands

```bash
# On server

# View all deployments
cd ~/deployments && ls -la

# Check container status
docker compose ps

# View logs (follow mode)
docker compose logs -f SERVICE_NAME

# Restart a service
docker compose restart SERVICE_NAME

# Stop all services
docker compose down

# Clean up old images
docker image prune -a

# View resource usage
docker stats

# Manual rollback
docker compose down
docker images | grep prod  # find previous version
# Update compose file to use previous tag
docker compose up -d
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│               GitHub Actions                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  Build   │→ │   Test   │→ │ Publish  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
│                                    ↓                │
│                           ┌──────────────────┐     │
│                           │ Deploy Workflow  │     │
│                           │ (Reusable)       │     │
│                           └────────┬─────────┘     │
└─────────────────────────────────────┼──────────────┘
                                      ↓
                            ┌──────────────────┐
                            │   Tailscale VPN  │
                            └────────┬─────────┘
                                     ↓
                      ┌──────────────────────────┐
                      │    Ubuntu Server         │
                      │  ┌────────────────────┐  │
                      │  │  Docker Compose    │  │
                      │  │  ┌──────┐ ┌──────┐ │  │
                      │  │  │ App  │ │  DB  │ │  │
                      │  │  └──────┘ └──────┘ │  │
                      │  └────────────────────┘  │
                      └──────────────────────────┘
```

## Security Checklist

- [x] Using Tailscale VPN (encrypted tunnel)
- [x] SSH key authentication (no passwords)
- [x] Secrets stored in GitHub (not in code)
- [x] Non-root user for deployments
- [x] Docker socket access via group (not sudo)
- [ ] Firewall configured (ufw)
- [ ] Automatic security updates enabled
- [ ] Secrets rotation schedule set
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented

## Common Parameters

Customize deployment behavior:

```yaml
with:
  # Basic (required)
  service_name: backend
  docker_image_artifact: backend-prod-container-${{ github.sha }}
  docker_image_file: backend-prod.tar
  docker_compose_file: backend/docker-compose.production.yml
  container_name: backend-app
  image_name: backend-prod

  # Optional - customize these
  remote_deploy_path: ~/deployments        # Default: ~
  health_check_enabled: true               # Default: true
  health_check_retries: 15                 # Default: 10
  health_check_interval: 3                 # Default: 3 (seconds)
  compose_profiles: with-celery            # Default: '' (none)
  env_file: backend/.env.production        # Default: '' (none)
```

## Support & Documentation

- **Quick Start**: This file
- **Full Setup Guide**: `DEPLOYMENT_SETUP_GUIDE.md`
- **Integration Examples**: `DEPLOYMENT_INTEGRATION_EXAMPLES.md`
- **Secrets Reference**: `.github/workflows/.env`
- **Reusable Workflow**: `.github/workflows/deploy-to-ubuntu.yml`

## Tips

💡 **Pro Tip**: Enable `workflow_dispatch` trigger for manual deployments during testing:

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:  # Allows manual trigger from Actions tab
```

💡 **Pro Tip**: Use GitHub Environments for approval gates:

```yaml
deploy:
  environment:
    name: production
    url: https://your-app.com
  uses: ./.github/workflows/deploy-to-ubuntu.yml
  # ... rest of config
```

💡 **Pro Tip**: Tag your Docker images with semantic versions:

```yaml
# In build job
docker tag backend-prod:${{ github.sha }} backend-prod:v1.2.3
docker tag backend-prod:${{ github.sha }} backend-prod:latest
```

## Success! 🎉

Your deployment pipeline is ready. Push to main and watch the magic happen! ✨
