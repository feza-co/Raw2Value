# P3 — ML Mühendisi Briefing

> **Hoş geldin.** Sen Modül A'nın **AI beynisin**. SSL4EO-S12 pretrained backbone'u 13→17 kanala genişletip Roberts 2017 spatial 5-fold blok CV ile fine-tune edeceksin. Çıktın **RAW olasılık** (Karar #6) — threshold uygulamayacaksın, füzyonu P4 yapacak.

---

## 1. ROLÜN ÖZETİ

**Sen P3 — ML Mühendisi'sin.** İki kritik teslimatın var:
1. **T3.5 — U-Net fine-tune** (saat 15) — `models/unet_pomza_ssl4eo.pt` (CRITICAL PATH)
2. **T3.10 — RAW inference fonksiyonu** (saat 17.5) — `code/p3/07_inference.py::predict_raw()` (CRITICAL PATH)

**6 saat slack zamanın var (saat 6-12)** — P1 ARD ve P2 etiket beklerken `inference.py` iskeleti ve Grad-CAM utility'leri hazırlarsın. Slack zamanı **boş geçmez**.

---

## 2. CRITICAL PATH SORUMLULUKLARIN

| Görev | Saat | CRITICAL? | Süre |
|---|---|---|---|
| T3.5 SSL4EO-S12 + 5-fold blok CV fine-tune | 12-15 | ✅ | 3h (A100) / 6h (T4) |
| T3.10 RAW inference fn | 16.5-17.5 | ✅ | 1h |

**v2 KRİTİK NOT:** Çıktın **RAW olasılık** [0,1], threshold/binarize YASAK. P4 fuse_confidence yapacak.

---

## 3. HESAP KURULUMUN (saat 0, ~15 dk)

### 3.1 GPU erişimi (kritik — birini seç)

**Seçenek A: Colab Pro ($9.99/ay) — Önerilen**
- https://colab.research.google.com/signup
- Pro abonelik: A100 erişim (kısıtlı), V100/T4 garanti
- Drive entegrasyonu kolay

**Seçenek B: Kaggle (ücretsiz, haftalık 30h GPU)**
- https://www.kaggle.com → kayıt
- Verify phone (haftalık 30h GPU için zorunlu)
- T4 x2 erişim, 16 GB GPU memory

**Seçenek C: Vast.ai veya Lambda Labs ($)**
- Pahalı ama A100 garanti

**Seçenek D: Yerel GPU (varsa)**
- RTX 3090 / 4090 ile 24h yapılabilir
- 5-fold CV her fold ~30dk (3090'da)

### 3.2 Opsiyonel: Weights & Biases
- https://wandb.ai → kayıt (ücretsiz)
- API key al → `code/p3/06_train.py` `--wandb` flag'i ile kullanır

### 3.3 SSL4EO-S12 weights
- Otomatik HuggingFace'den indirilir (`code/p3/02_ssl4eo_pretrained.py`)
- Repo: `wangyi111/SSL4EO-S12` (MoCo ResNet-50)
- Boyut: ~100 MB

### 3.4 Yerel kurulum (test için)
```bash
python -m venv venv
source venv/bin/activate
pip install -r code/p3/requirements.txt
```

---

## 4. KENDİ LLM'İNİ KUR (saat 0, ~10 dk)

```bash
cd Pomzadoya
claude --model claude-opus-4-7
```

**İlk mesaj:**

```
Sen .claude/agents/p3-ml-muhendisi.md tanımındaki P3 — ML Mühendisi rolündesin.
Tek doğru kaynağın: Modul_A_Critical_Path_Dependency_v2.md.

ŞİMDİKİ DURUM:
- Saat 0/24
- Ben P3 sorumlusu ekip üyesiyim
- handoff/P3_BRIEFING.md okudum
- Colab Pro / Kaggle GPU hesabım hazır
- Yerel Python venv hazır

KRİTİK HATIRLATMA:
- Çıktım RAW olasılık (Karar #6) — threshold YASAK
- 6 saat slack (6-12) inference iskelet + Grad-CAM yazmak için
- T3.5 fine-tune saat 12'de başlar, P2 raster mask saat 13'e bağımlı (1h slack toleransı)

YAPACAKLARIN:
1. agent_outputs/p3_status.md ve .claude/state/orchestrator_log.md oku
2. code/p3/07_inference.py'yi gözden geçir — predict_raw() fonksiyonu doğru mu, threshold YOK mu?
3. agent_outputs/p3_t3_1_runblock.md (GPU test) ile başla
4. Saat 6-12 slack zamanında inference iskeleti + Grad-CAM utility'lerini bana yazdırmaya hazır ol
5. T3.5 fine-tune RUN-BLOCK'unu Colab Pro/Kaggle'a uyarlı hazırla, ben Drive mount + dataset yükleme ile başlayacağım

T3.1'den başla.
```

---

## 5. SAATLİK GÖREV TABLOSU

| Saat | Görev | Tür | Süre |
|---|---|---|---|
| 0:00-0:15 | Hesap kurulumu (Colab Pro/Kaggle) | 👤 | 15dk |
| 0:15-0:30 | LLM kurulumu | 👤 | 15dk |
| **0:30-2:00** | **T3.1 GPU testi (Colab notebook `01_env_setup.ipynb`)** | 👤 Run + ⚙️ | 1.5h |
| **2:00-4:00** | **T3.2 SSL4EO-S12 yükleme + 13→17 multi-channel adapter** | ⚙️ | 2h |
| **4:00-6:00** | **T3.3 Sentetik sanity check (random tensor → forward → backward)** | ⚙️ | 2h |
| **6:00-12:00** | **🟡 T3.4 SLACK — inference iskelet + Grad-CAM utility (BOŞ DURMA)** | 🧠 ⚙️ | 6h |
| **12:00-15:00** | **🔴 T3.5 Fine-tune (CRITICAL, 5-fold blok CV)** | 👤 Run + ⚙️ asenkron | 3h |
| 15:00-16:00 | T3.6 F1-max threshold tuning | ⚙️ | 1h |
| 15:00-16:30 | T3.7 Ablation study (5 konfig — paralel) | ⚙️ | 1.5h |
| **16:30-17:30** | **🔴 T3.10 RAW inference fn (CRITICAL)** | ⚙️ | 1h |
| 17:30-18:30 | T3.11 Grad-CAM görselleştirme | ⚙️ | 1h |
| 18:30-20:00 | T3.12 P2 ile hata analizi (gerekirse 2. tur fine-tune) | 👥 P2 | 1.5h |
| 18:00-20:00 | T3.13 Model export (FP32 + FP16 + ONNX), P4/P5 entegrasyon | ⚙️ + 👥 | 2h |
| 18:00-20:00 | Entegrasyon | 👥 | 2h |
| 20:00 | **KOD FREEZE** | 🛑 | — |
| 20:00-24:00 | T3.14 KOD FREEZE + dry-run desteği | ⚙️ + 👥 | 4h |

---

## 6. T3.4 SLACK ZAMANI — 6 SAAT (saat 6-12)

P1 saat 8'de Full ARD, P2 saat 13'te raster mask teslim eder. Sen saat 6'dan 12'ye **boş kalırsın** (T3.3 sanity check bitti, gerçek veri yok). Bu zamanı **kullanılmazsa heba olur**.

LLM'inle şu işleri yap:

1. **inference.py iskelet revize** (`code/p3/07_inference.py` zaten yazıldı, gözden geçir — predict_raw + sliding window cosine-blend mantığı doğru mu)
2. **Grad-CAM utility** (`code/p3/08_gradcam.py` zaten yazıldı, target layer doğru mu — ResNet-50 son conv'u: `model.encoder.layer4`)
3. **Ablation runner** (`code/p3/09_ablation.py` 5 config — full / RGB-only / no-S1 / no-DEM / no-pretrained)
4. **Threshold tuning script test** (sentetik probability + label ile çalışıyor mu)
5. **W&B sweep config** (opsiyonel — hyperparameter exploration)
6. **Plan B fallback** (`code/p3/12_fallback_threshold.py` — Sabins/BSI manuel threshold, model-free baseline)
7. **Documentation:** `reports/p3_architecture.md` — model arch, multi-channel adapter mantığı, neden SSL4EO-S12

LLM'e şu prompt:
```
T3.4 slack başladı (saat 6). T3.5'e kadar 6 saatim var, P1 ve P2 verisi geliyor.
Sırayla şunları yap:
1. code/p3/07_inference.py'yi gözden geçir, predict_raw API'sını doğrula (threshold YOK kontrolü)
2. code/p3/08_gradcam.py target layer'ı SSL4EO-S12 ResNet-50'ye uyarla
3. code/p3/09_ablation.py 5 config çalışıyor mu, sentetik dataset ile test et
4. reports/p3_architecture.md yaz — model arch + adapter mantığı + neden bu seçim
5. T3.5 RUN-BLOCK'unu A100 ve T4 için ayrı tahmin sürelerle hazırla

Her adımda DELIVER üret, ben tamam dedikçe sıradakine geç.
```

---

## 7. T3.5 FINE-TUNE — KRİTİK ANI (saat 12-15)

### Önkoşul (saat 12'de)
- ✅ `data/ard/full_ard_20m.tif` (P1 saat 8)
- ✅ `data/tiles/` (P1 saat 10)
- ✅ `data/labels/full_mask.tif` (P2 saat 13 — 1h tolerans var)
- ✅ `data/labels/blok_cv_split.json` (P2 saat 11)

P2 saat 13'te `full_mask.tif` teslim ederse, sen saat 12'de **DataLoader sanity check** yapabilirsin (sentetik mask üret, T2.8 gelene kadar 1h dolu olur). Saat 13'te gerçek mask geldiğinde fine-tune başlar.

### Fine-tune notebook RUN-BLOCK
LLM şu şablonu üretir:
```
RUN-BLOCK [T3.5]
Hedef: Colab Pro A100 / Kaggle T4 / Yerel CUDA

1. Drive mount (Colab) veya Kaggle dataset upload
2. Path kontrolü: /content/drive/MyDrive/Pomzadoya/data/ ard, labels, tiles
3. SSL4EO-S12 weights (HuggingFace download)
4. Multi-channel adapter (13→17, ortalama replikasyon)
5. 5-fold blok CV training loop:
   for fold in 0..4:
     - load split JSON, train_tiles + val_tiles
     - DataLoader + augmentation
     - AdamW(lr=1e-4) + CosineLR + grad_clip=1.0 + AMP
     - 30-50 epoch, early stop val IoU plateau
     - save checkpoint /models/unet_pomza_fold{fold}.pt
6. 5-fold ortalama metrik raporu
7. Final ensemble checkpoint /models/unet_pomza_ssl4eo.pt
ETA: 3h (A100), 6h (T4 — Plan B'ye düşülebilir)
```

### VERIFY-BLOCK (saat 15'te yapıştırılacak)
- 5 fold için son 5 epoch loss/IoU
- 5 fold val IoU mean ± std
- Checkpoint dosya boyutu (`ls -lh`)
- W&B grafik (varsa)

### Sanity threshold
- Mean val IoU > 0.45
- Std < 0.08 (folds tutarlı)
- Yakınsamadıysa Plan B (RGB-only veya threshold fallback)

### Asenkron protokol
T3.5 koşarken (3-6h) sen LLM'le **paralel** iş yap:
- T3.6 threshold tuning script'ini fine-tune sonu hazır olsun (her fold için ayrı F1-max curve)
- T3.7 ablation: T3.5 sonrası ekstra 5 config çalıştırılır, paralel başlatma planı
- T3.10 RAW inference fonksiyonunu gerçek checkpoint ile test et (önceden sentetikti)

---

## 8. T3.10 RAW INFERENCE — KRİTİK API (saat 16.5-17.5)

P4 ve P5 senin `predict_raw()` fonksiyonunu kullanacak. **API contract:**

```python
def predict_raw(
    tile_tensor: torch.Tensor,         # shape: (B, 17, H, W), float32, normalized
    model_path: str = "models/unet_pomza_ssl4eo.pt",
    device: str = "cuda",
    use_amp: bool = True
) -> np.ndarray:                       # shape: (B, H, W), float32, [0, 1]
    """
    Returns RAW probability map. NO threshold, NO binarization.
    P4 fuse_confidence will multiply with QI × (1-CI).
    P5 historical (Landsat) will apply own threshold (default 0.5).
    """
```

Ek fonksiyonlar:
```python
def predict_raster(
    raster_path: str,                  # 17-kanal ARD
    output_path: str,                  # raw_prob.tif çıkışı
    tile_size: int = 256,
    overlap: int = 32,                 # cosine-blend
) -> None: ...

def predict_landsat_snapshot(
    landsat_path: str,                 # Roy 2016 harmonize
    output_path: str,
    threshold: float = 0.5,            # historical için sabit
) -> None: ...
```

VERIFY: P4 ve P5 RUN-BLOCK'larında `from code.p3.07_inference import predict_raw` import edip test eder.

---

## 9. KIM SANA NE TESLİM EDİYOR / SEN KİME NE TESLİM EDİYORSUN

### Sana gelen
| Saat | Girdi | Sağlayıcı | Kullanım |
|---|---|---|---|
| 8 | `data/ard/full_ard_20m.tif` | P1 | Fine-tune girdi tensörü |
| 10 | `data/tiles/` | P1 | DataLoader |
| 11 | `data/manifest.json` | P1 | Bant sıra/normalizasyon |
| 7 | `data/labels/positive_polygons.gpkg` | P2 | T3.4 slack'te erken sanity |
| 11 | `data/labels/blok_cv_split.json` | P2 | T3.5 5-fold CV |
| **13** | **`data/labels/full_mask.tif`** | **P2** | **T3.5 asıl etiket (CRITICAL)** |

### Senden çıkan
| Saat | Çıktı | Tüketici | Kullanım |
|---|---|---|---|
| **17.5** | **`code/p3/07_inference.py::predict_raw()`** | **P4, P5** | **T4.12 füzyon, T5.10 historical (CRITICAL)** |
| 18.5 | `models/unet_pomza_ssl4eo.pt` | P4, P5 | Streamlit canlı inference + füzyon |
| 19 | `models/unet_pomza_fp16.pt` | KOD FREEZE | Demo speed |
| 16 | `reports/metrics_5fold.json` | Demo | Sunum slaydı |

---

## 10. PLAN B'LERİN

| Tetikleyici | Plan B | Onay |
|---|---|---|
| T3.5 yakınsamıyor (val IoU < 0.30) | Plan B-1: S2 RGB-only baseline (3 kanal) | Grup chat |
| T3.5 yakınsamıyor (devam) | Plan B-2: `code/p3/12_fallback_threshold.py` Sabins+BSI manuel threshold | Eskalasyon |
| Colab T4'te 6h yetmiyor | Kaggle T4×2 paralel fold (5 fold yerine 3 fold + ensemble), VEYA Vast.ai A100 1h | Grup chat |
| GPU memory yetmiyor | Batch size düşür (16→8), gradient accumulation 2 step | Otomatik |
| T3.10 saat 17.5'te bitmedi | P5 historical Landsat'ta manuel threshold + P4 füzyon sentetik raw input | Eskalasyon |
| SSL4EO-S12 indirilmedi | ImageNet ResNet-50 fallback (akademik kalite düşer ama çalışır) | Otomatik |

---

## 11. GITHUB WORKFLOW

```bash
git checkout -b p3-t3.x-<kısa-ad>

# Model checkpoint'leri Git LFS:
git lfs track "models/*.pt"
git lfs track "models/*.onnx"

git add code/p3/* agent_outputs/p3_* reports/metrics*.json
git add models/unet_pomza_ssl4eo.pt  # LFS ile

git commit -m "[P3] T3.5 SSL4EO-S12 fine-tune (5-fold blok CV)

DELIVER: models/unet_pomza_ssl4eo.pt (mean val IoU 0.52 ± 0.06)
Bağımlı: P4 T4.12 + P5 T5.10 inference fn bekliyor"

git push origin p3-t3.x-<kısa-ad>
```

---

## 12. KENDİNİ KONTROL — saat 6, 12, 15, 17.5'te

### Saat 6 ✓ — slack başlangıcı
- [ ] T3.1, T3.2, T3.3 tamam
- [ ] SSL4EO-S12 weights yüklendi, 13→17 adapter ünite test geçti
- [ ] Sentetik DataLoader + forward + backward pass çalışıyor

### Saat 12 ✓ — fine-tune öncesi
- [ ] T3.4 slack işleri tamam (inference.py, gradcam, ablation, fallback hepsi gözden geçirildi)
- [ ] DataLoader gerçek ARD ile sanity check tamam
- [ ] T3.5 RUN-BLOCK Colab/Kaggle'a uyarlı hazır
- [ ] P2'den raster mask geldi mi? (saat 13 normal, 12'de yoksa orchestrator'a sor)

### Saat 15 ✓ **CRITICAL**
- [ ] `models/unet_pomza_ssl4eo.pt` exists
- [ ] 5-fold val IoU mean ± std rapor edildi
- [ ] Sanity: mean > 0.45, std < 0.08

### Saat 17.5 ✓ **CRITICAL**
- [ ] `code/p3/07_inference.py::predict_raw()` çalışıyor (gerçek checkpoint ile)
- [ ] P4 ve P5'e import edip test ettiklerini doğrula

---

## 13. DOSYA REFERANSLARIN

| Ne | Nerede |
|---|---|
| Rol tanımı | `.claude/agents/p3-ml-muhendisi.md` |
| Görev detay | `Modul_A_Critical_Path_Dependency_v2.md` § P3 |
| Kodlar | `code/p3/` (13 dosya hazır) |
| Inference API | `code/p3/07_inference.py` (RAW olasılık API) |
| RUN-BLOCK'lar | `agent_outputs/p3_t3_*_runblock.md` |
| Statü | `agent_outputs/p3_status.md` |
| Architecture doc | `reports/p3_architecture.md` (slack'te yazacaksın) |

---

## 14. SIK SORULAR

**S: SSL4EO-S12 13 kanal, biz 17 kanal — fark ne?**
C: SSL4EO-S12 sadece S2 (13 bant). Biz S1 VV/VH + DEM + slope eklediğimizde 17. Adapter: ortalama replikasyon — pretrained 13 kanal ortalamasını ek 4 kanala kopyala, fine-tune'da öğrenir.

**S: 5-fold blok CV neden randoma tercih?**
C: P2 dosyasında detayı var. Mekânsal sızıntı → IoU yapay yüksek. Roberts 2017 metodu gerçek genelleme.

**S: BCE+Dice kombinasyon ağırlığı?**
C: 0.5 BCE + 0.5 Dice. Pomza için class imbalance var (negative çok), Dice yardımcı.

**S: ignore_index=255 nasıl çalışır?**
C: WDPA buffer içi pikseller mask'te 255 — loss bu pikselleri atlar (`ignore_index=255` BCE'ye geçer).

**S: F1-max threshold ne demek?**
C: Validation set üzerinde threshold'u 0.1-0.9 sweep et, F1 maximum yapan threshold seç. Genelde 0.5 değil, dengesiz class'larda 0.3-0.4.

**S: ONNX export gerekli mi?**
C: Opsiyonel. Streamlit zaten PyTorch çalıştırabiliyor (P5 dashboard'da). ONNX hızlandırma için.

---

## 15. SENİN BAŞARI KRİTERLERİN

1. ✅ T3.5 saat 15'te bitti, mean val IoU > 0.45
2. ✅ T3.10 saat 17.5'te `predict_raw()` API çalışıyor
3. ✅ P4 fuse_confidence ve P5 historical inference seninle entegre çalıştı
4. ✅ Plan B'ye gerek kalmadı (yakınsama OK, GPU yetti)

---

## 16. STRATEJİ TÜYÜLERİ

- **W&B kullanırsan** real-time dashboard'dan eğitim ilerlemesini gör. Yakınsamayan run'ı erken kes (3 saat boşa harcamak yerine 30dk'da Plan B).
- **Mixed precision (AMP)** çok yardımcı, A100'da batch size 32→64'e çıkar, hız 1.5x.
- **Gradient accumulation** GPU memory yetmediğinde işe yarar (effective batch = N × accumulation_steps).
- **Early stopping** val IoU plateau'sunda (5 epoch sabit) — boşuna eğitme.
- **Folds paralel** çalıştırılabilir (Kaggle T4×2 ile 2 fold paralel, 30dk×3 = 1.5h yerine 1h).

---

**Saat 0 başladı sayılır. İlk eylemin: 3.1 GPU hesap kurulumu (Colab Pro veya Kaggle). Bittiğinde grup chat'e "P3 GPU hazır" yaz.**
