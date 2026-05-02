# RUN-BLOCK [T5.10] — Historical pomza inference (RAW)

**v2 KRİTİK AYRIM:**
- T5.10 (bu görev): **Historical Landsat → P3 RAW olasılık** + sabit threshold 0.5.
  Kontemporanöz ASTER yok → füzyon **yapılamaz**.
- T5.13 (ayrı): **Current 2025 S2+ASTER → P4 FUSED `final_confidence.tif`**.
  İkisi karıştırılmaz.

**Akademik gerekçe:** ASTER yalnızca 2000-2008 arası Cappadocia için sınırlı sahne. 1985 ve
1990 için ASTER yok → füzyon imkânsız. Roberts et al. 2017 ve domain best-practice: kontemporanöz
veriyle füzyon, eksiklikte sadece RAW + manuel threshold.

**Önkoşul:**
- `code/p3/inference.py` içinde `predict_raw(image_chw: np.ndarray) -> np.ndarray` mevcut (P3 T3.10, saat 17.5).
- `data/temporal/landsat_harmonized/*.tif` (T5.8 çıktısı).

**Beklenen süre:** ~30 dk (5 snapshot × ~6 dk inference + vectorize).

## Adımlar

```bash
python code/p5/08_historical_pomza_inference.py
```

İçeriği:
1. Harmonize Landsat snapshot oku (B-G-R-NIR-SWIR1-SWIR2).
2. P3 `predict_raw` çağır → float32 probability raster.
3. Threshold 0.5 → binary mask.
4. `rasterio.features.shapes` → polygon vectorize.
5. Yıllık alan (ha, EPSG:32636).

## Beklenen çıktı dosyaları
- `data/temporal/historical_pomza_overlay/<year>_raw_prob.tif`
- `data/temporal/historical_pomza_overlay/<year>_pomza.gpkg`
- `reports/historical_pomza_summary.json`

# VERIFY-BLOCK [T5.10]

Bana yapıştır:
- 1985 vs 2025 polygon overlay QGIS ekran görüntüsü
- `historical_pomza_summary.json` (yıllık area_ha tablosu)
- 1985 area, 2025 area, oran (büyüme x kat)
- P3 model gerçekten yüklendi mi (mock fallback'e düşmediğine emin ol)

Sanity threshold: 1985 < 2025 olmalı (pomza üretimi büyür). 1985 area > 0 (sıfır ise threshold çok yüksek). 2025 RAW ile T5.13 FUSED arasında %30'dan fazla sapma yoksa sağlıklı.

# DELIVER

```
[P5] T5.10 TAMAM
Çıktı: data/temporal/historical_pomza_overlay/ + historical_pomza_summary.json
Sanity: ✅ 1985: 18ha, 1990: 32ha, 2000: 87ha, 2010: 156ha, 2025: 312ha
Sıradaki: T5.11 KPI hesabı + T5.13 final entegrasyon
```

## Plan B (P3 inference fn yok / fail)
- `08_historical_pomza_inference.py` içinde mock `_mock_predict_raw` var (BSI + SWIR1/SWIR2 oranı).
- Mock akademik geçerli değil — sadece dashboard demo akışı için.
- T5.13 entegrasyonda mock olduğu açıkça belirtilir, raporda "P3 inference yok, BSI proxy" uyarısı.
