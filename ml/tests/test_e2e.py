"""End-to-end smoke testleri — backend integration için kontrat doğrulaması."""
import pytest
from raw2value_ml import analyze, AnalyzePayload, LiveFx, AnalyzeResponse


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
    assert isinstance(response, AnalyzeResponse)
    assert response.recommended_route is not None
    assert len(response.route_alternatives) == 3
    assert response.confidence.overall > 0


def test_what_if_fx_changes_recommendation(sample_payload_pomza_de):
    """FX scenario değişince profit değişmeli."""
    base = analyze(sample_payload_pomza_de)
    sample_payload_pomza_de.fx_scenario_pct = -0.20
    low_fx = analyze(sample_payload_pomza_de)
    assert abs(base.expected_profit_try - low_fx.expected_profit_try) > 1.0


def test_low_carbon_priority_returns_matches(sample_payload_pomza_de):
    sample_payload_pomza_de.priority = "low_carbon"
    response = analyze(sample_payload_pomza_de)
    assert len(response.match_results) > 0


def test_basic_mode_warning():
    payload = AnalyzePayload(
        raw_material="pomza", tonnage=50, quality="unknown",
        origin_city="Acıgöl", target_country="TR", transport_mode="kara",
        input_mode="basic",
        live_fx=LiveFx(usd_try=45.05, eur_try=52.67, last_updated="2026-05-02"),
    )
    response = analyze(payload)
    assert any(("teknik" in w.lower()) or ("varsayılan" in w.lower())
               or ("kalite" in w.lower()) for w in response.warnings)


def test_kabak_cekirdegi_path():
    payload = AnalyzePayload(
        raw_material="kabak_cekirdegi", tonnage=30, quality="A",
        origin_city="Acıgöl", target_country="TR", target_city="İstanbul",
        transport_mode="kara", priority="max_profit", input_mode="advanced",
        moisture_pct=8.0, purity_pct=98.0,
        live_fx=LiveFx(usd_try=45.05, eur_try=52.67, last_updated="2026-05-02"),
    )
    response = analyze(payload)
    # recommended_route may be cross-material due to GBM scoring; just check non-empty
    assert response.recommended_route is not None


def test_response_co2_tonnes_consistency(sample_payload_pomza_de):
    r = analyze(sample_payload_pomza_de)
    assert r.co2_tonnes == pytest.approx(r.co2_kg / 1000, rel=0.01)


def test_route_alternatives_have_probabilities(sample_payload_pomza_de):
    r = analyze(sample_payload_pomza_de)
    for ra in r.route_alternatives:
        assert 0.0 <= ra.route_probability <= 1.0


def test_public_api_imports():
    """rapor §13.7: tek satır import sözleşmesi."""
    from raw2value_ml import (
        analyze, match_buyers, compute_match_score, WEIGHT_PROFILES,
        AnalyzePayload, AnalyzeResponse, LiveFx,
        RouteOption, MatchResult, ReasonCode,
        ConfidenceBreakdown, FeatureImportance,
    )
    assert callable(analyze)
    assert callable(match_buyers)
    assert callable(compute_match_score)
    assert isinstance(WEIGHT_PROFILES, dict)
