"""UploadedFile ORM modeli — advanced mode lab raporları için audit trail.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §9.17, §13.

MVP: dosyalar `UPLOAD_DIR` altında YYYY/MM/DD/{uuid}-{filename} pattern'ine
yazılır. Tablo metadata + storage path'i tutar; binary'i tutmaz.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(80), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_backend: Mapped[str] = mapped_column(
        String(20), nullable=False, default="local"
    )
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    public_url: Mapped[str | None] = mapped_column(String(500))
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<UploadedFile id={self.id} kind={self.kind!r} "
            f"filename={self.filename!r} size={self.size_bytes}>"
        )
