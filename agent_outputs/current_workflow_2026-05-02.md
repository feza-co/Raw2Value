# Modul A Current Workflow - 2026-05-02

Bu dosya P1-P5 status dosyalarindan ve 2026-05-02 AOI duzeltmesinden sonra kalan
isi tek siraya indirir.

## 0. Durum Ozeti

- Kök neden: P2 CSV/poligon noktalarinin 24/27'si eski P1 rasterinin guneyinde kaldi.
- Duzeltme: AOI bbox `34.60,38.40,35.00,38.90` olarak genisletildi.
- Kontrol: `02_mapeg_query.csv` icindeki 27 noktanin 27'si yeni AOI icinde.
- Mevcut `data/ard/full_ard_20m.tif` hala eski kuzey rasterdir; P1 raster tekrar uretilmeden P2/P3 training baslamaz.

## 1. Baslatilan GEE Tasklari

2026-05-02'de `pomza` Python 3.11 venv ile su tasklar baslatildi:

| Cikti | Task ID | Drive hedefi | Lokal hedef |
|---|---|---|---|
| S2 L2A median 20m | `QTFPDUFGFLDCRFK5GMNCBIJ3` | `Pomzadoya_GEE_exports/s2_l2a_avanos_median_2024_20m.tif` | `data/s2_raw/s2_l2a_avanos_median_2024_20m.tif` |
| S1 VV/VH 20m | `L5UN3UXMSXWSWZ2GZK6EXEGR` | `Pomzadoya_GEE_exports/s1_vvvh_avanos.tif` | `data/s1_stack/s1_vvvh_avanos.tif` |
| DEM 20m | `EKDCEF2BSIAC2KBGBA2DHSHX` | `Pomzadoya_GEE_exports/dem_avanos.tif` | `data/dem/dem_avanos.tif` |
| Slope 20m | `JYQ777XV2RQZ2KQOLIANDK52` | `Pomzadoya_GEE_exports/slope_avanos.tif` | `data/dem/slope_avanos.tif` |

## 2. P1 - Raster Yeniden Uretim

GEE tasklari tamamlaninca Drive'dan yukaridaki dosyalari lokal hedeflere indir.
Sonra:

```powershell
.\pomza\Scripts\python.exe code/p1/04_s2_coregistration.py
.\pomza\Scripts\python.exe code/p1/07_full_coregistration.py
.\pomza\Scripts\python.exe code/p1/08_tile_splitting.py
.\pomza\Scripts\python.exe code/p1/09_export_manifest.py
```

Beklenen P1 ciktilari:

- `data/ard/s2_ard_20m.tif`
- `data/ard/full_ard_20m.tif`
- `data/tiles/tile_index.json`
- `data/manifest.json`

Verify:

```powershell
.\pomza\Scripts\python.exe -c "import rasterio; from rasterio.warp import transform_bounds; p='data/ard/full_ard_20m.tif'; s=rasterio.open(p); print(s.width,s.height,s.crs); print(transform_bounds(s.crs,'EPSG:4326',*s.bounds))"
```

Bounds lat olarak en az `38.40-38.90` araligini kapsamali.

## 3. P2 - Label Pipeline

P1 yeni raster geldikten sonra:

```powershell
.\pomza\Scripts\python.exe code/p2/04_pixel_sampling.py `
  --positives data/labels/positive_polygons.gpkg `
  --raster data/ard/full_ard_20m.tif `
  --out data/labels/positive_pixels.gpkg
```

Tarim maskesi opsiyonel ama onerilir:

```powershell
.\pomza\Scripts\python.exe code/p2/10_agriculture_mask.py --gee-export
```

Drive'dan `esa_worldcover_cropland_avanos.tif` indirildikten sonra:

```powershell
.\pomza\Scripts\python.exe code/p2/10_agriculture_mask.py `
  --worldcover data/raw/esa_worldcover_cropland_avanos.tif `
  --raster-ref data/ard/full_ard_20m.tif `
  --out data/labels/agriculture_mask.tif `
  --out-vector data/labels/agriculture_polygons.gpkg
```

WDPA, negatifler, CV ve final mask:

```powershell
.\pomza\Scripts\python.exe code/p2/06_wdpa_ignore_mask.py `
  --wdpa "data/raw/WDPA_WDOECM_May2026_Public_478637_shp-polygons.shp" `
  --raster-ref data/ard/full_ard_20m.tif `
  --out-buffer data/labels/wdpa_buffer.gpkg `
  --out-mask data/labels/ignore_mask.tif

.\pomza\Scripts\python.exe code/p2/05_negative_sampling.py `
  --positives data/labels/positive_polygons.gpkg `
  --raster data/ard/full_ard_20m.tif `
  --aoi data/aoi/avanos_aoi.gpkg `
  --agri-mask data/labels/agriculture_mask.tif `
  --agri-frac 0.30 `
  --out data/labels/negative_pixels.gpkg

.\pomza\Scripts\python.exe code/p2/07_spatial_block_cv.py `
  --manifest data/tiles/tile_index.json `
  --raster-ref data/ard/full_ard_20m.tif `
  --out data/labels/blok_cv_split.json

.\pomza\Scripts\python.exe code/p2/08_rasterize_mask.py `
  --positives data/labels/positive_pixels.gpkg `
  --negatives data/labels/negative_pixels.gpkg `
  --ignore-mask data/labels/ignore_mask.tif `
  --raster-ref data/ard/full_ard_20m.tif `
  --out data/labels/full_mask.tif
