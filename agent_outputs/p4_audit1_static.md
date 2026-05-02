# P4 STATIC AUDIT RAPORU

**Tarih:** 2026-05-02 03:30
**Auditor:** Senior QA & Spatial Data Architect
**Audit:** STATIC + STRUCTURAL (Audit-1/3)
**Repo state:** `56f2508` (branch P4/goktug, working tree clean)
**Çalışma dizini:** `c:\Users\tuna9\OneDrive\Masaüstü\Pomzadoya`

---

## EXECUTIVE SUMMARY

- **Toplam check:** 33
- ✅ **PASS:** 27 | ⏭ **SKIPPED:** 0 | ❌ **FAIL:** 6
- **Severity dağılımı:** 🔴 0 / 🟠 1 / 🟡 4 / 🟢 1
- **STATIC READINESS:** **CONDITIONAL** — Yapısal/akademik bütünlük READY, ancak dokümantasyon ve reproducibility hijyen sorunları (BLOCKER yok). Kritik patika kodu canlıya hazır.
- **Sıradaki audit:** **AUDIT-2 (Distribution Validation)** — Layer dağılım, histogram bimodality, pomza/karbonat etiket cross-check.

**Kritik gözlem:** `fuse_confidence` API + CLI 5/5 sanity testi PASS. Spatial alignment (S2 ARD ↔ aster_qi_20m ↔ final_confidence.tif) bit-perfect (aynı bounds, transform, shape, CRS). Karar #6 (no binarization), Karar #15 (bilinear-only), Karar #4 (oran-tabanlı QI), Karar #13 (Liang katsayıları aynen) kodda doğrulandı.

---

## FAZ 1 — Dosya envanteri & protokol uyumu

| ID | Check | Status | Severity | Evidence (LOC + 1 satır) |
|---|---|---|---|---|
| 1.1 | code/p4/ envanter — 11 ana dosya beyanı | ❌ FAIL | 🟢 MINOR | `code/p4/` içinde 14 .py + 1 .md + 1 .txt = 16 dosya. Status'ta "11 expected" — 3 helper (`_geo_aster_tir.py`, `_fetch_copernicus_dem.py`, `cmr_query_l1b.py`, `aster_download.py`, `cmr_query_l1t.py` yok) "11 file" beyanıyla uyumsuz. |
| 1.2 | RUN-BLOCK dosyaları (T4.1, T4.2, T4.3, T4.12 minimum) | ✅ PASS | — | `agent_outputs/p4_t4_{1,2,3,12}_runblock.md` mevcut, hepsi 3-blok protokol içeriyor. |
| 1.3 | RUN/VERIFY/DELIVER format uyumu | ✅ PASS | — | `p4_t4_12_runblock.md:1-117` — `# RUN-BLOCK`, `## VERIFY-BLOCK`, `## DELIVER` üçlüsü mevcut, ID etiketi tutarlı. |
| 1.4 | requirements.txt lock seviyesi (`==` pin) | ❌ FAIL | 🟡 MAJOR | `code/p4/requirements.txt:6-21` tüm satırlar `>=` (örn `rasterio>=1.3.9`, `numpy>=1.24`). Reproducibility tehlikesi: status'ta "numpy==1.26.4 pin" denmesine rağmen requirements.txt buna uymuyor. |

---

## FAZ 2 — Bağımlılık & girdi kontratı (P1→P4)

| ID | Check | Status | Severity | Evidence |
|---|---|---|---|---|
| 2.1 | S2 ARD bant=10, EPSG:32636, 20m | ✅ PASS | — | `data/ard/s2_ard_20m.tif` runtime: `count=10, crs=EPSG:32636, res=(20.0,20.0), shape=(1137,1327), dtype=float32, nodata=-9999.0` |
| 2.2 | Manifest B11=9, B12=10 | ✅ PASS | — | `data/manifest.json:14-15` `"B11": 9, "B12": 10` |
| 2.3 | Dinamik bant eşleştirme (manifest fallback) | ✅ PASS | — | `04_s2_indices.py:130-141` `if args.manifest: band_key = {k: int(v) for k, v in m.get("bands", BAND_KEY).items()}` + count safety check (raises if `src.count < max(band_key.values())`). |
| 2.4 | CRS birim metre, UTM 36N | ✅ PASS | — | runtime `crs.linear_units = 'metre'`, WKT `PROJECTION["Transverse_Mercator"], central_meridian=33` (UTM zone 36N matematik doğru). |
| 2.5 | NoData policy tutarlılığı | ❌ FAIL | 🟠 CRITICAL | **Karışık politika.** S2 ARD nodata=`-9999.0` (sentinel), P4 layer çıktıları nodata=`NaN` (`04_s2_indices.py:87`, `05_ninomiya_qi.py:97`, `fuse_confidence.py:164`). `read_band` (`04_s2_indices.py:104-106`) `arr == nodata` ile float karşılaştırma yapıyor — `-9999.0` strict eşitlik float'ta riskli (FP hata). DEM aspect nodata=`-9999.0`, hillshade=`0`. Bu üç farklı sentinel + NaN karışımı sessiz veri sızıntısı riski yaratır. |

