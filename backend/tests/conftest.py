"""Pytest paylaşılan fixture'lar.

Auth testleri sqlite (aiosqlite) üzerinde koşar — `users` ve `organizations`
tabloları portable tipler kullandığı için yeterli.

DB-yoğun testler (analysis_history JSONB, ARRAY tipleri) `requires_postgres`
ile işaretlenir ve `TEST_DATABASE_URL` set edilmediğinde skip olur.

Live Postgres'le tüm testleri koşmak için:
    set TEST_DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/test
"""
from __future__ import annotations

import os

# Test ortamı için minimal env override.
os.environ.setdefault("JWT_SECRET", "test-secret-min-32-chars-needed-here")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base


def _test_db_url() -> str | None:
    return os.environ.get("TEST_DATABASE_URL")


requires_postgres = pytest.mark.skipif(
    _test_db_url() is None,
    reason="TEST_DATABASE_URL set edilmediği için Postgres testleri atlandı",
)


@pytest_asyncio.fixture
async def pg_engine():
    """Live Postgres engine (analysis/profiles testleri için)."""
    url = _test_db_url()
    if url is None:
        pytest.skip("TEST_DATABASE_URL set değil")
    engine = create_async_engine(url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def pg_db(pg_engine) -> AsyncSession:
    """Live Postgres session."""
    Session = async_sessionmaker(pg_engine, expire_on_commit=False)
    async with Session() as session:
        yield session


@pytest_asyncio.fixture
async def auth_engine():
    """Auth + processors testleri için sqlite — users, orgs, profiles.

    `analysis_history` (JSONB) sqlite'a oturmadığı için hariç tutuldu;
    o tabloyu kullanan testler `requires_postgres` ile işaretlenir.
    """
    from app.db.models.analysis import AnalysisRecord
    from app.db.models.organization import Organization
    from app.db.models.profiles import BuyerProfile, ProcessorProfile, ProducerProfile
    from app.db.models.user import User

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    sqlite_safe_tables = [
        Organization.__table__,
        User.__table__,
        ProducerProfile.__table__,
        ProcessorProfile.__table__,
        BuyerProfile.__table__,
    ]
    # AnalysisRecord JSONB içerdiği için sqlite'da yaratmıyoruz.
    _ = AnalysisRecord
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                sync_conn, tables=sqlite_safe_tables
            )
        )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def auth_session_maker(auth_engine):
    return async_sessionmaker(auth_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def auth_client(auth_session_maker):
    """Test için DB dependency'sini sqlite session'a override eden httpx client."""
    from app.db.session import get_db
    from app.main import app

    async def _override():
        async with auth_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = _override
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def async_client():
    """ASGI üzerinden uygulamayı çağıran httpx client (DB override yok)."""
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
