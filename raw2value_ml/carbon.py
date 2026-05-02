"""CO2 hesaplaması — sabit hackathon faktörleri kullanır.

Faktörler `data/reference/carbon.parquet` üzerinden gelir; mod anahtarları
`reference_loader._CARBON_MODE_MAP` ile API anahtarlarına çevrilir.
"""
from __future__ import annotations

from .reference_loader import load_carbon_factors


def compute_co2(tonnage: float, distance_km: float, transport_mode: str) -> float:
    """tonnage × distance × emission_factor (kg CO2)."""
    factors = load_carbon_factors()
    if transport_mode not in factors:
        raise ValueError(
            f"Bilinmeyen transport_mode: {transport_mode!r}. "
            f"Geçerli: {sorted(factors)}"
        )
    return float(tonnage) * float(distance_km) * float(factors[transport_mode])


def get_emission_factor(transport_mode: str) -> float:
    """Belirli mod için kg CO2/ton-km faktörü; bilinmeyen mod -> 0.100 (kara default)."""
    factors = load_carbon_factors()
    return float(factors.get(transport_mode, 0.100))
