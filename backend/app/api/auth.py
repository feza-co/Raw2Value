"""Auth router — /api/auth/{register,login,me,refresh}.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md §9.3-9.5.
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db.models import User
from ..db.session import get_db
from ..deps import get_current_user
from ..schemas.auth import (
    CapabilityFlags,
    OrganizationOut,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from ..services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _serialize_user(user: User) -> UserOut:
    org_out: OrganizationOut | None = None
    if user.organization is not None:
        org = user.organization
        org_out = OrganizationOut(
            id=org.id,
            name=org.name,
            city=org.city,
            district=org.district,
            country=org.country,
            lat=float(org.lat) if org.lat is not None else None,
            lon=float(org.lon) if org.lon is not None else None,
            capabilities=CapabilityFlags(
                can_supply_raw_material=org.can_supply_raw_material,
                can_process_material=org.can_process_material,
                can_buy_material=org.can_buy_material,
                can_export=org.can_export,
                has_storage=org.has_storage,
                has_transport_capacity=org.has_transport_capacity,
            ),
        )
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        organization=org_out,
        created_at=user.created_at,
    )


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> UserOut:
    user = await auth_service.register_user(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )
    return _serialize_user(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user = await auth_service.authenticate(db, email=form.username, password=form.password)
    access, refresh = auth_service.issue_tokens(user)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TTL_MIN * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    new_access = await auth_service.refresh_access_token(
        db, refresh_token=payload.refresh_token
    )
    return TokenResponse(
        access_token=new_access,
        refresh_token=None,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TTL_MIN * 60,
    )


@router.get("/me", response_model=UserOut)
async def me(current: User = Depends(get_current_user)) -> UserOut:
    return _serialize_user(current)
