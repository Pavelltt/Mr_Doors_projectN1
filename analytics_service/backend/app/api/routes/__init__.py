"""API routers aggregation."""

from fastapi import APIRouter

from .health import router as health_router
from .ingestion import router as ingestion_router
from .requests import router as requests_router


router = APIRouter()

router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(ingestion_router, prefix="/ingestion", tags=["ingestion"])
router.include_router(requests_router, prefix="/requests", tags=["requests"])

