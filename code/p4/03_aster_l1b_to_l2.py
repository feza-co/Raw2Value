"""
T4.3 — ASTER L1B → L2 atmosferik düzeltme (DOS — Dark Object Subtraction).

Strateji:
  - Birincil: DOS1 (Chavez 1988) — her bantta histogramın dip noktasını "dark object"
    radiance'ı kabul edip çıkar. Hızlı, parametre gerektirmez.
  - 6S tam radiative transfer modeli hackathon süresinde aşırı pahalı; DOS akademik
    olarak yeterli (Sabins 1999; Chavez 1996 — DN-radiance dönüşümü zaten ASTER L1T'de
    radyometrik olarak kalibre, biz sadece atmosferik path radiance çıkarıyoruz).

Plan B (Karar #4 — kritik):
  Atmosferik düzeltme başarısız / DOS değerleri saçma çıkarsa → **L1T radiance ile
  devam**. Ninomiya QI = B11²/(B10·B12) oran-tabanlı olduğu için mutlak kalibrasyon
  zorunlu değildir. `--no-dos` flag'i ile aynı dosya `*_l2.tif` olarak yazılır.

Çıktı:
    data/aster/<scene>_l2_swir.tif      bantlar 4..9   (15..30 m, 30 m'e resample)
    data/aster/<scene>_l2_tir.tif       bantlar 10..14 (90 m)
    data/aster/<scene>_l2_meta.json     band stats (min/max/mean), DOS offset/band
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling


# ASTER bant grupları (L1T HDF subdataset isimleri)
SWIR_BANDS = ["ImageData4", "ImageData5", "ImageData6", "ImageData7", "ImageData8", "ImageData9"]
TIR_BANDS = ["ImageData10", "ImageData11", "ImageData12", "ImageData13", "ImageData14"]


def open_aster_subdataset(hdf_path: Path, band_name: str) -> tuple[np.ndarray, dict]:
    """ASTER L1T HDF içinden tek bantlı subdataset oku.

    GDAL HDF4 driver: `HDF4_EOS:EOS_SWATH:"path":SwathName:ImageData<N>`
    Pratikte rasterio HDF subdataset URI'sini destekler.
    """
    uri = f'HDF4_EOS:EOS_SWATH:"{hdf_path.as_posix()}":SWIR_Swath:{band_name}'
    try:
        ds = rasterio.open(uri)
    except rasterio.RasterioIOError:
        # bazı sahnelerde swath ismi farklı; alternatifleri dene
        for swath in ("VNIR_Swath", "TIR_Swath", "SWIR_Swath"):
            try:
                ds = rasterio.open(
                    f'HDF4_EOS:EOS_SWATH:"{hdf_path.as_posix()}":{swath}:{band_name}'
                )
                break
            except rasterio.RasterioIOError:
                continue
        else:
            raise
    arr = ds.read(1).astype(np.float32)
    profile = ds.profile.copy()
    ds.close()
    return arr, profile


def dos1_offset(arr: np.ndarray, percentile: float = 1.0) -> float:
    """Dark Object Subtraction — histogram alt %1 değeri.

    NoData=0 ASTER konvansiyonu; sıfırları hariç tut.
    """
    valid = arr[arr > 0]
    if valid.size == 0:
        return 0.0
    return float(np.percentile(valid, percentile))


def correct_band(arr: np.ndarray, no_dos: bool = False) -> tuple[np.ndarray, float]:
    """DOS uygula, NoData=0'a sadık kal."""
    if no_dos:
        return arr, 0.0
    offset = dos1_offset(arr)
    out = np.where(arr > 0, np.maximum(arr - offset, 0.0), 0.0).astype(np.float32)
    return out, offset


def stack_band_group(
    hdf_path: Path,
    band_names: list[str],
    no_dos: bool,
) -> tuple[np.ndarray, dict, dict]:
    """Bant grubunu (SWIR ya da TIR) tek 3D dizide birleştir."""
    arrays: list[np.ndarray] = []
    offsets: dict[str, float] = {}
    profile: dict | None = None
    for b in band_names:
        arr, prof = open_aster_subdataset(hdf_path, b)
        if profile is None:
            profile = prof
        if arr.shape != arrays[0].shape if arrays else False:
            # SWIR bantlarında nadiren tek piksel kayma görülebilir; bilinear resample
            with rasterio.open(
                f'HDF4_EOS:EOS_SWATH:"{hdf_path.as_posix()}":SWIR_Swath:{b}'
            ) as src:
                arr = src.read(
                    1,
                    out_shape=arrays[0].shape,
                    resampling=Resampling.bilinear,
                ).astype(np.float32)
        corrected, off = correct_band(arr, no_dos=no_dos)
        arrays.append(corrected)
        offsets[b] = off
    stacked = np.stack(arrays, axis=0)
    return stacked, profile, offsets


def write_geotiff(arr: np.ndarray, profile: dict, out_path: Path) -> None:
    out_profile = profile.copy()
    out_profile.update(
        driver="GTiff",
        dtype="float32",
        count=arr.shape[0],
        nodata=0.0,
        compress="deflate",
        predictor=2,
        tiled=True,
        blockxsize=256,
        blockysize=256,
        BIGTIFF="IF_SAFER",
    )
    out_profile.pop("HDF4_EOS:EOS_SWATH", None)
    with rasterio.open(out_path, "w", **out_profile) as dst:
        dst.write(arr)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--in", dest="hdf", required=True, help="ASTER L1T .hdf path")
    p.add_argument("--out", default="data/aster/")
    p.add_argument(
        "--no-dos",
        action="store_true",
        help="Plan B: DOS atla, L1T radiance ile devam (Karar #4 oran-tabanlı QI)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    hdf_path = Path(args.hdf)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = hdf_path.stem

    meta: dict[str, dict] = {}
    try:
        swir, prof_swir, off_swir = stack_band_group(hdf_path, SWIR_BANDS, args.no_dos)
        write_geotiff(swir, prof_swir, out_dir / f"{stem}_l2_swir.tif")
        meta["swir"] = {
            "bands": SWIR_BANDS,
            "dos_offsets": off_swir,
            "shape": list(swir.shape),
            "min": float(swir[swir > 0].min()) if (swir > 0).any() else None,
            "max": float(swir.max()),
            "mean": float(swir[swir > 0].mean()) if (swir > 0).any() else None,
        }
    except Exception as e:
        print(f"[err] SWIR stack failed: {e}", file=sys.stderr)
        if not args.no_dos:
            print("[hint] retry with --no-dos to use L1T radiance directly (Plan B)")
            return 3
        raise

    try:
        tir, prof_tir, off_tir = stack_band_group(hdf_path, TIR_BANDS, args.no_dos)
        write_geotiff(tir, prof_tir, out_dir / f"{stem}_l2_tir.tif")
        meta["tir"] = {
            "bands": TIR_BANDS,
            "dos_offsets": off_tir,
            "shape": list(tir.shape),
            "min": float(tir[tir > 0].min()) if (tir > 0).any() else None,
            "max": float(tir.max()),
            "mean": float(tir[tir > 0].mean()) if (tir > 0).any() else None,
        }
    except Exception as e:
        print(f"[err] TIR stack failed: {e}", file=sys.stderr)
        if not args.no_dos:
            print("[hint] retry with --no-dos (Plan B)")
            return 3
        raise

    meta["plan"] = "Plan B (no-DOS)" if args.no_dos else "DOS1 (Chavez 1988)"
    meta["source"] = hdf_path.name
    (out_dir / f"{stem}_l2_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"[ok] L2 written: {out_dir}/{stem}_l2_*.tif")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
