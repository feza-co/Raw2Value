"""Async Redis client singleton + helper.

Production: gerçek Redis (REDIS_URL).
Test: `tests.conftest` `fake_redis` fixture'ı ile override edilir.
"""
from __future__ import annotations

import redis.asyncio as redis_asyncio

from ..config import settings

_client: redis_asyncio.Redis | None = None


async def get_redis() -> redis_asyncio.Redis:
    """Lazy-init async Redis client. İlk çağrıda pool oluşturur."""
    global _client
    if _client is None:
        _client = redis_asyncio.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_POOL_SIZE,
            decode_responses=True,
            health_check_interval=30,
        )
    return _client


async def close_redis() -> None:
    """Lifespan shutdown'ta çağrılır."""
    global _client
    if _client is not None:
        try:
            await _client.aclose()
        finally:
            _client = None


def set_redis_for_test(client) -> None:
    """Pytest fixture'larından çağrılır — global'ı set eder."""
    global _client
    _client = client
