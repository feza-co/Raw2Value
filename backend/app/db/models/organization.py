"""Organization ORM modeli — capability-based KOBİ kaydı.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md §6.2.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    organization_type: Mapped[str | None] = mapped_column(String(50))
    district: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(2), nullable=False, default="TR")
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)

    # Capability flags — bir org birden fazla yeteneğe sahip olabilir.
    can_supply_raw_material: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    can_process_material: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    can_buy_material: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    can_export: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_storage: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_transport_capacity: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name={self.name!r}>"
