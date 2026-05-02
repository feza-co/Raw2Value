# RUN-BLOCK — T2.1 QGIS Kurulum + S2 RGB Altlık

```
RUN-BLOCK [T2.1]
Hedef ortam: Yerel Windows + QGIS LTR 3.34
Önkoşul:
  - QGIS LTR yükleyici hazır (https://qgis.org)
  - data/aoi/avanos_aoi.gpkg mevcut (P1 T1.2 çıktısı)
  - data/raw/s2_l2a_avanos_rgb.tif (P1 T1.4 çıktısı; saat 4'te tamam — T2.1 saat 0-1 oldugu icin
    altlık bu adımda eksik olabilir, Esri XYZ Tiles ile başla, S2 gelince değiştir)

Adımlar (manuel — dokümantasyon: code/p2/01_qgis_setup.md):
  1. QGIS LTR 3.34'ü kur (Windows installer).
  2. Yeni proje aç → Project Properties → CRS = EPSG:32636 (UTM 36N).
  3. data/aoi/avanos_aoi.gpkg yukle, "Zoom to Layer".
  4. Esri Satellite XYZ Tiles ekle (yedek altlik): 
     URL: https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}
  5. data/raw/s2_l2a_avanos_rgb.tif geldiginde Add Raster Layer ile yukle:
     - Symbology: Multiband color, R=B04 G=B03 B=B02
     - Stretch: Cumulative count cut 2-98%
  6. Project Save As: data/qgis_projects/avanos_etiketleme.qgz

Beklenen süre: ~60dk
```

## VERIFY-BLOCK [T2.1]

Bana yapıştır:
- QGIS About ekran goruntusu (LTR 3.34, GDAL 3.8+ teyit)
- Sag-alt status bar: `EPSG:32636` ve scale 1:25000 civari
- Ekran goruntusu: AOI poligonu Avanos uzerine zoom yapilmis halde, Esri (veya S2) altlik gorunur
- Komut: `dir data\\qgis_projects\\avanos_etiketleme.qgz` (PowerShell) → dosya var

Sanity threshold:
- QGIS surumu 3.34.x LTR
- Proje CRS = EPSG:32636
- AOI feature count ≥ 1
- (S2 hazirsa) raster band sayisi = 3, dtype uint16 veya float

## DELIVER

```
[P2] T2.1 TAMAM
Çıktı: data/qgis_projects/avanos_etiketleme.qgz, QGIS LTR 3.34 kurulu
Sanity: ✓ EPSG:32636, ✓ AOI yuklu, ⏳ S2 RGB altlik bekliyor (P1 T1.4)
Sıradaki bağımlı: T2.2 MAPEG sorgu (saat 1-3); altlik Esri ile baslanir, S2 gelince swap
```

## Notlar

- Eger QGIS LTR yerine Daily veya Latest sürüm kuruldu ise, T2.3 manuel cizim sirasinda
  bazi attribute formu davranislari farklilik gosterebilir — sorun olmasa bile LTR onerilir.
- S2 altlık geldiginde **Layer Properties → Set Layer to Project CRS** kontrol et: hatali
  reproject olmasin (T1.4 dosyasi zaten EPSG:32636 olmali, [K#15]).
