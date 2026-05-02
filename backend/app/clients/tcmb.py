"""TCMB EVDS client — günlük USD/EUR alış kuru.

Tenacity ile 3 deneme exponential backoff. Hata durumunda servis katmanı
(`fx_service.get_current_fx`) fallback'a düşer.

Kaynak: MASTER_BACKEND_GELISTIRME_RAPORU_PART2.md §10.1.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..config import settings


class TcmbError(Exception):
    """TCMB EVDS çağrısı 3 denemeden sonra başarısız oldu."""


class TcmbClient:
    """EVDS'den USD/TRY ve EUR/TRY günlük kuru alır."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.TCMB_EVDS_API_KEY
        self.base_url = (base_url or settings.TCMB_EVDS_BASE_URL).rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            timeout=timeout if timeout is not None else settings.TCMB_TIMEOUT_SEC
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=0.5, max=4),
        retry=retry_if_exception_type((httpx.HTTPError, TcmbError)),
        reraise=True,
    )
    async def get_fx(self) -> dict[str, Any]:
        """USD/TRY ve EUR/TRY için son günün kapanışını döner.

        Returns:
            `{"usd_try": float, "eur_try": float, "last_updated": "DD-MM-YYYY"}`

        Raises:
            TcmbError — yanıt eksik/parse edilemezse.
        """
        today = datetime.now(timezone.utc).date()
        # Hafta sonu / tatilde son veri T-1 ya da daha eski olabilir.
        start = today - timedelta(days=10)
        params = {
            "series": "TP.DK.USD.A.YTL-TP.DK.EUR.A.YTL",
            "startDate": start.strftime("%d-%m-%Y"),
            "endDate": today.strftime("%d-%m-%Y"),
            "type": "json",
            "key": self.api_key,
        }
        url = f"{self.base_url}/series"
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get("items") or []
        if not items:
            raise TcmbError("TCMB items boş döndü")

        # En yeni veri en sonda; tutar None olabilir (tatil günleri).
        last_valid = next(
            (
                row
                for row in reversed(items)
                if row.get("TP_DK_USD_A_YTL") and row.get("TP_DK_EUR_A_YTL")
            ),
            None,
        )
        if last_valid is None:
            raise TcmbError("Son 10 günde geçerli kur bulunamadı")

        try:
            usd_try = float(last_valid["TP_DK_USD_A_YTL"])
            eur_try = float(last_valid["TP_DK_EUR_A_YTL"])
        except (TypeError, ValueError) as exc:
            raise TcmbError(f"Kur değeri parse edilemedi: {exc}") from exc

        return {
            "usd_try": usd_try,
            "eur_try": eur_try,
            "last_updated": last_valid.get("Tarih") or today.strftime("%d-%m-%Y"),
        }
