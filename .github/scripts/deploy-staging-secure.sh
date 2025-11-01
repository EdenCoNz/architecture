#!/bin/bash

# ==============================================================================
# Alternative Secure Deployment Script for Staging
# ==============================================================================
# This is an alternative approach that passes environment variables more securely
# through stdin rather than as command-line arguments
# ==============================================================================

set -euo pipefail

echo "## Deploying to Staging (Secure Method)" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY
echo "### Deployment Configuration" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY

DEPLOY_DIR="/home/${SERVER_USER}/deployments/app-staging"
REGISTRY_PATH="${REGISTRY_PATH}"

# Log deployment details for visibility
echo "**Deployment Details:**" >> $GITHUB_STEP_SUMMARY
echo "- **Target Server**: ${SERVER_HOST}" >> $GITHUB_STEP_SUMMARY
echo "- **Deploy Directory**: ${DEPLOY_DIR}" >> $GITHUB_STEP_SUMMARY
echo "- **Backend Image**: ${REGISTRY_PATH}/backend:${BACKEND_VERSION}-${GITHUB_SHA}" >> $GITHUB_STEP_SUMMARY
echo "- **Frontend Image**: ${REGISTRY_PATH}/frontend:${FRONTEND_VERSION}-${GITHUB_SHA}" >> $GITHUB_STEP_SUMMARY
echo "- **Registry**: ${REGISTRY}" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY

echo "### Deployment Progress" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY

# ================================================================
# SECURE METHOD: Pass environment variables through stdin
# ================================================================
echo "#### Executing deployment on server (Secure Method)" >> $GITHUB_STEP_SUMMARY
echo "Passing sensitive environment variables through stdin to avoid shell escaping issues..." >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY

# Create a temporary script that will be executed on the remote server
# This avoids passing sensitive data through command-line arguments
cat << 'REMOTE_SCRIPT' | ssh -tt -i ~/.ssh/id_ed25519 ${SERVER_USER}@${SERVER_HOST} "cat > /tmp/deploy-env.sh && chmod +x /tmp/deploy-env.sh"
#!/bin/bash
set -euo pipefail

# Read environment variables from stdin
while IFS='=' read -r key value; do
    export "$key=$value"
done

# Change to deployment directory and run deployment
cd "${DEPLOY_DIR}"
bash deploy-staging.sh
REMOTE_SCRIPT

# Pass environment variables through stdin (safer than command-line)
{
    echo "REGISTRY=${REGISTRY}"
    echo "GITHUB_ACTOR=${GITHUB_ACTOR}"
    echo "GITHUB_TOKEN=${GITHUB_TOKEN}"
    echo "REDIS_PASSWORD=${REDIS_PASSWORD}"
} | ssh -tt -i ~/.ssh/id_ed25519 ${SERVER_USER}@${SERVER_HOST} \
    "export DEPLOY_DIR='${DEPLOY_DIR}' && /tmp/deploy-env.sh && rm -f /tmp/deploy-env.sh"

# Capture exit code from SSH session
DEPLOY_EXIT_CODE=$?

echo "" >> $GITHUB_STEP_SUMMARY
echo "---" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY

if [ $DEPLOY_EXIT_CODE -eq 0 ]; then
  echo "✅ **Staging deployment completed successfully**" >> $GITHUB_STEP_SUMMARY
  echo "" >> $GITHUB_STEP_SUMMARY
  echo "All containers are healthy and running." >> $GITHUB_STEP_SUMMARY
else
  echo "❌ **Staging deployment encountered issues**" >> $GITHUB_STEP_SUMMARY
  echo "" >> $GITHUB_STEP_SUMMARY
  echo "Exit code: $DEPLOY_EXIT_CODE" >> $GITHUB_STEP_SUMMARY
  echo "" >> $GITHUB_STEP_SUMMARY
  echo "The deployment script failed during execution. Review the logs above for details." >> $GITHUB_STEP_SUMMARY
  echo "Common issues:" >> $GITHUB_STEP_SUMMARY
  echo "- Containers failed health checks" >> $GITHUB_STEP_SUMMARY
  echo "- Image pull failures" >> $GITHUB_STEP_SUMMARY
  echo "- Configuration errors" >> $GITHUB_STEP_SUMMARY
  echo "- Resource constraints (disk space, memory)" >> $GITHUB_STEP_SUMMARY
  exit $DEPLOY_EXIT_CODE
fi
