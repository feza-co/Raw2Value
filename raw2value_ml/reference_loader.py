"""Referans parquet'leri Python objelere dönüştüren önbellekli loader fonksiyonları.

Backend ve ML pipeline tarafından ortak kullanılır. Tüm fonksiyonlar
``functools.lru_cache`` ile sarmalanmıştır; yani süreç ömrü boyunca her parquet
yalnızca bir kez okunur.

Tüm parquet'ler ``REFERENCE_DIR`` (varsayılan: ``<repo>/data/reference``) altında
``ml/src/etl.py`` tarafından üretilmiş olmalıdır.
"""
from __future__ import annotations

import functools
import pickle
from pathlib import Path

import pandas as pd

# Modül seviyesi sabit — repo köküne göre data/reference
REFERENCE_DIR: Path = Path(__file__).parent.parent / "data" / "reference"


# ---------------------------------------------------------------------------
# Carbon mode mapping (Excel anahtarı -> API/Türkçe anahtar)
# ---------------------------------------------------------------------------
_CARBON_MODE_MAP: dict[str, str] = {
    "road_truck_HGV": "kara",
    "sea_container": "deniz",
    "air_freight_long_haul": "hava",
    "rail_freight": "demiryolu",
}

# Delivery risk: API mode -> Excel anahtarı (12_risk_quality, RISK/Delivery bloku)
_DELIVERY_RISK_MAP: dict[str, str] = {
    "kara": "road_truck_domestic",
    "deniz": "sea_freight_med_north",
    "demiryolu": "rail_eu_block_train",
    "hava": "air_cargo",
}

# Price volatility: API material -> Excel anahtarı (12_risk_quality, RISK/Price bloku)
_PRICE_VOL_MAP: dict[str, str] = {
    "pomza": "pomza",
    "perlit": "perlit",
    "kabak_cekirdegi": "kabak_cekirdegi_ham",
}


# ---------------------------------------------------------------------------
# Loader fonksiyonları
# ---------------------------------------------------------------------------
@functools.lru_cache(maxsize=None)
def load_routes() -> pd.DataFrame:
    """15 işleme rotasını döndürür (3 hammadde × 5 rota)."""
    return pd.read_parquet(REFERENCE_DIR / "routes.parquet")


@functools.lru_cache(maxsize=None)
def load_materials() -> pd.DataFrame:
    """02_material_reference içeriği (~30 satır, hammadde özellikleri)."""
    return pd.read_parquet(REFERENCE_DIR / "materials.parquet")


@functools.lru_cache(maxsize=None)
def load_organizations(
    filter_type: str | None = None,
    material: str | None = None,
    city: str | None = None,
) -> pd.DataFrame:
    """Üretici/alıcı/ekipman organizasyonlarını döndürür; opsiyonel filtreler.

    Args:
        filter_type: ``Tip`` kolonu ('processor', 'buyer_city', 'equipment_supplier').
        material:    ``Hammadde/Sektor`` kolonu üzerinde case-insensitive substring filtresi.
        city:        ``Sehir/Ilce`` kolonu üzerinde case-insensitive substring filtresi.

    Returns:
        Filtrelenmiş DataFrame'in bağımsız kopyası.
    """
    df = pd.read_parquet(REFERENCE_DIR / "organizations.parquet").copy()
    if filter_type is not None:
        df = df[df["Tip"] == filter_type]
    if material is not None:
        df = df[df["Hammadde/Sektor"].fillna("").str.contains(material, case=False, na=False)]
    if city is not None:
        df = df[df["Sehir/Ilce"].fillna("").str.contains(city, case=False, na=False)]
    return df.reset_index(drop=True)


@functools.lru_cache(maxsize=None)
def load_distances() -> pd.DataFrame:
    """09_geo_distance temizlenmiş hâli (composite Source/Destination ID anahtarı)."""
    return pd.read_parquet(REFERENCE_DIR / "distances.parquet")


@functools.lru_cache(maxsize=None)
def load_distance_lookup() -> dict[tuple[str, str], dict[str, float]]:
    """``(src_id, dst_id) -> {'km': float, 'dakika': float}`` lookup tablosu (.pkl'den)."""
    with open(REFERENCE_DIR / "distance_lookup.pkl", "rb") as f:
        return pickle.load(f)


