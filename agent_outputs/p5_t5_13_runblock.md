# RUN-BLOCK [T5.13] — Final entegrasyon (CRITICAL PATH)

**Bağımlılık:** P4 T4.12 `final_confidence.tif` + P3 T3.10 inference + P1 T1.4 S2 ARD + T5.5/T5.7/T5.10 kendi çıktıların.
**v2 KRİTİK:** Bu görev current state için P4 FUSED `final_confidence.tif`'i ana katman olarak gösterir. Historical (T5.10) ayrı RAW katmanıdır — KARIŞTIRILMAZ.

**Önkoşul (saat 18:00 itibariyle):**
- `data/ard/s2_rgb.tif`              (P1 T1.4)
- `data/ard/aster_qi.tif`            (P4 T4.6)
- `data/ard/final_confidence.tif`    (P4 T4.12)  ← **kritik**
- `data/change/s1_change.tif`        (T5.5)
- `data/aoi/wdpa_goreme_buffer.gpkg` (T5.2)
- `data/temporal/landsat_timelapse.gif` (T5.7)
- `data/temporal/historical_pomza_overlay/` (T5.10)

**Beklenen süre:** 2 saat (saat 18-20 entegrasyon oturumu).

## Akış

```bash
# 1. Manifest üret (5 katman, Plan A/B otomatik karar)
python code/p5/09_layer_manifest.py

# 2. Red flag overlay
python code/p5/03_red_flag_logic.py

# 3. KPI
python code/p5/10_kpi_calc.py

# 4. Streamlit canlı
streamlit run code/p5/dashboard.py
# Tarayıcı: http://localhost:8501
```

## 5-katman doğrulama
1. **S2 RGB** (P1)            — varsayılan görünür, opacity 1.0
2. **ASTER QI** (P4 T4.6)     — varsayılan kapalı, viridis colormap
3. **S1 change** (kendi T5.5) — kategorik (stable/increase/decrease)
4. **UNESCO buffer** (T5.2)   — kırmızı kesik çizgi, 1000 m offset
5. **P4 `final_confidence.tif`** (P4 T4.12) — varsayılan görünür, magma colormap, kritik katman

# VERIFY-BLOCK [T5.13]

Bana yapıştır:
- Streamlit ana ekran screenshot (Sayfa 1: Saha Tarama, 5 layer toggle paneli)
- `data/layers.json` içeriği — `"plan": "A"` olduğunu gör
- `final_confidence.tif` overlay haritada görünüyor mu (heatmap)
- KPI tablosu screenshot (Sayfa 3: Operasyonel Karar)
- UNESCO red flag listesi (Sayfa 3 alt panel)
- Konsol hata? (varsa son 20 satır)

Sanity threshold:
- 5 layer görünür, hepsi tıklanır
- `final_confidence.tif` haritada renkli overlay (boş/şeffaf değil)
- KPI: 1985→2025 büyüme pozitif, UNESCO ihlal sayısı 0-10 arası makul
- Plan == "A" (Plan B'ye düştüyse uyarı bandı görünmeli)

# DELIVER

```
[P5] T5.13 TAMAM
Çıktı: code/p5/dashboard.py + data/layers.json (Plan A) + reports/kpi.json
Sanity: ✅ 5 katman, P4 FUSED final_confidence katman aktif, 1985-2025 büyüme +320%, UNESCO ihlal 2
Sıradaki: T5.14 PNG fallback + T5.15 dry-run
```

## Plan B (P4 T4.12 saat 20'de bitmedi)
- `09_layer_manifest.py` `final_confidence.tif` yokluğunu otomatik tespit eder, Plan B'ye düşer.
- Plan B manifest: P3 RAW (`data/ard/p3_raw_prob.tif`) ana katman, ASTER QI ayrı katman olarak görünür.
- Streamlit'te uyarı bandı: "Plan B aktif — füzyon yok".
- KPI raporunda `notes` alanına "current_layer = P3 RAW (FUSED yok)" eklenir.

## Plan B (Streamlit fail saat 20)
- T5.14 PNG fallback devreye: `python code/p5/12_demo_fallback.py`.
- `demo/fallback/index.html` offline sunulur (dry-run #2 senaryosu).

## Saat 18-20 entegrasyon checklist
- [ ] 18:00 `/data/`, `/models/` klasör doğrulama (Glob)
- [ ] 18:15 `final_confidence.tif` mevcut + projeksiyon EPSG:32636
- [ ] 18:30 P3 inference + P4 fuse_confidence canlı tek-tile testi
- [ ] 18:45 `09_layer_manifest.py` koşar, plan A çıktı
- [ ] 19:00 Streamlit 3 sayfa end-to-end
- [ ] 19:30 KPI sayısal sanity (alan, büyüme, UNESCO)
- [ ] 19:45 Bug listesi → fix sırası
- [ ] 20:00 KOD FREEZE
