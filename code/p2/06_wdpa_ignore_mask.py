"""
T2.6 — WDPA Göreme + 1000 m Buffer + Ignore Mask
================================================

Akademik gerekçe (v2 Karar K#8):
- Göreme Tarihi Milli Park (UNESCO + WDPA) UNESCO Tampon Bölgesi koruması altında.
- 1000 m buffer literatürde standart (UNESCO World Heritage Buffer Zone protokolü).
- Bu bölgede pomza ÇIKARMA YASAK ⇒ pozitif/negatif KESIN olarak öğrenilemez.
- Eğitim dışında bırakılır: ignore_mask = 255 (PyTorch ignore_index varsayılanı).

Girdi:
    data/raw/wdpa_goreme.gpkg              (WDPA shapefile, Cappadocia/Göreme polygon)
                                            Kaynak: protectedplanet.net WDPA download
    data/raw/s2_l2a_avanos_rgb.tif         (raster grid referansi — T1.4)

Çıktı:
    data/labels/wdpa_buffer.gpkg           (Göreme + 1000m buffer polygon)
    data/labels/ignore_mask.tif            (uint8 raster: 255 = ignore, 0 = etiket icin uygun)
"""

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
from shapely.ops import unary_union


WDPA_BUFFER_M = 1000  # K#8 — UNESCO buffer protokolü
IGNORE_VALUE = 255


def main(wdpa_path, raster_ref_path, out_buffer_gpkg, out_mask_tif):
    print(f"[T2.6] WDPA Göreme + {WDPA_BUFFER_M}m buffer + ignore mask")
    print(f"  WDPA kaynagi: {wdpa_path}")

    wdpa = gpd.read_file(wdpa_path)
    if wdpa.crs is None:
        raise ValueError("WDPA dosyasi CRS'siz — kontrol et")
    if wdpa.crs.to_epsg() != 32636:
        wdpa = wdpa.to_crs(32636)
    print(f"  WDPA feature sayisi: {len(wdpa)}, alan: {wdpa.geometry.area.sum()/1e6:.2f} km²")

    # Göreme/Cappadocia name filter (cok feature varsa)
    if "NAME" in wdpa.columns:
        mask_name = wdpa["NAME"].astype(str).str.contains(
            "Goreme|Göreme|Cappadocia|Kapadokya", case=False, na=False
        )
        if mask_name.any():
            wdpa = wdpa[mask_name]
            print(f"  Goreme filter sonrasi: {len(wdpa)} feature")

    # Buffer + union
    buffered = wdpa.geometry.buffer(WDPA_BUFFER_M)
    buffer_union = unary_union(buffered.values)
    print(f"  Buffer alani: {buffer_union.area/1e6:.2f} km²")

    # Buffer GPKG cikti
    Path(out_buffer_gpkg).parent.mkdir(parents=True, exist_ok=True)
    out_buf = gpd.GeoDataFrame(
        {"name": ["Göreme_NP_buffer_1000m"], "buffer_m": [WDPA_BUFFER_M]},
        geometry=[buffer_union],
        crs="EPSG:32636",
    )
    out_buf.to_file(out_buffer_gpkg, driver="GPKG", layer="wdpa_buffer")
    print(f"  Buffer GPKG: {out_buffer_gpkg}")

    # Raster mask uretimi (S2 ARD grid'ine uygun)
    with rasterio.open(raster_ref_path) as src:
        ref_transform = src.transform
        ref_shape = (src.height, src.width)
        ref_crs = src.crs
        if ref_crs.to_epsg() != 32636:
            raise ValueError(f"Raster CRS != EPSG:32636 (T1.4 ARD beklenir)")

    mask_arr = rasterize(
        [(buffer_union, IGNORE_VALUE)],
        out_shape=ref_shape,
        transform=ref_transform,
        fill=0,
        dtype=np.uint8,
    )

    pct = (mask_arr == IGNORE_VALUE).sum() / mask_arr.size * 100
    print(f"  Ignore mask oran: %{pct:.2f} (sanity: %2-5 beklenir)")

    profile = {
        "driver": "GTiff",
        "dtype": "uint8",
        "count": 1,
        "width": ref_shape[1],
        "height": ref_shape[0],
        "transform": ref_transform,
        "crs": "EPSG:32636",
        "nodata": 0,
        "compress": "lzw",
    }
    Path(out_mask_tif).parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_mask_tif, "w", **profile) as dst:
        dst.write(mask_arr, 1)
    print(f"  Ignore mask TIF: {out_mask_tif}")

    print(f"\n[T2.6] DONE")
    print(f"  ✓ WDPA buffer GPKG hazir")
    print(f"  ✓ Ignore mask TIF hazir (255 = ignore_index)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wdpa", default="data/raw/wdpa_goreme.gpkg")
    ap.add_argument("--raster-ref", default="data/raw/s2_l2a_avanos_rgb.tif")
    ap.add_argument("--out-buffer", default="data/labels/wdpa_buffer.gpkg")
    ap.add_argument("--out-mask", default="data/labels/ignore_mask.tif")
    args = ap.parse_args()
    main(args.wdpa, args.raster_ref, args.out_buffer, args.out_mask)
