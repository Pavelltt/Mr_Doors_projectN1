import asyncio
import asyncpg

async def test_connection():
    # Try transaction mode pooler on port 6543
    transaction_url = 'postgresql://postgres.tzwkaazqfcalmlsmvyop:L-3djzkBOfbH9VNhQ-LN2tHQen4fRaylcoe0upHH0Vs@aws-0-eu-central-1.pooler.supabase.com:6543/postgres'
    
    try:
        print("Testing transaction mode pooler connection (port 6543)...")
        conn = await asyncpg.connect(transaction_url)
        print("Transaction mode pooler connection successful!")
        await conn.close()
        return True
    except Exception as e:
        print(f"Transaction mode pooler connection failed: {e}")
    
    # Try session mode pooler on port 5432
    session_url = 'postgresql://postgres.tzwkaazqfcalmlsmvyop:L-3djzkBOfbH9VNhQ-LN2tHQen4fRaylcoe0upHH0Vs@aws-0-eu-central-1.pooler.supabase.com:5432/postgres'
    
    try:
        print("Testing session mode pooler connection (port 5432)...")
        conn = await asyncpg.connect(session_url)
        print("Session mode pooler connection successful!")
        await conn.close()
        return True
    except Exception as e:
        print(f"Session mode pooler connection failed: {e}")
    
    # Try direct connection as fallback
    direct_url = 'postgresql://postgres:L-3djzkBOfbH9VNhQ-LN2tHQen4fRaylcoe0upHH0Vs@db.tzwkaazqfcalmlsmvyop.supabase.co:5432/postgres'
    
    try:
        print("Testing direct connection...")
        conn = await asyncpg.connect(direct_url)
        print("Direct connection successful!")
        await conn.close()
        return True
    except Exception as e:
        print(f"Direct connection failed: {e}")
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if not success:
        print("All connection attempts failed!")
        exit(1)
