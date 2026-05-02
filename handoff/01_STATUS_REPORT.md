# Status Raporu — Pomzadoya Modül A v2

> **Saat 0/24 itibariyle.** Bu doküman 3 bölümden oluşur: ✅ Yapılmış olanlar, ⏳ Yapılması gerekenler, 👤 Manuel kısımlar (kim, ne, ne zaman).

---

## ✅ BÖLÜM A — YAPILMIŞ OLANLAR (kod scaffolding %100 tamam)

### A.1 Multi-agent altyapısı

| Dosya | İçerik | Durum |
|---|---|---|
| `.claude/agents/orchestrator.md` | Asenkron iş kuyruğu, dispatch protokolü, v2 critical path | ✅ |
| `.claude/agents/p1-veri-muhendisi.md` | P1 rol tanımı + RUN-BLOCK protokolü | ✅ |
| `.claude/agents/p2-etiketleme-lead.md` | P2 rol tanımı | ✅ |
| `.claude/agents/p3-ml-muhendisi.md` | P3 rol tanımı (RAW olasılık vurgusu) | ✅ |
| `.claude/agents/p4-spektral-muhendis.md` | P4 rol tanımı (T4.12 kritik) | ✅ |
| `.claude/agents/p5-change-detection-viz.md` | P5 rol tanımı (RAW vs FUSED ayrımı) | ✅ |
| `.claude/state/orchestrator_log.md` | Durum tablosu, 10 görevlik kritik patika checkbox | ✅ |
| `.claude/agents/README.md` | 2-terminal kurulum kılavuzu | ✅ |

### A.2 Klasör yapısı

```
Pomzadoya/
├── code/{p1,p2,p3,p4,p5}/   ✅ oluşturuldu
├── data/{ard,tiles,labels,layers,landsat,s1_stack,change,temporal}/   ✅
├── models/   ✅
├── reports/   ✅
├── demo/fallback/   ✅
├── agent_outputs/   ✅
└── handoff/   ✅ (bu dosya burada)
```

### A.3 P1 — Veri Mühendisi kodları (6 dosya)

| Dosya | Görev | Çalıştırılabilir mi? |
|---|---|---|
| `code/p1/01_gee_setup.ipynb` | T1.1 GEE auth Colab notebook | ✅ |
| `code/p1/02_aoi_avanos.py` | T1.2 Avanos AOI üretici (EPSG:32636) | ✅ |
| `code/p1/03_sentinel2_l2a_fetch.py` | T1.3 S2 L2A çekim + bulut maskeleme | ✅ |
| `code/p1/04_s2_coregistration.py` | T1.4 S2 ARD co-registration | ✅ |
| `code/p1/run_pipeline.sh` | Entegrasyon pipeline shell | ✅ (T1.2-T1.4 hazır, T1.5-T1.10 iskelet) |
| `code/p1/requirements.txt` | Python deps | ✅ |

> **Eksik:** T1.5 (S1 GRD), T1.6 (DEM), T1.7 (Full co-reg 17 kanal), T1.8 (tile splitting), T1.9 (manifest), T1.10 (Landsat) kodları **henüz yazılmadı** — saat 0 sonrası P1 LLM'ine yazdırılacak. Bkz. ⏳ Bölüm B.

### A.4 P2 — Etiketleme Lead kodları (10 dosya)

| Dosya | Görev | Durum |
|---|---|---|
| `code/p2/01_qgis_setup.md` | T2.1 QGIS kurulum talimatları (markdown) | ✅ |
| `code/p2/02_mapeg_query_template.md` | T2.2 MAPEG ÇED + Nevşehir 2014 sorgu | ✅ |
| `code/p2/03_polygon_template.gpkg.md` | T2.3 attribute schema | ✅ |
| `code/p2/04_pixel_sampling.py` | T2.4 pozitif piksel sampling | ✅ |
| `code/p2/05_negative_sampling.py` | T2.5 negatif piksel sampling (2km buffer) | ✅ |
| `code/p2/06_wdpa_ignore_mask.py` | T2.6 WDPA + ignore mask | ✅ |
| `code/p2/07_spatial_block_cv.py` | T2.7 Roberts 2017 5-fold blok CV | ✅ (3-fold Plan B dahil) |
| `code/p2/08_rasterize_mask.py` | T2.8 raster mask (CRITICAL) | ✅ |
| `code/p2/09_augmentation.py` | T2.9 augmentation pipeline | ✅ |
| `code/p2/requirements.txt` | Python deps | ✅ |

