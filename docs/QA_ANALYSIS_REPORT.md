# Raw2Value AI — QA Analiz Raporu

**Tarih:** 2026-05-03
**Kapsam:** Tüm repo (114 dosya, 546 graf düğümü, 3456 ilişki, 132 test)
**Yöntem:** 5 paralel uzman ajan — read-only inceleme; HİÇBİR koda dokunulmadı.
**Branch:** `main` (commit `9c6431f`)
**Uncommitted:** `backend/Dockerfile` (M), `docs/MASTER_BACKEND_GELISTIRME_RAPORU_PART{1,2}.md` (??)

---

## 1. Yönetici Özeti

| Metrik | Değer |
|---|---|
| Toplam bulgu | **108** |
| CRITICAL | **5** |
| HIGH | **29** |
| MEDIUM | **38** |
| LOW | **22** |
| INFO | **14** |
| Production-ready? | **HAYIR** — birkaç critical hardening gerekli |
| ML kontrat (analyze) sağlamlığı | **PARTIAL** — 2 sızıntı, 0 yapısal kırılma |
| Güvenlik durumu | **DEMO/DEV** — pilot/prod öncesi mutlaka iyileştir |
| CI olgunluğu | **Basic** — backend test çalışıyor; ML test yok, type-check yok |
| Container olgunluğu | **Demo** — gizli kelime defaultları, port ifşa, .dockerignore yok |

### En kritik 5 bulgu (acilen düzelt)

1. **CI ML testlerini hiç çalıştırmıyor** — `ml/tests/` (88 test, içlerinde target-leakage CRITICAL guard) PR'larda çalışmıyor. Sızıntı geri gelirse fark edilmez. (DEVOPS-F7 / TEST-F1)
2. **JWT_SECRET ve DB password commit edilmiş plain-text default** — `change-me-...` ve `secret`. `.env.example` çalışan değer yolluyor; üretimde de aynı kalırsa token forge + DB compromise. (SEC-F1, DEVOPS-F2/F5)
3. **/api/auth/{login,register,refresh}'te rate limit YOK** — `RATE_LIMIT_AUTH_LOGIN` ayarı tanımlı ama hiçbir endpoint'e bağlanmamış. Brute-force / credential stuffing açık. (SEC-F2)
4. **POST /api/orgs IDOR** — herhangi bir kullanıcı, sahip olduğu org'u defalarca üzerine yazabiliyor; org listesi ve detayı tüm KOBİ'lerin ticari verilerini (credit_score, unit_cost) auth olmuş herkese sızdırıyor. (SEC-F3, F4)
5. **`docker-compose.yml` hardcoded `secret`/`minioadmin` + portları `0.0.0.0`'a açıyor** + `.dockerignore` yok → laptop dışı her ortamda Postgres+Redis+MinIO direkt internete açılıyor; build context tüm `.git`, `.env`, `data/master` ile imaja sızıyor. (DEVOPS-F1/F3/F4, SEC-F17)

### En kritik 5 ML/kontrat bulgusu

1. **FX `FALLBACK` → ML pipeline'a `TCMB_LIVE` etiketiyle geçiyor** — `usd_try=45.0` hardcoded sabiti, ML feature olarak girip `fx_source: "TCMB_LIVE"` etiketiyle `data_confidence`'i +10 yükseltiyor. CLAUDE.md "live_fx zorunlu, default YOK" kuralının net ihlali. (API-F2, ML-F6)
2. **`/api/what-if` cevabı `co2_tonnes`, `warnings`, `route_alternatives` alanlarını düşürüyor** — frontend tutarsızlığı + senaryo-uyarıları görünmez. (API-F6)
3. **15 vs 10 route sınıfı API'da gizli** — `recommended_route ∈ trained_classes` garanti ediliyor ama hangi rotaların "MVP'de henüz yok" olduğunu UI'a verecek alan/endpoint yok. UI iki ayrı çağrı yapıp diff almak zorunda. (API-F4, ML-F1)
4. **K2 ablasyon (66.07%) ve K3 Haversine fallback için TEST YOK** — sözleşme dokümante ama otomatik guard yok. K2 feature listesi değişirse / K3 lookup formatı değişirse sessizce regress eder. (TEST-F2, F3)
5. **`feature_pipeline.pkl` inference'ta startup'ta yükleniyor ama hiç kullanılmıyor** — sklearn-versiyon kırılganlığı, gereksiz cold-start fail mode. (ML-F2)

