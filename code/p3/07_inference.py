"""
T3.10 — RAW olasilik inference (KRITIK, Karar #6)
Modul A v2, P3 ML Muhendisi (Pomzadoya hackathon)

ONEMLI KURAL:
  P3 ciktisi RAW olasilik haritasidir. THRESHOLD UYGULAMA YASAK,
  BINARIZE ETME YASAK. P4 score-level fuzyon yapacak (T4.12):
      final_confidence = P3_raw_prob × P4_QI × (1 - P4_CI)
  P5 historical Landsat icin threshold'u kendisi secer.

API:
  def predict_raw(tile_tensor: torch.Tensor, model_path: str,
                  device: str = "cuda") -> np.ndarray
  Returns: raw probability map [0, 1], shape (H, W) veya (B, H, W).

Ek yardimcilar:
  - load_model(...)            : checkpoint -> torch model
  - predict_raster(...)        : full GeoTIFF raster -> RAW prob GeoTIFF
                                 (sliding window, overlap+blend)
  - predict_landsat_snapshot() : P5 icin Landsat (RGB+NIR+SWIR) tile.

P4 (T4.12) ve P5 (T5.8, T5.10) bu fonksiyonu cagiracak.
"""
from __future__ import annotations

import os
import sys
from importlib import import_module
from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
ssl4eo_mod = import_module("02_ssl4eo_pretrained")
build_ssl4eo_unet = ssl4eo_mod.build_ssl4eo_unet


# -----------------------------------------------------------------------
# 1) Model loader
# -----------------------------------------------------------------------
def load_model(
    model_path: str | os.PathLike,
    in_channels: int = 17,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    fp16: bool = False,
) -> torch.nn.Module:
    """SSL4EO-S12 U-Net checkpoint'ini yukle, eval moduna gec.

    Args:
        model_path : .pt dosyasi (06_train.py uretir).
        in_channels: Egitim sirasindaki in_channels (default 17).
        device     : "cuda" | "cpu"
        fp16       : True ise model FP16'ya cevrilir (export sonrasi inference).
    """
    device = torch.device(device)
    raw = torch.load(str(model_path), map_location=device)
    if isinstance(raw, dict) and "model_state" in raw:
        state = raw["model_state"]
        meta_in = raw.get("args", {}).get("in_channels", in_channels)
        if raw.get("args", {}).get("rgb_only", False):
            meta_in = 3
        in_channels = meta_in
    else:
        state = raw

    model = build_ssl4eo_unet(
        num_classes=1,
        in_channels=in_channels,
        ssl4eo_ckpt=None,  # state_dict ile dolduracagiz
    ).to(device)
    model.load_state_dict(state, strict=False)
    model.eval()
    if fp16 and device.type == "cuda":
        model = model.half()
    return model


# -----------------------------------------------------------------------
# 2) RAW prediction (KRITIK API — P4 ve P5 kullanir)
# -----------------------------------------------------------------------
def predict_raw(
    tile_tensor: torch.Tensor,
    model_path: Union[str, os.PathLike, torch.nn.Module],
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    fp16: bool = False,
) -> np.ndarray:
    """RAW olasilik haritasi dondurur — threshold/binarize YOK.

    Args:
        tile_tensor : (C, H, W) veya (B, C, H, W). float32 normalize edilmis.
        model_path  : checkpoint yolu VEYA onceden yuklenmis torch.nn.Module.
        device      : "cuda" | "cpu"
        fp16        : True ise FP16 inference (Karar #13 export profili).

    Returns:
        np.ndarray, dtype float32, range [0, 1].
        Input (C, H, W)   -> output (H, W)
        Input (B, C, H, W) -> output (B, H, W)

    KURAL: Donmeden once threshold yok, sigmoid sonrasi RAW prob.
    """
    device = torch.device(device)

    if isinstance(model_path, torch.nn.Module):
        model = model_path
    else:
        model = load_model(model_path, device=str(device), fp16=fp16)

    if tile_tensor.dim() == 3:
        x = tile_tensor.unsqueeze(0)
        squeeze_batch = True
    elif tile_tensor.dim() == 4:
        x = tile_tensor
        squeeze_batch = False
    else:
        raise ValueError(f"tile_tensor 3 veya 4 boyutlu olmali, alindi {tile_tensor.dim()}")

    x = x.to(device, non_blocking=True)
    if fp16 and device.type == "cuda":
        x = x.half()

    with torch.no_grad():
        logits = model(x)
        probs = torch.sigmoid(logits).float().cpu().numpy()  # (B, 1, H, W)
    probs = probs.squeeze(1)  # (B, H, W)
    if squeeze_batch:
        probs = probs[0]  # (H, W)
    # NOT: hicbir threshold uygulanmaz (Karar #6)
    return probs.astype(np.float32)


