"""
T4.10 — Layer-bazlı GeoTIFF (COG) export + manifest (`reports/layer_docs.md`).

Bu script tüm P4 ürünlerini tek manifest'te toplar:
  - layer adı
  - dosya yolu, boyut, MD5
  - bant açıklaması, formül, akademik referans
  - CRS, çözünürlük, NoData
  - tipik aralık + sanity threshold

Manifest hem JSON (P5'in `layers.json` Folium konfigürasyonu için) hem
Markdown (insan okuyabilir) yazar.

Kullanım:
    python 09_layer_export.py --root data/layers/ --reports reports/
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import rasterio

LAYER_SPEC: dict[str, dict[str, Any]] = {
    "s2_ndvi.tif": {
        "name": "S2 NDVI",
        "formula": "(B8 - B4) / (B8 + B4)",
        "ref": "Tucker 1979",
        "typical_range": [-0.2, 0.8],
        "interpretation": "Düşük NDVI → bare ground; pomza yığınları NDVI < 0.15 olur.",
    },
    "s2_bsi.tif": {
        "name": "S2 BSI (Bare Soil Index)",
        "formula": "((B11+B4)-(B8+B2))/((B11+B4)+(B8+B2))",
        "ref": "Rikimaru 2002",
        "typical_range": [-0.4, 0.6],
        "interpretation": "Yüksek BSI → çıplak toprak / kaya; pomza saha BSI > 0.15.",
    },
    "s2_albedo.tif": {
        "name": "S2 Albedo (Liang 2001 shortwave broadband)",
        "formula": "0.356·B2+0.130·B4+0.373·B8+0.085·B11+0.072·B12 - 0.0018",
        "ref": "Liang 2001",
        "typical_range": [0.10, 0.55],
        "interpretation": "Pomza yüksek albedo (0.30–0.45 tipik) — açık renk.",
    },
    "s2_sabins.tif": {
        "name": "S2 Sabins B11/B12 (clay/carbonate 2.2 µm)",
        "formula": "B11 / B12",
        "ref": "Sabins 1999",
        "typical_range": [0.7, 2.0],
        "interpretation": "B12 (2.19 µm) clay/carbonate hydroxyl absorption merkezi; B11/B12 yüksek → silikat/aluminoz mineraller (pomza dahil) baskın. Pomza tipik 1.1–1.5.",
    },
    "aster_qi.tif": {
        "name": "ASTER Quartz Index (Ninomiya)",
        "formula": "B11² / (B10·B12)",
        "ref": "Ninomiya & Fu 2003",
        "typical_range": [0.5, 2.5],
        "interpretation": "Pomza saha mean QI > 1.2 (kuvars + felsic glass).",
    },
    "aster_ci.tif": {
        "name": "ASTER Carbonate Index (Ninomiya)",
        "formula": "B13 / B14",
        "ref": "Ninomiya 1995",
        "typical_range": [0.95, 1.10],
        "interpretation": "Yüksek CI → karbonat → pomza olasılığı düşer.",
    },
    "aster_sio2.tif": {
        "name": "ASTER SiO₂% Estimator",
        "formula": "56.2 + 12.4·log10(QI)",
        "ref": "Ninomiya 2003 (indicative)",
        "typical_range": [40.0, 80.0],
        "interpretation": "Yorum amaçlı — karar girişi DEĞİL (kalibrasyon saha-bazlı).",
    },
    "aster_qi_20m.tif": {
        "name": "ASTER QI (20m S2 grid, bilinear)",
        "formula": "B11²/(B10·B12) → bilinear resample",
        "ref": "Ninomiya & Fu 2003 + Karar #15",
        "typical_range": [0.5, 2.5],
        "interpretation": "P4 fuse_confidence girdisi.",
    },
    "aster_ci_20m.tif": {
        "name": "ASTER CI (20m S2 grid, bilinear)",
        "formula": "B13/B14 → bilinear resample",
        "ref": "Ninomiya 1995 + Karar #15",
        "typical_range": [0.95, 1.10],
        "interpretation": "P4 fuse_confidence eksi-ağırlık girdisi.",
    },
    "dem_aspect.tif": {
        "name": "DEM Aspect (deg)",
        "formula": "gdaldem aspect (Horn 1981)",
        "ref": "Horn 1981",
        "typical_range": [0, 360],
        "interpretation": "Yüzey yön açısı; saha-eğimi cross-reference.",
    },
    "dem_hillshade.tif": {
        "name": "DEM Hillshade (az=315, alt=45)",
        "formula": "Lambertian; gdaldem hillshade",
        "ref": "Burrough 1986",
        "typical_range": [0, 255],
        "interpretation": "Görsel altlık.",
    },
    "final_confidence.tif": {
        "name": "P3×P4 Final Confidence (FUSED)",
        "formula": "raw_prob × QI_norm × (1 - CI_norm)",
        "ref": "Karar #6 (score-level fusion)",
        "typical_range": [0.0, 1.0],
        "interpretation": "**P5 T5.13 ana katmanı** — eşik 0.5 üstü pomza adayı.",
    },
}


def md5_of(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for blob in iter(lambda: f.read(chunk), b""):
            h.update(blob)
    return h.hexdigest()


def describe(path: Path) -> dict:
    with rasterio.open(path) as src:
        return {
            "path": str(path).replace("\\", "/"),
            "size_mb": round(path.stat().st_size / 1e6, 3),
            "md5": md5_of(path),
            "crs": src.crs.to_string() if src.crs else None,
            "width": src.width,
            "height": src.height,
            "res": [float(src.res[0]), float(src.res[1])],
            "bounds": list(src.bounds),
            "nodata": src.nodata,
            "dtype": str(src.dtypes[0]),
            "count": src.count,
        }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--root", default="data/layers/")
    p.add_argument("--reports", default="reports/")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    reports = Path(args.reports)
    reports.mkdir(parents=True, exist_ok=True)

    manifest: list[dict] = []
    for fname, spec in LAYER_SPEC.items():
        path = root / fname
        if not path.exists():
            print(f"[skip] missing: {path}")
            continue
        info = describe(path)
        info.update(spec)
        manifest.append(info)

    json_path = reports / "layers.json"
    json_path.write_text(json.dumps(manifest, indent=2))

    md_lines = ["# P4 Layer Manifest", ""]
    md_lines.append(
        "| Katman | Dosya | CRS | Çözünürlük | Aralık | Formül | Referans |"
    )
    md_lines.append("|---|---|---|---|---|---|---|")
    for L in manifest:
        md_lines.append(
            f"| {L['name']} | `{Path(L['path']).name}` | {L['crs']} | "
            f"{L['res'][0]:.0f} m | {L['typical_range']} | `{L['formula']}` | {L['ref']} |"
        )
    md_lines.append("")
    md_lines.append("## Yorum Notları")
    for L in manifest:
        md_lines.append(f"### {L['name']}")
        md_lines.append(f"- Yorum: {L['interpretation']}")
        md_lines.append(f"- MD5: `{L['md5']}`  ·  Boyut: {L['size_mb']} MB")
        md_lines.append("")
    (reports / "layer_docs.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(f"[ok] {len(manifest)} layer manifest → {json_path}")
    print(f"[ok] human-readable docs → {reports / 'layer_docs.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
