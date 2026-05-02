"""
T3.7 — Ablation study runner (5 konfig)
Modul A v2, P3 ML Muhendisi (Pomzadoya hackathon)

5 konfigurasyon:
  1) full           : 17 kanal + SSL4EO pretrained
  2) rgb_only       : 3 kanal (B04, B03, B02) + ImageNet pretrained
  3) no_s1          : 15 kanal (S1 VV/VH yok)
  4) no_dem         : 15 kanal (DEM/slope yok)
  5) no_pretrained  : 17 kanal + random init

Her konfig icin 5-fold blok CV koş, mean IoU/F1 raporla.
Calistirma:
  python code/p3/09_ablation.py \
      --tile-dir /data/ard/tiles --full-mask /data/labels/full_mask.tif \
      --split-json /data/labels/blok_cv_split.json \
      --ssl4eo-ckpt /models/pretrained/B13_rn50_moco_0099_ckpt.pth \
      --output-dir /models/ablation --reports-dir /reports \
      --epochs 15 --folds 3   # ablation'da daha kisa fold/epoch onerilir
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np


CONFIGS = [
    {"name": "full",          "extra_args": []},
    {"name": "rgb_only",      "extra_args": ["--rgb-only"]},
    {"name": "no_s1",         "extra_args": ["--in-channels", "15"],
     "note": "ARD'den S1 VV/VH dropla (P1 manifest sub-sample gerekli)"},
    {"name": "no_dem",        "extra_args": ["--in-channels", "15"],
     "note": "ARD'den DEM/slope dropla"},
    {"name": "no_pretrained", "extra_args": ["--no-pretrained"]},
]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--tile-dir", required=True)
    p.add_argument("--full-mask", required=True)
    p.add_argument("--split-json", required=True)
    p.add_argument("--ssl4eo-ckpt", default=None)
    p.add_argument("--output-dir", default="/models/ablation")
    p.add_argument("--reports-dir", default="/reports")
    p.add_argument("--epochs", type=int, default=15)
    p.add_argument("--folds", type=int, default=3,
                   help="Ablation'da fold sayisini dusur (zaman kazan)")
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--amp", action="store_true")
    p.add_argument("--skip", nargs="*", default=[],
                   help="Atlanacak konfig isimleri")
    return p.parse_args()


def run_config(cfg: dict, base_args, train_script: Path) -> dict:
    name = cfg["name"]
    out_dir = Path(base_args.output_dir) / name
    out_dir.mkdir(parents=True, exist_ok=True)
    reports_dir = Path(base_args.reports_dir) / "ablation" / name
    reports_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, str(train_script),
        "--tile-dir", base_args.tile_dir,
        "--full-mask", base_args.full_mask,
        "--split-json", base_args.split_json,
        "--output-dir", str(out_dir),
        "--reports-dir", str(reports_dir),
        "--epochs", str(base_args.epochs),
        "--folds", str(base_args.folds),
        "--batch-size", str(base_args.batch_size),
        "--lr", str(base_args.lr),
    ]
    if base_args.ssl4eo_ckpt and "--no-pretrained" not in cfg["extra_args"]:
        cmd.extend(["--ssl4eo-ckpt", base_args.ssl4eo_ckpt])
    if base_args.amp:
        cmd.append("--amp")
    cmd.extend(cfg["extra_args"])

    print("\n" + "#" * 60)
    print(f"# Ablation: {name}")
    print(f"# CMD: {' '.join(cmd)}")
    print("#" * 60)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[{name}] HATA: {e}")
        return {"name": name, "error": str(e)}

    metrics_json = reports_dir / "metrics_5fold.json"
    if not metrics_json.exists():
        return {"name": name, "error": "metrics_5fold.json bulunamadi"}
    with open(metrics_json) as f:
        m = json.load(f)
    return {
        "name": name,
        "mean_iou": m["mean_iou"],
        "std_iou": m["std_iou"],
        "min_iou": m["min_iou"],
        "max_iou": m["max_iou"],
        "fold_count": len(m["folds"]),
    }


def main():
    args = parse_args()
    train_script = Path(__file__).resolve().parent / "06_train.py"
    if not train_script.exists():
        sys.exit(f"06_train.py bulunamadi: {train_script}")

    results = []
    for cfg in CONFIGS:
        if cfg["name"] in args.skip:
            print(f"[skip] {cfg['name']}")
            continue
        results.append(run_config(cfg, args, train_script))

    # Markdown rapor
    md_lines = [
        "# P3 Ablation Study (T3.7) — 5 Konfig\n",
        f"_Modul A v2, fold={args.folds}, epochs={args.epochs}_\n\n",
        "| Konfig | Mean IoU | Std IoU | Min IoU | Max IoU |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in results:
        if "error" in r:
            md_lines.append(f"| {r['name']} | ERROR | — | — | — |")
        else:
            md_lines.append(
                f"| {r['name']} | {r['mean_iou']:.3f} | {r['std_iou']:.3f} | "
                f"{r['min_iou']:.3f} | {r['max_iou']:.3f} |"
            )

    md_lines.extend([
        "\n## Yorum",
        "- **full** baseline. Diger satirlar bu satira gore relative degerlendirilmeli.",
        "- **rgb_only**: SAR + DEM katkisi yok. IoU dususu pozitif kanitidir multi-modal'in.",
        "- **no_s1**: Bulutsuz gun bilesimi varsa kucuk, bulutlu sezonda büyük dusus.",
        "- **no_dem**: Topografik prior etkisi.",
        "- **no_pretrained**: SSL4EO-S12 transferin etkisi (Karar #2).",
    ])
    out_md = Path(args.reports_dir) / "ablation.md"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md_lines), encoding="utf-8")

    out_json = Path(args.reports_dir) / "ablation.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nOK -> {out_md}")
    print(f"OK -> {out_json}")


if __name__ == "__main__":
    main()
