# PomzaScope — Kapadokya Hackathon 2026 Deep Research Raporu
**Hazırlık tarihi:** 1 Mayıs 2026 · **Hedef:** 24 saatte build edilecek pomza tespiti + üçlü sınıflandırma + yakıt-optimal rota MVP'si için veri/yöntem boşluk taraması.

> **Ön uyarı:** Bu rapor literatür ve halka açık portal taramasına dayanır. Sahaya özel doğrulama (özellikle MAPEG ruhsat poligonu indirilebilirliği, Kapadokya pomzasına ait *yayınlanmış spektral imza*, ve Türk pomza KOBİ SaaS fiyat benchmark'ı) doğrulanamadı; ilgili noktalar `⚠️ Doğrulanamadı` olarak işaretlenmiştir.

---

## 1. Uydu Seçimi & Veri Erişimi

### Sensör karşılaştırması (pomza = silisik volkanik kayaç + tüf eşlikçisi)

| Sensör | Çözünürlük / Bant | Pomza için katkı | Hackathon kararı |
|---|---|---|---|
| **Sentinel-2 MSI** | 10–60 m, 13 bant (VNIR + Red Edge + 2× SWIR) | SWIR1/SWIR2 (B11/B12) silika ve OH-mineraller (zeolit, kil) için iyi proxy; B11/B12 = "Sabins ratio" → hidroksil bant | ✅ 24 saat build için kullanılabilir (ana sensör) |
| **Sentinel-1 SAR** | 10 m, C-band VV+VH | Yüzey pürüzlülüğü → yığın/açık ocak topoğrafyası, NDVI ile karıştırılmaz | ✅ Kullanılabilir (yardımcı kanal, opsiyonel füzyon) |
| **Landsat 8/9 OLI+TIRS** | 30 m + 100 m termal | TIRS yüzey sıcaklığı (LST) — açık pomza yüksek albedo + soğuk gece imzası | ⚠️ TIRS kullanımı marjinal; pixel başına hesap ek iş |
| **ASTER** | 15–90 m, 14 bant (6 SWIR + 5 TIR) | **Mineral mapping için altın standart** — kuvars (TIR 10–14), karbonat ayrımı, Ninomiya silika indeksi | ❌ 24 saatte yetişmez (arşiv NASA Earthdata, ön işleme yoğun) |
| **PRISMA** | 30 m, 240 bant (400–2500 nm) | Pomza ↔ tüf ↔ obsidiyen ↔ kuvars ayrımı için ideal; HDF5 formatı | ❌ 24 saatte yetişmez (ASI kayıt süreci, HDF5 çevrimi, az tile) |
| **WorldView-3** | 0.3 m + 8 SWIR | Ticari, ücretli; kayda değer SWIR | ❌ 24 saatte yetişmez (lisans + maliyet) |

**Kritik bulgu:** Pomzanın *spesifik* bir "tek bant" imzası yok — silisik camsı yapı (SiO₂ %55–77) nedeniyle yüksek albedo + B11/B12 kil/silika bandında yüksek yansıma + NDVI ≈ 0 + yüksek Albedo Sentinel-2 RGB+SWIR kombinasyonu ile ayırt edilebilir. Van der Meer et al. 2014, Sentinel-2'nin B2/B4/B5/B6/B7/B11/B12 bantlarının lithology/alteration için kullanılabileceğini doğrulamış (Sabins ratio: B11/B12 RGB-R, B4/B2 RGB-G, B4/B11 RGB-B).

### Veri erişim platformları

| Platform | Hız (TR) | API kalitesi | 24h notu |
|---|---|---|---|
| **Copernicus Data Space Ecosystem (CDSE)** | Çok iyi (CDN AWS/EU) | OData + STAC + openEO + Sentinel Hub Process API | ✅ **Önerilen birincil kaynak** |
| **Google Earth Engine (GEE)** | Eşsiz (sunucusuz) | JS/Python; S2_HARMONIZED, COPERNICUS/DEM, ESA WorldCover hep hazır | ✅ **24 saat build için en güçlü tek seçim** |
| **Sentinel Hub** | İyi | RESTful + WMS/WMTS; CDSE üzerinden ücretsiz kota | ✅ Hızlı görselleştirme tarafı için kullanılabilir |
| **USGS Earth Explorer / NASA Earthdata** | Orta | Toplu indirme yavaş, API token gerek | ⚠️ Sadece ASTER/Landsat için |
| **Planet Labs** | İyi | Akademik Education and Research Program ücretsiz erişim sağlar (başvuru gerekir) | ❌ Onay süreci 24h'i aşar |
| **EO Browser** | İyi | UI ağırlıklı, headless değil | ⚠️ Manuel keşif için |

**Karar:** Google Earth Engine + Python (ee, geemap) ana platform; CDSE/Sentinel Hub API'si yedek raster servisleyici.

### Kapadokya pomza için referans spektral imza
- **USGS Spectral Library v7** (Kokaly et al. 2017, DOI 10.5066/F7RR1WDJ): Rhyolite, obsidian, tuff, pumice türevi camsı silikatlar bulunur; pomzaya en yakın "rhyolite glass" spektrumu kullanılabilir. ✅ İndirilebilir (tek arşiv).
- **ECOSTRESS Spectral Library** (JPL): USGS+ASTER+JHU birleşik kütüphane. ✅ Kullanılabilir.
- **MTA Maden Serisi — Pomza (Eroğlu & Şahiner)**: Türkiye/Nevşehir rezervi 2.2 milyar ton, dünya rezervinin %15.8'i; kimyasal kompozisyon %75'e varan SiO₂. ✅ Bağlamsal referans (mta.gov.tr/v3.0/sayfalar/bilgi-merkezi/maden-serisi/pomza.pdf).
- **MTA Yerbilimleri Harita Görüntüleyici** (yerbilimleri.mta.gov.tr): WMS jeoloji haritası, vektör ruhsat değil. ⚠️ İndirme teknik kısıtlı.
- **Orhan, Dinçer, Akın & Çoban — Nevşehir Pomza Endüstrisi** (Nevşehir Bilim ve Teknoloji Dergisi): Endüstriyel açıdan kapsamlı, spektral imza içermez. ⚠️ Spektral kütüphane değil, jeolojik bağlam.
- **Aksay Kılınç vd. 2016** spesifik referansı `⚠️ Doğrulanamadı` — Aksaray/Avanos pomza atık çalışmaları (Bilimsel Madencilik Dergisi 2020) bulundu ama uzaktan algılama spektral imzası içermez.

### Özet (Bölüm 1)
1. **Sentinel-2 + Sentinel-1 + Copernicus DEM** kombinasyonu pomza+arazi sınıflandırması için 24 saatte mantıklı tek minimum set. ✅
2. ASTER, PRISMA, WV-3 mineralojik ayrım için akademik açıdan üstün ama 24h hackathon için aşırı maliyet. ❌
3. Google Earth Engine + Python tek satırda S2 + DEM + WorldCover'a erişim sağlar — birincil platform önerisi. ✅
4. Kapadokya pomzası için *yayınlanmış spektral imza eğrisi* (JCPSL formatında) doğrulanamadı; USGS Spectral Library "rhyolite glass" en yakın proxy olarak kullanılmalı. ⚠️ Doğrulanamadı.
5. Pomza tespiti için ana ayırt edici sinyal: yüksek albedo + düşük NDVI + B11/B12 SWIR bandında yüksek yansıma + slope < 25° (yatak topoğrafyası).

**Birincil kaynaklar:**
- https://dataspace.copernicus.eu/data-collections/copernicus-sentinel-missions/sentinel-2
- https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
- https://www.usgs.gov/labs/spectroscopy-lab/usgs-spectral-library
- https://www.sciencedirect.com/science/article/abs/pii/S0034425714001084 (Van der Meer et al. — Sentinel-2 for geological applications)
- https://www.mta.gov.tr/v3.0/sayfalar/bilgi-merkezi/maden-serisi/pomza.pdf
- https://www.mdpi.com/2072-4292/8/11/883 (Sentinel-2A MSI + Landsat 8 OLI for geological remote sensing — Sabins ratio)

---

## 2. Uydu Görüntüsü Layer Anatomisi

### Ham spektral bantlar

| Layer | Ölçer | Sensör/Bant | Pomza/Tarım/Maden değeri | Formül |
|---|---|---|---|---|
| **RGB (B2/B3/B4)** | Görünür yansıma | Sentinel-2 10 m | İnsan-okur sanity check; pomza beyazımsı-gri | Doğrudan |
| **NIR (B8)** | Yakın IR | S2 10 m | Bitki örtüsü hızlı tarama (NDVI girdisi) | Doğrudan |
| **Red Edge (B5/B6/B7)** | Kırmızı kenar | S2 20 m | Bitki stresi/erken tarım sinyali — ince ayar | Doğrudan |
| **SWIR1/SWIR2 (B11/B12)** | Kısa dalga IR | S2 20 m | **Kil + silika + karbonat ayrımı; pomza için kritik** | Doğrudan |
| **Thermal (TIRS)** | Yüzey sıcaklığı | Landsat 8/9 100 m | LST = pomza yüksek albedo → düşük gece sıcaklığı | Brightness temp → LST (Planck inversion) |
| **SAR VV/VH** | Geri saçılım | Sentinel-1 10 m | Açık ocak yüzey pürüzlülüğü, kazı izleri | dB = 10·log₁₀(σ⁰) |

### Türetilmiş indeksler — formül + kullanım

| İndeks | Formül | Kullanım | Kritiklik |
|---|---|---|---|
| **NDVI** | (NIR-Red)/(NIR+Red) = (B8-B4)/(B8+B4) | Tarım/bitki örtüsü maskesi | ✅ Zorunlu |
| **EVI** | 2.5·(NIR-Red)/(NIR+6·Red-7.5·Blue+1) | NDVI doygunluk fix | ⚠️ Opsiyonel |
| **SAVI/MSAVI** | (NIR-Red)·(1+L)/(NIR+Red+L), L=0.5 | Çıplak toprak çok ise | ⚠️ Opsiyonel |
| **NDMI / NDWI** | (B8-B11)/(B8+B11) (NDMI); (B3-B8)/(B3+B8) (NDWI) | Toprak/bitki nemi | ✅ Tarım uygunluğu için |
| **BSI (Bare Soil)** | ((B11+B4)-(B8+B2))/((B11+B4)+(B8+B2)) | Açık ocak/verimsiz toprak | ✅ Maden/verimsiz için kritik |
| **NBR** | (NIR-SWIR2)/(NIR+SWIR2) = (B8-B12)/(B8+B12) | Yangın/değişim; rehabilitasyon proxy | ✅ Rehabilitasyon takibi |
| **Iron Oxide Ratio** | B4/B2 | Demir oksit (renkli pomza marker) | ⚠️ İkincil |
| **Clay Ratio (Sabins)** | B11/B12 | Hidroksil-içerikli alterasyon | ✅ Pomza yatağı yan-imza |
| **Ferrous Minerals** | B11/B8 | Fe-içerikli mineraller | ⚠️ İkincil |
| **NDSI (Snow)** | (B3-B11)/(B3+B11) | Kar maskesi (kış görüntüleri) | ⚠️ Sezonal |
| **Albedo / Brightness** | (0.356·B2+0.130·B4+0.373·B8+0.085·B11+0.072·B12-0.0018)/1.016 (Liang) | **Pomza yüksek albedo (>0.3) ana imzası** | ✅ Zorunlu |

### Topografik & fiziksel

| Layer | Kaynak | Çözünürlük | Hackathon notu |
|---|---|---|---|
| **DEM** | Copernicus DEM GLO-30 (TanDEM-X) | 30 m | ✅ GEE'de tek satırla `ee.ImageCollection('COPERNICUS/DEM/GLO30')` |
| **DEM (yedek)** | ASTER GDEM v3 | 30 m | ✅ `projects/sat-io/open-datasets/ASTER/GDEM` |
| **Slope/Aspect** | ee.Terrain.products(dem) | DEM'den türetilir | ✅ GEE 1 satır |
| **Solar Irradiance (GHI)** | Global Solar Atlas / Solargis | 250 m | ✅ ENERGYDATA.INFO Türkiye GeoTIFF (datacatalog.worldbank.org) |
| **PVOUT (PV potansiyel)** | Global Solar Atlas | 1 km | ✅ Aynı kaynak; "verimsiz ama güneşli" karar girdisi |
| **PVGIS** | JRC PVGIS API | Site-bazlı | ✅ REST endpoint, demo için saatlik prod simülasyonu |
| **LST** | Landsat 8/9 ST_B10 / MOD11A1 | 100 m / 1 km | ⚠️ İkincil; hackathon için atlanabilir |
| **Soil Moisture** | SMAP L3 / ESA CCI | 9 km / 25 km | ❌ Çözünürlük çok kaba; tarım kararı için zayıf |

### Zaman serisi / change detection
- **Bi-temporal difference (RGB veya NDVI)**: 2 tarihli görüntü farkı → açık ocak büyümesi.
- **Time-series NDVI trendi**: 12-aylık median composite + lineer regresyon eğimi → rehabilitasyon başarısı.
- **InSAR coherence (Sentinel-1 SLC)**: ❌ 24 saatte yetişmez (SLC işleme ağır).

### Sınıflandırma çıktı layerları
- **CORINE Land Cover 2018**: 100 m, eski. ⚠️
- **ESA WorldCover 10 m (2020/2021)**: 11 sınıf, %75 doğruluk. ✅ **Önerilen ana arazi örtüsü maskesi.** AWS bucket: `s3://esa-worldcover-v200`.
- **Dynamic World V1** (Google): 9 sınıf, 10 m, near-real-time, GEE'de hazır. ✅ **Tarım/built-up dinamik takip için kullanılabilir.**
- **ESA WorldCereal**: Global cropland binary mask (10 m). ✅ Tarım ground-truth zenginleştirmesi.
- **MAPEG ruhsat poligonları**: ⚠️ Doğrulanamadı (vektör halka açık değil — bkz. Bölüm 4).

### Minimum yeterli set — 24 saat scope discipline
**4 katman:** (1) Sentinel-2 L2A median composite (B2,B3,B4,B8,B11,B12) → RGB + NDVI + BSI + Albedo + Sabins ratio aynı taban; (2) Copernicus DEM → slope; (3) Global Solar Atlas GHI/PVOUT raster; (4) ESA WorldCover veya Dynamic World cropland sınıfı.

Bu 4 katman ile rule-based üçlü sınıflandırma mümkün, AI modeli üzerine eklenebilir.

### Özet (Bölüm 2)
1. **Albedo + NDVI + BSI + Slope + GHI** beşlisi minimum yeterli karar setidir. ✅
2. SWIR (B11/B12) bantları pomza ve yan-mineraller için spektral fingerprint sağlar — atlama. ✅
3. Sentinel-1 SAR ekleme marjinal değer, hackathon scope'da opsiyonel. ⚠️
4. Hyperspectral PRISMA hackathonda gerçekçi değil. ❌
5. ESA WorldCover + Dynamic World hazır segmentasyon zemini sağlar; sıfırdan land-cover model eğitmek 24h'e sığmaz. ✅

**Birincil kaynaklar:**
- https://qgis-in-mineral-exploration.readthedocs.io/en/latest/source/remote_sensing/sentinel_data.html (band ratios for mineral mapping)
- https://esa-worldcover.org/en/data-access
- https://dynamicworld.app
- https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_DEM_GLO30
- https://globalsolaratlas.info/
- https://www.mdpi.com/2072-4292/12/18/3028 (Sentinel-2 iron-bearing minerals; B6/B1, B6/B8A ratios)

---

## 3. Üçlü Sınıflandırma — Maden / Tarım Yapılabilir / Verimsiz Güneşli

### Mimari kararı: tek model + 3 head **vs.** 3 ayrı model
**Hackathon önerisi: 3 ayrı binary rule-based maske + bir CNN/U-Net "pomza var mı" head'i.**
- Multi-task U-Net (1 encoder + 3 decoder) literatürde geçerli ama eğitim verisi yokluğunda overfit kaçınılmaz.
- **Pratik yol:** (a) "tarım yapılabilir" = ESA WorldCereal cropland mask + NDVI > 0.3 history; (b) "verimsiz güneşli" = NDVI < 0.2 + slope < 15° + GHI > 1700 kWh/m²/yıl + WorldCover "bare/sparse"; (c) "pomza var" = küçük U-Net (Sentinel-2 13-bant input) + transfer öğrenmiş torchgeo ağırlığı.
- ✅ 24 saat için kullanılabilir.

### "Verimsiz ama güneşli" operasyonel tanımı
Hackathonda kullanılacak **rule-based eşik öneri seti** (literatür + Türkiye saha pratiği bileşimi):
- NDVI 12-ay medyan < 0.2 (çıplak/sparse)
- Slope < 15° (PV güvenli)
- GHI > 1750 kWh/m²/yıl (Türkiye orta-yüksek; Nevşehir bölgesinde ~1750-1850 kWh/m²/yıl, kaynak: Global Solar Atlas Türkiye fact-sheet)
- Toprak derinliği < 50 cm proxy: BSI > 0.1 + WorldCover "bare/sparse vegetation"
- Aşağıdaki sınırların hepsi **Kapadokya/Nevşehir için spesifik akademik ref ile doğrulanamadı**; ⚠️ Doğrulanamadı.
- Genel solar PV site-suitability literatüründe yaygın eşikler benzer (slope <15°-20°, GHI threshold bölgeye göre).

### Tarım uygunluk veri katmanları
- **FAO GAEZ v4** (gaez.fao.org): 50+ ürün için suitability + attainable yield; Türkiye dahil global. Çözünürlük 30 arc-sec (~1 km) — Hackathon için **yeterli rule-based**, pixel-level fine değil. ✅
- **TAGEM Ülkesel Toprak Bilgi Sistemi** (arastirma.tarim.gov.tr/toprakgubre): pH, EC, Organik karbon, P, K, doku, bünye haritaları. ✅ Türkiye için var ancak indirme/web servis erişimi ⚠️ Doğrulanamadı; web portal halka açık olabilir.
- **5403 Sayılı Toprak Koruma ve Arazi Kullanımı Kanunu** + Arazi Uygunluk Sınıflaması (S1–S4 / N): Resmi sınıflama metodu. ✅ Sıralama mantığı için referans, hackathon için özel veri seti yok.

### Özet (Bölüm 3)
1. 24 saat için 3 binary rule-based + 1 CNN head karması en sağlıklı stratejidir. ✅
2. "Verimsiz güneşli" eşikleri: NDVI < 0.2, slope < 15°, GHI > 1750 kWh/m²/yıl, BSI > 0.1 — başlangıç noktası. ⚠️ Saha kalibrasyon gerekir.
3. FAO GAEZ v4 global tarım suitability raster'ı GEE'de hazır kullanım için eklenmeli. ✅
4. TAGEM ülkesel toprak haritası akademik referans sağlar; API erişimi belirsiz. ⚠️
5. Multi-task tek-model mimarisi 24h'de overfit eder; modüler yaklaşım önerilir.

**Birincil kaynaklar:**
- https://www.fao.org/gaez/en
- https://gaez.fao.org/datasets/hqfao::gaez-suitability-and-attainable-yield/about
- https://arastirma.tarim.gov.tr/toprakgubre
- https://www.tarimorman.gov.tr/Belgeler/Mevzuat/Talimatlar/ToprakAraziSiniflamasiStandartlariTeknikTalimativeIlgiliMevzuat.pdf
- https://datacatalog.worldbank.org/search/dataset/0039835/turkey-solar-irradiation-and-pv-power-potential-maps
- https://documents1.worldbank.org/curated/en/466331592817725242/pdf/Global-Photovoltaic-Power-Potential-by-Country.pdf

---

## 4. Ground Truth & Etiketli Veri

### MAPEG ruhsat verisi
- **e-Maden platform** (mapeg.gov.tr/Sayfa/eMaden): GeoServer üzerinde WCS/WMS/WFS standartlarında servisler kurulduğu DUYURULUYOR; ancak halka açık otomatik vektör (shapefile/GeoJSON) indirme uç-noktası `⚠️ Doğrulanamadı`. Sektör uygulayıcıları (YTK'lar) için kapalı.
- **e-Devlet "Maden Ruhsatı Doğrulama / Sorgulama"**: Sadece tek ruhsat sorgulaması (turkiye.gov.tr/mapeg-ruhsat-safhasi-sorgulama). Toplu poligon **yok**. ❌
- **MTA Yerbilimleri Harita Görüntüleyici** (yerbilimleri.mta.gov.tr): Web GIS, jeoloji + maden noktasal görüntüleyici; vektör indirme zorlu. ⚠️
- **Workaround:** Kapadokya bölgesi için ~10–20 ruhsat alanı manuel olarak Sentinel-2 RGB üzerinden polig. çizilebilir (QGIS + EO Browser); hackathon için yeterli pozitif örnek. ✅
- **Pomza Export, Map-Stone, Emin Pomza, Miner Madencilik, BlokBims** gibi firmaların kendi ocak konumları kamuya açık (web sitesi; bkz. Bölüm 8).

### Hazır etiketli veri seti — pomza yok ama ilişkili açık-pit / mineral
| Veri seti | Boyut | Sentinel-2? | Pomza mı? | Hackathon değeri |
|---|---|---|---|---|
| **EuroMineNet** (2025, arXiv 2510.14661) | EU çapında 2015–2024, multitemporal mining footprint | Sentinel-2 | Hayır, generic mining | ✅ Transfer learning baseline |
| **MineSegSAT** (2023, arXiv 2311.01676) | 134 tile Western Canada, 12-band S2, SegFormer | Sentinel-2 | Hayır | ✅ Code+weights mevcut, fine-tune adayı |
| **BrazilDAM** (2020, arXiv 2007.01076) | Mine + tailings dam, S2+L8 | Sentinel-2 | Hayır | ⚠️ |
| **Mining-Detector** (Amazon Mining Watch, GitHub) | Artisanal gold mines | Sentinel-2 | Hayır | ⚠️ |
| **BigEarthNet** (590k S2 patches, 43 CORINE class) | Avrupa çapında, multilabel scene | Sentinel-2 (12-bant) | "Mineral extraction sites" sınıfı içerir | ✅ Pretraining baseline |
| **EuroSAT** (27k patch, 10 sınıf, 13-bant) | Avrupa | Sentinel-2 | Hayır | ✅ Sanity check encoder pretrain |
| **SEN12MS** (180k triplet S1+S2+MODIS-LC) | Global | Sentinel-1+2 | Hayır | ✅ Multi-modal füzyon baseline |
| **SSL4EO-S12** (Wang et al. 2023) | Global, self-supervised | S1+S2 | Hayır, ancak Sentinel-2 13-bant | ✅ **Önerilen pretraining** (torchgeo ResNet50 weights) |

**Hackathon stratejisi:** SSL4EO-S12 ResNet50 backbone (torchgeo) + manuel ~30 pozitif (Kapadokya pomza ocak) + 100 negatif (köy/tarım/su) etiket → 24h içinde fine-tune mümkün. ✅

### Negative sampling stratejisi
- **UNESCO Göreme buffer**: **Maskelenmiş** (sınıflandırma dışı, kullanıcıya kırmızı flag) olmalı. Mevcut iç-bölge taşları zaten tüf+pomza karışımıdır; buradaki spektral imza pozitif tetiklerse model gerçek ocakları yanlış pozitiflerle karıştırır.
- **Ek negatif sınıflar:** Tarım, su, yerleşim, açık tüf yüzeyi (peri bacaları), volkanik kayaç düzlüğü.
- ✅ Strateji 24 saat için uygulanabilir.

### Özet (Bölüm 4)
1. MAPEG ruhsat poligonları halka **açık değil** (e-Devlet birim sorgu var, toplu vektör yok). ❌ Workaround: manuel etiketleme.
2. Pomza-spesifik etiketli açık veri **bulunmuyor** (bilinen literatür/ Kaggle taraması sonrasında). ⚠️
3. **EuroMineNet + MineSegSAT** açık-pit transfer-learning baseline'ı sağlar. ✅
4. **SSL4EO-S12 ResNet50** (torchgeo) Sentinel-2 13-bant pretrained backbone önerilen pretrain. ✅
5. UNESCO Göreme buffer-zone negatif/maskelenmiş muamele edilmeli. ✅

**Birincil kaynaklar:**
- https://www.mapeg.gov.tr/Sayfa/eMaden
- https://www.turkiye.gov.tr/maden-ve-petrol-isleri-genel-mudurlugu
- https://arxiv.org/abs/2510.14661 (EuroMineNet)
- https://arxiv.org/abs/2311.01676 (MineSegSAT)
- https://arxiv.org/abs/2007.01076 (BrazilDAM)
- https://arxiv.org/abs/2001.06372 (BigEarthNet)
- https://github.com/microsoft/torchgeo (SSL4EO-S12 weights)

---

## 5. Model Mimarisi — 24 Saatte Eğitilebilir

### Aday model karşılaştırması

| Model | Pretrained ağırlık | Sentinel-2 13-bant? | Hackathon eğitim süresi (T4 GPU) | Karar |
|---|---|---|---|---|
| **U-Net (ResNet50 backbone, SSL4EO-S12 MoCo)** | TorchGeo `ResNet50_Weights.SENTINEL2_ALL_MOCO` | Evet, 13-bant | ~2-4 saat fine-tune | ✅ **Önerilen** |
| **DeepLabV3+ (ResNet50)** | ImageNet pretrained, S2'ye band adapter | RGB başlangıç + ek 10 kanal init lazım | ~3-5 saat | ⚠️ Daha karmaşık |
| **SegFormer (MIT-B0/B1)** | MineSegSAT örneği var, 12-bant | Evet (B10 atılır) | ~2-4 saat | ✅ Modern alternatif |
| **SatMAE / Scale-MAE** | Self-supervised foundation | Evet | Fine-tune ~4-6 saat | ⚠️ Setup zor |
| **Prithvi-EO-1.0/2.0 (NASA-IBM, HuggingFace)** | HLS 6-bant (B,G,R,NIR,SWIR1,SWIR2) | **Sadece 6-bant**, 13-bant değil | Setup ~2-3h, fine-tune ~2-4h | ✅ Yangın/sel için ispatlı; mining adaptasyonu yeni; segmenter için geçerli aday |
| **Plain CNN scratch** | — | — | 6-12 saat eğitim, az veri = overfit | ❌ |

**Karar:** **TorchGeo + U-Net (ResNet50, SSL4EO-S12 MoCo weights)** birincil; **Prithvi-EO-1.0** (ibm-nasa-geospatial/Prithvi-EO-1.0-100M) yedek. Prithvi 6-bant (Blue, Green, Red, Narrow NIR, SWIR1, SWIR2) → Sentinel-2'den B2, B3, B4, B8A, B11, B12 mapping yapılır.

### TorchGeo ile pretraining — somut kod örneği
```python
import timm
from torchgeo.models import ResNet50_Weights
weights = ResNet50_Weights.SENTINEL2_ALL_MOCO
model = timm.create_model("resnet50", in_chans=weights.meta["in_chans"], num_classes=2)
model.load_state_dict(weights.get_state_dict(progress=True), strict=False)
```
✅ TorchGeo Lightning DataModule + Trainer ile 24h içinde geçerli. 120+ pretrained weight (Landsat, NAIP, S1, S2) hazır.

### Hyperspectral PRISMA?
- 240 bant, 30 m, 30×30 km swath; HDF5 → GeoTIFF dönüşümü gerekli (rPRISMA paketi).
- ASI portal kayıt + tile seçimi + atmospheric correction uzun sürer.
- ❌ **24 saatte yetişmez.** Sentinel-2 + S1 füzyonu yeterli.

### Özet (Bölüm 5)
1. **TorchGeo + U-Net + ResNet50 (SSL4EO-S12 MoCo)** Sentinel-2 13-bant için en hızlı transfer öğrenir. ✅
2. **Prithvi-EO-1.0** alternatif, 6-bant adaptasyonu gerektirir. ✅
3. SegFormer (MineSegSAT örneği) modern alternatif. ✅
4. PRISMA hyperspectral 24 saatte yetişmez. ❌
5. Veri = ~100-300 etiketli patch yeterlilik (transfer learning ile); manuel polig. + augmentation strategy zorunlu.

**Birincil kaynaklar:**
- https://torchgeo.readthedocs.io/en/stable/tutorials/pretrained_weights.html
- https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-1.0-100M
- https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-1.0-100M-sen1floods11
- https://github.com/microsoft/torchgeo
- https://arxiv.org/abs/2111.08872 (TorchGeo paper)
- https://arxiv.org/abs/2412.02732 (Prithvi-EO-2.0)

---

## 6. Rota Optimizasyonu (Modül B)

### Hazır Python implementasyonları

| Tool | PRP destekler? | Yakıt/eğim modeli | Hackathon notu |
|---|---|---|---|
| **Google OR-Tools VRP** | Sınıflanmış VRP/CVRP/TW; PRP doğal değil ama travel cost matrisine fuel-eğim ağırlığı eklenebilir | Manuel | ✅ **Önerilen** — Python API, solver dahil, dokümantasyon güçlü |
| **VROOM** | CVRP+TW; Hızlı C++; Python wrapper | Distance/duration only | ✅ Hızlı bin-packing; PRP eklenmez |
| **Pyomo + CBC/HiGHS** | MIP formülasyonu yazılabilir | Custom | ⚠️ 24h'de kurmak zor |
| **PRP exact (akademik)** | ALNS, MathHeuristic | Demir-Bektaş-Laporte 2014 | ❌ Açık-kaynak referans implementasyonu sınırlı |
| **OSRM** | Pure shortest-path engine, multi-source | Yok | ✅ Mesafe/süre matrisi için |
| **GraphHopper** | Hem routing hem Route Optimization API (ücretli) | Built-in elevation (SRTM), elevation-aware | ✅ Açık-kaynak, kendi sunucuda; eğim entegre edilmiş |

**Karar:** **OSRM/GraphHopper** mesafe-süre matrisi → **OR-Tools** CVRP'ye payload-aware fuel cost arc weight'i olarak besle. Eğim opsiyonel olarak GraphHopper'tan elevation profile + Demir-Bektaş-Laporte fuel formülü ile post-process.

### Yakıt tüketim modeli — pratik formül
**Demir, Bektaş, Laporte (2014)** Comprehensive Modal Emissions Model (CMEM)'e dayalı formül:

`F = λ · (k·N·V·d/v + M·γ·α·d + β·γ·d·v²)`

Parametreler:
- λ = ξ/(κ·θ), ξ=1, κ=heating value, θ=fuel-to-density
- k=engine friction (0.2 kJ/rev/L), N=engine speed (rev/s), V=engine displacement (L)
- M=total mass (kg), α = a + g·sin(δ) + g·fr·cos(δ); δ = **road grade (eğim)** — DEM'den hesaplanır
- β = 0.5·Cd·ρ·A; v=speed, d=distance

**Bu formül slope (δ) içerir → DEM tabanlı eğim eklenmiş PRP doğal olarak modellenebilir.** Lai, Costa, Demir et al. 2021 (arXiv 2105.09229) Pollution-Routing Problem with Speed Optimization and Uneven Topography paper'ı tam buna karşılık gelir.

### DEM tabanlı eğim eklenmiş VRP
- **OSRM eco-routing fork** (Ghosh et al. 2020, arXiv 2011.13556): OSRM + CGIAR-CSI elevation. Açık-kaynak referans. ✅
- **GraphHopper**: Built-in elevation (SRTM/CGIAR), API ile eğim profili çıkar. ✅ En pratik.
- **Akademik solver (PRP-SO with elevation)**: Lai et al. 2021 branch-and-price; hackathonda implement edilemez. ❌

### Özet (Bölüm 6)
1. **OSRM/GraphHopper (mesafe matrisi) + OR-Tools CVRP (payload-aware arc weight) + Demir et al. 2014 formülü ile post-process eğim/yakıt** önerilen tek satırlı stack. ✅
2. Tam Pollution-Routing Problem ALNS implementasyonu 24h'de yetişmez; CMEM tabanlı yaklaşık çözüm yeterli. ⚠️
3. GraphHopper eğim entegre çözüm sağlar (open-source). ✅
4. Bektaş & Laporte 2011 ile başla, Demir et al. 2014 review paper'ı parametre değerleri için altın referans. ✅
5. Fuel cost demonstration için synthetic 5-müşteri × 2-fabrika × 3-saha mini örnek 2-3 dakikada çözülür.

**Birincil kaynaklar:**
- https://developers.google.com/optimization/routing (OR-Tools VRP)
- https://github.com/Project-OSRM/osrm-backend
- https://www.graphhopper.com/
- https://arxiv.org/abs/2105.09229 (PRP with elevation, Lai/Demir/Van Woensel 2021)
- https://arxiv.org/abs/2011.13556 (Eco-Routing OSRM with elevation)
- https://www.scribd.com/document/566333022/ (Demir, Bektaş, Laporte 2014 Bi-Objective PRP — parametre tablosu)
- https://www.cirrelt.ca/documentstravail/cirrelt-2014-26.pdf (Fleet Size and Mix PRP, Koç & Bektaş 2014)

---

## 7. Sürdürülebilirlik & Mevzuat Çapaları

### Maden Kanunu 3213 + ÇED Yönetmeliği 2022
- **ÇED Yönetmeliği** 29.07.2022 / 31907 sayılı Resmi Gazete (mülga 2014 yönetmeliği yerine).
  - **EK-I**: Zorunlu ÇED Raporu projeleri (büyük ölçek).
  - **EK-II**: Seçme-Eleme Kriterleri tabi projeler ("Çevresel Etki Önemlidir/Önemsizdir" karar).
  - Kapadokya pomza ocakları **EK-II'de** maden grubu II(a) olarak değerlendirilir; eşik 100.000 m³/yıl üstü ÇED kararı zorunlu olabilir (proje boyutuna bağlı).
- **Maden Kanunu 3213, Madde 7**:
  - "İçme ve kullanma suyu rezervuarının max su seviyesinden itibaren 1000-2000 m'lik şeritte galeri usulü patlatma yasak."
  - "2000 m sonrası koruma alanında ÇED'e göre uygun bulunan maden istihracı ve tesis yapılabilir."
  - Yerleşim mesafe sınırlaması Maden Yönetmeliği kapsamında değerlendirilir; **standart sayısal eşik yönetmelikte spesifik tek değer olarak verilmemiş** — proje bazında ÇED değerlendirmesi.
- **Hassas Yöre / EK-V** (eski yönetmelik terminolojisi): Korunan alanlar, milli parklar, dünya mirası. Göreme Milli Parkı bu kapsamdadır. ✅

### UNESCO Göreme Milli Parkı buffer-zone — GIS verisi
- **UNESCO whc.unesco.org/en/list/357/maps/**: Resmi nominasyon dosyası harita; **ESRI ArcGIS API üzerinden web map**, georeferenced polygons "GIS data alındığında yayınlanacak" notu var → **vektör shapefile/GeoJSON kamuya açık değildir**. ⚠️
- **OpenStreetMap**: "Goreme National Park" relation/way arama; bilfiil ~100 km² alanı kapsayan polygon mevcut; OSM Overpass API ile çekilebilir. ✅ **Hackathon önerisi: OSM relation indir + buffer 500-1000 m ekle.**
- **T.C. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı**: "Cultural and Tourism Conservation and Development Area" 2004'te yeni sınır; resmi Türkiye CBS portalı erişimi belirsiz. ⚠️
- **WCMC dataset** (world-heritage-datasheets): UNESCO+WCMC ortak metadata, vektör değil. ⚠️
- **GADM / Protected Planet (WDPA)**: WDPA "Goreme National Park" polygon mevcut, GeoJSON indirilebilir. ✅ **En pratik açık kaynak.**

### CBAM 2026 + Türkiye ETS pilot dönemi — pomza için ne reporting?
- **CBAM** (EU 2023/956): 1 Ocak 2026 itibarı definitive phase başladı. Kapsam: çimento, demir-çelik, alüminyum, gübre, elektrik, hidrojen. **Pomza/bims doğrudan CBAM kapsamında DEĞİL** ⚠️ — ancak müşteri tarafında çimento puzzolan katkısı olarak kullanılırsa dolaylı etki var. 2030'a kadar tüm EU ETS sektörleri kapsanması bekleniyor (Wikipedia EU CBAM).
- **Türkiye İklim Kanunu 7552** (9 Temmuz 2025'te yayımlandı): **2026'da pilot ETS başlıyor**, idari ceza %80 indirimli. Kapsam: enerji-yoğun sektörler (enerji, metal, çimento, gübre). Pomza üreticileri çimento sektörü ile dolaylı bağlantılı.
- **MRV altyapı şartları**: Emission permit zorunlu (3 yıl içinde), bağımsız doğrulama, dönemsel raporlama. Detay yönetmelik 22 Temmuz 2025'te taslağa açıldı. Pomza KOBİ'leri için Scope 1 (yakıt: kamyon dizel, jeneratör) + Scope 2 (elektrik) ölçümü → MRV sistemi gerekir.
- **Pomza spesifik metrikler:** Kamyon dizel litre/ton, fabrika elektrik kWh/m³, patlatma CO₂. Bu zaten PomzaScope'un Modül B (yakıt-optimal rota) çıktısıyla doğrudan örtüşür. ✅ — pitch'te güçlü açı.

### Rehabilitasyon ihtiyaç skoru — akademik baseline
- **Werner et al. (UNSW 2013, WorldView-2)**: NDVI tabanlı mine rehabilitation monitoring; aynı yaklaşım Sentinel-2'ye taşınabilir. ✅
- **Hengshanli mine (Sentinel-2A 2019–2024 + UAV, 2025 paper)**: NDVI Q6=0.31 (low slope) vs 0.40-0.43 (mid-steep slopes); **slope-stratified NDVI** rehabilitation indicator. ✅ Direkt uygulanabilir.
- **Springer Env Processes 2025 (NDVI+NDMI + SOM ML)**: rehabilitate vs natural reference NDVI/NDMI komparasyon; SOM interpolation. ✅
- **IFC Performance Standard 6** (Biyoçeşitlilik): "no net loss" prensibi; rehabilitasyon hedefi quantitatif değil — kalitatif framework. ⚠️ Skor için doğrudan formül yok.
- **Avustralya WA Mining Rehabilitation Fund (MRF) / QLD PRCP**: Düzenleyici şablonlar; metodoloji açık kaynak. ✅ Referans.

**Önerilen rehabilitasyon ihtiyaç skoru (RIS) formülü (synthetic, hackathon için):**
`RIS = w1·(1 - NDVI_current/NDVI_reference) + w2·NDVI_slope(neg.trend) + w3·BSI_current + w4·DEM_disturbance`

⚠️ Doğrulanmış akademik formül değil — saha kalibrasyonu gerekir.

### Özet (Bölüm 7)
1. UNESCO Göreme buffer GIS verisi resmi (UNESCO) olarak halka açık değil; **OSM + WDPA** workaround. ⚠️→✅
2. Maden Kanunu 3213 Madde 7 — su rezervuarı 2000 m kuralı + ÇED EK-II zorunluluğu pomza ocakları için kritik. ✅
3. CBAM pomza'yı doğrudan kapsamıyor ama Türkiye ETS pilot 2026 dolaylı kapsama başlıyor. ⚠️
4. Pomza Scope 1+2 MRV: kamyon dizel + fabrika elektrik + patlatma CO₂ — PomzaScope ile doğrudan örtüşür. ✅
5. Rehabilitasyon skoru için NDVI time-series (slope-stratified) literatürde yerleşmiş baseline'dır. ✅

**Birincil kaynaklar:**
- https://www.resmigazete.gov.tr/eskiler/2022/07/20220729-2.htm (ÇED Yönetmeliği 2022)
- https://orgtr.org/maden-kanunu-3213-sayili-kanun/ (Maden Kanunu)
- https://whc.unesco.org/en/list/357/ + https://whc.unesco.org/en/list/357/maps/
- https://icapcarbonaction.com/en/news/turkiye-adopts-landmark-climate-law-paving-way-national-ets
- https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en
- https://www.acsmp.unsw.edu.au/satellite-based-mine-rehabilitation-monitoring-using-worldview-2-imagery
- https://www.sciencedirect.com/science/article/abs/pii/S0301479725039581 (Hengshanli mine S2+UAV NDVI)
- https://link.springer.com/article/10.1007/s40710-025-00781-3 (NDVI+NDMI+SOM rehab)
- https://www.protectedplanet.net (WDPA Göreme polygon kaynağı)

---

## 8. Pilot Müşteri & Ticarileşme Doğrulaması

### Miner Madencilik (Avanos + Niğde)
- Web sitesi: miner.com.tr — Avanos (Nevşehir) merkez fabrika + Niğde maden ocakları.
- Kuruluş 1994, kalsit ve pomza üretimi.
- Kapasite: **200.000 ton/yıl** (mikronize ürün).
- Tesis: 5.000 m² kapalı + 15.000 m² açık.
- Kamyon sayısı / lojistik partneri: **kamuya açık değil** ⚠️
- Mikronize pomza müşteri sektörleri: tekstil (denim taşlama), diş hekimliği, tarım, endüstriyel sabun, boya/PVC.

### BlokBims (Ertaş Grup, Çardak Köyü Nevşehir)
- Web sitesi: blokbims.com.tr / ertasgrup.com / blokbimsmadencilik.com
- Kuruluş 1997-1998 (üretim başlangıcı).
- Kapasite: **220.000-300.000 adet/gün** (kaynaklar arasında değişiyor; 2024-2025 itibarıyla 300.000).
- Tesis: **35.000 m² kapalı + 1.200.000 m² açık** alan (en güncel rakam).
- Nakliye filo: **150 araçlık kendi filo** (önemli — yakıt rotası için ideal pilot müşteri).
- Bayi ağı: 160 bayi/satıcı, 10 kişilik teknik ekip.
- İhracat: 47 ülke, ABD/İngiltere/Suudi Arabistan distribütörlük.
- Çevre: 500 kW güneş enerjisi santrali (2014 kuruluş) — yenilenebilir bilinci yüksek; PomzaScope solar entegrasyonu için strong fit.

### Diğer pomza KOBİ'leri (Türkiye geneli)
- **Pomza Export A.Ş.** (1969, İzmir/Manisa/Erzincan): 50 yıllık tecrübe, kromozma elektrik araç dönüşümü ve güneş paneli yatırımı. ✅
- **Map-Stone** (Niğde Altunhisar): Yerli sermaye, sürdürülebilir madencilik vurgusu. ✅
- **Emin Pomza**: "Doğa-duyarlı pomza madenciliği". ⚠️
- **TÜRKİYE pomza rezervi:** 2.2 milyar ton, dünya rezervinin %15.8'i; Nevşehir Türkiye rezervinin %17'si + ruhsat sayısının %20'si (MTA, Orhan et al.).

### B2B SaaS benchmark fiyatlandırma — Türk MineTech / AgriTech
- **`⚠️ Doğrulanamadı`**: Türk pomza KOBİ B2B SaaS aylık fiyat benchmark veri seti **bulunmadı**. Genel TR AgriTech (örn. Tarla.io, Doktar) fiyatları ~1.500-15.000 TL/ay arasında raporlanıyor ancak doğrulanmış kaynak az.
- **Pratik öneri (hackathon pitch için):** "Pilot 3 ay ücretsiz + 7.500-25.000 TL/ay tier (üretim hacmi bağımlı)" konuşulabilir ama saha doğrulaması zorunlu.
- AgriTech KOBİ Tarla.io public pricing ⚠️ doğrulanamadı.

### TÜBİTAK 1512 BiGG 2026 dönem
- **2026-1 takvimi (uygulayıcı kuruluş kaynağı: BiGG Masters):**
  - Aşama 1 hızlandırma: 15 Nisan – 1 Temmuz 2026
  - Aşama 2 başvuru: 15 Haziran – 3 Temmuz 2026
  - Belge ulaştırma: 10 Temmuz 2026
  - Panel değerlendirme: 13 Temmuz – 28 Ağustos 2026
  - Desteklenenlerin duyurusu: 1-4 Eylül 2026
  - Şirket kurulumu son tarih: 30 Eylül 2026
- **Destek tutarı:** 1.350.000 TL (2026 itibarıyla), %3 hisse karşılığı TÜBİTAK BiGG Fonu yatırımı.
- **Şartlar:** 18 yaş üstü öğrenci/mezun (ön lisans-doktora), şirket ortaklığı yok, daha önce 1512/1812/Teknogirişim sermaye desteği almamış.
- **Tematik alanlar:** Yıllık en az 1 çağrı genel + bir "Yeşil Büyüme" çağrı planlanır. **"Akıllı Tedarik Zinciri / Madencilik Dijitalleşmesi" doğrudan ayrı tematik alt başlık olarak doğrulanamadı** ⚠️ — ancak Sanayi-Teknoloji Bakanlığı 2024–2030 Sanayi Stratejisi kapsamında ilgili olabilir.

### Özet (Bölüm 8)
1. **BlokBims (Ertaş Grup) ideal pilot müşteri**: 150 kamyon kendi filo + 300k adet/gün + 47 ülke ihracat + güneş enerjisi yatırımı. ✅
2. **Miner Madencilik** ikincil pilot: çift saha (Avanos + Niğde) yakıt rota optimizasyonu için demo'su güçlü. ✅
3. Türk pomza KOBİ B2B SaaS fiyat benchmark **veri yok**; saha-bazlı görüşme zorunlu. ⚠️
4. **TÜBİTAK BiGG 2026-1 takvimi**: Aşama 1 başlangıcı 15 Nisan 2026; PomzaScope hackathon sonrası direkt başvuru penceresi açık. ✅
5. **2026 BiGG destek**: 1.35 M TL / %3 hisse — proje ölçeği için uygun.

**Birincil kaynaklar:**
- https://www.miner.com.tr
- http://www.ertasgrup.com / https://www.blokbims.com.tr
- https://www.blokbimsmadencilik.com
- https://www.pomzaexport.com/en/
- https://www.map-stones.com/
- https://tubitak.gov.tr/en/funds/sanayi/ulusal-destek-programlari/1512-entrepreneurship-support-program
- https://biggmasters.com/takvim
- https://www.mta.gov.tr/v3.0/sayfalar/bilgi-merkezi/maden-serisi/pomza.pdf

---

## 24 Saat İçin Önerilen Stack (Build Reçetesi)

| Katman | Seçim | Neden |
|---|---|---|
| **Sensör** | Sentinel-2 L2A (10–60 m, 13 bant) + Sentinel-1 GRD (yedek) | 5-day revisit, 13 bant, ücretsiz, hazır pretrained ağırlıklar |
| **Veri platformu** | **Google Earth Engine** (Python) + Sentinel Hub (görselleştirme) | Sıfır-indirme cloud-native; ESA WorldCover, Dynamic World, Copernicus DEM, FAO GAEZ tek satır erişim |
| **DEM / topografya** | Copernicus DEM GLO-30 (TanDEM-X) | TR'de yüksek doğruluk, GEE'de hazır |
| **Solar** | Global Solar Atlas GHI/PVOUT (250 m / 1 km) GeoTIFF | Bedava, Türkiye için optimize |
| **Tarım maskesi** | ESA WorldCereal + FAO GAEZ v4 + Dynamic World cropland | Hazır, 10 m, near-realtime |
| **Land cover** | ESA WorldCover 10 m (2021) | %75 doğruluk, 11 sınıf |
| **Pomza tespiti modeli** | TorchGeo U-Net (ResNet50 backbone, **SSL4EO-S12 MoCo** Sentinel-2 13-bant pretrained) — fine-tune ~30 manuel etiketli pozitif + 100 negatif | Pretrained 13-bant tek seçim, T4 GPU 2-4 saat |
| **Üçlü sınıflandırma** | Rule-based 3 binary mask (Pomza CNN + Tarım WorldCereal + Verimsiz-güneşli NDVI<0.2 ∧ slope<15° ∧ GHI>1750 ∧ BSI>0.1) | 24h scope discipline |
| **Rota/yakıt modülü** | **OSRM** (mesafe matrisi) + **OR-Tools CVRP** Python (capacity, time-window) + **Demir-Bektaş-Laporte 2014 CMEM formülü** ile post-process eğim/yakıt | Tüm bileşenler open-source |
| **DEM-aware eğim** | GraphHopper (built-in elevation profile) opsiyonel | Açık-kaynak, kolay deploy |
| **UNESCO buffer red flag** | OSM Overpass API "Goreme National Park" relation + WDPA polygon + 500 m buffer | Vektör halka açık değil → workaround |
| **Rehabilitasyon takibi** | NDVI 12-aylık median time-series (Sentinel-2) + slope-stratified (Hengshanli baseline) | Demo-grade, 2 dakikada GEE'de hesaplar |
| **UI** | **Streamlit** (Python) + **Folium / Leafmap** harita + Plotly grafik | Tek dilli (Python), 2-3 saatte canlı dashboard |
| **Backend** | FastAPI (eğer modüller ayrı servis) veya doğrudan Streamlit içi | Hackathon basit |
| **Görselleştirme** | Leafmap (geemap+folium) — GEE layer toggle | "Layer-by-layer" demo etkili |

### 24 Saat Zaman Çizelgesi (öneri)
| Saat | Faaliyet |
|---|---|
| 0-2 | GEE auth, S2 + DEM + WorldCover composite hazır; Nevşehir AOI tanımı |
| 2-4 | Manuel etiketleme (QGIS): 30 pozitif pomza ocak + 100 negatif; UNESCO Göreme polygon (OSM) eklenir |
| 4-7 | TorchGeo U-Net (SSL4EO-S12) fine-tune (Colab T4) |
| 7-9 | Rule-based 3 binary mask (tarım, verimsiz-güneşli, aktif maden) |
| 9-12 | Streamlit harita + üçlü çıktı görselleştirme |
| 12-15 | OSRM kurulumu (Türkiye OSM bbox'ı) + OR-Tools CVRP synthetic 5-müşteri × 3-saha example |
| 15-18 | Demir et al. CMEM formülü → post-process; UI'da fuel saving % gösterimi |
| 18-20 | NDVI rehabilitasyon time-series + UNESCO buffer red flag |
| 20-22 | Pitch deck (Miner/BlokBims pilot, BiGG 2026-1 takvimi vurgu) |
| 22-24 | Cilalama, demo video, sunum prova |

---

## Kapanış Notu — Risk ve Uyarılar
- **MAPEG ruhsat poligonları toplu olarak halka açık değil** — bu hackathonda manuel etiketleme zorunlu. Ürün ticarileşmesi sırasında resmi YTK işbirliği gerekir.
- **Pomza spesifik açık etiketli veri seti yok** — transfer learning + domain expert manuel etiket tek yol.
- **Kapadokya pomzasına ait yayınlanmış spektral imza eğrisi doğrulanamadı** — USGS Spectral Library "rhyolite glass" proxy kullanılır, saha kalibrasyonu gerek.
- **CBAM doğrudan pomza kapsamıyor** ama Türkiye ETS pilot 2026 üzerinden çimento sektörü zinciri PomzaScope için fırsat. Pitch'te "İklim Kanunu 7552 + ETS pilot" çapaları kullanılmalı.
- **24 saat scope discipline kritik**: PRISMA hyperspectral, ASTER, gerçek InSAR coherence, multi-task neural network, Pollution-Routing exact branch-and-price gibi "gözüpek" tekniklerden uzak durulmalı; **bunların yerine hazır pretrained + rule-based + open-source çözücü** kullanılmalı. ✅ Yukarıdaki stack tam bu disiplini sağlar.

---

*Doğrulanamayan bilgiler "⚠️ Doğrulanamadı" olarak işaretlendi. Kritik ürün kararları öncesi MAPEG, MTA Uzaktan Algılama Merkezi, BlokBims/Miner ile direkt görüşme şarttır.*