---

## FAZ 3 — Akademik & matematiksel doğruluk

| ID | Check | Status | Severity | Evidence |
|---|---|---|---|---|
| 3.1 | Sabins B11/B12 (Sabins 1999) | ✅ PASS | — | `04_s2_indices.py:78` `return _safe_div(b11, b12)` + manifest doc `"S2 Sabins B11/B12 ... Sabins 1999"` (`09_layer_export.py:51-53`). Status notu: önceden `B11/B8` yanlıştı, düzeltilmiş. |
| 3.2 | Liang 2001 albedo katsayıları (0.356,0.130,0.373,0.085,0.072,−0.0018) | ✅ PASS | — | `04_s2_indices.py:67-74` `0.356 * b2 + 0.130 * b4 + 0.373 * b8 + 0.085 * b11 + 0.072 * b12 - 0.0018` — birebir doğru. |
| 3.3 | Ninomiya QI = B11²/(B10·B12) | ✅ PASS | — | `05_ninomiya_qi.py:57` `return _safe_div(b11 * b11, b10 * b12)` |
| 3.4 | Ninomiya CI = B13/B14 | ✅ PASS | — | `05_ninomiya_qi.py:62` `return _safe_div(b13, b14)` |
| 3.5 | _safe_div koruması | ✅ PASS | — | `05_ninomiya_qi.py:48-52` `mask = np.isfinite(num) & np.isfinite(den) & (den > 0)` — pozitif paydayı zorunlu kılar; `04_s2_indices.py:38-42` benzer (sadece `den != 0`). NDVI/BSI'da negatif payda olabilir, doğru. |
| 3.6 | SiO₂ estimator yorum uyarısı | ✅ PASS | — | `05_ninomiya_qi.py:26-29, 66` `"yorum amaçlı, karar girişi DEĞİL"` + `09_layer_export.py:74-76` `"Yorum amaçlı — karar girişi DEĞİL"`. |
| 3.7 | NDVI ve BSI formülleri | ✅ PASS | — | `04_s2_indices.py:46` `_safe_div(b8 - b4, b8 + b4)` (Tucker 1979); `:50-52` BSI = `((B11+B4)-(B8+B2))/((B11+B4)+(B8+B2))` (Rikimaru 2002). |
| 3.8 | Plan B `--no-dos` flag | ✅ PASS | — | `03_aster_l1b_to_l2.py:139-143` argparse `--no-dos` mevcut, `correct_band(...)` no_dos=True'da `return arr, 0.0`. Hata path'inde "[hint] retry with --no-dos" mesajı (`:169, :187`). |

---

## FAZ 4 — Spatial integrity

