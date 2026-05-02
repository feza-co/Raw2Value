"""T1.8 — Full ARD tile splitting (256x256, 32 px overlap).

Giris  : data/ard/full_ard_20m.tif  (17 bant)
Cikis  : data/tiles/{row:03d}_{col:03d}.tif
         data/tiles/tile_index.json  (row,col → bounds,pixel_offset)

Strateji : stride = 256 - overlap = 224 px
           Her tile 256×256, komsu tile 32 px paylasir
           Kenar tile'lar NoData=-9999 ile 256x256'ya doldirilir
           P3 inference'ta cosine-blend bu 32 px ile smooth merge yapar
"""
import json
import sys
from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS

REPO = Path(__file__).resolve().parents[2]

INPUT_ARD  = REPO / "data/ard/full_ard_20m.tif"
TILES_DIR  = REPO / "data/tiles"
INDEX_FILE = TILES_DIR / "tile_index.json"

TILE_SIZE = 256
OVERLAP   = 32
STRIDE    = TILE_SIZE - OVERLAP   # 224 px
NODATA    = -9999.0


def _check_input():
    if not INPUT_ARD.exists():
        print(f"[ERROR] Giris bulunamadi: {INPUT_ARD}")
        print("  Once T1.7 (07_full_coregistration.py) calistirin.")
        sys.exit(1)


def main():
    _check_input()
    TILES_DIR.mkdir(parents=True, exist_ok=True)

    with rasterio.open(INPUT_ARD) as src:
        n_bands = src.count
        height  = src.height
        width   = src.width
        profile = src.profile.copy()
        transform = src.transform
        crs = src.crs
        data = src.read().astype(np.float32)

    print(f"[T1.8] ARD boyutu: {width}x{height}, {n_bands} bant")

    # Tile sayisi hesabi (kenar dolgu dahil)
    n_rows = max(1, int(np.ceil((height - OVERLAP) / STRIDE)))
    n_cols = max(1, int(np.ceil((width  - OVERLAP) / STRIDE)))
    total  = n_rows * n_cols
    print(f"[T1.8] Tile adeti: {n_rows} satir x {n_cols} sutun = {total}")

    tile_profile = profile.copy()
    tile_profile.update({
        "width":  TILE_SIZE,
        "height": TILE_SIZE,
        "count":  n_bands,
        "dtype":  "float32",
        "nodata": NODATA,
        "compress": "lzw",
        "predictor": 2,
    })

    index = {}
    written = 0

    for row_i in range(n_rows):
        for col_i in range(n_cols):
            row0 = row_i * STRIDE
            col0 = col_i * STRIDE
            row1 = row0 + TILE_SIZE
            col1 = col0 + TILE_SIZE

            # Kaynak bölge (orijinal raster sinirlarinda kal)
            src_r0 = max(0, row0)
            src_c0 = max(0, col0)
            src_r1 = min(height, row1)
            src_c1 = min(width, col1)

            # Hedef (tile icindeki) bölge
            dst_r0 = src_r0 - row0
            dst_c0 = src_c0 - col0
            dst_r1 = dst_r0 + (src_r1 - src_r0)
            dst_c1 = dst_c0 + (src_c1 - src_c0)

            # Tile tamponu (NODATA ile dolu)
            tile = np.full((n_bands, TILE_SIZE, TILE_SIZE), NODATA, dtype=np.float32)
            tile[:, dst_r0:dst_r1, dst_c0:dst_c1] = data[:, src_r0:src_r1, src_c0:src_c1]

            # Tile transform (sol-ust köseden)
            x_off = transform.c + col0 * transform.a
            y_off = transform.f + row0 * transform.e
            tile_transform = rasterio.transform.from_origin(
                x_off, y_off,
                abs(transform.a), abs(transform.e)
            )

            tile_profile["transform"] = tile_transform

            fname = f"{row_i:03d}_{col_i:03d}.tif"
            out_path = TILES_DIR / fname
            with rasterio.open(out_path, "w", **tile_profile) as dst:
                dst.write(tile)

            # Bounds (kaynak piksel koordinati — gerçek veri alanı)
            index[fname] = {
                "row": row_i, "col": col_i,
                "pixel_offset": [int(col0), int(row0)],
                "src_window": [int(src_c0), int(src_r0), int(src_c1), int(src_r1)],
                "has_nodata_pad": bool(src_r1 < row1 or src_c1 < col1),
            }
            written += 1

    with open(INDEX_FILE, "w") as f:
        json.dump({
            "tile_size": TILE_SIZE,
            "overlap":   OVERLAP,
            "stride":    STRIDE,
            "n_rows":    n_rows,
            "n_cols":    n_cols,
            "total":     written,
            "source_shape": [height, width],
            "tiles": index,
        }, f, indent=2)

    print(f"[T1.8] TAMAMLANDI -- {written} tile yazildi -> {TILES_DIR}")
    print(f"  Tile index -> {INDEX_FILE}")

    # Sanity
    sizes = [p.stat().st_size for p in TILES_DIR.glob("*.tif")]
    print(f"  Tile boyutu ort: {np.mean(sizes)/1e3:.0f} KB, toplam: {sum(sizes)/1e6:.1f} MB")


if __name__ == "__main__":
    main()