### A.5 P3 — ML Mühendisi kodları (13 dosya)

| Dosya | Görev | Durum |
|---|---|---|
| `code/p3/01_env_setup.ipynb` | T3.1 GPU testi | ✅ |
| `code/p3/02_ssl4eo_pretrained.py` | T3.2 SSL4EO-S12 + 13→17 adapter | ✅ |
| `code/p3/03_datamodule.py` | T3.3 DataModule | ✅ |
| `code/p3/04_loss_metrics.py` | BCE+Dice + IoU/F1 metrics | ✅ |
| `code/p3/05_synthetic_sanity.py` | T3.3 sentetik sanity | ✅ |
| `code/p3/06_train.py` | T3.5 fine-tune (5-fold blok CV) **CRITICAL** | ✅ |
| `code/p3/07_inference.py` | T3.10 `predict_raw()` API **CRITICAL** | ✅ |
| `code/p3/08_gradcam.py` | T3.11 Grad-CAM | ✅ |
| `code/p3/09_ablation.py` | T3.7 ablation runner | ✅ |
| `code/p3/10_threshold_tuning.py` | T3.6 F1-max tuning | ✅ |
| `code/p3/11_export_fp16.py` | T3.13 FP16 export | ✅ |
| `code/p3/12_fallback_threshold.py` | Plan B threshold-based | ✅ |
| `code/p3/requirements.txt` | torch, smp, timm, gradcam | ✅ |

### A.6 P4 — Spektral Mühendis kodları (11 dosya)

| Dosya | Görev | Durum |
|---|---|---|
| `code/p4/01_earthdata_setup.md` | T4.1 .netrc kurulumu | ✅ |
| `code/p4/02_aster_l1b_download.py` | T4.2 ASTER indir (CMR API) | ✅ |
| `code/p4/03_aster_l1b_to_l2.py` | T4.3 atmosferik düzeltme + L1T fallback | ✅ |
| `code/p4/04_s2_indices.py` | T4.4 NDVI/BSI/Albedo/Sabins | ✅ |
| `code/p4/05_ninomiya_qi.py` | T4.5 QI/SiO₂/CI | ✅ |
| `code/p4/06_resample_to_s2_grid.py` | T4.6 90m→20m bilinear | ✅ |
| `code/p4/07_fusion_prototype.py` | T4.7 sentetik füzyon prototipi | ✅ |
| `code/p4/08_dem_aspect_hillshade.py` | T4.8 DEM aspect/hillshade | ✅ |
| `code/p4/09_layer_export.py` | T4.10 layer export + manifest | ✅ |
| `code/p4/fuse_confidence.py` | **T4.12 score-level füzyon (CRITICAL)** | ✅ |
| `code/p4/requirements.txt` | rasterio, gdal, numpy, requests | ✅ |

### A.7 P5 — Change Detection + Viz kodları (13 dosya)

