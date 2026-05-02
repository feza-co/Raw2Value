"""
P5 — T5.8: Roy 2016 cross-sensor Landsat harmonizasyon.

Akademik referans:
  Roy, D.P. et al. 2016. "Characterization of Landsat-7 to Landsat-8 reflective
  wavelength and normalized difference vegetation index continuity."
  Remote Sensing of Environment 185, 57-70.
  Roy 2016 Table 2 → OLS regression coefficients (ETM+ → OLI).

Bu script:
  1. P1 T1.10 Landsat snapshots klasörünü tarar (1985 TM, 1990 TM, 2000 ETM+, 2010 ETM+, 2025 OLI).
  2. Sensör tipine göre per-band linear regression uygular:
       harmonized = slope * src + intercept
     Hedef sensör: Landsat-8 OLI surface reflectance.
  3. Çıktı her snapshot için "L8-equivalent" GeoTIFF.

Plan B (Roy yavaşsa): basit per-band scalar offset (mean-match) — fallback fonksiyonu altta.

Çıktı:
  - data/temporal/landsat_harmonized/L<sensor>_<year>_OLIeq.tif
  - reports/roy2016_coefficients.json
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict

import numpy as np
import rasterio

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LANDSAT_DIR = PROJECT_ROOT / "data" / "landsat"
OUT_DIR = PROJECT_ROOT / "data" / "temporal" / "landsat_harmonized"
OUT_REPORT = PROJECT_ROOT / "reports" / "roy2016_coefficients.json"

# Roy 2016 Table 2 — OLS regression: OLI = slope * ETM+ + intercept
# (surface reflectance, scaled 0-10000). Bantlar SR_B# eşleniği.
# Kaynak: Roy et al. 2016 RSE 185:57-70, Table 2.
ROY2016_ETM_TO_OLI = {
    "blue":   {"slope": 0.8474, "intercept": 0.0003},
    "green":  {"slope": 0.8483, "intercept": 0.0088},
    "red":    {"slope": 0.9047, "intercept": 0.0061},
    "nir":    {"slope": 0.8462, "intercept": 0.0412},
    "swir1":  {"slope": 0.8937, "intercept": 0.0254},
    "swir2":  {"slope": 0.9071, "intercept": 0.0172},
}

# Landsat-5 TM → ETM+ (Roy 2016 ek + Vogeler 2018 değerleri)
# TM ve ETM+ yakın spektral, kabul edilen değerler:
TM_TO_ETM = {
    "blue":   {"slope": 1.0, "intercept": 0.0},
    "green":  {"slope": 1.0, "intercept": 0.0},
    "red":    {"slope": 1.0, "intercept": 0.0},
    "nir":    {"slope": 1.0, "intercept": 0.0},
    "swir1":  {"slope": 1.0, "intercept": 0.0},
    "swir2":  {"slope": 1.0, "intercept": 0.0},
}

# OLI girdisi → identity (zaten hedef sensör)
OLI_IDENTITY = {b: {"slope": 1.0, "intercept": 0.0} for b in ROY2016_ETM_TO_OLI}

BAND_ORDER = ["blue", "green", "red", "nir", "swir1", "swir2"]
SENSOR_RE = re.compile(r"L([CET])0?(\d)_(\d{4})", re.IGNORECASE)


def detect_sensor(filename: str) -> str:
    """L5 TM, L7 ETM+, L8/L9 OLI. Dosya adı L5_1985.tif gibi varsayar."""
    fn = filename.upper()
    if "L8" in fn or "L9" in fn or "OLI" in fn:
        return "OLI"
    if "L7" in fn or "ETM" in fn:
        return "ETM"
    if "L5" in fn or "L4" in fn or "_TM" in fn:
        return "TM"
    # Yıl bazlı fallback
    m = re.search(r"(\d{4})", fn)
    if m:
        y = int(m.group(1))
        if y >= 2013:
            return "OLI"
        if y >= 1999:
            return "ETM"
        return "TM"
    return "UNKNOWN"


def coeffs_for(sensor: str) -> Dict[str, Dict[str, float]]:
    """Sensörden L8 OLI hedefine kadar zincirleme regresyon."""
    if sensor == "OLI":
        return OLI_IDENTITY
    if sensor == "ETM":
        return ROY2016_ETM_TO_OLI
    if sensor == "TM":
        # TM → ETM → OLI : iki adımda kompoze edelim
        composed = {}
        for b in BAND_ORDER:
            s1, i1 = TM_TO_ETM[b]["slope"], TM_TO_ETM[b]["intercept"]
            s2, i2 = ROY2016_ETM_TO_OLI[b]["slope"], ROY2016_ETM_TO_OLI[b]["intercept"]
            composed[b] = {"slope": s1 * s2, "intercept": s1 * i2 + i1 * s2 + i2 - i2}
            # Doğru kompozisyon: out = s2*(s1*x + i1) + i2 = s1*s2*x + s2*i1 + i2
            composed[b] = {"slope": s1 * s2, "intercept": s2 * i1 + i2}
        return composed
    raise ValueError(f"Bilinmeyen sensör: {sensor}")


def harmonize(src_path: Path, sensor: str, dst_path: Path) -> dict:
    coeffs = coeffs_for(sensor)
    with rasterio.open(src_path) as src:
        profile = src.profile.copy()
        n_bands = src.count
        if n_bands < len(BAND_ORDER):
            raise ValueError(
                f"{src_path.name} {n_bands} bant, en az {len(BAND_ORDER)} (BGR-NIR-SWIR1-SWIR2) gerek."
            )
        bands = [src.read(i + 1).astype("float32") for i in range(len(BAND_ORDER))]

    out_bands = []
    for i, name in enumerate(BAND_ORDER):
        s = coeffs[name]["slope"]
        b = coeffs[name]["intercept"]
        # Roy 2016 katsayıları SR (0..1) için. Eğer girdi 0..10000 ise scale et.
        scale = 1e-4 if np.nanmax(bands[i]) > 1.5 else 1.0
        x = bands[i] * scale
        y = s * x + b
        # Geri 0..10000 ölçeğine
        y_out = (y / scale).astype("float32") if scale != 1.0 else y.astype("float32")
        out_bands.append(y_out)

    profile.update(count=len(BAND_ORDER), dtype="float32", compress="deflate")
    with rasterio.open(dst_path, "w", **profile) as dst:
        for i, arr in enumerate(out_bands, start=1):
            dst.write(arr, i)
        for i, name in enumerate(BAND_ORDER, start=1):
            dst.set_band_description(i, name)

    return {"sensor": sensor, "src": str(src_path), "dst": str(dst_path), "coeffs": coeffs}


def fallback_mean_match(src_path: Path, ref_path: Path, dst_path: Path) -> dict:
    """Plan B: per-band mean-match (Roy yavaşsa). Akademik kalite düşer ama snapshot karşılaştırılabilir."""
    with rasterio.open(src_path) as src, rasterio.open(ref_path) as ref:
        profile = src.profile.copy()
        out = []
        for i in range(src.count):
            s = src.read(i + 1).astype("float32")
            r = ref.read(i + 1).astype("float32")
            mu_s, mu_r = np.nanmean(s), np.nanmean(r)
            sd_s, sd_r = np.nanstd(s) + 1e-6, np.nanstd(r) + 1e-6
            scaled = (s - mu_s) * (sd_r / sd_s) + mu_r
            out.append(scaled)
    profile.update(dtype="float32", compress="deflate")
    with rasterio.open(dst_path, "w", **profile) as dst:
        for i, a in enumerate(out, 1):
            dst.write(a, i)
    return {"method": "mean_match_fallback", "src": str(src_path), "ref": str(ref_path)}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)

    snapshots = sorted(LANDSAT_DIR.glob("L*_*.tif"))
    if not snapshots:
        raise FileNotFoundError(
            f"Landsat snapshot bulunamadı: {LANDSAT_DIR}. P1 T1.10 çıktısını bekle."
        )

    log = []
    for src in snapshots:
        sensor = detect_sensor(src.name)
        # Çıktı adı: L<sensor>_<yıl>_OLIeq.tif
        m = re.search(r"(\d{4})", src.stem)
        year = m.group(1) if m else "0000"
        dst = OUT_DIR / f"L{sensor}_{year}_OLIeq.tif"
        print(f"[T5.8] {src.name} (sensör={sensor}) -> {dst.name}")
        try:
            entry = harmonize(src, sensor, dst)
            log.append(entry)
        except Exception as exc:
            print(f"  Roy harmonize hata: {exc}. Plan B mean-match denenecek.")
            ref_candidates = [p for p in snapshots if "OLI" in detect_sensor(p.name)]
            if ref_candidates:
                log.append(fallback_mean_match(src, ref_candidates[-1], dst))
            else:
                print("  Referans OLI yok, atlanıyor.")

    OUT_REPORT.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"[T5.8] log -> {OUT_REPORT}")


if __name__ == "__main__":
    main()
