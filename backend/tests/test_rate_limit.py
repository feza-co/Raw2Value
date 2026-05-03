"""Rate limit testleri.

`conftest.py` test ortamında `RATE_LIMIT_ENABLED=false` set ettiği için
production decorator'ları no-op'lanmış durumda. Yine de:

1. `_key_func` user-aware mantığı pure logic — test edilebilir.
2. `_rate_limit_handler` response formatı (Problem Details / RFC 7807) — kritik.
3. Bağımsız bir `Limiter` instance ile gerçek 429 davranışı doğrulanır
   (memory:// storage, izole; global state'i etkilemez).
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


# ============ _key_func ============


def test_key_func_returns_user_id_when_authenticated():
    from app.core.rate_limit import _key_func

    fake_request = SimpleNamespace(
        state=SimpleNamespace(user_id="u-123"),
        client=SimpleNamespace(host="1.2.3.4"),
        headers={},
    )
    assert _key_func(fake_request) == "user:u-123"


def test_key_func_falls_back_to_ip_when_anonymous():
    from app.core.rate_limit import _key_func

    fake_request = SimpleNamespace(
        state=SimpleNamespace(),
        client=SimpleNamespace(host="9.8.7.6"),
        headers={},
    )
    key = _key_func(fake_request)
    # get_remote_address: state.user_id yoksa client.host döner
    assert key == "9.8.7.6"


# ============ limit() decorator no-op davranışı (test env) ============


def test_limit_decorator_is_noop_when_disabled():
    """Test ortamında RATE_LIMIT_ENABLED=false → decorator pass-through."""
    from app.core.rate_limit import limit

    @limit("1/minute")
    def fn() -> str:
        return "ok"

    # 5 kez çağrı, hiçbiri patlamamalı
    for _ in range(5):
        assert fn() == "ok"


# ============ Problem Details handler ============


def test_rate_limit_handler_emits_problem_details():
    """RateLimitExceeded → 429 + RFC 7807 JSON."""
    from app.exceptions import _problem_details

    fake_request = SimpleNamespace(
        url=SimpleNamespace(path="/api/analyze"),
        state=SimpleNamespace(request_id="req_abc123"),
    )
    response = _problem_details(
        request=fake_request,
        status_code=429,
        code="rate_limited",
        title="Too Many Requests",
        detail="Rate limit exceeded: 30 per 1 minute",
    )
    assert response.status_code == 429
    body = response.body.decode()
    assert "rate_limited" in body
    assert "Too Many Requests" in body


# ============ İzole Limiter ile gerçek 429 ============


@pytest.fixture
def isolated_limited_app():
    """Bağımsız FastAPI + memory:// Limiter ile gerçek rate limit."""
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[],
        storage_uri="memory://",
        enabled=True,
    )
    app = FastAPI()
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    async def _handler(request: Request, exc: RateLimitExceeded):
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=429,
            content={
                "code": "rate_limited",
                "detail": str(exc.detail) if exc.detail else "rate exceeded",
            },
        )

    app.add_exception_handler(RateLimitExceeded, _handler)

    @app.get("/limited")
    @limiter.limit("3/minute")
    async def limited_endpoint(request: Request):
        return {"ok": True}

    return app


def test_isolated_limiter_returns_429_after_exceeding(isolated_limited_app):
    client = TestClient(isolated_limited_app)
    statuses = [client.get("/limited").status_code for _ in range(5)]
    # İlk 3'ü 200, sonraki 2'si 429
    assert statuses[:3] == [200, 200, 200]
    assert 429 in statuses[3:]


def test_isolated_limiter_429_body_has_rate_limited_code(isolated_limited_app):
    client = TestClient(isolated_limited_app)
    for _ in range(3):
        client.get("/limited")
    response = client.get("/limited")
    assert response.status_code == 429
    assert response.json()["code"] == "rate_limited"


# ============ Limiter konfig ============


def test_limiter_module_loads_with_test_config():
    """`limiter` module-level singleton düzgün init oluyor mu."""
    from app.core.rate_limit import limiter

    assert limiter is not None
    # Test ortamında RATE_LIMIT_ENABLED=false → memory storage
    assert limiter.enabled is False or "memory" in str(limiter._storage_uri)
