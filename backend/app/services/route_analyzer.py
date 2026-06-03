from datetime import datetime
from typing import Any

from fastapi import Depends
import networkx as nx

from app.core.graph import PaymentGraph
from app.services.constraint_service import constraint_service
from app.services.explanation_service import ExplanationService, ConstraintContext
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

        # ── 3. Get available providers from constraint service ──────────────────
        # For now, use all active providers if available_methods is not specified
        if available_methods is None:
            available_methods = ["wise", "revolut", "bank_transfer", "paypal"]
        else:
            # Filter to only valid providers
            available_methods = [m for m in available_methods if m in ["wise", "revolut", "bank_transfer", "paypal"]]

        # ── 4. Build constraint-based graph and find routes ──────────────────
        graph_engine = PaymentGraph(constraint_service)
        graph = graph_engine.build(
            source_currency=source_currency,
            target_currency=target_currency,
            amount_usd=amount_usd,
            requested_providers=available_methods,
            kyc_tier=2,  # TODO: get from current user
            fx_rates={},
        )

        # Find optimal and all routes
        optimal_path = graph_engine.find_optimal_route(graph, source_currency, target_currency)
        all_paths = graph_engine.find_all_routes(graph, source_currency, target_currency, max_hops=3)

        if not optimal_path or not all_paths:
            raise BadRequestError(
                f"No routes found between {source_currency} and {target_currency} "
                f"with the selected methods. Try enabling more payment methods."
            )

        # Convert paths to route dicts
        optimal = self._path_to_route_dict(optimal_path, graph, source_currency, target_currency, 1, True)
        all_routes = []
        for rank, path in enumerate(all_paths[:10], start=1):
            all_routes.append(self._path_to_route_dict(path, graph, source_currency, target_currency, rank, rank == 1))

        # ── Generate explanations for recommended route only ──────────────────
        constraint_ctx = ConstraintContext(
            kyc_filtered_count=graph_engine.kyc_excluded_count,
            amount_filtered_count=graph_engine.amount_excluded_count,
        )

        # Add explanations to optimal/recommended route only
        optimal["explanations"] = ExplanationService.generate(
            route=optimal,
            all_routes=all_routes,
            optimization_mode="cost",
            constraint_context=constraint_ctx,
        )

        # Ensure alternate routes have empty explanations
        for route in all_routes:
            route["explanations"] = []

        # Calculate savings
        if len(all_routes) < 2:
            savings_usd = 0.0
        else:
            savings_usd = round(all_routes[-1]["total_cost_usd"] - all_routes[0]["total_cost_usd"], 4)
        
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

    def _path_to_route_dict(
        self,
        path: list[str],
        graph: nx.DiGraph,
        source: str,
        target: str,
        rank: int,
        is_recommended: bool,
    ) -> dict[str, Any]:
        """Convert a NetworkX path to a route dict."""
        total_cost = 0.0
        max_days = 0
        max_settlement_hours = 0
        steps = []
        method_name = "unknown"
        
        # Calculate costs from edges
        for i in range(len(path) - 1):
            edge_data = graph.get_edge_data(path[i], path[i+1])
            if edge_data is None:
                continue
            
            weight = edge_data.get("weight", 0)
            total_cost += weight
            settlement = edge_data.get("settlement_hours", 0)
            max_days = max(max_days, settlement // 24 if settlement else 0)
            max_settlement_hours = max(max_settlement_hours, settlement)
            
            # Extract method name from method nodes
            if "__" in path[i+1]:  # This is a method node
                parts = path[i+1].split("__")
                if len(parts) >= 3:
                    method_name = parts[0]
        
        hop_count = len([n for n in path if "__" in n])
        
        # For single-hop, use the provider method name
        if hop_count == 1:
            for n in path:
                if "__" in n:
                    parts = n.split("__")
                    method_name = parts[0]
        else:
            method_name = "multi_hop"
        
        return {
            "method_name": method_name,
            "total_cost_usd": round(total_cost, 4),
            "fx_spread_pct": 0,
            "fx_cost_usd": 0,
            "fixed_fee_usd": 0,
            "variable_fee_pct": 0,
            "variable_fee_usd": 0,
            "processing_days": max_days,
            "settlement_hours": max_settlement_hours,
            "rank": rank,
            "is_recommended": is_recommended,
            "path": path,
            "currency_path": [n for n in path if "__" not in n],
            "steps": steps,
            "hop_count": hop_count,
        }


def get_route_analyzer(fx: FXService = Depends(get_fx_service)) -> RouteAnalyzer:
    """FastAPI dependency to get a RouteAnalyzer instance."""
    return RouteAnalyzer(fx)