### Olumlu yönler (kabul göstermek için)

- **Pydantic v2 hijyeni mükemmel** — backend genelinde sıfır v1 idiom (`.dict()`, `parse_obj`, `Config`-class). (API-F23)
- **SQL injection yüzeyi yok** — tüm sorgular SQLAlchemy ORM ile parametrik. (SEC-INFO-1)
- **Multi-stage Dockerfile düzgün yapılı** — non-root user, ayrı builder/runtime, HEALTHCHECK var. (DEVOPS-F24)
- **Alembic migrations linear ve down-rev'li** — `0001_initial → 0002_analysis_history` zinciri temiz, FK'lar indexli, cascade kuralları sağlam. (DEVOPS-F23)
- **Target leakage guard çok güçlü** — `ml/tests/test_no_target_leakage.py` 14 testle M1/M2 invariantlarını kilitliyor; M1_FEATURES ve M2_FEATURES temiz. (ML-F17, TEST guard matrix)
- **K1 carbon faktörleri tam doğru** — `kara=0.100, deniz=0.015, hava=0.500, demiryolu=0.030` parquet ve carbon.py'da birebir; testle assert ediliyor.
- **K2 ablation deltası gerçekten load-bearing** — `without_fx` |delta| = 66.07% (CLAUDE.md iddiasını doğrular).
- **Backend ML testi gerçek pipeline çağırıyor** (mock yok, fidelity yüksek).

---

## 2. Bulgu Konsolide Tablosu

| Alan | CRITICAL | HIGH | MEDIUM | LOW | INFO | Toplam |
|---|--:|--:|--:|--:|--:|--:|
| ML pipeline integrity | 0 | 4 | 6 | 4 | 3 | 18 |
| Backend security | 3 | 6 | 7 | 5 | 2 | 23 |
| API correctness & ML integration | 0 | 6 | 8 | 4 | 4 | 22 |
| Test quality & coverage | 1 | 7 | 8 | 4 | 2 | 22 |
| DevOps & infra | 1 | 6 | 9 | 5 | 2 | 23 |
| **Toplam** | **5** | **29** | **38** | **22** | **13** | **108** |

---

## 3. Compliance Matrix (CLAUDE.md "ZORUNLU İlkeler" Karşılığı)

| Kural | Durum | Kanıt | Eksik |
|---|---|---|---|
| **K1 — Carbon faktörleri tam değer** | ✅ PASS | `raw2value_ml/carbon.py` + `data/reference/carbon.parquet` her iki tarafta da `kara=0.100, deniz=0.015, hava=0.500, demiryolu=0.030`. `compute_co2 = tonnage × distance × emission_factor`. `np.random.uniform` ile CO₂ üretimi yok. `test_reference_loader.py:25-37` exact equality assert. | `Birim` parquet kolonu `kg CO2/ton` yazıyor — `-km` eksik (ML-F4). Re-extraction confusion riski. |
| **K2 — FX iki modelin de input'unda** | ✅ PASS | `M1_FEATURES` ve `M2_FEATURES` her ikisinde de `usd_try`, `eur_try`, `fx_scenario_pct` var (`features.py:151-153`). `ablation_results.json` → `without_fx.rmse_delta_pct = -66.07%`, |delta| > 10%. | Otomatik test YOK — TEST-F2. K2 invariant'ı bir guard testle korunmuyor. |
| **K3 — Geo ORS-bağımsız** | ✅ PASS | `geo.py` dependent değil; `lookup_distance` parquet → Haversine fallback. `find_nearby_processors` radius_km + material filter. | Haversine fallback için test yok (TEST-F3). `_norm` substring match ambiguous şehirlerde yanlış satır seçebilir (ML-F11). |
| **Target leakage** | ✅ PASS | 14 test `test_no_target_leakage.py`'da M1/M2 invariantlarını kilitliyor. `metadata.json` feature listeleri uyumlu. `processing_route_candidate` doğru yerde. | Test ÇALIŞMIYOR CI'da (DEVOPS-F7) — guard pratikte ölü. |
| **Reproducibility (seed=42)** | ⚠️ PASS-with-warn | Augmentation `default_rng(42)`, training `random_state=42`. `test_augmentation_bounds.py:101-105` build-twice testi var. | `01_data_prep.ipynb` legacy `np.random.seed(42)` kullanıyor (ML-F13). Train modellerinin reproducibility testi YOK (TEST guard matrix). |
| **`analyze()` sözleşmesi sabit** | ⚠️ PARTIAL | Lazy load OK, schemas pydantic v2 sabit, `co2_tonnes = co2_kg/1000` (`inference.py:386`). Backend `AnalyzePayload` field-by-field eşleşiyor. | (1) `_compute_uplift` `usd_try=45.0` default'a düşüyor — "no default" kuralı ihlali (ML-F6). (2) `_state["pipeline"]` boş yere yükleniyor (ML-F2). (3) `recommended_route ∈ trained_classes` runtime assert YOK (ML-F1). (4) FX FALLBACK API-F2'de yanlış etiketleniyor. |
| **Pydantic v2** | ✅ PASS | `model_dump()`, `model_validate`, `ConfigDict(extra="forbid")` yaygın. `.dict()` / `parse_obj` / `Config:` SIFIR hit. | — |
| **Atomic commits + Claude imzası yok** | ✅ PASS | Son 30 commit incelendi: hepsi `<tür>: <ne>` formatında, atomic, Claude imzası yok. | — |

