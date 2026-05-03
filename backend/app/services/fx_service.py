"""FX iş mantığı — Redis cache + TCMB call + fallback.

Cache key: `fx:current` (tek key, global). TTL: TCMB_FX_CACHE_TTL_SEC (5 dk).
TCMB hatası → open.er-api.com (key'siz canlı kaynak) → env fallback.
"""
from __future__ import annotations

from datetime import datetime, timezone

import httpx
import structlog

from ..clients.tcmb import TcmbClient, TcmbError
from ..config import settings
from ..core.cache import get_redis
from ..schemas.fx import FxResponse

_CACHE_KEY = "fx:current"
_OPEN_ER_API_URL = "https://open.er-api.com/v6/latest/USD"
_logger = structlog.get_logger("fx_service")


async def _fetch_open_er_api() -> dict[str, float | str] | None:
    """open.er-api.com — key'siz canlı kur kaynağı (TCMB ulaşılamadığında).

    Returns:
        ``{"usd_try": ..., "eur_try": ..., "last_updated": "YYYY-MM-DD"}``
        veya hata durumunda ``None``.
    """
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(_OPEN_ER_API_URL)
            r.raise_for_status()
            data = r.json()
            if data.get("result") != "success":
                return None
            rates = data.get("rates") or {}
            usd_try = float(rates.get("TRY"))
            usd_eur = float(rates.get("EUR"))
            if usd_try <= 0 or usd_eur <= 0:
                return None
            eur_try = usd_try / usd_eur
            return {
                "usd_try": round(usd_try, 4),
                "eur_try": round(eur_try, 4),
                "last_updated": datetime.now(timezone.utc).date().isoformat(),
            }
    except Exception as exc:  # noqa: BLE001
        _logger.warning("open_er_api_failed", error=str(exc))
        return None


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
            _logger.warning("fx_tcmb_failed_trying_open_er_api", error=str(exc))
            alt = await _fetch_open_er_api()
            if alt is not None:
                response = FxResponse(
                    usd_try=float(alt["usd_try"]),
                    eur_try=float(alt["eur_try"]),
                    last_updated=str(alt["last_updated"]),
                    source="OPEN_ER_API",
                    is_stale=False,
                    fetched_at=datetime.now(timezone.utc),
                )
                _logger.info(
                    "fx_fetched_open_er_api",
                    usd_try=response.usd_try,
                    eur_try=response.eur_try,
                )
            else:
                _logger.warning("fx_fallback_static")
                response = _build_fallback()
    finally:
        if client is None:
            await tcmb.aclose()

    await redis.setex(
        _CACHE_KEY, settings.TCMB_FX_CACHE_TTL_SEC, response.model_dump_json()
    )
    return response
