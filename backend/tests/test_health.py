"""/health endpoint testi — kabul kriteri ADIM 1."""
from __future__ import annotations

import os

# Test ortamı için minimal env override (Settings yüklerken hata vermesin diye).
os.environ.setdefault("JWT_SECRET", "test-secret-min-32-chars-needed-here")

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_returns_ok():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.1.0"
    assert "uptime_sec" in body


@pytest.mark.asyncio
async def test_health_returns_request_id_header():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert "x-request-id" in {k.lower() for k in response.headers.keys()}
    rid = response.headers.get("x-request-id") or response.headers.get("X-Request-ID")
    assert rid and rid.startswith("req_")


@pytest.mark.asyncio
async def test_health_propagates_incoming_request_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health", headers={"X-Request-ID": "req_test_xyz"})
    assert response.status_code == 200
    rid = response.headers.get("x-request-id") or response.headers.get("X-Request-ID")
    assert rid == "req_test_xyz"
