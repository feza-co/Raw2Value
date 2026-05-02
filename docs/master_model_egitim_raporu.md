# RAW2VALUE AI — MASTER MODEL EĞİTİM RAPORU

> **Versiyon:** v1.0 — 2 Mayıs 2026
> **Kapsam:** Veri seti hazır → Backend'e teslim edilebilir model artefaktları
> **Süre tahmini:** 6–9 saat (ML rolü için 24h plandaki M-1'den M-12'ye kadar olan blok)
> **Girdi:** `raw2value_master_v4_2026-05-02.xlsx` (16 sheet)
> **Çıktı:** `backend/models/` altında joblib + JSON artefaktlar + `inference.py` modülü

---

## 0. BU DOKÜMANI NASIL KULLANACAKSINIZ

### 0.1 Rolü

Bu rapor, projenin **veri tarafından modelle ilgili her şeyi bitirme aşamasının** tek referansıdır. Buradaki adımlar tamamlandığında:

- Backend ekibi `from raw2value_ml.inference import analyze` diyerek tek satırda tüm karar mantığını çağırabilir.
- `/api/analyze`, `/api/what-if`, `/api/model-evidence` endpoint'leri için ihtiyaç duyulan tüm hesaplama hazır olacaktır.
- Frontend tarafına geçmeden önce: 2 model + skorlayıcı + reason codes + confidence + ablation + benchmark hep birlikte tek bir Python paketinde teslim edilmiş olacak.

### 0.2 Okuma sırası

1. **Bölüm 1–4** stratejik. Liderle birlikte bir kez okunur, kararlar onaylanır.
2. **Bölüm 5–11** teknik. ML rolünü üstlenen kişi referans olarak kullanır.
3. **Bölüm 12 (MASTER ROADMAP)** uygulama. 13 adım sırayla yapılır; her adımda hazır Claude Code prompt'u var.
4. **Bölüm 13** kabul kriteri. Backend'e geçmeden önce tek tek işaretlenir.

### 0.3 Claude Code prompt'larını nasıl kullanacaksınız

Her roadmap adımında kutulu bir **CLAUDE CODE PROMPT** bölümü vardır. Bu prompt'u kopyalayıp Claude Code terminaline yapıştırarak adımı otomatik yaptırabilirsiniz. Prompt'lar şöyle yapılandırılmıştır:

- **🎯 ROL** — Claude Code'a hangi rolde davranacağı söylenir.
- **📁 GİRDİ** — Hangi dosyaları okuması gerektiği belirtilir.
- **📤 ÇIKTI** — Hangi dosyaları üretmesi gerektiği belirtilir.
- **🛠️ GÖREV** — Adım adım yapılacaklar.
- **✅ KABUL KRİTERİ** — Bittiğini nasıl anlayacağımız.

---

## 1. YÖNETİCİ ÖZETİ

### 1.1 Tek cümlelik hedef

> `raw2value_master_v4_2026-05-02.xlsx`'i girdi alıp `backend/models/` klasörüne `analyze(payload) → JSON` fonksiyonunu çalıştırmak için gereken tüm artefaktları (2 model dosyası, skorlayıcı, metadata, evidence) üretmek.

### 1.2 4 ana çıktı (deliverables)

| # | Çıktı | Format | Backend nereden çağırır? |
|---|---|---|---|
| 1 | **Profit Regression Model** | `model_profit.pkl` (joblib) | `predict_profit(features)` |
| 2 | **Route Classifier Model** | `model_route.pkl` (joblib) | `predict_route(features)` |
| 3 | **B2B Match Scorer + Reason Codes + Confidence** | `match_scorer.py` + `reasons.py` + `confidence.py` | `match_buyers(producer)` ve diğerleri |
| 4 | **Inference paketi** | `raw2value_ml/` Python paketi + `metadata.json` + `model_evidence.json` | `from raw2value_ml.inference import analyze` |

### 1.3 Üç doğrulama prensibi

Bu projede her tasarım kararı şu üç süzgeçten geçer:

1. **Kural uyumu (K1/K2/K3 zorunlu).** Karbon (hackathon resmi faktörleri 0.100/0.015/0.500/0.030), kur (TCMB EVDS), bağımsız geo (Nominatim/ORS) — bunlar süs değil, modelin **feature vector'üne giriyor** ve karar mekanizmasının parçası.
2. **Decision engine, marketplace değil.** LLM açıklayabilir ama **kararı ML modeli verir**. Dolayısıyla tahminin gerekçesi `reason_codes`, güveni `confidence_score` üzerinden çıkıyor.
3. **Target leakage yok.** `expected_profit_try`, `value_uplift_pct`, `match_score` hiçbir zaman input olarak modele girmez. Bu kuralı her veri pipeline değişikliğinde yeniden test ederiz.

### 1.4 Kapsam dışı (advanced/future work)

- LightGBM `LGBMRanker` (learning-to-rank) — MVP'de weighted scoring kalır.
- SHAP TreeExplainer — MVP'de feature importance yeterli.
- LLM açıklama — MVP'de template-based Türkçe metin üretimi.
- Optuna hyperparameter tuning — MVP'de sade grid/random search.
- CTGAN/TVAE deep augmentation — MVP'de domain-informed augmentation.

Saat 18+ checkpoint'inde zaman kalırsa bu öğeler eklenir; MVP fonksiyonelliği bunlara bağımlı **değildir**.

---

## 2. MEVCUT DURUM VE VARLIK ENVANTERİ

### 2.1 Master_v4.xlsx içinde ne hazır?

| Sheet | Satır | Hazır olan | Modelde kullanımı |
|---|---:|---|---|
| `01_source_registry` | 280 | Tüm kaynak referansları, A/B/C/D güven seviyesiyle | `data_confidence_score` türetimi |
| `02_material_reference` | 31 | 3 hammaddenin rezerv/üretim/fiyat aralıkları | `raw_price_*`, `regional_importance_score` |
| `03_processing_routes` | 16 | 16 rota: maliyet (TL+USD/ton), satış fiyatı min/max/typical | Hedef üretiminin altyapısı, route candidates |
| `04_organizations` | 49 | 33 işleyici (13 pomza + 10 perlit + 13 kabak ç.) + koordinatlar + kapasite | Producer/processor seed; nearby filter |
| `05_buyer_markets` | 32 | DE/NL/TR pazar boyutları, CAGR, TR-to-DE/NL nakliye maliyetleri | `demand_score`, `target_market` |
| `06_feature_dictionary` | 33 | Feature → kaynak dosya eşleşmesi | Schema kontrolü |
| `07_augmentation_rules` | 11 | 10 augmentation kuralı (SMOGN/Gauss/CTGAN) | Augmentation pipeline'ın specs'i |
| `08_assumptions_log` | 23 | Varsayımların liste + etki seviyesi | Confidence düşürme, savunma |
| `09_geo_distance` | 536 | **Gerçek ORS karayolu mesafeleri (önceden hesaplı)** | `source_to_processor_km`, `processor_to_buyer_km` |
| `10_carbon_factors` | 20 | Hackathon resmi + DEFRA + GLEC + EPA cross-ref | `emission_factor_kg_co2_ton_km` |
| `11_fx_rates` | 44 | TCMB + ECB cross günlük seri | Augmentation FX scenario sample |
| `12_risk_quality` | 37 | Delivery risk, price volatility, **kalite eşleşme matrisi** | `delivery_risk`, `quality_match_score` |
| `13_academic_refs` | 23 | 12 ML makalesi + 10 sektörel | Metodoloji savunması |
| `14_checklist` | 42 | Veri toplama checklist | Eksiklik tespiti |
| `15_comtrade_export` | 3 | (Sync bekliyor) | Future enrich |

### 2.2 Anahtar gözlem: **Veri büyük ölçüde hazır**

Bu, veri ekibinin başarısıdır. Aşağıdaki kritik şeyler **augmentation gerektirmez** çünkü gerçek veri hâlihazırda mevcut:

- ✅ **536 gerçek mesafe çifti** — `09_geo_distance`'den lookup. ORS'a tekrar çağrı yapmaya gerek yok.
- ✅ **16 rota × min/max/typical fiyat ve maliyet bandı** — `03_processing_routes`'ten çekilir.
- ✅ **49 gerçek koordinatlı organizasyon** — sentetik şehir/firma uydurmaya gerek yok.
- ✅ **Kalite eşleşme matrisi** — `12_risk_quality`'den deterministik fonksiyon.
- ✅ **Resmi karbon faktörleri** — `10_carbon_factors`'tan sabit.

### 2.3 Augmentation **gerçekten** ne için lazım?

Augmentation rastgele veri üretmek için **değil**, aşağıdaki senaryo çeşitliliğini sağlamak için:

- Tonaj çeşitliliği (1–1000 ton arası log-uniform)
- Kalite sınıfı dağılımı (A/B/C için 30/50/20)
- Kur senaryoları (TCMB ±%10 üzerinden 5 nokta)
- Lead time gürültüsü (±2 gün gauss)
- Risk skala gürültüsü (±0.05)
- 3 rota × 49 işleyici × 32 alıcı × 5 kur × 4 transport mode → kombinatoryal çeşitlilik

Hedef hacim: **~1.500 satır** (pomza %70 = 1.050, perlit %20 = 300, kabak ç. %10 = 150).

### 2.4 Eksik kalanlar (üretilecek)

Bu rapor sayesinde aşağıdakiler üretilecek:

- ❌ `data/processed/training_set_v1.parquet` — augmented + label'lı satırlar
- ❌ `models/model_profit.pkl` ve `models/model_route.pkl`
- ❌ `models/feature_pipeline.pkl` (sklearn ColumnTransformer)
- ❌ `models/metadata.json` (feature isimleri, route sınıfları, version, tarih)
- ❌ `models/model_evidence.json` (benchmark + ablation)
- ❌ `raw2value_ml/` Python paketi (inference, scorer, reason codes, confidence)
- ❌ Notebook'lar: `01_data_prep.ipynb`, `02_augmentation.ipynb`, `03_baselines.ipynb`, `04_gbm.ipynb`, `05_ablation.ipynb`

---

## 3. MODEL FELSEFESİ VE TASARIM KARARLARI

### 3.1 Neden gradient boosting (XGBoost / LightGBM / CatBoost)?

Tabular bir karar problemiyle karşı karşıyayız: küçük-orta boy dataset, karışık (kategorik + numerik) feature'lar, açıklanabilirlik gereksinimi, kalibre tahmin beklentisi.

**Akademik dayanak:**
- Chen & Guestrin 2016 (XGBoost), Ke et al. 2017 (LightGBM), Prokhorenkova et al. 2018 (CatBoost) — gradient-boosted decision tree'ler tabular problemlerde state-of-the-art.
- arXiv 2602.19237 (SAP RPT-1 değerlendirmesi) — tabular foundation modeller hâlâ GBDT'nin gerisinde, özellikle küçük örneklem regresyonunda.
- arXiv 2406.13166 (supply chain ML) — gradient-boosted modeller baseline'a kıyasla yüksek precision sağlıyor.

**Pratik dayanak:**
- ~1.500 satır veride neural net overfit eder, GBDT ortalama performans verir.
- Categorical encoding native (CatBoost) veya LabelEncoder + native handling (LightGBM).
- `feature_importances_` doğrudan reason codes için kullanılabilir.
- Eğitim süresi <30s — saatlik checkpoint ritmiyle uyumlu.

### 3.2 Neden 2 model + skorlayıcı, 1 dev model değil?

Üç ayrı soru, üç ayrı çıktı tipi:

| Soru | Çıktı tipi | Model |
|---|---|---|
| "Bu hammadde işlenirse ne kadar kâr getirir?" | Sürekli sayı (TRY) | **Model 1: Regressor** |
| "Bu hammadde için en iyi rota hangisi?" | Kategorik (16 rota arasından) | **Model 2: Classifier** |
| "Bu üretici için en uygun işleyici/alıcı hangisi?" | Sıralı liste (Top-K) | **B2B Match Scorer (weighted, MVP)** |

Tek bir uçtan uca sinir ağı bu üç çıktıyı verseydi:
- Açıklanabilirlik düşerdi.
- 1.500 satırda overfit ederdi.
- Reason codes üretmek zorlaşırdı.
- Backend tarafında parçalı kullanım imkânsız olurdu (örneğin sadece Top-3 alıcı listele).

### 3.3 Neden weighted scoring, learning-to-rank değil (MVP'de)?

LightGBM `LGBMRanker` LambdaRank/LambdaMART (Burges 2010) ile öğrenilmiş ranker'lar üretebilir. Ancak:

- Gerçek B2B işlem verimiz yok → ranker için ground-truth ranking de yok.
- Sentetik label kullanmak ranker'ı gerçek dünyaya genelleştirmez.
- Weighted scoring **açıklanabilir** (`reason_codes` doğrudan ağırlıklardan türer).
- Kullanıcının "düşük karbon önceliği" gibi seçimi ağırlıkları görünür şekilde değiştirir.

**Karar:** MVP'de weighted scoring. Pilot işlem verisi geldiğinde `LGBMRanker` ile değiştirilir (advanced).

### 3.4 Neden LLM **kararı vermiyor**, sadece açıklıyor?

| Görev | Kim yapar? |
|---|---|
| "150 ton pomza için hangi rota en kârlı?" | **ML modeli (gradient boosting)** |
| "Neden bu rota tavsiye edildi?" (Türkçe metin) | Template-based Türkçe açıklayıcı (MVP) / LLM (advanced) |
| "Bu skor nasıl hesaplandı?" (sayısal gerekçe) | **`reason_codes` modülü (feature importance)** |
| Pazar tahmini, fiyat tahmini, demand tahmini | **ML modeli + reference table lookup** |

LLM hallüsinasyon yapabilir, sayısal optimizasyona uygun değildir, kalibre tahmin vermez. Bu yüzden karar zinciri ML üzerinde kurulu.

### 3.5 Yapacaklarımız vs yapmayacaklarımız (özet matris)

| Konu | MVP (yapılacak) | Advanced/Future (zaman kalırsa) |
|---|---|---|
| Profit regression | XGBoost/LightGBM/CatBoost benchmark, en iyisi | Optuna 50-trial tuning |
| Route classification | XGBoost/LightGBM/CatBoost benchmark, en iyisi | Stacking ensemble |
| B2B match | Weighted scoring + reason codes | LightGBM `LGBMRanker` (NDCG@5) |
| Açıklanabilirlik | Feature importance + Türkçe template reasons | SHAP TreeExplainer + force plot |
| Açıklama metni | Template Türkçe ("X km mesafe ve Y kuru bu rotayı öne çıkardı") | LLM GPT-4o-mini, anonimleştirilmiş prompt |
| Augmentation | Domain-informed (10 kural, master_v4) | CTGAN/TVAE on full feature joint |
| Hyperparameter | Sabit / küçük random search | Optuna 50-100 trial |
| Calibration | Yok (raw output) | Isotonic calibration |
| Drift detection | Yok | Population Stability Index |

---

## 4. SİSTEM MİMARİSİ

### 4.1 Veri akışı (high-level)

