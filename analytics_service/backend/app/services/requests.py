"""Service for request querying."""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.request_event import RequestEvent, RequestStatus
from ..schemas.requests import AggregatedMetrics, RequestEventListResponse
from ..db.session import get_asyncpg_connection


async def fetch_request_events(
    *,
    session: AsyncSession,
    limit: int,
    offset: int,
    model: Optional[str],
    status_filter: Optional[str],
    chat_id: Optional[str],
    date_from: Optional[datetime],
    date_to: Optional[datetime],
) -> RequestEventListResponse:
    """Fetch request events with filters using asyncpg for pgbouncer compatibility."""

    # Build WHERE conditions
    where_conditions = []
    params = []
    param_count = 0

    if model:
        param_count += 1
        where_conditions.append(f"model = ${param_count}")
        params.append(model)
    
    if status_filter:
        param_count += 1
        where_conditions.append(f"status = ${param_count}")
        params.append(status_filter)
    
    if chat_id:
        param_count += 1
        where_conditions.append(f"chat_id = ${param_count}")
        params.append(chat_id)
    
    if date_from:
        param_count += 1
        where_conditions.append(f"originated_at >= ${param_count}")
        params.append(date_from)
    
    if date_to:
        param_count += 1
        where_conditions.append(f"originated_at <= ${param_count}")
        params.append(date_to)

    where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""

    async with get_asyncpg_connection() as conn:
        # Get total count
        count_query = f"SELECT COUNT(*) FROM request_events{where_clause}"
        total = await conn.fetchval(count_query, *params)

        # Get items
        items_query = f"""
            SELECT id, request_id, originated_at, chat_id, message_id, tile_id,
                   model, duration_seconds, input_tokens, output_tokens, cost_usd,
                   status, error_payload, numbers, raw_prompt, raw_response,
                   created_at, updated_at
            FROM request_events{where_clause}
            ORDER BY originated_at DESC
            LIMIT ${param_count + 1} OFFSET ${param_count + 2}
        """
        
        items_params = params + [limit, offset]
        rows = await conn.fetch(items_query, *items_params)
        
        # Convert rows to RequestEvent objects
        items = []
        for row in rows:
            item = RequestEvent(
                id=row['id'],
                request_id=row['request_id'],
                originated_at=row['originated_at'],
                chat_id=row['chat_id'],
                message_id=row['message_id'],
                tile_id=row['tile_id'],
                model=row['model'],
                duration_seconds=row['duration_seconds'],
                input_tokens=row['input_tokens'],
                output_tokens=row['output_tokens'],
                cost_usd=row['cost_usd'],
                status=RequestStatus(row['status']),
                error_payload=row['error_payload'],
                numbers=row['numbers'],
                raw_prompt=row['raw_prompt'],
                raw_response=row['raw_response'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            items.append(item)

        # Get aggregates
        agg_query = f"""
            SELECT COUNT(id),
                   COALESCE(SUM(cost_usd), 0.0),
                   COALESCE(SUM(input_tokens), 0),
                   COALESCE(SUM(output_tokens), 0),
                   COALESCE(AVG(duration_seconds), 0.0)
            FROM request_events{where_clause}
        """
        
        agg_row = await conn.fetchrow(agg_query, *params)

        aggregates = AggregatedMetrics(
            total_requests=agg_row[0],
            total_cost_usd=float(agg_row[1]),
            total_input_tokens=int(agg_row[2]),
            total_output_tokens=int(agg_row[3]),
            average_latency=float(agg_row[4]) if agg_row[4] is not None else None,
        )

        return RequestEventListResponse(
            items=items,
            total=int(total or 0),
            limit=limit,
            offset=offset,
            aggregates=aggregates,
        )

