"""
P5 — T5.5: Sentinel-1 amplitude difference change detection.

Akademik referans: Mazza et al. 2023 — "SAR amplitude log-ratio change detection".
Pipeline:
  1. P1 T1.5 S1 stack (VV+VH GRD, Lee filtered, dB) → 2 zaman dilimi (t0, t1).
  2. Pre-processing: dB → linear amplitude.
  3. Log-ratio: r = 10 * log10(A_t1 / A_t0)   (dB)
  4. CFAR-benzeri threshold: |r| > 3 dB (Mazza önerisi); pozitif / negatif değişim ayrı.
  5. Morphological cleanup (3x3 majority filter).
  6. Binary change map → GeoTIFF.

Çıktı:
  - data/change/s1_change.tif      (uint8, 0=stable, 1=increase, 2=decrease)
  - data/change/s1_logratio.tif    (float32 dB)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window

PROJECT_ROOT = Path(__file__).resolve().parents[2]
S1_STACK_DIR = PROJECT_ROOT / "data" / "s1_stack"
OUT_CHANGE = PROJECT_ROOT / "data" / "change" / "s1_change.tif"
OUT_LOGR = PROJECT_ROOT / "data" / "change" / "s1_logratio.tif"

THRESHOLD_DB = 3.0  # Mazza 2023 — 3 dB tipik eşik
POL = "VV"  # P1 T1.5: VV+VH; biz VV kullanıyoruz (kayma için daha duyarlı)


def db_to_linear(db: np.ndarray) -> np.ndarray:
    return np.power(10.0, db / 10.0)


def log_ratio(a_t0: np.ndarray, a_t1: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """Mazza 2023 log-ratio. Girdiler linear amplitude, çıktı dB."""
    a_t0 = np.maximum(a_t0, eps)
    a_t1 = np.maximum(a_t1, eps)
    return 10.0 * np.log10(a_t1 / a_t0)


def majority_filter_3x3(binary: np.ndarray) -> np.ndarray:
    """Basit 3x3 majority filter (scipy.ndimage olmadan)."""
    out = np.zeros_like(binary)
    h, w = binary.shape
    pad = np.pad(binary, 1, mode="edge")
    for dy in range(3):
        for dx in range(3):
            out += pad[dy : dy + h, dx : dx + w]
    return (out >= 5).astype(binary.dtype)


def detect_change(t0_path: Path, t1_path: Path) -> tuple[np.ndarray, np.ndarray, dict]:
    with rasterio.open(t0_path) as src0, rasterio.open(t1_path) as src1:
        if src0.shape != src1.shape:
            raise ValueError(
                f"S1 stack shape mismatch: {src0.shape} vs {src1.shape}. "
                "P1 T1.7 co-registration kontrol et."
            )
        profile = src0.profile.copy()
        a_t0 = db_to_linear(src0.read(1).astype("float32"))
        a_t1 = db_to_linear(src1.read(1).astype("float32"))

    r = log_ratio(a_t0, a_t1)

    increase = (r > THRESHOLD_DB).astype(np.uint8)
    decrease = (r < -THRESHOLD_DB).astype(np.uint8)
    increase = majority_filter_3x3(increase)
    decrease = majority_filter_3x3(decrease)

    change = np.zeros_like(increase, dtype=np.uint8)
    change[increase == 1] = 1  # yeni artış (yapı/açma)
    change[decrease == 1] = 2  # düşüş (taşıma/erozyon)

    profile_change = profile.copy()
    profile_change.update(dtype="uint8", count=1, nodata=255, compress="deflate")

    profile_logr = profile.copy()
    profile_logr.update(dtype="float32", count=1, nodata=-9999, compress="deflate")

    return change, r.astype("float32"), profile_change | {"_logr_profile": profile_logr}


def main():
    OUT_CHANGE.parent.mkdir(parents=True, exist_ok=True)

    candidates = sorted(S1_STACK_DIR.glob(f"S1_*{POL}*.tif"))
    if len(candidates) < 2:
        raise FileNotFoundError(
            f"En az 2 S1 sahnesi gerek. {S1_STACK_DIR} içeriği: "
            f"{[p.name for p in candidates]}"
        )
    t0 = candidates[0]
    t1 = candidates[-1]
    print(f"[T5.5] t0={t0.name}  t1={t1.name}  (Mazza 2023 log-ratio)")

    change, logr, prof = detect_change(t0, t1)
    logr_prof = prof.pop("_logr_profile")

    with rasterio.open(OUT_CHANGE, "w", **{k: v for k, v in prof.items() if not k.startswith("_")}) as dst:
        dst.write(change, 1)
    with rasterio.open(OUT_LOGR, "w", **logr_prof) as dst:
        dst.write(logr, 1)

    n_inc = int((change == 1).sum())
    n_dec = int((change == 2).sum())
    pix_area_ha = (prof["transform"][0] * abs(prof["transform"][4])) / 10_000.0
    print(
        f"[T5.5] increase={n_inc} px ({n_inc * pix_area_ha:.1f} ha)  "
        f"decrease={n_dec} px ({n_dec * pix_area_ha:.1f} ha)"
    )
    print(f"  -> {OUT_CHANGE}")
    print(f"  -> {OUT_LOGR}")


if __name__ == "__main__":
    main()
