# P4 Spektral Mühendis — DURUM (2026-05-02 güncel)

> **EXECUTION FAZI:** P4'ün tüm bağımsız görevleri (T4.1 → T4.10) tamamlandı.
> Sadece T4.12 GERÇEK koşumu için P3 `raw_prob.tif` bekleniyor; sentetik raw_prob
> ile API + format + alignment doğrulandı. P5 T5.13 dashboard hazır kabul edebilir.

## Üretilen artefaktlar (kod)

| # | Dosya | Görev | Durum |
|---|---|---|---|
| 01 | `code/p4/01_earthdata_setup.md` | T4.1 — Earthdata token + .netrc | ✅ TAMAM (.netrc yazıldı) |
| 02 | `code/p4/02_aster_l1b_download.py` (+ `cmr_query_l1b.py`, `aster_download.py`) | T4.2 — CMR + LP DAAC indirme | ✅ TAMAM (124.5 MB HDF) |
| 03 | `code/p4/03_aster_l1b_to_l2.py` | T4.3 — DOS atmosferik düzeltme | ✅ TAMAM (DOS offsets çıktı) |
| **+** | `code/p4/_geo_aster_tir.py` | T4.3+ georef helper (yeni) | ✅ TAMAM (121 GCP + UTM 36N WKT) |
| 04 | `code/p4/04_s2_indices.py` | T4.4 — NDVI/BSI/Albedo Liang/Sabins | ✅ TAMAM |
| 05 | `code/p4/05_ninomiya_qi.py` | T4.5 — QI=B11²/(B10·B12), CI=B13/B14, SiO₂ | ✅ TAMAM (DOS+georef stack) |
| 06 | `code/p4/06_resample_to_s2_grid.py` | T4.6 — bilinear 20m resample | ✅ TAMAM (gdalwarp + COG) |
| 07 | `code/p4/07_fusion_prototype.py` | T4.7 — sentetik P3 ile füzyon prototipi | ✅ TAMAM |
| **+** | `code/p4/_fetch_copernicus_dem.py` | DEM helper (P1 üretimi gelmedi) | ✅ TAMAM (Copernicus GLO-30 AWS) |
| 08 | `code/p4/08_dem_aspect_hillshade.py` | T4.8 — gdaldem path | ✅ TAMAM |
| 09 | `code/p4/09_layer_export.py` | T4.10 — COG export + manifest | ✅ TAMAM (12 layer, Sabins formula düzeltildi) |
| 10 | `code/p4/fuse_confidence.py` | T4.12 KRİTİK — score-level füzyon API + CLI | ✅ API HAZIR, CLI test PASS |
| 11 | `code/p4/requirements.txt` | bağımlılıklar | ✅ |

## Üretilen veri çıktıları (P5 ana giriş)

