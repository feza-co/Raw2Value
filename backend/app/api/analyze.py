"""/api/analyze — ana karar endpoint'i.

Akış:
1. Bearer JWT doğrula → User
2. TCMB cache'inden FX al
3. ML payload kur (target_city default ekle)
4. ML async analyze (cache + thread pool)
5. Response gönder; history insert fire-and-forget

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md §9.7,
        MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §18 ADIM 5.
"""
from __future__ import annotations

import asyncio
import time

import structlog
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from raw2value_ml import AnalyzePayload, LiveFx

from ..db.models import User
from ..db.session import SessionLocal, get_db
from ..deps import get_current_user
from ..schemas.analyze import AnalyzeRequest, AnalyzeResponseOut, FxUsed
from ..services.fx_service import get_current_fx
from ..services.history_service import build_record, save_analyze
from ..services.ml_service import run_analyze

router = APIRouter(prefix="/api", tags=["analyze"])
_logger = structlog.get_logger("analyze")

_DEFAULT_TARGET_CITY = {
    "DE": "Hamburg",
    "NL": "Rotterdam",
    "TR": "İstanbul",
}


def _build_ml_payload(
    request: AnalyzeRequest,
    fx_usd_try: float,
    fx_eur_try: float,
    fx_last_updated: str,
) -> AnalyzePayload:
    """`AnalyzeRequest` + `LiveFx` → ML `AnalyzePayload`."""
    target_city = request.target_city or _DEFAULT_TARGET_CITY.get(
        request.target_country
    )
    return AnalyzePayload(
        raw_material=request.raw_material,
        tonnage=request.tonnage,
        quality=request.quality,
        origin_city=request.origin_city,
        target_country=request.target_country,
        target_city=target_city,
        transport_mode=request.transport_mode,
        priority=request.priority,
        input_mode=request.input_mode,
        moisture_pct=request.moisture_pct,
        purity_pct=request.purity_pct,
        particle_size_class=request.particle_size_class,
        fx_scenario_pct=request.fx_scenario_pct,
        cost_scenario_pct=request.cost_scenario_pct,
        live_fx=LiveFx(
            usd_try=fx_usd_try, eur_try=fx_eur_try, last_updated=fx_last_updated
        ),
    )


@router.post(
    "/analyze",
    response_model=AnalyzeResponseOut,
    status_code=status.HTTP_200_OK,
)
async def analyze_endpoint(
    request: Request,
    payload: AnalyzeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponseOut:
    rid = getattr(request.state, "request_id", "unknown")

    fx = await get_current_fx()
    ml_payload = _build_ml_payload(
        payload, fx.usd_try, fx.eur_try, fx.last_updated
    )

    t0 = time.perf_counter()
    response = await run_analyze(ml_payload)
    duration_ms = int((time.perf_counter() - t0) * 1000)

    record = build_record(
        request_id=rid,
        user_id=user.id,
        organization_id=user.organization_id,
        payload=ml_payload,
        response=response,
        fx=fx,
        duration_ms=duration_ms,
    )
    # Fire-and-forget: response gönderildikten sonra DB'ye yazılır.
    asyncio.create_task(save_analyze(SessionLocal, record=record))

    return AnalyzeResponseOut(
        **response.model_dump(),
        request_id=rid,
        fx_used=FxUsed(
            usd_try=fx.usd_try, eur_try=fx.eur_try, last_updated=fx.last_updated
        ),
        duration_ms=duration_ms,
    )