---

## 4. CRITICAL Bulgular (toplam 5)

### CRIT-1 — JWT_SECRET ve `.env` placeholder commit'lenmiş
**Dosya:** `backend/app/config.py:33`, `backend/.env:15`
```python
JWT_SECRET: str = "change-me-to-a-very-long-random-string-min-32-chars"
```
`backend/.env` dosyası `.env.example` ile birebir aynı; gerçek secret yok. Startup'ta validator yok. Repoyu okuyan herhangi biri herhangi bir kullanıcının token'ını forge edebilir.
**Aksiyon:** `JWT_SECRET` zorunlu yap (default kaldır). `APP_ENV=production` ise startup'ta `len >= 32 and != "change-me-..."` assert et. Secret rotate et: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

### CRIT-2 — /api/auth endpoint'lerinde rate limit YOK
**Dosya:** `backend/app/api/auth.py:55-97`, `core/rate_limit.py`, `config.py:82`
`RATE_LIMIT_AUTH_LOGIN: str = "10/minute"` tanımlı; hiçbir auth endpoint'te `@rate_limit` decorator yok. Sadece `analyze.py:80` rate-limited.
**Aksiyon:** `/login`, `/register`, `/refresh`'a `@rate_limit(settings.RATE_LIMIT_AUTH_LOGIN)` ekle. Register için ayrı (`5/hour` IP başına) önerilir.

### CRIT-3 — POST /api/orgs broken access control + privilege escalation
**Dosya:** `backend/app/services/org_service.py:79-135`
```python
user.organization_id = org.id   # No check whether user already in an org
db.add(user); await db.commit()
```
Auth olmuş herhangi biri defalarca POST atıp `organization_id`'sini değiştirebilir. `Organization.name` üzerinde unique constraint yok → "BASF Deutschland GmbH" adında sahte org oluşturulabilir. Audit trail (`AnalysisRecord.organization_id`) silinir.
**Aksiyon:** `create_org`'da `if user.organization_id is not None: raise ConflictError`. `(name, country)` üzerinde unique constraint ekle. Davet/onay flow'u veya `Membership` tablosu düşün.

### CRIT-4 — CI ML testlerini çalıştırmıyor (88 testlik sızıntı guard'ı ölü)
**Dosya:** `.github/workflows/ci.yml:73-75`
Sadece `cd backend; pytest tests/`. `ml/tests/` HİÇ çalışmıyor — `test_no_target_leakage.py` (CLAUDE.md "CRITICAL"), K1 carbon, scorer profilleri, augmentation bounds, seed=42 reproducibility — hepsi PR'larda guard değil.
**Aksiyon:** `ml-lint-and-test` jobu ekle: `pip install -e . && pytest ml/tests/ -v`. Model artifactları için pipeline'ı önce çalıştır VEYA cache'le. (`*.pkl` gitignored olduğu için 4 test dosyası model dosyası bekliyor.)

