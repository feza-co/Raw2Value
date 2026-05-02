# Modül A — Critical Path & Dependency Planı

> **Amaç:** 5 kişinin 24 saat boyunca paralel ilerlerken birbirine girmemesi, kimin ne zaman boş kaldığında nereye yardım edeceği, kritik patikanın hangi görevlerden geçtiği.
>
> **Format:** Görev seviyesinde (mikro-detay yok) ID, sahip, süre, öncül, başlangıç-bitiş saatleri.

---

## 1. GÖREV ENVANTERİ

### P1 — Veri Mühendisi

| ID | Görev | Süre | Öncül | Başlangıç | Bitiş |
|---|---|:-:|:-:|:-:|:-:|
| T1.1 | Ortam kurulumu + GEE auth | 1h | — | 0 | 1 |
| T1.2 | AOI tanımı (Avanos polygon) | 0.5h | T1.1 | 1 | 1.5 |
| T1.3 | Sentinel-2 L2A çekim + bulut maskeleme | 1.5h | T1.2 | 1.5 | 3 |
| **T1.4** | **S2 co-registration → S2 ARD hazır** | **1h** | **T1.3** | **3** | **4** |
| T1.5 | Sentinel-1 GRD çekim + Lee filter | 1.5h | T1.2 | 4 | 5.5 |
| T1.6 | Copernicus DEM çekim + slope türevi | 1h | T1.2 | 5.5 | 6.5 |
| **T1.7** | **Full co-registration → Full ARD hazır** | **1.5h** | **T1.5, T1.6** | **6.5** | **8** |
| T1.8 | Tile splitting (256×256) | 2h | T1.7 | 8 | 10 |
| **T1.9** | **ARD export + manifest** | **1h** | **T1.8** | **10** | **11** |
| T1.10 | Landsat Tier 2 snapshot çekimi (P5 için) | 2h | T1.1 | 11 | 13 |
| T1.11 | QC raporu | 1h | T1.9 | 13 | 14 |
| **HELP→P2** | P2'ye etiketleme hızlandırma desteği | 2h | T1.11 | 14 | 16 |
| **HELP→P5** | P5'e demo offline cache + frontend desteği | 2h | — | 16 | 18 |
| T1.14 | Entegrasyon oturumu | 2h | tüm öncüller | 18 | 20 |
| T1.15 | KOD FREEZE + dry-run desteği | 4h | T1.14 | 20 | 24 |

### P2 — Etiketleme Lead

| ID | Görev | Süre | Öncül | Başlangıç | Bitiş |
|---|---|:-:|:-:|:-:|:-:|
| T2.1 | QGIS kurulumu + S2 RGB altlık | 1h | — | 0 | 1 |
| T2.2 | MAPEG sorgu + üretici saha doğrulama | 2h | T2.1 | 1 | 3 |
| **T2.3** | **Manuel pozitif poligon çizimi (30-40 saha)** | **4h** | **T2.2** | **3** | **7** |
| T2.4 | Manuel negatif poligon çizimi (100-150) | 2h | T2.3 | 7 | 9 |
| T2.5 | WDPA Göreme buffer + etiket dışı maske | 1h | T2.4 | 9 | 10 |
| T2.6 | Mekânsal train/val/test split | 1h | T2.5 | 10 | 11 |
| **T2.7** | **Raster mask üretimi → Full label hazır** | **2h** | **T2.6, T1.8** | **11** | **13** |
| T2.8 | Augmentation pipeline | 1h | T2.7 | 13 | 14 |
| T2.9 | P3 ile DataLoader entegrasyon test | 2h | T2.8, T3.3 | 14 | 16 |
| T2.10 | Etiket QC raporu | 1h | T2.9 | 16 | 17 |
| T2.11 | P3 inference sonuçlarıyla hata analizi | 1.5h | T3.10 | 17 | 18.5 |
| **HELP→P5** | P5'e KPI hesabı yardım | 1.5h | T2.11 | 18.5 | 20 |
| T2.13 | Entegrasyon oturumu | 2h | tüm öncüller | 18 | 20 |
| T2.14 | KOD FREEZE + dry-run desteği | 4h | T2.13 | 20 | 24 |

### P3 — ML Mühendisi

