"""Pytest paylaşılan fixture'lar.

Postgres-only tipler (UUID, ARRAY, JSONB) SQLite'da bulunmadığı için
DB-bağımlı testler `requires_postgres` ile işaretlenmiş ve
`TEST_DATABASE_URL` env değeri verilmediğinde otomatik skip edilir.

Live Postgres'le test koşmak için:
    set TEST_DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/test
    pytest backend/tests/
"""
from __future__ import annotations

import os

# Test ortamı için minimal env override (Settings instantiation hatasını önler).
os.environ.setdefault("JWT_SECRET", "test-secret-min-32-chars-needed-here")
os.environ.setdefault("APP_ENV", "test")

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
async def test_engine():
    """Test ömürlü async engine. Sadece TEST_DATABASE_URL ile aktif."""
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
async def test_db(test_engine) -> AsyncSession:
    """Transaction-rolled-back AsyncSession (her test taze)."""
    Session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with Session() as session:
        yield session


@pytest_asyncio.fixture
async def async_client():
    """ASGI üzerinden uygulamayı çağıran httpx client."""
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
