"""Demo seed — admin user + 5 organization (üretici/işleyici/alıcı karması).

Idempotent: zaten varsa skip eder. Tekrar çalıştırmak güvenli.
Kullanım: `docker compose exec api python scripts/seed_demo.py`
"""
from __future__ import annotations

import asyncio
import os
import sys

# Backend modülleri PYTHONPATH'te olmalı (Docker'da /app)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select  # noqa: E402

from app.config import settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.models import (  # noqa: E402
    BuyerProfile,
    Organization,
    ProcessorProfile,
    ProducerProfile,
    User,
)
from app.db.session import SessionLocal  # noqa: E402


_DEMO_ORGS = [
    {
        "name": "Doğa Pomza Ltd",
        "city": "Nevşehir",
        "district": "Acıgöl",
        "country": "TR",
        "lat": 38.55,
        "lon": 34.50,
        "capabilities": {
            "can_supply_raw_material": True,
            "can_export": True,
            "has_storage": True,
        },
        "producer": {
            "raw_materials": ["pomza"],
            "capacity_ton_year": 30000,
            "quality_grades": ["A", "B"],
        },
    },
    {
        "name": "Anadolu Perlit A.Ş.",
        "city": "İzmir",
        "district": "Menemen",
        "country": "TR",
        "lat": 38.61,
        "lon": 27.07,
        "capabilities": {"can_supply_raw_material": True, "can_export": True},
        "producer": {
            "raw_materials": ["perlit"],
            "capacity_ton_year": 25000,
            "quality_grades": ["A"],
        },
    },
    {
        "name": "Kapadokya Tarım Koop.",
        "city": "Nevşehir",
        "district": "Ürgüp",
        "country": "TR",
        "lat": 38.63,
        "lon": 34.91,
        "capabilities": {"can_supply_raw_material": True},
        "producer": {
            "raw_materials": ["kabak_cekirdegi"],
            "capacity_ton_year": 1500,
            "quality_grades": ["A", "B"],
        },
    },
    {
        "name": "Genper Madencilik A.Ş.",
        "city": "Nevşehir",
        "district": "Acıgöl",
        "country": "TR",
        "lat": 38.62,
        "lon": 34.71,
        "capabilities": {
            "can_process_material": True,
            "has_storage": True,
        },
        "processor": {
            "processing_routes": [
                "pomza_micronized_pumice",
                "pomza_filtration_media",
            ],
            "capacity_ton_year": 50000,
            "certifications": ["ISO9001"],
            "unit_cost_try_per_ton": 850.0,
        },
    },
    {
        "name": "BASF Deutschland GmbH",
        "city": "Hamburg",
        "country": "DE",
        "lat": 53.55,
        "lon": 9.99,
        "capabilities": {"can_buy_material": True},
        "buyer": {
            "product_interests": [
                "pomza_micronized_pumice",
                "perlit_filtration_product",
            ],
            "payment_terms_days": 30,
            "credit_score": 0.92,
        },
    },
]


async def upsert_admin(session) -> User:
    email = settings.DEMO_ADMIN_EMAIL.strip().lower()
    existing = (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    user = User(
        email=email,
        full_name="Demo Admin",
        hashed_password=hash_password(settings.DEMO_ADMIN_PASSWORD),
        role="admin",
        is_active=True,
    )
    session.add(user)
    await session.flush()
    return user


async def upsert_demo_user(
    session,
    *,
    email: str,
    full_name: str,
    password: str,
    org_name: str,
) -> User:
    """Demo persona user — belirli organization'a bağlı.

    Idempotent: email zaten varsa organization_id boşsa eşler, döner.
    """
    email = email.strip().lower()
    org = (
        await session.execute(
            select(Organization).where(Organization.name == org_name)
        )
    ).scalar_one_or_none()
    existing = (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if existing is not None:
        if org is not None and existing.organization_id is None:
            existing.organization_id = org.id
            await session.flush()
        return existing
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hash_password(password),
        role="user",
        is_active=True,
        organization_id=org.id if org is not None else None,
    )
    session.add(user)
    await session.flush()
    return user


async def upsert_org(session, *, spec: dict) -> Organization:
    existing = (
        await session.execute(
            select(Organization).where(Organization.name == spec["name"])
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    caps = spec.get("capabilities", {})
    org = Organization(
        name=spec["name"],
        city=spec.get("city"),
        district=spec.get("district"),
        country=spec.get("country", "TR"),
        lat=spec.get("lat"),
        lon=spec.get("lon"),
        can_supply_raw_material=caps.get("can_supply_raw_material", False),
        can_process_material=caps.get("can_process_material", False),
        can_buy_material=caps.get("can_buy_material", False),
        can_export=caps.get("can_export", False),
        has_storage=caps.get("has_storage", False),
        has_transport_capacity=caps.get("has_transport_capacity", False),
    )
    session.add(org)
    await session.flush()

    if (p := spec.get("producer")) is not None:
        session.add(
            ProducerProfile(
                organization_id=org.id,
                raw_materials=p["raw_materials"],
                capacity_ton_year=p["capacity_ton_year"],
                quality_grades=p["quality_grades"],
            )
        )
    if (p := spec.get("processor")) is not None:
        session.add(
            ProcessorProfile(
                organization_id=org.id,
                processing_routes=p["processing_routes"],
                capacity_ton_year=p["capacity_ton_year"],
                certifications=p.get("certifications", []),
                unit_cost_try_per_ton=p.get("unit_cost_try_per_ton"),
            )
        )
    if (p := spec.get("buyer")) is not None:
        session.add(
            BuyerProfile(
                organization_id=org.id,
                product_interests=p["product_interests"],
                payment_terms_days=p.get("payment_terms_days"),
                credit_score=p.get("credit_score"),
            )
        )
    return org


async def main() -> int:
    async with SessionLocal() as session:
        admin = await upsert_admin(session)
        for spec in _DEMO_ORGS:
            await upsert_org(session, spec=spec)
        # Demo persona — Mehmet Amca / Doğa Pomza Ltd
        mehmet = await upsert_demo_user(
            session,
            email="mehmet@dogapomza.tr",
            full_name="Mehmet Yılmaz",
            password="acigol2026",
            org_name="Doğa Pomza Ltd",
        )
        await session.commit()
        print(
            f"seed_complete admin={admin.email} demo_user={mehmet.email} "
            f"orgs={len(_DEMO_ORGS)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
