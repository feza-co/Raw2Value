"""/api/history endpoint + history_service testleri.

`analysis_history` tablosu JSONB ve PgUUID kullandığı için sqlite'da yaratılamaz.
Pure logic + auth davranışı sqlite'ta; tam DB persist `requires_postgres` ile.
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from .conftest import requires_postgres


@pytest_asyncio.fixture
async def history_client(auth_session_maker):
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


async def _token(client: AsyncClient, email: str = "hist@test.local") -> str:
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
async def test_history_list_unauthorized_returns_401(history_client):
    response = await history_client.get("/api/history")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_history_detail_unauthorized_returns_401(history_client):
    response = await history_client.get("/api/history/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_history_list_invalid_page_returns_422(history_client):
    token = await _token(history_client)
    r = await history_client.get(
        "/api/history?page=0",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_history_list_invalid_page_size_returns_422(history_client):
    token = await _token(history_client, email="hsize@test.local")
    r = await history_client.get(
        "/api/history?page=1&page_size=500",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 422


def test_parse_fx_date_handles_tcmb_format():
    from app.services.history_service import _parse_fx_date

    parsed = _parse_fx_date("03-05-2026")
    assert parsed is not None
    assert parsed.year == 2026
    assert parsed.month == 5
    assert parsed.day == 3


def test_parse_fx_date_handles_iso_format():
    from app.services.history_service import _parse_fx_date

    parsed = _parse_fx_date("2026-05-03")
    assert parsed is not None
    assert parsed.year == 2026


def test_parse_fx_date_returns_none_for_garbage():
    from app.services.history_service import _parse_fx_date

    assert _parse_fx_date("not-a-date") is None
    assert _parse_fx_date("") is None


def test_build_record_maps_payload_and_response():
    """build_record() audit trail için tam snapshot tutmalı."""
    import uuid

    from raw2value_ml import AnalyzePayload, AnalyzeResponse, LiveFx, analyze
    from app.schemas.fx import FxResponse
    from app.services.history_service import build_record

    payload = AnalyzePayload(
        raw_material="pomza",
        tonnage=150,
        quality="A",
        origin_city="Nevşehir",
        target_country="DE",
        target_city="Hamburg",
        transport_mode="kara",
        priority="max_profit",
        input_mode="basic",
        live_fx=LiveFx(usd_try=45.0, eur_try=52.0, last_updated="2026-05-03"),
    )
    response: AnalyzeResponse = analyze(payload)
    from datetime import datetime, timezone

    fx = FxResponse(
        usd_try=45.0,
        eur_try=52.0,
        last_updated="2026-05-03",
        source="TCMB_EVDS",
        is_stale=False,
        fetched_at=datetime.now(tz=timezone.utc),
    )
    record = build_record(
        request_id="req_test_1",
        user_id=uuid.uuid4(),
        organization_id=None,
        payload=payload,
        response=response,
        fx=fx,
        duration_ms=42,
    )
    assert record.request_id == "req_test_1"
    assert record.raw_material == "pomza"
    assert record.tonnage == 150
    assert record.recommended_route == response.recommended_route
    assert record.duration_ms == 42
    assert record.usd_try_at_call == 45.0
    assert record.fx_last_updated is not None
    assert isinstance(record.payload_json, dict)
    assert isinstance(record.response_json, dict)


@pytest.mark.asyncio
async def test_history_list_filters_apply_in_service():
    """list_history filtre kombinasyonu — pure service test (mocklu DB)."""
    from datetime import datetime
    from unittest.mock import AsyncMock, MagicMock

    from app.services import history_service

    db = MagicMock()
    db.execute = AsyncMock()

    # Boş sonuç simülasyonu — query inşası çalışıyor mu?
    rows_result = MagicMock()
    rows_result.scalars.return_value.all.return_value = []
    count_result = MagicMock()
    count_result.scalar_one.return_value = 0
    db.execute.side_effect = [rows_result, count_result]

    rows, total = await history_service.list_history(
        db,
        user_id=None,
        page=1,
        page_size=20,
        material="pomza",
        date_from=datetime(2026, 1, 1),
        date_to=datetime(2026, 12, 31),
    )
    assert rows == []
    assert total == 0
    assert db.execute.await_count == 2


# ============ Live Postgres integration ============


@requires_postgres
@pytest.mark.asyncio
async def test_history_persist_and_list_round_trip(pg_db):
    """Postgres'te insert → list → detail tam round-trip."""
    import uuid
    from datetime import datetime, timezone

    from app.db.models import AnalysisRecord, User
    from app.services import history_service

    user = User(
        id=uuid.uuid4(),
        email="histuser@test.local",
        password_hash="x" * 60,
        role="user",
    )
    pg_db.add(user)
    await pg_db.commit()

    record = AnalysisRecord(
        request_id=f"req_{uuid.uuid4().hex[:10]}",
        user_id=user.id,
        organization_id=None,
        raw_material="pomza",
        tonnage=100,
        quality="A",
        origin_city="Nevşehir",
        target_country="DE",
        target_city="Hamburg",
        transport_mode="kara",
        priority="max_profit",
        input_mode="basic",
        fx_scenario_pct=0,
        cost_scenario_pct=0,
        payload_json={"raw_material": "pomza"},
        recommended_route="export_raw_DE",
        expected_profit_try=1_000_000,
        value_uplift_pct=12.5,
        co2_kg=15000,
        confidence_overall=0.85,
        response_json={"recommended_route": "export_raw_DE"},
        usd_try_at_call=45.0,
        eur_try_at_call=52.0,
        fx_last_updated=datetime.now(tz=timezone.utc),
        duration_ms=42,
        model_version="v1.0",
    )
    pg_db.add(record)
    await pg_db.commit()

    rows, total = await history_service.list_history(
        pg_db, user_id=user.id, page=1, page_size=10
    )
    assert total == 1
    assert rows[0].recommended_route == "export_raw_DE"

    fetched = await history_service.get_history(
        pg_db, record_id=rows[0].id, user_id=user.id
    )
    assert fetched is not None
    assert fetched.id == rows[0].id


@requires_postgres
@pytest.mark.asyncio
async def test_history_get_other_user_record_returns_none(pg_db):
    """Owner-scope: başka kullanıcının kaydı user_id filter'da görünmemeli."""
    import uuid

    from app.db.models import AnalysisRecord, User
    from app.services import history_service

    owner = User(
        id=uuid.uuid4(),
        email="owner@test.local",
        password_hash="x" * 60,
        role="user",
    )
    other = User(
        id=uuid.uuid4(),
        email="other@test.local",
        password_hash="x" * 60,
        role="user",
    )
    pg_db.add_all([owner, other])
    await pg_db.commit()

    rec = AnalysisRecord(
        request_id=f"req_{uuid.uuid4().hex[:10]}",
        user_id=owner.id,
        raw_material="pomza",
        tonnage=50,
        quality="B",
        origin_city="Nevşehir",
        target_country="TR",
        transport_mode="kara",
        priority="max_profit",
        input_mode="basic",
        payload_json={},
        recommended_route="domestic_raw",
        response_json={},
    )
    pg_db.add(rec)
    await pg_db.commit()

    # Aynı kayıt admin (user_id=None) için bulunmalı
    found_as_admin = await history_service.get_history(
        pg_db, record_id=rec.id, user_id=None
    )
    assert found_as_admin is not None

    # Diğer user için None dönmeli (own kontrolü)
    not_found = await history_service.get_history(
        pg_db, record_id=rec.id, user_id=other.id
    )
    assert not_found is None