```
┌──────────────────────────┐
│ raw2value_master_v4.xlsx │  (16 sheet, 280+ kaynak)
└────────────┬─────────────┘
             │ ETL (notebook 01)
             ▼
┌────────────────────────────────────────┐
│ data/raw/{routes,orgs,distances,...}   │  parquet'ler
│ data/reference/{prices,carbon,fx,...}  │
└────────────┬───────────────────────────┘
             │ Augmentation (notebook 02)
             ▼
┌────────────────────────────────────────┐
│ data/processed/training_set_v1.parquet │  ~1500 satır + 30+ feature + 4 hedef
└────────────┬───────────────────────────┘
             │ Training (notebooks 03, 04)
             ▼
┌────────────────────────────────────────┐
│ models/                                │
│   ├── feature_pipeline.pkl             │  ColumnTransformer (preprocessing)
│   ├── model_profit.pkl                 │  Best regressor
│   ├── model_route.pkl                  │  Best classifier
│   ├── metadata.json                    │  Feature names, route classes, version
│   └── model_evidence.json              │  Benchmark + ablation results
└────────────┬───────────────────────────┘
             │ Wrapping (raw2value_ml/)
             ▼
┌─────────────────────────────────────────────┐
│ raw2value_ml/                               │
│   ├── inference.py    → analyze(payload)    │
│   ├── scorer.py       → match_buyers(...)   │
│   ├── reasons.py      → reason_codes(...)   │
│   ├── confidence.py   → score_confidence    │
│   ├── geo.py          → distance lookup     │
│   ├── carbon.py       → CO2 calculation     │
│   └── fx.py           → FX cache layer      │
└────────────┬────────────────────────────────┘
             │ Backend integration
             ▼
┌──────────────────────────┐
│ backend/api/analyze.py   │ FastAPI endpoint
│ from raw2value_ml import │
│   inference              │
└──────────────────────────┘
```

### 4.2 Repository yapısı (önerilen)

```
raw2value-ai/
├── data/
│   ├── master/
│   │   └── raw2value_master_v4_2026-05-02.xlsx   # tek doğruluk kaynağı
│   ├── raw/                                       # ETL çıktısı (parquet)
│   ├── reference/                                 # Lookup tabloları
│   └── processed/
│       └── training_set_v1.parquet               # Eğitim veri seti
│
├── ml/
│   ├── notebooks/
│   │   ├── 01_data_prep.ipynb
│   │   ├── 02_augmentation.ipynb
│   │   ├── 03_baselines.ipynb
│   │   ├── 04_gbm_benchmark.ipynb
│   │   ├── 05_ablation.ipynb
│   │   └── 06_export_artifacts.ipynb
│   ├── src/
│   │   ├── etl.py
│   │   ├── augmentation.py
│   │   ├── targets.py
│   │   ├── features.py
│   │   ├── train_profit.py
│   │   ├── train_route.py
│   │   └── evidence.py
│   └── tests/
│       ├── test_no_target_leakage.py
│       ├── test_augmentation_bounds.py
│       └── test_inference_smoke.py
│
├── models/                                        # Backend'in okuyacağı klasör
│   ├── feature_pipeline.pkl
│   ├── model_profit.pkl
│   ├── model_route.pkl
│   ├── metadata.json
│   └── model_evidence.json
│
├── raw2value_ml/                                  # Backend'in import edeceği paket
│   ├── __init__.py
│   ├── inference.py
│   ├── scorer.py
│   ├── reasons.py
│   ├── confidence.py
│   ├── geo.py
│   ├── carbon.py
│   ├── fx.py
│   └── schemas.py                                 # pydantic Input/Output
│
├── backend/                                       # FastAPI (sonraki faz)
└── frontend/                                      # Next.js (sonraki faz)
```

### 4.3 Backend kontratı — `analyze()` fonksiyonunun imzası

Bu kontrat, ML rolünün backend'e teslim ettiği "API"dır. Backend bu imzayla çağırır, biz bu imzayı **garanti ederiz**.

```python
# raw2value_ml/inference.py

from raw2value_ml.schemas import AnalyzePayload, AnalyzeResponse

def analyze(payload: AnalyzePayload) -> AnalyzeResponse:
    """
    Kullanıcının formundan gelen ham girdi → tam karar paketi.

    Girdi (AnalyzePayload):
        raw_material: "pomza" | "perlit" | "kabak_cekirdegi"
        tonnage: float
        quality: "A" | "B" | "C" | "unknown"
        origin_city: str
        target_country: str  # "TR" | "DE" | "NL"
        target_city: Optional[str]
        transport_mode: "kara" | "deniz" | "demiryolu" | "hava"
        priority: "max_profit" | "low_carbon" | "fast_delivery"
        input_mode: "basic" | "advanced"
        # advanced opsiyonel:
        moisture_pct: Optional[float]
        purity_pct: Optional[float]
        particle_size_class: Optional[str]
        fx_scenario_pct: Optional[float] = 0.0  # what-if için
        cost_scenario_pct: Optional[float] = 0.0
        live_fx: dict  # {"usd_try": ..., "eur_try": ...} — backend cache'inden

    Çıktı (AnalyzeResponse):
        recommended_route: str
        route_alternatives: List[RouteOption]  # Top-3
        expected_profit_try: float
        value_uplift_pct: float
        co2_kg: float
        co2_tonnes: float
        match_results: List[MatchResult]  # Top-5 işleyici/alıcı
        reason_codes: List[ReasonCode]
        confidence: ConfidenceBreakdown
        feature_importance: List[FeatureImportance]  # Top-10
        warnings: List[str]
    """
```

Bu imzanın detayları **Bölüm 11**'de. Kontrat sabittir; backend bu yapıyla canlıya geçer.

---

## 5. VERİ HAZIRLIK PİPELİNE

### 5.1 ETL: Excel → Parquet'ler (Adım 1)

`raw2value_master_v4.xlsx`'in 16 sheet'i okunur, her biri tipli bir parquet'e dönüştürülür. Parquet seçimi: hızlı okuma + tip korunumu + sıkıştırma.

| Excel Sheet | Parquet | Notlar |
|---|---|---|
| `02_material_reference` | `data/reference/materials.parquet` | min/max/typical sayıya çevir |
| `03_processing_routes` | `data/reference/routes.parquet` | maliyet & satış fiyatı sayısal |
| `04_organizations` | `data/reference/organizations.parquet` | Lat/Lon float, kapasite int |
| `05_buyer_markets` | `data/reference/buyer_markets.parquet` | demand_score türetilecek (CAGR + boyut) |
| `09_geo_distance` | `data/reference/distances.parquet` | (src_id, dst_id) → km, dakika |
| `10_carbon_factors` | `data/reference/carbon.parquet` | sadece `hackathon_official` filtrele |
| `11_fx_rates` | `data/reference/fx_rates.parquet` | tarih + USD/TRY + EUR/TRY |
| `12_risk_quality` | `data/reference/risk.parquet` | 3 alt blok: delivery, price_volatility, quality_match |
| `07_augmentation_rules` | `data/reference/aug_rules.parquet` | augmentation pipeline'ın config'i |

### 5.2 Feature engineering kuralları

#### 5.2.1 Sayısal feature'lar (modele direkt giren)

```python
NUMERIC_FEATURES = [
    "tonnage",                              # log-transform: log1p
    "raw_price_typical_usd_ton",            # min-max scale opsiyonel
    "processed_price_typical_usd_ton",
    "processing_cost_typical_usd_ton",
    "packaging_cost_usd_ton",
    "source_to_processor_km",
    "processor_to_buyer_km",
    "total_distance_km",                    # = source + processor → buyer
    "emission_factor_kg_co2_ton_km",        # transport_mode'a göre lookup
    "co2_kg",                               # = tonnage * total_distance_km * emission_factor
    "usd_try",                              # canlı kur
    "eur_try",
    "fx_scenario_pct",                      # what-if için ±%10 senaryosu
    "demand_score",                         # 0–1, CAGR + market_size türevi
    "lead_time_days",
    "delivery_risk",                        # 0–1, transport_mode + ülke
    "price_volatility_risk",                # 0–1, hammadde + rota
    "quality_match_score",                  # 0–1, producer_grade × buyer_required matrix
    "data_confidence_score",                # 0–100
    # advanced opsiyonel
    "moisture_pct",
    "purity_pct",
]
```

#### 5.2.2 Kategorik feature'lar

```python
CATEGORICAL_FEATURES = [
    "raw_material",                         # pomza/perlit/kabak_cekirdegi
    "raw_subtype",
    "origin_district",                      # Acıgöl/Avanos/Ürgüp/Merkez/...
    "processing_route_candidate",           # 16 rota
    "product_form",                         # ham_kaya/kırılmış/elenmiş/toz/paketli
    "quality_grade",                        # A/B/C/unknown
    "processor_type",
    "buyer_country",                        # TR/DE/NL
    "buyer_sector",                         # building_insulation/horticulture_substrate/...
    "transport_mode",                       # kara/deniz/demiryolu/hava
    "input_mode",                           # basic/advanced
    "priority",                             # max_profit/low_carbon/fast_delivery
    # advanced opsiyonel
    "particle_size_class",                  # fine/medium/coarse
]
```

#### 5.2.3 Boolean / flag feature'lar

```python
BOOLEAN_FEATURES = [
    "quality_unknown",                      # quality == "unknown"
    "technical_data_available",
    "default_values_used",
    "lab_report_uploaded",
    "processor_has_own_raw_material",
]
```

#### 5.2.4 Encoding stratejisi

| Tip | Yöntem | Neden |
|---|---|---|
| Sayısal | StandardScaler (sadece advanced düzeyde, gerekirse) | GBDT scale'e duyarsızdır, çoğunlukla atlanır |
| Düşük-cardinality kategorik (≤10) | One-hot (drop_first=False) | Açıklanabilirlik |
| Yüksek-cardinality kategorik (>10) | Target encoding (advanced) ya da hashed bucket | district, city için |
| CatBoost özel durumu | Native categorical handling | Tüm kategorikleri direkt verebiliriz |

**Karar:** MVP'de **CatBoost** ile native categorical, **XGBoost/LightGBM** ile one-hot. Karşılaştırılabilir sonuçlar.

### 5.3 Hedef değişkenler (target variables)

| Target | Tip | Hangi model | Kim hesaplar? |
|---|---|---|---|
| `expected_profit_try` | sürekli (TRY) | Model 1 | Augmentation sırasında formülle |
| `value_uplift_pct` | sürekli (%) | Model 1 alternatif veya monitoring | Formülle |
| `recommended_route_label` | kategorik (16 sınıf) | Model 2 | `argmax(route_score)` |
| `match_score` | sürekli (0–1) | Skorlayıcı (model değil) | Backend'de runtime |

#### 5.3.1 `expected_profit_try` formülü

```python
expected_profit_try = (
    processed_price_typical_usd_ton * fx_rate_usd_try * tonnage    # gelir
    - processing_cost_typical_usd_ton * fx_rate_usd_try * tonnage  # işleme
    - packaging_cost_usd_ton * fx_rate_usd_try * tonnage           # paketleme
    - transport_cost_usd_ton_km * total_distance_km * tonnage * fx_rate_usd_try  # nakliye
    - raw_price_typical_usd_ton * fx_rate_usd_try * tonnage        # hammadde alış
)

# Augmentation gürültüsü: gerçek kâr ±%5 gauss noise (operasyonel belirsizlik proxy)
expected_profit_try *= (1 + np.random.normal(0, 0.05))
```

#### 5.3.2 `value_uplift_pct` formülü

```python
raw_sale_profit_try = raw_price_typical_usd_ton * fx_rate_usd_try * tonnage \
                    - direct_transport_cost_try

value_uplift_pct = (expected_profit_try - raw_sale_profit_try) / abs(raw_sale_profit_try)
```

#### 5.3.3 `recommended_route_label` üretimi (sentetik label)

Her hammadde × üretici × alıcı kombinasyonu için tüm rota adayları skorlanır:

```python
route_score = (
    0.45 * normalized_profit_score
  + 0.20 * demand_score
  + 0.15 * carbon_score                     # 1 - co2_kg / max_co2_kg
  + 0.10 * delivery_score                   # 1 - delivery_risk
  + 0.10 * confidence_score                 # data_confidence_score / 100
)

recommended_route_label = argmax(route_score across candidate routes)
```

> **Önemli:** `route_score` **input olarak modele girmez**, sadece label üretmek için kullanılır. Model 2 daha sonra "doğal" feature'lardan (fiyat, mesafe, kur, vs.) bu label'ı tahmin etmeyi öğrenir.

### 5.4 Target leakage koruması

Aşağıdaki kurallar `tests/test_no_target_leakage.py` ile kod düzeyinde doğrulanır:

| Kural | Test |
|---|---|
| `expected_profit_try` Model 2 input setinde olmamalı | `assert "expected_profit_try" not in model_route.feature_names_in_` |
| `value_uplift_pct` her iki modelin input setinde olmamalı | `assert "value_uplift_pct" not in {m1,m2}.feature_names_in_` |
| `recommended_route_label` Model 1 input setinde olmamalı | `assert "recommended_route_label" not in model_profit.feature_names_in_` |
| `match_score` hiçbir modelin input setinde olmamalı | `assert "match_score" not in model.feature_names_in_` |
| `route_score` hiçbir modelin input setinde olmamalı | "" |

Eğer `processing_route_candidate` Model 1'in inputunda **var**, bu sorun değil — çünkü **rota verili kabul edilip kâr tahmin ediliyor**. Model 2 ise rotayı kendisi tahmin eder, dolayısıyla onun input'unda `processing_route_candidate` olmaz.

