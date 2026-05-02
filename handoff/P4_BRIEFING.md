# P4 — Spektral Mühendis Briefing

> **Hoş geldin.** Sen ASTER spektral indekslerini üretip P3'ün U-Net olasılığıyla **score-level füzyon** yapacaksın. **T4.12 v2'de critical path'e girdi** — saat 18-20 arasında `final_confidence.tif` üretmen P5 dashboard'un başarısı için kritik.

---

## 1. ROLÜN ÖZETİ

**Sen P4 — Spektral Mühendis'sin.** İki kritik teslimatın var:
1. **T4.5 — Ninomiya QI/SiO₂/CI üretimi** (saat 9) — `data/layers/aster_qi.tif`
2. **T4.12 — Score-level füzyon** (saat 20) — `data/layers/final_confidence.tif` (CRITICAL PATH)

**Füzyon formülü:**
```
final_confidence = P3_raw_prob × QI_norm × (1 - CI_norm)
```
- P3 RAW olasılık (saat 17.5'te `inference.py` ile gelir)
- QI normalize: percentile clip [2, 98] + min-max scale
- CI: yüksek karbonat = düşük pomza güveni

---

## 2. CRITICAL PATH SORUMLULUKLARIN

| Görev | Saat | CRITICAL? |
|---|---|---|
| **T4.12 Score-level füzyon canlı** | **18-20** | ✅ (v2 yeni) |

T4.12 saat 20'de bitmezse P5 dashboard'da `final_confidence.tif` ana katman olarak gösterilemez, demo kalitesi düşer.

---

## 3. HESAP KURULUMUN (saat 0, ~10 dk)

### 3.1 NASA Earthdata
- https://urs.earthdata.nasa.gov → "Register" → ücretsiz hesap
- Email confirm, profile complete
- **Uygulama yetkilendirmesi:** Profile → Applications → Authorize
  - "LP DAAC Data Pool" → Authorize
  - "ASTER L1T" → Authorize (eski API için)
- **Token oluştur:** Profile → Generate Token (60 gün geçerli)

### 3.2 .netrc dosyası

**Linux/Mac:**
```bash
echo "machine urs.earthdata.nasa.gov login YOUR_USERNAME password YOUR_PASSWORD" > ~/.netrc
chmod 600 ~/.netrc
```

**Windows (PowerShell):**
```powershell
@"
machine urs.earthdata.nasa.gov
login YOUR_USERNAME
password YOUR_PASSWORD
"@ | Out-File -FilePath $env:USERPROFILE\.netrc -Encoding ASCII
```

### 3.3 Yerel Python ortam
```bash
python -m venv venv
source venv/bin/activate
pip install -r code/p4/requirements.txt
```

`requirements.txt`: `rasterio, gdal, numpy, scipy, requests, beautifulsoup4`

### 3.4 GDAL kurulum (Windows için ekstra dikkat)
- Conda kullan: `conda install -c conda-forge gdal=3.7`
- VEYA OSGeo4W installer (https://trac.osgeo.org/osgeo4w/)
- `gdalwarp --version` çalışıyor olmalı

---

## 4. KENDİ LLM'İNİ KUR (saat 0, ~10 dk)

```bash
cd Pomzadoya
claude --model claude-opus-4-7
```

**İlk mesaj:**

```
Sen .claude/agents/p4-spektral-muhendis.md tanımındaki P4 — Spektral Mühendis rolündesin.
Tek doğru kaynağın: Modul_A_Critical_Path_Dependency_v2.md.

ŞİMDİKİ DURUM:
- Saat 0/24
- Ben P4 sorumlusu ekip üyesiyim
- handoff/P4_BRIEFING.md okudum
- NASA Earthdata hesap + .netrc hazır
- Yerel Python venv hazır, GDAL kurulu

KRİTİK HATIRLATMA:
- T4.12 score-level füzyon v2'de critical path'te (saat 18-20)
- Füzyon formülü: final_confidence = raw_prob × QI_norm × (1-CI_norm)
- Ninomiya QI = B11²/(B10×B12) (Karar #4 oran-tabanlı, L1T fallback OK)
- 20m S2 SWIR native grid (Karar #15) — bilinear resample, nearest YASAK

YAPACAKLARIN:
1. agent_outputs/p4_status.md ve .claude/state/orchestrator_log.md oku
2. code/p4/fuse_confidence.py'yi gözden geçir, API kontratını P3'ün predict_raw() ile uyumlu olduğunu doğrula
3. agent_outputs/p4_t4_1_runblock.md ile başla (Earthdata setup)
4. T4.2 ASTER indirme uzun (~30dk asenkron) — bu sırada T4.4 S2 indeksleri kodunu test edelim
5. T4.12 RUN-BLOCK'unu erken hazırla, saat 18'de yapıştır-koştur olsun

T4.1'den başla.
```

---

## 5. SAATLİK GÖREV TABLOSU

| Saat | Görev | Tür | Süre |
|---|---|---|---|
| 0:00-0:10 | Hesap kurulum (Earthdata + .netrc) | 👤 | 10dk |
| 0:10-0:30 | LLM kurulumu | 👤 | 20dk |
| **0:30-1:30** | **T4.1 Earthdata setup test (`code/p4/01_earthdata_setup.md`)** | 👤 | 1h |
| **1:30-3:00** | **T4.2 ASTER L1B indir (`02_aster_l1b_download.py`)** | 👤 curl + ⚙️ asenkron 30dk | 1.5h |
| **3:00-5:00** | **T4.3 Atmosferik düzeltme DOS1 (`03_aster_l1b_to_l2.py`)** | ⚙️ | 2h |
| **5:00-7:00** | **T4.4 S2 türetilmiş indeksler (`04_s2_indices.py`)** | ⚙️ | 2h |
| **7:00-9:00** | **T4.5 Ninomiya QI/SiO₂/CI (`05_ninomiya_qi.py`)** | ⚙️ | 2h |
| 9:00-10:00 | T4.6 90m→20m bilinear resample (`06_resample_to_s2_grid.py`) | ⚙️ | 1h |
| 10:00-12:00 | T4.7 Füzyon prototipi sentetik P3 output ile (`07_fusion_prototype.py`) | ⚙️ | 2h |
| 12:00-13:00 | T4.8 DEM aspect/hillshade (`08_dem_aspect_hillshade.py`) | ⚙️ | 1h |
| 13:00-15:00 | HELP→P5 Folium ASTER QI layer ekleme | 👥 P5 | 2h |
| 15:00-17:00 | T4.10 Layer GeoTIFF export + manifest dokümantasyon (`09_layer_export.py`) | ⚙️ | 2h |
| 17:00-18:00 | HELP→P3 fuse_confidence API alignment | 👥 P3 | 1h |
| **18:00-20:00** | **🔴 T4.12 Score-level füzyon canlı (CRITICAL)** | ⚙️ + 👥 | 2h |
| 18:00-20:00 | Entegrasyon | 👥 | 2h |
| 20:00 | **KOD FREEZE** | 🛑 | — |
| 20:00-24:00 | T4.13 KOD FREEZE + dry-run desteği | ⚙️ + 👥 | 4h |

---

## 6. T4.5 NINOMIYA QI — TEMEL FORMÜLLER

```python
# Quartz Index (Ninomiya 2003)
QI = (B11**2) / (B10 * B12)

# Carbonate Index (Ninomiya 1995)
CI = B13 / B14

# SiO2 estimator (Ninomiya 2003 lineer)
SiO2_pct = 56.20 + 271.09 * np.log10(QI) - ...  # tam formül 05_ninomiya_qi.py'da

# QI sanity:
# - Pomza/silikalı kayalar: QI > 1.2 (B11 yüksek, B10/B12 düşük)
# - Karbonatlar: QI < 1.0 + CI > 1.05
# - Vejetasyon: QI ~ 1.0 (düz spektrum)
```

`code/p4/05_ninomiya_qi.py` zaten bu formülleri içeriyor — sen test edip çalıştıracaksın.

---

## 7. T4.12 SCORE-LEVEL FÜZYON — KRİTİK API (saat 18-20)

### Önkoşul (saat 18'de)
- ✅ `code/p3/07_inference.py::predict_raw()` (P3 saat 17.5)
- ✅ `data/ard/full_ard_20m.tif` (P1 saat 8)
- ✅ `data/layers/aster_qi.tif`, `aster_ci.tif` (sen, saat 10)

### `fuse_confidence.py` API

```python
def fuse_confidence(
    raw_prob: np.ndarray,             # P3 predict_raw() çıktısı, [0, 1]
    qi: np.ndarray,                   # ASTER Quartz Index raster
    ci: np.ndarray,                   # ASTER Carbonate Index raster
    qi_percentile: tuple = (2, 98),   # normalize için percentile clip
    ci_percentile: tuple = (2, 98),
    qi_weight: float = 1.0,           # ablation için weight
    ci_weight: float = 1.0,
) -> np.ndarray:
    """
    Score-level füzyon:
        final_confidence = raw_prob × QI_norm^qi_weight × (1 - CI_norm)^ci_weight

    QI_norm: percentile_minmax_norm(QI)
    CI_norm: percentile_minmax_norm(CI) — yüksek karbonat = düşük pomza
    """
    qi_norm = percentile_minmax_norm(qi, *qi_percentile)
    ci_norm = percentile_minmax_norm(ci, *ci_percentile)
    return raw_prob * (qi_norm ** qi_weight) * ((1 - ci_norm) ** ci_weight)


def percentile_minmax_norm(
    arr: np.ndarray,
    lo: float = 2,
    hi: float = 98
) -> np.ndarray:
    """Percentile clip + min-max scale to [0, 1]."""
    p_lo, p_hi = np.percentile(arr, [lo, hi])
    arr = np.clip(arr, p_lo, p_hi)
    return (arr - p_lo) / (p_hi - p_lo + 1e-9)
```

### T4.12 RUN-BLOCK akışı (saat 18-20)

1. P3'ten `inference.py` import et
2. `data/ard/full_ard_20m.tif` üzerinde `predict_raw()` koştur → sliding window cosine-blend ile `data/raw_prob.tif`
3. `data/layers/aster_qi.tif`, `aster_ci.tif` aç (rasterio)
4. Hizalama kontrolü: aynı CRS, aynı transform, aynı shape
5. `fuse_confidence(raw_prob, qi, ci)` çağır
6. `data/layers/final_confidence.tif` olarak yaz (COG, EPSG:32636, 20m, NoData -9999)
7. Sanity:
   - Final confidence min=0, max=1
   - Pomza saha pikselleri (P2 etiketli) ortalama > 0.4
   - Karbonatlı bölgeler ortalama < 0.2
   - Vejetasyon ortalama < 0.1

---

## 8. KIM SANA NE TESLİM EDİYOR / SEN KİME NE TESLİM EDİYORSUN

### Sana gelen
| Saat | Girdi | Sağlayıcı | Kullanım |
|---|---|---|---|
| 4 | `data/ard/s2_ard_20m.tif` | P1 | T4.4 türetilmiş indeksler |
| 8 | `data/dem.tif`, `data/slope.tif` | P1 | T4.8 aspect/hillshade |
| 11 | `data/manifest.json` | P1 | Bant referansı |
| **17.5** | **`code/p3/07_inference.py::predict_raw()`** | **P3** | **T4.12 füzyon (CRITICAL)** |

### Senden çıkan
| Saat | Çıktı | Tüketici | Kullanım |
|---|---|---|---|
| 9 | `data/layers/aster_qi.tif` | P3 | Score-level füzyon prototip (T4.7'de) |
| 17 | `data/layers/aster_*.tif`, `s2_*.tif`, `dem_*.tif` | P5 | T5.9 Folium harita layer ekleme |
| 18 | `code/p4/fuse_confidence.py` API | P3 | Saat 17-18 alignment |
| **20** | **`data/layers/final_confidence.tif` (FUSED, CRITICAL)** | **P5** | **T5.13 dashboard ana katman** |

---

## 9. PLAN B'LERİN

| Tetikleyici | Plan B | Onay |
|---|---|---|
| **T4.3 ASTER L2 başarısız** | **L1T radiance ile devam (Karar #4)** — `--no-dos` flag ile çalıştır, QI oran-tabanlı olduğu için sonuç hala valid | Otomatik |
| ASTER indirilemedi (Earthdata down) | **JPL ASTER Volcano Archive** alternatif (çoğu sahne aynı) VEYA önceden indirilmiş `data/aster_cache/` | Grup chat |
| T4.6 90m→20m resample yavaş (büyük raster) | Önce AOI clip, sonra resample (boyut 5x küçülür) | Otomatik |
| **T4.12 saat 20'de bitmedi** | **P5 dashboard RAW + ASTER ayrı katman, FUSED demoda yok** — P5 ile koordineli | Eskalasyon |
| Hizalama (alignment) bozuk (CRS/transform farkı) | gdalwarp ile hedef raster grid'e hizala (`-tap` flag) | Otomatik |

---

## 10. T4.7 FÜZYON PROTOTİPİ (saat 10-12) — neden önemli

P3 saat 17.5'te `predict_raw()` teslim eder. Sen saat 10-12'de **sentetik raw_prob** ile fuse_confidence test edersin:

1. `code/p4/07_fusion_prototype.py` zaten yazıldı
2. Sentetik raw_prob: random Gaussian + spatial smooth (görsel olarak gerçeğe yakın)
3. QI ve CI gerçek (saat 10'da hazır)
4. Çıktı görsel kontrol: pomza sahaları yüksek confidence, karbonat düşük

Bu sayede saat 18'de gerçek raw_prob geldiğinde **sadece 1 satır değişikliği** ile T4.12 koşar.

---

## 11. KIM YAPAR, KIM RUN BUTONU TETIKLER

### Senin elinin değdiği fiziksel işler
- saat 0: Earthdata kayıt + .netrc
- saat 1: ASTER curl indir komutu (terminal)
- saat 18: T4.12 RUN-BLOCK Python script'ini koştur

### LLM'in ürettiği, senin koşturduğun otomasyonlar
- T4.3 atmosferik düzeltme (yerel Python)
- T4.4-T4.8 tüm spektral hesaplamalar
- T4.10 layer export
- T4.12 fuse_confidence

---

## 12. GITHUB WORKFLOW

```bash
git checkout -b p4-t4.x-<kısa-ad>

# layer GeoTIFF'leri Git LFS:
git lfs track "data/layers/*.tif"

git add code/p4/* agent_outputs/p4_*
git add data/layers/aster_qi.tif data/layers/final_confidence.tif

git commit -m "[P4] T4.12 Score-level füzyon (raw × QI × (1-CI))

DELIVER: data/layers/final_confidence.tif
Sanity: pomza mean conf 0.62, karbonat mean 0.08, vej mean 0.04
Bağımlı: P5 T5.13 dashboard ana katman (saat 18-20)"

git push origin p4-t4.x-<kısa-ad>
```

---

## 13. KENDİNİ KONTROL — saat 9, 17, 20'de

### Saat 9 ✓
- [ ] `data/layers/aster_qi.tif` exists, 20m grid, EPSG:32636
- [ ] QI değerleri makul: pomza saha mean > 1.2 (P2 polygon ile cross-check)
- [ ] `aster_ci.tif`, `aster_sio2.tif` de hazır

### Saat 17 ✓
- [ ] `data/layers/` 9 dosya: aster_*, s2_*, dem_* hepsi 20m EPSG:32636
- [ ] `reports/layer_docs.md` her layer için açıklama
- [ ] P5'e teslim mesajı

### Saat 18 ✓ HELP→P3 alignment
- [ ] `fuse_confidence(raw_prob, qi, ci)` API P3'ün predict_raw() ile uyumlu
- [ ] Test tile: P3'ten gerçek raw_prob al, P4 fuse_confidence çağır, sanity OK

### Saat 20 ✓ **CRITICAL**
- [ ] `data/layers/final_confidence.tif` exists
- [ ] Sanity threshold geçti
- [ ] P5'e DELIVER mesajı

---

## 14. DOSYA REFERANSLARIN

| Ne | Nerede |
|---|---|
| Rol tanımı | `.claude/agents/p4-spektral-muhendis.md` |
| Görev detay | `Modul_A_Critical_Path_Dependency_v2.md` § P4 |
| Kodlar | `code/p4/` (11 dosya hazır) |
| **Füzyon API** | **`code/p4/fuse_confidence.py` (T4.12 KRİTİK)** |
| RUN-BLOCK'lar | `agent_outputs/p4_t4_*_runblock.md` |
| **T4.12 RUN-BLOCK** | **`agent_outputs/p4_t4_12_runblock.md` (kritik)** |
| Statü | `agent_outputs/p4_status.md` |

---

## 15. SIK SORULAR

**S: ASTER L1B vs L1T vs L2 farkı?**
C: L1B = ham radyans (atmosfer düzeltmesiz), L1T = terrain-corrected radyans, L2 = atmosfer düzeltilmiş yansıma. Karar #4: QI oran-tabanlı, L1T yeterli (atmosfer düzeltme zorunlu değil). Plan B: T4.3 başarısızsa L1T ile devam.

**S: Ninomiya QI neden B11²/(B10×B12)?**
C: B10-B12 SWIR bantları, kuvars rezonans absorpsiyon noktasında. B11 (8.65 μm) yüksek = silika çok. B10×B12 baseline. Oran formu atmosferik etkiyi minimize eder (Karar #4 dayanağı).

**S: 20m grid neden, ASTER 90m değil mi?**
C: P3 fine-tune 20m S2 native grid kullanıyor (Karar #15). ASTER 90m'i 20m'e bilinear upsample → spektral bilgi korunur ama resolution artar. Bu trade-off kabul edildi (akademik dayanağı: Hewson 2005).

**S: fuse_confidence formülünde neden çarpım, neden toplama değil?**
C: Çarpım Bayesian conditional probability mantığında. Her faktör independent likelihood, çarpım posterior. Toplama olsaydı "düşük QI bile yüksek prob varsa kabul" olurdu — istemediğimiz şey.

**S: percentile_minmax_norm neden 2-98, 0-100 değil?**
C: Outlier'a karşı robust. Aşırı yüksek/düşük QI değerleri (genelde NoData veya artifact) min-max'ı bozuyor. 2-98 percentile clip outlier etkisini kaldırır.

---

## 16. SENİN BAŞARI KRİTERLERİN

1. ✅ T4.5 saat 9'da `aster_qi.tif` hazır, sanity OK
2. ✅ T4.7 saat 12'de prototip füzyon sentetik raw_prob ile çalışıyor
3. ✅ T4.10 saat 17'de tüm layer'lar P5'e teslim
4. ✅ T4.12 saat 20'de `final_confidence.tif` hazır (CRITICAL)
5. ✅ Plan B'ye gerek kalmadı

---

## 17. STRATEJİ TÜYÜLERİ

- **ASTER indirmeyi saat 0'da başlat** — 30dk asenkron, paralel başka iş yap
- **Pre-download:** Avanos'a yakın ASTER sahnelerini hackathon öncesi indirmeyi düşün (yedek)
- **GDAL/rasterio paralelizm:** Büyük raster'larda `windowed read` kullan (memory verimli)
- **Color ramp önerisi (P5 için):** QI için Spectral diverging (kırmızı=yüksek silika), CI için sequential blue, final_confidence için Magma (siyah-mor-sarı-beyaz)

---

**Saat 0 başladı sayılır. İlk eylemin: 3.1 NASA Earthdata kayıt + .netrc. Bittiğinde grup chat'e "P4 hazır" yaz.**
