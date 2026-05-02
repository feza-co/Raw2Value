"""
T4.7 — Score-level füzyon **prototipi** (sentetik P3 output).

P3 RAW inference fn saat 17.5'te canlı olacak. Bu script o güne kadar API
contract'ı doğrulanabilsin diye sentetik bir `raw_prob` üretir, gerçek QI/CI
raster'larıyla birleştirir, `final_confidence` raster'ını yazar ve sanity
istatistiklerini raporlar.

Formül:
    final_confidence = raw_prob × QI_norm × (1 - CI_norm)

Sentetik raw_prob şeması:
    Gauss bump merkezi: pomza saha bbox'unun merkezi (kullanıcı verir)
    σ: AOI genişliğinin %15'i
    Maksimum: 0.92 (gerçekçi U-Net çıktısına benzer)
    Arka plan: uniform(0.0, 0.05) gürültü

Beklenen davranış (sanity):
  - QI yüksek + CI düşük bölgelerde final_confidence ≈ raw_prob
  - QI düşük (kuvars yok) → final_confidence çöker
  - CI yüksek (karbonat var) → final_confidence cezalanır
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import rasterio

# fuse_confidence içinde gerçek API; burada import edip kullanıyoruz
from fuse_confidence import fuse_confidence, percentile_minmax_norm


def synthetic_raw_prob(shape: tuple[int, int], center_xy: tuple[int, int], seed: int = 42) -> np.ndarray:
    """Gauss bump + uniform background — gerçek U-Net çıktısı taklidi."""
    rng = np.random.default_rng(seed)
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    cy, cx = center_xy
    sigma = 0.15 * max(h, w)
    bump = 0.92 * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * sigma ** 2))
    noise = rng.uniform(0.0, 0.05, size=shape)
    out = np.clip(bump + noise, 0.0, 1.0).astype(np.float32)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--qi", required=True, help="ASTER QI 20m GeoTIFF")
    p.add_argument("--ci", required=True, help="ASTER CI 20m GeoTIFF")
    p.add_argument(
        "--center",
        default=None,
        help="sentetik bump merkezi 'col,row' (default: raster ortası)",
    )
    p.add_argument("--out", default="data/layers/final_confidence_proto.tif")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    qi_path = Path(args.qi)
    ci_path = Path(args.ci)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(qi_path) as src_qi:
        qi = src_qi.read(1).astype(np.float32)
        qi_profile = src_qi.profile.copy()
    with rasterio.open(ci_path) as src_ci:
        ci = src_ci.read(1).astype(np.float32)

    if qi.shape != ci.shape:
        raise SystemExit(f"QI/CI shape mismatch: {qi.shape} vs {ci.shape}")

    h, w = qi.shape
    if args.center:
        cx, cy = (int(x) for x in args.center.split(","))
    else:
        cy, cx = h // 2, w // 2

    raw_prob = synthetic_raw_prob(qi.shape, center_xy=(cy, cx))
    final = fuse_confidence(raw_prob, qi, ci)

    # Yaz
    profile = qi_profile.copy()
    profile.update(
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
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(final, 1)

    # Sanity raporu
    valid = final[np.isfinite(final)]
    raw_valid = raw_prob[np.isfinite(final)]
    report = {
        "raw_prob_mean": float(raw_valid.mean()) if raw_valid.size else None,
        "final_mean": float(valid.mean()) if valid.size else None,
        "final_max": float(valid.max()) if valid.size else None,
        "delta_mean_raw_minus_final": float((raw_valid - valid).mean()) if valid.size else None,
        "qi_norm_mean": float(np.nanmean(percentile_minmax_norm(qi))),
        "ci_norm_mean": float(np.nanmean(percentile_minmax_norm(ci))),
        "out_path": str(out_path),
    }
    (out_path.parent / "fusion_proto_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f"[ok] prototype written → {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
