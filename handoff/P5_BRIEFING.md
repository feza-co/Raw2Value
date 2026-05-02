# P5 — Change Detection + UNESCO + Visualization Briefing

> **Hoş geldin.** Sen Modül A'nın **finalini** sahnelersin. 4 kişinin çıktısını tek dashboard'da birleştir, S1 değişim tespiti, Roy 2016 Landsat harmonizasyon, Streamlit 3-ekran demo, KPI hesabı, demo backup. **Senin başarın = projenin görünür yüzü.**

---

## 1. ROLÜN ÖZETİ

**Sen P5 — Change Detection + UNESCO + Visualization sorumlusu**sun. **Modül A'yı sahneye sen koyuyorsun.** 

**Birincil çıktıların:**
1. **`code/p5/dashboard.py`** — Streamlit 3-ekran (Saha Tarama, AI Analizi, Operasyonel Karar)
2. **`data/temporal/landsat_timelapse.gif`** — 1985→2025 zaman serisi
3. **`reports/kpi.json`** — saha alan, büyüme %, UNESCO ihlal sayımı
4. **`demo/fallback/`** — internet kesintisi senaryosu için PNG fallback

**v2 KRİTİK AYRIM:**
- **Historical (1985-2025 Landsat)** → P3 RAW olasılık + manuel threshold (kontemporanöz ASTER yok, füzyon yok)
- **Current (2025 S2+ASTER)** → P4 FUSED `final_confidence.tif` (ana dashboard katmanı)

---

## 2. CRITICAL PATH SORUMLULUKLARIN

| Görev | Saat | CRITICAL? |
|---|---|---|
| **T5.10 Historical RAW inference** | **17.5-19** | ✅ |
| **T5.13 Final entegrasyon (5 katman)** | **18-20** | ✅ |
| **T5.15 Dry-run #1 #2 + ekran-paylaşım** | **22-24** | ✅ |

T5.13 saat 20'de bitmezse demo başarısız.

---

## 3. HESAP & ARAÇ KURULUMUN (saat 0, ~15 dk)

### 3.1 Yerel Python ortam
```bash
python -m venv venv
source venv/bin/activate
pip install -r code/p5/requirements.txt
```

`requirements.txt`: `streamlit, folium, leafmap, shapely, imageio, rasterio, geopandas, branca, numpy, pandas, requests`

### 3.2 GDAL (zorunlu)
- Conda: `conda install -c conda-forge gdal=3.7`
- VEYA OSGeo4W (Windows)

### 3.3 Streamlit Cloud (opsiyonel)
- https://streamlit.io/cloud → ücretsiz hesap → GitHub bağla
- Demo'yu cloud'a deploy edebilirsin (yedek)

### 3.4 WDPA Goreme shapefile (P2 ile aynı kaynak — paylaşımlı)
- Eğer P2 indirdiyse repo'da `data/wdpa_goreme.zip` var
- Yoksa: protectedplanet.net → Goreme National Park → Shapefile

### 3.5 OSM Overpass API erişimi
- Rate limit: ücretsiz, ama yoğun saatte yavaş
- `code/p5/02_wdpa_goreme.py` Overpass query'i kullanıyor
- Plan B: yerel Overpass (Docker) — gerek olmaz büyük ihtimalle

---

## 4. KENDİ LLM'İNİ KUR (saat 0, ~10 dk)

```bash
cd Pomzadoya
claude --model claude-opus-4-7
```

**İlk mesaj:**

