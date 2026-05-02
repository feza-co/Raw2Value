"""Hackathon mandatory rule helpers for PomzaScope.

Rules covered:
  1. Geographic carbon footprint: OSRM/OSM route distance -> CO2.
  2. Live FX: TCMB EVDS when `TCMB_EVDS_API_KEY` is available.
  3. Independent geographic operation: route geometry/distance filtering.

No exchange rate is hardcoded. If EVDS is unavailable, callers receive a clear
status and can show a compliance warning instead of silently using stale data.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import requests


OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"
EVDS_URL = "https://evds2.tcmb.gov.tr/service/evds/"

EMISSION_FACTORS_KG_CO2_PER_TON_KM = {
    "road": 0.100,
    "rail": 0.030,
    "sea": 0.015,
    "air": 0.500,
}

EVDS_SERIES = {
    "USD/TRY": "TP.DK.USD.A.YTL",
    "EUR/TRY": "TP.DK.EUR.A.YTL",
}


@dataclass(frozen=True)
class RouteResult:
    distance_km: float
    duration_min: float
    source: str


@dataclass(frozen=True)
class FxResult:
    pair: str
    rate: float | None
    source: str
    updated_at: str
    status: str


def route_distance_osrm(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    timeout: int = 20,
) -> RouteResult:
    url = OSRM_ROUTE_URL.format(
        lon1=origin_lon,
        lat1=origin_lat,
        lon2=dest_lon,
        lat2=dest_lat,
    )
    r = requests.get(
        url,
        params={"overview": "false", "alternatives": "false", "steps": "false"},
        headers={"User-Agent": "PomzaScopeHackathon/1.0"},
        timeout=timeout,
    )
    r.raise_for_status()
    payload = r.json()
    routes = payload.get("routes") or []
    if not routes:
        raise RuntimeError(f"OSRM route not found: {payload.get('code')}")
    route = routes[0]
    return RouteResult(
        distance_km=float(route["distance"]) / 1000.0,
        duration_min=float(route["duration"]) / 60.0,
        source="OSRM public demo server / OpenStreetMap",
    )


def carbon_kg(distance_km: float, tonnage: float, mode: str) -> float:
    factor = EMISSION_FACTORS_KG_CO2_PER_TON_KM[mode]
    return float(distance_km) * float(tonnage) * factor


def fetch_tcmb_evds_rate(pair: str = "USD/TRY", timeout: int = 20) -> FxResult:
    api_key = os.environ.get("TCMB_EVDS_API_KEY")
    now = datetime.now().isoformat(timespec="seconds")
    if not api_key:
        return FxResult(pair, None, "TCMB EVDS", now, "missing_api_key")

    series = EVDS_SERIES[pair]
    end = datetime.now()
    start = end - timedelta(days=10)
    params: dict[str, Any] = {
        "series": series,
        "startDate": start.strftime("%d-%m-%Y"),
        "endDate": end.strftime("%d-%m-%Y"),
        "type": "json",
        "key": api_key,
    }
    r = requests.get(EVDS_URL, params=params, timeout=timeout)
    r.raise_for_status()
    payload = r.json()
    rows = payload.get("items") or []
    for row in reversed(rows):
        raw = row.get(series)
        if raw not in (None, "", "null"):
            return FxResult(
                pair=pair,
                rate=float(str(raw).replace(",", ".")),
                source="TCMB EVDS",
                updated_at=row.get("Tarih") or now,
                status="ok",
            )
    return FxResult(pair, None, "TCMB EVDS", now, "no_recent_rate")


def compute_demo_decision(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    tonnage: float,
    mode: str,
    pair: str,
    carbon_price_usd_per_ton: float = 75.0,
) -> dict[str, Any]:
    route = route_distance_osrm(origin_lat, origin_lon, dest_lat, dest_lon)
    co2_kg = carbon_kg(route.distance_km, tonnage, mode)
    fx = fetch_tcmb_evds_rate(pair)
    co2_ton = co2_kg / 1000.0
    carbon_cost_usd = co2_ton * carbon_price_usd_per_ton
    carbon_cost_try = carbon_cost_usd * fx.rate if fx.rate else None
    return {
        "route": route.__dict__,
        "tonnage": tonnage,
        "mode": mode,
        "emission_factor": EMISSION_FACTORS_KG_CO2_PER_TON_KM[mode],
        "co2_kg": co2_kg,
        "carbon_price_usd_per_ton": carbon_price_usd_per_ton,
        "carbon_cost_usd": carbon_cost_usd,
        "carbon_cost_try": carbon_cost_try,
        "fx": fx.__dict__,
        "computed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
