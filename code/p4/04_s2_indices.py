"""
T4.4 — S2 türetilmiş indeksler (Karar #13).

Formüller (S2 L2A reflectance, [0,1] ölçek):
  NDVI    = (B8 - B4) / (B8 + B4)                              (Tucker 1979)
  BSI     = ((B11 + B4) - (B8 + B2)) / ((B11 + B4) + (B8 + B2))  (Rikimaru 2002)
  Albedo  = 0.356·B2 + 0.130·B4 + 0.373·B8 + 0.085·B11
            + 0.072·B12 - 0.0018                                (Liang 2001)
  Sabins  = B11 / B8                                            (Sabins 1999, clay/iron oxide)

Girdi: P1 ARD GeoTIFF — bantlar B2,B3,B4,B8,B11,B12 sıralı (manifest.json'dan oku).
Çıktı: data/layers/s2_{ndvi,bsi,albedo,sabins}.tif  (EPSG:32636, 20 m, COG)

Notlar:
  - 20 m grid hedef (Karar #15). B2/B4/B8 zaten 10 m → resample edilmiş varsayılır
    (P1 T1.4 ARD'da). B11/B12 native 20 m.
  - NoData propagasyonu: girdi NoData → çıktı NaN → write'da 0'a maskele.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling


# P1 ARD manifest'inde bant indexleri
BAND_KEY = {"B2": 1, "B3": 2, "B4": 3, "B8": 4, "B11": 5, "B12": 6}


def _safe_div(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    out = np.full_like(num, np.nan, dtype=np.float32)
    mask = np.isfinite(num) & np.isfinite(den) & (den != 0)
    out[mask] = num[mask] / den[mask]
    return out


def compute_ndvi(b4: np.ndarray, b8: np.ndarray) -> np.ndarray:
    return _safe_div(b8 - b4, b8 + b4)


def compute_bsi(b2: np.ndarray, b4: np.ndarray, b8: np.ndarray, b11: np.ndarray) -> np.ndarray:
    num = (b11 + b4) - (b8 + b2)
    den = (b11 + b4) + (b8 + b2)
    return _safe_div(num, den)


def compute_albedo_liang(
    b2: np.ndarray,
    b4: np.ndarray,
    b8: np.ndarray,
    b11: np.ndarray,
    b12: np.ndarray,
) -> np.ndarray:
    """Liang (2001) shortwave broadband albedo.

    Coefficients tuned for Landsat ETM+; Sentinel-2 yakın bant uyumu kabul edilir
    (B2≈blue, B4≈red, B8≈nir, B11≈swir1, B12≈swir2).
    """
    return (
        0.356 * b2
        + 0.130 * b4
        + 0.373 * b8
        + 0.085 * b11
        + 0.072 * b12
        - 0.0018
    ).astype(np.float32)


def compute_sabins(b8: np.ndarray, b11: np.ndarray) -> np.ndarray:
    return _safe_div(b11, b8)


def write_cog(arr: np.ndarray, profile: dict, out_path: Path) -> None:
    p = profile.copy()
    p.update(
        driver="GTiff",
        dtype="float32",
        count=1,
        nodata=np.float32(np.nan),
        compress="deflate",
        predictor=2,
        tiled=True,
        blockxsize=256,
        blockysize=256,
        BIGTIFF="IF_SAFER",
    )
    with rasterio.open(out_path, "w", **p) as dst:
        dst.write(arr.astype(np.float32), 1)
        # COG overviews
        dst.build_overviews([2, 4, 8, 16], Resampling.average)
        dst.update_tags(ns="rio_overview", resampling="average")


def read_band(src: rasterio.io.DatasetReader, idx: int) -> np.ndarray:
    arr = src.read(idx).astype(np.float32)
    nodata = src.nodatavals[idx - 1]
    if nodata is not None:
        arr = np.where(arr == nodata, np.nan, arr)
    # S2 reflectance ölçek varsayım: 0..1; eğer 0..10000 ise normalize et
    if np.nanmax(arr) > 100:
        arr = arr / 10000.0
    return arr


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--ard", required=True, help="P1 S2 ARD GeoTIFF (multi-band)")
    p.add_argument(
        "--manifest",
        default=None,
        help="optional ARD manifest.json (defines BAND_KEY); fallback hard-coded",
    )
    p.add_argument("--out", default="data/layers/")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    band_key = BAND_KEY
    if args.manifest:
        m = json.loads(Path(args.manifest).read_text())
        band_key = {k: int(v) for k, v in m.get("bands", BAND_KEY).items()}

    with rasterio.open(args.ard) as src:
        profile = src.profile.copy()
        b2 = read_band(src, band_key["B2"])
        b4 = read_band(src, band_key["B4"])
        b8 = read_band(src, band_key["B8"])
        b11 = read_band(src, band_key["B11"])
        b12 = read_band(src, band_key["B12"])

    ndvi = compute_ndvi(b4, b8)
    bsi = compute_bsi(b2, b4, b8, b11)
    albedo = compute_albedo_liang(b2, b4, b8, b11, b12)
    sabins = compute_sabins(b8, b11)

    write_cog(ndvi, profile, out_dir / "s2_ndvi.tif")
    write_cog(bsi, profile, out_dir / "s2_bsi.tif")
    write_cog(albedo, profile, out_dir / "s2_albedo.tif")
    write_cog(sabins, profile, out_dir / "s2_sabins.tif")

    stats = {
        "ndvi": _stat(ndvi),
        "bsi": _stat(bsi),
        "albedo": _stat(albedo),
        "sabins": _stat(sabins),
    }
    (out_dir / "s2_indices_stats.json").write_text(json.dumps(stats, indent=2))
    print(f"[ok] S2 indices written → {out_dir}/")
    print(json.dumps(stats, indent=2))
    return 0


def _stat(arr: np.ndarray) -> dict:
    valid = arr[np.isfinite(arr)]
    if valid.size == 0:
        return {"min": None, "max": None, "mean": None, "valid_pct": 0.0}
    return {
        "min": float(valid.min()),
        "max": float(valid.max()),
        "mean": float(valid.mean()),
        "valid_pct": round(float(valid.size / arr.size * 100), 2),
    }


if __name__ == "__main__":
    raise SystemExit(main())
