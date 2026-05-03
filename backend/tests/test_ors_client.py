"""ORS client unit testleri (respx + fakeredis)."""
from __future__ import annotations

import httpx
import pytest
import pytest_asyncio
import respx
import fakeredis.aioredis

from app.clients.ors import OrsClient, OrsError, _locations_hash
from app.config import settings
from app.core import cache as cache_module


ORS_URL = f"{settings.ORS_BASE_URL.rstrip('/')}/v2/matrix/driving-hgv"


@pytest_asyncio.fixture
async def fake_redis():
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    cache_module.set_redis_for_test(client)
    yield client
    await client.aclose()
    cache_module.set_redis_for_test(None)


def test_locations_hash_deterministic():
    h1 = _locations_hash([(34.71, 38.62), (10.0, 53.5)])
    h2 = _locations_hash([(34.71, 38.62), (10.0, 53.5)])
    assert h1 == h2
    h3 = _locations_hash([(10.0, 53.5), (34.71, 38.62)])
    assert h1 != h3  # sıra önemli


@pytest.mark.asyncio
async def test_matrix_returns_distances_and_durations():
    client = OrsClient(api_key="test-key", base_url=settings.ORS_BASE_URL)
    payload = {
        "distances": [[0, 2400000], [2400000, 0]],
        "durations": [[0, 86400], [86400, 0]],
    }
    with respx.mock:
        respx.post(ORS_URL).mock(return_value=httpx.Response(200, json=payload))
        result = await client.matrix(
            [(34.71, 38.62), (10.0, 53.5)], profile="driving-hgv"
        )
    assert result["distances"][0][1] == 2400000
    assert result["durations"][0][1] == 86400
    await client.aclose()


@pytest.mark.asyncio
async def test_matrix_raises_when_api_key_placeholder():
    client = OrsClient(api_key="your-ors-key-here")
    with pytest.raises(OrsError, match="ORS_API_KEY"):
        await client.matrix([(34.71, 38.62), (10.0, 53.5)])
    await client.aclose()


@pytest.mark.asyncio
async def test_matrix_raises_when_locations_too_few():
    client = OrsClient(api_key="real-key")
    with pytest.raises(OrsError, match="en az 2"):
        await client.matrix([(34.71, 38.62)])
    await client.aclose()


@pytest.mark.asyncio
async def test_matrix_raises_when_response_missing_keys():
    client = OrsClient(api_key="real-key", base_url=settings.ORS_BASE_URL)
    with respx.mock:
        respx.post(ORS_URL).mock(
            return_value=httpx.Response(200, json={"unexpected": "shape"})
        )
        with pytest.raises(OrsError, match="beklenmiyor"):
            await client.matrix([(34.71, 38.62), (10.0, 53.5)])
    await client.aclose()


@pytest.mark.asyncio
async def test_matrix_cached_hits_redis_on_second_call(fake_redis):
    client = OrsClient(api_key="real-key", base_url=settings.ORS_BASE_URL)
    payload = {
        "distances": [[0, 100000], [100000, 0]],
        "durations": [[0, 3600], [3600, 0]],
    }
    locations = [(34.71, 38.62), (35.0, 39.0)]
    with respx.mock:
        route = respx.post(ORS_URL).mock(
            return_value=httpx.Response(200, json=payload)
        )
        first = await client.matrix_cached(locations)
        second = await client.matrix_cached(locations)
        assert first == second
        # İkinci çağrı cache'ten döndüyse HTTP sayacı sadece 1 kez artar.
        assert route.call_count == 1
    await client.aclose()
