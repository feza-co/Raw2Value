# PomzaScope — Master Teknik Rapor

> **Proje:** Ahmet Abi'nin "Uydu+AI Pomza Alanı Tespiti + Rota Optimizasyonu" Fikri
> **Hazırlayan:** Tuna & Team Feza (Çankaya Üniversitesi)
> **Etkinlik:** Kapadokya Hackathon 2026 — *Cave2Cloud: Kapadokya'dan Global Pazara*
> **Tarih:** 1 Mayıs 2026
> **Versiyon:** v1.0 — Sade kapsam
> **Çerçeve:** Yalnızca pomza odaklı; pomza saha tespiti + pomza taşıma rotası. Başka uygulama alanı (tarım vb.) yok.
> **Coğrafi odak:** Nevşehir / Avanos derin demo
> **Müşteri:** Pomza üretici şirketler (B2B SaaS)

---

## 0. YÖNETİCİ ÖZETİ

PomzaScope, Türkiye'nin dünya lideri olduğu pomza üretiminin "ham mal düşük FOB fiyatı + sezgisel lojistik" sıkışmasını teknolojiyle çözmek için kurulan **iki katmanlı yapay zekâ platformudur**. Modül A çoklu uydu görüntülerinden makine öğrenmesiyle pomza alanlarını tespit eder ve değişimini izler; Modül B bu sahalardan üretici fabrikalara ham pomza taşıma rotalarını yakıt ve CO₂ minimize edecek şekilde optimize eder. Ürünün başka bir uygulama alanı yoktur — pomza üreticisinin saha-fabrika-müşteri zincirinin sadece başını dijitalleştirir. Hedef müşteri Nevşehir başta olmak üzere Türkiye genelindeki pomza üretici şirketlerdir; ürün B2B SaaS olarak konumlanır. Hackathon kategorisi *Akıllı Tedarik Zinciri*'dir; jüri kompozisyonu (Atasever, Öbekli, Bıkmazer, Karvar + sembolik AI koltuğu) için ürün her eksende ≥7 puan tutturacak şekilde tasarlanmıştır. 24 saatlik pencerede Modül A canlı çalışır (Sentinel-2 tabanlı U-Net pomza segmentasyonu), Modül B mock veri ile demo edilir; iki modül entegre vizyon olarak sunulur.

**Tek cümlelik proje tanımı:**
> *"PomzaScope, Türkiye'nin dünya lideri olduğu pomza ekonomisini çoklu uydu görüntüleri ve operasyonel optimizasyon yapay zekâsıyla yeniden şekillendiren — pomza saha tespitinden teslimat rotasına kadar pomza tedarik zincirinin başını dijitalleştiren — ilk Türk pomza maden teknoloji platformudur."*

---

## 1. PROJE KİMLİĞİ VE STRATEJİK KONUM

### 1.1 Cave2Cloud Teması ile Birebir Uyum

Hackathon teması *Cave2Cloud: Kapadokya'dan Global Pazara* sloganının literal cisimleşmesi pomzadır. Pomza Kapadokya'nın volkanik mirasının (Erciyes, Hasan Dağı, Acıgöl kompleksi) maddi karşılığıdır. Türkiye dünya pomza üretiminin yaklaşık %45'ini gerçekleştirir, dünya rezervinin %15,8'i Türkiye'dedir, bu rezervin %17'si Nevşehir'dedir. Yani "Kapadokya'dan global pazara" sloganının başka hiçbir hammaddesi pomza kadar literal değildir.

Buna rağmen Türkiye dünya pomza ihracat değerinde **4. sırada**dır. Türk ham pomza FOB fiyatı yaklaşık **38 USD/ton**, dünya ortalaması ~75 USD/ton. Türkiye en çok kazıyor, en az kazanıyor. Bu paradoksun ardındaki üç teknik boşluk:

- Pomza üreticileri hangi sahanın hangi konumda olduğunu, alan büyüklüğünün yıllar içinde nasıl değiştiğini ve hangi rezerv hattının ekonomik olduğunu sistematik veriyle bilmiyor (saha-bilgi kopukluğu)
- Saha-fabrika-liman arası kamyon lojistiği şoför sezgisinde yapılıyor; yakıt ve sefer optimizasyonu yok
- Sektör dijital olgunluğu ortalama 3,2/10; sistemli B2B platform yok

PomzaScope bu üç boşluğu sırayla kapatan iki modüllü bir veri-uygulama hattıdır. Pomzadan başka bir madde, başka bir uygulama veya başka bir kullanım alanı kapsamında değildir.

### 1.2 İki Katmanlı Mimari — Yüksek Seviye

```
┌────────────────────────────────────────────────────────────────────┐
│                  POMZASCOPE — SİSTEM MİMARİSİ                        │
│                                                                      │
│  GİRDİ KATMANI                                                       │
│  ─────────────                                                       │
│   • 8 farklı uydu (Sentinel-2/-1/-5P, Landsat, ASTER, EnMAP,         │
│     PRISMA, Copernicus DEM)                                          │
│   • OpenStreetMap yol ağı                                            │
│   • UNESCO Göreme Milli Parkı sınırı (WDPA, etik filtre)             │
│   • MAPEG ruhsatlı pomza saha shapefile (ground truth)               │
│                                                                      │
│  ─────────────────────  MODÜL A  ─────────────────────               │
│  Uydu+AI POMZA Alanı Tespiti                                         │
│  • Multispektral + SAR + DEM füzyonu                                 │
│  • U-Net (SSL4EO-S12 MoCo pretrained) semantik segmentasyon          │
│  • Önceki/şimdiki change detection (kazı genişlemesi takibi)         │
│  • Çıktı: pomza olasılık haritası (raster, 0-1) + saha sınır vektörü │
│                                                                      │
│  ─────────────────────  MODÜL B  ─────────────────────               │
│  Pomza Rota ve Lojistik Optimizasyonu                                │
│  • Multi-depot Pickup-Delivery VRP                                   │
│  • Payload-aware fuel cost (Demir-Bektaş-Laporte CMEM)               │
│  • Hub konum önerisi (vizyon — k-medoids facility location)          │
│  • Çıktı: günlük pomza taşıma rotası + yakıt tasarrufu + CO₂ raporu  │
│                                                                      │
│  KARAR ÇIKTISI                                                       │
│  ─────────────                                                       │
│   • Web dashboard (B2B SaaS, pomza şirketi başına login)             │
│   • Pomza saha haritası + günlük rota önerisi + KPI panosu           │
│   • UNESCO buffer-zone red flag (yeni pomza ruhsatı için etik kontrol)│
└────────────────────────────────────────────────────────────────────┘
```

İki modül birbirini gerçekten besler: Modül A "hangi pomza sahaları aktif, ne kadar büyük, yıllık kazı genişlemesi ne hızda" sorusuna cevap üretirken, Modül B bu sahalardan fabrikalara ulaşımı yakıt-optimal hâle getirir. Bu, Karvar (TTO) jürisinin sevdiği "data flywheel" anlatısıdır: uydu verisi → AI sınıflandırma → operasyonel pomza taşıma kararı → pomza şirketi geri bildirimi → modelin yeniden eğitimi.

### 1.3 Hackathon Kategorisi Konumu

| Kategori | Uygunluk | Yorum |
|---|:---:|---|
| 1. Dijital İhracat Çözümleri | 🟡 Orta | Dolaylı — pomza ihracatı altyapısı |
| 2. Yapay Zekâ Destekli E-Ticaret | 🔴 Düşük | E-ticaret arayüzü yok |
| **3. Akıllı Tedarik Zinciri** | 🟢 **Yüksek (★★★)** | **Doğal yuvası** — pomza saha-fabrika tedarik zinciri |
| 4. Doğal Depoların Gıda Harici Kullanımı | 🔴 Düşük | Tüf depolama ile karıştırılmamalı |
| 5. Doğal Mağara Yaşam Alanları | 🔴 Düşük | Açık ocak pomza madenciliği |

Konumlandırma **Kategori 3 — Akıllı Tedarik Zinciri** altındadır. Sunumda Kategori 1 (İhracat) ile dolaylı bağlantı verilir ama ana şemsiye Tedarik Zinciri'dir.

**Stratejik avantaj:** 2025 hackathon kazananları arasında ve 2026 rakip istihbarat raporundaki 20+ rakip projeden hiçbiri madencilik tedarik zincirini ele almamış; pomza+uydu+AI nişi neredeyse %100 bakir.

### 1.4 24 Saatlik MVP Söz-Tutma Sınırları

| Söz | Tutulur mu? | Demo'da Nasıl Görünür |
|---|:---:|---|
| Çoklu uydu (8 kaynak) füzyonu | ✅ | 4 uydu canlı (S2, S1, ASTER TIR, DEM) + 4 uydu pre-cache görsel kanıt |
| Pomza alanı tespiti | ✅ | Avanos sahnesi → CNN segmentasyon → pomza olasılık haritası canlı |
| Önceki/şimdiki change detection | ✅ | Landsat 1985-2025 zaman serisi (pre-cache GIF) + Sentinel-1 koherens (mock görsel) |
| Pomza taşıma rotası optimizasyonu | 🟡 Mock | OR-Tools sentetik 4 pomza sahası + 1 fabrika örneği — 2 saniyede çözüm |
| Hub konumu optimizasyonu | 🔴 Vizyon | Slayt + roadmap; demo değil |
| UNESCO buffer red flag | ✅ | Harita üzerine red overlay |
| CBAM/Türkiye ETS uyumlu emisyon raporu | 🟡 Mock | PDF çıktı örneği — backend rakamları sentetik |
| B2B SaaS arayüzü | ✅ | Streamlit + Folium pomza dashboard'u |

---

## 2. SEKTÖREL BAĞLAM — POMZA EKONOMİSİ

### 2.1 Türkiye-Nevşehir Pomza Profili

| Gösterge | Değer | Kaynak |
|---|---|---|
| Türkiye dünya pomza üretim payı | %45,5 (8,2 / 18 milyon ton) | USGS MCS 2025, OEC, UN Comtrade |
| Türkiye dünya pomza rezerv payı | %15,8 (2,2 milyar ton) | MTA Maden Serisi |
| Nevşehir'in Türkiye pomza rezerv payı | %17 (~370 milyon ton) | MTA, Orhan vd. |
| Nevşehir'in Türkiye pomza ruhsat payı | %20 | MAPEG |
| Türkiye yıllık pomza ihracat tonajı | ~600.000 ton | UN Comtrade |
| Türkiye yıllık pomza ihracat değeri | ~22-25 milyon USD | UN Comtrade |
| Türkiye ortalama pomza FOB | ~38 USD/ton | TİM, ITC TradeMap |
| Dünya ortalama pomza FOB | ~75 USD/ton | USGS |
| Pomza ihracat değer sırası | 4. (AU, IN, CN sonrası) | OEC HS 2513 |

Nevşehir merkez + Avanos + Acıgöl + Gülşehir aksı, Türkiye'nin asidik (yüksek SiO₂, beyaz, hafif) pomzasının ana üretim havzasıdır. Bu kapsam içinde tek odak budur. Bitlis bazik pomzası ve diğer bölgeler vizyon kapsamında, demo dışındadır.

### 2.2 Hedef Pilot Şirket Adayları (B2B Pomza Üreticisi)

PomzaScope'un müşterisi pomza üretici şirketlerdir. Pilot için Nevşehir merkezli 4 öncelikli aday:

| Firma | Lokasyon | Demo Uygunluğu Nedeni |
|---|---|---|
| **BlokBims (Ertaş Grup)** | Avanos / Çardak Köyü | **150 kamyon kendi filo**, 220-300.000 adet/gün pomza ürünü, 35.000 m² kapalı + 1.200.000 m² açık alan, 47 ülkeye pomza ihracatı, 500 kW solar santral. Modül B yakıt rotasının ideal demo müşterisi. |
| **Miner Madencilik** | Avanos + Niğde | Çift saha pomza işletmesi, 200.000 ton/yıl mikronize pomza kapasitesi, 9 dilli web (sektörde en olgun). Sade kapsamda Avanos sahası odakta tutulur, çift saha vizyon roadmap'inde işaretlenir. |
| **Pomza Export A.Ş.** | İzmir/Manisa kökenli, Nevşehir tedarikli | 1969'dan beri pomza sektöründe, ihracat odaklı, REACH bilinçli. |
| **Anorikan / Map-Stones** | Nevşehir / Niğde Altunhisar | Yerli sermaye, sürdürülebilir pomza madenciliği vurgusu. |

