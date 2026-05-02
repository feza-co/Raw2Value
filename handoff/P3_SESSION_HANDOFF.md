# P3 — Oturum Devir Brifingi (2026-05-01, saat ~5/24)

> Bu doküman P3 rolü için açılan **yeni bir Claude Code oturumuna** projeyi sıfırdan tanıtır. İçeriği yeni LLM'e ilk mesaj olarak yapıştır.

---

## SEN P3 — ML MÜHENDİSİ ROLÜNDESİN

**Proje:** Pomzadoya hackathon, Modül A. 24 saatlik pencerede Avanos/Nevşehir bölgesinde uydu tabanlı pomza (pumice) madencilik tespiti. 5 kişilik ekip: P1 (veri), P2 (etiketleme), **P3 (ben — ML)**, P4 (spektral), P5 (change detection + viz).

**Tek doğru kaynak:** `Modul_A_Critical_Path_Dependency_v2.md`

**P3 görev tanımı:** `.claude/agents/p3-ml-muhendisi.md`

**Briefing dosyası:** `handoff/P3_BRIEFING.md`

**P3 statü:** `agent_outputs/p3_status.md` (her iş bitince güncellenir)

---

## ŞU ANKİ DURUM (saat 4-5/24)

### Tamamlananlar
- ✅ **T3.1** Colab Pro H100/A100 setup, torch 2.10, smoke OK, peak VRAM b=4: 0.89 GB
- ✅ **T3.2** SSL4EO-S12 yükleme + adapter (Missing=0, Unexpected=324, 32.57M param)
- ✅ **T3.3** Sentetik sanity check (loss=0.7573, grad finite, NaN-free)
- ✅ **T3.4 SLACK iş 1** — `predict_raw()` API review + sentetik test (threshold yok doğrulandı, GeoTIFF metadata OK)
- ✅ **T3.4 SLACK iş 2** — Grad-CAM API (encoder.layer4 + RGB overlay PNG)
- ✅ **T3.4 SLACK iş 3** — Ablation CONFIGS + train CLI uyum doğrulama
- ✅ **T3.4 SLACK iş 7** — 06_train.py end-to-end smoke test (sentetik 16-tile mini-dataset + 1 fold + 1 epoch, 1.7s H100'de)

### Devam Eden — T3.4 SLACK (saat 4-12, 8h)
- ⏳ **İş 4 SIRADA**: 10_threshold_tuning.py sentetik prob+label test
- ⏳ İş 5: Plan B fallback (12_fallback_threshold.py — Sabins+BSI manuel threshold)
- ⏳ İş 6: T3.5 RUN-BLOCK hazırlığı (saat 12'de tek tıkla başlatma için)
- ⏳ İş 8: FP16 + ONNX export kuru test (11_export_fp16.py)
- ⏳ İş 9 (opsiyonel): reports/p3_architecture.md
- ⏳ İş 10 (ertelendi): predict_landsat_snapshot band_mapping (P5 ile sözleşme gerekli)

### Bekleyenler (kritik patika)
- 🔴 **T3.5** Fine-tune (saat 12-15) — P2 mask (saat 13!) gelmeden başlayamaz
- 🔴 **T3.10** RAW inference fn (saat 16.5-17.5) — P4 + P5 buna bağımlı

---

## ÖNEMLİ TEKNİK KARARLAR (BU OTURUMDA ALINDI)

1. **HuggingFace `wangyi111/SSL4EO-S12` reposunda B13 ResNet-50 MoCo bulunmuyor** — sadece ViT MAE versiyonları var. Bunun yerine **B3 ResNet-50 MoCo** (3-kanal Sentinel-2 RGB) kullanıldı.
2. **Adapter 13→17 yerine 3→17** mean_replicate olarak güncellendi.
3. **smp 0.5.0 + torch 2.10** kombinasyonunda `load_state_dict` None döndürüyor → manuel diff hesaplama fallback eklendi.
4. **torch.cuda.amp deprecated** → `torch.amp.GradScaler('cuda', ...)` ve `torch.amp.autocast('cuda', ...)` ile değiştirildi.

## BU OTURUMDA DEĞİŞTİRİLEN DOSYALAR

- `code/p3/02_ssl4eo_pretrained.py` (B3 default, DEFAULT_SSL4EO_CHANNELS=3, load_state_dict None handling)
- `code/p3/06_train.py` (torch.amp migration)
- `agent_outputs/p3_status.md`, `p3_t3_1_runblock.md`, `p3_t3_2_runblock.md`, `p3_t3_3_runblock.md` (DELIVER + status güncellemeleri)

---

## COLAB DURUMU

- **Repo:** `feza-co/CAVE2CLOUD` (private, PAT ile clone'landı)
- **Branch:** `p3-tuna`
- **Path:** `/content/Pomzadoya`
- **Drive:** `/content/drive/MyDrive/pomzadoya/`
- **SSL4EO weights:** `/content/drive/MyDrive/pomzadoya/models/pretrained/models--wangyi111--SSL4EO-S12/snapshots/75c72195d35201dc1fb210818993518c25da566b/B3_rn50_moco_0099_full_ckpt.pth`
- **Sentetik mini-dataset:** `/tmp/synth_dataset/` (16 tile, 1024×1024 mask, 1 fold split, manifest)
- **Aktif notebook'ta `model` değişkeni hâlâ yüklü** (kullanıcı yeni hücre açmaya devam ediyor)

---

## P3 KRİTİK BAĞIMLILIKLAR

### Bekleyenler (P1 + P2'den)
| Saat | Ne | Kimden | Yokluğunda |
|:-:|---|:-:|---|
| 8 | data/ard/full_ard_20m.tif (17-kanal ARD) | P1 (T1.7) | Sentetik ile devam |
| 10 | data/tiles/ (256×256) | P1 (T1.8) | DataLoader gerçek sanity yapamaz |
| 11 | data/manifest.json | P1 (T1.9) | DataModule init bloklu |
| 11 | data/labels/blok_cv_split.json | P2 (T2.6) | T3.5 başlatamaz |
| **13** ⚠️ | data/labels/full_mask.tif (CRITICAL) | P2 (T2.8) | T3.5 fine-tune **bloklu** |

### P3 Çıktıları (P4 + P5'in beklediği)
| Saat | Çıktı | Tüketici |
|:-:|---|:-:|
| **17.5** ⚠️ | predict_raw() API | **P4 T4.12 + P5 T5.10** (CRITICAL) |
| 18.5 | models/unet_pomza_ssl4eo.pt | P4, P5 |
| 19 | models/unet_pomza_fp16.pt + .onnx | demo |
| 16 | reports/metrics_5fold.json | demo slide |

---

## KARAR #6 (KIRMIZI ÇİZGİ)

P3 çıktısı **RAW olasılık** [0,1]. Threshold/binarize **YASAK**. Füzyonu P4 yapacak:
```
final_confidence = P3_raw_prob × P4_QI × (1 - P4_CI)
```

`code/p3/07_inference.py::predict_raw()` bu kuralı uygular — sigmoid sonrası direkt return, hiçbir threshold yok.

---

## SIRADAKİ İŞ — İş 4: Threshold Tuning Sentetik Test

`code/p3/10_threshold_tuning.py` F1-max threshold sweep yapar (T3.6). Sentetik prob + label ile çalıştığını doğrulayacağız.

Akış:
1. `10_threshold_tuning.py`'ı oku
2. Sentetik mini-dataset checkpoint'i (`/tmp/synth_dataset/output/unet_pomza_ssl4eo_fold0.pt`) ile threshold sweep koş
3. Çıktının F1-max threshold + curve içerdiğini doğrula
4. Status'u ✅ olarak güncelle, İş 5'e geç

---

## SLACK FELSEFESİ

Saat 4-12 arası 8h slack. P1/P2 verisi yok, ana T3.5 görevi başlayamaz. Boş kalmak yerine:
- Saat 17.5'teki `predict_raw()` API kalitesini sağlama al (saat 12'de Plan B'ye geçecek vakit yok)
- Saat 12'deki fine-tune'a tek tıkla geçiş için RUN-BLOCK ve sentetik test yap
- Saat 19'daki KOD FREEZE'de FP16 sürpriz olmasın diye export'u önceden test et

**Boş kalmak hackathon'un en pahalı hatasıdır.**

---

## YENİ OTURUMA İLK MESAJ ŞABLONU

```
Sen .claude/agents/p3-ml-muhendisi.md tanımındaki P3 — ML Mühendisi rolündesin.
Tek doğru kaynağın: Modul_A_Critical_Path_Dependency_v2.md.

Branch: p3-tuna (feza-co/CAVE2CLOUD)

Önce şunları oku:
1. handoff/P3_SESSION_HANDOFF.md (BU dosya — saat 4-5'teki tam durum)
2. agent_outputs/p3_status.md (statü tablosu)
3. handoff/P3_BRIEFING.md (rol detay)

Devraldığım iş: T3.4 SLACK İş 4 (10_threshold_tuning.py sentetik test).

Auto mode aktif. Kullanıcı Colab Pro H100/A100'de aynı notebook'tan
devam ediyor (model değişkeni hâlâ yüklü).

İş 4 RUN-BLOCK'unu üret, çıktıyı bekle.
```