| Dosya | Görev | Durum |
|---|---|---|
| `code/p5/01_env_setup.md` | T5.1 ortam kurulum | ✅ |
| `code/p5/02_wdpa_goreme.py` | T5.2 WDPA + 1000m + OSM | ✅ |
| `code/p5/03_red_flag_logic.py` | T5.3 UNESCO ihlal logic | ✅ |
| `code/p5/04_s1_amplitude_diff.py` | T5.5 Mazza 2023 S1 change | ✅ |
| `code/p5/05_folium_basemap.py` | T5.6 Folium baselayer | ✅ |
| `code/p5/06_landsat_roy_harmonization.py` | T5.8 Roy 2016 cross-sensor | ✅ |
| `code/p5/07_landsat_timelapse_gif.py` | Landsat GIF | ✅ |
| `code/p5/08_historical_pomza_inference.py` | T5.10 RAW historical (CRITICAL) | ✅ |
| `code/p5/09_layer_manifest.py` | T5.9/T5.13 5 katman manifest | ✅ |
| `code/p5/10_kpi_calc.py` | T5.11 KPI hesabı | ✅ |
| `code/p5/dashboard.py` | **T5.12 Streamlit (3 ekran)** | ✅ |
| `code/p5/12_demo_fallback.py` | T5.14 PNG fallback | ✅ |
| `code/p5/requirements.txt` | streamlit, folium, rasterio | ✅ |

### A.8 RUN-BLOCK + status dosyaları (17 dosya)

`agent_outputs/` altında her P_n için status raporu + ilk RUN-BLOCK'lar:

| Dosya | Durum |
|---|---|
| `p1_status.md`, `p1_t1_1_runblock.md`, `p1_t1_2_runblock.md`, `p1_t1_3_runblock.md` | ✅ |
| `p2_status.md`, `p2_t2_1_runblock.md`, `p2_t2_2_runblock.md`, `p2_t2_3_runblock.md` | ✅ |
| `p3_status.md`, `p3_t3_1_runblock.md`, `p3_t3_2_runblock.md`, `p3_t3_3_runblock.md` | ✅ |
| `p4_status.md`, `p4_t4_1_runblock.md`, `p4_t4_2_runblock.md`, `p4_t4_3_runblock.md`, `p4_t4_12_runblock.md` | ✅ |
| `p5_status.md`, `p5_t5_1_runblock.md`, `p5_t5_2_runblock.md`, `p5_t5_5_runblock.md`, `p5_t5_8_runblock.md`, `p5_t5_10_runblock.md`, `p5_t5_13_runblock.md` | ✅ |

### A.9 Mimari kararlar koda gömüldü

| Karar | Yer | Durum |
|---|---|---|
| Karar #4: ASTER QI oran-tabanlı, L1T fallback OK | `code/p4/03_aster_l1b_to_l2.py` (`--no-dos` flag) | ✅ |
| Karar #6: P3 RAW olasılık, füzyon P4'te | `code/p3/07_inference.py` (`predict_raw`) | ✅ |
| Karar #15: 20m S2 SWIR native grid | `code/p1/04_s2_coregistration.py` (`-tr 20 20`) | ✅ |
| Roberts 2017 spatial 5-fold blok CV | `code/p2/07_spatial_block_cv.py` | ✅ |
| Roy 2016 cross-sensor harmonization | `code/p5/06_landsat_roy_harmonization.py` | ✅ |
| Mazza 2023 S1 amplitude difference | `code/p5/04_s1_amplitude_diff.py` | ✅ |
| Ninomiya QI = B11²/(B10×B12) | `code/p4/05_ninomiya_qi.py` | ✅ |
| Liang 2001 albedo formülü | `code/p4/04_s2_indices.py` | ✅ |
| SSL4EO-S12 13→17 multi-channel adapter | `code/p3/02_ssl4eo_pretrained.py` | ✅ |

---

## ⏳ BÖLÜM B — YAPILMASI GEREKENLER (runtime + ek kod)

### B.1 Eksik kod batch'leri (LLM yazacak — manuel değil)

Bu kodlar henüz yazılmadı, P_n LLM'ine yazdırılacak (saat 0-1 arası):

#### P1 — Eksik kodlar (T1.5–T1.10)
| Görev | Kod | Saat |
|---|---|---|
| T1.5 | S1 GRD çekim + Lee filter | 4 |
| T1.6 | Copernicus DEM çekim + slope | 5.5 |
| T1.7 | Full co-registration (17 kanal merge) | 6.5 |
| T1.8 | Tile splitting (256×256 + 32 px overlap) | 8 |
| T1.9 | ARD export + manifest.json | 10 |
| T1.10 | Landsat Tier 2 snapshot | 11 |

