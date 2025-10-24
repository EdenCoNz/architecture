# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Frontend Application - Multi-stage Dockerfile
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# This Dockerfile supports both development and production environments using
# multi-stage builds with BuildKit optimization.
#
# Stages:
#   - base: Common dependencies and setup
#   - development: Hot module replacement, live code editing
#   - builder: Production build with optimizations
#   - production: Minimal nginx-based production server
#
# Build targets:
#   Development: docker build --target development -t frontend:dev .
#   Production:  docker build --target production -t frontend:prod .
#
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ============================================================================
# Base Stage - Common Dependencies
# ============================================================================
FROM node:20-alpine AS base

# Set working directory
WORKDIR /app

# Copy package files for dependency installation
COPY package.json package-lock.json ./

# ============================================================================
# Development Stage - Hot Module Replacement & Live Editing
# ============================================================================
FROM base AS development

# Install build dependencies if needed for native packages
RUN apk add --no-cache \
    python3 \
    make \
    g++

# Install all dependencies (including devDependencies)
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Create non-root user for development
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

# Switch to non-root user
USER nodejs

# Expose Vite dev server port
EXPOSE 5173

# Vite dev server with host binding for Docker
# --host 0.0.0.0 allows access from outside container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ============================================================================
# Builder Stage - Production Build
# ============================================================================
FROM base AS builder

# Runtime Configuration Strategy:
# Configuration is now loaded at runtime from the backend API endpoint.
# Build-time args are no longer required, making the image portable across environments.
#
# The frontend will:
# 1. Fetch configuration from /api/v1/config/frontend/ on startup
# 2. Fall back to these minimal defaults if the API is unavailable
#
# This allows the same image to be deployed to dev/staging/production
# without rebuilding.

# Minimal fallback configuration for local development
# These are only used if the backend API is not available
ARG VITE_API_URL=http://localhost:8000
ARG VITE_APP_NAME="Frontend Application"
ARG VITE_APP_VERSION=1.0.0

# Set minimal environment variables for build
# These provide fallback values only - runtime config takes precedence
ENV VITE_API_URL=$VITE_API_URL \
    VITE_APP_NAME=$VITE_APP_NAME \
    VITE_APP_VERSION=$VITE_APP_VERSION

# Install all dependencies (including devDependencies needed for build)
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copy application source
COPY . .

# Build application for production
# This creates optimized static assets in dist/
# Environment variables are embedded in the build
RUN npm run build

# ============================================================================
# Production Stage - Optimized Static Server
# ============================================================================
FROM nginx:1.27-alpine AS production

# Copy built static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create custom nginx configuration for SPA routing with optimizations
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Security headers \
    add_header X-Frame-Options "SAMEORIGIN" always; \
    add_header X-Content-Type-Options "nosniff" always; \
    add_header X-XSS-Protection "1; mode=block" always; \
    \
    # Enable gzip compression \
    gzip on; \
    gzip_vary on; \
    gzip_proxied any; \
    gzip_comp_level 6; \
    gzip_min_length 1000; \
    gzip_types \
        text/plain \
        text/css \
        text/xml \
        text/javascript \
        application/json \
        application/javascript \
        application/xml+rss \
        application/rss+xml \
        font/truetype \
        font/opentype \
        application/vnd.ms-fontobject \
        image/svg+xml; \
    \
    # Cache static assets aggressively \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|webp|avif)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
        access_log off; \
    } \
    \
    # Cache HTML with shorter duration \
    location ~* \.html$ { \
        expires 1h; \
        add_header Cache-Control "public, must-revalidate"; \
    } \
    \
    # SPA fallback - serve index.html for all routes \
    location / { \
        try_files $uri $uri/ /index.html =404; \
    } \
    \
    # Health check endpoint \
    location /health { \
        access_log off; \
        return 200 "healthy\\n"; \
        add_header Content-Type text/plain; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Remove default nginx config
RUN rm -f /etc/nginx/conf.d/default.conf.default 2>/dev/null || true

# Create directory for PID file and set permissions
RUN mkdir -p /var/cache/nginx/client_temp \
    /var/cache/nginx/proxy_temp \
    /var/cache/nginx/fastcgi_temp \
    /var/cache/nginx/uwsgi_temp \
    /var/cache/nginx/scgi_temp && \
    chmod -R 755 /var/cache/nginx && \
    chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    touch /var/run/nginx.pid && \
    chown nginx:nginx /var/run/nginx.pid

# Use built-in nginx user (created by nginx Alpine image)
USER nginx

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
