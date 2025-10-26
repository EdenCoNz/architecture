# Deployment Setup Guide - Ubuntu Server via Tailscale

This guide walks you through setting up automated deployments from GitHub Actions to your Ubuntu server using the reusable `deploy-to-ubuntu.yml` workflow.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Server Setup](#server-setup)
- [Tailscale Setup](#tailscale-setup)
- [SSH Key Setup](#ssh-key-setup)
- [GitHub Secrets Configuration](#github-secrets-configuration)
- [Workflow Integration](#workflow-integration)
- [Testing and Validation](#testing-and-validation)
- [Maintenance](#maintenance)
- [Security Considerations](#security-considerations)

## Overview

The deployment workflow provides:

- **Secure Connectivity**: Uses Tailscale VPN for encrypted connections between GitHub Actions and your server
- **Automated Deployment**: Triggered on successful builds to the main branch
- **Container-Based**: Deploys Docker containers using Docker Compose
- **Health Verification**: Validates deployment success with configurable health checks
- **Comprehensive Logging**: Detailed step summaries and error reporting

## Architecture

```
┌─────────────────────┐
│  GitHub Actions     │
│  (Workflow Runner)  │
└──────────┬──────────┘
           │
           │ 1. Connect to Tailscale VPN
           ▼
    ┌──────────────┐
    │  Tailscale   │
    │  VPN Network │
    └──────┬───────┘
           │
           │ 2. SSH over Tailscale
           ▼
┌──────────────────────┐
│  Ubuntu Server       │
│  - Docker Engine     │
│  - Docker Compose    │
│  - Application       │
└──────────────────────┘

Deployment Flow:
1. Build → 2. Test → 3. Publish → 4. Deploy → 5. Verify
```

## Prerequisites

### On Your Local Machine

- SSH key generation tools (ssh-keygen)
- Tailscale account and client
- Access to GitHub repository settings

### On Ubuntu Server

- Ubuntu 20.04 LTS or newer
- Docker Engine installed
- Docker Compose V2 installed
- Tailscale installed and configured
- SSH server running
- Sudo access (for initial setup)

## Server Setup

### 1. Install Docker Engine

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### 2. Create Deployment User

```bash
# Create dedicated deployment user (optional but recommended)
sudo useradd -m -s /bin/bash deploy

# Add user to docker group (allows Docker commands without sudo)
sudo usermod -aG docker deploy

# Create deployment directories
sudo mkdir -p /opt/deployments
sudo chown deploy:deploy /opt/deployments

# If using existing user (e.g., ubuntu)
sudo usermod -aG docker ubuntu
```

**Important**: Log out and back in after adding user to docker group for changes to take effect.

### 3. Configure Firewall (if using UFW)

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow application ports (adjust based on your needs)
sudo ufw allow 8000/tcp  # Backend API
sudo ufw allow 3000/tcp  # Frontend
sudo ufw allow 5432/tcp  # PostgreSQL (if exposing externally - not recommended)

# Enable firewall
sudo ufw enable
sudo ufw status
```

### 4. Create Docker Network (Optional)

```bash
# Create a dedicated network for production containers
docker network create prod-network
```

## Tailscale Setup

### 1. Install Tailscale on Ubuntu Server

```bash
# Add Tailscale's package signing key and repository
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list

# Install Tailscale
sudo apt-get update
sudo apt-get install -y tailscale

# Start Tailscale and authenticate
sudo tailscale up

# Verify status
tailscale status

# Get Tailscale IP (save this for GitHub secrets)
tailscale ip -4
# Example output: 100.101.102.103
```

### 2. Create Tailscale OAuth Client for GitHub Actions

1. Go to [Tailscale Admin Console](https://login.tailscale.com/admin/settings/oauth)
2. Click **"Generate OAuth client"**
3. Configure the client:
   - **Description**: `GitHub Actions CI/CD Deployment`
   - **Tags**: `tag:ci` (you may need to add this tag to your Tailscale ACL)
   - **Scopes**: `devices:write`
4. **Copy and save** the OAuth Client ID and Secret (shown only once)

### 3. Update Tailscale ACL (Optional)

Add a tag for CI/CD clients in your Tailscale ACL:

```json
{
  "tagOwners": {
    "tag:ci": ["your-email@example.com"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["tag:ci"],
      "dst": ["your-server-hostname:*"]
    }
  ]
}
```

## SSH Key Setup

### 1. Generate SSH Key Pair (On Your Local Machine)

```bash
# Generate ED25519 key pair
ssh-keygen -t ed25519 -C "github-actions-deployment" -f ~/.ssh/github_deploy_ed25519

# This creates two files:
# - ~/.ssh/github_deploy_ed25519 (private key)
# - ~/.ssh/github_deploy_ed25519.pub (public key)
```

**Security Note**: Use a strong passphrase or leave empty for CI/CD use. If empty, store the private key securely.

### 2. Copy Public Key to Server

**Option A: Using ssh-copy-id (Recommended)**

```bash
# Replace 'deploy' with your deployment user
# Replace 'your-tailscale-ip' with the server's Tailscale IP
ssh-copy-id -i ~/.ssh/github_deploy_ed25519.pub deploy@your-tailscale-ip
```

**Option B: Manual Copy**

```bash
# Display public key
cat ~/.ssh/github_deploy_ed25519.pub

# On the server, add to authorized_keys
ssh deploy@your-tailscale-ip
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat >> ~/.ssh/authorized_keys
# Paste the public key content
# Press Ctrl+D to save
chmod 600 ~/.ssh/authorized_keys
```

### 3. Test SSH Connection

```bash
# Test connection with the new key
ssh -i ~/.ssh/github_deploy_ed25519 deploy@your-tailscale-ip

# If successful, you should be logged into the server without password
```

### 4. Extract Private Key for GitHub Secrets

```bash
# Display the ENTIRE private key (including headers and footers)
cat ~/.ssh/github_deploy_ed25519

# Copy everything from -----BEGIN OPENSSH PRIVATE KEY----- to -----END OPENSSH PRIVATE KEY-----
```

**Security Warning**:
- Store this private key securely
- Never commit it to version control
- Delete it from your local machine after adding to GitHub Secrets
- Consider using a password manager for temporary storage

## GitHub Secrets Configuration

Navigate to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### Required Secrets

| Secret Name | Value | Example |
|-------------|-------|---------|
| `TS_OAUTH_CLIENT_ID` | Tailscale OAuth client ID | `kxxxxxxxxxxxxx` |
| `TS_OAUTH_SECRET` | Tailscale OAuth secret | `tskey-client-kxxxxxxxxxxxxx` |
| `SSH_PRIVATE_KEY` | **Complete** SSH private key including headers | `-----BEGIN OPENSSH PRIVATE KEY-----\nxxxxxx\n-----END OPENSSH PRIVATE KEY-----` |
| `SERVER_HOST` | Server's Tailscale IP address | `100.101.102.103` |
| `SERVER_USER` | SSH username on server | `deploy` or `ubuntu` |

### Adding Secrets Step-by-Step

1. **TS_OAUTH_CLIENT_ID**
   - Name: `TS_OAUTH_CLIENT_ID`
   - Value: Paste the OAuth client ID from Tailscale
   - Click "Add secret"

2. **TS_OAUTH_SECRET**
   - Name: `TS_OAUTH_SECRET`
   - Value: Paste the OAuth secret from Tailscale
   - Click "Add secret"

3. **SSH_PRIVATE_KEY**
   - Name: `SSH_PRIVATE_KEY`
   - Value: Paste the **entire** private key including:
     ```
     -----BEGIN OPENSSH PRIVATE KEY-----
     [key content]
     -----END OPENSSH PRIVATE KEY-----
     ```
   - Click "Add secret"

4. **SERVER_HOST**
   - Name: `SERVER_HOST`
   - Value: Your server's Tailscale IP (e.g., `100.101.102.103`)
   - Click "Add secret"

5. **SERVER_USER**
   - Name: `SERVER_USER`
   - Value: Your SSH username (e.g., `deploy` or `ubuntu`)
   - Click "Add secret"

### Verify Secrets

After adding all secrets, you should see them listed (values are hidden):

```
TS_OAUTH_CLIENT_ID        Set • Updated XXXX
TS_OAUTH_SECRET           Set • Updated XXXX
SSH_PRIVATE_KEY           Set • Updated XXXX
SERVER_HOST               Set • Updated XXXX
SERVER_USER               Set • Updated XXXX
```

## Workflow Integration

### 1. Backend Deployment

Add to `.github/workflows/backend-ci.yml`:

```yaml
  deploy-backend:
    name: Deploy Backend to Production
    uses: ./.github/workflows/deploy-to-ubuntu.yml
    needs: [build-backend-prod-container, security-scan-backend-prod, test-backend-prod-container]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    with:
      service_name: backend
      docker_image_artifact: backend-prod-container-${{ github.sha }}
      docker_image_file: backend-prod.tar
      docker_compose_file: compose.production.yml  # Updated: Use root compose file (Feature 15 Story 15.5)
      container_name: backend-app
      image_name: backend-prod
      remote_deploy_path: ~/deployments
      health_check_enabled: true
      health_check_retries: 15
      health_check_interval: 3

    secrets: inherit

    permissions:
      contents: read
```

### 2. Frontend Deployment

Add to `.github/workflows/frontend-ci.yml`:

```yaml
  deploy-frontend:
    name: Deploy Frontend to Production
    uses: ./.github/workflows/deploy-to-ubuntu.yml
    needs: [build-frontend-prod-container, security-scan-frontend-prod, test-frontend-prod-container]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    with:
      service_name: frontend
      docker_image_artifact: frontend-prod-container-${{ github.sha }}
      docker_image_file: frontend-prod.tar
      docker_compose_file: compose.production.yml  # Updated: Use root compose file (Feature 15 Story 15.6)
      container_name: frontend-app
      image_name: frontend-prod
      remote_deploy_path: ~/deployments
      health_check_enabled: true
      health_check_retries: 10
      health_check_interval: 3

    secrets: inherit

    permissions:
      contents: read
```

### 3. Create Production Docker Compose Files

**Note:** As of Feature 15 (Stories 15.5 and 15.6), backend and frontend services are defined in root-level compose files. Service-specific compose files have been removed.

**Root Production File: `compose.production.yml`**

```yaml
services:
  backend:
    image: backend-prod:latest
    container_name: backend-app
    restart: unless-stopped
    env_file:
      - .env.production
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s

  frontend:
    image: frontend-prod:latest
    container_name: frontend-app
    restart: unless-stopped
    environment:
      NODE_ENV: production
    ports:
      - "3000:80"
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:80/"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 20s
```

### 4. Create Environment Files on Server

```bash
# On the server, create production environment files
# Backend
vim ~/deployments/backend-deploy/.env.production

# Add your production environment variables:
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_HOST=localhost
DB_NAME=production_db
DB_USER=db_user
DB_PASSWORD=secure_password
# ... other variables
```

## Testing and Validation

### 1. Test Tailscale Connectivity

```bash
# On your local machine (with Tailscale running)
tailscale ping your-server-hostname

# Or ping by IP
ping 100.x.x.x
```

### 2. Test SSH Connection

```bash
# From local machine
ssh -i ~/.ssh/github_deploy_ed25519 deploy@100.x.x.x "echo 'SSH test successful'"

# Test Docker access
ssh -i ~/.ssh/github_deploy_ed25519 deploy@100.x.x.x "docker ps"
```

### 3. Manual Test Deployment

```bash
# On the server, simulate what the workflow does
cd ~/deployments/backend-deploy

# Load a Docker image (if you have a tar file)
docker load -i backend-prod.tar

# Start with docker compose
docker compose -f docker-compose.yml up -d

# Check status
docker compose ps
docker compose logs -f
```

### 4. Trigger Workflow

1. Make a change to your code
2. Commit to a feature branch
3. Create a pull request to main
4. After PR is merged, the workflow will trigger automatically
5. Monitor the workflow in the Actions tab

### 5. Verify Deployment

```bash
# On the server
cd ~/deployments/backend-deploy  # or frontend-deploy

# Check container status
docker compose ps

# View logs
docker compose logs -f backend-app

# Check health
curl http://localhost:8000/api/v1/health/

# Monitor resources
docker stats backend-app
```

## Maintenance

### Regular Tasks

**Weekly**:
- Review deployment logs for errors
- Check disk usage: `docker system df`
- Clean up unused images: `docker image prune -a`

**Monthly**:
- Update server packages: `sudo apt update && sudo apt upgrade`
- Review and rotate secrets if needed
- Backup volumes: `docker run --rm -v backend_data:/data -v $(pwd):/backup ubuntu tar czf /backup/backend_data_backup.tar.gz /data`

**Quarterly**:
- Rotate SSH keys
- Update Tailscale OAuth tokens
- Review and update ACLs

### Monitoring

Set up monitoring for:
- Container health: `docker compose ps`
- Resource usage: `docker stats`
- Disk space: `df -h`
- Application logs: `docker compose logs`

Consider implementing:
- Prometheus + Grafana for metrics
- ELK Stack or Loki for log aggregation
- Uptime monitoring (e.g., UptimeRobot, Pingdom)

### Backup Strategy

```bash
# Backup script example
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
docker exec backend-db pg_dump -U postgres production_db > $BACKUP_DIR/db_$DATE.sql

# Backup volumes
docker run --rm -v postgres_data:/data -v $BACKUP_DIR:/backup ubuntu tar czf /backup/postgres_$DATE.tar.gz /data

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Rollback Procedure

If a deployment fails:

```bash
# On the server
cd ~/deployments/backend-deploy

# Stop current containers
docker compose down

# List available images
docker images backend-prod

# Load previous version (if you kept the tar)
docker load -i backend-prod-previous.tar

# Or pull from registry
docker pull ghcr.io/yourorg/backend:previous-tag

# Update compose file to use previous tag
vim docker-compose.yml
# Change image: backend-prod:current to image: backend-prod:previous

# Start with previous version
docker compose up -d
```

## Security Considerations

### Server Hardening

1. **Disable password authentication**:
   ```bash
   sudo vim /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   # Set: PermitRootLogin no
   sudo systemctl restart sshd
   ```

2. **Enable automatic security updates**:
   ```bash
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure --priority=low unattended-upgrades
   ```

3. **Configure fail2ban**:
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

### Docker Security

1. **Run containers as non-root** (already implemented in Dockerfiles)
2. **Limit container resources** (CPU, memory) in compose files
3. **Use read-only filesystems where possible**
4. **Scan images for vulnerabilities** (Trivy - already in CI/CD)

### Secret Management

1. **Never commit secrets** to version control
2. **Rotate secrets regularly**:
   - SSH keys: every 6-12 months
   - OAuth tokens: every 90 days
   - Database passwords: annually
3. **Use environment-specific secrets**
4. **Audit secret access** in GitHub settings

### Network Security

1. **Use Tailscale ACLs** to restrict access
2. **Minimize exposed ports**
3. **Use HTTPS** for all external traffic
4. **Implement rate limiting** in your application

## Troubleshooting

See `DEPLOYMENT_INTEGRATION_EXAMPLES.md` for detailed troubleshooting steps.

Common issues:
- **SSH connection fails**: Check Tailscale status, SSH service, firewall rules
- **Container won't start**: Check logs, environment variables, resource limits
- **Health checks fail**: Increase retries/interval, verify health endpoint
- **Permission denied**: Ensure user is in docker group

## Additional Resources

- [Tailscale Documentation](https://tailscale.com/kb/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- Project secrets: `.github/workflows/.env`
- Integration examples: `.github/workflows/DEPLOYMENT_INTEGRATION_EXAMPLES.md`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review workflow logs in GitHub Actions
3. Check server logs: `docker compose logs`
4. Review project documentation in `context/devops/`

## License

This deployment configuration is part of the project and follows the same license.
