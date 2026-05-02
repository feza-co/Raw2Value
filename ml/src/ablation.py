"""Ablation calismasi (rapor §10.2 — Adim 7).

Her senaryoda belirli bir feature grubu cikarilir ve full-retrain ile
sonuc olculur. K1 (karbon), K2 (kur), K3 (geo) gruplarinin modelin karar
mekanizmasinda load-bearing oldugunu gostermek icin.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, CatBoostRegressor
from lightgbm import LGBMClassifier, LGBMRegressor, early_stopping, log_evaluation
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier, XGBRegressor

from .baselines import evaluate_classification, evaluate_regression, stratified_split
from .feature_pipeline import (
    HIGH_CARDINALITY,
    LOW_CARDINALITY,
    build_feature_pipeline,
)
from .features import BOOLEAN_FEATURES, M1_FEATURES
from .train_profit import (
    CATBOOST_PARAMS as PROFIT_CB_PARAMS,
    LIGHTGBM_PARAMS as PROFIT_LGB_PARAMS,
    XGBOOST_PARAMS as PROFIT_XGB_PARAMS,
)
from .train_route import (
    CATBOOST_PARAMS as ROUTE_CB_PARAMS,
    LIGHTGBM_PARAMS as ROUTE_LGB_PARAMS,
    XGBOOST_PARAMS as ROUTE_XGB_PARAMS,
)


# ---------------------------------------------------------------------------
# Ablation gruplari (rapor §10.2)
# ---------------------------------------------------------------------------
ABLATION_GROUPS: dict[str, list[str]] = {
    "full_features": [],  # baseline
    "without_fx": ["usd_try", "eur_try", "fx_scenario_pct"],
    "without_geo": [
        "source_to_processor_km",
        "processor_to_buyer_km",
        "total_distance_km",
    ],
    "without_carbon": ["emission_factor_kg_co2_ton_km", "co2_kg"],
    "without_demand": ["demand_score", "buyer_sector", "buyer_country"],
    "without_quality": [
        "quality_grade",
        "quality_match_score",
        "moisture_pct",
        "purity_pct",
    ],
    "without_cost": [
        "processing_cost_typical_usd_ton",
        "packaging_cost_usd_ton",
        "transport_cost_usd_ton_km",
    ],
}

# Turkce yorumlama metinleri (rapor §10.1 + §10.2 tablosu)
ABLATION_INTERPRETATIONS: dict[str, str] = {
    "full_features": (
        "Tum feature'lar mevcut — referans (baseline). RMSE delta=0% bu senaryodadir."
    ),
    "without_fx": (
        "Kur feature'lari (usd_try, eur_try, fx_scenario_pct) cikarildi. "
        "ihracat rotalari (DE/NL alicilari) zayifliyor; modelin TRY-cinsi profit tahmini bozuluyor."
    ),
    "without_geo": (
        "Cografi mesafe feature'lari (source-processor-buyer km) cikarildi. "
        "Eslesme (matching) bozuluyor; transport maliyeti ve CO2 dolayli olarak gorunmez kaliyor."
    ),
    "without_carbon": (
        "Karbon feature'lari (emission_factor, co2_kg) cikarildi. "
        "low_carbon priority sinyali kaybolur; karbon onceligi etkisizlesir."
    ),
    "without_demand": (
        "Talep feature'lari (demand_score, buyer_sector, buyer_country) cikarildi. "
        "Pazar uygunlugu zayiflar; ayni uretici icin tum alici ulkelerine ayni tahmin gelir."
    ),
    "without_quality": (
        "Kalite feature'lari (grade, match_score, moisture, purity) cikarildi. "
        "Premium pazar (DE/NL) ile yerel pazar (TR) arasindaki ayrim kayboluyor."
    ),
    "without_cost": (
        "Maliyet feature'lari (processing_cost, packaging, transport_cost) cikarildi. "
        "Kar tahmini onemli olcude bozulur; yuksek-marjinli rotalar ile dusuk-marjinliler ayirt edilemez."
    ),
}


# ---------------------------------------------------------------------------
# Yardimcilar — model fabrikalari
# ---------------------------------------------------------------------------
def _make_profit_model(kind: str):
    if kind == "xgboost":
        return XGBRegressor(**PROFIT_XGB_PARAMS)
    if kind == "lightgbm":
        return LGBMRegressor(**PROFIT_LGB_PARAMS)
    if kind == "catboost":
        return CatBoostRegressor(**PROFIT_CB_PARAMS)
    raise ValueError(kind)


def _make_route_model(kind: str, num_class: int):
    if kind == "xgboost":
        return XGBClassifier(num_class=num_class, **ROUTE_XGB_PARAMS)
    if kind == "lightgbm":
        return LGBMClassifier(num_class=num_class, **ROUTE_LGB_PARAMS)
    if kind == "catboost":
        return CatBoostClassifier(**ROUTE_CB_PARAMS)
    raise ValueError(kind)


def _profit_feat_cols(df: pd.DataFrame, drop: list[str]) -> list[str]:
    """M1 + boolean'lar - drop, dedup'lu."""
    seen: set[str] = set()
    cols: list[str] = []
    for c in M1_FEATURES + BOOLEAN_FEATURES:
        if c in seen or c not in df.columns or c in drop:
            continue
        seen.add(c)
        cols.append(c)
    return cols


def _route_feat_cols(df: pd.DataFrame, drop: list[str]) -> list[str]:
    candidates = [c for c in M1_FEATURES if c != "processing_route_candidate"]
    candidates += ["priority"]
    candidates += BOOLEAN_FEATURES
    seen: set[str] = set()
    cols: list[str] = []
    for c in candidates:
        if c in seen or c not in df.columns or c in drop:
            continue
        seen.add(c)
        cols.append(c)
    return cols


def _prepare_cb_frame(
    df_part: pd.DataFrame, feat_cols: list[str]
) -> tuple[pd.DataFrame, list[str]]:
    """CatBoost icin kategorik->str, bool->int, numerik->median impute."""
    out = df_part[feat_cols].copy()
    cat_features = [c for c in (LOW_CARDINALITY + HIGH_CARDINALITY) if c in feat_cols]
    for c in cat_features:
        out[c] = out[c].fillna("MISSING").astype(str)
    for c in BOOLEAN_FEATURES:
        if c in out.columns:
            out[c] = out[c].astype(int)
    for c in out.columns:
        if c in cat_features:
            continue
        if out[c].dtype.kind in "fi":
            out[c] = out[c].fillna(out[c].median())
    return out, cat_features


# ---------------------------------------------------------------------------
# Tek senaryo egitimi
# ---------------------------------------------------------------------------
def _train_profit_one(
    df: pd.DataFrame, drop: list[str], best_kind: str, seed: int
) -> dict[str, float]:
    feat_cols = _profit_feat_cols(df, drop)
    train, val, test = stratified_split(
        df, "expected_profit_try",
        stratify_cols=["raw_material", "processing_route_candidate"], seed=seed,
    )
    y_train = train["expected_profit_try"].values
    y_val = val["expected_profit_try"].values
    y_test = test["expected_profit_try"].values

    if best_kind == "catboost":
        df_tr, cat_features = _prepare_cb_frame(train, feat_cols)
        df_va, _ = _prepare_cb_frame(val, feat_cols)
        df_te, _ = _prepare_cb_frame(test, feat_cols)
        model = _make_profit_model("catboost")
        model.fit(df_tr, y_train, cat_features=cat_features,
                  eval_set=(df_va, y_val), verbose=False)
        y_pred = model.predict(df_te)
    else:
        pipe = build_feature_pipeline(best_kind, df_columns=feat_cols)
        pipe.fit(df[feat_cols])
        X_tr = pipe.transform(train[feat_cols])
        X_va = pipe.transform(val[feat_cols])
        X_te = pipe.transform(test[feat_cols])
        model = _make_profit_model(best_kind)
        if best_kind == "lightgbm":
            model.fit(X_tr, y_train, eval_set=[(X_va, y_val)],
                      callbacks=[early_stopping(30, verbose=False), log_evaluation(0)])
        else:
            model.fit(X_tr, y_train, eval_set=[(X_va, y_val)], verbose=False)
        y_pred = model.predict(X_te)

    return evaluate_regression(y_test, y_pred)


def _train_route_one(
    df: pd.DataFrame, drop: list[str], best_kind: str, seed: int
) -> dict[str, float]:
    feat_cols = _route_feat_cols(df, drop)
    classes = sorted(df["recommended_route_label"].unique().tolist())
    train, val, test = stratified_split(
        df, "recommended_route_label",
        stratify_cols=["raw_material"], seed=seed,
    )
    y_train_raw = train["recommended_route_label"].values
    y_val_raw = val["recommended_route_label"].values
    y_test_raw = test["recommended_route_label"].values

    if best_kind == "catboost":
        df_tr, cat_features = _prepare_cb_frame(train, feat_cols)
        df_va, _ = _prepare_cb_frame(val, feat_cols)
        df_te, _ = _prepare_cb_frame(test, feat_cols)
        model = _make_route_model("catboost", num_class=len(classes))
        model.fit(df_tr, y_train_raw, cat_features=cat_features,
                  eval_set=(df_va, y_val_raw), verbose=False)
        y_pred = model.predict(df_te).flatten()
    else:
        pipe = build_feature_pipeline(best_kind, df_columns=feat_cols)
        pipe.fit(df[feat_cols])
        X_tr = pipe.transform(train[feat_cols])
        X_va = pipe.transform(val[feat_cols])
        X_te = pipe.transform(test[feat_cols])
        le = LabelEncoder().fit(classes)
        y_tr = le.transform(y_train_raw)
        y_va = le.transform(y_val_raw)
        sw = compute_sample_weight("balanced", y_tr)
        model = _make_route_model(best_kind, num_class=len(classes))
        if best_kind == "lightgbm":
            model.fit(X_tr, y_tr, sample_weight=sw, eval_set=[(X_va, y_va)],
                      callbacks=[early_stopping(30, verbose=False), log_evaluation(0)])
        else:
            model.fit(X_tr, y_tr, sample_weight=sw, eval_set=[(X_va, y_va)], verbose=False)
        y_pred = le.inverse_transform(model.predict(X_te))

    return evaluate_classification(y_test_raw, y_pred)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def run_ablation(
    df: pd.DataFrame,
    best_profit_kind: str = "catboost",
    best_route_kind: str = "catboost",
    seed: int = 42,
) -> dict[str, dict]:
    """7 senaryo (full + 6 ablation) icin profit ve route metriklerini hesaplar.

    Returns:
        {
          "full_features": {"profit_rmse":..., "profit_mae":..., "route_macro_f1":..., "rmse_delta_pct": 0.0, "interpretation": "..."},
          "without_fx":    {... "rmse_delta_pct": +X.X%, ...},
          ...
        }
    """
    results: dict[str, dict] = {}
    full_rmse: float | None = None

    for name, drop in ABLATION_GROUPS.items():
        warnings.filterwarnings("ignore")
        m_p = _train_profit_one(df, drop, best_profit_kind, seed)
        m_r = _train_route_one(df, drop, best_route_kind, seed)

        if name == "full_features":
            full_rmse = m_p["rmse"]
            delta_pct = 0.0
        else:
            assert full_rmse is not None, "full_features must run first"
            delta_pct = float((m_p["rmse"] - full_rmse) / full_rmse * 100.0)

        results[name] = {
            "profit_rmse": float(m_p["rmse"]),
            "profit_mae": float(m_p["mae"]),
            "profit_r2": float(m_p["r2"]),
            "profit_mape": float(m_p["mape"]),
            "route_accuracy": float(m_r["accuracy"]),
            "route_macro_f1": float(m_r["macro_f1"]),
            "rmse_delta_pct": delta_pct,
            "interpretation": ABLATION_INTERPRETATIONS[name],
        }

    return results
