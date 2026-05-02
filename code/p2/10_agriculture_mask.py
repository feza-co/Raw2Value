"""T2.x - Tarim alani maskesi uretimi.

Primary source: ESA WorldCover class 40 (Cropland). The output is aligned to
P1 `full_ard_20m.tif` so P2/P3/P5 can use it as a hard-negative/exclusion
layer without grid drift.

Typical flow:
  1) Start GEE export:
     python code/p2/10_agriculture_mask.py --gee-export
  2) Download Drive export to data/raw/esa_worldcover_cropland_avanos.tif
  3) Align + vectorize:
     python code/p2/10_agriculture_mask.py ^
       --worldcover data/raw/esa_worldcover_cropland_avanos.tif ^
       --raster-ref data/ard/full_ard_20m.tif ^
       --out data/labels/agriculture_mask.tif ^
       --out-vector data/labels/agriculture_polygons.gpkg
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.features import shapes
from rasterio.warp import reproject
from shapely.geometry import shape


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "code" / "p1"))

from aoi_config import bbox_text, ee_rectangle  # noqa: E402


WORLD_COVER_COLLECTION = "ESA/WorldCover/v200"
CROPLAND_CLASS = 40
MASK_VALUE = 1


def start_gee_export(prefix: str, folder: str) -> None:
    import ee

    ee.Initialize(project="pomza-495012")
    aoi = ee_rectangle(ee)
    worldcover = ee.ImageCollection(WORLD_COVER_COLLECTION).first().select("Map")
    cropland = worldcover.eq(CROPLAND_CLASS).rename("cropland").toUint8()

    task = ee.batch.Export.image.toDrive(
        image=cropland.clip(aoi),
        description=prefix,
        folder=folder,
        fileNamePrefix=prefix,
        region=aoi,
        scale=20,
        crs="EPSG:32636",
        maxPixels=1e10,
        fileFormat="GeoTIFF",
    )
    task.start()
    print(f"[T2.x] ESA WorldCover cropland export task: {task.id}")
    print(f"  AOI: {bbox_text()}")
    print(f"  Drive: {folder}/{prefix}.tif")


def align_worldcover_to_ref(worldcover_path: Path, raster_ref: Path, out_path: Path) -> np.ndarray:
    with rasterio.open(raster_ref) as ref:
        if ref.crs.to_epsg() != 32636:
            raise ValueError(f"Raster ref CRS must be EPSG:32636, got {ref.crs}")
        ref_profile = ref.profile.copy()
        dst = np.zeros((ref.height, ref.width), dtype=np.uint8)
        dst_transform = ref.transform
        dst_crs = ref.crs

    with rasterio.open(worldcover_path) as src:
        src_arr = src.read(1)
        src_nodata = src.nodata
        reproject(
            source=src_arr,
            destination=dst,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=src_nodata,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            dst_nodata=0,
            resampling=Resampling.nearest,
        )

    mask = np.where(dst == CROPLAND_CLASS, MASK_VALUE, 0).astype(np.uint8)
    # If the GEE export already wrote binary 0/1, preserve it.
    if not mask.any() and np.isin(dst, [0, 1]).all():
        mask = np.where(dst == 1, MASK_VALUE, 0).astype(np.uint8)

    profile = ref_profile
    profile.update(
        driver="GTiff",
        count=1,
        dtype="uint8",
        nodata=0,
        compress="lzw",
        tiled=True,
        blockxsize=256,
        blockysize=256,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_path, "w", **profile) as dst_file:
        dst_file.write(mask, 1)
        dst_file.update_tags(source="ESA WorldCover v200", class_code=str(CROPLAND_CLASS))
    return mask


def vectorize_mask(mask_path: Path, out_vector: Path, min_area_ha: float) -> int:
    records = []
    with rasterio.open(mask_path) as src:
        mask = src.read(1)
        for geom, value in shapes(mask, mask=mask == MASK_VALUE, transform=src.transform):
            if int(value) != MASK_VALUE:
                continue
            shp = shape(geom)
            area_ha = shp.area / 10_000.0
            if area_ha < min_area_ha:
                continue
            records.append({"class": "agriculture", "area_ha": area_ha, "geometry": shp})

    if records:
        gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:32636")
    else:
        gdf = gpd.GeoDataFrame({"class": [], "area_ha": []}, geometry=[], crs="EPSG:32636")
    out_vector.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(out_vector, driver="GPKG", layer="agriculture_polygons")
    return len(gdf)


def write_stats(mask: np.ndarray, raster_ref: Path, out_path: Path) -> None:
    with rasterio.open(raster_ref) as ref:
        pixel_area_m2 = abs(ref.transform.a * ref.transform.e)
    out_label = out_path.resolve()
    try:
        out_label_text = str(out_label.relative_to(REPO))
    except ValueError:
        out_label_text = str(out_label)
    agri_px = int((mask == MASK_VALUE).sum())
    total_px = int(mask.size)
    stats = {
        "source": "ESA WorldCover v200 class 40 Cropland",
        "mask": out_label_text,
        "agriculture_pixels": agri_px,
        "total_pixels": total_px,
        "agriculture_pct": round(agri_px / max(1, total_px) * 100, 3),
        "agriculture_area_ha": round(agri_px * pixel_area_m2 / 10_000.0, 3),
    }
    stats_path = out_path.with_suffix(".stats.json")
    stats_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gee-export", action="store_true",
                    help="Start ESA WorldCover cropland export to Google Drive")
    ap.add_argument("--drive-folder", default="Pomzadoya_GEE_exports")
    ap.add_argument("--drive-prefix", default="esa_worldcover_cropland_avanos")
    ap.add_argument("--worldcover", default="data/raw/esa_worldcover_cropland_avanos.tif",
                    help="Downloaded WorldCover/cropland GeoTIFF")
    ap.add_argument("--raster-ref", default="data/ard/full_ard_20m.tif")
    ap.add_argument("--out", default="data/labels/agriculture_mask.tif")
    ap.add_argument("--out-vector", default="data/labels/agriculture_polygons.gpkg")
    ap.add_argument("--min-area-ha", type=float, default=1.0)
    ap.add_argument("--no-vector", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    if args.gee_export:
        start_gee_export(args.drive_prefix, args.drive_folder)
        return 0

    worldcover = Path(args.worldcover)
    raster_ref = Path(args.raster_ref)
    out = Path(args.out)
    if not worldcover.exists():
        raise SystemExit(
            f"WorldCover input not found: {worldcover}. "
            "Run with --gee-export first, then download the Drive GeoTIFF."
        )
    if not raster_ref.exists():
        raise SystemExit(f"Raster reference not found: {raster_ref}")

    mask = align_worldcover_to_ref(worldcover, raster_ref, out)
    write_stats(mask, raster_ref, out)
    if not args.no_vector:
        n_poly = vectorize_mask(out, Path(args.out_vector), args.min_area_ha)
        print(f"[T2.x] Agriculture polygons: {n_poly} -> {args.out_vector}")
    print(f"[T2.x] DONE -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
