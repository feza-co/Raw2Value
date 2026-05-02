"""FX what-if senaryo aplayıcısı.

Kullanıcı `fx_scenario_pct=-0.10..+0.10` aralığında değer verir; canlı kur
(TCMB tarafından backend cache'i tarafından sağlanır) bu değerle çarpılarak
modele girer.
"""
from __future__ import annotations


def apply_fx_scenario(live_fx: dict, scenario_pct: float) -> dict:
    """Canlı kura ±%X uygulayıp yeni dict döner.

    Args:
        live_fx: ``{"usd_try": float, "eur_try": float, ...}``.
        scenario_pct: -0.10 .. +0.10 arası decimal (örn. ``0.05`` = +%5).

    Returns:
        ``{"usd_try", "eur_try", "fx_scenario_pct", "fx_source"}`` sözlüğü.
    """
    multiplier = 1.0 + float(scenario_pct)
    return {
        "usd_try": float(live_fx["usd_try"]) * multiplier,
        "eur_try": float(live_fx["eur_try"]) * multiplier,
        "fx_scenario_pct": float(scenario_pct),
        "fx_source": "TCMB_LIVE",
    }