```
Sen .claude/agents/p5-change-detection-viz.md tanımındaki P5 — Change Detection + UNESCO + Visualization rolündesin.
Tek doğru kaynağın: Modul_A_Critical_Path_Dependency_v2.md.

ŞİMDİKİ DURUM:
- Saat 0/24
- Ben P5 sorumlusu ekip üyesiyim
- handoff/P5_BRIEFING.md okudum
- Yerel Python venv hazır, GDAL kurulu, Streamlit yüklü
- WDPA Goreme shapefile elimde

KRİTİK HATIRLATMA:
- T5.10 vs T5.13 ayrımı: historical=RAW (P3 predict_raw), current=FUSED (P4 final_confidence.tif)
- T5.13 final entegrasyon saat 18-20 critical path
- T5.15 dry-run saat 22-24 critical path
- 2 slack penceren var (saat 3-5.5 ve 9.5-13) — Folium iskelet + model export hazırlık

YAPACAKLARIN:
1. agent_outputs/p5_status.md ve .claude/state/orchestrator_log.md oku
2. code/p5/dashboard.py'yi gözden geçir, 3-ekran layout doğru mu
3. agent_outputs/p5_t5_1_runblock.md ile başla
4. Slack zamanlarımı planla — 3-5.5 saatte Folium iskelet, 9.5-13 saatte model export hazırlık
5. T5.13 RUN-BLOCK'unu erken hazırla, P4 final_confidence.tif geldiğinde yapıştır-koştur olsun

T5.1'den başla.
```

---

## 5. SAATLİK GÖREV TABLOSU

| Saat | Görev | Tür | Süre |
|---|---|---|---|
| 0:00-0:15 | Kurulum | 👤 | 15dk |
| 0:15-0:30 | LLM kurulumu | 👤 | 15dk |
| **0:30-1:30** | **T5.1 Ortam kurulum (`code/p5/01_env_setup.md`)** | 👤 + ⚙️ | 1h |
| 1:30-2:30 | T5.2 WDPA Goreme + 1000m + OSM cross-check (`02_wdpa_goreme.py`) | ⚙️ | 1h |
| 2:30-3:30 | T5.3 Red flag overlay logic (sentetik raster, `03_red_flag_logic.py`) | ⚙️ | 1h |
| 3:30-5:30 | 🟡 SLACK 1 — Folium iskelet T5.6 öne çek | 🧠 ⚙️ | 2h |
| **5:30-7:30** | **T5.5 S1 amplitude diff (Mazza 2023, `04_s1_amplitude_diff.py`)** | ⚙️ | 2h |
| 7:30-9:30 | T5.6 Folium harita altyapı + baselayer (`05_folium_basemap.py`) | ⚙️ | 2h |
| 9:30-13:00 | 🟡 SLACK 2 — model export hazırlık + P2 etiket görsel (HELP→P2 hazırlık) | 🧠 ⚙️ | 3.5h |
| **13:00-16:00** | **T5.8 Roy 2016 Landsat harmonization + GIF (`06_*.py`, `07_*.py`)** | ⚙️ | 3h |
| 16:00-17:30 | T5.9 Layer ekleme (5 katman manifest, `09_layer_manifest.py`) | ⚙️ | 1.5h |
| **17:30-19:00** | **🔴 T5.10 Historical RAW inference (CRITICAL, `08_historical_pomza_inference.py`)** | ⚙️ | 1.5h |
| 19:00-20:00 | T5.11 KPI hesabı (`10_kpi_calc.py`) | ⚙️ | 1h |
| 18:00-20:00 | T5.12 Streamlit dashboard entegrasyonu (`dashboard.py`) | ⚙️ | 2h |
| **18:00-20:00** | **🔴 T5.13 Final entegrasyon (CRITICAL) — P4 fused + 5 katman tek dashboard** | ⚙️ + 👥 | 2h |
| 18:00-20:00 | Entegrasyon | 👥 | 2h |
| 20:00 | **KOD FREEZE** | 🛑 | — |
| 20:00-22:00 | T5.14 Demo backup PNG fallback (`12_demo_fallback.py`) | ⚙️ | 2h |
| **22:00-24:00** | **🔴 T5.15 Dry-run #1 #2 + ekran-paylaşım (CRITICAL)** | 👤 + 👥 | 2h |
| 24:00 | Demo sunum | 👥 | — |

---

## 6. SLACK ZAMANLARI — DEĞERLENDİR (toplam 5.5 saat)

### Slack 1 (saat 3:30-5:30, 2h)
P1 S1 stack saat 5.5'te teslim edecek, sen önce bekliyorsun.

**Yap:**
- T5.6 Folium altyapısı RUN-BLOCK'unu erken koştur (saat 5.5'te değil, şimdi)
- Sentetik raster ile T5.3 red flag mantığını test et
- WDPA buffer ile sentetik tespit polygon'larını kesişme testi

