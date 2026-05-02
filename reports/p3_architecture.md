# P3 — Model Mimarisi ve Tasarım Kararları

**Modül A v2 — Pomzadoya Hackathon (24h penceresi)**
**Sahibi:** P3 ML Mühendisi
**Versiyon:** 2026-05-02

> Bu doküman P3'ün ML pipeline'ının mimari tercihlerini, akademik dayanaklarını ve kritik kararlarını anlatır. Demo sunumunda 1 slayt + jüri sorularına 5 dakika cevap için referans.

---

## 1. ÖZET

P3, Avanos/Nevşehir bölgesinde uydu tabanlı **pomza (pumice) madencilik tespiti** için bir derin öğrenme tabanlı segmentasyon modelini eğitir. Mimari yığın:

- **Backbone:** SSL4EO-S12 ResNet-50 (Wang et al. 2023, MoCo v2 self-supervised pretrained, 3-kanal)
- **Adapter:** 3 → 17 kanal `mean_replicate` genişletme (multi-channel ARD desteği)
- **Decoder:** segmentation_models_pytorch U-Net (skip connections, transpose conv upsampling)
- **Training:** Roberts 2017 spatial 5-fold blok CV, AdamW + CosineLR + AMP FP16
- **Loss:** BCE + Dice (combo, ignore_index=255 WDPA Göreme buffer)
- **Output:** **RAW olasılık** [0, 1] — threshold YASAK (Karar #6, P4 fuse_confidence yapacak)

**Hedef metrik:** 5-fold ortalama val IoU > 0.45, std < 0.08.

---

## 2. NEDEN SSL4EO-S12

### 2.1 Akademik dayanak

Wang et al. (2023) SSL4EO-S12, **3 milyon küresel Sentinel-2 sahnesinden** kendi denetimli (MoCo v2) önceğitilen bir ResNet-50'dir. Geleneksel ImageNet pretrained CNN'ler doğal RGB fotoğraflara optimize iken, SSL4EO uydu görüntüsünün spektral, mevsimsel ve atmosferik özelliklerine adapte olur:

- **Spektral domain match:** Reflectance bantları, RGB pikselleri değil.
- **Spatial scale match:** 10-20m piksel, doğal görüntü değil.
- **Atmospheric variance:** Bulut, sis, gölge varyasyonu öğrenilmiş.

### 2.2 Hackathon pratik avantajları

- 24h pencerede **sıfırdan eğitmek imkansız** (50K+ etiket gerek). Pretrained backbone ile 200-500 etiketli tile yeter.
- **Genelleme garantisi:** Avanos AOI'da gözlenmemiş atmosferik koşullar bile backbone'da temsil edilmiş.
- **Convergence:** ImageNet'e göre 3-5x daha hızlı yakınsama (uydu domain'inde gözlenen).

### 2.3 B3 vs B13 tercihi

Modül A v2 dökümanı orijinal olarak **13-kanal SSL4EO-S12** öneriyordu (tüm Sentinel-2 bantları). Hackathon başlangıcında HuggingFace `wangyi111/SSL4EO-S12` reposunda **B13 ResNet-50 MoCo bulunmadığı** keşfedildi (sadece ViT MAE versiyonları var). Karşılığında **B3 RN50 MoCo** (3-kanal Sentinel-2 RGB) seçildi.

**Sonuçları:**
- B3 backbone yalnızca 3 kanal görmüş, 13 kanal görmemiş → adapter genişletmesi gerekti.
- ImageNet kontaminasyonu yok (saf S2 RGB).
- Konvolüsyon ağırlıkları RGB istatistiklerine optimize, ama derin katmanlar (layer2-4) generic feature extractor.

---

## 3. 3 → 17 KANAL ADAPTER

### 3.1 ARD bant şeması (P1 sözleşmesi)

P1 17-bantlık ARD raster üretir (`data/ard/full_ard_20m.tif`):

