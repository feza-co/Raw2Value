"""Master Excel'i tip-temiz parquet referans tablolarına dönüştüren ETL modülü.

Kullanım:
    python -m ml.src.etl --xlsx data/master/raw2value_v4.xlsx --out data/reference/

veya:
    from ml.src.etl import extract_master_excel
    extract_master_excel("data/master/raw2value_v4.xlsx", "data/reference/")
"""
from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Yardımcı dönüştürücüler
# ---------------------------------------------------------------------------
def _to_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Verilen kolonları sayıya çevirir; çeviremediği değerleri NaN yapar."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _to_datetime(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Verilen kolonları datetime'a çevirir."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Sheet bazlı extractor'lar
# ---------------------------------------------------------------------------
def _extract_materials(xlsx: str | Path) -> pd.DataFrame:
    df = pd.read_excel(xlsx, sheet_name="02_material_reference")
    return _to_numeric(df, ["Min", "Max", "Typical"])


def _extract_routes(xlsx: str | Path) -> pd.DataFrame:
    df = pd.read_excel(xlsx, sheet_name="03_processing_routes")
    numeric_cols = [
        "Maliyet TL/ton (typical)",
        "Maliyet USD/ton (typical)",
        "CAPEX/ton",
        "Satis_USD_ton_min",
        "Satis_USD_ton_max",
        "Satis_USD_ton_typical",
    ]
    return _to_numeric(df, numeric_cols)


def _extract_organizations(xlsx: str | Path) -> pd.DataFrame:
    df = pd.read_excel(xlsx, sheet_name="04_organizations")
    return _to_numeric(df, ["Lat", "Lon", "Kapasite_ton_yil"])


def _extract_buyer_markets(xlsx: str | Path) -> pd.DataFrame:
    df = pd.read_excel(xlsx, sheet_name="05_buyer_markets")
    df = _to_numeric(df, ["Yil", "USD_milyon", "CAGR_pct", "Pazar_payi_eu_pct"])
    return df


def _extract_distances(xlsx: str | Path) -> tuple[pd.DataFrame, dict]:
    """09_geo_distance — sadece geçerli mesafe satırlarını üretir.

    Sheet iki tabloya bölünmüş:
      1) Mesafe matrisi (Source -> Destination, Type ∈ {osb, port, border, buyer_city})
      2) KOORDINATLAR (Type kolonu Lat içerir; Distance kolonu Lon olur)
    Filtre: Distance km numerik VE Type bir string (yani Lat değil).
    """
    df = pd.read_excel(xlsx, sheet_name="09_geo_distance")
    df["Distance km"] = pd.to_numeric(df["Distance km"], errors="coerce")
    df["Duration min"] = pd.to_numeric(df["Duration min"], errors="coerce")
    df = df[df["Distance km"].notna()]
    df = df[df["Type"].apply(lambda x: isinstance(x, str))]
    # parquet için object kolonları string'e çevir; Hammadde NaN'ları "" olur ama ayrım için pd.NA kullan
    for col in ["Source ID", "Source", "Destination ID", "Destination", "Type", "Hammadde"]:
        df[col] = df[col].astype("string")
    df = df.reset_index(drop=True)

    lookup: dict[tuple[str, str], dict[str, float]] = {}
    for _, row in df.iterrows():
        key = (str(row["Source ID"]), str(row["Destination ID"]))
        lookup[key] = {
            "km": float(row["Distance km"]),
            "dakika": float(row["Duration min"]) if pd.notna(row["Duration min"]) else float("nan"),
        }
    return df, lookup


