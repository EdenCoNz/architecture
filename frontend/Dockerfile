# ============================================================================
# Multi-Stage Dockerfile for React Frontend Application
# ============================================================================
#
# This Dockerfile creates a production-ready, optimized image for the React
# frontend application. It uses multi-stage builds to separate build-time
# dependencies from runtime, resulting in a minimal final image.
#
# Build Stage: Node 20 Alpine - Compiles TypeScript and builds production assets
# Production Stage: nginx:alpine - Serves static files with SPA routing support
#
# Target image size: <50MB
# ============================================================================

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage 1: Build Stage
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files first for better layer caching
# These files change less frequently than source code
COPY package.json package-lock.json ./

# Install dependencies with npm ci for reproducible builds
# Using BuildKit cache mount to speed up subsequent builds
# --only=production is NOT used here as we need devDependencies for building
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copy source code and configuration files
COPY . .

# Build arguments for environment variables
# These can be overridden at build time using --build-arg
ARG VITE_API_URL=http://localhost:8000
ARG VITE_DEV_MODE=false

# Set environment variables for the build process
# Vite will embed these into the JavaScript bundle at build time
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_DEV_MODE=${VITE_DEV_MODE}

# Build the application for production
# This creates optimized, minified assets in the dist/ directory
# Environment variables are embedded into the bundle during this step
RUN npm run build

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage 2: Production Stage
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FROM nginx:alpine

# Copy custom nginx configuration for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
# Only the compiled dist/ directory is copied - no source code or node_modules
COPY --from=builder /app/dist /usr/share/nginx/html

# Create non-root user and configure permissions
# Security best practice: never run containers as root
RUN addgroup -g 1001 -S nginx-app && \
    adduser -S nginx-app -u 1001 -G nginx-app && \
    chown -R nginx-app:nginx-app /usr/share/nginx/html && \
    chown -R nginx-app:nginx-app /var/cache/nginx && \
    chown -R nginx-app:nginx-app /var/log/nginx && \
    chown -R nginx-app:nginx-app /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx-app:nginx-app /var/run/nginx.pid

# Switch to non-root user
USER nginx-app

# Expose port 8080 (non-privileged port)
EXPOSE 8080

# Health check to verify nginx is serving content
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1

# Start nginx in foreground mode
CMD ["nginx", "-g", "daemon off;"]
