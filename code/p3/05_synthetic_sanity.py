"""
T3.3 — Sentetik veri sanity check
Modul A v2, P3 ML Muhendisi (Pomzadoya hackathon)

Hedef: P1 ARD ve P2 etiketi gelmeden once, model + loss + DataModule
       arayuzunun calistigini hizli dogrulamak.

Adimlar:
  1. Random tensor (B, 17, 256, 256) ile model forward
  2. Sentetik mask (B, 256, 256) ile loss compute (ignore_index dahil)
  3. Backward + grad finite kontrol
  4. Threshold sweep mini-test (synthetic prob & target)

Calistirma:
  python code/p3/05_synthetic_sanity.py --device cuda
  python code/p3/05_synthetic_sanity.py --device cpu --batch 2
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import torch

# code/p3/ modullerine erisim
sys.path.insert(0, str(Path(__file__).resolve().parent))

from importlib import import_module
ssl4eo_mod = import_module("02_ssl4eo_pretrained")
loss_mod = import_module("04_loss_metrics")

build_ssl4eo_unet = ssl4eo_mod.build_ssl4eo_unet
BCEDiceLoss = loss_mod.BCEDiceLoss
threshold_sweep = loss_mod.threshold_sweep
compute_metrics = loss_mod.compute_metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=str,
                        default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--batch", type=int, default=2)
    parser.add_argument("--in-channels", type=int, default=17)
    parser.add_argument("--ckpt", type=str, default=None,
                        help="(opsiyonel) SSL4EO-S12 .pth")
    args = parser.parse_args()

    device = torch.device(args.device)
    torch.manual_seed(42)
    np.random.seed(42)

    print("=" * 60)
    print(" P3 T3.3 — Sentetik Sanity Check")
    print("=" * 60)
    print(f" Device      : {device}")
    print(f" Batch       : {args.batch}")
    print(f" In channels : {args.in_channels}")
    print(f" SSL4EO ckpt : {args.ckpt}")
    print("-" * 60)

    # 1) Model
    model = build_ssl4eo_unet(
        num_classes=1,
        in_channels=args.in_channels,
        ssl4eo_ckpt=args.ckpt,
    ).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[1] Model     : SSL4EO-S12 U-Net, {n_params/1e6:.2f} M param")

    # 2) Sentetik input + mask (255 ignore, ~50% sinif 0, ~30% sinif 1)
    x = torch.randn(args.batch, args.in_channels, 256, 256, device=device)
    target = torch.zeros(args.batch, 256, 256, dtype=torch.long, device=device)
    target.fill_(0)
    pomza_mask = torch.rand(args.batch, 256, 256, device=device) > 0.7
    target[pomza_mask] = 1
    ignore_mask = torch.rand(args.batch, 256, 256, device=device) > 0.95
    target[ignore_mask] = 255  # WDPA buffer simulasyonu
    print(f"[2] Target    : pos={int((target==1).sum())} "
          f"neg={int((target==0).sum())} "
          f"ignore={int((target==255).sum())}")

    # 3) Forward
    model.train()
    logits = model(x)
    print(f"[3] Forward   : in={tuple(x.shape)} out={tuple(logits.shape)}")
    assert logits.shape == (args.batch, 1, 256, 256), "Shape uyumsuz!"

    # 4) Loss
    criterion = BCEDiceLoss(bce_weight=0.5, ignore_index=255)
    loss = criterion(logits, target)
    print(f"[4] Loss      : {loss.item():.4f}  (BCE+Dice combo)")
    assert torch.isfinite(loss), "Loss NaN/Inf!"

    # 5) Backward
    loss.backward()
    grad_norms = []
    for p in model.parameters():
        if p.grad is not None:
            grad_norms.append(p.grad.norm().item())
    gmin = min(grad_norms); gmax = max(grad_norms)
    print(f"[5] Backward  : grad norm min={gmin:.2e} max={gmax:.2e}")
    assert all(np.isfinite(grad_norms)), "Grad NaN/Inf!"

    # 6) Metrics + threshold sweep (synthetic)
    with torch.no_grad():
        probs = torch.sigmoid(logits).cpu().numpy()
    tgt_np = target.cpu().numpy()
    m = compute_metrics(probs, tgt_np, threshold=0.5)
    print(f"[6] Metrics @0.5: IoU={m.iou:.3f} F1={m.f1:.3f} "
          f"P={m.precision:.3f} R={m.recall:.3f}")

    sweep = threshold_sweep(probs, tgt_np)
    print(f"[7] Sweep     : best_thr={sweep['best_threshold']:.2f} "
          f"best_F1={sweep['best_f1']:.3f}")

    # 7) VRAM rapor
    if device.type == "cuda":
        peak = torch.cuda.max_memory_allocated() / 1e9
        print(f"[8] Peak VRAM : {peak:.2f} GB")

    print("-" * 60)
    print(" OK — sanity check tamam.")
    print("=" * 60)


if __name__ == "__main__":
    main()
