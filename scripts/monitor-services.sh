#!/bin/bash
# =============================================================================
# Service Health Monitoring Script (Story 12.9)
# =============================================================================
# Continuously monitors the health of all services and provides real-time
# status updates. This script helps operators monitor service health and
# detect issues quickly.
#
# Features:
#   - Real-time health monitoring for all services
#   - Automatic restart attempt tracking
#   - Failure notifications and alerts
#   - Detailed health status with timestamps
#   - Service uptime tracking
#   - Historical health check results
#
# Usage:
#   ./scripts/monitor-services.sh                    # Monitor continuously
#   ./scripts/monitor-services.sh --once             # Single check
#   ./scripts/monitor-services.sh --watch            # Watch mode (refresh every 5s)
#   ./scripts/monitor-services.sh --alert            # Alert on failures
#   ./scripts/monitor-services.sh --json             # JSON output
#   ./scripts/monitor-services.sh --help             # Show help
#
# Exit codes:
#   0 - All services healthy
#   1 - One or more services unhealthy
#   2 - Services not running
# =============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/logs/health-monitoring.log"
STATE_FILE="$PROJECT_ROOT/logs/health-state.json"
ALERT_LOG="$PROJECT_ROOT/logs/health-alerts.log"

# Default settings
MODE="continuous"
WATCH_INTERVAL=5
ALERT_ON_FAILURE=false
JSON_OUTPUT=false
NOTIFICATION_EMAIL=""
MAX_RESTART_ATTEMPTS=3
FAILURE_THRESHOLD=3

# Service list
SERVICES=("db" "redis" "backend" "frontend" "proxy")

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --once)
            MODE="once"
            shift
            ;;
        --watch)
            MODE="watch"
            shift
            ;;
        --alert)
            ALERT_ON_FAILURE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --interval)
            WATCH_INTERVAL="$2"
            shift 2
            ;;
        --email)
            NOTIFICATION_EMAIL="$2"
            shift 2
            ;;
        -h|--help)
            cat << EOF
Service Health Monitoring Script

Usage: $0 [OPTIONS]

Modes:
  --once              Run a single health check and exit
  --watch             Continuous monitoring with screen refresh (default: 5s)
  --alert             Enable failure alerts and notifications

Options:
  --interval SECONDS  Set watch interval in seconds (default: 5)
  --email EMAIL       Send notifications to this email address
  --json              Output in JSON format
  -h, --help          Show this help message

Examples:
  $0                                  # Continuous monitoring
  $0 --once                           # Single check
  $0 --watch --interval 10            # Watch mode, refresh every 10s
  $0 --alert --email admin@example.com # Alert mode with email

Exit codes:
  0 - All services healthy
  1 - One or more services unhealthy
  2 - Services not running
EOF
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# =============================================================================
# Helper Functions
# =============================================================================

# Setup logging
setup_logging() {
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$(dirname "$STATE_FILE")"
    mkdir -p "$(dirname "$ALERT_LOG")"
}

# Log message to file
log_to_file() {
    local level=$1
    local message=$2
    local timestamp=$(date -Iseconds)
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Get container health status
get_container_health() {
    local service=$1
    local container_name="app-$service"

    if ! docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        echo "not_running"
        return
    fi

    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "no_healthcheck")
    echo "$health"
}

# Get last health check timestamp
get_last_health_check() {
    local service=$1
    local container_name="app-$service"

    docker inspect --format='{{range .State.Health.Log}}{{.End}}{{end}}' "$container_name" 2>/dev/null | tail -n1 || echo "unknown"
}

# Get health check output
get_health_check_output() {
    local service=$1
    local container_name="app-$service"

    docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' "$container_name" 2>/dev/null | tail -n1 || echo "No output"
}

# Get container restart count
get_restart_count() {
    local service=$1
    local container_name="app-$service"

    docker inspect --format='{{.RestartCount}}' "$container_name" 2>/dev/null || echo "0"
}

