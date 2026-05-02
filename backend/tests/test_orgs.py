"""/api/orgs CRUD testleri."""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture
async def org_client(auth_session_maker):
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


async def _token(client: AsyncClient, email: str = "org@test.local") -> str:
    await client.post(
        "/api/auth/register",
        json={"email": email, "password": "supersecret1"},
    )
    r = await client.post(
        "/api/auth/login",
        data={"username": email, "password": "supersecret1"},
    )
    return r.json()["access_token"]


_PAYLOAD = {
    "name": "Doğa Pomza Ltd",
    "city": "Nevşehir",
    "district": "Acıgöl",
    "country": "TR",
    "lat": 38.55,
    "lon": 34.50,
    "capabilities": {
        "can_supply_raw_material": True,
        "can_export": True,
        "has_storage": True,
        "can_process_material": False,
        "can_buy_material": False,
        "has_transport_capacity": False,
    },
    "producer_profile": {
        "raw_materials": ["pomza"],
        "capacity_ton_year": 30000,
        "quality_grades": ["A", "B"],
    },
}


@pytest.mark.asyncio
async def test_create_org_201(org_client):
    token = await _token(org_client)
    response = await org_client.post(
        "/api/orgs",
        json=_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "Doğa Pomza Ltd"
    assert body["capabilities"]["can_supply_raw_material"] is True
    assert body["producer_profile"]["raw_materials"] == ["pomza"]


@pytest.mark.asyncio
async def test_get_org_after_create(org_client):
    token = await _token(org_client, email="get@test.local")
    create = await org_client.post(
        "/api/orgs",
        json=_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    org_id = create.json()["id"]

    response = await org_client.get(
        f"/api/orgs/{org_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["id"] == org_id


@pytest.mark.asyncio
async def test_list_orgs_capability_filter(org_client):
    token = await _token(org_client, email="filt@test.local")
    await org_client.post(
        "/api/orgs",
        json=_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await org_client.get(
        "/api/orgs?capability=can_supply_raw_material",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total"] >= 1


@pytest.mark.asyncio
async def test_patch_org_updates_capability(org_client):
    token = await _token(org_client, email="patch@test.local")
    create = await org_client.post(
        "/api/orgs",
        json=_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    org_id = create.json()["id"]

    response = await org_client.patch(
        f"/api/orgs/{org_id}",
        json={
            "capabilities": {
                "can_supply_raw_material": True,
                "can_export": True,
                "has_storage": True,
                "can_process_material": True,
                "can_buy_material": False,
                "has_transport_capacity": False,
            }
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["capabilities"]["can_process_material"] is True


@pytest.mark.asyncio
async def test_org_unauthorized_returns_401(org_client):
    response = await org_client.post("/api/orgs", json=_PAYLOAD)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_history_unauthorized_returns_401(org_client):
    """History endpoint authsız 401 döner. Live veri Postgres'te."""
    response = await org_client.get("/api/history")
    assert response.status_code == 401
