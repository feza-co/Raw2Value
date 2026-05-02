"""Producer / Processor / Buyer profile modelleri.

Org tek satır; profile alt-tablolar yetenek başına bilgi taşır.
Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md §6.2.
"""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class ProducerProfile(Base):
    __tablename__ = "producer_profiles"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    raw_materials: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)), nullable=False, server_default="{}"
    )
    capacity_ton_year: Mapped[int | None] = mapped_column(Integer)
    quality_grades: Mapped[list[str]] = mapped_column(
        ARRAY(String(2)), nullable=False, server_default="{}"
    )


class ProcessorProfile(Base):
    __tablename__ = "processor_profiles"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    processing_routes: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)), nullable=False, server_default="{}"
    )
    capacity_ton_year: Mapped[int | None] = mapped_column(Integer)
    certifications: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)), nullable=False, server_default="{}"
    )
    unit_cost_try_per_ton: Mapped[float | None] = mapped_column(Numeric(10, 2))


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    product_interests: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)), nullable=False, server_default="{}"
    )
    payment_terms_days: Mapped[int | None] = mapped_column(Integer)
    credit_score: Mapped[float | None] = mapped_column(Numeric(3, 2))
