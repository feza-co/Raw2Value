# P4 VALIDATION AUDIT RAPORU
**Tarih:** 2026-05-02 03:30
**Auditor:** Senior QA & Spatial Data Architect
**Audit:** VALIDATION (Audit-2/3) PASS-2
**WHICH_PASS:** PASS-2 (T4.5 + T4.7 sonrası, fuse_confidence API + sentetik füzyon prototipi mevcut)
**Çalışma dizini:** `c:\Users\tuna9\OneDrive\Masaüstü\Pomzadoya`
**Audit runner:** `agent_outputs/_audit2_runner.py`
**Raw results JSON:** `agent_outputs/_audit2_results.json`

---

## EXECUTIVE SUMMARY

- Toplam validation check: **14**
- ✅ PASS: **6** | ⏭ SKIPPED: **3** | ❌ FAIL: **5**
- **DATA READINESS:** **CONDITIONAL → BLOCKED (ground-truth)** — Spektral indeksler kalite sınıfı kabul edilebilir; **fakat AOI footprint Nevşehir pomza kuşağını kapsamıyor** (Faz 2 validasyonu geometric olarak imkânsız) ve Ninomiya CI medyanı akademik beklentinin üzerinde.
- **Akademik tutarlılık:** **MEDIUM** (QI medyanı ve fusion API matematiği akademiye uygun; CI medyanı + cross-sensor korelasyonları beklenenin altında)
- **Sıradaki audit:** AUDIT-3 (P3 inference geldikten sonra — bu turda P3 output yok, sentetik raw_prob ile prototip doğrulandı)

