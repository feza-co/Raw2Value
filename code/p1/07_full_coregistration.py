"""T1.7 — 17-kanal Full ARD co-registration + turev bantlar.

Giris  : data/ard/s2_ard_20m.tif    (10 bant, S2 L2A)
         data/s1_stack/s1_vvvh_avanos.tif  (2 bant: VV_dB, VH_dB)
         data/dem.tif                (1 bant: yukseklik)
         data/slope.tif              (1 bant: egim)
Cikis  : data/ard/full_ard_20m.tif  (17 bant, 20m, EPSG:32636, NoData=-9999)
Bant sirasi (Karar #15 + P3 DataLoader sozlesmesi):
  0:B2  1:B3  2:B4  3:B5  4:B6  5:B7  6:B8  7:B8A  8:B11  9:B12
  10:VV_dB  11:VH_dB  12:DEM  13:slope
  14:NDVI  15:BSI  16:Albedo(Liang2001)
CRS   : EPSG:32636 (UTM 36N)
Cozunurluk : 20 m — tum katmanlar S2 grid'e warp edilir
"""
import sys
from pathlib import Path
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject, calculate_default_transform

REPO = Path(__file__).resolve().parents[2]

S2_ARD   = REPO / "data/ard/s2_ard_20m.tif"
S1_STACK = REPO / "data/s1_stack/s1_vvvh_avanos.tif"
DEM_FILE = REPO / "data/dem/dem_avanos.tif"
SLOPE_FILE = REPO / "data/dem/slope_avanos.tif"
OUTPUT   = REPO / "data/ard/full_ard_20m.tif"
NODATA   = -9999.0

BAND_NAMES = [
    "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12",
    "VV_dB", "VH_dB", "DEM", "slope",
    "NDVI", "BSI", "Albedo_Liang2001",
]


def _check_inputs():
    missing = [p for p in [S2_ARD, S1_STACK, DEM_FILE, SLOPE_FILE] if not p.exists()]
    if missing:
        print("[ERROR] Eksik giris dosyalari:")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)


def _warp_to_ref(src_path: Path, ref_profile: dict) -> np.ndarray:
    """Kaynak dosyayi referans S2 grid'e bilinear warp et, float32 dondur."""
    with rasterio.open(src_path) as src:
        n_bands = src.count
        data = np.full(
            (n_bands, ref_profile["height"], ref_profile["width"]),
            NODATA, dtype=np.float32,
        )
        for i in range(1, n_bands + 1):
            reproject(
                source=rasterio.band(src, i),
                destination=data[i - 1],
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=ref_profile["transform"],
                dst_crs=ref_profile["crs"],
                resampling=Resampling.bilinear,
                src_nodata=src.nodata,
                dst_nodata=NODATA,
            )
    data[~np.isfinite(data)] = NODATA
    return data


def _valid(arr: np.ndarray) -> np.ndarray:
    return np.isfinite(arr) & (arr != NODATA)


def _compute_slope_from_dem(dem_data: np.ndarray, pixel_size: float) -> np.ndarray:
    """DEM bandindan derece cinsinden slope uret."""
    dem = dem_data[0].astype(np.float32)
    valid = _valid(dem)
    if not valid.any():
        return np.full_like(dem_data, NODATA, dtype=np.float32)

    filled = dem.copy()
    filled[~valid] = float(np.nanmean(dem[valid]))
    grad_y, grad_x = np.gradient(filled, pixel_size, pixel_size)
    slope = np.degrees(np.arctan(np.sqrt(np.square(grad_x) + np.square(grad_y))))
    slope[~valid] = NODATA
    return slope[np.newaxis].astype(np.float32)


