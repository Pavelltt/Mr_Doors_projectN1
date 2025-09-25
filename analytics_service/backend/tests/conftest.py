"""Pytest configuration for analytics backend tests."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest


@pytest.fixture(scope="session")
def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, Any]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