**Aksiyon:** P1 LLM'ine "T1.5–T1.10 kodlarını `code/p1/05_*.py` ... `10_*.py` adlarıyla yazdır" prompt'u verir.

### B.2 Runtime görevleri (kim, ne, ne zaman, ne tür)

> ⚙️ = otomatik (kod çalıştır), 👤 = manuel insan, 🧠 = LLM kararı

#### P1
| Saat | Görev | Tür | Süre |
|---|---|---|---|
| 0-1 | T1.1 GEE auth Colab | 👤 (Run + paste JSON) | 10dk |
| 1-1.5 | T1.2 AOI üretim | ⚙️ | 5dk |
| 1.5-3 | T1.3 S2 L2A çekim | 👤 GEE Run + ⚙️ bekleme | 30dk |
| 3-4 | T1.4 S2 co-reg | ⚙️ | 1h |
| 4-5.5 | T1.5 S1 çekim | 👤 GEE Run + ⚙️ | 1.5h |
| 5.5-6.5 | T1.6 DEM | ⚙️ | 1h |
| 6.5-8 | T1.7 Full co-reg | ⚙️ | 1.5h |
| 8-10 | T1.8 Tile splitting | ⚙️ | 2h |
| 10-11 | T1.9 ARD export + manifest | ⚙️ | 1h |
| 11-13 | T1.10 Landsat snapshot | 👤 GEE Run | 2h |
| 13-14 | T1.11 QC raporu | ⚙️ | 1h |
| 14-16 | HELP→P2 | 🧠 + 👤 | 2h |
| 16-18 | HELP→P5 | 🧠 + 👤 | 2h |
| 18-20 | Entegrasyon | 👥 | 2h |
| 20-24 | KOD FREEZE + dry-run | 👥 | 4h |

#### P2
| Saat | Görev | Tür | Süre |
|---|---|---|---|
| 0-1 | T2.1 QGIS kurulum | 👤 | 1h |
| 1-3 | T2.2 MAPEG sorgu | 👤 web search + okuma | 2h |
| **3-7** | **T2.3 Manuel poligon (4 saat — EN BÜYÜK MANUEL İŞ)** | **👤** | **4h** |
| 7-8 | T2.4 Pozitif piksel sampling | ⚙️ | 1h |
| 8-9 | T2.5 Negatif sampling | ⚙️ | 1h |
| 9-10 | T2.6 WDPA ignore mask | ⚙️ | 1h |
| 10-11 | T2.7 Spatial 5-fold blok CV | ⚙️ | 1h |
| 11-13 | **T2.8 Raster mask (CRITICAL)** | ⚙️ | 2h |
| 13-14 | T2.9 Augmentation | ⚙️ | 1h |
| 14-16 | T2.10 P3 DataLoader testi | ⚙️ + 👥 (P3) | 2h |
| 16-17 | T2.11 Etiket QC | ⚙️ | 1h |
| 17-18.5 | T2.12 Hata analizi | 👤 görsel inceleme | 1.5h |
| 18.5-20 | HELP→P5 KPI | 👥 | 1.5h |
| 18-20 | Entegrasyon | 👥 | 2h |
| 20-24 | KOD FREEZE | 👥 | 4h |

