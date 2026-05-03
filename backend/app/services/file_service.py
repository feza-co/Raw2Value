"""Dosya yükleme servisi — MIME beyaz liste + path traversal koruması + local FS.

S3_ENABLED=true ileride MinIO/S3 backend'i için stub bırakıyor; MVP local FS.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §9.17, §13.
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import structlog
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db.models import UploadedFile
from ..exceptions import ValidationAppError as ValidationError

_logger = structlog.get_logger("file_service")

# Path traversal + null byte + Windows reserved char defense.
_UNSAFE = re.compile(r"[\x00-\x1f\x7f<>:\"/\\|?*]+")


def _safe_filename(name: str) -> str:
    """`../etc/passwd` → `etc_passwd`. Boş string için fallback."""
    base = Path(name).name  # path bileşenlerini at
    cleaned = _UNSAFE.sub("_", base).strip(". ")
    if not cleaned:
        cleaned = "file"
    if len(cleaned) > 200:
        cleaned = cleaned[:200]
    return cleaned


def _validate_mime(content_type: str | None) -> str:
    if not content_type:
        raise ValidationError(
            "content_type missing", code="upload_missing_mime"
        )
    ct = content_type.split(";")[0].strip().lower()
    if ct not in settings.upload_allowed_mime_set:
        raise ValidationError(
            f"MIME tipi izin verilmiyor: {ct}",
            code="upload_invalid_mime",
        )
    return ct


def _build_storage_path(filename: str) -> tuple[Path, str]:
    """`UPLOAD_DIR/YYYY/MM/DD/{uuid}-{filename}` üretir; (abs_path, rel_part)."""
    today = datetime.now(timezone.utc)
    rel_dir = Path(str(today.year)) / f"{today.month:02d}" / f"{today.day:02d}"
    file_uuid = uuid.uuid4().hex[:12]
    rel_file = rel_dir / f"{file_uuid}-{filename}"
    abs_path = Path(settings.UPLOAD_DIR).resolve() / rel_file
    return abs_path, str(rel_file).replace("\\", "/")


async def save_upload(
    db: AsyncSession,
    *,
    file: UploadFile,
    kind: str,
    user_id: uuid.UUID,
    organization_id: uuid.UUID | None,
) -> UploadedFile:
    """Yükleme akışı: MIME → boyut → sanitize → disk → DB."""
    content_type = _validate_mime(file.content_type)

    # Akıştan oku, max boyut kontrolü
    max_bytes = settings.max_upload_size_bytes
    chunks: list[bytes] = []
    total = 0
    chunk_size = 64 * 1024
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ValidationError(
                f"Dosya boyutu {settings.MAX_UPLOAD_SIZE_MB} MB sınırını aşıyor",
                code="upload_too_large",
            )
        chunks.append(chunk)
    if total == 0:
        raise ValidationError("Boş dosya yüklenemez", code="upload_empty")

    # Diske yaz
    safe_name = _safe_filename(file.filename or "upload")
    abs_path, rel_path = _build_storage_path(safe_name)
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_bytes(b"".join(chunks))

    public_url = f"{settings.APP_BASE_URL.rstrip('/')}/static/uploads/{rel_path}"

    record = UploadedFile(
        user_id=user_id,
        organization_id=organization_id,
        kind=kind,
        filename=safe_name,
        content_type=content_type,
        size_bytes=total,
        storage_backend="local",
        storage_path=str(abs_path),
        public_url=public_url,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    _logger.info(
        "file_uploaded",
        file_id=str(record.id),
        kind=kind,
        size_bytes=total,
        content_type=content_type,
    )
    return record


async def get_upload(
    db: AsyncSession,
    *,
    file_id: uuid.UUID,
    user_id: uuid.UUID | None,
) -> UploadedFile | None:
    """Tek kayıt; user_id verilirse own kontrolü."""
    record = await db.get(UploadedFile, file_id)
    if record is None:
        return None
    if user_id is not None and record.user_id != user_id:
        return None
    return record
