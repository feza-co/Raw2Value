# RUN-BLOCK [T3.3] — DataModule + Loss + sentetik sanity check

**Owner:** P3 — ML Muhendisi
**Hedef ortam:** T3.1/T3.2 ile ayni
**Sure:** 4–6h (saat 4-6)
**Onkosul:** T3.2 OK (SSL4EO + adapter calisiyor)

**Karar referansi:** [K#10] spatial 5-fold blok CV (Roberts 2017).

## Adimlar

1. **Sentetik veri sanity (P1/P2 dosyalari gelmeden)**
   ```bash
   python code/p3/05_synthetic_sanity.py --device cuda --batch 4 \
       --ckpt /content/drive/MyDrive/pomzadoya/models/pretrained/B13_rn50_moco_0099_ckpt.pth
   ```
   Beklenen log:
   ```
   [1] Model     : SSL4EO-S12 U-Net, ~32 M param
   [2] Target    : pos=N1 neg=N2 ignore=N3
   [3] Forward   : in=(4, 17, 256, 256) out=(4, 1, 256, 256)
   [4] Loss      : 0.7-1.0 araligi (BCE+Dice combo)
   [5] Backward  : grad norm min ~1e-5 max ~1e+0
   [6] Metrics @0.5: IoU=~0.0 F1=~0.0 (random init bekleniyor)
   [7] Sweep     : best_thr=variable best_F1<0.4 (sentetik veri)
   [8] Peak VRAM : ~4-6 GB
   OK — sanity check tamam.
   ```

2. **DataModule iskelet testi (P1+P2 ciktisi gelir gelmez)**

   P1 T1.9 (saat 11) + P2 T2.7 (saat 13) sonrasinda:
   ```python
   from importlib import import_module
   import sys; sys.path.insert(0, 'code/p3')
   dm = import_module('03_datamodule').PomzaDataModule(
       tile_dir='/content/drive/MyDrive/pomzadoya/data/ard/tiles',
       full_mask='/content/drive/MyDrive/pomzadoya/data/labels/full_mask.tif',
       split_json='/content/drive/MyDrive/pomzadoya/data/labels/blok_cv_split.json',
       manifest_json='/content/drive/MyDrive/pomzadoya/data/ard/manifest.json',
       batch_size=4, num_workers=2,
   )
   dm.set_fold(0)
   loader = dm.train_dataloader()
   x, y = next(iter(loader))
   print('Batch input :', x.shape, x.dtype, 'min/max:', x.min().item(), x.max().item())
   print('Batch target:', y.shape, y.dtype, 'unique:', torch.unique(y).tolist())
   ```
   Beklenen:
   - `x.shape == (4, 17, 256, 256)`, dtype float32
   - `y.shape == (4, 256, 256)`, unique = `[0, 1]` veya `[0, 1, 255]` (ignore var)
   - x normalize edilmis (~[-3, +3] mean=0 std=1 etrafi)

3. **5-fold split sanity**
   ```python
   import json
   sp = json.load(open('/content/drive/MyDrive/pomzadoya/data/labels/blok_cv_split.json'))
   for k in range(5):
       tr = len(sp[f'fold_{k}']['train']); vl = len(sp[f'fold_{k}']['val'])
       print(f'fold_{k}: train={tr} val={vl}')
   ```
   Beklenen: her fold'un val ~%20, train ~%80. Toplam tile sayisi
   sabit. Foldlar arasi val tile'lar ayrik (intersection bos).

## ASENKRON
- T3.4 (saat 6-12 slack) icinde:
  - `code/p3/07_inference.py` zaten yazildi.
  - `code/p3/08_gradcam.py` zaten yazildi.
  - `code/p3/09_ablation.py` zaten yazildi.
  - `code/p3/10_threshold_tuning.py` zaten yazildi.
  - `code/p3/11_export_fp16.py` zaten yazildi.
  - `code/p3/12_fallback_threshold.py` (Plan B) zaten yazildi.

---

## VERIFY-BLOCK [T3.3]

Bana yapistir:
- `05_synthetic_sanity.py` tam ciktisi (8 satir).
- DataModule iskelet test ciktisi (Batch input/Batch target).
- 5-fold split satirlari.

**Sanity threshold:**
- Sentetik loss finite, grad finite.
- DataModule batch shape `(B, 17, 256, 256)` + `(B, 256, 256)`.
- Tile-mask CRS uyumu: HATA yok.
- 5-fold val intersection bos kume.

**Hata varsa:**
- `CRS uyumsuz` -> P1 manifest'i goster, P2 raster mask CRS'i sor.
- `tile shape != (17, 256, 256)` -> P1 T1.8 tile splitting parametrelerini
  goster, ben adapter ayarlarim.
- Etiket tum sifir / tum 255 -> P2 T2.7 mask uretimi sorunlu, P2'ye HELP.

---

## DELIVER

```
[P3] T3.3 SENTETIK SANITY TAMAM (2026-05-01, Colab Pro A100/H100)

Cikti:
  - PomzaTileDataset + PomzaDataModule + BCEDiceLoss + MetricAccumulator import OK
  - 05_synthetic_sanity.py end-to-end testi gecti

Metric:
  - Model: 32.57 M param (SSL4EO-S12 B3 RN50 + 3->17 adapter)
  - Target: pos=74860 neg=174277 ignore=13007 (sentetik mask)
  - Forward: (4,17,256,256) -> (4,1,256,256)
  - Loss: 0.7573 (BCE+Dice combo, 0.7-1.0 aralginda)
  - Backward: grad norm min=1.35e-03 max=6.35e-01 (NaN-free, healthy)
  - Metrics @0.5: IoU=0.272 F1=0.428 P=0.300 R=0.745 (sentetik, random)
  - Threshold sweep: best_thr=0.05 best_F1=0.462
  - Peak VRAM (b=4): 0.89 GB

BEKLEYEN:
  - Gercek DataLoader sanity P1 T1.9 (saat 11) ARD + manifest sonrasi
  - 5-fold split test P2 T2.7 (saat 11) blok_cv_split.json sonrasi
  - T3.5 fine-tune P2 T2.8 (saat 13) full_mask.tif sonrasi

Saat 4 itibariyle: T3.4 SLACK (6 saat) basladi. Inference review + Grad-CAM + ablation + Plan B fallback hazirlama.
```
