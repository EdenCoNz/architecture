#!/bin/bash
set -e

echo "=== Backend Production Container ==="

# Validate configuration first (critical for production)
echo "Validating production configuration..."
python manage.py check_config --quiet || exit 1
echo "Configuration validated successfully!"
echo ""

echo "Waiting for PostgreSQL to be ready..."

# Wait for database
python manage.py check_database --wait 60

echo "Database is ready!"

# Run production checks
echo "Running deployment checks..."
python manage.py check --deploy --fail-level WARNING

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Production setup complete!"
echo ""

# Execute the command
exec "$@"
