"""AnalysisRecord ORM modeli — her /api/analyze çağrısının audit trail'i.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md §6.3.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Input snapshot
    raw_material: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    tonnage: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quality: Mapped[str] = mapped_column(String(10), nullable=False)
    origin_city: Mapped[str] = mapped_column(String(100), nullable=False)
    target_country: Mapped[str] = mapped_column(String(2), nullable=False)
    target_city: Mapped[str | None] = mapped_column(String(100))
    transport_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    priority: Mapped[str] = mapped_column(String(30), nullable=False)
    input_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    fx_scenario_pct: Mapped[float] = mapped_column(
        Numeric(5, 4), nullable=False, default=0
    )
    cost_scenario_pct: Mapped[float] = mapped_column(
        Numeric(5, 4), nullable=False, default=0
    )
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Output snapshot
    recommended_route: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    expected_profit_try: Mapped[float | None] = mapped_column(Numeric(14, 2))
    value_uplift_pct: Mapped[float | None] = mapped_column(Numeric(8, 4))
    co2_kg: Mapped[float | None] = mapped_column(Numeric(12, 2))
    confidence_overall: Mapped[float | None] = mapped_column(Numeric(5, 2))
    response_json: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # FX snapshot — analiz anında geçerli kur (denetim için)
    usd_try_at_call: Mapped[float | None] = mapped_column(Numeric(8, 4))
    eur_try_at_call: Mapped[float | None] = mapped_column(Numeric(8, 4))
    fx_last_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Performans
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    model_version: Mapped[str | None] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    def __repr__(self) -> str:
        return (
            f"<AnalysisRecord id={self.id} request_id={self.request_id!r} "
            f"route={self.recommended_route!r}>"
        )
