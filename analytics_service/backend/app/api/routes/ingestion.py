"""Routes for ingesting analytics events."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_session
from ...schemas.events import IngestionEventCreate
from ...services.ingestion import ingest_event


router = APIRouter()


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event_endpoint(
    payload: IngestionEventCreate,
    session: AsyncSession = Depends(get_session),
):
    """Ingest a single analytics event."""

    await ingest_event(session=session, payload=payload)
    return {"status": "accepted"}

