"""
P5 — T5.2: WDPA Göreme National Park polygon + 1000 m buffer + OSM Overpass cross-check.

v2 referans: K#8 (UNESCO Göreme buffer = 1000 m).
WDPA WDPAID 1130 = "Goreme National Park" (Turkey, mixed UNESCO World Heritage).
Cross-check: OSM Overpass `boundary=protected_area` veya `boundary=national_park`
relation Cappadocia / Göreme.

Çıktı:
  - data/aoi/wdpa_goreme.gpkg          (raw polygon, EPSG:4326)
  - data/aoi/wdpa_goreme_buffer.gpkg   (1000 m buffer, EPSG:32636)
  - data/aoi/osm_goreme_check.gpkg     (OSM relation, cross-validation)
  - reports/wdpa_goreme_check.json     (alan, geometri farkı, doğrulama notu)
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import requests
from shapely.geometry import shape
from shapely.ops import unary_union

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WDPA_SHP = PROJECT_ROOT / "data" / "aoi" / "wdpa_tr" / "WDPA_TR.shp"  # P1 indirir
OUT_RAW = PROJECT_ROOT / "data" / "aoi" / "wdpa_goreme.gpkg"
OUT_BUF = PROJECT_ROOT / "data" / "aoi" / "wdpa_goreme_buffer.gpkg"
OUT_OSM = PROJECT_ROOT / "data" / "aoi" / "osm_goreme_check.gpkg"
OUT_REP = PROJECT_ROOT / "reports" / "wdpa_goreme_check.json"

GOREME_WDPAID = 1130  # WDPA ID for Göreme National Park
BUFFER_M = 1000  # K#8: 1000 m UNESCO buffer
EPSG_LL = 4326
EPSG_UTM = 32636  # Avanos AOI UTM zone

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_QUERY = """
[out:json][timeout:60];
(
  relation["boundary"="national_park"]["name"~"Göreme",i];
  relation["boundary"="protected_area"]["name"~"Göreme",i];
);
out geom;
"""


def load_wdpa_goreme(wdpa_path: Path = WDPA_SHP) -> gpd.GeoDataFrame:
    """WDPA shapefile'dan WDPAID=1130 (Göreme) feature'ını çek."""
    if not wdpa_path.exists():
        raise FileNotFoundError(
            f"WDPA shapefile yok: {wdpa_path}. P1 T1.2 ile indir veya UNEP-WCMC'den çek."
        )
    gdf = gpd.read_file(wdpa_path)
    # WDPAID alanı bazen WDPA_PID olarak gelir
    id_col = "WDPAID" if "WDPAID" in gdf.columns else "WDPA_PID"
    sub = gdf[gdf[id_col] == GOREME_WDPAID].copy()
    if sub.empty:
        # Name fallback
        sub = gdf[gdf["NAME"].str.contains("Göreme", case=False, na=False)].copy()
    if sub.empty:
        raise ValueError("WDPA verisinde Göreme bulunamadı. WDPA_PID/NAME kontrol et.")
    return sub.to_crs(EPSG_LL)


def buffer_unesco(gdf: gpd.GeoDataFrame, meters: int = BUFFER_M) -> gpd.GeoDataFrame:
    """1000 m buffer (K#8). UTM'de yapılır, sonuç EPSG:32636'da kalır."""
    utm = gdf.to_crs(EPSG_UTM)
    utm["geometry"] = utm.buffer(meters)
    return utm


def fetch_osm_goreme() -> gpd.GeoDataFrame:
    """Overpass API'den Göreme protected_area / national_park relation çek."""
    r = requests.post(OVERPASS_URL, data={"data": OVERPASS_QUERY}, timeout=90)
    r.raise_for_status()
    payload = r.json()
    geoms, attrs = [], []
    for el in payload.get("elements", []):
        if el.get("type") != "relation":
            continue
        # Overpass `out geom` her member için lat/lon listesi döndürür
        rings = []
        for m in el.get("members", []):
            if m.get("role") in ("outer", "") and "geometry" in m:
                ring = [(p["lon"], p["lat"]) for p in m["geometry"]]
                if len(ring) >= 4 and ring[0] != ring[-1]:
                    ring.append(ring[0])
                if len(ring) >= 4:
                    rings.append(ring)
        if not rings:
            continue
        try:
            poly = shape({"type": "Polygon", "coordinates": [rings[0]]})
        except Exception:
            continue
        geoms.append(poly)
        attrs.append({"osm_id": el.get("id"), "name": el.get("tags", {}).get("name", "")})
    if not geoms:
        return gpd.GeoDataFrame(
            columns=["osm_id", "name", "geometry"], geometry="geometry", crs=EPSG_LL
        )
    return gpd.GeoDataFrame(attrs, geometry=geoms, crs=EPSG_LL)


def cross_check(wdpa: gpd.GeoDataFrame, osm: gpd.GeoDataFrame) -> dict:
    """WDPA polygonu OSM polygonuyla intersection / IoU."""
    if osm.empty:
        return {"osm_found": False, "iou": None, "note": "Overpass boş döndü, manuel doğrula."}
    wdpa_u = unary_union(wdpa.to_crs(EPSG_UTM).geometry.values)
    osm_u = unary_union(osm.to_crs(EPSG_UTM).geometry.values)
    inter = wdpa_u.intersection(osm_u).area
    union = wdpa_u.union(osm_u).area
    iou = (inter / union) if union > 0 else 0.0
    return {
        "osm_found": True,
        "wdpa_area_m2": wdpa_u.area,
        "osm_area_m2": osm_u.area,
        "intersection_m2": inter,
        "iou": iou,
        "note": "OK" if iou > 0.5 else "Düşük IoU — manuel kontrol et.",
    }


def main():
    OUT_RAW.parent.mkdir(parents=True, exist_ok=True)
    OUT_REP.parent.mkdir(parents=True, exist_ok=True)

    print(f"[T5.2] WDPA Göreme okunuyor: {WDPA_SHP}")
    wdpa = load_wdpa_goreme()
    wdpa.to_file(OUT_RAW, driver="GPKG")
    print(f"  -> {OUT_RAW} ({len(wdpa)} feature)")

    print(f"[T5.2] 1000 m buffer (K#8)")
    buf = buffer_unesco(wdpa, BUFFER_M)
    buf.to_file(OUT_BUF, driver="GPKG")
    print(f"  -> {OUT_BUF} (alan: {buf.area.sum() / 1e6:.2f} km²)")

    print("[T5.2] OSM Overpass cross-check")
    try:
        osm = fetch_osm_goreme()
        if not osm.empty:
            osm.to_file(OUT_OSM, driver="GPKG")
        check = cross_check(wdpa, osm)
    except Exception as exc:
        check = {"osm_found": False, "error": str(exc), "note": "Overpass erişim hatası."}

    OUT_REP.write_text(json.dumps(check, indent=2), encoding="utf-8")
    print(f"  -> {OUT_REP}")
    print(f"  cross-check: {check.get('note')}")


if __name__ == "__main__":
    main()
