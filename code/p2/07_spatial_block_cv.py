"""
T2.7 — Spatial 5-Fold Blok CV Split (Roberts 2017)
==================================================

Akademik referans (v2 Karar K#10):
- Roberts, D. R., et al. (2017). "Cross-validation strategies for data with
  temporal, spatial, hierarchical, or phylogenetic structure." Ecography 40: 913–929.
- Sıradan random KFold spatial autocorrelation nedeniyle leakage üretir →
  bloklar coğrafi olarak ayrık olmalı, her fold farklı bölge.

Yöntem:
- Tile merkez koordinatlarını al (P1 T1.8 manifest'inden veya tile'ların
  bbox center'ından).
- AOI'yi NxM grid bloka böl (varsayılan 5x5 = 25 blok).
- Bloklar fold'lara DAĞITILIR ki her fold ~ aynı tile sayısı + coğrafi olarak ayrık.
- Çıktı: blok_cv_split.json (her fold icin train/val tile listesi).

Plan B (orchestrator onayi gerekirse):
- 5-fold yerine 3-fold: --n-folds 3 (NxM grid'i 3x3'e dusur).

Girdi:
    data/ard/tile_manifest.json            P1 T1.9 cikti (tile_id, bbox, ...)
    [opsiyonel] data/aoi/avanos_aoi.gpkg   blok grid bounds icin

Çıktı:
    data/labels/blok_cv_split.json
        {
          "method": "spatial_block_cv_roberts2017",
          "n_folds": 5,
          "block_grid": "5x5",
          "fold_0": {"train_tiles": [...], "val_tiles": [...], "blocks_val": [...]},
          ...
        }

Verde paketi opsiyonel (try/except). Kullaniliyor ise:
    https://www.fatiando.org/verde/latest/api/generated/verde.BlockKFold.html
Kullanilmaz ise manuel grid bloklama.
"""

import argparse
import json
from pathlib import Path
from collections import defaultdict

import numpy as np