#### P3
| Saat | Görev | Tür | Süre |
|---|---|---|---|
| 0-2 | T3.1 GPU testi (Colab Pro/Kaggle) | 👤 + ⚙️ | 2h |
| 2-4 | T3.2 SSL4EO-S12 yükleme + adapter | ⚙️ | 2h |
| 4-6 | T3.3 DataModule + sentetik sanity | ⚙️ | 2h |
| **6-12** | **T3.4 SLACK — inference iskelet + Grad-CAM** | **🧠** | **6h** |
| **12-15** | **T3.5 Fine-tune (CRITICAL)** | **👤 Run + ⚙️ asenkron** | **3h** |
| 15-16 | T3.6 Threshold tuning | ⚙️ | 1h |
| 15-16.5 | T3.7 Ablation (paralel) | ⚙️ | 1.5h |
| **16.5-17.5** | **T3.10 RAW inference fn (CRITICAL)** | **⚙️** | **1h** |
| 17.5-18.5 | T3.11 Grad-CAM | ⚙️ | 1h |
| 18.5-20 | T3.12 Hata analizi | 👥 | 1.5h |
| 18-20 | T3.13 Model export | ⚙️ | 2h |
| 20-24 | T3.14 KOD FREEZE + FP16 | ⚙️ | 4h |

#### P4
| Saat | Görev | Tür | Süre |
|---|---|---|---|
| 0-1 | T4.1 Earthdata token | 👤 | 1h |
| 1-3 | T4.2 ASTER indir | 👤 curl + ⚙️ | 2h |
| 3-5 | T4.3 Atmosferik düzeltme | ⚙️ | 2h |
| 5-7 | T4.4 S2 indeksleri | ⚙️ | 2h |
| 7-9 | T4.5 Ninomiya QI/SiO₂/CI | ⚙️ | 2h |
| 9-10 | T4.6 90m→20m resample | ⚙️ | 1h |
| 10-12 | T4.7 Füzyon prototipi | ⚙️ | 2h |
| 12-13 | T4.8 DEM aspect/hillshade | ⚙️ | 1h |
| 13-15 | HELP→P5 Folium QI layer | 👥 | 2h |
| 15-17 | T4.10 Layer export | ⚙️ | 2h |
| 17-18 | HELP→P3 API alignment | 👥 | 1h |
| **18-20** | **T4.12 Score-level füzyon canlı (CRITICAL)** | **⚙️** | **2h** |
| 20-24 | T4.13 KOD FREEZE | ⚙️ | 4h |

#### P5
| Saat | Görev | Tür | Süre |
|---|---|---|---|
| 0-1 | T5.1 Ortam kurulum | 👤 + ⚙️ | 1h |
| 1-2 | T5.2 WDPA + OSM | ⚙️ | 1h |
| 2-3 | T5.3 Red flag prototipi | ⚙️ | 1h |
| 3-5.5 | SLACK — Folium iskelet (T5.6 öne) | ⚙️ | 2.5h |
| 5.5-7.5 | T5.5 S1 amplitude diff | ⚙️ | 2h |
| 7.5-9.5 | T5.6 Folium altyapı | ⚙️ | 2h |
| 9.5-13 | SLACK — model export + etiket görsel | 🧠 + ⚙️ | 3.5h |
| 13-16 | T5.8 Roy 2016 + GIF | ⚙️ | 3h |
| 16-17.5 | T5.9 Layer ekleme | ⚙️ | 1.5h |
| **17.5-19** | **T5.10 Historical RAW (CRITICAL)** | **⚙️** | **1.5h** |
| 19-20 | T5.11 KPI | ⚙️ | 1h |
| 18-20 | T5.12 Streamlit | ⚙️ | 2h |
| **18-20** | **T5.13 Final entegrasyon (CRITICAL)** | **👥** | **2h** |
| 20-22 | T5.14 PNG fallback | ⚙️ | 2h |
| **22-24** | **T5.15 Dry-run #1 #2 (CRITICAL)** | **👥** | **2h** |

---

## 👤 BÖLÜM C — MANUEL KISIMLAR (sadece insan yapabilir)

> Bu işler kesinlikle insan eylem gerektirir. LLM yapamaz, otomatize edilemez. Toplam 5 kişi paralel çalışırsa **fiziksel iş yükü dengeli** dağılır.

### C.1 Manuel iş listesi (kim, ne, ne zaman, ne kadar)

