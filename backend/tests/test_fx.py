"""FX servisi ve `/api/fx/current` testleri.

- TCMB fakeredis ile cache lookup
- respx ile TCMB EVDS HTTP mock
- TCMB fail → fallback davranışı
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import fakeredis.aioredis
import httpx
import pytest
import pytest_asyncio
import respx

from app.clients.tcmb import TcmbClient
from app.config import settings
from app.core import cache as cache_module
from app.schemas.fx import FxResponse
from app.services.fx_service import _CACHE_KEY, get_current_fx

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "tcmb_response.json"
TCMB_URL = f"{settings.TCMB_EVDS_BASE_URL.rstrip('/')}/series"


@pytest_asyncio.fixture
async def fake_redis():
    """Test başına izole fakeredis client; modül singleton'ını override eder."""
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    cache_module.set_redis_for_test(client)
    yield client
    await client.aclose()
    cache_module.set_redis_for_test(None)


def _tcmb_payload() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.mark.asyncio
async def test_fx_cache_hit(fake_redis):
    """Cache'te değer varsa TCMB çağrısı YAPILMAMALI."""
    pre_cached = FxResponse(
        usd_try=44.10,
        eur_try=51.50,
        last_updated="01-05-2026",
        source="TCMB_EVDS",
        is_stale=False,
        fetched_at=datetime.now(timezone.utc),
    )
    await fake_redis.setex(_CACHE_KEY, 60, pre_cached.model_dump_json())

    with respx.mock(assert_all_called=False) as router:
        evds = router.get(TCMB_URL).mock(
            return_value=httpx.Response(500, json={"error": "should_not_be_called"})
        )
        result = await get_current_fx()

    assert result.usd_try == 44.10
    assert result.eur_try == 51.50
    assert evds.call_count == 0


@pytest.mark.asyncio
async def test_fx_cache_miss_calls_tcmb(fake_redis):
    """Cache miss → TCMB çağrılır, sonuç cache'lenir."""
    with respx.mock() as router:
        router.get(TCMB_URL).mock(return_value=httpx.Response(200, json=_tcmb_payload()))
        result = await get_current_fx()

    assert result.source == "TCMB_EVDS"
    assert result.is_stale is False
    assert result.usd_try == 45.05
    assert result.eur_try == 52.67
    cached_raw = await fake_redis.get(_CACHE_KEY)
    assert cached_raw is not None
    cached = FxResponse.model_validate_json(cached_raw)
    assert cached.usd_try == 45.05


@pytest.mark.asyncio
async def test_fx_tcmb_down_returns_fallback(fake_redis):
    """TCMB 3 deneme sonra fail ederse fallback kullanılmalı + is_stale."""
    with respx.mock() as router:
        router.get(TCMB_URL).mock(return_value=httpx.Response(500, json={"error": "down"}))
        result = await get_current_fx()

    assert result.source == "FALLBACK"
    assert result.is_stale is True
    assert result.usd_try == settings.TCMB_FALLBACK_USD_TRY
    assert result.eur_try == settings.TCMB_FALLBACK_EUR_TRY


@pytest.mark.asyncio
async def test_fx_tcmb_empty_items_falls_back(fake_redis):
    """`items` boş gelirse de fallback'a düşmeli."""
    with respx.mock() as router:
        router.get(TCMB_URL).mock(return_value=httpx.Response(200, json={"items": []}))
        result = await get_current_fx()

    assert result.source == "FALLBACK"
    assert result.is_stale is True


@pytest.mark.asyncio
async def test_fx_response_shape(fake_redis):
    """Response shape /api/fx/current sözleşmesini karşılamalı."""
    with respx.mock() as router:
        router.get(TCMB_URL).mock(return_value=httpx.Response(200, json=_tcmb_payload()))
        result = await get_current_fx()

    body = result.model_dump()
    assert {"usd_try", "eur_try", "last_updated", "source", "is_stale", "fetched_at"} <= set(body)


@pytest.mark.asyncio
async def test_tcmb_client_skips_holiday_rows():
    """Tatil/null günleri atlayıp en yeni geçerli satırı almalı."""
    async with httpx.AsyncClient() as inner:
        client = TcmbClient(api_key="dummy", client=inner)
        with respx.mock() as router:
            router.get(TCMB_URL).mock(return_value=httpx.Response(200, json=_tcmb_payload()))
            data = await client.get_fx()
    assert data["usd_try"] == 45.05
    assert data["eur_try"] == 52.67
    assert data["last_updated"] == "03-05-2026"


@pytest.mark.asyncio
async def test_fx_endpoint_returns_200(fake_redis, async_client):
    """Public endpoint smoke testi (TCMB mock'lu)."""
    with respx.mock() as router:
        router.get(TCMB_URL).mock(return_value=httpx.Response(200, json=_tcmb_payload()))
        response = await async_client.get("/api/fx/current")
    assert response.status_code == 200
    body = response.json()
    assert body["usd_try"] == 45.05
    assert body["source"] == "TCMB_EVDS"
