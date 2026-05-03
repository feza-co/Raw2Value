"""OpenRouteService client — opsiyonel matrix mesafe hesabı.

Backend MVP'de geo işleri ML paketinin `geo.py` (precomputed lookup +
Haversine fallback) ile çözüyor. ORS sadece opsiyonel: ileride alternatif
rotalar veya şehirler arası gerçek karayolu mesafesi gerekirse devreye girer.

ORS down → caller tarafı `geo.py.haversine_km()` kullanmalı (zaten yapıyor).

Cache key: `ors:matrix:{profile}:{hash(locations)}` TTL 1 saat.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §10.2.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..config import settings
from ..core.cache import get_redis


class OrsError(Exception):
    """ORS çağrısı 3 denemeden sonra başarısız oldu ya da yanıt parse edilemedi."""


def _locations_hash(locations: list[tuple[float, float]]) -> str:
    """Cache key için stabil hash."""
    payload = json.dumps(locations, separators=(",", ":"), sort_keys=False)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


class OrsClient:
    """ORS Matrix API ince sarmalayıcı. Backend kullanımı opsiyonel."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.ORS_API_KEY
        self.base_url = (base_url or settings.ORS_BASE_URL).rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            timeout=timeout if timeout is not None else settings.ORS_TIMEOUT_SEC
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=0.5, max=4),
        retry=retry_if_exception_type((httpx.HTTPError, OrsError)),
        reraise=True,
    )
    async def matrix(
        self,
        locations: list[tuple[float, float]],
        profile: str = "driving-hgv",
        metrics: tuple[str, ...] = ("distance", "duration"),
    ) -> dict[str, Any]:
        """Çoklu nokta için mesafe + süre matrisi.

        Args:
            locations: `[(lon, lat), ...]` — DİKKAT, ORS sırası `(lon, lat)`.
            profile: `driving-hgv`, `driving-car`, vs.
            metrics: `("distance", "duration")` — metre + saniye.

        Returns:
            `{"distances": [[m, m, ...], ...], "durations": [[s, s, ...], ...]}`

        Raises:
            OrsError — API key yok ya da yanıt eksikse.
        """
        if not self.api_key or self.api_key.startswith("your-"):
            raise OrsError("ORS_API_KEY tanımlı değil; geo.py fallback kullanın")
        if not locations or len(locations) < 2:
            raise OrsError("ORS matrix en az 2 lokasyon ister")

        url = f"{self.base_url}/v2/matrix/{profile}"
        body = {
            "locations": [[lon, lat] for (lon, lat) in locations],
            "metrics": list(metrics),
            "units": "m",
        }
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = await self._client.post(url, json=body, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "distances" not in data and "durations" not in data:
            raise OrsError(f"ORS yanıtı beklenmiyor: {list(data.keys())}")
        return {
            "distances": data.get("distances"),
            "durations": data.get("durations"),
        }

    async def matrix_cached(
        self,
        locations: list[tuple[float, float]],
        profile: str = "driving-hgv",
    ) -> dict[str, Any]:
        """Redis cache'li matrix çağrısı (TTL `ORS_DISTANCE_CACHE_TTL_SEC`)."""
        redis = await get_redis()
        cache_key = f"ors:matrix:{profile}:{_locations_hash(locations)}"
        cached = await redis.get(cache_key)
        if cached:
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                await redis.delete(cache_key)

        result = await self.matrix(locations, profile=profile)
        ttl = settings.ORS_DISTANCE_CACHE_TTL_SEC
        if ttl > 0:
            await redis.setex(cache_key, ttl, json.dumps(result))
        return result
