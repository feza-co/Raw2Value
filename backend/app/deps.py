"""FastAPI dependency injection — DB oturumu ve aktif kullanıcı çözümleyici."""
from __future__ import annotations

import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .core.security import decode_token
from .db.models import User
from .db.session import get_db
from .exceptions import AuthError, ForbiddenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Bearer JWT'den User çek; yoksa veya geçersizse `AuthError` (401)."""
    if not token:
        raise AuthError("Missing bearer token", code="missing_token")
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise AuthError("Not an access token", code="invalid_token_type")
    sub = payload.get("sub")
    if not sub:
        raise AuthError("Missing subject", code="invalid_token")
    try:
        user_id = uuid.UUID(sub)
    except (ValueError, TypeError) as exc:
        raise AuthError("Invalid subject", code="invalid_token") from exc
    user = await db.get(User, user_id)
    if user is None:
        raise AuthError("User not found", code="user_not_found")
    if not user.is_active:
        raise AuthError("User inactive", code="inactive_user")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Yalnızca admin rolündeki kullanıcılar geçer; aksi halde 403."""
    if user.role != "admin":
        raise ForbiddenError("Admin only")
    return user
