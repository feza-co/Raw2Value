"""Raw2Value AI backend FastAPI uygulamasının giriş noktası.

Bu modül ADIM 0'da iskelet olarak oluşturuldu. Config, logging, middleware,
exception handler, lifespan ve router'lar sonraki adımlarda eklenecek.
"""
from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Raw2Value AI", version="0.1.0")
