# RAW2VALUE AI — MASTER BACKEND GELİŞTİRME RAPORU (PART 2/2)

**Versiyon:** v1.0
**Tarih:** 2026-05-03
**Bu dosya:** Bölüm 9.9 → 22 (Kalan endpoint'ler + Operasyon + ROADMAP + Claude Code prompt'ları)
**Önceki dosya:** `MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md` (Bölüm 0 → 9.8)

---

## 9. ENDPOINT SPEC'LERİ — TAM DETAY (2/2 — Processors, Evidence, Orgs, History, Files)

> Bu kısım Part 1'deki §9.1–9.8'in devamıdır. Part 1'de auth, fx, analyze ve what-if endpoint'leri tanımlandı.

### 9.9 `GET /api/processors/nearby` — Bağımsız geo lookup (K3)

**Auth:** Bearer. **Hackathon kuralı K3 uyumu.**

**Query params:**
- `lat` (zorunlu, float) — kullanıcının veya seçilen üreticinin enlemi
- `lon` (zorunlu, float) — boylam
- `radius_km` (default 100, max 500)
- `material` (opsiyonel: `pomza` | `perlit` | `kabak_cekirdegi`) — sadece bu materyali işleyenleri filtrele
- `min_capacity` (opsiyonel, int) — yıllık kapasite alt sınırı

**Response 200:**
```json
{
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "name": "Genper Madencilik A.Ş.",
      "city": "Nevşehir",
      "district": "Acıgöl",
      "lat": 38.62, "lon": 34.71,
      "distance_km": 12.5,
      "processing_routes": ["pomza_micronized_pumice", "pomza_filtration_media"],
      "capacity_ton_year": 50000,
      "certifications": ["ISO9001"],
      "unit_cost_try_per_ton": 850.00,
      "capabilities": {
        "can_process_material": true,
        "has_storage": true,
        "has_transport_capacity": false
      }
    },
    {
      "id": "550e8400-...",
      "name": "Akper A.Ş.",
      "city": "Acıgöl",
      "lat": 38.55, "lon": 34.50,
      "distance_km": 28.3,
      "processing_routes": ["pomza_bims_aggregate"],
      "capacity_ton_year": 30000
    }
  ],
  "count": 2,
  "radius_km": 100,
  "method": "haversine_bbox"
}
```

**Davranış:**
- MVP: bbox + Haversine post-filter (`method: "haversine_bbox"`).
- Advanced: PostGIS `ST_DWithin` aktifse `method: "postgis_geography"`.
- Sıralama: `distance_km` artan.
- Capability filtresi: `can_process_material = TRUE` zorunlu.

**Curl:**
```bash
curl -G "http://localhost:8000/api/processors/nearby" \
  -H "Authorization: Bearer eyJ..." \
  --data-urlencode "lat=38.62" \
  --data-urlencode "lon=34.71" \
  --data-urlencode "radius_km=100" \
  --data-urlencode "material=pomza"
```

**Hatalar:** `422` (`radius_km > 500`), `400` (lat/lon range dışı).

---

### 9.10 `GET /api/model-evidence` — Jüri için public endpoint

**Auth:** Public (jüriye açık). **Cache:** in-memory `lru_cache`, app ömrü.
**Kaynak:** `models/model_evidence.json` + `models/metadata.json`.

**Response 200:**
```json
{
  "version": "v1.0",
  "trained_at": "2026-05-02T20:58:00Z",
  "dataset": {
    "n_total": 1500,
    "splits": { "train": 1200, "val": 150, "test": 150, "seed": 42 },
    "augmentation": "domain_informed_v1",
    "raw_reference_rows": 78
  },
  "profit_regression": {
    "best_model": "catboost",
    "models": {
      "rule_based":         { "rmse": 768082, "mae": 176208, "r2": 0.9998, "mape": 0.04 },
      "linear_regression":  { "rmse": 48849871, "mae": 23153547, "r2": 0.0042, "mape": 1535.15 },
      "random_forest":      { "rmse": 25749650, "mae": 4552738, "r2": 0.7233, "mape": 14.49 },
      "xgboost":            { "rmse": 19632941, "mae": 3141633, "r2": 0.8391, "mape": 13.38 },
      "lightgbm":           { "rmse": 18781529, "mae": 3866058, "r2": 0.8528, "mape": 23.94 },
      "catboost":           { "rmse": 11219334, "mae": 1964460, "r2": 0.9475, "mape": 18.00 }
    }
  },
  "route_classification": {
    "best_model": "catboost",
    "models": {
      "majority_baseline":  { "accuracy": 0.667, "macro_f1": 0.100, "weighted_f1": 0.533 },
      "logistic_regression":{ "accuracy": 0.880, "macro_f1": 0.587, "weighted_f1": 0.869, "top2_accuracy": 0.960 },
      "random_forest":      { "accuracy": 0.973, "macro_f1": 0.698, "weighted_f1": 0.963, "top2_accuracy": 0.993 },
      "catboost":           { "accuracy": 0.953, "macro_f1": 0.782, "weighted_f1": 0.962, "top2_accuracy": 0.987 }
    }
  },
  "ablation": {
    "full_features":   { "rmse": 11267473, "rmse_delta_pct":  0.00 },
    "without_fx":      { "rmse":  3823200, "rmse_delta_pct": -66.07 },
    "without_geo":     { "rmse":  4905337, "rmse_delta_pct": -56.46 },
    "without_carbon":  { "rmse":  5384593, "rmse_delta_pct": -52.21 },
    "without_demand":  { "rmse": 12338203, "rmse_delta_pct": +9.50 }
  },
  "feature_importance": {
    "model_profit": [
      { "feature": "total_distance_km", "importance": 0.342 },
      { "feature": "usd_try", "importance": 0.211 }
    ],
    "model_route": [
      { "feature": "raw_material", "importance": 0.405 },
      { "feature": "buyer_country", "importance": 0.198 }
    ]
  },
  "rule_compliance": {
    "K1_carbon": { "status": "PASS", "evidence": "compute_co2() 4 mod sabit faktörlerle" },
    "K2_fx":     { "status": "PASS", "evidence": "ablation without_fx rmse_delta_pct=-66.07" },
    "K3_geo":    { "status": "PASS", "evidence": "geo.py ORS-precomputed lookup + Haversine fallback" }
  },
  "honesty_note": "1500 satırlık sentetik veride bazı feature'ların ablation deltası negatif yönde (overfit sinyali). Pilot gerçek veri ile yeniden kalibrasyon planlandı."
}
```

**Curl:** `curl http://localhost:8000/api/model-evidence | jq .`

---

### 9.11 `POST /api/orgs` — Organization oluştur

**Auth:** Bearer. **İzin:** Authenticated user (kendi orgunu açar; user.organization_id ile bağlanır).

**Body:**
```json
{
  "name": "Doğa Pomza Ltd",
  "city": "Nevşehir",
  "district": "Acıgöl",
  "country": "TR",
  "lat": 38.55,
  "lon": 34.50,
  "capabilities": {
    "can_supply_raw_material": true,
    "can_export": true,
    "has_storage": true,
    "can_process_material": false,
    "can_buy_material": false,
    "has_transport_capacity": false
  },
  "producer_profile": {
    "raw_materials": ["pomza"],
    "capacity_ton_year": 30000,
    "quality_grades": ["A", "B"]
  },
  "processor_profile": null,
  "buyer_profile": null
}
```

**Response 201:**
```json
{
  "id": "550e8400-...",
  "name": "Doğa Pomza Ltd",
  "city": "Nevşehir", "district": "Acıgöl", "country": "TR",
  "lat": 38.55, "lon": 34.50,
  "capabilities": { ... },
  "producer_profile": { ... },
  "created_at": "2026-05-03T12:00:00Z"
}
```

> Capability flag aynı org için birden fazla TRUE olabilir → user aynı kayıt altında hem `producer_profile` hem `processor_profile` doldurabilir (`raw2value_revised.md` §3.2 capability modeli).

### 9.12 `GET /api/orgs/{id}` — Organization detay
**Auth:** Bearer. **Response:** OrgOut (yukarıdaki şema).

