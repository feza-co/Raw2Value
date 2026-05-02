"""/api/processors/nearby response schemas."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ProcessorCapabilities(BaseModel):
    can_process_material: bool
    has_storage: bool
    has_transport_capacity: bool


class NearbyProcessor(BaseModel):
    id: str
    name: str
    city: str | None
    district: str | None
    lat: float
    lon: float
    distance_km: float
    processing_routes: list[str]
    capacity_ton_year: int | None
    certifications: list[str]
    unit_cost_try_per_ton: float | None
    capabilities: ProcessorCapabilities


class NearbyProcessorsResponse(BaseModel):
    results: list[NearbyProcessor]
    count: int
    radius_km: float
    method: Literal["haversine_bbox", "postgis_geography"] = "haversine_bbox"
