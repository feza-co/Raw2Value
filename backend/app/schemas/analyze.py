"""/api/analyze request + response schemas.

Frontend `live_fx` GÖNDERMEZ — backend TCMB cache'inden doldurur.
Response = ML AnalyzeResponse + meta alanlar (request_id, fx_used, duration_ms).

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md §9.7.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from raw2value_ml import AnalyzeResponse


class AnalyzeRequest(BaseModel):
    """Frontend'den gelen istek; live_fx YOK (backend doldurur)."""

    model_config = ConfigDict(extra="forbid")

    raw_material: Literal["pomza", "perlit", "kabak_cekirdegi"]
    tonnage: float = Field(gt=0, le=100_000)
    quality: Literal["A", "B", "C", "unknown"]
    origin_city: str = Field(min_length=1, max_length=100)
    target_country: Literal["TR", "DE", "NL"]
    target_city: str | None = Field(default=None, max_length=100)
    transport_mode: Literal["kara", "deniz", "demiryolu", "hava"]
    priority: Literal["max_profit", "low_carbon", "fast_delivery"] = "max_profit"
    input_mode: Literal["basic", "advanced"] = "basic"
    moisture_pct: float | None = Field(default=None, ge=0, le=100)
    purity_pct: float | None = Field(default=None, ge=0, le=100)
    particle_size_class: str | None = Field(default=None, max_length=50)
    fx_scenario_pct: float = Field(default=0.0, ge=-0.20, le=0.20)
    cost_scenario_pct: float = Field(default=0.0, ge=-0.20, le=0.20)


class FxUsed(BaseModel):
    usd_try: float
    eur_try: float
    last_updated: str


class AnalyzeResponseOut(AnalyzeResponse):
    """ML response + backend meta alanları."""

    request_id: str
    fx_used: FxUsed
    duration_ms: int
    model_version: str = "v1.0"


class WhatIfScenario(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    fx_scenario_pct: float | None = Field(default=None, ge=-0.20, le=0.20)
    tonnage_override: float | None = Field(default=None, gt=0, le=100_000)
    transport_mode_override: (
        Literal["kara", "deniz", "demiryolu", "hava"] | None
    ) = None


class WhatIfRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base_payload: AnalyzeRequest
    scenarios: list[WhatIfScenario] = Field(min_length=1, max_length=10)


class WhatIfResultRow(BaseModel):
    scenario: str
    expected_profit_try: float
    value_uplift_pct: float
    co2_kg: float
    recommended_route: str
    confidence_overall: float


class WhatIfResponse(BaseModel):
    results: list[WhatIfResultRow]
    base_fx: FxUsed
    duration_ms: int
