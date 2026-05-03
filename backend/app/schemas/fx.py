"""FX response schema — `/api/fx/current` ve analyze servisinin paylaştığı tip.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md §9.6.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FxResponse(BaseModel):
    usd_try: float = Field(gt=0)
    eur_try: float = Field(gt=0)
    last_updated: str  # TCMB date (DD-MM-YYYY) ya da ISO; UI tarafı parse eder
    source: Literal["TCMB_EVDS", "FALLBACK"] = "TCMB_EVDS"
    is_stale: bool = False
    fetched_at: datetime
