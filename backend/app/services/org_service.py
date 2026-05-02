"""Organization CRUD iş katmanı."""
from __future__ import annotations

import math
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import (
    BuyerProfile,
    Organization,
    ProcessorProfile,
    ProducerProfile,
    User,
)
from ..exceptions import ForbiddenError, NotFoundError
from ..schemas.organization import OrgCreate, OrgUpdate


def _serialize(org: Organization, *, profiles: dict | None = None) -> dict:
    return {
        "id": org.id,
        "name": org.name,
        "organization_type": org.organization_type,
        "district": org.district,
        "city": org.city,
        "country": org.country,
        "lat": org.lat,
        "lon": org.lon,
        "capabilities": {
            "can_supply_raw_material": org.can_supply_raw_material,
            "can_process_material": org.can_process_material,
            "can_buy_material": org.can_buy_material,
            "can_export": org.can_export,
            "has_storage": org.has_storage,
            "has_transport_capacity": org.has_transport_capacity,
        },
        "producer_profile": profiles.get("producer") if profiles else None,
        "processor_profile": profiles.get("processor") if profiles else None,
        "buyer_profile": profiles.get("buyer") if profiles else None,
        "created_at": org.created_at,
    }


async def _load_profiles(db: AsyncSession, org_id: uuid.UUID) -> dict:
    out: dict = {}
    producer = await db.get(ProducerProfile, org_id)
    if producer is not None:
        out["producer"] = {
            "raw_materials": list(producer.raw_materials or []),
            "capacity_ton_year": producer.capacity_ton_year,
            "quality_grades": list(producer.quality_grades or []),
        }
    processor = await db.get(ProcessorProfile, org_id)
    if processor is not None:
        out["processor"] = {
            "processing_routes": list(processor.processing_routes or []),
            "capacity_ton_year": processor.capacity_ton_year,
            "certifications": list(processor.certifications or []),
            "unit_cost_try_per_ton": (
                float(processor.unit_cost_try_per_ton)
                if processor.unit_cost_try_per_ton is not None
                else None
            ),
        }
    buyer = await db.get(BuyerProfile, org_id)
    if buyer is not None:
        out["buyer"] = {
            "product_interests": list(buyer.product_interests or []),
            "payment_terms_days": buyer.payment_terms_days,
            "credit_score": (
                float(buyer.credit_score) if buyer.credit_score is not None else None
            ),
        }
    return out


async def create_org(db: AsyncSession, *, user: User, payload: OrgCreate) -> dict:
    """Yeni org kaydet, kullanıcının organization_id'sini güncelle."""
    caps = payload.capabilities
    org = Organization(
        name=payload.name,
        organization_type=payload.organization_type,
        district=payload.district,
        city=payload.city,
        country=payload.country,
        lat=payload.lat,
        lon=payload.lon,
        can_supply_raw_material=caps.can_supply_raw_material,
        can_process_material=caps.can_process_material,
        can_buy_material=caps.can_buy_material,
        can_export=caps.can_export,
        has_storage=caps.has_storage,
        has_transport_capacity=caps.has_transport_capacity,
    )
    db.add(org)
    await db.flush()

    if payload.producer_profile:
        db.add(
            ProducerProfile(
                organization_id=org.id,
                raw_materials=payload.producer_profile.raw_materials,
                capacity_ton_year=payload.producer_profile.capacity_ton_year,
                quality_grades=payload.producer_profile.quality_grades,
            )
        )
    if payload.processor_profile:
        db.add(
            ProcessorProfile(
                organization_id=org.id,
                processing_routes=payload.processor_profile.processing_routes,
                capacity_ton_year=payload.processor_profile.capacity_ton_year,
                certifications=payload.processor_profile.certifications,
                unit_cost_try_per_ton=payload.processor_profile.unit_cost_try_per_ton,
            )
        )
    if payload.buyer_profile:
        db.add(
            BuyerProfile(
                organization_id=org.id,
                product_interests=payload.buyer_profile.product_interests,
                payment_terms_days=payload.buyer_profile.payment_terms_days,
                credit_score=payload.buyer_profile.credit_score,
            )
        )

    user.organization_id = org.id
    db.add(user)
    await db.commit()
    await db.refresh(org)

    profiles = await _load_profiles(db, org.id)
    return _serialize(org, profiles=profiles)


async def get_org(db: AsyncSession, *, org_id: uuid.UUID) -> dict:
    org = await db.get(Organization, org_id)
    if org is None:
        raise NotFoundError("Organization not found", code="org_not_found")
    profiles = await _load_profiles(db, org.id)
    return _serialize(org, profiles=profiles)


async def update_org(
    db: AsyncSession, *, user: User, org_id: uuid.UUID, payload: OrgUpdate
) -> dict:
    org = await db.get(Organization, org_id)
    if org is None:
        raise NotFoundError("Organization not found", code="org_not_found")
    if user.role != "admin" and user.organization_id != org.id:
        raise ForbiddenError("Not your organization")

    for field in ("name", "organization_type", "district", "city", "country", "lat", "lon"):
        new_val = getattr(payload, field)
        if new_val is not None:
            setattr(org, field, new_val)
    if payload.capabilities is not None:
        for flag in (
            "can_supply_raw_material",
            "can_process_material",
            "can_buy_material",
            "can_export",
            "has_storage",
            "has_transport_capacity",
        ):
            setattr(org, flag, getattr(payload.capabilities, flag))

    db.add(org)
    await db.commit()
    await db.refresh(org)
    profiles = await _load_profiles(db, org.id)
    return _serialize(org, profiles=profiles)


async def list_orgs(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
    capability: str | None = None,
    city: str | None = None,
    country: str | None = None,
) -> tuple[list[dict], int, int]:
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)

    stmt = select(Organization)
    count_stmt = select(func.count(Organization.id))

    capability_columns = {
        "can_supply_raw_material": Organization.can_supply_raw_material,
        "can_process_material": Organization.can_process_material,
        "can_buy_material": Organization.can_buy_material,
        "can_export": Organization.can_export,
        "has_storage": Organization.has_storage,
        "has_transport_capacity": Organization.has_transport_capacity,
    }
    if capability and capability in capability_columns:
        col = capability_columns[capability]
        stmt = stmt.where(col.is_(True))
        count_stmt = count_stmt.where(col.is_(True))
    if city:
        stmt = stmt.where(Organization.city == city)
        count_stmt = count_stmt.where(Organization.city == city)
    if country:
        stmt = stmt.where(Organization.country == country)
        count_stmt = count_stmt.where(Organization.country == country)

    stmt = stmt.order_by(Organization.created_at.desc()).limit(page_size).offset(
        (page - 1) * page_size
    )
    rows = (await db.execute(stmt)).scalars().all()
    total = int((await db.execute(count_stmt)).scalar_one())
    items: list[dict] = []
    for org in rows:
        profiles = await _load_profiles(db, org.id)
        items.append(_serialize(org, profiles=profiles))
    total_pages = max(math.ceil(total / page_size), 1) if total else 0
    return items, total, total_pages
