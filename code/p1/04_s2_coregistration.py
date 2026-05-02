"""T1.4 — S2 ARD co-registration: ortak 20m grid (EPSG:32636).

Karar #15: SWIR native 20m grid. 10m B2/B3/B4/B8 -> 20m bilinear downsample.
Cikti: data/ard/s2_ard_20m.tif (10 bant, 20m, EPSG:32636, NoData=-9999).

GEE export'tan inen dosya zaten 20m'e resample edilmis sekilde gelir.
Bu script:
  1) AOI ile tam clip (rasterio.mask),
  2) NoData = -9999 atama,
  3) bant isimlerini metadata'ya yazma,
  4) -tap grid alignment (ileride S1/DEM ayni origin'e oturacak).
"""
import math
from pathlib import Path
import sys

import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.mask import mask as rio_mask
from rasterio.warp import calculate_default_transform, reproject
import geopandas as gpd

REPO = Path(__file__).resolve().parents[2]
RAW  = REPO / "data" / "s2_raw" / "s2_l2a_avanos_median_2024_20m.tif"
OUT  = REPO / "data" / "ard" / "s2_ard_20m.tif"
AOI  = REPO / "data" / "aoi" / "avanos_aoi_utm36n.geojson"

BAND_NAMES = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]
TARGET_CRS = CRS.from_epsg(32636)
PIXEL_SIZE = 20.0
NODATA_IN  = 0       # GEE export'ta 0 = no data
NODATA_OUT = -9999.0

OUT.parent.mkdir(parents=True, exist_ok=True)

if not RAW.exists():
    sys.exit(f"HATA: {RAW} bulunamadi. Once T1.3 GEE export'unu data/s2_raw/ altina indir.")
if not AOI.exists():
    sys.exit(f"HATA: {AOI} bulunamadi. Once T1.2 calistir.")


def _snap_to_tap(left, bottom, right, top, res):
    """Target Aligned Pixels: sinirları res grid'e yasla."""
    left   = math.floor(left   / res) * res
    bottom = math.floor(bottom / res) * res
    right  = math.ceil(right   / res) * res
    top    = math.ceil(top     / res) * res
    return left, bottom, right, top


def main():
    # AOI geometrisini UTM 36N'de oku
    aoi_gdf = gpd.read_file(AOI)
    aoi_geom = [aoi_gdf.geometry.iloc[0].__geo_interface__]

    with rasterio.open(RAW) as src:
        print(f"[T1.4] Ham dosya: {src.width}x{src.height} px, {src.count} bant, CRS={src.crs}")

        # CRS uyumsuzsa once reproject yap
        if src.crs != TARGET_CRS:
            print(f"[T1.4] CRS donusturuluyor: {src.crs} -> {TARGET_CRS}")
            transform_new, w_new, h_new = calculate_default_transform(
                src.crs, TARGET_CRS, src.width, src.height, *src.bounds
            )
            reprojected = np.full((src.count, h_new, w_new), NODATA_OUT, dtype=np.float32)
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=reprojected[i - 1],
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform_new,
                    dst_crs=TARGET_CRS,
                    resampling=Resampling.bilinear,
                    src_nodata=NODATA_IN,
                    dst_nodata=NODATA_OUT,
                )
            tmp_profile = src.profile.copy()
            tmp_profile.update(crs=TARGET_CRS, transform=transform_new,
                               width=w_new, height=h_new, dtype="float32", nodata=NODATA_OUT)
            import tempfile, os
            tmp_path = Path(tempfile.mktemp(suffix=".tif"))
            with rasterio.open(tmp_path, "w", **tmp_profile) as tmp:
                tmp.write(reprojected)
            src_for_clip = rasterio.open(tmp_path)
        else:
            src_for_clip = src
            tmp_path = None

        # AOI ile mask + clip
        clipped, clip_transform = rio_mask(
            src_for_clip, aoi_geom,
            crop=True, filled=True, nodata=NODATA_OUT,
            all_touched=False,
        )
        clipped = clipped.astype(np.float32)

        # Kaynak NoData (0) -> -9999
        clipped[clipped == NODATA_IN] = NODATA_OUT

        clip_profile = src_for_clip.profile.copy()

    if tmp_path and tmp_path.exists():
        src_for_clip.close()
        tmp_path.unlink()

    # TAP grid: sinirları 20m grid'e yasla
    left   = clip_transform.c
    top    = clip_transform.f
    right  = left + clip_transform.a * clipped.shape[2]
    bottom = top  + clip_transform.e * clipped.shape[1]

    tap_left, tap_bottom, tap_right, tap_top = _snap_to_tap(left, bottom, right, top, PIXEL_SIZE)
    tap_width  = int(round((tap_right - tap_left) / PIXEL_SIZE))
    tap_height = int(round((tap_top   - tap_bottom) / PIXEL_SIZE))

    from rasterio.transform import from_origin
    tap_transform = from_origin(tap_left, tap_top, PIXEL_SIZE, PIXEL_SIZE)

    # TAP grid'e reproject (zaten ayni CRS, sadece grid kaymasi duzeltiliyor)
    tapped = np.full((clipped.shape[0], tap_height, tap_width), NODATA_OUT, dtype=np.float32)
    for i in range(clipped.shape[0]):
        reproject(
            source=clipped[i],
            destination=tapped[i],
            src_transform=clip_transform,
            src_crs=TARGET_CRS,
            dst_transform=tap_transform,
            dst_crs=TARGET_CRS,
            resampling=Resampling.bilinear,
            src_nodata=NODATA_OUT,
            dst_nodata=NODATA_OUT,
        )

    # Yaz
    out_profile = clip_profile.copy()
    out_profile.update({
        "crs":       TARGET_CRS,
        "transform": tap_transform,
        "width":     tap_width,
        "height":    tap_height,
        "dtype":     "float32",
        "nodata":    NODATA_OUT,
        "count":     clipped.shape[0],
        "compress":  "deflate",
        "tiled":     True,
        "bigtiff":   "IF_SAFER",
        "driver":    "GTiff",
    })

    with rasterio.open(OUT, "w", **out_profile) as dst:
        dst.write(tapped)
        for i, name in enumerate(BAND_NAMES[:clipped.shape[0]], start=1):
            dst.update_tags(i, name=name)

    # Sanity
    nodata_frac = (tapped == NODATA_OUT).mean()
    size_mb = OUT.stat().st_size / 1e6
    print(f"[T1.4] TAMAMLANDI -> {OUT}")
    print(f"  Grid: {tap_width}x{tap_height} px @ {PIXEL_SIZE}m, CRS: EPSG:32636")
    print(f"  Bantlar: {clipped.shape[0]}, NoData: {nodata_frac:.2%}, Boyut: {size_mb:.1f} MB")
    if clipped.shape[0] != 10:
        print(f"  [UYARI] Bant sayisi {clipped.shape[0]}, beklenen 10!")
    if nodata_frac > 0.05:
        print(f"  [UYARI] NoData %5 esigini asti!")


if __name__ == "__main__":
    main()
