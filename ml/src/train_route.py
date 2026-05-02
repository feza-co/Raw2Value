"""GBDT route classifier — XGBoost / LightGBM / CatBoost benchmark (Adim 6).

15 sinifli (multi-class) classifier. macro_f1'e gore en iyi model secilir.
Class imbalance icin XGB/LGB'de sample_weight=balanced, CatBoost'ta
auto_class_weights='Balanced'.
"""
from __future__ import annotations

import time
import warnings
from typing import Any

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier, early_stopping, log_evaluation
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

from .baselines import evaluate_classification, stratified_split
from .feature_pipeline import build_feature_pipeline
from .features import BOOLEAN_FEATURES, M1_FEATURES


# ---------------------------------------------------------------------------
# Hiperparametre setleri
# ---------------------------------------------------------------------------
XGBOOST_PARAMS: dict[str, Any] = {
    "objective": "multi:softprob",
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
    "eval_metric": "mlogloss",
    "verbosity": 0,
}

LIGHTGBM_PARAMS: dict[str, Any] = {
    "objective": "multiclass",
    "n_estimators": 500,
    "num_leaves": 31,
    "learning_rate": 0.05,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "min_child_samples": 10,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "random_state": 42,
    "metric": "multi_logloss",
    "verbosity": -1,
}

CATBOOST_PARAMS: dict[str, Any] = {
    "iterations": 500,
    "depth": 6,
    "learning_rate": 0.05,
    "l2_leaf_reg": 3.0,
    "loss_function": "MultiClass",
    "random_seed": 42,
    "early_stopping_rounds": 30,
    "verbose": 0,
    "auto_class_weights": "Balanced",
}


def _unique_feature_cols(df: pd.DataFrame) -> list[str]:
    seen: set[str] = set()
    cols: list[str] = []
    # Model 2: processing_route_candidate target oldugu icin cikar
    candidates = [c for c in M1_FEATURES if c != "processing_route_candidate"] + ["priority"]
    candidates += BOOLEAN_FEATURES
    for c in candidates:
        if c in seen or c not in df.columns:
            continue
        seen.add(c)
        cols.append(c)
    return cols


def train_route_models(
    df: pd.DataFrame,
    pipeline_xgb_lgb=None,
    seed: int = 42,
) -> tuple[dict[str, dict[str, float]], str, dict[str, Any], list[str]]:
    """3 GBDT classifier'i ayni split uzerinde fit eder.

    Returns:
        ``(metrics, best_kind, models, classes)``
    """
    feat_cols = _unique_feature_cols(df)
    classes = sorted(df["recommended_route_label"].unique().tolist())

    train, val, test = stratified_split(
        df,
        target_col="recommended_route_label",
        stratify_cols=["raw_material"],
        seed=seed,
    )
    y_train_raw = train["recommended_route_label"].values
    y_val_raw = val["recommended_route_label"].values
    y_test_raw = test["recommended_route_label"].values

    # Label encode (XGB/LGB int label ister)
    le = LabelEncoder()
    le.fit(classes)
    y_train = le.transform(y_train_raw)
    y_val = le.transform(y_val_raw)
    y_test = le.transform(y_test_raw)

    if pipeline_xgb_lgb is None:
        pipeline_xgb_lgb = build_feature_pipeline("xgboost", df_columns=feat_cols)
        pipeline_xgb_lgb.fit(df[feat_cols])

    X_train = pipeline_xgb_lgb.transform(train[feat_cols])
    X_val = pipeline_xgb_lgb.transform(val[feat_cols])
    X_test = pipeline_xgb_lgb.transform(test[feat_cols])

    sample_weight = compute_sample_weight("balanced", y_train)

    metrics: dict[str, dict[str, float]] = {}
    models: dict[str, Any] = {}

    # 1) XGBoost — int label, num_class otomatik
    t0 = time.time()
    xgb = XGBClassifier(num_class=len(classes), **XGBOOST_PARAMS)
    xgb.fit(
        X_train,
        y_train,
        sample_weight=sample_weight,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    y_pred = le.inverse_transform(xgb.predict(X_test))
    y_proba = xgb.predict_proba(X_test)
    proba_classes = list(le.inverse_transform(xgb.classes_))
    m = evaluate_classification(y_test_raw, y_pred, y_proba, proba_classes)
    m["train_sec"] = time.time() - t0
    metrics["xgboost"] = m
    models["xgboost"] = xgb

    # 2) LightGBM
    t0 = time.time()
    lgb = LGBMClassifier(num_class=len(classes), **LIGHTGBM_PARAMS)
    lgb.fit(
        X_train,
        y_train,
        sample_weight=sample_weight,
        eval_set=[(X_val, y_val)],
        callbacks=[early_stopping(stopping_rounds=30, verbose=False), log_evaluation(0)],
    )
    y_pred = le.inverse_transform(lgb.predict(X_test))
    y_proba = lgb.predict_proba(X_test)
    proba_classes = list(le.inverse_transform(lgb.classes_))
    m = evaluate_classification(y_test_raw, y_pred, y_proba, proba_classes)
    m["train_sec"] = time.time() - t0
    metrics["lightgbm"] = m
    models["lightgbm"] = lgb

    # 3) CatBoost
    t0 = time.time()
    from .feature_pipeline import HIGH_CARDINALITY, LOW_CARDINALITY

    cat_features = [
        c for c in (LOW_CARDINALITY + HIGH_CARDINALITY) if c in feat_cols
    ]
    df_train_cb = train[feat_cols].copy()
    df_val_cb = val[feat_cols].copy()
    df_test_cb = test[feat_cols].copy()
    for c in cat_features:
        df_train_cb[c] = df_train_cb[c].fillna("MISSING").astype(str)
        df_val_cb[c] = df_val_cb[c].fillna("MISSING").astype(str)
        df_test_cb[c] = df_test_cb[c].fillna("MISSING").astype(str)
    for c in BOOLEAN_FEATURES:
        if c in df_train_cb.columns:
            df_train_cb[c] = df_train_cb[c].astype(int)
            df_val_cb[c] = df_val_cb[c].astype(int)
            df_test_cb[c] = df_test_cb[c].astype(int)
    for c in df_train_cb.columns:
        if c in cat_features:
            continue
        if df_train_cb[c].dtype.kind in "fi":
            med = df_train_cb[c].median()
            df_train_cb[c] = df_train_cb[c].fillna(med)
            df_val_cb[c] = df_val_cb[c].fillna(med)
            df_test_cb[c] = df_test_cb[c].fillna(med)

    cb = CatBoostClassifier(**CATBOOST_PARAMS)
    cb.fit(
        df_train_cb,
        y_train_raw,
        cat_features=cat_features,
        eval_set=(df_val_cb, y_val_raw),
        verbose=False,
    )
    y_pred = cb.predict(df_test_cb).flatten()
    y_proba = cb.predict_proba(df_test_cb)
    proba_classes = list(cb.classes_)
    m = evaluate_classification(y_test_raw, y_pred, y_proba, proba_classes)
    m["train_sec"] = time.time() - t0
    metrics["catboost"] = m
    models["catboost"] = cb

    best_kind = max(metrics, key=lambda k: metrics[k]["macro_f1"])
    return metrics, best_kind, models, classes
