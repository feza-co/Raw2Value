"""Sklearn ColumnTransformer (preprocessing) — rapor §5.2.4 + Adim 4.

Modelin alacagi feature'lari (sayisal + kategorik + boolean) tek bir
ColumnTransformer ile asagidaki sirada hazirlar:

  - sayisal: SimpleImputer(median) + (opsiyonel scale, GBDT icin gerek yok)
  - dusuk-cardinality kategorik (≤10): SimpleImputer("MISSING") + OneHotEncoder
  - yuksek-cardinality kategorik: SimpleImputer + OneHotEncoder(max_categories=20)
  - CatBoost icin: passthrough (model native handling yapacak)

handle_unknown='ignore' sayesinde inference'ta gorulmemis kategori 0-vector
olur (hata firlatmaz).
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .features import BOOLEAN_FEATURES, M1_FEATURES, NUMERIC_FEATURES


# ---------------------------------------------------------------------------
# Helper transformer — bool -> int8 (SimpleImputer bool dtype'i kabul etmiyor)
# ---------------------------------------------------------------------------
class _BoolToInt(BaseEstimator, TransformerMixin):
    """Bool dtype'i int8'e cevirir, SimpleImputer downstream'i bozulmasin."""

    def fit(self, X, y=None):  # noqa: D401, N802
        return self

    def transform(self, X):  # noqa: N802
        if isinstance(X, pd.DataFrame):
            return X.astype("int8").values
        return np.asarray(X, dtype="int8")

    def get_feature_names_out(self, input_features=None):  # noqa: N802
        return np.asarray(input_features) if input_features is not None else np.array([])


# ---------------------------------------------------------------------------
# Feature gruplari (rapor §5.2.4)
# ---------------------------------------------------------------------------
# Dusuk cardinality (<=10 distinct value)
LOW_CARDINALITY: list[str] = [
    "raw_material",  # 3
    "quality_grade",  # 3 (A/B/C)
    "transport_mode",  # 4
    "priority",  # 3
    "buyer_country",  # 3
    "input_mode",  # 2
    "product_form",  # ~5
    "particle_size_class",  # 3
]

# Orta/yuksek cardinality (max_categories=20 ile sinirli)
HIGH_CARDINALITY: list[str] = [
    "origin_district",
    "buyer_sector",
    "buyer_city",
    "processor_type",
    "raw_subtype",
    "processing_route_candidate",
]


# ---------------------------------------------------------------------------
# Pipeline kurucusu
# ---------------------------------------------------------------------------
def _filter_existing(cols: list[str], df_cols: list[str]) -> list[str]:
    """df'te bulunan kolonlari dondur; eksik olanlari sessizce at."""
    return [c for c in cols if c in df_cols]


def build_feature_pipeline(
    model_kind: str = "xgboost",
    *,
    df_columns: list[str] | None = None,
) -> ColumnTransformer:
    """ColumnTransformer kurar.

    Args:
        model_kind: ``"xgboost" | "lightgbm"``: one-hot encoding.
                    ``"catboost"``: passthrough (CatBoost native categorical).
        df_columns: Eger verilirse, sadece bu liste icindeki kolonlar pipeline'a
                    eklenir (eksik kolonlar sessizce atilir, partial fit icin).

    Returns:
        Henuz fit edilmemis ColumnTransformer.
    """
    if df_columns is None:
        # Tum M1 setini bekle
        df_columns = M1_FEATURES + BOOLEAN_FEATURES

    num_cols = _filter_existing(NUMERIC_FEATURES, df_columns)
    bool_cols = _filter_existing(BOOLEAN_FEATURES, df_columns)
    low_cat = _filter_existing(LOW_CARDINALITY, df_columns)
    high_cat = _filter_existing(HIGH_CARDINALITY, df_columns)

    numerical_pipe = Pipeline(
        [("impute", SimpleImputer(strategy="median"))]
    )

    boolean_pipe = Pipeline(
        [
            ("to_int", _BoolToInt()),
            ("impute", SimpleImputer(strategy="most_frequent")),
        ]
    )

    if model_kind in ("xgboost", "lightgbm"):
        cat_low_pipe = Pipeline(
            [
                ("impute", SimpleImputer(strategy="constant", fill_value="MISSING")),
                (
                    "onehot",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ),
            ]
        )
        cat_high_pipe = Pipeline(
            [
                ("impute", SimpleImputer(strategy="constant", fill_value="MISSING")),
                (
                    "onehot",
                    OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False,
                        max_categories=20,
                    ),
                ),
            ]
        )
        transformers = [
            ("num", numerical_pipe, num_cols),
            ("bool", boolean_pipe, bool_cols),
            ("cat_low", cat_low_pipe, low_cat),
            ("cat_high", cat_high_pipe, high_cat),
        ]
    elif model_kind == "catboost":
        # CatBoost native categorical handling — passthrough
        cat_passthrough = Pipeline(
            [("impute", SimpleImputer(strategy="constant", fill_value="MISSING"))]
        )
        transformers = [
            ("num", numerical_pipe, num_cols),
            ("bool", boolean_pipe, bool_cols),
            ("cat", cat_passthrough, low_cat + high_cat),
        ]
    else:
        raise ValueError(f"Unknown model_kind: {model_kind!r}")

    # Bos transformer'lari at
    transformers = [(n, t, cols) for n, t, cols in transformers if cols]

    return ColumnTransformer(transformers, remainder="drop", sparse_threshold=0.0)


def fit_and_save(
    df: pd.DataFrame,
    kind: str = "xgboost",
    out_path: str | Path = "models/feature_pipeline.pkl",
) -> ColumnTransformer:
    """Pipeline'i df uzerinde fit eder ve joblib ile diske yazar.

    Args:
        df: Egitim seti — M1_FEATURES (+ BOOLEAN_FEATURES) kolonlarinin
            altkumesini icermeli. Eksik kolon var ise sessizce atlanir.
        kind: ``"xgboost" | "lightgbm" | "catboost"``.
        out_path: ``models/feature_pipeline.pkl`` (relative, repo root'a gore).

    Returns:
        Fit edilmis ColumnTransformer.
    """
    # Tekil kolonlar: M1_FEATURES + boolean'larin M1'e eklenmemis olanlari
    seen: set[str] = set()
    feature_cols: list[str] = []
    for c in M1_FEATURES + BOOLEAN_FEATURES:
        if c in seen or c not in df.columns:
            continue
        seen.add(c)
        feature_cols.append(c)

    pipe = build_feature_pipeline(kind, df_columns=feature_cols)
    pipe.fit(df[feature_cols])

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, out_path)
    return pipe
