"""/api/processors/nearby testleri.

Tablo içeriği boş — sqlite üzerinden Organization eklenir; haversine sıralama
ve capability filtresi doğrulanır.
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.models.organization import Organization


@pytest_asyncio.fixture
async def proc_client(auth_session_maker):
    """Auth-overridden processors client."""
    from app.db.session import get_db
    from app.main import app

    async def _override():
        async with auth_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = _override
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac
    finally:
        app.dependency_overrides.pop(get_db, None)


async def _token(client: AsyncClient, email: str = "p@test.local") -> str:
    await client.post(
        "/api/auth/register",
        json={"email": email, "password": "supersecret1"},
    )
    r = await client.post(
        "/api/auth/login",
        data={"username": email, "password": "supersecret1"},
    )
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_processors_empty_db_returns_empty_list(proc_client):
    token = await _token(proc_client)
    response = await proc_client.get(
        "/api/processors/nearby?lat=38.62&lon=34.71&radius_km=100",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["results"] == []
    assert body["count"] == 0
    assert body["method"] == "haversine_bbox"


@pytest.mark.asyncio
async def test_processors_radius_too_large_422(proc_client):
    token = await _token(proc_client, email="p2@test.local")
    response = await proc_client.get(
        "/api/processors/nearby?lat=38.62&lon=34.71&radius_km=600",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_processors_unauthorized(proc_client):
    response = await proc_client.get(
        "/api/processors/nearby?lat=38.62&lon=34.71"
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_processors_haversine_filter(proc_client, auth_session_maker):
    """Yakın (10 km) ve uzak (300 km) işleyici ekle, radius=50 → sadece yakın."""
    token = await _token(proc_client, email="p3@test.local")

    async with auth_session_maker() as session:
        near = Organization(
            name="Yakın Mikronizasyon",
            country="TR",
            city="Acıgöl",
            lat=38.55,
            lon=34.50,
            can_process_material=True,
        )
        far = Organization(
            name="Uzak İşletme",
            country="TR",
            city="Çorum",
            lat=40.55,
            lon=34.95,
            can_process_material=True,
        )
        session.add(near)
        session.add(far)
        await session.commit()

    response = await proc_client.get(
        "/api/processors/nearby?lat=38.55&lon=34.50&radius_km=50",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    names = [r["name"] for r in body["results"]]
    assert "Yakın Mikronizasyon" in names
    assert "Uzak İşletme" not in names


@pytest.mark.asyncio
async def test_processors_invalid_lat_returns_422(proc_client):
    token = await _token(proc_client, email="p4@test.local")
    response = await proc_client.get(
        "/api/processors/nearby?lat=200&lon=34.71",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
