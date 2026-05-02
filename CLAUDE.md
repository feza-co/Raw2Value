# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: Raw2Value AI

Karar destek motoru — Kapadokya'daki 3 hammaddeyi (pomza, perlit, kabak çekirdeği) işleyip ihraç etmek için en kârlı rota, beklenen kâr (TRY), CO₂ ve alıcı eşleşmesini öneren ML pipeline. Hackathon (Kapadokya 2026) projesi.

**Single source of truth:** `data/master/raw2value_v4.xlsx` (16 sheet) → `models/` (joblib + JSON) → `raw2value_ml/` (Python paketi) → backend `from raw2value_ml import analyze`.

**Detailed status & contract:** `docs/STATUS_REPORT_ML_TESLIM.md`. Master training spec: `docs/master_model_egitim_raporu.md` (referans, 13 ADIM).

## Komutlar

Tüm komutlar repo kökünde çalıştırılır.

| Görev | Komut |
|---|---|
| Kurulum | `pip install -e .` (Python ==3.11.* zorunlu) |
| Tüm testler | `python -m pytest ml/tests/ -v` |
| Tek test dosyası | `python -m pytest ml/tests/test_no_target_leakage.py -v` |
| Tek test fonksiyonu | `python -m pytest ml/tests/test_scorer.py::test_low_carbon_profile_prefers_low_co2 -v` |
| ETL (Excel→parquet) | `python -m ml.src.etl --xlsx data/master/raw2value_v4.xlsx --out data/reference/` |
| Evidence + metadata regen | `python -m ml.src.evidence` |
| Tam pipeline (POSIX) | `bash scripts/run_full_pipeline.sh` |
| Tam pipeline (Windows) | `pwsh scripts/run_full_pipeline.ps1` |
| Smoke API | `python -c "from raw2value_ml import analyze, AnalyzePayload, LiveFx; ..."` |

Ortam: Windows + PowerShell (Bash de mevcut). `&&` PowerShell'de yok — `; if ($?) { ... }` veya ayrı çağrılar kullanın.

## Mimari (büyük resim)

