# Pomzadoya — Master Koordinasyon Dokümanı

> **5 kişilik ekip, 24 saat hackathon, Modül A.** Bu doküman herkesin önce okuması gereken ortak kurallar setidir. Kendi rolüne özel briefing için: `P1_BRIEFING.md` … `P5_BRIEFING.md`.

---

## 0. Hızlı başlangıç (her kişi 5 dakikada okur)

1. **Bu dokümanı sonuna kadar oku** (ortak kurallar)
2. **Kendi P_n_BRIEFING.md dosyanı oku** (rolüne özel her şey)
3. **`01_STATUS_REPORT.md`'yi oku** (neyin hazır olduğu, neyin yapılacağı)
4. **`Modul_A_Critical_Path_Dependency_v2.md`'yi oku** (ana plan, tek doğru kaynak)
5. **Hesaplarını oluştur** (kendi briefing'inde liste var)
6. **Kendi LLM'ini kur** (aşağıda detay)
7. **Saat 0'da başla**

Toplam onboarding süresi: ~30 dakika hesap kurulumu, ~30 dakika okuma.

---

## 1. Proje konteksti

**Proje:** Pomzadoya — Avanos/Nevşehir bölgesinde uydu tabanlı pomza (pumice) madencilik tespiti, UNESCO Göreme National Park ihlal red flag sistemi.

**Modül A:** Veri pipeline + AI eğitimi + score-level füzyon + Streamlit dashboard. 24 saat penceresi.

**Çıktı:** Streamlit dashboard'da 3 ekran (Saha Tarama, AI Analizi, Operasyonel Karar) — gerçek zamanlı pomza tespit haritası + 1985-2025 zaman serisi + UNESCO ihlal listesi.

**Tek doğru kaynak:** `Modul_A_Critical_Path_Dependency_v2.md` (repo kökünde). Bu dosya değişirse tüm ekip okumak zorunda.

---

## 2. 5 kişilik rol dağılımı

| Kişi | Rol | Ana sorumluluk | Critical Path görevleri |
|---|---|---|---|
| **P1** | Veri Mühendisi | 17-kanal 20m ARD üretim zinciri (S2 + S1 + DEM + Landsat) | T1.3, T1.4, T1.7, T1.9 |
| **P2** | Etiketleme Lead | MAPEG ÇED sorgu, manuel poligon, Roberts 2017 5-fold blok CV, raster mask | **T2.8** |
| **P3** | ML Mühendisi | SSL4EO-S12 + 13→17 adapter, fine-tune, RAW olasılık inference | T3.5, T3.10 |
| **P4** | Spektral Mühendis | ASTER + Ninomiya QI/SiO₂/CI, score-level füzyon | **T4.12** |
| **P5** | Change Detection + Viz | S1 amplitude, Roy 2016 Landsat, Streamlit dashboard, KPI, demo | T5.13, T5.15 |

**Critical path** (10 görev, gecikmesin):
```
T1.3 → T1.4 → T1.7 → T1.9 → T2.8 → T3.5 → T3.10 → T4.12 → T5.13 → T5.15
```

---

## 3. Her kişinin kendi LLM'ini kurması

Her kişi kendi makinesinde kendi LLM ajanını çalıştırır. Bu sayede paralel iş yapılır, tek noktada darboğaz oluşmaz.

### Tavsiye edilen kurulum: Claude Code

**Adım 1 — Anthropic API key veya Claude Pro hesabı (her ekip üyesi kendisi alır):**
- https://console.anthropic.com (API key) **veya** Claude Pro abonelik

**Adım 2 — Claude Code CLI kurulumu (her ekip üyesinin makinesinde):**
```bash
# Windows / macOS / Linux
npm install -g @anthropic-ai/claude-code
```
veya VSCode extension olarak kur (Claude Code).

**Adım 3 — Repo'yu klon ve aç:**
```bash
git clone <repo-url> Pomzadoya
cd Pomzadoya
claude --model claude-opus-4-7
```

**Adım 4 — İlk mesaj olarak rolünü yapıştır:**

P1 için (P2, P3, P4, P5 için aynı mantık, sadece dosya adı değişir):
```
Sen .claude/agents/p1-veri-muhendisi.md tanımındaki P1 rolündesin.
Tek doğru kaynağın Modul_A_Critical_Path_Dependency_v2.md.
Ben P1 sorumlusu olan ekip üyesiyim.
.claude/state/orchestrator_log.md dosyasındaki güncel durumu oku.
agent_outputs/p1_status.md dosyasını oku.
İlk RUN-BLOCK'umu (T1.1) ver, ben Colab'da koşturacağım.
```

LLM seninle birlikte çalışır: RUN-BLOCK üretir, sen koşturursun, VERIFY-BLOCK çıktısını yapıştırırsın, LLM DELIVER üretir, sen GitHub'a push'larsın.

### Alternatif LLM'ler

İsteyen kendi LLM'ini kullanabilir (ChatGPT Plus, Cursor, Gemini, Aider vb.). Tek şart: rol dosyasını (`.claude/agents/p_n-*.md`) ve `Modul_A_Critical_Path_Dependency_v2.md`'yi kontekste yükle. RUN-BLOCK / VERIFY-BLOCK / DELIVER protokolünü uyguladığı sürece sorun yok.

> **Önemli:** Hangi LLM'i kullanırsan kullan, **kendi rol briefing'in** + **kritik patika dosyası** + **agent_outputs/p_n_status.md** kontekste olmalı. Eksik kontekstle başlama.

---

## 4. GitHub workflow

### Repo yapısı

```
Pomzadoya/
├── .claude/agents/        # Agent rol tanımları (DOKUNMA)
├── .claude/state/         # Orchestrator state (P_n yazmaz, sadece okur)
├── code/p1/ ... p5/       # Her P_n kendi klasörüne yazar
├── data/                  # Veri çıktıları (büyük dosyalar Git LFS veya .gitignore)
├── models/                # Model checkpoint'leri (Git LFS)
├── reports/               # Metric raporları, KPI
├── demo/                  # Demo PNG fallback
├── agent_outputs/         # RUN-BLOCK / status (GitHub'a push EDİLİR)
├── handoff/               # Bu klasör — ekip onboarding
└── Modul_A_Critical_Path_Dependency_v2.md
```

### Branch kuralları

- `main` — final, dokunulmaz, sadece PR ile birleşir
- `p1-*`, `p2-*`, `p3-*`, `p4-*`, `p5-*` — her kişi kendi prefix'iyle branch açar
  - Örn: `p1-t1.3-s2-fetch`, `p3-t3.5-finetune`, `p4-t4.12-fusion`

### Commit mesaj formatı

```
[P_n] T_x.y <kısa açıklama>

DELIVER: <çıktı path>
Bağımlı: <kim bekliyor — varsa>
```

**Örnek:**
```
[P3] T3.5 SSL4EO-S12 fine-tune (5-fold blok CV)

DELIVER: models/unet_pomza_ssl4eo.pt (5 fold ortalama IoU 0.52)
Bağımlı: P4 T4.12 + P5 T5.10 inference fn bekliyor
```

### Push frekansı

- **Her DELIVER'dan sonra push** (en geç 30 dk içinde)
- Critical path görevlerinde push **zorunlu**
- WIP commit'leri OK ama push etmeden önce çalıştığını doğrula

### .gitignore (kök dizinde olacak — ekibin biri push'lasın)

```
# Veri dosyaları (büyük)
data/ard/*.tif
data/tiles/
data/landsat/
data/s1_stack/
data/aster/
*.tif
*.gpkg

# Model checkpoint'leri (Git LFS)
models/*.pt
models/*.onnx

# Token / credentials
*.json
!**/manifest.json
!**/layers.json
!**/kpi.json
.netrc
.env

# Python
__pycache__/
*.pyc
.venv/
venv/

# OS
.DS_Store
Thumbs.db
```

### Büyük dosyalar — Git LFS

ARD GeoTIFF'leri (~5-20 GB) ve model checkpoint'leri (~500 MB) Git LFS ile takip edilir:
```bash
git lfs install
git lfs track "models/*.pt"
git lfs track "data/ard/*.tif"
```

Eğer LFS quota yetmezse: model + ARD'leri Google Drive paylaşımlı klasörde tut, repo'da sadece `link.txt` yer alsın.

---

## 5. Ekip içi iletişim protokolü

### Sürekli senkron — 1 grup chat (Discord/Slack/WhatsApp)

**Otomatik bildirim formatı (mesajını şu şablonla at):**
```
[P_n][T_x.y][saat-h] <BAŞLA / TAMAM / BLOKLU / PLAN-B>
detay: <1 satır>
bekleyen: <varsa kim>
```

**Örnek:**
```
[P1][T1.3][saat-2] BAŞLA
detay: GEE export tetiklendi, ETA saat 3
bekleyen: P3 T3.5 (saat 12), P4 T4.4 (saat 5)
```

```
[P3][T3.5][saat-15] TAMAM
detay: 5-fold ortalama val IoU 0.52
bekleyen: P4 T4.12 (saat 18), P5 T5.10 (saat 17.5)
```

### Sync noktaları

| Saat | Kim | Ne |
|---|---|---|
| 0:00 | Hepsi | Kick-off, herkes T_n.1 başlasın |
| 4:00 | P1 → P4 | S2 ARD teslim |
| 8:00 | P1 → P3, P4 | Full ARD (17 kanal) teslim |
| 11:00 | P2 → P3 | Spatial blok CV split teslim |
| 13:00 | P2 → P3 | Raster mask (T2.8 critical) teslim |
| 13:00 | P1 → P5 | Landsat snapshot teslim |
| 17:30 | P3 → P4, P5 | RAW inference fn (T3.10) teslim |
| 18:00 | Hepsi | **Entegrasyon başlangıcı** — Discord call açılır |
| 20:00 | Hepsi | **KOD FREEZE** |
| 22:00 | P5 + Hepsi | Dry-run #1 + #2 |
| 24:00 | Demo | Sunum |

### Eskalasyon kuralı

Bir görev tahmini süresinin **%150'sini** geçtiğinde grup chat'e yaz: "Plan B'ye mi geçeyim?" — Plan B'ye geçiş kararı **birlikte** verilir.

---

## 6. RUN-BLOCK / VERIFY-BLOCK / DELIVER protokolü

Her görevde 3 fazlı çalışma:

```
[1] HAZIRLA           [2] SEN KOŞTUR             [3] DOĞRULA + RAPORLA
─────────────         ──────────────────         ──────────────────────
LLM RUN-BLOCK        Sen Colab/QGIS/GEE'de      Sen VERIFY-BLOCK çıktısını
+ VERIFY-BLOCK       koşturursun                LLM'e yapıştırırsın → 
üretir               (15dk - 6h offline)        DELIVER üretir → grup
                                                chat + GitHub push
```

**RUN-BLOCK** = LLM'in sana verdiği çalıştırılabilir adım listesi (Colab notebook hücresi, QGIS adımı, terminal komutu).

**VERIFY-BLOCK** = Çıktının doğru olduğunu kanıtlamak için sen LLM'e yapıştıracağın log/screenshot/path.

**DELIVER** = LLM'in "TAMAM, çıktı buradadır, bağımlılar tetiklendi" raporu. Bu rapor commit mesajının ve grup chat bildiriminin temelidir.

---

## 7. Plan B kararları (Risk yönetimi)

`Modul_A_Critical_Path_Dependency_v2.md` § 6'daki risk tablosu tek doğru kaynak. Tetikleyici oluşursa:

1. Grup chat'e yaz: "Plan B tetik: T_x.y, gerekçe: ..."
2. **30 saniye bekle** — itiraz var mı?
3. Yoksa Plan B'ye geç, LLM'e RUN-BLOCK üret dedirt.

Plan B özetleri:

| Tetikleyici | Plan B |
|---|---|
| T1.3 saat 3'te bitmedi | Pre-cache temiz tile fallback (P1) |
| T2.7 5-fold karmaşık | 3-fold'a düş (P2) |
| T3.5 yakınsamıyor | RGB-only baseline veya threshold fallback (P3) |
| T4.3 ASTER L2 başarısız | L1T radiance ile devam (P4 — Karar #4) |
| T4.12 saat 20'de bitmedi | P5 dashboard'da RAW + ASTER ayrı katman (P5) |
| Roy 2016 yavaş | Basit per-band linear regression (P5) |
| Streamlit saat 20'de bitmedi | PNG fallback T5.14 (P5) |

---

## 8. Hesap & token kontrol listesi (her kişi kendisi kurar)

| P_n | Gereken hesap/token | Süre |
|---|---|---|
| P1 | GCP + Earth Engine API + service account JSON | ~30 dk |
| P2 | QGIS yerel kurulum, MAPEG ÇED erişim, WDPA download | ~20 dk |
| P3 | Colab Pro VEYA Kaggle GPU, opsiyonel W&B | ~15 dk |
| P4 | NASA Earthdata (urs.earthdata.nasa.gov) | ~10 dk |
| P5 | Yerel Python 3.10+, opsiyonel Streamlit Cloud | ~15 dk |

Hesap kurulum talimatları her P_n_BRIEFING.md içinde tam olarak yazılı.

---

## 9. Klasör hijyeni — herkes uyacak

- **Asla diğer P_n'in klasörüne yazma** (örn. P3, `code/p1/` altına dosya yazmaz)
- **Sadece kendi `code/p_n/`, `data/<rolüne ait alt klasör>/`, `agent_outputs/p_n_*.md` dosyalarını değiştir**
- **Ortak klasörler** (paylaşılan input/output): `data/manifest.json`, `data/layers.json` — koordineli güncelle, mesaj at
- **`.claude/state/orchestrator_log.md`** orchestrator yazsın — sen sadece okuyucusun
- **`Modul_A_Critical_Path_Dependency_v2.md`** dokunulmaz, tek doğru kaynak

---

## 10. Acil durum protokolü

**Eğer:**
- Critical path bir görev 1 saatten uzun gecikti → grup chat eskalasyon
- Bir kişi internet/elektrik kaybetti → Discord call açılır, sırasındaki görevi başkası devralır
- LLM hatalı kod üretti → grup chat'e yapıştır, başka biri review etsin
- GitHub conflict → branch koruyucu (P1) müdahale eder, gerekirse manuel merge

**Önceliklenme:**
1. Demo akışı (saat 22-24) > kod kalitesi
2. Critical path görevleri > paralel görevler
3. Çalışan Plan B > yarıda kalmış Plan A

---

## 11. Sonuç teslim kontrol listesi (saat 18 entegrasyon öncesi)

Her P_n şu dosyaların var olduğunu doğrular (`Glob`/`ls`):

### P1 sahibi
- [ ] `data/ard/full_ard_20m.tif` (17-kanal, 20m)
- [ ] `data/tiles/` (256×256 + 32 px overlap)
- [ ] `data/manifest.json`
- [ ] `data/landsat/` (P5 için)
- [ ] `data/s1_stack/` (P5 için)

### P2 sahibi
- [ ] `data/labels/positive_polygons.gpkg`
- [ ] `data/labels/positive_pixels.gpkg`, `negative_pixels.gpkg`
- [ ] `data/labels/full_mask.tif` (T2.8 kritik)
- [ ] `data/labels/blok_cv_split.json` (Roberts 2017 5-fold)
- [ ] `data/labels/ignore_mask.tif`

### P3 sahibi
- [ ] `code/p3/07_inference.py` (`predict_raw()` API)
- [ ] `models/unet_pomza_ssl4eo.pt` (FP32)
- [ ] `models/unet_pomza_fp16.pt` (KOD FREEZE öncesi)
- [ ] `reports/metrics_5fold.json`, `threshold_curve.json`

### P4 sahibi
- [ ] `data/layers/aster_qi.tif`, `aster_sio2.tif`, `aster_ci.tif` (20m grid)
- [ ] `data/layers/s2_*.tif` (NDVI, BSI, Albedo, Sabins)
- [ ] `data/layers/dem_aspect.tif`, `dem_hillshade.tif`
- [ ] `code/p4/fuse_confidence.py`
- [ ] `data/layers/final_confidence.tif` (T4.12 kritik)

### P5 sahibi
- [ ] `data/change/s1_change.tif`
- [ ] `data/temporal/landsat_harmonized/`, `landsat_timelapse.gif`
- [ ] `data/temporal/historical_pomza_overlay/` (T5.10 RAW)
- [ ] `code/p5/dashboard.py` (Streamlit çalışır)
- [ ] `data/layers.json` (5 katman manifest)
- [ ] `reports/kpi.json`
- [ ] `demo/fallback/` (PNG fallback)

---

## 12. Glossary

| Terim | Anlam |
|---|---|
| **ARD** | Analysis Ready Data — co-registered, harmonize edilmiş 17 kanal raster |
| **Critical path** | En uzun bağımlılık zinciri — gecikme tüm projeyi geciktirir |
| **RAW olasılık** | P3 inference çıktısı, threshold uygulanmamış [0,1] |
| **FUSED** | P4 score-level füzyon sonrası `final_confidence.tif` |
| **WDPA** | World Database on Protected Areas — Göreme National Park sınırı |
| **MAPEG** | Maden ve Petrol İşleri Genel Müdürlüğü — pomza saha kayıtları |
| **5-fold blok CV** | Roberts 2017 spatial cross-validation — bloklar coğrafi olarak ayrık |
| **Roy 2016** | Cross-sensor Landsat harmonization (TM/ETM+/OLI lineer regresyon) |
| **Mazza 2023** | S1 amplitude difference change detection metodu |
| **SSL4EO-S12** | Sentinel-2 self-supervised pretrained backbone (Wang et al.) |
| **Ninomiya QI** | Quartz Index = B11²/(B10×B12) (ASTER) |

---

## 13. Hızlı referans tablosu

| İhtiyacın | Bak |
|---|---|
| Rolüm ne? | `P_n_BRIEFING.md` |
| Nelerin hazır olduğu? | `01_STATUS_REPORT.md` |
| Detaylı görev tablom? | `Modul_A_Critical_Path_Dependency_v2.md` § P_n |
| Sıradaki RUN-BLOCK'um? | `agent_outputs/p_n_t_x_y_runblock.md` |
| Anlık durum? | `.claude/state/orchestrator_log.md` |
| Kim kime ne teslim ediyor? | v2 dosyası § 3 Dependency Tablosu |
| Plan B nedir? | v2 dosyası § 6 Risk Path |
| Slack zamanım? | v2 dosyası § 4 Help Slot |

---

*Soru varsa kendi briefing'inde ya da tek doğru kaynakta cevabı vardır. Bulamadığında grup chat — son çare.*
