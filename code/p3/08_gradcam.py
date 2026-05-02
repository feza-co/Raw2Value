"""
T3.11 — Grad-CAM gorsellestirme utility
Modul A v2, P3 ML Muhendisi (Pomzadoya hackathon)

pytorch-grad-cam paketi kullaniyoruz (Jacob Gildenblat).
Hedef: U-Net'in son encoder katmanindan Grad-CAM aktivasyon haritasi
       cikar, tile'i RGB ile blendele, /reports/gradcam/ altina kaydet.

Calistirma:
  python code/p3/08_gradcam.py --model /models/unet_pomza_ssl4eo_fold0.pt \
      --input /data/ard/tiles/tile_0001.tif \
      --output /reports/gradcam/tile_0001_cam.png
"""
from __future__ import annotations

import os
import sys
from importlib import import_module
from pathlib import Path
from typing import List, Optional

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
inf_mod = import_module("07_inference")
load_model = inf_mod.load_model


# -----------------------------------------------------------------------
class SegmentationTarget:
    """pytorch-grad-cam icin sigmoid logit -> scalar score.

    U-Net output (B, 1, H, W) logits -> mean(sigmoid(logits)) skaler
    """

    def __init__(self, mask: Optional[np.ndarray] = None):
        self.mask = mask  # (H, W) bool/0-1 — yalnizca pomza pikselleri

    def __call__(self, model_output: torch.Tensor) -> torch.Tensor:
        # model_output: (1, H, W) (smp Unet'tan grad-cam squeeze edebilir)
        if model_output.dim() == 3:
            score = torch.sigmoid(model_output)
        elif model_output.dim() == 4:
            score = torch.sigmoid(model_output[:, 0])
        else:
            score = torch.sigmoid(model_output)
        if self.mask is not None:
            m = torch.as_tensor(self.mask, device=score.device).bool()
            sel = score.squeeze()[m]
            if sel.numel() == 0:
                return score.mean()
            return sel.mean()
        return score.mean()


def make_rgb_overlay(
    tile: np.ndarray,
    cam: np.ndarray,
    rgb_indices: tuple = (3, 2, 1),
    alpha: float = 0.45,
    percentile: float = 99.0,
) -> np.ndarray:
    """ARD tile (C, H, W) + cam (H, W) -> RGB+heatmap blend (H, W, 3) uint8."""
    r = tile[rgb_indices[0]]; g = tile[rgb_indices[1]]; b = tile[rgb_indices[2]]
    rgb = np.stack([r, g, b], axis=-1)
    p = np.percentile(rgb, percentile)
    rgb = np.clip(rgb / max(p, 1e-6), 0, 1)
    rgb_uint = (rgb * 255).astype(np.uint8)

    cam_n = (cam - cam.min()) / max(cam.max() - cam.min(), 1e-6)
    # turbo colormap (matplotlib istemiyoruz extra dep)
    heat = np.stack([
        np.clip(1.5 - np.abs(4 * cam_n - 3), 0, 1),
        np.clip(1.5 - np.abs(4 * cam_n - 2), 0, 1),
        np.clip(1.5 - np.abs(4 * cam_n - 1), 0, 1),
    ], axis=-1)
    heat = (heat * 255).astype(np.uint8)
    blend = ((1 - alpha) * rgb_uint + alpha * heat).astype(np.uint8)
    return blend


# -----------------------------------------------------------------------
def grad_cam_for_tile(
    tile: np.ndarray,
    model: torch.nn.Module,
    target_layer_name: str = "encoder.layer4",
    target_mask: Optional[np.ndarray] = None,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> np.ndarray:
    """Grad-CAM aktivasyon haritasi (H, W) [0, 1].

    Args:
        tile             : (C, H, W) normalize edilmis tile.
        model            : SSL4EO U-Net.
        target_layer_name: encoder.layer4 (ResNet-50 son blok).
        target_mask      : (H, W) — yalnizca pomza piksellerine score odakla.
    """
    try:
        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.image import preprocess_image
    except ImportError as e:
        raise ImportError("pip install grad-cam") from e

    device = torch.device(device)
    model = model.to(device).eval()

    # target layer (smp Unet ResNet-50 encoder)
    target_layer = model
    for part in target_layer_name.split("."):
        target_layer = getattr(target_layer, part)

    x = torch.from_numpy(tile).float().unsqueeze(0).to(device)
    x.requires_grad_(True)

    cam = GradCAM(model=model, target_layers=[target_layer])
    targets = [SegmentationTarget(mask=target_mask)]
    grayscale = cam(input_tensor=x, targets=targets)  # (1, H, W)
    return grayscale[0]


# -----------------------------------------------------------------------
def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--input", required=True, help="tile .tif (17 kanal)")
    p.add_argument("--output", required=True, help="png cikis yolu")
    p.add_argument("--target-layer", default="encoder.layer4")
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--rgb", default="3,2,1", help="RGB band indices (B04, B03, B02)")
    args = p.parse_args()

    try:
        import rasterio
        with rasterio.open(args.input) as s:
            tile = s.read().astype(np.float32)
    except ImportError:
        tile = np.load(args.input).astype(np.float32)

    # Hizli normalizasyon (manifest verilmediginde)
    dm_mod = import_module("03_datamodule")
    mean = dm_mod.DEFAULT_MEAN[: tile.shape[0]]
    std = dm_mod.DEFAULT_STD[: tile.shape[0]]
    tile_n = (tile - mean[:, None, None]) / (std[:, None, None] + 1e-6)
    tile_n = np.nan_to_num(tile_n, nan=0.0)

    model = load_model(args.model, device=args.device)
    cam = grad_cam_for_tile(tile_n, model, target_layer_name=args.target_layer,
                            device=args.device)
    rgb_idx = tuple(int(x) for x in args.rgb.split(","))
    overlay = make_rgb_overlay(tile, cam, rgb_indices=rgb_idx)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    try:
        import imageio.v3 as iio
        iio.imwrite(args.output, overlay)
    except ImportError:
        from PIL import Image
        Image.fromarray(overlay).save(args.output)
    print(f"OK -> {args.output}  (cam range [{cam.min():.3f}, {cam.max():.3f}])")


if __name__ == "__main__":
    main()