### CRIT-5 — `.dockerignore` YOK → tüm `.git`, `.env`, `data/master` build context'e giriyor
**Dosya:** `(eksik)` repo kökünde
Build context = repo kökü. `.git/`, `catboost_info/`, `.code-review-graph/`, `backend/.env` (eğer secret içeriyorsa), `data/master/raw2value_v4.xlsx` (commercial data), `docs/MASTER_BACKEND_GELISTIRME_RAPORU_PART*.md` — hepsi build cache layer'ında veya pushed builder image'da.
**Aksiyon:** `.dockerignore` oluştur:
```
.git
.github
.venv
**/__pycache__
**/.pytest_cache
catboost_info
.code-review-graph
.claude
**/.env
**/.env.*
*.md
raw2value_ml.egg-info
backend/tests
ml/notebooks/*.ipynb
ml/tests
```

---

## 5. HIGH Bulgular Özeti (29 adet)

### Backend Security (6)
| ID | Bulgu | Dosya | Etki |
|---|---|---|---|
| SEC-F4 | `/api/orgs` listesi tüm KOBİ profil verilerini (credit_score, unit_cost_try_per_ton) auth olmuş herkese veriyor | `api/organizations.py:33-57` | Trade secret exfil |
| SEC-F5 | `asyncio.create_task(save_analyze)` fire-and-forget — shutdown'ta iptal, GC'de kayıp, hata sessizce yutuluyor | `api/analyze.py:108` | Audit trail kaybı + connection pool starvation |
| SEC-F6 | `payload_json` + `response_json` JSONB sonsuza dek, GDPR retention/redaction yok, `DELETE /me` yok | `db/models/analysis.py:62,70` | GDPR Art.5(1)(e) ihlali riski |
| SEC-F7 | CORS `allow_methods=["*"], allow_headers=["*"]` + credentials; `cors_origins_list` validator yok | `main.py:81-87` | Yanlış config'le credentialed CORS açık kalır |
| SEC-F8 | `Content-Security-Policy`, `Permissions-Policy`, `COOP`, `CORP` yok; HSTS sadece prod'da | `core/security_headers.py` | `/docs` Swagger XSS yüzeyi + downgrade |
| SEC-F9 | Custom email regex çok permisif, password kompleksite yok (`hunter22` geçer); F2 ile birlikte brute-force tractable | `schemas/auth.py:16,26` | Account spam + zayıf parola |
| SEC-F10 | Refresh token'da `jti` yok, rotation yok, revocation tablosu yok, logout endpoint yok | `core/security.py:54-61`, `services/auth_service.py:73` | Çalınan refresh 14 gün geçerli |

### API Correctness (6)
| ID | Bulgu | Dosya | Etki |
|---|---|---|---|
| API-F2 | FX `FALLBACK` source ML'e `TCMB_LIVE` etiketiyle geçiyor — CLAUDE.md "no default" ihlali | `services/fx_service.py:21`, `raw2value_ml/fx.py:25`, `api/analyze.py:89` | Audit/UI sahte "live" gösteriyor |
| API-F3 | F&F history insert (SEC-F5 ile aynı) | `api/analyze.py:108` | Audit kaybı |
| API-F4 | 15 vs 10 route surface API'da yok (tek source-of-truth field veya endpoint) | `schemas/analyze.py:44`, `api/evidence.py:13` | UI iki call diff'lemek zorunda; cache mismatch |
| API-F5 | `/api/processors/nearby` (DB-backed) ve `analyze()` (parquet-backed) iki ayrı kaynak | `api/processors.py:17`, `inference.py:305` | Match results vs nearby list divergence |
| API-F6 | `/api/what-if` cevabı `co2_tonnes`, `warnings`, `route_alternatives` düşürüyor | `schemas/analyze.py:69-76` | FE convenience guarantee bozuldu |
| API-F7 | Rate limit user-aware key path ölü kod (`request.state.user_id` set edilmiyor) | `core/rate_limit.py:19`, `deps.py:18` | NAT ardından kullanıcılar quota paylaşıyor |

