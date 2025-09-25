"""Ingestion service logic."""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.events import IngestionEventCreate
from ..db.session import get_asyncpg_connection


async def ingest_event(*, session: AsyncSession, payload: IngestionEventCreate) -> None:
    """Persist an ingestion event using asyncpg for pgbouncer compatibility."""

    data = payload.model_dump()
    status_value = data.pop("status")
    
    # Use asyncpg directly to avoid prepared statement issues
    async with get_asyncpg_connection() as conn:
        # Check if record exists
        existing_id = await conn.fetchval(
            "SELECT id FROM request_events WHERE request_id = $1",
            payload.request_id
        )
        
        timestamp = datetime.now(timezone.utc)
        
        if existing_id:
            # Update existing record
            await conn.execute("""
                UPDATE request_events 
                SET originated_at = $2, model = $3, duration_seconds = $4, 
                    input_tokens = $5, output_tokens = $6, cost_usd = $7, 
                    status = $8, chat_id = $9, message_id = $10, tile_id = $11,
                    error_payload = $12, numbers = $13, raw_prompt = $14, 
                    raw_response = $15, updated_at = $16
                WHERE request_id = $1
            """,
                payload.request_id,
                data.get('originated_at'),
                data.get('model'),
                data.get('duration_seconds'),
                data.get('input_tokens'),
                data.get('output_tokens'),
                data.get('cost_usd'),
                status_value,
                data.get('chat_id'),
                data.get('message_id'),
                data.get('tile_id'),
                data.get('error_payload'),
                data.get('numbers'),
                data.get('raw_prompt'),
                data.get('raw_response'),
                timestamp
            )
        else:
            # Insert new record
            await conn.execute("""
                INSERT INTO request_events (
                    request_id, originated_at, model, duration_seconds,
                    input_tokens, output_tokens, cost_usd, status,
                    chat_id, message_id, tile_id, error_payload,
                    numbers, raw_prompt, raw_response, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $16)
            """,
                payload.request_id,
                data.get('originated_at'),
                data.get('model'),
                data.get('duration_seconds'),
                data.get('input_tokens'),
                data.get('output_tokens'),
                data.get('cost_usd'),
                status_value,
                data.get('chat_id'),
                data.get('message_id'),
                data.get('tile_id'),
                data.get('error_payload'),
                data.get('numbers'),
                data.get('raw_prompt'),
                data.get('raw_response'),
                timestamp
            )

