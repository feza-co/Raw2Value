"""Dosya yükleme response/listing schema'ları.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §9.17.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    id: uuid.UUID
    url: str | None = None
    kind: str
    filename: str
    size_bytes: int
    content_type: str
    organization_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    storage_backend: Literal["local", "s3"] = "local"
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UploadDetail(UploadResponse):
    storage_path: str