| Feature | Model 1 input? | Model 2 input? |
|---|---|---|
| `processing_route_candidate` | ✅ EVET (verilmiş varsayılır) | ❌ HAYIR (target'tır) |
| `expected_profit_try` | ❌ HAYIR (target'tır) | ❌ HAYIR (leakage) |
| `recommended_route_label` | ❌ HAYIR (leakage) | ❌ HAYIR (target'tır) |

### 5.5 Augmentation pipeline (07_augmentation_rules ile uyumlu)

`07_augmentation_rules` sheet'indeki 10 kural Python kod olarak somutlaşır. **Hiçbiri rastgele değildir** — hepsi gerçek aralık veya formül üzerine ±gürültüdür.

```python
AUGMENTATION_PLAN = [
    # AUG-01: Pomza fiyatı SMOGN-vari noise
    {"feature": "raw_price_typical_usd_ton",
     "method": "gauss",
     "sigma_pct": 0.08,                              # ±%8
     "clip": ("min", "max"),                         # 02_material_reference'tan
     "ref": "Branco 2017 SMOGN regression noise"},

    # AUG-02: Mesafe ±%5 (trafik/mevsim proxy)
    {"feature": "source_to_processor_km",
     "method": "gauss",
     "sigma_pct": 0.05,
     "ref": "ORS deterministik üzerinden, 09_geo_distance"},

    # AUG-03: Kur senaryosu (what-if uyumlu)
    {"feature": "fx_scenario_pct",
     "method": "discrete",
     "values": [-0.10, -0.05, 0.0, +0.05, +0.10],
     "ref": "Hackathon what-if zorunlu"},

    # AUG-04: Lead time ± 2 gün
    {"feature": "lead_time_days",
     "method": "gauss",
     "sigma_abs": 2,
     "clip": (1, 90),
     "ref": "Hava/liman tıkanması proxy"},

    # AUG-05: Demand score: TradeMap CAGR + sektör + ±0.1 noise
    {"feature": "demand_score",
     "method": "compose_then_noise",
     "components": ["cagr_normalized", "market_size_normalized", "sector_relevance"],
     "weights": [0.5, 0.3, 0.2],
     "noise_sigma": 0.05,
     "clip": (0.0, 1.0),
     "ref": "Sentetik etiket — pilot ile kalibre"},

    # AUG-06: Quality grade dağılımı
    {"feature": "quality_grade",
     "method": "categorical_dist",
     "distribution": {"A": 0.30, "B": 0.50, "C": 0.20},
     "ref": "Sektör heuristik"},

    # AUG-07: CO2 tonaj ölçüm hatası ±%3
    {"feature": "co2_kg",
     "method": "formula_then_noise",
     "formula": "tonnage * total_distance_km * emission_factor_kg_co2_ton_km",
     "noise_sigma_pct": 0.03,
     "ref": "DEFRA ölçüm belirsizliği"},

    # AUG-08: Risk skala ±0.05
    {"feature": "delivery_risk",
     "method": "lookup_then_noise",
     "lookup": "12_risk_quality.delivery",            # transport_mode'a göre
     "noise_sigma": 0.05,
     "clip": (0.0, 1.0),
     "ref": "Christopher & Peck 2004"},

    # AUG-09: B2B match label tier (high/mid/low)
    {"feature": "match_label",
     "method": "tier_from_score",
     "thresholds": {"high": 0.75, "mid": 0.50},      # SCORE>=0.75 → high
     "imbalanced": "SMOTE applied at training (class_weight)",
     "ref": "Imbalanced — SMOTE/SMOGN"},

    # AUG-10: CTGAN nadir tablo (advanced/future)
    {"feature": "tabular_full",
     "method": "ctgan",
     "trigger": "if total_rows < 1000",
     "ref": "Xu et al. 2019 — MVP'de kapalı"},
]
```

### 5.6 Augmentation sırası (kritik)

Yanlış sıralama yapılırsa CO2 / total_distance gibi formüllü feature'lar tutarsız olur. **Doğru sıra:**

```
1. Bootstrap base rows: pomza×%70, perlit×%20, kabak×%10
2. Sample categorical: raw_material, raw_subtype, origin_district, route_candidate, transport_mode, quality_grade, priority
3. Lookup deterministic: source/processor/buyer coords (4_organizations), distances (9_geo_distance),
   raw/processed prices (3_processing_routes), emission_factor (10_carbon_factors)
4. Apply noise to lookup values: prices ±%8, distance ±%5, lead_time ±2g
5. Compute formula features: co2_kg, total_distance_km, transport_total_cost_usd
6. Apply formula noise: co2 ±%3
7. Sample fx_scenario_pct ∈ {-10,-5,0,+5,+10}%
8. Compute targets: expected_profit_try, value_uplift_pct, route_score → label
9. Validate: bounds, no NaN, no target leakage
10. Save: data/processed/training_set_v1.parquet
```

### 5.7 Train/Val/Test split

Stratified 80/10/10 split:

```python
from sklearn.model_selection import train_test_split

# Stratify on raw_material × processing_route_candidate
strata = df["raw_material"] + "_" + df["processing_route_candidate"]

train, holdout = train_test_split(df, test_size=0.20, stratify=strata, random_state=42)
val, test = train_test_split(holdout, test_size=0.50, stratify=holdout_strata, random_state=42)

# Sonuç: ~%80 train, ~%10 val, ~%10 test
```

**Time-aware split (advanced):** `fx_last_updated`'a göre 2024 train, 2025 test → concept drift gösterimi. MVP'de **stratified random**.

---

## 6. MODEL 1 — VALUE ROUTE OPTIMIZER (Profit Regression)

### 6.1 Hedef

Verilen feature vektörü için (rota dahil), o spesifik rotada **beklenen kâr (TRY)** tahmini.

### 6.2 Algoritma karşılaştırması

| Model | Niye dener? | Beklenen sonuç |
|---|---|---|
| Rule-based | "ML değer katıyor mu?" sorusu için baseline | Düşük, ham formül |
| Linear Regression | Naif sayısal baseline | Orta-düşük (lineer yetersiz) |
| Random Forest (n=200, depth=10) | Non-linear baseline | Orta-iyi |
| **XGBoost** (depth=6, lr=0.1, n_est=500) | İlk seçenek (Chen 2016) | İyi-mükemmel |
| **LightGBM** (num_leaves=31, lr=0.05, n_est=500) | Hız + kategorik | İyi-mükemmel |
| **CatBoost** (depth=6, lr=0.05, n_est=500) | Native cat + ordered boosting | İyi-mükemmel |

**MVP karar:** En iyi RMSE'ye sahip GBDT seçilir, `model_profit.pkl` olarak kaydedilir.

### 6.3 Hiperparametre seti (sabit, MVP)

```python
XGBOOST_PARAMS = {
    "objective": "reg:squarederror",
    "n_estimators": 500,
    "max_depth": 6,
    "learning_rate": 0.1,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "min_child_weight": 3,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "random_state": 42,
    "early_stopping_rounds": 30,
    "eval_metric": "rmse",
}

LIGHTGBM_PARAMS = {
    "objective": "regression",
    "n_estimators": 500,
    "num_leaves": 31,
    "learning_rate": 0.05,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "min_child_samples": 10,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "random_state": 42,
    "early_stopping_round": 30,
    "metric": "rmse",
}

CATBOOST_PARAMS = {
    "iterations": 500,
    "depth": 6,
    "learning_rate": 0.05,
    "l2_leaf_reg": 3.0,
    "loss_function": "RMSE",
    "eval_metric": "RMSE",
    "random_seed": 42,
    "early_stopping_rounds": 30,
    "verbose": 100,
    # cat_features parametre olarak ayrıca veriliyor
}
```

### 6.4 Metrik tablosu

| Metrik | Hedef MVP | Anlamı |
|---|---|---|
| RMSE (TRY) | < %15 mean profit | Karar yanlışı tolerans |
| MAE (TRY) | < %10 mean profit | Robust outlier tolerans |
| R² | > 0.70 | Sentetik veride bile öğrendi mi? |
| MAPE | < %20 | Yüzdesel hata |

**Şeffaflık notu:** MVP veri seti sentetik (~%70 augmented). Bu metrikler sentetik holdout üzerinde ölçülür ve `model_evidence.json`'a yazılır. Pilot gerçek veri geldiğinde yeniden kalibre edilir.

### 6.5 Feature listesi (Model 1 input)

```python
M1_FEATURES = [
    # material
    "raw_material", "raw_subtype", "origin_district",
    "tonnage", "quality_grade", "quality_unknown", "product_form",
    # rota
    "processing_route_candidate",                # !! Model 1'de input, Model 2'de target
    # fiyat & maliyet (lookup'tan + augment'lı)
    "raw_price_typical_usd_ton",
    "processed_price_typical_usd_ton",
    "processing_cost_typical_usd_ton",
    "packaging_cost_usd_ton",
    # coğrafi
    "source_to_processor_km", "processor_to_buyer_km", "total_distance_km",
    "transport_mode", "transport_cost_usd_ton_km",
    # karbon (zorunlu kural)
    "emission_factor_kg_co2_ton_km", "co2_kg",
    # kur (zorunlu kural)
    "usd_try", "eur_try", "fx_scenario_pct",
    # pazar
    "buyer_country", "buyer_sector", "buyer_city", "demand_score",
    # operasyonel
    "lead_time_days", "delivery_risk", "price_volatility_risk",
    # kalite
    "quality_match_score",
    # confidence (eklenir)
    "data_confidence_score",
    # mod
    "input_mode",
    # advanced (opsiyonel — eksikse default)
    "moisture_pct", "purity_pct", "particle_size_class",
]
```

`expected_profit_try`, `value_uplift_pct`, `recommended_route_label`, `match_score` **YOKtur**.

---

## 7. MODEL 2 — ROUTE CLASSIFIER

### 7.1 Hedef

Verilen üretici/hammadde/pazar koşullarında **en iyi işleme rotasını** seçmek.

Sınıf sayısı: 16 (3 hammadde × ortalama ~5 rota; gerçekte 5+5+5+1=16 distinct route).

### 7.2 Algoritma karşılaştırması

Model 1 ile aynı aile, ancak `objective` değişir:

| Model | Hyperparam |
|---|---|
| Majority class baseline | Sınıf modu (en sık rota) |
| Logistic Regression (multi-class, softmax) | C=1.0 |
| Random Forest Classifier | n=200, depth=10 |
| **XGBoost** | objective='multi:softprob', num_class=16 |
| **LightGBM** | objective='multiclass', num_class=16 |
| **CatBoost** | loss_function='MultiClass' |

### 7.3 Class imbalance

Sınıflar dengesizdir:
- `pomza_raw_sale` ve `bims_aggregate` baskın (rota augmentation oranı yüksek)
- `kabak_cekirdegi_protein_powder` ve `tourism_gift_pack` nadir

**Çözüm:** `class_weight="balanced"` veya `sample_weight` ile training. SMOTE nadir sınıflar için augmentation aşamasında uygulanabilir (07_augmentation_rules AUG-09 zaten bunu işaretliyor).

### 7.4 Metrikler

| Metrik | Hedef MVP | Anlamı |
|---|---|---|
| Accuracy | > 0.55 | Random'dan iyi (1/16=6%) |
| Macro-F1 | > 0.50 | Sınıf-dengesiz robust ölçü |
| Top-2 accuracy | > 0.75 | "İlk 2 önerimden biri doğru" — UX için kritik |
| Confusion matrix | Görsel | Hangi sınıflar karışıyor? |

### 7.5 Feature listesi (Model 2 input)

`processing_route_candidate` **YOK** (target'tır), gerisi Model 1 ile aynı.

```python
M2_FEATURES = [f for f in M1_FEATURES if f != "processing_route_candidate"]
M2_FEATURES += ["priority"]   # max_profit/low_carbon/fast_delivery — kullanıcı önceliği rota seçimini etkiler
```

---

## 8. B2B MATCH SCORER (Weighted, MVP)

### 8.1 Görev

Verilen üretici/hammadde için **Top-K (genellikle 5)** işleyici × alıcı kombinasyonu sıralamak.

> **Önemli:** Bu bir model değil, deterministik bir **fonksiyon**dur. Eğitilmemiştir. Ağırlıklar görünürdür ve `priority` parametresine göre dinamik değişir.

### 8.2 Skor formülü

```python
def compute_match_score(producer, processor, buyer, context, priority="max_profit"):
    weights = WEIGHT_PROFILES[priority]   # max_profit / low_carbon / fast_delivery

    profit_score        = normalize(estimate_profit(producer, processor, buyer, context))
    demand_score        = lookup_demand(buyer.sector, buyer.country)               # 0–1
    distance_score      = 1 - clip(total_distance_km / MAX_DISTANCE, 0, 1)         # daha yakın = daha iyi
    carbon_score        = 1 - clip(co2_kg / MAX_CO2, 0, 1)
    delivery_score      = 1 - lookup_delivery_risk(transport_mode, country)
    quality_score       = quality_match_matrix[producer.grade, buyer.required_grade]

    match_score = (
        weights["profit"]   * profit_score
      + weights["demand"]   * demand_score
      + weights["distance"] * distance_score
      + weights["carbon"]   * carbon_score
      + weights["delivery"] * delivery_score
      + weights["quality"]  * quality_score
    )
    return match_score, components_dict
```

### 8.3 Ağırlık profilleri

| Profil | profit | demand | distance | carbon | delivery | quality |
|---|---:|---:|---:|---:|---:|---:|
| **max_profit (default)** | 0.35 | 0.20 | 0.15 | 0.15 | 0.10 | 0.05 |
| **low_carbon** | 0.25 | 0.15 | 0.10 | 0.30 | 0.15 | 0.05 |
| **fast_delivery** | 0.25 | 0.15 | 0.20 | 0.10 | 0.25 | 0.05 |

Her profil **toplam 1.0**'dır. Demo'da kullanıcı priority değiştirince ekranda Top-3 yeniden sıralanır — bu what-if'in B2B versiyonudur.

### 8.4 Quality match matrix lookup

`12_risk_quality` sheet'inden direkt:

```python
QUALITY_MATCH = {
    ("A", "A"): 1.00, ("A", "B"): 1.00, ("A", "C"): 0.95,
    ("B", "A"): 0.55, ("B", "B"): 1.00, ("B", "C"): 0.95,
    ("C", "A"): 0.20, ("C", "B"): 0.50, ("C", "C"): 1.00,
}
# unknown grade için: 0.70 (orta — confidence düşürür)
```

### 8.5 Top-K seçimi

```python
def match_buyers(producer, candidates, context, priority="max_profit", top_k=5):
    scored = []
    for processor, buyer in candidates:
        score, components = compute_match_score(producer, processor, buyer, context, priority)
        reasons = generate_reason_codes(components, priority)
        scored.append({
            "processor": processor,
            "buyer": buyer,
            "score": score,
            "components": components,
            "reasons": reasons,
        })
    return sorted(scored, key=lambda x: -x["score"])[:top_k]
```

---

## 9. AÇIKLANABILIRLIK + GÜVEN SKORU

### 9.1 Reason codes (template-based, MVP)

Top-3 feature contribution → Türkçe metin. Source: GBDT `feature_importances_` (gain).

```python
REASON_TEMPLATES = {
    "total_distance_km": {
        "high": "{km:.0f} km mesafe lojistik maliyeti yükseltiyor.",
        "low":  "{km:.0f} km kısa mesafe maliyet avantajı sağlıyor.",
    },
    "usd_try": {
        "high": "USD/TRY {fx:.2f} ihracat gelirini güçlendiriyor.",
        "low":  "USD/TRY {fx:.2f} ihracat gelirini sınırlıyor.",
    },
    "co2_kg": {
        "high": "{co2:.0f} kg CO₂ karbon ayak izini büyütüyor.",
        "low":  "{co2:.0f} kg CO₂ ile düşük karbon avantajı var.",
    },
    "demand_score": {
        "high": "Hedef pazardaki talep skoru {score:.2f} — pazar uygun.",
        "low":  "Hedef pazar talep skoru {score:.2f} — alternatif pazar düşünülebilir.",
    },
    "quality_match_score": {
        "high": "Kalite {prod_grade} ↔ alıcı talebi {buy_grade} tam eşleşiyor.",
        "low":  "Kalite uyumsuzluğu fiyat penalty yaratıyor.",
    },
    # ... diğer feature'lar için
}

def generate_reason_codes(features, prediction, top_k=3):
    importances = MODEL.feature_importances_                          # gain bazlı
    top_features = sorted(zip(FEATURE_NAMES, importances), key=lambda x: -x[1])[:top_k]
    reasons = []
    for fname, imp in top_features:
        value = features[fname]
        is_high = value > FEATURE_MEDIANS[fname]                       # baseline median
        template = REASON_TEMPLATES[fname]["high" if is_high else "low"]
        reasons.append(template.format(**features))
    return reasons
```

### 9.2 Confidence breakdown

`data_confidence_score` (0–100) ve `model_confidence_score` (0–100) ayrı ayrı raporlanır.

```python
def compute_confidence(features, prediction_proba):
    # Data confidence
    data_conf = 100
    if not features["technical_data_available"]:
        data_conf -= 15
    if features["raw_price_source_confidence"] in ("C", "D"):
        data_conf -= 10
    if features["processor_capacity_confidence"] in ("C", "D"):
        data_conf -= 5
    if features["fx_source"] == "TCMB_LIVE":
        data_conf += 10
    if features["distance_source"] == "ORS_LIVE":
        data_conf += 5
    data_conf = clip(data_conf, 0, 100)

    # Model confidence (GBDT için)
    if prediction_proba is not None:
        # Multi-class için top-1 probability
        model_conf = max(prediction_proba) * 100
    else:
        # Regression için: ensemble disagreement (advanced) ya da sabit
        model_conf = 75  # MVP placeholder

    overall = (data_conf * 0.4 + model_conf * 0.6) / 100              # 0–1

    return {
        "data_confidence": data_conf,
        "model_confidence": model_conf,
        "overall": overall,
        "warnings": collect_warnings(features),
    }
```

### 9.3 Feature importance (global, model_evidence.json'a)

```python
{
  "model_profit": {
    "top_features": [
      {"name": "total_distance_km", "importance": 0.18},
      {"name": "usd_try",            "importance": 0.15},
      {"name": "processed_price_typical_usd_ton", "importance": 0.12},
      {"name": "tonnage",            "importance": 0.10},
      {"name": "co2_kg",             "importance": 0.08},
      // ... top-15
    ]
  },
  "model_route": { ... }
}
```

Bu Model Evidence ekranında bar chart olarak görselleşir. Frontend bu JSON'u doğrudan tüketir.

---

## 10. MODEL EVIDENCE — Benchmark + Ablation

### 10.1 Benchmark protokolü

Her aday model aynı `(train, val, test)` split üzerinde çalışır, aynı seed (42), aynı feature set.

`model_evidence.json` çıktısı şöyle olacak:

```json
{
  "version": "v1.0",
  "trained_at": "2026-05-02T14:32:00Z",
  "dataset": {
    "n_total": 1487,
    "n_train": 1190,
    "n_val": 149,
    "n_test": 148,
    "split_strategy": "stratified_80_10_10",
    "stratify_on": ["raw_material", "processing_route_candidate"],
    "augmentation": "domain_informed_v1",
    "raw_reference_rows": 78
  },
  "profit_regression": {
    "rule_based_baseline":  {"rmse": ___, "mae": ___, "r2": ___, "train_sec": __},
    "linear_regression":    {"rmse": ___, "mae": ___, "r2": ___, "train_sec": __},
    "random_forest":        {"rmse": ___, "mae": ___, "r2": ___, "train_sec": __},
    "xgboost":              {"rmse": ___, "mae": ___, "r2": ___, "train_sec": __},
    "lightgbm":             {"rmse": ___, "mae": ___, "r2": ___, "train_sec": __},
    "catboost":             {"rmse": ___, "mae": ___, "r2": ___, "train_sec": __},
    "best_model": "xgboost"
  },
  "route_classification": {
    "majority_baseline":    {"accuracy": ___, "macro_f1": ___, "top2_acc": ___},
    "random_forest":        {"accuracy": ___, "macro_f1": ___, "top2_acc": ___},
    "xgboost":              {"accuracy": ___, "macro_f1": ___, "top2_acc": ___},
    "lightgbm":             {"accuracy": ___, "macro_f1": ___, "top2_acc": ___},
    "catboost":             {"accuracy": ___, "macro_f1": ___, "top2_acc": ___},
    "best_model": "lightgbm"
  },
  "ablation": {
    "full_features": {"profit_rmse": ___, "route_macro_f1": ___},
    "without_fx": {
      "profit_rmse": ___,
      "route_macro_f1": ___,
      "rmse_delta_pct": "+__",
      "interpretation": "FX feature'ları kaldırıldığında ihracat rotaları skoru zayıflıyor."
    },
    "without_geo": {
      "profit_rmse": ___,
      "route_macro_f1": ___,
      "rmse_delta_pct": "+__",
      "interpretation": "Mesafe feature'ları kaldırıldığında işleyici/alıcı eşleşmesi bozuluyor."
    },
    "without_carbon": {
      "profit_rmse": ___,
      "route_macro_f1": ___,
      "rmse_delta_pct": "+__",
      "interpretation": "Karbon feature'ları kaldırıldığında düşük karbon önceliği etkisizleşiyor."
    },
    "without_demand": {
      "profit_rmse": ___,
      "route_macro_f1": ___,
      "rmse_delta_pct": "+__",
      "interpretation": "Talep feature'ları kaldırıldığında pazar uygunluğu zayıflıyor."
    }
  },
  "feature_importance": { ... },
  "honesty_note": "Sayılar augmented holdout üzerinde ölçüldü. Pilot gerçek veriyle yeniden kalibre edilecektir."
}
```

### 10.2 Ablation çalışması

Her ablation senaryosu, ilgili feature grubunu çıkarıp aynı eğitim hattını çalıştırır.

| Senaryo | Çıkarılan feature grubu | Beklenen yorum |
|---|---|---|
| `without_fx` | `usd_try, eur_try, fx_scenario_pct` | İhracat rotaları zayıflar |
| `without_geo` | `source_to_processor_km, processor_to_buyer_km, total_distance_km` | Eşleşme bozulur |
| `without_carbon` | `emission_factor_kg_co2_ton_km, co2_kg` | Karbon önceliği etkisizleşir |
| `without_demand` | `demand_score, buyer_sector, buyer_country` | Pazar uygunluğu zayıflar |
| `without_quality` | `quality_grade, quality_match_score, moisture_pct, purity_pct` | Kalite-bağlı ayrım azalır |
| `without_cost` | `processing_cost_typical_usd_ton, packaging_cost_usd_ton, transport_cost_usd_ton_km` | Kâr tahmini bozulur |

Ablation **kanıtlamak istediğimiz**: K1 (karbon), K2 (kur), K3 (geo) sadece UI'da değil, modelin karar mekanizmasındadır.


---

## 11. PAKETLEME — Backend için Üretilecek Artefaktlar

### 11.1 Artefakt listesi

`models/` klasörü backend tarafından mount edilir. `raw2value_ml/` paketi `pip install -e .` ile yüklenir.

```
models/
├── feature_pipeline.pkl       # ColumnTransformer (one-hot, scale)
├── model_profit.pkl           # Best regressor (XGB/LGB/CB)
├── model_route.pkl            # Best classifier
├── metadata.json              # Versiyon, feature isimleri, sınıf isimleri, train timestamp
└── model_evidence.json        # Benchmark + ablation + feature importance

raw2value_ml/
├── __init__.py                # Public API
├── inference.py               # analyze() — tek giriş noktası
├── scorer.py                  # Weighted match scoring
├── reasons.py                 # Reason code template engine
├── confidence.py              # Confidence breakdown
├── geo.py                     # Distance lookup + Haversine fallback
├── carbon.py                  # CO2 hesabı + lookup
├── fx.py                      # FX what-if scenario generator
├── schemas.py                 # pydantic AnalyzePayload, AnalyzeResponse
└── reference_loader.py        # Excel → reference parquet'leri yükleyici
```

### 11.2 `metadata.json` yapısı

```json
{
  "version": "v1.0",
  "trained_at": "2026-05-02T14:32:00Z",
  "models": {
    "profit": {
      "type": "xgboost",
      "file": "model_profit.pkl",
      "feature_names": ["raw_material", "tonnage", ...],
      "n_features": 31,
      "target": "expected_profit_try"
    },
    "route": {
      "type": "lightgbm",
      "file": "model_route.pkl",
      "feature_names": ["raw_material", "tonnage", ...],
      "n_features": 30,
      "target": "recommended_route_label",
      "classes": ["pomza_raw_sale", "bims_aggregate", "micronized_pumice", ...]
    }
  },
  "preprocessing": {
    "file": "feature_pipeline.pkl",
    "type": "ColumnTransformer",
    "categorical_features": [...],
    "numerical_features": [...],
    "imputation_strategy": "regional_default_for_advanced_fields"
  },
  "default_values": {
    "moisture_pct": {
      "pomza": 5.0,
      "perlit": 4.0,
      "kabak_cekirdegi": 7.0
    },
    "purity_pct": {
      "pomza": 92.0,
      "perlit": 95.0,
      "kabak_cekirdegi": 98.0
    },
    "particle_size_class": "medium",
    "lead_time_days": 7
  },
  "reference_tables": {
    "distances": "data/reference/distances.parquet",
    "carbon_factors": "data/reference/carbon.parquet",
    "quality_match_matrix": "data/reference/risk.parquet",
    "processing_routes": "data/reference/routes.parquet",
    "organizations": "data/reference/organizations.parquet"
  }
}
```

### 11.3 Inference modülünün davranış sözleşmesi

```python
# raw2value_ml/inference.py — pseudo-code

from typing import Optional
from pydantic import BaseModel
from .schemas import AnalyzePayload, AnalyzeResponse
from .scorer import match_buyers
from .reasons import generate_reason_codes
from .confidence import compute_confidence
from .geo import lookup_distance, find_nearby_processors
from .carbon import compute_co2
from .fx import apply_fx_scenario
from .reference_loader import (
    load_routes, load_organizations, load_carbon_factors,
    load_quality_matrix, load_demand_scores
)

# Lazy-loaded singletons
_MODEL_PROFIT = None
_MODEL_ROUTE = None
_PIPELINE = None
_METADATA = None

def _ensure_loaded():
    global _MODEL_PROFIT, _MODEL_ROUTE, _PIPELINE, _METADATA
    if _MODEL_PROFIT is None:
        _MODEL_PROFIT = joblib.load("models/model_profit.pkl")
        _MODEL_ROUTE = joblib.load("models/model_route.pkl")
        _PIPELINE = joblib.load("models/feature_pipeline.pkl")
        _METADATA = json.load(open("models/metadata.json"))


def analyze(payload: AnalyzePayload) -> AnalyzeResponse:
    _ensure_loaded()

    # 1. Default değer doldur (basic mode)
    features = fill_defaults(payload, _METADATA["default_values"])

    # 2. Coğrafi & karbon hesapları (kural 1, 3)
    distances = lookup_distance(features.origin_city,
                                features.target_city,
                                features.transport_mode)
    co2_kg = compute_co2(features.tonnage,
                         distances.total_km,
                         features.transport_mode)
    features.update({**distances.dict(), "co2_kg": co2_kg})

    # 3. FX (kural 2) + what-if senaryosu
    fx = apply_fx_scenario(features.live_fx, features.fx_scenario_pct)
    features.update(fx)

    # 4. Model 2: Rota tahmini
    X_route = _PIPELINE.transform(_to_frame(features, M2_FEATURES))
    route_proba = _MODEL_ROUTE.predict_proba(X_route)[0]
    top3_routes = top_k_routes(route_proba, _METADATA["models"]["route"]["classes"], k=3)

    # 5. Her aday rota için Model 1: Profit tahmini
    route_alternatives = []
    for route_name, prob in top3_routes:
        feats_with_route = {**features, "processing_route_candidate": route_name}
        X_profit = _PIPELINE.transform(_to_frame(feats_with_route, M1_FEATURES))
        predicted_profit = float(_MODEL_PROFIT.predict(X_profit)[0])
        value_uplift = compute_uplift(predicted_profit, feats_with_route)
        route_alternatives.append({
            "route": route_name,
            "predicted_profit_try": predicted_profit,
            "value_uplift_pct": value_uplift,
            "co2_kg": co2_kg,
            "route_probability": prob,
        })

    recommended = max(route_alternatives, key=lambda r: r["predicted_profit_try"])

    # 6. B2B Match: yakın işleyiciler arasından Top-5
    nearby_processors = find_nearby_processors(features.origin_city,
                                               features.raw_material,
                                               radius_km=200)
    candidate_buyers = filter_buyers_by_route(recommended["route"], features.target_country)
    candidate_combos = combine(nearby_processors, candidate_buyers)
    match_results = match_buyers(producer=features,
                                 candidates=candidate_combos,
                                 context={"co2": co2_kg, "fx": fx},
                                 priority=features.priority,
                                 top_k=5)

    # 7. Reason codes
    reason_codes = generate_reason_codes(features,
                                          model_top_features=top_features(_MODEL_PROFIT),
                                          recommendation=recommended)

    # 8. Confidence
    confidence = compute_confidence(features, prediction_proba=route_proba)

    # 9. Response
    return AnalyzeResponse(
        recommended_route=recommended["route"],
        route_alternatives=route_alternatives,
        expected_profit_try=recommended["predicted_profit_try"],
        value_uplift_pct=recommended["value_uplift_pct"],
        co2_kg=co2_kg,
        co2_tonnes=co2_kg / 1000,
        match_results=match_results,
        reason_codes=reason_codes,
        confidence=confidence,
        feature_importance=top_features(_MODEL_PROFIT, k=10),
        warnings=collect_warnings(features),
    )
```

### 11.4 Performans hedefi

| Operasyon | Hedef latency | Notlar |
|---|---|---|
| `analyze()` cold start (model load) | <2s | Bir kez ilk istekte |
| `analyze()` warm | <300ms | Demo için kritik |
| `match_buyers()` (top_k=5, 50 candidates) | <50ms | Pure Python |
| `lookup_distance()` (parquet'ten) | <5ms | DataFrame query |

---

## 12. MASTER ROADMAP — 13 ADIM

Her adım: **Amaç / Girdi örneği / Çıktı örneği / Claude Code prompt / Kabul kriteri**.

### ADIM 0 — Repo iskeleti ve bağımlılık kurulumu

**Amaç:** Boş bir Python ortamından `pyproject.toml`, `requirements.txt` ve klasör yapısı hazır hâle gelmek.

**Girdi:** Hiçbir şey (boş repo veya mevcut repo).

**Çıktı:** Yukarıda Bölüm 4.2'de gösterilen klasör yapısı + `pyproject.toml`.

**📋 CLAUDE CODE PROMPT — ADIM 0:**

```markdown
🎯 ROL: Sen Raw2Value AI projesinin ML mühendisisin. Repo iskeletini kuracaksın.

📁 GİRDİ:
- Mevcut repo köküde olduğunu varsay.
- Aşağıdaki klasör yapısını oluştur.

📤 ÇIKTI:
- /data/{master,raw,reference,processed}/ (boş klasörler + .gitkeep)
- /ml/{notebooks,src,tests}/ (boş, ileride doldurulacak)
- /models/ (boş + .gitkeep)
- /raw2value_ml/ paketi (boş __init__.py + tüm modüller boş ama import edilebilir)
- pyproject.toml (Python 3.11, paket adı raw2value-ml)
- requirements.txt
- .gitignore (Python standart + jupyter checkpoint + parquet)
- README.md (kısaca proje hakkında, Bölüm 1 yönetici özetinden 5 satır)

🛠️ GÖREV:
1. Klasör yapısını oluştur.
2. requirements.txt içine: pandas==2.2.*, numpy==1.26.*, scikit-learn==1.4.*, xgboost==2.0.*, lightgbm==4.3.*, catboost==1.2.*, joblib, pyarrow, openpyxl, pydantic==2.*, pytest, jupyter, matplotlib, seaborn
3. raw2value_ml/__init__.py: __version__ = "0.1.0"
4. raw2value_ml/{inference,scorer,reasons,confidence,geo,carbon,fx,schemas,reference_loader}.py — her birinde sadece module docstring + bir TODO yorumu olsun, henüz implementasyon yok.
5. Master Excel'i (raw2value_master_v4_2026-05-02.xlsx) data/master/ altına kopyala.

✅ KABUL KRİTERLERİ:
- `python -c "import raw2value_ml"` hata vermez.
- `tree -L 2 -d` çıktısı Bölüm 4.2'deki yapıyla birebir aynıdır.
- pip install -e . çalışır.
```

---

### ADIM 1 — ETL: Excel → Parquet referans tabloları

**Amaç:** Master Excel'in 16 sheet'ini tip-temiz parquet'lere dönüştürmek.

**Girdi (örnek):**
```
data/master/raw2value_master_v4_2026-05-02.xlsx
  └── 03_processing_routes (16 satır, str/sayı karışık)
```

**Çıktı (örnek):**
```python
# data/reference/routes.parquet okunduğunda
import pandas as pd
df = pd.read_parquet("data/reference/routes.parquet")
df.head(2).to_dict("records")
# [
#   {"raw_material": "pomza",
#    "route": "raw_sale",
#    "processing_cost_typical_usd_ton": 6.0,
#    "selling_price_typical_usd_ton": 91.7,
#    ...},
#   {"raw_material": "pomza",
#    "route": "bims_aggregate",
#    "processing_cost_typical_usd_ton": 33.0,
#    "selling_price_typical_usd_ton": 55.0,
#    ...}
# ]
```

**📋 CLAUDE CODE PROMPT — ADIM 1:**

```markdown
🎯 ROL: Sen ML pipeline'ının veri mühendisisin. Master Excel'i parquet'lere dönüştüreceksin.

📁 GİRDİ:
- data/master/raw2value_master_v4_2026-05-02.xlsx (16 sheet)
- master_model_egitim_raporu.md Bölüm 5.1 (sheet → parquet eşleşmesi)

📤 ÇIKTI:
- data/reference/materials.parquet     (02_material_reference)
- data/reference/routes.parquet        (03_processing_routes)
- data/reference/organizations.parquet (04_organizations)
- data/reference/buyer_markets.parquet (05_buyer_markets)
- data/reference/distances.parquet     (09_geo_distance)
- data/reference/carbon.parquet        (10_carbon_factors — sadece hackathon_official rows)
- data/reference/fx_rates.parquet      (11_fx_rates)
- data/reference/risk_delivery.parquet (12_risk_quality, RISK/Delivery bloku)
- data/reference/risk_price.parquet    (12_risk_quality, RISK/Price bloku)
- data/reference/quality_match.parquet (12_risk_quality, QUALITY MATCH MATRIX bloku)
- data/reference/quality_demand.parquet(12_risk_quality, BUYER TYPICAL QUALITY DEMAND bloku)
- ml/src/etl.py (yeniden çalıştırılabilir module)
- ml/notebooks/01_data_prep.ipynb (etl.py'yi çağıran ve pandas info() ile doğrulayan)

🛠️ GÖREV:
1. ml/src/etl.py içine `extract_master_excel(xlsx_path: str, out_dir: str) -> dict[str, pd.DataFrame]` yaz.
2. Her sheet için tip dönüşümü:
   - Min/Max/Typical kolonlarını sayıya çevir (errors='coerce', sonra fillna(NaN)).
   - Lat/Lon float, kapasite int (NaN izin).
   - Tarih kolonlarını datetime'a çevir.
3. 12_risk_quality sheet'i 4 alt-bloğa bölünür ('RISK/Delivery', 'RISK/Price', 'QUALITY MATCH MATRIX', 'BUYER TYPICAL QUALITY DEMAND') — boş satırlar (None) ile ayrılmış. Bu blokları doğru parse et.
4. 10_carbon_factors'tan sadece `Faktor adi == 'hackathon_official'` olanları al; diğerleri (DEFRA/GLEC/EPA) cross-reference olarak başka parquet'e yaz: data/reference/carbon_alternatives.parquet
5. 09_geo_distance: Source ID + Destination ID kolonlarını composite key olarak kullan; lookup için index (Source, Destination) → (km, dakika) sözlüğü .pkl olarak da kaydet: data/reference/distance_lookup.pkl
6. Notebook'ta her parquet'i okuyup df.info() ve df.head() çıktısını göster.

✅ KABUL KRİTERLERİ:
- 10 parquet + 1 pkl üretildi.
- `pd.read_parquet("data/reference/routes.parquet")` döner ve `.dtypes` numerik kolonları float/int olarak gösterir (object değil).
- `pd.read_parquet("data/reference/distances.parquet").shape[0] == 535` (ilk satır header).
- Notebook hatasız çalışır.
- ml/src/etl.py içinde `python -m ml.src.etl --xlsx data/master/raw2value_master_v4_2026-05-02.xlsx --out data/reference/` çalışır.
```

---

### ADIM 2 — Reference loader modülü

**Amaç:** Parquet'leri Python objelere dönüştüren helper fonksiyonlar (backend de bunu kullanacak).

**Girdi (örnek):**
```python
from raw2value_ml.reference_loader import load_routes, load_organizations
routes = load_routes()  # → pd.DataFrame
orgs = load_organizations(filter_type="processor", material="pomza")  # → filtered df
```

**Çıktı (örnek):**
```python
>>> routes.query("raw_material == 'pomza'").head(2)
  raw_material           route  processing_cost_typical_usd_ton  selling_price_typical_usd_ton
0        pomza        raw_sale                              6.0                           91.7
1        pomza  bims_aggregate                             33.0                           55.0
```

**📋 CLAUDE CODE PROMPT — ADIM 2:**

```markdown
🎯 ROL: ML mühendisi. Reference loader modülünü yazacaksın.

📁 GİRDİ:
- data/reference/*.parquet (Adım 1'de üretildi)
- master_model_egitim_raporu.md Bölüm 11

📤 ÇIKTI:
- raw2value_ml/reference_loader.py (eksiksiz)
- ml/tests/test_reference_loader.py

🛠️ GÖREV:
raw2value_ml/reference_loader.py içine şu fonksiyonları yaz:

1. load_routes() → pd.DataFrame
2. load_organizations(filter_type=None, material=None, city=None) → filtered DataFrame
3. load_distances() → pd.DataFrame (composite indexed)
4. load_distance_lookup() → dict[tuple[str,str], dict] (.pkl'den)
5. load_carbon_factors() → dict[str, float] (transport_mode → emission_factor)
   Örnek: {"road": 0.100, "sea": 0.015, "air": 0.500, "rail": 0.030}
   NOT: 10_carbon_factors'taki kategori alanları:
        road_truck_HGV → "kara"/"road"
        sea_container → "deniz"/"sea"
        rail_freight → "demiryolu"/"rail"
        air_freight_long_haul → "hava"/"air"
6. load_quality_match_matrix() → dict[tuple[str,str], float]
   Örnek: {("A","A"): 1.00, ("A","B"): 1.00, ("A","C"): 0.95, ...}
7. load_delivery_risk(transport_mode: str) → float (typical değer)
8. load_price_volatility(material: str) → float
9. load_buyer_demand_score(country: str, sector: str) → float (0–1)
   - 05_buyer_markets'tan CAGR + USD_milyon_2024 normalize edip ortalamasını al
10. cache decoratoru kullan (functools.lru_cache) — her loader bir kez yüklesin.

Tüm dönüş tipleri annotated olsun. Module-level constant: REFERENCE_DIR = Path("data/reference").

ml/tests/test_reference_loader.py:
- 8 fonksiyon için pytest testi
- load_carbon_factors()["kara"] == 0.100 doğrulaması
- load_quality_match_matrix()[("A","A")] == 1.0 doğrulaması
- load_organizations(material="pomza") en az 13 satır döndürür

✅ KABUL KRİTERLERİ:
- pytest ml/tests/test_reference_loader.py geçer.
- python -c "from raw2value_ml.reference_loader import load_carbon_factors; print(load_carbon_factors())" çalışır ve 4 mode gösterir.
- Tüm fonksiyonların lru_cache decoratoru var.
```

---

### ADIM 3 — Augmentation pipeline

**Amaç:** ~78 referans satırdan 1.500 satır augmented training set üretmek.

**Girdi (örnek):**
```python
# Adım 1'de üretilen reference parquet'ler + 07_augmentation_rules
augmentation_config = {
    "target_rows": 1500,
    "material_distribution": {"pomza": 0.70, "perlit": 0.20, "kabak_cekirdegi": 0.10},
    "random_state": 42,
}
```

**Çıktı (örnek):**
```python
# data/processed/training_set_v1.parquet
>>> df = pd.read_parquet("data/processed/training_set_v1.parquet")
>>> df.shape
(1487, 38)  # 1487 satır (NaN drop sonrası), 38 kolon
>>> df["raw_material"].value_counts(normalize=True)
pomza              0.703
perlit             0.197
kabak_cekirdegi    0.100

>>> df["expected_profit_try"].describe()
count       1487
mean      482900
std       891200
min      -125000   # bazı kötü senaryolarda zarar — model bunu öğrenmeli
25%        87000
50%       312000
75%       649000
max     12450000
```

**📋 CLAUDE CODE PROMPT — ADIM 3:**

```markdown
🎯 ROL: ML mühendisi. Domain-informed augmentation pipeline'ını implemente edeceksin.

📁 GİRDİ:
- data/reference/*.parquet (Adım 1)
- raw2value_ml/reference_loader.py (Adım 2)
- master_model_egitim_raporu.md Bölüm 5 (özellikle 5.5 ve 5.6)

📤 ÇIKTI:
- ml/src/augmentation.py
- ml/src/targets.py (target hesaplama)
- ml/src/features.py (feature engineering)
- data/processed/training_set_v1.parquet
- ml/notebooks/02_augmentation.ipynb (görselleştirme + sanity check)
- ml/tests/test_augmentation_bounds.py
- ml/tests/test_no_target_leakage.py

🛠️ GÖREV:

PART A — ml/src/augmentation.py:
Sıralı pipeline (Bölüm 5.6'daki 10 adıma uygun):

```python
def build_training_set(
    target_rows: int = 1500,
    material_dist: dict = {"pomza": 0.70, "perlit": 0.20, "kabak_cekirdegi": 0.10},
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # 1. Bootstrap base rows (boş DataFrame target_rows uzunluğunda)
    rows = bootstrap_base_rows(target_rows, material_dist, rng)

    # 2. Sample categorical
    rows = sample_categorical_features(rows, rng)

    # 3. Lookup deterministic
    rows = lookup_prices_costs(rows)
    rows = lookup_distances(rows, rng)        # rng for source/processor/buyer choice
    rows = lookup_emission_factors(rows)
    rows = lookup_quality_match(rows)
    rows = lookup_delivery_risk(rows, rng)
    rows = compute_demand_score(rows)

    # 4. Apply noise
    rows = apply_price_noise(rows, sigma_pct=0.08, rng=rng)
    rows = apply_distance_noise(rows, sigma_pct=0.05, rng=rng)
    rows = apply_lead_time_noise(rows, sigma_abs=2.0, rng=rng)

    # 5. Compute formula features
    rows = compute_total_distance(rows)
    rows = compute_co2(rows)
    rows = compute_transport_cost(rows)

    # 6. Apply formula noise
    rows = apply_co2_measurement_noise(rows, sigma_pct=0.03, rng=rng)

    # 7. Sample fx scenario
    rows = sample_fx_scenario(rows, current_fx={"usd_try": 45.05, "eur_try": 52.67}, rng=rng)

    # 8. Compute targets
    from .targets import compute_targets
    rows = compute_targets(rows)

    # 9. Validate
    rows = validate_and_drop(rows)

    return rows
```

PART B — ml/src/targets.py:
- compute_expected_profit_try(row) → float (Bölüm 5.3.1 formülü)
- compute_value_uplift_pct(row) → float (Bölüm 5.3.2)
- compute_route_score(row, route) → float (Bölüm 5.3.3, 5 component'lı weighted)
- compute_recommended_route_label(row, candidate_routes) → str (argmax)
- compute_targets(df) → df with 4 target columns added

PART C — ml/src/features.py:
- M1_FEATURES list (Bölüm 6.5)
- M2_FEATURES list (Bölüm 7.5)
- BOOLEAN_FEATURES list (Bölüm 5.2.3)
- get_feature_split() → dict{numerical, categorical, boolean}

PART D — Sanity testleri:

ml/tests/test_augmentation_bounds.py:
- df = build_training_set(target_rows=200, seed=42)
- co2_kg > 0 her satırda
- expected_profit_try kolonu finite (no inf/NaN)
- raw_price_typical_usd_ton sınırlar içinde (02_material_reference min/max ± augmentation noise)
- emission_factor kara için 0.100, deniz için 0.015 (sadece typical noise sonrası)
- df["raw_material"].value_counts ratio'su 0.70/0.20/0.10'a yakın (±5%)
- co2_kg = tonnage × total_distance_km × emission_factor doğrulama (±%5 noise tolerance)

ml/tests/test_no_target_leakage.py (CRITICAL):
- M1_FEATURES içinde expected_profit_try YOK
- M1_FEATURES içinde value_uplift_pct YOK
- M1_FEATURES içinde recommended_route_label YOK
- M1_FEATURES içinde match_score YOK
- M2_FEATURES içinde processing_route_candidate YOK
- Diğer kombinasyonlar Bölüm 5.4'teki tabloyla uyumlu

PART E — Notebook (02_augmentation.ipynb):
- build_training_set() çalıştır
- Hammadde/rota dağılımı bar chart
- expected_profit_try histogram
- co2_kg vs total_distance_km scatter (transport_mode renk)
- df.describe() çıktısı

✅ KABUL KRİTERLERİ:
- pytest ml/tests/ tüm testler yeşil
- data/processed/training_set_v1.parquet üretildi, ~1500 satır
- df.isna().sum() — sadece advanced opsiyonel kolonlarda (moisture_pct, purity_pct) NaN olabilir
- Notebook end-to-end çalışıyor
- df["co2_kg"].mean() makul (yaklaşık 1000–10000 kg arası, mesafe ve tonaja göre)
```

---

### ADIM 4 — Feature pipeline (preprocessing)

**Amaç:** Ham feature DataFrame → modele verilebilir matris (sklearn ColumnTransformer).

**Girdi (örnek):**
```python
features_dict = {
    "raw_material": "pomza",
    "tonnage": 150,
    "quality_grade": "A",
    "origin_district": "Acıgöl",
    "processing_route_candidate": "micronized_pumice",
    "transport_mode": "kara",
    "total_distance_km": 1240,
    "usd_try": 45.05,
    # ... 30+ feature
}
```

**Çıktı (örnek):**
```python
>>> X = pipeline.transform(pd.DataFrame([features_dict]))
>>> X.shape
(1, 87)   # one-hot expanded
```

**📋 CLAUDE CODE PROMPT — ADIM 4:**

```markdown
🎯 ROL: ML mühendisi. Sklearn feature pipeline'ı kuracaksın.

📁 GİRDİ:
- data/processed/training_set_v1.parquet (Adım 3)
- ml/src/features.py (M1_FEATURES, M2_FEATURES tanımları)
- master_model_egitim_raporu.md Bölüm 5.2.4 (encoding stratejisi)

📤 ÇIKTI:
- ml/src/feature_pipeline.py
- models/feature_pipeline.pkl (joblib)
- ml/notebooks/02_augmentation.ipynb içine pipeline fit & test cell'i

🛠️ GÖREV:
ml/src/feature_pipeline.py:

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

def build_feature_pipeline(model_kind: str = "xgboost") -> ColumnTransformer:
    """
    model_kind:
      - "xgboost" / "lightgbm": one-hot for low-cardinality, label-encoded for high-card
      - "catboost": passthrough categorical (CatBoost native handling)
    """
    numerical_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        # GBDT için scaling şart değil, opsiyonel:
        # ("scale", StandardScaler())
    ])
    
    categorical_low = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="MISSING")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    # raw_material(3), quality_grade(4), transport_mode(4), priority(3), 
    # buyer_country(3), input_mode(2), product_form(5), particle_size_class(3) — düşük cardinality
    
    categorical_high = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="MISSING")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False, max_categories=20)),
    ])
    # origin_district, buyer_sector, buyer_city, processor_type, raw_subtype — orta cardinality
    
    transformer = ColumnTransformer([
        ("num", numerical_pipe, NUMERICAL_FEATURES),
        ("cat_low", categorical_low, LOW_CARDINALITY),
        ("cat_high", categorical_high, HIGH_CARDINALITY),
    ], remainder="drop")
    
    return transformer

def fit_and_save(df: pd.DataFrame, kind: str = "xgboost", out_path: str = "models/feature_pipeline.pkl"):
    pipe = build_feature_pipeline(kind)
    # Train için Model 1 ya da Model 2 column setine göre fit
    # NOT: M1 ve M2 farklı feature setlerine sahip → ya iki ayrı pipeline ya da union
    # MVP'de: tek pipeline, M1'in superset'i (processing_route_candidate dahil)
    pipe.fit(df[M1_FEATURES])
    joblib.dump(pipe, out_path)
    return pipe
```

Notebook'a bir test cell:
```python
import joblib
pipe = joblib.load("models/feature_pipeline.pkl")
X = pipe.transform(df[M1_FEATURES].head(3))
print(X.shape)
print(pipe.get_feature_names_out())
```

✅ KABUL KRİTERLERİ:
- models/feature_pipeline.pkl üretildi
- pipe.transform(df) hata vermez ve 1487 satır döner
- pipe.get_feature_names_out() ile ~80–100 expanded feature ismi gelir
- Yeni gelen kategorik değerlerde (handle_unknown="ignore") fail etmez
- joblib.load ile reload edilebilir
```

---

### ADIM 5 — Baseline modelleri (rule-based, LR, RF)

**Amaç:** GBDT'leri kıyaslayacağımız 3 baseline elde etmek.

**Girdi:** `data/processed/training_set_v1.parquet`

**Çıktı (örnek):**
```python
# baselines_results.json
{
  "rule_based":      {"profit_rmse": 285_000, "route_accuracy": 0.18},
  "linear_regression":{"profit_rmse": 215_000, "route_accuracy": 0.32},   # logistic for route
  "random_forest":   {"profit_rmse": 142_000, "route_accuracy": 0.51}
}
```

**📋 CLAUDE CODE PROMPT — ADIM 5:**

```markdown
🎯 ROL: ML mühendisi. Baseline modellerini kuracaksın.

📁 GİRDİ:
- data/processed/training_set_v1.parquet
- models/feature_pipeline.pkl
- ml/src/features.py

📤 ÇIKTI:
- ml/src/baselines.py
- ml/notebooks/03_baselines.ipynb
- data/processed/baseline_results.json

🛠️ GÖREV:

ml/src/baselines.py içine 3 baseline:

1. RuleBasedRegressor (sklearn-compat, profit için):
   - fit/predict pure formula
   - predict(X): processed_price - processing_cost - transport_cost - raw_price
   - Hiç öğrenmiyor; sadece formül doğrulayıcı

2. LinearRegression / LogisticRegression (sklearn standart)

3. RandomForestRegressor / RandomForestClassifier (n=200, max_depth=10, random_state=42)

Notebook (03_baselines.ipynb):
- df.read → train/val/test split (Bölüm 5.7'deki stratified 80/10/10)
- 3 baseline fit + evaluate (RMSE, MAE, R² for profit; accuracy, macro-f1, top-2 acc for route)
- baseline_results.json'a yaz
- Confusion matrix görsel (route classifier için)
- Bir bar chart: "Baseline comparison"

✅ KABUL KRİTERLERİ:
- baseline_results.json üretildi
- random_forest profit RMSE < linear_regression profit RMSE (genelde)
- random_forest route accuracy > 0.30 (random'dan 5x iyi)
- Notebook çalışıyor
```

---

### ADIM 6 — GBDT benchmark (XGBoost / LightGBM / CatBoost)

**Amaç:** 3 GBDT'yi train et, en iyisini seç.

**Girdi:** Adım 4 + Adım 5 çıktıları

**Çıktı (örnek):**
```
models/model_profit.pkl       (best of XGB/LGB/CB regressor)
models/model_route.pkl        (best of XGB/LGB/CB classifier)
data/processed/gbm_results.json
```

**📋 CLAUDE CODE PROMPT — ADIM 6:**

```markdown
🎯 ROL: ML mühendisi. GBDT benchmark'ı yapacaksın.

📁 GİRDİ:
- data/processed/training_set_v1.parquet
- models/feature_pipeline.pkl
- master_model_egitim_raporu.md Bölüm 6, 7

📤 ÇIKTI:
- ml/src/train_profit.py
- ml/src/train_route.py
- models/model_profit.pkl
- models/model_route.pkl
- data/processed/gbm_results.json
- ml/notebooks/04_gbm_benchmark.ipynb
- Görseller: feature_importance bar chart, predicted vs actual scatter, confusion matrix

🛠️ GÖREV:

ml/src/train_profit.py:
```python
def train_profit_models(df, pipeline, params: dict):
    X = pipeline.transform(df[M1_FEATURES])
    y = df["expected_profit_try"]
    
    train, val, test = stratified_split(...)  # %80/10/10
    
    results = {}
    for kind, model_cls, param_set in [
        ("xgboost",  XGBRegressor,  XGBOOST_PARAMS),
        ("lightgbm", LGBMRegressor, LIGHTGBM_PARAMS),
        ("catboost", CatBoostRegressor, CATBOOST_PARAMS),
    ]:
        model = model_cls(**param_set)
        # NOT: catboost cat_features parametresi ayrı verilmeli
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], early_stopping_rounds=30)
        y_pred = model.predict(X_test)
        results[kind] = {
            "rmse": rmse(y_test, y_pred),
            "mae": mae(y_test, y_pred),
            "r2": r2(y_test, y_pred),
            "mape": mape(y_test, y_pred),
            "train_sec": elapsed,
        }
    
    # Pick best by RMSE
    best_kind = min(results, key=lambda k: results[k]["rmse"])
    joblib.dump(best_models[best_kind], "models/model_profit.pkl")
    return results, best_kind
```

ml/src/train_route.py:
- Aynı pattern, ama `XGBClassifier(objective='multi:softprob')`, `LGBMClassifier(objective='multiclass')`, `CatBoostClassifier(loss_function='MultiClass')`
- Class weight balanced
- Metrics: accuracy, macro_f1, weighted_f1, top_2_accuracy
- En iyi macro_f1'e göre seç

Notebook 04_gbm_benchmark.ipynb:
- 3 model train edilir
- Sonuçlar tablo halinde gösterilir
- Best model seçilir, kaydedilir
- Feature importance Top-15 bar chart (her iki model için)
- Predicted vs actual scatter (regression)
- Confusion matrix (classification)
- gbm_results.json'a yaz

✅ KABUL KRİTERLERİ:
- models/model_profit.pkl ve models/model_route.pkl üretildi
- gbm_results.json'da 3 GBDT'nin metrikleri ve "best_model" alanı var
- En iyi GBDT'nin RMSE'si Random Forest'tan düşük (genelde)
- Feature importance plot'u total_distance_km, usd_try, processed_price gibi feature'ları üst sıralarda gösteriyor (sanity check)
- Yüklenebilirlik: joblib.load("models/model_profit.pkl").predict(X_sample) çalışıyor
```

---

### ADIM 7 — Ablation çalışması

**Amaç:** K1 (karbon), K2 (kur), K3 (geo) feature gruplarının modele ne kadar değer kattığını ölçmek.

**Girdi:** Adım 6 sonrası

**Çıktı (örnek):**
```json
{
  "ablation": {
    "full_features":   {"profit_rmse": 142_000, "route_macro_f1": 0.62},
    "without_fx":      {"profit_rmse": 168_000, "route_macro_f1": 0.55, "rmse_delta_pct": "+18%"},
    "without_geo":     {"profit_rmse": 195_000, "route_macro_f1": 0.50, "rmse_delta_pct": "+37%"},
    "without_carbon":  {"profit_rmse": 152_000, "route_macro_f1": 0.59, "rmse_delta_pct": "+7%"},
    "without_demand":  {"profit_rmse": 175_000, "route_macro_f1": 0.53, "rmse_delta_pct": "+23%"}
  }
}
```

**📋 CLAUDE CODE PROMPT — ADIM 7:**

```markdown
🎯 ROL: ML mühendisi. Ablation çalışmasını yapacaksın.

📁 GİRDİ:
- ml/src/train_profit.py, train_route.py (Adım 6)
- data/processed/training_set_v1.parquet
- master_model_egitim_raporu.md Bölüm 10.2

📤 ÇIKTI:
- ml/src/ablation.py
- data/processed/ablation_results.json
- ml/notebooks/05_ablation.ipynb

🛠️ GÖREV:

ml/src/ablation.py:
```python
ABLATION_GROUPS = {
    "full_features": [],  # baseline, hiçbir şey çıkarılmaz
    "without_fx": ["usd_try", "eur_try", "fx_scenario_pct"],
    "without_geo": ["source_to_processor_km", "processor_to_buyer_km", "total_distance_km"],
    "without_carbon": ["emission_factor_kg_co2_ton_km", "co2_kg"],
    "without_demand": ["demand_score", "buyer_sector", "buyer_country"],
    "without_quality": ["quality_grade", "quality_match_score", "moisture_pct", "purity_pct"],
    "without_cost": ["processing_cost_typical_usd_ton", "packaging_cost_usd_ton", "transport_cost_usd_ton_km"],
}

def run_ablation(df: pd.DataFrame, best_model_kind: str) -> dict:
    results = {}
    for ablation_name, features_to_remove in ABLATION_GROUPS.items():
        feats = [f for f in M1_FEATURES if f not in features_to_remove]
        X = preprocess_subset(df, feats)
        # Ayrı pipeline + ayrı model fit (full retrain)
        ...
        results[ablation_name] = {
            "profit_rmse": ...,
            "profit_mae": ...,
            "route_macro_f1": ...,
            "rmse_delta_pct": (rmse - full_rmse) / full_rmse * 100,
            "interpretation": ABLATION_INTERPRETATIONS[ablation_name],
        }
    return results
```

Notebook 05_ablation.ipynb:
- Tüm ablasyonları çalıştır (~5–10 dakika)
- Sonuçları DataFrame'e yaz, sıralı göster (delta'ya göre)
- Bar chart: "Feature group → RMSE delta"
- Heatmap: ablation × metric matrix
- ablation_results.json'a yaz

✅ KABUL KRİTERLERİ:
- ablation_results.json üretildi (7 senaryo: full + 6 ablasyon)
- En azından bir ablasyon (genellikle without_geo) RMSE'yi anlamlı şekilde (>10%) bozuyor → kanıt sağlandı
- Notebook çalışıyor
- Yorum cümleleri Bölüm 10.2'deki metinlerle uyumlu
```

---

### ADIM 8 — Reason codes + confidence + feature importance

**Amaç:** Model çıktısının yanına Türkçe açıklama ve güven skoru üretmek.

**📋 CLAUDE CODE PROMPT — ADIM 8:**

```markdown
🎯 ROL: ML mühendisi. Açıklanabilirlik katmanını yazacaksın.

📁 GİRDİ:
- models/model_profit.pkl, model_route.pkl
- master_model_egitim_raporu.md Bölüm 9

📤 ÇIKTI:
- raw2value_ml/reasons.py
- raw2value_ml/confidence.py
- ml/tests/test_reasons.py, test_confidence.py

🛠️ GÖREV:

raw2value_ml/reasons.py:

```python
REASON_TEMPLATES = {
    "total_distance_km": {
        "high": "{total_distance_km:.0f} km mesafe lojistik maliyeti yükseltiyor.",
        "low":  "{total_distance_km:.0f} km kısa mesafe maliyet avantajı sağlıyor.",
    },
    "usd_try": {
        "high": "USD/TRY {usd_try:.2f} ihracat gelirini güçlendiriyor.",
        "low":  "USD/TRY {usd_try:.2f} ihracat gelirini sınırlıyor.",
    },
    "co2_kg": {
        "high": "{co2_kg:.0f} kg CO₂ karbon ayak izini büyütüyor.",
        "low":  "{co2_kg:.0f} kg CO₂ ile düşük karbon avantajı var.",
    },
    "demand_score": {
        "high": "Hedef pazardaki talep skoru {demand_score:.2f} — pazar uygun.",
        "low":  "Hedef pazar talep skoru {demand_score:.2f} — alternatif pazar düşünülebilir.",
    },
    "quality_match_score": {
        "high": "Kalite uyumu yüksek ({quality_match_score:.2f}) — alıcı talebine uygun.",
        "low":  "Kalite uyumu düşük ({quality_match_score:.2f}) — fiyat penalty olası.",
    },
    "tonnage": {
        "high": "{tonnage:.0f} ton büyük tonaj birim maliyeti düşürüyor.",
        "low":  "{tonnage:.0f} ton küçük tonaj birim maliyeti yükseltiyor.",
    },
    "delivery_risk": {
        "high": "Teslim risk skoru {delivery_risk:.2f} yüksek — alternatif transport önerilebilir.",
        "low":  "Teslim risk skoru {delivery_risk:.2f} düşük — operasyonel istikrar yüksek.",
    },
    # 8+ template eklemen lazım
}

FEATURE_MEDIANS = {}  # eğitim sırasında hesaplanır, JSON'a kaydedilir

def generate_reason_codes(features: dict, model, top_k: int = 3) -> list[dict]:
    importances = dict(zip(model.feature_names_in_, model.feature_importances_))
    top_features = sorted(importances.items(), key=lambda x: -x[1])[:top_k]
    
    reasons = []
    for fname, imp in top_features:
        if fname not in REASON_TEMPLATES:
            continue
        value = features.get(fname)
        median = FEATURE_MEDIANS.get(fname, 0)
        is_high = value > median
        template = REASON_TEMPLATES[fname]["high" if is_high else "low"]
        reasons.append({
            "feature": fname,
            "importance": float(imp),
            "value": value,
            "text": template.format(**features),
        })
    return reasons
```

raw2value_ml/confidence.py:

```python
def compute_data_confidence(features: dict) -> int:
    score = 100
    if not features.get("technical_data_available", False):
        score -= 15
    if features.get("raw_price_source_confidence") in ("C", "D"):
        score -= 10
    if features.get("processor_capacity_confidence") in ("C", "D"):
        score -= 5
    if features.get("fx_source") == "TCMB_LIVE":
        score += 10
    if features.get("distance_source") == "ORS_LIVE":
        score += 5
    return max(0, min(100, score))

def compute_model_confidence(prediction_proba=None, ensemble_disagreement=None) -> int:
    if prediction_proba is not None:
        return int(max(prediction_proba) * 100)
    return 75  # default

def compute_overall_confidence(features, prediction_proba=None) -> dict:
    data_conf = compute_data_confidence(features)
    model_conf = compute_model_confidence(prediction_proba)
    overall_pct = data_conf * 0.4 + model_conf * 0.6
    
    warnings = []
    if not features.get("technical_data_available"):
        warnings.append("Teknik analiz verisi girilmedi; sistem bölgesel varsayılanları kullandı.")
    if features.get("default_values_used"):
        warnings.append("Bazı değerler için varsayılan kullanıldı; güven skoru düşürüldü.")
    
    return {
        "data_confidence": data_conf,
        "model_confidence": model_conf,
        "overall": round(overall_pct, 1),
        "warnings": warnings,
    }
```

Testler:
- 6+ template doğrulanır
- Confidence < 70 olan örnek için warning üretildi mi?
- Confidence 100 → her şey ideal

✅ KABUL KRİTERLERİ:
- pytest tüm reasons + confidence testleri yeşil
- Örnek bir feature dict ile generate_reason_codes 3 Türkçe cümle döndürüyor
- compute_overall_confidence dict'i 4 alan (data, model, overall, warnings) içeriyor
```

---

### ADIM 9 — B2B Match Scorer

**📋 CLAUDE CODE PROMPT — ADIM 9:**

```markdown
🎯 ROL: ML mühendisi. B2B weighted match scorer'ı yazacaksın.

📁 GİRDİ:
- raw2value_ml/reference_loader.py (quality matrix, demand scores)
- master_model_egitim_raporu.md Bölüm 8

📤 ÇIKTI:
- raw2value_ml/scorer.py
- ml/tests/test_scorer.py

🛠️ GÖREV:

raw2value_ml/scorer.py:

```python
WEIGHT_PROFILES = {
    "max_profit":    {"profit": 0.35, "demand": 0.20, "distance": 0.15, "carbon": 0.15, "delivery": 0.10, "quality": 0.05},
    "low_carbon":    {"profit": 0.25, "demand": 0.15, "distance": 0.10, "carbon": 0.30, "delivery": 0.15, "quality": 0.05},
    "fast_delivery": {"profit": 0.25, "demand": 0.15, "distance": 0.20, "carbon": 0.10, "delivery": 0.25, "quality": 0.05},
}

MAX_DISTANCE_KM = 3000   # normalize için (TR-DE kara)
MAX_CO2_KG = 200_000

def compute_match_score(
    producer: dict,
    processor: dict,
    buyer: dict,
    context: dict,           # {co2, fx, predicted_profit, ...}
    priority: str = "max_profit",
) -> tuple[float, dict]:
    weights = WEIGHT_PROFILES[priority]
    
    profit_score   = clip(context["predicted_profit"] / 1_000_000, 0, 1)  # normalize
    demand_score   = lookup_buyer_demand(buyer["country"], buyer["sector"])
    distance_score = 1 - clip(context["total_distance_km"] / MAX_DISTANCE_KM, 0, 1)
    carbon_score   = 1 - clip(context["co2_kg"] / MAX_CO2_KG, 0, 1)
    delivery_score = 1 - lookup_delivery_risk(context["transport_mode"])
    quality_score  = lookup_quality_match(producer["quality_grade"], buyer["required_grade"])
    
    components = {
        "profit": profit_score, "demand": demand_score, "distance": distance_score,
        "carbon": carbon_score, "delivery": delivery_score, "quality": quality_score,
    }
    
    score = sum(weights[k] * components[k] for k in weights)
    return score, components

def match_buyers(
    producer: dict,
    candidates: list[tuple[dict, dict]],  # [(processor, buyer), ...]
    context: dict,
    priority: str = "max_profit",
    top_k: int = 5,
) -> list[dict]:
    scored = []
    for processor, buyer in candidates:
        score, components = compute_match_score(producer, processor, buyer, context, priority)
        scored.append({
            "processor": processor,
            "buyer": buyer,
            "score": score,
            "components": components,
        })
    return sorted(scored, key=lambda x: -x["score"])[:top_k]
```

Test (test_scorer.py):
- max_profit profilinde "yakın+yüksek kâr" kombinasyonu en üstte
- low_carbon profili aktifken "deniz transport+düşük CO2" kombinasyonu öne geçiyor
- top_k=5 her zaman 5 (veya len(candidates)) sonuç döndürüyor
- score sınırı 0–1 arası

✅ KABUL KRİTERLERİ:
- 4+ test geçiyor
- WEIGHT_PROFILES'da her profilin sum == 1.0
- match_buyers([], ...) boş liste döndürüyor (defensive)
```

---

### ADIM 10 — Inference modülü (analyze fonksiyonu)

**📋 CLAUDE CODE PROMPT — ADIM 10:**

```markdown
🎯 ROL: ML mühendisi. Backend'in çağıracağı analyze() fonksiyonunu yazacaksın.

📁 GİRDİ:
- Tüm önceki adımların çıktıları
- master_model_egitim_raporu.md Bölüm 11.3 (kontrat)

📤 ÇIKTI:
- raw2value_ml/inference.py (eksiksiz)
- raw2value_ml/schemas.py (pydantic models)
- raw2value_ml/geo.py (distance lookup)
- raw2value_ml/carbon.py (CO2 hesabı)
- raw2value_ml/fx.py (what-if scenarios)
- ml/tests/test_inference_smoke.py

🛠️ GÖREV:

raw2value_ml/schemas.py — pydantic v2:

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class LiveFx(BaseModel):
    usd_try: float
    eur_try: float
    last_updated: str

class AnalyzePayload(BaseModel):
    raw_material: Literal["pomza", "perlit", "kabak_cekirdegi"]
    tonnage: float = Field(gt=0, le=100_000)
    quality: Literal["A", "B", "C", "unknown"]
    origin_city: str
    target_country: Literal["TR", "DE", "NL"]
    target_city: Optional[str] = None
    transport_mode: Literal["kara", "deniz", "demiryolu", "hava"]
    priority: Literal["max_profit", "low_carbon", "fast_delivery"] = "max_profit"
    input_mode: Literal["basic", "advanced"] = "basic"
    moisture_pct: Optional[float] = None
    purity_pct: Optional[float] = None
    particle_size_class: Optional[str] = None
    fx_scenario_pct: float = 0.0
    cost_scenario_pct: float = 0.0
    live_fx: LiveFx

class RouteOption(BaseModel):
    route: str
    predicted_profit_try: float
    value_uplift_pct: float
    co2_kg: float
    route_probability: float

class ReasonCode(BaseModel):
    feature: str
    importance: float
    value: float | str
    text: str

class MatchResult(BaseModel):
    processor_name: str
    buyer_name: str
    score: float
    components: dict[str, float]

class ConfidenceBreakdown(BaseModel):
    data_confidence: int
    model_confidence: int
    overall: float
    warnings: list[str]

class FeatureImportance(BaseModel):
    feature: str
    importance: float

class AnalyzeResponse(BaseModel):
    recommended_route: str
    route_alternatives: list[RouteOption]
    expected_profit_try: float
    value_uplift_pct: float
    co2_kg: float
    co2_tonnes: float
    match_results: list[MatchResult]
    reason_codes: list[ReasonCode]
    confidence: ConfidenceBreakdown
    feature_importance: list[FeatureImportance]
    warnings: list[str]
```

raw2value_ml/geo.py:
```python
from .reference_loader import load_distance_lookup, load_organizations

def lookup_distance(origin_city: str, destination_city: str, transport_mode: str) -> dict:
    lookup = load_distance_lookup()
    # Try direct match
    for src_id, dst_id in find_id_pairs(origin_city, destination_city):
        if (src_id, dst_id) in lookup:
            return {**lookup[(src_id, dst_id)], "source": "ORS_PRECOMPUTED"}
    # Fallback: Haversine
    return haversine_fallback(origin_city, destination_city)

def find_nearby_processors(origin_city: str, raw_material: str, radius_km: int = 200) -> list[dict]:
    orgs = load_organizations(filter_type="processor", material=raw_material)
    distances = load_distances()
    # Filter by distance
    ...
    return list_of_processors_within_radius
```

raw2value_ml/carbon.py:
```python
from .reference_loader import load_carbon_factors

def compute_co2(tonnage: float, distance_km: float, transport_mode: str) -> float:
    factors = load_carbon_factors()
    factor = factors[transport_mode]
    return tonnage * distance_km * factor
```

raw2value_ml/fx.py:
```python
def apply_fx_scenario(live_fx: dict, scenario_pct: float) -> dict:
    multiplier = 1 + scenario_pct
    return {
        "usd_try": live_fx["usd_try"] * multiplier,
        "eur_try": live_fx["eur_try"] * multiplier,
        "fx_scenario_pct": scenario_pct,
        "fx_source": "TCMB_LIVE",
    }
```

raw2value_ml/inference.py:

```python
import joblib
import json
import pandas as pd
from .schemas import AnalyzePayload, AnalyzeResponse, RouteOption, MatchResult, ReasonCode, FeatureImportance, ConfidenceBreakdown
from .scorer import match_buyers
from .reasons import generate_reason_codes
from .confidence import compute_overall_confidence
from .geo import lookup_distance, find_nearby_processors
from .carbon import compute_co2
from .fx import apply_fx_scenario

# Lazy load
_state = {"loaded": False}

def _load():
    if _state["loaded"]:
        return
    _state["model_profit"] = joblib.load("models/model_profit.pkl")
    _state["model_route"] = joblib.load("models/model_route.pkl")
    _state["pipeline"] = joblib.load("models/feature_pipeline.pkl")
    _state["metadata"] = json.load(open("models/metadata.json"))
    _state["loaded"] = True

def analyze(payload: AnalyzePayload) -> AnalyzeResponse:
    _load()
    
    # 1. Default doldur
    features = fill_defaults(payload, _state["metadata"]["default_values"])
    
    # 2. Geo + Carbon
    distances = lookup_distance(payload.origin_city, payload.target_city or _default_buyer_city(payload.target_country), payload.transport_mode)
    co2_kg = compute_co2(payload.tonnage, distances["total_km"], payload.transport_mode)
    features.update({**distances, "co2_kg": co2_kg})
    
    # 3. FX what-if
    fx = apply_fx_scenario(payload.live_fx.dict(), payload.fx_scenario_pct)
    features.update(fx)
    
    # 4. Model 2: route prediction → top 3
    X_route = _state["pipeline"].transform(pd.DataFrame([features])[M2_FEATURES])
    route_proba = _state["model_route"].predict_proba(X_route)[0]
    classes = _state["metadata"]["models"]["route"]["classes"]
    top3 = sorted(zip(classes, route_proba), key=lambda x: -x[1])[:3]
    
    # 5. Her aday rota için Model 1: profit
    route_alternatives = []
    for route_name, prob in top3:
        feats = {**features, "processing_route_candidate": route_name}
        X_profit = _state["pipeline"].transform(pd.DataFrame([feats])[M1_FEATURES])
        predicted_profit = float(_state["model_profit"].predict(X_profit)[0])
        value_uplift = compute_uplift(predicted_profit, feats)
        route_alternatives.append(RouteOption(
            route=route_name,
            predicted_profit_try=predicted_profit,
            value_uplift_pct=value_uplift,
            co2_kg=co2_kg,
            route_probability=float(prob),
        ))
    
    recommended = max(route_alternatives, key=lambda r: r.predicted_profit_try)
    
    # 6. B2B match
    nearby = find_nearby_processors(payload.origin_city, payload.raw_material, radius_km=200)
    buyers = filter_buyers_for_route(recommended.route, payload.target_country)
    candidates = [(p, b) for p in nearby[:10] for b in buyers[:10]]
    matches = match_buyers(features, candidates, {**features, "predicted_profit": recommended.predicted_profit_try}, payload.priority, top_k=5)
    
    # 7. Reasons
    reasons = generate_reason_codes(features, _state["model_profit"], top_k=3)
    
    # 8. Confidence
    confidence = compute_overall_confidence(features, route_proba)
    
    # 9. Feature importance (model_evidence.json'dan, hızlı)
    fi = _state["metadata"].get("top_features", [])[:10]
    
    return AnalyzeResponse(
        recommended_route=recommended.route,
        route_alternatives=route_alternatives,
        expected_profit_try=recommended.predicted_profit_try,
        value_uplift_pct=recommended.value_uplift_pct,
        co2_kg=co2_kg,
        co2_tonnes=co2_kg / 1000,
        match_results=[MatchResult(**m) for m in matches],
        reason_codes=[ReasonCode(**r) for r in reasons],
        confidence=ConfidenceBreakdown(**confidence),
        feature_importance=[FeatureImportance(**f) for f in fi],
        warnings=confidence["warnings"],
    )
```

Test (test_inference_smoke.py):
```python
def test_analyze_basic_pomza():
    payload = AnalyzePayload(
        raw_material="pomza", tonnage=150, quality="A",
        origin_city="Nevşehir", target_country="DE",
        target_city="Hamburg", transport_mode="kara",
        priority="max_profit", input_mode="basic",
        live_fx=LiveFx(usd_try=45.05, eur_try=52.67, last_updated="2026-05-02"),
    )
    response = analyze(payload)
    assert response.recommended_route in VALID_ROUTES
    assert response.expected_profit_try > 0  # makul senaryoda
    assert len(response.route_alternatives) == 3
    assert len(response.match_results) <= 5
    assert len(response.reason_codes) == 3
    assert 0 <= response.confidence.overall <= 100
```

✅ KABUL KRİTERLERİ:
- test_inference_smoke.py geçer
- analyze() <500ms (warm) çalışır
- Response pydantic validation'dan geçer
- recommended_route ∈ {16 known routes}
- match_results en fazla 5 kayıt
- reason_codes tam 3 cümle (Türkçe)
- confidence.warnings list (boş veya dolu)
```

---

### ADIM 11 — Model Evidence çıktısı

**📋 CLAUDE CODE PROMPT — ADIM 11:**

```markdown
🎯 ROL: ML mühendisi. Model Evidence ekranı için JSON çıktıyı üretiyorsun.

📁 GİRDİ:
- gbm_results.json (Adım 6)
- ablation_results.json (Adım 7)
- baseline_results.json (Adım 5)

📤 ÇIKTI:
- models/model_evidence.json
- models/metadata.json (eğer henüz değilse complete et)

🛠️ GÖREV:

ml/src/evidence.py:
```python
def build_model_evidence() -> dict:
    return {
        "version": "v1.0",
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "dataset": {...},  # row counts, split strategy, augmentation
        "profit_regression": load_json("data/processed/baseline_results.json")["profit"]
                             | load_json("data/processed/gbm_results.json")["profit"],
        "route_classification": load_json("data/processed/baseline_results.json")["route"]
                                | load_json("data/processed/gbm_results.json")["route"],
        "ablation": load_json("data/processed/ablation_results.json"),
        "feature_importance": {
            "model_profit": top_features(joblib.load("models/model_profit.pkl"), k=15),
            "model_route":  top_features(joblib.load("models/model_route.pkl"), k=15),
        },
        "honesty_note": "Sayılar augmented holdout üzerinde ölçüldü. Pilot gerçek veriyle yeniden kalibre edilecektir.",
    }

def build_metadata() -> dict:
    # Bölüm 11.2'deki yapı
    ...
```

Notebook 06_export_artifacts.ipynb:
- evidence.py'yi çalıştır
- model_evidence.json ve metadata.json'u models/ altına yaz
- Görsel: feature importance comparison plot

✅ KABUL KRİTERLERİ:
- models/model_evidence.json Bölüm 10.1'deki yapıya uygun
- models/metadata.json Bölüm 11.2'deki yapıya uygun
- Frontend bu JSON'u Model Evidence ekranında doğrudan kullanabilir
- "honesty_note" alanı var
```

---

### ADIM 12 — Public API + Package install

**📋 CLAUDE CODE PROMPT — ADIM 12:**

```markdown
🎯 ROL: ML mühendisi. Paketi backend'in import edebileceği hâle getiriyorsun.

📁 GİRDİ: Tüm önceki adımlar.

📤 ÇIKTI:
- raw2value_ml/__init__.py (public API)
- pyproject.toml güncelle (entry_points opsiyonel)
- README.md (ML kullanım bölümü)

🛠️ GÖREV:

raw2value_ml/__init__.py:
```python
"""Raw2Value AI — ML inference package."""

__version__ = "0.1.0"

from .inference import analyze
from .scorer import match_buyers, compute_match_score, WEIGHT_PROFILES
from .schemas import (
    AnalyzePayload, AnalyzeResponse, LiveFx,
    RouteOption, MatchResult, ReasonCode,
    ConfidenceBreakdown, FeatureImportance,
)

__all__ = [
    "analyze",
    "match_buyers", "compute_match_score", "WEIGHT_PROFILES",
    "AnalyzePayload", "AnalyzeResponse", "LiveFx",
    "RouteOption", "MatchResult", "ReasonCode",
    "ConfidenceBreakdown", "FeatureImportance",
]
```

README.md (ML bölümü ekle):

```markdown
## ML inference (backend için)

```python
from raw2value_ml import analyze, AnalyzePayload, LiveFx

payload = AnalyzePayload(
    raw_material="pomza",
    tonnage=150,
    quality="A",
    origin_city="Nevşehir",
    target_country="DE",
    transport_mode="kara",
    priority="max_profit",
    live_fx=LiveFx(usd_try=45.05, eur_try=52.67, last_updated="2026-05-02"),
)
response = analyze(payload)
print(response.recommended_route, response.expected_profit_try)
```

### Eğitim
```bash
jupyter notebook ml/notebooks/01_data_prep.ipynb   # 1. ETL
jupyter notebook ml/notebooks/02_augmentation.ipynb # 2. Augmentation
jupyter notebook ml/notebooks/03_baselines.ipynb   # 3. Baselines
jupyter notebook ml/notebooks/04_gbm_benchmark.ipynb # 4. GBDT
jupyter notebook ml/notebooks/05_ablation.ipynb    # 5. Ablation
jupyter notebook ml/notebooks/06_export_artifacts.ipynb # 6. Export
```
```

✅ KABUL KRİTERLERİ:
- pip install -e . ile paket kurulur
- python -c "from raw2value_ml import analyze" hata vermez
- README ML bölümü güncel
```

---

### ADIM 13 — End-to-end smoke test

**📋 CLAUDE CODE PROMPT — ADIM 13:**

```markdown
🎯 ROL: ML mühendisi. Tüm pipeline'ın baştan sona çalıştığını doğruluyorsun.

📁 GİRDİ: Tüm önceki adımlar.

📤 ÇIKTI:
- ml/tests/test_e2e.py
- scripts/run_full_pipeline.sh

🛠️ GÖREV:

ml/tests/test_e2e.py:
```python
"""End-to-end smoke test: backend integration için kontrat doğrulaması."""

import pytest
from raw2value_ml import analyze, AnalyzePayload, LiveFx

@pytest.fixture
def sample_payload_pomza_de():
    return AnalyzePayload(
        raw_material="pomza", tonnage=150, quality="A",
        origin_city="Nevşehir", target_country="DE", target_city="Hamburg",
        transport_mode="kara", priority="max_profit", input_mode="basic",
        live_fx=LiveFx(usd_try=45.05, eur_try=52.67, last_updated="2026-05-02"),
    )

def test_basic_analyze(sample_payload_pomza_de):
    response = analyze(sample_payload_pomza_de)
    assert response.recommended_route is not None
    assert len(response.route_alternatives) == 3
    assert response.confidence.overall > 0

def test_what_if_fx_changes_recommendation(sample_payload_pomza_de):
    # Default kurda
    base = analyze(sample_payload_pomza_de)
    # USD %20 düşerse
    sample_payload_pomza_de.fx_scenario_pct = -0.20
    low_fx = analyze(sample_payload_pomza_de)
    # En azından profit değişti
    assert abs(base.expected_profit_try - low_fx.expected_profit_try) > 1000

def test_low_carbon_priority_changes_match_order(sample_payload_pomza_de):
    sample_payload_pomza_de.priority = "max_profit"
    profit_match = analyze(sample_payload_pomza_de)
    sample_payload_pomza_de.priority = "low_carbon"
    carbon_match = analyze(sample_payload_pomza_de)
    # Match order değişebilir (deterministik test zor — sadece response döndüğünü doğrula)
    assert len(carbon_match.match_results) > 0

def test_basic_mode_warning():
    payload = AnalyzePayload(
        raw_material="pomza", tonnage=50, quality="unknown",
        origin_city="Acıgöl", target_country="TR", transport_mode="kara",
        input_mode="basic",  # advanced fields yok
        live_fx=LiveFx(usd_try=45.05, eur_try=52.67, last_updated="2026-05-02"),
    )
    response = analyze(payload)
    assert any("teknik" in w.lower() or "varsayılan" in w.lower() for w in response.warnings)

def test_kabak_cekirdegi_path():
    payload = AnalyzePayload(
        raw_material="kabak_cekirdegi", tonnage=30, quality="A",
        origin_city="Acıgöl", target_country="TR", target_city="İstanbul",
        transport_mode="kara", priority="max_profit", input_mode="advanced",
        moisture_pct=8.0, purity_pct=98.0,
        live_fx=LiveFx(usd_try=45.05, eur_try=52.67, last_updated="2026-05-02"),
    )
    response = analyze(payload)
    valid_routes = ["bulk_sale", "roasted_packaged", "pumpkin_seed_oil", "protein_powder", "tourism_gift_pack"]
    assert response.recommended_route in valid_routes
```

scripts/run_full_pipeline.sh:
```bash
#!/usr/bin/env bash
set -euo pipefail
echo "Step 1: ETL"
jupyter nbconvert --execute --to html ml/notebooks/01_data_prep.ipynb
echo "Step 2: Augmentation"
jupyter nbconvert --execute --to html ml/notebooks/02_augmentation.ipynb
echo "Step 3: Baselines"
jupyter nbconvert --execute --to html ml/notebooks/03_baselines.ipynb
echo "Step 4: GBM"
jupyter nbconvert --execute --to html ml/notebooks/04_gbm_benchmark.ipynb
echo "Step 5: Ablation"
jupyter nbconvert --execute --to html ml/notebooks/05_ablation.ipynb
echo "Step 6: Export"
jupyter nbconvert --execute --to html ml/notebooks/06_export_artifacts.ipynb
echo "Step 7: Tests"
pytest ml/tests/ -v
echo "✅ Pipeline complete!"
```

✅ KABUL KRİTERLERİ:
- pytest ml/tests/test_e2e.py geçer (5+ test)
- bash scripts/run_full_pipeline.sh end-to-end çalışır (~10–15 dakika)
- Hiçbir test runtime warning fırlatmıyor (DeprecationWarning hariç)
- Backend bu noktada sadece "import et + analyze() çağır" yaparak entegre olabilir
```

---

## 13. BACKEND'E GEÇMEDEN ÖNCE — DONE TANIMI (kabul checklist'i)

Bu listede her madde TAMAMLANDI işaretlendiğinde model katmanı bitmiştir ve backend'e güvenle geçilebilir.

### 13.1 Veri katmanı

- [ ] `data/master/raw2value_master_v4_2026-05-02.xlsx` repo'ya commit edildi
- [ ] `data/reference/` altında 10 parquet + 1 pkl üretildi
- [ ] `data/processed/training_set_v1.parquet` ~1.500 satır, 38+ kolon
- [ ] Veri dağılımı: pomza %70, perlit %20, kabak çekirdeği %10 (±%5 tolerans)
- [ ] `pytest ml/tests/test_augmentation_bounds.py` yeşil
- [ ] `pytest ml/tests/test_no_target_leakage.py` yeşil

### 13.2 Model katmanı

- [ ] `models/feature_pipeline.pkl` üretildi, joblib.load çalışıyor
- [ ] `models/model_profit.pkl` üretildi (XGB ya da LGB ya da CatBoost)
- [ ] `models/model_route.pkl` üretildi
- [ ] `data/processed/baseline_results.json` 3 baseline metrikleriyle dolu
- [ ] `data/processed/gbm_results.json` 3 GBDT metrikleriyle dolu
- [ ] `data/processed/ablation_results.json` 7 senaryoyla dolu
- [ ] En iyi GBDT regresyon RMSE'si Random Forest'tan **düşük**
- [ ] En iyi GBDT classification macro-F1 majority baseline'dan **yüksek**
- [ ] Ablation'da en azından bir grup (genelde geo) RMSE'yi >%10 bozuyor → kanıt sağlandı

### 13.3 Inference katmanı

- [ ] `raw2value_ml` Python paketi `pip install -e .` ile kurulabiliyor
- [ ] `from raw2value_ml import analyze, AnalyzePayload, LiveFx` hata vermez
- [ ] `analyze(payload)` warm <500ms (smoke test)
- [ ] `analyze()` AnalyzeResponse döndürüyor, pydantic validation geçiyor
- [ ] `recommended_route` her zaman 16 known route'tan biri
- [ ] `route_alternatives` her zaman tam 3 eleman
- [ ] `match_results` en fazla 5 eleman
- [ ] `reason_codes` her zaman 3 Türkçe cümle
- [ ] `confidence.overall` 0–100 arası
- [ ] `co2_kg = tonnage × total_distance_km × emission_factor` formülü doğrulanmış

### 13.4 Açıklanabilirlik

- [ ] `models/metadata.json` Bölüm 11.2 yapısına uygun
- [ ] `models/model_evidence.json` Bölüm 10.1 yapısına uygun
- [ ] `feature_importance` Top-15 her iki model için var
- [ ] Reason codes 8+ feature için Türkçe template tanımlı
- [ ] What-if (FX -%20, +%20) `analyze()` çağrılarında profit'i değiştiriyor

### 13.5 Kural uyumu (zorunlu — hackathon)

- [ ] **K1 (Karbon):** `compute_co2()` 4 transport mode için sırasıyla 0.100, 0.015, 0.500, 0.030 emisyon faktörü kullanıyor
- [ ] **K2 (Kur):** `usd_try`, `eur_try` her iki modelin input'unda — ablation `without_fx` testi RMSE'yi anlamlı bozuyor
- [ ] **K3 (Bağımsız Geo):** `find_nearby_processors()` Haversine veya parquet lookup ile çalışıyor — ORS'tan ayrı modül

### 13.6 Test ve reproducibility

- [ ] `bash scripts/run_full_pipeline.sh` baştan sona hatasız çalışıyor (~10–15 dk)
- [ ] Tüm seedler 42 (random_state)
- [ ] `pytest ml/tests/` 100% geçiyor
- [ ] `git status` clean — veri ve model artefaktları commit edildi (LFS opsiyonel)
- [ ] README'de **ML kullanımı** bölümü güncel

### 13.7 Backend'e teslim paketi

- [ ] Backend ekibine bu rapor verilir.
- [ ] `models/` klasörü ve `raw2value_ml/` paketi backend repo'sunda mevcut (ya ortak repo ya submodule).
- [ ] `from raw2value_ml import analyze` ile backend kodda 1-line entegrasyon kanıtlanıyor.
- [ ] Sample request/response örnekleri Bölüm 11.3'teki yapıyla `docs/api_examples.json` altında.

---

## 14. EKLER

### 14.1 Sık karşılaşılan tuzaklar

| Tuzak | Belirti | Çözüm |
|---|---|---|
| **Target leakage** | Test R² > 0.99, gerçek dağılımda RMSE büyük | `expected_profit_try` ya da `match_score` input'a sızdı — `test_no_target_leakage.py` çalıştır |
| **Augmentation rastgele oldu** | Model "öğrendiğini" iddia ediyor ama ablation hiçbir şey değiştirmiyor | Augmentation kurallarını `07_augmentation_rules`'a sıkı bağla, lookup'lardan oku |
| **CO2 random üretildi** | CO2 değerleri gerçeklikle uyumsuz, transport_mode'a duyarsız | `compute_co2()` formülünü kullan, asla `np.random.uniform` ile üretme |
| **FX sabitlendi** | `usd_try` her satırda aynı | `fx_scenario_pct` 5 değerden sample edilmeli (AUG-03) |
| **Class imbalance ihmal edildi** | Bazı route'lar hiç tahmin edilmiyor | `class_weight="balanced"` kullan |
| **CatBoost cat_features verilmedi** | CatBoost tüm feature'ları sayısal kabul ediyor | `cat_features=CATEGORICAL_FEATURES` parametresini ver |
| **Pipeline reload başarısız** | `joblib.load` farklı sklearn versiyonunda fail | `requirements.txt` exact versiyonları sabitle |
| **Reason codes tutarsız** | Aynı feature için bazen "yüksek" bazen "düşük" yazıyor | `FEATURE_MEDIANS` eğitim sırasında hesapla, JSON'a yaz, inference'ta yükle |
| **Match scorer ağırlıkları toplam 1 değil** | Skorlar 0–1 dışına çıkıyor | `WEIGHT_PROFILES` validation'ı testte yap |
| **Distance lookup miss** | Yeni şehir için NaN | Haversine fallback aktif olmalı (`geo.py`) |

### 14.2 Hyperparameter tuning yapmak istersem? (advanced)

```python
import optuna

def objective(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 200, 800),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
    }
    model = XGBRegressor(**params, random_state=42)
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], early_stopping_rounds=30, verbose=False)
    return rmse(y_val, model.predict(X_val))

study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=50)
print(study.best_params)
```

### 14.3 SHAP ekleme planı (advanced)

```python
import shap

explainer = shap.TreeExplainer(model_profit)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test, feature_names=feature_names)
shap.force_plot(explainer.expected_value, shap_values[0], X_test.iloc[0])
```

`raw2value_ml/explain_shap.py` modülü olarak eklenir; reason codes onu da kullanabilir.

### 14.4 LightGBM Ranker ekleme planı (advanced)

```python
import lightgbm as lgb

# B2B ranking için group bazlı
groups = df.groupby("query_id").size().values    # her producer-tonaj-kalite kombinasyonu bir query
ranker = lgb.LGBMRanker(objective="lambdarank", metric="ndcg", random_state=42)
ranker.fit(X_train, y_train, group=groups)
```

### 14.5 LLM Türkçe açıklama ekleme planı (advanced)

```python
# raw2value_ml/explain_llm.py
def llm_explain_decision(features, recommendation, top_reasons):
    prompt = f"""
    Sen bir tedarik zinciri uzmanısın. Aşağıdaki veriyi okuyup bir KOBİ sahibine
    Türkçe, jargon-free 3-4 cümlelik bir öneri yaz.

    Veri:
    - Hammadde: {features['raw_material']}
    - Önerilen rota: {recommendation['route']}
    - Beklenen kâr: {recommendation['profit']:.0f} TL
    - Top 3 etken: {', '.join(r['feature'] for r in top_reasons)}

    KURAL: Spesifik sayıları koru. Hipotez kurma. Sertifika önerme.
    """
    return llm_client.complete(prompt, max_tokens=200, temperature=0.2)
```

### 14.6 Akademik dayanak özeti (mentör/jüriye savunma için)

| Argüman | Referans |
|---|---|
| Tabular ML için GBDT state-of-the-art | Chen & Guestrin 2016, Ke et al. 2017, Prokhorenkova et al. 2018 |
| Tabular foundation modeller hâlâ GBDT'nin gerisinde | arXiv 2602.19237 |
| Supply chain ML'de GBDT yüksek precision | arXiv 2406.13166 |
| Domain-informed augmentation meşru | Branco 2017 (SMOGN), Xu et al. 2019 (CTGAN) |
| LambdaRank/LambdaMART (advanced) | Burges 2010 |
| SHAP (advanced) | Lundberg & Lee 2017 |
| Inventory demand forecasting GBDT | Nguyen et al. 2024 (IOS Press) |

### 14.7 Reproducibility kontrolleri

- Tüm seedler 42 (numpy, sklearn, xgboost, lightgbm, catboost, train_test_split)
- requirements.txt exact versiyonlar
- `train_test_split(stratify=...)` kullan
- joblib model dump versiyon notu (`metadata.json`'da)
- Notebook'lar Output cell'leri commit'e dahil değil (`jupyter nbconvert --clear-output`)

### 14.8 İlerideki backup planı (hackathon esnekliği)

Eğer Saat 18 checkpoint'inde modeller hazır değilse:
- **Yedek 1:** Sadece rule-based regressor + manuel route lookup. Pipeline mevcut, model_profit.pkl içinde rule_based dump'lanır. Demo "ML training devam ediyor, baseline ile çalışıyor" diye konumlanır.
- **Yedek 2:** Sadece Model 2 (route classifier) + formülle profit hesabı. Decision Cockpit %80 fonksiyonel kalır.
- **Yedek 3:** Tek bir hammadde (pomza) için tam pipeline. Diğerleri "future scope".

Hiçbir yedek `analyze()` API kontratını bozmaz; sadece içerikte basitleşme olur.

---

## 15. SONUÇ

Bu rapor `raw2value_master_v4_2026-05-02.xlsx`'i girdi alıp **backend ekibine teslim edilebilir model paketi** üretmenin tüm adımlarını içerir.

**Özet kararlar:**
- 2 model + skorlayıcı (LLM kararı vermez, açıklayabilir).
- Algoritma: XGBoost / LightGBM / CatBoost benchmark, en iyisi.
- Veri: ~78 referans + ~1.500 augmented = 1.500 satır.
- Augmentation: 10 domain-informed kural; rastgele yok, formül + lookup + ±gürültü.
- Hedef: target leakage'sız 4 hedef değişken (profit, uplift, route, match).
- Açıklanabilirlik: Türkçe template reason codes + feature importance + confidence breakdown.
- Kural uyumu: K1 (CO2 formülü), K2 (FX feature), K3 (geo lookup) — ablation kanıtı.
- Teslimat: `models/*.pkl + .json` + `raw2value_ml/` paketi + `analyze(payload)` fonksiyonu.

**Süre tahmini (sırayla, paralel mümkün değilse):**
- Adım 0–1 (iskelet + ETL): 1 saat
- Adım 2–3 (loader + augmentation): 1.5 saat
- Adım 4 (pipeline): 30 dakika
- Adım 5 (baselines): 1 saat
- Adım 6 (GBDT benchmark): 1.5 saat
- Adım 7 (ablation): 1 saat
- Adım 8–9 (reasons, confidence, scorer): 1 saat
- Adım 10 (inference): 1 saat
- Adım 11–12 (evidence + package): 30 dakika
- Adım 13 (e2e test): 30 dakika

**Toplam: ~9 saat** (24h plandaki M satırlarıyla uyumlu, saat 18 checkpoint öncesi tamamlanır).

Bu rapor bittiğinde backend ekibi tek satırla entegre olur:

```python
from raw2value_ml import analyze, AnalyzePayload
response = analyze(payload)   # FastAPI /api/analyze endpoint'i bunu wrap eder
```

Ve frontend'e geçildiğinde modelden hiçbir engel kalmaz.

— **Raw2Value AI Master Model Eğitim Raporu, v1.0 son.**
