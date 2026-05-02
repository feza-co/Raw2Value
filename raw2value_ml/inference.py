"""analyze() — backend'in tek import edeceği fonksiyon (rapor §11.3 sözleşmesi).

Tasarım:
    * Tüm pickled modeller modül seviyesi `_state` dict'inde lazy yüklenir.
    * `_load()` idempotent: ikinci çağrıda no-op.
    * Pipeline (raw payload -> AnalyzeResponse):
        1) Defaults + categorical/numeric base
        2) Geo + Carbon
        3) FX what-if
        4) Demand score
        5) Top-3 rota (Model 2)
        6) Her aday için profit (Model 1)
        7) B2B match (top-5)
        8) Reason codes
        9) Confidence breakdown
       10) Top-10 feature importance
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from .carbon import compute_co2, get_emission_factor
from .confidence import compute_overall_confidence
from .fx import apply_fx_scenario
from .geo import find_nearby_processors, lookup_distance
from .reasons import generate_reason_codes
from .reference_loader import load_buyer_demand_score
from .schemas import (
    AnalyzePayload,
    AnalyzeResponse,
    ConfidenceBreakdown,
    FeatureImportance,
    MatchResult,
    ReasonCode,
    RouteOption,
)
from .scorer import match_buyers

_PROJECT_ROOT = Path(__file__).parent.parent
_MODELS_DIR = _PROJECT_ROOT / "models"

# Metadata yoksa düşülen güvenli defaults — metadata.json varsa onunla override edilir.
_FALLBACK_DEFAULTS: dict[str, Any] = {
    "moisture_pct": {"pomza": 5.0, "perlit": 4.0, "kabak_cekirdegi": 7.0},
    "purity_pct": {"pomza": 92.0, "perlit": 95.0, "kabak_cekirdegi": 98.0},
    "particle_size_class": "medium",
    "lead_time_days": 7,
}

# Backward-compatible: rota oranı routes.parquet'tan ham/işlenmiş fiyat eşlerken
# rotaya bağlı tipik değerleri çekmek için kullanılır.
_ROUTE_RAW_FALLBACKS: dict[str, str] = {
    "pomza": "raw_sale",
    "perlit": "raw_sale",
    "kabak_cekirdegi": "bulk_sale",
}

_state: dict[str, Any] = {"loaded": False}


def _load() -> None:
    """Modelleri ve metadata'yı bir kez yükler. Idempotent."""
    if _state.get("loaded"):
        return
    _state["model_profit"] = joblib.load(_MODELS_DIR / "model_profit.pkl")
    _state["model_route"] = joblib.load(_MODELS_DIR / "model_route.pkl")
    pipeline_path = _MODELS_DIR / "feature_pipeline.pkl"
    _state["pipeline"] = joblib.load(pipeline_path) if pipeline_path.exists() else None

    md_path = _MODELS_DIR / "metadata.json"
    if md_path.exists():
        _state["metadata"] = json.loads(md_path.read_text(encoding="utf-8"))
    else:
        _state["metadata"] = {"default_values": _FALLBACK_DEFAULTS}

    classes = list(getattr(_state["model_route"], "classes_", []))
    if not classes:
        classes = _state["metadata"].get("models", {}).get("route", {}).get("classes", [])
    _state["route_classes"] = [str(c) for c in classes]
    _state["loaded"] = True


