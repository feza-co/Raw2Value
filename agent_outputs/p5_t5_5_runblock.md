# RUN-BLOCK [T5.5] — Sentinel-1 amplitude difference (Mazza 2023)

**Akademik referans:** Mazza et al. 2023 — SAR log-ratio change detection. K#5 (VV+VH GRD).
**Önkoşul:** P1 T1.5 S1 stack hazır (`data/s1_stack/S1_*VV*.tif`), Lee filtreli, dB.
**Beklenen süre:** 2 saat (P1 saat 5.5'te bitirir, biz 5.5–7.5).

## Pipeline

1. P1 T1.5 S1 stack: VV+VH GRD, Lee filter, dB ölçek.
2. dB → linear amplitude: A = 10^(dB/10).
3. Log-ratio: r = 10·log10(A_t1 / A_t0)  [dB]
4. CFAR-benzeri eşik: |r| > 3 dB (Mazza). +3 dB → increase, -3 dB → decrease.
5. Morphological cleanup: 3×3 majority filter.
6. Çıktı: uint8 `s1_change.tif` (0=stable, 1=increase, 2=decrease).

## Adımlar

```bash
python code/p5/04_s1_amplitude_diff.py
```

## Beklenen çıktı dosyaları
- `data/change/s1_change.tif`     (uint8, 3 kategori)
- `data/change/s1_logratio.tif`   (float32 dB, görsel inceleme için)

# VERIFY-BLOCK [T5.5]

Bana yapıştır:
- `s1_change.tif` QGIS render (kırmızı=increase, mavi=decrease)
- Histogram log-ratio (Mazza tipik: ortalama 0 civarı, kuyruk ±5 dB)
- Increase/decrease piksel sayımı (`gdalinfo -stats s1_change.tif`)
- AOI'ye göre değişim alanı (ha)

Sanity threshold: increase + decrease toplamı %0.5–10 arası (aşırı değişim → noise/calibration sorunu).

# DELIVER

```
[P5] T5.5 TAMAM
Çıktı: data/change/s1_change.tif
Sanity: ✅ increase 124 ha, decrease 38 ha, threshold ±3 dB (Mazza 2023)
Sıradaki: T5.6 Folium baselayer
```

## Plan B (S1 stack tek sahne / co-reg fail)
- 04_s1_amplitude_diff.py P1 stack'inde 2 sahne yoksa hata verir.
- Plan B: Tek sahne için variance map (texture) → değişim yerine "aktif yüzey" göstergesi.
- T5.13 dashboard'da "S1 change yok — sadece S1 amplitude (single date)" notu.
