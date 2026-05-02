"""FX iş mantığı — Redis cache + TCMB call + fallback.

Cache key: `fx:current` (tek key, global). TTL: TCMB_FX_CACHE_TTL_SEC (5 dk).
TCMB hatası → settings.TCMB_FALLBACK_USD_TRY/EUR_TRY ile is_stale=true response.
"""
from __future__ import annotations

from datetime import datetime, timezone

import structlog

from ..clients.tcmb import TcmbClient, TcmbError
from ..config import settings
from ..core.cache import get_redis
from ..schemas.fx import FxResponse

_CACHE_KEY = "fx:current"
_logger = structlog.get_logger("fx_service")


def _build_fallback() -> FxResponse:
    """TCMB erişilemezse env'den son bilinen kuru kullan."""
    return FxResponse(
        usd_try=settings.TCMB_FALLBACK_USD_TRY,
        eur_try=settings.TCMB_FALLBACK_EUR_TRY,
        last_updated=datetime.now(timezone.utc).date().isoformat(),
        source="FALLBACK",
        is_stale=True,
        fetched_at=datetime.now(timezone.utc),
    )


async def get_current_fx(*, client: TcmbClient | None = None) -> FxResponse:
    """`/api/fx/current` ana iş mantığı.

    1. Redis cache'i kontrol et.
    2. Miss ise TCMB EVDS'den çek.
    3. TCMB başarısız ise fallback kullan ve cache'e yine de yaz (stale flag).
    """
    redis = await get_redis()
    cached_raw = await redis.get(_CACHE_KEY)
    if cached_raw:
        try:
            return FxResponse.model_validate_json(cached_raw)
        except Exception:
            _logger.warning("fx_cache_corrupt_evicting")
            await redis.delete(_CACHE_KEY)

    tcmb = client or TcmbClient()
    try:
        try:
            data = await tcmb.get_fx()
            response = FxResponse(
                usd_try=data["usd_try"],
                eur_try=data["eur_try"],
                last_updated=data["last_updated"],
                source="TCMB_EVDS",
                is_stale=False,
                fetched_at=datetime.now(timezone.utc),
            )
            _logger.info(
                "fx_fetched", usd_try=response.usd_try, eur_try=response.eur_try
            )
        except (TcmbError, Exception) as exc:
            _logger.warning("fx_fallback", error=str(exc))
            response = _build_fallback()
    finally:
        if client is None:
            await tcmb.aclose()

    await redis.setex(
        _CACHE_KEY, settings.TCMB_FX_CACHE_TTL_SEC, response.model_dump_json()
    )
    return response
