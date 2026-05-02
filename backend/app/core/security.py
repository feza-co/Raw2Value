"""JWT + bcrypt yardımcı fonksiyonları.

passlib yerine `bcrypt` paketini doğrudan kullanırız (passlib 1.7.4 +
bcrypt 4.x/5.x tip uyumsuzluğu yaşandığında en az sürpriz yaklaşım).

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §18 ADIM 3.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from ..config import settings
from ..exceptions import AuthError

# bcrypt 72-byte limitini güvenli kesim ile karşılayalım (NIST tavsiyesi).
_BCRYPT_MAX_BYTES = 72


def _truncate(secret: str) -> bytes:
    """Şifreyi UTF-8 byte'a çevirir ve 72 byte ile sınırlar."""
    return secret.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(plain: str) -> str:
    """bcrypt ile şifre hash'le (varsayılan rounds=settings.PASSWORD_HASH_ROUNDS)."""
    salt = bcrypt.gensalt(rounds=settings.PASSWORD_HASH_ROUNDS)
    return bcrypt.hashpw(_truncate(plain), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Düz şifreyi hash ile karşılaştır."""
    try:
        return bcrypt.checkpw(_truncate(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    sub: str, *, extra: dict[str, Any] | None = None, ttl_min: int | None = None
) -> str:
    """Kısa ömürlü access token üret."""
    return _encode(
        sub,
        extra=extra,
        ttl=timedelta(minutes=ttl_min or settings.JWT_ACCESS_TTL_MIN),
        token_type="access",
    )


def create_refresh_token(sub: str, *, ttl_days: int | None = None) -> str:
    """Uzun ömürlü refresh token üret."""
    return _encode(
        sub,
        extra=None,
        ttl=timedelta(days=ttl_days or settings.JWT_REFRESH_TTL_DAYS),
        token_type="refresh",
    )


def decode_token(token: str) -> dict[str, Any]:
    """JWT'yi doğrula ve payload'u dön. Geçersizse `AuthError`."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise AuthError(f"Invalid token: {exc}") from exc


def _encode(
    sub: str, *, extra: dict[str, Any] | None, ttl: timedelta, token_type: str
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
        "type": token_type,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
