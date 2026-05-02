"""Backend contract — pydantic v2 modelleri.

`analyze()` fonksiyonunun girdi/çıktı sözleşmesi rapor §11.3'te tanımlandı; sabittir.
Bu modül backend-FE tarafından da kullanılacaktır.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class LiveFx(BaseModel):
    """Backend cache'inden gelen canlı kur."""

    usd_try: float = Field(gt=0)
    eur_try: float = Field(gt=0)
    last_updated: str  # ISO date string


class AnalyzePayload(BaseModel):
    """Kullanıcı formundan gelen ham girdi."""

    model_config = ConfigDict(extra="forbid")

    raw_material: Literal["pomza", "perlit", "kabak_cekirdegi"]
    tonnage: float = Field(gt=0, le=100_000)
    quality: Literal["A", "B", "C", "unknown"]
    origin_city: str
    target_country: Literal["TR", "DE", "NL"]
    target_city: str | None = None
    transport_mode: Literal["kara", "deniz", "demiryolu", "hava"]
    priority: Literal["max_profit", "low_carbon", "fast_delivery"] = "max_profit"
    input_mode: Literal["basic", "advanced"] = "basic"
    moisture_pct: float | None = None
    purity_pct: float | None = None
    particle_size_class: str | None = None
    fx_scenario_pct: float = 0.0
    cost_scenario_pct: float = 0.0
    live_fx: LiveFx


class RouteOption(BaseModel):
    """Tek bir aday rota — top-3 listesinden biri."""

    route: str
    predicted_profit_try: float
    value_uplift_pct: float
    co2_kg: float
    route_probability: float


class ReasonCode(BaseModel):
    """Top-K feature'a karşılık üretilen Türkçe gerekçe."""

    feature: str
    importance: float
    value: Any
    text: str


class MatchResult(BaseModel):
    """B2B match scorer'ın ürettiği processor×buyer çifti."""

    processor_name: str
    buyer_name: str
    score: float
    components: dict[str, float]


class ConfidenceBreakdown(BaseModel):
    """Veri + model güven skorları + uyarılar."""

    data_confidence: int
    model_confidence: int
    overall: float
    warnings: list[str]


class FeatureImportance(BaseModel):
    """Eğitilmiş model'den gelen tek bir feature önemi."""

    feature: str
    importance: float


class AnalyzeResponse(BaseModel):
    """Karar paketinin tamamı — UI tarafında doğrudan render edilir."""

    recommended_route: str
    route_alternatives: list[RouteOption]
    expected_profit_try: float
    value_uplift_pct: float
    co2_kg: float
    co2_tonnes: float
    match_results: list[MatchResult]
    reason_codes: list[ReasonCode]
    confidence: ConfidenceBreakdown
    feature_importance: list[FeatureImportance]
    warnings: list[str]