| idx | Bant | Kaynak | Birim | Pomza ile ilgisi |
|---|---|---|---|---|
| 0 | S2 B2 (Blue 490nm) | Sentinel-2 L2A | reflectance | Yüksek albedo |
| 1 | S2 B3 (Green 560) | Sentinel-2 L2A | reflectance | Yüksek albedo |
| 2 | S2 B4 (Red 665) | Sentinel-2 L2A | reflectance | Liang albedo komponenti |
| 3 | S2 B5 (RE 705) | Sentinel-2 L2A | reflectance | Vegetation discrimination |
| 4 | S2 B6 (RE 740) | Sentinel-2 L2A | reflectance | Vegetation discrimination |
| 5 | S2 B7 (RE 783) | Sentinel-2 L2A | reflectance | Vegetation discrimination |
| 6 | S2 B8 (NIR 842) | Sentinel-2 L2A | reflectance | NDVI komponenti, vej. red. |
| 7 | S2 B8A (NIR narrow 865) | Sentinel-2 L2A | reflectance | Su buharı azaltılmış NIR |
| 8 | S2 B11 (SWIR1 1610) | Sentinel-2 L2A | reflectance | **Pomza/silikat eşik** (Sabins 1999) |
| 9 | S2 B12 (SWIR2 2190) | Sentinel-2 L2A | reflectance | **B11/B12 ratio** (van der Meer 2014) |
| 10 | S1 VV_dB | Sentinel-1 GRD | dB | Pürüz/açık alan ayrımı |
| 11 | S1 VH_dB | Sentinel-1 GRD | dB | Volüm scattering (orman maskeleme) |
| 12 | DEM (m) | Copernicus GLO-30 | metre | Topografi (madencilik genelde alçak) |
| 13 | slope (deg) | EE Terrain | derece | Düz alan filtreleme |
| 14 | NDVI | derived | [-1, 1] | Vejetasyon dışlama |
| 15 | BSI | derived | [-1, 1] | Bare soil index (pomza ↑) |
| 16 | Albedo | Liang 2001 | [0, 1] | Yüksek albedo (pomza özelliği) |

### 3.2 Adapter mantığı: `mean_replicate`

SSL4EO B3 backbone `conv1` katmanı `(64, 3, 7, 7)` ağırlık şeklinde. ARD 17 kanallı, doğrudan beslenemez. İki seçenek:

**Seçenek A — Random init ek kanallar:** İlk 3 kanal pretrained, kalan 14 kanal random. Sorun: random init gradient ilk birkaç epoch boyunca rastgele sinyalle backbone'u bozar.

**Seçenek B — Mean replicate (seçildi):** İlk 3 kanal pretrained ortalaması (`weight.mean(dim=1, keepdim=True)`) tüm 17 kanala kopyalanır. Sonra her kanal kendi gradient ile diferansiye olur. Bu yaklaşım, **EuroSAT ve BigEarthNet transfer çalışmalarında** standart (Helber et al. 2019).

```python
# code/p3/02_ssl4eo_pretrained.py: build_ssl4eo_unet()
old_conv = backbone.conv1  # (64, 3, 7, 7)
new_conv = nn.Conv2d(17, 64, kernel_size=7, stride=2, padding=3, bias=False)
mean_w = old_conv.weight.data.mean(dim=1, keepdim=True)  # (64, 1, 7, 7)
new_conv.weight.data = mean_w.repeat(1, 17, 1, 1)        # (64, 17, 7, 7)
backbone.conv1 = new_conv
```

### 3.3 Validasyon

