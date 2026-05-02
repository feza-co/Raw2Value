"""Producer / Processor / Buyer profile modelleri.

Org tek satır; profile alt-tablolar yetenek başına bilgi taşır. Portable
tipler için ARRAY → JSON `with_variant`; testler sqlite üzerinde de koşar.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md §6.2.
"""
from __future__ import annotations

import uuid

from sqlalchemy import JSON, ForeignKey, Integer, Numeric, String, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


def _str_array(length: int = 50):
    """Postgres'te ARRAY(VARCHAR), sqlite'da JSON listesi."""
    return ARRAY(String(length)).with_variant(JSON(), "sqlite")


class ProducerProfile(Base):
    __tablename__ = "producer_profiles"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    raw_materials: Mapped[list[str]] = mapped_column(
        _str_array(50), nullable=False, default=list
    )
    capacity_ton_year: Mapped[int | None] = mapped_column(Integer)
    quality_grades: Mapped[list[str]] = mapped_column(
        _str_array(2), nullable=False, default=list
    )


class ProcessorProfile(Base):
    __tablename__ = "processor_profiles"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    processing_routes: Mapped[list[str]] = mapped_column(
        _str_array(50), nullable=False, default=list
    )
    capacity_ton_year: Mapped[int | None] = mapped_column(Integer)
    certifications: Mapped[list[str]] = mapped_column(
        _str_array(50), nullable=False, default=list
    )
    unit_cost_try_per_ton: Mapped[float | None] = mapped_column(Numeric(10, 2))


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    product_interests: Mapped[list[str]] = mapped_column(
        _str_array(50), nullable=False, default=list
    )
    payment_terms_days: Mapped[int | None] = mapped_column(Integer)
    credit_score: Mapped[float | None] = mapped_column(Numeric(3, 2))
