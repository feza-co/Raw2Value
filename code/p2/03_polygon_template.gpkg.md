# T2.3 — Manuel Pozitif Poligon Çizim Şablonu

> **Görev sahibi:** P2 — Etiketleme Lead (TAMAMEN MANUEL — kullanıcı yapacak)
> **Süre:** ~4 saat (saat 3–7) **— en yorucu görev, kritik**
> **Öncül:** T2.2 (saha listesi hazır)
> **Çıktı:** `data/labels/positive_polygons.gpkg` — 30–40 saha poligonu
> **CRS:** EPSG:32636 (UTM 36N) — metre tabanlı, alan/buffer hesabı için zorunlu

---

## 1. GeoPackage Layer Oluşturma (QGIS)

1. **Layer → Create Layer → New GeoPackage Layer** (Ctrl+Shift+N).
2. Form alanları:
   ```
   Database:        data/labels/positive_polygons.gpkg
   Table name:      positive_polygons
   Geometry type:   Polygon
   CRS:             EPSG:32636 (WGS 84 / UTM zone 36N)
   ✓ Include Z dimension: NO
   ✓ Create spatial index: YES
   ```
3. **New Field** ile aşağıdaki schema'yı oluştur (sırayla):

---

## 2. Attribute Schema (Zorunlu Alanlar)

| Alan Adı | Tip | Genişlik | Açıklama | Doldurma Zamanı |
|---|---|---|---|---|
| `saha_id` | Text (string) | 10 | `S001`–`S040` formatı, T2.2 CSV'sinden | Çizim öncesi (CSV join) |
| `mapeg_no` | Text (string) | 20 | MAPEG ruhsat numarası (varsa), boş olabilir | Çizim öncesi (CSV join) |
| `uretici` | Text (string) | 100 | Şirket / üretici adı | Çizim öncesi (CSV join) |
| `koy_mevki` | Text (string) | 80 | Köy ve mevki | Çizim öncesi (CSV join) |
| `durum` | Text (string) | 20 | `Aktif` / `Pasif` / `Terkedilmiş` / `Belirsiz` | Çizim öncesi (CSV join) |
| `kaynak` | Text (string) | 50 | `MAPEG_2018` / `Nevsehir_2014` / `OSM` / `Saha` | Çizim öncesi (CSV join) |
| `geom_kalitesi` | Integer | 1 | 1=net sınır, 2=biraz belirsiz, 3=çok belirsiz | **Çizim sırasında** |
| `cizim_tarihi` | Date | — | Çizim günü (auto-fill veya elle) | Çizim sırasında |
| `cizim_yapan` | Text (string) | 50 | Etiketleyici adı/inisyali | Sabit (Project Variable) |
| `pomza_orani` | Real (double) | — | Poligon içi pomza yüzde tahmini (0.0–1.0); homojen sahalar 1.0 | Çizim sırasında |
| `s2_scene_id` | Text (string) | 60 | Çizim sırasında baz alınan S2 sahnesinin ID'si (örn. `20240715T084551_T36SUH`) | Çizim sırasında (sabit, projede 1 kere) |
| `notlar` | Text (string) | 200 | Çevre özelliği, ihlal, tartışmalı sınır | Opsiyonel |

---

## 3. Çizim Protokolü (Adım Adım)

### Hazırlık (15 dk)
1. T2.2 `uretici_saha_listesi.csv`'yi QGIS'e yükle (Add Delimited Text Layer, X/Y yok — sadece attribute join için).
2. Yeni `positive_polygons` layer'ı için **Snap & Topology** ayarla:
   - Project → Snapping Options → Enable snapping (S kısayol)
   - Mode: All Layers, Tolerance: 12 px, Type: Vertex + Segment
3. **Project Variables** (Project → Properties → Variables):
   - `cizim_yapan` = "P2_TUNA" (örnek)
   - `cizim_tarihi` = bugünün tarihi
4. Layer → positive_polygons → **Properties → Attributes Form** → bu iki alan için default value: `@cizim_yapan` ve `@cizim_tarihi` koy.

