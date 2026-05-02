"""Augmentation pipeline'inin sayisal/dagilimsal sinirlarini dogrular."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ml.src.augmentation import build_training_set


# Tek kez build et, hizli (~5s); session-scope cache ile testler ayni df'i kullanir.
@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return build_training_set(target_rows=1500, seed=42)


# ---------------------------------------------------------------------------
# Boyut & dagilimlar
# ---------------------------------------------------------------------------
def test_row_count(df: pd.DataFrame) -> None:
    """Validate sonrasi satir sayisi 1400-1500 arasi olmali."""
    assert 1400 <= df.shape[0] <= 1500


def test_material_distribution(df: pd.DataFrame) -> None:
    """0.70/0.20/0.10 dagilimina ±5% tolerans."""
    counts = df["raw_material"].value_counts(normalize=True)
    assert 0.65 <= counts["pomza"] <= 0.75
    assert 0.15 <= counts["perlit"] <= 0.25
    assert 0.05 <= counts["kabak_cekirdegi"] <= 0.15


def test_quality_grade_distribution(df: pd.DataFrame) -> None:
    """AUG-06: A=0.30, B=0.50, C=0.20 (±5% tolerans)."""
    counts = df["quality_grade"].value_counts(normalize=True)
    assert 0.25 <= counts["A"] <= 0.35
    assert 0.45 <= counts["B"] <= 0.55
    assert 0.15 <= counts["C"] <= 0.25


def test_route_count(df: pd.DataFrame) -> None:
    """Tum 15 rota processing_route_candidate kolonunda gorunmeli."""
    assert df["processing_route_candidate"].nunique() == 15


def test_fx_scenario_discrete(df: pd.DataFrame) -> None:
    """AUG-03: fx_scenario_pct sadece {-0.10, -0.05, 0, 0.05, 0.10} icinden."""
    allowed = {-0.10, -0.05, 0.0, 0.05, 0.10}
    actual = set(df["fx_scenario_pct"].unique())
    assert actual.issubset(allowed)


# ---------------------------------------------------------------------------
# Formul tutarliligi
# ---------------------------------------------------------------------------
def test_co2_positive(df: pd.DataFrame) -> None:
    assert (df["co2_kg"] > 0).all()


def test_co2_formula(df: pd.DataFrame) -> None:
    """co2_kg = tonnage * total_distance_km * emission_factor (±%15 measurement noise)."""
    expected = (
        df["tonnage"] * df["total_distance_km"] * df["emission_factor_kg_co2_ton_km"]
    )
    rel_err = np.abs(df["co2_kg"] - expected) / df["co2_kg"]
    # AUG-07 noise ±%3 sigma → ~%99 satir <%10 sapar; nadiren 4-sigma %12-15'e cikar
    assert (rel_err < 0.15).all(), (
        f"co2_kg formul saptisi: max rel_err = {rel_err.max():.4f}"
    )
    # Beklenen: ortalama sapma <%5 (sigma~3 normal)
    assert rel_err.mean() < 0.05, f"co2 ortalama sapma yuksek: {rel_err.mean():.4f}"


def test_expected_profit_finite(df: pd.DataFrame) -> None:
    """expected_profit_try inf veya NaN icermez."""
    assert np.isfinite(df["expected_profit_try"]).all()


# ---------------------------------------------------------------------------
# Karbon faktoru lookup
# ---------------------------------------------------------------------------
def test_emission_factor_kara(df: pd.DataFrame) -> None:
    """transport_mode='kara' satirlarinda emission_factor ~ 0.100 (sabit lookup)."""
    sub = df[df["transport_mode"] == "kara"]
    assert len(sub) > 0
    # Lookup deterministik; 0.100 tam degeri
    assert (np.abs(sub["emission_factor_kg_co2_ton_km"] - 0.100) < 0.001).all()


def test_emission_factor_deniz(df: pd.DataFrame) -> None:
    """deniz -> 0.015 sabit lookup."""
    sub = df[df["transport_mode"] == "deniz"]
    if len(sub) == 0:
        pytest.skip("Bu seed'de deniz mode satiri yok.")
    assert (np.abs(sub["emission_factor_kg_co2_ton_km"] - 0.015) < 0.001).all()


# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
def test_seed_reproducibility() -> None:
    """seed=42 ile iki kez cagri, ilk 100 satir tum kolonlarda ozdes."""
    df1 = build_training_set(target_rows=500, seed=42)
    df2 = build_training_set(target_rows=500, seed=42)
    pd.testing.assert_frame_equal(df1.head(100), df2.head(100))
