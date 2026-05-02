"""Geo service — Haversine bbox + DB filtreleme.

Hackathon kuralı K3: ORS bağımsız mesafe hesabı. PostGIS opsiyonel; MVP'de
SQL-side bbox filter + Python-side Haversine sıralama yeterli.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §18 ADIM 6.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Organization, ProcessorProfile

EARTH_RADIUS_KM = 6371.0088


@dataclass(frozen=True)
class BoundingBox:
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine formula — iki nokta arası büyük çember mesafesi (km)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def bbox_from_radius(lat: float, lon: float, radius_km: float) -> BoundingBox:
    """Verilen merkez+radius için yaklaşık enlem-boylam kutusu."""
    deg_lat = radius_km / 111.0
    cos_lat = math.cos(math.radians(lat)) or 1e-6
    deg_lon = radius_km / (111.0 * cos_lat)
    return BoundingBox(
        min_lat=lat - deg_lat,
        max_lat=lat + deg_lat,
        min_lon=lon - deg_lon,
        max_lon=lon + deg_lon,
    )


async def find_nearby_processors(
    db: AsyncSession,
    *,
    lat: float,
    lon: float,
    radius_km: float = 100,
    material: str | None = None,
    min_capacity: int | None = None,
) -> list[dict[str, Any]]:
    """Capability flag'i `can_process_material=TRUE` olan org'ları döner.

    Sıralama: artan distance_km. Method: `haversine_bbox`.
    """
    bbox = bbox_from_radius(lat, lon, radius_km)
    stmt = (
        select(Organization, ProcessorProfile)
        .outerjoin(
            ProcessorProfile,
            ProcessorProfile.organization_id == Organization.id,
        )
        .where(Organization.can_process_material.is_(True))
        .where(Organization.lat.isnot(None))
        .where(Organization.lon.isnot(None))
        .where(Organization.lat.between(bbox.min_lat, bbox.max_lat))
        .where(Organization.lon.between(bbox.min_lon, bbox.max_lon))
    )

    rows = (await db.execute(stmt)).all()
    out: list[dict[str, Any]] = []
    for org, profile in rows:
        if org.lat is None or org.lon is None:
            continue
        # ARRAY filtresi Python tarafında — sqlite/Postgres farkını kapatır.
        if material and profile is not None:
            if material not in (profile.processing_routes or []):
                continue
        if min_capacity is not None and profile is not None:
            if (profile.capacity_ton_year or 0) < min_capacity:
                continue
        d = haversine_km(lat, lon, float(org.lat), float(org.lon))
        if d > radius_km:
            continue
        out.append(
            {
                "id": str(org.id),
                "name": org.name,
                "city": org.city,
                "district": org.district,
                "lat": float(org.lat),
                "lon": float(org.lon),
                "distance_km": round(d, 2),
                "processing_routes": list(profile.processing_routes) if profile else [],
                "capacity_ton_year": profile.capacity_ton_year if profile else None,
                "certifications": list(profile.certifications) if profile else [],
                "unit_cost_try_per_ton": (
                    float(profile.unit_cost_try_per_ton)
                    if profile and profile.unit_cost_try_per_ton is not None
                    else None
                ),
                "capabilities": {
                    "can_process_material": org.can_process_material,
                    "has_storage": org.has_storage,
                    "has_transport_capacity": org.has_transport_capacity,
                },
            }
        )
    out.sort(key=lambda x: x["distance_km"])
    return out