### ML Pipeline (4)
| ID | Bulgu | Dosya | Etki |
|---|---|---|---|
| ML-F1 | `recommended_route ∈ trained_classes` runtime assert yok | `inference.py:270-302` | Refit drift'i sessizce UI'a sızar |
| ML-F2 | `feature_pipeline.pkl` startup'ta yükleniyor, hiç kullanılmıyor | `inference.py:73-74` | sklearn upgrade → cold-start crash; gereksiz memory |
| ML-F3 | `_FALLBACK_DEFAULTS` `metadata.json` eksikse sessizce maskeliyor; route_classes [] olabilir | `inference.py:76-86` | Boş top-3 alternatives, no diagnostic |
| ML-F4 | `carbon.parquet` `Birim` "kg CO2/ton" (`-km` eksik) | `data/reference/carbon.parquet` | Future re-extraction confusion |

### Tests (7)
| ID | Bulgu | Dosya | Etki |
|---|---|---|---|
| TEST-F2 | K2 ablation invariant testi YOK | `(eksik) test_ablation.py` | FX features kaldırılırsa CI yeşil kalır |
| TEST-F3 | K3 Haversine fallback testi YOK | `(eksik) test_geo.py` | parquet format değişimi sessizce CO₂'yi bozar |
| TEST-F4 | Cross-org / IDOR isolation testi YOK | `tests/test_orgs.py` | SEC-F3/F4 düzelirse de regress yakalanmaz |
| TEST-F5 | `test_history.py` yok; sadece auth-required smoke var | `(eksik)` | Cross-user history isolation, pagination uncovered |
| TEST-F6 | JWT expired/tampered/wrong-secret token testleri yok | `tests/test_auth.py` | Signature verification regression görünmez |
| TEST-F7 | Login user-enumeration negatif testi yok (timing identical assert) | `tests/test_auth.py:62-72` | SEC-F13 ile birleşince enumeration mümkün |
| TEST-F8 | Password reset / role escalation testi yok | `tests/test_auth.py` | Self-promote to admin testlenmemiş |

### DevOps (6)
| ID | Bulgu | Dosya | Etki |
|---|---|---|---|
| DEVOPS-F2 | `secret` DB password compose+config+env.example'da | `docker-compose.yml:10,27`, `config.py:40` | Cloud VM'de exposed Postgres |
| DEVOPS-F3 | Postgres/Redis/MinIO 0.0.0.0'a publish | `docker-compose.yml:14-15,36-37,44-45` | LAN/internet exposure |
| DEVOPS-F4 | Redis `--requirepass` yok | `docker-compose.yml:39-50` | Auth-less Redis |
| DEVOPS-F5 | `JWT_SECRET` insecure default + validator yok | `config.py:33` | Token forge |
| DEVOPS-F6 | `DEMO_ADMIN_PASSWORD=admin123` + `SEED_DEMO_ON_STARTUP=true` (default) | `config.py:93`, `.env.example:74` | Known admin/admin123 in any default deploy |
| DEVOPS-F8 | mypy configured, never invoked; pytest-cov in deps, never used | `.github/workflows/ci.yml:64`, `backend/pyproject.toml:44` | Type contract decay; no coverage signal |

---

## 6. MEDIUM Bulgular Tematik Özet (38 adet)

### Veri/sözleşme drift
- `transport_cost_usd_ton_km` haritası iki dosyada hardcoded — train/inference drift riski (ML-F5).
- `data_confidence_score` augmentation'da [60-95] clip, inference [0-100] — distribution mismatch (ML-F7).
- `_DEFAULT_TARGET_CITY` Literal genişletilirse `None` döner, sessiz 1500 km Haversine fallback (API-F8).
- `fx_scenario_pct` backend ±20% kabul, ML docstring ±10% — extrapolation (API-F9).
- `Numeric(5,2)` confidence_overall, `Numeric(8,4)` value_uplift_pct — boundary risk (API-F10).
- `request_id` String(40), inbound trace-id daha uzun olabilir → silent truncation (API-F11).
- `model_version="v1.0"` iki yerde hardcoded; retrain sonrası yanlış tag (API-F20).

### Asenkron / cache / lifecycle
- `evidence_service.load_evidence` `@lru_cache(maxsize=1)`, mtime invalidation yok — retrain sonrası restart şart (API-F12).
- Evidence missing-file fallback `200 OK + {}` — `503` olmalı (API-F13).
- FX `_parse_fx_date` parse fail'i sessiz `None` (API-F14).
- `total_pages = 0` empty result için → FE pager div-by-zero riski (API-F15).
- Cache stampede: FX TTL boundary'sinde concurrent miss patlaması (SEC-F21).
- Rate limiter Redis bağlantı hatasında sessizce in-memory'ye düşebilir (SEC-F11).

