#!/usr/bin/env python3
"""Migrate data from SQLite to Supabase PostgreSQL."""

import asyncio
import sqlite3
import json
from datetime import datetime

import asyncpg


async def migrate_data():
    """Migrate all data from SQLite to Supabase."""
    
    print("🚀 Starting data migration from SQLite to Supabase...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('analytics.db')
    sqlite_conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = sqlite_conn.cursor()
    
    # Connect to Supabase
    supabase_conn = await asyncpg.connect(
        "postgresql://postgres:MfEhNB3e12sLAUrU@db.tzwkaazqfcalmlsmvyop.supabase.co:5432/postgres",
        statement_cache_size=0
    )
    
    try:
        # Get all records from SQLite
        cursor.execute("SELECT * FROM request_events ORDER BY id")
        records = cursor.fetchall()
        
        print(f"📊 Found {len(records)} records to migrate")
        
        # Clear existing data in Supabase (if any)
        await supabase_conn.execute("DELETE FROM request_events")
        print("🗑️  Cleared existing data in Supabase")
        
        # Migrate records
        migrated_count = 0
        
        for record in records:
            try:
                # Parse JSON fields
                error_payload = json.loads(record['error_payload']) if record['error_payload'] else None
                numbers = json.loads(record['numbers']) if record['numbers'] else None
                raw_prompt = json.loads(record['raw_prompt']) if record['raw_prompt'] else None
                raw_response = json.loads(record['raw_response']) if record['raw_response'] else None
                
                # Convert datetime strings to proper datetime objects
                originated_at = datetime.fromisoformat(record['originated_at'].replace('Z', '+00:00'))
                created_at = datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
                updated_at = datetime.fromisoformat(record['updated_at'].replace('Z', '+00:00')) if record['updated_at'] else None
                
                # Insert into Supabase
                await supabase_conn.execute("""
                    INSERT INTO request_events (
                        request_id, originated_at, chat_id, message_id, tile_id,
                        model, duration_seconds, input_tokens, output_tokens, cost_usd,
                        status, error_payload, numbers, raw_prompt, raw_response,
                        created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                """, 
                    record['request_id'],
                    originated_at,
                    record['chat_id'],
                    record['message_id'],
                    record['tile_id'],
                    record['model'],
                    record['duration_seconds'],
                    record['input_tokens'],
                    record['output_tokens'],
                    record['cost_usd'],
                    record['status'],
                    json.dumps(error_payload) if error_payload else None,
                    json.dumps(numbers) if numbers else None,
                    json.dumps(raw_prompt) if raw_prompt else None,
                    json.dumps(raw_response) if raw_response else None,
                    created_at,
                    updated_at
                )
                
                migrated_count += 1
                
                if migrated_count % 10 == 0:
                    print(f"✅ Migrated {migrated_count}/{len(records)} records...")
                    
            except Exception as e:
                print(f"❌ Failed to migrate record {record['id']}: {e}")
                continue
        
        # Verify migration
        count_result = await supabase_conn.fetchval("SELECT COUNT(*) FROM request_events")
        print("\n🎉 Migration completed!")
        print(f"📊 Successfully migrated {migrated_count} out of {len(records)} records")
        print(f"🔍 Supabase now contains {count_result} records")
        
        # Show sample data
        sample = await supabase_conn.fetch("SELECT request_id, model, status, cost_usd FROM request_events LIMIT 3")
        print("\n📋 Sample migrated data:")
        for row in sample:
            print(f"  - {row['request_id']}: {row['model']} ({row['status']}) - ${row['cost_usd']}")
            
    except Exception as e:
        print(f"💥 Migration failed: {e}")
        raise
    finally:
        # Close connections
        sqlite_conn.close()
        await supabase_conn.close()
        print("🔌 Connections closed")


if __name__ == "__main__":
    asyncio.run(migrate_data())