# -----------------------------------------------------------------------
# 3) Sliding-window full-raster inference (RAW prob GeoTIFF uretir)
# -----------------------------------------------------------------------
def predict_raster(
    raster_path: str | os.PathLike,
    model_path: Union[str, os.PathLike, torch.nn.Module],
    output_path: str | os.PathLike,
    tile_size: int = 256,
    overlap: int = 32,
    mean: Optional[np.ndarray] = None,
    std: Optional[np.ndarray] = None,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    fp16: bool = False,
    batch_size: int = 4,
) -> str:
    """Full ARD raster'i sliding window ile RAW olasilik raster'ina cevir.

    Output: float32 GeoTIFF (1 band), [0, 1] olasilik.
    Overlap region cosine-blend ile birlestirilir (kenar artefaktlari azalir).
    """
    try:
        import rasterio
        from rasterio.windows import Window
    except ImportError as e:
        raise ImportError("rasterio gerekli.") from e

    if isinstance(model_path, torch.nn.Module):
        model = model_path
    else:
        model = load_model(model_path, device=device, fp16=fp16)

    with rasterio.open(raster_path) as src:
        c, h, w = src.count, src.height, src.width
        profile = src.profile.copy()
        crs = src.crs
        transform = src.transform

        if mean is None or std is None:
            from importlib import import_module as _im
            dm = _im("03_datamodule")
            mean = dm.DEFAULT_MEAN[:c] if mean is None else mean
            std = dm.DEFAULT_STD[:c] if std is None else std

        prob_acc = np.zeros((h, w), dtype=np.float32)
        weight_acc = np.zeros((h, w), dtype=np.float32)

        # Cosine blend window
        coords = np.linspace(-np.pi / 2, np.pi / 2, tile_size)
        ramp = np.cos(coords) ** 2
        blend = np.outer(ramp, ramp).astype(np.float32)

        step = tile_size - overlap
        ys = list(range(0, max(h - tile_size, 0) + 1, step))
        if ys[-1] != h - tile_size:
            ys.append(max(h - tile_size, 0))
        xs = list(range(0, max(w - tile_size, 0) + 1, step))
        if xs[-1] != w - tile_size:
            xs.append(max(w - tile_size, 0))

        positions = [(y, x) for y in ys for x in xs]
        device_t = torch.device(device)

        for i in range(0, len(positions), batch_size):
            batch = positions[i:i + batch_size]
            tiles = []
            for (yy, xx) in batch:
                window = Window(xx, yy, tile_size, tile_size)
                arr = src.read(window=window, boundless=True, fill_value=0).astype(np.float32)
                # normalize
                arr = (arr - mean[:, None, None]) / (std[:, None, None] + 1e-6)
                arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
                tiles.append(arr)
            tt = torch.from_numpy(np.stack(tiles)).to(device_t)
            if fp16 and device_t.type == "cuda":
                tt = tt.half()
            with torch.no_grad():
                logits = model(tt)
                probs = torch.sigmoid(logits).float().cpu().numpy()  # (B, 1, ts, ts)
            for k, (yy, xx) in enumerate(batch):
                p = probs[k, 0]
                # boyut ayar (kenar tile'lari icin)
                ph = min(tile_size, h - yy)
                pw = min(tile_size, w - xx)
                prob_acc[yy:yy + ph, xx:xx + pw] += p[:ph, :pw] * blend[:ph, :pw]
                weight_acc[yy:yy + ph, xx:xx + pw] += blend[:ph, :pw]

        prob_acc /= np.maximum(weight_acc, 1e-6)

        profile.update(
            dtype=rasterio.float32,
            count=1,
            compress="deflate",
            predictor=2,
            tiled=True,
            blockxsize=512, blockysize=512,
            nodata=None,
        )
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(prob_acc.astype(np.float32), 1)
            dst.update_tags(
                P3_OUTPUT="RAW_PROBABILITY",
                P3_NOTE="Karar#6: threshold/binarize uygulanmadi. P4 fuzyon yapacak.",
                P3_RANGE="[0, 1]",
            )
    return str(output_path)


