#!/usr/bin/env python3
"""Simple test to verify Supabase connection works."""

import asyncio
import asyncpg

async def test_simple_connection():
    """Test basic asyncpg connection to Supabase."""
    
    # Direct connection string (using correct format from .env.example)
    connection_string = "postgresql://postgres:MfEhNB3e12sLAUrU@db.tzwkaazqfcalmlsmvyop.supabase.co:5432/postgres"
    
    try:
        print("Testing direct asyncpg connection...")
        
        # Create connection with disabled prepared statements
        conn = await asyncpg.connect(
            connection_string,
            statement_cache_size=0
        )
        
        # Test basic query
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Connection successful! PostgreSQL version: {version}")
        
        # Test table query
        tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        print(f"✅ Found {len(tables)} tables: {[t['tablename'] for t in tables]}")
        
        await conn.close()
        print("✅ Connection closed successfully")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_simple_connection())
    if success:
        print("\n🎉 Simple connection test passed!")
    else:
        print("\n💥 Simple connection test failed!")