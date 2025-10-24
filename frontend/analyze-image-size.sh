#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Container Image Size Optimization Validation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# This script performs comprehensive image size analysis including:
#   - Total image size reporting
#   - Per-layer size breakdown
#   - Size threshold validation with warnings
#   - Cross-build size comparison
#   - Multi-stage build validation
#   - Optimization recommendations
#
# Usage:
#   ./analyze-image-size.sh <image-name> [previous-size-file] [size-threshold-mb]
#
# Arguments:
#   image-name          Docker image name with tag (e.g., frontend:prod-abc123)
#   previous-size-file  Optional: Path to file containing previous build size
#   size-threshold-mb   Optional: Warning threshold in MB (default: 100 for prod, 500 for dev)
#
# Examples:
#   ./analyze-image-size.sh frontend:prod-abc123
#   ./analyze-image-size.sh frontend:prod-abc123 /tmp/previous-size.txt 50
#   ./analyze-image-size.sh frontend:dev-abc123 /tmp/dev-size.txt 500
#
# Exit codes:
#   0 - Success, image size is optimal
#   1 - Error: Missing arguments or image not found
#   2 - Warning: Image exceeds size threshold (non-fatal)
#
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Size thresholds (in MB)
DEFAULT_PROD_THRESHOLD=100  # Production images should be under 100MB
DEFAULT_DEV_THRESHOLD=500   # Development images can be larger
SIZE_INCREASE_WARNING=10    # Warn if size increases by more than 10%

# ============================================================================
# Functions
# ============================================================================

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Convert size string to MB (handles KB, MB, GB)
convert_to_mb() {
    local size=$1
    local value=$(echo "$size" | grep -oE '[0-9.]+')
    local unit=$(echo "$size" | grep -oE '[A-Za-z]+')

    case "$unit" in
        kB|KB)
            echo "$value / 1024" | bc -l
            ;;
        MB)
            echo "$value"
            ;;
        GB)
            echo "$value * 1024" | bc -l
            ;;
        *)
            # Assume bytes
            echo "$value / 1024 / 1024" | bc -l
            ;;
    esac
}

# Format MB to human-readable
format_size() {
    local size_mb=$1

    if (( $(echo "$size_mb < 1" | bc -l) )); then
        # Less than 1 MB, show in KB
        local size_kb=$(echo "$size_mb * 1024" | bc -l)
        printf "%.2f kB" "$size_kb"
    elif (( $(echo "$size_mb < 1024" | bc -l) )); then
        # Less than 1 GB, show in MB
        printf "%.2f MB" "$size_mb"
    else
        # Show in GB
        local size_gb=$(echo "$size_mb / 1024" | bc -l)
        printf "%.2f GB" "$size_gb"
    fi
}

# ============================================================================
# Argument Parsing
# ============================================================================

