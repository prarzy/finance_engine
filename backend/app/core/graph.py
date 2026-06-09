"""
PaymentGraph — builds a directed weighted graph of ONLY valid corridors.
Invalid corridors are never added to the graph.
"""
from __future__ import annotations
import networkx as nx
from typing import Optional
from app.services.constraint_service import ConstraintService

SUPPORTED_CURRENCIES = ["INR", "USD", "EUR", "GBP", "AED", "SGD", "CAD", "AUD", "JPY"]


class PaymentGraph:
    def __init__(self, constraint_service: ConstraintService):
        self.cs = constraint_service
        self.kyc_excluded_count = 0
        self.amount_excluded_count = 0

    def build(
        self,
        source_currency: str,
        target_currency: str,
        amount_usd: float,
        requested_providers: list[str],
        kyc_tier: int = 1,
        fx_rates: dict[str, float] = None,  # {currency: rate_to_usd}
    ) -> nx.DiGraph:
        """
        Build a graph containing ONLY valid, amount-eligible edges.
        Node naming: currency nodes = "USD", method nodes = "wise__USD__EUR"

        Edge rules:
        - currency → method_node: weight=0
        - method_node → currency: weight=total_cost_usd

        Corridors excluded if:
        1. Provider not in requested_providers
        2. corridor not in provider_corridors (not verified/supported)
        3. kyc_tier_required > user's kyc_tier
        4. amount_usd > max_transfer_usd for that corridor step
        """
        G = nx.DiGraph()
        
        # Reset counters for this build
        self.kyc_excluded_count = 0
        self.amount_excluded_count = 0

        # Add all currency nodes
        for currency in SUPPORTED_CURRENCIES:
            G.add_node(currency)

        for provider_slug in requested_providers:
            provider_config = self.cs.get_provider_cost_config(provider_slug)
            if provider_config is None:
                continue  # unknown provider — skip entirely

            # Get all corridors for this provider that are KYC-eligible
            for (p_slug, src, tgt), corridor in self.cs._corridors.items():
                if p_slug != provider_slug:
                    continue
                if corridor.kyc_tier_required > kyc_tier:
                    self.kyc_excluded_count += 1
                    continue  # KYC insufficient — do not add edge

                # Compute per-step cost
                step_cost = self._compute_step_cost(
                    provider_config=provider_config,
                    source_currency=src,
                    target_currency=tgt,
                    amount_usd=amount_usd,
                    fx_rates=fx_rates or {},
                )

                # Amount validation: if amount_usd exceeds max for this corridor step, skip
                if corridor.max_transfer_usd is not None and amount_usd > corridor.max_transfer_usd:
                    self.amount_excluded_count += 1
                    continue  # amount exceeds limit — do not add edge

                if step_cost is None:
                    continue

                method_node = f"{provider_slug}__{src}__{tgt}"
                G.add_node(method_node)
                G.add_edge(src, method_node, weight=0)
                G.add_edge(method_node, tgt, weight=step_cost,
                           provider=provider_slug,
                           from_currency=src,
                           to_currency=tgt,
                           cost=step_cost,
                           fx_cost=amount_usd * (provider_config["fx_spread_pct"] / 100),
                           variable_fee=amount_usd * (provider_config["variable_fee_pct"] / 100),
                           fixed_fee=provider_config["fixed_fee_usd"],
                           fx_spread_pct=provider_config["fx_spread_pct"],
                           variable_fee_pct=provider_config["variable_fee_pct"],
                           settlement_hours=provider_config["settlement_hours"])
                
        return G

    def _compute_step_cost(
        self,
        provider_config: dict,
        source_currency: str,
        target_currency: str,
        amount_usd: float,
        fx_rates: dict,
    ) -> Optional[float]:
        try:
            fx_cost = amount_usd * (provider_config["fx_spread_pct"] / 100)
            variable_fee = amount_usd * (provider_config["variable_fee_pct"] / 100)
            fixed_fee = provider_config["fixed_fee_usd"]
            return fx_cost + variable_fee + fixed_fee
        except Exception:
            return None

    def find_optimal_route(
        self,
        G: nx.DiGraph,
        source_currency: str,
        target_currency: str,
    ) -> Optional[list[str]]:
        try:
            return nx.dijkstra_path(G, source_currency, target_currency, weight="weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def find_all_routes(
        self,
        G: nx.DiGraph,
        source_currency: str,
        target_currency: str,
        max_hops: int = 3,
    ) -> list[list[str]]:
        try:
            paths = list(nx.all_simple_paths(G, source_currency, target_currency,
                                              cutoff=max_hops * 2))  # *2 because method nodes count
            return sorted(paths, key=lambda p: self._path_cost(G, p))[:10]
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def _path_cost(self, G: nx.DiGraph, path: list[str]) -> float:
        total = 0.0
        for i in range(len(path) - 1):
            data = G.get_edge_data(path[i], path[i+1])
            if data:
                total += data.get("weight", 0)
        return total

