"""Healthcheck endpoints."""

from typing import Dict

from fastapi import APIRouter

from ...core.config import settings


router = APIRouter()


@router.get("/ready", summary="Readiness probe")
async def readiness() -> Dict[str, str]:
    """Return readiness information."""

    return {"status": "ok", "environment": settings.environment}


@router.get("/live", summary="Liveness probe")
async def liveness() -> Dict[str, str]:
    """Return liveness information."""

    return {"status": "alive"}

