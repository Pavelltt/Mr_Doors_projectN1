"""Schemas for request querying."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class RequestEventResponse(BaseModel):
    """Single request event representation."""

    id: int
    request_id: str
    originated_at: datetime
    chat_id: Optional[str]
    message_id: Optional[int]
    tile_id: Optional[str]
    model: str
    duration_seconds: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    status: str
    numbers: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AggregatedMetrics(BaseModel):
    """Aggregated metrics over the result set."""

    total_requests: int
    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int
    average_latency: Optional[float]


class RequestEventListResponse(BaseModel):
    """Paginated response for request events."""

    items: List[RequestEventResponse]
    total: int
    limit: int
    offset: int
    aggregates: AggregatedMetrics