# Get container uptime
get_container_uptime() {
    local service=$1
    local container_name="app-$service"

    local started_at=$(docker inspect --format='{{.State.StartedAt}}' "$container_name" 2>/dev/null || echo "")
    if [ -z "$started_at" ] || [ "$started_at" = "0001-01-01T00:00:00Z" ]; then
        echo "not running"
        return
    fi

    local started_epoch=$(date -d "$started_at" +%s 2>/dev/null || echo "0")
    local current_epoch=$(date +%s)
    local uptime_seconds=$((current_epoch - started_epoch))

    local days=$((uptime_seconds / 86400))
    local hours=$(((uptime_seconds % 86400) / 3600))
    local minutes=$(((uptime_seconds % 3600) / 60))

    if [ $days -gt 0 ]; then
        echo "${days}d ${hours}h ${minutes}m"
    elif [ $hours -gt 0 ]; then
        echo "${hours}h ${minutes}m"
    else
        echo "${minutes}m"
    fi
}

# Check if service health has changed
check_health_change() {
    local service=$1
    local current_health=$2

    if [ ! -f "$STATE_FILE" ]; then
        return 0
    fi

    local previous_health
    if ! command -v jq &> /dev/null; then
        # Simple CSV format: service,health,timestamp,restart_count
        previous_health=$(grep "^$service," "$STATE_FILE" 2>/dev/null | cut -d',' -f2 || echo "unknown")
    else
        previous_health=$(jq -r ".\"$service\".health // \"unknown\"" "$STATE_FILE" 2>/dev/null || echo "unknown")
    fi

    if [ "$current_health" != "$previous_health" ]; then
        return 0
    else
        return 1
    fi
}

# Update service state
update_service_state() {
    local service=$1
    local health=$2
    local timestamp=$(date -Iseconds)
    local restart_count=$(get_restart_count "$service")

    # If jq is not available, use simple state tracking
    if ! command -v jq &> /dev/null; then
        if [ ! -f "$STATE_FILE" ]; then
            echo "$service,$health,$timestamp,$restart_count" > "$STATE_FILE"
        else
            # Update or append state (simple CSV format)
            if grep -q "^$service," "$STATE_FILE"; then
                sed -i "s/^$service,.*/$service,$health,$timestamp,$restart_count/" "$STATE_FILE"
            else
                echo "$service,$health,$timestamp,$restart_count" >> "$STATE_FILE"
            fi
        fi
        return
    fi

    local temp_file=$(mktemp)

    if [ ! -f "$STATE_FILE" ] || [ ! -s "$STATE_FILE" ]; then
        echo "{}" > "$STATE_FILE"
    fi

    jq --arg service "$service" \
       --arg health "$health" \
       --arg timestamp "$timestamp" \
       --arg restarts "$restart_count" \
       '.[$service] = {
           health: $health,
           timestamp: $timestamp,
           restart_count: ($restarts | tonumber),
           consecutive_failures: (
               if $health == "unhealthy" or $health == "not_running" then
                   (.[$service].consecutive_failures // 0) + 1
               else
                   0
               end
           )
       }' "$STATE_FILE" > "$temp_file" && mv "$temp_file" "$STATE_FILE"
}

