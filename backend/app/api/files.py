"""/api/files endpoint'leri — advanced mode lab raporu yükleme.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §9.17.
"""

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import User
from ..db.session import get_db
from ..deps import get_current_user
from ..exceptions import NotFoundError
from ..schemas.file_upload import UploadResponse
from ..services import file_service

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dosya yükle (lab raporu / kalite belgesi)",
)
async def upload_file(
    file: UploadFile = File(..., description="Yüklenecek dosya"),
    kind: str = Form(..., max_length=40, description="Örn: lab_report, quality_cert"),
    organization_id: uuid.UUID | None = Form(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    record = await file_service.save_upload(
        db,
        file=file,
        kind=kind,
        user_id=user.id,
        organization_id=organization_id,
    )
    return UploadResponse(
        id=record.id,
        url=record.public_url,
        kind=record.kind,
        filename=record.filename,
        size_bytes=record.size_bytes,
        content_type=record.content_type,
        organization_id=record.organization_id,
        user_id=record.user_id,
        storage_backend=record.storage_backend,
        uploaded_at=record.uploaded_at,
    )


@router.get("/{file_id}", response_model=UploadResponse)
async def get_file(
    file_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    scope_user_id = None if user.role == "admin" else user.id
    record = await file_service.get_upload(
        db, file_id=file_id, user_id=scope_user_id
    )
    if record is None:
        raise NotFoundError("Dosya bulunamadı", code="file_not_found")
    return UploadResponse(
        id=record.id,
        url=record.public_url,
        kind=record.kind,
        filename=record.filename,
        size_bytes=record.size_bytes,
        content_type=record.content_type,
        organization_id=record.organization_id,
        user_id=record.user_id,
        storage_backend=record.storage_backend,
        uploaded_at=record.uploaded_at,
    )
