"""
T2.4 — Pozitif Piksel Örneklemesi
==================================

Pomza sahaları için saha başına ~300 piksel stratified random sampling.
Her saha içi alanına oranla ağırlıklandırılmış (büyük saha → daha çok piksel),
ama her sahaya min 100, max 500 cap uygulanır (sınıf-içi denge için).

Akademik referans:
- Stratified random within polygon (Roberts 2017'deki spatial CV ile uyumlu).
- Piksel-bazlı örnekleme protokolü v2'de eklendi (poligon-bazlı eğitimden farklı).

Girdi:
    data/labels/positive_polygons.gpkg
    data/raw/s2_l2a_avanos_rgb.tif    (raster grid referansı için, piksel merkez koordinatları)

Çıktı:
    data/labels/positive_pixels.gpkg
        - Her satır 1 piksel (Point geometry, EPSG:32636)
        - Alanlar: pixel_id, saha_id, mapeg_no, geom_kalitesi, x_utm, y_utm, label=1

Hedef:
    ~300 px/saha × 35 saha ≈ 10.500 pozitif piksel
"""

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import xy as rio_xy
from rasterio.features import geometry_mask
from shapely.geometry import Point


PIXEL_SIZE_M = 20  # S2 ARD grid (T1.4 [K#15])
TARGET_PER_SITE = 300
MIN_PER_SITE = 100
MAX_PER_SITE = 500
RNG = np.random.default_rng(42)


def sample_pixels_in_polygon(geom, raster_transform, raster_shape, n_samples):
    """
    Polygon içindeki raster piksellerinden stratified random örnekle.

    Parameters
    ----------
    geom : shapely Polygon
    raster_transform : rasterio Affine
    raster_shape : (rows, cols)
    n_samples : int

    Returns
    -------
    list of (row, col, x_utm, y_utm) tuples
    """
    # Poligon mask: polygonun kapladığı pikseller True
    mask = geometry_mask(
        [geom.__geo_interface__],
        out_shape=raster_shape,
        transform=raster_transform,
        invert=True,  # invert=True → polygon içi True
    )
    rows, cols = np.where(mask)
    if len(rows) == 0:
        return []

    # Mevcut piksel sayısı target'tan azsa hepsini al
    n_available = len(rows)
    n_pick = min(n_samples, n_available)
    if n_pick < MIN_PER_SITE and n_available >= MIN_PER_SITE:
        n_pick = MIN_PER_SITE

    idx = RNG.choice(n_available, size=n_pick, replace=False)
    sampled = []
    for i in idx:
        r, c = int(rows[i]), int(cols[i])
        # Pixel center coords
        x, y = rio_xy(raster_transform, r, c, offset="center")
        sampled.append((r, c, x, y))
    return sampled


def allocate_per_site(area_ha):
    """
    Saha alanına orantılı piksel quota'sı, min/max cap ile.
    Ortalama saha ~5 ha kabul edilirse 300 px ≈ 60 px/ha → küçük sahaya 200, büyüğüne 500.
    """
    n = int(round(60 * area_ha))
    return max(MIN_PER_SITE, min(MAX_PER_SITE, n if n > 0 else TARGET_PER_SITE))


def main(positives_gpkg, raster_path, out_gpkg):
    print(f"[T2.4] Pozitif piksel örneklemesi başlıyor")
    print(f"  Pozitif poligon: {positives_gpkg}")
    print(f"  Raster grid:     {raster_path}")

    polys = gpd.read_file(positives_gpkg)
    if polys.crs is None or polys.crs.to_epsg() != 32636:
        print(f"  WARN: poligon CRS != EPSG:32636 — reproject ediliyor")
        polys = polys.to_crs(32636)

    print(f"  Poligon sayisi: {len(polys)}")

    with rasterio.open(raster_path) as src:
        raster_transform = src.transform
        raster_shape = (src.height, src.width)
        raster_crs = src.crs
        if raster_crs.to_epsg() != 32636:
            raise ValueError(f"Raster CRS {raster_crs} ≠ EPSG:32636 — T1.4 ARD grid'i hatalı")

    all_records = []
    pixel_id = 0
    for _, row in polys.iterrows():
        geom = row.geometry
        area_ha = geom.area / 10_000.0  # m² → ha
        n_target = allocate_per_site(area_ha)

        samples = sample_pixels_in_polygon(geom, raster_transform, raster_shape, n_target)
        for r, c, x, y in samples:
            pixel_id += 1
            all_records.append({
                "pixel_id": f"P{pixel_id:06d}",
                "saha_id": row.get("saha_id"),
                "mapeg_no": row.get("mapeg_no"),
                "geom_kalitesi": int(row.get("geom_kalitesi", 1)) if row.get("geom_kalitesi") is not None else 1,
                "row": r,
                "col": c,
                "x_utm": x,
                "y_utm": y,
                "label": 1,
                "geometry": Point(x, y),
            })
        print(f"  {row.get('saha_id'):<6} alan={area_ha:6.2f} ha → {len(samples)} piksel")

    out = gpd.GeoDataFrame(all_records, geometry="geometry", crs="EPSG:32636")
    Path(out_gpkg).parent.mkdir(parents=True, exist_ok=True)
    out.to_file(out_gpkg, driver="GPKG", layer="positive_pixels")

    print(f"\n[T2.4] DONE")
    print(f"  Toplam pozitif piksel: {len(out)}")
    print(f"  Çıktı: {out_gpkg}")
    print(f"  Saha basina ort: {len(out)/max(1,len(polys)):.1f} px")
    print(f"  CRS: EPSG:32636 ✓")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--positives", default="data/labels/positive_polygons.gpkg")
    ap.add_argument("--raster", default="data/raw/s2_l2a_avanos_rgb.tif",
                    help="S2 ARD grid referansi (T1.4 cikti)")
    ap.add_argument("--out", default="data/labels/positive_pixels.gpkg")
    args = ap.parse_args()
    main(args.positives, args.raster, args.out)
