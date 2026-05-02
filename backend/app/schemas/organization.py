"""Organization CRUD pydantic schemas.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §9.11-9.14.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .auth import CapabilityFlags


class ProducerProfileIn(BaseModel):
    raw_materials: list[str] = Field(default_factory=list)
    capacity_ton_year: int | None = None
    quality_grades: list[str] = Field(default_factory=list)


class ProcessorProfileIn(BaseModel):
    processing_routes: list[str] = Field(default_factory=list)
    capacity_ton_year: int | None = None
    certifications: list[str] = Field(default_factory=list)
    unit_cost_try_per_ton: float | None = None


class BuyerProfileIn(BaseModel):
    product_interests: list[str] = Field(default_factory=list)
    payment_terms_days: int | None = None
    credit_score: float | None = None


class OrgCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    organization_type: str | None = Field(default=None, max_length=50)
    district: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    country: str = Field(default="TR", min_length=2, max_length=2)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lon: float | None = Field(default=None, ge=-180, le=180)
    capabilities: CapabilityFlags = Field(default_factory=CapabilityFlags)
    producer_profile: ProducerProfileIn | None = None
    processor_profile: ProcessorProfileIn | None = None
    buyer_profile: BuyerProfileIn | None = None


class OrgUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, max_length=200)
    organization_type: str | None = Field(default=None, max_length=50)
    district: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, min_length=2, max_length=2)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lon: float | None = Field(default=None, ge=-180, le=180)
    capabilities: CapabilityFlags | None = None


class OrgOut(BaseModel):
    id: uuid.UUID
    name: str
    organization_type: str | None
    district: str | None
    city: str | None
    country: str
    lat: float | None
    lon: float | None
    capabilities: CapabilityFlags
    producer_profile: ProducerProfileIn | None = None
    processor_profile: ProcessorProfileIn | None = None
    buyer_profile: BuyerProfileIn | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedOrgs(BaseModel):
    items: list[OrgOut]
    page: int
    page_size: int
    total: int
    total_pages: int
