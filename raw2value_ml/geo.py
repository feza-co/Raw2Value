"""Mesafe lookup + Haversine fallback (rapor §K3 zorunlu).

`distances.parquet` precomputed (ORS) ve `distance_lookup.pkl` ID-bazlı dict.
Eşleşme bulunamazsa organizations.parquet'deki Lat/Lon koordinatları üzerinden
Haversine ile kuşuçuşu km, oradan x1.3 katsayısıyla "yol km" tahmini üretilir.
"""
from __future__ import annotations

import math

import pandas as pd

from .reference_loader import (
    load_distance_lookup,
    load_distances,
    load_organizations,
)

EARTH_RADIUS_KM = 6371.0
ROAD_MULTIPLIER = 1.3
DEFAULT_TOTAL_KM = 1500.0
SRC_FRACTION = 0.3
BUYER_FRACTION = 0.7

# Türkçe karakter normalize tablosu (Excel'den parquet'e kötü encoding nedeniyle
# bazı satırlar bozuk). Karşılaştırmayı tolere etmek için string'i ASCII'ye indiriyoruz.
_TR_FOLD = str.maketrans({
    "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ı": "i", "İ": "i",
    "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u",
})


def _norm(s: str) -> str:
    """Karşılaştırma için ASCII-fold + lower; bilinmeyen byte'ları '?' ile değiştirir."""
    if s is None:
        return ""
    s = str(s).translate(_TR_FOLD).lower()
    # Bozuk replacement char ve diğer non-ASCII'leri at.
    return "".join(ch for ch in s if ch.isascii() and ch != "�")


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """İki lat/lon noktası arası kuş uçuşu km."""
    rlat1, rlat2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS_KM * c


def _city_to_org_coord(city: str) -> tuple[float, float] | None:
    """Şehir/ilçe substring (ASCII-folded) eşleşmesiyle ilk org'un (lat, lon)'unu döner."""
    if not city:
        return None
    orgs = load_organizations()
    if "Sehir/Ilce" not in orgs.columns:
        return None
    needle = _norm(city)
    if not needle:
        return None
    folded = orgs["Sehir/Ilce"].astype(str).map(_norm)
    matches = orgs[folded.str.contains(needle, regex=False, na=False)]
    if matches.empty:
        return None
    for _, r in matches.iterrows():
        la, lo = r.get("Lat"), r.get("Lon")
        if not pd.isna(la) and not pd.isna(lo):
            return float(la), float(lo)
    return None


def lookup_distance(
    origin_city: str,
    destination_city: str | None,
    transport_mode: str = "kara",
) -> dict:
    """Origin → destination toplam mesafe + tahmini süre.

    Sıra:
      1. distances.parquet substring match (ORS_PRECOMPUTED).
      2. organizations.parquet Lat/Lon -> Haversine x ROAD_MULTIPLIER.
      3. Default 1500 km (DEFAULT_FALLBACK).

    Returns:
        ``{"total_km", "duration_min", "source",
           "source_to_processor_km", "processor_to_buyer_km"}``
    """
    if not destination_city:
        # Backend bunu set etmezse sadece bir default kullan (testler için).
        destination_city = "Hamburg"

    # 1) ORS precomputed substring match (ASCII-folded)
    distances_df = load_distances()
    if (
        "Source" in distances_df.columns
        and "Destination" in distances_df.columns
    ):
        src_norm = _norm(origin_city)
        dst_norm = _norm(destination_city)
        src_col = distances_df["Source"].astype(str).map(_norm)
        dst_col = distances_df["Destination"].astype(str).map(_norm)
        mask = src_col.str.contains(src_norm, regex=False, na=False) & dst_col.str.contains(
            dst_norm, regex=False, na=False
        )
        if mask.any():
            row = distances_df[mask].iloc[0]
            km = float(row.get("Distance km", 0) or 0)
            mins_raw = row.get("Duration min")
            try:
                mins = float(mins_raw) if mins_raw is not None and not pd.isna(mins_raw) else None
            except (ValueError, TypeError):
                mins = None
            if km > 0:
                return {
                    "total_km": km,
                    "duration_min": mins,
                    "source": "ORS_PRECOMPUTED",
                    "source_to_processor_km": km * SRC_FRACTION,
                    "processor_to_buyer_km": km * BUYER_FRACTION,
                }

    # 2) Haversine fallback üzerinden tahmin
    o_coord = _city_to_org_coord(origin_city)
    d_coord = _city_to_org_coord(destination_city)
    if o_coord and d_coord:
        crow_km = haversine(o_coord[0], o_coord[1], d_coord[0], d_coord[1])
        road_km = crow_km * ROAD_MULTIPLIER if transport_mode == "kara" else crow_km
        return {
            "total_km": road_km,
            "duration_min": None,
            "source": "HAVERSINE_FALLBACK",
            "source_to_processor_km": road_km * SRC_FRACTION,
            "processor_to_buyer_km": road_km * BUYER_FRACTION,
        }

    # 3) Last-resort default
    return {
        "total_km": DEFAULT_TOTAL_KM,
        "duration_min": None,
        "source": "DEFAULT_FALLBACK",
        "source_to_processor_km": DEFAULT_TOTAL_KM * SRC_FRACTION,
        "processor_to_buyer_km": DEFAULT_TOTAL_KM * BUYER_FRACTION,
    }


# Hammadde adından Excel'deki "Hammadde/Sektor" değerine eşlik (substring kontrolü için).
_MATERIAL_TOKEN: dict[str, str] = {
    "pomza": "Pomza",
    "perlit": "Perlit",
    "kabak_cekirdegi": "Kabak",
}


def find_nearby_processors(
    origin_city: str,
    raw_material: str,
    radius_km: float = 200.0,
) -> list[dict]:
    """Origin'e radius_km içindeki, raw_material'a uygun processor'ları döner.

    Returns:
        ``[{"name", "city", "distance_km", "lat", "lon"}, ...]`` mesafeye göre artan.
    """
    orgs = load_organizations()
    if orgs.empty:
        return []

    df = orgs[orgs.get("Tip", pd.Series([""] * len(orgs))).astype(str) == "processor"]
    if "Hammadde/Sektor" in df.columns:
        token = _MATERIAL_TOKEN.get(raw_material, raw_material)
        df = df[
            df["Hammadde/Sektor"]
            .astype(str)
            .str.contains(token, case=False, na=False)
        ]
    if df.empty:
        return []

    o_coord = _city_to_org_coord(origin_city)
    results: list[dict] = []
    for _, row in df.iterrows():
        lat = row.get("Lat")
        lon = row.get("Lon")
        if pd.isna(lat) or pd.isna(lon):
            continue
        if o_coord:
            d = haversine(o_coord[0], o_coord[1], float(lat), float(lon))
        else:
            d = 0.0
        if radius_km <= 0 or d <= radius_km:
            results.append({
                "name": str(row.get("Firma adi", "?")),
                "city": str(row.get("Sehir/Ilce", "")),
                "distance_km": float(d),
                "lat": float(lat),
                "lon": float(lon),
            })
    return sorted(results, key=lambda r: r["distance_km"])