### Slack 2 (saat 9:30-13:00, 3.5h)
P1 Landsat snapshot saat 13'te teslim edecek.

**Yap:**
- **P3 model export hazırlık:** Streamlit dashboard'a checkpoint loader test et (sentetik checkpoint ile mock)
- **P2 etiket görsel grafik üretimi (HELP→P2):** sınıf dağılımı, augmentation örnekleri, 5-fold blok dağılımı görselleri — bu P2 saat 16'da QC raporu için kullanır
- **Streamlit ön versiyon hazırla:** `dashboard.py` 3 ekran iskelet, mock data ile çalışır olsun
- **OSM Overpass cache:** Goreme + çevre OSM verisini önceden çek, çevrim dışı çalışsın

---

## 7. T5.10 HISTORICAL RAW INFERENCE — KRİTİK (saat 17.5-19)

### Önkoşul (saat 17.5'te)
- ✅ `code/p3/07_inference.py::predict_raw()` (P3 saat 17.5)
- ✅ `data/temporal/landsat_harmonized/` (sen, T5.8 saat 16)

### Akış
```python
# code/p5/08_historical_pomza_inference.py mantığı:
from code.p3.inference import predict_raw

for year in [1985, 1990, 2000, 2010, 2025]:
    landsat_tile = load_landsat(f"data/temporal/landsat_harmonized/L_{year}.tif")
    
    # Landsat 7 bant — model 17 bant bekliyor — bant adapter
    adapted_tile = adapt_landsat_to_17ch(landsat_tile)  # Plan B mock fallback dahili
    
    raw_prob = predict_raw(adapted_tile)
    
    # Historical: füzyon yok (ASTER yok), sabit threshold
    binary_mask = (raw_prob > 0.5).astype(np.uint8)
    
    # Polygon vectorize (alanlar için)
    polygons = vectorize_mask(binary_mask)
    
    save(f"data/temporal/historical_pomza_overlay/pomza_{year}.gpkg", polygons)
```

### Plan B: Landsat 7 bant ≠ S2 17 bant adapter sorunu
- Landsat: B-G-R-NIR-SWIR1-SWIR2 (6 bant)
- Model 17 bant bekliyor (S2 ARD)
- **Çözüm:** `adapt_landsat_to_17ch()` — eksik bantları (S1, DEM) sıfır doldur, ortak bantları S2 eşdeğerine map et
- **Plan B (kalite yetersizse):** BSI threshold mock fallback (`code/p5/08_*.py` dahili) — Sabins-style manuel threshold

---

## 8. T5.13 FINAL ENTEGRASYON — KRİTİK (saat 18-20)

### 5 Katman manifest (`data/layers.json`)

```json
{
  "version": "v2",
  "layers": [
    {
      "name": "S2 RGB Sentinel-2 True Color",
      "path": "data/ard/s2_rgb_2025.tif",
      "type": "raster",
      "owner": "P1",
      "critical": false,
      "color_ramp": "natural"
    },
    {
      "name": "ASTER Quartz Index",
      "path": "data/layers/aster_qi.tif",
      "type": "raster",
      "owner": "P4",
      "critical": false,
      "color_ramp": "spectral"
    },
    {
      "name": "S1 Amplitude Change",
      "path": "data/change/s1_change.tif",
      "type": "raster",
      "owner": "P5",
      "critical": false,
      "color_ramp": "RdBu"
    },
    {
      "name": "UNESCO Goreme Buffer (1000m)",
      "path": "data/labels/wdpa_buffer.gpkg",
      "type": "vector",
      "owner": "P2/P5",
      "critical": false,
      "style": "red outline, semi-transparent fill"
    },
    {
      "name": "Final Confidence (FUSED)",
      "path": "data/layers/final_confidence.tif",
      "type": "raster",
      "owner": "P4",
      "critical": true,
      "color_ramp": "magma"
    }
  ]
}
```

### Streamlit 3 Ekran (`dashboard.py`)

**Ekran 1: Saha Tarama**
- Folium harita (5 katman toggle)
- Saha listesi (P2 polygon → mouse hover → attribute card)
- WDPA red flag (kırmızı çerçeve)

