"""Analiz geçmişi persist + listeleme servisi.

`save_analyze` `/api/analyze` çağrısı sonrası `asyncio.create_task` ile
fire-and-forget çağrılır — response client'a gittikten sonra DB'ye yazılır.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import structlog
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine

from raw2value_ml import AnalyzePayload, AnalyzeResponse

from ..db.models import AnalysisRecord
from ..schemas.fx import FxResponse

_logger = structlog.get_logger("history_service")


def _parse_fx_date(date_str: str) -> datetime | None:
    """TCMB DD-MM-YYYY ya da ISO yyyy-mm-dd parse et."""
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
    return None


def build_record(
    *,
    request_id: str,
    user_id: uuid.UUID | None,
    organization_id: uuid.UUID | None,
    payload: AnalyzePayload,
    response: AnalyzeResponse,
    fx: FxResponse,
    duration_ms: int,
    model_version: str = "v1.0",
) -> AnalysisRecord:
    """`AnalyzeRequest` + `AnalyzeResponse` → `AnalysisRecord`."""
    return AnalysisRecord(
        request_id=request_id,
        user_id=user_id,
        organization_id=organization_id,
        raw_material=payload.raw_material,
        tonnage=payload.tonnage,
        quality=payload.quality,
        origin_city=payload.origin_city,
        target_country=payload.target_country,
        target_city=payload.target_city,
        transport_mode=payload.transport_mode,
        priority=payload.priority,
        input_mode=payload.input_mode,
        fx_scenario_pct=payload.fx_scenario_pct,
        cost_scenario_pct=payload.cost_scenario_pct,
        payload_json=payload.model_dump(mode="json"),
        recommended_route=response.recommended_route,
        expected_profit_try=response.expected_profit_try,
        value_uplift_pct=response.value_uplift_pct,
        co2_kg=response.co2_kg,
        confidence_overall=response.confidence.overall,
        response_json=response.model_dump(mode="json"),
        usd_try_at_call=fx.usd_try,
        eur_try_at_call=fx.eur_try,
        fx_last_updated=_parse_fx_date(fx.last_updated),
        duration_ms=duration_ms,
        model_version=model_version,
    )


async def save_analyze(
    session_maker: async_sessionmaker[AsyncSession] | None,
    *,
    record: AnalysisRecord,
) -> None:
    """Tek satır insert. Hata fırlatırsa swallow + log (fire-and-forget güvencesi)."""
    if session_maker is None:
        _logger.warning(
            "history_skip_no_session", request_id=record.request_id
        )
        return
    try:
        async with session_maker() as session:
            session.add(record)
            await session.commit()
        _logger.info(
            "history_saved",
            request_id=record.request_id,
            route=record.recommended_route,
        )
    except Exception as exc:  # pragma: no cover  (defensive — fire-and-forget)
        _logger.exception(
            "history_save_failed", request_id=record.request_id, error=str(exc)
        )


async def list_history(
    db: AsyncSession,
    *,
    user_id: uuid.UUID | None,
    page: int,
    page_size: int,
    material: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[AnalysisRecord], int]:
    """Sayfalı liste döner; `user_id=None` admin yetkisi anlamına gelir."""
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)

    stmt = select(AnalysisRecord)
    count_stmt = select(func.count(AnalysisRecord.id))

    conds: list[Any] = []
    if user_id is not None:
        conds.append(AnalysisRecord.user_id == user_id)
    if material:
        conds.append(AnalysisRecord.raw_material == material)
    if date_from is not None:
        conds.append(AnalysisRecord.created_at >= date_from)
    if date_to is not None:
        conds.append(AnalysisRecord.created_at <= date_to)
    for cond in conds:
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    stmt = stmt.order_by(desc(AnalysisRecord.created_at)).limit(page_size).offset(
        (page - 1) * page_size
    )
    rows = (await db.execute(stmt)).scalars().all()
    total = (await db.execute(count_stmt)).scalar_one()
    return list(rows), int(total)


async def get_history(
    db: AsyncSession, *, record_id: int, user_id: uuid.UUID | None
) -> AnalysisRecord | None:
    """Detay; user_id verilirse own kontrolü."""
    record = await db.get(AnalysisRecord, record_id)
    if record is None:
        return None
    if user_id is not None and record.user_id != user_id:
        return None
    return record


# Engine -> sessionmaker accessor (lazy)
def session_maker_from_engine(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)
