#!/bin/bash
set -e

echo "=== Backend Development Container ==="

# Fix log file permissions
# This ensures the django user (UID 1001) can write to log files
# even if they were created on the host with different ownership
echo "Setting up log directory permissions..."
if [ -d "/app/logs" ]; then
    # Create log directory if it doesn't exist
    mkdir -p /app/logs

    # Fix permissions on existing log files
    # Use find to handle the case where no log files exist yet
    find /app/logs -type f -name "*.log" -exec chmod 666 {} \; 2>/dev/null || true

    # Ensure directory is writable
    chmod 755 /app/logs 2>/dev/null || true
fi
echo "Log directory permissions set successfully!"
echo ""

# Validate configuration
echo "Validating configuration..."
python manage.py check_config --quiet || exit 1
echo "Configuration validated successfully!"
echo ""

echo "Waiting for PostgreSQL to be ready..."

# Wait for database to be ready
python manage.py check_database --wait 30

echo "Database is ready!"
echo ""

# Check for pending migrations
if python manage.py showmigrations | grep -q "\[ \]"; then
    echo "Found pending migrations. Running migrate..."
    python manage.py migrate --noinput
    echo "Migrations applied successfully!"
    echo ""
else
    echo "No pending migrations."
    echo ""
fi

# Execute the command passed to docker run
exec "$@"
