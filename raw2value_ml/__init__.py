"""Raw2Value AI — ML inference paketi.

Backend tek satır import ile tüm karar mantığını çağırabilir:

    from raw2value_ml import analyze, AnalyzePayload, LiveFx
    response = analyze(payload)

Sözleşme: rapor §11.3 (sabit). Models klasörü: ./models/
"""

__version__ = "0.1.0"

from .inference import analyze
from .scorer import match_buyers, compute_match_score, WEIGHT_PROFILES
from .schemas import (
    AnalyzePayload,
    AnalyzeResponse,
    LiveFx,
    RouteOption,
    MatchResult,
    ReasonCode,
    ConfidenceBreakdown,
    FeatureImportance,
)

__all__ = [
    "__version__",
    "analyze",
    "match_buyers",
    "compute_match_score",
    "WEIGHT_PROFILES",
    "AnalyzePayload",
    "AnalyzeResponse",
    "LiveFx",
    "RouteOption",
    "MatchResult",
    "ReasonCode",
    "ConfidenceBreakdown",
    "FeatureImportance",
]
