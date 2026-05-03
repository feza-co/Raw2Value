"""Public model evidence endpoint — jüri ve şeffaflık paneli için."""

from typing import Any

from fastapi import APIRouter

from ..services.evidence_service import load_evidence

router = APIRouter(prefix="/api", tags=["evidence"])


@router.get("/model-evidence")
async def model_evidence() -> dict[str, Any]:
    """`models/metadata.json` + `models/model_evidence.json`'u birleşik döner."""
    return load_evidence()
