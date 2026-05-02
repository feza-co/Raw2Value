"""raw2value_ml.scorer testleri.

ADIM 9 — B2B match scorer (rapor §8). Ağırlık profilleri, normalize sınırları,
kalite matrisi ve top-K sıralamasının doğruluğunu doğrular.
"""
from __future__ import annotations

import pytest

from raw2value_ml.scorer import (
    MAX_CO2_KG,
    MAX_DISTANCE_KM,
    MAX_PROFIT_TRY,
    WEIGHT_PROFILES,
    compute_match_score,
    match_buyers,
)


# ---------------------------------------------------------------------------
# Profil sözleşmesi
# ---------------------------------------------------------------------------
def test_weight_profiles_sum_to_1() -> None:
    """Her profilin ağırlık toplamı 1.0 olmalı (rapor §8.3)."""
    for name, weights in WEIGHT_PROFILES.items():
        s = sum(weights.values())
        assert abs(s - 1.0) < 1e-9, f"Profile {name!r} sum is {s}, expected 1.0"


def test_three_profiles_present() -> None:
    """max_profit, low_carbon, fast_delivery profilleri tanımlı olmalı."""
    assert set(WEIGHT_PROFILES.keys()) == {"max_profit", "low_carbon", "fast_delivery"}


def test_each_profile_has_six_components() -> None:
    """Her profil tam 6 komponent içermeli."""
    expected = {"profit", "demand", "distance", "carbon", "delivery", "quality"}
    for name, weights in WEIGHT_PROFILES.items():
        assert set(weights.keys()) == expected, f"Profile {name!r} missing keys"


# ---------------------------------------------------------------------------
# compute_match_score temel sözleşme
# ---------------------------------------------------------------------------
def test_compute_match_score_returns_tuple() -> None:
    """Skor 0-1 arası, components 6 alanlı, hepsi 0-1 arası."""
    score, components = compute_match_score(
        producer={"quality_grade": "A"},
        processor={"name": "p1"},
        buyer={"country": "DE", "sector": "building_insulation", "required_grade": "A"},
        context={
            "predicted_profit": 1_000_000,
            "total_distance_km": 1500,
            "co2_kg": 50_000,
            "transport_mode": "kara",
        },
        priority="max_profit",
    )
    assert 0.0 <= score <= 1.0
    assert set(components.keys()) == {
        "profit", "demand", "distance", "carbon", "delivery", "quality"
    }
    for k, v in components.items():
        assert 0.0 <= v <= 1.0, f"component {k}={v} out of [0,1]"


def test_invalid_priority_raises() -> None:
    """Bilinmeyen priority -> ValueError."""
    with pytest.raises(ValueError):
        compute_match_score(
            producer={"quality_grade": "A"},
            processor={},
            buyer={"country": "TR", "sector": "x", "required_grade": "B"},
            context={"predicted_profit": 0, "total_distance_km": 0, "co2_kg": 0,
                     "transport_mode": "kara"},
            priority="nonexistent",
        )


# ---------------------------------------------------------------------------
# match_buyers defensive davranış + sıralama
# ---------------------------------------------------------------------------
def test_match_buyers_empty() -> None:
    """Defensive: boş candidates -> boş liste."""
    out = match_buyers(producer={}, candidates=[], context={},
                       priority="max_profit", top_k=5)
    assert out == []


def test_match_buyers_topk_limit_and_sorted() -> None:
    """top_k sınırı uygulanır ve sonuçlar skora göre azalan sıralı döner."""
    candidates = [
        ({"name": f"p{i}"}, {"country": "TR", "sector": "building_insulation",
                              "required_grade": "B"})
        for i in range(20)
    ]
    out = match_buyers(
        producer={"quality_grade": "A"},
        candidates=candidates,
        context={
            "predicted_profit": 500_000,
            "total_distance_km": 800,
            "co2_kg": 5000,
            "transport_mode": "kara",
        },
        priority="max_profit",
        top_k=5,
    )
    assert len(out) == 5
    scores = [r["score"] for r in out]
    assert scores == sorted(scores, reverse=True)


