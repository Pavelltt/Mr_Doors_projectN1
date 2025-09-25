#!/usr/bin/env python3
"""Test Supabase PostgreSQL connection."""

import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

async def test_supabase_connection():
    """Test connection to Supabase PostgreSQL database."""
    print("Testing Supabase PostgreSQL connection...")
    print(f"Database URL: {settings.database_url}")
    
    try:
        # Test async connection with SQLAlchemy
        engine = create_async_engine(settings.database_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # Test basic connection
            result = await session.execute(text("SELECT version();"))
            version = result.scalar()
            print("✅ Async SQLAlchemy connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # Test table listing
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            print(f"📋 Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
                
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Async SQLAlchemy connection failed: {e}")
        return False
    
    try:
        # Test sync connection for Alembic
        sync_url = settings.build_alembic_url()
        print(f"Testing sync connection for Alembic: {sync_url}")
        
        # Use psycopg2-binary instead of psycopg2
        try:
            import psycopg2  # noqa: F401
            
            sync_engine = create_engine(sync_url)
            with sync_engine.connect() as conn:
                result = conn.execute(text("SELECT current_database();"))
                db_name = result.scalar()
                print("✅ Sync connection successful!")
                print(f"Current database: {db_name}")
                
            sync_engine.dispose()
            
        except ImportError:
            print("⚠️ psycopg2 not available, skipping sync connection test")
            return True  # Skip this test but don't fail
        
    except Exception as e:
        print(f"❌ Sync connection failed: {e}")
        return False
    
    print("\n🎉 All Supabase connection tests passed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_supabase_connection())