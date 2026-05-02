"""
P5 — T5.11: KPI hesabı (alan, yıllık büyüme %, UNESCO ihlal sayısı).

Saha bazında metrikler:
  - total_area_ha  (yıl bazında)
  - growth_pct     (1985 -> 2025 geometric mean annual growth)
  - unesco_violations  (1000 m buffer içine düşen tespit polygon sayısı)

Girdi:
  - data/temporal/historical_pomza_overlay/<year>_pomza.gpkg  (T5.10)
  - data/aoi/wdpa_goreme_buffer.gpkg                            (T5.2)
  - data/ard/final_confidence.tif (varsa, P4 FUSED — current state)

Çıktı:
  - reports/kpi.json
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import geopandas as gpd
from shapely.ops import unary_union

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OVERLAY_DIR = PROJECT_ROOT / "data" / "temporal" / "historical_pomza_overlay"
BUFFER_GPKG = PROJECT_ROOT / "data" / "aoi" / "wdpa_goreme_buffer.gpkg"
OUT = PROJECT_ROOT / "reports" / "kpi.json"

EPSG_UTM = 32636


def annual_areas() -> dict:
    out = {}
    for f in sorted(OVERLAY_DIR.glob("*_pomza.gpkg")):
        m = re.search(r"(\d{4})", f.stem)
        if not m:
            continue
        year = int(m.group(1))
        gdf = gpd.read_file(f).to_crs(EPSG_UTM)
        out[year] = {
            "n_polygons": int(len(gdf)),
            "area_ha": float(gdf.area.sum() / 10_000.0),
        }
    return out


def growth_metrics(areas: dict) -> dict:
    if not areas:
        return {"growth_pct_total": None, "cagr_pct": None}
    years = sorted(areas.keys())
    a0 = areas[years[0]]["area_ha"]
    aN = areas[years[-1]]["area_ha"]
    if a0 <= 0:
        return {"growth_pct_total": None, "cagr_pct": None, "first_year": years[0], "last_year": years[-1]}
    total_pct = (aN - a0) / a0 * 100.0
    n = years[-1] - years[0]
    cagr = (math.pow(aN / a0, 1.0 / n) - 1.0) * 100.0 if n > 0 else None
    return {
        "growth_pct_total": total_pct,
        "cagr_pct": cagr,
        "first_year": years[0],
        "last_year": years[-1],
        "first_area_ha": a0,
        "last_area_ha": aN,
    }


def unesco_violations(buffer_path: Path = BUFFER_GPKG) -> dict:
    if not buffer_path.exists():
        return {"violations_per_year": {}, "buffer_missing": True}
    buf = gpd.read_file(buffer_path).to_crs(EPSG_UTM)
    buf_geom = unary_union(buf.geometry.values)
    by_year = {}
    for f in sorted(OVERLAY_DIR.glob("*_pomza.gpkg")):
        m = re.search(r"(\d{4})", f.stem)
        if not m:
            continue
        year = int(m.group(1))
        gdf = gpd.read_file(f).to_crs(EPSG_UTM)
        n = int(gdf.geometry.intersects(buf_geom).sum())
        by_year[year] = n
    return {"violations_per_year": by_year, "buffer_missing": False}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not OVERLAY_DIR.exists():
        print(f"[T5.11] UYARI: {OVERLAY_DIR} yok. T5.10'u önce çalıştır.")
        OUT.write_text(json.dumps({"error": "historical overlay missing"}, indent=2))
        return

    areas = annual_areas()
    growth = growth_metrics(areas)
    violations = unesco_violations()

    payload = {
        "annual_areas": areas,
        "growth": growth,
        "unesco_violations": violations,
        "notes": [
            "v2: T5.10 historical RAW threshold 0.5; T5.13 current FUSED threshold P3 T3.6 F1-max.",
            "UNESCO buffer = WDPA Göreme + 1000 m (K#8).",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[T5.11] -> {OUT}")
    if growth.get("cagr_pct") is not None:
        print(
            f"  growth: {growth['first_year']}->{growth['last_year']} "
            f"toplam %{growth['growth_pct_total']:.1f}  CAGR %{growth['cagr_pct']:.2f}"
        )
    print(f"  UNESCO ihlal/yıl: {violations.get('violations_per_year')}")


if __name__ == "__main__":
    main()
