# Raw2Value AI

Türkiye'nin Kapadokya bölgesindeki üç hammaddeyi (pomza, perlit, kabak çekirdeği) işleyip ihraç etmek için karar destek motoru. Hammadde + tonaj + kalite + hedef pazar girilir → en kârlı işleme rotası, beklenen kâr (TRY), CO₂ ayak izi, alıcı eşleşmesi ve Türkçe gerekçe metni döner.

## 4 ana çıktı (deliverables)

- **Profit Regression Model** (`models/model_profit.pkl`) — `predict_profit(features)`
- **Route Classifier Model** (`models/model_route.pkl`) — `predict_route(features)`
- **B2B Match Scorer + Reason Codes + Confidence** (`raw2value_ml/scorer.py`, `reasons.py`, `confidence.py`)
- **Inference paketi** (`raw2value_ml/`) — `from raw2value_ml import analyze`

## Hızlı kullanım

```python
from raw2value_ml import analyze, AnalyzePayload, LiveFx

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
    live_fx=LiveFx(usd_try=45.05, eur_try=52.67, last_updated="2026-05-02"),
)

response = analyze(payload)
print(response.recommended_route)
print(response.expected_profit_try)
print(response.co2_kg)
for reason in response.reason_codes:
    print("-", reason.text)
```

## Eğitim pipeline (sıfırdan)

```bash
# Linux/Mac
bash scripts/run_full_pipeline.sh

# Windows
pwsh scripts/run_full_pipeline.ps1
```

Veya tek tek notebook çalıştırılabilir:

```bash
jupyter notebook ml/notebooks/01_data_prep.ipynb
jupyter notebook ml/notebooks/02_augmentation.ipynb
jupyter notebook ml/notebooks/03_baselines.ipynb
jupyter notebook ml/notebooks/04_gbm_benchmark.ipynb
jupyter notebook ml/notebooks/05_ablation.ipynb
jupyter notebook ml/notebooks/06_export_artifacts.ipynb
```

## Kurulum

```bash
pip install -e .
```

Python 3.11 gereklidir. Bağımlılıklar `requirements.txt` dosyasında pinli.

## Test

```bash
pytest ml/tests/ -v
```

80+ test, hepsi yeşil olmalıdır.

## Performans hedefi

| Operasyon | Hedef |
|---|---|
| `analyze()` cold start | <2s |
| `analyze()` warm | <500ms |
| `match_buyers()` (top_k=5) | <50ms |

## Sözleşme

Backend tarafıyla `analyze(payload) → AnalyzeResponse` sözleşmesi sabittir. Detay: `docs/master_model_egitim_raporu.md` §11.3.

## Backend (FastAPI)

Tek komutla tüm stack:

```bash
cp backend/.env.example backend/.env
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_demo.py
# → http://localhost:8000/docs
```

Lokal dev (Docker'sız):

```bash
pip install -e .                                          # ML paketi
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
cd backend && uvicorn app.main:app --reload
# Postgres + Redis env'lerini .env'de ayarla
```

QA smoke (G4 gate):

```bash
bash backend/scripts/qa_smoke.sh    # 7/7 OK olmalı
```

Backend test:

```bash
cd backend && pytest tests/ -v
```

### Troubleshooting — Docker

**Port çakışması (5432 / 6379):** Yerel makinede zaten Postgres veya Redis çalışıyorsa `docker compose up` "bind: address already in use" hatası verir. Çözüm — dev override ile host portlarını kaydır:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
# host'tan db: localhost:5433, redis: localhost:6380
# container içinden api: db:5432, redis:6379 (değişmez)
```

Hangi process tutuyor?

```powershell
# Windows
netstat -ano | findstr :5432
Get-Process -Id <PID>
```

```bash
# Linux/Mac
lsof -i :5432
```

**`backend/.env` yok:** İlk kuruluşta `cp backend/.env.example backend/.env` çalıştırılmamış olabilir. `JWT_SECRET` ve `TCMB_EVDS_API_KEY` placeholder kalsa da local dev için yeterlidir; TCMB anahtarı yoksa `/api/fx/current` fallback'e düşer (USD=45, EUR=52).

**`models/*.pkl` Docker imajına alınmamış:** `.dockerignore` dosyasında `*.pkl` satırı varsa kaldır. Build context proje root'u olmalı (`docker-compose.yml`'de `context: .`).

**ML warmup uzun sürüyor:** İlk `docker compose up` sonrası ~20–30 sn bekle; `/health` 503 dönerse `docker compose logs api -f` ile `ml_warmup_complete` mesajını ara.

Detaylı dokümantasyon: `docs/MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md` ve `PART2.md`.
