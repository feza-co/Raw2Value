# P3 — ML Muhendisi DURUM

_Modul A v2 — Pomzadoya hackathon, 24h penceresi_
_Son guncelleme: 2026-05-01_

## Saat 0-6 (T3.1, T3.2, T3.3) — TAMAM (kod hazirlandi, GPU calistirma kullanicida)

| Görev | Durum | Cikti |
|---|---|---|
| T3.1 Ortam + GPU test | KOD HAZIR | `code/p3/01_env_setup.ipynb` + RUN-BLOCK |
| T3.2 SSL4EO-S12 + 13->17 adapter | KOD HAZIR | `code/p3/02_ssl4eo_pretrained.py` + RUN-BLOCK |
| T3.3 DataModule + Loss + sanity | KOD HAZIR | `code/p3/03_datamodule.py`, `04_loss_metrics.py`, `05_synthetic_sanity.py` + RUN-BLOCK |

## Saat 6-12 (T3.4 — 6h slack) — TAMAM (kod hazirlandi)

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
