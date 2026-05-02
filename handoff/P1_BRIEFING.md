# P1 — Veri Mühendisi Briefing

> **Hoş geldin.** Bu doküman senin 24 saat boyunca yapacağın her şeyi içerir. Ayrıca bir yere bakma — burada her şey var. İlk 30 dk hesap kurulumu, kalan 23.5 saat planlı iş.

---

## 1. ROLÜN ÖZETİ

**Sen P1 — Veri Mühendisi'sin.** Modül A critical path'inin **başısın**. Senin gecikmen tüm projeyi geciktirir. Senin ürettiğin **17-kanallı, 20m grid Full ARD** olmadan P3 fine-tune yapamaz, P4 indeks üretemez, P5 dashboard'a katman ekleyemez.

**Birincil çıktın:** `data/ard/full_ard_20m.tif` — 17 kanal (S2: 10 bant + S1: VV+VH + DEM: yükseklik+slope + türev: NDVI/BSI/Albedo), 20m grid (Karar #15 SWIR native), EPSG:32636 (UTM 36N), co-registered, AOI içine clip'lenmiş, NoData oranı %5'in altında.

**Yanı sıra ürettiklerin:** S1 stack (P5 için), Landsat snapshot 1985-2025 (P5 için), tile'lara bölünmüş ARD (P3 DataLoader için), `data/manifest.json` (herkesin referansı).

---

## 2. CRITICAL PATH SORUMLULUKLARIN

| Görev | Saat | CRITICAL? |
|---|---|---|
| T1.3 S2 çekim | 3 | ✅ |
| T1.4 S2 ARD | 4 | ✅ |
| T1.7 17-kanal Full ARD | 8 | ✅ |
| T1.9 ARD export + manifest | 11 | ✅ |

Bu 4 görevde gecikme = tüm Modül A geç.

---

## 3. HESAP KURULUMUN (saat 0, ~30 dk)

### 3.1 Google Cloud Platform + Earth Engine API

1. **GCP hesap aç:** https://console.cloud.google.com (Google hesabınla giriş yap, ücretsiz $300 kredi alırsın yeterli)
2. **Yeni proje oluştur:** "Pomzadoya" adıyla
3. **Earth Engine API enable:** APIs & Services → Library → "Earth Engine API" ara → Enable
4. **Earth Engine kayıt:** https://earthengine.google.com/signup → "Use without Cloud Project" YERİNE "Register Cloud Project" → Pomzadoya seç
5. **Service Account oluştur:**
   - IAM & Admin → Service Accounts → Create
   - Adı: `pomzadoya-gee-sa`
   - Rol: **Earth Engine Resource Admin** + **Service Account Token Creator**
   - Create
6. **Service Account JSON key indir:**
   - Açtığın service account'a tıkla → Keys → Add Key → Create new key → JSON
   - İndir → adını `pomzadoya-sa.json` yap → repo'nun KÖK dizinine yerleştir (ama git'e ekleme — `.gitignore`'da `*.json` var)

### 3.2 Yerel ortam

```bash
# Python 3.10+
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r code/p1/requirements.txt
```

`code/p1/requirements.txt` içeriği zaten hazır: `earthengine-api, rasterio, geopandas, gdal, numpy, scipy`.

### 3.3 Doğrulama

```bash
python -c "import ee; ee.Initialize(); print('OK')"
```
"OK" görürsen tamam. Hata alırsan grup chat.

---

## 4. KENDİ LLM'İNİ KUR (saat 0, ~10 dk)

```bash
cd Pomzadoya
claude --model claude-opus-4-7
```

**İlk mesajını şu şekilde yapıştır:**

```
Sen .claude/agents/p1-veri-muhendisi.md tanımındaki P1 — Veri Mühendisi rolündesin.
Tek doğru kaynağın: Modul_A_Critical_Path_Dependency_v2.md.

ŞİMDİKİ DURUM:
- Saat 0/24, hackathon başladı
- Ben P1 sorumlusu ekip üyesiyim
- handoff/P1_BRIEFING.md dosyası benim onboarding'imdi, okudum
- Hesap kurulumumu yaptım (GCP + GEE + service account JSON hazır)
- Yerel Python venv hazır, requirements.txt yüklü

YAPACAKLARIN:
1. agent_outputs/p1_status.md ve .claude/state/orchestrator_log.md dosyalarını oku
2. agent_outputs/p1_t1_1_runblock.md dosyasını oku — bu ilk RUN-BLOCK
3. T1.1 başlamadan önce eksik kod dosyalarımı (T1.5-T1.10) yazmaya hazırlan, ama ÖNCE T1.1'i koşturayım
4. Bana T1.1 RUN-BLOCK'unu konuşma dilinde özetle, ben Colab'da koşturacağım
5. VERIFY-BLOCK çıktımı yapıştırdığımda DELIVER üret + GitHub commit mesajı taslağı + grup chat bildirimi öner

Ben şu an Colab'da T1.1 için hazırlanıyorum. Başla.
```

LLM seninle çalışma protokolünü kuracak.

---

## 5. SAATLİK GÖREV TABLOSU

> ⚙️ = otomatik (yerel script, LLM yardımıyla), 👤 = manuel insan, 🧠 = LLM kararı, 👥 = ekipten biriyle birlikte

### Ana zincir (saat 0-24)

| Saat | Görev | Tür | Süre | Çıktı |
|---|---|---|---|---|
| 0:00-0:30 | Hesap kurulumu (GCP, GEE, service account) | 👤 | 30dk | `pomzadoya-sa.json` |
| 0:30-1:00 | LLM kurulumu + RUN-BLOCK protokolü oku | 👤 | 30dk | LLM aktif |
| **1:00-2:00** | **T1.1 GEE auth Colab notebook (`code/p1/01_gee_setup.ipynb`)** | 👤 Run + ⚙️ | 1h | GEE oturum aktif, drive mount |
| 2:00-2:30 | T1.2 AOI üretim (`code/p1/02_aoi_avanos.py`) | ⚙️ | 30dk | `data/avanos_aoi.geojson`, `.gpkg` |
| **2:30-4:00** | **T1.3 S2 L2A çekim** (GEE Code Editor — kod LLM'den, sen Run) | 👤 Run + ⚙️ asenkron | 1.5h | `data/s2_l2a_<date>.tif` (Drive) |
| **4:00-5:00** | **T1.4 S2 co-registration** (`code/p1/04_s2_coregistration.py`) | ⚙️ | 1h | `data/ard/s2_ard_20m.tif` |
| **4:00-5:30** | **T1.5 S1 GRD çekim** (paralel — kod LLM yazacak `code/p1/05_*.py`) | 👤 Run + ⚙️ | 1.5h | `data/s1_stack/s1_<dates>.tif` |
| 5:30-6:30 | T1.6 DEM çekim (kod LLM yazacak `code/p1/06_*.py`) | ⚙️ | 1h | `data/dem.tif`, `data/slope.tif` |
| **6:30-8:00** | **T1.7 Full co-reg 17 kanal** (kod LLM yazacak `code/p1/07_*.py`) | ⚙️ | 1.5h | `data/ard/full_ard_20m.tif` |
| 8:00-10:00 | T1.8 Tile splitting 256×256+32 overlap (kod LLM yazacak) | ⚙️ | 2h | `data/tiles/*.tif` |
| **10:00-11:00** | **T1.9 ARD export + manifest.json** (kod LLM yazacak) | ⚙️ | 1h | `data/manifest.json` |
| 11:00-13:00 | T1.10 Landsat Tier 2 snapshot (1985, 1990, 2000, 2010, 2025 — kod LLM yazacak) | 👤 Run + ⚙️ | 2h | `data/landsat/L*_<year>.tif` |
| 13:00-14:00 | T1.11 QC raporu (`reports/p1_qc.md`) | ⚙️ | 1h | QC raporu |
| **14:00-16:00** | **HELP→P2 etiketleme yardım** (P2 4-saat poligon çiziminin son 2 saatinde yardıma gel) | 👥 | 2h | 5-10 ek negatif poligon birlikte |
| 16:00-18:00 | HELP→P5 demo offline cache (P5'e fallback sahnesi hazırla) | 👥 | 2h | `demo/offline_cache/` |
| **18:00-20:00** | **Entegrasyon oturumu** (Discord call, hep birlikte) | 👥 | 2h | `run_pipeline.sh` test |
| 20:00 | **KOD FREEZE** | 🛑 | — | — |
| 20:00-24:00 | T1.15 Dry-run desteği + bug fix support | 👥 | 4h | demo hazır |

---

## 6. ASENKRON İŞ KURALI

GEE export'ları **arka planda koşar, sen başka iş yaparsın**:

- T1.3 S2 export Run → 30dk asenkron → bu sırada sen T1.5 S1 RUN-BLOCK'unu LLM'den iste, T1.4 co-reg script'ini hazırla
- T1.5 S1 export Run → 20dk asenkron → bu sırada T1.6 DEM hazırla
- T1.10 Landsat 5 yıl snapshot → her biri 5-10dk → 5 paralel job tetikle, 30dk sonra hepsini al

**Kural:** Bir RUN-BLOCK koşturduğunda etiketle "T1.x Run Run, ETA 30dk" → LLM hemen sıradaki RUN-BLOCK'u verir.

---

## 7. KIM SANA NE TESLİM EDİYOR / SEN KİME NE TESLİM EDİYORSUN

### Sana gelen (HİÇ — sen critical path'in başısın)
P1 olarak kimseyi beklemiyorsun. Saat 0'dan başla.

### Senden çıkan (kim ne zaman bekliyor)

| Saat | Çıktı | Tüketici | Kullanım |
|---|---|---|---|
| 4 | `data/ard/s2_ard_20m.tif` | P4 | T4.4 S2 türetilmiş indeksler (NDVI/BSI/Albedo/Sabins) |
| 5.5 | `data/s1_stack/` | P5 | T5.5 S1 amplitude difference (Mazza 2023) |
| 8 | `data/ard/full_ard_20m.tif` (17-kanal) | P3 | T3.5 fine-tune girdi tensörü |
| 8 | `data/dem.tif`, `data/slope.tif` | P4 | T4.8 DEM aspect/hillshade |
| 10 | `data/tiles/` | P2, P3 | T2.8 raster mask + T3.5 DataLoader |
| 11 | `data/manifest.json` | P3, P4, P5 | Bant bilgisi, CRS, bounds |
| 13 | `data/landsat/L*_<year>.tif` | P5 | T5.8 Roy 2016 + GIF + T5.10 historical pomza tespit |

**Her teslimattan sonra grup chat:**
```
[P1][T1.x][saat-h] TAMAM
çıktı: <path>
bağımlı: <kim>
```

---

## 8. PLAN B'LERİN

| Tetikleyici | Plan B | Onay |
|---|---|---|
| T1.3 saat 3'te bitmediyse (bulutlu sahne) | Pre-cache temiz tile fallback (hackathon öncesi indirilmiş — eğer yoksa: 2 hafta öncesindeki en yakın bulut-az sahneyi kullan) | Grup chat 30sn |
| GEE quota aşıldı | İkinci GCP hesabıyla failover (yedek olarak hazır tut) | Grup chat |
| ARD dosya çok büyük (>20 GB) | Tile-based local export, full-image export iptal | Grup chat |
| S1 sahne tarih uyuşmazlığı | En yakın S2 tarihiyle ±5 gün toleransla S1 seç | Otomatik (LLM karar verir) |

---

## 9. EKSİK KOD BATCH — İlk yapacağın iş

Saat 0'da, T1.1'i Colab'da koşturmaya başlamadan önce LLM'ine şu prompt'u yapıştır:

```
T1.1'e geçmeden önce, eksik kalan T1.5-T1.10 kodlarını paralel olarak şu dosya adlarıyla yazmanı istiyorum:

- code/p1/05_sentinel1_grd_fetch.py — T1.5 S1 GRD çekim + Lee filter + dB conversion
- code/p1/06_dem_slope.py — T1.6 Copernicus GLO-30 DEM çekim + slope/aspect
- code/p1/07_full_coregistration.py — T1.7 Full 17-kanal co-reg (S2 + S1 + DEM + slope + türev). Output: data/ard/full_ard_20m.tif
- code/p1/08_tile_splitting.py — T1.8 256x256 + 32 px overlap tile splitting. Output: data/tiles/<row>_<col>.tif
- code/p1/09_export_manifest.py — T1.9 ARD export validation + data/manifest.json üretici (bant açıklamaları, CRS, bounds, çözünürlük 20m, NoData değerleri)
- code/p1/10_landsat_snapshots.py — T1.10 Landsat Tier 2 snapshots (yıllar: 1985, 1990, 2000, 2010, 2025), Avanos AOI clip, EPSG:32636

Her dosya gerçek çalışabilir kod, placeholder DEĞİL. Path'ler relative. 20m grid (Karar #15). EPSG:32636. Modul_A_Critical_Path_Dependency_v2.md § P1'e bak detaylar için.

Yazdıktan sonra 1-paragraf özet ver, ben sonra T1.1'e geçeyim.
```

LLM bu kodları yazar (~5 dakika). Sonra T1.1'e geçersin.

---

## 10. GITHUB WORKFLOW

### Branch + commit

```bash
# Her görev için:
git checkout -b p1-t1.x-<kısa-ad>
# çalış, kod üret
git add code/p1/* agent_outputs/p1_*
git commit -m "[P1] T1.x <açıklama>

DELIVER: <çıktı path>
Bağımlı: <kim>"
git push origin p1-t1.x-<kısa-ad>
```

### PR

PR aç ana branch'e (`main`), grup chat'te "PR #X review" mesajı at. Critical path görevlerinde 5dk içinde merge edilir (review opsiyonel hızlı).

---

## 11. GRUPLA SENKRON NOKTALAR

| Saat | Olay | Senin rolün |
|---|---|---|
| 0:00 | Kick-off | "P1 hazır" mesajı |
| 4:00 | S2 ARD teslim | Grup chat'e bildir, P4 başlasın |
| 8:00 | Full ARD + DEM teslim | Grup chat, P3 + P4 başlasın |
| 11:00 | Manifest teslim | Grup chat, herkes manifest'i okusun |
| 13:00 | Landsat teslim | Grup chat, P5 başlasın |
| 14:00 | HELP→P2 başla | P2'nin yanına geç (Discord call veya yan yana) |
| 16:00 | HELP→P5 başla | P5 ile demo backup üzerinde çalış |
| 18:00 | **Entegrasyon Discord call** | Hep birlikte |
| 20:00 | **KOD FREEZE** | Sadece bug fix |
| 22:00 | Dry-run #1 | Hep birlikte |
| 23:00 | Dry-run #2 | Hep birlikte |
| 24:00 | Demo | Sunum |

---

## 12. KENDİNİ KONTROL — saat 4, 8, 11, 13'te şu listeyi gör

### Saat 4 ✓
- [ ] `data/ard/s2_ard_20m.tif` exists
- [ ] `gdalinfo` çıktısı: 10 bant, 20m, EPSG:32636, NoData -9999
- [ ] P4'e mesaj attın mı?

### Saat 8 ✓
- [ ] `data/ard/full_ard_20m.tif` exists, **17 bant**
- [ ] Bant sırası manifest'te: B2,B3,B4,B5,B6,B7,B8,B8A,B11,B12,VV,VH,DEM,slope,NDVI,BSI,Albedo
- [ ] P3 ve P4'e mesaj attın mı?

### Saat 11 ✓
- [ ] `data/manifest.json` exists, valid JSON
- [ ] `data/tiles/` 256×256 + 32 overlap dosyaları var
- [ ] Tüm ekibe duyuru attın mı?

### Saat 13 ✓
- [ ] `data/landsat/L*_<year>.tif` 5 yıl için var (1985, 1990, 2000, 2010, 2025)
- [ ] P5'e mesaj attın mı?

Listeden bir madde ✗ ise grup chat eskalasyon.

---

## 13. DOSYA REFERANSLARIN

| Ne | Nerede |
|---|---|
| Rol tanımım | `.claude/agents/p1-veri-muhendisi.md` |
| Görev detayım | `Modul_A_Critical_Path_Dependency_v2.md` § P1 |
| Mevcut kodlarım | `code/p1/` (6 dosya hazır, T1.5-T1.10 LLM yazacak) |
| RUN-BLOCK'larım | `agent_outputs/p1_t1_*_runblock.md` |
| Statüm | `agent_outputs/p1_status.md` |
| Pipeline shell | `code/p1/run_pipeline.sh` |
| Bağımlılarım | v2 § 3 Dependency Tablosu |
| Plan B'lerim | v2 § 6 Risk Path |

---

## 14. SIK KARŞILAŞTIĞIM SORULAR

**S: GEE service account JSON'u Colab'a nasıl yükleyeceğim?**
C: T1.1 RUN-BLOCK'unda hücre var. Colab `files.upload()` kullanır, sen file picker'dan JSON'u seçersin.

**S: GEE export Drive'a mı, GCS'ye mi yazıyor?**
C: T1.3 RUN-BLOCK'unda Drive'a yazıyor (`Export.image.toDrive`). Drive mount ederek erişirsin.

**S: 17 kanal sırası ne?**
C: B2-B12 (10 S2 bant), VV+VH (2 S1), DEM+slope (2), NDVI+BSI+Albedo (3 türev). Manifest'te kesin sıra yazılı.

**S: Tile overlap 32 niye?**
C: Edge artifact'larını azaltmak için. Inference sırasında P3 ve P5 cosine-blend ile 32 px overlap'i smooth merge eder.

**S: T1.5 ve T1.6 ne zaman başlamalı?**
C: T1.4 paralel ile saat 4'te başla. S1 ve DEM bağımsız, paralel çekersin.

**S: Bulutlu sahne çıkarsa?**
C: 03_sentinel2_l2a_fetch.py'de `cloud_pct < 20%` filter var. Eşleşen sahne yoksa pencereyi 60 günden 90 güne genişlet, en bulut-az sahneyi al.

---

## 15. SENİN BAŞARI KRİTERLERİN

Saat 24'te demo başarılıysa **senin** sorumluluğun:
1. ✅ `data/ard/full_ard_20m.tif` saat 8'de hazır oldu
2. ✅ `data/manifest.json` saat 11'de hazır oldu
3. ✅ `data/landsat/` saat 13'te hazır oldu
4. ✅ P3, P4, P5 senden gelen veriyle hatasız çalıştı
5. ✅ Critical path'te gecikme yok

Bu 5 maddeyi tutturursan rolün başarılı.

---

## 16. SAĞLIK & GÜVENLİK

- 24 saat boyunca uyanık kalma. **Saat 14-16 HELP slot'unda** kısa şekerleme alman önerilir (P2 yardımı uzun sürebilir ama P3 de senin verine bağımlı değil bu pencerede, slack zamanın).
- Su iç. Kafein dengeli kullan.
- 18:00 entegrasyon öncesi 1 saat ara ver eğer mümkünse.

---

**Saat 0 başladı sayılır. İlk eylemin: 3.1 GCP hesap kurulumu. Bittiğinde grup chat'e "P1 hesap hazır" yaz.**
