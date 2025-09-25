"""Tests for ingestion service."""

from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings_for_testing
from app.db.base import Base
from app.models.request_event import RequestEvent, RequestStatus
from app.services.ingestion import ingest_event
from app.schemas.events import IngestionEventCreate


@pytest_asyncio.fixture
async def engine():
    settings = get_settings_for_testing(database_url="sqlite+aiosqlite:///:memory:")
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.mark.asyncio
async def test_ingest_event(session: AsyncSession):
    payload = IngestionEventCreate(
        request_id="123",
        originated_at=datetime.now(timezone.utc),
        model="gpt-4o",
        duration_seconds=1.23,
        input_tokens=100,
        output_tokens=50,
        cost_usd=0.01,
        status="success",
    )

    await ingest_event(session=session, payload=payload)

    result = await session.execute(
        RequestEvent.__table__.select().where(RequestEvent.request_id == "123")
    )
    row = result.fetchone()
    assert row is not None
    assert row.request_id == "123"
    assert row.status == RequestStatus.SUCCESS

