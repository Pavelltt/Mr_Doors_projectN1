"""Application configuration."""

from functools import lru_cache
from typing import Any, List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    project_name: str = "Mr Doors Analytics"
    version: str = "0.1.0"
    environment: str = "development"

    api_v1_prefix: str = "/api/v1"
    docs_url: Optional[str] = "/docs"
    redoc_url: Optional[str] = "/redoc"

    # Database - Direct connection without pooler
    database_url: str = "postgresql+asyncpg://postgres:MfEhNB3e12sLAUrU@db.tzwkaazqfcalmlsmvyop.supabase.co:5432/postgres"
    alembic_database_url: Optional[str] = None

    # Security
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24

    # CORS
    backend_cors_origins: List[str] = ["http://localhost:5173", "http://localhost:5174"]

    # Feature toggles
    enable_metrics: bool = True
    enable_healthchecks: bool = True

    # Telemetry
    log_level: str = "INFO"

    def build_sqlalchemy_url(self) -> str:
        """Return SQLAlchemy URL."""
        return self.database_url

    def build_alembic_url(self) -> str:
        """Return Alembic sync URL."""
        if self.alembic_database_url:
            return self.alembic_database_url
        
        # Convert async URLs to sync for Alembic
        url = self.database_url
        if url.startswith("postgresql+asyncpg://"):
            # Use standard postgresql driver for Alembic migrations
            return url.replace("postgresql+asyncpg://", "postgresql://")
        elif url.startswith("sqlite+aiosqlite://"):
            return url.replace("sqlite+aiosqlite://", "sqlite://")
        else:
            return url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings: Settings = get_settings()


def get_settings_for_testing(**overrides: Any) -> Settings:
    """Get settings instance for testing with overrides."""
    return Settings(**overrides)