#### Hesap kurulumları (saat 0, paralel — toplam ~30 dk)
| Kişi | İş | Süre | Detay |
|---|---|---|---|
| **P1** | GCP + Earth Engine API + service account JSON | 30dk | console.cloud.google.com → yeni proje → API enable → IAM service account → JSON key indir |
| **P2** | QGIS kurulum + WDPA shapefile indir | 20dk | qgis.org/download → WDPA Goreme shapefile (protectedplanet.net) |
| **P3** | Colab Pro abonelik VEYA Kaggle hesap | 15dk | Colab Pro: $9.99/ay; Kaggle: ücretsiz GPU haftalık 30h |
| **P4** | NASA Earthdata hesap + .netrc | 10dk | urs.earthdata.nasa.gov → kayıt → uygulama yetkilendirme: LP DAAC OPeNDAP, ASTER L1T |
| **P5** | Yerel Python 3.10+ env + Streamlit pip install | 15dk | Conda veya venv, requirements.txt'e göre |

#### Web search / belge okuma — P2 manuel araştırma (saat 1-3, 2 saat)
- **MAPEG ÇED** (mapeg.gov.tr) sorgu: "Avanos pomza" arama, ÇED raporu PDF indir, üretici listesi çıkar
- **Nevşehir İl Çevre Durum Raporu 2014** (csb.gov.tr veya Nevşehir Valilik) PDF indir, pomza sahaları bölümü çıkar
- ~30-40 saha listesi tablosu üret: saha_id, üretici, koordinat, MAPEG no, durum
- LLM bu işi yapamaz — kullanıcı PDF'leri açar, ilgili sayfaları okur, tabloya çıkarır

