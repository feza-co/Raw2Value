"""
T4.12 — **CRITICAL PATH** score-level füzyon API.

Kontrat (P3 ile saat 17–18 HELP slotunda kesinleşti):

    fuse_confidence(raw_prob, qi, ci) -> final_confidence

Formül:

    final_confidence = raw_prob × QI_norm × (1 - CI_norm)

Bileşenler:
  - raw_prob   : P3 inference RAW olasılığı [0,1], shape (H, W) ya da (H, W, 1)
                 NaN propagasyonu: NaN giriş → NaN çıkış (kapatılmaz).
  - qi         : ASTER Quartz Index raster, native ölçek (~0.5..2.5).
                 percentile_minmax_norm(qi, lo=2, hi=98) ile [0,1]'e ölçeklenir.
  - ci         : ASTER Carbonate Index raster, native ölçek (~0.95..1.10).
                 percentile_minmax_norm(ci, lo=2, hi=98) ile [0,1]'e ölçeklenir.
                 (1 - CI_norm) → karbonat yüksekse cezalandırma katsayısı.

Boyut uyumu:
  - Üç girdinin shape'i birebir aynı olmalı (P5 T5.13 ana katman üretimi).
  - Eğer farklıysa SystemExit raise eder; çağıran taraf 06_resample_to_s2_grid.py
    ile QI/CI'yi 20 m grid'e taşımış olmalı.

Plan B (Karar #6 fail):
  - QI/CI eksik / şekil uyumsuz → final_confidence yerine raw_prob döndürülür
    ve fail_reason loglanır. P5 dashboard'da FUSED demosu kapatılır,
    raw_prob + ASTER ayrı katman olarak gösterilir.

CLI ek mod (T4.12 canlı RUN-BLOCK için):
    python fuse_confidence.py \
        --raw  data/inference/raw_prob.tif \
        --qi   data/layers/aster_qi_20m.tif \
        --ci   data/layers/aster_ci_20m.tif \
        --out  data/layers/final_confidence.tif
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


# ---------------------------------------------------------------------------
# Normalize
# ---------------------------------------------------------------------------
def percentile_minmax_norm(
    arr: np.ndarray,
    lo_pct: float = 2.0,
    hi_pct: float = 98.0,
    eps: float = 1e-6,
) -> np.ndarray:
    """Percentile-based clip + min-max → [0,1].

    Adımlar:
      1. NaN'ları çıkararak lo/hi percentile hesapla
      2. Aralık [lo, hi]'a clip
      3. (x - lo) / (hi - lo) ile [0,1]'e ölçekle
      4. NaN'ları geri yerleştir (propagate)
    """
    if arr.size == 0:
        return arr.astype(np.float32)
    valid = arr[np.isfinite(arr)]
    if valid.size == 0:
        return np.full_like(arr, np.nan, dtype=np.float32)

    lo = float(np.percentile(valid, lo_pct))
    hi = float(np.percentile(valid, hi_pct))
    if hi - lo < eps:
        # düz raster — sabit 0.5 döndür (cezalandırma yapma)
        out = np.where(np.isfinite(arr), 0.5, np.nan).astype(np.float32)
        return out

    clipped = np.clip(arr, lo, hi)
    norm = (clipped - lo) / (hi - lo)
    norm = norm.astype(np.float32)
    norm[~np.isfinite(arr)] = np.nan
    return norm


# ---------------------------------------------------------------------------
# Fuse
# ---------------------------------------------------------------------------
def fuse_confidence(
    raw_prob: np.ndarray,
    qi: np.ndarray,
    ci: np.ndarray,
    *,
    qi_norm_kwargs: dict | None = None,
    ci_norm_kwargs: dict | None = None,
) -> np.ndarray:
    """Score-level füzyon.

    Args:
        raw_prob: P3 inference RAW olasılık [0,1]. shape (H,W) veya (1,H,W) veya (H,W,1).
        qi:       P4 Ninomiya QI raster (normalize edilecek).
        ci:       P4 Carbonate Index raster (yüksek karbonat → düşük pomza).
        qi_norm_kwargs / ci_norm_kwargs: percentile_minmax_norm'a ekstra parametre.

    Returns:
        final_confidence np.ndarray, dtype float32, shape (H,W), aralık [0,1].
    """
    raw = _squeeze2d(raw_prob)
    qi_a = _squeeze2d(qi)
    ci_a = _squeeze2d(ci)

    if not (raw.shape == qi_a.shape == ci_a.shape):
        raise SystemExit(
            f"shape mismatch: raw={raw.shape} qi={qi_a.shape} ci={ci_a.shape}"
        )

    qi_n = percentile_minmax_norm(qi_a, **(qi_norm_kwargs or {}))
    ci_n = percentile_minmax_norm(ci_a, **(ci_norm_kwargs or {}))

    # raw_prob'u defansif olarak [0,1]'e clip et
    raw_clip = np.clip(raw, 0.0, 1.0).astype(np.float32)

    final = raw_clip * qi_n * (1.0 - ci_n)
    final = np.clip(final, 0.0, 1.0).astype(np.float32)
    # NaN propagate et
    nan_mask = ~np.isfinite(raw) | ~np.isfinite(qi_a) | ~np.isfinite(ci_a)
    final[nan_mask] = np.nan
    return final


def _squeeze2d(arr: np.ndarray) -> np.ndarray:
    a = np.asarray(arr, dtype=np.float32)
    if a.ndim == 2:
        return a
    if a.ndim == 3:
        # (1,H,W) ya da (H,W,1)
        if a.shape[0] == 1:
            return a[0]
        if a.shape[-1] == 1:
            return a[..., 0]
    raise SystemExit(f"expected 2D raster, got shape {a.shape}")


# ---------------------------------------------------------------------------
# CLI (canlı RUN-BLOCK için saat 18-20)
# ---------------------------------------------------------------------------
def _read_raster(path: Path):
    import rasterio
    with rasterio.open(path) as src:
        arr = src.read(1).astype(np.float32)
        nd = src.nodata
        if nd is not None:
            arr = np.where(arr == nd, np.nan, arr)
        return arr, src.profile.copy()


def _write_raster(path: Path, arr: np.ndarray, profile: dict) -> None:
    import rasterio
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
    )
    with rasterio.open(path, "w", **p) as dst:
        dst.write(arr.astype(np.float32), 1)


def _cli() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--raw", required=True, help="P3 raw_prob GeoTIFF")
    p.add_argument("--qi", required=True, help="P4 ASTER QI 20m GeoTIFF")
    p.add_argument("--ci", required=True, help="P4 ASTER CI 20m GeoTIFF")
    p.add_argument("--out", required=True, help="final_confidence.tif çıktı yolu")
    p.add_argument("--report", default=None, help="opsiyonel JSON sanity rapor")
    args = p.parse_args()

    try:
        raw, raw_prof = _read_raster(Path(args.raw))
        qi, _ = _read_raster(Path(args.qi))
        ci, _ = _read_raster(Path(args.ci))
    except Exception as e:
        print(f"[err] read failed: {e}", file=sys.stderr)
        return 2

    try:
        final = fuse_confidence(raw, qi, ci)
    except SystemExit as e:
        print(f"[fail] {e}", file=sys.stderr)
        print("[planB] writing raw_prob unchanged as fallback", file=sys.stderr)
        final = np.clip(np.asarray(raw, dtype=np.float32), 0.0, 1.0)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _write_raster(out_path, final, raw_prof)

    # Sanity
    valid = final[np.isfinite(final)]
    raw_valid = np.asarray(raw)[np.isfinite(final)]
    report = {
        "raw_mean": float(np.nanmean(raw)),
        "final_mean": float(valid.mean()) if valid.size else None,
        "final_min": float(valid.min()) if valid.size else None,
        "final_max": float(valid.max()) if valid.size else None,
        "shape": list(final.shape),
        "delta_mean_raw_minus_final": (
            float((raw_valid - valid).mean()) if valid.size else None
        ),
        "out_path": str(out_path),
    }
    print(json.dumps(report, indent=2))
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
