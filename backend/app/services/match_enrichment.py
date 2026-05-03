"""Match score zenginleştirme — DB'deki gerçek processor×buyer çiftlerinden
heterojen match listesi üretir.

ML inference'ı (`raw2value_ml.analyze`) processor isimlerini referans
parquet'ten alıyor; demo seed'de yeni processor org'ları eklediğimizde
isim eşleşmesi olmuyordu. Bu modül ML response'undaki match listesini
**override eder**: DB'deki ``can_process_material=True`` olan org'lar
× ``can_buy_material=True`` olan org'lar tüm kombinasyonları için
``raw2value_ml.scorer.compute_match_score``'u çağırır, her processor
için processor-spesifik distance + carbon kullanarak gerçekçi
heterojen skorlar üretir.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from raw2value_ml.scorer import compute_match_score

from ..db.models import BuyerProfile, Organization, ProcessorProfile
from ..services.geo_service import haversine_km


_CITY_COORDS: dict[str, tuple[float, float]] = {
    # TR
    "antalya": (36.8969, 30.7133),
    "nevsehir": (38.6939, 34.6857),
    "acigol": (38.5478, 34.5028),
    "istanbul": (41.0082, 28.9784),
    "izmir": (38.4192, 27.1287),
    "ankara": (39.9334, 32.8597),
    "kayseri": (38.7220, 35.4881),
    "aksaray": (38.3687, 34.0370),
    # DE
    "duisburg": (51.4344, 6.7623),     # Avrupa'nın en büyük iç limanı
    "hamburg": (53.5511, 9.9937),
    "bremen": (53.0793, 8.8017),
    "berlin": (52.52, 13.405),
    # NL
    "rotterdam": (51.9244, 4.4777),
    "amsterdam": (52.3676, 4.9041),
}

_TURKISH_FOLD = str.maketrans({
    "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g",
    "ı": "i", "I": "i", "İ": "i",
    "ö": "o", "Ö": "o", "ş": "s", "Ş": "s",
    "ü": "u", "Ü": "u",
})

_EMISSION_FACTORS: dict[str, float] = {
    "kara": 0.100, "deniz": 0.015, "demiryolu": 0.030, "hava": 0.500,
}


def _city_key(s: str | None) -> str:
    if not s:
        return ""
    return s.translate(_TURKISH_FOLD).lower().strip().replace(" ", "")


def _city_coords(city: str | None) -> tuple[float, float] | None:
    return _CITY_COORDS.get(_city_key(city))


def _route_matches_material(routes: list[str], raw_material: str) -> bool:
    """Processor route listesi bu hammaddeyi destekliyor mu? (prefix-match)."""
    return any(r == raw_material or r.startswith(f"{raw_material}_") for r in routes)


async def enrich_match_results(
    db: AsyncSession,
    *,
    matches: list[dict[str, Any]],  # ML response'undan; isim ipucu için
    raw_material: str,
    origin_city: str,
    target_country: str,
    target_city: str | None,
    tonnage: float,
    transport_mode: str,
    predicted_profit_try: float,
    quality: str,
    priority: str,
    top_k: int = 6,
) -> list[dict[str, Any]]:
    """DB'deki processor × buyer çiftleri için heterojen skorlar üretir.

    Returns:
        Score'a göre azalan ``[{processor_name, buyer_name, score,
        components}, ...]`` listesi (en fazla ``top_k`` adet).
        DB sorgusu boş dönerse ``matches`` (orijinal ML çıktısı) aynen döner.
    """
    origin = _city_coords(origin_city)
    default_target_map = {"DE": "duisburg", "NL": "rotterdam", "TR": "istanbul"}
    dest = _city_coords(target_city) or _city_coords(
        default_target_map.get(target_country, "istanbul")
    )

    # DB'den processor org'ları (lat/lon dolu olanlar) ve buyer org'ları çek
    processor_rows = (
        await db.execute(
            select(Organization, ProcessorProfile).join(
                ProcessorProfile,
                ProcessorProfile.organization_id == Organization.id,
            )
            .where(Organization.can_process_material.is_(True))
            .where(Organization.lat.isnot(None))
            .where(Organization.lon.isnot(None))
        )
    ).all()

    buyer_rows = (
        await db.execute(
            select(Organization, BuyerProfile).join(
                BuyerProfile,
                BuyerProfile.organization_id == Organization.id,
            )
            .where(Organization.can_buy_material.is_(True))
            .where(Organization.country == target_country)
        )
    ).all()

    # Hedef ülkede buyer yoksa (ör. TR target için) tüm buyer'lardan al
    if not buyer_rows:
        buyer_rows = (
            await db.execute(
                select(Organization, BuyerProfile).join(
                    BuyerProfile,
                    BuyerProfile.organization_id == Organization.id,
                )
                .where(Organization.can_buy_material.is_(True))
            )
        ).all()

    if not processor_rows or not buyer_rows or origin is None or dest is None:
        return matches  # fallback: ML çıktısını koru

    # Hammadde-uyumlu processor'ları filtrele
    valid_processors = [
        (org, prof) for (org, prof) in processor_rows
        if _route_matches_material(list(prof.processing_routes or []), raw_material)
    ]
    if not valid_processors:
        valid_processors = processor_rows  # uyumlu yoksa hepsi

    emission_factor = _EMISSION_FACTORS.get(transport_mode, 0.100)
    out: list[dict[str, Any]] = []

    for proc_org, proc_profile in valid_processors:
        d_o_p = haversine_km(
            origin[0], origin[1], float(proc_org.lat), float(proc_org.lon)
        )
        # buyer-spesifik distance & carbon — her buyer'la kombinasyon
        for buyer_org, buyer_profile in buyer_rows:
            if buyer_org.lat is None or buyer_org.lon is None:
                d_p_b = haversine_km(
                    float(proc_org.lat), float(proc_org.lon), dest[0], dest[1]
                )
            else:
                d_p_b = haversine_km(
                    float(proc_org.lat), float(proc_org.lon),
                    float(buyer_org.lat), float(buyer_org.lon),
                )
            total_distance_km = d_o_p + d_p_b
            co2_kg = tonnage * total_distance_km * emission_factor

            # Processor cost varyasyonu (median 850 TRY/ton)
            cost_kick = 1.0
            if proc_profile.unit_cost_try_per_ton:
                ucost = float(proc_profile.unit_cost_try_per_ton)
                cost_kick = max(0.85, min(1.15, 850.0 / max(1.0, ucost)))

            # Buyer credit score — küçük profit etkisi
            credit_kick = 1.0
            if buyer_profile.credit_score is not None:
                credit_kick = 0.92 + 0.10 * float(buyer_profile.credit_score)

            adjusted_profit = predicted_profit_try * cost_kick * credit_kick

            producer = {"quality_grade": quality}
            processor = {"name": proc_org.name}
            # Buyer sector — UI'da default; product_interests'tan kabaca türet
            interests = list(buyer_profile.product_interests or [])
            sector = (
                "construction" if any("pumice" in s or "bims" in s for s in interests)
                else "filtration" if any("filtration" in s for s in interests)
                else "industrial"
            )
            buyer_dict = {
                "country": buyer_org.country or target_country,
                "sector": sector,
                "required_grade": "A" if quality == "A" else "B",
            }
            context = {
                "predicted_profit": adjusted_profit,
                "total_distance_km": total_distance_km,
                "co2_kg": co2_kg,
                "transport_mode": transport_mode,
            }

            score, components = compute_match_score(
                producer, processor, buyer_dict, context, priority=priority
            )

            out.append(
                {
                    "processor_name": proc_org.name,
                    "buyer_name": buyer_org.name,
                    "score": score,
                    "components": components,
                }
            )

    out.sort(key=lambda x: -x["score"])
    return out[:top_k]
