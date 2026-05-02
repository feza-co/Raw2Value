"""
T4.5 — ASTER Ninomiya indeksleri (KRİTİK — Karar #4 oran-tabanlı).

Indeksler:
  QI  = B11² / (B10 · B12)                     Quartz Index (Ninomiya 2003)
  CI  = B13 / B14                              Carbonate Index (Ninomiya 1995)
  SiO₂% ≈ a + b·QI                             Lineer estimator (Ninomiya 2003)

Bant referansı (ASTER TIR):
  B10  8.125–8.475 µm
  B11  8.475–8.825 µm
  B12  8.925–9.275 µm
  B13 10.250–10.950 µm
  B14 10.950–11.650 µm

QI mantığı: kuvars (SiO₂) B11'de güçlü emisivite minimumu (Reststrahlen) gösterir;
B11² pay → kuvarsa karşı kuvvetli yanıt; B10·B12 paydası "çevre normalleştirme"
yaparak atmosferik / yüzey-pürüzlülük etkisini iptal eder. Dolayısıyla **mutlak
radyans kalibrasyonu zorunlu değil** — Plan B (DOS başarısız) durumunda L1T
radiance ile çalışılır (Karar #4 dayanağı).

CI mantığı: karbonatlar B14'te derin emisivite minimumu yapar; B13/B14 oranı
yüksek → karbonat var → pomza olasılığı düşük (T4.12 füzyonunda 1-CI_norm
katsayısı ile cezalandırılır).

SiO₂ estimator (Ninomiya 2003 Table II, indicative):
  SiO₂% ≈ 56.2 + 12.4·log10(QI)         (ortalama curve, ±5% yorum payı)
  — Bu lineer log değil; kalibrasyon saha-bazlı; orchestrator'a "yorum amaçlı,
    karar girişi DEĞİL" işaretlenmeli.

Çıktı: data/layers/aster_{qi,ci,sio2}.tif (TIR native ~90 m grid)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import rasterio


# TIR multi-band stack içinde index (1-based)
TIR_BAND_INDEX = {"B10": 1, "B11": 2, "B12": 3, "B13": 4, "B14": 5}


def _safe_div(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    out = np.full_like(num, np.nan, dtype=np.float32)
    mask = np.isfinite(num) & np.isfinite(den) & (den > 0)
    out[mask] = num[mask] / den[mask]
    return out


def quartz_index(b10: np.ndarray, b11: np.ndarray, b12: np.ndarray) -> np.ndarray:
    """QI = B11² / (B10·B12). Ninomiya & Fu 2003."""
    return _safe_div(b11 * b11, b10 * b12)


def carbonate_index(b13: np.ndarray, b14: np.ndarray) -> np.ndarray:
    """CI = B13 / B14. Ninomiya 1995."""
    return _safe_div(b13, b14)


def sio2_estimator(qi: np.ndarray) -> np.ndarray:
    """Ninomiya 2003 lineer-log estimator (yorum amaçlı, karar girişi değil)."""
    out = np.full_like(qi, np.nan, dtype=np.float32)
    valid = np.isfinite(qi) & (qi > 0)
    out[valid] = 56.2 + 12.4 * np.log10(qi[valid])
    # mantıksız aralığı kırp
    out = np.clip(out, 30.0, 90.0)
    return out


def read_tir_stack(path: Path) -> tuple[np.ndarray, dict]:
    with rasterio.open(path) as src:
        if src.count < 5:
            raise SystemExit(
                f"TIR stack must have ≥5 bands (B10..B14); got {src.count} in {path}"
            )
        arr = src.read().astype(np.float32)  # (5, H, W)
        # NoData
        if src.nodata is not None:
            arr = np.where(arr == src.nodata, np.nan, arr)
        # Sıfırları da NoData kabul et (ASTER konvansiyonu)
        arr = np.where(arr == 0, np.nan, arr)
        profile = src.profile.copy()
    return arr, profile


def write_single_band(arr: np.ndarray, profile: dict, out_path: Path) -> None:
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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--tir", required=True, help="ASTER L2 TIR stack (5 band, B10..B14)")
    p.add_argument("--out", default="data/layers/")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    arr, profile = read_tir_stack(Path(args.tir))
    b10, b11, b12, b13, b14 = arr[0], arr[1], arr[2], arr[3], arr[4]

    qi = quartz_index(b10, b11, b12)
    ci = carbonate_index(b13, b14)
    sio2 = sio2_estimator(qi)

    write_single_band(qi, profile, out_dir / "aster_qi.tif")
    write_single_band(ci, profile, out_dir / "aster_ci.tif")
    write_single_band(sio2, profile, out_dir / "aster_sio2.tif")

    stats = {
        "qi": _stat(qi, expected_range=(0.5, 2.5)),
        "ci": _stat(ci, expected_range=(0.95, 1.10)),
        "sio2": _stat(sio2, expected_range=(40.0, 80.0)),
        "source_tir": str(args.tir),
        "academic_refs": [
            "Ninomiya & Fu 2003 — Quartz Index",
            "Ninomiya 1995 — Carbonate Index",
        ],
        "note": "Karar #4: oran-tabanlı, mutlak radyans kalibrasyonu gerektirmez.",
    }
    (out_dir / "aster_indices_stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))
    print(f"[ok] Ninomiya layers → {out_dir}/aster_{{qi,ci,sio2}}.tif")
    return 0


def _stat(arr: np.ndarray, expected_range: tuple[float, float] | None = None) -> dict:
    valid = arr[np.isfinite(arr)]
    if valid.size == 0:
        return {"min": None, "max": None, "mean": None, "valid_pct": 0.0}
    out = {
        "min": float(valid.min()),
        "max": float(valid.max()),
        "mean": float(valid.mean()),
        "valid_pct": round(float(valid.size / arr.size * 100), 2),
    }
    if expected_range is not None:
        lo, hi = expected_range
        in_range = float(((valid >= lo) & (valid <= hi)).mean())
        out["expected_range"] = [lo, hi]
        out["in_range_pct"] = round(in_range * 100, 2)
    return out


if __name__ == "__main__":
    raise SystemExit(main())