| ID | Görev | Süre | Öncül | Başlangıç | Bitiş |
|---|---|:-:|:-:|:-:|:-:|
| T3.1 | Ortam kurulumu + GPU testi | 2h | — | 0 | 2 |
| T3.2 | Pretrained yükleme + multi-channel adapter | 2h | T3.1 | 2 | 4 |
| T3.3 | Loss + DataModule + sentetik veri sanity check | 2h | T3.2 | 4 | 6 |
| T3.4 | Bekleme/hazırlık (P1 ARD + P2 etiket gelmesi) | 1h | T1.9, T2.3 | 11 | 12 |
| **T3.5** | **Fine-tune** | **3h** | **T3.4, T2.7** | **12** | **15** |
| T3.6 | Threshold tuning + metric raporu | 1h | T3.5 | 15 | 16 |
| T3.7 | Ablation study (5 konfig) | 1.5h | T3.5 | 15 | 16.5 |
| **T3.10** | **Inference function** | **1h** | **T3.6** | **16.5** | **17.5** |
| T3.11 | Grad-CAM görselleştirme | 1h | T3.10 | 17.5 | 18.5 |
| T3.12 | P2 ile hata analizi (gerekirse 2. tur) | 1.5h | T3.11 | 18.5 | 20 |
| T3.13 | Model export + P5 entegrasyon | 2h | T3.12 | 18 | 20 |
| T3.14 | KOD FREEZE + FP16 + dry-run | 4h | T3.13 | 20 | 24 |

