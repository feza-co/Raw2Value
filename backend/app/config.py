"""Uygulama ayarları — pydantic-settings ile .env'den yüklenir.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART1.md §5.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Tüm ortam değişkenleri tek tip-güvenli yerde."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # APP
    APP_NAME: str = "raw2value-ai-backend"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_BASE_URL: str = "http://localhost:8000"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # SECURITY
    JWT_SECRET: str = "change-me-to-a-very-long-random-string-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TTL_MIN: int = 60
    JWT_REFRESH_TTL_DAYS: int = 14
    PASSWORD_HASH_ROUNDS: int = 12

    # DATABASE
    DATABASE_URL: str = "postgresql+asyncpg://raw2value:secret@db:5432/raw2value"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 5

    # REDIS
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_POOL_SIZE: int = 20

    # ML PAKETI
    ML_MODELS_DIR: str = "/app/models"
    ML_DATA_DIR: str = "/app/data"
    ML_WARMUP_ON_STARTUP: bool = True
    ML_RESPONSE_CACHE_TTL_SEC: int = 300

    # TCMB EVDS
    TCMB_EVDS_API_KEY: str = ""
    TCMB_EVDS_BASE_URL: str = "https://evds3.tcmb.gov.tr/service/evds"
    TCMB_FX_CACHE_TTL_SEC: int = 300
    TCMB_TIMEOUT_SEC: int = 10
    TCMB_FALLBACK_USD_TRY: float = 45.0
    TCMB_FALLBACK_EUR_TRY: float = 52.0

    # OPENROUTESERVICE
    ORS_API_KEY: str = ""
    ORS_BASE_URL: str = "https://api.openrouteservice.org"
    ORS_TIMEOUT_SEC: int = 10
    ORS_DISTANCE_CACHE_TTL_SEC: int = 3600

    # FILE STORAGE
    S3_ENABLED: bool = False
    S3_ENDPOINT_URL: str = "http://minio:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "raw2value-uploads"
    S3_REGION: str = "us-east-1"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_ALLOWED_MIME: str = (
        "application/pdf,image/jpeg,image/png"
    )

    # RATE LIMIT
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_ANALYZE: str = "30/minute"
    RATE_LIMIT_FX: str = "60/minute"
    RATE_LIMIT_AUTH_LOGIN: str = "10/minute"

    # OBSERVABILITY
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    PROMETHEUS_ENABLED: bool = True

    # SEED
    SEED_DEMO_ON_STARTUP: bool = False
    DEMO_ADMIN_EMAIL: str = "admin@raw2value.local"
    DEMO_ADMIN_PASSWORD: str = "admin123"

    @property
    def cors_origins_list(self) -> list[str]:
        """`CORS_ORIGINS` string'ini whitelist listesine dönüştürür."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def upload_allowed_mime_set(self) -> frozenset[str]:
        """MIME beyaz listesi — virgülle ayrılmış string'ten."""
        return frozenset(
            m.strip().lower()
            for m in self.UPLOAD_ALLOWED_MIME.split(",")
            if m.strip()
        )

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """Settings cache; modül load sırasında bir kez okunur."""
    return Settings()


settings = get_settings()
