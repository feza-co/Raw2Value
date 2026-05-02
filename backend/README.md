# Raw2Value AI Backend

FastAPI tabanlı backend. ML paketi `raw2value_ml`'i tek satır `import` ile çağırır.

## Hızlı Kurulum (Lokal)

```bash
# Repo root'tan
cp backend/.env.example backend/.env

# ML paketi root'tan editable
pip install -e .

# Backend deps
pip install -r backend/requirements.txt -r backend/requirements-dev.txt

# Sunucuyu başlat
cd backend && uvicorn app.main:app --reload
```

## Docker ile (önerilen)

```bash
cp backend/.env.example backend/.env
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_demo.py
# → http://localhost:8000/docs
```

## Test

```bash
pytest backend/tests/ -v
```

## Yapı

- `app/api/` — FastAPI router'ları
- `app/services/` — İş mantığı (ml_service, fx_service, vb.)
- `app/db/` — SQLAlchemy 2.0 async modelleri ve oturum
- `app/core/` — security, cache, rate limit, middleware
- `app/clients/` — TCMB EVDS, OpenRouteService HTTP client'ları
- `alembic/` — migration'lar

Detay için `MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md` ve `PART2.md`.
