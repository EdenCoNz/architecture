#!/bin/bash

#
# Container Build Cache Effectiveness Test
#
# This script tests the effectiveness of Docker build layer caching by:
# 1. Building a container from scratch (cold build)
# 2. Building the same container again (warm build)
# 3. Making a minor code change and rebuilding (incremental build)
# 4. Comparing build times to verify cache effectiveness
#
# Usage: ./test-cache-effectiveness.sh [development|production]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default target
TARGET=${1:-development}
IMAGE_NAME="frontend-cache-test"

# Validate target
if [[ "$TARGET" != "development" && "$TARGET" != "production" ]]; then
    echo -e "${RED}Error: Target must be 'development' or 'production'${NC}"
    echo "Usage: $0 [development|production]"
    exit 1
fi

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Container Build Cache Effectiveness Test${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${YELLOW}Target:${NC} $TARGET"
echo ""

# Function to build container and measure time
build_container() {
    local build_type=$1
    local cache_option=$2

    echo -e "${YELLOW}Building: $build_type${NC}"

    local start_time=$(date +%s)

    if [[ "$TARGET" == "production" ]]; then
        docker buildx build \
            --target production \
            --tag "$IMAGE_NAME:$TARGET-test" \
            --build-arg VITE_API_URL=https://api.example.com \
            --build-arg VITE_APP_NAME="Frontend Application" \
            --build-arg VITE_APP_VERSION=1.0.0 \
            $cache_option \
            -f Dockerfile \
            . > /dev/null 2>&1
    else
        docker buildx build \
            --target development \
            --tag "$IMAGE_NAME:$TARGET-test" \
            $cache_option \
            -f Dockerfile \
            . > /dev/null 2>&1
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo -e "${GREEN}✓ Build completed in ${duration}s${NC}"
    echo "$duration"
}

# Function to clean build caches
clean_caches() {
    echo -e "${YELLOW}Cleaning build caches...${NC}"
    docker builder prune -af > /dev/null 2>&1
    echo -e "${GREEN}✓ Caches cleaned${NC}"
}

# Change to frontend directory
cd "$(dirname "$0")"

echo -e "${BLUE}Test 1: Cold Build (No Cache)${NC}"
echo "----------------------------------------"
clean_caches
COLD_BUILD_TIME=$(build_container "Cold build" "--no-cache")
echo ""

echo -e "${BLUE}Test 2: Warm Build (Full Cache)${NC}"
echo "----------------------------------------"
WARM_BUILD_TIME=$(build_container "Warm build" "")
echo ""

echo -e "${BLUE}Test 3: Incremental Build (Code Change)${NC}"
echo "----------------------------------------"
# Create a temporary file to simulate code change
TEMP_FILE="src/.cache-test-temp-$(date +%s).ts"
echo "// Temporary file for cache testing" > "$TEMP_FILE"

INCREMENTAL_BUILD_TIME=$(build_container "Incremental build" "")

# Clean up temp file
rm -f "$TEMP_FILE"
echo ""

# Calculate cache effectiveness
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Results Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Display results table
printf "%-25s %10s\n" "Build Type" "Time (s)"
printf "%-25s %10s\n" "-------------------------" "----------"
printf "%-25s %10s\n" "Cold Build (no cache)" "$COLD_BUILD_TIME"
printf "%-25s %10s\n" "Warm Build (full cache)" "$WARM_BUILD_TIME"
printf "%-25s %10s\n" "Incremental Build" "$INCREMENTAL_BUILD_TIME"
echo ""

# Calculate improvements
WARM_IMPROVEMENT=$(awk "BEGIN {printf \"%.1f\", (($COLD_BUILD_TIME - $WARM_BUILD_TIME) / $COLD_BUILD_TIME) * 100}")
INCREMENTAL_IMPROVEMENT=$(awk "BEGIN {printf \"%.1f\", (($COLD_BUILD_TIME - $INCREMENTAL_BUILD_TIME) / $COLD_BUILD_TIME) * 100}")

echo -e "${BLUE}Cache Effectiveness:${NC}"
echo ""
printf "%-35s %10s\n" "Warm build improvement:" "${WARM_IMPROVEMENT}%"
printf "%-35s %10s\n" "Incremental build improvement:" "${INCREMENTAL_IMPROVEMENT}%"
echo ""

# Determine cache effectiveness level
if (( $(echo "$WARM_IMPROVEMENT >= 70" | bc -l) )); then
    echo -e "${GREEN}✓ EXCELLENT${NC} - Cache is highly effective (≥70% improvement)"
elif (( $(echo "$WARM_IMPROVEMENT >= 50" | bc -l) )); then
    echo -e "${YELLOW}✓ GOOD${NC} - Cache is working well (50-70% improvement)"
elif (( $(echo "$WARM_IMPROVEMENT >= 30" | bc -l) )); then
    echo -e "${YELLOW}⚠ MODERATE${NC} - Cache is providing some benefit (30-50% improvement)"
else
    echo -e "${RED}✗ POOR${NC} - Cache is not effective (<30% improvement)"
    echo -e "${YELLOW}Consider reviewing Dockerfile layer ordering and .dockerignore${NC}"
fi

echo ""
echo -e "${BLUE}Acceptance Criteria Verification:${NC}"
echo ""

# AC 1: Unchanged dependencies use cached layers
if (( $(echo "$WARM_IMPROVEMENT >= 50" | bc -l) )); then
    echo -e "${GREEN}✓ AC1: Cached layers reused for unchanged dependencies${NC}"
else
    echo -e "${RED}✗ AC1: Cache not effectively reusing layers${NC}"
fi

# AC 2: Only affected layers rebuild
if (( $(echo "$INCREMENTAL_IMPROVEMENT >= 40" | bc -l) )); then
    echo -e "${GREEN}✓ AC2: Only affected layers rebuild on change${NC}"
else
    echo -e "${RED}✗ AC2: Too many layers rebuilding on minor changes${NC}"
fi

# AC 3: Cached builds significantly faster
if (( $(echo "$WARM_BUILD_TIME <= $COLD_BUILD_TIME / 2" | bc -l) )); then
    echo -e "${GREEN}✓ AC3: Cached builds significantly faster than cold builds${NC}"
else
    echo -e "${RED}✗ AC3: Cached builds not significantly faster${NC}"
fi

echo ""
echo -e "${BLUE}Notes:${NC}"
echo "- Cold build time represents worst-case scenario (no cache)"
echo "- Warm build time represents best-case scenario (full cache hit)"
echo "- Incremental build time represents typical development workflow"
echo "- In CI/CD, builds benefit from GitHub Actions cache across runs"
echo ""

# Clean up
echo -e "${YELLOW}Cleaning up test artifacts...${NC}"
docker rmi "$IMAGE_NAME:$TARGET-test" > /dev/null 2>&1 || true
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Test Complete${NC}"
echo -e "${BLUE}================================================${NC}"
