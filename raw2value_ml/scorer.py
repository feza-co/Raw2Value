"""B2B match scorer — weighted scoring with priority profiles (rapor §8).

Bu bir model değil, deterministik bir fonksiyondur. Eğitilmemiştir.
Ağırlıklar görünürdür ve ``priority`` parametresine göre dinamik değişir.
"""
from __future__ import annotations

from typing import Any

from .reference_loader import (
    load_buyer_demand_score,
    load_delivery_risk,
    load_quality_match_matrix,
)

# Ağırlık profilleri (rapor §8.3) — her profilin toplamı 1.0'dır.
WEIGHT_PROFILES: dict[str, dict[str, float]] = {
    "max_profit": {
        "profit": 0.35,
        "demand": 0.20,
        "distance": 0.15,
        "carbon": 0.15,
        "delivery": 0.10,
        "quality": 0.05,
    },
    "low_carbon": {
        "profit": 0.25,
        "demand": 0.15,
        "distance": 0.10,
        "carbon": 0.30,
        "delivery": 0.15,
        "quality": 0.05,
    },
    "fast_delivery": {
        "profit": 0.25,
        "demand": 0.15,
        "distance": 0.20,
        "carbon": 0.10,
        "delivery": 0.25,
        "quality": 0.05,
    },
}

# Normalize sabitleri (rapor §8.2). Training set 95-percentile'a yakın seçildi.
MAX_DISTANCE_KM: float = 3000.0       # TR-DE kara üst sınırı
MAX_CO2_KG: float = 200_000.0
MAX_PROFIT_TRY: float = 5_000_000.0   # ~p95 training profit (~5M TRY)

# Quality match defaultları (rapor §8.4).
_QUALITY_UNKNOWN_DEFAULT: float = 0.70  # unknown grade -> orta skor
_QUALITY_FALLBACK: float = 0.50          # matriste bulunamayan kombinasyon


def _clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """[lo, hi] aralığına kırpar."""
    return max(lo, min(hi, x))


def compute_match_score(
    producer: dict[str, Any],
    processor: dict[str, Any],
    buyer: dict[str, Any],
    context: dict[str, Any],
    priority: str = "max_profit",
) -> tuple[float, dict[str, float]]:
    """Verilen üretici/işleyici/alıcı kombinasyonu için 0–1 arası skor üretir.

    Args:
        producer: ``{"quality_grade": "A"|"B"|"C"|"unknown", ...}``.
        processor: İşleyici dict — MVP'de bypass; ileride kapasite/sertifika için.
        buyer: ``{"country": "TR"|"DE"|"NL", "sector": str,
            "required_grade": "A"|"B"|"C"|"unknown", ...}``.
        context: ``{"predicted_profit": float, "total_distance_km": float,
            "co2_kg": float, "transport_mode": "kara"|"deniz"|"demiryolu"|"hava", ...}``.
        priority: ``WEIGHT_PROFILES`` anahtarı.

    Returns:
        ``(score, components)`` — ``score`` 0–1 arası, ``components``
        6 bileşenli dict (profit, demand, distance, carbon, delivery, quality).

    Raises:
        ValueError: ``priority`` bilinmeyen bir profil ise.
    """
    if priority not in WEIGHT_PROFILES:
        raise ValueError(
            f"Unknown priority: {priority!r}. "
            f"Valid: {sorted(WEIGHT_PROFILES.keys())}"
        )

    weights = WEIGHT_PROFILES[priority]

    # 1. Profit (positive normalize) — yüksek kâr daha iyi.
    predicted_profit = float(context.get("predicted_profit", 0.0))
    profit_score = _clip(predicted_profit / MAX_PROFIT_TRY, 0.0, 1.0)

    # 2. Demand — buyer_markets'tan ülke + sektör bazlı 0-1 skoru.
    demand_score = _clip(
        load_buyer_demand_score(
            buyer.get("country", "TR"),
            buyer.get("sector", ""),
        ),
        0.0,
        1.0,
    )

    # 3. Distance — daha yakın daha iyi (1 - normalize).
    total_distance_km = float(context.get("total_distance_km", 0.0))
    distance_score = 1.0 - _clip(total_distance_km / MAX_DISTANCE_KM, 0.0, 1.0)

    # 4. Carbon — daha az emisyon daha iyi (1 - normalize).
    co2_kg = float(context.get("co2_kg", 0.0))
    carbon_score = 1.0 - _clip(co2_kg / MAX_CO2_KG, 0.0, 1.0)

    # 5. Delivery — daha az risk daha iyi.
    transport_mode = context.get("transport_mode", "kara")
    try:
        delivery_score = 1.0 - _clip(load_delivery_risk(transport_mode), 0.0, 1.0)
    except (KeyError, ValueError, FileNotFoundError):
        delivery_score = 0.5  # defensive: bilinmeyen mod -> nötr

    # 6. Quality match — producer × buyer grade lookup.
    p_grade = str(producer.get("quality_grade", "unknown"))
    b_grade = str(buyer.get("required_grade", "B"))
    if p_grade == "unknown" or b_grade == "unknown":
        quality_score = _QUALITY_UNKNOWN_DEFAULT
    else:
        try:
            qm = load_quality_match_matrix()
        except (KeyError, ValueError, FileNotFoundError):
            qm = {}
        quality_score = float(qm.get((p_grade, b_grade), _QUALITY_FALLBACK))
    quality_score = _clip(quality_score, 0.0, 1.0)

    components: dict[str, float] = {
        "profit": profit_score,
        "demand": demand_score,
        "distance": distance_score,
        "carbon": carbon_score,
        "delivery": delivery_score,
        "quality": quality_score,
    }

    score = sum(weights[k] * components[k] for k in weights)
    return _clip(score, 0.0, 1.0), components


def match_buyers(
    producer: dict[str, Any],
    candidates: list[tuple[dict[str, Any], dict[str, Any]]],
    context: dict[str, Any],
    priority: str = "max_profit",
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Aday (processor, buyer) çiftlerini skorlayıp Top-K listesini döner.

    Args:
        producer: Üretici dict.
        candidates: ``[(processor, buyer), ...]`` adayları. Boş liste verilirse
            defensive olarak boş liste döner.
        context: Skor için bağlam (predicted_profit, total_distance_km,
            co2_kg, transport_mode).
        priority: ``"max_profit" | "low_carbon" | "fast_delivery"``.
        top_k: Kaç sonuç döndürüleceği (varsayılan 5). ``len(candidates)``
            top_k'dan azsa hepsi döner.

    Returns:
        Skoruna göre azalan sırada
        ``[{"processor", "buyer", "score", "components"}, ...]`` listesi.
    """
    if not candidates:
        return []

    scored: list[dict[str, Any]] = []
    for processor, buyer in candidates:
        score, components = compute_match_score(
            producer, processor, buyer, context, priority=priority,
        )
        scored.append(
            {
                "processor": processor,
                "buyer": buyer,
                "score": score,
                "components": components,
            }
        )

    return sorted(scored, key=lambda x: -x["score"])[:top_k]