> **Not P3:** T3.1-T3.3 (saat 0-6) kendi başına ilerler. Saat 6-11 arası **slack zamanı** (P1+P2'yi bekler) — bu sürede `inference.py` boilerplate ve Grad-CAM yardımcı kodları yazılır. Saat 11'de gerçek veri gelir, fine-tune başlar.

### P4 — Spektral Mühendis

| ID | Görev | Süre | Öncül | Başlangıç | Bitiş |
|---|---|:-:|:-:|:-:|:-:|
| T4.1 | Ortam kurulumu + Earthdata token | 1h | — | 0 | 1 |
| T4.2 | ASTER L1B Avanos sahnesi indirme | 2h | T4.1 | 1 | 3 |
| T4.3 | ASTER L1B → L2 atmosferik düzeltme | 2h | T4.2 | 3 | 5 |
| T4.4 | Bekleme (P1 S2 ARD için kısa) | 0h | T1.4 | 4 | 4 |
| T4.5 | Sentinel-2 türetilmiş indeksler (NDVI/BSI/Albedo/Sabins) | 2h | T1.4 | 5 | 7 |
| **T4.6** | **ASTER Ninomiya indeksleri (QI/SiO₂/CI)** | **2h** | **T4.3** | **7** | **9** |
| T4.7 | ASTER 90m → S2 10m resample | 1h | T4.6 | 9 | 10 |
| T4.8 | Score-level füzyon prototipi | 2h | T4.7 | 10 | 12 |
| T4.9 | DEM aspect + hillshade | 1h | T1.7 | 12 | 13 |
| T4.10 | Hyperspectral Tier 2 görsel kanıt | 2h | — | 13 | 15 |
| T4.11 | Layer-bazlı GeoTIFF export | 2h | T4.5, T4.6, T4.9 | 15 | 17 |
| T4.12 | Layer dokümantasyonu | 1h | T4.11 | 17 | 18 |
| **T4.13** | **P3 ile entegrasyon: U-Net × QI füzyon canlı** | **2h** | **T3.10, T4.11** | **18** | **20** |
| T4.14 | KOD FREEZE + dry-run | 4h | T4.13 | 20 | 24 |

### P5 — Change Detection + UNESCO Overlay + Visualization

| ID | Görev | Süre | Öncül | Başlangıç | Bitiş |
|---|---|:-:|:-:|:-:|:-:|
| T5.1 | Ortam kurulumu (folium, leafmap, shapely, imageio) | 1h | — | 0 | 1 |
| T5.2 | WDPA Göreme polygon + 1000m buffer + OSM cross-check | 1h | T5.1 | 1 | 2 |
| T5.3 | Red flag overlay logic prototipi (sentetik veri) | 1h | T5.2 | 2 | 3 |
| T5.4 | Bekleme (P1 S1 stack için) | — | T1.5 | 3 | 5.5 |
| **T5.5** | **Sentinel-1 amplitude difference change detection** | **2h** | **T1.5** | **5.5** | **7.5** |
| T5.6 | Folium harita altyapısı + baselayer | 2h | T5.3 | 7.5 | 9.5 |
| T5.7 | Landsat 1985→2025 snapshot işleme + animasyon GIF | 2.5h | T1.10 | 13 | 15.5 |
| **T5.8** | **Landsat snapshots üzerinde pomza tespiti (P3 inference fn ile)** | **1.5h** | **T3.10, T5.7** | **17.5** | **19** |
| T5.9 | Yıllık alan büyüme % hesabı | 1h | T5.8 | 19 | 20 |
| T5.10 | Layer ekleme (S2 RGB, U-Net olasılık, ASTER QI, S1 change, UNESCO buffer, GIF) | 2h | T5.5, T4.11 | 15.5 | 17.5 |
| T5.11 | KPI hesaplama (saha bazında alan, büyüme, UNESCO ihlali) | 1h | T5.9 | 19 | 20 |
| T5.12 | Streamlit dashboard entegrasyonu | 2h | T5.10 | 18 | 20 |
| **T5.13** | **Final entegrasyon — manifest + 4 kişinin çıktısı tek dashboard** | **2h** | **T1.14, T2.13, T3.13, T4.13** | **18** | **20** |
| T5.14 | Demo backup PNG fallback | 2h | T5.12 | 20 | 22 |
| T5.15 | Dry-run #1 #2 + ekran-paylaşım testi | 2h | T5.14 | 22 | 24 |

> **Not P5:** Saat 3-5.5 (P1 S1 stack beklerken) ve saat 9.5-13 (P1 Landsat beklerken) **iki bekleme penceresi var**. İlk pencere T5.6 Folium altyapısına çekilir; ikinci pencere için aşağıdaki Help Slot tablosuna bak.

---

## 2. CRITICAL PATH

> En uzun bağımlılık zinciri — bu zincirde herhangi bir görev gecikirse tüm Modül A geç teslim edilir.

```
T1.3 ──→ T1.4 ──→ T1.5 ──→ T1.6 ──→ T1.7 ──→ T1.8 ──→ T1.9 ──→ T3.4 ──→ T3.5
[S2]    [S2 ARD] [S1]     [DEM]    [Full]   [Tile]   [Export] [Wait]   [Fine-tune]
1.5h     1h      1.5h     1h       1.5h     2h       1h       1h       3h

   ──→ T3.6 ──→ T3.10 ──→ T5.8 ──→ T5.11 ──→ T5.13 ──→ T5.15
       [Tune]  [Infer]    [Time-  [KPI]    [Final]   [Dry-run]
                          series]
       1h     1h           1.5h    1h        2h         2h

TOPLAM: ~21.5h (24 saat penceresi içinde 2.5h slack)
```

**Critical path görevleri (kalın):**
- **T1.3, T1.4, T1.7, T1.9** — P1'in ARD üretim zinciri
- **T3.5, T3.10** — P3'ün eğitim ve inference
- **T5.8, T5.11, T5.13** — P5'in change detection + entegrasyon

**Critical olmayan (slack'i olan) görevler:**
- P2'nin tüm görevleri (kendi içinde sıralı, ama T2.7 saat 13'te bittiğinde T3.5 zaten ARD bekliyordu)
- P4'ün tüm görevleri (paralel rota — saat 18'de buluşuyor)
- T1.10 (Landsat) — P5'in T5.7'sinde kullanılıyor ama saat 13'te yetiştiği için kritik değil
- T3.7 ablation, T3.11 Grad-CAM, T3.12 hata analizi

---

## 3. DEPENDENCY TABLOSU (KİM → KİM)

