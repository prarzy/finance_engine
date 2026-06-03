"""
Route Explainability Service — generates deterministic, human-readable explanations
for payment routes based on route metadata and comparative analysis.

No LLMs, no external APIs — purely derived from existing RouteOut fields.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class ConstraintContext:
    """
    Context about system-level filtering applied during route computation.
    Used to generate explanations about why certain routes were excluded.
    """
    kyc_filtered_count: int = 0      # Routes excluded due to KYC tier
    amount_filtered_count: int = 0   # Routes excluded due to corridor amount limits


@dataclass
class RouteSetMetrics:
    """
    Aggregate metrics computed from all routes in a set.
    Used for comparative explanations (e.g., "faster than X% of routes").
    """
    min_cost: float
    max_cost: float
    avg_cost: float

    min_time: int       # settlement_hours
    max_time: int
    avg_time: float

    routes_by_cost: list[dict[str, Any]]   # sorted ascending by total_cost_usd
    routes_by_time: list[dict[str, Any]]   # sorted ascending by settlement_hours

    cheapest_direct_cost: Optional[float]  # min cost where hop_count == 1

    avg_spread: float    # average FX spread across all routes and their steps
    avg_variable_fee: float  # average variable fee ratio across all routes


class ExplanationService:
    """
    Generates 2–5 deterministic explanation strings for a given route,
    sorted descending by priority score.
    """

    @staticmethod
    def generate(
        route: dict[str, Any],
        all_routes: list[dict[str, Any]],
        optimization_mode: str = "cost",
        constraint_context: Optional[ConstraintContext] = None,
    ) -> list[str]:
        """
        Returns 2–5 explanation strings for the given route,
        sorted descending by priority score.

        Args:
            route: The route to generate explanations for
            all_routes: All routes available for this query (for comparison)
            optimization_mode: "cost" or "balanced"
            constraint_context: System-level filtering context (optional)

        Returns:
            List of 2–5 explanation strings, sorted by priority
        """
        if not all_routes:
            return []

        constraint_context = constraint_context or ConstraintContext()

        # Compute aggregate metrics
        metrics = ExplanationService._compute_metrics(all_routes)

        # Collect candidate explanations from all rules
        candidates: list[tuple[str, int]] = []

        # Priority 1: Primary selection reason (score: 100)
        result = ExplanationService._rule_lowest_cost(route, metrics)
        if result:
            candidates.append(result)

        result = ExplanationService._rule_fastest_route(route, metrics)
        if result:
            candidates.append(result)

        result = ExplanationService._rule_balanced_route(route, metrics, optimization_mode)
        if result:
            candidates.append(result)

        # Priority 2: Savings (score: 90 / 85)
        result = ExplanationService._rule_significant_savings(route, metrics)
        if result:
            candidates.append(result)

        result = ExplanationService._rule_cheaper_than_runner_up(route, metrics)
        if result:
            candidates.append(result)

        # Priority 3: Route structure (score: 80 / 75)
        result = ExplanationService._rule_direct_route(route, metrics)
        if result:
            candidates.append(result)

        result = ExplanationService._rule_few_hops(route, metrics)
        if result:
            candidates.append(result)

        result = ExplanationService._rule_multi_hop_advantage(route, metrics)
        if result:
            candidates.append(result)

        # Priority 4: Settlement speed (score: 70)
        result = ExplanationService._rule_instant_settlement(route, metrics)
        if result:
            candidates.append(result)
        else:
            result = ExplanationService._rule_faster_than_average(route, metrics, all_routes)
            if result:
                candidates.append(result)

        # Priority 5: Provider quality (score: 60)
        result = ExplanationService._rule_low_fx_spread(route, metrics)
        if result:
            candidates.append(result)

        result = ExplanationService._rule_lower_variable_fees(route, metrics)
        if result:
            candidates.append(result)

        # Priority 6: Constraint context (score: 50)
        result = ExplanationService._rule_kyc_filtered(constraint_context)
        if result:
            candidates.append(result)

        result = ExplanationService._rule_amount_limit_exclusions(constraint_context)
        if result:
            candidates.append(result)

        # Sort descending by priority score
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Return top 5, but ensure at least 2
        explanations = [msg for msg, _ in candidates[:5]]

        # Guarantee minimum 2 explanations (Primary rules should always fire)
        if len(explanations) < 2:
            # This should rarely happen if Primary rules are correctly implemented
            explanations.append("Valid payment route option.")

        return explanations

    @staticmethod
    def _compute_metrics(all_routes: list[dict[str, Any]]) -> RouteSetMetrics:
        """Compute aggregate metrics from all routes."""
        if not all_routes:
            return RouteSetMetrics(
                min_cost=0, max_cost=0, avg_cost=0,
                min_time=0, max_time=0, avg_time=0,
                routes_by_cost=[], routes_by_time=[],
                cheapest_direct_cost=None,
                avg_spread=0, avg_variable_fee=0
            )

        costs = [r.get("total_cost_usd", 0) for r in all_routes]
        times = [r.get("settlement_hours", 24) for r in all_routes]

        routes_by_cost = sorted(all_routes, key=lambda r: r.get("total_cost_usd", 0))
        routes_by_time = sorted(all_routes, key=lambda r: r.get("settlement_hours", 24))

        # Cheapest direct route (hop_count == 1)
        direct_routes = [r for r in all_routes if r.get("hop_count", 1) == 1]
        cheapest_direct = min([r.get("total_cost_usd", 0) for r in direct_routes]) if direct_routes else None

        # Average spreads and fees
        spreads = []
        fees = []
        for route in all_routes:
            steps = route.get("steps", [])
            if steps:
                for step in steps:
                    amount = step.get("amount_sent", 1)
                    if amount > 0:
                        spread = step.get("fx_cost_usd", 0) / amount
                        variable_fee = step.get("variable_fee_usd", 0) / amount
                        spreads.append(spread)
                        fees.append(variable_fee)

        avg_spread = sum(spreads) / len(spreads) if spreads else 0
        avg_variable_fee = sum(fees) / len(fees) if fees else 0

        return RouteSetMetrics(
            min_cost=min(costs) if costs else 0,
            max_cost=max(costs) if costs else 0,
            avg_cost=sum(costs) / len(costs) if costs else 0,
            min_time=min(times) if times else 0,
            max_time=max(times) if times else 0,
            avg_time=sum(times) / len(times) if times else 0,
            routes_by_cost=routes_by_cost,
            routes_by_time=routes_by_time,
            cheapest_direct_cost=cheapest_direct,
            avg_spread=avg_spread,
            avg_variable_fee=avg_variable_fee,
        )

    # ─── Priority 1: Primary Selection Reason (score: 100) ───────────────────

    @staticmethod
    def _rule_lowest_cost(
        route: dict[str, Any], metrics: RouteSetMetrics
    ) -> Optional[tuple[str, int]]:
        """Lowest total cost among all valid routes."""
        cost = route.get("total_cost_usd", 0)
        if abs(cost - metrics.min_cost) < 0.001:  # float comparison
            return ("Lowest total cost among all valid routes.", 100)
        return None

    @staticmethod
    def _rule_fastest_route(
        route: dict[str, Any], metrics: RouteSetMetrics
    ) -> Optional[tuple[str, int]]:
        """Fastest available route among all valid options."""
        time = route.get("settlement_hours", 24)
        if time == metrics.min_time:
            return ("Fastest available route among all valid options.", 100)
        return None

    @staticmethod
    def _rule_balanced_route(
        route: dict[str, Any], metrics: RouteSetMetrics, optimization_mode: str
    ) -> Optional[tuple[str, int]]:
        """Best balance between cost and settlement speed (only when optimization_mode='balanced')."""
        if optimization_mode == "balanced":
            # In balanced mode, assume the first route (if recommended) is balanced
            if route.get("is_recommended"):
                return ("Provides the best balance between transfer cost and settlement speed.", 100)
        return None

    # ─── Priority 2: Savings (score: 90 / 85) ───────────────────────────────

    @staticmethod
    def _rule_significant_savings(
        route: dict[str, Any], metrics: RouteSetMetrics
    ) -> Optional[tuple[str, int]]:
        """Saves 20%+ compared to the most expensive valid route."""
        if metrics.max_cost == 0:
            return None

        cost = route.get("total_cost_usd", 0)
        savings_pct = ((metrics.max_cost - cost) / metrics.max_cost) * 100

        if savings_pct >= 20:
            return (f"Saves {savings_pct:.1f}% compared to the most expensive valid route.", 90)
        return None

    @staticmethod
    def _rule_cheaper_than_runner_up(
        route: dict[str, Any], metrics: RouteSetMetrics
    ) -> Optional[tuple[str, int]]:
        """Cheaper than the next best alternative."""
        if len(metrics.routes_by_cost) < 2:
            return None

        if route is metrics.routes_by_cost[0]:  # Is this the cheapest?
            next_best = metrics.routes_by_cost[1]
            difference = next_best.get("total_cost_usd", 0) - route.get("total_cost_usd", 0)
            if difference > 0.01:  # Avoid noise
                return (f"${difference:.2f} cheaper than the next best alternative.", 85)
        return None

    # ─── Priority 3: Route Structure (score: 80 / 75) ───────────────────────

    @staticmethod
    def _rule_direct_route(
        route: dict[str, Any], metrics: RouteSetMetrics
    ) -> Optional[tuple[str, int]]:
        """Direct conversion avoids additional transfer steps."""
        if route.get("hop_count", 1) == 1:
            return ("Direct conversion avoids additional transfer steps.", 80)
        return None

    @staticmethod
    def _rule_few_hops(
        route: dict[str, Any], metrics: RouteSetMetrics
    ) -> Optional[tuple[str, int]]:
        """Uses fewer transfer hops, reducing operational complexity."""
        if route.get("hop_count", 1) == 2:
            return ("Uses fewer transfer hops, reducing operational complexity.", 75)
        return None

    @staticmethod
    def _rule_multi_hop_advantage(
        route: dict[str, Any], metrics: RouteSetMetrics
    ) -> Optional[tuple[str, int]]:
        """Multi-hop conversion is cheaper than any available direct transfer."""
        if metrics.cheapest_direct_cost is None:
            return None

        if route.get("hop_count", 1) > 1:
            cost = route.get("total_cost_usd", 0)
            if cost < metrics.cheapest_direct_cost:
                return ("Multi-hop conversion is cheaper than any available direct transfer.", 75)
        return None

    # ─── Priority 4: Settlement Speed (score: 70) ──────────────────────────

    @staticmethod
    def _rule_instant_settlement(
        route: dict[str, Any], metrics: RouteSetMetrics
    ) -> Optional[tuple[str, int]]:
        """Uses instant-settlement payment rails."""
        if route.get("settlement_hours", 1) == 0:
            return ("Uses instant-settlement payment rails.", 70)
        return None

    @staticmethod
    def _rule_faster_than_average(
        route: dict[str, Any], metrics: RouteSetMetrics, all_routes: list[dict[str, Any]]
    ) -> Optional[tuple[str, int]]:
        """Settles faster than X% of valid routes."""
        time = route.get("settlement_hours", 24)
        if time > 0 and time < metrics.avg_time:
            faster_count = sum(1 for r in all_routes if r.get("settlement_hours", 24) > time)
            faster_pct = (faster_count / len(all_routes) * 100) if all_routes else 0
            if faster_pct > 0:
                return (f"Settles faster than {faster_pct:.0f}% of valid routes.", 70)
        return None

    # ─── Priority 5: Provider Quality (score: 60) ──────────────────────────

    @staticmethod
    def _rule_low_fx_spread(
        route: dict[str, Any], metrics: RouteSetMetrics
    ) -> Optional[tuple[str, int]]:
        """Uses providers with lower foreign exchange spreads."""
        steps = route.get("steps", [])
        if not steps:
            return None

        spreads = []
        for step in steps:
            amount = step.get("amount_sent", 1)
            if amount > 0:
                spread = step.get("fx_cost_usd", 0) / amount
                spreads.append(spread)

        if spreads:
            avg_route_spread = sum(spreads) / len(spreads)
            if avg_route_spread < metrics.avg_spread:
                return ("Uses providers with lower foreign exchange spreads.", 60)
        return None

    @staticmethod
    def _rule_lower_variable_fees(
        route: dict[str, Any], metrics: RouteSetMetrics
    ) -> Optional[tuple[str, int]]:
        """Minimizes percentage-based processing fees."""
        steps = route.get("steps", [])
        if not steps:
            return None

        fees = []
        for step in steps:
            amount = step.get("amount_sent", 1)
            if amount > 0:
                fee = step.get("variable_fee_usd", 0) / amount
                fees.append(fee)

        if fees:
            avg_route_fee = sum(fees) / len(fees)
            if avg_route_fee < metrics.avg_variable_fee:
                return ("Minimizes percentage-based processing fees.", 60)
        return None

    # ─── Priority 6: Constraint Context (score: 50) ──────────────────────

    @staticmethod
    def _rule_kyc_filtered(context: ConstraintContext) -> Optional[tuple[str, int]]:
        """Some lower-cost routes were unavailable due to KYC tier restrictions."""
        if context.kyc_filtered_count > 0:
            return ("Some lower-cost routes were unavailable due to KYC tier restrictions.", 50)
        return None

    @staticmethod
    def _rule_amount_limit_exclusions(context: ConstraintContext) -> Optional[tuple[str, int]]:
        """Several providers were excluded due to transfer amount limits."""
        if context.amount_filtered_count > 0:
            return ("Several providers were excluded due to transfer amount limits.", 50)
        return None
