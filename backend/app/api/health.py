"""Liveness ve readiness endpoint'leri.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md §9.1, §9.2.
"""

import time

from fastapi import APIRouter

from .. import __version__

router = APIRouter(tags=["health"])

_BOOT_TS = time.time()


@router.get("/health")
async def health() -> dict:
    """Basit liveness probe — uptime ve sürüm bilgisi."""
    return {
        "status": "ok",
        "version": __version__,
        "uptime_sec": int(time.time() - _BOOT_TS),
    }
