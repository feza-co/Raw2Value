"""/api/processors/nearby — bağımsız geo lookup (K3)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import User
from ..db.session import get_db
from ..deps import get_current_user
from ..exceptions import ValidationAppError
from ..schemas.processor import NearbyProcessor, NearbyProcessorsResponse
from ..services.geo_service import find_nearby_processors

router = APIRouter(prefix="/api/processors", tags=["processors"])


@router.get("/nearby", response_model=NearbyProcessorsResponse)
async def processors_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(100, gt=0, le=500),
    material: str | None = Query(default=None, max_length=50),
    min_capacity: int | None = Query(default=None, ge=0),
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NearbyProcessorsResponse:
    if radius_km > 500:
        raise ValidationAppError("radius_km max 500")
    rows = await find_nearby_processors(
        db,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        material=material,
        min_capacity=min_capacity,
    )
    return NearbyProcessorsResponse(
        results=[NearbyProcessor.model_validate(r) for r in rows],
        count=len(rows),
        radius_km=radius_km,
        method="haversine_bbox",
    )
