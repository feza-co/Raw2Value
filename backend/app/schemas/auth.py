"""Auth endpoint'leri için pydantic schemas.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md §9.3-9.5.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=200)

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, value: str | EmailStr) -> str:
        return str(value).strip().lower() if value else value


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
    email: EmailStr
    full_name: str | None
    role: str
    is_active: bool
    organization: OrganizationOut | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
