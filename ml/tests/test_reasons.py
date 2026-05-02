"""raw2value_ml.reasons testleri.

Türkçe template-tabanlı reason kod üretimini ve median-based high/low branş seçimini
doğrular.
"""
from __future__ import annotations

import joblib

from raw2value_ml.reasons import (
    REASON_TEMPLATES,
    _load_medians,
    generate_reason_codes,
)


def test_templates_count() -> None:
    """En az 12 feature template'i bulunmalı."""
    assert len(REASON_TEMPLATES) >= 12


def test_template_keys_have_high_low() -> None:
    for fname, t in REASON_TEMPLATES.items():
        assert "high" in t and "low" in t, f"{fname} missing high/low"


def test_medians_loaded() -> None:
    m = _load_medians()
    assert "total_distance_km" in m
    assert "usd_try" in m


def test_generate_reasons_top3() -> None:
    """Gerçek model + örnek feature dict → 3 Türkçe gerekçe."""
    model = joblib.load("models/model_profit.pkl")
    features = {
        "raw_material": "pomza",
        "tonnage": 150,
        "total_distance_km": 1240,
        "usd_try": 45.05,
        "eur_try": 52.67,
        "co2_kg": 18600,
        "demand_score": 0.7,
        "quality_match_score": 0.9,
        "delivery_risk": 0.15,
        "lead_time_days": 7,
        "data_confidence_score": 80,
        "processed_price_typical_usd_ton": 300,
        "raw_price_typical_usd_ton": 50,
        "processing_cost_typical_usd_ton": 45,
        "price_volatility_risk": 0.17,
        "fx_scenario_pct": 0.0,
    }
    reasons = generate_reason_codes(features, model, top_k=3)
    assert len(reasons) == 3
    for r in reasons:
        assert "text" in r and "feature" in r
        assert isinstance(r["text"], str) and len(r["text"]) > 5


def test_reasons_high_low_branch() -> None:
    """Median'a göre high vs low template seçimini doğrula."""
    model = joblib.load("models/model_profit.pkl")
    medians = _load_medians()
    huge_distance = float(medians["total_distance_km"]) * 5
    features = {
        "total_distance_km": huge_distance,
        "tonnage": 100,
        "usd_try": 45,
        "eur_try": 52,
        "co2_kg": 1000,
        "demand_score": 0.5,
        "quality_match_score": 0.5,
        "delivery_risk": 0.2,
        "lead_time_days": 7,
        "data_confidence_score": 80,
        "processed_price_typical_usd_ton": 100,
        "raw_price_typical_usd_ton": 50,
        "processing_cost_typical_usd_ton": 30,
        "price_volatility_risk": 0.2,
        "fx_scenario_pct": 0.0,
    }
    reasons = generate_reason_codes(features, model, top_k=5)
    dist_r = next((r for r in reasons if r["feature"] == "total_distance_km"), None)
    if dist_r is not None:
        assert "yükseltiyor" in dist_r["text"]


def test_reasons_no_crash_on_missing_feature() -> None:
    """Model eksik feature istediğinde defansif fallback."""
    model = joblib.load("models/model_profit.pkl")
    minimal = {"tonnage": 100}
    reasons = generate_reason_codes(minimal, model, top_k=3)
    assert isinstance(reasons, list)


def test_reason_text_is_turkish_unicode() -> None:
    model = joblib.load("models/model_profit.pkl")
    features = {f: v for f, v in zip(REASON_TEMPLATES.keys(), [100] * len(REASON_TEMPLATES))}
    features.update({"usd_try": 45.0, "eur_try": 52.0, "fx_scenario_pct": 0.0})
    reasons = generate_reason_codes(features, model, top_k=3)
    for r in reasons:
        assert (
            any(c in r["text"] for c in "ığüşöçİĞÜŞÖÇ")
            or "USD" in r["text"]
            or "ton" in r["text"]
            or "km" in r["text"]
        )
