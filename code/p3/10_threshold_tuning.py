"""
T3.6 — F1-max threshold tuning + curve raporu
Modul A v2, P3 ML Muhendisi (Pomzadoya hackathon)

Karar referansi: [K#14] sabit 0.5 yerine F1-max threshold

ONEMLI: Bu threshold P3 inference fn icinde uygulanmaz (Karar #6).
P3 RAW prob dondurur. Threshold yalnizca:
  (a) Validation metric raporu icin
  (b) P5 historical Landsat Tier 2 icin (P5 secimi)
  (c) Kullaniciya gosterilen "binary maske" demo katmani icin (P5 Streamlit)

Calistirma:
  python code/p3/10_threshold_tuning.py \
      --model /models/unet_pomza_ssl4eo_fold0.pt \
      --tile-dir /data/ard/tiles --full-mask /data/labels/full_mask.tif \
      --split-json /data/labels/blok_cv_split.json \
      --output /reports/threshold_curve.json
"""
from __future__ import annotations

import argparse
import json
import sys
from importlib import import_module
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
dm_mod = import_module("03_datamodule")
loss_mod = import_module("04_loss_metrics")
inf_mod = import_module("07_inference")

PomzaDataModule = dm_mod.PomzaDataModule
default_val_aug = dm_mod.default_val_aug
threshold_sweep = loss_mod.threshold_sweep
MetricAccumulator = loss_mod.MetricAccumulator
load_model = inf_mod.load_model


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--tile-dir", required=True)
    p.add_argument("--full-mask", required=True)
    p.add_argument("--split-json", required=True)
    p.add_argument("--manifest-json", default=None)
    p.add_argument("--fold", type=int, default=0,
                   help="Hangi fold'un val seti kullanilsin")
    p.add_argument("--folds-all", action="store_true",
                   help="Tum fold'lari topla (concatenated curve)")
    p.add_argument("--in-channels", type=int, default=17)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--output", default="/reports/threshold_curve.json")
    p.add_argument("--n-points", type=int, default=37,
                   help="Threshold cozunurlugu (0.05..0.95 arasinda)")
    return p.parse_args()


def main():
    args = parse_args()
    device = torch.device(args.device)
    model = load_model(args.model, in_channels=args.in_channels, device=str(device))

    dm = PomzaDataModule(
        tile_dir=args.tile_dir,
        full_mask=args.full_mask,
        split_json=args.split_json,
        manifest_json=args.manifest_json,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        train_aug=None,
        val_aug=default_val_aug(),
        in_channels=args.in_channels,
    )

    folds = list(range(dm.fold_count)) if args.folds_all else [args.fold]
    acc = MetricAccumulator(ignore_index=255)

    for k in folds:
        dm.set_fold(k)
        loader = dm.val_dataloader()
        with torch.no_grad():
            for x, y in loader:
                x = x.to(device, non_blocking=True)
                logits = model(x)
                probs = torch.sigmoid(logits).squeeze(1).cpu().numpy()
                acc.update(probs, y.numpy())
        print(f"[fold {k}] biriktirildi. n_pixel={acc._n}")

    thresholds = np.linspace(0.05, 0.95, args.n_points)
    sweep = acc.threshold_sweep(thresholds=thresholds)
    sweep["folds_evaluated"] = folds
    sweep["model"] = str(args.model)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(sweep, f, indent=2)

    print("=" * 60)
    print(f" Best threshold = {sweep['best_threshold']:.3f}")
    print(f" Best F1        = {sweep['best_f1']:.3f}")
    print(f" Best IoU       = {sweep['best_iou']:.3f}")
    print(f" Curve -> {out}")
    print("=" * 60)


if __name__ == "__main__":
    main()
