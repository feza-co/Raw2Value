"""Analiz geçmişi response schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AnalysisRecordSummary(BaseModel):
    id: int
    request_id: str
    created_at: datetime
    raw_material: str
    tonnage: float
    quality: str
    origin_city: str
    target_country: str
    transport_mode: str
    recommended_route: str
    expected_profit_try: float | None
    value_uplift_pct: float | None
    co2_kg: float | None
    confidence_overall: float | None
    duration_ms: int | None

    model_config = ConfigDict(from_attributes=True)


class AnalysisRecordDetail(AnalysisRecordSummary):
    payload_json: dict[str, Any]
    response_json: dict[str, Any]


class PaginatedHistory(BaseModel):
    items: list[AnalysisRecordSummary]
    page: int
    page_size: int
    total: int
    total_pages: int
