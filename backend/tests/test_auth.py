"""Auth endpoint testleri — register, login, me, refresh.

Sqlite (aiosqlite) üzerinde koşar; conftest'in `auth_client` fixture'ı
DB dependency'sini override eder.
"""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_register_success(auth_client):
    response = await auth_client.post(
        "/api/auth/register",
        json={"email": "ali@example.com", "password": "supersecret1", "full_name": "Ali Y."},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == "ali@example.com"
    assert body["full_name"] == "Ali Y."
    assert body["role"] == "user"
    assert body["is_active"] is True
    assert "id" in body


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(auth_client):
    payload = {"email": "dup@example.com", "password": "supersecret1"}
    r1 = await auth_client.post("/api/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = await auth_client.post("/api/auth/register", json=payload)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_register_short_password_returns_422(auth_client):
    response = await auth_client.post(
        "/api/auth/register",
        json={"email": "short@example.com", "password": "1234567"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_correct_password(auth_client):
    await auth_client.post(
        "/api/auth/register",
        json={"email": "login@example.com", "password": "supersecret1"},
    )
    response = await auth_client.post(
        "/api/auth/login",
        data={"username": "login@example.com", "password": "supersecret1"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"].count(".") == 2  # JWT
    assert body["refresh_token"]
    assert body["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(auth_client):
    await auth_client.post(
        "/api/auth/register",
        json={"email": "wrong@example.com", "password": "supersecret1"},
    )
    response = await auth_client.post(
        "/api/auth/login",
        data={"username": "wrong@example.com", "password": "different1"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_valid_token(auth_client):
    await auth_client.post(
        "/api/auth/register",
        json={"email": "me@example.com", "password": "supersecret1", "full_name": "Me"},
    )
    login = await auth_client.post(
        "/api/auth/login",
        data={"username": "me@example.com", "password": "supersecret1"},
    )
    token = login.json()["access_token"]

    response = await auth_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["email"] == "me@example.com"
    assert body["full_name"] == "Me"
    assert body["organization"] is None


@pytest.mark.asyncio
async def test_me_without_token_returns_401(auth_client):
    response = await auth_client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_token_returns_401(auth_client):
    response = await auth_client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not.a.valid.jwt"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_issues_new_access(auth_client):
    await auth_client.post(
        "/api/auth/register",
        json={"email": "refresh@example.com", "password": "supersecret1"},
    )
    login = await auth_client.post(
        "/api/auth/login",
        data={"username": "refresh@example.com", "password": "supersecret1"},
    )
    refresh_token = login.json()["refresh_token"]

    response = await auth_client.post(
        "/api/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200, response.text
    body = response.json()
    new_access = body["access_token"]
    assert new_access and new_access.count(".") == 2
    # Yeni access token /me'de doğrulanabilir olmalı.
    me = await auth_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {new_access}"}
    )
    assert me.status_code == 200
    assert me.json()["email"] == "refresh@example.com"


@pytest.mark.asyncio
async def test_refresh_with_access_token_rejected(auth_client):
    """Access token, refresh endpoint'ine geçmemeli (type=access)."""
    await auth_client.post(
        "/api/auth/register",
        json={"email": "swap@example.com", "password": "supersecret1"},
    )
    login = await auth_client.post(
        "/api/auth/login",
        data={"username": "swap@example.com", "password": "supersecret1"},
    )
    access_token = login.json()["access_token"]

    response = await auth_client.post(
        "/api/auth/refresh", json={"refresh_token": access_token}
    )
    assert response.status_code == 401
