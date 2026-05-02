"""
T4.8 — DEM aspect + hillshade (gdaldem).

Girdi: P1 T1.7 çıktısı `data/dem/dem.tif` (Copernicus DEM, EPSG:32636, 20 m).
Çıktı:
  data/layers/dem_aspect.tif     (0..360°, NoData=-9999)
  data/layers/dem_hillshade.tif  (0..255, azimuth=315, altitude=45)

Komutlar:
  gdaldem aspect    dem.tif aspect.tif    -of GTiff -compute_edges
  gdaldem hillshade dem.tif hill.tif      -of GTiff -compute_edges -az 315 -alt 45 -z 1

Bu script subprocess wrapper; gdaldem yoksa rasterio + numpy fallback verir
(slope/aspect manuel hesap; hillshade Lambertian).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio


def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def gdaldem_aspect(dem: Path, out: Path) -> None:
    subprocess.run(
        [
            "gdaldem",
            "aspect",
            str(dem),
            str(out),
            "-of", "GTiff",
            "-compute_edges",
            "-co", "COMPRESS=DEFLATE",
            "-co", "PREDICTOR=2",
            "-co", "TILED=YES",
        ],
        check=True,
    )


def gdaldem_hillshade(dem: Path, out: Path, az: float = 315, alt: float = 45) -> None:
    subprocess.run(
        [
            "gdaldem",
            "hillshade",
            str(dem),
            str(out),
            "-of", "GTiff",
            "-compute_edges",
            "-az", str(az),
            "-alt", str(alt),
            "-z", "1",
            "-co", "COMPRESS=DEFLATE",
            "-co", "PREDICTOR=2",
            "-co", "TILED=YES",
        ],
        check=True,
    )


def fallback_aspect_hillshade(
    dem_path: Path, aspect_out: Path, hillshade_out: Path, az: float = 315, alt: float = 45
) -> None:
    """gdaldem yoksa: numpy gradient ile aspect + Lambertian hillshade."""
    with rasterio.open(dem_path) as src:
        z = src.read(1).astype(np.float32)
        profile = src.profile.copy()
        dx, dy = src.res

    gy, gx = np.gradient(z)
    gx_m = gx / dx
    gy_m = -gy / dy  # north positive

    slope = np.arctan(np.sqrt(gx_m ** 2 + gy_m ** 2))
    aspect = np.arctan2(gy_m, -gx_m)
    aspect_deg = np.degrees(aspect)
    aspect_deg = (aspect_deg + 360.0) % 360.0

    az_rad = np.radians(az)
    alt_rad = np.radians(alt)
    hs = (
        np.cos(slope) * np.sin(alt_rad)
        + np.sin(slope) * np.cos(alt_rad) * np.cos(az_rad - aspect)
    )
    hs = np.clip(hs * 255.0, 0, 255).astype(np.uint8)

    p_a = profile.copy()
    p_a.update(dtype="float32", nodata=-9999.0, count=1, compress="deflate", predictor=2)
    aspect_out_arr = np.where(np.isfinite(aspect_deg), aspect_deg, -9999.0).astype(np.float32)
    with rasterio.open(aspect_out, "w", **p_a) as dst:
        dst.write(aspect_out_arr, 1)

    p_h = profile.copy()
    p_h.update(dtype="uint8", nodata=0, count=1, compress="deflate")
    with rasterio.open(hillshade_out, "w", **p_h) as dst:
        dst.write(hs, 1)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--dem", required=True, help="Copernicus DEM GeoTIFF (P1 T1.7)")
    p.add_argument("--out", default="data/layers/")
    p.add_argument("--az", type=float, default=315.0)
    p.add_argument("--alt", type=float, default=45.0)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    dem = Path(args.dem)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    aspect_out = out_dir / "dem_aspect.tif"
    hill_out = out_dir / "dem_hillshade.tif"

    if _have("gdaldem"):
        gdaldem_aspect(dem, aspect_out)
        gdaldem_hillshade(dem, hill_out, args.az, args.alt)
        print("[ok] gdaldem path: aspect + hillshade written")
    else:
        print("[warn] gdaldem not found, using numpy fallback", file=sys.stderr)
        fallback_aspect_hillshade(dem, aspect_out, hill_out, args.az, args.alt)
        print("[ok] fallback path: aspect + hillshade written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