Sentetik sanity (`05_synthetic_sanity.py`):
- Forward `(4, 17, 256, 256) → (4, 1, 256, 256)` ✅
- Loss 0.7573 (BCE+Dice combo, [0.5, 1.0] sağlıklı aralık)
- Gradient norm: min 1.35e-3, max 6.35e-1 (vanish/explode yok)
- Peak VRAM b=4: 0.89 GB H100 (A100/T4'te de rahat)

---

## 4. ROBERTS 2017 SPATIAL BLOK CV

### 4.1 Neden random k-fold yetmez

Random KFold uydu segmentasyonunda **mekansal sızıntı** üretir: tile A train'de, komşu tile A' val'da → val IoU yapay yüksek, gerçek genelleme test edilmez. Roberts et al. (2017) bu fenomeni kanıtladı, çözüm önerdi: **mekansal blok CV**.

### 4.2 Uygulama (P2 sözleşmesi)

P2 AOI'yı **5 mekansal bloğa** böler (Avanos için ~5km grid hücreleri). Her fold val seti **bütün bir blok** alır, train kalan 4 blok. Bu sayede train ve val tile'ları arasında **minimum 5km uzaklık** garanti edilir → komşuluk sızıntısı yok.

JSON şeması:
```json
{
  "fold_0": {"train": ["tile_0001.tif", ...], "val": ["tile_0123.tif", ...]},
  "fold_1": {...},
  ...
  "fold_4": {...}
}
```

### 4.3 Beklenen etki

Roberts'a göre random KFold ile spatial blok CV arasındaki IoU farkı genelde **+0.10 ila +0.15 (random şişirme)**. Bizim hedefimiz **gerçek genelleme** olduğu için spatial blok CV doğru tercih.

---

## 5. LOSS, METRIC, IGNORE INDEX

### 5.1 BCE + Dice combo (`code/p3/04_loss_metrics.py`)

```
loss = 0.5 * BCE(logits, target) + 0.5 * (1 - Dice(sigmoid(logits), target))
```

- **BCE:** Pixel-wise classification, sınıf dengesizliğinde recall'a meyilli.
- **Dice:** Set overlap, küçük pozitif sınıfta IoU'yu doğrudan hedefler.
- **0.5/0.5:** Pomza pozitif piksel oranı ~%2-5 (sınıf dengesiz). Dice komponenti küçük objeleri maskelemekten korur.

### 5.2 ignore_index=255

P2 mask'inde **WDPA Göreme Milli Parkı 1000m buffer** içi piksellere `255` yazılır. Loss bu pikselleri atlar — koruma alanlarında pomza tespiti **etik olarak istenmiyor** (Karar #11).

### 5.3 Streaming MetricAccumulator

Validation'da tüm probability ve target arrays bellekte tutulamaz (5K+ tile × 256² = 327M piksel). `MetricAccumulator`:
- `max_pixels=5_000_000` budget'la random subsample,
- F1-max threshold sweep aynı subsample üzerinden hesaplanır.

---

## 6. KARAR #6 — RAW PROBABILITY OUTPUT (KRİTİK)

### 6.1 Kural

P3'ün `predict_raw()` fonksiyonu **threshold uygulamaz, binarize etmez**:

```python
# code/p3/07_inference.py
def predict_raw(tile_tensor, model_path, device="cuda") -> np.ndarray:
    """Returns RAW probability map. NO threshold, NO binarization."""
    logits = model(tile_tensor)
    probs = torch.sigmoid(logits)  # [0, 1] continuous
    return probs.cpu().numpy()      # ← raw return, no .where(probs > 0.5)
```

### 6.2 Gerekçe

P4 (Spektral Mühendis) **score-level füzyon** yapacak (T4.12):
```
final_confidence = P3_raw_prob × P4_QI × (1 − P4_CI)
```
- **P3_raw_prob:** ML model olasılığı [0, 1]
- **P4_QI:** Quartz Index (Ninomiya 2002, ASTER-derived)
- **P4_CI:** Cloud Index

Eğer P3 threshold uygularsa fuze ham bilgisi kaybolur (bool × float = bilgi azalır). RAW olasılık, P4'ün quartz spektral imzasıyla **ağırlıklı çarpım** yapmasına izin verir.

### 6.3 P5 historical Landsat

P5 (T5.10) Landsat snapshot'larda **kendi threshold'unu** seçer (genelde 0.5, fold0'dan F1-max threshold da kullanılabilir). Bu P5'in seçimi, P3'ü etkilemez.

### 6.4 Streamlit demo

P5 dashboard'da kullanıcıya threshold slider sunulur. P3 RAW prob layer'ı arka planda hep [0, 1], kullanıcı slider'la binarize ettiği layer üstüne render eder.

---

## 7. F1-MAX THRESHOLD (KARAR #14)

`code/p3/10_threshold_tuning.py` validation set üzerinde threshold'u 0.05-0.95 arası 37 noktada tarar, **F1'i maksimize eden threshold**'u bulur:

```python
sweep = acc.threshold_sweep(thresholds=np.linspace(0.05, 0.95, 37))
# sweep["best_threshold"], sweep["best_f1"], sweep["best_iou"]
```

**Neden 0.5 değil?** Pomza sınıf dengesizliği nedeniyle (~%3 pozitif). 0.5 sigmoid çıktısı **recall'a baskı yapar**, F1 dengeli noktada oturmaz. Tipik pomza datasetlerinde best threshold 0.30-0.40 aralığında çıkar.

**Bu threshold P3 inference'inde uygulanmaz** (Karar #6) — yalnızca:
1. Validation metric raporu
2. P5 historical Landsat (P5 seçimi)
3. Streamlit demo binary layer

---

## 8. EXPORT (T3.13)

`code/p3/11_export_fp16.py` üç format üretir:

### 8.1 FP16 PT (`unet_pomza_fp16.pt`)
- State dict tüm float32 tensörler `.half()` ile FP16'ya cast.
- Boyut: ~65 MB (FP32 130 MB'in tam yarısı).
- Tüketici: P5 Streamlit live inference (CPU yarı hızında ama hâlâ kabul).

### 8.2 ONNX (`unet_pomza.onnx` + `.onnx.data`)
- Torch 2.10 yeni dynamo exporter ile (`torch.onnx.export`).
- **External data**: Graph 0.4 MB, weights 130 MB ayrı dosya. Demo deployment'ında **iki dosya birlikte** taşınmalı.
- Dynamic axes: `['batch', 17, 'h', 'w']` → P5 farklı tile boyutlarıyla çağırabilir.
- Opset 18 (17 talep, torch 2.10 18'e zorladı, kalite kaybı yok).

### 8.3 Manifest (`unet_pomza_manifest.json`)
```json
{
  "input_shape": [null, 17, 256, 256],
  "output_shape": [null, 1, 256, 256],
  "output_meaning": "RAW probability (sigmoid). KARAR #6: thresholdsuz.",
  "channel_order": ["S2_B2", "S2_B3", ..., "Albedo"],
  "consumers": ["P4 (T4.12 fuse_confidence)", "P5 (T5.8, T5.10)"]
}
```

### 8.4 PyTorch ↔ ONNX numerik doğrulama

Sentetik random input üzerinde:
- Logits abs diff: max 2.1e-3, mean 3.2e-4
- Probs abs diff: max 5.3e-4, mean 7.9e-5
- Platform farkı (cuDNN vs MKL conv toplam sırası), kabul.

---

## 9. PLAN B (FALLBACK STRATEJİSİ)

| Tetikleyici | Plan | Dosya |
|---|---|---|
| T3.5 yakınsamıyor (val IoU < 0.30) | RGB-only baseline (3 kanal) | `06_train.py --rgb-only` |
| RGB-only de yakınsamıyor | Sabins+BSI manuel threshold (model-free) | `12_fallback_threshold.py` |
| GPU memory yetmiyor | Batch 8 → 4, AMP zorunlu | `06_train.py --batch-size 4 --amp` |
| Colab T4 6h yetmiyor | Kaggle T4×2 paralel, veya 3-fold | `--folds 3` |
| ONNX export bozuk | FP16 PT yeterli (P5 PyTorch çalıştırıyor) | — |

`12_fallback_threshold.py` 17-bant ARD'den **albedo + SWIR ratio + BSI** sigmoid eşikleriyle direkt skor üretir. Sentetik testte pomza yarısı 0.561, background 0.000 (fark 0.561). Model gerektirmez, **emergency fallback**.

---

## 10. CRITICAL PATH ZAMAN ÇİZGİSİ

| Saat | Görev | Status |
|---|---|---|
| 0-6 | T3.1-T3.3: Ortam + SSL4EO + sentetik sanity | ✅ |
| 4-12 | T3.4 SLACK: 9 iş (review + sentetik testler + RUN-BLOCK doc) | ⏳ 8/9 |
| 12-15 | **T3.5 fine-tune (CRITICAL)** | 🔴 P1+P2 bekleniyor |
| 15-16 | T3.6 F1-max threshold | ⏳ |
| 16-17.5 | **T3.10 RAW inference (CRITICAL)** | ⏳ |
| 17.5-18.5 | T3.11 Grad-CAM | ⏳ |
| 18-20 | T3.13 Export (FP16 + ONNX) | ⏳ (kuru test ✅) |
| 20-24 | T3.14 KOD FREEZE + dry-run | ⏳ |

---

## 11. BAĞIMLILIK MATRİSİ

### Sana gelen
| Saat | Girdi | Sağlayıcı |
|---|---|---|
| 8 | data/ard/full_ard_20m.tif | P1 T1.7 |
| 10 | data/tiles/*.tif | P1 T1.8 |
| 11 | data/manifest.json (ideal: mean/std) | P1 T1.9 |
| 11 | data/labels/blok_cv_split.json | P2 T2.6 |
| **13** | **data/labels/full_mask.tif** | **P2 T2.8 (CRITICAL)** |

### Senden çıkan
| Saat | Çıktı | Tüketici |
|---|---|---|
| **17.5** | **predict_raw() API** | **P4 T4.12 + P5 T5.10** |
| 18.5 | models/unet_pomza_ssl4eo.pt | P4, P5 |
| 19 | models/unet_pomza_fp16.pt + .onnx | demo |
| 16 | reports/metrics_5fold.json | demo slide |

---

## 12. AKADEMIK REFERANSLAR

1. **Wang, Y. et al. (2023).** "SSL4EO-S12: A Large-Scale Multi-Modal, Multi-Temporal Dataset for Self-Supervised Learning in Earth Observation." *arXiv:2211.07044*.
2. **Roberts, D. R. et al. (2017).** "Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure." *Ecography 40(8): 913-929*.
3. **Sabins, F. F. (1999).** "Remote sensing for mineral exploration." *Ore Geology Reviews 14: 157-183*.
4. **Liang, S. (2001).** "Narrowband to broadband conversions of land surface albedo." *Remote Sensing of Environment 76: 213-238*.
5. **van der Meer, F. D. et al. (2014).** "Multi- and hyperspectral geologic remote sensing: A review." *International Journal of Applied Earth Observation 14: 112-128*.
6. **Ninomiya, Y. (2002).** "Mapping quartz, carbonate minerals, and mafic-ultramafic rocks using ASTER thermal infrared data." *SPIE Proceedings 4710*.
7. **Helber, P. et al. (2019).** "EuroSAT: A novel dataset and deep learning benchmark for land use and land cover classification." *IEEE JSTARS 12(7): 2217-2226*.
8. **Roy, D. P. et al. (2016).** "Characterization of Landsat-7 to Landsat-8 reflective wavelength and normalized difference vegetation index continuity." *Remote Sensing of Environment 185: 57-70*.

---

## 13. KARARLAR ÖZETİ

| # | Karar | Gerekçe |
|---|---|---|
| K#6 | RAW probability output, threshold YASAK | P4 score-level füzyonu yapacak |
| K#10 | Spatial 5-fold blok CV (Roberts 2017) | Random KFold mekansal sızıntı yapar |
| K#11 | WDPA Göreme buffer ignore (255) | Etik koruma alanları, loss'tan dışla |
| K#13 | AMP FP16 train + export | Hız 1.5-2x, A100/H100'de güvenli |
| K#14 | F1-max threshold (sabit 0.5 değil) | Sınıf dengesizliği, F1 dengeli noktada |
