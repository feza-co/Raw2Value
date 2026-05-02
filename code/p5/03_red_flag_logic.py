"""
P5 — T5.3: UNESCO red flag overlay logic prototipi.

Mantık:
  - Tespit polygonları (P3 RAW veya P4 FUSED'tan binary üretilmiş) +
    WDPA Göreme 1000 m buffer (T5.2 çıktısı).
  - Tespit polygonu buffer ile **intersect** ediyorsa → kırmızı bayrak.
  - Sentetik raster ile prototip, sonra gerçek veriyle çağrılır.

Çıktı:
  - reports/red_flags.json      ({polygon_id, area_m2, intersects_unesco, distance_m})
  - data/layers/red_flags.gpkg  (kırmızı bayraklı tespit polygonları)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import geopandas as gpd
from shapely.geometry import Polygon, box, mapping
from shapely.ops import unary_union

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUFFER_GPKG = PROJECT_ROOT / "data" / "aoi" / "wdpa_goreme_buffer.gpkg"
OUT_GPKG = PROJECT_ROOT / "data" / "layers" / "red_flags.gpkg"
OUT_JSON = PROJECT_ROOT / "reports" / "red_flags.json"

EPSG_UTM = 32636


def load_unesco_buffer(path: Path = BUFFER_GPKG) -> gpd.GeoDataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"UNESCO buffer yok: {path}. Önce 02_wdpa_goreme.py çalıştır."
        )
    return gpd.read_file(path).to_crs(EPSG_UTM)


def evaluate_red_flags(
    detections: gpd.GeoDataFrame,
    unesco_buffer: gpd.GeoDataFrame,
) -> tuple[gpd.GeoDataFrame, list[dict]]:
    """Her tespit için intersect ve uzaklık hesabı."""
    if detections.crs is None:
        raise ValueError("detections CRS yok.")
    det = detections.to_crs(EPSG_UTM).copy()
    buf_geom = unary_union(unesco_buffer.geometry.values)

    records = []
    flags = []
    for idx, row in det.iterrows():
        g = row.geometry
        if g is None or g.is_empty:
            continue
        intersects = g.intersects(buf_geom)
        # Polygon → buffer dış sınırına en kısa mesafe (m)
        dist = g.distance(buf_geom.boundary) if not intersects else 0.0
        rec = {
            "polygon_id": int(row.get("id", idx)),
            "area_m2": float(g.area),
            "intersects_unesco": bool(intersects),
            "distance_to_unesco_m": float(dist),
        }
        records.append(rec)
        if intersects:
            flags.append(idx)

    flagged = det.loc[flags].copy()
    flagged["red_flag"] = True
    return flagged, records


def synthetic_demo() -> gpd.GeoDataFrame:
    """Sentetik tespit polygonları — Avanos civarı UTM koordinatları."""
    polys = [
        Polygon([(670000, 4280000), (670500, 4280000), (670500, 4280500), (670000, 4280500)]),
        Polygon([(675000, 4282000), (675400, 4282000), (675400, 4282400), (675000, 4282400)]),
        Polygon([(680000, 4275000), (680300, 4275000), (680300, 4275300), (680000, 4275300)]),
    ]
    return gpd.GeoDataFrame({"id": [1, 2, 3]}, geometry=polys, crs=EPSG_UTM)


def main():
    OUT_GPKG.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    buf = load_unesco_buffer()
    print(f"[T5.3] UNESCO buffer alanı: {buf.area.sum() / 1e6:.2f} km²")

    # Sentetik demo (gerçekte P3/P4 binary'den vectorize edilen polygon gelir)
    det = synthetic_demo()
    print(f"[T5.3] Sentetik tespit: {len(det)} polygon")

    flagged, records = evaluate_red_flags(det, buf)
    print(f"[T5.3] Red flag sayısı: {len(flagged)} / {len(det)}")

    if not flagged.empty:
        flagged.to_file(OUT_GPKG, driver="GPKG")
    OUT_JSON.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"  -> {OUT_JSON}")
    print(f"  -> {OUT_GPKG}")


if __name__ == "__main__":
    main()