# Send alert notification
send_alert() {
    local service=$1
    local health=$2
    local message=$3
    local timestamp=$(date -Iseconds)

    local alert_message="[$timestamp] ALERT: Service '$service' is $health - $message"

    # Log alert
    echo "$alert_message" >> "$ALERT_LOG"
    log_to_file "ALERT" "$alert_message"

    # Console output
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  ALERT: Service Health Issue${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}Service:${NC}   $service"
    echo -e "${WHITE}Status:${NC}    ${RED}$health${NC}"
    echo -e "${WHITE}Time:${NC}      $timestamp"
    echo -e "${WHITE}Message:${NC}   $message"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Send email notification if configured
    if [ -n "$NOTIFICATION_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$alert_message" | mail -s "Service Health Alert: $service is $health" "$NOTIFICATION_EMAIL"
    fi
}

# Check for persistent failures
check_persistent_failure() {
    local service=$1
    local consecutive_failures=0

    if ! command -v jq &> /dev/null; then
        # Skip persistent failure check if jq not available (simplified mode)
        return 1
    fi

    consecutive_failures=$(jq -r ".\"$service\".consecutive_failures // 0" "$STATE_FILE" 2>/dev/null || echo "0")

    if [ "$consecutive_failures" -ge "$FAILURE_THRESHOLD" ]; then
        local restart_count=$(get_restart_count "$service")

        if [ "$restart_count" -ge "$MAX_RESTART_ATTEMPTS" ]; then
            send_alert "$service" "PERSISTENT_FAILURE" \
                "Service has failed $consecutive_failures consecutive health checks and reached maximum restart attempts ($restart_count/$MAX_RESTART_ATTEMPTS). Manual intervention required."
            return 0
        fi
    fi

    return 1
}

# Print service status (terminal output)
print_service_status() {
    local service=$1
    local health=$2
    local uptime=$3
    local restart_count=$4
    local last_check=$5

    local health_icon="❓"
    local health_color=$WHITE

    case $health in
        healthy)
            health_icon="✅"
            health_color=$GREEN
            ;;
        unhealthy)
            health_icon="❌"
            health_color=$RED
            ;;
        starting)
            health_icon="⏳"
            health_color=$YELLOW
            ;;
        not_running)
            health_icon="⭕"
            health_color=$RED
            ;;
        no_healthcheck)
            health_icon="⚠️"
            health_color=$YELLOW
            ;;
    esac

    printf "${health_icon} ${CYAN}%-12s${NC} ${health_color}%-15s${NC} Uptime: %-12s Restarts: %-3s Last: %s\n" \
        "$service" "$health" "$uptime" "$restart_count" "$last_check"
}

# Print JSON output
print_json_output() {
    if ! command -v jq &> /dev/null; then
        echo "{\"error\": \"jq is required for JSON output. Install jq: apt-get install jq or brew install jq\"}"
        return 1
    fi

    local services_json="["
    local first=true

    for service in "${SERVICES[@]}"; do
        local health=$(get_container_health "$service")
        local uptime=$(get_container_uptime "$service")
        local restart_count=$(get_restart_count "$service")
        local last_check=$(get_last_health_check "$service")
        local health_output=$(get_health_check_output "$service")
        local consecutive_failures=$(jq -r ".\"$service\".consecutive_failures // 0" "$STATE_FILE" 2>/dev/null || echo "0")

        if [ "$first" = true ]; then
            first=false
        else
            services_json+=","
        fi

        services_json+=$(jq -n \
            --arg service "$service" \
            --arg health "$health" \
            --arg uptime "$uptime" \
            --arg restart_count "$restart_count" \
            --arg last_check "$last_check" \
            --arg health_output "$health_output" \
            --arg consecutive_failures "$consecutive_failures" \
            '{
                service: $service,
                health: $health,
                uptime: $uptime,
                restart_count: ($restart_count | tonumber),
                last_check: $last_check,
                health_output: $health_output,
                consecutive_failures: ($consecutive_failures | tonumber)
            }')
    done

    services_json+="]"

    jq -n \
        --arg timestamp "$(date -Iseconds)" \
        --argjson services "$services_json" \
        '{
            timestamp: $timestamp,
            services: $services
        }'
}