### 9.13 `PATCH /api/orgs/{id}` — Güncelleme
**İzin:** Sahip user veya admin. Capability flag'leri güncellenebilir; profile alanları nested patch.

### 9.14 `GET /api/orgs` — Filtreli listeleme

**Query params:**
- `capability` (opsiyonel: `can_process_material` vb.)
- `material` (opsiyonel — processor için processing_routes içinde search)
- `city` / `country`
- `page` (default 1) / `page_size` (default 20, max 100)

**Response 200 (paginated):**
```json
{
  "items": [ { /* OrgOut */ }, ... ],
  "page": 1,
  "page_size": 20,
  "total": 47,
  "total_pages": 3
}
```

### 9.15 `GET /api/history` — Kullanıcının analiz geçmişi

**Auth:** Bearer. **Scope:** Sadece `user_id == current_user.id` kayıtları (admin tüm veriyi görür).

**Query params:**
- `page=1&page_size=20`
- `material=pomza` (opsiyonel filtre)
- `from=2026-05-01T00:00:00Z` (opsiyonel tarih aralığı)
- `to=2026-05-03T23:59:59Z`

**Response 200:**
```json
{
  "items": [
    {
      "id": 123,
      "request_id": "req_01HX2...",
      "created_at": "2026-05-03T12:00:00Z",
      "raw_material": "pomza",
      "tonnage": 150,
      "quality": "A",
      "origin_city": "Nevşehir",
      "target_country": "DE",
      "transport_mode": "kara",
      "recommended_route": "pomza_micronized_pumice",
      "expected_profit_try": 1425000.50,
      "value_uplift_pct": 4.85,
      "co2_kg": 37542.0,
      "confidence_overall": 83.5,
      "duration_ms": 28
    }
  ],
  "page": 1, "page_size": 20, "total": 47, "total_pages": 3
}
```

### 9.16 `GET /api/history/{id}` — Tek kayıt detayı
Tüm `payload_json` + `response_json` döner (frontend "Detail / Re-run" ekranı için).

### 9.17 `POST /api/files/upload` (opsiyonel — advanced mode lab raporu)

**Auth:** Bearer. **Content-Type:** `multipart/form-data`.
**Form fields:** `file=@labreport.pdf`, `kind=lab_report`, `organization_id=uuid`.
**Limits:** 10 MB max, MIME beyaz liste (`application/pdf`, `image/jpeg`, `image/png`).

**Response 201:**
```json
{
  "id": "uuid",
  "url": "http://minio:9000/raw2value-uploads/2026/05/03/labreport_xyz.pdf",
  "kind": "lab_report",
  "filename": "labreport.pdf",
  "size_bytes": 287654,
  "content_type": "application/pdf",
  "organization_id": "uuid",
  "uploaded_at": "2026-05-03T12:30:00Z"
}
```

**Davranış:**
- `S3_ENABLED=true` → MinIO'ya yükle, presigned URL döndür.
- `S3_ENABLED=false` → `/var/raw2value/uploads/YYYY/MM/DD/{uuid}-{filename}` lokal FS'ye düşer; URL `${APP_BASE_URL}/static/uploads/...`.

---

## 10. EXTERNAL SERVICES — CLIENT TASARIMI

### 10.1 TCMB EVDS client (`app/clients/tcmb.py`)

```python
import httpx
from datetime import datetime, timedelta, timezone
from tenacity import retry, stop_after_attempt, wait_exponential

class TcmbClient:
    def __init__(self, api_key: str, base_url: str, timeout: float):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=timeout)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=0.5, max=4))
    async def get_fx(self) -> dict:
        today = datetime.now(timezone.utc).strftime("%d-%m-%Y")
        last_week = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%d-%m-%Y")
        params = {
            "series": "TP.DK.USD.A.YTL-TP.DK.EUR.A.YTL",
            "startDate": last_week,
            "endDate": today,
            "type": "json",
            "key": self.api_key,
        }
        r = await self.client.get(f"{self.base_url}/series", params=params)
        r.raise_for_status()
        data = r.json()
        last = data["items"][-1]  # en yeni gün
        return {
            "usd_try": float(last["TP_DK_USD_A_YTL"]),
            "eur_try": float(last["TP_DK_EUR_A_YTL"]),
            "last_updated": last["Tarih"],
        }
```

**Hata stratejisi:**
1. 3 deneme (exponential backoff 0.5–4 s).
2. 3'ü de fail → fallback (env'den son bilinen değer + `is_stale=true`).
3. Sentry'ye warning log.

### 10.2 ORS client (`app/clients/ors.py`)

```python
class OrsClient:
    async def matrix(
        self,
        locations: list[tuple[float, float]],
        profile: str = "driving-hgv",
    ) -> dict:
        # locations: [(lon, lat), ...] — DİKKAT: ORS sırası (lon, lat)!
        ...
```

**Cache key:** `ors:{profile}:{hash(locations)}`, TTL 1 saat.

**Fallback:** ORS down → ML paketinin `geo.py` lookup table + Haversine fallback'i devreye girer (zaten yapıyor). Backend tarafında ORS opsiyonel.

---

## 11. CACHE STRATEJİSİ — REDIS LAYOUT

| Key prefix | Value | TTL | Sebep |
|---|---|---:|---|
| `fx:current` | `{usd_try, eur_try, last_updated, fetched_at}` | 5 dk | TCMB günde güncellenir; 5 dk yeterli |
| `ors:matrix:{hash}` | distances JSON | 1 saat | Mesafeler değişmez |
| `analyze:{hash(payload)}` | response JSON | 5 dk | What-if slider ardışık aynı çağrı |
| `evidence:json` | model_evidence.json | 1 gün | Yeniden eğitime kadar değişmez |
| `ratelimit:user:{id}:analyze` | sayaç | 1 dk | Rate limit window |
| `auth:refresh:{jti}` | user_id | 14 gün | Refresh token allow-list |

**Connection pool:** Redis için `max_connections=20`. async client (`redis.asyncio`).

---

## 12. ASYNC TASK QUEUE — KARARI

**Karar: Celery / RQ MVP'DE GEREKMİYOR.**

**Gerekçe:**
- `analyze()` warm latency 20 ms — request içinde tamamlanır.
- TCMB/ORS çağrıları `httpx async` ile event loop'ta non-blocking.
- DB insert'leri (`history_service.save`) `asyncio.create_task(...)` ile fire-and-forget yapılabilir (response gönderildikten sonra çalışır).

**Future (advanced) — Celery gereken durumlar:**
- Lab report PDF parsing (pdfplumber + OCR; saniyeler sürebilir).
- Toplu CSV upload + 1000 satır analiz.
- Model retraining trigger.

Bu özellikleri MVP'ye dahil etmiyoruz; future faza Celery + Redis broker eklenebilir. Backend kodu hazırlığı: `services/` katmanı zaten async; Celery task'a geçiş 1 saatte yapılır.

---

## 13. DOSYA YÜKLEME — STRATEJİ

**MVP karar:** `S3_ENABLED=false` → local FS (`/var/raw2value/uploads/`). Bu yeterli; demo'da bir lab raporu yüklersek görünür.

