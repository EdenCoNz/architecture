#!/bin/bash

# ==============================================================================
# Staging Deployment Script
# ==============================================================================
# This script is executed on the staging server via SSH to deploy the application.
# It performs the following steps:
# 1. Stop existing containers
# 2. Authenticate to container registry
# 3. Pull latest images
# 4. Start services with health monitoring
# 5. Post-deployment tasks (Redis cache flush, Docker image cleanup)
# ==============================================================================

# Enable strict error handling:
# -e: Exit immediately if any command fails
# -u: Treat undefined variables as errors
# -o pipefail: Return exit code of the first failing command in a pipeline
set -euo pipefail

# Required environment variables (passed from GitHub Actions):
# - REGISTRY: Container registry URL (e.g., ghcr.io)
# - GITHUB_ACTOR: GitHub username for registry authentication
# - GITHUB_TOKEN: GitHub token for registry authentication
# - REDIS_PASSWORD: Redis password for cache flush operation

echo ""
echo "==================================================================="
echo "STAGING DEPLOYMENT - STARTING"
echo "==================================================================="
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "Deploy Directory: $(pwd)"
echo "==================================================================="
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Stopping Existing Containers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose -f docker-compose.yml -f compose.staging.yml down --remove-orphans || true
echo "✅ Existing containers stopped"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Authenticating to Container Registry"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Registry: ${REGISTRY}"
echo "User: ${GITHUB_ACTOR}"
echo "${GITHUB_TOKEN}" | docker login ${REGISTRY} -u ${GITHUB_ACTOR} --password-stdin
echo "✅ Successfully authenticated to registry"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Pulling Latest Images from Registry"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose -f docker-compose.yml -f compose.staging.yml config | grep "image:" | sed 's/^ *//' || true
echo ""
docker compose -f docker-compose.yml -f compose.staging.yml pull
echo "✅ Images pulled successfully"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Starting Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose -f docker-compose.yml -f compose.staging.yml up -d --force-recreate --pull always
echo "✅ Services started - beginning health monitoring"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: MONITORING CONTAINER HEALTH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Give services a moment to initialize
sleep 3

MAX_WAIT=600  # 10 minutes max wait (allows for migrations, collectstatic, health checks, and service dependencies)
ELAPSED=0
CHECK_INTERVAL=5
PREVIOUS_UNHEALTHY=""

