"""Target leakage testleri (KRITIK).

Rapor §5.4'teki leakage kurallarini kod duzeyinde dogrular. Bu testlerden
herhangi biri kirmizi olursa egitim/inference dogru calismiyor demektir.
"""
from __future__ import annotations

import pytest

from ml.src.features import M1_FEATURES, M2_FEATURES


# ---------------------------------------------------------------------------
# Model 1 — profit regression (input: rota verili)
# ---------------------------------------------------------------------------
def test_m1_no_profit_target() -> None:
    assert "expected_profit_try" not in M1_FEATURES


def test_m1_no_uplift() -> None:
    assert "value_uplift_pct" not in M1_FEATURES


def test_m1_no_route_label() -> None:
    assert "recommended_route_label" not in M1_FEATURES


def test_m1_no_match_score() -> None:
    assert "match_score" not in M1_FEATURES


def test_m1_no_route_score() -> None:
    # route_score ham target uretim aracidir; modele girmemeli
    assert "route_score" not in M1_FEATURES


def test_m1_has_route_candidate() -> None:
    """processing_route_candidate Model 1'de input'tur (rota verili kabul edilir)."""
    assert "processing_route_candidate" in M1_FEATURES


# ---------------------------------------------------------------------------
# Model 2 — route classifier (target: rota)
# ---------------------------------------------------------------------------
def test_m2_no_profit() -> None:
    assert "expected_profit_try" not in M2_FEATURES


def test_m2_no_uplift() -> None:
    assert "value_uplift_pct" not in M2_FEATURES


def test_m2_no_route_label() -> None:
    """recommended_route_label Model 2'nin TARGET'idir; input olamaz."""
    assert "recommended_route_label" not in M2_FEATURES


def test_m2_no_route_candidate() -> None:
    """processing_route_candidate Model 2'nin TARGET turevidir; input olmamali."""
    assert "processing_route_candidate" not in M2_FEATURES


def test_m2_no_match_score() -> None:
    assert "match_score" not in M2_FEATURES


def test_m2_no_route_score() -> None:
    assert "route_score" not in M2_FEATURES


def test_m2_has_priority() -> None:
    """priority kullanici onceligi rota seciminde sinyaldir."""
    assert "priority" in M2_FEATURES


# ---------------------------------------------------------------------------
# Karsilastirma — M1 vs M2 farki
# ---------------------------------------------------------------------------
def test_m1_m2_overlap_consistency() -> None:
    """M1 ile M2 arasinda fark sadece processing_route_candidate (M1'de var) ve priority (M2'de var)."""
    only_in_m1 = set(M1_FEATURES) - set(M2_FEATURES)
    only_in_m2 = set(M2_FEATURES) - set(M1_FEATURES)
    assert only_in_m1 == {"processing_route_candidate"}
    assert only_in_m2 == {"priority"}
