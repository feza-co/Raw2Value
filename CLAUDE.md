# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Pomzadoya** — Kapadokya pomza (pumice) madenciliğini uydu görüntüleriyle tespit eden AI/ML sistemi. Kapadokya Hackathon 2026 için geliştirilmektedir. 5 kişilik ekip, 24 saatlik sprint ile çalışır.

**Hackathon zorunlu kurallar** için bkz. [HACKATHON_KURALLARI.md](HACKATHON_KURALLARI.md):
- Kural 1: Coğrafi karbon izi (Nominatim + OpenRouteService)
- Kural 2: Canlı TCMB EVDS döviz kuru entegrasyonu
- Kural 3: OpenStreetMap tabanlı coğrafi işlem (Google Maps geçersiz)
- **Bonus:** 3 kuralı tek hesap zincirinde birleştirmek ek puan kazandırır

## Architecture

5 modüler rol tabanlı pipeline, birbirinin çıktısına bağımlı:

```
P1 (Veri)  →  P2 (Etiket)  →  P3 (Model)  →  P4 (Füzyon)  →  P5 (Dashboard)
ARD 17ch       full_mask.tif   raw_prob.tif   confidence.tif   Streamlit + Folium
```

**Kritik çıktı zinciri:**
- `data/ard/s2_l2a_20m.tif` — 17 kanallı Analysis Ready Data (P1 üretir, P3 tüketir)
- `data/labels/full_mask.tif` — Raster maske (P2 üretir, P3 tüketir)
- `data/labels/blok_cv_split.json` — 5-fold spatial CV bölünmesi (P2 üretir, P3 tüketir)
- `data/inference/raw_probability.tif` — U-Net çıktısı (P3 üretir, P4 tüketir)
- `data/inference/final_confidence.tif` — Füzyon sonucu (P4 üretir, P5 tüketir)
- `data/manifest.json` — Tüm çıktıların merkezi envanteri

**Koordinasyon referansı:** 24 saatlik kritik path ve bağımlılıklar için [Modul_A_Critical_Path_Dependency_v2.md](Modul_A_Critical_Path_Dependency_v2.md) primary kaynak olarak kullanılır.

## Running the Project

```bash
# Dashboard (P5 — ana demo çıktısı)
streamlit run code/p5/dashboard.py

# Model eğitimi (P3 — Colab GPU gerektirir)
python code/p3/06_train.py \
  --tile-dir data/ard/tiles \
  --full-mask data/labels/full_mask.tif \
  --split-json data/labels/blok_cv_split.json \
  --ssl4eo-ckpt <pretrained.pth> \
  --epochs 30 --batch-size 8 --lr 1e-4 --folds 5

# ARD pipeline sırası (P1)
python code/p1/02_aoi_avanos.py
python code/p1/03_sentinel2_l2a_fetch.py
python code/p1/07_full_coregistration.py
python code/p1/08_tile_splitting.py
python code/p1/09_export_manifest.py

# Spektral füzyon (P4)
python code/p4/fuse_confidence.py  # confidence = prob × QI_norm × (1 - CI_norm)
```

## Dependencies (Per Module)

Her modülün kendi `requirements.txt`'i var:

```bash
pip install -r code/p1/requirements.txt  # earthengine-api, rasterio, geopandas, GDAL
pip install -r code/p2/requirements.txt  # verde, scikit-learn, shapely
pip install -r code/p3/requirements.txt  # torch, segmentation_models_pytorch, timm
pip install -r code/p4/requirements.txt  # rasterio, GDAL, scipy, requests
pip install -r code/p5/requirements.txt  # streamlit, folium, leafmap, imageio
```

## Key Technical Details

**Koordinat sistemi:** Tüm rasterlar UTM 36N (EPSG:32636), 20m çözünürlük

**ARD kanalları (17ch):**
- S2 L2A: B2,B3,B4,B5,B6,B7,B8,B8A,B11,B12 (10 kanal, SWIR grid)
- S1 GRD: VV,VH (2 kanal)
- Türetilmiş: NDVI, NBR2, NDWI, BSI, Slope (5 kanal)

**Model:** SSL4EO-S12 pretrained ResNet-50 (MoCo) + U-Net decoder, 5-fold spatial block CV (Roberts 2017), F1-max threshold arama

**Füzyon formülü (P4):** `final_confidence = raw_prob × QI_norm × (1 - CI_norm)`
- QI: Ninomiya silica index (pomza mineral imzası)
- CI: Clay index (negatif maske)

**Tile boyutu:** 256×256 piksel, 32 piksel overlap (30 tile toplam)

## Agent Orchestration Protocol

Bu repo, Claude Code agent'larıyla koordineli çalışmak üzere tasarlanmıştır:

- Her P-rolü için agent tanımı: `.claude/agents/p_n-*.md`
- Orchestrator durumu: `.claude/state/orchestrator_log.md`
- Her role kendi ortamında çalışır (Colab / QGIS / lokal)
- **RUN-BLOCK → VERIFY-BLOCK → DELIVER** döngüsü kullanılır

**Commit formatı:**
```
[P_n] T_x.y <kısa açıklama>

DELIVER: <çıktı_yolu>
Bağımlı: <P_m T_z.w varsa>
```

**Branch adı:** `p_n-t_x.y-kisa-aciklama`

## Credentials & Data Access

- **Google Earth Engine:** `pomzadoya-sa.json` servis hesabı (proje: `pomzadoya`)
- **NASA Earthdata:** ASTER L1B için `.netrc` kimlik bilgisi gerekir
- **TCMB EVDS:** API anahtarı `EVDS_API_KEY` env değişkeni olarak tanımlanmalıdır
- `data/` klasörü Git'e push edilmez (.gitignore); büyük dosyalar için Git LFS kullanılır

## Data Locations

```
data/aoi/           # AOI poligonları (Avanos/Nevşehir)
data/ard/           # 17 kanallı 20m ARD rasterlar
data/tiles/         # 256×256 eğitim tile'ları
data/labels/        # Etiket maskeleri ve CV bölünmeleri
data/dem/           # Copernicus DEM
data/landsat/       # 1985–2025 Landsat zaman serisi
data/inference/     # Model çıktıları (raw + fused)
data/manifest.json  # Merkezi çıktı envanteri
```
