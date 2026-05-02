"""FX endpoint — public (auth gerekmez)."""
from __future__ import annotations

from fastapi import APIRouter

from ..schemas.fx import FxResponse
from ..services.fx_service import get_current_fx

router = APIRouter(prefix="/api/fx", tags=["fx"])


@router.get("/current", response_model=FxResponse)
async def fx_current() -> FxResponse:
    """TCMB EVDS canlı kuru (Redis 5dk TTL cache + fallback)."""
    return await get_current_fx()
