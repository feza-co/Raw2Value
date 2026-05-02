"""/api/what-if testleri — paralel senaryolar gerçek ML çağrısıyla."""
from __future__ import annotations

from datetime import datetime, timezone

import fakeredis.aioredis
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core import cache as cache_module
from app.schemas.fx import FxResponse
from app.services.fx_service import _CACHE_KEY


@pytest_asyncio.fixture
async def fake_redis():
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    cache_module.set_redis_for_test(client)
    fx = FxResponse(
        usd_try=45.05,
        eur_try=52.67,
        last_updated="2026-05-02",
        source="TCMB_EVDS",
        is_stale=False,
        fetched_at=datetime.now(timezone.utc),
    )
    await client.setex(_CACHE_KEY, 300, fx.model_dump_json())
    yield client
    await client.aclose()
    cache_module.set_redis_for_test(None)


@pytest_asyncio.fixture
async def whatif_client(auth_session_maker, fake_redis):
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


_BASE = {
    "raw_material": "pomza",
    "tonnage": 150,
    "quality": "A",
    "origin_city": "Nevşehir",
    "target_country": "DE",
    "target_city": "Hamburg",
    "transport_mode": "kara",
    "priority": "max_profit",
    "input_mode": "basic",
}


async def _token(client: AsyncClient, email: str = "wi@test.local") -> str:
    await client.post(
        "/api/auth/register",
        json={"email": email, "password": "supersecret1"},
    )
    r = await client.post(
        "/api/auth/login",
        data={"username": email, "password": "supersecret1"},
    )
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_whatif_three_fx_scenarios(whatif_client):
    token = await _token(whatif_client)
    response = await whatif_client.post(
        "/api/what-if",
        json={
            "base_payload": _BASE,
            "scenarios": [
                {"name": "kur_dusuk", "fx_scenario_pct": -0.10},
                {"name": "kur_normal", "fx_scenario_pct": 0.0},
                {"name": "kur_yuksek", "fx_scenario_pct": 0.10},
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["results"]) == 3
    names = [r["scenario"] for r in body["results"]]
    assert names == ["kur_dusuk", "kur_normal", "kur_yuksek"]


@pytest.mark.asyncio
async def test_whatif_too_many_scenarios_returns_422(whatif_client):
    token = await _token(whatif_client, email="too@test.local")
    big = [
        {"name": f"s{i}", "fx_scenario_pct": 0.0}
        for i in range(11)
    ]
    response = await whatif_client.post(
        "/api/what-if",
        json={"base_payload": _BASE, "scenarios": big},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_whatif_unauthorized(whatif_client):
    response = await whatif_client.post(
        "/api/what-if",
        json={"base_payload": _BASE, "scenarios": [{"name": "a"}]},
    )
    assert response.status_code == 401
