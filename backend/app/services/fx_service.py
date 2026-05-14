from typing import Any

import httpx
from fastapi import Depends

from app.core.config import settings as default_settings
from app.core.config import get_settings, Settings
from app.core.cache import fx_cache
from app.core.exceptions import ServiceUnavailableError


class FXService:
    """Foreign exchange rate service with caching and fallback endpoints."""

    SPREAD_BY_METHOD: dict[str, float] = {
        "bank_transfer": 1.5,
        "credit_card": 2.5,
        "debit_card": 1.8,
        "paypal": 3.0,
        "wise": 0.45,
        "revolut": 0.2,
        "crypto": 0.5,
    }

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def get_rate(self, base: str, target: str) -> float:
        """
        Fetch exchange rate between two currencies.
        
        Uses in-memory cache with TTL. Tries primary API first (ExchangeRate-API),
        falls back to Frankfurter API.
        
        Args:
            base: Source currency code.
            target: Target currency code.
            
        Returns:
            Exchange rate (target per base).
            
        Raises:
            ServiceUnavailableError: If all APIs fail.
        """
        if base == target:
            return 1.0

        base = base.upper()
        target = target.upper()
        cache_key = f"fx:{base}:{target}"

        cached = fx_cache.get(cache_key)
        if cached:
            return float(cached)

        rate: float | None = None

        # Primary API
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"https://v6.exchangerate-api.com/v6/{self.settings.EXCHANGERATE_API_KEY}/pair/{base}/{target}"
                )
                if response.status_code == 200:
                    data = response.json()
                    rate = data["conversion_rate"]
        except Exception:
            pass

        # Fallback API
        if rate is None:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(
                        f"https://api.frankfurterapp.org/latest?from={base}&to={target}"
                    )
                    if response.status_code == 200:
                        data = response.json()
                        rate = data["rates"][target]
            except Exception:
                pass

        if rate is None:
            raise ServiceUnavailableError("FX rates unavailable")

        fx_cache.set(cache_key, str(rate), self.settings.FX_CACHE_TTL_SECONDS)
        return rate

    async def get_spread_estimate(self, method: str) -> float:
        """
        Get the FX spread estimate for a payment method.
        
        Args:
            method: Payment method name.
            
        Returns:
            FX spread percentage.
        """
        return self.SPREAD_BY_METHOD.get(method, 2.0)


def get_fx_service(settings: Settings = Depends(get_settings)) -> FXService:
    """FastAPI dependency to get FXService instance."""
    return FXService(settings)
