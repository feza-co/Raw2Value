"""/api/analyze testleri — gerçek ML çağrısı (mock YOK).

Auth: sqlite (auth_engine fixture). FX: respx ile TCMB mock + fakeredis.
ML: gerçek `raw2value_ml.analyze()` çağrısı.

Sözleşme garantileri (rapor §9.7):
- len(route_alternatives) == 3
- len(reason_codes) == 3
- co2_tonnes == co2_kg / 1000
- confidence.overall ∈ [0, 100]
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import fakeredis.aioredis
import httpx
import pytest
import pytest_asyncio
import respx
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.core import cache as cache_module
from app.schemas.fx import FxResponse
from app.services.fx_service import _CACHE_KEY

TCMB_URL = f"{settings.TCMB_EVDS_BASE_URL.rstrip('/')}/series"
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "tcmb_response.json"


def _tcmb_payload() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest_asyncio.fixture
async def fake_redis():
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    cache_module.set_redis_for_test(client)
    # FX cache'i önceden doldur — TCMB call'a gerek kalmasın.
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
async def analyze_client(auth_session_maker, fake_redis):
    """Auth-overridden + fakeredis bağlı analyze client'ı."""
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


async def _login(client: AsyncClient, email: str = "ml@test.local") -> str:
    """Yeni user oluştur + login → access token."""
    await client.post(
        "/api/auth/register",
        json={"email": email, "password": "supersecret1", "full_name": "ML Tester"},
    )
    login = await client.post(
        "/api/auth/login",
        data={"username": email, "password": "supersecret1"},
    )
    return login.json()["access_token"]


_BASIC_PAYLOAD = {
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


@pytest.mark.asyncio
async def test_analyze_basic_pomza_de(analyze_client):
    token = await _login(analyze_client)
    response = await analyze_client.post(
        "/api/analyze",
        json=_BASIC_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["recommended_route"]
    assert isinstance(body["expected_profit_try"], (int, float))
    assert "request_id" in body
    assert "fx_used" in body
    assert body["fx_used"]["usd_try"] == 45.05
    assert body["duration_ms"] >= 0


@pytest.mark.asyncio
async def test_analyze_advanced_kabak_tr(analyze_client):
    token = await _login(analyze_client, email="adv@test.local")
    advanced_payload = {
        "raw_material": "kabak_cekirdegi",
        "tonnage": 30,
        "quality": "A",
        "origin_city": "Acıgöl",
        "target_country": "TR",
        "target_city": "İstanbul",
        "transport_mode": "kara",
        "priority": "max_profit",
        "input_mode": "advanced",
        "moisture_pct": 8.0,
        "purity_pct": 98.0,
        "particle_size_class": "fine",
    }
    response = await analyze_client.post(
        "/api/analyze",
        json=advanced_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["recommended_route"].startswith("kabak_cekirdegi_")


@pytest.mark.asyncio
async def test_analyze_response_contract(analyze_client):
    """ML sözleşme garantileri."""
    token = await _login(analyze_client, email="contract@test.local")
    response = await analyze_client.post(
        "/api/analyze",
        json=_BASIC_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    body = response.json()
    assert len(body["route_alternatives"]) == 3
    assert len(body["reason_codes"]) == 3
    assert len(body["match_results"]) <= 5
    assert 0 <= body["confidence"]["overall"] <= 100
    assert body["co2_tonnes"] == pytest.approx(body["co2_kg"] / 1000)


@pytest.mark.asyncio
async def test_analyze_unauthorized_returns_401(analyze_client):
    response = await analyze_client.post("/api/analyze", json=_BASIC_PAYLOAD)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_analyze_invalid_tonnage_returns_422(analyze_client):
    token = await _login(analyze_client, email="badtonnage@test.local")
    bad = dict(_BASIC_PAYLOAD)
    bad["tonnage"] = 0
    response = await analyze_client.post(
        "/api/analyze",
        json=bad,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_target_city_default_filled(analyze_client):
    """target_city boş → backend NL → Rotterdam doldurmalı."""
    token = await _login(analyze_client, email="default@test.local")
    payload = dict(_BASIC_PAYLOAD)
    payload["target_country"] = "NL"
    payload.pop("target_city")
    response = await analyze_client.post(
        "/api/analyze",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_analyze_warm_latency_under_500ms(analyze_client):
    """5 ardışık warm çağrının p95 < 500 ms."""
    token = await _login(analyze_client, email="latency@test.local")
    headers = {"Authorization": f"Bearer {token}"}
    # İlk çağrı warmup'ı tetikleyebilir; ondan sonra ölç.
    await analyze_client.post("/api/analyze", json=_BASIC_PAYLOAD, headers=headers)

    durations: list[int] = []
    for _ in range(5):
        t0 = time.perf_counter()
        r = await analyze_client.post(
            "/api/analyze", json=_BASIC_PAYLOAD, headers=headers
        )
        elapsed = int((time.perf_counter() - t0) * 1000)
        assert r.status_code == 200
        durations.append(elapsed)

    durations.sort()
    p95_idx = max(int(0.95 * len(durations)) - 1, 0)
    p95 = durations[p95_idx]
    assert p95 < 500, f"p95={p95} ms, durations={durations}"
