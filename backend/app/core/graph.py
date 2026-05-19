"""
graph.py — Multi-hop payment routing engine.

Graph structure (bipartite: currency nodes ↔ method-instance nodes):
  Currency nodes : "USD", "EUR", "INR", "GBP", "AED"
  Method nodes   : "wise__USD__EUR", "revolut__USD__EUR", ...

Edges:
  currency → method_instance   weight=0          (enter the rail)
  method_instance → currency   weight=total_cost  (exit the rail, paying fees)

This allows Dijkstra / all_simple_paths to find multi-hop routes naturally:
  INR → bank_transfer__INR__USD → USD → revolut__USD__EUR → EUR
"""

from __future__ import annotations

from typing import Any

import networkx as nx

# ── Separator used in method-instance node IDs ────────────────────────────────
SEP = "__"

# ── Maximum rail hops (1 hop = 1 method used) ────────────────────────────────
MAX_HOPS = 3
# max nodes in a valid path = source_currency + MAX_HOPS*(method_node+currency)
MAX_PATH_NODES = 1 + MAX_HOPS * 2

# ── Payment rail definitions ───────────────────────────────────────────────────
# Each rail declares which (src, tgt) currency pairs it supports.
# Costs are: fixed_fee (USD) + variable_pct (% of amount_usd) + FX spread.
PAYMENT_RAILS: dict[str, dict[str, Any]] = {
    "bank_transfer": {
        "fixed_fee": 5.00,
        "variable_pct": 0.00,
        "typical_spread": 1.50,
        "processing_days": 2,
        "supported_pairs": [
            ("USD", "EUR"), ("USD", "GBP"), ("USD", "INR"), ("USD", "AED"),
            ("EUR", "USD"), ("EUR", "GBP"), ("EUR", "INR"),
            ("GBP", "USD"), ("GBP", "EUR"),
            ("INR", "USD"), ("INR", "EUR"),
            ("AED", "USD"),
        ],
    },
    "credit_card": {
        "fixed_fee": 0.30,
        "variable_pct": 2.90,
        "typical_spread": 2.50,
        "processing_days": 0,
        "supported_pairs": [
            ("USD", "EUR"), ("USD", "GBP"), ("USD", "INR"),
            ("EUR", "USD"), ("GBP", "USD"), ("INR", "USD"),
        ],
    },
    "debit_card": {
        "fixed_fee": 0.30,
        "variable_pct": 1.50,
        "typical_spread": 1.80,
        "processing_days": 0,
        "supported_pairs": [
            ("USD", "EUR"), ("USD", "GBP"), ("USD", "INR"),
            ("EUR", "USD"), ("GBP", "USD"), ("INR", "USD"),
        ],
    },
    "paypal": {
        "fixed_fee": 0.30,
        "variable_pct": 3.49,
        "typical_spread": 3.00,
        "processing_days": 0,
        "supported_pairs": [
            ("USD", "EUR"), ("USD", "GBP"),
            ("EUR", "USD"), ("GBP", "USD"), ("INR", "USD"),
        ],
    },
    "wise": {
        "fixed_fee": 0.60,
        "variable_pct": 0.45,
        "typical_spread": 0.45,
        "processing_days": 1,
        "supported_pairs": [
            ("USD", "EUR"), ("USD", "GBP"), ("USD", "INR"), ("USD", "AED"),
            ("EUR", "USD"), ("EUR", "GBP"), ("EUR", "INR"),
            ("GBP", "USD"), ("GBP", "EUR"),
            ("INR", "USD"), ("INR", "EUR"),
            ("AED", "USD"),
        ],
    },
    "revolut": {
        "fixed_fee": 0.00,
        "variable_pct": 0.00,
        "typical_spread": 0.20,
        "processing_days": 0,
        "supported_pairs": [
            ("USD", "EUR"), ("USD", "GBP"), ("USD", "INR"), ("USD", "AED"),
            ("EUR", "USD"), ("EUR", "GBP"), ("EUR", "INR"),
            ("GBP", "USD"), ("GBP", "EUR"),
            ("INR", "USD"),
        ],
    },
    "crypto": {
        "fixed_fee": 1.00,
        "variable_pct": 0.50,
        "typical_spread": 0.50,
        "processing_days": 0,
        "supported_pairs": [
            ("USD", "EUR"), ("USD", "GBP"), ("USD", "INR"),
            ("EUR", "USD"), ("GBP", "USD"), ("INR", "USD"),
        ],
    },
}


