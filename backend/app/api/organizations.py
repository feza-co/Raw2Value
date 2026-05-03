"""/api/orgs CRUD endpoint'leri."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import User
from ..db.session import get_db
from ..deps import get_current_user
from ..schemas.organization import (
    OrgCreate,
    OrgOut,
    OrgUpdate,
    PaginatedOrgs,
)
from ..services import org_service

router = APIRouter(prefix="/api/orgs", tags=["orgs"])


@router.post("", response_model=OrgOut, status_code=status.HTTP_201_CREATED)
async def create_org(
    payload: OrgCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrgOut:
    data = await org_service.create_org(db, user=user, payload=payload)
    return OrgOut.model_validate(data)


@router.get("", response_model=PaginatedOrgs)
async def list_orgs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    capability: str | None = Query(default=None, max_length=50),
    city: str | None = Query(default=None, max_length=100),
    country: str | None = Query(default=None, min_length=2, max_length=2),
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedOrgs:
    items, total, total_pages = await org_service.list_orgs(
        db,
        page=page,
        page_size=page_size,
        capability=capability,
        city=city,
        country=country,
    )
    return PaginatedOrgs(
        items=[OrgOut.model_validate(it) for it in items],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/{org_id}", response_model=OrgOut)
async def get_org(
    org_id: uuid.UUID,
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrgOut:
    data = await org_service.get_org(db, org_id=org_id)
    return OrgOut.model_validate(data)


@router.patch("/{org_id}", response_model=OrgOut)
async def update_org(
    org_id: uuid.UUID,
    payload: OrgUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrgOut:
    data = await org_service.update_org(db, user=user, org_id=org_id, payload=payload)
    return OrgOut.model_validate(data)
