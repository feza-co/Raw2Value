"""Async SQLAlchemy engine + session factory.

`get_db` dependency FastAPI endpoint'lerine context-managed AsyncSession verir.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..config import settings


def _build_engine(url: str) -> AsyncEngine:
    """Engine factory — sqlite asenkron olduğunda pool param'ları geçersiz."""
    is_sqlite = url.startswith("sqlite")
    kwargs: dict = {"echo": settings.DATABASE_ECHO}
    if not is_sqlite:
        kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
        kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
        kwargs["pool_pre_ping"] = True
    return create_async_engine(url, **kwargs)


engine: AsyncEngine = _build_engine(settings.DATABASE_URL)
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI Depends — request scope'lu AsyncSession verir."""
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