### Çizim Sırası (Önerilen — Saha Yoğunluğuna Göre)
**Avanos AOI'yi 4 alt-bölgeye böl:**
- Bölge A: Avanos merkez kuzey (Çalış, Bahçelievler) — yoğun pomza, ~12 saha
- Bölge B: Sarıhıdır + Boğaz Köyü — orta yoğunluk, ~10 saha
- Bölge C: Çavuşin yönü (Göreme'ye yakın!) — DİKKAT: WDPA buffer sınırı kontrol et — ~8 saha
- Bölge D: Kızılırmak güneyi — düşük yoğunluk, ~5 saha

Her bölgeyi tek seansta bitir (mola verme, dikkat dağılması azalır).

### Tek Saha Çizim Adımları
1. Saha listesinden sıradaki `saha_id` ve `koy_mevki` ile QGIS'i o lokasyona zoom et (Locator bar veya manual pan).
2. S2 RGB altlıkta pomza imzasını tespit et:
   - **Renk:** açık-bej / kirli-beyaz / pembemsi-gri (kuru pomza)
   - **Doku:** düzensiz polygon, bitki örtüsü yok, kenar net
   - **Kontekst:** çevresinde nakliye yolları, depolama yığınları, bazen makine
3. **Toggle Editing** (kalem ikon) → **Add Polygon Feature** (Ctrl+.).
4. Poligonun dış sınırlarını **20 m hassasiyetle** çiz (S2 piksel çözünürlüğü = 20 m, daha hassas çizmenin anlamı yok).
5. Sağ tık → poligonu kapat → attribute formu açılır.
6. Form'u doldur:
   - `saha_id` → CSV'den
   - `geom_kalitesi`:
     - **1** = sınır net, %100 emin
     - **2** = sınırın bir kısmı belirsiz (örn. depolama vs aktif kazı belirsiz)
     - **3** = çok belirsiz, sadece imza tahmin
   - `pomza_orani`:
     - **1.0** = tüm poligon homojen pomza
     - **0.7–0.9** = içinde küçük cüruf yığını / araç parkı var ama pomza dominant
     - **< 0.7** = bu poligonu yeniden çiz, daha sıkı sınır kullan
   - `s2_scene_id` → projede sabit, 1 kez gir, sonrası kopyala
7. **Save Layer Edits** (Ctrl+S) → her 5 sahada bir kaydet (kayıp riskine karşı).

### İlerleme Tablosu (Her 30 dk Doldur)
```
Saat   Tamamlanan  Toplam   Bölge   Notlar
3:00      0           0      —       Başla
3:30      4           4      A       
4:00      9           9      A       Çalış bitti
4:30      13          13     B       
5:00      17          17     B       Sarıhıdır 1 saha tartışmalı
5:30      21          21     B/C     
6:00      26          26     C       WDPA çakışması var mı kontrol
6:30      32          32     C       
7:00      37          37     D       Hedef: 35 ± 5 ✓
```

---

## 4. Kalite Kontrol — Çizim Sırasında

### Kabul Kriterleri
- ✓ Hiçbir poligon < 200 m² (S2 piksel ≈ 400 m², en az 1 piksel olmalı; reel olarak en az 10 piksel istenir → ~4000 m²).
- ✓ Hiçbir poligon başka bir poligonla ÜST ÜSTE BİNMEMELİ (overlap = 0).
- ✓ Hiçbir poligonda **self-intersection** olmamalı (Vector → Geometry Tools → Check Validity).
- ✓ `geom_kalitesi=3` olan saha sayısı < 5 (eğitim verisinde gürültü olur).
- ✓ Tüm poligonlar Avanos AOI içinde (Vector → Research Tools → Select by Location ile kontrol).

### Geçersiz Durum
- Eğer bir saha **WDPA Göreme + 1000 m buffer** içine düşüyorsa → poligonu çiz, ama T2.6'da `ignore_mask` olarak işaretlenecek (etiket dışı). `notlar` alanına `"WDPA buffer içi — ignore"` yaz.

---

## 5. Çizim Sonrası Validasyon

Çizim bittiğinde QGIS Python Console'da:
```python
import processing

# Geometri geçerliliği
processing.run("native:checkvalidity", {
    'INPUT_LAYER': 'positive_polygons',
    'METHOD': 2,  # GEOS
    'VALID_OUTPUT': 'memory:valid',
    'INVALID_OUTPUT': 'memory:invalid',
    'ERROR_OUTPUT': 'memory:errors'
})

# Topology check (overlap)
processing.run("qgis:checkgeometries", {
    'INPUT': 'positive_polygons',
    'METHOD': 0
})
```

Veya komut satırı (proje köküne `cd`):
```bash
ogrinfo data/labels/positive_polygons.gpkg -al -so
# Beklenen: Feature Count: 30-40
# Beklenen: Geometry: Polygon
# Beklenen: Layer SRS WKT: EPSG:32636
```

---

## 6. Çıktı

```
data/labels/positive_polygons.gpkg
├── Feature count: 30-40
├── Geometry: Polygon
├── CRS: EPSG:32636
└── Attributes: 12 alan (yukarıdaki schema)
```

---

## 7. Plan B

- **4 saatte 30 saha bitirilemiyor:**
  - Saat 14'te P1'in HELP→P2 desteği geliyor (T1.12 slack). P1'e 5–10 ek negatif poligon yardımı için bu doküman aynı şablonu kullanır.
- **WDPA buffer'ı sahaların yarısını yutuyor:**
  - Bu pozitif poligon sayısını drop etmez; T2.6'da `ignore_mask` ile eğitim dışı kalırlar. `geom_kalitesi=1` olan saha hedefi en az 25.
- **Çok belirsiz sınır (geom_kalitesi=3 sayısı çoksa):**
  - Buffer-shrink stratejisi: poligonu 1 piksel (20 m) içe küçült, sadece çekirdek kullan. T2.4 piksel örneklemede güvenli.

---

*T2.3 tamamlandığında T2.4 piksel örneklemesi başlar (otomatik script — `04_pixel_sampling.py`).*
