# Modül A — 5 Kişilik Development Rol Dağıtımı

> **Kapsam:** Sadece Modül A (uydu+AI ile pomza alanı tespiti, change detection, UNESCO buffer overlay) teknik development işleridir. Modül B, müşteri profili, ticarileşme, jüri stratejisi bu dosyanın kapsamı dışındadır.
>
> **Önkabul:** 5 kişi paralel çalışır, her birinin atomic scope'u vardır. Kişiler birbirleriyle sadece **interface contract** (girdi/çıktı dosya formatı) üzerinden konuşur. Final entegrasyon Saat 18-20 arası tek bir oturumda yapılır.

---

## 0. MODÜL A TEKNİK AKIŞ (ATOMİK)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MODÜL A — 5 KİŞİLİK PARALEL AKIŞ                   │
│                                                                       │
│  P1: Veri Mühendisi              ──→ clean_stack.tif (17 kanal ARD)  │
│  P2: Etiketleme Lead             ──→ labels.geojson + mask raster    │
│  P3: ML Mühendisi                ──→ model.pt + inference_fn         │
│  P4: Spektral Mühendis           ──→ derived_indices/ (NDVI, BSI,    │
│                                       Albedo, Sabins, Ninomiya QI)   │
│  P5: Change Detection + Overlay  ──→ change_layers/ + UNESCO overlay │
│                                                                       │
│       ▼  SAAT 18-20: ENTEGRASYON OTURUMU  ▼                          │
│       Score-level füzyon: U-Net × ASTER QI × spektral eşleme         │
│       → final_pumice_confidence.tif + layers manifest                │
└─────────────────────────────────────────────────────────────────────┘
```

**Bağımlılık zinciri (kim kime ne zaman ne verir):**

```
SAAT 0   → P1, P2, P3, P4, P5 paralel başlar
SAAT 4   → P1 → P4 (S2 ARD hazır, türetilmiş indeksler başlar)
SAAT 6-7 → P1 + P2 → P3 (ARD + etiket → fine-tune başlar)
SAAT 8-10 → P3 → P5 (inference_fn → Landsat snapshot pomza tespiti)
SAAT 12-14 → P4 → P5 (ASTER QI → score-level füzyon overlay)
SAAT 14-16 → P3 + P4 ↔ entegrasyon (U-Net olasılık × ASTER QI ağırlık)
SAAT 18-20 → 5 kişi entegrasyon
SAAT 20-22 → KOD FREEZE
SAAT 22-24 → Demo dry-run
```

---

## 1. P1 — VERİ MÜHENDİSİ (Data Pipeline & Pre-processing)

### Atomic Sorumluluk
Tüm uydu verilerini Avanos AOI için çek, atmosferik düzeltmeleri uygula, bulut maskele, aynı grid'e re-projeksiyonla, tek bir multi-band tensör (Analysis-Ready Data, ARD) olarak kayıt et. Modülün **veri arka kapısı**dır.

### Spesifik Görev Listesi
- AOI tanımı: Avanos+Acıgöl+Gülşehir kuşağı, ~30×30 km bbox, merkez (38.7°N, 34.85°E), GeoJSON polygon
- Sentinel-2 L2A çekimi: GEE `COPERNICUS/S2_SR_HARMONIZED`, son 6 ay, bulut <%20, median composite
- Sentinel-1 GRD çekimi: GEE `COPERNICUS/S1_GRD`, IW mode, VV+VH, son 1 yıl, ascending+descending ortalaması, dB ölçeğine çevirim, Lee filter (multi-look noise reduction)
- Copernicus DEM GLO-30: GEE `COPERNICUS/DEM/GLO30`, AOI clip, slope (eğim) türevi
- Bulut maskeleme: S2 SCL bandı (sınıflar 3, 8, 9, 10, 11 = mask)
- Co-registration: tüm bantlar S2 10 m grid'ine resample (bilinear), ortak CRS EPSG:32636 (UTM Zone 36N)
- NoData / outlier handling: S1 dB clip [-30, +5]
- Tile splitting: 256×256 piksel patch, 32 piksel overlap
- ARD output: 17 kanal multi-band GeoTIFF (S2 13-bant + S1 VV/VH + DEM elevation/slope)
- Tier 2 pre-cache (P5 için): Landsat 1985/2000/2015/2025 Avanos snapshot indirme
- Demo offline cache: internet kesilirse Streamlit'in patlamaması için yerel cache

### Saatlik Plan
| Saat | İş |
|:-:|---|
| 0-1 | GEE auth, ortam (`earthengine-api`, `geemap`, `rasterio`); Avanos AOI GeoJSON |
| 1-3 | S2 L2A median composite, SCL bulut maskesi, RGB+SWIR doğrulama görseli |
| 3-5 | S1 GRD çekimi, dB dönüşüm, Lee filter |
| 5-6 | Copernicus DEM çekimi, slope türevi |
| 6-8 | Co-registration: tüm bantlar S2 10 m grid'ine resample; QC overlay testi |
| 8-10 | Tile splitting (256×256, overlap 32) |
| 10-12 | ARD GeoTIFF export, manifest JSON yazımı |
| 12-14 | Tier 2 pre-cache: Landsat 1985/2000/2015/2025 snapshot çekimi |
| 14-16 | Bug fix, P3-P4'ten gelen veri talebine göre re-export |
| 16-18 | QC raporu: bulut yüzdesi, NoData yüzdesi, kanal histogram |
| 18-20 | **Entegrasyon:** pipeline tek tıkla koşuyor mu doğrula |
| 20-22 | Demo offline cache hazırlığı |
| 22-24 | Demo dry-run desteği |

### Out of Scope
- ML model eğitimi (P3'ün işi)
- Türetilmiş indeks hesaplama: NDVI, BSI, Sabins, Ninomiya QI (P4'ün işi)
- Manuel etiket çizimi (P2'nin işi)
- Change detection (P5'in işi)
- ASTER L1B atmosferik düzeltme (P4'ün işi — sadece ham çekme isterse P1 destek olur, ama atmospheric correction P4)
- InSAR koherans (Modül A scope dışı)
- Hyperspectral PRISMA canlı işleme (Modül A scope dışı)
- Frontend / Streamlit (P5 + frontend takımı)

### Interface Contract (Çıktı)
```
/data/ard/
  ├── avanos_stack.tif              # 17-kanal ARD raster
  ├── avanos_stack_manifest.json    # bant adları, CRS, geo-bounds
  ├── tiles/
  │   ├── train/*.tif               # 256×256 patch'ler
  │   ├── val/*.tif
  │   └── test/*.tif
  ├── tier2/
  │   ├── landsat_1985.tif
  │   ├── landsat_2000.tif
  │   ├── landsat_2015.tif
  │   └── landsat_2025.tif
  └── qc/
      ├── cloud_pct.json
      └── histograms.png
```

**Manifest JSON şeması:**
```json
{
  "crs": "EPSG:32636",
  "bounds": [x_min, y_min, x_max, y_max],
  "resolution_m": 10,
  "channels": [
    {"index": 0, "name": "S2_B2", "wavelength_nm": 490},
    {"index": 1, "name": "S2_B3", "wavelength_nm": 560},
    "...",
    {"index": 13, "name": "S1_VV", "unit": "dB"},
    {"index": 14, "name": "S1_VH", "unit": "dB"},
    {"index": 15, "name": "DEM_elevation", "unit": "m"},
    {"index": 16, "name": "DEM_slope", "unit": "degrees"}
  ],
  "cloud_coverage_pct": 4.2,
  "acquisition_date_range": ["2025-10-01", "2026-04-30"]
}
```

---

## 2. P2 — ETİKETLEME LEAD (Ground Truth Curator)

### Atomic Sorumluluk
Avanos için pomza pozitif/negatif etiketli yer doğrusu (ground truth) veri setini sıfırdan oluştur. MAPEG ruhsat sorgusu, manuel poligon çizimi, dengeli negatif örnekleme, mekânsal train/val/test split, augmentation pipeline. P3'ün modeli bu kişinin verisi olmadan eğitilemez.

### Spesifik Görev Listesi
- MAPEG ruhsat sorgusu: e-Maden tek-tek sorgu, Avanos için ~10-15 ruhsatlı pomza sahası listesi
- Bilinen pomza üreticisi konumları: BlokBims, Miner Madencilik, Pomza Export, Map-Stones — web sitesi/Google Maps doğrulama
- Manuel pozitif poligon çizimi: QGIS + Sentinel-2 RGB altlık + EO Browser; 30-40 pozitif saha
- Negatif örnekleme: yerleşim/yol/su, açık tüf yüzeyleri (Göreme/Zelve peri bacası), volkanik kayaç düzlüğü pomza olmayan, çıplak kayaç pomza olmayan; 100-150 örnek
- UNESCO buffer alanı **etiket dışı** (mask out, ne pozitif ne negatif)
- Train/val/test split: %70/15/15, **mekânsal split** (aynı saha hem train hem test'te olmasın)
- Raster mask üretimi: poligon → 256×256 binary raster (1=pomza, 0=arkaplan, 255=mask out)
- Augmentation pipeline: albumentations (random flip, rotate 90/180/270°, brightness ±%10, channel-drop p=0.1)
- Quality check: tile başına pozitif piksel oranı, sınıf dengesizliği

### Saatlik Plan
| Saat | İş |
|:-:|---|
| 0-1 | QGIS kurulumu, Sentinel-2 RGB layer (EO Browser canlı görüntü, P1 ARD beklemiyor) |
| 1-3 | MAPEG e-Maden sorgu, BlokBims/Miner saha konumları doğrulama, ön-liste |
| 3-7 | **Manuel pozitif poligon çizimi** (kritik faz) — 30-40 saha |
| 7-9 | Manuel negatif poligon çizimi — 100-150 örnek |
| 9-10 | WDPA Göreme polygon indir, 1000m buffer, etiket dışı maskeleme |
| 10-11 | Mekânsal train/val/test split |
| 11-13 | Raster mask üretme: poligon → 10m raster, P1 tile'larıyla aynı grid |
| 13-14 | Augmentation pipeline (albumentations) |
| 14-16 | P3 ile DataLoader entegrasyon test |
| 16-18 | QC raporu: sınıf dağılımı, pozitif piksel oranı, augmentation görsel kanıt |
| 18-20 | **Entegrasyon** — labels P3 modeline akıyor mu doğrula |
| 20-22 | Hata analizi: yanlış-pozitif/negatif örnek incelemesi (P3 inference sonuçlarıyla) |
| 22-24 | Demo dry-run desteği |

### Out of Scope
- S2/S1/DEM ham veri çekme (P1)
- Model eğitme (P3)
- Türetilmiş indeks hesaplama (P4)
- Change detection (P5)
- Avanos dışı bölge için etiket — sade kapsam: sadece Avanos
- Pomza kalite alt-sınıfları (asidik/bazik vs) — sade kapsam: binary "pomza var/yok"

### Interface Contract (Çıktı)
```
/data/labels/
  ├── positive_polygons.geojson      # 30-40 pozitif pomza saha sınırı
  ├── negative_polygons.geojson      # 100-150 negatif örnek
  ├── unesco_buffer_mask.geojson     # etiket dışı alan
  ├── splits/
  │   ├── train_tiles.txt
  │   ├── val_tiles.txt
  │   └── test_tiles.txt
  ├── masks/
  │   └── tile_<id>_mask.tif         # 256×256 binary raster
  └── stats.json                     # sınıf dağılımı, pozitif piksel oranı
```

---

## 3. P3 — ML MÜHENDİSİ (Model & Inference)

### Atomic Sorumluluk
TorchGeo + SSL4EO-S12 MoCo pretrained Sentinel-2 13-bant ağırlığını yükle, ek SAR ve DEM kanalları için multi-channel input adapter yaz, U-Net (ResNet50 backbone) mimari kur, P2'nin verisiyle fine-tune et, threshold tuning yap, ablation study koştur, inference function üret. Modülün **AI beyni**dır.

### Spesifik Görev Listesi
- Ortam: Colab T4 GPU veya yerel GPU; PyTorch 2.0+, TorchGeo 0.5+, segmentation-models-pytorch 0.3.3+
- Pretrained backbone: `torchgeo.models.ResNet50_Weights.SENTINEL2_ALL_MOCO`
- Multi-channel input adapter: 13 bant → 17 bant (S2 13 + S1 2 + DEM 2); pretrained ağırlıklar S2 13'e kalır, ek 4 bant random init
- U-Net mimari: `segmentation_models_pytorch.Unet(encoder='resnet50', encoder_weights=None, in_channels=17, classes=1)`
- Loss: Dice + BCE hibrit (`loss = 0.5*dice + 0.5*bce`); UNESCO buffer mask piksellerini loss'tan çıkar
- DataLoader: PyTorch Lightning DataModule + albumentations
- Eğitim: AdamW (lr=1e-4, wd=1e-5), 30-50 epoch, cosine LR, early stopping val IoU
- Threshold tuning: F1-optimal threshold grid search [0.3, 0.7]
- Ablation study: 5 konfigürasyon — (a) S2 RGB, (b) +SWIR, (c) +S1, (d) +DEM, (e) +ASTER QI post-process
- Inference function: tek tile için <2 saniye
- Grad-CAM görselleştirme: hangi banda model dikkat ediyor görsel
- Model export: `.pt` checkpoint

### Saatlik Plan
| Saat | İş |
|:-:|---|
| 0-2 | Ortam kurulum, GPU testi, TorchGeo + smp import |
| 2-4 | Pretrained yükleme, multi-channel adapter, U-Net iskelet |
| 4-6 | Loss + DataModule + sentetik veriyle sanity check (overfit one batch) |
| 6-7 | **P1 ARD + P2 etiket alındı** → gerçek veriyle DataLoader test |
| 7-10 | İlk fine-tune koşusu (T4 GPU, 30 epoch, ~2-3 saat) |
| 10-11 | Threshold tuning + validation metrik raporu |
| 11-13 | Ablation study (5 konfigürasyon × ~30 dk) |
| 13-14 | Inference function, end-to-end test |
| 14-15 | Grad-CAM görselleştirme |
| 15-17 | Hata analizi (P2 ile false pos/neg incele); gerekirse fine-tune ikinci tur |
| 17-18 | Model export, inference fn dokümantasyonu |
| 18-20 | **Entegrasyon** — P5 frontend pipeline'ında inference çalışıyor mu |
| 20-22 | Inference süresi optimizasyonu (FP16) |
| 22-24 | Demo dry-run, P5'le ortak prova |

### Out of Scope
- Veri çekme (P1)
- Etiket çizimi (P2)
- Türetilmiş indeks hesaplama (P4)
- Change detection (P5)
- Frontend Streamlit (P5)
- Custom CNN scratch — pretrained kullan
- Hyperspectral fine-tuning — Tier 2 pre-cache görsel
- Foundation model fine-tuning (Prithvi-EO) — sade kapsam SSL4EO-S12

### Interface Contract (Çıktı)
```
/models/
  ├── pumice_unet_v1.pt              # PyTorch checkpoint
  ├── inference.py                    # predict(tile) → raster
  ├── ablation_results.json          # 5 konfig F1/IoU karşılaştırması
  ├── threshold.json                 # optimal threshold (örn. 0.42)
  └── grad_cam_examples/
      └── *.png
```

**Inference function imzası:**
```python
def predict(tile_path: str, threshold: float = 0.42) -> dict:
    """
    Args:
        tile_path: P1'in ARD GeoTIFF dosya yolu
        threshold: binarization eşiği
    Returns:
        {
          "probability_raster_path": "/output/prob.tif",
          "binary_mask_path": "/output/mask.tif",
          "polygon_geojson": "/output/polygons.geojson",
          "confidence_summary": {
              "max_prob": 0.93,
              "mean_prob": 0.21,
              "positive_area_ha": 47.3
          },
          "inference_time_sec": 1.8
        }
    """
```

---

## 4. P4 — SPEKTRAL MÜHENDİS (Türetilmiş İndeksler + ASTER TIR + Multi-Sensor Füzyon)

### Atomic Sorumluluk
Pomzanın 5 fiziksel imzasını sayısal olarak ölçen tüm türetilmiş indeksleri hesapla. ASTER TIR sahnesini Earthdata'dan indir, L1B → L2 atmosferik düzeltme yap, Ninomiya Quartz Index hesapla. Score-level füzyon mantığını yaz: U-Net olasılığı × ASTER QI ağırlığı × spektral imza eşleme. **Modülün domain-spesifik bilgi katmanı**dır.

### Spesifik Görev Listesi
- Sentinel-2 türetilmiş indeksler:
  - NDVI = (B8-B4)/(B8+B4) — yeşil bitki dışlama maskesi
  - BSI = ((B11+B4)-(B8+B2))/((B11+B4)+(B8+B2)) — çıplak kayaç tespiti
  - Albedo (Liang 2001 formülü) — pomza yüksek albedo (>0.3) ana imzası
  - Sabins ratio = B11/B12 — Al-OH proxy
  - Iron Oxide Ratio = B4/B2 — pomza renk varyasyonu (ikincil)
- ASTER L1B Avanos sahnesi indir (NASA Earthdata)
- ASTER L1B → L2 atmosferik düzeltme (NASA AROP, `pyatcor`, veya basit subtract-dark-object yöntemi)
- ASTER Quartz Index: QI = B11² / (B10 × B12) — silika içerik tahmini (Ninomiya 2002)
- ASTER SiO₂ Kimyasal İndeksi: B13/B12 + B12/B14 (Ninomiya et al. 2005)
- ASTER Carbonate Index: (B6+B9)/(B7+B8) — traverten eler (pomza ile karışmasın)
- DEM türevleri: aspect, hillshade (slope P1'in çıktısında zaten var)
- ASTER 90 m → S2 10 m grid'ine resample (bilinear); QC görsel
- Score-level füzyon mantığı: `final_confidence = unet_prob × normalize(QI) × (1 - normalize(CI))`
- Hyperspectral spektral imza eşleme (Tier 2 görsel kanıt): EnMAP varsa USGS Spectral Library "rhyolite glass" SAM eşleme
- Layer-bazlı GeoTIFF export
- Layer dokümantasyonu: her indeksin formülü, anlamı, pomza için tipik aralığı

### Saatlik Plan
| Saat | İş |
|:-:|---|
| 0-1 | Ortam: `rasterio`, `numpy`, `xarray`; ASTER Earthdata token |
| 1-3 | ASTER L1B Avanos indirme (P1 stack'i beklenmiyor, paralel); L1B → L2 düzeltme |
| 3-4 | **P1 S2 ARD geldi** → Sentinel-2 türetilmiş indeksler (NDVI, BSI, Albedo, Sabins, Iron Oxide) |
| 4-6 | ASTER Quartz Index, SiO₂ Kimyasal İndeksi, Carbonate Index |
| 6-7 | ASTER 90 m → S2 10 m grid'ine resample; QC görsel |
| 7-9 | Score-level füzyon prototipi (P3 örnek output ile test) |
| 9-10 | DEM aspect + hillshade |
| 10-12 | EnMAP varsa SAM eşleme; yoksa Tier 2 statik görsel kanıt |
| 12-14 | Layer-bazlı GeoTIFF export |
| 14-16 | Dokümantasyon: her indeksin ne ölçtüğü, pomza için ortalama, false positive senaryosu |
| 16-18 | P3 ile entegrasyon: ASTER QI U-Net post-process'te ağırlık olarak kullanılıyor |
| 18-20 | **Entegrasyon** — final score-level füzyon canlı |
| 20-22 | Pitch slaytı için her indeksin katma değeri |
| 22-24 | Demo dry-run desteği |

### Out of Scope
- S2/S1/DEM ham veri çekme (P1)
- Etiket çizimi (P2)
- U-Net eğitimi (P3)
- Change detection (P5)
- Frontend (P5)
- Hyperspectral PRISMA atmospheric correction — sadece pre-cache görsel
- EnMAP foundation model fine-tuning — sadece SAM eşleme statik
- Custom radiative transfer modeli — açık kaynak araç yeter
- Pomza kalite alt-skoru — sade kapsam binary olasılık
- Pomza fiziksel parametre tahmini (tane boyu, gözeneklilik) — uydudan henüz olgun değil

### Interface Contract (Çıktı)
```
/data/derived/
  ├── ndvi.tif
  ├── bsi.tif
  ├── albedo.tif
  ├── sabins_b11_b12.tif
  ├── iron_oxide_ratio.tif
  ├── aster_qi.tif
  ├── aster_sio2_chemical.tif
  ├── aster_carbonate_index.tif
  ├── dem_aspect.tif
  ├── dem_hillshade.tif
  ├── fusion_logic.py
  └── derived_layers_manifest.json
```

**Füzyon function imzası:**
```python
def fuse_confidence(unet_prob_path: str,
                    aster_qi_path: str,
                    aster_ci_path: str,
                    weights: dict = None) -> str:
    """
    weights: {"unet": 0.7, "qi": 0.2, "ci_penalty": 0.1}
    Returns: final_confidence_path (GeoTIFF, 0-1 float)
    """
```

---

## 5. P5 — CHANGE DETECTION + UNESCO OVERLAY + VISUALIZATION (Geo-Analyst)

### Atomic Sorumluluk
"Önceki ve şimdiki" change detection: Sentinel-1 SAR amplitude difference (son 1-2 yıl) + Landsat tarihi arşiv (1985→2025) + yıllık alan büyüme hızı. WDPA Göreme polygon + buffer ile UNESCO red flag overlay üret. Tüm Modül A çıktılarını (P3 olasılık raster + P4 indeks layer'ları + change detection + UNESCO overlay) Folium/Leafmap üzerinde **frontend için tek manifest** olarak hazırla. Modülün **görselleştirme ve coğrafi etik filtre katmanı**.

### Spesifik Görev Listesi
- Sentinel-1 SAR amplitude difference: P1'in ham S1 dB stack'inden T1 (2024-Q4) ve T2 (2025-Q4) ortalama amplitude farkı; eşiklenmiş binary değişim maskesi
- Landsat tarihi snapshot işleme: P1 Tier 2 cache (1985, 2000, 2015, 2025); RGB composite, Avanos crop, 30m → ortak grid resample
- Yıllık alan değişim hesabı: her snapshot için P3 inference fn ile pomza poligon → alan (hektar) → yıllık büyüme %
- Zaman serisi animasyon GIF: imageio / Pillow ile 4 snapshot tek GIF
- WDPA Göreme polygon: protectedplanet.net WDPA API
- Buffer ekleme: shapely 1000m konservatif buffer
- OSM cross-check: "Goreme National Park" OSM relation Overpass API; WDPA çapraz doğrulama
- Red flag overlay logic: P3 olasılık raster × WDPA buffer mask = "buffer içi pomza" kırmızı uyarı
- Folium / Leafmap layer: her layer GeoTIFF/GeoJSON → folium TileLayer / FeatureGroup; layer toggle UI
- Frontend manifest: `layers.json` — Streamlit'in okuyacağı tek manifest
- KPI hesaplama: saha bazında alan, 5-yıl büyüme %, UNESCO ihlali (var/yok), ortalama pomza güveni
- Streamlit/Folium entegrasyon: P3 inference fn + P4 indeks layer + bu kişinin overlay'leri tek dashboard

### Saatlik Plan
| Saat | İş |
|:-:|---|
| 0-1 | Ortam: `folium`, `leafmap`, `geopandas`, `shapely`, `osmnx`, `imageio` |
| 1-2 | WDPA Göreme polygon indir, 1000m buffer, OSM çapraz doğrulama |
| 2-3 | UNESCO red flag overlay logic prototip (sentetik raster) |
| 3-5 | **P1 S1 stack geldi** → Sentinel-1 amplitude difference change detection |
| 5-8 | **P1 Landsat Tier 2 geldi** → 1985/2000/2015/2025 composite, Avanos crop, GIF |
| 8-10 | **P3 inference fn hazır** → her Landsat snapshot için pomza poligon, yıllık alan değişim |
| 10-12 | Folium harita altyapısı: Avanos centered, layer toggle skeleton, baselayer |
| 12-14 | Layer ekleme: S2 RGB, P3 olasılık ısı haritası, P4 ASTER QI, S1 change, UNESCO buffer kırmızı, Landsat GIF |
| 14-16 | KPI hesaplama: saha bazında alan, büyüme oranı, UNESCO ihlali |
| 16-18 | Streamlit dashboard entegrasyonu: 3 ekran içinde Modül A layer'ları |
| 18-20 | **Entegrasyon** — 4 kişinin çıktısını tek manifest'te toplama |
| 20-22 | Demo backup: pre-rendered statik PNG fallback |
| 22-24 | Demo dry-run #1 #2; ekran-paylaşım testi |

### Out of Scope
- Ham veri çekme (P1)
- Etiket (P2)
- Model eğitimi (P3)
- Türetilmiş indeks hesaplama (P4)
- InSAR koherans — sadece amplitude (sade kapsam)
- Sahanın 3D hacim hesabı — sade kapsam
- Drone/UAV görseli — sade kapsam
- AR/VR sahne ziyareti — sade kapsam
- Animasyonlu mining timelapse video editing — basit GIF yeter
- Mobile responsive — Streamlit desktop yeter

### Interface Contract (Çıktı)
```
/data/change_and_overlay/
  ├── s1_amplitude_diff_2024_2025.tif
  ├── landsat_timeseries/
  │   ├── 1985.tif
  │   ├── 2000.tif
  │   ├── 2015.tif
  │   ├── 2025.tif
  │   └── animation.gif
  ├── pumice_growth_rates.geojson         # saha bazında yıllık % değişim
  ├── wdpa_goreme_buffer1000m.geojson
  ├── red_flag_alerts.json
  └── kpi_summary.json

/frontend/
  ├── layers.json                          # Streamlit manifest
  └── folium_map_init.py
```

**layers.json şeması:**
```json
{
  "base_layers": [
    {"name": "Sentinel-2 RGB", "path": "...", "type": "raster", "default_visible": true}
  ],
  "modul_a_outputs": [
    {"name": "Pomza Olasılığı (U-Net)", "path": "/output/prob.tif", "colormap": "hot", "opacity": 0.7},
    {"name": "ASTER Quartz Index", "path": "/data/derived/aster_qi.tif", "colormap": "viridis", "opacity": 0.5},
    {"name": "Sentinel-1 Change Detection", "path": "/data/change_and_overlay/s1_amplitude_diff_2024_2025.tif"},
    {"name": "Landsat 1985-2025 Animation", "path": "/data/change_and_overlay/landsat_timeseries/animation.gif", "type": "gif"}
  ],
  "overlays": [
    {"name": "UNESCO Buffer (1000m) — Red Flag", "path": "/data/change_and_overlay/wdpa_goreme_buffer1000m.geojson", "color": "red", "fill_opacity": 0.3}
  ],
  "kpi_summary_path": "/data/change_and_overlay/kpi_summary.json"
}
```

---

## 6. ENTEGRASYON OTURUMU — SAAT 18-20

5 kişi birlikte tek oturumda:
- **P1:** Pipeline tek tıkla koşuyor mu doğrula (`run_pipeline.sh`)
- **P2:** Train/val/test split donmuş, etiket QC raporu hazır
- **P3:** Model donmuş, inference fn `<2 sn` test edildi
- **P4:** Score-level füzyon (`fuse_confidence()`) canlı sonuç veriyor
- **P5:** Streamlit dashboard 3 ekranı (Saha Tarama → AI Analizi → Operasyonel Karar geçiş slot'u) Modül A için tam çalışıyor

**Final çıktı zinciri:**
```
P1 (ARD)
  └─→ P3 (U-Net olasılık raster: prob.tif)
        └─→ P4 (score-level füzyon: prob × QI × CI penalty → final_confidence.tif)
              └─→ P5 (Folium harita layer + UNESCO red flag overlay + KPI)
                    └─→ Streamlit dashboard (frontend takımı)
```

---

## 7. RİSK SAHİBİ EŞLEŞMESİ

| Risk | Sahip | Mitigasyon |
|---|:-:|---|
| Sentinel-2 son tile bulutlu | P1 | Cloud mask + en yakın temiz tile fallback (pre-cache) |
| MAPEG ruhsat shapefile yok | P2 | Manuel poligon (BlokBims/Miner saha konumları kamuya açık) |
| GPU yok / Colab T4 yetmez | P3 | Pretrained + 256×256 tile + FP16 |
| ASTER L1B → L2 atmosferik düzeltme yavaş | P4 | NASA AROP yerine `pyatcor` veya subtract-dark-object; sürerse L1T (radiance) ile devam — QI relatif ölçüm, mutlak gerekmez |
| Landsat tarihi arşivde Avanos bulutlu | P5 | 4 yerine 3 snapshot (1990/2010/2025); GIF kısalır |
| Streamlit demo crash | P5 | Pre-rendered statik PNG fallback hazır |
| P1 → P3 ARD gecikirse | P1 + P3 | P3 sentetik veriyle iskelet kursun, ARD geldiğinde DataLoader değişir |

---

# DEEP RESEARCH PROMPTLARI (5 KİŞİ İÇİN BAĞIMSIZ)

> Aşağıdaki 5 prompt, her ekip üyesinin hackathon başlamadan önce ChatGPT Deep Research, Claude Deep Research veya Gemini Deep Research'e doğrudan yapıştırarak çalıştırabileceği şekilde hazırlanmıştır. Promptlar bağımsızdır — her biri kendi başına yetecek bağlamı içerir.

---

## P1 — VERİ MÜHENDİSİ DEEP RESEARCH PROMPTU

```
ROL: "PomzaScope" pomza tespit projesinde Veri Mühendisi rolündesin.
24 saat içinde Avanos/Nevşehir bölgesi için Sentinel-2 L2A, Sentinel-1
GRD ve Copernicus DEM GLO-30 verilerini Google Earth Engine ve yerel
Python ortamında çekip, co-register edip, 17-kanal ARD GeoTIFF olarak
export edeceksin.

SOMUT KOŞULLAR:
- AOI: Avanos+Acıgöl+Gülşehir, ~30×30 km, merkez (38.7°N, 34.85°E)
- Hedef CRS: EPSG:32636 (UTM Zone 36N)
- Hedef çözünürlük: 10 m (S2 grid)
- Çıktı: 17 kanal (S2 13-bant + S1 VV/VH + DEM elevation/slope)
- Tile: 256×256 piksel, 32 piksel overlap
- Bulut maskeleme: S2 SCL bandı

ARAŞTIRMA SORULARI:
1. GEE'de Sentinel-2 L2A median composite üretirken bulut maskeleme
   için en güncel best practice nedir? `s2cloudless` mı, SCL mi, Cloud
   Score Plus (CS+) mu? Kapadokya kış aylarında bulut yoğun olduğu
   için son 6 ay vs 12 ay penceresi karşılaştırması ne fark yaratır?

2. Sentinel-1 GRD'yi GEE'den IW mode VV+VH ile çekip yerel GeoTIFF
   olarak export ederken Refined Lee speckle filter + multi-temporal
   averaging'in en sade Python implementasyonu nedir? GEE içi mi
   yoksa export sonrası SNAPISTA mı?

3. Copernicus DEM GLO-30 vs ASTER GDEM v3 vs SRTM — Avanos açık ocak
   madenciliği için yükseklik doğruluğu hangisinde daha iyi? Yerel
   kalibrasyon noktası önerin var mı?

4. Co-registration: S2 (10m) + S1 (10m) + DEM (30m → 10m resample)
   pixel-perfect alignment için `rasterio.warp.reproject` parametre
   seçimi (resampling=bilinear vs cubic vs nearest), shifting tolerance
   ne olmalı?

5. Tile splitting: 256×256 patch için en hızlı Python yöntemi
   (`xarray-spatial`, `rasterio.windows`, custom numpy slicing) — 10
   GB'lık ARD stack için 5 dakikada biten hangisi?

6. ARD output formatı: GeoTIFF multi-band vs Zarr chunked vs Cloud-
   Optimized GeoTIFF (COG) — PyTorch DataLoader hızı için hangisi
   optimal? COG + STAC manifest 24 saatlik MVP için aşırı mı?

7. Demo offline cache: internet kesilirse Streamlit canlı inference
   patlamaması için `joblib.Memory` veya `diskcache` ile yerel cache
   örneği var mı?

8. Hata fallback: S2 son temiz tile 30+ gün eski (kış bulutu) — daha
   eski tile mi, ESA WorldCover 2021 baseline mı, sentetik mi? Pomza
   ocak değişim hızı yıllık olduğuna göre 30 gün eskimek modeli ne
   kadar bozar?

ÇIKTI:
- 8 sorunun her birine 200-300 kelime cevap, en az 2 birincil kaynak
  (akademik, GEE doc, GitHub repo) URL'si
- Kopyala-yapıştır çalışan Python kod parçaları: GEE çekim, S1 Lee
  filter, co-registration, tile splitter
- Saatlik plana risk haritası: hangi adım hangi saatte patlarsa hangi
  fallback

KAPSAM DIŞI (yazma):
- ML model mimarisi
- Etiketleme stratejisi
- ASTER TIR atmosferik düzeltme
- Türetilmiş indeksler (NDVI/BSI/QI)
- Change detection
- Frontend / Streamlit
- VRP / rota optimizasyonu (Modül B)

DİL: Türkçe; teknik terimler (band, raster, CRS, tile) İngilizce
kalsın.
```

---

## P2 — ETİKETLEME LEAD DEEP RESEARCH PROMPTU

```
ROL: "PomzaScope" pomza tespit projesinde Etiketleme Lead rolündesin.
24 saat içinde Avanos için pomza pozitif/negatif yer doğrusu (ground
truth) veri setini sıfırdan oluşturacaksın: MAPEG ruhsat sorgusu,
manuel poligon çizimi, dengeli negatif örnekleme, mekânsal train/val/
test split, augmentation pipeline.

SOMUT KOŞULLAR:
- Bölge: Avanos+Acıgöl+Gülşehir
- Pozitif hedef: 30-40 pomza saha poligonu
- Negatif hedef: 100-150 dengeli örnek
- UNESCO Göreme buffer (1000m) etiket dışı
- Split: %70/15/15 mekânsal
- Tile boyutu: 256×256 (P1'in çıktısıyla aynı grid)
- Augmentation: albumentations
- Araç: QGIS + Sentinel-2 RGB altlık + EO Browser

ARAŞTIRMA SORULARI:
1. MAPEG e-Maden GeoServer toplu vektör indirme yolu var mı?
   Workaround olarak Avanos için pomza ruhsat poligonlarını hangi
   alternatif kaynaklardan (MTA Yerbilimleri Harita Görüntüleyici,
   Çevre Şehircilik CBS, OSM landuse=quarry) çapraz toplayabilirim?

2. BlokBims (Çardak), Miner Madencilik (Avanos+Niğde), Pomza Export,
   Map-Stones, Anorikan, Emin Pomza ve diğer Nevşehir pomza
   üreticilerinin saha (ocak) konumlarını web sitelerinden ve Google
   Maps'ten doğrulamanın en hızlı yolu nedir? Bu firmaların açık
   ocaklarının uydu-görünür sınırını manuel çizerken hangi referans
   görüntü tarihi en iyi (kış mı yaz mı, hangi yıl)?

3. Manuel poligon etiketleme için QGIS vs CVAT vs Roboflow Annotate
   vs LabelMe — Sentinel-2 RGB altlık üzerinde 30-40 saha için en
   hızlısı hangisi? Sınırları belirsiz açık ocaklar için "fuzzy
   boundary" sözleşmesi nasıl kurulmalı (örn. dış kenar +5 piksel
   buffer)?

4. Negatif örnekleme stratejisi: Kapadokya'da pomza dışındaki
   spektral olarak benzer ama pomza-olmayan yüzeyler nedir? Açık
   tüf yüzeyleri (Göreme/Zelve), volkanik kayaç düzlüğü, çakıllı
   yüzey, açık inşaat sahası, yapay yapay açık alan — bunların
   her birinden kaç negatif örnek almak gerekiyor?

5. Mekânsal split: rastgele split yerine spatial blocking
   (`spacv` veya manuel grid) — hangisi pomza için overfit'i azaltır?
   Avanos kuşağında pomza sahaları kümeli olduğu için block size ne
   olmalı (5 km mi, 10 km mi)?

6. Augmentation: Sentinel-2 multi-spectral (13 bant) + S1 (2 bant) +
   DEM (2 türev) tensörü üzerinde hangi augmentation güvenli, hangisi
   spektral/fiziksel tutarlılığı bozar? `albumentations.ChannelDropout`
   spektrum modeli için anlamlı mı? Mixup/CutMix mineral segmentasyon
   için literatürde önerilmiş mi?

7. Etiket tutarlılığı (inter-annotator agreement) tek kişi etiketse
   nasıl ölçülür? Aynı 5 sahayı 2 kez etiketleyip Cohen's Kappa /
   IoU karşılaştırması yapmak 24 saat içinde değer katar mı?

8. UNESCO buffer alanını "etiket dışı" yapmanın PyTorch loss'unda
   tek standart yolu var mı (sample_weight, ignore_index=255,
   masked loss)? Loss seviyesinde mi, DataLoader seviyesinde mi
   maskelemek daha temiz?

ÇIKTI:
- 8 sorunun her birine 200-300 kelime cevap, en az 2 birincil kaynak
- Kopyala-yapıştır kod: QGIS Python console saha import script,
  spatial split snippet, albumentations pipeline (multi-channel),
  Cohen's Kappa hesabı
- 30-40 saha hedefini saatlik mikro-plana indir (saat başına kaç
  pozitif çizilecek)

KAPSAM DIŞI (yazma):
- Ham veri çekme
- Model eğitimi
- Türetilmiş indeksler
- Change detection
- Frontend
- Avanos dışı bölge
- Pomza kalite alt-sınıfları (sadece binary "pomza var/yok")

DİL: Türkçe; teknik terimler İngilizce.
```

---

## P3 — ML MÜHENDİSİ DEEP RESEARCH PROMPTU

```
ROL: "PomzaScope" pomza tespit projesinde ML Mühendisi rolündesin.
24 saat içinde TorchGeo + SSL4EO-S12 MoCo pretrained Sentinel-2
13-bant ağırlığı üzerine multi-channel adapter ekleyerek 17-kanal
(S2 + S1 + DEM) U-Net modelini fine-tune edeceksin. Threshold tuning,
ablation study, inference function ve Grad-CAM görseli üreteceksin.

SOMUT KOŞULLAR:
- Backbone: ResNet50 (TorchGeo SSL4EO-S12 MoCo pretrained)
- Mimari: U-Net (segmentation_models_pytorch)
- Input: 17 kanal — 13 bant pretrained + 4 random init
- Output: binary segmentation (pomza/arkaplan)
- Loss: Dice + BCE hibrit
- Optimizer: AdamW (lr=1e-4)
- Eğitim: 30-50 epoch, T4 GPU (Colab veya yerel)
- Hedef inference süresi: <2 saniye / 256×256 tile
- Hedef metrik: F1 ≥0.75, IoU ≥0.60
- Veri: P2'den ~30 pozitif + 100 negatif tile, mekânsal split

ARAŞTIRMA SORULARI:
1. TorchGeo'nun `ResNet50_Weights.SENTINEL2_ALL_MOCO` ağırlığı
   `segmentation_models_pytorch.Unet` encoder'ına nasıl yüklenir?
   Örnek kod var mı? `strict=False` kullanmak gerek mi?

2. Multi-channel input adapter: pretrained 13-kanal first conv'u
   17-kanala genişletmenin en sağlam yolu nedir? Ek 4 kanalın (S1 VV,
   VH, DEM yükseklik, eğim) ağırlık başlatma stratejisi (random,
   replicate, zero, ImageNet RGB ortalama)? Literatür ne öneriyor?

3. Dice + BCE hibrit loss + UNESCO buffer için `ignore_index=255`
   maskelemenin PyTorch'ta tek temiz implementasyonu nedir?
   `MONAI.losses.DiceCELoss` mi, custom mı?

4. Az veri (30 pozitif × 8 augmentation = ~240 örnek) ile fine-tuning
   için en güncel literatür ne öneriyor? Layer-wise learning rate
   decay (LLRD), partial freeze (encoder ilk 2 stage donduralım mı),
   warmup epoch sayısı?

5. Threshold tuning: validation set'te F1-optimal threshold ararken
   `youden_j_statistic` mi, sadece F1 grid mi? Pomza için sınıf
   dengesizliği (~%4 pozitif piksel) varsa precision-recall AUC
   tabanlı eşik mi daha sağlam?

6. Ablation study: 5 konfigürasyon (S2 RGB / +SWIR / +S1 / +DEM /
   +ASTER QI post-process) için fair karşılaştırma için aynı seed,
   aynı epoch sayısı, aynı val set'i kullanırken karşılaşılan tipik
   tuzaklar nelerdir?

7. Grad-CAM hangi katmanda hesaplanmalı (encoder son conv vs decoder
   üst katman)? Multi-bant input'ta tek bir Grad-CAM'in yorumu
   anlamlı mı, yoksa kanal-bazlı saliency mı? Pomza tespitinde
   örnek görselleştirme repo var mı?

8. Inference süresi optimizasyonu: T4 GPU'da 256×256 tile için
   FP16 / `torch.compile` / TorchScript / ONNX — hangisi 24 saatte
   en kolay ve <2sn'ye indirir? Streamlit içinde CUDA üzerinden
   inference için memory leak riskleri?

ÇIKTI:
- 8 sorunun her birine 200-300 kelime cevap, en az 2 birincil kaynak
- Kopyala-yapıştır kod: SSL4EO-S12 → smp Unet yükleme, multi-channel
  adapter, hibrit loss, threshold tuning, ablation runner, Grad-CAM
- Eğitim süresi tahmini saatlik plana göre uyarlama (T4 GPU ile 30
  epoch ne kadar sürer)

KAPSAM DIŞI (yazma):
- Veri çekme
- Etiket çizimi
- Türetilmiş indeksler
- Change detection
- Frontend
- Custom CNN scratch
- Hyperspectral fine-tuning
- Foundation model (Prithvi-EO) fine-tuning

DİL: Türkçe; teknik terimler İngilizce.
```

---

## P4 — SPEKTRAL MÜHENDİS DEEP RESEARCH PROMPTU

```
ROL: "PomzaScope" pomza tespit projesinde Spektral Mühendis
rolündesin. 24 saat içinde pomzanın 5 fiziksel imzasını sayısal
olarak ölçen tüm türetilmiş indeksleri hesaplayacaksın: Sentinel-2
NDVI / BSI / Albedo / Sabins B11/B12 / Iron Oxide; ASTER L1B → L2
düzeltme + Ninomiya Quartz Index, SiO₂ Kimyasal İndeks, Carbonate
Index. Score-level füzyon mantığını yazacaksın: U-Net olasılığı ×
ASTER QI ağırlığı.

SOMUT KOŞULLAR:
- AOI: Avanos+Acıgöl+Gülşehir
- S2 grid: 10 m, EPSG:32636
- ASTER TIR: 90 m → 10 m bilinear resample
- Pomza spektral fingerprint: yüksek albedo (>0.3), Al-OH absorpsiyon
  2.1-2.3 µm, SiO₂ TIR 8-12 µm Si-O esnek-bük titreşimi
- Akademik dayanak: Ninomiya 2002, Liang 2001, van der Meer 2014

ARAŞTIRMA SORULARI:
1. ASTER L1B Avanos sahnesi NASA Earthdata'dan en hızlı nasıl
   indirilir? `astera2tools` mu, manuel HDF-EOS download mu, Earthdata
   Cloud (Harmony) API mi? L1B → L2 atmosferik düzeltme için NASA
   AROP (eski), `pyatcor`, ENVI/IDL FLAASH alternatifleri içinde 24
   saatte koşturulabilir hangisi?

2. Ninomiya 2002 Quartz Index = B11²/(B10×B12) — bu indeks Avanos
   gibi asidik volkanik camsı pomza (riyolitik) için literatürde
   doğrulanmış mı? Cuprite Nevada veya benzer riyolitik bölgelerde
   tipik QI değer aralığı nedir? Pomza vs yan-tüf ayrımı QI ile
   yapılabilir mi yoksa sadece silikat mineral mi ölçer?

3. ASTER 90m → S2 10m bilinear resample tutarlı mı yoksa pansharpening
   gerekir mi? `rasterio.enums.Resampling` seçenekleri arasında pomza
   için en az artefakt yaratan hangisi?

4. Sentinel-2 Sabins ratio (B11/B12) Al-OH proxy olarak kullanılırken
   atmosferik düzeltme tutarlılığı kritik mi? L2A surface reflectance
   üzerinde mi yapılmalı, yoksa TOA'da da çalışır mı?

5. Albedo Liang 2001 formülü Sentinel-2 için katsayıları (0.356·B2 +
   0.130·B4 + 0.373·B8 + 0.085·B11 + 0.072·B12 - 0.0018)/1.016 —
   bu formül Landsat için kalibre edilmişti, Sentinel-2 için yeniden
   katsayı türetilmiş mi? Bonafoni 2016 veya sonrası referans?

6. Score-level füzyon: `final = unet_prob × normalize(QI) ×
   (1 - normalize(CI))` formülü için literature'da önerilen ağırlık
   öğrenme yöntemleri var mı (Bayesian Model Averaging, Dempster-
   Shafer, basit linear regression)? 24 saatte fixed-weight (manual
   tuning) yeter mi?

7. USGS Spectral Library v7 (Kokaly 2017) "rhyolite glass" +
   ECOSTRESS Spectral Library "pumice" referans imzalarına Sentinel-2
   resampled spektrum nasıl üretilir? `spectral` Python paketi yeterli
   mi? Spectral Angle Mapper (SAM) + Spectral Information Divergence
   (SID) hangisi pomza için daha güçlü?

8. Tüm türetilmiş indeksleri tek `xarray.Dataset` olarak yönetmenin
   diske yazma (Zarr) ve PyTorch DataLoader ile okuma performansı
   nedir? `rioxarray` + `dask` gerekiyor mu?

ÇIKTI:
- 8 sorunun her birine 200-300 kelime cevap, en az 2 birincil kaynak
- Kopyala-yapıştır kod: ASTER L1B çekim+düzeltme, Ninomiya QI/SiO2/CI
  numpy implementasyonu, Sentinel-2 indeksleri, score-level füzyon,
  SAM eşleme
- Her indeks için pomza tipik değer aralığı tahmini (literatür-tabanlı)

KAPSAM DIŞI (yazma):
- Ham S2/S1/DEM çekme
- Etiket
- U-Net eğitimi
- Change detection
- Frontend
- Hyperspectral PRISMA atmospheric correction (sadece pre-cache görsel)
- EnMAP foundation model fine-tuning (sadece SAM eşleme statik)
- Custom radiative transfer

DİL: Türkçe; teknik terimler İngilizce.
```

---

## P5 — CHANGE DETECTION + UNESCO + VISUALIZATION DEEP RESEARCH PROMPTU

```
ROL: "PomzaScope" pomza tespit projesinde Change Detection + UNESCO
Overlay + Visualization Lead rolündesin. 24 saat içinde Avanos pomza
ocaklarının "önceki ve şimdiki" change detection'ını üreteceksin
(Sentinel-1 SAR amplitude difference + Landsat 1985→2025 zaman
serisi), WDPA Göreme polygon + buffer ile UNESCO red flag overlay
yapacaksın, tüm Modül A çıktılarını Folium/Leafmap üzerinde
Streamlit dashboard için tek manifest olarak hazırlayacaksın.

SOMUT KOŞULLAR:
- Bölge: Avanos+Acıgöl+Gülşehir
- Sentinel-1 change: T1 (2024-Q4) ve T2 (2025-Q4) ortalama amplitude farkı
- Landsat snapshot: 1985, 2000, 2015, 2025
- WDPA Göreme polygon + 1000m buffer
- Folium / Leafmap + Streamlit
- KPI: saha bazında alan (ha), 5-yıl büyüme %, UNESCO ihlali (var/yok)

ARAŞTIRMA SORULARI:
1. Sentinel-1 amplitude difference change detection için en sade
   yöntem nedir — log-ratio, normalized difference, basit subtraction?
   Açık ocak madenciliği literatüründe hangisi standart (Mazza et al.
   2023, Wang et al. 2021)? Eşikleme yöntemi (Otsu, K-means, sabit
   percentile) nasıl seçilmeli?

2. Landsat Collection 2 SR (Surface Reflectance) vs Level-1 (TOA)
   tarihi snapshot'lar (1985, 2000, 2015, 2025) için karşılaştırılabilir
   RGB composite üretmek mümkün mü? Pre-1984 Landsat-5 TM ve sonrası
   Landsat-7/-8/-9 farklı sensör — radyometrik harmonizasyon gerekli
   mi (Roy et al. 2016 cross-sensor calibration)?

3. WDPA Göreme National Park polygon: protectedplanet.net API'den
   programatik indirme nasıl? OSM "Goreme National Park" relation
   Overpass API sorgusu ne? İki kaynak arasında polygon farkı tipik
   olarak ne kadar (UNESCO buffer için 500m mı 1000m mı 2000m
   konservatif olmalı)?

4. Folium vs Leafmap vs Streamlit-Folium vs `pydeck` vs `kepler.gl` —
   Streamlit dashboard'da 5+ raster + 3+ vektör layer toggle ile en
   smooth deneyim hangisi? Performance trade-off (özellikle GeoTIFF
   raster overlay için)?

5. Yıllık alan büyüme % hesaplama: poligon → alan (ha) → yıllık
   geometric mean growth rate (GMR). Açık ocak madenciliği
   literatüründe hangi formül standart? Paterson 2018 veya benzer
   referans var mı?

6. Demo backup: canlı Folium render Streamlit'te crash olursa
   pre-rendered statik PNG fallback'in tek satır implementasyonu nedir
   (`folium.Map.save()` + `selenium` headless screenshot, veya
   `imgkit`)? 5 katmanın her biri için ayrı PNG mi, kompozit mi?

7. Sentinel-1 amplitude difference için "kazı genişlemesi" anlamlı
   sinyali "yağış nedeniyle nem değişimi" gürültüsünden ayırmak için
   filtre (örn. ortalama yağış maskesi, multi-temporal median) gerekli
   mi? Avanos için kuru sezon (Mayıs-Eylül) mu kullanmalı?

8. Streamlit + Folium içinde GeoTIFF raster overlay'i performant
   render etmek için tile pyramid (`gdal2tiles`, `xyzservices`,
   `rio-tiler`) gerekli mi yoksa tek-tile direct mi?

ÇIKTI:
- 8 sorunun her birine 200-300 kelime cevap, en az 2 birincil kaynak
- Kopyala-yapıştır kod: S1 amplitude diff, Landsat zaman serisi GIF,
  WDPA polygon + buffer (shapely), Folium çoklu-layer skeleton,
  Streamlit-Folium entegrasyon, demo PNG fallback
- 4 Landsat snapshot'tan tek GIF üretmenin imageio/Pillow tek dosyalık
  scripti

KAPSAM DIŞI (yazma):
- Ham veri çekme
- Etiket
- Model eğitimi
- Türetilmiş indeksler (NDVI/BSI/QI)
- InSAR koherans (sadece amplitude)
- Sahanın 3D hacim hesabı
- AR/VR
- Mobile responsive

DİL: Türkçe; teknik terimler İngilizce.
```

---

*Hazırlama tarihi: 1 Mayıs 2026*
*Kapsam: sadece Modül A development; müşteri / ticarileşme / jüri içeriği yok*
