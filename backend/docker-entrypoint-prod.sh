#!/bin/bash
set -e

# Function to log with timestamp and duration
log_step() {
    local step_name="$1"
    local step_start=$(date +%s)
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $step_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

log_complete() {
    local step_name="$1"
    local step_start="$2"
    local step_end=$(date +%s)
    local duration=$((step_end - step_start))
    echo "✅ $step_name completed in ${duration}s"
    echo ""
}

CONTAINER_START=$(date +%s)

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║          Backend Production Container - Initialization           ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Validate configuration
STEP_START=$(date +%s)
log_step "STEP 1/5: Validating production configuration"
python manage.py check_config --quiet || exit 1
log_complete "Configuration validation" "$STEP_START"

# Step 2: Wait for database
STEP_START=$(date +%s)
log_step "STEP 2/5: Waiting for PostgreSQL"
python manage.py check_database --wait 60
log_complete "Database connectivity" "$STEP_START"

# Step 3: Run deployment checks
STEP_START=$(date +%s)
log_step "STEP 3/5: Running deployment checks"
python manage.py check --deploy --fail-level WARNING
log_complete "Deployment checks" "$STEP_START"

# Step 4: Apply migrations
STEP_START=$(date +%s)
log_step "STEP 4/5: Applying database migrations"
python manage.py migrate --noinput
log_complete "Database migrations" "$STEP_START"

# Step 5: Collect static files
STEP_START=$(date +%s)
log_step "STEP 5/5: Collecting static files"
python manage.py collectstatic --noinput --clear
log_complete "Static file collection" "$STEP_START"

CONTAINER_END=$(date +%s)
TOTAL_DURATION=$((CONTAINER_END - CONTAINER_START))

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║            Production Initialization Complete                     ║"
echo "╠═══════════════════════════════════════════════════════════════════╣"
echo "║  Total startup time: ${TOTAL_DURATION}s                                     "
echo "║  Health checks will begin after start_period (180s)               ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Execute the command
exec "$@"
