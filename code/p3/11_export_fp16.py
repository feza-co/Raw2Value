"""
T3.13 — Model export FP16 + ONNX (opsiyonel)
Modul A v2, P3 ML Muhendisi (Pomzadoya hackathon)

Iki format:
  1) PT FP16  : /models/unet_pomza_fp16.pt  (P5 Streamlit)
  2) ONNX     : /models/unet_pomza.onnx     (opsiyonel, P4 entegrasyon)
  3) Manifest : input shape, normalization, kanal sirasi

Calistirma:
  python code/p3/11_export_fp16.py \
      --model /models/unet_pomza_ssl4eo_fold0.pt \
      --output-pt /models/unet_pomza_fp16.pt \
      --output-onnx /models/unet_pomza.onnx \
      --output-manifest /models/unet_pomza_manifest.json
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
inf_mod = import_module("07_inference")
dm_mod = import_module("03_datamodule")
load_model = inf_mod.load_model


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="best fold checkpoint")
    p.add_argument("--in-channels", type=int, default=17)
    p.add_argument("--output-pt", default="/models/unet_pomza_fp16.pt")
    p.add_argument("--output-onnx", default=None,
                   help="None ise ONNX export atlanir")
    p.add_argument("--output-manifest", default="/models/unet_pomza_manifest.json")
    p.add_argument("--input-h", type=int, default=256)
    p.add_argument("--input-w", type=int, default=256)
    p.add_argument("--opset", type=int, default=17)
    p.add_argument("--dynamic", action="store_true",
                   help="ONNX dynamic batch + spatial axes")
    return p.parse_args()


def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 1) Yukle (FP32) -> FP16 cevir
    model = load_model(args.model, in_channels=args.in_channels, device=str(device))
    model.eval()

    # FP16 PT
    out_pt = Path(args.output_pt)
    out_pt.parent.mkdir(parents=True, exist_ok=True)
    if device.type == "cuda":
        model_fp16 = model.half()
        sd = {k: v.half() if v.dtype == torch.float32 else v
              for k, v in model.state_dict().items()}
    else:
        # CPU FP16 desteklenmez; downcast et ama uyari
        print("[FP16] CUDA yok; state_dict half() ile kaydediliyor (CPU inference yavas).")
        sd = {k: v.half() if v.dtype == torch.float32 else v
              for k, v in model.state_dict().items()}
    torch.save({
        "model_state": sd,
        "in_channels": args.in_channels,
        "format": "fp16",
        "source": str(args.model),
    }, out_pt)
    print(f"OK FP16 -> {out_pt}  ({out_pt.stat().st_size/1e6:.1f} MB)")

    # 2) ONNX (opsiyonel)
    if args.output_onnx:
        out_onnx = Path(args.output_onnx)
        out_onnx.parent.mkdir(parents=True, exist_ok=True)
        # ONNX export FP32 ile yapilir (FP16 hedef runtime'da donusturulur).
        model_fp32 = load_model(args.model, in_channels=args.in_channels,
                                device=str(device)).eval()
        dummy = torch.randn(1, args.in_channels, args.input_h, args.input_w,
                            device=device)
        dyn_axes = None
        if args.dynamic:
            dyn_axes = {
                "input": {0: "batch", 2: "h", 3: "w"},
                "output": {0: "batch", 2: "h", 3: "w"},
            }
        torch.onnx.export(
            model_fp32, dummy, str(out_onnx),
            opset_version=args.opset,
            input_names=["input"], output_names=["output"],
            dynamic_axes=dyn_axes,
            do_constant_folding=True,
        )
        print(f"OK ONNX -> {out_onnx}  ({out_onnx.stat().st_size/1e6:.1f} MB)")

    # 3) Manifest
    manifest = {
        "model_name": "unet_pomza_ssl4eo",
        "format": ["fp16_pt"] + (["onnx"] if args.output_onnx else []),
        "input_shape": [None, args.in_channels, args.input_h, args.input_w],
        "input_dtype": "float32",
        "output_shape": [None, 1, args.input_h, args.input_w],
        "output_meaning": "RAW probability (sigmoid). KARAR #6: thresholdsuz.",
        "channel_order": [
            # P1 Modul A v2 sozlesmesi (manifest.json bands array uyumlu)
            "S2_B2", "S2_B3", "S2_B4", "S2_B5", "S2_B6", "S2_B7",
            "S2_B8", "S2_B8A", "S2_B11", "S2_B12",
            "S1_VV_dB", "S1_VH_dB",
            "DEM_m", "slope_deg",
            "NDVI", "BSI", "Albedo",
        ][:args.in_channels],
        "normalization": {
            "mean": dm_mod.DEFAULT_MEAN[:args.in_channels].tolist(),
            "std":  dm_mod.DEFAULT_STD[:args.in_channels].tolist(),
            "note": "P1 ARD manifest JSON gercek mean/std ile override et.",
        },
        "ignore_index": 255,
        "consumers": ["P4 (T4.12 fuse_confidence)", "P5 (T5.8, T5.10)"],
        "akademik_referans": [
            "Wang et al. 2023 — SSL4EO-S12",
            "Roberts et al. 2017 — spatial blok CV",
            "Karar #6 — score-level fuzyon P4'te",
        ],
    }
    out_man = Path(args.output_manifest)
    out_man.parent.mkdir(parents=True, exist_ok=True)
    with open(out_man, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"OK MANIFEST -> {out_man}")


if __name__ == "__main__":
    main()
