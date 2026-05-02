"""
T2.8 — Raster Mask Üretimi (CRITICAL PATH, v2)
==============================================

Etiket raster mask:
  - Pozitif piksel = 1 (positive_pixels.gpkg üzerinden)
  - Negatif piksel = 0 (negative_pixels.gpkg üzerinden)
  - Etiketsiz alan = NoData veya 0
  - WDPA buffer içi (ignore_mask.tif == 255) = 255 (ignore_index, eğitim dışı)

Önemli (v2):
- T2.8 critical path'te → saat 13'te bitmesi şart.
- 20m grid, EPSG:32636, P1 T1.4 ARD ile EXACT alignment.
- P3 fine-tune (T3.5) bu dosyayı PyTorch DataLoader üzerinden okuyacak.

Girdi:
    data/labels/positive_pixels.gpkg
    data/labels/negative_pixels.gpkg
    data/labels/ignore_mask.tif
    data/raw/s2_l2a_avanos_rgb.tif       (grid referansi — T1.4)

Çıktı:
    data/labels/full_mask.tif
        - dtype: uint8
        - 0 = etiketsiz / negatif
        - 1 = pozitif
        - 255 = ignore (WDPA buffer içi)
        - nodata = 255 ⇒ PyTorch ignore_index=255 ile uyumlu
"""

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio


POSITIVE_VAL = 1
NEGATIVE_VAL = 0
IGNORE_VAL = 255


def main(positives_gpkg, negatives_gpkg, ignore_mask_tif, raster_ref, out_path):
    print(f"[T2.8] Raster Mask Uretimi (CRITICAL PATH)")

    # Raster grid referans
    with rasterio.open(raster_ref) as src:
        transform = src.transform
        height = src.height
        width = src.width
        crs = src.crs
        if crs.to_epsg() != 32636:
            raise ValueError(f"Raster CRS != EPSG:32636 (T1.4 ARD beklenir)")
    print(f"  Grid: {width}x{height} @ EPSG:32636")

    # Tum pikseller default 0 (etiketsiz/negatif)
    mask = np.zeros((height, width), dtype=np.uint8)

    # Pozitif piksellerin row/col bilgisini kullan (zaten T2.4'te eklenmis)
    pos = gpd.read_file(positives_gpkg)
    if "row" in pos.columns and "col" in pos.columns:
        rows = pos["row"].astype(int).values
        cols = pos["col"].astype(int).values
        # Sinir kontrolu
        valid = (rows >= 0) & (rows < height) & (cols >= 0) & (cols < width)
        mask[rows[valid], cols[valid]] = POSITIVE_VAL
        print(f"  Pozitif piksel rasterize: {valid.sum()} / {len(pos)}")
    else:
        # Fallback: koordinat -> row/col cevir
        print(f"  WARN: pozitif gpkg'de row/col yok, koordinattan hesaplaniyor")
        from rasterio.transform import rowcol
        n_set = 0
        for _, r in pos.iterrows():
            x, y = r.geometry.x, r.geometry.y
            row, col = rowcol(transform, x, y)
            if 0 <= row < height and 0 <= col < width:
                mask[row, col] = POSITIVE_VAL
                n_set += 1
        print(f"  Pozitif piksel rasterize: {n_set} / {len(pos)}")

    # Negatif piksellerin label'ini sabitle (ozellikle 0 zaten ama explicit)
    neg = gpd.read_file(negatives_gpkg)
    if "row" in neg.columns and "col" in neg.columns:
        rows = neg["row"].astype(int).values
        cols = neg["col"].astype(int).values
        valid = (rows >= 0) & (rows < height) & (cols >= 0) & (cols < width)
        # Negatif=0 zaten default; sadece overlap durumunda pozitifi koruruz
        # (ama negatif sampling pozitif disindan oldugu icin overlap olmamali — kontrol)
        overlap = (mask[rows[valid], cols[valid]] == POSITIVE_VAL).sum()
        if overlap > 0:
            print(f"  WARN: {overlap} negatif piksel pozitif piksellere denk geldi — pozitif korunuyor")
        # Negatif=0 zaten default; explicit set etmiyoruz (her sey 0'di).
        print(f"  Negatif piksel sayisi (label=0): {valid.sum()}")
    else:
        print(f"  WARN: negatif gpkg'de row/col yok")

    # Ignore mask uygula (WDPA buffer ici = 255, herhangi bir labels'in uzerine yazar)
    if Path(ignore_mask_tif).exists():
        with rasterio.open(ignore_mask_tif) as src:
            ignore_arr = src.read(1)
            if ignore_arr.shape != mask.shape:
                raise ValueError(
                    f"ignore_mask boyut uyumsuz: {ignore_arr.shape} vs {mask.shape}"
                )
        ignore_pixels = (ignore_arr == IGNORE_VAL)
        # Pozitif piksel WDPA buffer ici varsa not + uyari (manuel kontrol icin)
        pos_in_ignore = ((mask == POSITIVE_VAL) & ignore_pixels).sum()
        if pos_in_ignore > 0:
            print(f"  NOTE: {pos_in_ignore} pozitif piksel WDPA buffer icinde — ignore'a tasiniyor")
        mask[ignore_pixels] = IGNORE_VAL
        print(f"  Ignore mask uygulandi: {ignore_pixels.sum()} piksel = 255")
    else:
        print(f"  WARN: {ignore_mask_tif} yok, ignore zone uygulanmadi")

    # Sanity sayilar
    n_pos = (mask == POSITIVE_VAL).sum()
    n_neg = (mask == NEGATIVE_VAL).sum()  # default-0; total - pos - ignore
    n_ign = (mask == IGNORE_VAL).sum()
    print(f"\n  Mask sayilar:")
    print(f"    Pozitif (1): {n_pos}")
    print(f"    Negatif/etiketsiz (0): {n_neg}")
    print(f"    Ignore (255): {n_ign}")
    print(f"    Toplam: {mask.size}")

    # Yaz
    profile = {
        "driver": "GTiff",
        "dtype": "uint8",
        "count": 1,
        "width": width,
        "height": height,
        "transform": transform,
        "crs": "EPSG:32636",
        "nodata": IGNORE_VAL,  # PyTorch ignore_index ile uyumlu
        "compress": "lzw",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(mask, 1)

    print(f"\n[T2.8] DONE — CRITICAL PATH HAZIR")
    print(f"  Çıktı: {out_path}")
    print(f"  P3 T3.5 fine-tune'a hazir.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--positives", default="data/labels/positive_pixels.gpkg")
    ap.add_argument("--negatives", default="data/labels/negative_pixels.gpkg")
    ap.add_argument("--ignore-mask", default="data/labels/ignore_mask.tif")
    ap.add_argument("--raster-ref", default="data/raw/s2_l2a_avanos_rgb.tif")
    ap.add_argument("--out", default="data/labels/full_mask.tif")
    args = ap.parse_args()
    main(args.positives, args.negatives, args.ignore_mask, args.raster_ref, args.out)