# Monitor services once
monitor_once() {
    setup_logging

    if [ "$JSON_OUTPUT" = true ]; then
        print_json_output
        return
    fi

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Service Health Monitor - $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    local all_healthy=true
    local any_running=false

    for service in "${SERVICES[@]}"; do
        local health=$(get_container_health "$service")
        local uptime=$(get_container_uptime "$service")
        local restart_count=$(get_restart_count "$service")
        local last_check=$(get_last_health_check "$service")

        # Format last check time
        if [ "$last_check" != "unknown" ] && [ -n "$last_check" ]; then
            last_check=$(date -d "$last_check" '+%H:%M:%S' 2>/dev/null || echo "unknown")
        fi

        print_service_status "$service" "$health" "$uptime" "$restart_count" "$last_check"

        # Update state
        update_service_state "$service" "$health"

        # Check for health changes and alerts
        if [ "$ALERT_ON_FAILURE" = true ]; then
            if [ "$health" = "unhealthy" ] || [ "$health" = "not_running" ]; then
                if check_health_change "$service" "$health"; then
                    local health_output=$(get_health_check_output "$service")
                    send_alert "$service" "$health" "Health check output: $health_output"
                fi

                check_persistent_failure "$service"
                all_healthy=false
            fi
        fi

        if [ "$health" != "not_running" ]; then
            any_running=true
        fi

        if [ "$health" != "healthy" ]; then
            all_healthy=false
        fi
    done

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Overall status
    if [ "$all_healthy" = true ]; then
        echo -e "${GREEN}✓ All services are healthy${NC}"
        echo ""
        return 0
    elif [ "$any_running" = false ]; then
        echo -e "${RED}✗ No services are running${NC}"
        echo ""
        return 2
    else
        echo -e "${YELLOW}⚠ Some services are not healthy${NC}"
        echo ""
        return 1
    fi
}

# Watch mode (continuous monitoring with refresh)
monitor_watch() {
    while true; do
        clear
        monitor_once

        echo -e "${CYAN}Refreshing in ${WATCH_INTERVAL}s... (Press Ctrl+C to stop)${NC}"
        sleep "$WATCH_INTERVAL"
    done
}

# Continuous monitoring mode
monitor_continuous() {
    setup_logging

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Service Health Monitor - Continuous Mode${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${CYAN}Monitoring services every ${WATCH_INTERVAL}s...${NC}"
    echo -e "${CYAN}Press Ctrl+C to stop${NC}"
    echo ""

    log_to_file "INFO" "Starting continuous monitoring mode (interval: ${WATCH_INTERVAL}s)"

    while true; do
        for service in "${SERVICES[@]}"; do
            local health=$(get_container_health "$service")
            local previous_health="unknown"

            if command -v jq &> /dev/null; then
                previous_health=$(jq -r ".\"$service\".health // \"unknown\"" "$STATE_FILE" 2>/dev/null || echo "unknown")
            elif [ -f "$STATE_FILE" ]; then
                previous_health=$(grep "^$service," "$STATE_FILE" 2>/dev/null | cut -d',' -f2 || echo "unknown")
            fi

            # Update state
            update_service_state "$service" "$health"

            # Check for health changes
            if [ "$health" != "$previous_health" ]; then
                local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
                echo -e "${YELLOW}[$timestamp]${NC} Service ${CYAN}$service${NC} health changed: $previous_health → $health"
                log_to_file "INFO" "Service $service health changed: $previous_health → $health"

                if [ "$ALERT_ON_FAILURE" = true ]; then
                    if [ "$health" = "unhealthy" ] || [ "$health" = "not_running" ]; then
                        local health_output=$(get_health_check_output "$service")
                        send_alert "$service" "$health" "Health check output: $health_output"
                    fi
                fi
            fi

            # Check for persistent failures
            if [ "$ALERT_ON_FAILURE" = true ]; then
                check_persistent_failure "$service"
            fi
        done

        sleep "$WATCH_INTERVAL"
    done
}

# =============================================================================
# Main Execution
# =============================================================================

# Trap Ctrl+C
trap 'echo -e "\n${YELLOW}Monitoring stopped${NC}"; exit 0' INT TERM

case $MODE in
    once)
        monitor_once
        exit $?
        ;;
    watch)
        monitor_watch
        ;;
    continuous)
        monitor_continuous
        ;;
esac
