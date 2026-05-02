# RUN-BLOCK [T5.8] — Roy 2016 cross-sensor Landsat harmonizasyon

**Akademik referans:** Roy et al. 2016 RSE 185:57-70, Table 2 (ETM+ → OLI OLS regression).
**Önkoşul:** P1 T1.10 Landsat snapshots (`data/landsat/L*_<year>.tif`, en az 6 bant: BGR-NIR-SWIR1-SWIR2 SR).
**Beklenen süre:** ~45 dk (5 snapshot × her biri ~9 dk).

## Sensör → hedef OLI dönüşüm zinciri
- L5 TM → ETM+ → OLI (iki adım kompoze)
- L7 ETM+ → OLI (Roy 2016 Table 2 doğrudan)
- L8/L9 OLI → identity

## Roy 2016 Table 2 katsayıları (ETM+ → OLI, SR 0..1 ölçeğinde)

| Bant   | slope  | intercept |
|--------|-------:|----------:|
| Blue   | 0.8474 | 0.0003    |
| Green  | 0.8483 | 0.0088    |
| Red    | 0.9047 | 0.0061    |
| NIR    | 0.8462 | 0.0412    |
| SWIR1  | 0.8937 | 0.0254    |
| SWIR2  | 0.9071 | 0.0172    |

## Adımlar

```bash
python code/p5/06_landsat_roy_harmonization.py
python code/p5/07_landsat_timelapse_gif.py   # GIF üret (1985, 1990, 2000, 2010, 2025)
```

## Beklenen çıktı dosyaları
- `data/temporal/landsat_harmonized/L<sensor>_<year>_OLIeq.tif` (×5)
- `data/temporal/landsat_frames/L_<year>.png`
- `data/temporal/landsat_timelapse.gif`
- `reports/roy2016_coefficients.json`

# VERIFY-BLOCK [T5.8]

Bana yapıştır:
- 5 yıl için harmonized RGB ekran görüntüsü (1985 vs 2025 yan yana)
- `landsat_timelapse.gif` (GIF dosyası açılıyor mu, etiketler doğru mu)
- `roy2016_coefficients.json` içeriği
- Histogram karşılaştırma: harmonize öncesi/sonrası (özellikle 1985 TM → 2025 OLI hizalaması)

Sanity threshold: yıllar arasında reflectance ortalaması ±10% drift'in altında, görsel olarak süreklilik var.

# DELIVER

```
[P5] T5.8 TAMAM
Çıktı: data/temporal/landsat_harmonized/ + landsat_timelapse.gif
Sanity: ✅ Roy 2016 ETM→OLI katsayıları uygulandı, 5 yıl GIF render OK
Sıradaki: T5.10 historical RAW inference (P3 inference.py bağımlı)
```

## Plan B (Roy 2016 yavaş veya hatalı)
- `06_landsat_roy_harmonization.py` içinde `fallback_mean_match()` fonksiyonu var.
- L5/L7 sahnesini L8 referansına mean-match (per-band z-score → L8 dağılımı).
- Akademik kalite düşer ama snapshot karşılaştırılabilir.
