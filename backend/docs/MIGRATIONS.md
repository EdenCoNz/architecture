# Database Migrations Guide

This document provides comprehensive guidance on database migrations using Alembic with SQLAlchemy 2.0 async support.

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Creating Migrations](#creating-migrations)
- [Running Migrations](#running-migrations)
- [Rollback Migrations](#rollback-migrations)
- [Migration Workflow](#migration-workflow)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

We use **Alembic** for database schema migrations. Alembic provides:
- Version control for database schemas
- Automatic migration generation from model changes
- Forward and backward migration support
- Production-safe schema changes

### Migration System Components

```
backend/
├── alembic/
│   ├── versions/          # Migration files
│   │   └── 001_initial_schema.py
│   ├── env.py            # Alembic environment configuration
│   └── script.py.mako    # Migration template
├── alembic.ini           # Alembic configuration
└── app/
    └── models/           # SQLAlchemy models
        ├── base.py       # Base model with common fields
        └── user.py       # User model
```

## Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or using make
make install
```

### 2. Start Database

```bash
# Start PostgreSQL and Redis in Docker
make db-up

# Verify connection
make db-test
```

### 3. Configure Environment

Ensure `.env` file has correct database settings:

```bash
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app_dev
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
```

## Creating Migrations

### Automatic Migration Generation

Alembic can automatically detect model changes and generate migrations:

```bash
# Create migration with autogenerate
make migration MSG="add user profile fields"

# Or using alembic directly
alembic revision --autogenerate -m "add user profile fields"
```

### Manual Migration Creation

For complex schema changes, create migrations manually:

```bash
# Create empty migration
alembic revision -m "custom migration"
```

Then edit the generated file in `alembic/versions/` to add upgrade/downgrade logic.

### Migration File Structure

```python
"""Migration message

Revision ID: 001
Revises: None
Create Date: 2025-10-18 22:15:00

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None

def upgrade() -> None:
    """Apply schema changes."""
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        # ... more columns
    )

def downgrade() -> None:
    """Revert schema changes."""
    op.drop_table('users')
```

## Running Migrations

### Apply All Pending Migrations

```bash
# Run all pending migrations
make migrate

# Or using alembic directly
alembic upgrade head
```

### Apply Specific Migration

```bash
# Upgrade to specific revision
alembic upgrade <revision_id>

# Upgrade one step forward
alembic upgrade +1
```

### Check Migration Status

```bash
# Test migrations and check status
make migrate-test

# View current migration version
make migration-current

# View migration history
make migration-history
```

## Rollback Migrations

### Rollback Last Migration

```bash
# Rollback one migration
make migration-down

# Or using alembic directly
alembic downgrade -1
```

### Rollback to Specific Version

```bash
# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### Rollback in Production

⚠️ **WARNING**: Rollbacks in production can cause data loss!

Before rolling back in production:
1. Create a database backup
2. Review the downgrade() function
3. Test rollback in staging environment
4. Coordinate with team (may require downtime)

## Migration Workflow

### Development Workflow

1. **Make Model Changes**
   ```python
   # app/models/user.py
   class User(BaseModel):
       email: Mapped[str] = mapped_column(String(255))
       # Add new field
       phone: Mapped[Optional[str]] = mapped_column(String(20))
   ```

2. **Generate Migration**
   ```bash
   make migration MSG="add phone field to user"
   ```

3. **Review Migration**
   - Check generated file in `alembic/versions/`
   - Verify upgrade() and downgrade() logic
   - Add indexes, constraints as needed

4. **Test Migration Locally**
   ```bash
   # Apply migration
   make migrate

   # Test it works
   make migrate-test

   # Test rollback
   make migration-down

   # Re-apply
   make migrate
   ```

5. **Commit Migration**
   ```bash
   git add alembic/versions/
   git add app/models/
   git commit -m "Add phone field to user model"
   ```

### Production Deployment Workflow

1. **Backup Database**
   ```bash
   pg_dump -h <host> -U <user> <database> > backup.sql
   ```

2. **Review Migrations**
   ```bash
   # Check pending migrations
   alembic current
   alembic history
   ```

3. **Apply Migrations**
   ```bash
   # Run in production
   alembic upgrade head
   ```

4. **Verify Success**
   ```bash
   # Check migration status
   alembic current

   # Run application health check
   curl http://localhost:8000/health
   ```

## Best Practices

### Model Design

1. **Use BaseModel for Common Fields**
   ```python
   from app.models.base import BaseModel

   class MyModel(BaseModel):  # Inherits id, created_at, updated_at
       name: Mapped[str] = mapped_column(String(100))
   ```

2. **Define Proper Indexes**
   ```python
   __table_args__ = (
       Index('ix_users_email_active', 'email', 'is_active'),
   )
   ```

3. **Use Proper Data Types**
   - UUID for primary keys (better distribution, security)
   - DateTime(timezone=True) for timestamps
   - String with max length for text fields
   - Boolean for flags (with defaults)

### Migration Best Practices

1. **One Logical Change Per Migration**
   - Keep migrations focused and atomic
   - Easier to review, test, and rollback

2. **Always Test Migrations**
   ```bash
   # Test forward migration
   make migrate

   # Test backward migration
   make migration-down
   make migrate
   ```

3. **Make Migrations Reversible**
   - Always implement proper downgrade()
   - Test rollback works correctly

4. **Avoid Data Migrations in Schema Migrations**
   - Separate data changes from schema changes
   - Use separate scripts for large data migrations

5. **Use Transactions**
   - Alembic wraps migrations in transactions by default
   - For non-transactional DDL, use `op.execute()`

### Production Safety

1. **Test in Staging First**
   - Always test migrations in staging environment
   - Verify no data loss or corruption

2. **Plan for Zero-Downtime**
   - Add columns as nullable first
   - Backfill data in separate step
   - Make column NOT NULL after backfill

3. **Monitor Migration Performance**
   - Large table migrations may lock tables
   - Consider maintenance window for heavy migrations

4. **Keep Backups**
   - Always backup before running migrations
   - Test restore procedure

## Troubleshooting

### Common Issues

#### 1. "Target database is not up to date"

```bash
# Check current version
alembic current

# View history
alembic history

# Upgrade to head
alembic upgrade head
```

#### 2. "Can't locate revision identified by..."

```bash
# Check all migration files exist in alembic/versions/
# Check alembic_version table
psql -h localhost -U postgres -d app_dev -c "SELECT * FROM alembic_version;"
```

#### 3. Migration Conflicts

```bash
# If multiple branches exist
alembic merge -m "merge branches" <rev1> <rev2>
```

#### 4. Database Connection Issues

```bash
# Test connection
make db-test

# Check .env configuration
cat .env | grep DATABASE_URL

# Check database is running
make db-up
```

#### 5. Import Errors in Migrations

```bash
# Ensure all models are imported in app/models/__init__.py
# Check alembic/env.py imports Base correctly
```

### Reset Migrations (Development Only)

⚠️ **WARNING**: This will delete all data!

```bash
# Reset database and migrations
make db-reset

# Re-run all migrations
make migrate
```

## Advanced Topics

### Branching Migrations

```bash
# Create branch
alembic revision -m "feature branch" --head=<base_revision>

# Merge branches
alembic merge -m "merge feature" <rev1> <rev2>
```

### Custom Migration Context

Edit `alembic/env.py` to customize migration behavior:
- Add custom compare functions
- Configure migration context
- Set up logging

### Offline SQL Generation

Generate SQL without applying:

```bash
# Generate SQL for all migrations
alembic upgrade head --sql > migrations.sql

# Generate SQL for specific version
alembic upgrade <revision> --sql > migration.sql
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- Project DATABASE.md for database configuration details
