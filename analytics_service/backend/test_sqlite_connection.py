"""Test SQLite database connection."""

import asyncio
import sqlite3
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def test_sqlite_connection():
    """Test SQLite database connection and basic operations."""
    
    print(f"Testing SQLite connection with URL: {settings.database_url}")
    
    try:
        # Test async SQLAlchemy connection
        engine = create_async_engine(settings.database_url, echo=True)
        
        # Test connection
        async with engine.begin() as conn:
            print("✓ Async SQLAlchemy connection successful!")
            
            # Check if tables exist
            from sqlalchemy import text
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table';")
            )
            tables = result.fetchall()
            print(f"✓ Found {len(tables)} tables: {[table[0] for table in tables]}")
            
            # Test if request_events table exists and has data
            if any('request_events' in str(table) for table in tables):
                result = await conn.execute(text("SELECT COUNT(*) FROM request_events;"))
                count = result.scalar()
                print(f"✓ request_events table has {count} records")
            else:
                print("⚠ request_events table not found - migrations may be needed")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"✗ SQLite connection failed: {e}")
        return False


def test_sync_sqlite():
    """Test synchronous SQLite connection."""
    
    try:
        # Test direct SQLite connection
        conn = sqlite3.connect('./analytics.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✓ Direct SQLite connection successful! Found tables: {[table[0] for table in tables]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Direct SQLite connection failed: {e}")
        return False


async def main():
    """Run all database tests."""
    
    print("=== Testing Database Configuration ===")
    print(f"Database URL: {settings.database_url}")
    print(f"Environment: {settings.environment}")
    print()
    
    # Test sync SQLite first
    print("1. Testing direct SQLite connection...")
    sync_success = test_sync_sqlite()
    print()
    
    # Test async SQLAlchemy
    print("2. Testing async SQLAlchemy connection...")
    async_success = await test_sqlite_connection()
    print()
    
    if sync_success and async_success:
        print("✅ All database tests passed!")
        return True
    else:
        print("❌ Some database tests failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        exit(1)