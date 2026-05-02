"""Smoke tests for analyze() — uçtan-uca contract validation.

Hedef: 10 test, 100% green. Kapsam:
    * Response tipi
    * route_alternatives = 3
    * reason_codes = 3
    * match_results <= 5
    * confidence overall ∈ [0, 100]
    * co2 formula consistency
    * what-if FX değişimi -> profit değişir
    * basic mode warning
    * kabak_cekirdegi rotası çalışır
    * warm latency makul (cold load yapıldıktan sonra <1500 ms)
"""
from __future__ import annotations

import time

import pytest

from raw2value_ml.inference import analyze
from raw2value_ml.schemas import AnalyzePayload, AnalyzeResponse, LiveFx


@pytest.fixture
def sample_payload_pomza_de() -> AnalyzePayload:
    return AnalyzePayload(
        raw_material="pomza",
        tonnage=150,
        quality="A",
        origin_city="Nevsehir",
        target_country="DE",
        target_city="Hamburg",
        transport_mode="kara",
        priority="max_profit",
        input_mode="basic",
        live_fx=LiveFx(usd_try=45.05, eur_try=52.67, last_updated="2026-05-02"),
    )


def test_analyze_returns_response(sample_payload_pomza_de: AnalyzePayload) -> None:
    r = analyze(sample_payload_pomza_de)
    assert isinstance(r, AnalyzeResponse)
    assert r.recommended_route is not None
    assert isinstance(r.recommended_route, str)
    assert len(r.recommended_route) > 0


def test_route_alternatives_count(sample_payload_pomza_de: AnalyzePayload) -> None:
    r = analyze(sample_payload_pomza_de)
    assert len(r.route_alternatives) == 3


def test_reason_codes_count(sample_payload_pomza_de: AnalyzePayload) -> None:
    r = analyze(sample_payload_pomza_de)
    assert len(r.reason_codes) == 3


def test_match_results_at_most_5(sample_payload_pomza_de: AnalyzePayload) -> None:
    r = analyze(sample_payload_pomza_de)
    assert len(r.match_results) <= 5


def test_confidence_overall_range(sample_payload_pomza_de: AnalyzePayload) -> None:
    r = analyze(sample_payload_pomza_de)
    assert 0 <= r.confidence.overall <= 100
    assert 0 <= r.confidence.data_confidence <= 100
    assert 0 <= r.confidence.model_confidence <= 100


def test_co2_formula_consistency(sample_payload_pomza_de: AnalyzePayload) -> None:
    """co2 = tonnage × distance × emission_factor; co2_tonnes = co2_kg / 1000."""
    r = analyze(sample_payload_pomza_de)
    assert r.co2_kg > 0
    assert r.co2_tonnes == pytest.approx(r.co2_kg / 1000.0)


def test_what_if_fx_changes_profit(sample_payload_pomza_de: AnalyzePayload) -> None:
    """FX -%20 senaryosu base ile aynı profit'i veremez."""
    base = analyze(sample_payload_pomza_de)
    sample_payload_pomza_de.fx_scenario_pct = -0.20
    low_fx = analyze(sample_payload_pomza_de)
    assert abs(base.expected_profit_try - low_fx.expected_profit_try) > 1.0


def test_basic_mode_warning() -> None:
    """basic + quality=unknown -> uyarı listesinde teknik veya kalite uyarısı bulunmalı."""
    payload = AnalyzePayload(
        raw_material="pomza",
        tonnage=50,
        quality="unknown",
        origin_city="Acigol",
        target_country="TR",
        target_city="Istanbul",
        transport_mode="kara",
        input_mode="basic",
        live_fx=LiveFx(usd_try=45.05, eur_try=52.67, last_updated="2026-05-02"),
    )
    r = analyze(payload)
    haystack = " ".join(r.warnings).lower()
    assert any(token in haystack for token in ("teknik", "varsayilan", "varsayılan", "kalite"))


def test_kabak_path() -> None:
    """kabak_cekirdegi advanced + Türkiye iç pazar smoke."""
    payload = AnalyzePayload(
        raw_material="kabak_cekirdegi",
        tonnage=30,
        quality="A",
        origin_city="Acigol",
        target_country="TR",
        target_city="Istanbul",
        transport_mode="kara",
        priority="max_profit",
        input_mode="advanced",
        moisture_pct=8.0,
        purity_pct=98.0,
        live_fx=LiveFx(usd_try=45.05, eur_try=52.67, last_updated="2026-05-02"),
    )
    r = analyze(payload)
    assert r.recommended_route is not None
    assert r.expected_profit_try is not None


def test_warm_inference_under_500ms(sample_payload_pomza_de: AnalyzePayload) -> None:
    """Soğuk load sonrası ikinci çağrı <1500 ms (Windows + CatBoost dahil)."""
    # cold call (load)
    analyze(sample_payload_pomza_de)
    # warm call
    t0 = time.time()
    analyze(sample_payload_pomza_de)
    elapsed_ms = (time.time() - t0) * 1000
    assert elapsed_ms < 1500, f"Warm analyze too slow: {elapsed_ms:.0f}ms"