#### **EN BÜYÜK MANUEL İŞ — P2 QGIS poligon çizimi (saat 3-7, 4 saat)**
- QGIS aç → S2 RGB altlık yükle (P1 saat 4'te teslim edecek) → MAPEG ÇED sahalarına göre 30-40 pozitif poligon elle çiz → her birine attribute gir
- **Bu görev otomatize EDİLEMEZ.** Tek çıkış yolu: 4 saat klavye+mouse iş.
- Hızlandırıcı: Saat 14-16 P1 yardıma gelir (HELP→P2), 5-10 ek negatif poligon birlikte tamamlanır.
- Plan B: 30-40 yerine 25-30 pozitifle yetin, daha az saha = daha az yorgunluk.

#### `Run` butonu basma (asenkron — fiziksel iş 1-2 dk, bekleme uzun)
| Kişi | İş | Saat | Bekleme |
|---|---|---|---|
| P1 | GEE Code Editor: S2 export Run | 1.5 | ~30dk |
| P1 | GEE: S1 GRD export Run | 4 | ~20dk |
| P1 | GEE: DEM export Run | 5.5 | ~10dk |
| P1 | GEE: Landsat Tier 2 export Run | 11 | ~30dk |
| P3 | Colab Pro: GPU notebook Run | 0 | sürekli |
| P3 | Colab Pro: Fine-tune notebook Run (T3.5) | 12 | ~3h (A100) / 6h (T4) |
| P4 | Terminal: ASTER curl indir | 1 | ~30dk |
| P5 | Terminal: streamlit run dashboard.py | 18-22 | sürekli |

#### Çıktı yapıştırma (her DELIVER sonrası)
- **5 kişinin de** kendi LLM'ine VERIFY-BLOCK çıktısını yapıştırması gerekir
- Her görev sonrası ~30 saniye iş, 24 saatte ortalama **30-40 yapıştırma** kişi başı

#### Entegrasyon oturumu (saat 18-20, hep birlikte)
- Discord call açılır, hep birlikte oturulur
- Her kişi kendi çıktısının harita/dashboard'a entegrasyonunu doğrular
- Bug'lar grup chat'te listelenir

#### Demo dry-run + sunum (saat 22-24, hep birlikte)
- 2 dry-run koş, problem var mı kontrol
- İnternet kesintisi senaryosu test (offline mode)
- Final sunumda sırayla kim ne anlatacak — bunu önceden konuş

### C.2 Manuel iş yükü dağılımı (saatlik tahmin)

| Kişi | Hesap kurulum | Web research | Manuel poligon | Run + bekleme | Çıktı paste | Entegrasyon | Demo | **Toplam aktif** |
|---|---|---|---|---|---|---|---|---|
| P1 | 30dk | — | — | 4× Run (~5dk) | ~30 paste | 2h | 2h | **~5h aktif / 24h** |
| **P2** | 20dk | **2h** | **4h** | — | ~30 paste | 2h | 2h | **~10h aktif / 24h** ⚠️ EN YOĞUN |
| P3 | 15dk | — | — | 2× Run (~5dk, 6h bekleme arka plan) | ~30 paste | 2h | 2h | **~5h aktif / 24h** |
| P4 | 10dk | — | — | curl + bekleme | ~30 paste | 2h | 2h | **~5h aktif / 24h** |
| P5 | 15dk | — | — | streamlit run | ~30 paste | **3h** (final entegre kendi sorumluluğu) | 2h | **~6h aktif / 24h** |

> P2 en yoğun. P1, P3, P4 ortalama. P5 entegrasyon nedeniyle hafif fazla.
> **Eşitleme önerisi:** P1 saat 14-16 boş kaldığında P2'ye yardıma gider (HELP→P2 zaten planlı). P3 6h slack'inde inference iskelet + Grad-CAM yazar.

### C.3 Manuel iş için **yüksek kaliteli girdi gereksinimleri**

Her manuel görevin LLM'e geri yapıştırılan VERIFY çıktısı şu kalitede olmalı:

| Görev | Yapıştırılacak şey | Kalite kriteri |
|---|---|---|
| GEE auth | Console hata yok + sanity sahne ID + `getInfo()==42` | 3 satır, copy-paste |
| GEE export | Job ID + status link | 1 satır + URL |
| QGIS poligon | `ogrinfo positive_polygons.gpkg -al -so` çıktısı + screenshot | Feature count + attribute table |
| Colab fine-tune | Son 5 epoch loss/IoU + 5 fold mean ± std + checkpoint boyut | 15-20 satır |
| ASTER indir | `ls -lh data/aster/*.hdf` çıktısı + dosya boyut | 1 satır |
| Streamlit | Ana ekran screenshot + konsol hata var mı (son 20 satır) | 1 PNG + log |
| Layer manifest | `cat data/layers.json` içeriği | JSON (10-20 satır) |
| KPI | `cat reports/kpi.json` içeriği | JSON (5-10 satır) |

---

## 📊 ÖZET DAŞBOARD

| Metrik | Değer |
|---|---|
| Toplam üretilmiş kod dosyası | **70+** |
| Toplam yapılması gereken runtime saati | ~21h critical path |
| Slack zamanı | ~3h |
| **EN BÜYÜK MANUEL İŞ** | **P2 4 saat poligon çizimi** |
| Toplam aktif insan saati (5 kişi × ~5-10h) | ~30-35 saat |
| Critical path görevleri | 10 |
| Plan B fallback'leri | 7 (kodlanmış) |
| Hesap kurulum + bağımlılık | 5 (her kişi kendi) |

---

## 🚦 BAŞLAMA SİNYALİ

Tüm 5 kişi şunu yaptığında "saat 0" başlar:
1. ✅ Bu dokümanı okudu
2. ✅ Kendi P_n_BRIEFING.md'ı okudu
3. ✅ `00_MASTER_COORDINATION.md` okudu
4. ✅ Hesap kurulumunu yaptı (kendi briefing'inde liste)
5. ✅ Kendi LLM'ini ayağa kaldırdı (ilk prompt'u yapıştırdı)
6. ✅ Grup chat'e "P_n hazır" mesajı attı

5/5 hazır olduğunda biri saat 0 başlat sinyali verir, herkes T_n.1'e geçer.

---

*Bu doküman saat 0'da freeze edilir. Sonraki güncellemeler `.claude/state/orchestrator_log.md`'de.*