def _fill_defaults(payload: AnalyzePayload) -> dict[str, Any]:
    """Basic-mode payload için missing alanları metadata default'larıyla doldur."""
    defaults = _state["metadata"].get("default_values", _FALLBACK_DEFAULTS)

    moisture = payload.moisture_pct
    if moisture is None:
        moisture = defaults.get("moisture_pct", {}).get(payload.raw_material, 5.0)

    purity = payload.purity_pct
    if purity is None:
        purity = defaults.get("purity_pct", {}).get(payload.raw_material, 95.0)

    particle = payload.particle_size_class or defaults.get(
        "particle_size_class", "medium"
    )
    used_defaults = (
        payload.moisture_pct is None
        or payload.purity_pct is None
        or payload.particle_size_class is None
    )

    # Sektör eşlemesi kabaca:
    sector_by_material = {
        "pomza": "building_insulation",
        "perlit": "building_insulation",
        "kabak_cekirdegi": "food_snack",
    }

    return {
        "raw_material": payload.raw_material,
        "raw_subtype": payload.raw_material,
        "origin_district": payload.origin_city,
        "tonnage": float(payload.tonnage),
        "quality_grade": payload.quality,
        "quality_unknown": payload.quality == "unknown",
        "product_form": "ham_kaya",
        "transport_mode": payload.transport_mode,
        "buyer_country": payload.target_country,
        "buyer_city": payload.target_city or "",
        "buyer_sector": sector_by_material.get(payload.raw_material, "building_insulation"),
        "input_mode": payload.input_mode,
        "priority": payload.priority,
        "fx_scenario_pct": float(payload.fx_scenario_pct),
        "moisture_pct": float(moisture),
        "purity_pct": float(purity),
        "particle_size_class": str(particle),
        "lead_time_days": float(defaults.get("lead_time_days", 7)),
        "delivery_risk": 0.15,
        "price_volatility_risk": 0.20,
        "quality_match_score": 0.95,
        "data_confidence_score": 80,
        "technical_data_available": payload.input_mode == "advanced",
        "default_values_used": used_defaults,
        "lab_report_uploaded": False,
        "processor_has_own_raw_material": False,
        "fx_source": "TCMB_LIVE",
        "distance_source": "ORS_PRECOMPUTED",
    }


def _enrich_with_route_lookup(features: dict, route: str) -> dict:
    """routes.parquet'tan rota fiyat/maliyet kolonlarını enjekte et."""
    from .reference_loader import load_routes

    routes = load_routes()
    material = features.get("raw_material", "pomza")
    # Rota adı "<material>_<rota>" formatında.
    if route.startswith(f"{material}_"):
        rota = route[len(f"{material}_"):]
    elif "_" in route:
        # Material payload'da material'la başlamıyorsa ilk segmenti material kabul et.
        material, rota = route.split("_", 1)
    else:
        rota = route

    match = routes[(routes["Hammadde"] == material) & (routes["Rota"] == rota)]
    if match.empty:
        match = routes[routes["Hammadde"] == material]

    if not match.empty:
        row = match.iloc[0]
        sale = float(row.get("Satis_USD_ton_typical", 100.0) or 100.0)
        cost = float(row.get("Maliyet USD/ton (typical)", 30.0) or 30.0)
        # Ham fiyat: aynı materyalin "raw_sale" / "bulk_sale" rotasının satış fiyatı.
        raw_route = _ROUTE_RAW_FALLBACKS.get(material, "raw_sale")
        raw_match = routes[(routes["Hammadde"] == material) & (routes["Rota"] == raw_route)]
        raw_price = (
            float(raw_match.iloc[0].get("Satis_USD_ton_typical", 50.0) or 50.0)
            if not raw_match.empty
            else 50.0
        )
        features["raw_price_typical_usd_ton"] = raw_price
        features["processed_price_typical_usd_ton"] = sale
        features["processing_cost_typical_usd_ton"] = cost
    else:
        features.setdefault("raw_price_typical_usd_ton", 50.0)
        features.setdefault("processed_price_typical_usd_ton", 100.0)
        features.setdefault("processing_cost_typical_usd_ton", 30.0)

    features.setdefault("packaging_cost_usd_ton", 5.0)
    return features


def _build_model_features(features: dict, model_features: list[str]) -> pd.DataFrame:
    """Model feature listesindeki kolonlardan tek satırlık DataFrame üret.

    None (eksik) değerler boyut için tutulur — CatBoost native handling.
    """
    row = {f: features.get(f) for f in model_features}
    df = pd.DataFrame([row])

    # CatBoost categorical kolonlar için string/object dtype, numeric'ler float.
    # None'ları NaN'a çevir; tip belirsizliği CatBoost native handling tarafından kapsanır.
    return df


