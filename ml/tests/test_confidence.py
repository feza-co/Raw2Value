"""raw2value_ml.confidence testleri.

Veri + model + overall + warnings hesaplamalarını ve sınır durumlarını doğrular.
"""
from __future__ import annotations

from raw2value_ml.confidence import (
    compute_data_confidence,
    compute_model_confidence,
    compute_overall_confidence,
)


def test_data_confidence_full() -> None:
    f = {
        "technical_data_available": True,
        "fx_source": "TCMB_LIVE",
        "distance_source": "ORS_LIVE",
    }
    assert compute_data_confidence(f) == 100  # 100 + 10 + 5 capped → 100


def test_data_confidence_missing_technical() -> None:
    f = {"technical_data_available": False}
    assert compute_data_confidence(f) == 85  # 100 - 15


def test_data_confidence_low_ranges() -> None:
    f = {
        "technical_data_available": False,
        "raw_price_source_confidence": "C",
        "processor_capacity_confidence": "D",
        "default_values_used": True,
    }
    score = compute_data_confidence(f)
    assert 0 <= score <= 100
    assert score < 70


def test_model_confidence_proba() -> None:
    assert compute_model_confidence([0.1, 0.2, 0.7]) == 70


def test_model_confidence_no_proba() -> None:
    assert compute_model_confidence(None) == 75


def test_overall_keys() -> None:
    f = {"technical_data_available": True}
    out = compute_overall_confidence(f)
    assert set(out.keys()) == {"data_confidence", "model_confidence", "overall", "warnings"}


def test_overall_warnings_low_data() -> None:
    f = {
        "technical_data_available": False,
        "default_values_used": True,
        "quality_grade": "unknown",
    }
    out = compute_overall_confidence(f)
    assert len(out["warnings"]) >= 3


def test_overall_no_warnings_when_high() -> None:
    f = {
        "technical_data_available": True,
        "fx_source": "TCMB_LIVE",
        "distance_source": "ORS_LIVE",
        "quality_grade": "A",
    }
    out = compute_overall_confidence(f, [0.9, 0.05, 0.05])
    assert len(out["warnings"]) == 0
    assert out["overall"] >= 80