```

Critical P2 ciktilari:

- `data/labels/positive_pixels.gpkg`
- `data/labels/negative_pixels.gpkg`
- `data/labels/ignore_mask.tif`
- `data/labels/blok_cv_split.json`
- `data/labels/full_mask.tif`

## 4. P3 - Training

P3 su iki P2 dosyasini bekliyor:

- `data/labels/full_mask.tif`
- `data/labels/blok_cv_split.json`

P1'den de:

- `data/tiles/`
- `data/manifest.json`

Sonra `agent_outputs/p3_t3_5_runblock.md` icindeki training komutu calisir.
Training baslamadan once P1 manifest mean/std degerleri guncel ARD'den alinmali.

## 5. P4 - Spektral Katmanlar

Yeni P1 raster geldikten sonra P4 katmanlari ayni genisletilmis gridde tekrar
kontrol edilmeli:

```powershell
.\pomza\Scripts\python.exe code/p4/04_s2_indices.py --ard data/ard/s2_ard_20m.tif --out data/layers
.\pomza\Scripts\python.exe code/p4/06_resample_to_s2_grid.py `
  --reference data/ard/s2_ard_20m.tif `
  --inputs data/layers/aster_qi.tif data/layers/aster_ci.tif data/layers/aster_sio2.tif `
  --out data/layers
```

P3 raw probability geldikten sonra:

```powershell
.\pomza\Scripts\python.exe code/p4/fuse_confidence.py `
  --raw data/inference/raw_prob.tif `
  --qi data/layers/aster_qi_20m.tif `
  --ci data/layers/aster_ci_20m.tif `
  --out data/layers/final_confidence.tif `
  --report reports/fuse_report.json
```

## 6. P5 - Dashboard

P5 ana bekledikleri:

- P1 Landsat/S1 ciktilari
- P3 `raw_prob.tif`
- P4 `final_confidence.tif`
- P2/P5 WDPA buffer

Sonra:

```powershell
.\pomza\Scripts\python.exe code/p5/04_s1_amplitude_diff.py
.\pomza\Scripts\python.exe code/p5/06_landsat_roy_harmonization.py
.\pomza\Scripts\python.exe code/p5/08_historical_pomza_inference.py
.\pomza\Scripts\python.exe code/p5/09_layer_manifest.py
streamlit run code/p5/dashboard.py
```

## 7. Bugun Kalan Kritik Is

1. GEE Tasks panelinden 4 taskin bittigini kontrol et.
2. 4 GeoTIFF'i Drive'dan lokal hedeflere indir.
3. P1 local pipeline'i `04 -> 07 -> 08 -> 09` calistir.
4. P2 `04/06/05/07/08` label pipeline'ini calistir.
5. P3 training'i baslat.
6. P4 fused confidence ve P5 dashboard entegrasyonunu yenile.

## 8. 2026-05-02 16:20 Guncel Gerceklesme

Tamamlananlar:

- 4 yeni GEE TIFF lokal hedeflere indirildi ve dogrulandi:
  - S2/S1/DEM/slope: `1796x2810`, EPSG:32636, 20 m.
  - WGS84 bounds yaklasik `34.589-35.014 / 38.394-38.906`.
- P1 tamamlandi:
  - `data/ard/s2_ard_20m.tif`
  - `data/ard/full_ard_20m.tif`
  - `data/ard/s2_rgb.tif`
  - `data/tiles/tile_index.json` (`104` tile)
  - `data/manifest.json`
- P2 critical path tamamlandi:
  - `data/labels/positive_pixels.gpkg` (`952` px)
  - `data/aoi/wdpa_goreme.gpkg` OSM relation `252585` fallback
  - `data/labels/wdpa_buffer.gpkg`
  - `data/labels/ignore_mask.tif`
  - `data/labels/negative_pixels.gpkg` (`6000` px)
  - `data/labels/blok_cv_split.json`
  - `data/labels/full_mask.tif`
- P4/P5 demo layers guncellendi:
  - `data/layers/s2_{ndvi,bsi,albedo,sabins}.tif`
  - `data/layers/aster_{qi,ci,sio2}.tif`
  - `data/layers/aster_{qi,ci,sio2}_20m.tif`
  - `data/inference/raw_prob.tif` Plan B fallback
  - `data/layers/final_confidence.tif`
  - `data/layers.json` Plan A (`6` layer)
- Hackathon kural uyumu icin P5 dashboard'a `4) Cave2Cloud Uyumu` sayfasi eklendi:
  - OSRM/OpenStreetMap dinamik rota mesafesi.
  - CO2 hesabı.
  - TCMB EVDS kur entegrasyonu (`TCMB_EVDS_API_KEY` gerekli).

Acik kalanlar:

- ESA WorldCover agriculture export task `MEA2PS6722KFTWJXVZWM5443` Drive'dan indirilince:
  - `code/p2/10_agriculture_mask.py` align/vectorize calistir.
  - Istenirse `05_negative_sampling.py --agri-mask ...` tekrar calistir.
- TCMB EVDS demo icin ortam degiskeni ayarlanmali:
  - `$env:TCMB_EVDS_API_KEY="..."`
- P3 gercek training hala yapilmadi; `full_mask.tif` artik hazir.
- ASTER valid coverage yeni AOI'de yaklasik `%19.9`; zaman varsa genis AOI icin yeni ASTER sahnesi sorgulanabilir.
