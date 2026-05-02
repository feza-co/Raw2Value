#!/usr/bin/env bash
# P1 — Pomzadoya ARD pipeline (Modul A v2)
# Akis: T1.2 AOI -> T1.3 S2 GEE (asenkron) -> T1.4 S2 ARD ->
#       T1.5 S1 GEE (asenkron, paralel) -> T1.6 DEM GEE (asenkron, paralel) ->
#       T1.7 17-kanal co-reg -> T1.8 tile split -> T1.9 manifest
#       T1.10 Landsat GEE (saat 11, paralel asenkron)
#
# GEE task'lar asenkron — scripti calistir, GEE Tasks panelinden izle,
# Drive'dan ilgili data/ klasorune indir, sonra local scripti calistir.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

echo "[P1] pipeline basliyor — repo=$REPO"
echo "---------------------------------------------"

# ---------------------------------------------------------------------------
# T1.2 — AOI uretimi (yerel, ~5 sn)
# ---------------------------------------------------------------------------
echo "[P1][T1.2] AOI uretimi basliyor..."
python code/p1/02_aoi_avanos.py
echo "[P1][T1.2] TAMAM — data/avanos_aoi.geojson, .gpkg"

# ---------------------------------------------------------------------------
# T1.3 — S2 L2A GEE export (asenkron ~30 dk)
# ---------------------------------------------------------------------------
echo "[P1][T1.3] S2 GEE export task tetikleniyor..."
python code/p1/03_sentinel2_l2a_fetch.py
echo "[P1][T1.3] GEE task baslatildi. Drive/Pomzadoya_GEE_exports/'dan:"
echo "  s2_l2a_avanos_median_2024_20m.tif → data/s2_raw/"
echo "  ~30 dk bekle, sonra T1.4 calistir."

# ---------------------------------------------------------------------------
# T1.4 — S2 ARD co-registration (yerel, Drive download sonrasi)
# ---------------------------------------------------------------------------
S2_RAW="data/s2_raw/s2_l2a_avanos_median_2024_20m.tif"
if [ -f "$S2_RAW" ]; then
  echo "[P1][T1.4] S2 co-registration basliyor..."
  python code/p1/04_s2_coregistration.py
  echo "[P1][T1.4] TAMAM — data/ard/s2_ard_20m.tif"
else
  echo "[P1][T1.4] ATLANDI — $S2_RAW bulunamadi."
  echo "  Drive download sonrasi 'bash code/p1/run_pipeline.sh' tekrar calistir."
fi

# ---------------------------------------------------------------------------
# T1.5 — S1 GRD GEE export (asenkron ~20 dk, T1.3 ile paralel baslatilabilir)
# ---------------------------------------------------------------------------
echo "[P1][T1.5] S1 GRD GEE export task tetikleniyor..."
python code/p1/05_sentinel1_grd_fetch.py
echo "[P1][T1.5] GEE task baslatildi. Drive'dan:"
echo "  s1_vvvh_avanos.tif → data/s1_stack/"

# ---------------------------------------------------------------------------
# T1.6 — Copernicus DEM + slope GEE export (asenkron ~10 dk, paralel)
# ---------------------------------------------------------------------------
echo "[P1][T1.6] DEM + slope GEE export task tetikleniyor..."
python code/p1/06_dem_slope.py
echo "[P1][T1.6] GEE task baslatildi. Drive'dan:"
echo "  dem_avanos.tif → data/dem.tif"
echo "  slope_avanos.tif → data/slope.tif"

# ---------------------------------------------------------------------------
# T1.7 — 17-kanal Full ARD co-registration (yerel, T1.4+T1.5+T1.6 indikten sonra)
# ---------------------------------------------------------------------------
ARD_S2="data/ard/s2_ard_20m.tif"
S1_STACK="data/s1_stack/s1_vvvh_avanos.tif"
DEM="data/dem.tif"
SLOPE="data/slope.tif"

if [ -f "$ARD_S2" ] && [ -f "$S1_STACK" ] && [ -f "$DEM" ] && [ -f "$SLOPE" ]; then
  echo "[P1][T1.7] Full ARD 17-kanal co-registration basliyor..."
  python code/p1/07_full_coregistration.py
  echo "[P1][T1.7] TAMAM — data/ard/full_ard_20m.tif (17 bant)"
  echo "  [CRITICAL] P3 saat 8'de bu dosyayi bekliyor — grup chat bildir."
else
  echo "[P1][T1.7] ATLANDI — giris dosyalari eksik:"
  [ ! -f "$ARD_S2" ]   && echo "  eksik: $ARD_S2"
  [ ! -f "$S1_STACK" ] && echo "  eksik: $S1_STACK"
  [ ! -f "$DEM" ]      && echo "  eksik: $DEM"
  [ ! -f "$SLOPE" ]    && echo "  eksik: $SLOPE"
fi

# ---------------------------------------------------------------------------
# T1.8 — Tile splitting 256x256 + 32 px overlap
# ---------------------------------------------------------------------------
FULL_ARD="data/ard/full_ard_20m.tif"
if [ -f "$FULL_ARD" ]; then
  echo "[P1][T1.8] Tile splitting basliyor (256x256, overlap=32)..."
  python code/p1/08_tile_splitting.py
  echo "[P1][T1.8] TAMAM — data/tiles/"
  echo "  [CRITICAL] P2 T2.8 ve P3 DataLoader bu klasoru bekliyor."
else
  echo "[P1][T1.8] ATLANDI — $FULL_ARD bulunamadi. Once T1.7 tamamla."
fi

# ---------------------------------------------------------------------------
# T1.9 — ARD dogrulama + manifest.json
# ---------------------------------------------------------------------------
if [ -f "$FULL_ARD" ] && [ -d "data/tiles" ]; then
  echo "[P1][T1.9] Manifest uretiliyor..."
  python code/p1/09_export_manifest.py
  echo "[P1][T1.9] TAMAM — data/manifest.json"
  echo "  [CRITICAL] P3/P4/P5 manifest'i okur — grup chat bildir."
else
  echo "[P1][T1.9] ATLANDI — once T1.7 ve T1.8 tamamla."
fi

# ---------------------------------------------------------------------------
# T1.10 — Landsat Tier 2 snapshot (saat 11, asenkron paralel — 5 job)
# ---------------------------------------------------------------------------
echo ""
echo "[P1][T1.10] Landsat 5 yil snapshot GEE export basliyor..."
echo "  Yillar: 1985, 1990, 2000, 2010, 2025"
python code/p1/10_landsat_snapshots.py
echo "[P1][T1.10] GEE task'lari baslatildi (~30 dk). Drive'dan:"
echo "  L5_1985.tif, L5_1990.tif, L7_2000.tif, L7_2010.tif, L9_2025.tif → data/landsat/"
echo "  P5 saat 13'te bekliyor — grup chat bildir."

echo ""
echo "---------------------------------------------"
echo "[P1] pipeline adimlari tamamlandi."
echo "GEE task'lar asenkron — Tasks panelinden izle, indikten sonra tekrar calistir."
