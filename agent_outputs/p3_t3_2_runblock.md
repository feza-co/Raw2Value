# RUN-BLOCK [T3.2] — SSL4EO-S12 pretrained yukleme + 13->17 multi-channel adapter

**Owner:** P3 — ML Muhendisi
**Hedef ortam:** T3.1 ile ayni (Colab Pro / Kaggle / yerel CUDA)
**Sure:** 2–4h (saat 2-4)
**Onkosul:** T3.1 OK; `code/p3/02_ssl4eo_pretrained.py` repo'ya yuklenmis.

**Karar referansi:** [K#2] SSL4EO-S12 pretrained, [K#6] multi-channel adapter

## Adimlar

1. **SSL4EO-S12 weights indir (HuggingFace)**
   ```python
   from huggingface_hub import hf_hub_download
   ckpt = hf_hub_download(
       repo_id='wangyi111/SSL4EO-S12',
       filename='B13_rn50_moco_0099_ckpt.pth',
       cache_dir='/content/drive/MyDrive/pomzadoya/models/pretrained',
   )
   print('SSL4EO ckpt:', ckpt)
   ```
   - Filename varyantlari: `B13_rn50_moco_0099_ckpt.pth` (ResNet-50, 13ch, MoCo).
   - Erisim sorunu olursa GitHub release: https://github.com/zhu-xlab/SSL4EO-S12/releases

2. **Adapter testi (13 -> 17 kanal)**
   ```bash
   python code/p3/02_ssl4eo_pretrained.py \
       --ckpt /content/drive/MyDrive/pomzadoya/models/pretrained/B13_rn50_moco_0099_ckpt.pth \
       --in-channels 17 --device cuda
   ```
   - Beklenen log: `[SSL4EO] Yuklendi. Missing keys: <small>, Unexpected: <small>`
   - `[ADAPTER] conv1 genisletildi: 13 -> 17 (mean_replicate)`
   - `OK — SSL4EO-S12 + 13->17 adapter calisti.`

3. **Sentetik sanity (T3.3 on test, paralel)**
   ```bash
   python code/p3/05_synthetic_sanity.py \
       --ckpt /content/drive/MyDrive/pomzadoya/models/pretrained/B13_rn50_moco_0099_ckpt.pth \
       --device cuda --batch 2
   ```

**Adapter mantigi (kod yorumu):**
- ImageNet 3-kanal -> 1-kanal grayscale donusumunde standart yontem: ortalama
  agirlik replikasyonu. Biz bunu 13 -> 17'ye genisletiyoruz.
- 13 SSL4EO bandinin agirligi conv1.weight[:, :13]'e olduğu gibi kopyalanir.
- Yeni 4 kanal (S1 VV, S1 VH, DEM, slope) icin agirlik =
  conv1.weight[:, :13].mean(dim=1, keepdim=True)
- Bu "agnostik" baslangictir; fine-tune sirasinda gradient bu agirliklari
  domain'e adapte eder (S1 dB, DEM yukseklik istatistikleri farklidir).
- Referans: Carreira & Zisserman 2017 (I3D weight inflation), He et al. 2017.

## ASENKRON
- Indirme 200-300 MB. Drive cache hizli, 2. calistirmada bedava.
- Sen indirme bekliyorsan T3.3 sanity script'ini paralel hazirla (zaten 05_synthetic_sanity.py mevcut).

---

## VERIFY-BLOCK [T3.2]

Bana yapistir:
- `[SSL4EO] Yuklendi. Missing keys: N, Unexpected: M` log satiri
- Missing key listesinin ilk 5'i (FC head haric encoder'da MISSING olmamali)
- `[ADAPTER] conv1 genisletildi: 13 -> 17 (mean_replicate)` satiri
- Forward test: `Input : (2, 17, 256, 256) Output: (2, 1, 256, 256) OK`
- Peak VRAM (batch=2)

**Sanity threshold:**
- `Missing keys` < 10 (encoder uyumlu)
- `Unexpected` <= 5 (FC head, projector vs.)
- Output shape `(2, 1, 256, 256)`
- Peak VRAM < 4 GB (batch=2, 17 kanal)

**Yakinsamazsa / hata varsa:**
- `state_dict` anahtar prefix'leri farkli -> `load_ssl4eo_resnet50_state_dict`
  fonksiyonundaki `prefixes_to_strip` listesine yeni prefix ekle (yapistir,
  ben guncellerim).
- `Missing keys` cok fazla (>50) -> SSL4EO weights farkli backbone'a ait
  olabilir (ViT vs ResNet). `B13_rn50_moco_*.pth` dosyasini iste.
- HuggingFace 404 -> alternatif: GitHub release `B13_rn50_moco_0099_ckpt.pth`
  manuel `wget` ile indir.

---

## DELIVER

```
[P3] T3.2 TAMAM
Cikti: SSL4EO-S12 ResNet-50 backbone yuklendi + 13->17 adapter (mean_replicate).
Metric: encoder missing=N, unexpected=M; forward (2,17,256,256)->(2,1,256,256) OK.
Adapter: conv1.weight[:, :13]=SSL4EO, conv1.weight[:, 13:17]=mean(SSL4EO 13).
Siradaki bagimli: T3.3 DataModule + sanity check; T3.5 fine-tune (saat 12).
```
