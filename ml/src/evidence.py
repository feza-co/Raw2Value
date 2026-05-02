"""model_evidence.json + metadata.json builder (rapor §10.1, §11.2).

build_model_evidence(): baseline + GBM + ablation + feature importance birleşimi.
build_metadata(): models klasöründeki pickled artefakt'ların contract dosyası.

Not: Bu modülün ana çalışma yolu doğrudan ``python -m ml.src.evidence``'tır.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# rapor §11.2: routes.parquet 15 ham × rota satırı içerir; modelimiz bunlardan
# sadece argmax kazanan ~10 tanesi için sentetik label görmüştür.
FULL_KNOWN_ROUTES: list[str] = [
    "pomza_raw_sale",
    "pomza_bims_aggregate",
    "pomza_micronized_pumice",
    "pomza_filtration_media",
    "pomza_textile_washing_stone",
    "perlit_raw_sale",
    "perlit_expanded_perlite",
    "perlit_agriculture_substrate",
    "perlit_insulation_filler",
    "perlit_filtration_product",
    "kabak_cekirdegi_bulk_sale",
    "kabak_cekirdegi_roasted_packaged",
    "kabak_cekirdegi_pumpkin_seed_oil",
    "kabak_cekirdegi_protein_powder",
    "kabak_cekirdegi_tourism_gift_pack",
]


def _top_features(model, k: int = 15) -> list[dict]:
    if not hasattr(model, "feature_importances_"):
        return []
    names = list(
        getattr(model, "feature_names_", []) or getattr(model, "feature_names_in_", [])
    )
    if not names:
        names = [str(i) for i in range(len(model.feature_importances_))]
    pairs = sorted(
        zip(names, model.feature_importances_), key=lambda x: -x[1]
    )[:k]
    return [{"feature": str(n), "importance": float(v)} for n, v in pairs]


def build_model_evidence() -> dict:
    """Tüm benchmark + ablation + feature importance bir araya getirilir."""
    baselines = json.loads(
        (PROCESSED_DIR / "baseline_results.json").read_text(encoding="utf-8")
    )
    gbm = json.loads(
        (PROCESSED_DIR / "gbm_results.json").read_text(encoding="utf-8")
    )
    ablation = json.loads(
        (PROCESSED_DIR / "ablation_results.json").read_text(encoding="utf-8")
    )

    df = pd.read_parquet(PROCESSED_DIR / "training_set_v1.parquet")
    n_total = int(len(df))

    profit_section = {**baselines["profit"], **gbm["profit"]}
    route_section = {**baselines["route"], **gbm["route"]}

    m_profit = joblib.load(MODELS_DIR / "model_profit.pkl")
    m_route = joblib.load(MODELS_DIR / "model_route.pkl")

    split = baselines.get("split", {})
    return {
        "version": "v1.0",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "n_total": n_total,
            "n_train": int(split.get("train", int(n_total * 0.8))),
            "n_val": int(split.get("val", int(n_total * 0.1))),
            "n_test": int(split.get("test", int(n_total * 0.1))),
            "split_strategy": "stratified_80_10_10",
            "stratify_on": split.get(
                "stratify_cols",
                ["raw_material", "processing_route_candidate"],
            ),
            "augmentation": "domain_informed_v1",
            "raw_reference_rows": 78,
        },
        "profit_regression": profit_section,
        "route_classification": route_section,
        "ablation": ablation,
        "feature_importance": {
            "model_profit": _top_features(m_profit, 15),
            "model_route": _top_features(m_route, 15),
        },
        "honesty_note": (
            "Sayılar augmented holdout üzerinde ölçüldü. "
            "Pilot gerçek veriyle yeniden kalibre edilecektir."
        ),
    }


def build_metadata() -> dict:
    """``models/metadata.json`` (rapor §11.2)."""
    m_profit = joblib.load(MODELS_DIR / "model_profit.pkl")
    m_route = joblib.load(MODELS_DIR / "model_route.pkl")

    profit_features = list(
        getattr(m_profit, "feature_names_", [])
        or getattr(m_profit, "feature_names_in_", [])
    )
    route_features = list(
        getattr(m_route, "feature_names_", [])
        or getattr(m_route, "feature_names_in_", [])
    )
    route_classes = [str(c) for c in getattr(m_route, "classes_", [])]
    missing = [r for r in FULL_KNOWN_ROUTES if r not in route_classes]

    return {
        "version": "v1.0",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "models": {
            "profit": {
                "type": type(m_profit).__name__.lower().replace("regressor", ""),
                "file": "model_profit.pkl",
                "feature_names": profit_features,
                "n_features": len(profit_features),
                "target": "expected_profit_try",
            },
            "route": {
                "type": type(m_route).__name__.lower().replace("classifier", ""),
                "file": "model_route.pkl",
                "feature_names": route_features,
                "n_features": len(route_features),
                "target": "recommended_route_label",
                "classes": route_classes,
                "all_known_routes": FULL_KNOWN_ROUTES,
                "missing_classes_in_trained_model": missing,
            },
        },
        "preprocessing": {
            "file": "feature_pipeline.pkl",
            "type": "ColumnTransformer",
            "imputation_strategy": "regional_default_for_advanced_fields",
        },
        "default_values": {
            "moisture_pct": {"pomza": 5.0, "perlit": 4.0, "kabak_cekirdegi": 7.0},
            "purity_pct": {"pomza": 92.0, "perlit": 95.0, "kabak_cekirdegi": 98.0},
            "particle_size_class": "medium",
            "lead_time_days": 7,
        },
        "reference_tables": {
            "distances": "data/reference/distances.parquet",
            "carbon_factors": "data/reference/carbon.parquet",
            "quality_match_matrix": "data/reference/quality_match.parquet",
            "processing_routes": "data/reference/routes.parquet",
            "organizations": "data/reference/organizations.parquet",
        },
        "notes": (
            f"Trained model kapsadığı sınıf sayısı = {len(route_classes)} "
            f"(15 ham rotanın {len(missing)}'sı argmax'ta hiç kazanmadığı için "
            "sentetik label'da görünmedi). Pilot gerçek veriyle yeniden balanslanacak."
        ),
    }


if __name__ == "__main__":
    ev = build_model_evidence()
    md = build_metadata()
    (MODELS_DIR / "model_evidence.json").write_text(
        json.dumps(ev, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (MODELS_DIR / "metadata.json").write_text(
        json.dumps(md, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote {MODELS_DIR / 'model_evidence.json'}")
    print(f"Wrote {MODELS_DIR / 'metadata.json'}")
