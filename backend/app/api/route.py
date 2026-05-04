"""/api/route — gerçek karayolu/denizyolu polyline (ORS Directions).

Frontend haritada düz çizgi yerine kara rotasını çizebilsin diye. ORS
yanıtı GeoJSON LineString [[lon, lat], ...] formatında. ORS down ya da
key yoksa düz çizgi (2 nokta) fallback dönülür.

Deniz/hava modu: ORS bu modları desteklemiyor; gerçekçi görsel için
küresel yay (great-circle) interpolasyonu yapılır + tahmini mesafe
Haversine + mod düzeltme katsayısı ile hesaplanır.
"""
from __future__ import annotations

import math
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..clients.ors import OrsClient, OrsError
from ..db.models import User
from ..deps import get_current_user
from ..logging import get_logger
from ..services.geo_service import haversine_km

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
    source: Literal[
        "ors_directions",
        "great_circle_sea",
        "great_circle_air",
        "great_circle_rail",
        "fallback_straight",
    ]


# Deniz/hava/demiryolu için ortalama hız (km/saat) — duration_s tahmini.
_TRANSPORT_AVG_KMH: dict[str, float] = {
    "deniz": 30.0,        # konteyner gemisi ~16 knot
    "hava": 850.0,        # kargo uçağı cruise
    "demiryolu": 80.0,    # yük treni
}

# Gerçek rota Haversine'dan ne kadar uzun olur (rough)?
_TRANSPORT_DETOUR_FACTOR: dict[str, float] = {
    "deniz": 1.40,    # boğazlar/limanlar/kıyı takip
    "hava": 1.05,     # nearly direct
    "demiryolu": 1.25,
}


def _great_circle_interpolate(
    p1: tuple[float, float],  # (lon, lat)
    p2: tuple[float, float],
    n: int = 64,
) -> list[list[float]]:
    """İki nokta arası kavisli great-circle yayını N noktaya böler."""
    lon1, lat1 = math.radians(p1[0]), math.radians(p1[1])
    lon2, lat2 = math.radians(p2[0]), math.radians(p2[1])
    d = 2 * math.asin(math.sqrt(
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    ))
    if d == 0:
        return [[p1[0], p1[1]], [p2[0], p2[1]]]
    out: list[list[float]] = []
    for i in range(n + 1):
        f = i / n
        a = math.sin((1 - f) * d) / math.sin(d)
        b = math.sin(f * d) / math.sin(d)
        x = a * math.cos(lat1) * math.cos(lon1) + b * math.cos(lat2) * math.cos(lon2)
        y = a * math.cos(lat1) * math.sin(lon1) + b * math.cos(lat2) * math.sin(lon2)
        z = a * math.sin(lat1) + b * math.sin(lat2)
        lat_i = math.atan2(z, math.sqrt(x * x + y * y))
        lon_i = math.atan2(y, x)
        out.append([math.degrees(lon_i), math.degrees(lat_i)])
    return out


def _build_great_circle_route(
    points: list[tuple[float, float]],  # (lon, lat)
    mode: str,
) -> tuple[list[list[float]], float, float]:
    """Tüm waypoint'ler için great-circle interpolasyonu birleştirir.

    Returns:
        ``(coordinates, distance_m, duration_s)``
    """
    coords: list[list[float]] = []
    total_haversine_km = 0.0
    for i in range(len(points) - 1):
        seg = _great_circle_interpolate(points[i], points[i + 1], n=64)
        if i > 0:
            seg = seg[1:]  # önceki segmentin son noktasıyla çift olmasın
        coords.extend(seg)
        total_haversine_km += haversine_km(
            points[i][1], points[i][0],
            points[i + 1][1], points[i + 1][0],
        )
    detour = _TRANSPORT_DETOUR_FACTOR.get(mode, 1.0)
    avg_kmh = _TRANSPORT_AVG_KMH.get(mode, 60.0)
    distance_km = total_haversine_km * detour
    duration_h = distance_km / avg_kmh if avg_kmh > 0 else 0.0
    return coords, distance_km * 1000.0, duration_h * 3600.0


@router.post("/route", response_model=RouteResponse)
async def build_route(
    payload: RouteRequest,
    _user: User = Depends(get_current_user),
) -> RouteResponse:
    locations = [(p.lon, p.lat) for p in payload.points]

    # ORS Directions sadece kara için. Deniz/hava/demiryolu için
    # great-circle yay interpolasyonu — düz çizgi yerine küresel kavis,
    # mesafeyi Haversine + mod-spesifik detour katsayısıyla hesapla.
    if payload.transport_mode != "kara":
        coords, dist_m, dur_s = _build_great_circle_route(
            locations, mode=payload.transport_mode
        )
        source_map = {
            "deniz": "great_circle_sea",
            "hava": "great_circle_air",
            "demiryolu": "great_circle_rail",
        }
        return RouteResponse(
            coordinates=coords,
            distance_m=dist_m,
            duration_s=dur_s,
            source=source_map.get(payload.transport_mode, "fallback_straight"),  # type: ignore[arg-type]
        )

    client = OrsClient()
    try:
        try:
            result = await client.directions_cached(locations, profile="driving-hgv")
        except Exception as primary_exc:
            # 3+ waypoint çağrısında ORS bazen 404 (snap fail) verir;
            # uçtan uca (origin → destination) tekrar dene, ara işleyiciyi atla.
            if len(locations) > 2:
                logger.warning(
                    "ors_directions_multipoint_failed_retry_endpoints",
                    reason=repr(primary_exc),
                )
                endpoints = [locations[0], locations[-1]]
                result = await client.directions_cached(
                    endpoints, profile="driving-hgv"
                )
            else:
                raise
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
