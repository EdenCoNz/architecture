# Database Persistence Layer

## Overview

The backend uses PostgreSQL 15+ as the primary data store with Django ORM for database interactions. This document covers database configuration, connectivity management, health monitoring, and best practices.

## Table of Contents

1. [Configuration](#configuration)
2. [Connection Management](#connection-management)
3. [Health Monitoring](#health-monitoring)
4. [Error Handling](#error-handling)
5. [Environment-Specific Settings](#environment-specific-settings)
6. [Migrations](#migrations)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Configuration

### Environment Variables

Database configuration is managed through environment variables (never hardcoded). Create a `.env` file based on `.env.example`:

```bash
# Database Configuration
DB_NAME=backend_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### Connection Settings

Database settings are defined in `config/settings/base.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='backend_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'ATOMIC_REQUESTS': True,  # Wrap each request in a transaction
        'CONN_MAX_AGE': 600,      # Connection pooling (10 minutes)
    }
}
```

### Key Features

1. **Connection Pooling** (`CONN_MAX_AGE=600`):
   - Reuses database connections for 10 minutes
   - Reduces connection overhead
   - Improves performance under load

2. **Atomic Requests** (`ATOMIC_REQUESTS=True`):
   - Each request wrapped in a transaction
   - Automatic rollback on errors
   - Ensures data consistency

3. **Environment-Based Configuration**:
   - Different settings for dev/test/prod
   - No hardcoded credentials
   - Secure credential management

## Connection Management

### Health Check Utility

The `DatabaseHealthCheck` class provides comprehensive connection monitoring:

```python
from apps.core.database import DatabaseHealthCheck

# Check database connectivity
checker = DatabaseHealthCheck()
result = checker.check()

if result['status'] == 'healthy':
    print(f"Database connected: {result['response_time_ms']}ms")
else:
    print(f"Database error: {result['error']}")
```

### Management Command

Check database connectivity from the command line:

```bash
# Single check
python manage.py check_database

# Wait up to 30 seconds for database to become available
python manage.py check_database --wait 30

# Custom retry interval
python manage.py check_database --wait 30 --retry-interval 5
```

### Programmatic Checks

```python
from apps.core.database import (
    check_database_connection,
    get_database_status,
    ensure_database_connection
)

# Simple boolean check
if check_database_connection(verbose=True):
    print("Database ready!")

# Detailed status information
status = get_database_status()
print(f"Connected: {status['connected']}")
print(f"Response time: {status['response_time_ms']}ms")

# Ensure connection or raise error
ensure_database_connection()  # Raises OperationalError if fails
```

## Health Monitoring

### Startup Checks

The application automatically checks database connectivity on startup:

- **Development (`runserver`)**: Warns but allows startup
- **Production (WSGI/ASGI)**: Checks connectivity
- **Management Commands**: Smart skip for commands that don't need DB

### Response Format

Health check returns detailed status:

```json
{
    "status": "healthy",
    "database": "connected",
    "response_time_ms": 2.34,
    "connection_info": {
        "engine": "django.db.backends.postgresql",
        "host": "localhost",
        "port": "5432",
        "name": "backend_db",
        "user": "postgres"
    }
}
```

### Graceful Degradation

Two modes for handling database failures:

1. **Warn Mode** (Development):
   ```python
   from apps.core.management.commands.check_database import DatabaseReadyCheck

   # Warns but continues
   if not DatabaseReadyCheck.check_and_warn():
       print("Database unavailable but continuing...")
   ```

2. **Fail Mode** (Production):
   ```python
   # Exits application if database unavailable
   DatabaseReadyCheck.ensure_or_fail()
   ```

## Error Handling

### Clear Error Messages

The health check provides user-friendly error messages:

```python
# Database doesn't exist
"Database 'backend_db' does not exist. Please create the database
or check DB_NAME environment variable."

# Authentication failed
"Authentication failed for user 'postgres'. Please check DB_USER
and DB_PASSWORD environment variables."

# Connection refused
"Could not connect to database server at localhost:5432. Please
ensure PostgreSQL is running and check DB_HOST and DB_PORT."

# User doesn't exist
"Database user 'postgres' does not exist. Please create the user
or check DB_USER environment variable."
```

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | PostgreSQL not running | `sudo systemctl start postgresql` |
| Database does not exist | Database not created | `createdb backend_db` |
| Authentication failed | Wrong credentials | Check `.env` file credentials |
| Role does not exist | User not created | `createuser -P postgres` |
| Permission denied | Insufficient privileges | Grant permissions to user |

## Environment-Specific Settings

### Development (`config/settings/development.py`)

```python
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Uses environment variables from .env
# Typically: DB_HOST=localhost, DB_NAME=backend_db
```

### Testing (`config/settings/testing.py`)

```python
# Uses separate test database (automatically created/destroyed)
# Faster settings optimized for test performance
DATABASES['default']['CONN_MAX_AGE'] = 0  # No pooling in tests
```

### Production (`config/settings/production.py`)

```python
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

# Production database settings from environment
# Typically: DB_HOST=db.example.com, SSL required
```

## Migrations

### Creating Migrations

```bash
# Create migrations after model changes
python manage.py makemigrations

# Create named migration
python manage.py makemigrations --name add_user_profile_fields

# Show SQL for migration
python manage.py sqlmigrate app_name 0001

# Check for migration issues
python manage.py check
```

### Applying Migrations

```bash
# Apply all pending migrations
python manage.py migrate

# Apply to specific app
python manage.py migrate app_name

# Show migration status
python manage.py showmigrations

# Migrate to specific migration
python manage.py migrate app_name 0003
```

### Migration Best Practices

1. **Always create migrations in development**
2. **Review migrations before committing**
3. **Test migrations on production copy**
4. **Use data migrations for complex changes**
5. **Never edit applied migrations**
6. **Use `RunPython` for data migrations**

## Best Practices

### 1. Use Transactions

```python
from django.db import transaction

# Atomic decorator
@transaction.atomic
def create_user_with_profile(user_data, profile_data):
    user = User.objects.create(**user_data)
    Profile.objects.create(user=user, **profile_data)
    return user

# Context manager
with transaction.atomic():
    user = User.objects.create(**user_data)
    Profile.objects.create(user=user, **profile_data)
```

### 2. Use select_related and prefetch_related

```python
# Avoid N+1 queries with select_related (ForeignKey)
users = User.objects.select_related('profile').all()

# Use prefetch_related for reverse relationships
users = User.objects.prefetch_related('orders').all()

# Combine both
users = User.objects.select_related('profile').prefetch_related('orders')
```

### 3. Use Database Indexes

```python
class User(models.Model):
    email = models.EmailField(db_index=True)  # Single index

    class Meta:
        indexes = [
            models.Index(fields=['last_name', 'first_name']),  # Composite index
            models.Index(fields=['-created_at']),  # Descending index
        ]
```

### 4. Use QuerySet Methods

```python
# Good - single query
User.objects.filter(is_active=True).update(last_login=timezone.now())

# Bad - multiple queries
for user in User.objects.filter(is_active=True):
    user.last_login = timezone.now()
    user.save()
```

### 5. Handle Database Errors

```python
from django.db import IntegrityError, OperationalError

try:
    user = User.objects.create(email=email)
except IntegrityError:
    # Handle duplicate key error
    logger.error(f"User with email {email} already exists")
except OperationalError:
    # Handle database connection error
    logger.error("Database connection failed")
```

### 6. Use Connection Pooling

Already configured via `CONN_MAX_AGE=600`:
- Connections reused for 10 minutes
- Reduces connection overhead
- Improves performance

### 7. Monitor Query Performance

```python
from django.db import connection

# Check query count
print(len(connection.queries))

# Log slow queries
for query in connection.queries:
    if float(query['time']) > 0.1:  # Slower than 100ms
        logger.warning(f"Slow query: {query['sql']}")
```

## Troubleshooting

### Database Won't Connect

1. **Check if PostgreSQL is running:**
   ```bash
   sudo systemctl status postgresql
   sudo systemctl start postgresql
   ```

2. **Verify database exists:**
   ```bash
   psql -U postgres -l
   createdb backend_db
   ```

3. **Test connection manually:**
   ```bash
   psql -U postgres -h localhost -d backend_db
   ```

4. **Check Django configuration:**
   ```bash
   python manage.py check_database
   ```

### Connection Pooling Issues

If seeing "too many connections" errors:

```python
# Reduce CONN_MAX_AGE in settings
DATABASES['default']['CONN_MAX_AGE'] = 60  # 1 minute instead of 10
```

### Migration Conflicts

```bash
# Show migration status
python manage.py showmigrations

# Merge conflicting migrations
python manage.py makemigrations --merge

# Fake a migration if already applied manually
python manage.py migrate --fake app_name 0001
```

### Performance Issues

1. **Enable query logging in development:**
   ```python
   # settings/development.py
   LOGGING['loggers']['django.db.backends'] = {
       'level': 'DEBUG',
       'handlers': ['console'],
   }
   ```

2. **Use Django Debug Toolbar:**
   - Already installed in development
   - Shows all queries per request
   - Identifies N+1 query problems

3. **Profile with django-extensions:**
   ```bash
   python manage.py shell_plus --print-sql
   ```

### Common PostgreSQL Commands

```bash
# List databases
psql -U postgres -c "\l"

# List tables in database
psql -U postgres -d backend_db -c "\dt"

# Show table structure
psql -U postgres -d backend_db -c "\d+ table_name"

# Drop database (careful!)
dropdb backend_db

# Create database
createdb backend_db

# Create user
createuser -P postgres

# Grant privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE backend_db TO postgres;"
```

## Security Considerations

1. **Never commit credentials to version control**
2. **Use strong passwords in production**
3. **Enable SSL for production databases**
4. **Restrict database user permissions**
5. **Use read-only replicas when appropriate**
6. **Enable query logging for auditing**
7. **Regular backups (automated)**
8. **Monitor for suspicious queries**

## Production Checklist

- [ ] Database credentials in environment variables
- [ ] SSL/TLS enabled for database connections
- [ ] Connection pooling configured appropriately
- [ ] Database backups automated
- [ ] Monitoring and alerting configured
- [ ] Read replicas set up (if needed)
- [ ] Database user has minimal necessary permissions
- [ ] Query logging enabled for auditing
- [ ] Performance monitoring in place
- [ ] Disaster recovery plan documented

## Additional Resources

- [Django Database Documentation](https://docs.djangoproject.com/en/5.1/ref/databases/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Django ORM Optimization](https://docs.djangoproject.com/en/5.1/topics/db/optimization/)
- [Database Performance Tips](https://docs.djangoproject.com/en/5.1/topics/db/sql/)
