# RUN-BLOCK [T3.1] — Ortam kurulumu + GPU testi

**Owner:** P3 — ML Muhendisi
**Hedef ortam:** Colab Pro (A100/T4) / Kaggle GPU / yerel CUDA 11.8+
**Sure:** 0–2h
**Onkosul:** Hesap acildi, Drive baglanti hazir.

## Adimlar

1. **Drive mount + path kontrolu (Colab ise)**
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   import os
   os.makedirs('/content/drive/MyDrive/pomzadoya/models/pretrained', exist_ok=True)
   os.makedirs('/content/drive/MyDrive/pomzadoya/models/checkpoints', exist_ok=True)
   os.makedirs('/content/drive/MyDrive/pomzadoya/reports', exist_ok=True)
   ```

2. **Repo + bagimliklar**
   ```bash
   git clone https://github.com/<your-org>/pomzadoya /content/pomzadoya || true
   cd /content/pomzadoya
   pip install -q -r code/p3/requirements.txt
   ```

3. **Notebook calistir:** `code/p3/01_env_setup.ipynb`
   - Hucre 1: pip install
   - Hucre 2: CUDA + GPU kontrolu
   - Hucre 3: smp / timm / rasterio / grad-cam import
   - Hucre 4: U-Net (17 ch -> 1) smoke test
   - Hucre 5: VRAM batch=4 olcumu

4. **GPU bulunamazsa Plan B:** Kaggle GPU veya Vast.ai T4 ($0.20/h).

**Beklenen sure:** ~30 dk (kurulum + smoke test).

## ASENKRON
T3.2 SSL4EO-S12 yukleme RUN-BLOCK'unu paralel hazirlamami iste.

---

## VERIFY-BLOCK [T3.1]

Bana yapistir:
- `print('CUDA av.:', torch.cuda.is_available())` ciktisi
- `print('GPU :', torch.cuda.get_device_name(0))` ciktisi
- `print('VRAM tot:', ...)` ciktisi
- U-Net smoke test sonucu (`OK — forward pass calisti.`)
- Peak VRAM (batch=4 fwd+bwd) ciktisi

**Sanity threshold:**
- `torch.cuda.is_available()` -> True
- VRAM >= 12 GB (T4 yeterli; A100 idealdir)
- U-Net forward output shape == `(1, 1, 256, 256)`
- Peak VRAM (batch=4) < 8 GB (T4 16 GB icin guvenli marj)

**Yakinsamazsa:**
- `pip install` cakisma -> `pip install --upgrade --force-reinstall torch==2.1.0`
- CUDA mismatch -> `nvidia-smi` ciktisini paylas, env yeniden olustur
- VRAM yetersiz -> batch_size=4 yerine 2'e dus, gradient accumulation 2

---

## DELIVER

```
[P3] T3.1 TAMAM
Cikti: GPU erisimi + library importlar + U-Net smoke OK.
Metric: torch.cuda.is_available()=True, peak VRAM (b=4) ~X GB.
Siradaki bagimli: T3.2 SSL4EO-S12 pretrained yukleme + 13->17 adapter.
```