İki katmanlı: **`ml/`** (eğitim — notebook + src) ve **`raw2value_ml/`** (inference — backend'in import edeceği paket). Veri akışı tek yönlü:

```
data/master/raw2value_v4.xlsx
    │ ml/src/etl.py
    ▼
data/reference/*.parquet (12 dosya) + distance_lookup.pkl
    │ ml/src/augmentation.py + targets.py + features.py
    ▼
data/processed/training_set_v1.parquet (1500 row, 45 col)
    │ ml/src/{baselines,train_profit,train_route,ablation}.py
    ▼
models/{model_profit,model_route,feature_pipeline}.pkl  (gitignored)
models/{metadata,model_evidence}.json                    (committed)
data/processed/{baseline,gbm,ablation}_results.json     (committed)
data/processed/feature_medians.json                     (committed)
    │ raw2value_ml/inference.py (analyze)
    ▼
Backend: from raw2value_ml import analyze
```

### `raw2value_ml/` paket modülleri

| Modül | Sorumluluk |
|---|---|
| `inference.analyze(payload)` | TEK giriş noktası. Lazy load → defaults → geo + carbon + fx → Model 2 (route top-3) → Model 1 (profit per route) → match_buyers → reasons + confidence → `AnalyzeResponse` |
| `schemas.py` | Pydantic v2 sözleşmesi (9 model). `AnalyzePayload` ve `AnalyzeResponse` sabittir — backend buna güvenir. |
| `scorer.py` | Deterministik B2B match (eğitilmemiş). 3 ağırlık profili: `max_profit`, `low_carbon`, `fast_delivery`. 6 component (profit, demand, distance, carbon, delivery, quality), her profil sum=1.0. |
| `reasons.py` | 15 Türkçe template, median-based high/low branching, top-3 reason. `_load_medians()` `data/processed/feature_medians.json`'dan okur. |
| `confidence.py` | data + model + overall (40/60 ağırlık) + warnings list. |
| `geo.py` | `lookup_distance()` parquet → Haversine fallback (K3 zorunlu, ORS'tan bağımsız). `find_nearby_processors()` radius_km + material filter. ASCII-fold ile cp1254-mangled Turkish karakterler için defansif. |
| `carbon.py` | Hackathon-resmi sabit faktörler (K1): kara=0.100, deniz=0.015, hava=0.500, demiryolu=0.030 kg CO₂/ton-km. |
| `fx.py` | What-if senaryo aplayıcı (TCMB_LIVE source tag). |
| `reference_loader.py` | 10 `@lru_cache` parquet loader. Carbon mode mapping: `road_truck_HGV→kara`, `sea_container→deniz`, `air_freight_long_haul→hava`, `rail_freight→demiryolu`. |

### Modeller — kontrat ayrıntıları

- **Profit (Model 1):** CatBoostRegressor, 39 feature, target=`expected_profit_try`. Native categorical (one-hot YOK). Best by RMSE 11.2M (vs RF 25.7M).
- **Route (Model 2):** CatBoostClassifier, 39 feature, target=`recommended_route_label`. **10 trained sınıf, 15 known.** `metadata.models.route.missing_classes_in_trained_model` 5 eksik sınıfı listeler. Best by macro-F1 0.78.
- **`feature_pipeline.pkl`** sklearn ColumnTransformer'dır ama **inference'ta KULLANILMAZ** — sadece XGB/LGBM benchmark'ı için fit edilmişti. CatBoost direkt raw `pd.DataFrame[M1_FEATURES]` alır.

## ZORUNLU İlkeler

### Target leakage — sıfır tolerans
`expected_profit_try`, `value_uplift_pct`, `recommended_route_label`, `match_score` **HİÇBİR modelde input feature değil.** `processing_route_candidate` Model 1'de input (rota verili → kâr tahmini), Model 2'de target. `ml/tests/test_no_target_leakage.py` 14 test ile bu kuralı kilitler — feature listesini değiştirirken kırılmamalı.

### Reproducibility — `random_seed = 42`
Numpy `default_rng(42)`, sklearn, xgboost, lightgbm, catboost, train_test_split — hepsi 42. `np.random.seed` (legacy) **kullanmayın** — `np.random.default_rng(seed)` ile rng nesnesini tüm sub-fonksiyonlara geçirin.

### Kural uyumu (rapor §13.5)
- **K1 (Karbon):** sabit hackathon faktörleri (yukarıda). `compute_co2 = tonnage × distance × emission_factor`. `np.random.uniform` ile asla CO₂ üretmeyin.
- **K2 (Kur):** `usd_try`, `eur_try`, `fx_scenario_pct` her iki modelin input'unda. Ablation `without_fx` |delta| = 66.07% bu zorunluluğu doğrular.
- **K3 (Geo):** ORS'tan bağımsız modül. `geo.py` precomputed lookup → Haversine fallback. Yeni şehir gelince Haversine devreye girmeli.

### `analyze()` sözleşmesi sabit (rapor §11.3)
İmzayı değiştirmeyin. `AnalyzePayload` field'larını eklemek/çıkarmak backend'i kırar. Yeni alan eklemek gerekirse opsiyonel (`= None` default'lu) yapın ve schemas.py'da dokümante edin.

### Sentetik veri uyarısı
1500 satır augmented (≈%70 sentetik). Metrikler **augmented holdout** üzerinde. Pilot gerçek veri ile yeniden kalibre edilecek (`models/model_evidence.json.honesty_note`). Ablation deltalarının bazılarının negatif olması bu sentetik dağılımın doğal sonucudur — K1/K2/K3 yine load-bearing (mutlak |delta| > 10%).

## Kritik Sapmalar (yeni gelene açıklama)

- **15 vs 10 route sınıfı:** Excel'de 15 distinct route var, ama augmentation argmax'ında sadece 10'u kazandı. Backend `recommended_route ∈ trained_classes` (10) garantisi. UI 15'i göstermek isterse `metadata.all_known_routes` (15) ile `metadata.classes` (10) farkını "MVP'de henüz desteklenmiyor" olarak işaretleyebilir.
- **`co2_tonnes` her zaman `co2_kg / 1000`** — frontend kolaylığı için.
- **`live_fx` zorunlu** — backend TCMB cache'den besler, default değer YOK.
- **`target_city` opsiyonel** ama boşsa Haversine fallback DEFAULT_FALLBACK (1500 km) verebilir; backend `target_country` boyunca büyük şehir doldurması önerilir (DE→Hamburg, NL→Rotterdam, TR→İstanbul).
- **Pydantic v2 zorunlu** — `model_dump()` (NOT `dict()`).

## Commit Disiplini (`commit-discipline.md`)

ZERO TOLERANCE. Detay: [`commit-discipline.md`](commit-discipline.md).

- **Atomic:** her commit tek mantıksal değişiklik. Refactor + feature + fix aynı commit'te olmaz.
- **Claude imzası YASAK:** `Co-Authored-By: Claude`, `🤖 Generated with Claude Code` ve hiçbir AI imzası **kullanılmaz** (footer'da, body'de, başlıkta — hiçbir yerde).
- **Format:** `<tür>: <ne yapıldı>` (≤70 char). Türler: `add`, `fix`, `update`, `remove`, `refactor`, `docs`, `test`, `style`, `chore`.
- **Komut:** `git commit -m "<title>"` — heredoc YOK, imza YOK. Detay gerekirse ikinci `-m`.
- `git add <specific-file>` — `git add .` / `-A` **yasak** (sızıntı riski).
- `--amend` (push edilmiş commit'te), `--no-verify`, `--no-gpg-sign` **yasak**.
- Pre-commit hook fail ederse `--amend` kullanma; düzelt → yeni commit oluştur.

## Veri Yerleşimi

- `data/master/raw2value_v4.xlsx` — orijinal 16 sheet, **commit edilir**, hiçbir kod doğrudan değiştirmez. ETL bunu okur.
- `data/reference/*.parquet` (12 dosya) — ETL çıktısı, **commit edilir** (küçük, deterministik).
- `data/processed/*.parquet` ve `*.json` — augmentation/training çıktısı, **commit edilir**.
- `models/*.pkl` — `.gitignore`'da (büyük binary). `models/{metadata,model_evidence}.json` **commit edilir**.

## Test Kapsamı (88 test)

| Dosya | Test | Sorumluluk |
|---|--:|---|
| `test_reference_loader.py` | 11 | Parquet loader API + carbon mode mapping + quality matrix |
| `test_no_target_leakage.py` | 14 | M1/M2 feature listesinin sızıntısız kalması (CRITICAL) |
| `test_augmentation_bounds.py` | 11 | Material/quality dağılımı, CO₂ formülü tutarlılığı, seed reproducibility |
| `test_reasons.py` | 7 | 15 template + median branching + Türkçe Unicode |
| `test_confidence.py` | 8 | Data/model/overall + warning üretimi |
| `test_scorer.py` | 19 | 3 profil sum=1, top-K, defansif empty, profil-shift davranışı |
| `test_inference_smoke.py` | 10 | `analyze()` end-to-end, what-if FX, basic-mode warning, kabak path, warm latency |
| `test_e2e.py` | 8 | Public API import + co2_tonnes consistency + route alternatives probabilities |

Yeni feature ekledikten sonra **mutlaka** `test_no_target_leakage.py` çalıştırın.
