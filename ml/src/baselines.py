"""Baseline modelleri (rapor §6.2 / §7.2 — Adim 5).

3 profit baseline + 3 route baseline:

profit:
  - rule_based_predict()   formul tabanli, ogrenmiyor
  - LinearRegression       sklearn standart
  - RandomForestRegressor  n=200, depth=10

route:
  - majority_baseline()    en sik rota
  - LogisticRegression     multi-class softmax
  - RandomForestClassifier n=200, depth=10

stratified_split() rapor §5.7 ile uyumlu 80/10/10 split saglar.
evaluate_regression / evaluate_classification metrik tablolari uretir.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split


SEED = 42


# ---------------------------------------------------------------------------
# Rule-based regressor (formul; ogrenmiyor)
# ---------------------------------------------------------------------------
def rule_based_predict(df_raw: pd.DataFrame) -> np.ndarray:
    """Profit'i salt formulle tahmin eder.

    profit_per_ton_usd = processed_price - processing_cost - packaging - transport_total - raw_buy
    profit_total_try   = profit_per_ton_usd * tonnage * usd_try * (1+fx_scenario_pct)

    Args:
        df_raw: Augmentation pipeline ciktisi (M1_FEATURES sutunlari mevcut).

    Returns:
        ``shape=(n,)`` float numpy dizisi (TRY).
    """
    fx = df_raw["usd_try"].values * (1.0 + df_raw["fx_scenario_pct"].fillna(0).values)
    tonnage = df_raw["tonnage"].values
    revenue = df_raw["processed_price_typical_usd_ton"].values * fx * tonnage
    proc = df_raw["processing_cost_typical_usd_ton"].values * fx * tonnage
    pack = df_raw["packaging_cost_usd_ton"].values * fx * tonnage
    transport = (
        df_raw["transport_cost_usd_ton_km"].values
        * df_raw["total_distance_km"].values
        * tonnage
        * fx
    )
    raw_buy = df_raw["raw_price_typical_usd_ton"].values * fx * tonnage
    return revenue - proc - pack - transport - raw_buy


# ---------------------------------------------------------------------------
# Sklearn wrapper'lari (default hyperparam)
# ---------------------------------------------------------------------------
def make_linear_regressor() -> LinearRegression:
    return LinearRegression()


def make_logistic_classifier() -> LogisticRegression:
    return LogisticRegression(
        multi_class="multinomial",
        max_iter=1000,
        random_state=SEED,
        n_jobs=-1,
        solver="lbfgs",
    )


def make_rf_regressor() -> RandomForestRegressor:
    return RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=SEED,
        n_jobs=-1,
    )


def make_rf_classifier() -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=SEED,
        n_jobs=-1,
        class_weight="balanced",
    )


# ---------------------------------------------------------------------------
# Stratified 80/10/10 split (rapor §5.7)
# ---------------------------------------------------------------------------
def stratified_split(
    df: pd.DataFrame,
    target_col: str,
    stratify_cols: list[str] | str,
    test_size: float = 0.20,
    val_size: float = 0.50,
    seed: int = SEED,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """80/10/10 stratified split.

    Args:
        df: training_set_v1 DataFrame.
        target_col: Egitim hedefi (ornegin ``"expected_profit_try"``).
        stratify_cols: Strata icin tek kolon adi veya kolon listesi
            (liste ise concat edilir, rapor ornegi: ``["raw_material","processing_route_candidate"]``).
        test_size: Holdout (val + test) orani — default 0.20.
        val_size: Holdout icindeki val orani (val_size * test_size = 0.10).
        seed: random_state.

    Returns:
        ``(train, val, test)`` DataFrame uclusu.
    """
    if isinstance(stratify_cols, str):
        strata = df[stratify_cols].astype(str)
    else:
        strata = df[stratify_cols].astype(str).agg("_".join, axis=1)

    # Tek-orneklik strata'lari fallback'le birlestir (train_test_split'in
    # stratify=... 2 alt minimum gerektirir)
    counts = strata.value_counts()
    rare = counts[counts < 2].index.tolist()
    if rare:
        strata = strata.where(~strata.isin(rare), "_RARE_")

    train, holdout = train_test_split(
        df, test_size=test_size, stratify=strata, random_state=seed
    )
    h_strata = strata.loc[holdout.index]
    h_counts = h_strata.value_counts()
    h_rare = h_counts[h_counts < 2].index.tolist()
    if h_rare:
        h_strata = h_strata.where(~h_strata.isin(h_rare), "_RARE_")
    val, test = train_test_split(
        holdout, test_size=val_size, stratify=h_strata, random_state=seed
    )
    return train.reset_index(drop=True), val.reset_index(drop=True), test.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Metrik fonksiyonlari
# ---------------------------------------------------------------------------
def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """RMSE, MAE, R2, MAPE."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mse = mean_squared_error(y_true, y_pred)
    rmse = float(np.sqrt(mse))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    # MAPE: y_true=0 olursa sonsuz; sklearn buna toleranslidir (epsilon)
    try:
        mape = float(mean_absolute_percentage_error(y_true, y_pred))
    except Exception:
        mape = float("nan")
    return {"rmse": rmse, "mae": mae, "r2": r2, "mape": mape}


def evaluate_classification(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
    classes: list[str] | None = None,
) -> dict[str, float]:
    """Accuracy, macro_f1, weighted_f1; y_proba verilirse top2_accuracy."""
    out: dict[str, float] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
    }
    if y_proba is not None and classes is not None:
        # Top-2 accuracy: y_true class probability sirasi >= ikinci
        proba = np.asarray(y_proba)
        cls_arr = np.asarray(classes)
        # Her satir icin top-2 sinif indeksleri
        top2_idx = np.argsort(-proba, axis=1)[:, :2]
        top2_classes = cls_arr[top2_idx]
        y_true_arr = np.asarray(y_true).reshape(-1, 1)
        hits = (top2_classes == y_true_arr).any(axis=1)
        out["top2_accuracy"] = float(hits.mean())
    return out


def majority_baseline_predict(y_train: np.ndarray, n_test: int) -> np.ndarray:
    """En sik sinifi her zaman tahmin eder."""
    vals, counts = np.unique(y_train, return_counts=True)
    majority = vals[np.argmax(counts)]
    return np.full(n_test, majority)
