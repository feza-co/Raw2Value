"""Model 1 (profit regression) ve Model 2 (route classifier) için feature listeleri.

Bu modul rapor §5.2 ve §6.5/§7.5 ile uyumlu feature setlerini tek bir kaynaktan
saglar. Target leakage testleri (test_no_target_leakage.py) bu listeleri
import ederek dogrudan dogrular.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Sabitler — domain enum'lari
# ---------------------------------------------------------------------------
VALID_MATERIALS: list[str] = ["pomza", "perlit", "kabak_cekirdegi"]

VALID_ROUTES: list[str] = [
    # pomza (5)
    "pomza_raw_sale",
    "pomza_bims_aggregate",
    "pomza_micronized_pumice",
    "pomza_filtration_media",
    "pomza_textile_washing_stone",
    # perlit (5)
    "perlit_raw_sale",
    "perlit_expanded_perlite",
    "perlit_agriculture_substrate",
    "perlit_insulation_filler",
    "perlit_filtration_product",
    # kabak_cekirdegi (5)
    "kabak_cekirdegi_bulk_sale",
    "kabak_cekirdegi_roasted_packaged",
    "kabak_cekirdegi_pumpkin_seed_oil",
    "kabak_cekirdegi_protein_powder",
    "kabak_cekirdegi_tourism_gift_pack",
]

# Hammadde -> rota listesi (label uretimi icin candidate set).
# Kisaltilmis (material prefix'siz) anahtarlar; routes.parquet ile dogrudan eslestirilir.
ROUTES_BY_MATERIAL: dict[str, list[str]] = {
    "pomza": [
        "raw_sale",
        "bims_aggregate",
        "micronized_pumice",
        "filtration_media",
        "textile_washing_stone",
    ],
    "perlit": [
        "raw_sale",
        "expanded_perlite",
        "agriculture_substrate",
        "insulation_filler",
        "filtration_product",
    ],
    "kabak_cekirdegi": [
        "bulk_sale",
        "roasted_packaged",
        "pumpkin_seed_oil",
        "protein_powder",
        "tourism_gift_pack",
    ],
}


def make_route_label(material: str, route: str) -> str:
    """Material + route adlarini global benzersiz etikete cevirir.

    Ornek: ``("pomza", "raw_sale") -> "pomza_raw_sale"``.
    Bu sekilde "raw_sale" pomza/perlit arasinda paylasilsa bile 15 sinif korunur.
    """
    return f"{material}_{route}"


# ---------------------------------------------------------------------------
# Feature listeleri (rapor §6.5 / §7.5)
# ---------------------------------------------------------------------------
NUMERIC_FEATURES: list[str] = [
    "tonnage",
    "raw_price_typical_usd_ton",
    "processed_price_typical_usd_ton",
    "processing_cost_typical_usd_ton",
    "packaging_cost_usd_ton",
    "source_to_processor_km",
    "processor_to_buyer_km",
    "total_distance_km",
    "transport_cost_usd_ton_km",
    "emission_factor_kg_co2_ton_km",
    "co2_kg",
    "usd_try",
    "eur_try",
    "fx_scenario_pct",
    "demand_score",
    "lead_time_days",
    "delivery_risk",
    "price_volatility_risk",
    "quality_match_score",
    "data_confidence_score",
    "moisture_pct",
    "purity_pct",
]

CATEGORICAL_FEATURES: list[str] = [
    "raw_material",
    "raw_subtype",
    "origin_district",
    "processing_route_candidate",
    "product_form",
    "quality_grade",
    "processor_type",
    "buyer_country",
    "buyer_sector",
    "buyer_city",
    "transport_mode",
    "input_mode",
    "particle_size_class",
]

BOOLEAN_FEATURES: list[str] = [
    "quality_unknown",
    "technical_data_available",
    "default_values_used",
    "lab_report_uploaded",
    "processor_has_own_raw_material",
]


# Model 1 — profit regression (rapor §6.5). 32 feature.
M1_FEATURES: list[str] = [
    # material & input
    "raw_material",
    "raw_subtype",
    "origin_district",
    "tonnage",
    "quality_grade",
    "quality_unknown",
    "product_form",
    # rota (input)
    "processing_route_candidate",
    # fiyat & maliyet
    "raw_price_typical_usd_ton",
    "processed_price_typical_usd_ton",
    "processing_cost_typical_usd_ton",
    "packaging_cost_usd_ton",
    # cografi
    "source_to_processor_km",
    "processor_to_buyer_km",
    "total_distance_km",
    "transport_mode",
    "transport_cost_usd_ton_km",
    # karbon (zorunlu kural)
    "emission_factor_kg_co2_ton_km",
    "co2_kg",
    # kur (zorunlu kural)
    "usd_try",
    "eur_try",
    "fx_scenario_pct",
    # pazar
    "buyer_country",
    "buyer_sector",
    "buyer_city",
    "demand_score",
    # operasyonel
    "lead_time_days",
    "delivery_risk",
    "price_volatility_risk",
    # kalite
    "quality_match_score",
    # confidence
    "data_confidence_score",
    # mod
    "input_mode",
    # advanced
    "moisture_pct",
    "purity_pct",
    "particle_size_class",
]

# Model 2 — route classifier (rapor §7.5)
# processing_route_candidate target oldugu icin cikarilir, priority eklenir.
M2_FEATURES: list[str] = [
    f for f in M1_FEATURES if f != "processing_route_candidate"
] + ["priority"]


def get_feature_split(model: str = "M1") -> dict[str, list[str]]:
    """Modele gore numerical/categorical/boolean feature gruplarini dondurur.

    Args:
        model: ``"M1"`` veya ``"M2"``.

    Returns:
        ``{"numerical": [...], "categorical": [...], "boolean": [...]}``
    """
    if model == "M1":
        feats = M1_FEATURES
    elif model == "M2":
        feats = M2_FEATURES
    else:
        raise ValueError(f"Unknown model: {model!r}; expected 'M1' or 'M2'.")

    feat_set = set(feats)
    return {
        "numerical": [f for f in NUMERIC_FEATURES if f in feat_set],
        "categorical": [
            f
            for f in (CATEGORICAL_FEATURES + (["priority"] if model == "M2" else []))
            if f in feat_set
        ],
        "boolean": [f for f in BOOLEAN_FEATURES if f in feat_set],
    }