**Pitch'te seçilecek isim:** Demo akışında **BlokBims** öne çıkarılır (150 kamyon × yıllık taşıma km = somut yakıt tasarrufu rakamı dramatize edilebilir). Miner Madencilik vizyon roadmap'inde ikincil zikredilir.

### 2.3 Sektörel Acılar — PomzaScope'un Karşıladığı

Pomza KOBİ Envanteri raporundan:

- **Görünmezlik krizi:** 81 pomza firmasının %37'sinde kurumsal web sitesi yok, %85'inde doğrulanmış LinkedIn yok. Sektör dijital olgunluk ortalaması 3,2/10.
- **Saha-bilgi kopukluğu:** Pomza saha jeolojisi kâğıt/Excel'de, kamyon rotası şoför sezgisinde, üretim kararı sahibin başında. Sayısal sistem yok.
- **CBAM 2026 + Türkiye ETS pilot 2026-2027 baskısı:** Pomza dolaylı kapsamda (çimento puzzolanı, bims yapı malzemesi); doğrulanmış emisyon datası talep edilecek ama ölçüm altyapısı yok.
- **Maden Yönetmeliği rehabilitasyon yükümlülüğü:** ÇED + rehabilitasyon raporu zorunlu ama izleme zayıf; uydu tabanlı izleme sistemi yok.
- **Kapadokya UNESCO/Göreme buffer hassasiyeti:** Yeni pomza ruhsatı başvurularında "peri bacası havzası" itirazları artıyor; firmaların proaktif coğrafi farkındalık aracı yok.

PomzaScope bu beş acıyı tek bir B2B SaaS arayüzünde birleştirir.

---

## 3. MODÜL A — UYDU + AI POMZA ALANI TESPİTİ

### 3.1 Pomzanın Uydudan "Görünme" Mantığı — 5 Fiziksel İmza

Bir uydu kayacı doğrudan görmez; kayacın elektromanyetik spektrumla nasıl etkileştiğini ölçer. Pomzanın 5 ayrı imzası vardır ve her uydu bu imzalardan farklı bir alt kümesini ölçer. Doğru pomza tespiti = doğru bant kombinasyonu.

| # | Fiziksel Özellik (Pomza için) | Pomzadaki Değer | Ölçen Spektral Bölge | Ölçen Uydu(lar) |
|:-:|---|---|---|---|
| 1 | **Yüksek albedo** (asidik pomza beyaz/grimsi) | %50-80 yansıma VIS'te | Görünür + Yakın IR (0,4-1,0 µm) | Sentinel-2, Landsat |
| 2 | **Yüksek SiO₂ içeriği** (riyolitik camsı pomza) | %55-77 SiO₂ | Termal IR (8-12 µm) — Si-O esnek-bük titreşimi | **ASTER TIR** (en güçlü) |
| 3 | **Al-OH bağı** (pomza alümino-silikat amorf) | %13-17 Al₂O₃ + bağ suyu | SWIR, 2,1-2,3 µm absorpsiyon çukuru | Sentinel-2 B11/B12, EnMAP, PRISMA |
| 4 | **Yüzey pürüzlülüğü** (kazılmış pomza yüzeyi, granüler, tozlu) | Mohs 5-6 sertlik | Mikrodalga, C-band SAR (5,6 cm) | **Sentinel-1** |
| 5 | **Höyük geometrisi** (pomza açık ocak topografyası) | 5-50 m derinlik | Yükseklik (DEM) | **Copernicus DEM GLO-30**, ASTER GDEM |

Tek bir uyduyla pomza tespitine sıkışmak bilimsel olarak yanlıştır — Ahmet Abi'nin "8 farklı uydudan füzyon" sezgisi tam doğrudur. Çoklu uydu çoklu imza yakalar; ML modeli bu imzaların **birlikte ortaya çıktığı** alanları "yüksek olasılıkla pomza" olarak öğrenir.

**Pitch için pomza-spektral akademik temel:** Steinhauser et al. 2006 (Cappadocia Pumice INAA), Aksay Kılınç vd. 2016 (AKÜ FEMÜBİD), Zheng et al. 2022 (Pumice Raft Index, Sentinel-2 — okyanus pomzası ama spektral imza karasal pomzaya kısmen taşınabilir), Ninomiya 2002 (ASTER TIR Quartz Index — silikat kayaç sınıflandırması).

### 3.2 8 Uydulu Portföy — Tier 1 / 2 / 3 Mimarisi

| # | Uydu | Bant | Pomza için Hangi İmzayı Yakalar | MVP Tier |
|:-:|---|:-:|---|:-:|
| 1 | Sentinel-2 MSI | 13 | Pomza albedosu (VIS) + Al-OH (SWIR B11/B12) | **Tier 1 — canlı** |
| 2 | Sentinel-1 SAR | 2 (VV+VH) | Pomza yüzey pürüzlülüğü + change detection | **Tier 1 — canlı** |
| 3 | ASTER TIR + VNIR | 14 | Pomza SiO₂ kimyasal içerik (TIR) — Ninomiya QI | **Tier 1 — statik tile** |
| 4 | Copernicus DEM GLO-30 | DEM | Pomza ocağı höyük geometrisi + eğim profili | **Tier 1 — canlı** |
| 5 | Landsat 8/9 OLI+TIRS | 11 | Pomza ocaklarının tarihi arşivi 1972-bugün | **Tier 2 — pre-cache GIF** |
| 6 | EnMAP HSI | 230 | Pomza spektral fingerprint (hyperspektral) | **Tier 2 — pre-cache** |
| 7 | PRISMA HSI | 239 | Pomza için ikinci hyperspektral kaynak (çapraz doğrulama) | **Tier 2 — pre-cache** |
| 8 | Sentinel-5P TROPOMI | 4500+ | Atmosferik yan etki (Modül B kamyon emisyon doğrulaması) | **Tier 3 — slayt** |

