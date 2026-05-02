"""Model Evidence service — `models/*.json` dosyalarını birleştirip serve eder.

Public endpoint için tasarlandı (jüri / şeffaflık paneli).
`lru_cache` ile dosyalar bir kez okunur; warmup'tan sonra latency sıfır.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §9.10.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import structlog

from ..config import settings

_logger = structlog.get_logger("evidence_service")


def _models_dir() -> Path:
    """`ML_MODELS_DIR` env'i, yoksa proje root'undaki `models/`."""
    candidate = Path(settings.ML_MODELS_DIR)
    if candidate.exists() and candidate.is_dir():
        return candidate
    # Fallback — backend dev kurulumunda root'tan göreceli yol
    backend_root = Path(__file__).resolve().parents[2]
    project_root = backend_root.parent
    return project_root / "models"


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_evidence() -> dict[str, Any]:
    """`metadata.json` + `model_evidence.json` birleşimini döner."""
    base = _models_dir()
    metadata_path = base / "metadata.json"
    evidence_path = base / "model_evidence.json"

    metadata: dict[str, Any] = {}
    evidence: dict[str, Any] = {}
    if metadata_path.exists():
        metadata = _read_json(metadata_path)
    else:
        _logger.warning("metadata_missing", path=str(metadata_path))
    if evidence_path.exists():
        evidence = _read_json(evidence_path)
    else:
        _logger.warning("model_evidence_missing", path=str(evidence_path))

    return {
        "version": evidence.get("version") or metadata.get("version") or "v1.0",
        "trained_at": evidence.get("trained_at") or metadata.get("trained_at"),
        "metadata": metadata,
        **evidence,
    }


def reset_cache() -> None:
    """Test ve hot-reload için."""
    load_evidence.cache_clear()
