"""/api/files/upload testleri.

`uploaded_files` tablosu UUID + DateTime kullanıyor — sqlite'da çalışır.
Test ortamında UPLOAD_DIR pytest tmp_path'e yönlendirilir.
"""
from __future__ import annotations

import io
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest_asyncio.fixture
async def files_engine(tmp_path: Path, monkeypatch):
    """uploaded_files dahil sqlite engine + tmp upload dir."""
    monkeypatch.setattr(
        "app.config.settings.UPLOAD_DIR", str(tmp_path / "uploads"), raising=False
    )
    from app.db.base import Base
    from app.db.models.organization import Organization
    from app.db.models.profiles import (
        BuyerProfile,
        ProcessorProfile,
        ProducerProfile,
    )
    from app.db.models.uploaded_file import UploadedFile
    from app.db.models.user import User

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    safe_tables = [
        Organization.__table__,
        User.__table__,
        ProducerProfile.__table__,
        ProcessorProfile.__table__,
        BuyerProfile.__table__,
        UploadedFile.__table__,
    ]
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                sync_conn, tables=safe_tables
            )
        )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def files_session_maker(files_engine):
    return async_sessionmaker(files_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def files_client(files_session_maker):
    from app.db.session import get_db
    from app.main import app

    async def _override():
        async with files_session_maker() as session:
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


async def _token(client: AsyncClient, email: str = "files@test.local") -> str:
    await client.post(
        "/api/auth/register",
        json={"email": email, "password": "supersecret1"},
    )
    r = await client.post(
        "/api/auth/login",
        data={"username": email, "password": "supersecret1"},
    )
    return r.json()["access_token"]


# ============ Pure unit testler ============


def test_safe_filename_strips_path_traversal():
    from app.services.file_service import _safe_filename

    assert _safe_filename("../etc/passwd") == "passwd"
    assert _safe_filename("..\\windows\\system32") == "system32"
    assert _safe_filename("normal.pdf") == "normal.pdf"


def test_safe_filename_strips_unsafe_chars():
    from app.services.file_service import _safe_filename

    assert "<" not in _safe_filename("a<b>c.pdf")
    assert "\x00" not in _safe_filename("null\x00byte.pdf")


def test_safe_filename_falls_back_when_empty():
    from app.services.file_service import _safe_filename

    assert _safe_filename("") == "file"
    assert _safe_filename("...") == "file"


def test_validate_mime_accepts_pdf_jpeg_png():
    from app.services.file_service import _validate_mime

    assert _validate_mime("application/pdf") == "application/pdf"
    assert _validate_mime("image/jpeg") == "image/jpeg"
    assert _validate_mime("image/png") == "image/png"
    # Charset suffix temizlenmeli
    assert _validate_mime("application/pdf; charset=binary") == "application/pdf"


def test_validate_mime_rejects_executable():
    from app.exceptions import ValidationAppError
    from app.services.file_service import _validate_mime

    with pytest.raises(ValidationAppError, match="MIME"):
        _validate_mime("application/x-msdownload")


def test_build_storage_path_uses_yyyy_mm_dd_layout(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "app.config.settings.UPLOAD_DIR", str(tmp_path), raising=False
    )
    from app.services.file_service import _build_storage_path

    abs_path, rel = _build_storage_path("report.pdf")
    parts = rel.split("/")
    assert len(parts) == 4  # YYYY/MM/DD/{uuid}-filename
    assert len(parts[0]) == 4  # year
    assert parts[-1].endswith("report.pdf")
    assert str(tmp_path) in str(abs_path)


# ============ HTTP testleri ============


@pytest.mark.asyncio
async def test_upload_unauthorized_returns_401(files_client):
    response = await files_client.post(
        "/api/files/upload",
        files={"file": ("a.pdf", b"pdfbytes", "application/pdf")},
        data={"kind": "lab_report"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_pdf_201_and_record_persisted(files_client):
    token = await _token(files_client)
    pdf_bytes = b"%PDF-1.4\n%fake\n"
    response = await files_client.post(
        "/api/files/upload",
        files={"file": ("rapor.pdf", pdf_bytes, "application/pdf")},
        data={"kind": "lab_report"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["kind"] == "lab_report"
    assert body["filename"] == "rapor.pdf"
    assert body["content_type"] == "application/pdf"
    assert body["size_bytes"] == len(pdf_bytes)
    assert body["storage_backend"] == "local"
    assert body["url"].endswith(f"-rapor.pdf")

    # GET ile geri okunabilmeli
    detail = await files_client.get(
        f"/api/files/{body['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail.status_code == 200
    assert detail.json()["id"] == body["id"]


@pytest.mark.asyncio
async def test_upload_rejects_invalid_mime(files_client):
    token = await _token(files_client, email="mimerej@test.local")
    response = await files_client.post(
        "/api/files/upload",
        files={"file": ("malware.exe", b"MZ\x90\x00", "application/x-msdownload")},
        data={"kind": "malware"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "upload_invalid_mime"


@pytest.mark.asyncio
async def test_upload_rejects_oversized(files_client, monkeypatch):
    # 1 MB sınırı, 2 MB yükle
    monkeypatch.setattr(
        "app.config.settings.MAX_UPLOAD_SIZE_MB", 1, raising=False
    )
    token = await _token(files_client, email="sizerej@test.local")
    huge = b"\x00" * (2 * 1024 * 1024)
    response = await files_client.post(
        "/api/files/upload",
        files={"file": ("big.pdf", huge, "application/pdf")},
        data={"kind": "lab_report"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "upload_too_large"


@pytest.mark.asyncio
async def test_upload_rejects_empty(files_client):
    token = await _token(files_client, email="empty@test.local")
    response = await files_client.post(
        "/api/files/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
        data={"kind": "lab_report"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "upload_empty"


@pytest.mark.asyncio
async def test_upload_other_user_get_returns_404(files_client):
    """Owner-scope: A user'ın dosyasını B user'ı GET edemez."""
    import uuid as _uuid

    token_a = await _token(files_client, email=f"a_{_uuid.uuid4().hex[:6]}@t.local")
    token_b = await _token(files_client, email=f"b_{_uuid.uuid4().hex[:6]}@t.local")

    upload = await files_client.post(
        "/api/files/upload",
        files={"file": ("secret.pdf", b"%PDF-1.4 secret", "application/pdf")},
        data={"kind": "private"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert upload.status_code == 201
    file_id = upload.json()["id"]

    # B kullanıcısı 404 görmeli (owner-scope)
    other = await files_client.get(
        f"/api/files/{file_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert other.status_code == 404
    assert other.json()["code"] == "file_not_found"