# -----------------------------------------------------------------------
# 4) Landsat snapshot inference (P5 icin)
# -----------------------------------------------------------------------

# Roy et al. (2016) standart Landsat -> Sentinel-2 reflectance band mapping
# Kanal indeksleri 1-tabanli (rasterio okuma ile uyumlu).
# Hedef: P3 ARD 17-kanal yapisi (B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12,
# VV, VH, DEM, slope, NDVI, BSI, Albedo).
LANDSAT_TO_S2_DEFAULT = {
    # Landsat 8/9 OLI -> S2 indexes (P3 ARD'a)
    "L8_OLI": {
        # ARD idx -> Landsat band number
        0: ("B2", "Blue"),       # L8 B2 -> S2 B2
        1: ("B3", "Green"),      # L8 B3 -> S2 B3
        2: ("B4", "Red"),        # L8 B4 -> S2 B4
        # B5, B6, B7 (Red Edge) -> Landsat'ta yok, fill_zero
        6: ("B5", "NIR"),        # L8 B5 -> S2 B8 (NIR), Roy 2016 cross-sensor
        7: ("B5", "NIR"),        # L8 B5 -> S2 B8A (NIR narrow), ayni kaynak
        8: ("B6", "SWIR1"),      # L8 B6 -> S2 B11 (SWIR1)
        9: ("B7", "SWIR2"),      # L8 B7 -> S2 B12 (SWIR2)
    },
    # Landsat 5/7 ETM+ -> S2 indexes
    "L5_TM": {
        0: ("B1", "Blue"),       # L5 B1 -> S2 B2
        1: ("B2", "Green"),      # L5 B2 -> S2 B3
        2: ("B3", "Red"),        # L5 B3 -> S2 B4
        6: ("B4", "NIR"),        # L5 B4 -> S2 B8
        7: ("B4", "NIR"),        # L5 B4 -> S2 B8A
        8: ("B5", "SWIR1"),      # L5 B5 -> S2 B11
        9: ("B7", "SWIR2"),      # L5 B7 -> S2 B12
    },
    "L7_ETM": {
        0: ("B1", "Blue"),
        1: ("B2", "Green"),
        2: ("B3", "Red"),
        6: ("B4", "NIR"),
        7: ("B4", "NIR"),
        8: ("B5", "SWIR1"),
        9: ("B7", "SWIR2"),
    },
}