| Sağlayıcı | Çıktı | Zaman | Tüketici | Kullanım |
|:-:|---|:-:|:-:|---|
| P1 | S2 ARD (S2-only versiyon) | 4 | P4 | Türetilmiş indeksler için S2 bantları |
| P1 | Full ARD (17 kanal) | 8 | P3 | Fine-tune girdi tensörü |
| P1 | Tile dosyaları | 10 | P3 + P2 | DataLoader |
| P1 | ARD manifest JSON | 11 | P3 + P4 + P5 | Bant bilgisi, CRS, bounds |
| P1 | Landsat Tier 2 snapshot | 13 | P5 | Zaman serisi GIF + her snapshot için pomza tespiti |
| P2 | Pozitif poligon (ön-versiyon) | 7 | P3 | Erken sanity check fine-tune |
| P2 | Full label raster mask | 13 | P3 | Asıl fine-tune |
| P2 | Train/val/test split | 13 | P3 | DataLoader split |
| P3 | Inference function | 17.5 | P5 + P4 | Landsat snapshots üzerinde pomza tespiti, score-level füzyon test |
| P3 | Model checkpoint | 18.5 | P5 | Streamlit canlı inference |
| P4 | ASTER QI raster | 9 | P3 | Score-level füzyon ağırlığı (post-process) |
| P4 | Türetilmiş indeks layer'ları | 17 | P5 | Folium harita layer ekleme |
| P4 | Score-level füzyon `fuse_confidence()` | 20 | P5 | Final pomza güven raster'ı |
| P5 | Folium manifest (layers.json) | 20 | Frontend takımı | Streamlit dashboard render |
| P5 | UNESCO buffer overlay | 2 | (kendi içi) | Red flag logic |

---

## 4. SLACK & HELP SLOT TABLOSU

> 5 kişinin birbirine girmemesi + kimsenin boş kalmaması için **kim ne zaman müsait → kime/neye yardım eder**.

| Kişi | Boş Kalan Zaman | Niye Boş | Yapacağı Yardım |
|:-:|:-:|---|---|
| **P1** | 14-16 (2h) | T1.11 QC bitti, entegrasyona kadar 4h slack | **P2'ye etiketleme hızlandırma** — T2.9 DataLoader entegrasyon test desteği veya henüz çizilmemiş 5-10 ek negatif poligon |
| **P1** | 16-18 (2h) | Aynı slack | **P5'e demo offline cache + Streamlit performans testi** — internet kesilirse fallback sahnesinin doğru yüklenmesi |
| **P2** | 13-14 (1h) | T2.7 raster mask bitti, T2.8 augmentation kısa | **P3'e DataLoader sanity check** — etiket dosyasının PyTorch tarafında doğru okunduğu doğrulama |
| **P2** | 18.5-20 (1.5h) | T2.11 hata analizi bitti | **P5'e KPI hesabı yardım** — saha bazında alan/büyüme tablosu manuel doğrulama |
| **P3** | 6-11 (5h) | T3.3 sanity check bitti, P1 ARD ve P2 etiket bekliyor | **Inference fn iskelet kodu + Grad-CAM hazırlık** (kendi alanında çalışmaya devam) — bu görev T3.10 ve T3.11'i kısaltır |
| **P3** | 16.5-17.5 (1h) | T3.10 inference yazıldıktan sonra T5.8 öncesi | **P4 ile score-level füzyon entegrasyonu** — U-Net çıktısının QI ile çarpımı doğru sonuç veriyor mu |
| **P4** | 13-15 (2h) | T4.10 hyperspectral görsel kısa | **P5'e Folium layer ekleme** — ASTER QI katmanının harita üzerinde doğru render edilmesi |
| **P4** | 17-18 (1h) | T4.12 dokümantasyon bitti | **P3 entegrasyon hazırlığı** — `fuse_confidence()` API'sinin P3'ün inference fn'ini sarmalaması |
| **P5** | 9.5-13 (3.5h) | T5.6 Folium altyapısı bitti, P1 Landsat bekliyor | **P3 model export hazırlığı** — model checkpoint'in Streamlit içine yüklendiği test (P3 model bitince hızlı entegre) **VE/VEYA** P2'ye etiket QC görsel grafik üretimi (sınıf dağılımı, augmentation örnekleri) |

### Help Slot Görselleştirme (Saat × Kişi)

