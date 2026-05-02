# P3 — ML Muhendisi DURUM

_Modul A v2 — Pomzadoya hackathon, 24h penceresi_
_Son guncelleme: 2026-05-01_

## Saat 0-6 (T3.1, T3.2, T3.3)

| Görev | Durum | Cikti |
|---|---|---|
| T3.1 Ortam + GPU test | ✅ TAMAM (Colab Pro A100/H100) | torch 2.10, peak VRAM b=4: 0.89 GB |
| T3.2 SSL4EO-S12 + 3->17 adapter | ✅ TAMAM (B3 RN50 MoCo, 32.57M param) | Missing=0, Unexpected=324 (momentum+queue), forward OK |
| T3.3 DataModule + Loss + sanity | ✅ SENTETIK TAMAM (gercek P1/P2 verisi sonrasi DataLoader sanity yapilacak) | Loss 0.7573, grad finite, peak VRAM 0.89 GB |

## KRITIK KESIF (2026-05-02 ~saat 21, slack icinde)

P1 manifest.json (Drive'da hazir) P3 sozlesmesinden FARKLI:
- **Bant sayisi (17) UYUMLU** ama **bant sirasi tamamen farkli**.
- P1 yapisi: 10 S2 (B2-B8, B8A, B11, B12) + 2 S1 (VV/VH dB) + 2 topografya (DEM, slope) + **3 derived (NDVI, BSI, Albedo)**.
- P3 eski default 13 S2 + 2 S1 + 2 topografya bekliyordu — yanlis kanala mean/std uyguluyor olacakti.
- Aksiyon: `code/p3/03_datamodule.py` DEFAULT_MEAN/STD + `code/p3/11_export_fp16.py` channel_order GUNCELLENDI.
- Mean/std degerleri PLACEHOLDER — T3.5 oncesi (saat ~11) P1 ARD'sinden ampirik hesap + manifest'e yaz + `--manifest-json` ile override.
- P1 manifest'inde mean/std YOK; P1'e manifest'e ampirik istatistik ekleme istegi gonderilmeli.

## Saat 4-12 (T3.4 — 8h slack) — DEVAM EDIYOR

### Slack progress
| Is | Durum | Cikti |
|---|:-:|---|
| Is 1: predict_raw API review + sentetik test | ✅ TAMAM | TEST 1+2+3 gecti, threshold yok dogrulandi (64783 unique vals), GeoTIFF metadata OK |
| Is 2: Grad-CAM target layer + sentetik test | ✅ API SAGLAM | encoder.layer4 erisilebilir, GradCAM lib uyumlu, RGB overlay+PNG OK. Gercek CAM heatmap T3.11'de fine-tune sonrasi test edilecek (sentetik random veri = ReLU sonrasi 0, beklenen). |
| Is 3: Ablation 5-config dry-run | ✅ KISMI | CONFIGS yapisi + 06_train.py CLI uyumu OK; tam 5-config koşumu T3.7'de gercek datayla yapilacak |
| Is 4: Threshold tuning sentetik test | ✅ TAMAM | CLI end-to-end OK. n_pixel=262144 (4 val tile), 37-nokta sweep, best_thr=0.325 best_F1=0.059 best_IoU=0.030 (sentetik random+1ep, beklenen). JSON 10-anahtar semasi + Recall↓/Precision-floor monotonisitesi dogrulandi. |
| Is 5: Plan B fallback test | ✅ TAMAM | 12_fallback_threshold.py CLI end-to-end OK. Sentetik 17-band ARD (yari pomza/yari bg) -> bolgesel skor: pomza=0.561, bg=0.000, fark=0.561. Albedo+SWIR+BSI sigmoid AND mantigi saglikli. P3_OUTPUT=RAW_PROBABILITY_FALLBACK tag dogrulandi. |
| Is 6: T3.5 RUN-BLOCK hazirligi | ✅ TAMAM | agent_outputs/p3_t3_5_runblock.md uretildi. Onkosul kontrol + egitim hucresi (30ep, b=8, --amp, --seed 42) + async monitor + verify-block + Plan B trigger esikleri. Saat ~12-13'te P1+P2 dosyalari Drive'a inince tek tikla baslatilir. |
| Is 7: 06_train.py parametre review | ✅ TAMAM | Sentetik mini-dataset (16 tile, 1024x1024 mask) + 1-fold 1-epoch smoke test gecti (1.7s, H100). AMP deprecation patch'lendi (torch.amp.GradScaler/autocast). Train loop+DataLoader+SSL4EO+Adapter+AMP+threshold sweep+ckpt save hepsi calisti. |
| Is 8: FP16 + ONNX export kuru test | ✅ TAMAM | 11_export_fp16.py end-to-end. FP16 PT 65.4 MB (yari), ONNX 130 MB (graph+external .data). Dynamic batch+spatial OK. Torch GPU FP32 vs ONNX CPU FP32 max diff 2.1e-3 (platform farki). Manifest 17ch + P4/P5 consumer OK. Bagimlilik notu: onnxscript pip kurulmali, .onnx + .onnx.data BIRLIKTE deploy. |
| Is 9 (opt): reports/p3_architecture.md | ✅ TAMAM | 13 bolum: SSL4EO gerekce, 17-bant adapter, Roberts spatial CV, BCE+Dice loss, K#6 RAW output, F1-max threshold, export, Plan B, akademik referanslar. |
| Is 10 (opt): predict_landsat_snapshot band_mapping | ✅ ISKELET TAMAM | Roy 2016 standart Landsat-S2 mapping eklendi (L5_TM, L7_ETM, L8_OLI, L9_OLI). Eksik bantlar zero-fill, quality tag (HIGH/MEDIUM/LOW). P5 custom override edebilir. Tam test T3.10'da gercek checkpoint sonrasi yapilacak. |

## Saat 6-12 (T3.4 — 6h slack) — KOD HAZIR

| Iskelet | Dosya |
|---|---|
| RAW prob inference (KRITIK Karar #6) | `code/p3/07_inference.py` |
| Grad-CAM utility | `code/p3/08_gradcam.py` |
| Ablation runner (5 konfig) | `code/p3/09_ablation.py` |
| F1-max threshold tuning | `code/p3/10_threshold_tuning.py` |
| FP16 + ONNX export | `code/p3/11_export_fp16.py` |
| Plan B fallback (Sabins/Liang esikleri) | `code/p3/12_fallback_threshold.py` |
| Train script (5-fold blok CV) | `code/p3/06_train.py` |

## Saat 11-12 (T3.5a) — BEKLEYEN

- T1.9 (P1) saat 11: ARD GeoTIFF + manifest -> Drive
- T2.7 (P2) saat 13: full_mask.tif + blok_cv_split.json -> Drive
- T3.5 baslangic kosulu: ARD + label + split JSON Drive'da hazir.

## Saat 12-15 (T3.5) — CRITICAL PATH

```bash
python code/p3/06_train.py \
    --tile-dir /content/drive/MyDrive/pomzadoya/data/ard/tiles \
    --full-mask /content/drive/MyDrive/pomzadoya/data/labels/full_mask.tif \
    --split-json /content/drive/MyDrive/pomzadoya/data/labels/blok_cv_split.json \
    --ssl4eo-ckpt /content/drive/MyDrive/pomzadoya/models/pretrained/B13_rn50_moco_0099_ckpt.pth \
    --output-dir /content/drive/MyDrive/pomzadoya/models \
    --reports-dir /content/drive/MyDrive/pomzadoya/reports \
    --epochs 30 --batch-size 8 --lr 1e-4 --folds 5 --amp [--wandb]
```

Hedef: 5-fold mean val IoU > 0.45, std < 0.08.

## Saat 15-18.5 (T3.6, T3.7, T3.10, T3.11)

| Görev | Komut |
|---|---|
| T3.6 F1-max threshold | `python code/p3/10_threshold_tuning.py --model ... --folds-all --output /reports/threshold_curve.json` |
| T3.7 Ablation (5 konfig) | `python code/p3/09_ablation.py --epochs 15 --folds 3 ...` |
| T3.10 RAW inference | `predict_raw()` API hazir; `predict_raster()` full AOI; `predict_landsat_snapshot()` P5 icin |
| T3.11 Grad-CAM | `python code/p3/08_gradcam.py --model ... --input ... --output ...` |

## Saat 18-24 (T3.13, T3.14)

| Görev | Komut |
|---|---|
| T3.13 Export | `python code/p3/11_export_fp16.py --model ... --output-pt /models/unet_pomza_fp16.pt --output-onnx /models/unet_pomza.onnx` |
| T3.14 KOD FREEZE | Final dry-run + manifest paylasimi |

## Plan B (yakinsamazsa)
- `python code/p3/06_train.py --rgb-only` (S2 RGB sade baseline)
- `python code/p3/12_fallback_threshold.py --ard ... --output /reports/fallback_pomza_prob.tif` (model gerektirmez; albedo+SWIR ratio+BSI esikleri).

## Sozlesme — P4 ve P5 ile

```python
# code/p3/07_inference.py
def predict_raw(tile_tensor: torch.Tensor, model_path: str,
                device: str = "cuda", fp16: bool = False) -> np.ndarray:
    """RAW prob [0, 1]. THRESHOLD/BINARIZE YOK (Karar #6)."""
```

- **P4** (T4.12): `final = predict_raw(...) * QI * (1 - CI)` icin RAW prob alir.
- **P5** (T5.8): Landsat snapshot icin `predict_landsat_snapshot()` kullanir.
- **P5** (T5.10): Streamlit'te thresholdsuz olasilik layer ekler; threshold slider kullaniciya gosterir.

## Risk takibi

| Risk | Olasilik | Aksiyon |
|---|:-:|---|
| SSL4EO HuggingFace 404 | Dusuk | GitHub release `B13_rn50_moco_*.pth` indir |
| Fine-tune yakinsamiyor | Orta | `--rgb-only` veya `--no-pretrained` ablation; gerekirse Plan B fallback |
| P1/P2 gecikiyor | Orta | Slack T3.4 dolu kullaniliyor; Plan B fallback hazir |
| GPU VRAM yetersiz | Dusuk | `--batch-size 4 --amp` |
| W&B baglanmiyor | Dusuk | Env'de WANDB_API_KEY yoksa otomatik atlanir |

## Olusturulan dosyalar

```
code/p3/
  01_env_setup.ipynb
  02_ssl4eo_pretrained.py
  03_datamodule.py
  04_loss_metrics.py
  05_synthetic_sanity.py
  06_train.py
  07_inference.py
  08_gradcam.py
  09_ablation.py
  10_threshold_tuning.py
  11_export_fp16.py
  12_fallback_threshold.py
  requirements.txt

agent_outputs/
  p3_t3_1_runblock.md
  p3_t3_2_runblock.md
  p3_t3_3_runblock.md
  p3_status.md
```
