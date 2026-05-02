# P2 — Etiketleme Lead Briefing

> **Hoş geldin.** Sen Modül A'nın **en yorucu manuel görevini** yapacaksın: 4 saat QGIS'te poligon çizimi (T2.3). Bunun yanında MAPEG sorgu, piksel sampling, raster mask (T2.8 critical path) işleri var. İyi haber: en yorucu kısım saat 3-7 arasında biter, sonrası rahat.

---

## 1. ROLÜN ÖZETİ

**Sen P2 — Etiketleme Lead'sin.** P3'ün fine-tune yapacağı **etiket verisini** üretiyorsun. **T2.8 raster mask** v2'de critical path'e girdi — saat 13'te bitmesi şart.

**Birincil çıktın:** `data/labels/full_mask.tif` — 20m grid raster etiket: 1 (pomza pozitif), 0 (negatif), 255 (ignore — WDPA buffer içi).

**Yanı sıra ürettiklerin:**
- `data/labels/positive_polygons.gpkg` (30-40 saha, manuel çizim)
- `data/labels/positive_pixels.gpkg`, `negative_pixels.gpkg` (sampling sonrası)
- `data/labels/blok_cv_split.json` — **Roberts 2017 spatial 5-fold blok CV**
- `data/labels/wdpa_buffer.gpkg`, `ignore_mask.tif`

---

## 2. CRITICAL PATH SORUMLULUĞUN

| Görev | Saat | CRITICAL? |
|---|---|---|
| **T2.8 Raster mask** | **13** | ✅ (v2 yeni) |

T2.8 saat 13'te bitmezse P3 fine-tune (T3.5) başlayamaz, kaskad gecikme olur.

---

## 3. HESAP & ARAÇ KURULUMUN (saat 0, ~20 dk)

### 3.1 QGIS yerel kurulum
- https://qgis.org/download → **QGIS 3.34 LTR** (long-term release) kullan
- Python plugin: zaten dahili
- Doğrulama: QGIS aç → Python Console → `from qgis.core import *` hatasız

### 3.2 WDPA Goreme National Park shapefile
- https://www.protectedplanet.net/en/thematic-areas/wdpa
- Search: "Goreme" → Türkiye → Goreme National Park
- "Download" → Shapefile (zip) indir
- Repo'da `data/wdpa_goreme.zip` yerleştir, açma — 02_wdpa_goreme.py açacak

### 3.3 MAPEG ÇED erişimi
- https://www.mapeg.gov.tr/ → ÇED Bölümü → Avanos / Nevşehir filtre
- **Nevşehir İl Çevre Durum Raporu 2014** PDF — Nevşehir Valilik veya csb.gov.tr arşivinde

### 3.4 Yerel Python ortam

```bash
python -m venv venv
source venv/bin/activate
pip install -r code/p2/requirements.txt
```

`requirements.txt`: `geopandas, rasterio, shapely, numpy, scikit-learn, verde, pandas`

---

## 4. KENDİ LLM'İNİ KUR (saat 0, ~10 dk)

```bash
cd Pomzadoya
claude --model claude-opus-4-7
```

**İlk mesaj:**

```
Sen .claude/agents/p2-etiketleme-lead.md tanımındaki P2 — Etiketleme Lead rolündesin.
Tek doğru kaynağın: Modul_A_Critical_Path_Dependency_v2.md.

ŞİMDİKİ DURUM:
- Saat 0/24, hackathon başladı
- Ben P2 sorumlusu ekip üyesiyim
- handoff/P2_BRIEFING.md okudum
- QGIS kuruldu, WDPA Goreme shapefile indi, MAPEG erişimim var
- Yerel Python venv hazır

YAPACAKLARIN:
1. agent_outputs/p2_status.md ve .claude/state/orchestrator_log.md oku
2. agent_outputs/p2_t2_1_runblock.md (QGIS setup) oku
3. T2.1, T2.2, T2.3 RUN-BLOCK'larını sırayla benimle koşturalım
4. T2.3 manuel poligon çizimi 4 saat sürecek — bana 30dk'da bir progress check-in iste
5. Ben T2.3 koşturuyorken sen T2.4, T2.5, T2.6, T2.7, T2.8 script'lerini hazırlık yap (zaten code/p2/'de varlar, gözden geçir + Roberts 2017 5-fold blok CV mantığını doğrula)

Ben şu an QGIS açıyorum. T2.1'den başla.
```

---

## 5. SAATLİK GÖREV TABLOSU