**Ek 3 destekleyici (anlatı katmanı, demo'da veri olarak kullanılmaz):**
- **CORONA** (1960-72, deklasifiye, USGS) — 65 yıllık pomza ocak change detection, pitch hook
- **RASAT** (TÜBİTAK UZAY 2011-2021) — Türk arşivi, milliyetçi resonans
- **İMECE / GÖKTÜRK-2B** (2023+) — vizyon: "Türk uydusu Türk pomzasına bakıyor"

### 3.3 Tier 1 Uyduları — Detaylı Teknik Notlar

#### 3.3.1 Sentinel-2 (ESA Copernicus) — Modülün Omurgası

| Özellik | Değer |
|---|---|
| Operatör | ESA Copernicus |
| Bant sayısı | 13 (4×10 m, 6×20 m, 3×60 m) |
| Tekrar süresi | 5 gün (2A+2B), 2-3 gün (2C ekiyle, 2024+) |
| Erişim | Tamamen ücretsiz — Copernicus Browser, Sentinel Hub, Google Earth Engine |
| Maliyet | 0 |

**Pomza tespiti için kritik bantlar:**
- B2 (490 nm, 10 m) — pomza albedosu + atmosferik düzeltme
- B3 (560 nm, 10 m) — beyaz asidik pomzanın yansıma tepesi
- B4 (665 nm, 10 m) — pomza/kayaç ayrımı için referans
- B8 (842 nm, 10 m) — yeşil bitki örtüsü dışlama filtresi (NDVI; canlı bitki = pomza değil)
- **B11 (1610 nm, 20 m)** — Al-OH bandının düz omzu, referans
- **B12 (2190 nm, 20 m)** — pomza için Al-OH absorpsiyon çukuru — **en kritik tek bant**

**Sabins band oranı:** B11/B12 oranı pomza+alterasyon mineralleri içeren kayaçlarda yüksek çıkar; volkanik tüfler de yüksek değer verir, bu yüzden tek başına pomza-tüf ayrımı için yeterli değil ama mükemmel bir filtre katmanıdır. Akademik referans: van der Meer et al. 2014 (*Remote Sensing of Environment* 148:124-133).

**Türetilmiş indeksler (pomza tespiti için):**
- **NDVI** (B8-B4)/(B8+B4) — yeşil bitki örtüsü dışlama maskesi (canlı bitki olan piksel = pomza değil; eleyici filtre)
- **BSI** ((B11+B4)-(B8+B2))/((B11+B4)+(B8+B2)) — çıplak kayaç/açık ocak yüzey tespiti
- **Albedo (Liang formülü)** (0,356·B2 + 0,130·B4 + 0,373·B8 + 0,085·B11 + 0,072·B12 - 0,0018)/1,016 — pomza yüksek albedo (>0,3) ana imzası

**24 saat fizibilitesi:** ✅ Çok yüksek. Google Earth Engine üzerinden tek satır kodla Avanos bölgesi çekilir. Pretrained U-Net + Segformer modelleri Sentinel-2 için literatürde hazır (EuroSAT, BigEarthNet, MineSegSAT veri setleri).

#### 3.3.2 Sentinel-1 (ESA Copernicus) — Pomza Yüzey Pürüzlülüğü ve Change Detection

| Özellik | Değer |
|---|---|
| Sensör | C-band SAR (5,6 cm dalga boyu) |
| Polarizasyon | Çift: VV + VH |
| Çözünürlük | 5-20 m (IW modu en yaygın: 10 m) |
| Tekrar | 6 gün (1A+1C), 12 gün (1B kaybı sonrası geçici), 1C ile 2024'ten itibaren 6 güne döndü |
| Bulut bağımsız | ✅ — mikrodalga buluttan geçer |
| Erişim | Ücretsiz — Copernicus Browser, ASF DAAC |

**Pomza için 3 kullanım katmanı:**
1. **Yüzey pürüzlülüğü:** Açık pomza ocaklarının kırılmış/kazılmış kayaç yüzeyleri yüksek geri-saçılım verir. Sentinel-2 bulut-cover'a takıldığında SAR yedek olarak çalışır (Kapadokya kış ayları sıkça bulutlu).
2. **InSAR koherans:** İki ardışık geçiş arasındaki faz koherens kaybı yüzeyde değişiklik olduğunu söyler. Aktif kazılan pomza ocağı düşük koherens, terkedilmiş ocak yüksek koherens verir.
3. **Change detection (Ahmet Abi'nin "önceki ve şimdiki" şartının teknik karşılığı):** Pomza ocak alanının yıllar içinde nasıl genişlediğini SAR amplitude difference ile takip etmek mümkündür. Optik sensörlere kıyasla SAR'ın bulutlardan etkilenmemesi büyük avantajdır. Akademik referans: Mazza et al. 2023, *Remote Sensing* 15(24):5664 — Sentinel-1 SAR ile açık ocak madeni change detection için yarı-denetimli derin öğrenme çerçevesi.

**24 saat fizibilitesi:** 🟡 Orta. Sentinel-1 ham çekme kolay, ama InSAR processing (SNAP toolbox, SARProz) öğrenme eğrisi var. **MVP önerisi:** Sadece amplitude (geri-saçılım) ve VV/VH oranını kullan — pomza yüzey pürüzlülüğü için yeterli. InSAR koherens vizyon slaydında bırakılır.

#### 3.3.3 ASTER TIR (NASA-METI Terra) — Pomza Jeolojik Altın Standart

| Özellik | Değer |
|---|---|
| Operatör | NASA + Japonya METI, Terra uydusu |
| Lansman | 1999 (hâlâ aktif) |
| Bant sayısı | 14: 3 VNIR (15 m) + 6 SWIR (30 m, 2008'de bozuldu) + 5 TIR (90 m) |
| Erişim | Ücretsiz — NASA Earthdata / USGS Earth Explorer |
| Tarihi arşiv | 2000-2008 SWIR + 2000-bugün VNIR/TIR |

**Pomza için ASTER'ın "süper güç"ü = TIR bantları:**

ASTER, dünyada uydu seviyesinde silikat kayaç sınıflandırması yapabilen tek geniş erişimli sensördür. ASTER'ın TIR bantları, hidroksil mineral grupları ile silika ve karbonat mineralleri için temel absorpsiyon özelliklerini bölgesel haritalama amacıyla yeterli spektral çözünürlüğe sahiptir.

**Ninomiya 2002 indeksleri — pomza için altın anahtar:**
- **Quartz Index (QI):** ASTER B11² / (B10 × B12) — silika içerik tahminini doğrudan verir. Asidik pomza (yüksek SiO₂) yüksek QI verir, bazik pomza düşük QI. Pomza saha kalite skoru için ana proxy.
- **SiO₂ Kimyasal İndeksi:** B13/B12 + B12/B14 — bulk silisyum içerik tahmini
- **Carbonate Index (CI):** Karbonat kayaçları (traverten) eler — pomza ile karışmasın

**Volkanik camsı kayaçlar için spesifik spektroskopi:** Termal IR'da Si-O-Al bağları gerilme ve bükülme titreşimleri yapar; bu titreşimlerin spektral konumu ve morfolojisi kompozisyon, vesikülarite, kristalinite ve sıcaklığa bağlıdır. Yansıma özellikleri 8 µm (1200 cm⁻¹) ve 9 µm (1050 cm⁻¹) civarında SiO₂ ve Al/(Al+Si) arttıkça daha yüksek dalga sayılarına kayar. Pomza tam olarak alümino-silikat amorf cam (volkanik glass) — bu literatür birebir bu projeye yazılmış gibidir.

**24 saat fizibilitesi:** ✅ Yüksek. ASTER TIR sahneleri Earthdata'dan hızlı çekilir; QI/SiO₂ indeks hesaplama tek satır numpy kodu.

#### 3.3.4 Copernicus DEM GLO-30 — Pomza Ocağı Topografyası

| Özellik | Değer |
|---|---|
| Operatör | ESA Copernicus (TanDEM-X türevi) |
| Çözünürlük | 10 m global, 30 m public access |
| Erişim | Ücretsiz — Copernicus Open Access |

**Pomza için 3 kullanım:**
1. Açık pomza ocağı höyüklerinin 3D rekonstrüksiyonu — saha hacmi tahmini için
2. Eğim haritası → Modül B Pollution-Routing Problem girdisi (kamyon yakıt eğim hesaplamaları)
3. UNESCO Göreme Milli Parkı buffer-zone overlay'i — yeni pomza ruhsatı için coğrafi etik filtre

ASTER GDEM v3 (30 m) ile birlikte kullanılır; Copernicus DEM daha doğru, ASTER global daha uzun arşiv. Modül A'nın hem segmentasyon ek girdisi hem Modül B'nin eğim profili kaynağıdır.

### 3.4 Tier 2 ve Tier 3 Uyduları — Pre-Cache + Anlatı

| Uydu | Pomza için Rol | MVP Stratejisi |
|---|---|---|
| Landsat 8/9 | Pomza ocaklarının 1972-2025 tarihi zaman serisi | Earth Engine'den önceden çekilir, GIF olarak demo'da gösterilir; pitch için "Landsat Türkiye Cumhuriyeti'nden eski, Avanos pomza ocaklarının 53 yıllık değişimini biliyor" anlatısı |
| EnMAP (DLR Almanya, 2022+) | Pomza spektral imzasının hyperspektral (230 bant) fingerprint'i | DLR EOC Geoservice'ten Avanos sahnesi indirilir; SpectralEarth pretrained foundation model fine-tune edilir; pitch'te Atasever ekseni için "akademik ciddiyet" sinyali |
| PRISMA (ASI İtalya, 2019+) | İkinci hyperspektral pomza imzası — çapraz doğrulama | ASI başvurusu hackathon öncesi açılırsa Avanos sahnesi alınır; alınamazsa Lipari (İtalya pomzası) referans sahnesi gösterilir |
| Sentinel-5P TROPOMI | Pomza taşıyan kamyon NO₂/CO₂ emisyonunun bölgesel doğrulaması | Vizyon slaydı: "Modül B'nin emisyon hesabı atmosferik veriyle çapraz kontrol ediliyor" |
| CORONA (1960-72) | Avanos pomza ocaklarının 65 yıl önceki hâli | Pitch hook görsel: "1968'de bu pomza ocağı yoktu, 2025'te 47 hektar" |
| RASAT (Türk uydu) | Pomza ocak arşivi 2011-2021 | Vizyon slaydı, milliyetçi anlatı |
| İMECE / GÖKTÜRK-2B | "Türk uydusu Türk pomzasına bakıyor" | Vizyon slaydı, Karvar/AI etik koltuğu için resonans |

### 3.5 ML Mimarisi — Pomza Segmentasyonu

#### 3.5.1 Model Seçimi

| Model | Pretrained ağırlık | Sentinel-2 13-bant? | Hackathon eğitim süresi | Karar |
|---|---|---|---|---|
| **U-Net (ResNet50, SSL4EO-S12 MoCo)** | TorchGeo `ResNet50_Weights.SENTINEL2_ALL_MOCO` | ✅ 13-bant | 2-4 saat fine-tune (T4 GPU) | ✅ **Birincil** |
| **SegFormer (MIT-B0/B1)** | MineSegSAT örneği var, 12-bant | ✅ B10 atılır | 2-4 saat | ✅ Modern alternatif |
| **DeepLabV3+ (ResNet50)** | ImageNet, S2'ye band adapter gerek | RGB başlangıç + 10 kanal init | 3-5 saat | ⚠️ Daha karmaşık |
| **Prithvi-EO-1.0 (NASA-IBM)** | HLS 6-bant | Sadece 6-bant | 2-4 saat | ✅ Yedek |
| **Plain CNN scratch** | Yok | — | 6-12 saat, az veri overfit | ❌ |

**Karar:** **TorchGeo + U-Net + ResNet50 (SSL4EO-S12 MoCo)** birincil. SegFormer (MineSegSAT pomza literatür baseline'ı için) yedek.

#### 3.5.2 Bant Kombinasyonu — Pomza için Optimal Girdi Tensörü

Pomza tespiti için U-Net'e verilecek input channel'lar:
1. Sentinel-2 RGB (B2, B3, B4)
2. Sentinel-2 NIR (B8) — yeşil bitki dışlama (NDVI üretimi için)
3. Sentinel-2 SWIR (B11, B12) — Al-OH absorpsiyon
4. NDVI türetilmiş kanal (B8-B4)/(B8+B4) — yeşil bitki maskesi
5. BSI türetilmiş kanal — çıplak kayaç tespiti
6. Sabins ratio B11/B12 — pomza+alterasyon proxy
7. Sentinel-1 VV amplitude — yüzey pürüzlülüğü
8. Sentinel-1 VH amplitude — polarizasyon farkı
9. Copernicus DEM yükseklik
10. DEM eğim (slope)

Toplam 10-12 input kanalı. SSL4EO-S12 MoCo backbone Sentinel-2 13 bant için pretrained; ek SAR + DEM kanallarını fine-tuning'de adaptasyon ile öğretiriz.

#### 3.5.3 Multi-Sensor Füzyon Stratejisi

Modül A'nın "8 uydudan füzyon" söylemini teknik olarak somutlaştıran iki seviyeli mimari:

**Seviye 1 — Pixel-Level Füzyon (Modülde Çalışıyor):**
- Sentinel-2 13 bant + Sentinel-1 2 bant + DEM 2 türev (yükseklik + eğim) → tek tensor → U-Net
- ASTER TIR Quartz Index ayrı bir post-processing katmanı (90 m çözünürlüğünde, S2 tile'ına resampled)

**Seviye 2 — Score-Level Füzyon (Mimari Vizyon):**
- U-Net pomza olasılığı (S2+S1+DEM) × ASTER TIR QI ağırlığı × EnMAP hyperspektral spektral imza eşleme skoru → final pomza güven haritası

Demo'da Seviye 1 canlı çalışır; Seviye 2'nin ASTER TIR QI katmanı statik tile olarak post-processing yapar (canlı API çağrısı yok, Avanos bölgesi için pre-computed). EnMAP hyperspektral skor mock görsel.

### 3.6 Ground Truth ve Etiketleme Stratejisi

**Sorun:** Pomza için yayınlanmış etiketli açık veri seti **yoktur**. (Pumice Raft Index — Zheng 2022 — okyanus pomzası, karasal pomza ocaklarına direkt transfer edilemez.)

**Çözümler:**

1. **MAPEG ruhsatlı pomza saha shapefile'ı:**
   - Halka açık tek-tek sorgu var, toplu vektör indirme yok (e-Maden GeoServer kapalı YTK için).
   - Workaround: Avanos bölgesi için ~10-20 ruhsat alanı manuel olarak Sentinel-2 RGB üzerinden QGIS'te poligon çizilir; pozitif örnek olarak işaretlenir.

2. **Bilinen pomza üreticilerinin saha konumları:**
   - BlokBims, Pomza Export, Map-Stones, Miner Madencilik gibi firmaların ocak konumları kamuya açık (web sitesi, Google Maps); manuel etiketlemede kullanılır.

3. **Negatif örnek stratejisi:**
   - Volkanik olmayan alanlar (yerleşim, yol, su)
   - Açık tüf yüzeyleri (Göreme/Zelve peri bacası alanları) — UNESCO buffer'da tüf+pomza karışıktır; bu alanlar **maskelenmiş ve etiket dışı tutulur**
   - Volkanik kayaç düzlüğü ama pomza olmayan
   - Çıplak toprak/kayaç ama pomza olmayan

4. **Manuel etiket bütçesi (24 saat içinde):**
   - 30-40 pozitif pomza ocağı poligon (Avanos+Acıgöl+Gülşehir civarı)
   - 100-150 negatif örnek
   - Toplam 2-3 saat manuel etiketleme (QGIS + EO Browser)

5. **Augmentation stratejisi:**
   - Spatial: random rotation, flip, scale
   - Spectral: random band drop (modelin tek banda overfit etmesini engellemek için)
   - Tile-level: 256×256 patch sliding window

### 3.7 Çıktı Katmanları — Modül A

Modül A 3 ana çıktı üretir, hepsi pomza odaklı:

```
ÇIKTI 1: POMZA VARLIĞI OLASILIK HARİTASI
─────────────────────────────────────────
• Format: Raster (GeoTIFF), 10 m çözünürlük, 0-1 sigmoid değer
• Beslemesi: Sentinel-2 + Sentinel-1 + DEM → U-Net
• Post-processing: ASTER TIR QI ile güven ağırlığı çarpımı
• Demo'da görselleştirme: harita üzerine renkli ısı haritası (mavi=düşük, kırmızı=yüksek pomza olasılığı)

ÇIKTI 2: POMZA SAHA CHANGE DETECTION (ÖNCEKİ/ŞİMDİKİ)
─────────────────────────────────────────────────────
• Format: Vektör poligon (GeoJSON) + raster fark haritası
• Beslemesi: Sentinel-1 SAR amplitude difference (ardışık geçiş) +
            Landsat tarihi arşiv (1985, 2000, 2015, 2025 snapshot)
• Çıktı: "Bu pomza ocağı son 5 yılda %X büyüdü, yıllık genişleme hızı Y hektar"
• Demo'da görselleştirme: zaman kaydırıcısı + alan değişim grafiği

ÇIKTI 3: UNESCO BUFFER RED FLAG (ETİK FİLTRE)
─────────────────────────────────────────────
• Format: Vektör overlay + binary uyarı bayrağı
• Beslemesi: WDPA Göreme Milli Parkı polygon + 500-1000 m buffer
• Çıktı: "Tespit edilen pomza alanı UNESCO buffer içinde — yeni ruhsat
        başvurusu için coğrafi risk; kırmızı işaret"
• Demo'da görselleştirme: harita üzerine kırmızı tarama overlay
```

### 3.8 Doğruluk Metrikleri ve Ablation

**Pitch'te Atasever ekseni için sunulacak metrikler:**

| Metrik | Hedef | Nasıl Ölçülür |
|---|:-:|---|
| Pixel-level F1 | ≥0,75 | MAPEG poligon + manuel pozitif vs U-Net çıktı |
| Pixel-level IoU | ≥0,60 | Aynı set |
| Object-level Recall (saha bazında) | ≥0,80 | Bilinen 10-15 saha üzerinde |
| False Positive Rate (UNESCO bölgesinde) | ≤0,05 | Etik kontrol — buffer içinde yanlış pozitif düşük olmalı |

**Ablation study (sunumda 1 slayt):**

| Konfigürasyon | Beklenen F1 | Yorum |
|---|:-:|---|
| Sadece S2 RGB (3 bant) | ~0,55 | Baseline |
| + S2 SWIR (B11, B12) | ~0,67 | Al-OH ekstre edildi |
| + Sentinel-1 SAR | ~0,72 | Yüzey pürüzlülüğü eklendi |
| + DEM eğim | ~0,75 | Topografya eklendi |
| + ASTER TIR QI | ~0,78 | Silika içerik filtresi |
| **+ EnMAP hyperspektral (full)** | **~0,82** | Vizyon — hackathonda demo değil |

Bu ablation tablosu, "her uydu gerçekten katma değer veriyor mu?" sorusuna proaktif cevaptır. Pitch'te Atasever'in *"Modelinizi nasıl doğruladınız?"* sorusunun karşılığıdır.

---

## 4. MODÜL B — POMZA ROTA VE LOJİSTİK OPTİMİZASYONU

### 4.1 VRP Çerçevesi — Pomza Lojistiğinin Matematiksel Karşılığı

Modül B'nin çözdüğü problem: **Multi-Depot Pickup-Delivery Vehicle Routing Problem with Payload-Aware Fuel Cost (MD-PDVRP-FC)**.

Türkçe operasyonel karşılık: "Birden fazla pomza ocağına dağılmış ham mali, kamyon filosuyla en az yakıtla, fabrika kapasitesini aşmadan ve teslim zamanlarına uyarak fabrika/limana taşıma."

**Bileşenler:**
- **Multi-Depot:** Pomza şirketi 2+ fabrikası varsa (örn. Miner Madencilik Avanos+Niğde), her fabrika bir depot
- **Pickup-Delivery:** Ahmet Abi'nin "toplana toplana gitme" sözünün matematiksel karşılığı; kamyon birden fazla ocaktan pomza alıp tek fabrikaya götürür
- **Payload-Aware Fuel Cost:** Boş kamyon vs dolu kamyon yakıtı farklı; eğim ile birlikte modellenir

**Akademik temel:** Bektaş & Laporte 2011 (Pollution-Routing Problem, *Transportation Research Part B* 45:8); Demir, Bektaş, Laporte 2014 (Bi-objective PRP, *European Journal of Operational Research*); Lai, Costa, Demir et al. 2021 (PRP with Speed Optimization and Uneven Topography, arXiv:2105.09229).

### 4.2 Pollution-Routing Problem — Pomza Kamyonu İçin Yakıt Modeli

Demir-Bektaş-Laporte 2014 Comprehensive Modal Emissions Model (CMEM) tabanlı pomza kamyonu yakıt formülü:

```
F = λ · (k·N·V·d/v + M·γ·α·d + β·γ·d·v²)

λ  = ξ/(κ·θ)           # yakıt-enerji dönüşüm sabiti
ξ  = 1                  # kütle/aks oranı
κ  = ısı değeri (44 MJ/kg, dizel)
θ  = yakıt-yoğunluk (737 kg/m³)
k  = motor sürtünme (~0,2 kJ/rev/L)
N  = motor devir/sn
V  = motor hacmi (L)
M  = TOPLAM kütle (boş kamyon + pomza yükü, kg) — POMZA YÜKÜNE DUYARLI
α  = a + g·sin(δ) + g·fr·cos(δ)
δ  = yol eğimi — DEM'den (Copernicus DEM GLO-30) hesaplanır
β  = 0,5·Cd·ρ·A         # hava direnci
v  = hız (m/s)
d  = mesafe (m)
γ  = sürücü/araç verim
fr = yuvarlanma direnci (~0,01)
g  = 9,81 m/s²
```

**Pomza özelinde anlam:**
- M parametresi pomza yüküne duyarlı; dolu kamyon ~25 ton pomza, boş ~12 ton kamyon = M değişir → yakıt tüketimi değişir
- δ parametresi DEM'den hesaplanır → Avanos-Niğde hattının eğim profili modele girer
- Aynı km mesafe için Avanos→fabrika ve fabrika→Avanos farklı yakıt tüketir (yük durumu)

**Beklenen kazanç:** Demir et al. 2014 ve takip eden literatürde PRP optimizasyonu tipik olarak %10-25 yakıt tasarrufu sağlar. Pomza için somut rakam:
- BlokBims tipi 150 kamyon × ortalama 250 km/gün × ~30 L dizel/100 km = ~11.250 L/gün dizel
- %15 tasarruf = 1.687 L/gün × 365 gün = ~615.000 L/yıl
- Türkiye dizel fiyatı (mayıs 2026 tahmini) ~₺50/L → ~**₺30,7 milyon/yıl tasarruf** (tek pomza şirketi için)
- CO₂ karşılığı: ~1.642 ton CO₂eq/yıl azalma

Bu rakam pitch'te Öbekli ve Karvar eksenlerine doğrudan dokunur.

### 4.3 Multi-Depot Pickup-Delivery — Mimari

```
DEPOT (Pomza Fabrikası, örn. BlokBims Avanos)
    │
    ├── KAMYON 1 → POMZA OCAK 1 (10 ton al) → POMZA OCAK 2 (8 ton al) → DEPOT (18 ton bırak)
    ├── KAMYON 2 → POMZA OCAK 3 (15 ton al) → DEPOT (15 ton bırak)
    ├── KAMYON 3 → POMZA OCAK 4 (12 ton al) → POMZA OCAK 5 (8 ton al) → DEPOT (20 ton bırak)
    └── ...
```

**Kısıtlar:**
- Her kamyonun kapasitesi (örn. 25 ton)
- Her ocak için minimum/maximum günlük çekim miktarı (kontrat veya rezerv kısıtı)
- Zaman pencereleri (ocak çalışma saatleri 08:00-17:00)
- Sürücü çalışma süresi (max 9 saat)
- DEM eğim (yol fiziği)

**Multi-depot uzantısı:** Pomza şirketinin 2+ fabrikası varsa (Miner Avanos + Niğde gibi), her ocağın hangi fabrikaya gitmesi gerektiğini de kararla — kapasiteye göre dengeli dağıtım. Bu sade kapsamda 1 fabrika+4 ocak demo edilir; multi-depot vizyon roadmap'inde işaretlenir.

### 4.4 Stack — Açık Kaynak Bileşenler

| Tool | Rol | Hackathon Notu |
|---|---|---|
| **OSRM** (Open Source Routing Machine) | Avanos-fabrika gerçek karayolu mesafe + süre matrisi | Türkiye OSM bbox indirilir, yerel docker kurulur |
| **GraphHopper** (alternatif) | Built-in elevation profile (SRTM/CGIAR) — PRP için eğim entegre çözüm | OSRM+CMEM yerine tek-tool seçimi olarak kullanılabilir |
| **Google OR-Tools** | CVRP / Pickup-Delivery / Multi-Depot çözücü, Python API | Birincil VRP çözücü |
| **VROOM** (alternatif) | Hızlı C++ CVRP solver | Yedek; PRP eklenmesi zor |
| **Pyomo + CBC/HiGHS** | MIP formülasyonu — exact PRP | ❌ 24 saatte yetişmez |

**Karar:** **OSRM** (mesafe matrisi, Türkiye OSM lokal docker) → **OR-Tools** (Pickup-Delivery + capacity + time-window) → **Demir-Bektaş-Laporte CMEM formülü** (Python post-process) ile arc cost'a yakıt+CO₂ ağırlığı ekleme.

### 4.5 Hub Konum Optimizasyonu (Vizyon)

Ahmet Abi'nin "*çalışma üssü nereye nasıl kurmalı, dağıtım hub'unu nasıl optimize etmeli*" sözünün matematiksel karşılığı **Capacitated Facility Location Problem (CFLP)**'dir.

**Yaklaşım:**
- Aday hub konumları: mevcut yol ağı kavşakları + boş arazi parselleri (planlama için)
- Talep noktaları: pomza ocakları (Modül A'dan)
- Talep miktarı: ocak rezerv tahmini × yıllık çekim oranı
- Çözücü: k-medoids + capacity constraint, veya MIP (Pyomo) ile exact CFLP
- Hedef: toplam taşıma maliyetini (km × yakıt × CO₂) minimize et

**24 saatte yapılmayacak:** Bu modül **vizyon roadmap'inin parçasıdır**, demo'da çalışmaz. Pitch'te Slayt 7 (Vizyon) içinde "yıl 2'de Modül B'nin Hub Konum Optimizasyonu eklemesi" olarak yer alır.

### 4.6 Mock Veri Seti — Demo İçin

24 saatte Modül B canlı VRP çözümü yapsa da **gerçek pomza şirketi verisi yok**. Demo için sentetik veri:

**Avanos Mock Senaryosu:**
- 1 fabrika: BlokBims (Çardak Köyü, Avanos) — gerçek konum
- 4 pomza ocağı: Avanos-Acıgöl-Gülşehir aksında Modül A'nın tespit ettiği gerçek konumlar (sentetik talep miktarı atanmış)
- 3 kamyon (kapasite 25 ton, hız 60 km/h, dizel tüketim 30 L/100 km baz)
- Zaman penceresi: 08:00-17:00
- Yol ağı: gerçek Türkiye OSM (Avanos bölgesi)
- DEM: gerçek Copernicus DEM (eğim profili gerçek)

Bu sentetik veri 5-6 saniyede OR-Tools tarafından çözülür; demo'da harita üzerinde rota animasyonu + KPI tablosu (toplam km, toplam yakıt, CO₂, alternatif rotaya göre tasarruf %) gösterilir.

### 4.7 Çıktı Katmanları — Modül B

```
ÇIKTI 1: GÜNLÜK KAMYON ROTASI
─────────────────────────────
• Format: Sıralı duraklar listesi (her kamyon için)
• Görselleştirme: harita üzerinde renkli rota çizgisi
• KPI: km, süre, yakıt (L), CO₂ (kg), kapasite kullanımı (%)

ÇIKTI 2: YAKIT TASARRUFU RAPORU
───────────────────────────────
• "Önerilen rota vs. baseline rota" karşılaştırması
• Günlük + aylık + yıllık tasarruf rakamları
• ₺ ve ton CO₂ karşılığı

ÇIKTI 3: CBAM / TÜRKİYE ETS UYUMLU EMİSYON KAYDI (MOCK PDF)
──────────────────────────────────────────────────────────
• Tarihli ölçüm kaydı: rota ID, kamyon ID, başlangıç/bitiş zaman,
  km, yakıt L, CO₂eq kg
• PDF/CSV export — Türkiye ETS MRV altyapısına uyumlu format
• Demo'da: 1 örnek PDF gösterilir
```

---

## 5. MİMARİ BÜTÜNLÜK VE VERİ AKIŞI

### 5.1 Modül A → Modül B Beslemesi

İki modülün entegre olduğu kritik mimari noktası:

```
MODÜL A ÇIKTILARI                          →  MODÜL B GİRDİLERİ
─────────────────                              ─────────────────
Pomza olasılık haritası (raster)            →  Aday ocak konumları (poligon centroid)
Pomza saha sınır vektörü (GeoJSON)          →  Saha kapasite tahmini (alan × derinlik proxy)
Change detection (yıllık genişleme hızı)    →  Saha aktif/pasif durumu — VRP'de hangi
                                               ocaktan günlük ne kadar mal alınabilir
DEM eğim haritası                           →  Yol eğim profili (CMEM δ parametresi)
UNESCO buffer red flag                      →  VRP'de buffer içindeki ocaklar
                                               otomatik olarak rota dışında bırakılır
```

Bu veri akışı sunumda 1 mimari diyagram ile gösterilir; jüri "iki modül gerçekten birbiriyle konuşuyor mu?" sorusuna görsel kanıt verir.

### 5.2 SaaS Dashboard — Bıkmazer Ekseni İçin

Bıkmazer (Butiksoft, SaaS/PMS uzmanı) ekseninde demo'nun zayıf kalmaması için **B2B SaaS arayüzü** kritik. PomzaScope dashboard'unun minimum yeterli ekranları:

**Ekran 1 — Saha Tarama (Pomza Şirketi sahibi giriş yapar):**
- "Ben BlokBims'im" login
- Türkiye haritası, kullanıcı bir poligon çiziyor (Avanos bölgesi)
- "Bu bölgede pomza var mı?" butonuna tıklıyor
- Modül A canlı çalışıyor — Sentinel-2 görüntüsü çekiliyor, U-Net segmentasyon koşuyor

**Ekran 2 — Pomza Tespit Sonucu:**
- Multispektral bantlar görselleştirme (RGB, B11/B12 oranı, NDVI)
- Pomza olasılık haritası ısı haritası
- Saha bazında özet kart: "Saha 1: 23 ha, %85 güven, son 5 yıl %12 büyüdü"
- UNESCO buffer red flag eğer var

**Ekran 3 — Operasyonel Karar (Pomza Lojistik):**
- Pomza şirketi fabrika konumu girdi (BlokBims Çardak)
- VRP çözücü 5 saniyede günlük rotayı hesaplıyor
- Çıktı: "Bugünkü pomza taşıma rotası: 3 kamyon, 7 saat, 142 km, 189 L yakıt = 504 kg CO₂"
- Alternatif rota karşılaştırması: "%15 fazla yakıt tüketirdi"
- Aylık tasarruf grafiği

Bu üç ekranın akışı pitch demo'nun omurgasıdır.

---

## 6. TEKNİK STACK

### 6.1 Backend ve ML Pipeline

| Katman | Seçim | Neden |
|---|---|---|
| Dil | **Python 3.11** | Tek dilli, ML+VRP+harita aynı runtime |
| Veri platformu | **Google Earth Engine** + Sentinel Hub | Sıfır-indirme cloud-native, Avanos örnek tile <1 dk |
| ML framework | **PyTorch + TorchGeo + PyTorch Lightning** | Pretrained S2 ağırlıkları + clean training loop |
| Pretrained backbone | `ResNet50_Weights.SENTINEL2_ALL_MOCO` (SSL4EO-S12) | 13-bant tek ağırlık seçeneği |
| Mimari kütüphanesi | `segmentation-models-pytorch` (smp) | U-Net+ResNet50 hazır |
| Optimizasyon | **Google OR-Tools** | Pickup-Delivery + capacity + time-window |
| Routing | **OSRM** (Türkiye lokal docker) | Mesafe matrisi |
| Yakıt modeli | Custom Python (Demir-Bektaş-Laporte 2014 CMEM) | Post-process eğim/yakıt |

### 6.2 Frontend

| Katman | Seçim | Neden |
|---|---|---|
| Web framework | **Streamlit** | Python-native, 2-3 saatte canlı dashboard |
| Harita | **Folium / Leafmap** | GEE layer toggle, mock veri overlay kolay |
| Grafik | **Plotly** | Interaktif tasarruf grafiği |
| Tablo / KPI | Streamlit native | yeterli |

**Alternatif:** React + Mapbox + FastAPI backend — daha cilalı görünür ama 24 saatte risk yüksek. Streamlit MVP için optimal.

### 6.3 Veri Yönetimi

| Veri | Yer | Format |
|---|---|---|
| Sentinel-2 / -1 ham | Google Earth Engine cache | EE asset, sadece export sırasında GeoTIFF |
| ASTER TIR Avanos sahnesi | `/data/aster/` lokal | GeoTIFF |
| Copernicus DEM Avanos | `/data/dem/` lokal | GeoTIFF |
| Manuel etiket (pozitif+negatif) | `/data/labels/` | GeoJSON + raster mask |
| Pretrained ağırlık | TorchGeo cache | .pt |
| Mock VRP girdi | `/mock/vrp_inputs.json` | JSON |
| Türkiye OSM | `/osrm/turkey-latest.osm.pbf` | PBF |
| WDPA Göreme polygon | `/data/wdpa_goreme.geojson` | GeoJSON |

### 6.4 Bağımlılık Listesi (requirements.txt taslağı)

```
# Veri
earthengine-api>=0.1.380
geemap>=0.30.0
rasterio>=1.3.9
shapely>=2.0
geopandas>=0.14
gdal>=3.7

# ML
torch>=2.0
torchgeo>=0.5
segmentation-models-pytorch>=0.3.3
pytorch-lightning>=2.1
albumentations>=1.3
scikit-learn>=1.3
numpy>=1.26

# VRP / Optimizasyon
ortools>=9.8
osrm-py  # OR HTTP client
networkx>=3.2

# Frontend
streamlit>=1.30
folium>=0.15
leafmap>=0.30
plotly>=5.18

# Yardımcı
pandas>=2.1
tqdm>=4.66
pydantic>=2.5
```

---

## 7. VERİ ERİŞİM HATTI — HACKATHON ÖNCESİ HESAP HAZIRLIĞI

| Veri Kaynağı | Hesap Açma | Beklenen Süre | Öncelik |
|---|---|---|:-:|
| **Copernicus Browser** (S1, S2, S5P) | dataspace.copernicus.eu | Anında | ★★★ |
| **Google Earth Engine** | earthengine.google.com (akademik) | 1-2 gün onay | ★★★ |
| **NASA Earthdata** (ASTER, Landsat) | earthdata.nasa.gov | Anında | ★★★ |
| **USGS Earth Explorer** (CORONA dahil) | earthexplorer.usgs.gov | Anında | ★★ |
| **DLR EnMAP EOC** | geoservice.dlr.de + EnMAP-Box plugin | Anında veri görüntüleme | ★★ |
| **PRISMA ASI** | prisma.asi.it | 1-2 hafta akademik onay | ★ |
| **GEZGİN (RASAT)** | gezgin.gov.tr (e-Devlet) | Anında | ★ |
| **MAPEG e-Maden** | mapeg.gov.tr | Anında (sadece tek-sorgu) | ★★ |
| **OpenStreetMap Türkiye** | geofabrik.de/europe/turkey | Anında PBF | ★★★ |
| **WDPA Göreme polygon** | protectedplanet.net | Anında | ★★ |
| **Copernicus DEM GLO-30** | spacedata.copernicus.eu | Anında | ★★★ |

**Stratejik tavsiye:** Tier 1 hesaplar (★★★ ve ★★ üst) hackathon başlamadan açılmalı. PRISMA dışında hepsi anında. PRISMA için akademik başvuru hackathon öncesi yapılırsa Avanos sahnesi olmasa bile referans Lipari/Cuprite sahnesi pitch'te kullanılır.

---

## 8. 24 SAATLİK BUILD PLANI

### 8.1 Saatlik İş Bölümü (4 kişilik ekip varsayımı)

| Saat | Modül A (CV+Uydu) | Modül B (VRP+Lojistik) | Frontend+Pitch | Veri+Etiketleme |
|:-:|---|---|---|---|
| 0-2 | GEE auth, S2+S1+DEM Avanos tile çekimi | Türkiye OSM + OSRM docker kurulum | Streamlit iskelet | MAPEG ruhsat sorgu, manuel etiket başlat |
| 2-4 | TorchGeo + SSL4EO-S12 yükleme, U-Net mimari | OR-Tools Pickup-Delivery tutorial | Folium harita, layer toggle | 30 pozitif + 100 negatif manuel etiket |
| 4-7 | U-Net fine-tune (Colab T4) | Mock veri seti yazımı (sentetik) | KPI dashboard, plotly grafik | ASTER TIR Avanos sahne indir, QI hesapla |
| 7-9 | Inference pipeline + threshold tuning | OR-Tools VRP çözüm + arc cost CMEM | Modül A çıktı görselleştirme | UNESCO buffer WDPA polygon hazırla |
| 9-12 | Change detection (Landsat 1985-2025 GIF) | Demir-Bektaş-Laporte CMEM Python implementasyonu | Modül B mock dashboard | Pre-cache: EnMAP/PRISMA görsel kanıt |
| 12-15 | Multi-sensor füzyon (S2+S1+DEM+ASTER) | DEM eğim entegrasyonu, fuel cost validasyon | 3 ekran flow entegrasyon | CORONA tarihi görsel pitch hook |
| 15-18 | Ablation study tablosu | Yakıt tasarruf rakamı (BlokBims senaryosu) | UI cila, animation | Mock CBAM PDF örneği |
| 18-20 | Edge case test (bulutlu sahne fallback) | Multi-depot vizyon mock görsel | Pitch deck draft | Jüri-soru hazırlık dosyası |
| 20-22 | **KOD FREEZE** (sadece bug fix) | **KOD FREEZE** | Pitch slayt finalizasyon | Demo backup script |
| 22-23 | Demo dry-run #1 | Demo dry-run #1 | Pitch provası #1 | Q&A simülasyon |
| 23-24 | Demo dry-run #2 + buffer | Demo dry-run #2 + buffer | Pitch provası #2 | Final hazırlık |

### 8.2 Ekip Beceri Profili Gereksinimi

| Rol | Beceri | Adı (TBD) |
|---|---|---|
| Modül A Lead | Python, PyTorch, uzaktan algılama temel, GEE | TBD |
| Modül B Lead | Python, OR-Tools, optimizasyon, OSM/OSRM | TBD |
| Frontend + Pitch | Streamlit, Folium, sunum becerisi, hibrit dil sunum | Tuna |
| Veri + Etiket + DevOps | QGIS, GeoJSON, docker, Linux | TBD |

### 8.3 "Won't Do" Listesi (24 Saatte YAPILMAYACAK)

- ❌ Hyperspectral PRISMA canlı işleme (sadece pre-cache görsel kanıt)
- ❌ Sentinel-1 InSAR koherens ağır işleme (sadece amplitude)
- ❌ Multi-depot canlı VRP (vizyon)
- ❌ Hub konum optimizasyonu canlı (vizyon)
- ❌ Gerçek pomza şirketi verisi ile demo (etik+KVKK riski)
- ❌ Mobile app (sadece web)
- ❌ Production-grade microservices (Streamlit monolitik)
- ❌ Otomatik DPP (Digital Product Passport) (vizyon)
- ❌ Gerçek zamanlı IoT kamyon takip
- ❌ Blockchain izlenebilirlik

---

## 9. DEMO AKIŞI — 3 EKRAN, 10 DAKİKA

### 9.1 Üç Ekran Mantığı

Cave2Cloud Winning Framework'ün altın kuralı: Sahnede tıklayacağım 3 ekran, üzerinde aşırı cila. Diğer modüller mock olabilir, bu üç ekran canlı + sıfır-bug.

#### Ekran 1 — INPUT: Pomza Saha Tarama (CANLI)
- Pomza şirketi sahibi (BlokBims persona) login
- Avanos haritası, kullanıcı poligon çiziyor
- "Bu bölgede pomza var mı?" → Modül A canlı koşuyor
- Loading: "Sentinel-2 görüntüsü çekiliyor (3 sn)... Sentinel-1 SAR çekiliyor (3 sn)... ASTER TIR yükleniyor (1 sn)... U-Net inference (5 sn)..."

#### Ekran 2 — TRANSFORMATION: Multispektral AI Analizi (CANLI)
- Multispektral bantlar görselleştirme (RGB, B11/B12 oranı, NDVI yeşil dışlama, Albedo)
- U-Net segmentasyon çıktısı: pomza olasılık haritası ısı haritası
- Yan panel: tespit edilen pomza sahaları liste, her birinin %güven + alan bilgisi
- UNESCO buffer red flag overlay (varsa)
- Change detection: Landsat 1985-2025 zaman kaydırıcı animasyonu

#### Ekran 3 — OUTPUT: Operasyonel Pomza Lojistik Kararı (MOCK CANLI HİSSİ)
- Fabrika konumu girdi (BlokBims Çardak)
- VRP çözücü 5 sn'de günlük pomza taşıma rotası
- Harita üzerinde 3 kamyonun rotası animasyonlu çiziliyor
- KPI tablosu: "3 kamyon, 7 saat, 142 km, 189 L yakıt, 504 kg CO₂"
- Alternatif rota karşılaştırması: "Sezgisel rota %15 fazla yakıt"
- "Yıllık tasarruf BlokBims için: ~₺30,7 milyon" infografik
- "CBAM-uyumlu emisyon kaydı PDF indir" buton (mock PDF)

### 9.2 Pitch Story Spine (10 dakika)

| Süre | Bölüm | Anahtar Mesaj |
|:-:|---|---|
| 0:00-0:30 | Hook | "Türkiye dünya pomza üretimi 1. — ihracat değerinde 4. 600 bin ton ham mal, ton başı 38 dolar. Yunanistan aynı tonajla 5 katı para kazanıyor. Neden?" |
| 0:30-1:30 | Problem | Saha-bilgi kopukluğu + sezgisel kamyon rotası + dijital görünmezlik |
| 1:30-3:00 | Çözüm Anatomisi | İki modüllü AI mimarisi (görsel diyagram) |
| 3:00-6:00 | **CANLI DEMO** | 3 ekran — Avanos haritası → AI tespit → rota optimizasyon |
| 6:00-7:00 | Sürdürülebilirlik & Etik | UNESCO red flag, CBAM emisyon kaydı, Türkiye İklim Kanunu uyumu |
| 7:00-8:00 | Ticarileşme | TÜBİTAK BiGG 2026, gelir modeli, ilk 5 pomza pilot müşterisi |
| 8:00-9:00 | Vizyon | "Avanos'tan başlar, Niğde-Bitlis'e, Yali-Lipari-Idaho'ya. Türk uydusu Türk pomzasına bakıyor." |
| 9:00-10:00 | Q&A | |

### 9.3 Hibrit Sunum Dili Stratejisi

**Türkçe konuşulacak bölümler:** Hook, Problem, Sürdürülebilirlik, Vizyon (Atasever, Karvar, Öbekli ve yerel jüri için samimi bağ).

**İngilizce konuşulacak bölümler:** Çözüm anatomisi (teknik mimari diyagram, akademik terimler U-Net, Pollution-Routing, CMEM), Ticarileşme (TÜBİTAK BiGG, CBAM, ETS terimleri).

**İki dilli (geçişli) bölümler:** CANLI DEMO sırasında ekran başlıkları İngilizce ("Pumice Detection Confidence Map"), spiker Türkçe açıklıyor. Q&A jürinin diline göre.

Bu strateji sembolik AI koltuğu ve Karvar (uluslararası TTO ağı bağlantısı) için "uluslararası zemin" sinyali verir; aynı zamanda Türk jüriler için samimi diyalog korunur.

---

## 10. RİSK MATRİSİ VE MİTİGASYON

### 10.1 Modül A Riskleri

| Risk | Olasılık | Etki | Mitigasyon |
|---|:-:|:-:|---|
| Sentinel-2 Avanos sahnesi bulutlu | Orta | Düşük | 5 günlük revisit + cloud mask + en yakın temiz tile fallback; pre-cached temiz tile zaten lokal |
| Sentinel-1 SAR processing yavaş | Düşük | Orta | Sadece amplitude (VV+VH), InSAR vizyonda |
| ASTER SWIR 2008 sonrası bozuk | Yüksek (gerçek) | Düşük | TIR yeterli; S2 SWIR onu zaten kapsıyor |
| MAPEG ruhsat shapefile yok | Yüksek (gerçek) | Orta | Manuel poligon çizimi (Avanos için 30 saha 2 saat) |
| Etiketli pomza veri seti yok | Yüksek (gerçek) | Orta | Transfer learning (SSL4EO-S12) + manuel etiket; küçük veri ile fine-tune mümkün |
| GPU yok | Düşük | Yüksek | Google Colab T4 yedek; pretrained weights küçük tile (256×256) ile T4'e sığar |
| U-Net F1 < 0,70 | Orta | Orta | Ablation study farklı bant kombinasyonları; threshold tuning |
| UNESCO buffer false positive | Orta | Orta | WDPA polygon + 1000 m konservatif buffer; bu alanlar etiket dışı |

### 10.2 Modül B Riskleri

| Risk | Olasılık | Etki | Mitigasyon |
|---|:-:|:-:|---|
| OSRM Türkiye PBF büyük (>1 GB) | Yüksek | Orta | Hackathon öncesi indir; sadece TR-71 bbox kırpılır |
| OR-Tools Pickup-Delivery öğrenme eğrisi | Orta | Orta | Resmi tutorial 4 saatte örnek koddan müdahale yapılabilir |
| CMEM parametreleri Türkiye dizel için kalibre değil | Yüksek (gerçek) | Düşük | Demir et al. 2014 default değerleri kullan; pitch'te "ileri çalışmada Türkiye filo verisiyle kalibre edilecek" |
| Mock veri inandırıcı değil | Orta | Yüksek | Avanos gerçek konumlar + gerçek DEM eğim; sadece talep miktarı sentetik |
| Çözüm 5 sn'den uzun | Düşük | Orta | Problem boyutu (4 ocak + 1 fabrika + 3 kamyon) küçük; çözüm <2 sn |
| Yakıt tasarrufu rakamı abartılı | Orta | Yüksek | Konservatif %15 (literatür alt sınırı); pitch'te "literatür aralığı %10-25" denir |

### 10.3 Demo / Sunum Riskleri

| Risk | Olasılık | Etki | Mitigasyon |
|---|:-:|:-:|---|
| Demo crash (canlı U-Net inference) | Orta | Yüksek | "Demo modu" fallback: pre-computed JSON çıktıları; aynı ekrana yüklenir |
| İnternet kesintisi (GEE) | Düşük | Yüksek | Avanos sahnesi lokal cache; offline mod hazır |
| Pitch süresi 10 dk aşıyor | Orta | Orta | Dry-run ×2; segment-bazlı saat tutma |
| Jüri "neden 8 uydu, 1 yetmiyor mu?" sorusu | Yüksek | Orta | §3.1 5 fiziksel imza tablosu cevap olarak hazır |
| Jüri "tarım için kullanılır mı?" sorusu | Düşük | Düşük | "Pomza odaklıyız; pomza ekonomisi başka bir uygulama alanına ihtiyaç duymadan kendi başına %45 dünya üretimi anlatısıdır" |
| Jüri "yeni pomza ocakları açtırır mı, UNESCO'ya zarar?" | Orta | Yüksek | UNESCO buffer red flag + change detection ile mevcut alan izleme = mimari kanıt |

---

## 11. HEDEF MÜŞTERİ PROFİLİ — B2B POMZA ÜRETİCİSİ ŞİRKETLER

### 11.1 İdeal Müşteri Profili (ICP)

| Boyut | Tanım |
|---|---|
| Sektör | Pomza üretimi (HS 2513), bims yapı malzemesi, mikronize pomza |
| Coğrafya | Birincil: Nevşehir/Avanos, Niğde, Aksaray; ikincil: Bitlis, Kayseri, Isparta |
| Şirket büyüklüğü | Yıllık üretim ≥50.000 ton, kamyon filosu ≥10 araç |
| Karar verici | Şirket sahibi/genel müdür (sektör KOBİ ağırlıklı, hiyerarşi düz) |
| Mevcut yazılım kullanımı | Excel + WhatsApp ağırlıklı; ERP varlığı düşük |
| Bütçe | Yıllık IT/yazılım bütçesi ₺50K-500K bandı |
| Alım kararı süresi | 1-3 ay (sahibin kişisel kararı) |

### 11.2 Pomza Üreticisi Müşteri Persona — "Pomza Ali Bey"

> *Avanos'ta 1985'ten beri pomza işiyle ilgilenen Ali Bey, 65 yaşında, mühendis değil ama saha bilgisi 40 yıllık. 12 kamyonu, 2 fabrikası (Avanos+Niğde), 3 ruhsatlı sahası var. Yıllık üretim ~80.000 ton, 6 ülkeye ihracat. Ofis Excel'de, kamyon rotası şoförün başında, saha jeolojisi kafasında. Oğlu (35) bilgisayar mühendisi ama şirkete daha tam katılmadı.*
>
> *Ali Bey'in dediği şey: "Geçen yıl mazot 280 milyon liraya çıktı. Ben ne yapacağımı bilmiyorum, sezgiyle gidiyorum. Bana bir yazılım gelse, deseki 'bugün şu rotayı takip et', %15 yakıt kazandırırsa ayda 3-4 milyon eder. Ama ben hiçbir teknolojiyi çalıştıramam, basit olsun, telefondan girilsin."*

### 11.3 Değer Önerisi — Beş Acıya Beş Çözüm

| Pomza Üreticisi Acısı | PomzaScope Çözümü | Ölçülebilir Fayda |
|---|---|---|
| Kamyon rotası sezgisel, mazot yüksek | Modül B günlük yakıt-optimal rota önerisi | %10-25 yakıt tasarrufu (literatür) |
| Saha jeolojisi kâğıtta, ruhsat yenileme zor | Modül A uydu tabanlı saha izleme + rezerv proxy | Saha karar süresi 2 hafta → 1 gün |
| Pomza ocağı yıl yıl genişliyor, izleme yok | Modül A change detection (yıllık alan değişimi) | Otomatik %X büyüme raporu |
| CBAM/ETS uyum stresi var, ölçüm altyapısı yok | Modül B CBAM-uyumlu emisyon kaydı PDF | MRV-hazır rapor üretimi |
| Yeni saha açma, UNESCO/ÇED riski belirsiz | UNESCO buffer red flag uyarısı | Coğrafi etik filtre, ön-itiraz önleme |

### 11.4 Gelir Modeli (B2B SaaS)

| Tier | Aylık Fiyat | Kapsam | Hedef Müşteri |
|---|---|---|---|
| **Başlangıç** | ₺7.500/ay | Modül A saha izleme + 1 fabrika lokasyonu, ayda 50 saha tarama | Mikro pomza üreticisi (5-15 kamyon) |
| **Pro** | ₺15.000/ay | + Modül B canlı VRP, 3 fabrika, sınırsız tarama, CBAM raporu | Orta ölçek (15-50 kamyon) |
| **Enterprise** | ₺25.000-40.000/ay | + multi-depot + hub konum optimizasyonu + API erişimi + özelleştirilmiş raporlama | BlokBims tipi büyük üretici (50+ kamyon) |

**Ek gelir:**
- Per-API: saha analizi başına ₺500, rota optimizasyonu başına ₺50
- Premium hizmet: CBAM/ETS rapor hazırlama danışmanlığı (proje başına ₺25.000-75.000)

**TAM hesabı:**
- Türkiye'de 81 pomza firması × ortalama ₺15.000/ay = ~₺14,5M/yıl
- Uluslararası genişleme (Yunanistan, İtalya, ABD pomza üreticileri) ile 5-10× (~₺75-150M)

---

## 12. TİCARİLEŞME HATTI

### 12.1 30/60/90 Yol Haritası

| Vade | Hedef | Karvar/Öbekli için Anlam |
|---|---|---|
| **30 gün** | BlokBims veya Miner Madencilik ile pilot anlaşması; 1 saha + 1 fabrika için Avanos demo deploy | Karvar: TR-71 bölgesinde ilk müşteri |
| **90 gün** | Modül A doğruluk skoru >%85 saha doğrulama; Modül B yakıt tasarrufu rakamı pilot ile validate | Öbekli: Endüstriyel kanıt |
| **6 ay** | TÜBİTAK 1512 BiGG başvurusu; CAPPIN²C kuluçka programı | Karvar: TTO entegrasyon |
| **12 ay** | Bitlis 2. saha pilotu; LAVA Mining (Yunanistan) ile dış pazarlama görüşmesi | Vizyon: global ölçek |
| **24 ay** | AB DPP entegrasyonu; 5+ Türk pomza üreticisi müşteri; CBAM declarant servisi | Tam ürün-pazar uyumu |

### 12.2 TÜBİTAK 1512 BiGG 2026-1 Takvimi

| Aşama | Tarih |
|---|---|
| Aşama 1 hızlandırma başlangıcı | 15 Nisan 2026 |
| Aşama 2 başvuru penceresi | 15 Haziran – 3 Temmuz 2026 |
| Belge ulaştırma | 10 Temmuz 2026 |
| Panel değerlendirme | 13 Temmuz – 28 Ağustos 2026 |
| Sonuç açıklaması | 1-4 Eylül 2026 |
| Şirket kurulum son tarihi | 30 Eylül 2026 |
| Destek tutarı | ₺1.350.000 / %3 hisse |

**Hackathon ile bağlantı:** Hackathon 24 saatlik MVP, BiGG Aşama 1 başvurusunun teknik kanıtı. PomzaScope BiGG için **doğrudan başvuru hazır**.

### 12.3 Hibe ve Fon Eşleşmesi

| Program | Bütçe / Tutar | Pomza Uygunluğu |
|---|---|---|
| **AHİKA Yeşil Dönüşüm Hibe 2025** | 25 milyon TL bölge bütçesi | Mikro/küçük pomza işletmeleri için açık; PomzaScope onların MRV altyapısı |
| **EBRD-KOSGEB Dijital Dönüşüm** | 300 milyon Avro | KOBİ dijital dönüşüm; SaaS aboneliği finanse edilebilir |
| **TÜBİTAK 1512 BiGG** | 1,35M TL | Yukarıda |
| **TÜBİTAK 1501** | Proje bazında | Pomza Ar-Ge projesi olarak kurgulanabilir |
| **AB Horizon Europe Mining Innovation** | 2027 sonrası | Türk-Yunan-İtalyan pomza konsorsiyumu vizyon |

### 12.4 IP / Patent Stratejisi

| IP Kategori | Patentlenebilirlik | Yorum |
|---|:-:|---|
| U-Net mimari | ❌ | 2015'ten beri kamuya açık |
| Multi-sensor pomza segmentasyon kombinasyonu | 🟡 Fayda modeli | "S2+S1+ASTER TIR+DEM kombinasyonu pomza için özgün" iş süreci patenti |
| CMEM tabanlı pomza kamyonu yakıt formülü | 🔴 | 2014 akademik literatür |
| **PomzaScope Saha Karakterizasyon → Lojistik Karar entegrasyon mimarisi** | 🟢 İş süreci patenti | İki modülün birbirini beslediği veri akışı **ürün-spesifik** |
| UNESCO buffer red flag mimari kuralı | 🟡 | Domain-specific iş kuralı |
| CBAM-uyumlu pomza emisyon raporu formatı | 🟡 Telif/format | Standart formata atıfla |

**Karvar ekseni için:** Patent + fayda modeli + iş süreci patenti üçlü stratejisi sunulur. Saf teknik patent zayıf olsa da **uçtan uca pomza-özelinde mimari** bir bütün olarak korunabilir.

---

## 13. JÜRİ-BAZLI PİTCH STRATEJİSİ

### 13.1 Doç. Dr. Sema Atasever (NEVÜ — Akademik AI/ML)

**Hassasiyetler:** Doğru ML modeli, açıklanabilirlik (XAI), doğru veri seti, yöntem gerekçelendirme.

**PomzaScope cevapları:**
- TorchGeo + SSL4EO-S12 MoCo pretrained Sentinel-2 13-bant — akademik literatür ile bağ (Wang et al. 2023, Braham et al. 2025 SpectralEarth foundation models)
- U-Net'e Grad-CAM eklenmiş — hangi bantın hangi piksel için baskın olduğu görselleştirilir
- Ablation study tablosu: her uydunun katma değeri ölçülmüş
- Ground truth: MAPEG ruhsat poligonları + manuel etiket; transfer learning ile küçük veri durumu yönetiliyor
- Ninomiya 2002 Quartz Index akademik referansı

**Beklenen skor:** 8/10

### 13.2 Arif Öbekli (NEVSAC, TOBB Genç Girişimciler — Sanayi/Tedarik Zinciri) ★

Bu jürinin altın madeni kategori. PomzaScope'un en yüksek puan alacağı eksen.

**Hassasiyetler:** Sanayicinin somut acı noktası, yerel iş insanı için anlamlılık, ölçülebilir verim, 30 günde pilot.

**PomzaScope cevapları:**
- "BlokBims 150 kamyon × günlük 250 km × %15 yakıt tasarrufu = ~₺30,7 milyon/yıl" somut rakam
- Pomza KOBİ envanteri 81 firma — pilot müşteri segmenti hazır ve görünür
- 30 gün içinde Miner Madencilik veya BlokBims ile pilot anlaşması yapılabilir
- Mazot optimizasyonu Öbekli'nin sektörel diline tam uyuyor

**Beklenen skor:** 9/10

### 13.3 Yasin Bıkmazer (Butiksoft — SaaS/Otelcilik)

**Hassasiyetler:** Ürün-pazar uyumu, SaaS mantığı, demo akıcılığı, kullanıcı akışı (UX), tekrar eden gelir modeli.

**PomzaScope cevapları:**
- Streamlit + Folium B2B SaaS dashboard canlı demo
- 3 tier'lı abonelik gelir modeli (Başlangıç/Pro/Enterprise) — net SaaS yapı
- Per-API ek gelir + Premium danışmanlık
- TAM ~₺14,5M Türkiye / 5-10× uluslararası
- Kullanıcı akışı: 3 tıkla saha tarama, 1 tıkla rota — "telefonu açan şirket sahibi anlar" basitlik

**Risk:** Bıkmazer'in konfor bölgesi turizm/PMS, B2B madencilik SaaS değil. Bu eksende skoru 7'ye çekmek için **demo akıcılığı** ve **UX basitliği** öne çıkarılır.

**Beklenen skor:** 7/10

### 13.4 Pakize Yeşiltaş Karvar (Kapadokya Teknopark — TTO/Ticarileşme)

**Hassasiyetler:** TÜBİTAK 1512 BiGG uygunluğu, IP/Patent, TR-71 bölgesi etkisi, Yeşil Mutabakat hikâyesi.

**PomzaScope cevapları:**
- BiGG 2026-1 takvimi takip ediliyor; PomzaScope tam Aşama 1 hazır
- AHİKA TR-71 Master Dökümanı'nın Stratejik Öncelik 2 (Sanayi/Yeşil) ile birebir örtüşür
- IP stratejisi: iş süreci patenti + fayda modeli + telif (mimari kombinasyon)
- CBAM 2026 + Türkiye İklim Kanunu (Temmuz 2025) doğrudan hattı
- TR-71 (Nevşehir, Niğde, Aksaray) bölgesinin tamamı pomza/endüstriyel mineral kuşağı

**Beklenen skor:** 8/10

### 13.5 Sembolik AI Koltuğu (LLM Rubric Scoring)

**Boyutlar:** Innovation, Feasibility, Impact, Scalability, Presentation, Ethics.

**PomzaScope cevapları:**
- **Innovation:** Pomza+uydu+AI literatürde nadir; 8 uydulu çoklu kaynak füzyonu özgün
- **Feasibility:** Sentinel-2 ücretsiz, OR-Tools açık kaynak, pretrained models hazır
- **Impact:** 600 bin ton/yıl × somut tasarruf rakamı; CBAM hazırlık
- **Scalability:** Türkiye'den global pazara — Yunanistan/Yali, İtalya/Lipari, ABD/Idaho/Hess pomzasına model genişletilebilir
- **Ethics:** UNESCO buffer red flag mimari kural — sistem **kendi içinde etik filtre** taşıyor; "kazıyı artırma değil, akıllı kazma" anlatısı

**Beklenen skor:** 8/10

### 13.6 Birleşik Tahmin

| Jüri | Beklenen Skor |
|---|:-:|
| Atasever | 8 |
| Öbekli | 9 |
| Bıkmazer | 7 |
| Karvar | 8 |
| AI Koltuğu | 8 |
| **Ortalama** | **8,0** |

Cave2Cloud Winning Framework'ün eşiği "her eksen ≥7 + en az bir eksen ≥9". PomzaScope **iki kuralı da karşılıyor** (en zayıf eksen 7, en güçlü 9).

---

## 14. KPI VE DOĞRULAMA METRİKLERİ

### 14.1 Modül A — Teknik KPI'lar

| KPI | Hedef | Ölçüm Yöntemi |
|---|:-:|---|
| Pixel-level F1 (pomza vs non-pomza) | ≥0,75 | Manuel etiket test seti |
| IoU (saha bazında) | ≥0,60 | Aynı |
| Object-level Recall | ≥0,80 | Bilinen 10 sahanın kaçı tespit edildi |
| FPR UNESCO buffer içinde | ≤0,05 | WDPA buffer içinde yanlış pozitif sayısı |
| Inference süresi (1 km² Avanos sahnesi) | ≤10 sn | T4 GPU veya Colab |
| Change detection accuracy | ≥%80 | Landsat 1985→2025 manuel kontrol |

### 14.2 Modül B — Operasyonel KPI'lar

| KPI | Hedef | Ölçüm Yöntemi |
|---|:-:|---|
| Yakıt tasarrufu (mock senaryo) | %15 | Optimal vs sezgisel rota karşılaştırma |
| VRP çözüm süresi (4 ocak + 1 fabrika + 3 kamyon) | ≤5 sn | OR-Tools wall time |
| CO₂ azalma (somut rakam) | ~1.642 ton/yıl (BlokBims senaryosu) | CMEM hesaplama |
| Çözüm kalitesi (gap to optimal) | ≤%5 | OR-Tools first-improvement metasezgi raporu |

### 14.3 Demo / Pitch KPI'ları

| KPI | Hedef |
|---|---|
| Demo crash sayısı | 0 |
| Pitch süre uyumu | 9-10 dk arası |
| Q&A cevap-soru oranı | 100% (hazır FAQ ile) |
| Jüri "evet" şüphesiz cevap oranı | ≥%80 |

### 14.4 Hackathon Sonrası Doğrulama (30 Gün)

| KPI | Hedef |
|---|---|
| Pilot pomza şirketi anlaşması | 1 (BlokBims veya Miner) |
| Saha doğrulama (uzman jeoloğun manuel kontrolü) | 5 saha |
| Modül A F1 saha doğrulamasında | ≥0,75 |
| Modül B yakıt tasarrufu (gerçek pilot veriyle) | ≥%10 |

---

## 15. AKADEMİK ÇAPALAR VE REFERANSLAR

### 15.1 Pomza Karakterizasyonu (Domain Akademik Temel)

| Konu | Referans |
|---|---|
| Kapadokya pomzası jeokimyasal parmak izi | Steinhauser et al. 2006 — *Journal of Quaternary Science* / *Applied Radiation & Isotopes*, INAA ile Kavak/Çemilköy/Tahar/Gördeles ignimbritleri |
| Pomza zenginleştirme ve hazırlama | Aksay Kılınç vd. 2016 — "Pomza Cevherinin Hazırlanması ve Zenginleştirilmesi" *AKÜ FEMÜBİD* 16:025802 |
| Türkiye pomza rezerv ve sektör profili | MTA Maden Serisi — Pomza (Eroğlu & Şahiner) |
| Nevşehir pomza endüstrisi | Orhan, Dinçer, Akın, Çoban — *Nevşehir Bilim ve Teknoloji Dergisi* |
| Pomza spektral imza (okyanus, transfer ile karasal) | Zheng et al. 2022 — Pumice Raft Index, *Remote Sensing* 14(22):5854 |
| Volkanik camsı kayaçlar TIR spektroskopi | Lee et al. 2018 — AGU Fall Meeting V51D-0142 |

### 15.2 Uzaktan Algılama ve Mineral Tespiti

| Konu | Referans |
|---|---|
| Sentinel-2 jeolojik kullanım potansiyeli | van der Meer et al. 2014 — *Remote Sensing of Environment* 148:124-133 |
| Sentinel-2 + ASTER + Landsat alterasyon haritalama | Salem et al. 2023 — *Scientific Reports* 13:7309 |
| Sentinel-2 13-bant lithology classification | Wang et al. 2018 — *Remote Sensing* 10(4):638 (Shibanjing Ophiolite) |
| ASTER TIR Quartz Index ve SiO₂ kimyasal içerik | Ninomiya 2002 — SPIE 4710:191; Ninomiya et al. 2005 *RSE* |
| Sentinel-1 SAR açık ocak change detection | Mazza et al. 2023 — *Remote Sensing* 15(24):5664 |
| Sentinel-1 InSAR koherens maden aktivitesi | Wang et al. 2021 — Sentinel-1A InSAR Coherence Open-Pit Coal Mines |
| EnMAP hyperspektral mineral keşfi | Chirico et al. 2024 — McDermitt kalderası |
| EnMAP foundation models | Braham et al. 2025 — SpectralEarth, *IEEE JSTARS*, arXiv:2408.08447 |
| PRISMA hyperspektral mineral haritalama | Bedini & Chen 2020 — Cuprite Nevada |
| Açık ocak madeni semantic segmentation | MineSegSAT (MacDonald et al. 2023) — arXiv:2311.01676 |
| Maden tespiti GEE + Sentinel-2 | Balaniuk et al. 2020 — mining-discovery-with-deep-learning |
| Bi-temporal change detection benchmark | MineNetCD (Yu et al. 2024) — arXiv:2407.03971 |
| Sentinel-2 self-supervised pretraining | SSL4EO-S12 (Wang et al. 2023) |
| Kapadokya volkanik haritalama | Demirkesen 2008 — Landsat-7 ETM+ + SRTM DEM Nevşehir, *IJRS* 29(14) |

### 15.3 Optimizasyon ve Lojistik

| Konu | Referans |
|---|---|
| Pollution-Routing Problem temel | Bektaş & Laporte 2011 — *Transportation Research Part B* 45(8) |
| Bi-objective PRP (yakıt + CO₂) | Demir, Bektaş, Laporte 2014 — *European Journal of Operational Research* |
| PRP fleet size and mix | Koç & Bektaş 2014 — CIRRELT-2014-26 |
| PRP with Speed Optimization & Uneven Topography | Lai, Costa, Demir et al. 2021 — arXiv:2105.09229 |
| Eco-routing OSRM elevation | Ghosh et al. 2020 — arXiv:2011.13556 |
| Open-pit mine truck dispatching | Souza et al. 2010; Rodrigues & Pereira 2020 |
| DRL truck dispatch | Noriega & Pourrahimian 2024 — *Computers & Operations Research* |
| RL fleet dispatching GHG reduction | Huo, Sari, Zhang 2022 |

### 15.4 Hackathon Domain ve Mevzuat

| Konu | Referans |
|---|---|
| ÇED Yönetmeliği 2022 | Resmi Gazete 29.07.2022 / 31907 |
| Maden Kanunu 3213 | orgtr.org/maden-kanunu-3213-sayili-kanun |
| UNESCO Göreme Milli Parkı | whc.unesco.org/en/list/357 + WDPA polygon (protectedplanet.net) |
| CBAM | EU Reg 2023/956 — taxation-customs.ec.europa.eu/cbam |
| Türkiye İklim Kanunu 7552 | 9 Temmuz 2025 — icapcarbonaction.com |
| Maden rehabilitasyon NDVI | Werner et al. UNSW 2013 (WorldView-2) |

---

## 16. MEVZUAT ÇERÇEVESİ

### 16.1 Maden Kanunu 3213 — Pomza için Kritik Maddeler

- **Madde 7:** "İçme ve kullanma suyu rezervuarının max su seviyesinden itibaren 1000-2000 m'lik şeritte galeri usulü patlatma yasak. 2000 m sonrası koruma alanında ÇED'e göre uygun bulunan maden istihracı ve tesis yapılabilir."
- Yerleşim mesafe sınırlaması yönetmelikte tek standart sayısal eşik olarak verilmemiş; proje bazında ÇED değerlendirmesi.
- **Hassas Yöre kavramı:** Korunan alanlar, milli parklar, dünya mirası — Göreme Milli Parkı bu kapsamda. Pomza ruhsat başvurusunda kritik filtre.

### 16.2 ÇED Yönetmeliği 2022

- **EK-I:** Zorunlu ÇED Raporu projeleri (büyük ölçek)
- **EK-II:** Seçme-Eleme Kriterleri ("Çevresel Etki Önemlidir/Önemsizdir" karar)
- Kapadokya pomza ocakları **EK-II'de** maden grubu II(a) olarak değerlendirilir; eşik 100.000 m³/yıl üstü ÇED kararı zorunlu olabilir.

### 16.3 CBAM 2026 ve Türkiye ETS

- **CBAM (EU 2023/956):** 1 Ocak 2026 itibarıyla definitive phase başladı. Pomza/bims **doğrudan** kapsamda değil ama **çimento puzzolanı** olarak kullanıldığında dolaylı etki var. 2030'a kadar tüm EU ETS sektörleri kapsanması bekleniyor.
- **Türkiye İklim Kanunu 7552 (9 Temmuz 2025):** 2026'da pilot ETS başlıyor, idari ceza %80 indirimli. Kapsam: enerji-yoğun sektörler (enerji, metal, çimento, gübre). Pomza üreticileri çimento sektörü ile dolaylı bağlantılı.
- **MRV altyapı şartları:** Emission permit zorunlu (3 yıl içinde), bağımsız doğrulama, dönemsel raporlama. Pomza KOBİ'leri için Scope 1 (kamyon dizel, jeneratör) + Scope 2 (elektrik) ölçümü → MRV sistemi gerekli.
- **PomzaScope ile bağlantı:** Modül B çıktısı (kamyon dizel L/ton-km × CO₂ faktörü) tam olarak Scope 1 emisyon kaydıdır — ETS MRV altyapısına uyumlu.

### 16.4 UNESCO Göreme Milli Parkı

- **WHC Liste No:** 357 — Göreme Milli Parkı ve Kapadokya Kayalık Sit Alanları (1985)
- **GIS verisi:** Resmi UNESCO vektör shapefile halka açık değil. Workaround: **WDPA polygon (protectedplanet.net)** + OSM "Goreme National Park" relation + 500-1000 m konservatif buffer.
- **Pomza için anlam:** Buffer içinde tespit edilen pomza alanı için yeni ruhsat başvurusu yüksek riskli; PomzaScope bu alanları kırmızı işaretle gösterir, üreticiyi proaktif uyarır.

---

## 17. EYLEM LİSTESİ — HACKATHON ÖNCESİ 24 SAAT

### 17.1 Hesap Hazırlığı (Önce yapılacak)

1. ✅ Copernicus Browser hesap (anında)
2. ✅ Google Earth Engine akademik onay (1-2 gün — **HEMEN BAŞVUR**)
3. ✅ NASA Earthdata hesap (anında)
4. ✅ USGS Earth Explorer hesap (anında)
5. ✅ DLR EnMAP EOC + EnMAP-Box QGIS plugin (anında)
6. ✅ WDPA Protected Planet API key (anında)

### 17.2 Veri Pre-Cache (Hackathon başlamadan)

7. ✅ Sentinel-2 Avanos sahnesi (en son temiz, bulutsuz) GEE'de cache + lokal GeoTIFF
8. ✅ Sentinel-1 Avanos GRD sahnesi (1 ay) lokal
9. ✅ ASTER TIR Avanos sahnesi (Earthdata) lokal
10. ✅ Copernicus DEM GLO-30 Avanos tile lokal
11. ✅ Landsat 1985, 2000, 2015, 2025 Avanos snapshot GIF
12. ✅ EnMAP Avanos sahnesi (varsa) DLR EOC indirme
13. ✅ Türkiye OSM PBF (geofabrik) → Avanos bbox kırp
14. ✅ WDPA Göreme polygon GeoJSON
15. ✅ MAPEG ruhsat (Avanos için manuel poligon — QGIS, 1-2 saat)

### 17.3 Yazılım Stack Hazırlığı

16. ✅ Python 3.11 venv kurulumu
17. ✅ TorchGeo + segmentation-models-pytorch kurulumu
18. ✅ SSL4EO-S12 MoCo pretrained ağırlık indirilmiş
19. ✅ OR-Tools + ortools-python kurulumu
20. ✅ OSRM Türkiye lokal docker test
21. ✅ Streamlit + Folium + Leafmap kurulumu
22. ✅ Ngrok / localtunnel demo paylaşım için yedek

### 17.4 Ekip Hazırlığı

23. ✅ Ekip 4 kişi rolleri netleştirildi (Modül A / Modül B / Frontend+Pitch / Veri+Etiket)
24. ✅ Tuna pitch hibrit dil senaryosu kafasında
25. ✅ Demo backup script (canlı çökerse mock JSON yükleme)
26. ✅ FAQ dokümanı (Jüri için 30 muhtemel soru + cevap)
27. ✅ Pitch deck taslağı (8 ana slayt)

### 17.5 Sunum Hazırlığı

28. ✅ Hibrit dil pasajları belirlenmiş (TR/EN geçişler)
29. ✅ "Pomza odaklı" mesajı her slaytta korunmuş — başka uygulama yok
30. ✅ BlokBims senaryosu somut rakamla hazır
31. ✅ UNESCO red flag etik anlatı net
32. ✅ Vizyon slaytı (Yali/Lipari/Idaho global ölçek)

---

## 18. KAPANIŞ NOTU

PomzaScope Ahmet Abi'nin orijinal iki katmanlı vizyonunun teknik tercümesidir; tarım, güneş paneli veya başka uygulama alanı içermez, sadece pomza tedarik zincirinin başını dijitalleştirir. Modül A çoklu uydudan pomza alanı tespiti ve change detection yapar; Modül B bu sahalardan üretici fabrikalara taşıma rotasını yakıt-optimal hâle getirir. İki modül entegre bir B2B SaaS olarak pomza üretici şirketlere sunulur.

24 saatlik hackathon penceresinde Modül A canlı (Sentinel-2 + Sentinel-1 + ASTER TIR + Copernicus DEM, U-Net + SSL4EO-S12 pretrained) çalışır; Modül B sentetik Avanos verisiyle mock olarak demo edilir; iki modülün entegrasyonu mimari diyagram ile sunulur. Cave2Cloud temasının literal cisimleşmesi olarak (Türkiye dünya pomza üretiminin %45'i, rezervinin %15,8'i, Nevşehir'in %17 payı), proje hackathon kategorisi *Akıllı Tedarik Zinciri*'nin doğal yuvasıdır.

Beş jüri ekseninde beklenen ortalama skor 8,0/10 (Atasever 8, Öbekli 9, Bıkmazer 7, Karvar 8, AI Koltuğu 8); her eksen ≥7 ve en az bir eksen ≥9 kuralı karşılanır. Pilot müşteri olarak BlokBims (150 kamyon, 47 ülke, 500 kW solar) öne çıkar; somut yakıt tasarrufu rakamı (~₺30,7M/yıl) Öbekli ekseninde dramatik etki yaratır.

Hackathon sonrası 30 günde pilot anlaşması, 6 ayda TÜBİTAK 1512 BiGG başvurusu (1,35M TL destek), 12 ayda Bitlis 2. saha + LAVA Mining Yunanistan görüşmesi, 24 ayda AB DPP entegrasyonu yol haritasındadır.

> *"Kapadokya'nın peri bacaları milyonlarca yılda tek tek şekillendi; bu fikrin pomza ekonomisini global pazara taşırken onları korumaya nasıl yardım ettiğini göstermek 24 saatinizdir."*

---

## EK A — DOSYA REFERANSLARI

Bu rapor aşağıdaki proje dosyalarındaki bilgileri sentezleyerek hazırlanmıştır:

| Dosya | Katkı |
|---|---|
| `ahmet_abi_proje_fikri.txt` | Orijinal fikir metni — iki katmanlı AI mimarisi |
| `ahmet_abi_proje_fikri_analizi.md` | Jüri-bazlı skor matrisi, SWOT, sektör profili, BlokBims/Miner pilot adayları |
| `uydu_verileri_derinlemesine_arastirma.md` | 8 uydulu Tier 1/2/3 portföyü, Ninomiya QI, EnMAP foundation models |
| `PomzaScope__Kapadokya_Hackathon_2026_Deep_Research_Report.md` | TorchGeo SSL4EO-S12 stack, OSRM+OR-Tools, mevzuat çerçevesi |
| `Pumice_Mining_Intelligence__Satellite_AI_and_Route_Optimization_Landscape_for_Cappadocia_Hackathon_2026.md` | Rakip projeler (KoBold, Earth AI, MineSegSAT, EnMAP+EnGeoMAP), özgünlük analizi |
| `kapadokya_hackathon_2026_juri_raporu.md` | Jüri profilleri (Atasever, Öbekli, Bıkmazer, Karvar) |
| `pomza_global_pazar_analizi_md.pdf` | Türkiye 4. ihracat sırası, FOB rakamları |
| `pomza_kobi_envanter_md.pdf` | 81 firma profili, dijital olgunluk 3,2/10 |
| `pomza_yesil_mutabakat_analizi_md.pdf` | CBAM, Türkiye ETS, Scope 1+2 emisyon |
| `Team_Feza_Cave2Cloud__Kapadokya_Hackathon_2026_Winning_Framework.md` | 3 ekran kuralı, jüri eşik 7-9 kuralı |
| `5_Ana_Kategori_için_Derin_Analiz___Strateji_Raporu.md` | Akıllı Tedarik Zinciri kategorisi |
| `AHIKA_TR71_Master_Dokuman.md` | TR-71 Stratejik Öncelik 2 — Sanayi/Yeşil |

---

*Rapor Hazırlama Tarihi: 1 Mayıs 2026 — Kapadokya Hackathon 2026 başlangıcına kalan süre: 24 saatten az*
*Hazırlayan: Tuna & Team Feza için Master Teknik Referans*
*Versiyon: v1.0 — Sade kapsam (sadece pomza, başka uygulama yok)*
*Çerçeve onayı: Ahmet Abi'nin orijinal fikrine sadık iki modül + Avanos derin demo + B2B pomza üreticisi müşteri*
