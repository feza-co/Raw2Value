"""Domain-informed augmentation pipeline (rapor §5.5–§5.6).

build_training_set() ~1500 satirlik egitim setini sirasiyla 10 adimda
uretir. Tum random ureteci ``np.random.default_rng(seed)``'dir; ``seed=42``
ile cagrildiginda her zaman ayni sonuc dondurur (test_seed_reproducibility
bunu dogrular).

10 augmentation kuralinin (AUG-01..AUG-10) hangisinin nerede uygulandigi
fonksiyon docstring'lerinde belirtilmistir.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from raw2value_ml.reference_loader import (
    load_buyer_demand_score,
    load_carbon_factors,
    load_delivery_risk,
    load_distance_lookup,
    load_organizations,
    load_price_volatility,
    load_quality_match_matrix,
    load_routes,
)

from .features import ROUTES_BY_MATERIAL, VALID_MATERIALS, make_route_label
from .targets import compute_targets


# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
DEFAULT_FX = {"usd_try": 45.05, "eur_try": 52.67}

# Tasima modu -> typical lead-time (gun)
LEAD_TIME_BY_MODE = {"kara": 7.0, "deniz": 14.0, "demiryolu": 10.0, "hava": 3.0}

# Material -> buyer sektor adaylari (anlamli eslesme icin)
SECTORS_BY_MATERIAL: dict[str, list[str]] = {
    "pomza": ["building_insulation", "construction_aggregate"],
    "perlit": ["building_insulation", "horticulture_substrate"],
    "kabak_cekirdegi": ["food_snack"],
}

# Hammadde -> raw_subtype adaylari
SUBTYPES_BY_MATERIAL: dict[str, list[str]] = {
    "pomza": ["acik_renk_iri", "acik_renk_ince", "koyu_renk", "scoria"],
    "perlit": ["expandable_grade_a", "expandable_grade_b", "raw_lump"],
    "kabak_cekirdegi": ["urgup_sivrisi", "kazimirka", "icme", "kabuksuz"],
}

# Hammadde -> origin_district adaylari (Nevsehir merkezli; perlit/kabak Nevsehir tarimsal)
DISTRICTS_BY_MATERIAL: dict[str, list[str]] = {
    "pomza": ["Acigol", "Avanos", "Urgup", "Merkez", "Gulsehir", "Hacibektas"],
    "perlit": ["Cumra", "Bergama", "Karaman", "Kutahya"],
    "kabak_cekirdegi": ["Urgup", "Merkez", "Avanos", "Acigol", "Derinkuyu"],
}

# Hammadde -> processor_type
PROCESSOR_TYPES_BY_MATERIAL: dict[str, list[str]] = {
    "pomza": ["pomza_kirici", "bims_uretici", "mikronize_tesis"],
    "perlit": ["perlit_genlestirme", "perlit_islem"],
    "kabak_cekirdegi": ["kuruyemis_isleme", "yag_uretici", "paketleme"],
}

# Hammadde -> product_form adaylari
PRODUCT_FORMS_BY_MATERIAL: dict[str, list[str]] = {
    "pomza": ["ham_kaya", "kirilmis", "elenmis", "toz"],
    "perlit": ["ham_kaya", "kirilmis", "genlestirilmis"],
    "kabak_cekirdegi": ["kabuklu", "ic", "kavrulmus", "paketli"],
}

# Sehir -> ulke
BUYER_CITIES = {
    "TR": ["Istanbul", "Ankara", "Izmir", "Antalya", "Kayseri", "Mersin"],
    "DE": ["Hamburg", "Berlin", "Dusseldorf", "Munich"],
    "NL": ["Amsterdam", "Rotterdam"],
}

# Tasima modu dagilimlari (TR ici kara baskin; ihracatta deniz/hava artar)
TRANSPORT_MODE_BY_COUNTRY = {
    "TR": ["kara", "kara", "kara", "demiryolu", "kara"],
    "DE": ["kara", "deniz", "deniz", "demiryolu", "hava"],
    "NL": ["deniz", "deniz", "kara", "hava"],
}

# AUG-06 — quality_grade dagilimi
QUALITY_GRADE_DIST = {"A": 0.30, "B": 0.50, "C": 0.20}

PRIORITY_VALUES = ["max_profit", "low_carbon", "fast_delivery"]
INPUT_MODES = ["basic", "advanced"]
PARTICLE_SIZE_CLASSES = ["fine", "medium", "coarse"]

# AUG-03 — fx senaryo discrete kume
FX_SCENARIO_VALUES = np.array([-0.10, -0.05, 0.0, 0.05, 0.10])

# Distance lookup sabit anahtar prefix'leri
SRC_KEYS = [
    "src_acigol",
    "src_avanos",
    "src_derinkuyu",
    "src_gulsehir",
    "src_hacibektas",
    "src_kozakli",
    "src_nevsehir_merkez",
    "src_urgup",
]


# ---------------------------------------------------------------------------
# Private yardimci fonksiyonlar
# ---------------------------------------------------------------------------
def _bootstrap_base_rows(
    target_rows: int,
    material_dist: dict[str, float],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """target_rows boyutlu DataFrame; sadece raw_material kolonu doldurulur."""
    materials = list(material_dist.keys())
    weights = np.array([material_dist[m] for m in materials], dtype=float)
    weights /= weights.sum()
    chosen = rng.choice(materials, size=target_rows, p=weights)
    return pd.DataFrame({"raw_material": chosen})


def _sample_categorical_features(
    df: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    """raw_subtype, origin_district, route_candidate, transport_mode, quality_grade,
    priority, processor_type, product_form, particle_size_class, input_mode,
    buyer_country/city/sector — hepsini sample eder.

    AUG-06 quality_grade dagilimini uygular.
    """
    out = df.copy()
    n = len(out)

    # Hammadde-bagli alanlar
    out["raw_subtype"] = [
        rng.choice(SUBTYPES_BY_MATERIAL[m]) for m in out["raw_material"]
    ]
    out["origin_district"] = [
        rng.choice(DISTRICTS_BY_MATERIAL[m]) for m in out["raw_material"]
    ]
    out["processing_route_candidate"] = [
        make_route_label(m, rng.choice(ROUTES_BY_MATERIAL[m]))
        for m in out["raw_material"]
    ]
    out["processor_type"] = [
        rng.choice(PROCESSOR_TYPES_BY_MATERIAL[m]) for m in out["raw_material"]
    ]
    out["product_form"] = [
        rng.choice(PRODUCT_FORMS_BY_MATERIAL[m]) for m in out["raw_material"]
    ]

    # Buyer ulkesi: TR 40, DE 35, NL 25
    countries = rng.choice(["TR", "DE", "NL"], size=n, p=[0.40, 0.35, 0.25])
    out["buyer_country"] = countries
    out["buyer_city"] = [rng.choice(BUYER_CITIES[c]) for c in countries]
    out["buyer_sector"] = [
        rng.choice(SECTORS_BY_MATERIAL[m]) for m in out["raw_material"]
    ]
    out["transport_mode"] = [
        rng.choice(TRANSPORT_MODE_BY_COUNTRY[c]) for c in countries
    ]

    # Quality grade — AUG-06 (A=0.30, B=0.50, C=0.20)
    grades = list(QUALITY_GRADE_DIST.keys())
    grade_p = [QUALITY_GRADE_DIST[g] for g in grades]
    out["quality_grade"] = rng.choice(grades, size=n, p=grade_p)
    out["quality_unknown"] = False  # MVP: bilinen grade

    # Operasyonel
    out["priority"] = rng.choice(PRIORITY_VALUES, size=n)
    out["input_mode"] = rng.choice(INPUT_MODES, size=n, p=[0.65, 0.35])
    out["particle_size_class"] = rng.choice(PARTICLE_SIZE_CLASSES, size=n)

    # Boolean flag'ler — sentetik dagilim (rapor "Önemli notlar")
    out["technical_data_available"] = rng.random(n) < 0.70
    out["default_values_used"] = ~out["technical_data_available"].values
    out["lab_report_uploaded"] = rng.random(n) < 0.40
    out["processor_has_own_raw_material"] = rng.random(n) < 0.30

    # Tonnage: log-uniform [1, 1000]
    out["tonnage"] = np.exp(rng.uniform(np.log(1.0), np.log(1000.0), size=n))

    # advanced kolonlar (moisture, purity) — input_mode=='advanced' iken bilgisi var
    moisture_typical = {"pomza": 5.0, "perlit": 4.0, "kabak_cekirdegi": 7.0}
    purity_typical = {"pomza": 92.0, "perlit": 95.0, "kabak_cekirdegi": 98.0}
    moisture_vals = []
    purity_vals = []
    for m, mode in zip(out["raw_material"], out["input_mode"]):
        if mode == "advanced":
            moisture_vals.append(
                float(np.clip(rng.normal(moisture_typical[m], 1.0), 0.5, 20.0))
            )
            purity_vals.append(
                float(np.clip(rng.normal(purity_typical[m], 2.0), 70.0, 99.9))
            )
        else:
            moisture_vals.append(np.nan)
            purity_vals.append(np.nan)
    out["moisture_pct"] = moisture_vals
    out["purity_pct"] = purity_vals

    return out


def _lookup_prices_costs(df: pd.DataFrame) -> pd.DataFrame:
    """routes.parquet'tan rota-bagimli fiyat ve maliyet kolonlarini esle."""
    routes = load_routes()
    out = df.copy()
    # Hizli lookup
    key_cols = ["Hammadde", "Rota"]
    routes_indexed = routes.set_index(key_cols)

    raw_prices = []
    proc_prices = []
    proc_costs = []
    for _, row in out.iterrows():
        material = row["raw_material"]
        # processing_route_candidate prefix'li (ornek: "pomza_raw_sale")
        prefix = f"{material}_"
        route_short = row["processing_route_candidate"]
        if route_short.startswith(prefix):
            route_short = route_short[len(prefix) :]
        try:
            r = routes_indexed.loc[(material, route_short)]
            sale = float(r["Satis_USD_ton_typical"])
            cost = float(r["Maliyet USD/ton (typical)"])
        except KeyError:
            sale = 100.0
            cost = 30.0
        proc_prices.append(sale)
        proc_costs.append(cost)
        # Ham fiyat = ayni materyalin "raw_sale" rotasinin sale fiyati
        raw_route = "raw_sale" if material != "kabak_cekirdegi" else "bulk_sale"
        try:
            r_raw = routes_indexed.loc[(material, raw_route)]
            raw_prices.append(float(r_raw["Satis_USD_ton_typical"]))
        except KeyError:
            raw_prices.append(50.0)
    out["raw_price_typical_usd_ton"] = raw_prices
    out["processed_price_typical_usd_ton"] = proc_prices
    out["processing_cost_typical_usd_ton"] = proc_costs
    # Paketleme deterministik 5.0 USD/ton (transparan default; rapor "advanced opsiyonel" alani)
    out["packaging_cost_usd_ton"] = 5.0
    return out


