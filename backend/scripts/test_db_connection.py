#!/usr/bin/env python3
"""
Database connection test script.

This script tests the database connection and displays connection information.
Run this script to verify database configuration before starting the application.

Usage:
    python scripts/test_db_connection.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import (
    check_db_connection,
    get_db_info,
    engine,
    close_db_connections,
)
from app.core.config import settings


async def test_connection():
    """Test database connection and display information."""
    print("=" * 70)
    print("Database Connection Test")
    print("=" * 70)
    print()

    # Display configuration
    print("Configuration:")
    print(f"  Environment: {settings.environment}")
    print(f"  Database URL: {str(settings.database_url).split('@')[1] if '@' in str(settings.database_url) else 'invalid'}")
    print(f"  Pool Size: {settings.database_pool_size}")
    print(f"  Max Overflow: {settings.database_max_overflow}")
    print(f"  Pool Timeout: {settings.database_pool_timeout}s")
    print(f"  Pool Recycle: {settings.database_pool_recycle}s")
    print()

    # Test connection
    print("Testing connection...")
    is_healthy = await check_db_connection()

    if is_healthy:
        print("✓ Connection successful!")
        print()

        # Get detailed info
        print("Database Information:")
        db_info = await get_db_info()

        if "error" not in db_info:
            print(f"  PostgreSQL Version: {db_info['version']}")
            print(f"  Database: {db_info['database']}")
            print(f"  User: {db_info['user']}")
            print(f"  Host: {db_info['host']}")
            print(f"  Port: {db_info['port']}")
            print(f"  Driver: {db_info['driver']} (async: {db_info['is_async']})")
            print(f"  Pool Size: {db_info['pool_size']}")
            print(f"  Max Overflow: {db_info['max_overflow']}")
            print()
            print("=" * 70)
            print("✓ Database is ready for use!")
            print("=" * 70)
            return True
        else:
            print(f"  Error: {db_info['error']}")
            print(f"  Status: {db_info['status']}")
            print()
            print("=" * 70)
            print("✗ Failed to retrieve database information")
            print("=" * 70)
            return False
    else:
        print("✗ Connection failed!")
        print()
        print("Troubleshooting:")
        print("  1. Ensure PostgreSQL is running")
        print("  2. Check DATABASE_URL in .env file")
        print("  3. Verify database credentials")
        print("  4. Confirm database exists")
        print("  5. Check network connectivity to database host")
        print()
        print("=" * 70)
        print("✗ Database connection test failed")
        print("=" * 70)
        return False


async def main():
    """Main entry point."""
    try:
        success = await test_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print()
        print("=" * 70)
        print("✗ Unexpected error during connection test")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up connections
        await close_db_connections()


if __name__ == "__main__":
    asyncio.run(main())
