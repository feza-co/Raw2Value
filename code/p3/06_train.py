"""
T3.5 — U-Net + SSL4EO-S12 fine-tune (5-fold spatial blok CV)
Modul A v2, P3 ML Muhendisi (Pomzadoya hackathon)

Karar referansi: [K#1] U-Net, [K#2] SSL4EO pretrained, [K#10] spatial blok CV.

CRITICAL PATH (saat 12-15). Plan B: --rgb-only veya --no-pretrained flag'leri.

Calistirma (Colab/Kaggle):
  python code/p3/06_train.py \
      --tile-dir /content/drive/MyDrive/pomzadoya/data/ard/tiles \
      --full-mask /content/drive/MyDrive/pomzadoya/data/labels/full_mask.tif \
      --split-json /content/drive/MyDrive/pomzadoya/data/labels/blok_cv_split.json \
      --ssl4eo-ckpt /content/drive/MyDrive/pomzadoya/models/pretrained/B13_rn50_moco_0099_ckpt.pth \
      --output-dir /content/drive/MyDrive/pomzadoya/models \
      --epochs 30 --batch-size 8 --lr 1e-4 --folds 5 \
      [--wandb]  # WANDB_API_KEY env varsa aktif

Cikti:
  /models/unet_pomza_ssl4eo_fold{0..4}.pt
  /reports/metrics_5fold.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from importlib import import_module
from pathlib import Path

import numpy as np
import torch
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

sys.path.insert(0, str(Path(__file__).resolve().parent))
ssl4eo_mod = import_module("02_ssl4eo_pretrained")
dm_mod = import_module("03_datamodule")
loss_mod = import_module("04_loss_metrics")

build_ssl4eo_unet = ssl4eo_mod.build_ssl4eo_unet
PomzaDataModule = dm_mod.PomzaDataModule
default_train_aug = dm_mod.default_train_aug
default_val_aug = dm_mod.default_val_aug
BCEDiceLoss = loss_mod.BCEDiceLoss
MetricAccumulator = loss_mod.MetricAccumulator


# -----------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--tile-dir", default=None,
                   help="Manifest tiles_dir override (opsiyonel — manifest yoksa zorunlu).")
    p.add_argument("--full-mask", required=True)
    p.add_argument("--split-json", required=True)
    p.add_argument("--manifest-json", required=True,
                   help="P1 data/manifest.json — sözleşme zorunlu (DEFAULT fallback yok).")
    p.add_argument("--ssl4eo-ckpt", default=None,
                   help="SSL4EO-S12 .pth (yoksa random init)")
    p.add_argument("--output-dir", default="/models")
    p.add_argument("--reports-dir", default="/reports")
    p.add_argument("--in-channels", type=int, default=17)
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--start-fold", type=int, default=0)
    p.add_argument("--bce-weight", type=float, default=0.5)
    p.add_argument("--pos-weight", type=float, default=None)
    p.add_argument("--amp", action="store_true", help="Mixed precision (FP16)")
    p.add_argument("--wandb", action="store_true",
                   help="W&B aktif (WANDB_API_KEY env gerekli)")
    p.add_argument("--seed", type=int, default=42)
    # Plan B
    p.add_argument("--rgb-only", action="store_true",
                   help="Plan B: yalnizca 3 RGB kanal (B04, B03, B02)")
    p.add_argument("--no-pretrained", action="store_true",
                   help="Plan B: SSL4EO yukleme")
    return p.parse_args()


def maybe_init_wandb(args, fold: int):
    if not args.wandb:
        return None
    if not os.environ.get("WANDB_API_KEY"):
        print("[W&B] WANDB_API_KEY env yok — atliyor.")
        return None
    try:
        import wandb
    except ImportError:
        print("[W&B] paket yok — atliyor.")
        return None
    run = wandb.init(
        project="pomzadoya-modulA",
        name=f"unet_ssl4eo_fold{fold}",
        config=vars(args),
        reinit=True,
    )
    return run


def train_one_fold(args, fold: int, device: torch.device) -> dict:
    print("\n" + "=" * 60)
    print(f" FOLD {fold} / {args.folds - 1}")
    print("=" * 60)

    # DataModule
    dm = PomzaDataModule(
        tile_dir=args.tile_dir,
        full_mask=args.full_mask,
        split_json=args.split_json,
        manifest_json=args.manifest_json,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        train_aug=default_train_aug(),
        val_aug=default_val_aug(),
        in_channels=args.in_channels,
    )
    dm.set_fold(fold)
    train_loader = dm.train_dataloader()
    val_loader = dm.val_dataloader()
    print(f"[DM] train={len(train_loader.dataset)} val={len(val_loader.dataset)}")

    # Model
    in_ch = 3 if args.rgb_only else args.in_channels
    ckpt = None if args.no_pretrained else args.ssl4eo_ckpt
    model = build_ssl4eo_unet(
        num_classes=1,
        in_channels=in_ch,
        ssl4eo_ckpt=ckpt,
    ).to(device)

    # Optimizer + scheduler
    optimizer = AdamW(model.parameters(), lr=args.lr,
                      weight_decay=args.weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=args.lr * 0.01)

    criterion = BCEDiceLoss(bce_weight=args.bce_weight,
                            pos_weight=args.pos_weight,
                            ignore_index=255)

    scaler = torch.amp.GradScaler('cuda', enabled=args.amp and device.type == "cuda")

    wandb_run = maybe_init_wandb(args, fold)

    best_iou = -1.0
    best_path = Path(args.output_dir) / f"unet_pomza_ssl4eo_fold{fold}.pt"
    best_path.parent.mkdir(parents=True, exist_ok=True)
    epoch_log = []

    for epoch in range(args.epochs):
        # ---- Train ----
        model.train()
        t0 = time.time()
        train_loss_sum, n_batches = 0.0, 0
        for x, y in train_loader:
            x = x.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)
            if args.rgb_only:
                # B04, B03, B02 (S2 L2A indeksleri 3, 2, 1)
                x = x[:, [3, 2, 1], :, :]
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast('cuda', enabled=args.amp and device.type == "cuda"):
                logits = model(x)
                loss = criterion(logits, y)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            scaler.step(optimizer)
            scaler.update()
            train_loss_sum += loss.item()
            n_batches += 1
        scheduler.step()
        train_loss = train_loss_sum / max(n_batches, 1)

        # ---- Validate ----
        model.eval()
        acc = MetricAccumulator(ignore_index=255)
        val_loss_sum, n_val = 0.0, 0
        with torch.no_grad():
            for x, y in val_loader:
                x = x.to(device, non_blocking=True)
                y = y.to(device, non_blocking=True)
                if args.rgb_only:
                    x = x[:, [3, 2, 1], :, :]
                with torch.amp.autocast('cuda', enabled=args.amp and device.type == "cuda"):
                    logits = model(x)
                    loss = criterion(logits, y)
                val_loss_sum += loss.item(); n_val += 1
                probs = torch.sigmoid(logits).squeeze(1).cpu().numpy()
                acc.update(probs, y.cpu().numpy())
        val_loss = val_loss_sum / max(n_val, 1)
        m05 = acc.metrics(threshold=0.5)
        sweep = acc.threshold_sweep()
        dt = time.time() - t0

        log_row = {
            "epoch": epoch, "train_loss": train_loss, "val_loss": val_loss,
            "val_iou_05": m05.iou, "val_f1_05": m05.f1,
            "val_iou_best": sweep["best_iou"],
            "val_f1_best": sweep["best_f1"],
            "best_thr": sweep["best_threshold"],
            "lr": optimizer.param_groups[0]["lr"],
            "time_s": round(dt, 1),
        }
        epoch_log.append(log_row)
        print(f"E{epoch:02d} | train={train_loss:.4f} val={val_loss:.4f} | "
              f"IoU@.5={m05.iou:.3f} F1@.5={m05.f1:.3f} | "
              f"IoU*={sweep['best_iou']:.3f} F1*={sweep['best_f1']:.3f}@thr{sweep['best_threshold']:.2f} | "
              f"{dt:.1f}s")

        if wandb_run is not None:
            wandb_run.log(log_row)

        # Best checkpoint (val IoU @ best threshold)
        if sweep["best_iou"] > best_iou:
            best_iou = sweep["best_iou"]
            torch.save({
                "model_state": model.state_dict(),
                "fold": fold,
                "epoch": epoch,
                "metrics": log_row,
                "best_threshold": sweep["best_threshold"],
                "args": vars(args),
            }, best_path)
            print(f"  -> Yeni best (IoU*={best_iou:.3f}). Kaydedildi: {best_path.name}")

    if wandb_run is not None:
        wandb_run.finish()

    return {
        "fold": fold,
        "best_iou": best_iou,
        "ckpt_path": str(best_path),
        "epoch_log": epoch_log,
    }


def main():
    args = parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[ENV] device={device}, AMP={args.amp}")

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    Path(args.reports_dir).mkdir(parents=True, exist_ok=True)

    fold_results = []
    for k in range(args.start_fold, args.folds):
        try:
            res = train_one_fold(args, k, device)
            fold_results.append(res)
        except Exception as e:
            print(f"[FOLD {k}] HATA: {e}")
            raise

    # Aggregate
    ious = [r["best_iou"] for r in fold_results]
    summary = {
        "folds": fold_results,
        "mean_iou": float(np.mean(ious)),
        "std_iou": float(np.std(ious)),
        "min_iou": float(np.min(ious)),
        "max_iou": float(np.max(ious)),
        "args": vars(args),
    }
    out_json = Path(args.reports_dir) / "metrics_5fold.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print("\n" + "=" * 60)
    print(f" 5-fold mean IoU = {summary['mean_iou']:.3f} ± {summary['std_iou']:.3f}")
    print(f" Rapor: {out_json}")
    print("=" * 60)


if __name__ == "__main__":
    main()