if [ $# -lt 1 ]; then
    print_error "Missing required argument: image-name"
    echo ""
    echo "Usage: $0 <image-name> [previous-size-file] [size-threshold-mb]"
    echo ""
    echo "Arguments:"
    echo "  image-name          Docker image name with tag (e.g., frontend:prod-abc123)"
    echo "  previous-size-file  Optional: Path to file containing previous build size"
    echo "  size-threshold-mb   Optional: Warning threshold in MB (default: 100 for prod, 500 for dev)"
    echo ""
    echo "Examples:"
    echo "  $0 frontend:prod-abc123"
    echo "  $0 frontend:prod-abc123 /tmp/previous-size.txt 50"
    echo "  $0 frontend:dev-abc123 /tmp/dev-size.txt 500"
    exit 1
fi

IMAGE_NAME="$1"
PREVIOUS_SIZE_FILE="${2:-}"
SIZE_THRESHOLD_MB="${3:-}"

# Determine if this is a dev or prod image
if [[ "$IMAGE_NAME" == *":dev-"* ]]; then
    IMAGE_TYPE="development"
    DEFAULT_THRESHOLD=$DEFAULT_DEV_THRESHOLD
else
    IMAGE_TYPE="production"
    DEFAULT_THRESHOLD=$DEFAULT_PROD_THRESHOLD
fi

# Use provided threshold or default
if [ -z "$SIZE_THRESHOLD_MB" ]; then
    SIZE_THRESHOLD_MB=$DEFAULT_THRESHOLD
fi

# ============================================================================
# Verify Image Exists
# ============================================================================

print_header "Container Image Size Analysis: $IMAGE_NAME"
echo ""

if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    print_error "Image '$IMAGE_NAME' not found"
    echo ""
    print_info "Available images:"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    exit 1
fi

print_success "Image found: $IMAGE_NAME"
print_info "Image type: $IMAGE_TYPE"
print_info "Size threshold: ${SIZE_THRESHOLD_MB} MB"
echo ""

# ============================================================================
# Extract Image Size and Metadata
# ============================================================================

print_header "Image Metadata"
echo ""

# Get image size
IMAGE_SIZE_RAW=$(docker images "$IMAGE_NAME" --format "{{.Size}}")
IMAGE_SIZE_MB=$(convert_to_mb "$IMAGE_SIZE_RAW")
IMAGE_SIZE_FORMATTED=$(format_size "$IMAGE_SIZE_MB")

# Get image metadata
IMAGE_ID=$(docker inspect "$IMAGE_NAME" --format='{{.Id}}' | cut -c8-19)
IMAGE_CREATED=$(docker inspect "$IMAGE_NAME" --format='{{.Created}}')
IMAGE_ARCH=$(docker inspect "$IMAGE_NAME" --format='{{.Architecture}}')
IMAGE_OS=$(docker inspect "$IMAGE_NAME" --format='{{.Os}}')

echo "Image ID:       $IMAGE_ID"
echo "Created:        $IMAGE_CREATED"
echo "Architecture:   $IMAGE_ARCH"
echo "OS:             $IMAGE_OS"
echo "Total Size:     $IMAGE_SIZE_FORMATTED ($IMAGE_SIZE_MB MB)"
echo ""

# ============================================================================
# Layer Breakdown Analysis
# ============================================================================

print_header "Layer Size Breakdown"
echo ""

# Get layer information with sizes
# docker history shows each layer with its size
LAYER_DATA=$(docker history "$IMAGE_NAME" --format "{{.CreatedBy}}\t{{.Size}}" --no-trunc)

# Create temporary file for layer analysis
TEMP_LAYER_FILE=$(mktemp)
echo "$LAYER_DATA" > "$TEMP_LAYER_FILE"

# Count total layers
TOTAL_LAYERS=$(wc -l < "$TEMP_LAYER_FILE")
print_info "Total layers: $TOTAL_LAYERS"
echo ""

# Parse layers and find largest ones
echo "Top 10 Largest Layers:"
echo "─────────────────────────────────────────────────────────────────────"
printf "%-60s %15s\n" "Layer Command" "Size"
echo "─────────────────────────────────────────────────────────────────────"

# Process each layer, convert to MB, and sort by size
layer_count=0
while IFS=$'\t' read -r command size; do
    if [ "$size" != "0B" ] && [ -n "$size" ]; then
        size_mb=$(convert_to_mb "$size")
        # Truncate command to 60 chars
        truncated_command=$(echo "$command" | sed 's/^\/bin\/sh -c #(nop) //' | cut -c1-60)
        printf "%-60s %15s\n" "$truncated_command" "$(format_size "$size_mb")"

        # Store for sorting
        echo "$size_mb|$truncated_command" >> "${TEMP_LAYER_FILE}.sorted"
    fi
done < "$TEMP_LAYER_FILE"

# Show top 10 largest layers
if [ -f "${TEMP_LAYER_FILE}.sorted" ]; then
    echo ""
    echo "Largest Contributors (Sorted by Size):"
    echo "─────────────────────────────────────────────────────────────────────"
    printf "%-60s %15s\n" "Layer Command" "Size"
    echo "─────────────────────────────────────────────────────────────────────"

    sort -t'|' -k1 -rn "${TEMP_LAYER_FILE}.sorted" | head -10 | while IFS='|' read -r size_mb command; do
        printf "%-60s %15s\n" "$command" "$(format_size "$size_mb")"
    done
fi

rm -f "$TEMP_LAYER_FILE" "${TEMP_LAYER_FILE}.sorted"
echo ""

# ============================================================================
# Multi-Stage Build Validation
# ============================================================================

print_header "Multi-Stage Build Validation"
echo ""

# Check if this appears to be from a multi-stage build
# Production images should use nginx/minimal base
# Development images should use node base

if [[ "$IMAGE_TYPE" == "production" ]]; then
    # Check if nginx is present (production builds should use nginx)
    if docker run --rm --entrypoint="" "$IMAGE_NAME" sh -c "which nginx" &>/dev/null; then
        print_success "Production image uses nginx server"
        NGINX_VERSION=$(docker run --rm --entrypoint="" "$IMAGE_NAME" nginx -v 2>&1 | grep -oE 'nginx/[0-9.]+')
        print_info "Nginx version: $NGINX_VERSION"
    else
        print_warning "Production image does not appear to use nginx"
    fi

    # Check if node is NOT present (should not be in final prod image)
    if docker run --rm --entrypoint="" "$IMAGE_NAME" sh -c "which node" &>/dev/null; then
        print_warning "Node.js found in production image - multi-stage build may not be working correctly"
        print_info "Production images should only contain static assets and nginx"
    else
        print_success "No Node.js in final production image (correct multi-stage build)"
    fi
else
    # Development image should have node
    if docker run --rm --entrypoint="" "$IMAGE_NAME" sh -c "which node" &>/dev/null; then
        print_success "Development image contains Node.js"
        NODE_VERSION=$(docker run --rm --entrypoint="" "$IMAGE_NAME" node --version)
        print_info "Node.js version: $NODE_VERSION"
    else
        print_warning "Node.js not found in development image"
    fi
fi

echo ""

# ============================================================================
# Size Threshold Validation
# ============================================================================

print_header "Size Threshold Validation"
echo ""

THRESHOLD_EXCEEDED=false

echo "Image Size:       $IMAGE_SIZE_FORMATTED ($IMAGE_SIZE_MB MB)"
echo "Size Threshold:   ${SIZE_THRESHOLD_MB} MB"
echo ""

# Compare against threshold
if (( $(echo "$IMAGE_SIZE_MB > $SIZE_THRESHOLD_MB" | bc -l) )); then
    THRESHOLD_EXCEEDED=true
    SIZE_OVER=$(echo "$IMAGE_SIZE_MB - $SIZE_THRESHOLD_MB" | bc -l)
    SIZE_OVER_FORMATTED=$(format_size "$SIZE_OVER")
    PERCENT_OVER=$(echo "scale=2; ($IMAGE_SIZE_MB / $SIZE_THRESHOLD_MB - 1) * 100" | bc -l)

    print_warning "Image exceeds size threshold by $SIZE_OVER_FORMATTED (${PERCENT_OVER}%)"
    echo ""
    print_info "Recommendations:"
    echo "  - Review layer breakdown above to identify largest contributors"
    echo "  - Consider using smaller base images (Alpine, distroless)"
    echo "  - Remove unnecessary dependencies and build artifacts"
    echo "  - Use .dockerignore to exclude unnecessary files"
    echo "  - Enable multi-stage builds to separate build and runtime dependencies"
else
    SIZE_UNDER=$(echo "$SIZE_THRESHOLD_MB - $IMAGE_SIZE_MB" | bc -l)
    SIZE_UNDER_FORMATTED=$(format_size "$SIZE_UNDER")
    PERCENT_USAGE=$(echo "scale=2; ($IMAGE_SIZE_MB / $SIZE_THRESHOLD_MB) * 100" | bc -l)

    print_success "Image size is within threshold"
    print_info "Threshold usage: ${PERCENT_USAGE}% ($SIZE_UNDER_FORMATTED under threshold)"
fi

echo ""

# ============================================================================
# Cross-Build Size Comparison
# ============================================================================

if [ -n "$PREVIOUS_SIZE_FILE" ] && [ -f "$PREVIOUS_SIZE_FILE" ]; then
    print_header "Cross-Build Size Comparison"
    echo ""

    PREVIOUS_SIZE_MB=$(cat "$PREVIOUS_SIZE_FILE")
    PREVIOUS_SIZE_FORMATTED=$(format_size "$PREVIOUS_SIZE_MB")

    SIZE_DIFF=$(echo "$IMAGE_SIZE_MB - $PREVIOUS_SIZE_MB" | bc -l)
    SIZE_DIFF_ABS=$(echo "$SIZE_DIFF" | tr -d '-')
    SIZE_DIFF_FORMATTED=$(format_size "$SIZE_DIFF_ABS")

    echo "Current Build:    $IMAGE_SIZE_FORMATTED ($IMAGE_SIZE_MB MB)"
    echo "Previous Build:   $PREVIOUS_SIZE_FORMATTED ($PREVIOUS_SIZE_MB MB)"
    echo ""

    # Calculate percentage change
    if (( $(echo "$PREVIOUS_SIZE_MB != 0" | bc -l) )); then
        PERCENT_CHANGE=$(echo "scale=2; ($SIZE_DIFF / $PREVIOUS_SIZE_MB) * 100" | bc -l)
        PERCENT_CHANGE_ABS=$(echo "$PERCENT_CHANGE" | tr -d '-')

        if (( $(echo "$SIZE_DIFF > 0" | bc -l) )); then
            # Image size increased
            echo "Size Change:      +$SIZE_DIFF_FORMATTED (+${PERCENT_CHANGE}%)"

            # Check if increase is significant
            if (( $(echo "$PERCENT_CHANGE_ABS > $SIZE_INCREASE_WARNING" | bc -l) )); then
                print_warning "Significant size increase detected (>${SIZE_INCREASE_WARNING}%)"
                echo ""
                print_info "Possible causes:"
                echo "  - New dependencies added"
                echo "  - Build artifacts not properly cleaned up"
                echo "  - Changes to base image"
                echo "  - Additional static assets"
                echo ""
                print_info "Review recent changes and layer breakdown above"
            else
                print_info "Minor size increase within acceptable range"
            fi
        elif (( $(echo "$SIZE_DIFF < 0" | bc -l) )); then
            # Image size decreased
            echo "Size Change:      -$SIZE_DIFF_FORMATTED (-${PERCENT_CHANGE_ABS}%)"
            print_success "Image size reduced - good optimization!"
        else
            # No change
            echo "Size Change:      No change"
            print_success "Image size remained stable"
        fi
    fi

    echo ""
fi

# Save current size for next comparison
if [ -n "$PREVIOUS_SIZE_FILE" ]; then
    echo "$IMAGE_SIZE_MB" > "$PREVIOUS_SIZE_FILE"
    print_info "Current size saved to: $PREVIOUS_SIZE_FILE"
    echo ""
fi

# ============================================================================
# Optimization Recommendations
# ============================================================================

print_header "Optimization Recommendations"
echo ""

if [[ "$IMAGE_TYPE" == "production" ]]; then
    echo "Production Image Optimizations:"
    echo ""

    # Check base image
    BASE_IMAGE=$(docker history "$IMAGE_NAME" --no-trunc | tail -1 | awk '{print $1}')

    if (( $(echo "$IMAGE_SIZE_MB > 50" | bc -l) )); then
        echo "1. Base Image Selection:"
        echo "   Current size suggests room for optimization"
        echo "   - Consider using nginx:alpine (smaller than standard nginx)"
        echo "   - Verify multi-stage build is correctly configured"
        echo ""
    fi

    if (( $(echo "$IMAGE_SIZE_MB > 30" | bc -l) )); then
        echo "2. Static Asset Optimization:"
        echo "   - Ensure JavaScript/CSS is minified and tree-shaken"
        echo "   - Enable gzip compression in nginx"
        echo "   - Optimize images (use WebP, compress PNGs/JPEGs)"
        echo "   - Remove source maps from production builds"
        echo ""
    fi

    echo "3. Layer Optimization:"
    echo "   - Combine RUN commands to reduce layers"
    echo "   - Clean up package manager caches in same layer"
    echo "   - Use .dockerignore to exclude unnecessary files"
    echo ""

    echo "4. Build Process:"
    echo "   - Use BuildKit cache mounts for faster builds"
    echo "   - Verify production build removes dev dependencies"
    echo "   - Check that only dist/ contents are copied to final image"
    echo ""

else
    echo "Development Image Optimizations:"
    echo ""

    echo "1. Dependencies:"
    echo "   - Development images can be larger than production"
    echo "   - Ensure only necessary build tools are included"
    echo "   - Use cache mounts for node_modules to speed up builds"
    echo ""

    echo "2. Build Performance:"
    echo "   - Use named volumes for node_modules in docker-compose"
    echo "   - Enable BuildKit features for better caching"
    echo "   - Consider using bind mounts for source code during development"
    echo ""
fi

echo "General Best Practices:"
echo "  - Use .dockerignore to exclude .git, node_modules, coverage, etc."
echo "  - Leverage layer caching by copying package files before source"
echo "  - Use --no-cache flag to verify build still works without cache"
echo "  - Regularly update base images for security and performance improvements"
echo ""

# ============================================================================
# Summary and Exit
# ============================================================================

print_header "Analysis Summary"
echo ""

echo "Image Name:       $IMAGE_NAME"
echo "Image Type:       $IMAGE_TYPE"
echo "Total Size:       $IMAGE_SIZE_FORMATTED ($IMAGE_SIZE_MB MB)"
echo "Size Threshold:   ${SIZE_THRESHOLD_MB} MB"
echo "Threshold Status: $(if [ "$THRESHOLD_EXCEEDED" = true ]; then echo "⚠ EXCEEDED"; else echo "✓ WITHIN LIMIT"; fi)"
echo "Total Layers:     $TOTAL_LAYERS"
echo ""

if [ "$THRESHOLD_EXCEEDED" = true ]; then
    print_warning "Image size validation completed with warnings"
    echo ""
    print_info "This is a non-fatal warning. Consider optimizing the image size."
    exit 2
else
    print_success "Image size validation completed successfully"
    exit 0
fi