| ID | Check | Status | Severity | Evidence |
|---|---|---|---|---|
| 4.1 | Resample = bilinear (Karar #15, nearest YASAK) | ✅ PASS | — | `06_resample_to_s2_grid.py:71` `"-r", "bilinear"`; `:119` `resampling=Resampling.bilinear,  # NEAREST YASAK`. Repo tamamında `nearest` araması: sadece `06_*.py` içinde 2 yorumda "nearest YASAK" (kullanım YOK). |
| 4.2 | Hedef CRS = EPSG:32636 | ✅ PASS | — | `06_resample_to_s2_grid.py:63` `"-t_srs", "EPSG:32636"`; `:99` `dst_crs = "EPSG:32636"`. Runtime: `aster_qi_20m.tif crs=EPSG:32636`. |
| 4.3 | Hedef çözünürlük = 20m | ✅ PASS | — | `06_resample_to_s2_grid.py:137` `--res default=20.0`; `:64` `"-tr", str(res), str(res)`. Runtime: `res=(20.0, 20.0)`. |
| 4.4 | Reference grid alignment | ✅ PASS | — | Runtime check: `aster_qi_20m bounds == s2_ard_20m bounds == True`, transform identical, shape (1137,1327) eşleşiyor. |
| 4.5 | Output dtype float32 + deflate sıkıştırma | ✅ PASS | — | `fuse_confidence.py:163-170` `dtype="float32", compress="deflate", predictor=2, tiled=True`; tüm 04/05/06/07'de aynı profil. DEM hillshade istisna `uint8` (görsel altlık, doğru). |

---

## FAZ 5 — Output kontratı & T4.12 füzyon (KRİTİK)

| ID | Check | Status | Severity | Evidence |
|---|---|---|---|---|
| 5.1 | Binarization YASAĞI (Karar #6) | ✅ PASS | — | `fuse_confidence.py` içinde `> threshold`, `astype(bool)`, `binarize` aramaları boş döndü. Çıktı `np.clip(final, 0.0, 1.0).astype(np.float32)` (`:124`) — sürekli skor. |
| 5.2 | Percentile normalize (lo=2, hi=98, np.nanpercentile-eşdeğeri) | ✅ PASS | — | `fuse_confidence.py:52-56` `lo_pct=2.0, hi_pct=98.0`; `:68, 72-73` `valid = arr[np.isfinite(arr)]; np.percentile(valid, lo_pct/hi_pct)` — NaN-aware (manuel filter, np.nanpercentile yerine eşdeğer). |
| 5.3 | Füzyon formülü = `raw * qi_n * (1 - ci_n)` | ✅ PASS | — | `fuse_confidence.py:123` `final = raw_clip * qi_n * (1.0 - ci_n)` — formül birebir. |
| 5.4 | NaN propagation | ✅ PASS | — | `fuse_confidence.py:126-127` `nan_mask = ~np.isfinite(raw) | ~np.isfinite(qi_a) | ~np.isfinite(ci_a); final[nan_mask] = np.nan`. Runtime test 2: NaN giriş → NaN çıkış doğrulandı. |
| 5.5 | API kontratı (P3 ile) | ✅ PASS | — | `fuse_confidence.py:89-128` signature `fuse_confidence(raw_prob, qi, ci, *, qi_norm_kwargs, ci_norm_kwargs)`, briefing API ile uyumlu (kwarg-only opsiyonlar). Shape mismatch → SystemExit (Plan B path). |
| 5.6 | Logging | ❌ FAIL | 🟡 MAJOR | `fuse_confidence.py:188-219` `print(...)` ve stderr kullanılıyor; `logging` modülü yok. Reproducible audit log için yetersiz (timestamp, level, format yok). T4.12 kritik patika için pre-flight log standardı eksik. |
| 5.7 | T4.12 doc "expected" değerleri vs. gerçek davranış | ❌ FAIL | 🟡 MAJOR | `p4_t4_12_runblock.md:30` `"Beklenen: shape (100,100) min ~0 max ~0.7 mean ~0.35"` — runtime ölçüm: `min=0.0, max=0.175, mean=0.112` (TEST1). Doc P3 alignment kontratını yanlış yönlendirir; saat 17:30-18:00 HELP→P3 sırasında yanlış pozitif "FAIL" sinyali yaratabilir. |

---

## FAZ 6 — Reproducibility & Plan B

| ID | Check | Status | Severity | Evidence |
|---|---|---|---|---|
| 6.1 | Random seed | ✅ PASS | — | `07_fusion_prototype.py:37, 39` `seed: int = 42; rng = np.random.default_rng(seed)` — sentetik raw_prob deterministik. fuse_confidence'da random yok (gerek yok). |
| 6.2 | Manifest üretim komutu reproducible | ✅ PASS | — | `09_layer_export.py:124-138` `describe()` her layer için MD5 + size + CRS + bounds + dtype kayıt; `reports/layers.json` artık 12-layer. CLI: `--root --reports`. |
| 6.3 | Plan B dokümantasyonu | ❌ FAIL | 🟡 MAJOR | Plan B yolları **kısmi**: `--no-dos` mevcut (`03_*.py`), shape mismatch fallback raw_prob'a düşüyor (`fuse_confidence.py:194-197`), ama T4.12 RUN-BLOCK Plan B (`p4_t4_12_runblock.md:105-109`) "raw_prob.tif kopyala" demesine rağmen otomasyon scripti yok (manuel adım). T4.6 büyük raster AOI clip planı dokümante edilmemiş (`P4_BRIEFING.md:243`'te bahsediliyor ama kod yok). |
| 6.4 | Unit test mevcudiyeti | ❌ FAIL | 🟡 MAJOR | `code/p4/` içinde test_*.py / *_test.py / tests/ klasörü YOK. requirements.txt `pytest>=7.4` listeliyor (`:21`) ama test dosyası yok. Status'ta "5/5 in-memory sanity test PASS" inline koşturuluyor (otomasyon yok, regresyon koruması yok). |

---

## FAIL DETAYLARI

### FAIL #1 — 1.1 Dosya envanteri uyumsuzluğu [🟢 MINOR]
- **LOC:** `agent_outputs/p4_status.md:7-23`
- **QUOTE (observed):** `"Üretilen artefaktlar (kod) | # | Dosya | ... | 11 | requirements.txt"` (status 11 dosya beyanı)
- **EXPECTED:** code/p4/ gerçek içeriği 16 dosya (4 helper + 5 numbered + fuse_confidence + requirements + 01.md + 4 cmr/aster_download/_geo/_fetch helpers).
- **METHOD:** STATIC (dosya listesi karşılaştırma)
- **ETKİ:** Dokümantasyon yanıltıcı; auditor + new contributor "11 dosya" ararken helper'ları gözden kaçırabilir. Critical path etkisi yok.
- **DÜZELTME:**
  1. p4_status.md tablosunu 16 satıra genişlet, helper'ları ayrı bölüm olarak işaretle.
  2. veya `code/p4/__pycache__` ve helper kategorisini tabloda belirgin yap.

---

### FAIL #2 — 1.4 requirements.txt lock seviyesi [🟡 MAJOR]
- **LOC:** `code/p4/requirements.txt:6-21`
- **QUOTE (observed):** `rasterio>=1.3.9` ... `numpy>=1.24` ... `GDAL>=3.6`
- **EXPECTED:** `==` pin (Status: "numpy==1.26.4 pin" — numpy 2.x rasterio ABI uyumsuzluğu yaşandı; pin yokken regresyon riski yüksek).
- **METHOD:** STATIC (grep)
- **ETKİ:** Tekrar üretilebilir kurulumlar garanti değil. Demo gününde `pip install` `numpy 2.x` çekerse rasterio import patlar (status'ta zaten yaşanmış sorun).
- **DÜZELTME:**
  1. `pomza/Scripts/pip freeze | grep -E '^(rasterio|numpy|scipy|requests|matplotlib|tqdm|GDAL|beautifulsoup4|lxml|pytest)=='` ile pin değerleri al.
  2. `requirements.txt`'i tüm satırlar `==X.Y.Z` olacak şekilde güncelle.
  3. CI/dry-run komutunda `pip install -r code/p4/requirements.txt --no-deps` test et.

---

### FAIL #3 — 2.5 NoData policy tutarsızlığı [🟠 CRITICAL]
- **LOC:** `data/ard/s2_ard_20m.tif` (nodata=-9999.0) vs `code/p4/04_s2_indices.py:104-106, :87` vs `code/p4/08_dem_aspect_hillshade.py:97, :103`
- **QUOTE (observed):** `s2_indices write_cog: nodata=np.float32(np.nan)` // `read_band: arr = np.where(arr == nodata, np.nan, arr)` // `dem_aspect nodata=-9999.0` // `dem_hillshade nodata=0`
- **EXPECTED:** Tek tutarlı NoData politikası — okuma için strict eşitlikten kaçın (`np.isclose` veya bit-cast), yazımda tüm float32 layer'lar için tek sentinel (NaN VEYA -9999 ama karışık değil).
- **METHOD:** STATIC + META
- **ETKİ:** S2 ARD `-9999.0` float strict-eşitlik sorgusu IEEE-754 round-trip'te kaymalar üretebilir; etkilenen pikseller NaN'a kapanmaz, pomza/karbonat skoruna sızar. fuse_confidence NaN propagate ediyor ama NaN'a hiç düşmeyen pixel "valid" sayılıp yanlış skor üretir. DEM aspect=-9999, hillshade=0 karışımı: P5 Folium katmanı 0'ı geçerli aydınlık olarak gösterir.
- **DÜZELTME:**
  1. `read_band`'i `nodata` varsa `np.isclose(arr, nodata, atol=1e-3)` kullan.
  2. Tüm P4 layer çıktıları için tek sentinel: NaN (mevcut çoğunluk). DEM aspect/hillshade'i de NaN'a çevir veya ayrı maskeleme adımı ekle.
  3. `09_layer_export.py` manifest'e her layer için `nodata_strategy` alanı ekle (NaN | sentinel-9999 | uint8-0) — P5 dashboard render katmanı bilgilenir.

---

### FAIL #4 — 5.6 Logging eksikliği [🟡 MAJOR]
- **LOC:** `code/p4/fuse_confidence.py:188-219`
- **QUOTE (observed):** `print(f"[err] read failed: {e}", file=sys.stderr)` // `print(json.dumps(report, indent=2))`
- **EXPECTED:** `logging.getLogger(__name__)` + `logging.basicConfig(level=INFO, format='%(asctime)s %(levelname)s %(message)s')` — kritik patika için zaman damgalı, level'lı log.
- **METHOD:** STATIC
- **ETKİ:** Saat 18:00-20:00 T4.12 canlı koşumda hata olursa stdout/stderr karışık; root cause analizi gecikir. Demo sonrası post-mortem için zaman damgası yok.
- **DÜZELTME:**
  1. `import logging; log = logging.getLogger(__name__); logging.basicConfig(...)` ekle.
  2. Tüm `print(... file=sys.stderr)` → `log.error(...)`, status print'leri `log.info(...)`.
  3. `--log-file <path>` argparse opsiyonu ekle, default `reports/fuse_run_<ts>.log`.

---

### FAIL #5 — 5.7 T4.12 RUN-BLOCK doc beklenen değer hatası [🟡 MAJOR]
- **LOC:** `agent_outputs/p4_t4_12_runblock.md:30`
- **QUOTE (observed):** `"Beklenen: shape (100,100) min ~0 max ~0.7 mean ~0.35"`
- **EXPECTED:** Linear QI (0.5-2.5) + linear CI (0.95-1.10) ile gerçek formül `raw × qi_n × (1-ci_n)` çıktısı `min=0, max≈0.175, mean≈0.112` (auditor runtime ölçüm).
- **METHOD:** STATIC + runtime cross-check
- **ETKİ:** Saat 18:00 P3-P4 alignment kontrolünde gerçek ölçümler doc'tan saparken P3 takımı "API patladı" yanlış alarmı verir. Critical path zaman kaybı.
- **DÜZELTME:**
  1. `p4_t4_12_runblock.md:30` satırını `"Beklenen: min ~0, max ~0.18, mean ~0.11"` olarak güncelle.
  2. Beklenen değerlerin altına bir satır: `"(matematik: max(qi_n)=1, max(1-ci_n)=1, ama lineer dağılımda iki maksimum aynı pikselde değil → ürün max ~0.18)"`.

---

### FAIL #6 — 6.3 Plan B otomasyonu eksik [🟡 MAJOR]
- **LOC:** `agent_outputs/p4_t4_12_runblock.md:105-109` + `code/p4/fuse_confidence.py:194-197`
- **QUOTE (observed):** `"final_confidence.tif yerine data/inference/raw_prob.tif kopyala"` (manuel) // `print("[planB] writing raw_prob unchanged as fallback", file=sys.stderr)` (kod-içi sadece shape-mismatch case)
- **EXPECTED:** Plan B otomasyonu — `--planB` flag veya ayrı `code/p4/_fuse_planB.py` script saat 20:00'da `final_confidence.tif`'i raw_prob ile aynı bounds'ta + bayrak metadata (`tags={"planB": "true", "reason": "..."}`)' yazar.
- **METHOD:** STATIC + META
- **ETKİ:** Saat 20:00 T4.12 fail olursa P5 dashboard kırılır; manuel kopyalama insan hatasına açık. Demo backup yok.
- **DÜZELTME:**
  1. `fuse_confidence.py`'a `--planb-on-error` flag ekle: shape mismatch / IO hata → raw_prob'u final_confidence olarak yaz, tag `planB=true`.
  2. `09_layer_export.py` manifest'inde `planB` flag varsa P5'e "FUSED demo iptal" sinyali ekle.
  3. T4.6 AOI clip Plan B (briefing'de bahsedilen) için `06_resample_to_s2_grid.py`'a `--clip-bbox` opsiyonu ekle.

---

### FAIL #7 — 6.4 Unit test mevcut değil [🟡 MAJOR]
- **LOC:** `code/p4/` (test dosyası yok)
- **QUOTE (observed):** glob `test_*.py / *_test.py / tests/`: 0 sonuç. `requirements.txt:21` `pytest>=7.4`.
- **EXPECTED:** Asgari `tests/test_fuse_confidence.py` 5 senaryo (status'taki 5/5 in-memory sanity'i pytest'e dök).
- **METHOD:** STATIC
- **ETKİ:** Critical path API regresyon koruması yok. Yarın commit `fuse_confidence.py` formülünü değiştirirse sessiz veri korupsiyonu olur.
- **DÜZELTME:**
  1. `tests/p4/test_fuse_confidence.py` oluştur — 5 sanity testi (shape/range, NaN propagate, shape mismatch SystemExit, pomza vs vegetation contrast, CI penalty).
  2. `tests/p4/test_s2_indices.py` — Liang katsayıları + Sabins B11/B12 + NDVI symmetric test.
  3. CI/pre-commit'e `pytest tests/p4/` ekle.

---

## ESCALATION

- 🔴 **BLOCKER:** YOK. Critical path canlıya hazır.
- 🟠 **CRITICAL (1):** NoData policy karışıklığı — sessiz veri sızıntısı riski. **P4 sorumlusu (göktug) FAIL #3'ü Audit-2 öncesi düzeltmeli.**
- 🟡 **MAJOR (4):** requirements pin, T4.12 doc beklenen değer, Plan B otomasyon, unit test yokluğu — KOD FREEZE öncesi (saat 20) en az 2'sini kapatmak demo riskini düşürür.
- 🟢 **MINOR (1):** Status dosya envanteri sayım hatası.
- **≥3 🔴 yok** → mimari review gerekmez.
- Genel hüküm: **STATIC CONDITIONAL READY** — Audit-2'ye geçilebilir, FAIL #3 paralel olarak hotfix.

---

## SKIPPED CHECKLIST

Hiçbir check atlanmadı. Distribution validation (histogram bimodality, Otsu kontrol, Z-score outlier) ve live integration (P3 gerçek raw_prob, P5 Folium render) Audit-2/3 kapsamında.

---

## EK NOTLAR

- **Pozitif gözlemler:**
  - Spatial alignment runtime'da bit-perfect doğrulandı (bounds + transform + shape eş).
  - SiO₂ "yorum amaçlı, karar girişi DEĞİL" hem koddata (`05_ninomiya_qi.py:66`) hem manifest'te (`09_layer_export.py:76`) çift mühürlü — akademik dürüstlük güçlü.
  - Karar #15 bilinear-only kuralı `06_resample_to_s2_grid.py`'da `# NEAREST YASAK` yorumu + `Resampling.bilinear` ile çift garantili. Repoda hiç `Resampling.nearest` yok.
  - `_safe_div` her iki modülde de NaN-aware ve sıfır-payda korumalı.
  - Reference grid alignment için `--reference` flag, `get_target_extent` (P1 ARD bounds'tan otomatik) — kod hardcode değil.

- **Audit-2 için flag'lenenler:**
  - `aster_*_20m.tif` valid_pct=%26.4 (status'tan): ASTER coverage %74 NaN. Distribution audit'inde QI mean=1.04 hesabı sadece valid pixels üzerinde — pomza saha cross-check (P2 polygon) Audit-2'de gerekiyor.
  - Final confidence max=0.0498 (`fuse_report.json:5`) — pomza adayları için maksimum %5 güven, eşik 0.5 unrealistic. Bu "sentetik raw_prob" çıktısı; gerçek P3 raw_prob geldiğinde Audit-3'te tekrar değerlendirilecek.

---

*Rapor sonu — Audit-1/3 STATIC + STRUCTURAL kapsamı tamamlandı.*
