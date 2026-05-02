"""Geçici doğrulama scripti — torch'a bağımlı olmayan manifest contract testi.
QA/ dizininde tutuyor; istersen sil."""
import json
import numpy as np
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
manifest_path = REPO / "data" / "manifest.json"

m = json.load(open(manifest_path, encoding="utf-8"))
bands = m["bands"]
mean = np.asarray([b["mean"] for b in bands], dtype=np.float32)
std = np.asarray([b["std"] for b in bands], dtype=np.float32)
nodata = float(m["ard"]["nodata"])
scale = float(m["scale"])
crs = m["ard"]["crs"]
tile_dir_raw = m["tiles"]["tiles_dir"]
tile_dir_norm = Path(str(tile_dir_raw).replace("\\", "/"))

assert len(bands) == 17, f"bant sayısı {len(bands)}"
assert nodata == -9999.0
assert scale == 10000.0
assert crs == "EPSG:32636"
assert np.all(np.isfinite(mean))
assert np.all(std > 0)
print(f"PASS bant={len(bands)} nodata={nodata} scale={scale} crs={crs}")
print(f"PASS tile_dir raw={tile_dir_raw!r} norm={tile_dir_norm.as_posix()}")
print(f"PASS mean[0..4]={mean[:5].tolist()}")
print(f"PASS std[0..4]={std[:5].tolist()}")
print(f"PASS bands[0..4]={[b['name'] for b in bands[:5]]}")

# NoData davranış simülasyonu — yeni datamodule mantığı
sim_tile = np.full((17, 4, 4), 100.0, dtype=np.float32)
sim_tile[3, 0, 0] = -9999.0   # idx 3 (B5) tek piksel NoData
sim_tile[7, 1, 1] = np.nan    # idx 7 (B8A) tek piksel NaN
sim_mask = np.zeros((4, 4), dtype=np.uint8)
IGNORE = 255

valid_per_ch = (sim_tile != nodata) & np.isfinite(sim_tile)
valid_pixel = valid_per_ch.all(axis=0)
sim_mask[~valid_pixel] = IGNORE
# Per-channel mean fill
for c in range(sim_tile.shape[0]):
    invalid_c = ~valid_per_ch[c]
    if invalid_c.any():
        sim_tile[c, invalid_c] = mean[c]

# Normalize
norm = (sim_tile - mean[:, None, None]) / (std[:, None, None] + 1e-6)
assert np.isfinite(norm).all(), "NaN/inf hala var"
assert sim_mask[0, 0] == IGNORE, "(0,0) mask ignore olmalı"
assert sim_mask[1, 1] == IGNORE, "(1,1) mask ignore olmalı"
assert sim_mask[0, 1] == 0,     "(0,1) mask değişmemeli"
print(f"PASS NoData mask: ignore_count={int((sim_mask == IGNORE).sum())}/16, finite={bool(np.isfinite(norm).all())}")
print(f"PASS norm range: min={norm.min():.3f} max={norm.max():.3f}")
print("ALL CHECKS PASSED")
