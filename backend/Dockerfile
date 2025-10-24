# =============================================================================
# Backend Development Dockerfile
# =============================================================================
# Multi-stage Dockerfile optimized for both development and production
# Development: Full-featured environment with hot reload and debugging tools
# Production: Minimal image with only runtime dependencies
# =============================================================================

# -----------------------------------------------------------------------------
# Base Stage: Common dependencies and setup
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS base

# Set environment variables to prevent Python from writing pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for PostgreSQL and other packages
# Use --mount=type=cache to cache apt packages for faster rebuilds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    # PostgreSQL client and development headers
    postgresql-client \
    libpq-dev \
    # Build tools for Python packages
    gcc \
    g++ \
    # Additional utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Create non-root user for security
# UID 1001 is conventional for application users
RUN groupadd -g 1001 -r django && \
    useradd -r -u 1001 -g django -m -d /home/django -s /bin/bash django && \
    chown -R django:django /app

# -----------------------------------------------------------------------------
# Development Stage: Full development environment
# -----------------------------------------------------------------------------
FROM base AS development

# Install development dependencies
COPY --chown=django:django requirements/base.txt requirements/dev.txt /app/requirements/

# Use cache mount for pip packages to speed up rebuilds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements/dev.txt

# Create directories for logs and media files
RUN mkdir -p /app/logs /app/media /app/staticfiles && \
    chown -R django:django /app/logs /app/media /app/staticfiles

# Copy application code
# In development, this will be overridden by volume mount for live code reloading
COPY --chown=django:django . /app/

# Create entrypoint script for development
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=== Backend Development Container ==="\n\
\n\
# Validate configuration\n\
echo "Validating configuration..."\n\
python manage.py check_config --quiet || exit 1\n\
echo "Configuration validated successfully!"\n\
echo ""\n\
\n\
echo "Waiting for PostgreSQL to be ready..."\n\
\n\
# Wait for database to be ready\n\
python manage.py check_database --wait 30\n\
\n\
echo "Database is ready!"\n\
echo ""\n\
\n\
# Check for pending migrations\n\
if python manage.py showmigrations | grep -q "\[ \]"; then\n\
    echo "Found pending migrations. Running migrate..."\n\
    python manage.py migrate --noinput\n\
    echo "Migrations applied successfully!"\n\
    echo ""\n\
else\n\
    echo "No pending migrations."\n\
    echo ""\n\
fi\n\
\n\
# Execute the command passed to docker run\n\
exec "$@"' > /app/docker-entrypoint-dev.sh && \
    chmod +x /app/docker-entrypoint-dev.sh && \
    chown django:django /app/docker-entrypoint-dev.sh

# Switch to non-root user
USER django

# Expose port for development server
EXPOSE 8000

# Health check for development
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Set entrypoint and default command
ENTRYPOINT ["/app/docker-entrypoint-dev.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# -----------------------------------------------------------------------------
# Production Builder Stage: Build dependencies
# -----------------------------------------------------------------------------
FROM base AS builder

# Install production dependencies only
COPY requirements/base.txt requirements/prod.txt /app/requirements/

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --user --no-warn-script-location -r requirements/prod.txt

# -----------------------------------------------------------------------------
# Production Stage: Minimal runtime image
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS production

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Install only runtime dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Create non-root user
RUN groupadd -g 1001 -r django && \
    useradd -r -u 1001 -g django -m -d /home/django -s /bin/bash django

# Copy Python packages from builder
COPY --from=builder --chown=django:django /root/.local /home/django/.local

# Copy application code
COPY --chown=django:django . /app/

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/staticfiles && \
    chown -R django:django /app/logs /app/media /app/staticfiles

# Create production entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=== Backend Production Container ==="\n\
\n\
# Validate configuration first (critical for production)\n\
echo "Validating production configuration..."\n\
python manage.py check_config --quiet || exit 1\n\
echo "Configuration validated successfully!"\n\
echo ""\n\
\n\
echo "Waiting for PostgreSQL to be ready..."\n\
\n\
# Wait for database\n\
python manage.py check_database --wait 60\n\
\n\
echo "Database is ready!"\n\
\n\
# Run production checks\n\
echo "Running deployment checks..."\n\
python manage.py check --deploy --fail-level WARNING\n\
\n\
# Apply migrations\n\
echo "Applying database migrations..."\n\
python manage.py migrate --noinput\n\
\n\
# Collect static files\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput --clear\n\
\n\
echo "Production setup complete!"\n\
echo ""\n\
\n\
# Execute the command\n\
exec "$@"' > /app/docker-entrypoint-prod.sh && \
    chmod +x /app/docker-entrypoint-prod.sh && \
    chown django:django /app/docker-entrypoint-prod.sh

# Update PATH to include user-installed packages
ENV PATH=/home/django/.local/bin:$PATH

# Switch to non-root user
USER django

# Expose port for production server
EXPOSE 8000

# Health check for production
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Set entrypoint and default command
ENTRYPOINT ["/app/docker-entrypoint-prod.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "30"]
