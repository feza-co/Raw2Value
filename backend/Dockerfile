# syntax=docker/dockerfile:1.6
# Raw2Value AI backend multi-stage Dockerfile.
# Build context: repo root (raw2value_ml ve models/data buradan kopyalanır).
# Build:    docker build -f backend/Dockerfile -t raw2value-backend .

# ---- builder ----
FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /build/requirements.txt
RUN pip wheel --wheel-dir /wheels -r /build/requirements.txt

# ---- runtime ----
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq5 curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/*.whl \
 && rm -rf /wheels

# ML paketi + artefactler (pickled modeller ml/* import edebilsin)
COPY raw2value_ml /app/raw2value_ml
COPY ml /app/ml
COPY models /app/models
COPY data /app/data

# Backend kodu
COPY backend/app /app/app
COPY backend/alembic /app/alembic
COPY backend/alembic.ini /app/alembic.ini
COPY backend/scripts /app/scripts

# Non-root user
RUN useradd -m -u 1000 app && chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["python", "scripts/healthcheck.py"]

CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "1", \
     "-b", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--timeout", "60"]
