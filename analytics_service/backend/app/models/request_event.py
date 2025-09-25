"""Request event model."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, List, Dict

from sqlalchemy import JSON, BigInteger, DateTime, Enum as SqlEnum, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.sqlite import JSON as SqliteJSON
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class RequestStatus(str, Enum):
    """Possible request statuses."""

    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class RequestEvent(Base):
    """Analytics record for bot request."""

    __tablename__ = "request_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    originated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    chat_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    tile_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    model: Mapped[str] = mapped_column(String(64), nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[RequestStatus] = mapped_column(SqlEnum(RequestStatus, name="request_status"), nullable=False)
    error_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql").with_variant(SqliteJSON, "sqlite"), nullable=True
    )

    numbers: Mapped[Optional[List[str]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql").with_variant(SqliteJSON, "sqlite"), nullable=True
    )
    raw_prompt: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql").with_variant(SqliteJSON, "sqlite"), nullable=True
    )
    raw_response: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql").with_variant(SqliteJSON, "sqlite"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