### Reasons / scorer / confidence semantics
- `reasons._safe_format` outer `except Exception` template'i unsubstituted döndürüyor → UI'da `{usd_try:.2f}` (ML-F8).
- `apply_fx_scenario` her zaman `fx_source: "TCMB_LIVE"` — F2'nin altyapı versiyonu (ML-F9).
- `feature_medians.json` 20 key, 15 template feature'ın medianı eksik kalanlar için sürekli "high" branch (ML-F10).
- `geo._norm` substring match — kısa/ambiguous şehirlerde yanlış satır seçimi (ML-F11).

### Test fidelity / isolation
- conftest sqlite default, `requires_postgres` marker hiçbir testte kullanılmıyor — Postgres-spesifik (JSONB, ARRAY, GIN) test edilmiyor (TEST-F9).
- `test_processors` sqlite + haversine; PostGIS path uncovered (TEST-F10).
- ML smoke/e2e testleri `models/*.pkl` (gitignored) bekliyor; CI'da çalışmıyor (TEST-F11, ayrıca CRIT-4).
- `test_analyze.py` warm latency `<500ms`, `test_inference_smoke.py` `<1500ms` — flake risk (TEST-F13, F14).
- `test_emission_factor_deniz` skip'lenebilir; K1 deniz değeri görünmüyor olabilir (TEST-F15).
- `test_quality_grade_distribution` ±5pp tolerance — distribution drift maskeleyebilir (TEST-F16).

### Security misc
- `/metrics` auth'suz expose — internal route + latency leak (SEC-F14).
- `unhandled_exception_handler` 500 sanitized ama AccessLogMiddleware traceback'i full dump — log aggregator leak riski (SEC-F15).
- History sequential `id` enumeration → kullanım pattern fingerprint (SEC-F16).

### DevOps
- Lockfile YOK (`Pipfile.lock`/`poetry.lock` actively gitignored) — transitive drift, pickled model fragility (DEVOPS-F9).
- `models/` gitignored ama Dockerfile `COPY models /app/models` — clean build edilemez (DEVOPS-F10).
- Single gunicorn worker, no `--preload`, no resource limits (DEVOPS-F11).
- Base image tag-only (`python:3.11-slim`) — digest pinning yok (DEVOPS-F12).
- CI image build ediyor ama hiç çalıştırmıyor (no smoke) (DEVOPS-F13).
- Single `/health` endpoint shallow — DB/Redis/model yüklendi mi check yok (DEVOPS-F14).
- `wait_for_db.py` compose lifecycle'da çağrılmıyor (DEVOPS-F16).
- `seed_demo.py` `APP_ENV=production` guard'ı yok (DEVOPS-F17).

---

## 7. OWASP Top 10 (2021) Eşleştirme — Backend

| OWASP | Durum | Notlar |
|---|---|---|
| A01 Broken Access Control | **FAIL** | SEC-F3 (org hijack), F4 (PII listesi), F16 (history enumeration) |
| A02 Cryptographic Failures | **FAIL** | CRIT-1 (default JWT secret), SEC-F10 (refresh rotation/revocation yok) |
| A03 Injection | **PASS** | SQLAlchemy ORM parametrik (SEC-INFO-1) |
| A04 Insecure Design | **PARTIAL** | SEC-F5 F&F audit, F10 refresh, DEVOPS-F6 demo seed default, F11 dead user-key path |
| A05 Security Misconfiguration | **FAIL** | CRIT-1, SEC-F7 (CORS), F8 (no CSP), F14 (open /metrics), DEVOPS-F2/F3/F4 |
| A06 Vulnerable Components | **PARTIAL** | `python-jose==3.3.0` (2021, CVE-2024-33663/64) — exploit edilemez ama eski. `passlib` listed ama unused |
| A07 Auth Failures | **FAIL** | CRIT-2 (rate limit yok), SEC-F9 (weak email/password), F10 (refresh), F13 (timing) |
| A08 Software & Data Integrity | **PASS** | Pinned deps, ML model trusted local path, no dynamic eval |
| A09 Logging & Monitoring | **PARTIAL** | SEC-F6 (PII forever), F14 (/metrics public), F15 (traceback redact yok) |
| A10 SSRF | **PARTIAL** | SEC-F19 — TCMB/ORS base URL env-driven, host allowlist yok |

