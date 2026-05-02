"""GBDT profit regression — XGBoost / LightGBM / CatBoost benchmark (Adim 6).

train_profit_models() 3 modeli ayni split uzerinde fit eder, RMSE'ye gore
en iyiyi secer. CatBoost icin native categorical handling kullanilir
(ColumnTransformer'in catboost variant'i).
"""
from __future__ import annotations

import time
import warnings
from typing import Any

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor, early_stopping, log_evaluation
from xgboost import XGBRegressor

from .baselines import evaluate_regression, stratified_split
from .feature_pipeline import build_feature_pipeline
from .features import BOOLEAN_FEATURES, M1_FEATURES


# ---------------------------------------------------------------------------
# Hiperparametre setleri (rapor §6.3, sabit MVP)
# ---------------------------------------------------------------------------
XGBOOST_PARAMS: dict[str, Any] = {
    "objective": "reg:squarederror",
    "n_estimators": 500,
    "max_depth": 6,
    "learning_rate": 0.1,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "min_child_weight": 3,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "random_state": 42,
    "early_stopping_rounds": 30,
    "eval_metric": "rmse",
    "verbosity": 0,
}

LIGHTGBM_PARAMS: dict[str, Any] = {
    "objective": "regression",
    "n_estimators": 500,
    "num_leaves": 31,
    "learning_rate": 0.05,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "min_child_samples": 10,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "random_state": 42,
    "metric": "rmse",
    "verbosity": -1,
}

CATBOOST_PARAMS: dict[str, Any] = {
    "iterations": 500,
    "depth": 6,
    "learning_rate": 0.05,
    "l2_leaf_reg": 3.0,
    "loss_function": "RMSE",
    "eval_metric": "RMSE",
    "random_seed": 42,
    "early_stopping_rounds": 30,
    "verbose": 0,
}


# ---------------------------------------------------------------------------
# Yardimcilar
# ---------------------------------------------------------------------------
def _unique_feature_cols(df: pd.DataFrame) -> list[str]:
    seen: set[str] = set()
    cols: list[str] = []
    for c in M1_FEATURES + BOOLEAN_FEATURES:
        if c in seen or c not in df.columns:
            continue
        seen.add(c)
        cols.append(c)
    return cols


# ---------------------------------------------------------------------------
# Egitim API
# ---------------------------------------------------------------------------
def train_profit_models(
    df: pd.DataFrame,
    pipeline_xgb_lgb=None,
    seed: int = 42,
) -> tuple[dict[str, dict[str, float]], str, dict[str, Any]]:
    """3 GBDT'yi ayni 80/10/10 split uzerinde fit eder.

    Args:
        df: Augmentation DataFrame (training_set_v1).
        pipeline_xgb_lgb: Onceden fit edilmis (XGB/LGB icin) ColumnTransformer.
            None ise build_feature_pipeline('xgboost') + fit.
        seed: stratified_split ve modeller icin random_state.

    Returns:
        ``(metrics_dict, best_kind, models_dict)``
        - metrics_dict: ``{"xgboost": {...}, "lightgbm": {...}, "catboost": {...}}``
        - best_kind: en iyi RMSE'ye sahip model adi
        - models_dict: ``{"xgboost": fitted, "lightgbm": fitted, "catboost": fitted}``
    """
    feat_cols = _unique_feature_cols(df)

    train, val, test = stratified_split(
        df,
        target_col="expected_profit_try",
        stratify_cols=["raw_material", "processing_route_candidate"],
        seed=seed,
    )
    y_train = train["expected_profit_try"].values
    y_val = val["expected_profit_try"].values
    y_test = test["expected_profit_try"].values

    if pipeline_xgb_lgb is None:
        pipeline_xgb_lgb = build_feature_pipeline("xgboost", df_columns=feat_cols)
        pipeline_xgb_lgb.fit(df[feat_cols])

    X_train = pipeline_xgb_lgb.transform(train[feat_cols])
    X_val = pipeline_xgb_lgb.transform(val[feat_cols])
    X_test = pipeline_xgb_lgb.transform(test[feat_cols])

    metrics: dict[str, dict[str, float]] = {}
    models: dict[str, Any] = {}

    # 1) XGBoost
    t0 = time.time()
    xgb = XGBRegressor(**XGBOOST_PARAMS)
    xgb.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    elapsed = time.time() - t0
    m = evaluate_regression(y_test, xgb.predict(X_test))
    m["train_sec"] = elapsed
    metrics["xgboost"] = m
    models["xgboost"] = xgb

    # 2) LightGBM
    t0 = time.time()
    lgb = LGBMRegressor(**LIGHTGBM_PARAMS)
    lgb.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[early_stopping(stopping_rounds=30, verbose=False), log_evaluation(0)],
    )
    elapsed = time.time() - t0
    m = evaluate_regression(y_test, lgb.predict(X_test))
    m["train_sec"] = elapsed
    metrics["lightgbm"] = m
    models["lightgbm"] = lgb

    # 3) CatBoost — native categorical, ham df uzerinde fit
    t0 = time.time()
    from .feature_pipeline import HIGH_CARDINALITY, LOW_CARDINALITY

    cat_features = [c for c in (LOW_CARDINALITY + HIGH_CARDINALITY) if c in feat_cols]
    df_train_cb = train[feat_cols].copy()
    df_val_cb = val[feat_cols].copy()
    df_test_cb = test[feat_cols].copy()
    # Kategorik dtype'leri str'e cevir; nan'i 'MISSING' yap
    for c in cat_features:
        df_train_cb[c] = df_train_cb[c].fillna("MISSING").astype(str)
        df_val_cb[c] = df_val_cb[c].fillna("MISSING").astype(str)
        df_test_cb[c] = df_test_cb[c].fillna("MISSING").astype(str)
    # Boolean -> int
    for c in BOOLEAN_FEATURES:
        if c in df_train_cb.columns:
            df_train_cb[c] = df_train_cb[c].astype(int)
            df_val_cb[c] = df_val_cb[c].astype(int)
            df_test_cb[c] = df_test_cb[c].astype(int)
    # Numerik NaN -> median (per col)
    for c in df_train_cb.columns:
        if c in cat_features:
            continue
        if df_train_cb[c].dtype.kind in "fi":
            med = df_train_cb[c].median()
            df_train_cb[c] = df_train_cb[c].fillna(med)
            df_val_cb[c] = df_val_cb[c].fillna(med)
            df_test_cb[c] = df_test_cb[c].fillna(med)

    cb = CatBoostRegressor(**CATBOOST_PARAMS)
    cb.fit(
        df_train_cb,
        y_train,
        cat_features=cat_features,
        eval_set=(df_val_cb, y_val),
        verbose=False,
    )
    elapsed = time.time() - t0
    m = evaluate_regression(y_test, cb.predict(df_test_cb))
    m["train_sec"] = elapsed
    metrics["catboost"] = m
    models["catboost"] = cb

    # Best by RMSE
    best_kind = min(metrics, key=lambda k: metrics[k]["rmse"])

    return metrics, best_kind, models
