# RUN-BLOCK — T2.3 Manuel Pozitif Poligon Çizimi (4 SAAT — EN YORUCU GÖREV)

> **UYARI:** Bu görev tamamen manuel. Sen (orchestrator/agent) çizmezsin. Kullanıcı QGIS'te elle çizer. Sen şablon ve check-in zamanlamasını yönetirsin.

```
RUN-BLOCK [T2.3]
Hedef ortam: QGIS LTR 3.34 (T2.1'de açıldı)
Önkoşul:
  - T2.1 tamam (QGIS, EPSG:32636, S2 RGB altlık)
  - T2.2 tamam (data/labels/uretici_saha_listesi.csv 30-40 saha)
  - Çizim şablonu: code/p2/03_polygon_template.gpkg.md

Adımlar (manuel):
  1. (15 dk) Layer → Create Layer → New GeoPackage Layer
     → data/labels/positive_polygons.gpkg
     → Polygon, EPSG:32636
     → 12 attribute alanı (saha_id, mapeg_no, uretici, koy_mevki, durum, kaynak,
        geom_kalitesi, cizim_tarihi, cizim_yapan, pomza_orani, s2_scene_id, notlar)
  2. (15 dk) uretici_saha_listesi.csv'yi Add Delimited Text Layer ile yükle (X/Y yok).
     Project Variables: cizim_yapan, cizim_tarihi default değerler.
     Snap & Topology aç (S kısayol, tolerance 12 px, vertex+segment).
  3. (3.5 saat) Bölge bölge çizim (4 alt-bolge: A=Çalış kuzey, B=Sarıhıdır, C=Çavuşin
     [WDPA dikkat], D=Kızılırmak güneyi). Saha listesinden saha_id ile ilerle.
     Her saha için:
       - S2 RGB altlıkta pomza imzasını teyit (açık-bej / kirli-beyaz)
       - 20m hassasiyetle dış sınır çiz
       - Attribute formu doldur: geom_kalitesi (1-3), pomza_orani (0.7-1.0), notlar
       - Her 5 sahada bir Save Layer Edits (Ctrl+S)
  4. (15 dk) Çizim sonrası validasyon (QGIS Python Console):
       processing.run("native:checkvalidity", ...) — overlap/self-intersect kontrol
       Vector → Research Tools → Select by Location ile AOI içinde mi kontrol

Beklenen süre: ~240dk (4 saat) — KRİTİK, T2.4 için saat 7'de tamam olmalı
```

## CHECK-IN ZAMANLAMASI (her 30 dk)

Orchestrator/agent şu sıralı sorgu yapacak (otomatik scheduler veya kullanıcıya bildirim):

| Zaman | Hedef Saha | Soru |
|---|---|---|
| 3:00 | 0 | "T2.3 başladı mı? Layer oluşturuldu mu?" |
| 3:30 | 4 | "Bölge A başladı mı? Kaç saha bitti? Sorun var mı?" |
| 4:00 | 9 | "Çalış bölgesi tamam mı? Pomza imzası tespit kolay mı?" |
| 4:30 | 13 | "Bölge B (Sarıhıdır) başladı mı? Tartışmalı sınırlı saha var mı?" |
| 5:00 | 17 | "WDPA buffer'a yakın saha çıktı mı? geom_kalitesi=3 sayısı?" |
| 5:30 | 21 | "Yorgunluk seviyesi? 5 dk mola öner." |
| 6:00 | 26 | "Bölge C başladı mı? Çavuşin civarı WDPA çakışması var mı?" |
| 6:30 | 32 | "Hedefe yaklaştı (35±5). geom_kalitesi=3 sayısı <5 mi?" |
| 7:00 | 35-40 | "T2.3 BİTTİ mi? VERIFY-BLOCK çalıştır." |

Eğer 4:30'da 9'dan az saha ⇒ orchestrator'a slip sinyali ver, **HELP→P2 saat 14'te aktif edilir**.

## VERIFY-BLOCK [T2.3]

Bana yapıştır:
- `ogrinfo data/labels/positive_polygons.gpkg -al -so` çıktısı:
  - Feature Count: 30-40
  - Geometry: Polygon
  - Layer SRS WKT: PROJCRS["WGS 84 / UTM zone 36N", ...] EPSG:32636
- QGIS attribute table screenshot (12 alan dolu görünür)
- QGIS Python Console:
  ```python
  layer = QgsProject.instance().mapLayersByName('positive_polygons')[0]
  print(f"Feature count: {layer.featureCount()}")
  print(f"CRS: {layer.crs().authid()}")
  invalid = [f for f in layer.getFeatures() if not f.geometry().isGeosValid()]
  print(f"Invalid geometries: {len(invalid)}")
  ```
- Overlap testi:
  ```python
  processing.run("qgis:checkgeometries", {'INPUT': 'positive_polygons', 'METHOD': 0})
  # 0 overlap olmalı
  ```
- AOI dışı kontrol: tüm poligonlar AOI içinde olmalı (Select by Location).

Sanity threshold:
- 30 ≤ feature ≤ 40
- 100% geometry valid (no self-intersection, no overlap)
- geom_kalitesi=3 sayısı < 5 (eğitim verisinde gürültü kabul edilebilir tavanı)
- pomza_orani ≥ 0.7 her satırda
- saha_id CSV'deki saha_id'lerle 1:1 eşleşiyor

## DELIVER

```
[P2] T2.3 TAMAM
Çıktı: data/labels/positive_polygons.gpkg (38 saha, EPSG:32636)
Sanity:
  ✓ feature count 38 (hedef 30-40)
  ✓ tüm geom_kalitesi ≤ 2 (3 olan 0 saha — yüksek kalite!)
  ✓ pomza_orani ≥ 0.85 ortalama
  ✓ overlap 0, self-intersect 0
  ✓ AOI içinde 38/38
Sıradaki bağımlı:
  - P3 (T3.4 sanity check için ön-versiyon — saat 7'de teslim)
  - T2.4 piksel örneklemesi (otomatik script — code/p2/04_pixel_sampling.py)
```

## Plan B (4 saatte yetişmezse)

| Senaryo | Tetik | Aksiyon |
|---|---|---|
| Saat 4:30, < 9 saha | Bölge A bitmedi | Orchestrator'a slip sinyali. HELP→P2 saat 14'te kesin aktif. |
| Saat 6:00, < 25 saha | İki bölge hâlâ açık | T2.4 öncesi mevcut sahalar ile başla; T2.5 negatif sampling pozitif sayısının 2x'i ile orantılı (örn. 25 poz → 5K neg, planlananın altında ama kabul edilebilir). |
| Saat 7:00, 30 saha | Hedef alt sınır | DEVAM, T2.4'e geç. Eksik sahalar T2.12 hata analizinde 2. tur etiketleme ile tamamlanabilir. |
| Yorgunluk / dikkat dağınıklığı | Her saatte | 5 dk mola, kahve. Çizim hızı %20 yavaşlarsa quality > quantity. |
