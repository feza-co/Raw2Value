# T2.1 — QGIS Kurulumu + S2 RGB Altlık Yükleme

> **Görev sahibi:** P2 — Etiketleme Lead (manuel kurulum)
> **Süre:** ~1 saat (saat 0–1)
> **Öncül:** Yok
> **Çıktı:** QGIS projesi açık, EPSG:32636, S2 RGB altlık görünür

---

## 1. QGIS LTR (Long Term Release) Kurulumu

### Windows
1. https://qgis.org/en/site/forusers/download.html adresine git.
2. **QGIS Standalone Installer (Long Term Release) — 3.34 LTR** indir (~1.2 GB).
3. Kurulumu çalıştır → tüm bileşenler (GRASS, SAGA dahil) seçili kalsın.
4. Kurulum bittikten sonra **QGIS Desktop 3.34** kısayolunu aç (QGIS LTR yazanı seç, masaüstüne 4 tane kısayol gelir).

### Doğrulama
```
Help → About QGIS
```
- QGIS sürümü: 3.34.x LTR ✓
- GDAL: 3.8+ ✓
- Python: 3.11+ ✓

---

## 2. Yeni Proje + CRS Ayarı

1. **Project → New** (Ctrl+N).
2. **Project → Properties → CRS** (Ctrl+Shift+P).
3. Filtre kutusuna `32636` yaz → **WGS 84 / UTM zone 36N — EPSG:32636** seç → **Apply → OK**.
4. Project → Save As → `data/qgis_projects/avanos_etiketleme.qgz`.

> **Neden EPSG:32636?** Avanos, Türkiye, UTM 36N zone'unda. Metre cinsinden ölçüm (poligon alanı, buffer mesafesi 1000 m / 2000 m) için projekte CRS şart. Coğrafi (EPSG:4326) derece-tabanlı, **kullanma**.

---

## 3. S2 RGB Altlık Yükleme

P1'in T1.4 çıktısı `data/raw/s2_l2a_avanos_rgb.tif` (B04, B03, B02 — kırmızı, yeşil, mavi) saat 4'te hazır olur. Eğer P1 yetiştiremediyse, geçici olarak **GEE'den indirilmiş ham scene** veya **OSM offline tile** kullan.

### 3a. Yerel S2 GeoTIFF (önerilen)
1. **Layer → Add Layer → Add Raster Layer** (Ctrl+Shift+R).
2. `data/raw/s2_l2a_avanos_rgb.tif` seç → **Add → Close**.
3. Layer paneli → S2 layer'a sağ tık → **Properties → Symbology**:
   - Render type: **Multiband color**
   - Red band: **Band 1 (B04)**
   - Green band: **Band 2 (B03)**
   - Blue band: **Band 3 (B02)**
   - Contrast enhancement: **Stretch to MinMax**
   - Min/Max values: **Cumulative count cut 2%–98%**
4. **OK** → görüntü Avanos bölgesinde renkli görünmeli (yeşil/kahverengi/beyaz pomza alanları).

### 3b. Esri World Imagery (yedek altlık — pomza sahaları yüksek çözünürlükte)
1. Browser panel → **XYZ Tiles** → sağ tık → **New Connection**.
2. Name: `Esri Satellite`
3. URL: `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`
4. Min zoom: 0, Max zoom: 18 → **OK**.
5. Browser → XYZ Tiles → Esri Satellite → **double-click** → harita ekran üzerinde renderlenir.

> Esri'yi sadece referans olarak kullan; **etiketleme için S2 RGB asıl altlık** olmalı (modelin gördüğü görüntü).

---

## 4. Avanos AOI Yükleme

P1'in T1.2 AOI poligonunu yükle:
1. **Layer → Add Layer → Add Vector Layer** (Ctrl+Shift+V).
2. `data/aoi/avanos_aoi.gpkg` seç → **Add**.
3. AOI'ye sağ tık → **Zoom to Layer** (haritayı Avanos'a odakla).

---

## 5. Plugin Kurulumları (Opsiyonel ama Faydalı)

**Plugins → Manage and Install Plugins:**
- **QuickOSM** — OSM verisinden hızlı feature çekme (kontrol için).
- **Profile Tool** — DEM kesiti için (P4 ile koordinasyon).
- **Semi-Automatic Classification Plugin (SCP)** — eğer manuel çizim hızı yetmezse hibrit yardım.

---

## 6. Verify

```
[QGIS Status Bar — Sağ Alt]
- Coordinate: ortada (örn. 678500, 4287000) — UTM 36N koordinatları olmalı
- Scale: 1:25000 civarı → pomza sahaları ~50–500 m çapında görünür
- CRS: EPSG:32636 ✓
```

**Ekran görüntüsü al** → `agent_outputs/p2_t2_1_screenshot.png` olarak kaydet, RUN-BLOCK doğrulaması için.

---

## 7. Plan B (Risk)

- **S2 RGB tif gelmedi (P1 gecikti):** Esri altlığı ile başla, S2 geldiğinde değiştir. Manuel poligon koordinatları aynı kalır.
- **QGIS kurulumu çakışıyor:** QGIS LTR yerine **OSGeo4W Network Installer** dene (daha temiz, paket-tabanlı).
- **GPU rendering yavaş:** Settings → Options → Rendering → "Use render caching" aç.

---

*Son güncelleme: T2.1 RUN-BLOCK için.*
