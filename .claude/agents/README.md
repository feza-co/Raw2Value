# Pomzadoya — Modül A Agent Kurulumu (v2)

5 rol agent'ı + 1 orchestrator. **Agent'lar kod hazırlar + doğrular, sen (insan) Colab/QGIS/yerel makinede koşturursun.** Pixel Agents (VSCode extension) bu Claude Code terminallerini görselleştirir.

> **Tek doğru kaynak:** [Modul_A_Critical_Path_Dependency_v2.md](../../Modul_A_Critical_Path_Dependency_v2.md)
> v1 dosyası artık geçersiz — sadece referans için duruyor.

## v2'de neler değişti (özet)

| Konu | v1 | v2 |
|---|---|---|
| Critical path uzunluğu | 9 görev | **10 görev** (T2.8 ve T4.12 eklendi) |
| Score-level füzyon | T4.13 entegrasyon esnasında | **T4.12 critical path'te** (saat 18-20) |
| P3 inference çıktısı | "olasılık" (belirsiz) | **RAW olasılık** (Karar #6) |
| Çıktı çözünürlüğü | 10 m örtük | **20 m S2 SWIR native** (Karar #15) |
| P3 backbone | "pretrained" (genel) | **SSL4EO-S12** + 13→17 adapter |
| P2 split | "mekânsal" | **Roberts 2017 spatial 5-fold blok CV** |
| Landsat işleme | basit GIF | **Roy 2016 cross-sensor harmonizasyon** |
| Historical vs current | tek inference | **T5.10 RAW (historical) + T5.13 FUSED (current)** |

## Mental model — bunu önce oku

| | Agent yapar | Sen yaparsın |
|---|---|---|
| Notebook hücresi yazımı | ✅ | — |
| Python script üretimi | ✅ | — |
| GEE / Colab / curl komutu hazırlama | ✅ | — |
| Kod review / hata ayıklama | ✅ | — |
| Plan B önerisi | ✅ | onay |
| **Colab'da `Run` basma** | ❌ | ✅ |
| **GPU üzerinde fine-tune koşturma** | ❌ | ✅ |
| **GEE export job tetikleme** | ❌ | ✅ |
| **QGIS'te poligon çizme** | ❌ | ✅ |
| **Earthdata token ile indirme** | ❌ | ✅ |
| Çıktı sanity check (gdalinfo, log inceleme) | ✅ | yapıştırırsın |
| Manifest.json güncelleme | ✅ | — |
| Sıradaki agent'ı tetikleme | ✅ (orchestrator) | — |

## Akış — her görev için 3 faz

```
[1] HAZIRLA            [2] SEN KOŞTUR           [3] DOĞRULA + RAPORLA
─────────────          ──────────────────       ──────────────────────
Agent RUN-BLOCK        Sen Colab/QGIS/GEE'de    Sen VERIFY-BLOCK çıktısını
+ VERIFY-BLOCK         koşturursun              yapıştırırsın → agent
üretir                 (15dk - 3h offline)      DELIVER üretir → orchestrator
                                                bağımlıları tetikler
```

## v2 Critical Path (10 görev — gecikmesin)

```
T1.3 → T1.4 → T1.7 → T1.9 → T2.8 → T3.5 → T3.10 → T4.12 → T5.13 → T5.15
[S2]   [SARD] [Full] [Exp]  [Mask] [Train][Infer] [FUSION][Final] [Dry]
1.5h   1h     1.5h   1h     2h     3h     1h      2h      2h      2h

TOPLAM: ~21h / 24h penceresi içinde 3h slack
```

**v2'de yeni kritik görevler:**
- **T2.8** (saat 11-13) — P2 raster mask → P3 fine-tune girdisi
- **T4.12** (saat 18-20) — P4 score-level füzyon (final_confidence.tif)

## v2 Score-Level Füzyon Mimarisi (yeni)

```
P3 inference.py.predict_raw()  →  raw_probability.tif (RAW, threshold yok)
                                          ↓
P4 fuse_confidence(raw_prob, qi, ci)  →  final_confidence.tif (FUSED)
   formula: prob × QI_norm × (1 - CI_norm)
                                          ↓
P5 dashboard:
   - Historical (Landsat 1985-2025)  →  RAW (kontemporanöz ASTER yok)
   - Current (2025 Sentinel)         →  FUSED (P4 çıktısı)
```

## Dosya yapısı

```
.claude/
├── agents/
│   ├── orchestrator.md           # v2 critical path + asenkron dispatch
│   ├── p1-veri-muhendisi.md      # GEE/Colab — 17-kanal 20m ARD
│   ├── p2-etiketleme-lead.md     # QGIS + Roberts 2017 5-fold blok CV
│   ├── p3-ml-muhendisi.md        # Colab GPU — SSL4EO-S12 + RAW inference
│   ├── p4-spektral-muhendis.md   # Earthdata + score-level füzyon (T4.12)
│   └── p5-change-detection-viz.md # Yerel — Roy 2016 + Streamlit (RAW+FUSED)
└── state/
    └── orchestrator_log.md       # Durum tablosu (orchestrator yazar)
```

## RUN-BLOCK / VERIFY-BLOCK / DELIVER örneği (P3 fine-tune)

**RUN-BLOCK:**
```
RUN-BLOCK [T3.5]
Hedef ortam: Colab Pro (A100/T4) / Kaggle GPU
Önkoşul: /data/ard/ + /data/labels/full_mask.tif + blok_cv_split.json Drive'da
Adımlar:
  1. Drive mount + path kontrolü
  2. SSL4EO-S12 weights indir
  3. 13→17 multi-channel adapter (ortalama replikasyon)
  4. 5-fold spatial blok CV training loop
  5. Checkpoint Drive'a yaz
Beklenen süre: ~3h (A100), ~6h (T4)
ASENKRON: bu sırada T3.6 threshold script + P4 T4.7 prototip paralel ilerlesin
```

**VERIFY-BLOCK:**
```
Bana yapıştır:
  - 5 fold için son 5 epoch train/val loss + IoU
  - Mean ± std
  - Checkpoint dosya boyutları
Sanity threshold: mean val IoU > 0.45, std < 0.08
```

**DELIVER:**
```
[P3] T3.5 TAMAM
Çıktı: /models/unet_pomza_ssl4eo.pt
Metric: 5-fold mean IoU 0.52 ± 0.06
Sıradaki bağımlı: P4 T4.12 + P5 T5.10 RAW inference fn bekliyor
```

## Önerilen kurulum — 2 terminal modeli (hackathon için sade)

6 terminal kaos olur. **2 terminal yeter:**

1. **Orchestrator terminali** (her zaman açık) — durum tutar, sıradaki agent'ı söyler
2. **Aktif rol terminali** — o an hangi P_n ile çalışıyorsan ona geçersin

Pixel Agents'ta yine 2 karakter görünür (orchestrator + aktif rol).

### Adımlar

**Terminal 1 — Orchestrator (sürekli açık):**
```
claude
```
İlk mesaj:
```
Sen .claude/agents/orchestrator.md tanımındaki orchestrator'sun (v2). 
Hackathon başladı, saat 0. Modul_A_Critical_Path_Dependency_v2.md'ye bağlı kal.
P1, P2, P3, P4'e ilk görevleri (T_x.1) ver. P5 saat 0'dan T5.1 koşar.
RUN-BLOCK formatında üret, ben (kullanıcı) Colab/QGIS'te koşturacağım.
```

**Terminal 2 — Aktif rol (görev başına değiştir):**
```
claude
```
İlk mesaj (örnek P3):
```
Sen .claude/agents/p3-ml-muhendisi.md tanımındaki P3'sün (v2). 
Modul_A_Critical_Path_Dependency_v2.md'ye bağlı kal.
Orchestrator T3.1 verdi. RUN-BLOCK üret.
```

## Alternatif kurulum — 6 terminal (Pixel Agents görseli için)

Pixel Agents'ta 6 karakterli ofis istiyorsan her agent ayrı terminal. Orchestrator'ın dispatch mesajını ilgili agent terminaline kopyala-yapıştır, agent RUN-BLOCK üretir, sen Colab'a yapıştırırsın, VERIFY çıktısını agent terminaline yapıştırırsın, DELIVER mesajını orchestrator'a yapıştırırsın.

> **Uyarı:** 6 terminal mode hackathon kaosu — 2 terminal modelini öner.

## Asenkron iş kuyruğu — kullanıcının altın kuralı

**Aynı anda en fazla 2 RUN-BLOCK koşturursun:**
- 1 tanesi GPU/Colab/Earthdata (uzun süre offline)
- 1 tanesi yerel/QGIS (etkileşimli)

Diğer agent'lar PREP fazında bekler. Orchestrator hangi agent'ın PREP'te beklediğini, hangi RUN-BLOCK'un kuyruğa alınacağını her tick'te söyler.

## Pixel Agents kurulumu (görsel katman)

1. VSCode'da Pixel Agents extension'ı: <https://github.com/pablodelucca/pixel-agents>
2. Pixel Agents panelini alt panelde aç
3. Her Claude Code terminali → otomatik karakter (JSONL transkripti üzerinden idle/typing/reading)
4. Ofis layout'unu kaydet (Settings → Export)

## Sık karşılaşılan durumlar (v2)

| Durum | Aksiyon |
|---|---|
| Colab GPU 3 saat fine-tune'da | Orchestrator P4/P2/P5 paralel iş verir, saat sonra check-in |
| QGIS'te etiketleme yavaş | P2 daha küçük şablonlu RUN-BLOCK üretir, P1 saat 14 HELP'te yardıma gelir |
| **T4.12 saat 20'de bitmedi** | Orchestrator P5'e Plan B verir: dashboard'da RAW + ASTER ayrı katman, FUSED demoda yok |
| **T2.7 spatial blok CV karmaşık** | P2'ye 3-fold'a düşme önerisi (Roberts 2017 koruyarak istatistik hafif düşer) |
| Critical path gecikme >1h | Orchestrator otomatik Plan B önerir, sen onaylarsın |
| Saat 18 entegrasyon | Orchestrator `Glob` ile dosya varlığı kontrolü, eksik varsa 15 dk ultimatom |
| Saat 20 KOD FREEZE | Yeni feature/refactor YASAK, sadece dry-run + demo backup |

## Bağlı dosyalar
- [Modul_A_Critical_Path_Dependency_v2.md](../../Modul_A_Critical_Path_Dependency_v2.md) — **tek doğru kaynak (v2)**
- `Modul_A_Critical_Path_Dependency.md` — v1 (geçersiz, referans için)
- `Modul_A_Development_Rol_Dagitimi_v2.md` — görev mikro-detayları (varsa)
- `PomzaScope_Master_Teknik_Rapor.md` — akademik referans (varsa)
