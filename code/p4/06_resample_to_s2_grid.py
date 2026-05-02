"""
T4.6 — ASTER 90 m → Sentinel-2 20 m grid bilinear resample (Karar #15).

Hedef:
  - CRS    : EPSG:32636 (UTM zone 36N)
  - Pixel  : 20 m × 20 m
  - Hizalama: P1 ARD ile birebir (origin + extent eşleşsin)
  - Yöntem : bilinear  (nearest YASAK — gradient yumuşaklığı için)
  - Format : COG (Cloud Optimized GeoTIFF), Deflate predictor=2

Girdi: data/layers/aster_{qi,ci,sio2}.tif (native ~90 m, TIR grid)
Çıktı: data/layers/aster_{qi,ci,sio2}_20m.tif

Çağrı (gdalwarp):
    gdalwarp -overwrite -t_srs EPSG:32636 -tr 20 20 \
             -r bilinear -te <xmin> <ymin> <xmax> <ymax> \
             -of COG -co COMPRESS=DEFLATE -co PREDICTOR=2 \
             aster_qi.tif aster_qi_20m.tif

Bu script gdalwarp'u subprocess ile çağırır + Python rasterio fallback sağlar.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling


def _gdalwarp_available() -> bool:
    return shutil.which("gdalwarp") is not None


def get_target_extent(reference_tif: Path) -> tuple[float, float, float, float]:
    """P1 ARD'den hedef extent al (xmin, ymin, xmax, ymax)."""
    with rasterio.open(reference_tif) as src:
        if src.crs.to_string() != "EPSG:32636":
            print(
                f"[warn] reference CRS={src.crs}, beklenen EPSG:32636",
                file=sys.stderr,
            )
        b = src.bounds
        return b.left, b.bottom, b.right, b.top


def warp_with_gdal(
    src: Path,
    dst: Path,
    extent: tuple[float, float, float, float],
    res: float = 20.0,
) -> None:
    xmin, ymin, xmax, ymax = extent
    cmd = [
        "gdalwarp",
        "-overwrite",
        "-t_srs", "EPSG:32636",
        "-tr", str(res), str(res),
        "-te", str(xmin), str(ymin), str(xmax), str(ymax),
        "-r", "bilinear",
        "-of", "COG",
        "-co", "COMPRESS=DEFLATE",
        "-co", "PREDICTOR=2",
        "-co", "BLOCKSIZE=256",
        "-co", "RESAMPLING=BILINEAR",
        "-srcnodata", "nan",
        "-dstnodata", "nan",
        str(src),
        str(dst),
    ]
    print("[gdalwarp]", " ".join(cmd))
    subprocess.run(cmd, check=True)


def warp_with_rasterio(
    src_path: Path,
    dst_path: Path,
    extent: tuple[float, float, float, float],
    res: float = 20.0,
) -> None:
    """gdalwarp yoksa rasterio fallback (Windows wheel'lerinde GDAL CLI ek paket)."""
    xmin, ymin, xmax, ymax = extent
    width = int(round((xmax - xmin) / res))
    height = int(round((ymax - ymin) / res))
    dst_transform = rasterio.transform.from_origin(xmin, ymax, res, res)
    dst_crs = "EPSG:32636"

    with rasterio.open(src_path) as src:
        profile = src.profile.copy()
        profile.update(
            driver="GTiff",
            crs=dst_crs,
            transform=dst_transform,
            width=width,
            height=height,
            dtype="float32",
            nodata=np.float32(np.nan),
            compress="deflate",
            predictor=2,
            tiled=True,
            blockxsize=256,
            blockysize=256,
        )
        with rasterio.open(dst_path, "w", **profile) as dst:
            for b in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, b),
                    destination=rasterio.band(dst, b),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=dst_transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.bilinear,  # NEAREST YASAK
                )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument(
        "--reference",
        required=True,
        help="P1 ARD GeoTIFF (extent + CRS hedefi olarak kullanılır)",
    )
    p.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="resample edilecek ASTER GeoTIFF'leri (qi, ci, sio2 ...)",
    )
    p.add_argument("--out", default="data/layers/")
    p.add_argument("--res", type=float, default=20.0)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    extent = get_target_extent(Path(args.reference))
    print(f"[target] EPSG:32636, {args.res}m, extent={extent}")

    use_gdal = _gdalwarp_available()
    if not use_gdal:
        print("[warn] gdalwarp not found, using rasterio fallback")

    manifest = []
    for src in args.inputs:
        src_path = Path(src)
        dst_path = out_dir / f"{src_path.stem}_20m.tif"
        if use_gdal:
            warp_with_gdal(src_path, dst_path, extent, res=args.res)
        else:
            warp_with_rasterio(src_path, dst_path, extent, res=args.res)
        manifest.append(
            {
                "input": str(src_path),
                "output": str(dst_path),
                "method": "bilinear",
                "target_crs": "EPSG:32636",
                "target_res": args.res,
            }
        )

    (out_dir / "resample_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"[ok] resampled {len(manifest)} layers → {out_dir}/*_20m.tif")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