# ── Node ID helpers ───────────────────────────────────────────────────────────

def method_node_id(method: str, src: str, tgt: str) -> str:
    """Build a unique node ID for a method-instance edge."""
    return f"{method}{SEP}{src}{SEP}{tgt}"


def parse_method_node(node: str) -> tuple[str, str, str]:
    """Parse 'wise__USD__EUR' → ('wise', 'USD', 'EUR')."""
    parts = node.split(SEP, 2)
    return parts[0], parts[1], parts[2]


def is_method_node(node: str) -> bool:
    return SEP in node


# ── Graph ─────────────────────────────────────────────────────────────────────

class PaymentGraph:
    """
    Multi-hop directed payment routing graph.

    Build once per request (costs are amount-dependent).
    Use get_all_routes() for a ranked list of paths.
    Use get_optimal_route() for Dijkstra's cheapest single path.
    """

    def __init__(
        self,
        amount_usd: float,
        source_currency: str,
        target_currency: str,
        available_methods: list[str] | None = None,
        live_spreads: dict[str, float] | None = None,
    ) -> None:
        self.amount_usd = amount_usd
        self.source_currency = source_currency.upper()
        self.target_currency = target_currency.upper()
        self.available_methods: set[str] = set(
            available_methods or PAYMENT_RAILS.keys()
        )
        self.live_spreads: dict[str, float] = live_spreads or {}
        self.graph: nx.DiGraph = nx.DiGraph()
        self._build_graph()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _step_costs(self, method: str, amount_usd: float) -> dict[str, float]:
        """Compute per-step cost breakdown for a given method and amount."""
        rail = PAYMENT_RAILS[method]
        spread = self.live_spreads.get(method, rail["typical_spread"])
        fx_cost      = amount_usd * (spread / 100)
        fixed_fee    = rail["fixed_fee"]
        variable_fee = amount_usd * (rail["variable_pct"] / 100)
        total        = fx_cost + fixed_fee + variable_fee
        return {
            "fx_spread_pct":    round(spread, 4),
            "fx_cost_usd":      round(fx_cost, 4),
            "fixed_fee_usd":    round(fixed_fee, 4),
            "variable_fee_pct": round(rail["variable_pct"], 4),
            "variable_fee_usd": round(variable_fee, 4),
            "total_cost_usd":   round(total, 4),
            "processing_days":  rail["processing_days"],
        }

    def _build_graph(self) -> None:
        """
        Add bipartite edges for every (method, src_currency, tgt_currency) triple.
        Each hop uses the full amount_usd for cost calculation (conservative upper bound).
        """
        for method, rail in PAYMENT_RAILS.items():
            if method not in self.available_methods:
                continue
            costs = self._step_costs(method, self.amount_usd)
            for src, tgt in rail["supported_pairs"]:
                mn = method_node_id(method, src, tgt)
                # Enter: currency → method_instance (zero cost)
                self.graph.add_edge(
                    src, mn,
                    weight=0,
                    method=method,
                    from_currency=src,
                    to_currency=tgt,
                    **costs,
                )
                # Exit: method_instance → currency (carries the cost)
                self.graph.add_edge(
                    mn, tgt,
                    weight=costs["total_cost_usd"],
                    method=method,
                    from_currency=src,
                    to_currency=tgt,
                    **costs,
                )

    def _path_to_route(
        self, path: list[str], rank: int, is_recommended: bool
    ) -> dict[str, Any]:
        """Convert a raw graph path into a structured route dict."""
        steps: list[dict[str, Any]] = []
        total_cost = 0.0
        max_days = 0

        for node in path:
            if not is_method_node(node):
                continue
            method, src, tgt = parse_method_node(node)
            # Edge data lives on method_instance → tgt_currency
            data = self.graph.edges[node, tgt]
            step = {
                "from_currency":    src,
                "method":           method,
                "to_currency":      tgt,
                "fx_spread_pct":    data["fx_spread_pct"],
                "fx_cost_usd":      data["fx_cost_usd"],
                "fixed_fee_usd":    data["fixed_fee_usd"],
                "variable_fee_pct": data["variable_fee_pct"],
                "variable_fee_usd": data["variable_fee_usd"],
                "step_cost_usd":    data["total_cost_usd"],
                "processing_days":  data["processing_days"],
            }
            steps.append(step)
            total_cost += data["total_cost_usd"]
            max_days = max(max_days, data["processing_days"])

        hop_count = len(steps)
        currency_path = [n for n in path if not is_method_node(n)]

        # Aggregate totals
        total_fx_cost      = sum(s["fx_cost_usd"]      for s in steps)
        total_fixed_fee    = sum(s["fixed_fee_usd"]    for s in steps)
        total_variable_fee = sum(s["variable_fee_usd"] for s in steps)

        # Backward-compatible method_name: use method for single-hop, "multi_hop" otherwise
        method_name = steps[0]["method"] if hop_count == 1 else "multi_hop"
        first = steps[0] if steps else {}

        return {
            # ── Backward-compatible fields ──
            "method_name":      method_name,
            "total_cost_usd":   round(total_cost, 4),
            "fx_spread_pct":    first.get("fx_spread_pct", 0) if hop_count == 1 else 0,
            "fx_cost_usd":      round(total_fx_cost, 4),
            "fixed_fee_usd":    round(total_fixed_fee, 4),
            "variable_fee_pct": first.get("variable_fee_pct", 0) if hop_count == 1 else 0,
            "variable_fee_usd": round(total_variable_fee, 4),
            "processing_days":  max_days,
            "rank":             rank,
            "is_recommended":   is_recommended,
            # ── Multi-hop fields ──
            "path":             path,
            "currency_path":    currency_path,
            "steps":            steps,
            "hop_count":        hop_count,
        }

    # ── Public API ────────────────────────────────────────────────────────────

    def get_all_routes(self, top_n: int = 10) -> list[dict[str, Any]]:
        """
        Enumerate all simple paths from source_currency to target_currency
        up to MAX_HOPS rail hops. Returns top_n routes sorted by total cost.
        """
        src, tgt = self.source_currency, self.target_currency
        if src == tgt or not self.graph.has_node(src) or not self.graph.has_node(tgt):
            return []

        try:
            raw_paths = list(
                nx.all_simple_paths(self.graph, src, tgt, cutoff=MAX_PATH_NODES)
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

        # Validate: must alternate currency→method→currency...
        valid: list[tuple[float, list[str]]] = []
        for path in raw_paths:
            if len(path) < 3 or len(path) % 2 == 0:
                continue
            ok = all(
                (i % 2 == 0) != is_method_node(n)   # even=currency, odd=method
                for i, n in enumerate(path)
            )
            if not ok:
                continue
            cost = nx.path_weight(self.graph, path, weight="weight")
            valid.append((cost, path))

        if not valid:
            return []

        valid.sort(key=lambda x: x[0])
        routes = []
        for rank, (_, path) in enumerate(valid[:top_n], start=1):
            routes.append(self._path_to_route(path, rank=rank, is_recommended=(rank == 1)))
        return routes

    def get_optimal_route(self) -> dict[str, Any] | None:
        """Return the single cheapest route using Dijkstra's algorithm."""
        try:
            path = nx.dijkstra_path(
                self.graph, self.source_currency, self.target_currency, weight="weight"
            )
            return self._path_to_route(path, rank=1, is_recommended=True)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def get_savings_vs_worst(self, routes: list[dict[str, Any]]) -> float:
        if len(routes) < 2:
            return 0.0
        return round(routes[-1]["total_cost_usd"] - routes[0]["total_cost_usd"], 4)