def load_tile_manifest(manifest_path, raster_ref=None):
    """
    İki format desteklenir:

    Format A — P1 orijinal beklenti (bbox_utm listesi):
      {"tiles": [{"tile_id": "...", "bbox_utm": [xmin,ymin,xmax,ymax]}, ...]}

    Format B — tile_index.json (pixel_offset + src_window dict):
      {"tile_size": 256, "tiles": {"000_000.tif": {"pixel_offset": [cx,cy], "src_window": [...]}}}

    Format B için raster_ref (EPSG:32636 GeoTIFF) zorunlu — UTM koordinat hesabı için.
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        m = json.load(f)

    tiles_raw = m.get("tiles", m if isinstance(m, list) else [])

    # Format B: tiles bir dict (tile_id → metadata)
    if isinstance(tiles_raw, dict):
        if raster_ref is None:
            raise ValueError(
                "tile_index.json (Format B) için --raster-ref belirtilmeli "
                "(UTM bbox hesabında kaynak transform gerekir)."
            )
        import rasterio as _rio
        with _rio.open(raster_ref) as src:
            tf = src.transform  # Affine: origin + pixel size
        tile_size = m.get("tile_size", 256)
        out = []
        for tile_id, meta in tiles_raw.items():
            po = meta.get("pixel_offset", [0, 0])  # [col_start, row_start]
            col_start, row_start = po[0], po[1]
            # src_window varsa gerçek boyutu kullan (kenar tile'lar)
            sw = meta.get("src_window")
            col_end = sw[2] if sw else col_start + tile_size
            row_end = sw[3] if sw else row_start + tile_size
            xmin = tf.c + col_start * tf.a
            xmax = tf.c + col_end * tf.a
            ymax = tf.f + row_start * tf.e
            ymin = tf.f + row_end * tf.e
            cx = (xmin + xmax) / 2
            cy = (ymin + ymax) / 2
            out.append({"tile_id": tile_id, "cx": cx, "cy": cy,
                        "bbox": [xmin, ymin, xmax, ymax]})
        return out

    # Format A: tiles bir liste
    out = []
    for t in tiles_raw:
        bbox = t.get("bbox_utm") or t.get("bbox") or t.get("bounds")
        if bbox is None or len(bbox) != 4:
            raise ValueError(f"Tile {t.get('tile_id')} bbox eksik")
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        out.append({"tile_id": t["tile_id"], "cx": cx, "cy": cy, "bbox": bbox})
    return out


def manual_block_assignment(tiles, n_blocks_x, n_blocks_y):
    """
    Tile merkezlerini NxM grid'e ata. Her tile -> block_id (int).
    """
    xs = np.array([t["cx"] for t in tiles])
    ys = np.array([t["cy"] for t in tiles])
    xmin, xmax = xs.min(), xs.max()
    ymin, ymax = ys.min(), ys.max()

    # Grid sinirlari
    x_edges = np.linspace(xmin, xmax + 1e-6, n_blocks_x + 1)
    y_edges = np.linspace(ymin, ymax + 1e-6, n_blocks_y + 1)

    block_assign = []
    for t in tiles:
        bx = np.searchsorted(x_edges, t["cx"], side="right") - 1
        by = np.searchsorted(y_edges, t["cy"], side="right") - 1
        bx = max(0, min(bx, n_blocks_x - 1))
        by = max(0, min(by, n_blocks_y - 1))
        block_id = by * n_blocks_x + bx
        block_assign.append(block_id)
    return block_assign, (n_blocks_x, n_blocks_y), (x_edges.tolist(), y_edges.tolist())


def assign_blocks_to_folds(block_ids, n_folds, seed=42):
    """
    Bloklari fold'lara dagit, her fold ~ esit blok sayisi alsin.
    Roberts 2017 yaklasimi: bloklar shuffle edilir, fold'lara round-robin atanir
    boylece her fold cografi olarak farkli bolgelerden bloklar alir.
    """
    rng = np.random.default_rng(seed)
    unique_blocks = sorted(set(block_ids))
    rng.shuffle(unique_blocks)
    fold_of_block = {}
    for i, b in enumerate(unique_blocks):
        fold_of_block[b] = i % n_folds
    return fold_of_block


def try_verde(tiles, n_folds):
    """
    Verde paketi varsa onu kullan (akademik open-source standart).
    """
    try:
        import verde as vd
    except ImportError:
        return None

    coords = np.column_stack([
        np.array([t["cx"] for t in tiles]),
        np.array([t["cy"] for t in tiles]),
    ])
    # Spacing default — AOI capina gore 5 blok x 5 blok
    span_x = coords[:, 0].max() - coords[:, 0].min()
    span_y = coords[:, 1].max() - coords[:, 1].min()
    spacing = max(span_x, span_y) / 5.0  # 5x5 grid

    bkfold = vd.BlockKFold(spacing=spacing, n_splits=n_folds, shuffle=True, random_state=42)
    splits = list(bkfold.split(coords))
    return splits  # [(train_idx, test_idx), ...]


def main(manifest_path, raster_ref, out_path, n_folds, block_grid, use_verde):
    print(f"[T2.7] Roberts 2017 Spatial Blok CV Split")
    print(f"  N-fold: {n_folds}, Block grid: {block_grid[0]}x{block_grid[1]}")
    print(f"  Use verde: {use_verde}")

    tiles = load_tile_manifest(manifest_path, raster_ref=raster_ref)
    if not tiles:
        raise RuntimeError("Tile manifest bos! P1 T1.9 calistirilmis mi?")
    print(f"  Tile sayisi: {len(tiles)}")

    folds_data = {f"fold_{k}": {"train_tiles": [], "val_tiles": [], "blocks_val": []}
                  for k in range(n_folds)}
    method_used = None

    if use_verde:
        verde_result = try_verde(tiles, n_folds)
        if verde_result is not None:
            method_used = "verde.BlockKFold"
            for k, (train_idx, val_idx) in enumerate(verde_result):
                folds_data[f"fold_{k}"]["train_tiles"] = [tiles[i]["tile_id"] for i in train_idx]
                folds_data[f"fold_{k}"]["val_tiles"] = [tiles[i]["tile_id"] for i in val_idx]
        else:
            print(f"  WARN: verde import edilemedi, manuel bloklamaya geciliyor")

    if method_used is None:
        # Manuel grid bloklama (fallback ve default)
        method_used = "manual_grid_blocks"
        block_assign, grid_shape, edges = manual_block_assignment(
            tiles, block_grid[0], block_grid[1]
        )
        # Block size sanity check
        unique_blocks = sorted(set(block_assign))
        print(f"  Toplam dolu blok: {len(unique_blocks)} / {block_grid[0]*block_grid[1]}")
        if len(unique_blocks) < n_folds:
            raise RuntimeError(
                f"Dolu blok sayisi ({len(unique_blocks)}) < n_folds ({n_folds}). "
                f"Block grid'i artirin veya n_folds'u dusurun (Plan B: 3-fold)."
            )

        fold_of_block = assign_blocks_to_folds(block_assign, n_folds)

        for i, t in enumerate(tiles):
            blk = block_assign[i]
            val_fold = fold_of_block[blk]
            for k in range(n_folds):
                if k == val_fold:
                    folds_data[f"fold_{k}"]["val_tiles"].append(t["tile_id"])
                else:
                    folds_data[f"fold_{k}"]["train_tiles"].append(t["tile_id"])

        # Hangi blok hangi fold'da bilgisi (debug + viz icin)
        for blk, k in fold_of_block.items():
            folds_data[f"fold_{k}"]["blocks_val"].append(int(blk))

    # Sanity print
    for k in range(n_folds):
        fk = folds_data[f"fold_{k}"]
        print(f"  fold_{k}: train={len(fk['train_tiles'])}, val={len(fk['val_tiles'])}")

    out = {
        "method": f"spatial_block_cv_roberts2017_{method_used}",
        "n_folds": n_folds,
        "block_grid": f"{block_grid[0]}x{block_grid[1]}",
        "n_tiles": len(tiles),
        "academic_ref": "Roberts et al. 2017, Ecography 40:913-929 (K#10)",
        **folds_data,
    }

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"\n[T2.7] DONE")
    print(f"  Çıktı: {out_path}")
    print(f"  Yontem: {method_used}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/tiles/tile_index.json",
                    help="P1 tile manifest (tile_index.json veya eski format)")
    ap.add_argument("--raster-ref", default="data/ard/full_ard_20m.tif",
                    help="UTM bbox hesabi icin ARD raster (Format B icin zorunlu)")
    ap.add_argument("--out", default="data/labels/blok_cv_split.json")
    ap.add_argument("--n-folds", type=int, default=5,
                    help="5 (varsayilan) veya 3 (Plan B — orchestrator onayli)")
    ap.add_argument("--blocks-x", type=int, default=5)
    ap.add_argument("--blocks-y", type=int, default=5)
    ap.add_argument("--use-verde", action="store_true", default=True,
                    help="verde.BlockKFold dene; basarisiz ise manuel grid'e dus")
    args = ap.parse_args()
    main(args.manifest, args.raster_ref, args.out, args.n_folds,
         (args.blocks_x, args.blocks_y), args.use_verde)