def test_match_buyers_topk_exceeds_candidates() -> None:
    """top_k > len(candidates) -> tüm adaylar döner."""
    candidates = [
        ({"name": "p1"}, {"country": "DE", "sector": "building_insulation",
                          "required_grade": "A"}),
        ({"name": "p2"}, {"country": "DE", "sector": "building_insulation",
                          "required_grade": "B"}),
    ]
    out = match_buyers(
        producer={"quality_grade": "A"},
        candidates=candidates,
        context={"predicted_profit": 100_000, "total_distance_km": 500,
                 "co2_kg": 1000, "transport_mode": "kara"},
        priority="max_profit",
        top_k=10,
    )
    assert len(out) == 2


# ---------------------------------------------------------------------------
# Profil davranışı (ağırlık etkisi)
# ---------------------------------------------------------------------------
def test_low_carbon_profile_prefers_low_co2() -> None:
    """low_carbon profili altında düşük CO2'lu opsiyon yüksek CO2'yu geçmeli."""
    producer = {"quality_grade": "A"}
    processor = {"name": "p1"}
    buyer = {"country": "DE", "sector": "building_insulation", "required_grade": "A"}

    ctx_low = {
        "predicted_profit": 1_000_000,
        "total_distance_km": 1500,
        "co2_kg": 5_000,
        "transport_mode": "deniz",
    }
    ctx_high = {
        "predicted_profit": 1_000_000,
        "total_distance_km": 1500,
        "co2_kg": 150_000,
        "transport_mode": "hava",
    }

    s_low, _ = compute_match_score(producer, processor, buyer, ctx_low, "low_carbon")
    s_high, _ = compute_match_score(producer, processor, buyer, ctx_high, "low_carbon")
    assert s_low > s_high


def test_max_profit_profile_prefers_high_profit() -> None:
    """max_profit profilinde yüksek kâr opsiyonu üstte olmalı."""
    producer = {"quality_grade": "A"}
    processor = {"name": "p1"}
    buyer = {"country": "DE", "sector": "building_insulation", "required_grade": "A"}

    ctx_low = {
        "predicted_profit": 100_000,
        "total_distance_km": 1000,
        "co2_kg": 5000,
        "transport_mode": "kara",
    }
    ctx_high = {
        "predicted_profit": 4_000_000,
        "total_distance_km": 1000,
        "co2_kg": 5000,
        "transport_mode": "kara",
    }

    s_low, _ = compute_match_score(producer, processor, buyer, ctx_low, "max_profit")
    s_high, _ = compute_match_score(producer, processor, buyer, ctx_high, "max_profit")
    assert s_high > s_low


def test_fast_delivery_profile_prefers_low_risk_transport() -> None:
    """fast_delivery profilinde düşük teslimat riskli mod (kara) hava'yı geçmeli."""
    producer = {"quality_grade": "A"}
    processor = {"name": "p1"}
    buyer = {"country": "DE", "sector": "building_insulation", "required_grade": "A"}

    base_ctx = {
        "predicted_profit": 1_000_000,
        "total_distance_km": 1000,
        "co2_kg": 50_000,
    }
    ctx_kara = {**base_ctx, "transport_mode": "kara"}     # risk 0.15
    ctx_hava = {**base_ctx, "transport_mode": "hava"}     # risk 0.60

    s_kara, _ = compute_match_score(producer, processor, buyer, ctx_kara, "fast_delivery")
    s_hava, _ = compute_match_score(producer, processor, buyer, ctx_hava, "fast_delivery")
    assert s_kara > s_hava


# ---------------------------------------------------------------------------
# Quality matrix davranışı (rapor §8.4)
# ---------------------------------------------------------------------------
def test_quality_unknown_default() -> None:
    """unknown grade -> default 0.70 (rapor §8.4)."""
    _, components = compute_match_score(
        producer={"quality_grade": "unknown"},
        processor={},
        buyer={"country": "TR", "sector": "x", "required_grade": "A"},
        context={"predicted_profit": 0, "total_distance_km": 0, "co2_kg": 0,
                 "transport_mode": "kara"},
        priority="max_profit",
    )
    assert components["quality"] == 0.70


