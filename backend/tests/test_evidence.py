"""/api/model-evidence testleri."""
from __future__ import annotations

import pytest

from app.services import evidence_service


@pytest.mark.asyncio
async def test_evidence_endpoint_returns_200(async_client):
    evidence_service.reset_cache()
    response = await async_client.get("/api/model-evidence")
    assert response.status_code == 200
    body = response.json()
    # En az şu alanların biri olmalı (gerçek dosyalardan):
    assert "version" in body
    # ML rapor'undan beklenen anahtarlar
    assert "metadata" in body or "profit_regression" in body or "ablation" in body


@pytest.mark.asyncio
async def test_evidence_lists_best_models():
    evidence_service.reset_cache()
    payload = evidence_service.load_evidence()
    profit = payload.get("profit_regression") or {}
    route = payload.get("route_classification") or {}
    if profit:
        assert profit.get("best_model") == "catboost"
    if route:
        assert route.get("best_model") == "catboost"


@pytest.mark.asyncio
async def test_evidence_endpoint_is_public(async_client):
    """Auth header olmadan da 200 dönmeli."""
    evidence_service.reset_cache()
    response = await async_client.get("/api/model-evidence")
    assert response.status_code == 200
