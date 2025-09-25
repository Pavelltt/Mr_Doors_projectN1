#!/usr/bin/env python3
"""Migrate data from SQLite to Supabase via API endpoints."""

import sqlite3
import json
import httpx
from datetime import datetime


def migrate_data_via_api():
    """Migrate all data from SQLite to Supabase using API endpoints."""
    
    print("🚀 Starting data migration from SQLite to Supabase via API...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('analytics.db')
    sqlite_conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = sqlite_conn.cursor()
    
    try:
        # Get all records from SQLite
        cursor.execute("SELECT * FROM request_events ORDER BY id")
        records = cursor.fetchall()
        
        print(f"📊 Found {len(records)} records to migrate")
        
        # Migrate records via API
        migrated_count = 0
        failed_count = 0
        
        with httpx.Client(timeout=30.0) as client:
            for record in records:
                try:
                    # Parse JSON fields
                    numbers = json.loads(record['numbers']) if record['numbers'] else None
                    
                    # Convert datetime string to ISO format
                    originated_at = datetime.fromisoformat(record['originated_at'].replace('Z', '+00:00'))
                    
                    # Prepare payload for ingestion API
                    payload = {
                        "request_id": record['request_id'],
                        "originated_at": originated_at.isoformat(),
                        "chat_id": record['chat_id'],
                        "message_id": record['message_id'],
                        "tile_id": record['tile_id'],
                        "model": record['model'],
                        "duration_seconds": record['duration_seconds'],
                        "input_tokens": record['input_tokens'],
                        "output_tokens": record['output_tokens'],
                        "cost_usd": record['cost_usd'],
                        "status": record['status'].lower(),  # API expects lowercase
                        "numbers": numbers
                    }
                    
                    # Send to ingestion API
                    response = client.post(
                        "http://localhost:8000/api/v1/ingestion/events",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        migrated_count += 1
                        if migrated_count % 10 == 0:
                            print(f"✅ Migrated {migrated_count}/{len(records)} records...")
                    else:
                        print(f"❌ Failed to migrate record {record['id']}: HTTP {response.status_code} - {response.text}")
                        failed_count += 1
                        
                except Exception as e:
                    print(f"❌ Failed to migrate record {record['id']}: {e}")
                    failed_count += 1
                    continue
        
        print("\n🎉 Migration completed!")
        print(f"✅ Successfully migrated: {migrated_count}")
        print(f"❌ Failed migrations: {failed_count}")
        print(f"📊 Total records: {len(records)}")
        
        # Verify migration by checking API
        try:
            response = client.get("http://localhost:8000/api/v1/requests?limit=1")
            if response.status_code == 200:
                data = response.json()
                print(f"🔍 API verification: {data['total']} records in Supabase")
            else:
                print(f"⚠️  Could not verify migration: HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️  Could not verify migration: {e}")
            
    except Exception as e:
        print(f"💥 Migration failed: {e}")
        raise
    finally:
        # Close SQLite connection
        sqlite_conn.close()
        print("🔌 SQLite connection closed")


if __name__ == "__main__":
    migrate_data_via_api()