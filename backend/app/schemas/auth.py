"""Auth endpoint'leri için pydantic schemas.

Email validasyonu basit regex — `EmailStr` `.local` gibi rezerve TLD'leri
reddediyor; demo/test ortamlarında qa@test.local kullanılabilir olmalı.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md §9.3-9.5.
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=200)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=200)

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("email must be a string")
        norm = value.strip().lower()
        if not _EMAIL_RE.match(norm):
            raise ValueError("Invalid email format")
        return norm


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class CapabilityFlags(BaseModel):
    can_supply_raw_material: bool = False
    can_process_material: bool = False
    can_buy_material: bool = False
    can_export: bool = False
    has_storage: bool = False
    has_transport_capacity: bool = False


class OrganizationOut(BaseModel):
    id: uuid.UUID
    name: str
    capabilities: CapabilityFlags

    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None
    role: str
    is_active: bool
    organization: OrganizationOut | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
