"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router
from .core.config import settings


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add basic health endpoint (without /api/v1 prefix)
    @app.get("/health")
    async def basic_health():
        """Basic health check endpoint."""
        return {"status": "ok"}

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()