**Advanced:** `S3_ENABLED=true` → MinIO (docker-compose'da hazır). boto3 client.

```python
async def save_file(file: UploadFile, kind: str, org_id: UUID) -> str:
    if settings.S3_ENABLED:
        return await s3_upload(file, kind, org_id)
    return await local_upload(file, kind, org_id)
```

**Güvenlik:**
- Max boyut: 10 MB (`max_upload_size` middleware).
- MIME beyaz liste: `application/pdf`, `image/jpeg`, `image/png`.
- Filename sanitize (path traversal koru: `secure_filename(...)`).
- Virus scan: hackathon kapsamı dışı; future ClamAV.

---

## 14. LOGGING + MONITORING + ERROR TRACKING

### 14.1 Structlog konfigürasyonu

```python
# backend/app/logging.py
import structlog, logging, sys

def configure_logging(level: str = "INFO", as_json: bool = True):
    logging.basicConfig(stream=sys.stdout, level=level, format="%(message)s")
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer() if as_json else structlog.dev.ConsoleRenderer(),
    ]
    structlog.configure(processors=processors, wrapper_class=structlog.make_filtering_bound_logger(level))
```

### 14.2 Request ID middleware

```python
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or f"req_{uuid7()}"
    structlog.contextvars.bind_contextvars(request_id=rid, path=request.url.path, method=request.method)
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = int((time.perf_counter() - start) * 1000)
    logger.info("http_request", status=response.status_code, duration_ms=duration_ms)
    response.headers["X-Request-ID"] = rid
    return response
```

### 14.3 Sentry (opsiyonel)

`SENTRY_DSN` set edilmişse aktif. Her exception otomatik gönderilir; PII filtresi (`send_default_pii=False`).

```python
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=False,
        environment=settings.APP_ENV,
    )
```

### 14.4 Prometheus metrics

`/metrics` endpoint, default histogram'lar:
- `http_requests_total{method,path,status}`
- `http_request_duration_seconds`
- Custom: `analyze_inference_duration_ms`, `tcmb_fx_cache_hit_total`, `ors_call_total`.

### 14.5 Log örneği (JSON)

```json
{
  "timestamp": "2026-05-03T12:00:01.234Z",
  "level": "info",
  "event": "http_request",
  "request_id": "req_01HX2...",
  "method": "POST",
  "path": "/api/analyze",
  "status": 200,
  "duration_ms": 28,
  "user_id": "uuid",
  "raw_material": "pomza",
  "recommended_route": "pomza_micronized_pumice"
}
```

---

## 15. RATE LIMITING & SECURITY KATMANLARI

### 15.1 Rate limit (slowapi)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)
app.state.limiter = limiter

@router.post("/analyze")
@limiter.limit(settings.RATE_LIMIT_ANALYZE)
async def analyze_endpoint(...): ...
```

Auth'lu endpoint'lerde `key_func` user_id'ye göre değişir.

### 15.2 Güvenlik checklist

- ✅ **HTTPS** — Reverse proxy (Caddy/Nginx) tarafında. Backend HTTP konuşur, X-Forwarded-Proto okur.
- ✅ **CORS** — `CORS_ORIGINS` env'den whitelist; `*` asla kullanılmaz.
- ✅ **Security headers** — middleware: `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`.
- ✅ **SQL injection** — SQLAlchemy parametrik query'leri zaten korur. Raw SQL yok.
- ✅ **JWT secret** — env'den, min 32 char rastgele.
- ✅ **bcrypt rounds** — 12 (dengeli).
- ✅ **Pydantic strict** — `extra=forbid`; ekstra alan reddedilir.
- ✅ **Request size limit** — `LimitUploadSize` middleware: 10 MB.
- ✅ **Login throttle** — `RATE_LIMIT_AUTH_LOGIN=10/minute`.
- ✅ **Secrets** — `.env` git'e gitmez; CI'da GitHub Secrets.
- ✅ **DB connection** — read-only kullanıcı analytics endpoint'leri için (future).

### 15.3 Custom exception handler (RFC 7807)

```python
@app.exception_handler(RequestValidationError)
async def validation_handler(request, exc):
    return JSONResponse(status_code=422, content={
        "type": "https://raw2value.ai/errors/validation",
        "title": "Validation Error",
        "status": 422,
        "detail": exc.errors(),
        "instance": str(request.url),
        "request_id": structlog.contextvars.get_contextvars().get("request_id"),
    })
```

---

## 16. DEPLOYMENT — DOCKER + DOCKER-COMPOSE + CI/CD

### 16.1 `backend/Dockerfile` (multi-stage)

```dockerfile
# ---- builder ----
FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt

# ---- runtime ----
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/*.whl

# ML paketi + artefactler
COPY raw2value_ml /app/raw2value_ml
COPY models /app/models
COPY data /app/data
COPY backend/pyproject.toml /app/pyproject.toml
RUN pip install -e .

# Backend kodu
COPY backend/app /app/app
COPY backend/alembic /app/alembic
COPY backend/alembic.ini /app/alembic.ini
COPY backend/scripts /app/scripts

RUN useradd -m -u 1000 app && chown -R app:app /app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python scripts/healthcheck.py
CMD ["gunicorn","app.main:app","-k","uvicorn.workers.UvicornWorker","-w","1","-b","0.0.0.0:8000","--access-logfile","-","--error-logfile","-"]
```

### 16.2 `docker-compose.yml`

```yaml
version: "3.9"
services:
  api:
    build:
      context: .
      dockerfile: backend/Dockerfile
    env_file: ./backend/.env
    ports:
      - "8000:8000"
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_started }
    restart: unless-stopped

  db:
    image: postgis/postgis:16-3.4-alpine
    environment:
      POSTGRES_USER: raw2value
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: raw2value
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U raw2value"]
      interval: 5s
      timeout: 5s
      retries: 5
    ports: ["5432:5432"]

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports: ["6379:6379"]

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    ports: ["9000:9000","9001:9001"]
    profiles: ["full"]   # docker compose --profile full up

volumes:
  db_data:
  redis_data:
  minio_data:
```

### 16.3 `.github/workflows/ci.yml`

```yaml
name: CI
on: [push, pull_request]
jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:16-3.4-alpine
        env: { POSTGRES_USER: test, POSTGRES_PASSWORD: test, POSTGRES_DB: test }
        ports: ["5432:5432"]
        options: --health-cmd="pg_isready -U test"
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -e . -r backend/requirements.txt -r backend/requirements-dev.txt
      - run: ruff check backend/
      - run: pytest backend/tests/ -v --cov=backend/app --cov-report=term-missing
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0
          JWT_SECRET: test-secret-min-32-chars-needed-here
          TCMB_EVDS_API_KEY: dummy
          ORS_API_KEY: dummy
```

### 16.4 Tek komutla başlatma

```bash
cp backend/.env.example backend/.env
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_demo.py
# API: http://localhost:8000/docs
```

---

## 17. TEST STRATEJİSİ

| Tür | Araç | Hedef |
|---|---|---|
| Unit | pytest | Her service fonksiyonu — TCMB parser, distance calc, JWT decode |
| Integration | pytest + httpx.AsyncClient | Endpoint'ler + DB + Redis (test container) |
| Contract | pytest | `analyze()` ML çıktısının `AnalyzeResponse` şemasına uyduğunu doğrula |
| Load (opsiyonel) | k6 / locust | `/api/analyze` p95 ölçüm |

**Coverage hedef:** %75 (services + api). MVP'de %60 yeterli.

**conftest.py temel fixture'lar:** `async_client`, `test_db` (transactional rollback), `test_user`, `auth_token`, `mock_tcmb` (respx), `mock_ors` (respx).

---

## 18. ROADMAP — ADIM ADIM CLAUDE CODE PROMPTLARI

> **Tahmini süre:** 8–10 saat (paralel 2 kişi: Backend Lead + Backend Support).
> **Ön koşul:** ML pipeline tamamlanmış (88/88 PASS), `models/` ve `raw2value_ml/` mevcut.
> **Kural:** Her commit atomic + Türkçe başlık + Claude imzası YOK (`commit-discipline.md`).

---

### ADIM 0 — Backend iskeleti (30 dk)

**📋 CLAUDE CODE PROMPT:**

````markdown
🎯 ROL: Backend mühendisi. Raw2Value AI projesinde backend dizinini sıfırdan kuruyorsun.

📁 GİRDİ:
- Proje root'unda zaten `raw2value_ml/`, `models/`, `data/` var (ML ekibi teslim etti).
- `commit-discipline.md` mevcut: atomic + sade Türkçe + Claude imzası YOK.
- `MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md` Bölüm 3 (klasör yapısı), §4 (deps), §5 (.env).

📤 ÇIKTI:
- backend/ dizininde tam klasör tree (boş `__init__.py`'lar)
- backend/pyproject.toml
- backend/requirements.txt (rapor §4.1 ile birebir)
- backend/requirements-dev.txt
- backend/.env.example (rapor §5)
- backend/.dockerignore
- backend/.gitignore (.env, __pycache__, .pytest_cache, .coverage)
- backend/README.md (kurulum 10 satır)
- backend/pytest.ini

🛠️ GÖREV:
1. `mkdir -p backend/app/{api,schemas,services,db/models,core,clients}` ile tüm klasörleri yarat
2. Her klasöre `__init__.py` koy (boş)
3. pyproject.toml'a `[tool.ruff]` + `[tool.pytest.ini_options]` + raw2value-ml editable dep ekle
4. requirements.txt'i raporun §4.1'inden tam kopyala
5. .env.example'ı raporun §5'inden kopyala (gerçek secret YOK)
6. README.md kısa: "Kurulum: pip install -e . -r backend/requirements.txt; uvicorn app.main:app"

⚠️ DİKKAT:
- Henüz kod yazmıyoruz; sadece iskelet ve dosya
- Hiçbir gerçek API key yazma; example'da placeholder kalsın
- backend/app/main.py'a basit bir `app = FastAPI(title="Raw2Value AI")` koy ki `pip install -e .` patlamasın

✅ KABUL KRİTERLERİ:
- `cd backend && pip install -e . -r requirements.txt` hatasız çalışır
- `uvicorn app.main:app` 8000 portunda boş bir app açar (404 olur ama crash etmez)
- `pytest backend/tests/` 0 test bulur ama hatasız çalışır
- Commit: `add: backend iskeleti ve bagimliliklar`
````

---

### ADIM 1 — Config + Logging + Exceptions (45 dk)

**📋 CLAUDE CODE PROMPT:**

````markdown
🎯 ROL: Backend mühendisi. Config, logging ve exception altyapısını kuruyorsun.

📁 GİRDİ: ADIM 0 çıktısı + raporun §5 (env), §14 (logging), §15.3 (exception handler).

📤 ÇIKTI:
- backend/app/config.py — pydantic-settings ile tüm env değişkenleri
- backend/app/logging.py — structlog konfigürasyon
- backend/app/exceptions.py — custom exception sınıfları + handler'lar
- backend/app/core/middleware.py — RequestID + AccessLog middleware
- backend/app/main.py — app oluştur, lifespan placeholder, middleware'ları mount et
- backend/app/api/health.py — /health, /readiness
- backend/tests/test_health.py — `/health` testi

🛠️ GÖREV:

config.py:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "raw2value-ai-backend"
    APP_ENV: str = "development"
    JWT_SECRET: str
    DATABASE_URL: str
    REDIS_URL: str
    ML_MODELS_DIR: str = "/app/models"
    ML_WARMUP_ON_STARTUP: bool = True
    TCMB_EVDS_API_KEY: str = ""
    TCMB_EVDS_BASE_URL: str = "https://evds2.tcmb.gov.tr/service/evds"
    TCMB_FX_CACHE_TTL_SEC: int = 300
    TCMB_FALLBACK_USD_TRY: float = 45.0
    TCMB_FALLBACK_EUR_TRY: float = 52.0
    ORS_API_KEY: str = ""
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    CORS_ORIGINS: str = "http://localhost:3000"
    RATE_LIMIT_ENABLED: bool = True
    # ... rapor §5'teki tüm alanlar

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

settings = Settings()
```

logging.py: rapor §14.1 birebir.

exceptions.py:
- `AppException(status_code, code, message)`
- `NotFoundError`, `ValidationAppError`, `AuthError`, `RateLimitError`
- `register_exception_handlers(app)` — RFC 7807 formatında JSON döner

middleware.py:
- `RequestIdMiddleware` — `X-Request-ID` üret/propagate, structlog contextvars'a bind
- `AccessLogMiddleware` — duration_ms + status logla

main.py:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from .config import settings
from .logging import configure_logging
from .exceptions import register_exception_handlers
from .core.middleware import RequestIdMiddleware, AccessLogMiddleware
from .api import health

configure_logging(level=settings.LOG_LEVEL, as_json=(settings.LOG_FORMAT == "json"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ML / DB / Redis init buraya gelecek (sonraki adımlar)
    yield

app = FastAPI(title="Raw2Value AI", version="0.1.0", lifespan=lifespan,
              default_response_class=ORJSONResponse)

app.add_middleware(CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AccessLogMiddleware)
app.add_middleware(RequestIdMiddleware)
register_exception_handlers(app)

app.include_router(health.router)
```

api/health.py:
```python
from fastapi import APIRouter
router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
```

test_health.py:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
```

⚠️ DİKKAT:
- pydantic v2 kullan (BaseSettings pydantic-settings'ten import)
- ORJSONResponse default — Türkçe karakterler escape edilmesin
- CORS_ORIGINS string env'den geliyor; comma-split ile listeye çevir

✅ KABUL KRİTERLERİ:
- `pytest backend/tests/test_health.py -v` PASS
- `curl http://localhost:8000/health` → `{"status":"ok","version":"0.1.0"}`
- Log JSON formatında ve `request_id` içeriyor
- 3 atomic commit: `add: config ve logging altyapisi`, `add: exception handlerlari`, `add: health endpoint ve middleware`
````

---

### ADIM 2 — Database katmanı + Alembic (1 saat)

**📋 CLAUDE CODE PROMPT:**

````markdown
🎯 ROL: Backend mühendisi. SQLAlchemy 2.0 async + Alembic kuruyor, capability-based modeli yazıyorsun.

📁 GİRDİ: Rapor §6 (database şeması), `raw2value_revised.md` §9.6.

📤 ÇIKTI:
- backend/app/db/base.py — DeclarativeBase + Naming convention
- backend/app/db/session.py — async_engine, async_session_maker, get_db dependency
- backend/app/db/models/user.py — User model
- backend/app/db/models/organization.py — Organization (capability flags)
- backend/app/db/models/profiles.py — ProducerProfile / ProcessorProfile / BuyerProfile
- backend/app/db/models/analysis.py — AnalysisRecord (rapor §6.3)
- backend/alembic/env.py + alembic.ini
- backend/alembic/versions/0001_initial.py
- backend/alembic/versions/0002_analysis_history.py
- backend/tests/conftest.py — test_db fixture (transactional rollback)

🛠️ GÖREV:

base.py:
```python
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

NAMING = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING)
```

session.py:
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import settings

engine = create_async_engine(settings.DATABASE_URL, pool_size=10, max_overflow=5, echo=settings.DATABASE_ECHO)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
```

models/organization.py — rapor §6.2 birebir; PostGIS geom kolonu opsiyonel ALTER ile sonradan.

Alembic env.py:
- async engine kullanmak için `run_async_migrations` pattern
- target_metadata = Base.metadata (tüm modeller import edilmiş olmalı)

0001_initial.py: users + organizations + 3 profile tablosu (rapor §6.2 SQL).
0002_analysis_history.py: analysis_history (rapor §6.3 SQL).

conftest.py:
```python
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import engine, SessionLocal
from app.db.base import Base

@pytest_asyncio.fixture
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

⚠️ DİKKAT:
- UUID primary key: `Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))`
- pgcrypto extension gerekli; migration'ın başına `op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")` ekle
- `analysis_history.payload_json` JSONB; SQLAlchemy `from sqlalchemy.dialects.postgresql import JSONB`
- PostGIS migration'ı şimdilik YAZMA — opsiyonel, sonraki adımda ele alınacak

✅ KABUL KRİTERLERİ:
- `alembic upgrade head` Postgres'te tabloları oluşturur, hata vermez
- `alembic downgrade base` temiz geri alır
- `pytest backend/tests/` test_db fixture ile çalışır (geçici DB tablo yaratır, drop eder)
- 3 atomic commit: `add: db base ve session`, `add: capability based organization modeli`, `add: alembic ile initial migration`
````

---

### ADIM 3 — Auth katmanı (45 dk)

**📋 CLAUDE CODE PROMPT:**

````markdown
🎯 ROL: Backend mühendisi. JWT + bcrypt auth katmanını kuruyorsun.

📁 GİRDİ: ADIM 2 çıktısı + rapor §8 (auth) + §9.3-9.5 (auth endpoint'leri).

📤 ÇIKTI:
- backend/app/core/security.py — `hash_password`, `verify_password`, `create_access_token`, `decode_token`
- backend/app/services/auth_service.py — register, login fonksiyonları
- backend/app/schemas/auth.py — RegisterRequest, LoginRequest, TokenResponse, UserOut
- backend/app/api/auth.py — `/api/auth/register`, `/login`, `/me`, `/refresh`
- backend/app/deps.py — `get_current_user`, `require_admin`
- backend/tests/test_auth.py — register + login + me + invalid token testleri

🛠️ GÖREV:

security.py:
```python
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from .config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.PASSWORD_HASH_ROUNDS)

def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_access_token(sub: str, extra: dict | None = None, ttl_min: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl_min or settings.JWT_ACCESS_TTL_MIN)).timestamp()),
        **(extra or {}),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise AuthError(str(e))
```

deps.py:
```python
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)) -> User:
    payload = decode_token(token)
    user = await db.get(User, UUID(payload["sub"]))
    if not user or not user.is_active:
        raise AuthError("Invalid credentials")
    return user
```

api/auth.py:
- `POST /register`: email unique check → hash_password → User insert → 201
- `POST /login`: OAuth2PasswordRequestForm → verify → access + refresh token → 200
- `GET /me`: Depends(get_current_user) → UserOut
- `POST /refresh`: refresh_token verify → yeni access_token

test_auth.py:
- test_register_success
- test_register_duplicate_email_409
- test_login_correct_password
- test_login_wrong_password_401
- test_me_with_valid_token
- test_me_without_token_401

⚠️ DİKKAT:
- Password min 8 char: pydantic field validator
- Email lowercased + stripped
- Refresh token Redis allow-list'te saklanmalı (logout için) — MVP'de skip, sadece JWT
- JWT secret env'den, test'te override

✅ KABUL KRİTERLERİ:
- `pytest backend/tests/test_auth.py -v` PASS
- `curl -X POST localhost:8000/api/auth/register -H "Content-Type: application/json" -d '{"email":"a@b.com","password":"12345678","full_name":"Ali"}'` → 201
- 4 atomic commit: `add: jwt ve bcrypt security helperlari`, `add: auth servis ve schemalar`, `add: auth endpointleri`, `add: auth testleri`
````

---

### ADIM 4 — Redis cache + TCMB EVDS client + `/api/fx/current` (1 saat)

**📋 CLAUDE CODE PROMPT:**

````markdown
🎯 ROL: Backend mühendisi. Redis cache, TCMB EVDS client ve `/api/fx/current` endpoint'ini yazıyorsun.

📁 GİRDİ: Rapor §10.1 (TCMB client), §11 (cache layout), §9.6 (fx endpoint).

📤 ÇIKTI:
- backend/app/core/cache.py — Redis async client + `cached` decorator
- backend/app/clients/tcmb.py — TcmbClient (httpx + tenacity retry)
- backend/app/services/fx_service.py — get_current_fx (cache + fallback)
- backend/app/schemas/fx.py — FxResponse
- backend/app/api/fx.py — `/api/fx/current`
- backend/tests/test_fx.py — TCMB mock + cache hit/miss + fallback testleri
- backend/tests/fixtures/tcmb_response.json — örnek TCMB response

🛠️ GÖREV:

cache.py:
```python
import redis.asyncio as redis
from .config import settings

_redis: redis.Redis | None = None

async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.REDIS_URL, max_connections=settings.REDIS_POOL_SIZE, decode_responses=True)
    return _redis

async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None
```

clients/tcmb.py:
- httpx.AsyncClient timeout=10
- @tenacity.retry stop=3, wait=exponential(0.5,4)
- TCMB EVDS endpoint: rapor §10.1 query string
- response içindeki `items[-1]` en yeni gün
- USD: TP_DK_USD_A_YTL (alış); EUR: TP_DK_EUR_A_YTL

services/fx_service.py:
```python
async def get_current_fx() -> FxResponse:
    r = await get_redis()
    cached = await r.get("fx:current")
    if cached:
        return FxResponse.model_validate_json(cached)
    try:
        data = await tcmb_client.get_fx()
        out = FxResponse(**data, source="TCMB_EVDS", is_stale=False, fetched_at=now())
    except Exception as e:
        logger.warning("tcmb_fallback", error=str(e))
        out = FxResponse(usd_try=settings.TCMB_FALLBACK_USD_TRY,
                         eur_try=settings.TCMB_FALLBACK_EUR_TRY,
                         last_updated=date.today().isoformat(),
                         source="FALLBACK", is_stale=True, fetched_at=now())
    await r.setex("fx:current", settings.TCMB_FX_CACHE_TTL_SEC, out.model_dump_json())
    return out
```

api/fx.py:
```python
@router.get("/api/fx/current", response_model=FxResponse)
async def fx_current():
    return await get_current_fx()
```

test_fx.py:
- test_fx_cache_hit (Redis'e önceden set, TCMB call yok)
- test_fx_cache_miss_calls_tcmb (respx ile mock)
- test_fx_tcmb_down_returns_fallback
- test_fx_response_shape

⚠️ DİKKAT:
- TCMB date format: DD-MM-YYYY (US değil)
- Hafta sonu/tatil → endDate aynı, ama items uzunluğu değişir; defansif son element al
- Redis cache key SADECE `fx:current` (tek key, global)
- Fallback değeri kullanılırsa Sentry'ye warning

✅ KABUL KRİTERLERİ:
- `curl localhost:8000/api/fx/current` → 200 ile JSON döner
- İlk çağrı miss, ikinci çağrı hit (Redis'te `fx:current` görünür: `redis-cli GET fx:current`)
- TCMB mock fail → fallback kullanılır
- 4 atomic commit: `add: redis async client`, `add: tcmb evds httpx clienti`, `add: fx servisi ve cache`, `add: fx endpoint ve testleri`
````

---

### ADIM 5 — ML servisi + `/api/analyze` (1.5 saat) — KRİTİK

**📋 CLAUDE CODE PROMPT:**

````markdown
🎯 ROL: Backend mühendisi. ML paketini servis edip `/api/analyze` endpoint'ini hayata geçiriyorsun. BU EN KRİTİK ENDPOINT.

📁 GİRDİ:
- ML kontratı: `docs/STATUS_REPORT_ML_TESLIM.md` §5 (analyze imzası), §9 (sözleşme garantileri)
- ML paket sözleşmesi: `from raw2value_ml import analyze, AnalyzePayload, AnalyzeResponse, LiveFx`
- Rapor §7 (ML serving), §9.7 (analyze endpoint), §11 (cache)
- `docs/api_examples.json` (2 hazır örnek)

📤 ÇIKTI:
- backend/app/services/ml_service.py — run_analyze (thread pool), warmup
- backend/app/services/history_service.py — analyze sonucu DB'ye yazma (fire-and-forget)
- backend/app/schemas/analyze.py — AnalyzeRequest (live_fx ÇIKARILMIŞ — backend doldurur), AnalyzeResponseOut (ML response + meta alanlar)
- backend/app/api/analyze.py — `POST /api/analyze`
- backend/app/main.py'a lifespan'da ML warmup ekle
- backend/tests/test_analyze.py

🛠️ GÖREV:

schemas/analyze.py:
```python
from pydantic import BaseModel, Field
from typing import Literal
from raw2value_ml import AnalyzeResponse  # ML'in tipini reuse et

class AnalyzeRequest(BaseModel):
    """Frontend'den gelen istek; live_fx YOK (backend doldurur)."""
    raw_material: Literal["pomza", "perlit", "kabak_cekirdegi"]
    tonnage: float = Field(gt=0, le=100_000)
    quality: Literal["A", "B", "C", "unknown"]
    origin_city: str
    target_country: Literal["TR", "DE", "NL"]
    target_city: str | None = None
    transport_mode: Literal["kara", "deniz", "demiryolu", "hava"]
    priority: Literal["max_profit", "low_carbon", "fast_delivery"] = "max_profit"
    input_mode: Literal["basic", "advanced"] = "basic"
    moisture_pct: float | None = None
    purity_pct: float | None = None
    particle_size_class: str | None = None
    fx_scenario_pct: float = 0.0
    cost_scenario_pct: float = 0.0

class AnalyzeResponseOut(AnalyzeResponse):
    """ML response + backend meta."""
    request_id: str
    fx_used: dict
    duration_ms: int
    model_version: str = "v1.0"
```

services/ml_service.py:
```python
import asyncio, time, hashlib
from raw2value_ml import analyze as ml_analyze, AnalyzePayload, AnalyzeResponse, LiveFx
from ..config import settings
from ..core.cache import get_redis

async def warmup_ml():
    """Lifespan startup'ta çağrılır; pickle'ları load eder."""
    payload = AnalyzePayload(
        raw_material="pomza", tonnage=100, quality="A",
        origin_city="Nevşehir", target_country="DE", target_city="Hamburg",
        transport_mode="kara",
        live_fx=LiveFx(usd_try=45.0, eur_try=52.0, last_updated="2026-05-03"),
    )
    loop = asyncio.get_event_loop()
    t0 = time.perf_counter()
    await loop.run_in_executor(None, ml_analyze, payload)
    logger.info("ml_warmup_complete", duration_ms=int((time.perf_counter()-t0)*1000))

async def run_analyze(payload: AnalyzePayload) -> AnalyzeResponse:
    if settings.ML_RESPONSE_CACHE_TTL_SEC > 0:
        r = await get_redis()
        key = f"analyze:{_hash_payload(payload)}"
        if cached := await r.get(key):
            return AnalyzeResponse.model_validate_json(cached)

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, ml_analyze, payload)

    if settings.ML_RESPONSE_CACHE_TTL_SEC > 0:
        await r.setex(key, settings.ML_RESPONSE_CACHE_TTL_SEC, response.model_dump_json())
    return response

def _hash_payload(p: AnalyzePayload) -> str:
    return hashlib.sha256(p.model_dump_json().encode()).hexdigest()[:16]
```

services/history_service.py:
```python
async def save_analyze(db, *, request_id, user, payload, response, fx, duration_ms):
    record = AnalysisRecord(
        request_id=request_id,
        user_id=user.id if user else None,
        organization_id=user.organization_id if user else None,
        raw_material=payload.raw_material,
        tonnage=payload.tonnage,
        # ... tüm alanlar
        payload_json=payload.model_dump(mode="json"),
        response_json=response.model_dump(mode="json"),
        recommended_route=response.recommended_route,
        expected_profit_try=response.expected_profit_try,
        co2_kg=response.co2_kg,
        confidence_overall=response.confidence.overall,
        usd_try_at_call=fx.usd_try,
        eur_try_at_call=fx.eur_try,
        duration_ms=duration_ms,
    )
    db.add(record)
    await db.commit()
```

api/analyze.py:
```python
@router.post("/api/analyze", response_model=AnalyzeResponseOut)
@limiter.limit(settings.RATE_LIMIT_ANALYZE)
async def analyze_endpoint(
    request: Request,
    payload: AnalyzeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rid = request.state.request_id
    fx = await get_current_fx()
    ml_payload = AnalyzePayload(
        **payload.model_dump(),
        live_fx=LiveFx(usd_try=fx.usd_try, eur_try=fx.eur_try, last_updated=fx.last_updated),
    )
    # target_city default doldur
    if not ml_payload.target_city and ml_payload.target_country:
        ml_payload.target_city = {"DE":"Hamburg","NL":"Rotterdam","TR":"İstanbul"}[ml_payload.target_country]

    t0 = time.perf_counter()
    response = await run_analyze(ml_payload)
    duration_ms = int((time.perf_counter() - t0) * 1000)

    # Fire-and-forget DB save
    asyncio.create_task(save_analyze(db, request_id=rid, user=user, payload=ml_payload,
                                      response=response, fx=fx, duration_ms=duration_ms))

    return AnalyzeResponseOut(
        **response.model_dump(),
        request_id=rid,
        fx_used={"usd_try": fx.usd_try, "eur_try": fx.eur_try, "last_updated": fx.last_updated},
        duration_ms=duration_ms,
    )
```

main.py lifespan'a ekle:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ML_WARMUP_ON_STARTUP:
        await warmup_ml()
    yield
```

test_analyze.py — DİKKAT, ML paketi gerçek kullanılır (mock YOK):
- test_analyze_basic_pomza_de — pomza/150/A/Nevşehir→Hamburg
- test_analyze_advanced_kabak_tr — moisture/purity dolu
- test_analyze_response_contract:
  - len(route_alternatives) == 3
  - len(reason_codes) == 3
  - co2_tonnes == co2_kg/1000
  - confidence.overall ∈ [0,100]
- test_analyze_unauthorized_401
- test_analyze_invalid_tonnage_422
- test_analyze_persists_history (DB'de kayıt var mı kontrol)
- test_analyze_warm_latency_p95_under_500ms (5 çağrı, p95 ölç)

⚠️ DİKKAT:
- ML paket sync; `run_in_executor` ZORUNLU; doğrudan await edemezsin
- `feature_pipeline.pkl` YÜKLEME; CatBoost direkt DataFrame alır
- target_city boş + target_country dolu → backend default doldurur (rapor §7'deki bilinen sınırlama #9)
- response_json'a fx_used + duration_ms + request_id ekle (frontend için)
- `asyncio.create_task` history save için; bekleme; response gönderilsin önce

✅ KABUL KRİTERLERİ:
- `pytest backend/tests/test_analyze.py -v` 7/7 PASS
- Warmup log'u görünür: `ml_warmup_complete duration_ms=1400`
- Curl ile login → bearer token al → `/api/analyze` çağır → 200 + tam response
- p95 < 500 ms (warm)
- DB'de `analysis_history` tablosunda kayıt görünür
- 5 atomic commit:
  - `add: ml servisi ve warmup`
  - `add: analiz request response schemalari`
  - `add: analyze endpoint`
  - `add: analiz gecmisi persist servisi`
  - `add: analyze endpoint testleri`
````

---

### ADIM 6 — `/api/what-if` + `/api/processors/nearby` + `/api/model-evidence` (1 saat)

**📋 CLAUDE CODE PROMPT:**

````markdown
🎯 ROL: Backend mühendisi. Geri kalan ana endpoint'leri tamamlıyorsun.

📁 GİRDİ: Rapor §9.8-9.10 (3 endpoint), §10.2 (ORS client).

📤 ÇIKTI:
- backend/app/api/whatif.py
- backend/app/api/processors.py
- backend/app/api/evidence.py
- backend/app/clients/ors.py
- backend/app/services/geo_service.py
- backend/app/services/evidence_service.py
- backend/app/schemas/processor.py
- backend/tests/test_whatif.py + test_processors.py + test_evidence.py

🛠️ GÖREV:

api/whatif.py:
```python
@router.post("/api/what-if")
async def whatif(req: WhatIfRequest, ...):
    base = req.base_payload
    fx = await get_current_fx()
    tasks = []
    for s in req.scenarios:
        p = base.model_copy(update={
            "fx_scenario_pct": s.get("fx_scenario_pct", base.fx_scenario_pct),
            "tonnage": s.get("tonnage_override", base.tonnage),
            "transport_mode": s.get("transport_mode_override", base.transport_mode),
        })
        ml_p = build_ml_payload(p, fx)
        tasks.append(run_analyze(ml_p))
    results = await asyncio.gather(*tasks)
    return {"results": [{"scenario": s.name, "expected_profit_try": r.expected_profit_try,
                         "value_uplift_pct": r.value_uplift_pct, "co2_kg": r.co2_kg,
                         "recommended_route": r.recommended_route,
                         "confidence_overall": r.confidence.overall}
                        for s, r in zip(req.scenarios, results)],
            "base_fx": fx.model_dump(),
            "duration_ms": ...}
```

services/geo_service.py:
```python
def haversine_km(lat1, lon1, lat2, lon2) -> float:
    # standard formula
    ...

async def find_nearby_processors(db, lat, lon, radius_km=100, material=None):
    # MVP: bbox + Haversine filtreleme
    bbox = bbox_from_radius(lat, lon, radius_km)
    stmt = select(Organization).where(
        Organization.can_process_material == True,
        Organization.lat.between(bbox.min_lat, bbox.max_lat),
        Organization.lon.between(bbox.min_lon, bbox.max_lon),
    )
    if material:
        stmt = stmt.join(ProcessorProfile).where(
            ProcessorProfile.processing_routes.any(material)  # array contains
        )
    rows = (await db.execute(stmt)).scalars().all()
    out = []
    for org in rows:
        d = haversine_km(lat, lon, org.lat, org.lon)
        if d <= radius_km:
            out.append({...})
    return sorted(out, key=lambda x: x["distance_km"])
```

api/processors.py:
```python
@router.get("/api/processors/nearby")
async def processors_nearby(
    lat: float, lon: float, radius_km: int = 100, material: str | None = None,
    user = Depends(get_current_user), db = Depends(get_db),
):
    if radius_km > 500:
        raise ValidationAppError("radius_km max 500")
    results = await find_nearby_processors(db, lat, lon, radius_km, material)
    return {"results": results, "count": len(results), "radius_km": radius_km, "method": "haversine_bbox"}
```

services/evidence_service.py:
- `models/metadata.json` ve `models/model_evidence.json`'ı disk'ten oku, `lru_cache` ile bellekte tut
- Endpoint sadece bunları birleştirip döner

api/evidence.py:
```python
@router.get("/api/model-evidence")  # PUBLIC (auth yok)
async def model_evidence():
    return load_evidence()
```

⚠️ DİKKAT:
- ORS client şimdilik whatif'te gerek yok (ML zaten internal lookup yapıyor); processors/nearby'da DA gerek yok (Haversine yeterli)
- Future ORS client kütüphanesi olarak dursun ama API'larda kullanma
- evidence endpoint cache: `lru_cache(maxsize=1)` + Redis'e gerek yok
- `len(scenarios) <= 10` validation (DOS koruma)

✅ KABUL KRİTERLERİ:
- 3 endpoint smoke test PASS
- `/api/what-if` 4 senaryo paralel <200 ms
- `/api/processors/nearby` boş DB'de `[]` döner; seed sonra dolu
- `/api/model-evidence` model_evidence.json içeriğini döner
- 4 atomic commit: `add: whatif endpoint ve servisi`, `add: geo servisi ve haversine`, `add: processors nearby endpoint`, `add: model evidence endpoint`
````

---

### ADIM 7 — Organizations CRUD + History (1 saat)

**📋 CLAUDE CODE PROMPT:**

````markdown
🎯 ROL: Backend mühendisi. Organization CRUD ve History endpoint'lerini yazıyorsun.

📁 GİRDİ: Rapor §9.11-9.16.

📤 ÇIKTI:
- backend/app/services/org_service.py
- backend/app/services/history_service.py (zaten var, get/list ekle)
- backend/app/schemas/organization.py + history.py + common.py (PaginatedResponse)
- backend/app/api/organizations.py
- backend/app/api/history.py
- backend/tests/test_orgs.py + test_history.py

🛠️ GÖREV:

schemas/organization.py:
- OrgCreate, OrgUpdate, OrgOut
- CapabilityFlags (6 boolean)
- ProducerProfileIn / ProcessorProfileIn / BuyerProfileIn (opsiyonel nested)

api/organizations.py:
- `POST /api/orgs` — auth + create + bağlı user'a org_id ata
- `GET /api/orgs/{id}` — auth + read
- `PATCH /api/orgs/{id}` — own user veya admin
- `GET /api/orgs?capability=can_process_material&material=pomza` — filtre + pagination

api/history.py:
- `GET /api/history?page=1&page_size=20&material=pomza&from=2026-05-01` — own user'ın kayıtları
- `GET /api/history/{id}` — full payload + response

⚠️ DİKKAT:
- pagination helper yaz (`PaginatedResponse[T]`)
- admin değilse own scope (user_id == current_user.id) zorla
- org silme YOK (audit için soft delete future)

✅ KABUL KRİTERLERİ:
- POST org → 201 → user'a org_id atanmış
- GET history → analyze sonrası kayıt görünür
- Filter + pagination çalışır
- 5 atomic commit: `add: org schemalari ve servisi`, `add: org crud endpointleri`, `add: history schemalari ve servisi`, `add: history endpointleri`, `add: orgs ve history testleri`
````

---

### ADIM 8 — Rate limit + Metrics + Hardening (45 dk)

**📋 CLAUDE CODE PROMPT:**

````markdown
🎯 ROL: Backend mühendisi. Rate limit, Prometheus metrics ve security hardening ekliyorsun.

📁 GİRDİ: Rapor §15 (rate limit + security).

📤 ÇIKTI:
- backend/app/core/rate_limit.py — slowapi limiter
- backend/app/main.py'a Prometheus instrumentator ekle
- Security headers middleware (X-Content-Type-Options, HSTS)
- backend/tests/test_rate_limit.py

🛠️ GÖREV:

core/rate_limit.py:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL if settings.RATE_LIMIT_ENABLED else None,
    enabled=settings.RATE_LIMIT_ENABLED,
)
```

main.py:
```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.APP_ENV == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

test_rate_limit.py:
- 31 hızlı `/api/analyze` çağrısı → 31. çağrı 429
- Auth login 11. başarısız deneme → 429

✅ KABUL KRİTERLERİ:
- `/metrics` endpoint Prometheus formatında çıktı verir
- Rate limit aşıldığında 429 + `Retry-After` header
- Security headers her response'ta
- 3 atomic commit: `add: slowapi rate limiter`, `add: prometheus metrics`, `add: security headers middleware`
````

---

### ADIM 9 — Docker + docker-compose + Seed (45 dk)

**📋 CLAUDE CODE PROMPT:**

````markdown
🎯 ROL: DevOps. Docker imajı + compose + seed script + healthcheck yazıyorsun.

📁 GİRDİ: Rapor §16 (deployment).

📤 ÇIKTI:
- backend/Dockerfile (multi-stage, rapor §16.1)
- docker-compose.yml (root, rapor §16.2)
- docker-compose.dev.yml (override: volumes, debug)
- backend/scripts/seed_demo.py — 5 producer + 3 processor + 3 buyer + 1 admin user
- backend/scripts/healthcheck.py — `/health` cevabını kontrol
- backend/scripts/wait_for_db.py — DB hazır olana kadar bekle
- README.md (root) — Quick start

🛠️ GÖREV:

seed_demo.py:
- 5 organization (pomza üreticisi, perlit üreticisi, kabak çekirdeği üreticisi, mikronizasyon işleyicisi, BASF benzeri buyer)
- demo admin user (env'den email/password)
- idempotent: zaten varsa skip

healthcheck.py:
```python
import sys, urllib.request
try:
    r = urllib.request.urlopen("http://localhost:8000/health", timeout=3)
    sys.exit(0 if r.status == 200 else 1)
except Exception:
    sys.exit(1)
```

README.md (root) Quick Start:
```bash
git clone ...
cp backend/.env.example backend/.env
# JWT_SECRET, TCMB_EVDS_API_KEY, ORS_API_KEY env'i doldur
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_demo.py
# → http://localhost:8000/docs
```

⚠️ DİKKAT:
- Dockerfile'da `models/` ve `data/reference/` mutlaka kopyalansın (ML için kritik)
- ML pickle dosyaları `*.pkl` `.dockerignore`'da OLMAMALI (kopyalansın)
- HEALTHCHECK 30 sn interval (lifespan warmup ~1.4 s, ilk healthcheck'i geçer)
- compose'da `db` healthcheck depends_on ile api'nin önünde

✅ KABUL KRİTERLERİ:
- `docker compose up -d --build` 4 servis (api, db, redis, minio opsiyonel) ayağa kalkar
- `docker compose ps` hepsi healthy
- `curl localhost:8000/api/fx/current` 200
- `docker compose exec api python scripts/seed_demo.py` idempotent
- 4 atomic commit: `add: backend dockerfile multistage`, `add: docker compose stack`, `add: demo seed scripti`, `add: healthcheck ve readme`
````

---

### ADIM 10 — CI/CD + Final QA (30 dk)

**📋 CLAUDE CODE PROMPT:**

````markdown
🎯 ROL: DevOps. GitHub Actions CI ve final QA pass.

📁 GİRDİ: Rapor §16.3.

📤 ÇIKTI:
- .github/workflows/ci.yml (rapor §16.3)
- backend/scripts/qa_smoke.sh — full e2e curl flow
- backend/README.md güncelle (test komutları, endpoint listesi)

🛠️ GÖREV:

ci.yml: rapor §16.3 birebir.

qa_smoke.sh:
```bash
#!/bin/bash
set -e
BASE=http://localhost:8000
echo "1. Health"
curl -sf $BASE/health | jq .
echo "2. FX"
curl -sf $BASE/api/fx/current | jq .
echo "3. Register + Login"
curl -sf -X POST $BASE/api/auth/register -H "Content-Type: application/json" \
  -d '{"email":"qa@test.local","password":"qatest12345","full_name":"QA"}' | jq .
TOKEN=$(curl -sf -X POST $BASE/api/auth/login \
  -d "username=qa@test.local&password=qatest12345" | jq -r .access_token)
echo "4. Me"
curl -sf $BASE/api/auth/me -H "Authorization: Bearer $TOKEN" | jq .
echo "5. Analyze"
curl -sf -X POST $BASE/api/analyze \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"raw_material":"pomza","tonnage":150,"quality":"A","origin_city":"Nevşehir","target_country":"DE","target_city":"Hamburg","transport_mode":"kara","priority":"max_profit","input_mode":"basic"}' | jq .
echo "6. What-if"
curl -sf -X POST $BASE/api/what-if -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"base_payload":{...},"scenarios":[{"name":"a","fx_scenario_pct":-0.1}]}' | jq .
echo "7. Model Evidence"
curl -sf $BASE/api/model-evidence | jq .profit_regression.best_model
echo "ALL OK"
```

✅ KABUL KRİTERLERİ:
- GitHub Actions yeşil
- `bash backend/scripts/qa_smoke.sh` 7/7 OK
- 2 atomic commit: `add: github actions ci`, `add: qa smoke scripti ve readme`
````

---

## 19. KABUL KRİTERLERİ (GATE'LER) — BACKEND TAMAMLANDI MI?

| Gate | Kriter | Doğrulama |
|---|---|---|
| **G1 — Foundation** | Iskelet + config + logging + exceptions | `uvicorn` boot eder, `/health` 200, JSON log akar |
| **G2 — DB + Auth** | PostgreSQL + Alembic + JWT login flow | `/api/auth/register/login/me` çalışır, DB'de user var |
| **G3 — FX & ML** | TCMB EVDS + `/api/analyze` | Curl 200, p95 <500 ms warm, history kaydı düşer |
| **G4 — Tüm endpoint'ler** | What-if + processors + evidence + orgs + history | `qa_smoke.sh` 7/7 OK |
| **G5 — Operasyon** | Docker compose + CI yeşil + rate limit + metrics | `docker compose up` ile sıfırdan başlar; `/metrics` çalışır |

5 gate de PASS olmadan frontend'e geçilmez.

---

## 20. RİSK MATRİSİ + YEDEK PLAN

| Risk | Olasılık | Etki | Yedek |
|---|:-:|:-:|---|
| ML model RAM yetersiz (CatBoost ~50 MB × worker) | Orta | Yüksek | `-w 1` worker; demo single-user OK |
| TCMB EVDS API key alınamadı | Düşük | Orta | `TCMB_FALLBACK_*` env değerleri devreye girer; `is_stale=true` |
| ORS rate limit (free 40/dk) | Düşük | Düşük | ML paketinin geo.py lookup'ı zaten lokal; ORS opsiyonel |
| PostgreSQL kurulum gecikme | Düşük | Yüksek | SQLite fallback (sadece development); compose ile kolay |
| Demo gününde lokalden tunneling | Orta | Orta | ngrok / cloudflared yedek (`raw2value_revised.md` §9.8) |
| Hackathon süre baskısı | Yüksek | Yüksek | ADIM 7 (orgs+history) opsiyonel; minimum G1+G2+G3 ile demo edilebilir |

**Asgari demoable backend:** G1 + G2 + G3 (analyze + fx + auth). Kalan endpoint'ler frontend ile paralel geliştirilebilir.

---

## 21. FRONTEND'E TESLİM SÖZLEŞMESİ

Backend bittiğinde frontend şu garantilerle çalışacak:

1. **Base URL:** `http://localhost:8000` (dev), prod'da `https://api.raw2value.ai`.
2. **OpenAPI docs:** `/docs` (Swagger UI), `/redoc` (Redoc), `/openapi.json` (TS client gen).
3. **Auth:** JWT Bearer; token `/api/auth/login`'den; `Authorization: Bearer <token>` header.
4. **CORS:** `CORS_ORIGINS` env'de localhost:3000 zaten. Prod'da frontend domain eklenir.
5. **Error format:** RFC 7807 `{type, title, status, detail, instance, request_id}`.
6. **Response içeriği:** ML kontratı + `request_id`, `fx_used`, `duration_ms` ekstra alanlar.
7. **Performans:** `/api/analyze` warm p95 <500 ms; cold start (1. request) ~1.5 s.
8. **TS client:** Frontend `openapi-typescript` ile `openapi.json`'dan otomatik tip üretir.

**Frontend için faydalı endpoint'ler:**
- Decision Cockpit ana → `POST /api/analyze`
- What-if slider → `POST /api/what-if`
- Canlı kur widget'ı → `GET /api/fx/current`
- Model Evidence ekranı → `GET /api/model-evidence`
- Reports & history → `GET /api/history` + `GET /api/history/{id}`
- Onboarding capability → `POST /api/orgs`
- Processor catalog → `GET /api/orgs?capability=can_process_material&material=pomza`
- Nearby işleyici → `GET /api/processors/nearby`

---

## 22. ÖZET

Bu rapor (Part 1 + Part 2) backend'in **sıfırdan teslim edilebilir hâle gelmesi** için 11 adımı (ADIM 0–10) tanımladı. Her adım Claude Code prompt'u + kabul kriteriyle yazıldı.

**Toplam tahmini süre:** 8–10 saat (1 kişi seri), 5–6 saat (2 kişi paralel: 0–4 + 5 lead, 6–10 support).

**Sözleşme garantileri:**
- ML paketinin `analyze()` fonksiyonu HİÇ değiştirilmeyecek; backend etrafına HTTP, auth, persistence, cache, monitoring sarıyor.
- Frontend'e teslim edilen API kontratı OpenAPI ile otomatik dokümante.
- Tüm endpoint'ler test'li (G4'te `qa_smoke.sh` 7/7).

**Kural uyumu (hackathon kuralları K1/K2/K3):**
- **K1 (Karbon)** → ML paketinde `compute_co2()` zaten sabit faktörlerle. Backend response'ta `co2_kg` + `co2_tonnes`'i frontend'e taşır.
- **K2 (Kur)** → `/api/fx/current` ile TCMB canlı + `live_fx` her `analyze()` çağrısında modele gönderiliyor. Ablation kanıtı `/api/model-evidence`'da.
- **K3 (Bağımsız geo)** → `/api/processors/nearby` Haversine bbox; ML paketi içinde de geo lookup ayrı.

**Sonraki faz:** Frontend (Next.js + Tailwind + Leaflet + Recharts + Decision Cockpit). Backend bu rapora göre tamamlandığında frontend ekibinin tek ihtiyacı `/docs` ve `/api/*` endpoint'leri olacak.

— **Raw2Value AI Master Backend Geliştirme Raporu (Part 2/2) son.**