def _lookup_distances(
    df: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    """source_to_processor_km ve processor_to_buyer_km'i distance_lookup'tan ornekle.

    src->osb cifti her satira atanir (intra-Anatolia mesafeleri).
    proc->buyer cifti buyer_city'ye gore filtre+ornekleme yapilir.
    """
    dl = load_distance_lookup()
    out = df.copy()

    # src -> osb pairs
    src_osb_pairs = [(k, v["km"]) for k, v in dl.items() if k[1].startswith("osb_")]
    # buyer_city -> proc->buyer pairs (key is buyer dst)
    proc_to_buyer: dict[str, list[float]] = {}
    for k, v in dl.items():
        if k[0].startswith("proc_") and k[1].startswith("buyer_"):
            proc_to_buyer.setdefault(k[1], []).append(v["km"])

    # Buyer city alpha mapping (lookup keys are tr-spelling 'D�sseldorf' due to encoding)
    city_lookup_aliases = {
        "Istanbul": ["buyer_Istanbul", "buyer_İstanbul"],
        "Ankara": ["buyer_Ankara"],
        "Izmir": ["buyer_Izmir", "buyer_İzmir"],
        "Antalya": ["buyer_Antalya"],
        "Kayseri": ["buyer_Kayseri"],
        "Mersin": ["buyer_Mersin"],
        "Hamburg": ["buyer_Hamburg"],
        "Berlin": ["buyer_Berlin"],
        "Dusseldorf": ["buyer_Dusseldorf", "buyer_Düsseldorf"],
        "Munich": ["buyer_Munich", "buyer_Münih"],
        "Amsterdam": ["buyer_Amsterdam"],
        "Rotterdam": ["buyer_Rotterdam"],
    }

    src_proc_kms = []
    proc_buyer_kms = []
    for _, row in out.iterrows():
        # src -> processor: src_osb_pairs uniform random
        idx = rng.integers(0, len(src_osb_pairs))
        src_proc_kms.append(src_osb_pairs[idx][1])

        # proc -> buyer: lookup buyer_city
        city = row["buyer_city"]
        candidates: list[float] = []
        for alias in city_lookup_aliases.get(city, []):
            if alias in proc_to_buyer:
                candidates.extend(proc_to_buyer[alias])
        # Encoding-sicim varyantlari icin: substring match
        if not candidates:
            for k, kms in proc_to_buyer.items():
                if city.lower() in k.lower():
                    candidates.extend(kms)
        if not candidates:
            # Fallback: tum buyer mesafelerinden ortalama band
            all_kms = [v for vs in proc_to_buyer.values() for v in vs]
            candidates = all_kms

        idx2 = rng.integers(0, len(candidates))
        proc_buyer_kms.append(candidates[idx2])

    out["source_to_processor_km"] = src_proc_kms
    out["processor_to_buyer_km"] = proc_buyer_kms
    return out


def _lookup_emission_factors(df: pd.DataFrame) -> pd.DataFrame:
    """transport_mode -> emission_factor_kg_co2_ton_km (kara=0.100, deniz=0.015 vb.)."""
    factors = load_carbon_factors()  # {'kara':0.100, 'deniz':0.015, ...}
    out = df.copy()
    out["emission_factor_kg_co2_ton_km"] = [
        factors.get(mode, 0.100) for mode in out["transport_mode"]
    ]
    return out


def _lookup_quality_match(df: pd.DataFrame) -> pd.DataFrame:
    """quality_match_score: producer_grade × buyer_required_grade (rapor §8.4).

    Buyer required grade: ulkeye gore basit heuristik:
      - TR -> B baskin (insaat sektoru toleransli)
      - DE/NL -> A baskin (premium pazar)
    """
    matrix = load_quality_match_matrix()
    out = df.copy()

    def buyer_grade(country: str) -> str:
        # Deterministik (her zaman ayni grade) — rng kullanmadan
        if country in ("DE", "NL"):
            return "A"
        return "B"

    scores = []
    for _, row in out.iterrows():
        prod = str(row["quality_grade"])
        buyer = buyer_grade(row["buyer_country"])
        scores.append(matrix.get((prod, buyer), 0.7))
    out["quality_match_score"] = scores
    return out


def _lookup_delivery_risk(
    df: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    """AUG-08: transport_mode -> typical risk + N(0, 0.05) noise, [0,1] clip."""
    out = df.copy()
    base = np.array([load_delivery_risk(m) for m in out["transport_mode"]])
    noise = rng.normal(0.0, 0.05, size=len(out))
    out["delivery_risk"] = np.clip(base + noise, 0.0, 1.0)

    # Price volatility — rapor §5.2.1
    out["price_volatility_risk"] = [
        load_price_volatility(m) for m in out["raw_material"]
    ]
    return out


def _compute_demand_score(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """AUG-05: cagr_normalized + market_size_normalized + sector_relevance + ±0.05 noise."""
    out = df.copy()
    # buyer_country × buyer_sector -> reference_loader skoru (0.5*USD + 0.3*CAGR + 0.2*1)
    base_scores = [
        load_buyer_demand_score(c, s)
        for c, s in zip(out["buyer_country"], out["buyer_sector"])
    ]
    noise = rng.normal(0.0, 0.05, size=len(out))
    out["demand_score"] = np.clip(np.array(base_scores) + noise, 0.0, 1.0)
    return out


def _apply_price_noise(
    df: pd.DataFrame, sigma_pct: float, rng: np.random.Generator
) -> pd.DataFrame:
    """AUG-01: raw + processed fiyatlara ±sigma_pct gauss noise (clip min/max)."""
    out = df.copy()
    for col in ["raw_price_typical_usd_ton", "processed_price_typical_usd_ton"]:
        vals = out[col].values
        noise = rng.normal(0.0, sigma_pct, size=len(vals))
        new_vals = vals * (1.0 + noise)
        # Min: yarisina kadar dusurmemek; Max: 2x asmak
        out[col] = np.clip(new_vals, vals * 0.5, vals * 2.0)
    return out


def _apply_distance_noise(
    df: pd.DataFrame, sigma_pct: float, rng: np.random.Generator
) -> pd.DataFrame:
    """AUG-02: source_to_processor + processor_to_buyer ±sigma_pct (>=1 km clip)."""
    out = df.copy()
    for col in ["source_to_processor_km", "processor_to_buyer_km"]:
        vals = out[col].values
        noise = rng.normal(0.0, sigma_pct, size=len(vals))
        out[col] = np.maximum(vals * (1.0 + noise), 1.0)
    return out


def _apply_lead_time_noise(
    df: pd.DataFrame, sigma_abs: float, rng: np.random.Generator
) -> pd.DataFrame:
    """AUG-04: lead_time_days = base_by_mode + N(0, sigma_abs), clip [1, 90]."""
    out = df.copy()
    base = np.array([LEAD_TIME_BY_MODE.get(m, 7.0) for m in out["transport_mode"]])
    noise = rng.normal(0.0, sigma_abs, size=len(out))
    out["lead_time_days"] = np.clip(base + noise, 1.0, 90.0)
    return out


def _compute_total_distance(df: pd.DataFrame) -> pd.DataFrame:
    """total_distance_km = source_to_processor_km + processor_to_buyer_km."""
    out = df.copy()
    out["total_distance_km"] = (
        out["source_to_processor_km"] + out["processor_to_buyer_km"]
    )
    return out


def _compute_co2(df: pd.DataFrame) -> pd.DataFrame:
    """co2_kg = tonnage * total_distance_km * emission_factor_kg_co2_ton_km."""
    out = df.copy()
    out["co2_kg"] = (
        out["tonnage"]
        * out["total_distance_km"]
        * out["emission_factor_kg_co2_ton_km"]
    )
    return out


def _compute_transport_cost(df: pd.DataFrame) -> pd.DataFrame:
    """transport_cost_usd_ton_km = mode-bagli baseline (deterministik)."""
    # MVP baseline: kara 0.05, deniz 0.02, demiryolu 0.03, hava 0.50 USD/ton-km
    cost_map = {"kara": 0.05, "deniz": 0.02, "demiryolu": 0.03, "hava": 0.50}
    out = df.copy()
    out["transport_cost_usd_ton_km"] = [cost_map.get(m, 0.05) for m in out["transport_mode"]]
    return out


def _apply_co2_measurement_noise(
    df: pd.DataFrame, sigma_pct: float, rng: np.random.Generator
) -> pd.DataFrame:
    """AUG-07: co2_kg ±sigma_pct DEFRA olcum belirsizligi."""
    out = df.copy()
    noise = rng.normal(0.0, sigma_pct, size=len(out))
    out["co2_kg"] = np.maximum(out["co2_kg"] * (1.0 + noise), 0.001)
    return out


def _sample_fx_scenario(
    df: pd.DataFrame, current_fx: dict[str, float], rng: np.random.Generator
) -> pd.DataFrame:
    """AUG-03: fx_scenario_pct ∈ {-0.10, -0.05, 0, 0.05, 0.10} discrete uniform."""
    out = df.copy()
    n = len(out)
    out["usd_try"] = current_fx["usd_try"]
    out["eur_try"] = current_fx["eur_try"]
    out["fx_scenario_pct"] = rng.choice(FX_SCENARIO_VALUES, size=n)
    return out


def _compute_data_confidence(df: pd.DataFrame) -> pd.DataFrame:
    """data_confidence_score: 80 baz + bonuslar (rapor "Onemli notlar")."""
    out = df.copy()
    score = np.full(len(out), 80.0)
    score = score + np.where(out["technical_data_available"], 5.0, -5.0)
    score = score + np.where(out["lab_report_uploaded"], 5.0, 0.0)
    score = score + np.where(out["default_values_used"], -5.0, 5.0)
    out["data_confidence_score"] = np.clip(score, 60.0, 95.0)
    return out


def _validate_and_drop(df: pd.DataFrame) -> pd.DataFrame:
    """Zorunlu kolonlarda NaN olan veya non-finite expected_profit_try barindiran satirlari at."""
    required_non_null = [
        "raw_material",
        "processing_route_candidate",
        "tonnage",
        "raw_price_typical_usd_ton",
        "processed_price_typical_usd_ton",
        "processing_cost_typical_usd_ton",
        "source_to_processor_km",
        "processor_to_buyer_km",
        "total_distance_km",
        "transport_mode",
        "emission_factor_kg_co2_ton_km",
        "co2_kg",
        "usd_try",
        "expected_profit_try",
        "recommended_route_label",
    ]
    out = df.dropna(subset=required_non_null).copy()
    out = out[np.isfinite(out["expected_profit_try"])]
    out = out[np.isfinite(out["co2_kg"])]
    out = out[out["co2_kg"] > 0]
    return out.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def build_training_set(
    target_rows: int = 1500,
    material_dist: dict[str, float] | None = None,
    seed: int = 42,
    current_fx: dict[str, float] | None = None,
) -> pd.DataFrame:
    """1500 satirlik egitim setini sira ile uretir (rapor §5.6).

    Sira:
      1) Bootstrap (raw_material)
      2) Sample categorical
      3) Lookup deterministic (prices, distances, emission, quality, risk, demand)
      4) Apply noise (price, distance, lead_time)
      5) Compute formula features (total_distance, co2, transport_cost)
      6) Apply formula noise (co2)
      7) Sample fx scenario
      8) Compute data_confidence_score
      9) Compute targets (profit, uplift, score, label)
     10) Validate & drop

    Returns:
        Reset-index DataFrame, ~1400-1500 satir.
    """
    if material_dist is None:
        material_dist = {"pomza": 0.70, "perlit": 0.20, "kabak_cekirdegi": 0.10}
    if current_fx is None:
        current_fx = DEFAULT_FX

    rng = np.random.default_rng(seed)

    # 1) Bootstrap
    df = _bootstrap_base_rows(target_rows, material_dist, rng)
    # 2) Sample categorical
    df = _sample_categorical_features(df, rng)
    # 3) Lookup deterministic
    df = _lookup_prices_costs(df)
    df = _lookup_distances(df, rng)
    df = _lookup_emission_factors(df)
    df = _lookup_quality_match(df)
    df = _lookup_delivery_risk(df, rng)
    df = _compute_demand_score(df, rng)
    # 4) Apply noise to lookup values
    df = _apply_price_noise(df, sigma_pct=0.08, rng=rng)
    df = _apply_distance_noise(df, sigma_pct=0.05, rng=rng)
    df = _apply_lead_time_noise(df, sigma_abs=2.0, rng=rng)
    # 5) Compute formula features (transport_cost lazim co2'den once)
    df = _compute_total_distance(df)
    df = _compute_transport_cost(df)
    df = _compute_co2(df)
    # 6) Apply formula noise (co2)
    df = _apply_co2_measurement_noise(df, sigma_pct=0.03, rng=rng)
    # 7) Sample fx scenario
    df = _sample_fx_scenario(df, current_fx, rng)
    # 8) Data confidence
    df = _compute_data_confidence(df)
    # 9) Compute targets (profit + label)
    df = compute_targets(df, rng)
    # 10) Validate
    df = _validate_and_drop(df)

    return df
