"""
P5 — T5.7: Landsat 1985, 1990, 2000, 2010, 2025 → animated GIF.

Girdi: 06_landsat_roy_harmonization.py çıktısı (OLI-equivalent SR).
RGB (red, green, blue) → 8-bit stretch → yıl etiketi → imageio GIF.

Çıktı:
  - data/temporal/landsat_timelapse.gif
  - data/temporal/landsat_frames/L_<year>.png  (frame backups)
"""

from __future__ import annotations

import re
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
import rasterio
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HARM_DIR = PROJECT_ROOT / "data" / "temporal" / "landsat_harmonized"
FRAME_DIR = PROJECT_ROOT / "data" / "temporal" / "landsat_frames"
OUT_GIF = PROJECT_ROOT / "data" / "temporal" / "landsat_timelapse.gif"

TARGET_YEARS = [1985, 1990, 2000, 2010, 2025]
FRAME_DURATION = 1.2  # saniye / kare


def stretch_8bit(arr: np.ndarray, p_lo: float = 2, p_hi: float = 98) -> np.ndarray:
    """Per-band percentile stretch."""
    out = np.zeros_like(arr, dtype=np.uint8)
    for i in range(arr.shape[0]):
        b = arr[i]
        lo, hi = np.nanpercentile(b, [p_lo, p_hi])
        if hi <= lo:
            continue
        out[i] = np.clip((b - lo) / (hi - lo) * 255, 0, 255).astype(np.uint8)
    return out


def render_frame(tif: Path, year: int) -> np.ndarray:
    with rasterio.open(tif) as src:
        # 06_landsat_roy_harmonization band sırası: blue, green, red, nir, swir1, swir2
        b = src.read(1).astype("float32")
        g = src.read(2).astype("float32")
        r = src.read(3).astype("float32")
    rgb = np.stack([r, g, b], axis=0)
    rgb8 = stretch_8bit(rgb)
    rgb8 = np.transpose(rgb8, (1, 2, 0))  # H,W,C

    img = Image.fromarray(rgb8, mode="RGB")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    label = f"{year}"
    pad = 12
    # Yıl etiketi siyah arkaplan
    box = draw.textbbox((0, 0), label, font=font)
    bw, bh = box[2] - box[0], box[3] - box[1]
    draw.rectangle([(pad, pad), (pad + bw + 12, pad + bh + 8)], fill=(0, 0, 0))
    draw.text((pad + 6, pad + 4), label, fill=(255, 255, 255), font=font)
    return np.array(img)


def main():
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    OUT_GIF.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(HARM_DIR.glob("*_OLIeq.tif"))
    if not files:
        raise FileNotFoundError(f"Harmonize Landsat yok: {HARM_DIR}. 06_landsat_roy_harmonization.py çalıştır.")

    by_year = {}
    for f in files:
        m = re.search(r"(\d{4})", f.stem)
        if m:
            by_year[int(m.group(1))] = f

    frames = []
    for y in TARGET_YEARS:
        if y not in by_year:
            print(f"[T5.7] {y} eksik, atlanıyor.")
            continue
        print(f"[T5.7] frame {y} <- {by_year[y].name}")
        arr = render_frame(by_year[y], y)
        Image.fromarray(arr).save(FRAME_DIR / f"L_{y}.png")
        frames.append(arr)

    if len(frames) < 2:
        raise RuntimeError("En az 2 frame gerek (GIF için).")

    imageio.mimsave(str(OUT_GIF), frames, duration=FRAME_DURATION, loop=0)
    print(f"[T5.7] GIF -> {OUT_GIF}  ({len(frames)} frame)")


if __name__ == "__main__":
    main()