| Path | Ne | Boyut | Sanity |
|---|---|---|---|
| `data/aster/AST_L1B_..._00407062020083241_..hdf` | Ham ASTER L1B (2020-07-06, %0 cloud) | 124.5 MB | Avanos AOI içinde |
| `data/aster/AST_TIR_geo_stack_dos.tif` | DOS-uygulanmış georef'li TIR (B10..B14) | 8.3 MB | UTM 36N, 90m, 5 bant |
| `data/dem/dem.tif` | Copernicus DEM 20m UTM 36N | 4.0 MB | 1137×1327, S2 ARD ile birebir |
| `data/layers/s2_ndvi.tif` | NDVI (Tucker 1979) | 6.8 MB | mean=0.18 ✅ |
| `data/layers/s2_bsi.tif` | BSI (Rikimaru 2002) | 6.8 MB | mean=0.13 ✅ |
| `data/layers/s2_albedo.tif` | Liang 2001 broadband | 6.6 MB | mean=0.23 ✅ |
| `data/layers/s2_sabins.tif` | B11/B12 (Sabins 1999) | 6.3 MB | mean=1.27 ✅ |
| `data/layers/aster_qi.tif` (90m) | Ninomiya QI native | 1.7 MB | mean=1.04, in_range %99.85 ✅ |
| `data/layers/aster_ci.tif` (90m) | Ninomiya CI native | 1.6 MB | mean=1.08, in_range %80.67 ✅ |
| `data/layers/aster_sio2.tif` (90m) | Ninomiya SiO₂ estimator | 1.5 MB | mean=56.4, in_range %99.99 ✅ |
| `data/layers/aster_qi_20m.tif` | QI bilinear → S2 grid | 1.2 MB | %26.4 valid (ASTER coverage) |
| `data/layers/aster_ci_20m.tif` | CI bilinear → S2 grid | 1.1 MB | %26.4 valid |
| `data/layers/aster_sio2_20m.tif` | SiO₂ bilinear → S2 grid | 1.1 MB | %26.4 valid |
| `data/layers/dem_aspect.tif` | Horn 1981 aspect | 5.2 MB | 0..360°, NoData=-9999 |
| `data/layers/dem_hillshade.tif` | Lambertian az=315 alt=45 | 0.9 MB | uint8 0..255 |
| `data/layers/final_confidence.tif` | **P3×P4 FUSED (sentetik raw_prob)** | 1.5 MB | EPSG:32636, 20m, %26.4 valid |
| `data/inference/raw_prob_synth.tif` | Sentetik P3 stand-in (Avanos Gauss bump) | 5.4 MB | max=0.90, mean=0.08 |
| `reports/layers.json` | 12-layer JSON manifest (P5 Folium) | 7 KB | Tüm CRS=EPSG:32636 |
| `reports/layer_docs.md` | İnsan-okunur layer dokümantasyonu | 4 KB | Formül + akademik ref |
| `reports/fuse_report.json` | T4.12 sanity raporu | <1 KB | shape, delta, min/max |

## Tamamlanan Görev Tablosu

