"""Auth iş mantığı — register/login/me iş katmanı.

Endpoint katmanı (api/auth.py) bu fonksiyonları çağırır.
"""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from ..db.models import User
from ..exceptions import AuthError, ConflictError


async def register_user(
    db: AsyncSession, *, email: str, password: str, full_name: str | None = None
) -> User:
    """Yeni kullanıcı oluştur. Email zaten varsa `ConflictError`."""
    email_norm = email.strip().lower()

    existing = (
        await db.execute(select(User).where(User.email == email_norm))
    ).scalar_one_or_none()
    if existing is not None:
        raise ConflictError(
            "Email already registered", code="email_exists", details={"email": email_norm}
        )

    user = User(
        email=email_norm,
        full_name=full_name,
        hashed_password=hash_password(password),
        role="user",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, *, email: str, password: str) -> User:
    """Email + şifre doğrula, geçerse User dön; aksi halde `AuthError`."""
    email_norm = email.strip().lower()
    user = (
        await db.execute(select(User).where(User.email == email_norm))
    ).scalar_one_or_none()
    if user is None or not verify_password(password, user.hashed_password):
        raise AuthError("Invalid email or password", code="invalid_credentials")
    if not user.is_active:
        raise AuthError("User is inactive", code="inactive_user")
    return user


def issue_tokens(user: User) -> tuple[str, str]:
    """Access + refresh token üretir."""
    extra = {"role": user.role, "email": user.email}
    if user.organization_id:
        extra["org_id"] = str(user.organization_id)
    access = create_access_token(str(user.id), extra=extra)
    refresh = create_refresh_token(str(user.id))
    return access, refresh


async def refresh_access_token(db: AsyncSession, *, refresh_token: str) -> str:
    """Refresh token'dan yeni access token üret."""
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise AuthError("Not a refresh token", code="invalid_token_type")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthError("Missing subject", code="invalid_token")
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError) as exc:
        raise AuthError("Invalid subject", code="invalid_token") from exc
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise AuthError("User not found or inactive", code="invalid_user")
    access, _ = issue_tokens(user)
    return access
