"""Hedef degisken hesaplamalari (rapor §5.3).

Dort target uretilir:
- ``expected_profit_try`` (sürekli, TRY) — Model 1 (profit regression) etiketi
- ``value_uplift_pct`` (yüzde) — bilgi amacli ek metrik
- ``route_score`` (0-1) — argmax ile ``recommended_route_label`` üretmek icin
- ``recommended_route_label`` (kategori) — Model 2 (route classifier) etiketi

Tum hesaplamalar pure-numpy / pandas; ``rng`` parametre olarak gelir
(reproducibility icin ZORUNLU). Hicbir target M1/M2 input'una sizmaz —
bu sart ``test_no_target_leakage.py`` ile dogrulanir.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from .features import ROUTES_BY_MATERIAL, make_route_label


# ---------------------------------------------------------------------------
# Yardimcilar
# ---------------------------------------------------------------------------
def _fx_rate(row: pd.Series | dict) -> float:
    """Senaryolu efektif USD/TRY kuru."""
    base = float(row["usd_try"])
    pct = float(row.get("fx_scenario_pct", 0.0) or 0.0)
    return base * (1.0 + pct)


# ---------------------------------------------------------------------------
# 5.3.1 — expected_profit_try
# ---------------------------------------------------------------------------
def compute_expected_profit_try(
    row: pd.Series | dict, rng: np.random.Generator | None = None
) -> float:
    """Tek satirlik beklenen kâr (TRY).

    Formul (rapor §5.3.1):
        gelir       = processed_price * fx * tonnage
        - islem     = processing_cost * fx * tonnage
        - paketleme = packaging_cost * fx * tonnage
        - nakliye   = transport_cost_usd_ton_km * total_distance_km * tonnage * fx
        - alis      = raw_price * fx * tonnage
        ---------------------------------------------------------------------
        sonuc        × (1 + N(0, 0.05))   # operasyonel belirsizlik proxy

    Args:
        row: Augmentation pipeline'in ürettigi bir satir (Series veya dict).
        rng: ``np.random.default_rng(seed)`` — None ise gürültü 0 (deterministik).
    """
    fx = _fx_rate(row)
    tonnage = float(row["tonnage"])
    revenue = float(row["processed_price_typical_usd_ton"]) * fx * tonnage
    proc = float(row["processing_cost_typical_usd_ton"]) * fx * tonnage
    pack = float(row["packaging_cost_usd_ton"]) * fx * tonnage
    transport = (
        float(row["transport_cost_usd_ton_km"])
        * float(row["total_distance_km"])
        * tonnage
        * fx
    )
    raw_buy = float(row["raw_price_typical_usd_ton"]) * fx * tonnage

    profit = revenue - proc - pack - transport - raw_buy

    if rng is not None:
        profit *= 1.0 + rng.normal(0.0, 0.05)

    return float(profit)


# ---------------------------------------------------------------------------
# 5.3.2 — value_uplift_pct
# ---------------------------------------------------------------------------
def compute_value_uplift_pct(row: pd.Series | dict) -> float:
    """Ham satisa kiyasla yüzdesel kâr farki.

    raw_sale_profit_try = raw_price * fx * tonnage - direct_transport_cost
    (Direct transport: raw_material'i isleme yapmadan dogrudan alici iline tasimak.)
    """
    fx = _fx_rate(row)
    tonnage = float(row["tonnage"])
    raw_price = float(row["raw_price_typical_usd_ton"])

    # Alternatif "ham sat" senaryosunda nakliye toplam mesafenin tamami
    direct_transport = (
        float(row["transport_cost_usd_ton_km"])
        * float(row["total_distance_km"])
        * tonnage
        * fx
    )
    raw_sale_profit = raw_price * fx * tonnage - direct_transport

    if abs(raw_sale_profit) < 1.0:
        # Sifira yakin: bolme guvensiz; kuçuk bir taban kullan
        raw_sale_profit = 1.0 if raw_sale_profit >= 0 else -1.0

    expected_profit = float(row["expected_profit_try"])
    return float((expected_profit - raw_sale_profit) / abs(raw_sale_profit))


# ---------------------------------------------------------------------------
# 5.3.3 — route_score (sentetik etiket)
# ---------------------------------------------------------------------------
def _normalize(x: float, lo: float, hi: float) -> float:
    """Min-max [0, 1] kirpmali normalize. lo>=hi ise 0.5."""
    if hi <= lo:
        return 0.5
    return float(max(0.0, min(1.0, (x - lo) / (hi - lo))))


def compute_route_score(
    row: pd.Series | dict,
    *,
    profit_lo: float = -1e7,
    profit_hi: float = 5e7,
    co2_max: float = 1.0e6,
) -> float:
    """5 bilesenli weighted skor (rapor §5.3.3).

        0.45 * normalized_profit
      + 0.20 * demand_score
      + 0.15 * (1 - co2_kg / co2_max)
      + 0.10 * (1 - delivery_risk)
      + 0.10 * (data_confidence_score / 100)
    """
    profit_norm = _normalize(float(row["expected_profit_try"]), profit_lo, profit_hi)
    demand = float(row.get("demand_score", 0.5) or 0.5)
    carbon_score = max(0.0, 1.0 - float(row["co2_kg"]) / co2_max)
    delivery_score = max(0.0, 1.0 - float(row.get("delivery_risk", 0.5) or 0.5))
    confidence_score = float(row.get("data_confidence_score", 75.0) or 75.0) / 100.0

    return float(
        0.45 * profit_norm
        + 0.20 * demand
        + 0.15 * carbon_score
        + 0.10 * delivery_score
        + 0.10 * confidence_score
    )


# ---------------------------------------------------------------------------
# 5.3.3 — recommended_route_label (argmax across candidate routes)
# ---------------------------------------------------------------------------
def compute_recommended_route_label(
    row: pd.Series | dict,
    candidate_routes: Iterable[str],
    routes_df: pd.DataFrame,
    rng: np.random.Generator | None = None,
) -> str:
    """Argmax route_score across candidate routes.

    Her aday rota icin row'u kopyalayip rota-bagimli alanlari (processed_price,
    processing_cost) lookup'tan yamar, expected_profit ve co2 kismen yeniden
    hesaplanir, sonra route_score bulunur. Argmax dondurulur.

    Args:
        row: orijinal satir (rota baslangici processing_route_candidate).
        candidate_routes: bu hammadde icin gecerli rota adlari listesi.
        routes_df: ``data/reference/routes.parquet`` (Hammadde × Rota anahtarli).
        rng: profit gurultusu icin (None ise deterministik).
    """
    material = row["raw_material"]
    best_score = -1e18
    best_route = None

    for route in candidate_routes:
        match = routes_df[
            (routes_df["Hammadde"] == material) & (routes_df["Rota"] == route)
        ]
        if match.empty:
            continue
        proc_cost = float(match["Maliyet USD/ton (typical)"].iloc[0])
        sale_price = float(match["Satis_USD_ton_typical"].iloc[0])

        scenario = dict(row)
        scenario["processing_cost_typical_usd_ton"] = proc_cost
        scenario["processed_price_typical_usd_ton"] = sale_price
        scenario["expected_profit_try"] = compute_expected_profit_try(scenario, rng=rng)
        # co2 ayni kalir (rota-bagimli degil, transport-bagimli)
        score = compute_route_score(scenario)

        if score > best_score:
            best_score = score
            best_route = route

    if best_route is None:
        # Fallback: ilk aday rota (kararli)
        best_route = next(iter(candidate_routes))
    return make_route_label(material, str(best_route))


# ---------------------------------------------------------------------------
# Toplu uretim — compute_targets
# ---------------------------------------------------------------------------
def compute_targets(
    df: pd.DataFrame, rng: np.random.Generator, routes_df: pd.DataFrame | None = None
) -> pd.DataFrame:
    """4 target kolonunu DataFrame'e ekler.

    Sira ile:
      1) ``expected_profit_try``  — gauss noise ile
      2) ``value_uplift_pct``     — deterministik (profit'e bagli)
      3) ``route_score``          — info amacli
      4) ``recommended_route_label`` — argmax across candidate routes

    Args:
        df: Augmentation sonrasi feature df (target sutunlari haric tum input
            sutunlari mevcut olmali).
        rng: ``np.random.default_rng(seed)`` — profit ve label uretimi icin.
        routes_df: routes parquet (None ise reference_loader'dan yuklenir).

    Returns:
        Yeni 4 kolonu olan kopya.
    """
    if routes_df is None:
        from raw2value_ml.reference_loader import load_routes

        routes_df = load_routes()

    out = df.copy()

    # 1) expected_profit_try
    profits = np.empty(len(out), dtype=float)
    for i, (_, row) in enumerate(out.iterrows()):
        profits[i] = compute_expected_profit_try(row, rng=rng)
    out["expected_profit_try"] = profits

    # 2) value_uplift_pct
    uplifts = np.empty(len(out), dtype=float)
    for i, (_, row) in enumerate(out.iterrows()):
        uplifts[i] = compute_value_uplift_pct(row)
    out["value_uplift_pct"] = uplifts

    # 3) route_score (info)
    scores = np.empty(len(out), dtype=float)
    for i, (_, row) in enumerate(out.iterrows()):
        scores[i] = compute_route_score(row)
    out["route_score"] = scores

    # 4) recommended_route_label — argmax across candidate routes
    labels: list[str] = []
    for _, row in out.iterrows():
        candidates = ROUTES_BY_MATERIAL.get(row["raw_material"], [])
        labels.append(
            compute_recommended_route_label(row, candidates, routes_df, rng=rng)
        )
    out["recommended_route_label"] = labels

    return out
