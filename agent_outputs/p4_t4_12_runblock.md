# RUN-BLOCK [T4.12] — **CRITICAL PATH (v2 yeni)** Score-level füzyon canlı (saat 18-20)

**Hedef**: `final_confidence = raw_prob × QI_norm × (1 - CI_norm)` raster üretmek.
**P5 T5.13 ana katmanı budur. Demo bu raster üzerine kurulu.**

**Önkoşul** (saat 17.5'te hazır olmalı):
- P3 `inference.py` RAW olasılık raster: `data/inference/raw_prob.tif`
- P4 `data/layers/aster_qi_20m.tif` (T4.6 sonrası)
- P4 `data/layers/aster_ci_20m.tif` (T4.6 sonrası)
- Üçü de **20 m, EPSG:32636, aynı extent**

**Süre**: ~10 dk (formül hesabı saniye, asıl iş sanity)
**Asenkron**: HAYIR — kritik patika. P3 inference biter bitmez başlar.

## Adımlar

### A) API contract sanity (saat 17.5–18, HELP→P3 sonu)

```bash
python -c "
from code.p4.fuse_confidence import fuse_confidence, percentile_minmax_norm
import numpy as np
raw = np.full((100,100), 0.7, dtype='f4')
qi  = np.linspace(0.5, 2.5, 100*100, dtype='f4').reshape(100,100)
ci  = np.linspace(0.95, 1.10, 100*100, dtype='f4').reshape(100,100)
out = fuse_confidence(raw, qi, ci)
print('shape', out.shape, 'min', out.min(), 'max', out.max(), 'mean', out.mean())
"
```
Beklenen: `shape (100,100) min ~0 max ~0.7 mean ~0.35`. Bu başarılıysa API sözleşmesi tamam.

### B) Shape sanity (saat 18:00)

```bash
for f in data/inference/raw_prob.tif data/layers/aster_qi_20m.tif data/layers/aster_ci_20m.tif; do
  echo "== $f =="
  gdalinfo "$f" | grep -E 'Size is|Pixel Size|Coordinate System|EPSG'
done
```
Üçünün de: `Size is W H` aynı, `Pixel Size = (20.0, -20.0)`, EPSG:32636.

Eğer farklıysa:
```bash
# qi/ci'yi raw'ın grid'ine align et
python code/p4/06_resample_to_s2_grid.py \
    --reference data/inference/raw_prob.tif \
    --inputs data/layers/aster_qi.tif data/layers/aster_ci.tif \
    --out data/layers/
```

### C) FÜZYON CANLI (saat 18:00–18:30)

```bash
python code/p4/fuse_confidence.py \
    --raw  data/inference/raw_prob.tif \
    --qi   data/layers/aster_qi_20m.tif \
    --ci   data/layers/aster_ci_20m.tif \
    --out  data/layers/final_confidence.tif \
    --report reports/fuse_report.json
```

Çıktı: `data/layers/final_confidence.tif` + JSON sanity.

### D) Sanity (18:30–19:00)

```bash
python -c "
import rasterio, numpy as np
with rasterio.open('data/layers/final_confidence.tif') as s: f = s.read(1)
v = f[np.isfinite(f)]
print('min', v.min(), 'max', v.max(), 'mean', v.mean(), 'p99', np.percentile(v,99))
print('above_0.5_pct', (v>0.5).mean()*100)
"
```

Beklenen:
- min=0, max≤1
- mean < raw_prob mean (CI cezası varsa)
- above_0.5_pct: %0.5–%5 (Avanos AOI'sinde)

### E) Preview PNG (P5'e teslim)

```bash
python -c "
import matplotlib.pyplot as plt, rasterio
with rasterio.open('data/layers/final_confidence.tif') as s:
    a = s.read(1)
plt.imshow(a, cmap='viridis', vmin=0, vmax=1)
plt.colorbar(label='final_confidence')
plt.title('P3×P4 Fused Confidence')
plt.savefig('reports/final_confidence_preview.png', dpi=150, bbox_inches='tight')
"
```

## VERIFY-BLOCK [T4.12]
Bana yapıştır:
- `gdalinfo data/layers/final_confidence.tif | head -20` (CRS=EPSG:32636, res=20m, NoData=NaN)
- `cat reports/fuse_report.json` — final_mean, delta, shape
- `reports/final_confidence_preview.png` (PNG)
- Sanity threshold:
  - final ∈ [0, 1] strict
  - delta_mean_raw_minus_final ≥ 0 (füzyon ortalama düşürür)
  - p99 > 0.3 (en güçlü adaylar var)

## Plan B — saat 20'de bitmediyse (Karar #6 fail)
1. P5'e haber: "FUSED demo iptal, raw + ASTER ayrı katman"
2. `final_confidence.tif` yerine `data/inference/raw_prob.tif` kopyala
3. Streamlit dashboard'da "Fusion (planned)" etiketi vizyon slaydında
4. Orchestrator log'una **kırmızı sinyal**

## DELIVER
```
[P4] T4.12 TAMAM ← CRITICAL PATH
Çıktı: data/layers/final_confidence.tif (EPSG:32636, 20m, COG, [0,1])
Sanity: ✅ shape match, ✅ aralık [0,1], ✅ delta>0 (CI cezası çalışıyor)
Sıradaki bağımlı: P5 T5.13 final entegrasyon ana katman olarak kullanır
```