def predict_landsat_snapshot(
    landsat_path: str | os.PathLike,
    model_path: Union[str, os.PathLike, torch.nn.Module],
    output_path: str | os.PathLike,
    sensor: str = "L8_OLI",
    band_mapping: Optional[dict] = None,
    fill_strategy: str = "zero",
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    fp16: bool = True,
    n_target_channels: int = 17,
) -> str:
    """Landsat snapshot (1985-2025, [K#9]) RAW prob raster.

    Landsat 5/7/8/9 -> 17 kanal Sentinel-2 esit kanal modeli. Eksik bantlar
    fill_strategy="zero" ile sifir doldurulur. P5 (T5.10) historical Landsat
    Tier 2 icin bu fonksiyonu cagirir; kalite gostergesi (eksik bant orani)
    P5'in zaman ekranina dusurulur.

    Args:
        sensor: "L8_OLI" | "L5_TM" | "L7_ETM" | "L9_OLI" (L8 ile ayni mapping)
        band_mapping: P5 custom mapping override (sensor parametresini gormezden gelir).
                      Format: {ard_idx (int): (landsat_band_name (str), description)}
        fill_strategy: "zero" | "interp" (sadece zero implement edilmis).
        n_target_channels: 17 (default ARD kanal sayisi).

    Returns:
        Output path (RAW prob GeoTIFF).
    """
    try:
        import rasterio
        import numpy as np
    except ImportError as e:
        raise ImportError("rasterio gerekli.") from e

    # Mapping cozumle
    if band_mapping is None:
        sensor_norm = sensor.upper().replace("LANDSAT", "L").replace("-", "_")
        if sensor_norm in ("L9_OLI", "L9OLI"):
            sensor_norm = "L8_OLI"  # L9 == L8 OLI mapping
        if sensor_norm not in LANDSAT_TO_S2_DEFAULT:
            raise ValueError(
                f"Bilinmeyen sensor: {sensor}. "
                f"Desteklenen: {list(LANDSAT_TO_S2_DEFAULT)}. "
                f"Custom band_mapping ile override edebilirsin."
            )
        band_mapping = LANDSAT_TO_S2_DEFAULT[sensor_norm]

    # Landsat raster -> 17 kanal sentetik ARD raster
    with rasterio.open(landsat_path) as src:
        h, w = src.height, src.width
        profile = src.profile.copy()
        landsat_bands = {f"B{i}": src.read(i).astype(np.float32) for i in range(1, src.count + 1)}

    # Hedef 17-kanal arrayi (eksikler 0)
    target = np.zeros((n_target_channels, h, w), dtype=np.float32)
    fill_log = {"mapped": [], "missing": []}
    for ard_idx in range(n_target_channels):
        if ard_idx in band_mapping:
            landsat_band_name, _desc = band_mapping[ard_idx]
            if landsat_band_name in landsat_bands:
                target[ard_idx] = landsat_bands[landsat_band_name]
                fill_log["mapped"].append((ard_idx, landsat_band_name))
            else:
                fill_log["missing"].append((ard_idx, landsat_band_name, "band_not_in_raster"))
        else:
            fill_log["missing"].append((ard_idx, None, "no_mapping_zero_filled"))

    # Quality flag: kac kanal eksik?
    n_missing = len(fill_log["missing"])
    n_mapped = len(fill_log["mapped"])
    print(f"[predict_landsat_snapshot] {sensor}: mapped={n_mapped}, "
          f"missing(zero-filled)={n_missing}/{n_target_channels}")
    if n_missing > 11:
        print(f"  UYARI: {n_missing} kanal eksik. Pomza tespit hassasiyeti dusuk olabilir.")

    # Sentetik 17-kanal raster'i Drive disindaki gecici dosyaya yaz
    # (predict_raster zaten dosyadan okur, en kolay yol gecici dosya)
    import tempfile
    tmp_path = tempfile.NamedTemporaryFile(suffix=".tif", delete=False).name
    profile.update(count=n_target_channels, dtype=rasterio.float32)
    with rasterio.open(tmp_path, "w", **profile) as dst:
        dst.write(target)

    try:
        result = predict_raster(
            raster_path=tmp_path,
            model_path=model_path,
            output_path=output_path,
            device=device,
            fp16=fp16,
        )
        # Output'a quality tag ekle
        with rasterio.open(output_path, "r+") as dst:
            dst.update_tags(
                P3_LANDSAT_SENSOR=sensor,
                P3_LANDSAT_MAPPED_CHANNELS=str(n_mapped),
                P3_LANDSAT_MISSING_CHANNELS=str(n_missing),
                P3_LANDSAT_QUALITY=("HIGH" if n_missing <= 7 else "MEDIUM" if n_missing <= 11 else "LOW"),
            )
        return result
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# -----------------------------------------------------------------------
# 5) CLI
# -----------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["tile", "raster", "landsat"], default="raster")
    p.add_argument("--input", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--fp16", action="store_true")
    args = p.parse_args()

    if args.mode == "raster":
        out = predict_raster(args.input, args.model, args.output,
                             device=args.device, fp16=args.fp16)
        print(f"OK -> {out}")
    elif args.mode == "landsat":
        out = predict_landsat_snapshot(args.input, args.model, args.output,
                                       device=args.device, fp16=args.fp16)
        print(f"OK -> {out}")
    elif args.mode == "tile":
        try:
            import rasterio
            with rasterio.open(args.input) as s:
                arr = s.read().astype(np.float32)
        except ImportError:
            arr = np.load(args.input)
        x = torch.from_numpy(arr)
        prob = predict_raw(x, args.model, device=args.device, fp16=args.fp16)
        np.save(args.output, prob)
        print(f"OK shape={prob.shape} range=[{prob.min():.3f}, {prob.max():.3f}]")