**Ekran 2: AI Analizi**
- Final confidence raster (P4 FUSED)
- RAW prob slider (P3 → kullanıcı threshold ayarlar)
- Grad-CAM overlay (P3 saat 17.5'te teslim edecek)
- Yıl seçici → historical overlay (T5.10 yıllık polygon)

**Ekran 3: Operasyonel Karar**
- KPI tablosu (saha bazında alan, büyüme %, UNESCO ihlal)
- Red flag listesi (UNESCO buffer içine düşen tespit)
- Landsat timelapse GIF
- "Saha export" → CSV/GPKG download

### Plan B (T4.12 saat 20'de bitmediyse)
- Final confidence layer **YOK**
- Yerine: P3 RAW probability + ASTER QI ayrı katmanlar (kullanıcı kafasında çarpsın)
- Demo'da "tam füzyon vizyon slaydında" diyerek geçiştir

---

## 9. T5.15 DRY-RUN — KRİTİK (saat 22-24)

### Dry-run #1 (saat 22-23)
- Streamlit aç, 3 ekran end-to-end test
- Tüm layer'lar yükleniyor mu
- KPI sayısal doğru mu (sample saha ile el hesabı cross-check)
- Performance: ilk render < 30 sn, layer toggle < 2 sn

### Dry-run #2 (saat 23-24)
- **İnternet kesintisi senaryosu**: WiFi kapat, dashboard hala açılıyor mu (offline cache devrede mi)
- P1 saat 16-18 HELP'inde demo offline cache hazırladı (`demo/offline_cache/`) — kontrol et
- Ekran paylaşım: Discord/Zoom screen share testi
- Sunum sırası prova: kim hangi ekranı ne zaman gösterecek

### Plan B
- Streamlit donarsa → `code/p5/12_demo_fallback.py` ile pre-rendered PNG sequence + statik HTML
- WiFi yoksa → Streamlit yerel localhost'ta hala çalışır, sadece OSM tile'ları cache'den (önceden yüklenmiş)

---

## 10. KIM SANA NE TESLİM EDİYOR / SEN KİME NE TESLİM EDİYORSUN

### Sana gelen
| Saat | Girdi | Sağlayıcı | Kullanım |
|---|---|---|---|
| 5.5 | `data/s1_stack/` | P1 | T5.5 amplitude diff |
| 11 | `data/manifest.json` | P1 | CRS/bounds referans |
| 13 | `data/landsat/L*_<year>.tif` | P1 | T5.8 Roy 2016 + GIF |
| **17** | **`data/layers/` (P4 layer'lar)** | **P4** | **T5.9 layer ekleme** |
| **17.5** | **`code/p3/07_inference.py::predict_raw()`** | **P3** | **T5.10 historical (CRITICAL)** |
| 18.5 | `models/unet_pomza_ssl4eo.pt` | P3 | Streamlit canlı inference |
| **20** | **`data/layers/final_confidence.tif` (FUSED)** | **P4** | **T5.13 dashboard ana katman (CRITICAL)** |

### Senden çıkan
| Saat | Çıktı | Tüketici | Kullanım |
|---|---|---|---|
| 16 | `data/temporal/landsat_timelapse.gif` | Demo | Sunum |
| 19 | `data/temporal/historical_pomza_overlay/*.gpkg` | Demo | Yıllık karşılaştırma |
| 20 | `data/layers.json` | Frontend | Dashboard render |
| 20 | `reports/kpi.json` | Demo | KPI tablosu |
| 20 | `code/p5/dashboard.py` (çalışır) | Demo | Streamlit ana giriş |
| 22 | `demo/fallback/` | Demo | Plan B PNG sequence |

---

## 11. PLAN B'LERİN

| Tetikleyici | Plan B | Onay |
|---|---|---|
| **T4.12 saat 20'de bitmedi** | **Dashboard'da RAW + ASTER ayrı katman, FUSED yok** — vizyon slaydında entegre | Eskalasyon |
| **Roy 2016 yavaş** | Basit per-band linear regression fallback (akademik kalite düşer) | Otomatik |
| Landsat tarih bulutlu | 4 yerine 3 snapshot (1990, 2010, 2025) | Otomatik |
| OSM Overpass timeout | Yerel WDPA shapefile + manuel buffer | Otomatik |
| Streamlit saat 20'de bitmedi | T5.14 PNG fallback (`12_demo_fallback.py`) | Eskalasyon |
| Streamlit demo'da donuyor | Cloud deploy (Streamlit Cloud yedek) | Grup chat |
| GIF dosya çok büyük | Frame sayısını azalt (5 yıl yerine 3 yıl), framerate düşür | Otomatik |
| P3 inference Landsat'a uyarlanmıyor | Mock BSI threshold fallback (P5 dahili) | Otomatik |

---

## 12. GITHUB WORKFLOW

```bash
git checkout -b p5-t5.x-<kısa-ad>

git lfs track "data/temporal/*.gif"
git lfs track "data/change/*.tif"
git lfs track "demo/fallback/*.png"

git add code/p5/* agent_outputs/p5_*
git add data/layers.json reports/kpi.json
git add code/p5/dashboard.py
git add demo/fallback/

git commit -m "[P5] T5.13 Final entegrasyon (5 katman dashboard)

DELIVER: code/p5/dashboard.py + data/layers.json + reports/kpi.json
Sanity: 5 katman, 38 saha, UNESCO ihlal 2, 1985-2025 büyüme +320%
Bağımlı: Demo (saat 22-24)"

git push origin p5-t5.x-<kısa-ad>
```

---

## 13. KENDİNİ KONTROL — saat 7.5, 16, 19, 20, 22'de

### Saat 7.5 ✓
- [ ] T5.5 `data/change/s1_change.tif` exists, S1 amplitude difference doğru
- [ ] WDPA Goreme polygon + 1000m buffer hazır

### Saat 16 ✓
- [ ] T5.8 Landsat harmonization + GIF tamam
- [ ] `data/temporal/landsat_timelapse.gif` görsel kontrol (5 frame, 1985-2025)

### Saat 19 ✓ **CRITICAL**
- [ ] T5.10 historical RAW inference 5 yıl için tamam
- [ ] `data/temporal/historical_pomza_overlay/*.gpkg` 5 dosya
- [ ] Yıllık alan büyüme % cross-check makul

### Saat 20 ✓ **CRITICAL**
- [ ] T5.13 final entegrasyon: 5 katman tek dashboard
- [ ] `code/p5/dashboard.py` Streamlit'te çalışıyor
- [ ] `data/layers.json` valid JSON
- [ ] `reports/kpi.json` saha tablosu hazır

### Saat 22 ✓ KOD FREEZE
- [ ] T5.14 PNG fallback `demo/fallback/` 5+ frame hazır
- [ ] Offline mod test edildi

### Saat 24 ✓ DEMO
- [ ] Dry-run #1 #2 başarılı
- [ ] Ekran paylaşımı çalışıyor
- [ ] Sunum sırası belli

---

## 14. DOSYA REFERANSLARIN

| Ne | Nerede |
|---|---|
| Rol tanımı | `.claude/agents/p5-change-detection-viz.md` |
| Görev detay | `Modul_A_Critical_Path_Dependency_v2.md` § P5 |
| Kodlar | `code/p5/` (13 dosya hazır) |
| **Dashboard** | **`code/p5/dashboard.py` (Streamlit ana giriş)** |
| RUN-BLOCK'lar | `agent_outputs/p5_t5_*_runblock.md` |
| Statü | `agent_outputs/p5_status.md` |
| Layer manifest | `data/layers.json` (sen yazacaksın) |
| KPI | `reports/kpi.json` (sen yazacaksın) |

---

## 15. SIK SORULAR

**S: Roy 2016 cross-sensor harmonization neden gerekli?**
C: Landsat-5 TM, Landsat-7 ETM+, Landsat-8 OLI farklı sensör. Spektral hassasiyetleri farklı. Roy 2016 per-band linear regression katsayıları ile harmonize edilir, zaman serisinde tutarlılık sağlanır.

**S: T5.10 historical neden FUSED değil RAW?**
C: ASTER 1985'te yok (ASTER 1999'da fırlatıldı). Kontemporanöz spektral indeks olmadan füzyon yapılamaz. Bu yüzden historical sadece P3 RAW + sabit threshold (0.5) kullanır.

**S: Mazza 2023 S1 amplitude difference nasıl çalışır?**
C: Multi-temporal S1 stack alır, log-ratio (dB) hesaplar, ±3 dB threshold ile binary change map üretir, 3×3 majority filter ile speckle azaltır. Açıklama `code/p5/04_s1_amplitude_diff.py` içinde.

**S: Streamlit Cloud yedek mi?**
C: Evet, yerel demo donarsa cloud'a deploy edilebilir. Ama yerel performansı daha iyi (latency yok). Cloud sadece Plan B.

**S: 5 katman çok değil mi?**
C: Demo için optimize. Ekran 1'de hepsi var ama default'ta sadece 2-3 açık. Kullanıcı toggle eder.

**S: KPI hesabı nasıl?**
C: Her saha (P2 polygon) için final_confidence > 0.5 piksel sayımı × pixel_area = ha. Yıl bazında karşılaştırma → büyüme %. UNESCO ihlal = WDPA buffer ile kesişen polygon sayımı.

**S: GIF kaç saniye sürmeli?**
C: 5 yıl × 1 sn/frame = 5 sn loop. Demo'da otomatik döner.

---

## 16. SENİN BAŞARI KRİTERLERİN

1. ✅ T5.13 saat 20'de 5 katmanlı dashboard çalışıyor
2. ✅ T5.15 saat 24'te dry-run başarılı, demo sırasında crash yok
3. ✅ KPI değerleri sanity geçti (saha alanı, büyüme %, UNESCO ihlal)
4. ✅ Plan B'ye gerek kalmadı (Streamlit performansı iyi, internet sorunu yok)
5. ✅ Sunumda dashboard'u akıcı gezdin

---

## 17. STRATEJİ TÜYÜLERİ

- **Streamlit caching:** `@st.cache_data` ve `@st.cache_resource` kullan, raster'ı her render'da yeniden okuma
- **Folium tile cache:** İnternet sorunu için OSM tile'ları önceden indir (`folium.TileLayer` ile static path)
- **GIF optimization:** `imageio` ile lossy compression, dosya boyut < 5 MB
- **Streamlit theme:** Dark mode demo'da daha profesyonel görünür (`st.set_page_config(layout='wide', page_icon='🪨')`)
- **KPI görsel:** Plotly ile interaktif grafik (saha bazında bar chart, yıllık büyüme line chart)
- **Demo güvenliği:** Saat 22 dry-run'dan önce kahve iç, 5 dk dinlen — temiz kafayla daha iyi yakalarsın bug'ları

---

## 18. SUNUM HAZIRLIK (saat 22-24)

### 5 dakikalık demo akışı
1. **0:00-0:30** — Açılış: "Avanos pomza tespiti, UNESCO Goreme koruma" (1-2 cümle)
2. **0:30-1:30** — Ekran 1 Saha Tarama: "5 katman, 38 saha, kırmızı UNESCO ihlal" (canlı zoom in)
3. **1:30-3:00** — Ekran 2 AI Analizi: "P3 SSL4EO-S12 fine-tune mean IoU 0.52, P4 score-level füzyon, Grad-CAM ile model açıklanabilirliği"
4. **3:00-4:00** — Ekran 3 Operasyonel Karar: "1985-2025 +320% büyüme, 2 UNESCO ihlal, KPI tablosu"
5. **4:00-5:00** — Landsat GIF + kapanış

### Sunumda kim ne anlatacak (5 kişi sırayla 1 dk)
- P1: "Veri pipeline — 17 kanal 20m ARD, 24 saatte üretildi"
- P2: "Etiketleme — Roberts 2017 spatial blok CV, 38 saha"
- P3: "AI — SSL4EO-S12, multi-channel adapter, RAW olasılık"
- P4: "Spektral füzyon — Ninomiya QI × CI, score-level fusion"
- P5: "Dashboard + zaman serisi — Streamlit, Roy 2016, UNESCO red flag"

---

**Saat 0 başladı sayılır. İlk eylemin: 3.1 yerel Python venv + pip install. Bittiğinde grup chat'e "P5 hazır" yaz.**
