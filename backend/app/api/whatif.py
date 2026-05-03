"""/api/what-if — base payload + senaryolar paralel çalışır."""

import asyncio
import time

from fastapi import APIRouter, Depends

from raw2value_ml import AnalyzePayload, LiveFx

from ..db.models import User
from ..deps import get_current_user
from ..schemas.analyze import (
    AnalyzeRequest,
    FxUsed,
    WhatIfRequest,
    WhatIfResponse,
    WhatIfResultRow,
    WhatIfScenario,
)
from ..services.fx_service import get_current_fx
from ..services.ml_service import run_analyze
from .analyze import _DEFAULT_TARGET_CITY

router = APIRouter(prefix="/api", tags=["analyze"])


def _apply_scenario(base: AnalyzeRequest, scn: WhatIfScenario) -> AnalyzeRequest:
    """Senaryo override'larını base payload'a uygula."""
    return base.model_copy(
        update={
            "fx_scenario_pct": (
                scn.fx_scenario_pct
                if scn.fx_scenario_pct is not None
                else base.fx_scenario_pct
            ),
            "tonnage": (
                scn.tonnage_override
                if scn.tonnage_override is not None
                else base.tonnage
            ),
            "transport_mode": (
                scn.transport_mode_override
                if scn.transport_mode_override is not None
                else base.transport_mode
            ),
        }
    )


def _to_ml_payload(req: AnalyzeRequest, fx_usd: float, fx_eur: float, fx_date: str) -> AnalyzePayload:
    target_city = req.target_city or _DEFAULT_TARGET_CITY.get(req.target_country)
    return AnalyzePayload(
        raw_material=req.raw_material,
        tonnage=req.tonnage,
        quality=req.quality,
        origin_city=req.origin_city,
        target_country=req.target_country,
        target_city=target_city,
        transport_mode=req.transport_mode,
        priority=req.priority,
        input_mode=req.input_mode,
        moisture_pct=req.moisture_pct,
        purity_pct=req.purity_pct,
        particle_size_class=req.particle_size_class,
        fx_scenario_pct=req.fx_scenario_pct,
        cost_scenario_pct=req.cost_scenario_pct,
        live_fx=LiveFx(usd_try=fx_usd, eur_try=fx_eur, last_updated=fx_date),
    )


@router.post("/what-if", response_model=WhatIfResponse)
async def whatif_endpoint(
    payload: WhatIfRequest,
    _user: User = Depends(get_current_user),
) -> WhatIfResponse:
    fx = await get_current_fx()

    tasks = []
    for scn in payload.scenarios:
        scn_request = _apply_scenario(payload.base_payload, scn)
        ml_payload = _to_ml_payload(
            scn_request, fx.usd_try, fx.eur_try, fx.last_updated
        )
        tasks.append(run_analyze(ml_payload))

    t0 = time.perf_counter()
    responses = await asyncio.gather(*tasks)
    duration_ms = int((time.perf_counter() - t0) * 1000)

    rows = [
        WhatIfResultRow(
            scenario=scn.name,
            expected_profit_try=resp.expected_profit_try,
            value_uplift_pct=resp.value_uplift_pct,
            co2_kg=resp.co2_kg,
            recommended_route=resp.recommended_route,
            confidence_overall=resp.confidence.overall,
        )
        for scn, resp in zip(payload.scenarios, responses, strict=True)
    ]

    return WhatIfResponse(
        results=rows,
        base_fx=FxUsed(
            usd_try=fx.usd_try, eur_try=fx.eur_try, last_updated=fx.last_updated
        ),
        duration_ms=duration_ms,
    )
