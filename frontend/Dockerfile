# Multi-stage Dockerfile for React + Vite application
# Following Docker best practices 2024-2025

# Base stage - common dependencies
FROM node:20-alpine AS base

WORKDIR /app

# Copy package files for dependency installation
COPY package*.json ./

# Install all dependencies with cache mount for faster builds
RUN --mount=type=cache,target=/root/.npm \
    npm install && \
    npm cache clean --force

# Development stage
FROM base AS development

# Set ownership of the app directory to node user (already exists in base image with UID/GID 1000)
RUN chown -R node:node /app

# Copy application source code
COPY --chown=node:node . .

# Switch to non-root user
USER node

# Expose Vite dev server port
EXPOSE 5173

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Build stage
FROM base AS builder

# Copy application source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:1.27-alpine AS production

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Set ownership to non-root user
RUN chown -R nodejs:nodejs /usr/share/nginx/html && \
    chown -R nodejs:nodejs /var/cache/nginx && \
    chown -R nodejs:nodejs /var/log/nginx && \
    chown -R nodejs:nodejs /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nodejs:nodejs /var/run/nginx.pid

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