---

## 8. Test Kapsamı Doğrulama (CLAUDE.md tablosu)

| Dosya | İddia | Gerçek | Durum |
|---|--:|--:|---|
| test_reference_loader.py | 11 | 11 | ✅ |
| test_no_target_leakage.py | 14 | 14 | ✅ |
| test_augmentation_bounds.py | 11 | 11 | ✅ |
| test_reasons.py | 7 | 7 | ✅ |
| test_confidence.py | 8 | 8 | ✅ |
| test_scorer.py | 19 | 19 | ✅ |
| test_inference_smoke.py | 10 | 10 | ✅ |
| test_e2e.py | 8 | 8 | ✅ |
| **ML toplam** | **88** | **88** | ✅ |
| Backend (CLAUDE.md'de yok) | — | 44 | INFO |

Backend test breakdown: test_health=3, test_auth=10, test_fx=7, test_evidence=3, test_analyze=7, test_whatif=3, test_processors=5, test_orgs=6.

**Kritik eksik testler (TEST-F2/F3/F4/F5/F6/F7/F8 toplamı):**
- K2 ablation invariant test
- K3 Haversine fallback test
- Cross-org IDOR test
- test_history.py (cross-user isolation, pagination)
- JWT expired/tampered token testleri
- Login user-enumeration assertion
- Password-reset / role-escalation testleri
- Model retrain reproducibility testi (seed=42 → predictions equal)

---

## 9. Production-Readiness Checklist

| Madde | Durum | Detay |
|---|---|---|
| Non-root container user | ✅ | `useradd -m -u 1000 app && USER app` |
| Pinned base image digest | ❌ | Tag-only `python:3.11-slim` |
| Healthcheck (Dockerfile) | ⚠️ | Var ama shallow (`/health` only) |
| Secrets via env (not commit) | ❌ | `.env.example` çalışan secret yolluyor; defaults insecure |
| DB password non-default | ❌ | `secret` her yerde |
| Redis auth | ❌ | `--requirepass` yok |
| CI runs both test suites | ❌ | Sadece backend; ML 88 test çalışmıyor |
| Lockfile committed | ❌ | `Pipfile.lock`/`poetry.lock` gitignored |
| Lint + type-check in CI | ⚠️ | ruff var, mypy yok |
| Migrations linear & tested | ⚠️ | Linear ✅, down-migration test yok |
| `.env.example` provided | ⚠️ | Var ama çalışan password'lar var |
| `.dockerignore` | ❌ | Yok |
| Resource limits in compose | ❌ | `deploy.resources` yok |
| Readiness vs liveness ayrımı | ❌ | Tek shallow `/health` |
| Prometheus metrics | ✅ | `/metrics` (auth'suz — SEC-F14) |
| Image tested in CI (run, not just build) | ❌ | `backend-docker-build` build edip duruyor |
| CSP / Security headers complete | ❌ | CSP, COOP, CORP yok; HSTS sadece prod |
| Rate limit on auth endpoints | ❌ | `RATE_LIMIT_AUTH_LOGIN` tanımlı, kullanılmıyor |
| GDPR / data retention | ❌ | `analysis_history` sonsuza dek; `DELETE /me` yok |
| Cross-user IDOR tests | ❌ | Yok |

---

## 10. Önerilen Düzeltme Sırası

### Bugün (P0 — hackathon demo öncesi mutlaka)
1. **Rotate JWT_SECRET**, `.env.example`'dan çalışan password'ları çıkar (CHANGEME placeholder), `Settings`'ten default kaldır + startup validator. (CRIT-1, DEVOPS-F5)
2. **Auth endpoint'lere rate limit ekle**: login + register + refresh. (CRIT-2)
3. **POST /api/orgs ownership check** + org listesini admin-gate VEYA public DTO ayrı. (CRIT-3, SEC-F4)
4. **`docker-compose.yml`** — port'ları `127.0.0.1:`'e bağla, `${POSTGRES_PASSWORD:?}`, Redis `--requirepass`. (DEVOPS-F2/F3/F4)
5. **`.dockerignore` oluştur**. (CRIT-5)
6. **`SEED_DEMO_ON_STARTUP=false` default**, `APP_ENV=production` guard `seed_demo.py`'de. (DEVOPS-F6, F17)

### Bu hafta (P1 — pilot öncesi)
7. **CI'a `ml-tests` job'u ekle** — `models/` artifact restore + `pytest ml/tests/`. (CRIT-4)
8. **FX FALLBACK propagation** — `fx_source: "TCMB_FALLBACK"`, `AnalyzeResponse.warnings`'e ekle. (API-F2, ML-F9)
9. **`recommended_route ∈ trained_classes` runtime assert** + regression test. (ML-F1)
10. **`feature_pipeline.pkl` load'ı kaldır** veya try/except'e al. (ML-F2)
11. **Refresh token rotation + revocation tablosu**, logout endpoint. (SEC-F10)
12. **Cross-org IDOR testleri**, JWT expired/tampered testleri, `test_history.py`. (TEST-F4/F5/F6)
13. **`/api/what-if` response'a `co2_tonnes` + `warnings` ekle**. (API-F6)
14. **History F&F → bounded queue VEYA await**. (SEC-F5, API-F3)

### Pilot öncesi (P2)
15. **CSP + COOP + CORP** header'ları, HSTS her zaman. (SEC-F8)
16. **Login constant-time** (dummy bcrypt verify). (SEC-F13)
17. **`analysis_history` retention policy** + `DELETE /me`. (SEC-F6)
18. **K2 ablation + K3 Haversine fallback test**. (TEST-F2/F3)
19. **`evidence_service` mtime invalidation** veya admin reload. (API-F12)
20. **mypy + coverage CI'da**. (DEVOPS-F8)
21. **Lockfile** (`uv pip compile` veya `pip-compile`). (DEVOPS-F9)
22. **Image smoke test** CI'da. (DEVOPS-F13)
23. **Readiness vs liveness ayrımı** (`/health/live`, `/health/ready`). (DEVOPS-F14)

### Yapılabilirse (P3 — backlog)
- `python-jose` → `pyjwt` migration. (SEC-INFO-2)
- Tüm scorer/reasons profil, confidence threshold magic number'larını constant'a çek. (TEST-F17)
- Notebook training → `ml/src/train_*.py` çağrısı. (DEVOPS-F18)
- Test_e2e ↔ test_inference_smoke duplicate cleanup. (TEST-F22)

---

## 11. Risk Heatmap

```
              Etki →
Olasılık ↓    LOW       MEDIUM       HIGH         CRITICAL
HIGH          TEST-F22  ML-F11/F13   API-F2       CRIT-1
              SEC-F23   SEC-F19/F21  API-F4       CRIT-2
                                     ML-F1        CRIT-3
                                     TEST-F2/F3   CRIT-4
MEDIUM        ML-F14    ML-F5/F7/F10 SEC-F4/F5    CRIT-5
              API-F19   API-F8/F12   SEC-F10
                        SEC-F11/F15  API-F6
LOW           DEVOPS-   DEVOPS-      SEC-F8       —
              F18/F22   F11/F12      DEVOPS-F2
                                     DEVOPS-F6
```

---

## 12. Ek — Detay Ajan Çıktıları

Bu rapor 5 paralel uzman ajanın bulgularının konsolidasyonudur. Detaylı evidence'lar ve tam kod alıntıları için ajan transcript'leri çağrılabilir:

- ML pipeline integrity (18 finding) — agent `a01f55e621d6a5eeb`
- Backend security (23 finding) — agent `a6debdb054ec833b6`
- API correctness (22 finding) — agent `ad6df4e3ccf2e05f1`
- Test quality (22 finding) — agent `a362da02c979d03a7`
- DevOps & infra (23 finding) — agent `adf8be5c823cd671e`

---

**Rapor sonu.** Bu rapor read-only analizdir; HİÇBİR koda dokunulmamıştır. Düzeltmeler için P0 → P1 → P2 sırasını takip et; her düzeltme atomic commit olarak `commit-discipline.md` kurallarına uygun yapılmalıdır.
