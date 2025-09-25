"""Schemas for ingestion events."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, List, Dict

from pydantic import BaseModel, Field


class IngestionEventCreate(BaseModel):
    """Schema for incoming analytics event."""

    request_id: str = Field(..., max_length=128)
    originated_at: datetime

    chat_id: Optional[str] = Field(default=None, max_length=64)
    message_id: Optional[int] = None
    tile_id: Optional[str] = Field(default=None, max_length=64)

    model: str
    duration_seconds: float = Field(..., ge=0)
    input_tokens: int = Field(..., ge=0)
    output_tokens: int = Field(..., ge=0)
    cost_usd: float = Field(..., ge=0)

    status: str = Field(..., pattern=r"^(success|error|partial)$")
    error_payload: Optional[Dict[str, Any]] = None

    numbers: Optional[List[str]] = None
    raw_prompt: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None