```
Saat:    0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
P1   :   ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓  ▓  ▓  ▓  ▓  H₂ H₂ H₅ H₅ ▓  ▓  ▓  ▓  ▓  ▓  ▓
P2   :   ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓  ▓  ▓  ▓  H₃ ▓  ▓  ▓  ▓  H₅ H₅ ▓  ▓  ▓  ▓  ▓
P3   :   ▓ ▓ ▓ ▓ ▓ ▓ s s s s  s  ▓  ▓  ▓  ▓  ▓  ▓  H₄ ▓  ▓  ▓  ▓  ▓  ▓  ▓
P4   :   ▓ ▓ ▓ ▓ . ▓ ▓ ▓ ▓ ▓  ▓  ▓  ▓  H₅ H₅ ▓  ▓  H₃ ▓  ▓  ▓  ▓  ▓  ▓  ▓
P5   :   ▓ ▓ ▓ . . . ▓ ▓ ▓ s  s  s  s  ▓  ▓  ▓  ▓  ▓  ▓  ▓  ▓  ▓  ▓  ▓  ▓

▓ = aktif kendi görevi   .  = kısa pasif bekleme   s = slack (kendi alanında devam)
H₂ = P2'ye yardım        H₃ = P3'e yardım          H₄ = P4'e yardım   H₅ = P5'e yardım
```

---

## 5. ENTEGRASYON OTURUMU — SAAT 18-20

5 kişi aynı odada/Discord kanalında, **kollektif** çalışır. Bireysel slot değil, ortak entegrasyon.

| Saat | Etkinlik |
|:-:|---|
| 18:00 | Tüm çıktılar `/data/` ve `/models/` klasörlerinde olduğunun doğrulanması |
| 18:15 | P1 → `run_pipeline.sh` tek tıkla koşuyor mu |
| 18:30 | P3 inference fn + P4 fuse_confidence() canlı test (1 tile) |
| 18:45 | P5 Folium harita 4 kişinin çıktısını birleştirebilmiş mi |
| 19:00 | Streamlit 3 ekran akışı end-to-end (Saha Tarama → AI Analizi → Operasyonel Karar slot'u) |
| 19:30 | KPI değerleri makul mu (sayısal sanity) |
| 19:45 | Bug listesi → KOD FREEZE öncesi son fix sırası |
| 20:00 | **KOD FREEZE** |

---

## 6. RİSK PATH (Critical Path Patlarsa Plan B)

| Risk | Etkilenen Görev | Plan B |
|---|:-:|---|
| P1 S2 sahnesi bulutlu, T1.3 saat 3'te bitmez | T1.4, T1.7, tüm critical path | Pre-cache temiz tile fallback (hackathon öncesi indirilmiş); 30 dk gecikme kabul edilebilir |
| P2 pozitif poligon T2.3 saat 7'de bitmez (yavaş etiketleme) | T2.7, T3.5 | P1 saat 14'te zaten yardıma geliyor (HELP→P2); 5-10 ek poligon birlikte tamamlanır |
| P3 fine-tune T3.5 yakınsamıyor | T3.10, T5.8, T5.13 | (a) Sade konfigürasyon (S2 RGB-only) ile minimum baseline çalıştır; (b) Manuel threshold-based segmentasyon (B11/B12 + albedo eşik) fallback |
| P3 T3.10 inference fn saat 17.5'te bitmez | T5.8 | P5 Landsat snapshots üzerinde sadece manuel polygon overlay ile devam (alan büyüme tahmini elle) |
| P4 ASTER L1B düzeltme T4.3 başarısız | T4.6, T4.13 | L1T (radiance) ile devam — Ninomiya QI relatif ölçüm, mutlak gerekmez |
| P5 Streamlit T5.12 saat 20'de bitmez | T5.13, demo | Pre-rendered statik PNG fallback (T5.14) — canlı Folium yerine PNG sequence |

---

## 7. ÖZET KURAL SETİ

1. **Critical path (T1.3 → T1.4 → T1.7 → T1.9 → T3.5 → T3.10 → T5.8 → T5.11 → T5.13 → T5.15) gecikmeyecek.** P1, P3, P5'in bu görevlerinde slack yok.
2. **P2 ve P4 paralel rotada — saat 18'de buluşurlar.** Bireysel gecikmeleri kendi rotalarında telafi edilebilir.
3. **Slack zamanları boş kalmayacak.** Yukarıdaki Help Slot tablosuna göre çalışılır.
4. **Saat 18:00 entegrasyon başlangıcına kadar herkes kendi `/data/` klasör formatında dosya teslim etmiş olacak.**
5. **Saat 20:00 KOD FREEZE.** Sonrası sadece dry-run, demo backup, sunum prova.

---

*Hazırlama tarihi: 1 Mayıs 2026*
*Kapsam: Modül A — 5 kişilik paralel akış için critical path & dependency planı*
*Bağlı dosyalar: Modul_A_Development_Rol_Dagitimi.md (görev detayları)*
