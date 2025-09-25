"""Tests for request querying service."""

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings_for_testing
from app.db.base import Base
from app.models.request_event import RequestEvent, RequestStatus
from app.schemas.requests import RequestEventListResponse
from app.services.requests import fetch_request_events


@pytest_asyncio.fixture
async def setup_db():
    settings = get_settings_for_testing(database_url="sqlite+aiosqlite:///:memory:")
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield engine, async_session
    await engine.dispose()


@pytest.mark.asyncio
async def test_fetch_request_events(setup_db):
    engine, async_session = setup_db
    async with async_session() as session:
        now = datetime.now(timezone.utc)
        for i in range(3):
            event = RequestEvent(
                request_id=f"req-{i}",
                originated_at=now - timedelta(minutes=i),
                model="gpt-4o",
                duration_seconds=1.0 + i,
                input_tokens=100 + i,
                output_tokens=50 + i,
                cost_usd=0.01 * (i + 1),
                status=RequestStatus.SUCCESS,
            )
            session.add(event)
        await session.commit()

    async with async_session() as session:
        response = await fetch_request_events(
            session=session,
            limit=10,
            offset=0,
            model="gpt-4o",
            status_filter="success",
            chat_id=None,
            date_from=None,
            date_to=None,
        )

    assert isinstance(response, RequestEventListResponse)
    assert response.total == 3
    assert response.aggregates.total_cost_usd > 0

