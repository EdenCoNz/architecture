# Database Configuration Guide

This guide covers database setup, connection management, and best practices for the FastAPI application with PostgreSQL and SQLAlchemy.

## Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Connection Pooling](#connection-pooling)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Migration Management](#migration-management)
- [Production Best Practices](#production-best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The application uses:
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 with async support
- **Driver**: asyncpg (async) and psycopg2 (sync for Alembic)
- **Migrations**: Alembic

### Key Features

- Async database operations using `asyncpg`
- Connection pooling with configurable limits
- Automatic connection health checks
- Environment-based configuration
- Transaction management with automatic rollback
- FastAPI dependency injection for database sessions

## Configuration

### Environment Variables

Configure the database connection in `.env`:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app_db

# Connection Pool Settings
DATABASE_POOL_SIZE=5              # Number of persistent connections
DATABASE_MAX_OVERFLOW=10          # Additional connections when pool is full
DATABASE_POOL_TIMEOUT=30          # Seconds to wait for connection from pool
DATABASE_POOL_RECYCLE=3600        # Recycle connections after seconds
DATABASE_ECHO=false               # Log all SQL statements
```

### Connection URL Format

```
postgresql+asyncpg://user:password@host:port/database
```

**Components:**
- `postgresql+asyncpg`: Async PostgreSQL driver
- `user`: Database username
- `password`: Database password
- `host`: Database server hostname or IP
- `port`: Database port (default: 5432)
- `database`: Database name

### Environment-Specific Settings

#### Development
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app_dev
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_ECHO=true  # Enable SQL logging for debugging
```

#### Testing
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app_test
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=5
```

#### Production
```bash
DATABASE_URL=postgresql+asyncpg://dbuser:secure_password@db.example.com:5432/app_production
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=20
DATABASE_ECHO=false
```

## Connection Pooling

### How It Works

SQLAlchemy maintains a pool of database connections to minimize connection overhead:

1. **Pool Size**: Minimum number of connections kept alive
2. **Max Overflow**: Additional connections created when pool is full
3. **Pool Timeout**: How long to wait for an available connection
4. **Pool Recycle**: How long before recycling a connection (prevents stale connections)
5. **Pre-Ping**: Tests connection health before use

### Pool Sizing Guidelines

**Formula**: `pool_size + max_overflow >= expected_concurrent_requests`

**Recommendations:**

| Environment | Pool Size | Max Overflow | Total Max | Use Case |
|-------------|-----------|--------------|-----------|----------|
| Development | 5         | 10           | 15        | Local dev, low concurrency |
| Testing     | 5         | 5            | 10        | Test isolation |
| Staging     | 20        | 10           | 30        | Pre-production testing |
| Production  | 50        | 20           | 70        | High traffic (1000+ RPS) |

**Important Notes:**
- PostgreSQL default `max_connections` is 100
- Reserve connections for admin tasks, monitoring
- Each application instance needs its own pool
- Monitor connection usage in production

## Usage Examples

### FastAPI Dependency Injection

The recommended way to use database sessions in FastAPI endpoints:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID with automatic transaction management."""
    from sqlalchemy import select
    from app.models import User

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
    # Transaction automatically committed or rolled back
```

### Manual Session Management

For operations outside FastAPI endpoints:

```python
from app.core.database import AsyncSessionLocal

async def create_user(username: str, email: str):
    """Create a new user."""
    async with AsyncSessionLocal() as session:
        try:
            user = User(username=username, email=email)
            session.add(user)
            await session.commit()
            await session.refresh(user)  # Load auto-generated fields
            return user
        except Exception as e:
            await session.rollback()
            raise
```

### Batch Operations

```python
async def create_multiple_users(users_data: list[dict]):
    """Efficiently create multiple users."""
    async with AsyncSessionLocal() as session:
        try:
            users = [User(**data) for data in users_data]
            session.add_all(users)
            await session.commit()
            return users
        except Exception as e:
            await session.rollback()
            raise
```

### Direct Engine Usage

For raw SQL queries:

```python
from sqlalchemy import text
from app.core.database import engine

async def execute_raw_query():
    """Execute raw SQL query."""
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT * FROM users WHERE created_at > :date"),
            {"date": "2025-01-01"}
        )
        rows = result.fetchall()
        return rows
```

## Testing

### Test Database Connection

Run the connection test script:

```bash
# Make sure PostgreSQL is running
python scripts/test_db_connection.py
```

**Expected Output:**
```
======================================================================
Database Connection Test
======================================================================

Configuration:
  Environment: development
  Database URL: localhost:5432/app_db
  Pool Size: 5
  Max Overflow: 10
  Pool Timeout: 30s
  Pool Recycle: 3600s

Testing connection...
✓ Connection successful!

Database Information:
  PostgreSQL Version: PostgreSQL 16.1 on x86_64-pc-linux-gnu
  Database: app_db
  User: postgres
  Host: 127.0.0.1
  Port: 5432
  Driver: asyncpg (async: True)
  Pool Size: 5
  Max Overflow: 10

======================================================================
✓ Database is ready for use!
======================================================================
```

### Health Check Endpoint

Test via FastAPI health check:

```bash
# Start the application
uvicorn main:app --reload

# Check health endpoint
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "0.1.0",
  "checks": {
    "database": "healthy"
  }
}
```

### Test Database Setup

For running tests with a separate test database:

```python
# conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.database import Base

@pytest.fixture
async def test_db():
    """Create test database and tables."""
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/app_test",
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
```

## Migration Management

### Using Alembic

```bash
# Create a new migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

### Migration Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations on staging** before production
3. **Create backup** before running migrations in production
4. **Use database transactions** for migration rollback capability
5. **Version control** all migration files in Git

## Production Best Practices

### Connection Pool Tuning

1. **Monitor connection usage**:
   ```sql
   SELECT count(*) FROM pg_stat_activity WHERE datname = 'app_production';
   ```

2. **Adjust pool size** based on:
   - Number of application instances
   - Expected concurrent requests
   - Database server capacity

3. **Set max_connections** in PostgreSQL:
   ```sql
   ALTER SYSTEM SET max_connections = 200;
   SELECT pg_reload_conf();
   ```

### Security

1. **Use strong passwords** for database users
2. **Restrict network access** with firewalls/security groups
3. **Enable SSL/TLS** for database connections:
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
   ```

4. **Use separate credentials** for different environments
5. **Rotate credentials** regularly
6. **Never commit** `.env` files to version control

### Performance Optimization

1. **Enable connection pooling** (already configured)
2. **Use indexes** on frequently queried columns
3. **Monitor slow queries**:
   ```sql
   SELECT query, mean_exec_time
   FROM pg_stat_statements
   ORDER BY mean_exec_time DESC
   LIMIT 10;
   ```

4. **Use `EXPLAIN ANALYZE`** to optimize queries
5. **Implement caching** with Redis for frequently accessed data

### Monitoring

1. **Track connection pool metrics**:
   - Pool size usage
   - Connection wait times
   - Connection errors

2. **Monitor database performance**:
   - Query execution times
   - Lock contention
   - Connection count

3. **Set up alerts** for:
   - Connection pool exhaustion
   - Slow queries (>1s)
   - Connection failures

## Troubleshooting

### Connection Failed

**Error**: `Connection refused`

**Solutions**:
1. Ensure PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   # or
   pg_ctl status
   ```

2. Check PostgreSQL port:
   ```bash
   sudo netstat -tlnp | grep 5432
   ```

3. Verify PostgreSQL accepts connections:
   ```bash
   psql -h localhost -U postgres -d app_db
   ```

### Authentication Failed

**Error**: `password authentication failed for user`

**Solutions**:
1. Verify credentials in `.env`
2. Check PostgreSQL `pg_hba.conf`:
   ```bash
   sudo nano /etc/postgresql/16/main/pg_hba.conf
   ```

3. Reload PostgreSQL configuration:
   ```bash
   sudo systemctl reload postgresql
   ```

### Database Does Not Exist

**Error**: `database "app_db" does not exist`

**Solution**:
```bash
# Create database
psql -U postgres -c "CREATE DATABASE app_db;"

# Or using createdb
createdb -U postgres app_db
```

### Pool Timeout Errors

**Error**: `QueuePool limit of size X overflow Y reached`

**Solutions**:
1. Increase `DATABASE_MAX_OVERFLOW`
2. Investigate slow queries blocking connections
3. Ensure sessions are properly closed
4. Scale horizontally (add more application instances)

### Migration Conflicts

**Error**: `Target database is not up to date`

**Solutions**:
```bash
# Check current version
alembic current

# View migration history
alembic history

# Stamp database to specific version
alembic stamp head

# Force upgrade
alembic upgrade head
```

## Resources

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [FastAPI Database Guide](https://fastapi.tiangolo.com/tutorial/sql-databases/)

## Support

For issues or questions:
1. Check this documentation
2. Review logs in `backend/logs/`
3. Run connection test: `python scripts/test_db_connection.py`
4. Check PostgreSQL logs
5. Review application logs during startup