def test_quality_match_matrix_C_to_A() -> None:
    """C üretici × A alıcı = 0.20 (iki kademe alt, ağır cezalı)."""
    _, components = compute_match_score(
        producer={"quality_grade": "C"},
        processor={},
        buyer={"country": "TR", "sector": "x", "required_grade": "A"},
        context={"predicted_profit": 0, "total_distance_km": 0, "co2_kg": 0,
                 "transport_mode": "kara"},
        priority="max_profit",
    )
    assert components["quality"] == 0.20


def test_quality_match_matrix_A_to_A_perfect() -> None:
    """A × A tam eşleşme = 1.0."""
    _, components = compute_match_score(
        producer={"quality_grade": "A"},
        processor={},
        buyer={"country": "TR", "sector": "x", "required_grade": "A"},
        context={"predicted_profit": 0, "total_distance_km": 0, "co2_kg": 0,
                 "transport_mode": "kara"},
        priority="max_profit",
    )
    assert components["quality"] == 1.0


# ---------------------------------------------------------------------------
# Normalize sınır davranışı
# ---------------------------------------------------------------------------
def test_distance_normalize_perfect() -> None:
    """Distance 0 -> distance_score 1.0."""
    _, components = compute_match_score(
        producer={"quality_grade": "B"},
        processor={},
        buyer={"country": "TR", "sector": "x", "required_grade": "B"},
        context={"predicted_profit": 0, "total_distance_km": 0, "co2_kg": 0,
                 "transport_mode": "kara"},
        priority="max_profit",
    )
    assert components["distance"] == 1.0


def test_distance_normalize_max() -> None:
    """Distance >= MAX_DISTANCE_KM -> distance_score 0.0."""
    _, components = compute_match_score(
        producer={"quality_grade": "B"},
        processor={},
        buyer={"country": "TR", "sector": "x", "required_grade": "B"},
        context={"predicted_profit": 0, "total_distance_km": MAX_DISTANCE_KM + 100,
                 "co2_kg": 0, "transport_mode": "kara"},
        priority="max_profit",
    )
    assert components["distance"] == 0.0


def test_carbon_normalize_max() -> None:
    """CO2 >= MAX_CO2_KG -> carbon_score 0.0."""
    _, components = compute_match_score(
        producer={"quality_grade": "B"},
        processor={},
        buyer={"country": "TR", "sector": "x", "required_grade": "B"},
        context={"predicted_profit": 0, "total_distance_km": 0,
                 "co2_kg": MAX_CO2_KG + 1, "transport_mode": "kara"},
        priority="max_profit",
    )
    assert components["carbon"] == 0.0


def test_profit_normalize_clipped_above_max() -> None:
    """Kâr MAX_PROFIT_TRY üstünde -> profit_score 1.0'a kırpılır."""
    _, components = compute_match_score(
        producer={"quality_grade": "B"},
        processor={},
        buyer={"country": "TR", "sector": "x", "required_grade": "B"},
        context={"predicted_profit": MAX_PROFIT_TRY * 10, "total_distance_km": 0,
                 "co2_kg": 0, "transport_mode": "kara"},
        priority="max_profit",
    )
    assert components["profit"] == 1.0


def test_profit_normalize_negative_clipped_to_zero() -> None:
    """Negatif kâr -> profit_score 0.0'a kırpılır."""
    _, components = compute_match_score(
        producer={"quality_grade": "B"},
        processor={},
        buyer={"country": "TR", "sector": "x", "required_grade": "B"},
        context={"predicted_profit": -1_000_000, "total_distance_km": 0,
                 "co2_kg": 0, "transport_mode": "kara"},
        priority="max_profit",
    )
    assert components["profit"] == 0.0
