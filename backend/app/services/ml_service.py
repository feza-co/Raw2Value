"""ML servisi — `raw2value_ml.analyze()` çağrısını async-uyumlu sarar.

Pickled CatBoost modelleri eğitim sırasında `ml.src.*` modüllerinden bazı
sınıflara referans verir. Bu yüzden `ml/` paketinin sys.path'te bulunması
zorunlu — backend herhangi bir cwd'den çalışsa da çözülmeli.

Sözleşme: `analyze()` SYNC fonksiyon (~20 ms warm). Event loop'u bloklamamak
için `loop.run_in_executor(None, ...)` ile thread pool'a delege ederiz.

Kaynak:
- MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §18 ADIM 5
- docs/STATUS_REPORT_ML_TESLIM.md §5
"""
from __future__ import annotations

import asyncio
import hashlib
import sys
import time
from pathlib import Path

import structlog

# --- ml/ paketini sys.path'e ekle (pickled modellerin bağımlılığı) ---
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_PROJECT_ROOT = _BACKEND_ROOT.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from raw2value_ml import (  # noqa: E402  (path inject sonrası import)
    AnalyzePayload,
    AnalyzeResponse,
    LiveFx,
)
from raw2value_ml import analyze as _ml_analyze  # noqa: E402

from ..config import settings  # noqa: E402
from ..core.cache import get_redis  # noqa: E402

_logger = structlog.get_logger("ml_service")
_warmup_done: bool = False


def _hash_payload(payload: AnalyzePayload) -> str:
    """Idempotent payload için 16-char sha256 prefix (cache key)."""
    return hashlib.sha256(payload.model_dump_json().encode()).hexdigest()[:16]


async def warmup_ml() -> None:
    """Lifespan startup'ta çağrılır; pickle'ları load eder ve ilk çağrı süresini soğurur."""
    global _warmup_done
    if _warmup_done:
        return
    payload = AnalyzePayload(
        raw_material="pomza",
        tonnage=100,
        quality="A",
        origin_city="Nevşehir",
        target_country="DE",
        target_city="Hamburg",
        transport_mode="kara",
        live_fx=LiveFx(usd_try=45.0, eur_try=52.0, last_updated="2026-05-03"),
    )
    loop = asyncio.get_event_loop()
    t0 = time.perf_counter()
    try:
        await loop.run_in_executor(None, _ml_analyze, payload)
        elapsed = int((time.perf_counter() - t0) * 1000)
        _logger.info("ml_warmup_complete", duration_ms=elapsed)
        _warmup_done = True
    except Exception as exc:  # pragma: no cover  (warmup hata logu)
        _logger.exception("ml_warmup_failed", error=str(exc))
        # Warmup hatası uygulamayı durdurmaz; lazy load denenir.


async def run_analyze(payload: AnalyzePayload) -> AnalyzeResponse:
    """Cache lookup + sync ML çağrısı + cache write."""
    redis = await get_redis()
    cache_key = f"analyze:{_hash_payload(payload)}"
    if settings.ML_RESPONSE_CACHE_TTL_SEC > 0:
        cached_raw = await redis.get(cache_key)
        if cached_raw:
            try:
                return AnalyzeResponse.model_validate_json(cached_raw)
            except Exception:
                _logger.warning("analyze_cache_corrupt_evicting")
                await redis.delete(cache_key)

    loop = asyncio.get_event_loop()
    response: AnalyzeResponse = await loop.run_in_executor(None, _ml_analyze, payload)

    if settings.ML_RESPONSE_CACHE_TTL_SEC > 0:
        await redis.setex(
            cache_key, settings.ML_RESPONSE_CACHE_TTL_SEC, response.model_dump_json()
        )
    return response