def _compute_ndvi(b8: np.ndarray, b4: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = np.where(
            (b8 + b4) != 0,
            (b8 - b4) / (b8 + b4),
            NODATA,
        )
    ndvi[(b8 == NODATA) | (b4 == NODATA)] = NODATA
    return ndvi.astype(np.float32)


def _compute_bsi(b11: np.ndarray, b4: np.ndarray, b8: np.ndarray, b2: np.ndarray) -> np.ndarray:
    """Bare Soil Index: ((B11+B4)-(B8+B2)) / ((B11+B4)+(B8+B2))"""
    with np.errstate(divide="ignore", invalid="ignore"):
        num = (b11 + b4) - (b8 + b2)
        den = (b11 + b4) + (b8 + b2)
        bsi = np.where(den != 0, num / den, NODATA)
    mask = (b11 == NODATA) | (b4 == NODATA) | (b8 == NODATA) | (b2 == NODATA)
    bsi[mask] = NODATA
    return bsi.astype(np.float32)


def _compute_albedo(s2: np.ndarray) -> np.ndarray:
    """Liang 2001 shortwave albedo:
    0.356*B2 + 0.130*B4 + 0.373*B8 + 0.085*B11 + 0.072*B12 - 0.0018
    Bantlar 0-indexed: B2=0, B3=1, B4=2, B5=3, B6=4, B7=5, B8=6, B8A=7, B11=8, B12=9
    """
    b2, b4, b8, b11, b12 = s2[0], s2[2], s2[6], s2[8], s2[9]
    mask = (b2 == NODATA) | (b4 == NODATA) | (b8 == NODATA) | (b11 == NODATA) | (b12 == NODATA)
    valid = ~mask
    reflectance_scale = 1e-4 if valid.any() and np.nanmax(b2[valid]) > 1.5 else 1.0
    b2_s, b4_s, b8_s = b2 * reflectance_scale, b4 * reflectance_scale, b8 * reflectance_scale
    b11_s, b12_s = b11 * reflectance_scale, b12 * reflectance_scale
    albedo = (0.356 * b2_s + 0.130 * b4_s + 0.373 * b8_s
              + 0.085 * b11_s + 0.072 * b12_s - 0.0018)
    albedo = np.clip(albedo, 0.0, 1.0)
    albedo[mask] = NODATA
    return albedo.astype(np.float32)


def main():
    _check_inputs()

    # Referans grid: S2 ARD (20m, EPSG:32636)
    with rasterio.open(S2_ARD) as ref:
        ref_profile = ref.profile.copy()
        s2_data = ref.read().astype(np.float32)
        s2_nodata = ref.nodata if ref.nodata is not None else 0.0

    # NoData tutarli yap
    s2_data[s2_data == s2_nodata] = NODATA
    s2_data[~np.isfinite(s2_data)] = NODATA
    h, w = ref_profile["height"], ref_profile["width"]
    print(f"[T1.7] Referans grid: {w}x{h} px, {ref_profile['crs']}")

    # S1 warp
    print("[T1.7] S1 GRD warping...")
    s1_data = _warp_to_ref(S1_STACK, ref_profile)

    # DEM warp
    print("[T1.7] DEM warping...")
    dem_data = _warp_to_ref(DEM_FILE, ref_profile)

    # Slope warp
    print("[T1.7] Slope warping...")
    slope_data = _warp_to_ref(SLOPE_FILE, ref_profile)
    if not _valid(slope_data).any():
        print("[T1.7] Slope kaynak raster bos; DEM'den slope fallback hesaplaniyor...")
        slope_data = _compute_slope_from_dem(dem_data, abs(ref_profile["transform"].a))

    # Turev bantlar
    print("[T1.7] NDVI, BSI, Albedo hesaplaniyor...")
    ndvi   = _compute_ndvi(s2_data[6], s2_data[2])           # B8, B4
    bsi    = _compute_bsi(s2_data[8], s2_data[2], s2_data[6], s2_data[0])
    albedo = _compute_albedo(s2_data)

    # Stack: 17 bant
    bands_17 = np.concatenate([
        s2_data,           # 0-9 : B2..B12 (10 bant)
        s1_data,           # 10-11: VV_dB, VH_dB
        dem_data,          # 12: DEM
        slope_data,        # 13: slope
        ndvi[np.newaxis],  # 14: NDVI
        bsi[np.newaxis],   # 15: BSI
        albedo[np.newaxis] # 16: Albedo
    ], axis=0)

    assert bands_17.shape[0] == 17, f"Bant sayisi hatalı: {bands_17.shape[0]}"

    # Yazma
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out_profile = ref_profile.copy()
    out_profile.update({
        "count": 17,
        "dtype": "float32",
        "nodata": NODATA,
        "compress": "lzw",
        "predictor": 2,
        "bigtiff": "IF_SAFER",
    })

    with rasterio.open(OUTPUT, "w", **out_profile) as dst:
        for i, (arr, name) in enumerate(zip(bands_17, BAND_NAMES), start=1):
            dst.write(arr, i)
            dst.update_tags(i, name=name)

    size_mb = OUTPUT.stat().st_size / 1e6
    print(f"[T1.7] TAMAMLANDI -> {OUTPUT}")
    print(f"  Boyut: {size_mb:.1f} MB, Bantlar: 17, Grid: {w}x{h}@20m")

    # Sanity
    nodata_frac = (bands_17 == NODATA).mean()
    print(f"  NoData orani: {nodata_frac:.2%}  (esik: %5)")
    if nodata_frac > 0.05:
        print("  [UYARI] NoData %5 esigini asti — bulut maskelemesi veya AOI kırpma kontrol et")


if __name__ == "__main__":
    main()