def _extract_carbon(xlsx: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """10_carbon_factors — hackathon_official ve alternatives ayrı parquetlere böl."""
    df = pd.read_excel(xlsx, sheet_name="10_carbon_factors")
    df["Deger"] = pd.to_numeric(df["Deger"], errors="coerce")
    official = df[df["Faktor adi"] == "hackathon_official"].reset_index(drop=True)
    alternatives = df[df["Faktor adi"] != "hackathon_official"].reset_index(drop=True)
    return official, alternatives


def _extract_fx(xlsx: str | Path) -> pd.DataFrame:
    df = pd.read_excel(xlsx, sheet_name="11_fx_rates")
    numeric_cols = [
        "USD/TRY (forex_buying)",
        "USD/TRY (forex_selling)",
        "EUR/TRY (forex_buying)",
        "EUR/TRY (forex_selling)",
    ]
    df = _to_numeric(df, numeric_cols)
    df = _to_datetime(df, ["Date"])
    return df


def _extract_risk_quality_blocks(xlsx: str | Path) -> dict[str, pd.DataFrame]:
    """12_risk_quality 4 alt-bloğa ayrılır.

    Anchor satırlar:
      - 'RISK/Delivery' -> sonra 'delivery' rows
      - 'RISK/Price' -> sonra 'price_volatility' rows
      - 'QUALITY MATCH MATRIX' -> Producer / Buyer requires / Score header
        + 9 grade satırı (Tip ∈ {A,B,C}, Anahtar ∈ {A,B,C})
      - 'BUYER TYPICAL QUALITY DEMAND' -> Buyer segment / Required grade rows
    """
    df = pd.read_excel(xlsx, sheet_name="12_risk_quality")

    # Min/Max/Typical sayısallaştırılır (header satırları zaten metin)
    risk_delivery = df[df["Tip"] == "delivery"].copy()
    risk_delivery = _to_numeric(risk_delivery, ["Min", "Max", "Typical"]).reset_index(drop=True)

    risk_price = df[df["Tip"] == "price_volatility"].copy()
    risk_price = _to_numeric(risk_price, ["Min", "Max", "Typical"]).reset_index(drop=True)

    # QUALITY MATCH MATRIX bloku — Tip ∈ {A,B,C} AND Anahtar ∈ {A,B,C}
    grades = {"A", "B", "C"}
    qm = df[(df["Tip"].isin(grades)) & (df["Anahtar"].isin(grades))].copy()
    qm = qm.rename(columns={"Tip": "Producer", "Anahtar": "Buyer", "Min": "Score"})
    qm["Score"] = pd.to_numeric(qm["Score"], errors="coerce")
    qm = qm[["Producer", "Buyer", "Score", "Drivers/Notlar"]].rename(
        columns={"Drivers/Notlar": "Rationale"}
    ).reset_index(drop=True)

    # BUYER TYPICAL QUALITY DEMAND — anchor sonrası satırlar
    anchor_idx_arr = df.index[df["Tip"] == "BUYER TYPICAL QUALITY DEMAND"].tolist()
    if not anchor_idx_arr:
        quality_demand = pd.DataFrame(columns=["Buyer segment", "Required grade", "Standards", "Notes"])
    else:
        start = anchor_idx_arr[0] + 2  # anchor + 'Buyer segment / Required grade / Standards' header
        block = df.loc[start:].copy()
        block = block[block["Tip"].notna()].reset_index(drop=True)
        quality_demand = block.rename(
            columns={
                "Tip": "Buyer segment",
                "Anahtar": "Required grade",
                "Min": "Standards",
                "Drivers/Notlar": "Notes",
            }
        )[["Buyer segment", "Required grade", "Standards", "Notes"]]

    return {
        "risk_delivery": risk_delivery,
        "risk_price": risk_price,
        "quality_match": qm,
        "quality_demand": quality_demand,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def extract_master_excel(xlsx_path: str, out_dir: str) -> dict[str, pd.DataFrame]:
    """Master Excel'i okuyup parquet + pkl çıktıları üretir.

    Args:
        xlsx_path: Master xlsx dosyasının yolu.
        out_dir:   Çıktıların yazılacağı dizin (data/reference/).

    Returns:
        İsim -> DataFrame eşleşmesi (lookup .pkl bu dict'te yer almaz).
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    materials = _extract_materials(xlsx_path)
    routes = _extract_routes(xlsx_path)
    organizations = _extract_organizations(xlsx_path)
    buyer_markets = _extract_buyer_markets(xlsx_path)
    distances, distance_lookup = _extract_distances(xlsx_path)
    carbon_official, carbon_alternatives = _extract_carbon(xlsx_path)
    fx_rates = _extract_fx(xlsx_path)
    rq_blocks = _extract_risk_quality_blocks(xlsx_path)

    # parquet writes
    materials.to_parquet(out / "materials.parquet", index=False)
    routes.to_parquet(out / "routes.parquet", index=False)
    organizations.to_parquet(out / "organizations.parquet", index=False)
    buyer_markets.to_parquet(out / "buyer_markets.parquet", index=False)
    distances.to_parquet(out / "distances.parquet", index=False)
    carbon_official.to_parquet(out / "carbon.parquet", index=False)
    carbon_alternatives.to_parquet(out / "carbon_alternatives.parquet", index=False)
    fx_rates.to_parquet(out / "fx_rates.parquet", index=False)
    rq_blocks["risk_delivery"].to_parquet(out / "risk_delivery.parquet", index=False)
    rq_blocks["risk_price"].to_parquet(out / "risk_price.parquet", index=False)
    rq_blocks["quality_match"].to_parquet(out / "quality_match.parquet", index=False)
    rq_blocks["quality_demand"].to_parquet(out / "quality_demand.parquet", index=False)

    # pkl write
    with open(out / "distance_lookup.pkl", "wb") as f:
        pickle.dump(distance_lookup, f)

    return {
        "materials": materials,
        "routes": routes,
        "organizations": organizations,
        "buyer_markets": buyer_markets,
        "distances": distances,
        "carbon": carbon_official,
        "carbon_alternatives": carbon_alternatives,
        "fx_rates": fx_rates,
        "risk_delivery": rq_blocks["risk_delivery"],
        "risk_price": rq_blocks["risk_price"],
        "quality_match": rq_blocks["quality_match"],
        "quality_demand": rq_blocks["quality_demand"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Raw2Value master Excel -> parquet ETL")
    parser.add_argument("--xlsx", required=True, help="Master Excel yolu")
    parser.add_argument("--out", required=True, help="Çıktı dizini (parquet + pkl)")
    args = parser.parse_args()

    result = extract_master_excel(args.xlsx, args.out)
    print(f"[etl] {len(result)} parquet + 1 pkl üretildi -> {args.out}")
    for name, df in result.items():
        print(f"  {name:25s} shape={df.shape}")


if __name__ == "__main__":
    main()
