"""Database session management."""

import asyncpg
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..core.config import settings


# Create async engine for PostgreSQL with pgbouncer compatibility
async_engine = create_async_engine(
    settings.build_sqlalchemy_url(), 
    echo=False, 
    pool_pre_ping=False,  # Disable pre-ping for pgbouncer
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "statement_cache_size": 0,
        "server_settings": {
            "application_name": "mr_doors_analytics",
        }
    }
)

SessionLocal = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

# Create asyncpg connection pool for direct database operations
_connection_pool = None

async def get_connection_pool():
    """Get or create asyncpg connection pool."""
    global _connection_pool
    if _connection_pool is None:
        database_url = str(settings.database_url).replace('postgresql+asyncpg://', 'postgresql://')
        _connection_pool = await asyncpg.create_pool(
            database_url,
            statement_cache_size=0,
            min_size=1,
            max_size=10
        )
    return _connection_pool

@asynccontextmanager
async def get_asyncpg_connection():
    """Get asyncpg connection from pool."""
    pool = await get_connection_pool()
    async with pool.acquire() as connection:
        yield connection

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope."""

    async with SessionLocal() as session:
        yield session