while [ $ELAPSED -lt $MAX_WAIT ]; do
  echo "-------------------------------------------------------------------"
  echo "Health Check (${ELAPSED}s / ${MAX_WAIT}s elapsed)"
  echo "-------------------------------------------------------------------"

  # Get detailed health status of all services with health checks
  HEALTH_STATUS=$(docker compose -f docker-compose.yml -f compose.staging.yml ps --format json | \
    jq -r 'select(.Health != "") | "\(.Service):\(.Health)"' 2>/dev/null || true)

  if [ -z "$HEALTH_STATUS" ]; then
    echo "⚠️ No health status available yet - services still initializing..."
  else
    echo "Container Health Status:"
    echo "$HEALTH_STATUS" | while IFS=: read -r service health; do
      case "$health" in
        "healthy")
          echo "  ✅ $service: healthy"
          ;;
        "starting")
          echo "  🔄 $service: starting (health check in progress)"
          ;;
        "unhealthy")
          echo "  ❌ $service: UNHEALTHY"
          ;;
        *)
          echo "  ⚠️  $service: $health"
          ;;
      esac
    done
  fi

  # Get list of unhealthy services
  UNHEALTHY=$(docker compose -f docker-compose.yml -f compose.staging.yml ps --format json | \
    jq -r 'select(.Health != "" and .Health != "healthy" and .Health != "starting") | .Service' 2>/dev/null || true)

  # Check if all services are healthy
  STARTING=$(docker compose -f docker-compose.yml -f compose.staging.yml ps --format json | \
    jq -r 'select(.Health == "starting") | .Service' 2>/dev/null || true)

  if [ -z "$UNHEALTHY" ] && [ -z "$STARTING" ]; then
    echo ""
    echo "==================================================================="
    echo "✅ ALL SERVICES ARE HEALTHY!"
    echo "==================================================================="
    echo ""
    docker compose -f docker-compose.yml -f compose.staging.yml ps
    echo ""

    # ============================================================
    # POST-DEPLOYMENT: Redis Cache Flush
    # ============================================================
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "STEP 6: Flushing Redis Cache"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Clearing all cached data to prevent serving stale application state..."
    echo ""

    # Flush Redis cache (requires password authentication)
    docker compose -f docker-compose.yml -f compose.staging.yml exec -T redis \
      redis-cli -a "${REDIS_PASSWORD}" FLUSHALL 2>&1 | grep -v "Warning: Using a password" || true

    echo "✅ Redis cache flushed successfully"
    echo ""

    # ============================================================
    # POST-DEPLOYMENT: Docker Image Cleanup
    # ============================================================
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "STEP 7: Cleaning Up Old Docker Images"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Removing unused images and build cache to free disk space..."
    echo "Retention: Keeping images from last 72 hours for rollback capability"
    echo ""

    # Show disk space before cleanup
    echo "Disk space before cleanup:"
    df -h / | tail -1 || true
    echo ""

    # Remove dangling and unused images older than 72 hours
    # This keeps recent images for quick rollback while freeing space
    PRUNED_IMAGES=$(docker image prune -af --filter "until=72h" 2>&1) || true
    echo "$PRUNED_IMAGES"
    echo ""

    # Remove unused build cache older than 72 hours
    PRUNED_CACHE=$(docker builder prune -af --filter "until=72h" 2>&1) || true
    echo "$PRUNED_CACHE"
    echo ""

    # Show disk space after cleanup
    echo "Disk space after cleanup:"
    df -h / | tail -1 || true
    echo ""

    # Extract and display space reclaimed
    RECLAIMED=$(echo "$PRUNED_IMAGES$PRUNED_CACHE" | grep -o "Total reclaimed space: [^[:space:]]*" | tail -1 || echo "Total reclaimed space: 0B")
    echo "✅ Cleanup complete: $RECLAIMED"
    echo ""

    echo "==================================================================="
    echo "✅ DEPLOYMENT COMPLETE - ALL POST-DEPLOYMENT TASKS FINISHED"
    echo "==================================================================="
    exit 0
  fi

  # Show logs for newly unhealthy services
  if [ -n "$UNHEALTHY" ]; then
    echo ""
    echo "📋 Displaying logs for unhealthy containers:"
    echo ""

    for service in $UNHEALTHY; do
      # Only show logs if this is a newly unhealthy service
      if ! echo "$PREVIOUS_UNHEALTHY" | grep -q "$service"; then
        echo ">>> NEW UNHEALTHY SERVICE DETECTED: $service <<<"
      fi

      echo "--- $service logs (last 30 lines) ---"
      docker compose -f docker-compose.yml -f compose.staging.yml logs --tail=30 "$service" 2>&1 || echo "Failed to retrieve logs for $service"
      echo ""

      # Show detailed container inspection for health check failures
      echo "--- $service health check details ---"
      CONTAINER_NAME=$(docker compose -f docker-compose.yml -f compose.staging.yml ps -q "$service" 2>/dev/null)
      if [ -n "$CONTAINER_NAME" ]; then
        docker inspect "$CONTAINER_NAME" | jq -r '.[0].State.Health | "Health Status: " + .Status + "\nFailing Streak: " + (.FailingStreak|tostring) + "\nLast Check Output: " + (if .Log then .Log[0].Output else "No logs" end)' 2>&1 || echo "Failed to inspect container $service"
      fi
      echo ""
    done

    PREVIOUS_UNHEALTHY="$UNHEALTHY"
  fi

  # Show which services we're still waiting for
  if [ -n "$STARTING" ]; then
    echo "⏳ Services still starting: $STARTING"
  fi
  if [ -n "$UNHEALTHY" ]; then
    echo "❌ Unhealthy services: $UNHEALTHY"
  fi

  sleep $CHECK_INTERVAL
  ELAPSED=$(($ELAPSED + $CHECK_INTERVAL))
  echo ""
done

echo "==================================================================="
echo "❌ TIMEOUT - SERVICES FAILED TO BECOME HEALTHY"
echo "==================================================================="
echo ""
echo "Final service status:"
docker compose -f docker-compose.yml -f compose.staging.yml ps
echo ""

echo "==================================================================="
echo "FINAL LOG DUMP - ALL SERVICES"
echo "==================================================================="
echo ""

for service in proxy backend frontend db redis; do
  echo "--- $service logs (last 200 lines) ---"
  docker compose -f docker-compose.yml -f compose.staging.yml logs --tail=200 "$service" 2>&1 || echo "Service $service not found"
  echo ""
done

exit 1