def _compute_uplift(predicted_profit: float, features: dict) -> float:
    """value_uplift_pct = (predicted - raw_sale_proxy) / |raw_sale_proxy|."""
    fx = float(features.get("usd_try", 45.0))
    raw_p = float(features.get("raw_price_typical_usd_ton", 50.0))
    tonnage = float(features.get("tonnage", 1.0))
    raw_sale = raw_p * fx * tonnage
    if abs(raw_sale) < 1.0:
        return 0.0
    return float((predicted_profit - raw_sale) / abs(raw_sale))


def analyze(payload: AnalyzePayload) -> AnalyzeResponse:
    """Tek giriş noktası — kullanıcı formundan tam karar paketine."""
    _load()

    m_profit = _state["model_profit"]
    m_route = _state["model_route"]

    # Eğitilmiş modellerin gerçek feature listesi (M1/M2'den daha kapsamlı —
    # boolean flag'leri de içerir). CatBoost feature_names_ kullanıyor.
    m1_features: list[str] = list(
        getattr(m_profit, "feature_names_", []) or getattr(m_profit, "feature_names_in_", [])
    )
    m2_features: list[str] = list(
        getattr(m_route, "feature_names_", []) or getattr(m_route, "feature_names_in_", [])
    )

    # 1) Defaults + base features
    features = _fill_defaults(payload)

    # 2) Geo + Carbon
    distances = lookup_distance(
        payload.origin_city, payload.target_city, payload.transport_mode
    )
    co2_kg = compute_co2(
        payload.tonnage, distances["total_km"], payload.transport_mode
    )
    features["total_distance_km"] = distances["total_km"]
    features["source_to_processor_km"] = distances["source_to_processor_km"]
    features["processor_to_buyer_km"] = distances["processor_to_buyer_km"]
    features["distance_source"] = distances["source"]
    features["co2_kg"] = co2_kg
    features["emission_factor_kg_co2_ton_km"] = get_emission_factor(payload.transport_mode)
    features["transport_cost_usd_ton_km"] = {
        "kara": 0.05,
        "deniz": 0.02,
        "demiryolu": 0.03,
        "hava": 0.50,
    }.get(payload.transport_mode, 0.05)

    # 3) FX what-if
    fx = apply_fx_scenario(payload.live_fx.model_dump(), payload.fx_scenario_pct)
    features["usd_try"] = fx["usd_try"]
    features["eur_try"] = fx["eur_try"]
    features["fx_scenario_pct"] = fx["fx_scenario_pct"]
    features["fx_source"] = fx["fx_source"]

    # 4) Demand score
    features["demand_score"] = float(
        load_buyer_demand_score(payload.target_country, features.get("buyer_sector", ""))
    )

    # 5) Model 2: Top-3 rota
    # M2_FEATURES'ta eksik kalan numerik kolonlar için varsayılan fiyat enjekte et,
    # böylece predict_proba NaN-only sayısal kolon almaz.
    default_route = _state["route_classes"][0] if _state["route_classes"] else "pomza_raw_sale"
    seed_features = _enrich_with_route_lookup(dict(features), default_route)
    for f in m2_features:
        seed_features.setdefault(f, None)

    X_route = _build_model_features(seed_features, m2_features)
    proba = np.asarray(m_route.predict_proba(X_route)[0])
    classes = _state["route_classes"]
    top3_idx = np.argsort(-proba)[: min(3, len(classes))]
    top3 = [(classes[i], float(proba[i])) for i in top3_idx]

    # 6) Her aday için profit (Model 1)
    route_alternatives: list[RouteOption] = []
    for route_name, prob in top3:
        feats_with_route = dict(features)
        feats_with_route["processing_route_candidate"] = route_name
        feats_with_route = _enrich_with_route_lookup(feats_with_route, route_name)
        for f in m1_features:
            feats_with_route.setdefault(f, None)
        X_profit = _build_model_features(feats_with_route, m1_features)
        predicted_profit = float(m_profit.predict(X_profit)[0])
        uplift = _compute_uplift(predicted_profit, feats_with_route)
        route_alternatives.append(
            RouteOption(
                route=route_name,
                predicted_profit_try=predicted_profit,
                value_uplift_pct=uplift,
                co2_kg=co2_kg,
                route_probability=prob,
            )
        )

    recommended = max(route_alternatives, key=lambda r: r.predicted_profit_try)

    # 7) B2B match (top-5)
    nearby = find_nearby_processors(
        payload.origin_city, payload.raw_material, radius_km=500
    )[:5]
    if not nearby:
        nearby = [{"name": "Default Processor", "city": payload.origin_city, "distance_km": 0.0}]
    buyers = [
        {
            "country": payload.target_country,
            "sector": features.get("buyer_sector", ""),
            "required_grade": payload.quality if payload.quality != "unknown" else "B",
            "name": payload.target_city or f"{payload.target_country} Buyer",
        }
    ]
    candidates = [(p, b) for p in nearby for b in buyers]
    matches_raw = match_buyers(
        producer={"quality_grade": payload.quality},
        candidates=candidates,
        context={
            "predicted_profit": recommended.predicted_profit_try,
            "total_distance_km": features["total_distance_km"],
            "co2_kg": co2_kg,
            "transport_mode": payload.transport_mode,
        },
        priority=payload.priority,
        top_k=5,
    )
    match_results = [
        MatchResult(
            processor_name=str(m["processor"].get("name", "?")),
            buyer_name=str(m["buyer"].get("name", "?")),
            score=float(m["score"]),
            components={k: float(v) for k, v in m["components"].items()},
        )
        for m in matches_raw
    ]

    # 8) Reason codes (predicted features dict üzerinde, recommended route ile)
    reason_features = dict(features)
    reason_features["processing_route_candidate"] = recommended.route
    reason_features = _enrich_with_route_lookup(reason_features, recommended.route)
    reasons_raw = generate_reason_codes(reason_features, m_profit, top_k=3)
    reasons = [
        ReasonCode(
            feature=str(r["feature"]),
            importance=float(r["importance"]),
            value=r["value"],
            text=str(r["text"]),
        )
        for r in reasons_raw
    ]

    # 9) Confidence breakdown
    conf = compute_overall_confidence(features, list(proba))
    confidence = ConfidenceBreakdown(
        data_confidence=int(conf["data_confidence"]),
        model_confidence=int(conf["model_confidence"]),
        overall=float(conf["overall"]),
        warnings=list(conf["warnings"]),
    )

    # 10) Top-10 feature importance (profit modeli)
    fi_list: list[FeatureImportance] = []
    if hasattr(m_profit, "feature_importances_"):
        names = list(
            getattr(m_profit, "feature_names_", []) or getattr(m_profit, "feature_names_in_", [])
        )
        if not names:
            names = [str(i) for i in range(len(m_profit.feature_importances_))]
        pairs = sorted(
            zip(names, m_profit.feature_importances_), key=lambda x: -x[1]
        )[:10]
        fi_list = [
            FeatureImportance(feature=str(n), importance=float(v)) for n, v in pairs
        ]

    return AnalyzeResponse(
        recommended_route=recommended.route,
        route_alternatives=route_alternatives,
        expected_profit_try=recommended.predicted_profit_try,
        value_uplift_pct=recommended.value_uplift_pct,
        co2_kg=co2_kg,
        co2_tonnes=co2_kg / 1000.0,
        match_results=match_results,
        reason_codes=reasons,
        confidence=confidence,
        feature_importance=fi_list,
        warnings=list(conf["warnings"]),
    )
