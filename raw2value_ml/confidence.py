"""Confidence breakdown — data + model + overall + warnings.

Veri güven skoru: kaynak güvenilirliği ve eksik bilgi düşürür, canlı API kaynağı yükseltir.
Model güven skoru: multi-class proba'dan top-1 olasılık; regresyon için sabit MVP placeholder.
Overall: 0.4 * data + 0.6 * model.
"""
from __future__ import annotations

from typing import Any, Sequence


def compute_data_confidence(features: dict[str, Any]) -> int:
    """Veri güven skoru 0-100. Default 100, eksik bilgi düşürür, canlı kaynak yükseltir."""
    score = 100
    if not features.get("technical_data_available", False):
        score -= 15
    if features.get("raw_price_source_confidence") in ("C", "D"):
        score -= 10
    if features.get("processor_capacity_confidence") in ("C", "D"):
        score -= 5
    if features.get("fx_source") == "TCMB_LIVE":
        score += 10
    if features.get("distance_source") == "ORS_LIVE":
        score += 5
    if features.get("default_values_used"):
        score -= 8
    return max(0, min(100, score))


def compute_model_confidence(prediction_proba: Sequence[float] | None = None) -> int:
    """Model güven skoru 0-100. Multi-class proba'dan top-1, regresyon için sabit."""
    if prediction_proba is not None and len(prediction_proba) > 0:
        return int(round(max(prediction_proba) * 100))
    return 75  # MVP placeholder for regression


def compute_overall_confidence(
    features: dict[str, Any],
    prediction_proba: Sequence[float] | None = None,
) -> dict[str, Any]:
    """Birleşik confidence breakdown. Returns dict with 4 keys."""
    data_conf = compute_data_confidence(features)
    model_conf = compute_model_confidence(prediction_proba)
    overall = round(data_conf * 0.4 + model_conf * 0.6, 1)

    warnings: list[str] = []
    if not features.get("technical_data_available", False):
        warnings.append(
            "Teknik analiz verisi girilmedi; sistem bölgesel varsayılanları kullandı."
        )
    if features.get("default_values_used"):
        warnings.append(
            "Bazı değerler için varsayılan kullanıldı; güven skoru düşürüldü."
        )
    if features.get("quality_grade") == "unknown":
        warnings.append("Kalite sınıfı belirsiz; öneri orta tahminle hesaplandı.")
    if data_conf < 70:
        warnings.append(
            f"Veri güven skoru ({data_conf}/100) düşük — sonuçları temkinli yorumlayın."
        )

    return {
        "data_confidence": data_conf,
        "model_confidence": model_conf,
        "overall": overall,
        "warnings": warnings,
    }
