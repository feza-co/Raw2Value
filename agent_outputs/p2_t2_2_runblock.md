# RUN-BLOCK — T2.2 MAPEG ÇED + Nevşehir İl Çevre Durum Raporu Sorgu

```
RUN-BLOCK [T2.2]
Hedef ortam: Web tarayıcı + QGIS + manuel CSV editor (Excel veya VS Code)
Önkoşul:
  - T2.1 tamam (QGIS açık, EPSG:32636)
  - İnternet erişimi (eced.csb.gov.tr, mapeg.gov.tr, csb.gov.tr arşivleri)
  - PDF okuyucu (Acrobat / SumatraPDF)

Adımlar (sırayla — şablon: code/p2/02_mapeg_query_template.md):
  1. (45 dk) MAPEG ÇED sorgu — eced.csb.gov.tr/ced/jsp/ek1/3
     Filtre: İl=Nevşehir, İlçe=Avanos, Sektör=Madencilik, Tarih=2010-2026
     → her ÇED kararının ruhsat no, üretici, koy_mevki, durum bilgisini csv'ye dök.
  2. (45 dk) Nevşehir İl Çevre Durum Raporu 2014 PDF (csb.gov.tr arşivi)
     Bölüm B.1 Madencilik tablolarından Avanos pomza satırlarını al.
     Çapraz doğrulama: aynı ruhsat no MAPEG'de de varsa kaynak alanı = "MAPEG+Nevsehir2014".
  3. (30 dk) QGIS QuickOSM eklenti ile AOI içinde landuse=quarry çek.
     material=pumice/bims olanlar pozitif aday; diğerlerini ele.
     MAPEG/Nevşehir listesinde olmayan ama OSM'de olan sahalari "manuel doğrulama" listesine ekle
     (Google Earth Pro Historical Imagery ile pomza imzasi kontrol).
  4. (15 dk) 3 kaynagi merge et, tekrarlari (mapeg_ruhsat_no veya koy_mevki ile) deduplicate et.
     Hedef: 30-40 satır. Sapmalar:
       - <30 → durum=Belirsiz olanlari da dahil et
       - >40 → durum=Pasif/Terkedilmis olanlari sona at, kalitesi yuksekleri tut.
  5. CSV'yi data/labels/uretici_saha_listesi.csv olarak kaydet (UTF-8, virgülle).

Beklenen süre: ~135dk (2.25 h)
```

## CSV Schema (zorunlu kolonlar — code/p2/03_polygon_template.gpkg.md ile join edilecek)

```csv
saha_id,mapeg_ruhsat_no,uretici,firma_tipi,koy_mevki,kaynak,durum,ruhsat_alani_ha,baslangic_yili,notlar
```

## VERIFY-BLOCK [T2.2]

Bana yapıştır:
- `wc -l data/labels/uretici_saha_listesi.csv` → satır sayısı (header dahil 31-41 arası)
- İlk 5 satır + son 5 satır (CSV head/tail çıktısı)
- Kaynak dağılımı:
  ```
  python -c "import pandas as pd; df=pd.read_csv('data/labels/uretici_saha_listesi.csv'); print(df['kaynak'].value_counts())"
  ```
  Beklenen: MAPEG ≥ 15, Nevsehir2014 ≥ 10, OSM ≤ 10
- Durum dagilimi: Aktif ≥ 25, Pasif/Terkedilmis ≤ 15
- saha_id unique mi:
  ```
  python -c "import pandas as pd; df=pd.read_csv('data/labels/uretici_saha_listesi.csv'); assert df['saha_id'].is_unique; print('OK')"
  ```

Sanity threshold:
- 30 ≤ satir ≤ 40
- saha_id unique
- kaynak alani bos olmamalı (her saha en az 1 kaynaktan teyit)
- koy_mevki Avanos ilçesi içinde

## DELIVER

```
[P2] T2.2 TAMAM
Çıktı: data/labels/uretici_saha_listesi.csv (35 saha)
Sanity: ✓ MAPEG=18, ✓ Nevsehir2014=12, ✓ OSM=5; durum=Aktif 28, Pasif 5, Belirsiz 2
Sıradaki bağımlı: T2.3 manuel poligon (saat 3-7, 4 saat — kritik)
```

## Plan B

- **MAPEG portali calismiyor:** Wayback Machine cache (web.archive.org/web/2024*/eced.csb.gov.tr).
- **Nevsehir 2014 PDF erisilemiyor:** 2015 / 2016 raporu da uygun (ayni tablolar tekrarli).
- **<30 saha:** P5'in WDPA + OSM cross-check kanalindan ek 5 saha (orchestrator onayi).