| Saat | Görev | Tür | Süre |
|---|---|---|---|
| 0:00-0:30 | Hesap + QGIS + Python kurulumu | 👤 | 30dk |
| 0:30-1:00 | LLM kurulumu | 👤 | 30dk |
| **1:00-2:00** | **T2.1 QGIS setup + S2 RGB altlık (P1'den saat 4'te gelecek S2 ARD bekleyebilir)** | 👤 | 1h |
| **2:00-3:00** | **T2.2 MAPEG ÇED + Nevşehir 2014 sorgu — saha listesi tablosu üret** | 👤 web research | 2h |
| **3:00-7:00** | **🔴 T2.3 MANUEL POLİGON ÇİZİMİ (30-40 saha, 4 saat — EN UZUN MANUEL İŞ)** | 👤 | 4h |
| 7:00-8:00 | T2.4 Pozitif piksel sampling (`code/p2/04_pixel_sampling.py`) | ⚙️ | 1h |
| 8:00-9:00 | T2.5 Negatif piksel sampling (`code/p2/05_negative_sampling.py`) | ⚙️ | 1h |
| 9:00-10:00 | T2.6 WDPA buffer + ignore mask (`code/p2/06_wdpa_ignore_mask.py`) | ⚙️ | 1h |
| 10:00-11:00 | T2.7 Roberts 2017 spatial 5-fold blok CV (`code/p2/07_spatial_block_cv.py`) | ⚙️ | 1h |
| **11:00-13:00** | **T2.8 Raster mask (CRITICAL) — `code/p2/08_rasterize_mask.py`** | ⚙️ | 2h |
| 13:00-14:00 | T2.9 Augmentation (`code/p2/09_augmentation.py`) | ⚙️ | 1h |
| 14:00-16:00 | T2.10 P3 ile DataLoader entegrasyon test | 👥 P3 | 2h |
| 16:00-17:00 | T2.11 Etiket QC raporu | ⚙️ | 1h |
| 17:00-18:30 | T2.12 P3 inference çıktılarıyla hata analizi | 👤 görsel + 👥 P3 | 1.5h |
| 18:30-20:00 | HELP→P5 KPI manuel doğrulama | 👥 P5 | 1.5h |
| 18:00-20:00 | Entegrasyon | 👥 | 2h |
| 20:00 | **KOD FREEZE** | 🛑 | — |
| 20:00-24:00 | Dry-run desteği | 👥 | 4h |

---

## 6. T2.3 — MANUEL POLİGON ÇİZİMİ DETAYI (En kritik 4 saat)

