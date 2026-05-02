# P5 — Status (Modül A v2)

Tarih: 2026-05-01
Sahip: P5 (Change Detection + UNESCO + Visualization)

## Tamamlanan üretimler (1. iterasyon)
| Görev | Dosya | Durum |
|---|---|---|
| T5.1  | `code/p5/01_env_setup.md` + `requirements.txt`           | ✅ Yazıldı |
| T5.2  | `code/p5/02_wdpa_goreme.py`                              | ✅ Yazıldı |
| T5.3  | `code/p5/03_red_flag_logic.py`                           | ✅ Yazıldı |
| T5.5  | `code/p5/04_s1_amplitude_diff.py` (Mazza 2023)           | ✅ Yazıldı |
| T5.6  | `code/p5/05_folium_basemap.py`                           | ✅ Yazıldı |
| T5.8  | `code/p5/06_landsat_roy_harmonization.py` (Roy 2016)     | ✅ Yazıldı |
| T5.7  | `code/p5/07_landsat_timelapse_gif.py`                    | ✅ Yazıldı |
| T5.10 | `code/p5/08_historical_pomza_inference.py` (RAW)         | ✅ Yazıldı |
| T5.9  | `code/p5/09_layer_manifest.py` (5 katman, Plan A/B auto) | ✅ Yazıldı |
| T5.11 | `code/p5/10_kpi_calc.py`                                 | ✅ Yazıldı |
| T5.12 | `code/p5/dashboard.py` (Streamlit, 3 sayfa)              | ✅ Yazıldı |
| T5.14 | `code/p5/12_demo_fallback.py` (PNG fallback)             | ✅ Yazıldı |

## Run-block dosyaları
- `agent_outputs/p5_t5_1_runblock.md`
- `agent_outputs/p5_t5_2_runblock.md`
- `agent_outputs/p5_t5_5_runblock.md`
- `agent_outputs/p5_t5_8_runblock.md` (Roy 2016 + P1 Landsat bağımlılık)
- `agent_outputs/p5_t5_10_runblock.md` (P3 inference + P1 Landsat bağımlılık)
- `agent_outputs/p5_t5_13_runblock.md` (CRITICAL — P4 final_confidence.tif bağımlılık)

## Bekleyen / dışsal bağımlılıklar
- **P1**: `data/ard/s2_rgb.tif` (T1.4), `data/s1_stack/S1_*VV*.tif` (T1.5), `data/landsat/L*_<year>.tif` (T1.10), WDPA shapefile.
- **P3**: `code/p3/inference.py` `predict_raw` fonksiyonu (T3.10) — T5.10 import eder, mock fallback mevcut.
- **P4**: `data/ard/aster_qi.tif` (T4.6), `data/ard/final_confidence.tif` (T4.12) — T5.13 ana katman.

## v2 ayrımı (kritik)
- **T5.10 historical** = Landsat → P3 **RAW** + sabit threshold 0.5. ASTER yok, füzyon yok.
- **T5.13 current**    = S2+ASTER → P4 **FUSED** `final_confidence.tif`. Ana dashboard katmanı.
- `09_layer_manifest.py` `final_confidence.tif` yoksa Plan B'ye otomatik düşer (P3 RAW + ayrı ASTER QI).

## Plan B'ler
- **Roy 2016 yavaş** → `fallback_mean_match()` (`06_landsat_roy_harmonization.py`).
- **P4 T4.12 fail** → Plan B manifest, P3 RAW ana katman.
- **Streamlit fail saat 20** → `12_demo_fallback.py` PNG fallback (offline HTML).
- **WDPA Overpass erişim hatası** → `02_wdpa_goreme.py` cross-check'i atlar, manuel doğrulama notu.
- **S1 stack tek sahne** → log-ratio yerine variance/texture map (manuel patch).

## Sıradaki
1. P1 Landsat snapshot ve S1 stack gelir gelmez `04_s1_amplitude_diff.py` + `06_landsat_roy_harmonization.py` koş.
2. P3 inference fn export edildiğinde `08_historical_pomza_inference.py` mock'tan gerçek `predict_raw`'a geçer.
3. Saat 18:00 entegrasyon oturumu — `09_layer_manifest.py` ile 5 katman manifest üret, dashboard.py ile dry-run.
4. Saat 22 dry-run #1 #2 + ekran-paylaşım testi (T5.15).

## Notlar
- Tüm `geopandas`, `rasterio` import'ları soft-fail edebilir; her script kendi başına çalışır.
- AOI merkezi: Avanos (38.7167, 34.85), EPSG:32636.
- UNESCO buffer mesafesi: 1000 m (K#8 sabit).
- S1 log-ratio threshold: ±3 dB (Mazza 2023).
- Roy 2016 katsayıları SR ölçeğine göre uygulanır; girdi 0-10000 ise scale otomatik.
