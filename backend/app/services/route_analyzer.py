from datetime import datetime
from typing import Any

from fastapi import Depends

from app.core.graph import PaymentGraph, PAYMENT_RAILS
from app.services.fx_service import FXService, get_fx_service
from app.core.exceptions import BadRequestError


class RouteAnalyzer:
    """Analyzes and ranks payment routes."""

    def __init__(self, fx_service: FXService) -> None:
        self.fx_service = fx_service

    async def analyze(
        self,
        amount: float,
        source_currency: str,
        target_currency: str,
        available_methods: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze payment routes for a transaction.
        
        Args:
            amount: Transaction amount.
            source_currency: Source currency code.
            target_currency: Target currency code.
            available_methods: Optional list of available methods to analyze.
            
        Returns:
            Analysis result dict with recommended route and all alternatives.
            
        Raises:
            BadRequestError: If validation fails.
        """
        source_currency = source_currency.upper()
        target_currency = target_currency.upper()

        # Validate inputs
        if amount <= 0:
            raise BadRequestError("amount must be positive")
        if len(source_currency) != 3 or len(target_currency) != 3:
            raise BadRequestError("Currency codes must be 3 characters")

        # Fetch mid-market rate
        rate = await self.fx_service.get_rate(source_currency, target_currency)

        # Normalize amount to USD
        if source_currency == "USD":
            amount_usd = amount
        else:
            usd_rate = await self.fx_service.get_rate(source_currency, "USD")
            amount_usd = amount * usd_rate

        # Fetch live spreads
        methods = available_methods or list(PAYMENT_RAILS.keys())
        live_spreads: dict[str, float] = {}
        for method in methods:
            live_spreads[method] = await self.fx_service.get_spread_estimate(method)

        # Build graph and analyze
        graph = PaymentGraph(amount_usd, source_currency, target_currency, live_spreads)
        all_routes = graph.get_all_routes()
        optimal = graph.get_optimal_route()
        savings = graph.get_savings_vs_worst()

        return {
            "amount": amount,
            "source_currency": source_currency,
            "target_currency": target_currency,
            "mid_market_rate": round(rate, 6),
            "amount_usd": round(amount_usd, 4),
            "recommended": optimal,
            "all_routes": all_routes,
            "savings_vs_worst_usd": round(savings, 4),
            "savings_vs_worst_pct": round((savings / amount_usd) * 100, 4) if amount_usd else 0,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


def get_route_analyzer(fx: FXService = Depends(get_fx_service)) -> RouteAnalyzer:
    """FastAPI dependency to get RouteAnalyzer instance."""
    return RouteAnalyzer(fx)
