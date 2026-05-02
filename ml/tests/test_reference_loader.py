"""raw2value_ml.reference_loader testleri.

Tüm loader fonksiyonlarının doğruluğunu ve lru_cache uygulanmış olduğunu doğrular.
"""
from __future__ import annotations

import pytest

from raw2value_ml.reference_loader import (
    load_buyer_demand_score,
    load_carbon_factors,
    load_delivery_risk,
    load_distance_lookup,
    load_organizations,
    load_quality_match_matrix,
    load_routes,
)


def test_load_routes_count() -> None:
    """15 işleme rotası beklenir (3 hammadde × 5 rota)."""
    assert load_routes().shape[0] == 15


def test_load_carbon_factors_keys() -> None:
    """4 API anahtarı (kara, deniz, hava, demiryolu) ve birebir hackathon değerleri."""
    factors = load_carbon_factors()
    assert set(factors.keys()) == {"kara", "deniz", "hava", "demiryolu"}
    assert factors["kara"] == 0.100
    assert factors["deniz"] == 0.015
    assert factors["hava"] == 0.500
    assert factors["demiryolu"] == 0.030


def test_load_carbon_factors_kara() -> None:
    """Kara taşıma hackathon resmi değeri 0.100 kg CO2/ton-km."""
    assert load_carbon_factors()["kara"] == 0.100


def test_load_quality_match_matrix_diag() -> None:
    """Tam eşleşme (A/A) skoru 1.0."""
    assert load_quality_match_matrix()[("A", "A")] == 1.0


def test_load_quality_match_matrix_penalty() -> None:
    """C üretici × A alıcı = 0.20 (iki kademe alt, reddedilir)."""
    assert load_quality_match_matrix()[("C", "A")] == 0.20


def test_load_organizations_pomza() -> None:
    """Pomza üreticileri en az 13 organizasyon."""
    df = load_organizations(material="pomza")
    assert df.shape[0] >= 13


def test_load_organizations_processor() -> None:
    """``filter_type='processor'`` -> tüm satırlar Tip == 'processor'."""
    df = load_organizations(filter_type="processor")
    assert (df["Tip"] == "processor").all()


def test_load_distance_lookup_type() -> None:
    """Lookup tuple anahtarlı ve dict döner."""
    lookup = load_distance_lookup()
    assert isinstance(lookup, dict)
    assert len(lookup) > 0
    sample_key = next(iter(lookup))
    assert isinstance(sample_key, tuple)
    assert len(sample_key) == 2
    assert isinstance(lookup[sample_key], dict)
    assert "km" in lookup[sample_key]
    assert "dakika" in lookup[sample_key]


def test_load_delivery_risk_kara() -> None:
    """Kara taşıma teslimat riski [0, 1] aralığında float."""
    risk = load_delivery_risk("kara")
    assert isinstance(risk, float)
    assert 0.0 <= risk <= 1.0


def test_load_buyer_demand_score_de_yapi() -> None:
    """DE × building_insulation skoru [0, 1] aralığında float."""
    score = load_buyer_demand_score("DE", "building_insulation")
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_lru_cache_decorator() -> None:
    """load_routes lru_cache ile sarmalanmış olmalı (cache_info() çağrılabilir)."""
    info = load_routes.cache_info()
    assert hasattr(info, "hits")
    assert hasattr(info, "misses")
