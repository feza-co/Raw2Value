"""
P5 — T5.10: Historical pomza inference (RAW).

v2 KRİTİK AYRIM:
  - T5.10 (bu dosya): Historical Landsat snapshots → P3 RAW olasılık + sabit threshold (0.5).
    Kontemporanöz ASTER yok → füzyon yapılamaz.
  - T5.13 (current): P4 final_confidence.tif (FUSED). Bu dosyaya KARIŞTIRILMAZ.

Akış:
  1. 06_landsat_roy_harmonization.py çıktısı (OLI-equivalent) yıl bazında okunur.
  2. P3 inference modülü (predict_raw) import edilir → RAW probability raster.
  3. Threshold 0.5 (RAW için sabit) → binary mask.
  4. Mask vectorize → polygon (yıllık tespit overlay).
  5. Yıllık alan (ha) hesaplanır.

Çıktı:
  - data/temporal/historical_pomza_overlay/<year>_raw_prob.tif
  - data/temporal/historical_pomza_overlay/<year>_pomza.gpkg
  - reports/historical_pomza_summary.json
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HARM_DIR = PROJECT_ROOT / "data" / "temporal" / "landsat_harmonized"
OUT_DIR = PROJECT_ROOT / "data" / "temporal" / "historical_pomza_overlay"
OUT_REPORT = PROJECT_ROOT / "reports" / "historical_pomza_summary.json"

# P3 inference modülünü import et (T3.10)
P3_PATH = PROJECT_ROOT / "code" / "p3"
if str(P3_PATH) not in sys.path:
    sys.path.insert(0, str(P3_PATH))

THRESHOLD_RAW = 0.5  # T5.10: RAW için sabit (P3 T3.6 F1-max threshold T5.13'te kullanılır)


def _try_import_p3():
    """P3 inference fn'i. Eğer P3 daha export etmediyse mock dön."""
    try:
        from inference import predict_raw  # type: ignore
        return predict_raw
    except Exception as exc:
        print(f"[T5.10] P3 inference fn import edilemedi ({exc}). Mock kullanılıyor.")
        return _mock_predict_raw


def _mock_predict_raw(image_chw: np.ndarray) -> np.ndarray:
    """Mock: SWIR1/SWIR2 oranı + albedo proxy ile basit pomza ihtimal raster.
    Üretim kodunda P3 T3.10 predict_raw kullanılır.
    """
    # band order: blue, green, red, nir, swir1, swir2
    swir1 = image_chw[4].astype("float32")
    swir2 = image_chw[5].astype("float32")
    red = image_chw[2].astype("float32")
    eps = 1e-3
    bsi = ((swir1 + red) - (image_chw[3] + image_chw[0])) / (
        (swir1 + red) + (image_chw[3] + image_chw[0]) + eps
    )
    swir_ratio = swir1 / (swir2 + eps)
    # Pomza tipik: yüksek albedo, BSI yüksek, SWIR1/SWIR2 ~1.05-1.15
    score = (np.clip(bsi, -1, 1) + 1) / 2 * 0.5 + np.clip((swir_ratio - 0.95) / 0.25, 0, 1) * 0.5
    return np.clip(score, 0.0, 1.0).astype("float32")


def vectorize(mask: np.ndarray, transform, crs) -> list:
    """Binary mask → polygon listesi."""
    polys = []
    for geom, val in shapes(mask.astype("uint8"), mask=mask.astype(bool), transform=transform):
        if val == 1:
            polys.append(shape(geom))
    return polys


def process_year(tif: Path, year: int, predict_fn) -> dict:
    with rasterio.open(tif) as src:
        img = src.read().astype("float32")
        transform = src.transform
        crs = src.crs
        profile = src.profile.copy()

    prob = predict_fn(img)
    if prob.shape != img.shape[1:]:
        raise ValueError(f"predict_raw output shape mismatch: {prob.shape} vs {img.shape[1:]}")

    mask = (prob >= THRESHOLD_RAW).astype("uint8")
    polys = vectorize(mask, transform, crs)

    out_prob = OUT_DIR / f"{year}_raw_prob.tif"
    out_gpkg = OUT_DIR / f"{year}_pomza.gpkg"

    profile.update(count=1, dtype="float32", compress="deflate", nodata=-9999)
    with rasterio.open(out_prob, "w", **profile) as dst:
        dst.write(prob, 1)

    if polys:
        import geopandas as gpd
        gdf = gpd.GeoDataFrame(
            {"year": [year] * len(polys)}, geometry=polys, crs=crs
        )
        gdf.to_file(out_gpkg, driver="GPKG")
        # Alan UTM zaten (Avanos EPSG:32636)
        if gdf.crs and gdf.crs.is_geographic:
            gdf_m = gdf.to_crs(32636)
        else:
            gdf_m = gdf
        area_ha = float(gdf_m.area.sum() / 10_000.0)
    else:
        area_ha = 0.0

    return {
        "year": year,
        "raw_prob": str(out_prob),
        "polygons": str(out_gpkg) if polys else None,
        "n_polygons": len(polys),
        "area_ha": area_ha,
        "threshold": THRESHOLD_RAW,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)

    predict_fn = _try_import_p3()

    files = sorted(HARM_DIR.glob("*_OLIeq.tif"))
    if not files:
        raise FileNotFoundError(f"Harmonize Landsat yok: {HARM_DIR}")

    summary = []
    for f in files:
        m = re.search(r"(\d{4})", f.stem)
        if not m:
            continue
        year = int(m.group(1))
        print(f"[T5.10] {year} -> RAW inference + vectorize")
        try:
            entry = process_year(f, year, predict_fn)
        except Exception as exc:
            entry = {"year": year, "error": str(exc)}
        summary.append(entry)

    OUT_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[T5.10] -> {OUT_REPORT}")
    for e in summary:
        if "area_ha" in e:
            print(f"  {e['year']}: {e['area_ha']:.1f} ha ({e['n_polygons']} polygon)")


if __name__ == "__main__":
    main()
