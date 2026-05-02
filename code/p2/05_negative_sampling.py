"""
T2.5 — Negatif Piksel Örneklemesi
===================================

Strateji: Pozitif poligonların 2 km buffer'ı dışından stratified random
~6000 negatif piksel. Buffer içi ALINMAZ (sınıf-içi karışmayı engelle).

Akademik gerekçe (v2 § P2 + Karar K#12):
- 2 km buffer dışı = "kesin pomza-dışı" zone (sınır belirsizliği yok).
- Negatif örnek = pozitifin 2x'i kadar (10K poz ↔ 6K neg → ~1.7:1 imbalance, manageable).
- WDPA Göreme + 1000 m buffer → bu zone NE pozitif NE negatif (T2.6 ignore_mask).

Girdi:
    data/labels/positive_polygons.gpkg
    data/raw/s2_l2a_avanos_rgb.tif         (raster grid referansı)
    data/aoi/avanos_aoi.gpkg               (AOI sınırı — negatifler AOI içinde olmalı)
    data/labels/wdpa_buffer.gpkg           (T2.6 çıktısı, varsa exclude)

Çıktı:
    data/labels/negative_pixels.gpkg       (~6000 piksel, label=0)
"""

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import xy as rio_xy
from rasterio.features import geometry_mask
from shapely.geometry import Point
from shapely.ops import unary_union


PIXEL_SIZE_M = 20
POSITIVE_BUFFER_M = 2000      # 2 km buffer dışı = negatif zone
TARGET_NEGATIVE = 6000
RNG = np.random.default_rng(43)


def main(positives_gpkg, raster_path, aoi_gpkg, wdpa_gpkg, out_gpkg, n_target):
    print(f"[T2.5] Negatif piksel örneklemesi başlıyor")
    print(f"  Pozitif buffer mesafesi: {POSITIVE_BUFFER_M} m")
    print(f"  Hedef negatif piksel: {n_target}")

    # Pozitifleri yukle, buffer at, union
    pos = gpd.read_file(positives_gpkg).to_crs(32636)
    pos_buffer = pos.geometry.buffer(POSITIVE_BUFFER_M)
    pos_union = unary_union(pos_buffer.values)
    print(f"  Pozitif union alani (2km buffer ile): {pos_union.area/1e6:.2f} km²")

    # AOI yukle, exclude region (positive buffer + WDPA buffer varsa)
    aoi = gpd.read_file(aoi_gpkg).to_crs(32636)
    aoi_geom = unary_union(aoi.geometry.values)

    exclude = pos_union
    if wdpa_gpkg and Path(wdpa_gpkg).exists():
        wdpa = gpd.read_file(wdpa_gpkg).to_crs(32636)
        wdpa_geom = unary_union(wdpa.geometry.values)
        exclude = unary_union([exclude, wdpa_geom])
        print(f"  WDPA exclusion eklendi")
    else:
        print(f"  WDPA buffer dosyasi yok (T2.6 sonra eklenecek). Su an sadece pozitif buffer.")

    # Aday negatif zone = AOI - exclude
    candidate_zone = aoi_geom.difference(exclude)
    if candidate_zone.is_empty or candidate_zone.area == 0:
        raise RuntimeError("Negatif zone bos! Buffer cok genis, AOI cok dar.")
    print(f"  Negatif aday zone: {candidate_zone.area/1e6:.2f} km²")

    # Raster grid'inde piksel mask cikar
    with rasterio.open(raster_path) as src:
        raster_transform = src.transform
        raster_shape = (src.height, src.width)
        if src.crs.to_epsg() != 32636:
            raise ValueError(f"Raster CRS != EPSG:32636")

    # candidate_zone MultiPolygon olabilir; geometry_mask listesi alir
    if hasattr(candidate_zone, "geoms"):
        geoms = list(candidate_zone.geoms)
    else:
        geoms = [candidate_zone]

    mask = geometry_mask(
        [g.__geo_interface__ for g in geoms],
        out_shape=raster_shape,
        transform=raster_transform,
        invert=True,
    )
    rows, cols = np.where(mask)
    n_available = len(rows)
    print(f"  Mevcut aday piksel: {n_available}")

    if n_available < n_target:
        print(f"  WARN: aday piksel < hedef ({n_available} < {n_target}). Hepsi alinacak.")
        n_pick = n_available
    else:
        n_pick = n_target

    idx = RNG.choice(n_available, size=n_pick, replace=False)
    records = []
    for i, k in enumerate(idx):
        r, c = int(rows[k]), int(cols[k])
        x, y = rio_xy(raster_transform, r, c, offset="center")
        records.append({
            "pixel_id": f"N{i+1:06d}",
            "row": r,
            "col": c,
            "x_utm": x,
            "y_utm": y,
            "label": 0,
            "geometry": Point(x, y),
        })

    out = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:32636")
    Path(out_gpkg).parent.mkdir(parents=True, exist_ok=True)
    out.to_file(out_gpkg, driver="GPKG", layer="negative_pixels")

    print(f"\n[T2.5] DONE")
    print(f"  Negatif piksel: {len(out)}")
    print(f"  Çıktı: {out_gpkg}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--positives", default="data/labels/positive_polygons.gpkg")
    ap.add_argument("--raster", default="data/raw/s2_l2a_avanos_rgb.tif")
    ap.add_argument("--aoi", default="data/aoi/avanos_aoi.gpkg")
    ap.add_argument("--wdpa", default="data/labels/wdpa_buffer.gpkg",
                    help="T2.6 cikti (yoksa exclude listesinde dahil edilmez)")
    ap.add_argument("--out", default="data/labels/negative_pixels.gpkg")
    ap.add_argument("--n-target", type=int, default=TARGET_NEGATIVE)
    args = ap.parse_args()
    main(args.positives, args.raster, args.aoi, args.wdpa, args.out, args.n_target)
