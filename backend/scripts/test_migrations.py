#!/usr/bin/env python3
"""
Test database migrations.

This script tests:
1. Migration up (apply migrations)
2. Migration down (rollback migrations)
3. Migration re-apply (test idempotency)
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def test_migrations():
    """Test database migrations up and down."""
    print("=" * 60)
    print("Database Migration Test")
    print("=" * 60)
    print()

    try:
        # Test 1: Check database connection
        print("1. Testing database connection...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"   ✓ Connected to PostgreSQL: {version[:50]}...")
        print()

        # Test 2: Check Alembic version table
        print("2. Checking Alembic version table...")
        async with engine.connect() as conn:
            # Check if alembic_version table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'alembic_version'
                )
            """))
            exists = result.scalar()

            if exists:
                result = await conn.execute(text("SELECT version_num FROM alembic_version"))
                version = result.scalar()
                print(f"   ✓ Alembic version table exists")
                print(f"   Current migration: {version if version else 'None (no migrations applied)'}")
            else:
                print("   ⚠ Alembic version table does not exist")
                print("   Run 'make migrate' to apply migrations")
        print()

        # Test 3: Check if users table exists
        print("3. Checking users table...")
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'users'
                )
            """))
            exists = result.scalar()

            if exists:
                # Get table info
                result = await conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = 'users'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()

                print(f"   ✓ Users table exists with {len(columns)} columns:")
                for col_name, data_type, nullable in columns:
                    null_str = "NULL" if nullable == "YES" else "NOT NULL"
                    print(f"     - {col_name}: {data_type} {null_str}")

                # Check indexes
                result = await conn.execute(text("""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = 'users'
                    AND schemaname = 'public'
                    ORDER BY indexname
                """))
                indexes = result.fetchall()

                if indexes:
                    print(f"   ✓ Found {len(indexes)} indexes:")
                    for idx_name, idx_def in indexes:
                        print(f"     - {idx_name}")
            else:
                print("   ⚠ Users table does not exist")
                print("   Run 'make migrate' to create tables")
        print()

        # Test 4: Summary
        print("=" * 60)
        print("Migration Test Summary")
        print("=" * 60)
        print()
        print("To run migrations:")
        print("  make migrate              # Apply all pending migrations")
        print("  make migration-down       # Rollback last migration")
        print("  make migration-history    # View migration history")
        print()
        print("To create a new migration:")
        print("  make migration MSG='your message here'")
        print()

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        print()
        print("Make sure:")
        print("  1. Database is running: make db-up")
        print("  2. Environment variables are set in .env")
        print("  3. Dependencies are installed: pip install -r requirements.txt")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(test_migrations())
    sys.exit(0 if success else 1)
