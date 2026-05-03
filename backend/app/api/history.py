"""/api/history endpoint'leri.

Owner-scope: admin değilse `user_id == current_user.id` zorlanır.
"""

import math
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import User
from ..db.session import get_db
from ..deps import get_current_user
from ..exceptions import NotFoundError
from ..schemas.history import (
    AnalysisRecordDetail,
    AnalysisRecordSummary,
    PaginatedHistory,
)
from ..services import history_service

router = APIRouter(prefix="/api/history", tags=["history"])


def _scope_user_id(user: User):
    return None if user.role == "admin" else user.id


@router.get("", response_model=PaginatedHistory)
async def list_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    material: str | None = Query(default=None, max_length=30),
    date_from: datetime | None = Query(default=None, alias="from"),
    date_to: datetime | None = Query(default=None, alias="to"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedHistory:
    rows, total = await history_service.list_history(
        db,
        user_id=_scope_user_id(user),
        page=page,
        page_size=page_size,
        material=material,
        date_from=date_from,
        date_to=date_to,
    )
    total_pages = max(math.ceil(total / page_size), 1) if total else 0
    return PaginatedHistory(
        items=[AnalysisRecordSummary.model_validate(r) for r in rows],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/{record_id}", response_model=AnalysisRecordDetail)
async def get_history_detail(
    record_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalysisRecordDetail:
    record = await history_service.get_history(
        db, record_id=record_id, user_id=_scope_user_id(user)
    )
    if record is None:
        raise NotFoundError("History record not found", code="history_not_found")
    return AnalysisRecordDetail.model_validate(record)
