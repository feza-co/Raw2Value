"""Slowapi tabanlı rate limiter — hem genel hem endpoint özel limitler.

`limit(...)` decorator'ı: rate limit kapalıysa fonksiyonu olduğu gibi geri
döndürür (FastAPI annotation introspection'u bozulmasın diye).

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §15.1.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import settings


def _key_func(request) -> str:
    """User-aware key — auth'lı endpoint'lerde user_id, aksi halde IP."""
    auth_user = getattr(getattr(request, "state", None), "user_id", None)
    if auth_user:
        return f"user:{auth_user}"
    return get_remote_address(request)


limiter = Limiter(
    key_func=_key_func,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    storage_uri=settings.REDIS_URL if settings.RATE_LIMIT_ENABLED else "memory://",
    enabled=settings.RATE_LIMIT_ENABLED,
)


def limit(rate: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """`@limit(rate)` — rate limit kapalıysa no-op pass-through."""
    if not settings.RATE_LIMIT_ENABLED:
        def _noop(func: Callable[..., Any]) -> Callable[..., Any]:
            return func

        return _noop
    return limiter.limit(rate)
