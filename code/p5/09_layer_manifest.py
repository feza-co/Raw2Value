"""
P5 — T5.9 + T5.13: Layer ekleme orchestration + manifest.

5 katman (v2 § P5):
  1. S2 RGB ground truth                  (P1 T1.4)
  2. ASTER QI                             (P4 T4.6)
  3. S1 change                            (kendi T5.5)
  4. UNESCO buffer                        (kendi T5.2)
  5. P4 final_confidence.tif (FUSED)      (P4 T4.12)  ← T5.13 ana katman

Eğer P4 T4.12 saat 20'de bitmediyse Plan B: P3 RAW olasılığı + ASTER QI ayrı katman olarak.

Çıktı:
  - data/layers.json (manifest)
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "data" / "layers.json"

LAYER_SPECS = [
    {
        "id": "s2_rgb",
        "name": "Sentinel-2 RGB (ground truth)",
        "path": "data/ard/s2_rgb.tif",
        "owner": "P1",
        "task": "T1.4",
        "type": "raster_rgb",
        "default_visible": True,
        "opacity": 1.0,
    },
    {
        "id": "aster_qi",
        "name": "ASTER Ninomiya QI (B11²/(B10·B12))",
        "path": "data/ard/aster_qi.tif",
        "owner": "P4",
        "task": "T4.6",
        "type": "raster_continuous",
        "colormap": "viridis",
        "default_visible": False,
        "opacity": 0.7,
    },
    {
        "id": "s1_change",
        "name": "Sentinel-1 amplitude change (Mazza 2023)",
        "path": "data/change/s1_change.tif",
        "owner": "P5",
        "task": "T5.5",
        "type": "raster_categorical",
        "categories": {"0": "stable", "1": "increase", "2": "decrease"},
        "default_visible": False,
        "opacity": 0.6,
    },
    {
        "id": "unesco_buffer",
        "name": "UNESCO Göreme buffer (1000 m)",
        "path": "data/aoi/wdpa_goreme_buffer.gpkg",
        "owner": "P5",
        "task": "T5.2",
        "type": "vector_polygon",
        "style": {"color": "#d62728", "fill": False, "weight": 2, "dash": "5,5"},
        "default_visible": True,
    },
    {
        "id": "final_confidence",
        "name": "P4 FUSED final_confidence (T5.13 ana katman)",
        "path": "data/ard/final_confidence.tif",
        "owner": "P4",
        "task": "T4.12",
        "type": "raster_continuous",
        "colormap": "magma",
        "default_visible": True,
        "opacity": 0.75,
        "critical": True,
    },
]

# Plan B: P4 T4.12 fail
PLAN_B_LAYERS = [
    {
        "id": "p3_raw",
        "name": "P3 RAW pomza probability (Plan B — füzyon yok)",
        "path": "data/ard/p3_raw_prob.tif",
        "owner": "P3",
        "task": "T3.10",
        "type": "raster_continuous",
        "colormap": "magma",
        "default_visible": True,
        "opacity": 0.75,
        "fallback_for": "final_confidence",
    },
]


def build_manifest(plan_b: bool = False) -> dict:
    layers = list(LAYER_SPECS)
    if plan_b:
        # final_confidence yerine P3 RAW ve ASTER QI ayrı
        layers = [l for l in layers if l["id"] != "final_confidence"]
        for q in layers:
            if q["id"] == "aster_qi":
                q["default_visible"] = True
        layers.extend(PLAN_B_LAYERS)
    return {
        "version": "v2",
        "aoi": {"name": "Avanos", "epsg": 32636, "center_ll": [38.7167, 34.85]},
        "plan": "B" if plan_b else "A",
        "layers": layers,
        "annotations": {
            "historical_pomza_dir": "data/temporal/historical_pomza_overlay",
            "landsat_timelapse_gif": "data/temporal/landsat_timelapse.gif",
            "red_flags": "reports/red_flags.json",
            "kpi": "reports/kpi.json",
        },
    }


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Plan A varsayılan; final_confidence dosyası yoksa Plan B'ye otomatik düş.
    final_conf = PROJECT_ROOT / "data" / "ard" / "final_confidence.tif"
    plan_b = not final_conf.exists()
    if plan_b:
        print("[T5.13] UYARI: final_confidence.tif yok → Plan B (RAW + ayrı ASTER QI).")
    manifest = build_manifest(plan_b=plan_b)
    OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[T5.9/T5.13] manifest -> {OUT} (plan {manifest['plan']}, {len(manifest['layers'])} katman)")


if __name__ == "__main__":
    main()
