# RUN-BLOCK [T5.2] — WDPA Göreme + 1000 m buffer + OSM cross-check

**Akademik referans:** K#8 (UNESCO Göreme buffer = 1000 m).
**Önkoşul:** T5.1 ortam, WDPA shapefile (`data/aoi/wdpa_tr/WDPA_TR.shp`).
**Beklenen süre:** 1 saat (Overpass yanıtı ~30s).

## WDPA shapefile temin
- Kaynak: https://www.protectedplanet.net (UNEP-WCMC, ücretsiz, kayıt gerekir)
- Filtre: country=TUR, indir, `data/aoi/wdpa_tr/` altına aç.
- WDPAID 1130 = "Göreme National Park" (Turkey, mixed UNESCO).

## Adımlar

```bash
python code/p5/02_wdpa_goreme.py
```

İçeriği:
1. WDPA shapefile → WDPAID=1130 feature.
2. UTM 32636'da 1000 m buffer.
3. OSM Overpass `boundary=protected_area|national_park` + name~Göreme cross-check.
4. IoU rapor (`reports/wdpa_goreme_check.json`).

## Beklenen çıktı dosyaları
- `data/aoi/wdpa_goreme.gpkg`
- `data/aoi/wdpa_goreme_buffer.gpkg`
- `data/aoi/osm_goreme_check.gpkg`
- `reports/wdpa_goreme_check.json`

# VERIFY-BLOCK [T5.2]

Bana yapıştır:
- `wdpa_goreme.gpkg` QGIS ekran görüntüsü (Göreme polygon görünüyor mu)
- `reports/wdpa_goreme_check.json` içeriği (IoU ≥ 0.5 olmalı)
- Buffer alanı (km²) — beklenen 50-100 km² arası

Sanity threshold: IoU > 0.5, buffer alanı 1000 m offset'e tutarlı, EPSG:32636.

# DELIVER

```
[P5] T5.2 TAMAM
Çıktı: data/aoi/wdpa_goreme_buffer.gpkg + reports/wdpa_goreme_check.json
Sanity: ✅ Göreme polygon, IoU OSM=0.78, buffer alanı 67 km²
Sıradaki: T5.3 Red flag overlay logic prototipi
```