### Hazırlık (saat 3:00'da)
1. QGIS aç
2. **Layer ekle:**
   - S2 RGB altlık (P1 saat 4'te teslim edecek; sen saat 3'te başlayacaksın → ÖNCE S2 olmadan başla, sonra altlık değiştir VEYA P1 saat 4'e kadar bekle, T2.3 saat 4-8'e kayar — orchestrator'a sor)
   - **Alternatif:** Saat 3'te Google Satellite altlık kullan (QuickMapServices plugin), pomza sahalarını oradan tanı, sonra S2 RGB'ye geçtiğinde poligonları doğrula
3. **Yeni Vector Layer oluştur:**
   - Layer → Create Layer → New GeoPackage Layer
   - Path: `data/labels/positive_polygons.gpkg`
   - Geometry: Polygon
   - CRS: EPSG:32636 (UTM Zone 36N)
   - **Attribute alanları:**
     - `saha_id` (integer)
     - `uretici` (text, 100)
     - `mapeg_no` (text, 50)
     - `durum` (text, 30) — 'aktif', 'kapalı', 'belirsiz'
     - `geom_kalitesi` (integer, 1-5) — 1 net, 5 belirsiz sınır
     - `notlar` (text, 200)

### Çizim sırası (saat 3:00-7:00)
- MAPEG sorgu sonucu (saat 2-3'te ürettiğin tablo) sırayla çiz
- **Hedef:** 30-40 saha
- **Hız hedefi:** Her saha ortalama 7-8 dakika (ortalama)
- **Saat başı check-in:**
  - Saat 4: 7-10 saha
  - Saat 5: 15-20 saha
  - Saat 6: 22-28 saha
  - Saat 7: 30-40 saha
- Geride kalırsan grup chat'e "T2.3 yavaş, plan B'ye geçeyim mi?" yaz — Plan B: 25-30 saha ile yetin (akademik kalite hafif düşer)

### Çizim kuralları
- Polygon kapalı olmalı
- Saha sınırları **kesin değilse** `geom_kalitesi=4-5` ata, train/val'da düşük ağırlık alır
- WDPA Göreme buffer **içine** poligon çizme (LLM'e sor şüphedeysen — 02_wdpa_goreme.py çıktısıyla cross-check)
- Min saha alanı: 0.5 ha (5000 m²) — daha küçükse pixel sampling sağlıklı olmaz

### LLM yardımı (saat 3:00-7:00 arası)
LLM'e her 30dk'da sor:
```
T2.3 progress: <X>/<40> saha bitti, saat <h>. 
Geri kalan tahmini süre, hız OK mi, paralel başka bir RUN-BLOCK hazırlamamı ister misin?
```

LLM bu sırada T2.4-T2.8 script'lerini gözden geçirir, gerekirse iyileştirir.

---

## 7. ASENKRON İŞ KURALI

T2.3 manuel ama çok uzun (4 saat). Bu sırada **LLM boş durmaz**:
- T2.4 piksel sampling script'inin sentetik test koşusu
- T2.6 WDPA shapefile parsing testi
- T2.7 5-fold blok CV mantık doğrulaması
- T2.8 rasterize_mask edge case kontrolleri

Sen T2.3'te çizim yaparken LLM yan tarafta hazırlık yapar. Bittiğinde "T2.4 başla" demen yeterli.

---

## 8. KIM SANA NE TESLİM EDİYOR / SEN KİME NE TESLİM EDİYORSUN

### Sana gelen
| Saat | Girdi | Sağlayıcı | Kullanım |
|---|---|---|---|
| 4 | `data/ard/s2_ard_20m.tif` | P1 | T2.3 QGIS RGB altlık + T2.8 raster mask grid referansı |
| 10 | `data/tiles/` | P1 | T2.8 mask'in tile boyutuyla uyumu |

### Senden çıkan
| Saat | Çıktı | Tüketici | Kullanım |
|---|---|---|---|
| 7 | `data/labels/positive_polygons.gpkg` | P3 | Erken sanity check (T3.4 slack) |
| 11 | `data/labels/blok_cv_split.json` | P3 | T3.5 5-fold CV |
| **13** | **`data/labels/full_mask.tif` (CRITICAL)** | **P3** | **T3.5 fine-tune asıl etiket** |
| 13 | `data/labels/ignore_mask.tif` | P3 | Loss computation ignore_index=255 |

---

## 9. PLAN B'LERİN

| Tetikleyici | Plan B | Onay |
|---|---|---|
| T2.3 saat 7'de bitmedi | P1 saat 14'te HELP gelir, 5-10 ek poligon birlikte. VEYA 25-30 sahayla yetin. | Grup chat |
| T2.7 spatial blok CV karmaşık | 5-fold yerine **3-fold** kullan (Roberts 2017 metodu korunur, istatistik hafif düşer) | Grup chat |
| T2.8 raster mask saat 13'te bitmedi | P1 yardıma gelir, 1 saat içinde bitir VEYA tile sayısını azalt (eğitim verisi azalır) | Eskalasyon — orchestrator |
| WDPA shapefile bozuk/eksik | OSM Overpass'tan Goreme polygon çek (P5 kullanıyor zaten, oradan kopyala) | Otomatik |
| MAPEG ÇED erişimi yavaş/yok | OpenStreetMap'te "quarry" tag'li alanları + Google Maps'ten manual saha listesi | Web research |

---

## 10. T2.7 ROBERTS 2017 SPATIAL 5-FOLD BLOK CV — neden önemli

Sıradan random KFold pomza tespiti için **yanıltıcıdır** çünkü poligon içindeki pikseller mekânsal olarak korelasyonlu — train/val arasında "leak" olur, IoU yapay yüksek çıkar.

Roberts 2017 önerisi:
- AOI'yi büyük bloklara böl (örn. 5×5 km grid)
- Her bloku bir fold'a ata, fold'lar coğrafi ayrık
- Train/val arasında mekânsal sızıntı olmaz, gerçek genelleme ölçülür

Kod: `code/p2/07_spatial_block_cv.py` zaten bunu yapıyor. `verde` paketi ile blok grid üretir, sahalara bloklara göre fold atar, JSON'a yazar.

---

## 11. GITHUB WORKFLOW

```bash
git checkout -b p2-t2.x-<kısa-ad>
git add code/p2/* agent_outputs/p2_* data/labels/*.gpkg data/labels/*.json
# .gitignore'da *.tif var, full_mask.tif Git LFS ile track edilir:
git lfs track "data/labels/*.tif"
git add data/labels/full_mask.tif
git commit -m "[P2] T2.x <açıklama>

DELIVER: <çıktı path>
Sayım: <pozitif/negatif/ignore oranı>
Bağımlı: P3 T3.5 etiket bekliyor"
git push origin p2-t2.x-<kısa-ad>
```

---

## 12. KENDİNİ KONTROL — saat 7, 11, 13'te

### Saat 7 ✓
- [ ] `data/labels/positive_polygons.gpkg` exists, feature count 30-40
- [ ] QGIS attribute table'da tüm alanlar dolu (saha_id, uretici, mapeg_no)
- [ ] `data/labels/positive_pixels.gpkg` (T2.4 sonrası) ~10K piksel

### Saat 11 ✓
- [ ] `data/labels/blok_cv_split.json` exists, 5 fold tanımlı
- [ ] Her fold'da train/val tile listesi, blok bazında ayrık
- [ ] `data/labels/wdpa_buffer.gpkg` + `ignore_mask.tif` hazır

### Saat 13 ✓ **CRITICAL**
- [ ] `data/labels/full_mask.tif` exists
- [ ] 20m grid, EPSG:32636, NoData/ignore=255, pomza=1, neg=0
- [ ] `gdalinfo` boyutu P1'in tile grid'iyle uyumlu (256×256 veya katları)
- [ ] P3'e mesaj attın mı?

---

## 13. DOSYA REFERANSLARIN

| Ne | Nerede |
|---|---|
| Rol tanımım | `.claude/agents/p2-etiketleme-lead.md` |
| Görev detayı | `Modul_A_Critical_Path_Dependency_v2.md` § P2 |
| Mevcut kodlarım | `code/p2/` (10 dosya hazır) |
| RUN-BLOCK'larım | `agent_outputs/p2_t2_*_runblock.md` |
| Statü | `agent_outputs/p2_status.md` |
| QGIS attribute schema | `code/p2/03_polygon_template.gpkg.md` |
| MAPEG sorgu şablonu | `code/p2/02_mapeg_query_template.md` |

---

## 14. SIK SORULAR

**S: 30-40 saha hedef, ne kadar büyük olmalı?**
C: Min 0.5 ha (5000 m²), max yok. Ortalama 1-3 ha.

**S: Sahaların yerini nereden bilirim?**
C: T2.2'de MAPEG ÇED + Nevşehir 2014 raporundan koordinat listesi çıkardın. Onu kullan.

**S: Bir saha aktif mi kapalı mı emin değilsem?**
C: `durum='belirsiz'` ata, daha sonra P3'ün inference sonucuna göre QC fazında hata analizi yapılır (T2.12).

**S: 5-fold blok CV neden randoma tercih?**
C: Pomza sahaları mekânsal olarak kümelenmiş — random split'te train/val korelasyonu yüksek, IoU yapay yüksek (overestimate). Blok CV gerçek genellemeyi ölçer (Roberts 2017).

**S: Augmentation hangi parametrelerle?**
C: `code/p2/09_augmentation.py` zaten ayarlı. Geometric: hflip/vflip/rot90 (P=0.5). Spectral: brightness ±10%, contrast ±10% (P=0.3 — daha düşük çünkü pomza spektrası dengeli).

---

## 15. SENİN BAŞARI KRİTERLERİN

1. ✅ T2.3 saat 7'de 30-40 poligon hazır oldu
2. ✅ T2.7 Roberts 2017 5-fold blok CV split JSON saat 11'de hazır
3. ✅ T2.8 raster mask saat 13'te hazır (CRITICAL)
4. ✅ P3'ün T3.5 fine-tune'unda etiketin sorun çıkarmadı (5-fold mean val IoU > 0.45)

---

## 16. FİZİKSEL HAZIRLIK

T2.3 4 saat sürer. Hazırlığını yap:
- Klavye + mouse rahat olsun
- Geniş ekran (mümkünse 27"+) — QGIS detay çalışmasında ekran boyutu hayat kurtarır
- Kahve/su yanında
- 4 saat aralıksız zor — saat başı 5dk ara ver, gözünü dinlendir

---

**Saat 0 başladı sayılır. İlk eylemin: 3.1 QGIS kurulumu + 3.2 WDPA shapefile indir. Bittiğinde grup chat'e "P2 hazır" yaz.**
