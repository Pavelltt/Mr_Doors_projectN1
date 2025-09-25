"""Endpoints for querying processed requests."""

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_session
from ...schemas.requests import RequestEventListResponse
from ...services.requests import fetch_request_events


router = APIRouter()


@router.get("", response_model=RequestEventListResponse)
async def list_request_events(
    *,
    session: AsyncSession = Depends(get_session),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    model: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default=None),
    chat_id: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
):
    """List request events with optional filters."""

    result = await fetch_request_events(
        session=session,
        limit=limit,
        offset=offset,
        model=model,
        status_filter=status_filter,
        chat_id=chat_id,
        date_from=date_from,
        date_to=date_to,
    )
    return result

