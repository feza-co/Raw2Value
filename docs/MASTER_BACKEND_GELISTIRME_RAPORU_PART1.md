# RAW2VALUE AI — MASTER BACKEND GELİŞTİRME RAPORU (PART 1/2)

**Versiyon:** v1.0
**Tarih:** 2026-05-03
**Durum:** ML PIPELINE TAMAMLANDI → BACKEND FAZI BAŞLADI
**Bu dosya:** Bölüm 0 → 9.8 (Mimari + Altyapı + İlk endpoint spec'leri)
**Devam:** `MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md` (Bölüm 9.9 → 22, Roadmap & Claude Code prompt'ları, Deployment, Risk matrisi)
**Hedef performans:** `/api/analyze` p95 < 700 ms (warm), p99 < 1.2 s

---

## 0. AMAÇ VE KAPSAM

Bu rapor, Raw2Value AI projesinin **backend katmanını sıfırdan teslim edilebilir hâle getirmek** için yazıldı. ML ekibi `raw2value_ml` paketini ve `models/` artefactlerini teslim etti (88/88 test PASS, `analyze()` warm latency ~20 ms). Backend artık tek satır import ile karar mantığını çağırabilir:

```python
from raw2value_ml import analyze, AnalyzePayload, LiveFx
response = analyze(payload)  # → AnalyzeResponse pydantic v2 model
```

Backend'in görevi bu sözleşmenin etrafına şunları kurmak:

1. **HTTP API** — FastAPI ile REST endpoint'leri (frontend'in tek konuştuğu yüzey).
2. **Canlı entegrasyonlar** — TCMB EVDS (kur), OpenRouteService (mesafe).
3. **Veri katmanı** — PostgreSQL (capability-based organizations, analiz geçmişi), Redis (cache).
4. **Kullanıcı yönetimi** — JWT auth + capability-based authorization.
5. **Dosya yükleme** — Lab raporu upload (advanced mode için, opsiyonel).
6. **Operasyon** — Docker, logging, error handling, rate limiting, metrics.
7. **Test + CI/CD** — pytest + GitHub Actions.

Bu rapor bittiğinde frontend ekibinin tek ihtiyacı `/api/*` endpoint'leri olacak. Backend'de yapılacak iş kalmayacak.

---

## 1. KARAR ÖZETİ — FRAMEWORK VE BİLEŞEN SEÇİMLERİ

| Bileşen | Seçim | Gerekçe |
|---|---|---|
| **Web framework** | **FastAPI 0.115+** (Python 3.11) | ML paketi pydantic v2 + Python 3.11. Aynı runtime → tek satır import. `async/await` native. OpenAPI auto-doc. Repo dökümantasyonu zaten FastAPI varsayıyor. |
| **ASGI server** | **Uvicorn** (dev) + **Gunicorn+Uvicorn worker** (prod) | Standard tercih. Prod'da `--workers $((CPU*2+1))`, demo'da `--workers 1` (model RAM tasarrufu). |
| **Veritabanı** | **PostgreSQL 16 + PostGIS** | Capability-based `organizations` tablosu zaten tasarlandı (`raw2value_revised.md` §9.6). PostGIS ile K3 nearby search advanced. |
| **ORM** | **SQLAlchemy 2.0** (async) + **Alembic** migration | Async FastAPI ile uyumlu. Type-safe. Migration disiplini için Alembic. |
| **Cache** | **Redis 7** | TCMB FX (5 dk TTL), ORS distance (1 saat TTL), rate limiting backend, optional analyze response cache. |
| **Auth** | **JWT (HS256) + bcrypt** | `python-jose[cryptography]` + `passlib[bcrypt]`. Hackathon için OAuth scope creep; basic JWT yeterli. |
| **Async task queue** | **YOK (MVP)** — `asyncio.create_task` yeterli | `analyze()` zaten ~20ms warm; queue overkill. Lab report parsing için future Celery. |
| **File storage** | **MinIO** (S3-uyumlu) | Self-hosted, docker-compose'a 1 satır. Lab raporu yükleme advanced mode için. MVP'de local FS fallback OK. |
| **Logging** | **structlog** (JSON formatlı) | Structured logging, request ID propagation, kolay grep. |
| **Error tracking** | **Sentry SDK** (opsiyonel) | Demo dışında; SENTRY_DSN boşsa devre dışı kalır. |
| **Metrics** | **prometheus-fastapi-instrumentator** | `/metrics` endpoint, latency histogram, in/out counter. |
| **Rate limit** | **slowapi** (Redis backend) | IP başı `/api/analyze` 30/dk, `/api/fx/current` 60/dk. |
| **HTTP client** | **httpx** (async) | TCMB EVDS + ORS için. Timeout + retry. |
| **Validation** | **pydantic v2** | ML paketiyle aynı sürüm — schema'lar paylaşılır. |
| **Test** | **pytest + pytest-asyncio + httpx.AsyncClient** | FastAPI ile standart kombinasyon. |
| **Container** | **Docker + docker-compose** | Tek komut: `docker compose up`. Servisler: `api`, `db`, `redis`, `minio`. |
| **CI** | **GitHub Actions** | Lint (ruff) + pytest + docker build smoke. |

> **Flask veya Node.js neden değil?** ML paketi Python 3.11 + pydantic v2; aynı runtime'da çalışmak zorundayız. Flask'ta async yok, sync içine sıkışırız. Node.js olsa modeli ya bir Python sidecar'la çağırırdık (ekstra gecikme + iki dil) ya ONNX'e dönüştürürdük (8 saatlik teslim riski). FastAPI tek doğru tercih.

---

## 2. MİMARİ — ÜST DÜZEY DİYAGRAM

```
                    ┌──────────────────────┐
                    │      FRONTEND        │
                    │   Next.js + React    │  (ileride)
                    └──────────┬───────────┘
                               │ REST/JSON (https)
                               ▼
              ┌────────────────────────────────────┐
              │           FASTAPI APP              │
              │  ┌──────────────────────────────┐  │
              │  │  Middleware Pipeline         │  │
              │  │  CORS → RequestID → Logging  │  │
              │  │  → RateLimit → Auth(JWT)     │  │
              │  └──────────────────────────────┘  │
              │  ┌──────────────────────────────┐  │
              │  │  Routers                     │  │
              │  │  /api/auth, /api/fx,         │  │
              │  │  /api/analyze, /api/whatif,  │  │
              │  │  /api/processors,            │  │
              │  │  /api/model-evidence,        │  │
              │  │  /api/orgs, /api/history     │  │
              │  └──────────────────────────────┘  │
              │  ┌──────────────────────────────┐  │
              │  │  Service Layer               │  │
              │  │  ml_service · fx_service     │  │
              │  │  geo_service · org_service   │  │
              │  │  history_service             │  │
              │  └──────────────────────────────┘  │
              └────┬──────────┬──────────┬─────────┘
                   │          │          │
       ┌───────────▼┐  ┌──────▼─────┐  ┌─▼──────────┐
       │ raw2value_ │  │ PostgreSQL │  │   Redis    │
       │  ml.analyze│  │ + PostGIS  │  │   cache    │
       │ (in-proc)  │  │            │  │            │
       └────────────┘  └────────────┘  └────────────┘
                   │          │
       ┌───────────┴──────────┴──────────────┐
       │  External APIs (httpx async)        │
       │  • TCMB EVDS  (kur, 30 dk cache)    │
       │  • OpenRouteService (mesafe, 1h)    │
       │  • Nominatim (geocoding, opsiyonel) │
       └─────────────────────────────────────┘
                   │
              ┌────▼────┐
              │  MinIO  │  (lab report uploads, opsiyonel)
              └─────────┘
```

**Akışın özeti — `/api/analyze` çağrısı:**

```
1. Frontend → POST /api/analyze (JWT Bearer + body)
2. Middleware: CORS pass → RequestID üret → JSON log → rate limit kontrol → JWT decode
3. Router: payload pydantic validate
4. ml_service.analyze():
   a. fx_service.get_current() → Redis cache → miss ise TCMB EVDS → cache set 5 dk
   b. live_fx ile birlikte AnalyzePayload oluştur
   c. raw2value_ml.analyze(payload) → AnalyzeResponse (in-process, ~20 ms)
5. history_service.save() → PostgreSQL `analysis_history` (async, non-blocking)
6. Response → frontend
7. Middleware: response log + metrics
```

---

## 3. KLASÖR YAPISI — TAM TREE

```
raw2value-ai/
├── backend/                              ← BU FAZ
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI app, lifespan, mount routers
│   │   ├── config.py                     # pydantic-settings .env loader
│   │   ├── deps.py                       # FastAPI dependencies (db, redis, current_user)
│   │   ├── exceptions.py                 # Custom exceptions + handlers
│   │   ├── logging.py                    # structlog konfigürasyonu
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── health.py                 # /health, /readiness
│   │   │   ├── auth.py                   # /api/auth/login, /register, /me
│   │   │   ├── fx.py                     # /api/fx/current
│   │   │   ├── analyze.py                # /api/analyze (THE endpoint)
│   │   │   ├── whatif.py                 # /api/what-if (batch)
│   │   │   ├── processors.py             # /api/processors/nearby
│   │   │   ├── evidence.py               # /api/model-evidence
│   │   │   ├── organizations.py          # /api/orgs CRUD
│   │   │   ├── history.py                # /api/history list/get
│   │   │   └── files.py                  # /api/files/upload (opsiyonel)
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── analyze.py                # /api/analyze request/response (ML wrap)
│   │   │   ├── auth.py                   # LoginRequest, TokenResponse, UserOut
│   │   │   ├── fx.py                     # FxResponse
│   │   │   ├── organization.py           # OrgCreate, OrgOut, CapabilityFlags
│   │   │   ├── processor.py              # NearbyProcessorOut
│   │   │   ├── history.py                # AnalysisRecordOut
│   │   │   └── common.py                 # PaginatedResponse, ErrorResponse
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ml_service.py             # raw2value_ml wrap + history persist
│   │   │   ├── fx_service.py             # TCMB EVDS + Redis cache
│   │   │   ├── geo_service.py            # ORS + Nominatim + PostGIS
│   │   │   ├── auth_service.py           # JWT encode/decode, bcrypt
│   │   │   ├── org_service.py            # Organization CRUD
│   │   │   ├── history_service.py        # Analiz geçmişi persist
│   │   │   └── evidence_service.py       # metadata.json + model_evidence.json read
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                   # SQLAlchemy DeclarativeBase
│   │   │   ├── session.py                # async_session_maker, get_db dependency
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py               # User
│   │   │   │   ├── organization.py       # Organization + capability flags
│   │   │   │   ├── profiles.py           # Producer/Processor/Buyer profiles
│   │   │   │   ├── analysis.py           # AnalysisRecord
│   │   │   │   └── shipment.py           # ShipmentHistory (future)
│   │   │   └── seed.py                   # Demo veri yükleme
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py               # password_hash, jwt_create, jwt_decode
│   │   │   ├── cache.py                  # Redis client + decorator
│   │   │   ├── rate_limit.py             # slowapi limiter
│   │   │   └── middleware.py             # RequestID, AccessLog
│   │   │
│   │   └── clients/
│   │       ├── __init__.py
│   │       ├── tcmb.py                   # EVDS REST client (httpx)
│   │       ├── ors.py                    # OpenRouteService client
│   │       └── nominatim.py              # Geocoding (opsiyonel)
│   │
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 0001_initial.py           # users, organizations, profiles
│   │       ├── 0002_analysis_history.py
│   │       └── 0003_postgis.py           # CREATE EXTENSION postgis (opsiyonel)
│   ├── alembic.ini
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                   # AsyncClient + test_db fixture
│   │   ├── test_health.py
│   │   ├── test_auth.py
│   │   ├── test_fx.py                    # TCMB mock
│   │   ├── test_analyze.py               # ML wrap tests
│   │   ├── test_whatif.py
│   │   ├── test_processors.py
│   │   ├── test_evidence.py
│   │   ├── test_orgs.py
│   │   ├── test_history.py
│   │   ├── test_rate_limit.py
│   │   └── fixtures/
│   │       └── tcmb_response.json
│   │
│   ├── scripts/
│   │   ├── seed_demo.py                  # Demo organization veri seti
│   │   ├── healthcheck.py                # Docker HEALTHCHECK
│   │   └── wait_for_db.py
│   │
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── pyproject.toml                    # backend bağımlılıkları
│   ├── requirements.txt                  # pinned versions
│   ├── requirements-dev.txt              # pytest, ruff, mypy
│   ├── .env.example
│   ├── README.md
│   └── pytest.ini
│
├── docker-compose.yml                    # api + db + redis + minio
├── docker-compose.dev.yml                # override (volumes, debug)
├── .github/
│   └── workflows/
│       ├── ci.yml                        # lint + test + build
│       └── docker.yml                    # image push (opsiyonel)
│
├── raw2value_ml/                         # ML ekibinden hazır (READ-ONLY backend için)
├── models/                               # ML artefactler (READ-ONLY)
├── data/                                 # ML reference parquet'leri (READ-ONLY)
└── ml/                                   # ML kodları (backend ilgilenmez)
```

---

## 4. DEPENDENCY LİSTESİ

### 4.1 `backend/requirements.txt` (pinned)

```
# --- Web framework ---
fastapi==0.115.5
uvicorn[standard]==0.32.1
gunicorn==23.0.0

# --- Validation & settings ---
pydantic==2.9.2
pydantic-settings==2.6.1

# --- ML paketi (lokal editable) ---
# raw2value-ml @ file://${PWD}/..   <-- pyproject.toml'da editable install

# --- Database ---
sqlalchemy[asyncio]==2.0.36
asyncpg==0.30.0
alembic==1.14.0
geoalchemy2==0.16.0   # PostGIS bindings (opsiyonel)

# --- Redis & cache ---
redis[hiredis]==5.2.0

# --- Auth ---
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.17   # form-data (file upload + login)

# --- HTTP client ---
httpx==0.28.0
tenacity==9.0.0   # retry helpers

# --- Logging & observability ---
structlog==24.4.0
prometheus-fastapi-instrumentator==7.0.0
sentry-sdk[fastapi]==2.18.0   # opsiyonel, SENTRY_DSN boşsa no-op

# --- Rate limiting ---
slowapi==0.1.9

# --- File storage (opsiyonel) ---
boto3==1.35.0   # MinIO S3-uyumlu

# --- Util ---
orjson==3.10.11   # FastAPI default_response_class için hızlı JSON
python-dotenv==1.0.1
```

### 4.2 `backend/requirements-dev.txt`

```
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
httpx==0.28.0
asgi-lifespan==2.1.0
respx==0.21.1            # httpx mock (TCMB, ORS testleri)
ruff==0.7.4
mypy==1.13.0
types-redis==4.6.0.20241004
faker==33.1.0
```

---

## 5. ENVIRONMENT VARIABLES — `.env.example`

```bash
# ============ APP ============
APP_NAME=raw2value-ai-backend
APP_ENV=development              # development | staging | production
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000
APP_BASE_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ============ SECURITY ============
JWT_SECRET=change-me-to-a-very-long-random-string-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TTL_MIN=60
JWT_REFRESH_TTL_DAYS=14
PASSWORD_HASH_ROUNDS=12

# ============ DATABASE ============
DATABASE_URL=postgresql+asyncpg://raw2value:secret@db:5432/raw2value
DATABASE_ECHO=false              # true = SQL log
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=5

# ============ REDIS ============
REDIS_URL=redis://redis:6379/0
REDIS_POOL_SIZE=20

# ============ ML PAKETI ============
ML_MODELS_DIR=/app/models                 # docker volume mount
ML_DATA_DIR=/app/data
ML_WARMUP_ON_STARTUP=true                 # ilk request beklemesin
ML_RESPONSE_CACHE_TTL_SEC=300             # idempotent payload için (opsiyonel)

# ============ TCMB EVDS ============
TCMB_EVDS_API_KEY=your-evds-key-here
TCMB_EVDS_BASE_URL=https://evds2.tcmb.gov.tr/service/evds
TCMB_FX_CACHE_TTL_SEC=300                 # 5 dk
TCMB_TIMEOUT_SEC=10
TCMB_FALLBACK_USD_TRY=45.00               # API down ise
TCMB_FALLBACK_EUR_TRY=52.00

# ============ OPENROUTESERVICE ============
ORS_API_KEY=your-ors-key-here
ORS_BASE_URL=https://api.openrouteservice.org
ORS_TIMEOUT_SEC=10
ORS_DISTANCE_CACHE_TTL_SEC=3600           # 1 saat

# ============ FILE STORAGE (MinIO) ============
S3_ENABLED=false                           # MVP'de false
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=raw2value-uploads
S3_REGION=us-east-1

# ============ RATE LIMIT ============
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_ANALYZE=30/minute
RATE_LIMIT_FX=60/minute
RATE_LIMIT_AUTH_LOGIN=10/minute

# ============ OBSERVABILITY ============
LOG_LEVEL=INFO                             # DEBUG | INFO | WARNING | ERROR
LOG_FORMAT=json                            # json | console
SENTRY_DSN=                                # boş = devre dışı
SENTRY_TRACES_SAMPLE_RATE=0.1
PROMETHEUS_ENABLED=true

# ============ SEED ============
SEED_DEMO_ON_STARTUP=true                  # development'ta true, prod'da false
DEMO_ADMIN_EMAIL=admin@raw2value.local
DEMO_ADMIN_PASSWORD=admin123               # ilk admin kullanıcı
```

> **Üretim notu:** `JWT_SECRET`, `TCMB_EVDS_API_KEY`, `ORS_API_KEY`, DB şifresi git'e gitmez. `.env` `.gitignore`'da; `.env.example` commit edilir (anahtarsız placeholder ile).

---

## 6. DATABASE ŞEMASI — TABLOLAR + MIGRATION

### 6.1 Tablolar (özet)

| Tablo | Amaç |
|---|---|
| `users` | Auth — email/password, role |
| `organizations` | Capability-based KOBİ kayıtları (`raw2value_revised.md` §9.6) |
| `producer_profiles` | Üretici detayı — raw_materials, capacity |
| `processor_profiles` | İşleyici detayı — routes, certifications, unit_cost |
| `buyer_profiles` | Alıcı detayı — product_interests, payment_terms |
| `analysis_history` | Her `/api/analyze` çağrısının kaydı |
| `lab_reports` | Yüklenen lab raporları (opsiyonel) |
| `shipment_history` | Sevkiyat kayıtları (future, MVP'de boş) |

### 6.2 SQL — `0001_initial.py` özeti

```sql
-- users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(200) UNIQUE NOT NULL,
    full_name VARCHAR(200),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',  -- user | admin
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);

-- organizations (capability-based)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    organization_type VARCHAR(50),        -- producer | processor | buyer | admin
    district VARCHAR(100),
    city VARCHAR(100),
    country VARCHAR(2) NOT NULL DEFAULT 'TR',
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    -- geom GEOGRAPHY(POINT, 4326),       -- PostGIS varsa
    can_supply_raw_material BOOLEAN NOT NULL DEFAULT FALSE,
    can_process_material   BOOLEAN NOT NULL DEFAULT FALSE,
    can_buy_material       BOOLEAN NOT NULL DEFAULT FALSE,
    can_export             BOOLEAN NOT NULL DEFAULT FALSE,
    has_storage            BOOLEAN NOT NULL DEFAULT FALSE,
    has_transport_capacity BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_org_supply  ON organizations(can_supply_raw_material) WHERE can_supply_raw_material = TRUE;
CREATE INDEX idx_org_process ON organizations(can_process_material)   WHERE can_process_material   = TRUE;
CREATE INDEX idx_org_buy     ON organizations(can_buy_material)       WHERE can_buy_material       = TRUE;
CREATE INDEX idx_org_geo     ON organizations(lat, lon);

-- producer_profiles
CREATE TABLE producer_profiles (
    organization_id UUID PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
    raw_materials VARCHAR(50)[] NOT NULL DEFAULT '{}',
    capacity_ton_year INT,
    quality_grades VARCHAR(2)[] NOT NULL DEFAULT '{}'
);

-- processor_profiles
CREATE TABLE processor_profiles (
    organization_id UUID PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
    processing_routes VARCHAR(50)[] NOT NULL DEFAULT '{}',
    capacity_ton_year INT,
    certifications VARCHAR(50)[] NOT NULL DEFAULT '{}',
    unit_cost_try_per_ton NUMERIC(10,2)
);

-- buyer_profiles
CREATE TABLE buyer_profiles (
    organization_id UUID PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
    product_interests VARCHAR(50)[] NOT NULL DEFAULT '{}',
    payment_terms_days INT,
    credit_score NUMERIC(3,2)
);
```

### 6.3 SQL — `0002_analysis_history.py`

```sql
CREATE TABLE analysis_history (
    id BIGSERIAL PRIMARY KEY,
    request_id VARCHAR(40) UNIQUE NOT NULL,           -- middleware'den gelen X-Request-ID
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,

    -- Input snapshot
    raw_material VARCHAR(30) NOT NULL,
    tonnage NUMERIC(10,2) NOT NULL,
    quality VARCHAR(10) NOT NULL,
    origin_city VARCHAR(100) NOT NULL,
    target_country VARCHAR(2) NOT NULL,
    target_city VARCHAR(100),
    transport_mode VARCHAR(20) NOT NULL,
    priority VARCHAR(30) NOT NULL,
    input_mode VARCHAR(20) NOT NULL,
    fx_scenario_pct NUMERIC(5,4) NOT NULL DEFAULT 0,
    cost_scenario_pct NUMERIC(5,4) NOT NULL DEFAULT 0,
    payload_json JSONB NOT NULL,                       -- tam input

    -- Output snapshot (model değişirse audit)
    recommended_route VARCHAR(80) NOT NULL,
    expected_profit_try NUMERIC(14,2),
    value_uplift_pct NUMERIC(8,4),
    co2_kg NUMERIC(12,2),
    confidence_overall NUMERIC(5,2),
    response_json JSONB NOT NULL,

    -- FX snapshot (audit için)
    usd_try_at_call NUMERIC(8,4),
    eur_try_at_call NUMERIC(8,4),
    fx_last_updated TIMESTAMPTZ,

    -- Performans
    duration_ms INT,
    model_version VARCHAR(20),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_history_user      ON analysis_history(user_id);
CREATE INDEX idx_history_org       ON analysis_history(organization_id);
CREATE INDEX idx_history_created   ON analysis_history(created_at DESC);
CREATE INDEX idx_history_material  ON analysis_history(raw_material);
CREATE INDEX idx_history_route     ON analysis_history(recommended_route);
```

### 6.4 PostGIS opsiyonel — `0003_postgis.py`

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
ALTER TABLE organizations ADD COLUMN geom GEOGRAPHY(POINT, 4326);
UPDATE organizations SET geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography
  WHERE lat IS NOT NULL AND lon IS NOT NULL;
CREATE INDEX idx_org_geom_gist ON organizations USING GIST(geom);
```

> Hackathon'da PostGIS kurmak zaman alırsa: MVP'de basit Haversine bbox filter ile geçilir. Yedek: ML paketinin `geo.py` modülü zaten Haversine fallback yapıyor; backend bunu doğrudan kullanabilir.

---

## 7. ML MODEL SERVING — PRODUCTION STRATEJİSİ

### 7.1 Loading — Lifespan event

```python
# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from raw2value_ml import analyze, AnalyzePayload, LiveFx

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    # 1. ML modelleri load et (ilk analyze() çağrısı tetikler ama warm-up için zorla)
    if settings.ML_WARMUP_ON_STARTUP:
        warmup_payload = AnalyzePayload(
            raw_material="pomza", tonnage=100, quality="A",
            origin_city="Nevşehir", target_country="DE", target_city="Hamburg",
            transport_mode="kara",
            live_fx=LiveFx(usd_try=45.0, eur_try=52.0, last_updated="2026-05-03"),
        )
        # Sync çağrı thread pool'a kaydır
        await asyncio.get_event_loop().run_in_executor(None, analyze, warmup_payload)
        logger.info("ml_warmup_complete", duration_ms=...)

    # 2. DB pool'u init et
    await init_db()

    # 3. Redis client init et
    await init_redis()

    yield

    # --- SHUTDOWN ---
    await close_redis()
    await close_db()

app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
```

**Neden warm-up?** ML paketinde `_state` lazy-load yapısı var (ilk `analyze()` çağrısında pickle'ları okur, ~1.4 s). Frontend ilk request'te bu 1.4 s'yi yememeli.

### 7.2 Inference çağrısı — sync model, async endpoint

`raw2value_ml.analyze()` **sync** bir fonksiyon. FastAPI endpoint async; sync ML çağrısı event loop'u bloklamamalı:

```python
# backend/app/services/ml_service.py
import asyncio
from raw2value_ml import analyze as ml_analyze, AnalyzePayload, AnalyzeResponse

async def run_analyze(payload: AnalyzePayload) -> AnalyzeResponse:
    loop = asyncio.get_event_loop()
    # CPU-bound + ~20 ms; thread pool'a göndermek event loop'u serbest bırakır
    response = await loop.run_in_executor(None, ml_analyze, payload)
    return response
```

> **Not:** CatBoost predict thread-safe (eski sürümlerde dikkat). Test'le doğrula. Gerekirse `concurrent.futures.ProcessPoolExecutor` kullanılabilir ama o zaman model her process'te ayrı RAM tutar.

### 7.3 Caching — idempotent payload optimizasyonu

What-if simülatöründe kullanıcı 3-4 farklı slider değeriyle aynı `analyze()`'i çağırabilir. Aynı payload için Redis cache:

```
Key: analyze:{sha256(payload_json)}
Value: response_json (orjson)
TTL: 5 dk (ML_RESPONSE_CACHE_TTL_SEC)
```

```python
async def cached_analyze(payload: AnalyzePayload) -> AnalyzeResponse:
    cache_key = f"analyze:{hash_payload(payload)}"
    if cached := await redis.get(cache_key):
        return AnalyzeResponse.model_validate_json(cached)
    response = await run_analyze(payload)
    await redis.setex(cache_key, settings.ML_RESPONSE_CACHE_TTL_SEC, response.model_dump_json())
    return response
```

### 7.4 Worker sayısı kararı

`gunicorn -w N` her worker için **modeller ayrı ayrı RAM'e yüklenir** (~50 MB × N). Hackathon demo makinesinde:
- **Demo modu:** `-w 1` (RAM ~200 MB) — single user, latency önemli.
- **Prod:** `-w 2` (RAM ~400 MB), ALB arkasında. Daha fazla worker için ONNX export gerek (future).

### 7.5 Performans hedefleri (backend perspektifinden)

| Endpoint | p50 | p95 | p99 | Sebep |
|---|---:|---:|---:|---|
| `/api/analyze` (warm + cache hit) | 5 ms | 20 ms | 40 ms | Redis lookup |
| `/api/analyze` (warm + cache miss) | 30 ms | 80 ms | 150 ms | ML inference + DB insert |
| `/api/analyze` (cold) | 1.4 s | 1.6 s | 2 s | Pickle load — sadece ilk request |
| `/api/fx/current` (cache hit) | 2 ms | 5 ms | 10 ms | Redis |
| `/api/fx/current` (cache miss) | 200 ms | 500 ms | 1 s | TCMB EVDS HTTP |
| `/api/processors/nearby` | 20 ms | 50 ms | 100 ms | Postgres + (PostGIS varsa hızlı) |

---

## 8. KİMLİK DOĞRULAMA & YETKİLENDİRME

### 8.1 Strateji

- **JWT (HS256)** — `python-jose`. Access token (60 dk) + refresh token (14 gün).
- **Password hashing** — `bcrypt` (12 round).
- **Capability-based authorization** — kullanıcının organizasyonunun capability flag'leri ile endpoint izinleri.

### 8.2 Roller ve izinler

| Endpoint | Anonim | Authenticated | Capability gerek |
|---|:-:|:-:|---|
| `GET /health` | ✅ | ✅ | — |
| `GET /api/fx/current` | ✅ | ✅ | — |
| `POST /api/auth/register` | ✅ | — | — |
| `POST /api/auth/login` | ✅ | — | — |
| `GET /api/auth/me` | — | ✅ | — |
| `POST /api/analyze` | ❌ | ✅ | — |
| `POST /api/what-if` | ❌ | ✅ | — |
| `GET /api/processors/nearby` | ❌ | ✅ | — |
| `GET /api/model-evidence` | ✅ | ✅ | — (public) |
| `POST /api/orgs` | ❌ | ✅ | — (own org) |
| `GET /api/orgs/{id}` | ❌ | ✅ | — |
| `PATCH /api/orgs/{id}` | ❌ | ✅ | own + admin |
| `GET /api/history` | ❌ | ✅ | own |
| `GET /api/admin/dashboard` | ❌ | ✅ | role=admin |

> **MVP shortcut:** Demo'da auth karışıklığı çıkmaması için `APP_ENV=demo` modunda `/api/analyze` için anonim erişim verilebilir (toggle'lı). Demo bittikten sonra prod modda kapatılır.

### 8.3 JWT payload örneği

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "role": "user",
  "org_id": "660e8400-...",
  "capabilities": ["can_supply_raw_material", "can_export"],
  "iat": 1714723200,
  "exp": 1714726800
}
```

### 8.4 Dependency

```python
# backend/app/deps.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_jwt(token)
    user = await db.get(User, UUID(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(401, "Invalid credentials")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403, "Admin only")
    return user
```

---

## 9. ENDPOINT SPEC'LERİ — TAM DETAY (1/2 — Auth + FX + Analyze + What-If)

> Tüm response'lar `application/json`. Hata response'ları RFC 7807 Problem Details formatında: `{type, title, status, detail, instance}`.
> Bu bölümün devamı (Processors / Evidence / Orgs / History / Files) **PART 2**'de §9.9–9.14 altında bulunur.

### 9.1 `GET /health`
**Status:** 200 — **Auth:** Public
```json
{ "status": "ok", "version": "0.1.0", "uptime_sec": 12345 }
```

### 9.2 `GET /readiness`
DB + Redis + ML model ping'i. ML hazır değilse 503 döner.
```json
{ "status": "ready", "db": "ok", "redis": "ok", "ml": "ok" }
```

### 9.3 `POST /api/auth/register`
**Body:**
```json
{ "email": "user@x.com", "password": "minimum8chars", "full_name": "Ahmet Yılmaz" }
```
**Response 201:**
```json
{ "id": "uuid", "email": "user@x.com", "full_name": "Ahmet Yılmaz", "role": "user", "created_at": "2026-05-03T12:00:00Z" }
```
**Hatalar:** `409` (email duplicate), `422` (validation: password<8 char vb.).

### 9.4 `POST /api/auth/login`
**Body** (form-data, OAuth2PasswordRequestForm):
```
username=user@x.com&password=minimum8chars
```
**Response 200:**
```json
{ "access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer", "expires_in": 3600 }
```
**Curl:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@x.com&password=minimum8chars"
```
**Hatalar:** `401` (yanlış credential), `429` (rate limit aşımı: 10/dk).

### 9.5 `GET /api/auth/me`
**Auth:** Bearer
**Response 200:**
```json
{
  "id": "uuid", "email": "user@x.com", "full_name": "Ahmet Yılmaz",
  "role": "user",
  "organization": {
    "id": "uuid", "name": "Doğa Pomza Ltd",
    "capabilities": {
      "can_supply_raw_material": true,
      "can_export": true,
      "can_process_material": false,
      "can_buy_material": false,
      "has_storage": true,
      "has_transport_capacity": false
    }
  }
}
```

### 9.6 `GET /api/fx/current` — TCMB canlı kur

**Auth:** Public. **Cache:** Redis 5 dk TTL.
**Response 200:**
```json
{
  "usd_try": 45.05,
  "eur_try": 52.67,
  "last_updated": "2026-05-03T09:00:00Z",
  "source": "TCMB_EVDS",
  "is_stale": false,
  "fetched_at": "2026-05-03T11:55:00Z"
}
```
**Davranış:**
- Hafta sonu / tatil → TCMB son veriyi döner; `is_stale=true` ve `last_updated` T-1.
- TCMB API down → `TCMB_FALLBACK_*` env değerleri + `is_stale=true` + `source="FALLBACK"`.

**Curl:** `curl http://localhost:8000/api/fx/current`

### 9.7 `POST /api/analyze` — ANA ENDPOINT

**Auth:** Bearer. **Rate limit:** 30/dk per user.

**Request body:**
```json
{
  "raw_material": "pomza",
  "tonnage": 150,
  "quality": "A",
  "origin_city": "Nevşehir",
  "target_country": "DE",
  "target_city": "Hamburg",
  "transport_mode": "kara",
  "priority": "max_profit",
  "input_mode": "basic",
  "fx_scenario_pct": 0.0,
  "cost_scenario_pct": 0.0
}
```

> Backend `live_fx`'i kendisi doldurur (TCMB cache'inden). Frontend göndermez.

**Response 200:**
```json
{
  "request_id": "req_01HX2...",
  "recommended_route": "pomza_micronized_pumice",
  "route_alternatives": [
    {
      "route": "pomza_micronized_pumice",
      "predicted_profit_try": 1425000.50,
      "value_uplift_pct": 4.85,
      "co2_kg": 37542.0,
      "route_probability": 0.87
    },
    { "route": "pomza_filtration_media", "predicted_profit_try": 980000.0, "value_uplift_pct": 3.2, "co2_kg": 37542.0, "route_probability": 0.08 },
    { "route": "pomza_bims_aggregate",   "predicted_profit_try": 280000.0, "value_uplift_pct": 0.6, "co2_kg": 37542.0, "route_probability": 0.05 }
  ],
  "expected_profit_try": 1425000.50,
  "value_uplift_pct": 4.85,
  "co2_kg": 37542.0,
  "co2_tonnes": 37.542,
  "match_results": [
    {
      "processor_name": "Genper Madencilik A.Ş.",
      "buyer_name": "BASF Deutschland GmbH",
      "score": 0.91,
      "components": { "distance": 0.85, "quality": 0.95, "price": 0.92, "delivery": 0.88, "demand": 0.95 }
    }
  ],
  "reason_codes": [
    { "feature": "total_distance_km", "importance": 0.34, "value": 2502.0, "text": "Toplam 2502 km mesafe yüksek; karbon ayak izi ve taşıma maliyeti kârı sınırlıyor." },
    { "feature": "usd_try", "importance": 0.21, "value": 45.05, "text": "USD/TRY 45.05 seviyesinde; ihracat geliri TL bazında güçlü." },
    { "feature": "demand_score", "importance": 0.17, "value": 0.85, "text": "Hedef pazar talep skoru 0.85 — Almanya inşaat sektöründe mikronize pomza talebi yüksek." }
  ],
  "confidence": {
    "data_confidence": 80,
    "model_confidence": 87,
    "overall": 83.5,
    "warnings": ["Nem ve saflık girilmedi; bölgesel varsayılan kullanıldı."]
  },
  "feature_importance": [
    { "feature": "total_distance_km", "importance": 0.342 },
    { "feature": "usd_try", "importance": 0.211 }
  ],
  "warnings": ["Nem ve saflık girilmedi; bölgesel varsayılan kullanıldı."],
  "fx_used": { "usd_try": 45.05, "eur_try": 52.67, "last_updated": "2026-05-03T09:00:00Z" },
  "duration_ms": 28,
  "model_version": "v1.0"
}
```

**Curl:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"raw_material":"pomza","tonnage":150,"quality":"A","origin_city":"Nevşehir","target_country":"DE","target_city":"Hamburg","transport_mode":"kara","priority":"max_profit","input_mode":"basic"}'
```

**Hata response'ları:**
- `400` / `422` — Validation: `{"detail":[{"loc":["body","tonnage"],"msg":"input should be greater than 0","type":"greater_than"}]}`
- `401` — Auth eksik/geçersiz.
- `429` — Rate limit aşıldı: `{"detail":"Rate limit exceeded: 30/minute"}`
- `503` — ML model yükleme başarısız (startup hatası).

**Sözleşme garantileri (ML §9.1'den):**
- `recommended_route ∈ metadata.json.models.route.classes` (10 trained sınıf)
- `len(route_alternatives) == 3`
- `len(reason_codes) == 3`
- `len(match_results) ≤ 5`
- `confidence.overall ∈ [0, 100]`
- `co2_tonnes == co2_kg / 1000`

### 9.8 `POST /api/what-if` — Batch what-if simülasyonu

**Auth:** Bearer. **Max 10 senaryo per request.**

**Body:**
```json
{
  "base_payload": {
    "raw_material": "pomza",
    "tonnage": 150,
    "quality": "A",
    "origin_city": "Nevşehir",
    "target_country": "DE",
    "target_city": "Hamburg",
    "transport_mode": "kara",
    "priority": "max_profit",
    "input_mode": "basic"
  },
  "scenarios": [
    { "name": "kur_dusuk",  "fx_scenario_pct": -0.10 },
    { "name": "kur_normal", "fx_scenario_pct": 0.0 },
    { "name": "kur_yuksek", "fx_scenario_pct": 0.10 },
    { "name": "tonaj_2x",   "tonnage_override": 300 },
    { "name": "deniz_yolu", "transport_mode_override": "deniz" }
  ]
}
```

**Response 200:**
```json
{
  "results": [
    { "scenario": "kur_dusuk",  "expected_profit_try": 1100000.00, "value_uplift_pct": 3.10, "co2_kg": 37542.0, "recommended_route": "pomza_micronized_pumice", "confidence_overall": 81.2 },
    { "scenario": "kur_normal", "expected_profit_try": 1425000.50, "value_uplift_pct": 4.85, "co2_kg": 37542.0, "recommended_route": "pomza_micronized_pumice", "confidence_overall": 83.5 },
    { "scenario": "kur_yuksek", "expected_profit_try": 1750000.00, "value_uplift_pct": 6.50, "co2_kg": 37542.0, "recommended_route": "pomza_micronized_pumice", "confidence_overall": 82.0 },
    { "scenario": "tonaj_2x",   "expected_profit_try": 2810000.00, "value_uplift_pct": 4.85, "co2_kg": 75084.0, "recommended_route": "pomza_micronized_pumice", "confidence_overall": 83.5 },
    { "scenario": "deniz_yolu", "expected_profit_try": 1530000.00, "value_uplift_pct": 5.20, "co2_kg":  5631.3, "recommended_route": "pomza_micronized_pumice", "confidence_overall": 80.1 }
  ],
  "base_fx": { "usd_try": 45.05, "eur_try": 52.67, "last_updated": "2026-05-03T09:00:00Z" },
  "duration_ms": 142
}
```

**Davranış:**
- Backend `analyze()`'i her senaryo için `asyncio.gather` ile **paralel** çağırır.
- 5 senaryo warm ~50 ms (cache hit) — 150 ms (cache miss).
- Her senaryo bağımsız Redis cache key'i üretir (`analyze:{hash}`); ardışık aynı senaryo cache'ten döner.

**Curl:**
```bash
curl -X POST http://localhost:8000/api/what-if \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"base_payload":{...},"scenarios":[{"name":"a","fx_scenario_pct":-0.1},{"name":"b","fx_scenario_pct":0.1}]}'
```

**Hatalar:**
- `422` — `len(scenarios) > 10` (DOS koruma) veya `fx_scenario_pct` ∉ [-0.20, 0.20].

---

## ▶ DEVAM — PART 2

Bu raporun devamı `MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md` dosyasında. Part 2 şunları içerir:

- **§9.9–9.14** — Geri kalan endpoint'ler (`/api/processors/nearby`, `/api/model-evidence`, `/api/orgs`, `/api/history`, `/api/files/upload`)
- **§10** — External Services (TCMB, ORS client tasarımı)
- **§11** — Cache stratejisi (Redis layout)
- **§12** — Async task queue kararı (Celery gerekli mi?)
- **§13** — File upload stratejisi
- **§14** — Logging + Monitoring + Sentry
- **§15** — Rate limiting + Security hardening
- **§16** — Deployment (Dockerfile, docker-compose, CI/CD)
- **§17** — Test stratejisi
- **§18** — **ROADMAP — 11 ADIM × CLAUDE CODE PROMPT** (en kritik bölüm)
- **§19** — Kabul kriterleri (5 Gate)
- **§20** — Risk matrisi + yedek plan
- **§21** — Frontend'e teslim sözleşmesi
- **§22** — Özet

---

— **Part 1/2 son. Part 2'ye geçin.**