@functools.lru_cache(maxsize=None)
def load_carbon_factors() -> dict[str, float]:
    """Hackathon resmi taşıma karbon katsayıları (kg CO2 / ton-km).

    Returns:
        ``{"kara": 0.100, "deniz": 0.015, "hava": 0.500, "demiryolu": 0.030}``
    """
    df = pd.read_parquet(REFERENCE_DIR / "carbon.parquet")
    out: dict[str, float] = {}
    for _, row in df.iterrows():
        excel_key = str(row["Mod/Proses"])
        api_key = _CARBON_MODE_MAP.get(excel_key)
        if api_key is None:
            continue
        out[api_key] = float(row["Deger"])
    return out


@functools.lru_cache(maxsize=None)
def load_quality_match_matrix() -> dict[tuple[str, str], float]:
    """Producer × buyer kalite eşleşme skorları.

    Returns:
        ``{(producer_grade, buyer_grade): score}`` — A/B/C × A/B/C, 9 satır.
        Örnek: ``("A","A") -> 1.0``, ``("C","A") -> 0.20``.
    """
    df = pd.read_parquet(REFERENCE_DIR / "quality_match.parquet")
    return {
        (str(row["Producer"]), str(row["Buyer"])): float(row["Score"])
        for _, row in df.iterrows()
    }


@functools.lru_cache(maxsize=None)
def load_delivery_risk(transport_mode: str) -> float:
    """Taşıma modu için typical teslimat-gecikme risk değeri (0–1).

    Args:
        transport_mode: ``"kara"`` | ``"deniz"`` | ``"demiryolu"`` | ``"hava"``.

    Returns:
        Excel ``Typical`` değeri. Bilinmeyen mod için 0.5 (orta) döner.
    """
    excel_key = _DELIVERY_RISK_MAP.get(transport_mode)
    if excel_key is None:
        return 0.5
    df = pd.read_parquet(REFERENCE_DIR / "risk_delivery.parquet")
    sub = df[df["Anahtar"] == excel_key]
    if sub.empty:
        return 0.5
    return float(sub["Typical"].iloc[0])


@functools.lru_cache(maxsize=None)
def load_price_volatility(material: str) -> float:
    """Hammadde için typical fiyat oynaklığı (0–1).

    Args:
        material: ``"pomza"`` | ``"perlit"`` | ``"kabak_cekirdegi"``.

    Returns:
        Excel ``Typical`` değeri. Bilinmeyen hammadde için 0.3 döner.
    """
    excel_key = _PRICE_VOL_MAP.get(material)
    if excel_key is None:
        return 0.3
    df = pd.read_parquet(REFERENCE_DIR / "risk_price.parquet")
    sub = df[df["Anahtar"] == excel_key]
    if sub.empty:
        return 0.3
    return float(sub["Typical"].iloc[0])


def _safe_norm(value: float, vmin: float, vmax: float) -> float:
    """[vmin, vmax] aralığına min-max normalize eder; aralık 0 ise 0.5 döner."""
    if pd.isna(value):
        return 0.5
    if vmax <= vmin:
        return 0.5
    return float(max(0.0, min(1.0, (value - vmin) / (vmax - vmin))))


@functools.lru_cache(maxsize=None)
def load_buyer_demand_score(country: str, sector: str) -> float:
    """Ülke + sektör için 0–1 talep skoru (USD_milyon ve CAGR_pct karışımı).

    Formül: ``0.5 * norm(USD_milyon) + 0.3 * norm(CAGR, 0, 25) + 0.2 * 1.0``,
    ardından [0, 1] aralığına kırpılır. Eşleşme yoksa 0.5.

    Args:
        country: Ülke kodu — ``"TR"`` | ``"DE"`` | ``"NL"``.
        sector:  Sektör — ``"building_insulation"``, ``"food_snack"`` vb.

    Returns:
        0.0–1.0 arası float skor.
    """
    df = pd.read_parquet(REFERENCE_DIR / "buyer_markets.parquet")

    sub = df[(df["Bolge"] == country) & (df["Sektor"] == sector)]
    if sub.empty:
        return 0.5

    # Global min/max — sayısal Bolge satırları üzerinden
    valid = df[df["USD_milyon"].notna()]
    if valid.empty:
        return 0.5
    g_min = float(valid["USD_milyon"].min())
    g_max = float(valid["USD_milyon"].max())

    usd = sub["USD_milyon"].dropna()
    cagr = sub["CAGR_pct"].dropna()
    usd_val = float(usd.mean()) if not usd.empty else float("nan")
    cagr_val = float(cagr.mean()) if not cagr.empty else float("nan")

    score = (
        0.5 * _safe_norm(usd_val, g_min, g_max)
        + 0.3 * _safe_norm(cagr_val, 0.0, 25.0)
        + 0.2 * 1.0
    )
    return float(max(0.0, min(1.0, score)))