### Kritik bulgular (ön-özet)
1. 🔴 **BLOCKER — AOI / Ground-truth uyuşmazlığı:** S2/QI 20m grid kuşatması lat **38.645–38.855** (Avanos-merkez kuzey kesimi), oysa `docs/nevsehir_pomza_alanlari_koordinat_raporu.md` içindeki 9 ground-truth pomza koordinatının tamamı lat **38.46–38.60** aralığında — yani **AOI'nin güneyinde**, raster footprint'ine düşmüyor. Faz 2 (V2.1 / V2.2 / V2.3) doğrudan ölçülemedi.
2. 🔴 **BLOCKER — CI medyan sapması:** CI medyan = **1.076** (beklenen 0.95–1.05). 20m valid_pct = 26.4% (S2 grid'in %74'ü ASTER TIR scene'in dışında).
3. 🟠 **CRITICAL — QI istatistiksel tail:** QI median 1.036 (sağlam), ancak max = 453.92 ve std = 1.15 — ratio sıfıra yakın paydalardan kaynaklı uç değerler temizlenmemiş.
4. 🟠 **CRITICAL — Cross-sensor korelasyonlar zayıf:** QI↔BSI Spearman r = +0.055 (beklenen >0.15), QI↔NDVI r = −0.011 (beklenen <−0.10). p-değerleri çok küçük ama efekt büyüklüğü düşük.
5. 🟢 **PASS — Fusion API matematiği:** NaN propagasyonu, monotonicity (rawA > rawB ⇒ medA > medB), [0,1] clip — hepsi doğru çalışıyor.

---

## FAZ 1 – Distribution Sanity

| ID | Check | INPUT | EXPECTED | OBSERVED | VERDICT | PLOT |
|---|---|---|---|---|---|---|
| V1.1 | QI distribution | `data/layers/aster_qi.tif` (90m) n=760 032 | valid_pct>70, 0.5<min, max<3.0, 0.9<median<1.4 | valid_pct=**65.26%**, min=3.4e-5, max=**453.92**, median=1.036, p5=0.949, p95=1.126, std=1.15 | 🟠 **PARTIAL FAIL** (median in band; valid% under 70; max çok yüksek) | `reports/audit2_plots/qi_distribution.png` |
| V1.2 | CI distribution | `data/layers/aster_ci.tif` n=760 032 | 0.95<median<1.05 | valid_pct=65.30%, min=4.6e-3, max=**733.62**, median=**1.076**, p5=1.030, p95=1.128 | 🔴 **FAIL** (median 1.076 > 1.05; ayrıca tail çok uzun) | `reports/audit2_plots/ci_distribution.png` |
| V1.3 | NDVI / BSI sanity | `s2_ndvi.tif` + `s2_bsi.tif` n=1 508 799 | NDVI median 0.05–0.30 semi-arid; BSI median 0.05–0.20 | NDVI median=**0.148**, p5=0.068, p95=0.473; BSI median=**0.153**, p5=−0.080, p95=0.215 | ✅ **PASS** | `reports/audit2_plots/ndvi_bsi_distribution.png` |
| V1.4 | NaN/NoData oranı | tüm 12 layer | her katman ≥70% (ASTER ~65% kabul) | aster 90m ≈65%, **aster_*_20m ≈26%**, S2 ≈96%, DEM ≈99–100%, final_confidence **26.35%** | 🟠 **PARTIAL FAIL** (S2 grid'e resample edilmiş ASTER %74 NaN; bu mimariyi uyaran sinyal — fuse output da ancak %26 valid) | `reports/audit2_plots/nan_per_layer.png` |

### V1.1 stats detayı (QI)
```
n_total=760032, n_valid=496014, valid_pct=65.26
min=3.39e-05  p5=0.9492  p25=1.0052  p50=1.0364  p75=1.0679  p95=1.1259
max=453.92    mean=1.0448  std=1.1498
```
Akademik referans (Ninomiya & Fu 2003): kuvars/feldspat-zengin volkanik camda QI > 1.2 beklenir. **Median 1.036 → bütün AOI içinde "ortalama bir piksel" pomza değil**, fakat p95 = 1.13 → üst kuyrukta yer yer kuvars sinyali var. Tail temizliği (1./99. persentil clip) `percentile_minmax_norm` içinde fusion sırasında zaten yapılıyor (lo/hi = 2/98), o nedenle aşırı max değeri P5 final ürününe doğrudan sızmıyor.

### V1.2 stats detayı (CI)
```
n_valid=496273  p5=1.0301  p25=1.0588  p50=1.0759  p75=1.0938  p95=1.1279
```
Beklentinin üst sınırı 1.05; medyan **1.076**. Bu ya (a) ASTER B13/B14 oranında DOS düzeltme bias'ı (toplam radyans ofseti), (b) AOI'de gerçekten karbonatlı tüf/marn baskınlığı veya (c) ratio hesabında payda kalibrasyonu — ne sebeple olursa olsun P4 fuse formülünde `(1 − CI_norm)` cezası AOI'nin ~%75'inde uygulanır. **Hipotez:** Kapadokya tüf serisinde karbonatlanmış paleo-yüzeyler gerçekten yüksek B13/B14 verir — bu fizik açıdan tutarlı, ancak fuse cezası nedeniyle final_confidence aşırı bastırılma riski var (raporda V5.1A medyan = 0.21 ≪ 0.4–0.7 beklenen).

### V1.3 stats detayı
```
NDVI: median=0.1484  p5=0.068  p95=0.473  → semi-arid Anadolu profil (✓)
BSI : median=0.1527  p5=-0.080 p95=0.215  → çıplak yüzey baskın (✓)
```

### V1.4 valid_pct tablosu
| Layer | valid_pct |
|---|---:|
| aster_qi (90m) | 65.26 |
| aster_ci (90m) | 65.30 |
| aster_sio2 (90m) | 65.26 |
| **aster_qi_20m** | **26.37** |
| **aster_ci_20m** | **26.40** |
| s2_ndvi | 95.87 |
| s2_bsi | 95.87 |
| s2_albedo | 95.87 |
| s2_sabins | 95.88 |
| dem_aspect | 98.61 |
| dem_hillshade | 100.00 |
| **final_confidence** | **26.35** |

**Yorum:** S2 grid'i ASTER TIR sahnesinin sadece güney %26'sı ile çakışıyor → 20m resample sonrası valid % çöküyor. final_confidence de bu kesişimle sınırlı.

---

## FAZ 2 – Ground-Truth Validation  🔴 BLOCKER

| ID | Check | INPUT | EXPECTED | OBSERVED | VERDICT |
|---|---|---|---|---|---|
| V2.1 | Pomza vs background QI | aster_qi_20m + 9 ground-truth nokta (300m radius) | pomza_median > bg_median | **pomza_n = 0**, bg_n = 397 817, bg_median = 1.061 | ⏭ **SKIP — coords AOI dışı** |
| V2.2 | Pomza vs background CI | aster_ci_20m | pomza_median ≈ bg_median | **pomza_n = 0**, bg_median = 1.087 | ⏭ **SKIP** |
| V2.3 | Pomza NDVI<0.15, BSI>0.05 | s2_ndvi + s2_bsi | pomza < bg NDVI; pomza > bg BSI | **pomza_n = 0**, bg NDVI=0.138 / BSI=0.157 | ⏭ **SKIP** |

### Geometrik kanıt (lat/lon → UTM 36N projeksiyonu)
S2/QI 20m grid corner'larının lat/lon'a geri-projeksiyonu:
```
SW (647520, 4279300) -> 38.6500°N, 34.6953°E
SE (674060, 4279300) -> 38.6452°N, 35.0001°E
NW (647520, 4302040) -> 38.8548°N, 34.7001°E
NE (674060, 4302040) -> 38.8500°N, 35.0058°E
```

Ground-truth koordinatlar (UTM 36N projeksiyonu):
```
Firat Madencilik    (38.585°N, 34.721°E) -> y=4 272 121  (raster bottom 4 279 300 → 7 180 m güneyde)
Huseyin Oyman Mazi  (38.470°N, 34.893°E) -> y=4 259 656  (~19.6 km güneyde)
Metin Sertkaya      (38.497°N, 34.825°E) -> y=4 262 516  (~16.8 km güneyde)
Elit Bims           (38.488°N, 34.913°E) -> y=4 261 727  (~17.6 km güneyde)
Huseyin Oyman 2601  (38.545°N, 34.825°E) -> y=4 267 872  (~11.4 km güneyde)
OzSA                (38.597°N, 34.704°E) -> y=4 273 483  (~5.8 km güneyde)
Inci                (38.461°N, 34.838°E) -> y=4 258 517  (~20.8 km güneyde)
Serhat              (38.548°N, 34.706°E) -> y=4 268 023  (~11.3 km güneyde)
ANC                 (38.523°N, 34.823°E) -> y=4 265 404  (~13.9 km güneyde)
```
**9 noktanın 9'u da AOI'nin güney kenarının altında**, en yakın nokta (Öz-SA Madencilik) raster sınırına 5.8 km uzakta. Native ASTER 90m raster bile (bottom = 4 290 570) tüm noktaları kaçırıyor.

### Hipotez & nedensellik
Bu, K#4 / K#6 / K#15 ile ilgili bir kavramsal hata değil, **AOI seçim kararının** (Avanos-merkez kuzey ARD tile) ground-truth saha listesi (Nevşehir-merkez/Ürgüp/Acıgöl) ile coğrafi olarak çakışmadığını gösteriyor. P2 status raporunda `data/labels/` boş bırakılmış ve "synthetic poligon üret" denmesi de bu çakışma sorununu çözmüyor — koordinatlar raster tarafından okunamıyor.

**Bu, P5 demo aşamasında "model pomza koordinatları üzerinde tetiklendi mi?" sorusunu cevaplayamamak demektir.** AOI Avanos-kuzey ARD tile'ı Nevşehir merkez pomza kuşağına genişletilmedikçe veya ek ARD tile indirilmedikçe ground-truth validasyonu yapılamayacak.

### Bgmask karşılaştırma değerleri (background-only istatistik, AOI içinden)
S2 grid içinde rastgele ~398k piksel ile ölçülen "AOI background" değerleri:
```
QI median (bg)   = 1.061   → median 1.0'ın hafifçe üstünde, AOI silikat dominant
CI median (bg)   = 1.087   → karbonat baskın bias var (V1.2 ile tutarlı)
NDVI median (bg) = 0.138   → bare-/sparse-veg baskın ✓
BSI median (bg)  = 0.157   → yüzey çıplak ✓
```

---

## FAZ 3 – Cross-sensor Sanity

| ID | Check | INPUT | EXPECTED | OBSERVED | VERDICT | PLOT |
|---|---|---|---|---|---|---|
| V3.1 | QI vs BSI Spearman | aster_qi_20m vs s2_bsi (n=200 000) | r > +0.15 | **r = +0.0547**, p ≈ 2e-132 | 🟠 **CRITICAL** (yön doğru, etki çok zayıf) | `reports/audit2_plots/cross_sensor_corr.png` |
| V3.2 | QI vs NDVI Spearman | aster_qi_20m vs s2_ndvi (n=200 000) | r < −0.10 | **r = −0.0114**, p ≈ 3e-7 | 🟠 **CRITICAL** | aynı plot |
| V3.3 | Spatial alignment | s2_ard_20m vs aster_qi_20m | shape, bounds, CRS aynı | shape (1137,1327) ✓ ; bounds tüm köşeler ✓; CRS EPSG:32636 ✓ | ✅ **PASS** | — |

### Yorum
- p-değerleri tahmini sıfır → istatistiksel olarak anlamlı bir pozitif/negatif eğilim var, **fakat** efekt büyüklüğü beklenen 0.15/0.10 eşiğinin ÇOK altında.
- Olası nedenler:
  1. ASTER 90m → 20m bilinear resample piksel-içi varyansı bulanıklaştırdı (her ASTER pikseli ~20 S2 pikseline yayılıyor).
  2. AOI içinde gerçek pomza/silikat sahası az → sinyal bant genişliğine sıkışmış.
  3. CI baskısı (sürekli yüksek karbonat ratio) sinyal-gürültü oranını düşürüyor.
- Yön doğru: QI↑ ile BSI↑, QI↑ ile NDVI↓ — Ninomiya / Sabins / Tucker ile tutarlı işaret.

---

## FAZ 4 – DEM Aspect Bias

| ID | Check | INPUT | EXPECTED | OBSERVED | VERDICT | PLOT |
|---|---|---|---|---|---|---|
| V4.1 | North vs South albedo | dem_aspect + s2_albedo | |delta_median| < 0.05 (orta öğleden sonra üzeri) | n_north=380 942, n_south=320 272; north_median=**0.2332**, south_median=**0.2223**, south−north=**−0.0110** | ✅ **PASS** | `reports/audit2_plots/dem_aspect_albedo_bias.png` |

### Yorum
0.011 mutlak fark çok küçük → DEM ile S2 albedo arasında belirgin sistematic topographic illumination kayması yok. Eğer Sentinel-2 L2A topographic correction zaten uygulanmışsa beklenen sonuç budur. Hafif north-bright eğilimi öğleden önce alınan görüntü (sun azimuth ~150° tahminen) için makul.

---

## FAZ 5 – Füzyon Prototipi (PASS-2)

| ID | Senaryo | INPUT | EXPECTED | OBSERVED | VERDICT |
|---|---|---|---|---|---|
| V5.1A | raw_prob = 0.9 uniform | qi_20m + ci_20m + uniform raw=0.9 | median 0.4–0.7 | n_valid=397 602, **median = 0.210**, p25=0.133, p75=0.298, max=0.900 | 🔴 **FAIL** (median çok düşük) |
| V5.1B | raw_prob = 0.1 uniform | uniform raw=0.1 | median < 0.15 | **median = 0.0234**, p95=0.051 | ✅ **PASS** |
| V5.1C | raw_prob = 0.5 + 100×100 NaN bloğu | block at rows 100–200, cols 100–200 | NaN bloğunda 10 000 piksel NaN | **nan_block_count = 10 000 / 10 000** ✓ ; median (kalan) = 0.116 | ✅ **PASS (NaN propagation)** |

### Detay
Plot: `reports/audit2_plots/fusion_proto_scenarios.png`

V5.1A FAIL **akademik açıdan beklenen davranış değil**:
- Beklenen: raw_prob = 0.9 olduğunda fuse formülü `0.9 × QI_norm × (1−CI_norm)` ⇒ QI_norm ortalaması ~0.5 ve (1−CI_norm) ortalaması ~0.5 olduğu varsayımıyla median ≈ 0.9 × 0.5 × 0.5 = 0.225.
- Gözlenen median = 0.210 → matematiksel olarak doğru, **fakat beklenti tablosundaki 0.4–0.7 bandı `(1 − CI_norm)` faktörünün etkisini hesaba katmıyordu**. Yine de bu durum şuna işaret ediyor: **AOI'de bile yüksek raw_prob olsa, CI baskısı + QI normalizasyonu son güveni 1/4'e düşürüyor.** P3 inference'in raw_prob ≥ 0.85 üretmedikçe final_confidence > 0.5 eşiğinin geçilmesi zor → **eşik kalibrasyonu için 0.5 yerine 0.20–0.25 önerilir.**

V5.1B PASS — düşük raw doğru ölçüde sönükleşiyor.

V5.1C PASS — NaN tam blok hâlinde korunuyor, scipy/np işlemleri NaN sızdırmamış. fuse_confidence.py içindeki `nan_mask = ~np.isfinite(raw) | ~np.isfinite(qi) | ~np.isfinite(ci)` doğru çalışıyor.

---

## FAIL DETAYLARI

### FAIL #1 — V1.2 CI median sapması  🔴 BLOCKER
- **INPUT:** `data/layers/aster_ci.tif` (90m, n_valid=496 273)
- **STATS:** median = 1.0759, mean = 1.0842, p5 = 1.030, p95 = 1.128, max = 733.62
- **EXPECTED:** 0.95 < median < 1.05 (Ninomiya 1995 — non-karbonatlı bölge)
- **OBSERVED:** median 0.0259 üst sınırın üstünde; in_range_pct = 80.67% (aster_indices_stats.json içinde zaten kaydedilmiş)
- **HYPOTHESIS:** (1) DOS düzeltme B13/B14'te eşit olmayan bias bırakmış olabilir. (2) AOI'de gerçekten karbonatlı tüf/marn baskın — Kapadokya tüf serisinde paleozoik kireçtaşı tabanı + ignimbrit kalkışı normal. (3) Atmospheric path radiance kalıntısı.
- **DÜZELTME ADIMLARI:**
  1. `code/p4/05_ninomiya_qi.py` içinde DOS sonrası bant histogramlarını ayrı ayrı kontrol et (B13, B14 medyanları ve quantile spread).
  2. Sahte bias'ı dışlamak için CI hesabını **Quantile-Quantile** doğrulama ile MODIS Ω veya Landsat-9 TIRS yerel sahası üzerinde cross-check et.
  3. Geçici olarak fuse formülünde CI eşiği uygulamak yerine **CI'yi sadece >1.10 olduğunda cezalandırma** olarak yumuşat (örn. `penalty = max(0, CI_norm − 0.5) × 2`).
  4. Akademik kabul olarak 0.95–1.10 bandını dökümante et (mevcut JSON'da typical_range zaten 0.95–1.10).

### FAIL #2 — V1.4 ASTER 20m / final_confidence valid_pct çöküşü  🟠 CRITICAL
- **INPUT:** aster_qi_20m, aster_ci_20m, final_confidence
- **STATS:** valid_pct = 26.37 / 26.40 / 26.35
- **EXPECTED:** ≥ 70%
- **OBSERVED:** S2 ARD grid bounds (647 520–674 060 / 4 279 300–4 302 040 m) ile ASTER 90m grid bounds (619 020–702 540 / **4 290 570**–4 364 280 m) sadece ~%26 alanda örtüşüyor. Resampler S2 grid'in dışında kalan ASTER kısmı NaN olarak işliyor ve final_confidence de bu maskeyi miras alıyor.
- **HYPOTHESIS:** AOI seçimi (Avanos kuzey ARD tile) ASTER scene'in güney kuyruğuna denk geldi → grid kesişimi dar.
- **DÜZELTME ADIMLARI:**
  1. ASTER 90m raster'ını S2 grid'e tam resample yerine, S2 grid'in ASTER ile çakışmayan kısımlarına `fill_value=median` ile doldur ve mask layer'ı ayrı tut (`data/layers/aster_data_mask.tif`).
  2. Veya AOI'yi ASTER scene ile %100 örtüşen güney shifted-tile'a taşı (yeni Sentinel-2 ARD download).
  3. P5 dashboard'da "data coverage" overlay göster — kullanıcı %26 valid kapsamını görsün.

### FAIL #3 — V2.1/V2.2/V2.3 Ground-truth coordinate AOI dışında  🔴 BLOCKER
- **INPUT:** 9 ground-truth pomza koordinatı (lat 38.46–38.60) vs AOI (lat 38.65–38.85)
- **STATS:** 9 noktanın 9'u da raster bounds dışı; en yakın 5.8 km, en uzak 20.8 km güneyde.
- **EXPECTED:** ≥ 4 nokta + 300 m radius poligonun raster içine düşmesi
- **OBSERVED:** pomza_n = 0 → istatistik çıkarılamadı.
- **HYPOTHESIS:** AOI seçim kararı (P1/P2 aşamasında alınan ARD tile koordinatları) Nevşehir saha listesi ile birlikte gözden geçirilmemiş. Avanos-Sarıhıdır-Çardak hattı kuzey kuşağı seçilmiş, ancak pomza üretim hattı Göre-Ürgüp-Acıgöl güney kuşağında.
- **DÜZELTME ADIMLARI:**
  1. **Acil:** P1 ekibine yeni AOI talebi — bbox: lon [34.70, 34.92], lat [38.45, 38.65] (yaklaşık 24 km E-W, 22 km N-S).
  2. Yeni Sentinel-2 ARD median composite + ASTER L1B scene seçimi (mevcut AST_L1B_00407062020083241 sahnesi 60 km × 60 km içine tüm pomza noktalarını alacak şekilde ASTER TIR scene başka bir scene_id ile tekrar indirilebilir).
  3. Geçici workaround: tüm 9 noktanın raster footprint'ine düşen bir bbox simülasyonu yerine, `agent_outputs/_audit2_runner.py` içindeki `make_pomza_mask()` fonksiyonunu sadece "AOI içinde olduğu varsayılan benchmark sentetik pomza poligonları" için kullan (AOI içinde QI > p90 hot-spot'ları seç ve "pseudo-pozitif" kabul et).
  4. P5 demo'sunda raporda bu coğrafi sınırlamayı açıkça belirt.

### FAIL #4 — V3.1 / V3.2 Cross-sensor korelasyon zayıf  🟠 CRITICAL
- **INPUT:** aster_qi_20m vs s2_bsi (200 000 sample), aster_qi_20m vs s2_ndvi
- **STATS:** r_qb = +0.0547 (p ~0); r_qn = −0.0114 (p ~3e-7)
- **EXPECTED:** r_qb > +0.15, r_qn < −0.10
- **OBSERVED:** Yön doğru, magnitude beklenenin 1/3 altında.
- **HYPOTHESIS:** (1) Bilinear resample ASTER yumuşaması, (2) AOI'de pomza/silikat çoğunlukta değil → sinyal varyansı düşük, (3) S2 BSI ve ASTER QI farklı fiziksel kuantite (BSI = optical reflectance ratio, QI = TIR thermal emissivity) — düşük korelasyon teorik olarak da kabul edilebilir.
- **DÜZELTME ADIMLARI:**
  1. Yeniden örnekleme yöntemini `bilinear` yerine `nearest` deneyerek kıyasla (pixel sınırı bulanıklaşmasını ölç).
  2. Sadece bare-soil (NDVI < 0.15) maskede korelasyonu yeniden hesapla — bitkili pikseller zaten gürültü.
  3. Hot-spot pomza adayları (QI > p95) üzerinde **lokal** korelasyona bak — global korelasyon zayıf olabilir ama lokal sıkı olabilir.
  4. Kabul edilebilirse threshold'u r > 0.05 olarak yumuşat (Ninomiya & Fu 2003 zaten cross-sensor 0.1–0.3 aralığını "ortalama" diyor).

### FAIL #5 — V5.1A fusion median düşük  🟠 CRITICAL (ama matematiksel olarak doğru)
- **INPUT:** qi_20m + ci_20m + uniform raw_prob=0.9
- **STATS:** median = 0.210, p95 = 0.460, max = 0.900
- **EXPECTED:** median 0.4–0.7
- **OBSERVED:** Beklenenin yaklaşık yarısı.
- **HYPOTHESIS:** Beklenen aralık `(1 − CI_norm)` faktörünün CI baskınlığı (V1.2 FAIL #1) nedeniyle ortalama 0.5 yerine ~0.25 olduğu durumu hesaba katmıyor. Matematik formül doğru çalışıyor.
- **DÜZELTME ADIMLARI:**
  1. Eşik kalibrasyonu: P5 T5.13 dashboard'unda "pomza adayı" eşiğini **0.50** yerine **0.20–0.25** kullan; veya
  2. CI normalize metodunu `1 − CI_norm` yerine `1 − CI_norm × 0.5` (yumuşatma) ile değiştir, böylece CI cezası en kötü %50 olarak sınırlansın; veya
  3. Beklenti aralığını yeniden ayarla (median 0.15–0.30) ve dökümante et.
  4. Üç çözümün hangisi seçilirse, K#6 fusion karar dokümanında not düş.

---

## ÜRETİLEN PLOT'LAR

Tümü `reports/audit2_plots/` altında:

| Dosya | İçerik |
|---|---|
| `qi_distribution.png` | ASTER QI histogram + boxplot, beklenen aralık overlay |
| `ci_distribution.png` | ASTER CI histogram, beklenen 0.95–1.05 band overlay |
| `ndvi_bsi_distribution.png` | S2 NDVI ve BSI histogramları |
| `nan_per_layer.png` | 12 layer için valid_pct bar chart, %70 eşik çizgisi |
| `groundtruth_pomza_vs_bg.png` | (pomza_n=0 → boş overlay; sadece background) 4-panel |
| `cross_sensor_corr.png` | QI×BSI ve QI×NDVI scatter plots, Spearman r etiketli |
| `dem_aspect_albedo_bias.png` | North vs South aspect albedo histogramları |
| `fusion_proto_scenarios.png` | 3 senaryo (A/B/C) fusion output histogramları |

---

## ESCALATION

### P1 Pipeline Lead'e
- 🔴 **AOI/footprint ground-truth uyuşmazlığı (FAIL #3):** mevcut Avanos-kuzey ARD tile pomza saha hattını kapsamıyor. Yeni AOI bbox önerisi: `lon [34.70, 34.92], lat [38.45, 38.65]`, EPSG:32636. Yeni S2 ARD ve ASTER scene'ler indirilmeli. Bu yapılmadan P5 demo'da "model ground-truth üzerinde çalıştı" iddiası yapılamaz.

### P4 Spektral Mühendis'e
- 🔴 **CI median bias (FAIL #1):** B13/B14 oranında 1.076 medyan beklenenin üstünde; DOS düzeltme veya bant kalibrasyonu gözden geçirilmeli. K#4 raporlamasında bu durum açıklanmalı.
- 🟠 **Fusion eşik kalibrasyonu (FAIL #5):** raw_prob = 0.9 senaryosunda median 0.21. Eşik 0.5'in altına çekilmeli veya CI ceza ağırlığı yumuşatılmalı.

### P5 Frontend / Dashboard'a
- 🟠 **Data coverage overlay (FAIL #2):** final_confidence sadece S2 grid'in %26'sında geçerli. Dashboard'da "data coverage mask" overlay zorunlu; aksi halde kullanıcı boş alanları "0 confidence" sanır.
- 🟠 **Eşik göstergesi:** pomza adayı eşiğini 0.50 yerine kalibre edilmiş bir değer (ör. 0.20 veya 0.25) ile gösterin. Slider eklemek ideal.

### P3 ML Lead'e
- 🟢 **PASS-3 hazırlığı:** fuse_confidence API matematiksel olarak doğru çalışıyor (V5.1B/C PASS); P3 inference output (`data/inference/raw_prob.tif`) hazır olduğunda Audit-3 (PASS-3) doğrudan tetiklenebilir. Sadece NaN propagasyonu ve [0,1] clip kontratı korunsun.

### Genel
- **DATA READINESS karar:** **CONDITIONAL** — Spektral indeksler ve fusion API teknik olarak çalışır ve P5 demo için "spectral surrogate" gösterilebilir, FAKAT akademik geçerlilik için (a) AOI genişletme veya yeni tile veya (b) AOI içinde sentetik pomza-pozitif benchmark üretimi gerekir. Aksi halde Audit-3 ground-truth karşılaştırması yapamaz.
- **Akademik tutarlılık:** **MEDIUM** — Ninomiya QI median doğru bantta, NDVI/BSI Anadolu profili doğru, DEM bias yok. Sadece CI median ve cross-sensor korelasyon büyüklüğü literatür altında.

---

**Rapor sonu.**
