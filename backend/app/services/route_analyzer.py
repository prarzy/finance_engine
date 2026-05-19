from datetime import datetime
from typing import Any

from fastapi import Depends

from app.core.graph import PaymentGraph, PAYMENT_RAILS
from app.services.fx_service import FXService, get_fx_service
from app.core.exceptions import BadRequestError


class RouteAnalyzer:
    """
    Analyzes payment routes using the multi-hop PaymentGraph.

    For each request:
      1. Fetch live mid-market rate (source → target).
      2. Normalize amount to USD.
      3. Fetch per-method spread estimates.
      4. Build a PaymentGraph and enumerate all routes (up to MAX_HOPS).
      5. Return ranked routes with full step breakdown.
    """

    def __init__(self, fx_service: FXService) -> None:
        self.fx_service = fx_service

    async def analyze(
        self,
        amount: float,
        source_currency: str,
        target_currency: str,
        available_methods: list[str] | None = None,
    ) -> dict[str, Any]:
        source_currency = source_currency.upper()
        target_currency = target_currency.upper()

        if amount <= 0:
            raise BadRequestError("amount must be positive")
        if len(source_currency) != 3 or len(target_currency) != 3:
            raise BadRequestError("Currency codes must be 3 characters")

        # ── 1. Fetch mid-market exchange rate ──────────────────────────────────
        rate = await self.fx_service.get_rate(source_currency, target_currency)

        # ── 2. Normalize to USD ────────────────────────────────────────────────
        if source_currency == "USD":
            amount_usd = amount
        else:
            usd_rate = await self.fx_service.get_rate(source_currency, "USD")
            amount_usd = amount * usd_rate

        # ── 3. Fetch live spreads for each requested method ───────────────────
        methods = available_methods or list(PAYMENT_RAILS.keys())
        live_spreads: dict[str, float] = {}
        for method in methods:
            if method in PAYMENT_RAILS:
                live_spreads[method] = await self.fx_service.get_spread_estimate(method)

        # ── 4. Build graph and enumerate routes ───────────────────────────────
        graph = PaymentGraph(
            amount_usd=amount_usd,
            source_currency=source_currency,
            target_currency=target_currency,
            available_methods=methods,
            live_spreads=live_spreads,
        )

        all_routes = graph.get_all_routes(top_n=10)
        optimal    = graph.get_optimal_route()

        if not optimal or not all_routes:
            raise BadRequestError(
                f"No routes found between {source_currency} and {target_currency} "
                f"with the selected methods. Try enabling more payment methods."
            )

        savings_usd = graph.get_savings_vs_worst(all_routes)
        savings_pct = round((savings_usd / amount_usd) * 100, 4) if amount_usd else 0

        return {
            "amount":               amount,
            "source_currency":      source_currency,
            "target_currency":      target_currency,
            "mid_market_rate":      round(rate, 6),
            "amount_usd":           round(amount_usd, 4),
            "recommended":          optimal,
            "all_routes":           all_routes,
            "savings_vs_worst_usd": savings_usd,
            "savings_vs_worst_pct": savings_pct,
            "timestamp":            datetime.utcnow().isoformat() + "Z",
        }


def get_route_analyzer(fx: FXService = Depends(get_fx_service)) -> RouteAnalyzer:
    """FastAPI dependency to get a RouteAnalyzer instance."""
    return RouteAnalyzer(fx)
