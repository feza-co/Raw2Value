"""T1.9 — ARD dogrulama + data/manifest.json uretimi.

Giris  : data/ard/full_ard_20m.tif, data/tiles/, data/s1_stack/, data/dem.tif, data/slope.tif
Cikis  : data/manifest.json  (P3/P4/P5 tarafından okunur)

Manifest P3 DataLoader'ı, P4 fuse_confidence()'ı ve P5 dashboard katmanlarını besler.
Dogrulama basarisizsa cikis kodu 1 ile durur — pipeline otomatik durur.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio

REPO = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO / "data/manifest.json"
ARD_PATH      = REPO / "data/ard/full_ard_20m.tif"
TILES_DIR     = REPO / "data/tiles"
S1_PATH       = REPO / "data/s1_stack/s1_vvvh_avanos.tif"
DEM_PATHS     = [REPO / "data/dem.tif", REPO / "data/dem/dem_avanos.tif"]
SLOPE_PATHS   = [REPO / "data/slope.tif", REPO / "data/dem/slope_avanos.tif"]
NODATA        = -9999.0
REFLECTANCE_SCALE = 10000.0

EXPECTED_BANDS = 17
EXPECTED_RES   = 20.0        # metre
EXPECTED_CRS   = "EPSG:32636"
NODATA_THRESH  = 0.05        # %5

BAND_META = [
    {"index": 0,  "name": "B2",           "description": "Blue 490nm",            "source": "Sentinel-2 L2A", "unit": "reflectance_scaled"},
    {"index": 1,  "name": "B3",           "description": "Green 560nm",           "source": "Sentinel-2 L2A", "unit": "reflectance_scaled"},
    {"index": 2,  "name": "B4",           "description": "Red 665nm",             "source": "Sentinel-2 L2A", "unit": "reflectance_scaled"},
    {"index": 3,  "name": "B5",           "description": "Red Edge 705nm",        "source": "Sentinel-2 L2A", "unit": "reflectance_scaled"},
    {"index": 4,  "name": "B6",           "description": "Red Edge 740nm",        "source": "Sentinel-2 L2A", "unit": "reflectance_scaled"},
    {"index": 5,  "name": "B7",           "description": "Red Edge 783nm",        "source": "Sentinel-2 L2A", "unit": "reflectance_scaled"},
    {"index": 6,  "name": "B8",           "description": "NIR 842nm",             "source": "Sentinel-2 L2A", "unit": "reflectance_scaled"},
    {"index": 7,  "name": "B8A",          "description": "NIR Narrow 865nm",      "source": "Sentinel-2 L2A", "unit": "reflectance_scaled"},
    {"index": 8,  "name": "B11",          "description": "SWIR 1610nm",           "source": "Sentinel-2 L2A", "unit": "reflectance_scaled"},
    {"index": 9,  "name": "B12",          "description": "SWIR 2190nm",           "source": "Sentinel-2 L2A", "unit": "reflectance_scaled"},
    {"index": 10, "name": "VV_dB",        "description": "S1 GRD VV polarization","source": "Sentinel-1 GRD", "unit": "dB"},
    {"index": 11, "name": "VH_dB",        "description": "S1 GRD VH polarization","source": "Sentinel-1 GRD", "unit": "dB"},
    {"index": 12, "name": "DEM",          "description": "Copernicus GLO-30 elevation","source": "Copernicus DEM", "unit": "metres"},
    {"index": 13, "name": "slope",        "description": "Terrain slope",          "source": "ee.Terrain.slope", "unit": "degrees"},
    {"index": 14, "name": "NDVI",         "description": "(B8-B4)/(B8+B4)",        "source": "derived_T1.7", "unit": "index [-1,1]"},
    {"index": 15, "name": "BSI",          "description": "((B11+B4)-(B8+B2))/((B11+B4)+(B8+B2))","source": "derived_T1.7", "unit": "index [-1,1]"},
    {"index": 16, "name": "Albedo",       "description": "Liang 2001 shortwave",   "source": "derived_T1.7", "unit": "fraction [0,1]"},
]


def _fail(msg: str):
    print(f"[MANIFEST ERROR] {msg}")
    sys.exit(1)


def _validate_ard():
    if not ARD_PATH.exists():
        _fail(f"full_ard_20m.tif bulunamadi: {ARD_PATH}")

    with rasterio.open(ARD_PATH) as src:
        n_bands = src.count
        res_x   = abs(src.transform.a)
        res_y   = abs(src.transform.e)
        crs_str = src.crs.to_epsg()
        bounds  = src.bounds
        height  = src.height
        width   = src.width

        # Bant sayisi
        if n_bands != EXPECTED_BANDS:
            _fail(f"Bant sayisi {n_bands}, beklenen {EXPECTED_BANDS}")

        # CRS
        if crs_str != 32636:
            _fail(f"CRS EPSG:{crs_str}, beklenen EPSG:32636")

        # Cozunurluk (%5 tolerans)
        if not (abs(res_x - EXPECTED_RES) < 1.0 and abs(res_y - EXPECTED_RES) < 1.0):
            _fail(f"Cozunurluk {res_x}x{res_y} m, beklenen ~{EXPECTED_RES} m")

        # NoData orani (tum bantlarda ortalama)
        total_px = n_bands * height * width
        nd_count = 0
        band_counts = np.zeros(n_bands, dtype=np.float64)
        band_sums = np.zeros(n_bands, dtype=np.float64)
        band_sums_sq = np.zeros(n_bands, dtype=np.float64)
        CHUNK = 4  # bellegi korumak icin bant gruplari
        for band_group in range(0, n_bands, CHUNK):
            bands = list(range(band_group + 1, min(band_group + CHUNK + 1, n_bands + 1)))
            arr = src.read(bands).astype(np.float64)
            valid = np.isfinite(arr) & (arr != NODATA)
            nd_count += int(np.sum(~valid))
            for local_idx, band_no in enumerate(bands):
                vals = arr[local_idx][valid[local_idx]]
                out_idx = band_no - 1
                band_counts[out_idx] += vals.size
                band_sums[out_idx] += vals.sum(dtype=np.float64)
                band_sums_sq[out_idx] += np.square(vals).sum(dtype=np.float64)

        nd_frac = nd_count / total_px
        if nd_frac > NODATA_THRESH:
            _fail(f"NoData orani {nd_frac:.2%}, esik {NODATA_THRESH:.0%}")

    means = np.divide(
        band_sums,
        band_counts,
        out=np.full_like(band_sums, np.nan),
        where=band_counts > 0,
    )
    variances = np.divide(
        band_sums_sq,
        band_counts,
        out=np.full_like(band_sums_sq, np.nan),
        where=band_counts > 0,
    ) - np.square(means)
    stds = np.sqrt(np.maximum(variances, 0.0))
    band_stats = [
        {"mean": float(means[i]), "std": float(stds[i])}
        for i in range(n_bands)
    ]

    print(f"[T1.9] ARD dogrulama OK — {n_bands} bant, {res_x:.0f}m, EPSG:{crs_str}")
    print(f"  NoData: {nd_frac:.2%}, boyut: {ARD_PATH.stat().st_size/1e6:.1f} MB")

    return (
        {
            "path": str(ARD_PATH.relative_to(REPO)),
            "band_count": n_bands,
            "resolution_m": float(res_x),
            "crs": EXPECTED_CRS,
            "bounds": {"west": bounds.left, "south": bounds.bottom, "east": bounds.right, "north": bounds.top},
            "shape": [height, width],
            "nodata": NODATA,
            "nodata_pct": round(nd_frac * 100, 3),
            "size_mb": round(ARD_PATH.stat().st_size / 1e6, 1),
        },
        band_stats,
    )


def _bands_with_stats(band_stats):
    bands = []
    for meta, stats in zip(BAND_META, band_stats):
        item = dict(meta)
        item["mean"] = stats["mean"]
        item["std"] = stats["std"]
        bands.append(item)
    return bands


def _count_tiles() -> dict:
    tif_list = sorted(TILES_DIR.glob("*.tif"))
    if not tif_list:
        _fail(f"Tile klasoru bos: {TILES_DIR}. Once T1.8 calistirin.")

    idx_file = TILES_DIR / "tile_index.json"
    tile_info = {}
    if idx_file.exists():
        with open(idx_file) as f:
            tile_info = json.load(f)

    print(f"[T1.9] Tile sayisi: {len(tif_list)}")
    return {
        "tiles_dir": str(TILES_DIR.relative_to(REPO)),
        "count": len(tif_list),
        "tile_size": tile_info.get("tile_size", 256),
        "overlap": tile_info.get("overlap", 32),
        "stride": tile_info.get("stride", 224),
    }


def _check_ancillary() -> dict:
    result = {}
    candidates = [
        ("s1_stack", [S1_PATH]),
        ("dem", DEM_PATHS),
        ("slope", SLOPE_PATHS),
    ]
    for label, paths in candidates:
        path = next((p for p in paths if p.exists()), None)
        if path is not None:
            result[label] = str(path.relative_to(REPO))
        else:
            print(f"[UYARI] {label} bulunamadi: {[str(p) for p in paths]}")
    return result


def main():
    print("[T1.9] ARD dogrulama + manifest uretimi basliyor...")

    ard_info, band_stats = _validate_ard()
    tile_info  = _count_tiles()
    ancillary  = _check_ancillary()
    bands = _bands_with_stats(band_stats)

    manifest = {
        "created":    datetime.now(timezone.utc).isoformat(),
        "project":    "Pomzadoya",
        "version":    "modul-a-v2",
        "scale":      REFLECTANCE_SCALE,
        "ard": ard_info,
        "mean": [b["mean"] for b in bands],
        "std": [b["std"] for b in bands],
        "bands": bands,
        "tiles": tile_info,
        "files": {
            "full_ard": str(ARD_PATH.relative_to(REPO)),
            **ancillary,
        },
    }

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[T1.9] TAMAMLANDI -> {MANIFEST_PATH}")
    print(f"  Bantlar: {len(BAND_META)}, Tile: {tile_info['count']}, NoData: {ard_info['nodata_pct']}%")


if __name__ == "__main__":
    main()
