"""/api/route — gerçek karayolu/denizyolu polyline (ORS Directions).

Frontend haritada düz çizgi yerine kara rotasını çizebilsin diye. ORS
yanıtı GeoJSON LineString [[lon, lat], ...] formatında. ORS down ya da
key yoksa düz çizgi (2 nokta) fallback dönülür.
"""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..clients.ors import OrsClient, OrsError
from ..db.models import User
from ..deps import get_current_user
from ..logging import get_logger

logger = get_logger("api.route")

router = APIRouter(prefix="/api", tags=["route"])


class RoutePoint(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class RouteRequest(BaseModel):
    points: list[RoutePoint] = Field(min_length=2, max_length=10)
    transport_mode: Literal["kara", "deniz", "demiryolu", "hava"] = "kara"


class RouteResponse(BaseModel):
    coordinates: list[list[float]]  # [[lon, lat], ...]
    distance_m: float
    duration_s: float
    source: Literal["ors_directions", "fallback_straight"]


@router.post("/route", response_model=RouteResponse)
async def build_route(
    payload: RouteRequest,
    _user: User = Depends(get_current_user),
) -> RouteResponse:
    locations = [(p.lon, p.lat) for p in payload.points]

    # ORS Directions sadece kara için anlamlı; deniz/hava/demiryolu → düz çizgi
    if payload.transport_mode != "kara":
        return RouteResponse(
            coordinates=[[lon, lat] for (lon, lat) in locations],
            distance_m=0.0,
            duration_s=0.0,
            source="fallback_straight",
        )

    client = OrsClient()
    try:
        result = await client.directions_cached(locations, profile="driving-hgv")
        return RouteResponse(
            coordinates=result["coordinates"],
            distance_m=result["distance_m"],
            duration_s=result["duration_s"],
            source="ors_directions",
        )
    except OrsError as e:
        logger.warning("ors_directions_fallback", reason=str(e))
        return RouteResponse(
            coordinates=[[lon, lat] for (lon, lat) in locations],
            distance_m=0.0,
            duration_s=0.0,
            source="fallback_straight",
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("ors_directions_exception", reason=repr(e))
        return RouteResponse(
            coordinates=[[lon, lat] for (lon, lat) in locations],
            distance_m=0.0,
            duration_s=0.0,
            source="fallback_straight",
        )
    finally:
        await client.aclose()
