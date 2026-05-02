"""
Plan B — Manuel threshold-based pomza tespiti (fallback)
Modul A v2, P3 ML Muhendisi (Pomzadoya hackathon)

Aktive olur: T3.5 fine-tune yakinsamiyorsa veya P2 etiket gecikirse.

Akademik dayanak:
  - Sabins 1999 / van der Meer 2014 — SWIR (B11/B12) yansima esikleri
    pomza/silikat zenginlerini ayirir.
  - Liang 2001 — albedo formulu
        alpha = 0.356 B02 + 0.130 B04 + 0.373 B08 + 0.085 B11 + 0.072 B12 - 0.0018
    pomza yuksek albedo'lu (acik ton).
  - Ninomiya 2002 — QI = B11^2 / (B10 * B12) ASTER icin (P4 hesaplar).

Bu fallback yalnizca SENTINEL-2 + DEM kullanir, model gerektirmez.

Calistirma:
  python code/p3/12_fallback_threshold.py \
      --ard /data/ard/full_17band.tif \
      --output /reports/fallback_pomza_prob.tif \
      [--alpha-th 0.30] [--swir-ratio 0.95]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def liang_albedo(b02: np.ndarray, b04: np.ndarray, b08: np.ndarray,
                 b11: np.ndarray, b12: np.ndarray) -> np.ndarray:
    """Liang 2001 broadband albedo (Sentinel-2 reflectance girdileri ile)."""
    return (
        0.356 * b02 + 0.130 * b04 + 0.373 * b08
        + 0.085 * b11 + 0.072 * b12 - 0.0018
    )


def fallback_pomza_score(
    bands: dict,
    alpha_th: float = 0.30,
    swir_ratio_th: float = 0.95,
    bsi_min: float = 0.10,
) -> np.ndarray:
    """Albedo + SWIR ratio + BSI tabanli yumusak skor (raw [0, 1]).

    Args:
        bands: {"B02", "B04", "B08", "B11", "B12"} reflectance map'leri.
        alpha_th: albedo esigi (uzeri pomza adayi).
        swir_ratio_th: B11/B12 orani (van der Meer 2014).
        bsi_min: Bare Soil Index alt esigi (vejetasyon dislama).

    Returns:
        score : (H, W) float32 [0, 1]
    """
    b02, b04, b08, b11, b12 = (
        bands["B02"], bands["B04"], bands["B08"], bands["B11"], bands["B12"]
    )
    alpha = liang_albedo(b02, b04, b08, b11, b12)
    swir_ratio = b11 / np.maximum(b12, 1e-6)
    # BSI = ((B11+B04) - (B08+B02)) / ((B11+B04)+(B08+B02))
    bsi = ((b11 + b04) - (b08 + b02)) / np.maximum((b11 + b04) + (b08 + b02), 1e-6)

    # Yumusak gecis (sigmoid)
    def soft(x, th, k=20.0):
        return 1.0 / (1.0 + np.exp(-k * (x - th)))

    s_alpha = soft(alpha, alpha_th)
    s_swir = soft(swir_ratio, swir_ratio_th)
    s_bsi = soft(bsi, bsi_min)
    score = (s_alpha * s_swir * s_bsi).astype(np.float32)
    return np.clip(score, 0.0, 1.0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ard", required=True,
                        help="17 kanal ARD GeoTIFF (P1 T1.7 cikti)")
    parser.add_argument("--output", required=True,
                        help="RAW prob GeoTIFF cikis")
    parser.add_argument("--alpha-th", type=float, default=0.30)
    parser.add_argument("--swir-ratio", type=float, default=0.95)
    parser.add_argument("--bsi-min", type=float, default=0.10)
    parser.add_argument("--bands", default="2,4,8,11,12",
                        help="ARD icindeki B02,B04,B08,B11,B12 1-tabanli indeks")
    args = parser.parse_args()

    try:
        import rasterio
    except ImportError as e:
        raise SystemExit("rasterio gerekli.") from e

    idxs = [int(x) for x in args.bands.split(",")]
    if len(idxs) != 5:
        raise SystemExit("--bands tam olarak 5 indeks gerektirir (B02,B04,B08,B11,B12).")

    with rasterio.open(args.ard) as src:
        b02 = src.read(idxs[0]).astype(np.float32)
        b04 = src.read(idxs[1]).astype(np.float32)
        b08 = src.read(idxs[2]).astype(np.float32)
        b11 = src.read(idxs[3]).astype(np.float32)
        b12 = src.read(idxs[4]).astype(np.float32)
        profile = src.profile.copy()

    score = fallback_pomza_score(
        {"B02": b02, "B04": b04, "B08": b08, "B11": b11, "B12": b12},
        alpha_th=args.alpha_th,
        swir_ratio_th=args.swir_ratio,
        bsi_min=args.bsi_min,
    )

    profile.update(dtype="float32", count=1, compress="deflate", predictor=2)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(args.output, "w", **profile) as dst:
        dst.write(score, 1)
        dst.update_tags(
            P3_OUTPUT="RAW_PROBABILITY_FALLBACK",
            P3_NOTE="Plan B — albedo + SWIR ratio + BSI esikleri (Sabins 1999 / Liang 2001).",
            P3_RANGE="[0, 1]",
        )
    print(f"OK fallback -> {args.output}  range=[{score.min():.3f}, {score.max():.3f}]")


if __name__ == "__main__":
    main()
