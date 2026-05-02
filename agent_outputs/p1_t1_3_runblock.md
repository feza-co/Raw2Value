# [P1] T1.3 — Sentinel-2 L2A Fetch + SCL Bulut Maskeleme

> **!! ASENKRON UYARI !!**
> GEE export task'i ~25-35 dk surer. Sen 'Run' dedikten sonra ben paralel olarak
> T1.4 (S2 ARD co-registration), T1.5 (S1 fetch) ve T1.6 (DEM) RUN-BLOCK'larini hazirlamaya devam edebilirim.
> Export bittiginde Drive'dan dosyayi `data/s2_raw/` altina indirip T1.4'u tetikle.

## RUN-BLOCK [T1.3]
**Hedef ortam:** Colab (T1.1 notebook'una hucre ekle) **VEYA** GEE Code Editor (https://code.earthengine.google.com).
**Onkosul:**
- T1.1 tamam: `ee.Initialize()` aktif, service account auth canli.
- T1.2 tamam: AOI bbox sabit (Avanos 34.70-35.00 E, 38.65-38.85 N).

**Adimlar:**

### A) Colab (onerilen — ayni session'da export job ID alirsin):
```python
%cd /content/drive/MyDrive/Pomzadoya
# ee.Initialize() onceki hucreden devam ediyor
exec(open('code/p1/03_sentinel2_l2a_fetch.py').read())
```

### B) GEE Code Editor (alternatif):
1. https://code.earthengine.google.com/ ac.
2. Yeni script — `03_sentinel2_l2a_fetch.py` icerigini JS'e cevirip yapistir
   (script Python, Code Editor JS — ayni mantik: ImageCollection filter + map(mask_scl) + Export.image.toDrive).
3. Run > Tasks > Run task — folder `Pomzadoya_GEE_exports`.

**Service account / token alani:**
- Eger `ee.Initialize()` hata verirse:
  ```python
  credentials = ee.ServiceAccountCredentials('PASTE_SERVICE_ACCOUNT_EMAIL_HERE', 'PASTE_KEY_FILE_PATH_HERE')
  ee.Initialize(credentials, project='PASTE_PROJECT_ID_HERE')
  ```

**Beklenen sure:** ~25-35 dk (export). Submit ~5 sn.

**Cikti:** GEE Drive folder `Pomzadoya_GEE_exports/s2_l2a_avanos_median_2024_20m.tif`
- 10 bant: B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12
- 20m grid (Karar #15 SWIR native), EPSG:32636
- SCL maskesi uygulanmis (cloud_pct < 20%, SCL keep = [4,5,6,11])

## VERIFY-BLOCK [T1.3]
Bana yapistir (export submit aninda):
- `S2 L2A scenes (cloud<20%, SCL-masked): N` — N >= 10 olmali (yaz donemi 4 ay)
- `Export task baslatildi. Task id: <TASK_ID>` — task ID'sini bana ver.

Bana yapistir (export bittikten sonra, dosyayi `data/s2_raw/` altina indirdikten sonra):
- `gdalinfo data/s2_raw/s2_l2a_avanos_median_2024_20m.tif` ilk 25 satir.
- Beklenen: `Driver: GTiff`, `Size is ~1500 1100`, `Pixel Size = (20.000,-20.000)`,
  `PROJCS[...UTM zone 36N...]`, bant sayisi >= 10.

**Sanity threshold:**
- Dosya boyutu: 80-300 MB (10 bant float32, ~28x22 km, 20m).
- NoData orani < %15 (SCL maskesinden sonra bulutsuz toplam alan)
- Bant min/max: B2-B8 reflectance [0, 0.5] araliginda, B11/B12 [0, 0.7] araliginda.

## ASENKRON HAZIRLIK SINYALI
> Export koustuyor (~30 dk). Onayla: T1.4 + T1.5 RUN-BLOCK hazirlamaya devam edeyim mi? (varsayilan: EVET)

## DELIVER (sen yapistirinca soyleyecegim)
```
[P1] T1.3 TAMAM
Cikti: data/s2_raw/s2_l2a_avanos_median_2024_20m.tif (10 bant, 20m, EPSG:32636)
Sanity: bulut < %20, NoData < %15, dosya boyutu sanity OK
Siradaki: T1.4 S2 ARD co-registration (CRITICAL PATH — saat 4'te P4 bekliyor)
```
