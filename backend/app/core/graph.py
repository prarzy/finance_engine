from typing import Any

import networkx as nx


PAYMENT_RAILS: dict[str, dict[str, Any]] = {
    "bank_transfer": {"fixed_fee": 5.00, "variable_pct": 0.00, "typical_spread": 1.50, "processing_days": 2},
    "credit_card": {"fixed_fee": 0.30, "variable_pct": 2.90, "typical_spread": 2.50, "processing_days": 0},
    "debit_card": {"fixed_fee": 0.30, "variable_pct": 1.50, "typical_spread": 1.80, "processing_days": 0},
    "paypal": {"fixed_fee": 0.30, "variable_pct": 3.49, "typical_spread": 3.00, "processing_days": 0},
    "wise": {"fixed_fee": 0.60, "variable_pct": 0.45, "typical_spread": 0.45, "processing_days": 1},
    "revolut": {"fixed_fee": 0.00, "variable_pct": 0.00, "typical_spread": 0.20, "processing_days": 0},
    "crypto": {"fixed_fee": 1.00, "variable_pct": 0.50, "typical_spread": 0.50, "processing_days": 0},
}


class PaymentGraph:
    """Directed graph representing payment method routing with Dijkstra optimization."""

    def __init__(
        self,
        amount_usd: float,
        source_currency: str,
        target_currency: str,
        live_spreads: dict[str, float] | None = None,
    ) -> None:
        """
        Initialize the payment graph.
        
        Args:
            amount_usd: Amount in USD.
            source_currency: Source currency code.
            target_currency: Target currency code.
            live_spreads: Optional dict mapping method names to live FX spreads.
        """
        self.amount_usd = amount_usd
        self.source_currency = source_currency
        self.target_currency = target_currency
        self.live_spreads = live_spreads or {}
        
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the directed graph of payment methods."""
        self.graph.add_node("SOURCE")
        self.graph.add_node("DESTINATION")

        for method in PAYMENT_RAILS:
            self.graph.add_node(method)
            self.graph.add_edge("SOURCE", method, weight=0)
            
            # Compute total cost edge
            spread = self.live_spreads.get(method, PAYMENT_RAILS[method]["typical_spread"])
            fx_cost = self.amount_usd * (spread / 100)
            fixed_fee = PAYMENT_RAILS[method]["fixed_fee"]
            var_fee = self.amount_usd * (PAYMENT_RAILS[method]["variable_pct"] / 100)
            total_cost = fx_cost + fixed_fee + var_fee
            
            self.graph.add_edge(method, "DESTINATION", weight=total_cost)

    def _route_detail(self, method: str, rank: int, is_recommended: bool) -> dict[str, Any]:
        """
        Compute detailed route information for a payment method.
        
        Args:
            method: Payment method name.
            rank: Route ranking.
            is_recommended: Whether this is the recommended route.
            
        Returns:
            Route detail dict.
        """
        spread = self.live_spreads.get(method, PAYMENT_RAILS[method]["typical_spread"])
        fx_cost = self.amount_usd * (spread / 100)
        fixed_fee = PAYMENT_RAILS[method]["fixed_fee"]
        var_fee = self.amount_usd * (PAYMENT_RAILS[method]["variable_pct"] / 100)
        total_cost = fx_cost + fixed_fee + var_fee

        return {
            "method_name": method,
            "total_cost_usd": round(total_cost, 4),
            "fx_spread_pct": round(spread, 4),
            "fx_cost_usd": round(fx_cost, 4),
            "fixed_fee_usd": round(fixed_fee, 4),
            "variable_fee_pct": round(PAYMENT_RAILS[method]["variable_pct"], 4),
            "variable_fee_usd": round(var_fee, 4),
            "processing_days": PAYMENT_RAILS[method]["processing_days"],
            "rank": rank,
            "is_recommended": is_recommended,
        }

    def get_all_routes(self) -> list[dict[str, Any]]:
        """
        Get all payment routes sorted by cost (lowest first).
        
        Returns:
            List of route detail dicts with ranks assigned.
        """
        routes = []
        for method in PAYMENT_RAILS:
            routes.append(self._route_detail(method, rank=0, is_recommended=False))
        
        # Sort by cost
        routes.sort(key=lambda r: r["total_cost_usd"])
        
        # Assign ranks and mark recommended
        for i, route in enumerate(routes, start=1):
            route["rank"] = i
            route["is_recommended"] = (i == 1)
        
        return routes

    def get_optimal_route(self) -> dict[str, Any]:
        """
        Get the optimal (cheapest) route using Dijkstra's algorithm.
        
        Returns:
            Optimal route detail dict.
        """
        path = nx.dijkstra_path(self.graph, "SOURCE", "DESTINATION", weight="weight")
        method = path[1]
        return self._route_detail(method, rank=1, is_recommended=True)

    def get_savings_vs_worst(self) -> float:
        """
        Calculate savings using the best route vs the worst route.
        
        Returns:
            Savings amount in USD.
        """
        routes = self.get_all_routes()
        return routes[-1]["total_cost_usd"] - routes[0]["total_cost_usd"]