| Görev | Durum | Sanity |
|---|---|---|
| T4.1 Earthdata setup | ✅ | .netrc ASCII |
| T4.2 ASTER L1B indirme | ✅ | 124.5 MB, 2020-07-06, %0 cloud |
| T4.3 DOS atmosferik düzeltme | ✅ | TIR DOS offsets B10=1311..B14=1854 (radiance scale OK) |
| T4.3+ Georef refactor | ✅ | 121 GCP → UTM 36N, 90m grid (gdal.Warp+TPS) |
| T4.4 S2 türetilmiş indeksler | ✅ | 4 layer üretildi, mean değerleri bekenenle uyumlu |
| T4.5 Ninomiya QI/CI/SiO₂ | ✅ | QI mean=1.04 in_range %99.85 (Karar #4 doğrulandı) |
| T4.6 Bilinear 20m resample | ✅ | 3 layer S2 grid'inde, identical bounds |
| T4.7 Sentetik füzyon prototipi | ✅ | delta=0.063, max=0.33 |
| T4.8 DEM aspect+hillshade | ✅ | gdaldem path (Horn 1981 + Lambertian) |
| T4.10 Layer export+manifest | ✅ | 12 layer, MD5 + COG |
| **T4.12 Score-level füzyon** | ✅ **API + CLI HAZIR** | shape match, delta>0, NaN propagate, pomza/CI cezaları doğrulandı |

## fuse_confidence API testleri (T4.12 critical contract)

5/5 in-memory sanity test PASS:
1. **Shape/range**: 100×100 raster → output [0,1], shape preserved
2. **NaN propagation**: NaN giriş → NaN çıkış (kapatılmaz)
3. **Shape mismatch**: SystemExit raise (Plan B çağıran taraf)
4. **Pomza-vs-vegetation**: high QI → 5.6× higher confidence than low QI
5. **CI penalty**: low CI bölgesi 18× higher confidence than high CI

## Bekleyen dış girdi (sadece bir tane)

| Bekleyen | Sahibi | Durumu | Etki |
|---|---|---|---|
| `data/inference/raw_prob.tif` (gerçek) | P3 (T3.10) | henüz yok | Mevcut `final_confidence.tif` sentetik proxy ile üretildi; P3 gerçek geldiğinde tek komutla yeniden üretilir |

P3 raw_prob gelirse:
```powershell
$env:PROJ_LIB="C:/temp_proj"; $env:GDAL_DATA="C:/temp_gdal"
.\pomza\Scripts\python.exe code\p4\fuse_confidence.py `
  --raw  data\inference\raw_prob.tif `
  --qi   data\layers\aster_qi_20m.tif `
  --ci   data\layers\aster_ci_20m.tif `
  --out  data\layers\final_confidence.tif `
  --report reports\fuse_report.json
```

## Audit Bulguları + Düzeltmeler

| Bulgu | Etki | Düzeltme |
|---|---|---|
| `09_layer_export.py` Sabins formula `B11/B8` (yanlış) | Manifest yanlış belge | ✅ `B11/B12` + interpretation güncellendi |
| ASTER L1B HDF subdataset CRS yok (transform=identity) | T4.6 resample fail | ✅ `_geo_aster_tir.py` 121 GCP + UTM 36N WKT |
| GDAL EPSG database fail Türkçe path | proj.db açılamıyor | ✅ `C:/temp_proj` + `C:/temp_gdal` ASCII path |
| numpy 2.x rasterio 1.3.8 ABI uyumsuz | rasterio import fail | ✅ `numpy==1.26.4` pin |
| ASTER scene Avanos AOI'sinin %26'sını kapsıyor | final_confidence %26 valid | Plan B (Karar #6 fail bölgesi NaN) — kabul edilebilir |
| SWIR DOS offset 255 (saturated DN) | T4.3 SWIR çıktısı bozuk | T4.5 sadece TIR kullanıyor — etkisi yok |

## Kararlar / Akademik Dayanaklar (kanıtlı)

- **K#3** ASTER L1B → L2 (DOS1, Chavez 1988) ✅
- **K#4** QI = B11²/(B10·B12) **oran-tabanlı** → DOS olsun olmasın QI mean ~1.04 (sanity ile doğrulandı) ✅
- **K#6** `final = raw_prob × QI_norm × (1 − CI_norm)` (T4.12 API + CLI) ✅
- **K#13** S2 albedo Liang 2001 katsayıları aynen kodda ✅
- **K#15** ASTER 90 m → 20 m **bilinear** resample (nearest YASAK) ✅

## Ortam Notları (yeniden çalıştırma için)

- Python venv: `pomza/` (Pomzadoya kökünde)
- GDAL 3.7.1 + rasterio 1.3.8 + numpy 1.26.4
- HDF4/HDF4Image/HDF5/HDF5Image driver mevcut
- PROJ_LIB=`C:/temp_proj`, GDAL_DATA=`C:/temp_gdal` (ASCII path zorunluluğu)
- PYTHONIOENCODING=utf-8, PYTHONUTF8=1 (Windows charmap fix)

## Diğer P'lerle uyum

| P | P4 katkısı | P4 talebi |
|---|---|---|
| P1 | DEM beklerken `_fetch_copernicus_dem.py` ile geçici DEM (P1 T1.6 geldiğinde override edilebilir) | yok (S2 ARD elle gelmişti) |
| P2 | yok | yok |
| P3 | sentetik `raw_prob_synth.tif` ile füzyon test edildi | gerçek `data/inference/raw_prob.tif` (T3.10) — opsiyonel, mevcut sentetik proxy P5 demosu için yeterli |
| P5 | 12 layer manifest + final_confidence.tif HAZIR | T5.13 entegrasyon |

## Sıradaki adımlar

1. ⏳ P3 raw_prob.tif gelince: tek komutla `final_confidence.tif` regenerate
2. 🟢 P5 T5.13 entegrasyon: `reports/layers.json` Folium'a feed
3. 🟢 KOD FREEZE öncesi: dry-run + commit
