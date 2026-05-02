# P2 — Etiketleme Lead Güncel Durum Raporu

> Tarih: 2026-05-02  
> Kaynak: `Modul_A_Critical_Path_Dependency_v2.md`  
> Son guncelleme: P1 AOI uyumsuzlugu tespit edildi, duzeltme yapildi

---

## 1. Tamamlanan Gorevler

| Gorev | Cikti | Durum |
|---|---|---|
| T2.1 QGIS kurulumu | — | TAMAM |
| T2.2 MAPEG CED sorgu | `data/labels/02_mapeg_query.csv` | TAMAM |
| T2.3 Manuel pozitif poligon (27 saha) | `data/labels/positive_polygons.gpkg` | TAMAM |

---

## 2. Kritik Sorun — AOI Uyumsuzlugu (COZULDU)

### Tespit
P1'den gelen `data/ard/full_ard_20m.tif` raster'i ile P2'nin cizilen poligonlari arasinda
**cografi uyumsuzluk** tespit edildi:

| | Enlem (WGS84) | Boylam (WGS84) |
|---|---|---|
| P1 raster kapsami | 38.65°N – 38.85°N | 34.70°E – 35.00°E |
| P2 poligon kapsami | 38.47°N – 38.71°N | 34.66°E – 34.82°E |
| Ortusme | **sadece ~0.06° (~7 km)** | kismi |

**Sonuc:** 27 poligonun 24'u (%89) raster kapsami disinda kaldi. Ortusen alan sadece 3 poligon,
toplamda 19 piksel — egitim icin yetersiz.

### Yapilan Duzeltme

`code/p1/02_aoi_avanos.py` guncellendi:

```python
# Eski
BBOX_WGS84 = (34.70, 38.65, 35.00, 38.85)

# Yeni — tum pomza sahalari dahil, 0.05 derece buffer ile
BBOX_WGS84 = (34.60, 38.40, 35.00, 38.90)
```

`code/p2/07_spatial_block_cv.py` guncellendi:  
`tile_index.json` formatini (pixel_offset) UTM bbox'a cevirme destegi eklendi.

---

## 3. Mevcut Bekleme Durumu (P1 Blokaj)

Asagidaki gorevler **yeni raster gelene kadar baslayamaz**:

| Gorev | Bekledigi P1 Ciktisi |
|---|---|
| T2.4 Pozitif piksel ornekleme | `data/ard/full_ard_20m.tif` (yeni) |
| T2.5 Negatif piksel ornekleme | `data/ard/full_ard_20m.tif` (yeni) |
| T2.6 WDPA ignore mask | `data/ard/full_ard_20m.tif` (yeni) |
| T2.7 Spatial 5-fold blok CV | `data/tiles/tile_index.json` (yeni) |
| **T2.8 full_mask.tif (CRITICAL PATH)** | T2.4–T2.7 ciktilarinin tamami |

**P1'in calistirmasi gereken komutlar (sirasyla):**
```bash
python code/p1/02_aoi_avanos.py          # AOI yenile (duzeltme zaten yapildi)
python code/p1/03_sentinel2_l2a_fetch.py # S2 yeniden cek
python code/p1/05_sentinel1_grd_fetch.py # S1 yeniden cek
python code/p1/06_dem_slope.py           # DEM/slope yenile
python code/p1/07_full_coregistration.py # 17 kanal co-register
python code/p1/08_tile_splitting.py      # Tile'lari bol
python code/p1/09_export_manifest.py     # Manifest uret
```

---

## 4. P1 Ciktilari Gelince Calistirilacak Siradaki Adimlar

```bash
# T2.4 — Pozitif piksel ornekleme
python code/p2/04_pixel_sampling.py \
  --positives data/labels/positive_polygons.gpkg \
  --raster data/ard/full_ard_20m.tif \
  --out data/labels/positive_pixels.gpkg

# T2.6 — WDPA ignore mask (T2.4 ile paralel)
python code/p2/06_wdpa_ignore_mask.py \
  --wdpa "data/raw/WDPA_WDOECM_May2026_Public_478637_shp-polygons.shp" \
  --raster-ref data/ard/full_ard_20m.tif \
  --out-buffer data/labels/wdpa_buffer.gpkg \
  --out-mask data/labels/ignore_mask.tif

# T2.5 — Negatif piksel ornekleme (T2.6 sonrasi)
python code/p2/05_negative_sampling.py \
  --positives data/labels/positive_polygons.gpkg \
  --raster data/ard/full_ard_20m.tif \
  --aoi data/aoi/avanos_aoi.gpkg \
  --out data/labels/negative_pixels.gpkg

# T2.7 — Spatial 5-fold blok CV (tile_index.json gelince)
python code/p2/07_spatial_block_cv.py \
  --manifest data/tiles/tile_index.json \
  --raster-ref data/ard/full_ard_20m.tif \
  --out data/labels/blok_cv_split.json

# T2.8 — Raster mask — CRITICAL PATH (hepsi tamamlaninca)
python code/p2/08_rasterize_mask.py \
  --positives data/labels/positive_pixels.gpkg \
  --negatives data/labels/negative_pixels.gpkg \
  --ignore-mask data/labels/ignore_mask.tif \
  --raster-ref data/ard/full_ard_20m.tif \
  --out data/labels/full_mask.tif
```

---

## 5. Diger P Rollerine Etkisi

### P3 (ML Muhendisi) — BLOKE

| P2 Ciktisi | P3 Gorev | Gecikme Etkisi |
|---|---|---|
| `positive_polygons.gpkg` (on versiyon) | T3.4 sanity check | Mevcut 27 poligon kullanilabilir ama raster disinda |
| `blok_cv_split.json` | T3.5 fine-tune (CV split) | T2.7 tamamlanana dek bekliyor |
| **`full_mask.tif`** | **T3.5 fine-tune (CRITICAL)** | **P1 raster gelmeden uretilemiyor** |

P3'un T3.5 fine-tune'u (critical path) `full_mask.tif` olmadan baslayamaz.
P1 raster uretimindeki her saat kaymasi, T3.5'i ve ardindan T3.10, T5.8, T5.13 zincirini kaydirir.

### P1 (Veri Muhendisi) — AKSIYON GEREKLI

AOI guncellemesi yapildi (`code/p1/02_aoi_avanos.py`).
Yeni raster boyutu: ~2700×2750 px (orijinal 1327×1137 yerine, ~5x daha genis alan).
Pipeline basi basina yeniden calistirilmali.

### P4 (Spektral Muhendis) — DOLAYLI ETKI

P4 dogrudan P2'ye bagimli degil. Ancak genisletilmis AOI P4'un ASTER/S2 indeks
layerlarinin da bu alani kapsamasini gerektirir. P1'in yeni raster'i geldikten sonra
P4'un `04_s2_indices.py` ve `06_resample_to_s2_grid.py` adimlarinin da ayni
genisletilmis grid uzerinde calistigini dogrulamali.

### P5 (Dashboard / Vizualizasyon) — DOLAYLI ETKI

P5, P3'un inference ciktisina (`raw_probability.tif`) bagli. P3 fine-tune P2'nin
`full_mask.tif`'ini bekledigi icin P5 downstream zinciri de baskili.
Streamlit dashboard test edilirken demo fallback PNG'lerin hazir olmasi onem kazanir.

---

## 6. Beklenen Ciktilar (Tamamlaninca)

```
data/labels/
  positive_pixels.gpkg     ~10K Point (label=1)      T2.4
  negative_pixels.gpkg     ~6K Point  (label=0)      T2.5
  wdpa_buffer.gpkg         Goreme + 1000m buffer     T2.6
  ignore_mask.tif          uint8, 255=ignore zone    T2.6
  blok_cv_split.json       Roberts 2017, 5-fold      T2.7
  full_mask.tif            uint8 0/1/255 -- CRITICAL T2.8
```

---

## 7. Risk & Plan B

| Risk | Tetik | Plan B |
|---|---|---|
| P1 raster gecikirse | full_mask.tif saat 13'u kacirir | P3 T3.5'e 3h slack var; P1 en gec saat 10'da teslim etmeli |
| 27 poligon yetersiz (~sanity esigi 30-40) | T2.4 ciktisi | P1 HELP slotunda (saat 14-16) 5-10 ek poligon cizebilir |
| 5-fold blok CV yetersiz dolu blok | T2.7 hata | `--n-folds 3 --blocks-x 3 --blocks-y 3` (orchestrator onayi) |

---

*Son durum: P1 yeni raster uretimi bekleniyor. P2 tarafinda T2.3 tamamlandi,
T2.4-T2.8 pipeline hazir — tetiklenmeyi bekliyor.*
