"""
Unit tests for ExplanationService — covering all explanation rules.
"""
import pytest
from app.services.explanation_service import ExplanationService, ConstraintContext, RouteSetMetrics


class TestExplanationService:
    """Test suite for route explanation generation."""

    def test_single_route_generates_minimum_two_explanations(self):
        """Single route should generate at least 2 explanations."""
        route = {
            "total_cost_usd": 10.0,
            "settlement_hours": 24,
            "hop_count": 1,
            "is_recommended": True,
            "steps": [],
        }
        
        explanations = ExplanationService.generate(
            route=route,
            all_routes=[route],
            optimization_mode="cost",
        )
        
        assert len(explanations) >= 2, "Should generate at least 2 explanations"
        assert len(explanations) <= 5, "Should generate at most 5 explanations"
        assert all(isinstance(e, str) for e in explanations), "All explanations should be strings"
        assert len(set(explanations)) == len(explanations), "All explanations should be unique"

    def test_lowest_cost_rule(self):
        """Lowest cost route should get the 'Lowest total cost' explanation."""
        routes = [
            {"total_cost_usd": 5.0, "settlement_hours": 24, "hop_count": 1, "is_recommended": True, "steps": []},
            {"total_cost_usd": 10.0, "settlement_hours": 24, "hop_count": 1, "is_recommended": False, "steps": []},
        ]
        
        explanations = ExplanationService.generate(
            route=routes[0],
            all_routes=routes,
            optimization_mode="cost",
        )
        
        assert any("Lowest total cost" in e for e in explanations), \
            "Should include lowest cost explanation"

    def test_fastest_route_rule(self):
        """Fastest route should get the 'Fastest available' explanation."""
        routes = [
            {"total_cost_usd": 10.0, "settlement_hours": 0, "hop_count": 1, "is_recommended": True, "steps": []},
            {"total_cost_usd": 10.0, "settlement_hours": 24, "hop_count": 1, "is_recommended": False, "steps": []},
        ]
        
        explanations = ExplanationService.generate(
            route=routes[0],
            all_routes=routes,
            optimization_mode="cost",
        )
        
        assert any("Fastest available" in e for e in explanations), \
            "Should include fastest route explanation"

    def test_significant_savings_rule(self):
        """Route saving 20%+ should get savings explanation."""
        routes = [
            {"total_cost_usd": 5.0, "settlement_hours": 24, "hop_count": 1, "is_recommended": True, "steps": []},
            {"total_cost_usd": 25.0, "settlement_hours": 24, "hop_count": 1, "is_recommended": False, "steps": []},
        ]
        
        explanations = ExplanationService.generate(
            route=routes[0],
            all_routes=routes,
            optimization_mode="cost",
        )
        
        assert any("Saves" in e and "%" in e for e in explanations), \
            "Should include savings explanation"

    def test_direct_route_rule(self):
        """Single-hop route should get 'Direct conversion' explanation."""
        route = {
            "total_cost_usd": 10.0,
            "settlement_hours": 24,
            "hop_count": 1,
            "is_recommended": True,
            "steps": [],
        }
        
        explanations = ExplanationService.generate(
            route=route,
            all_routes=[route],
            optimization_mode="cost",
        )
        
        assert any("Direct conversion" in e for e in explanations), \
            "Should include direct conversion explanation"

    def test_few_hops_rule(self):
        """Two-hop route should get 'fewer transfer hops' explanation."""
        routes = [
            {
                "total_cost_usd": 5.0,
                "settlement_hours": 24,
                "hop_count": 2,
                "is_recommended": True,
                "steps": [
                    {"amount_sent": 1000, "fx_cost_usd": 5, "variable_fee_usd": 10},
                    {"amount_sent": 1000, "fx_cost_usd": 5, "variable_fee_usd": 10},
                ],
            },
            {
                "total_cost_usd": 10.0,
                "settlement_hours": 24,
                "hop_count": 3,
                "is_recommended": False,
                "steps": [],
            },
        ]
        
        explanations = ExplanationService.generate(
            route=routes[0],
            all_routes=routes,
            optimization_mode="cost",
        )
        
        assert any("fewer transfer hops" in e for e in explanations), \
            "Should include fewer hops explanation for 2-hop routes"

    def test_multi_hop_advantage_rule(self):
        """Multi-hop cheaper than direct should get advantage explanation."""
        routes = [
            {
                "total_cost_usd": 5.0,
                "settlement_hours": 24,
                "hop_count": 3,
                "is_recommended": True,
                "steps": [],
            },
            {
                "total_cost_usd": 15.0,
                "settlement_hours": 24,
                "hop_count": 1,
                "is_recommended": False,
                "steps": [],
            },
        ]
        
        explanations = ExplanationService.generate(
            route=routes[0],
            all_routes=routes,
            optimization_mode="cost",
        )
        
        assert any("Multi-hop conversion" in e for e in explanations), \
            "Should include multi-hop advantage explanation"

    def test_instant_settlement_rule(self):
        """Route with 0 settlement hours should get instant settlement explanation."""
        route = {
            "total_cost_usd": 10.0,
            "settlement_hours": 0,
            "hop_count": 1,
            "is_recommended": True,
            "steps": [],
        }
        
        explanations = ExplanationService.generate(
            route=route,
            all_routes=[route],
            optimization_mode="cost",
        )
        
        assert any("instant-settlement" in e for e in explanations), \
            "Should include instant settlement explanation"

    def test_faster_than_average_rule(self):
        """Route faster than average should get percentage explanation."""
        routes = [
            {"total_cost_usd": 10.0, "settlement_hours": 12, "hop_count": 1, "is_recommended": True, "steps": []},
            {"total_cost_usd": 10.0, "settlement_hours": 24, "hop_count": 1, "is_recommended": False, "steps": []},
            {"total_cost_usd": 10.0, "settlement_hours": 24, "hop_count": 1, "is_recommended": False, "steps": []},
        ]
        
        explanations = ExplanationService.generate(
            route=routes[0],
            all_routes=routes,
            optimization_mode="cost",
        )
        
        assert any("Settles faster than" in e and "%" in e for e in explanations), \
            "Should include faster than average explanation"

    def test_low_fx_spread_rule(self):
        """Route with low FX spread should get provider quality explanation."""
        routes = [
            {
                "total_cost_usd": 10.0,
                "settlement_hours": 24,
                "hop_count": 1,
                "is_recommended": True,
                "steps": [
                    {"amount_sent": 1000, "fx_cost_usd": 5, "variable_fee_usd": 10},
                ],
            },
            {
                "total_cost_usd": 10.0,
                "settlement_hours": 24,
                "hop_count": 1,
                "is_recommended": False,
                "steps": [
                    {"amount_sent": 1000, "fx_cost_usd": 20, "variable_fee_usd": 10},
                ],
            },
        ]
        
        explanations = ExplanationService.generate(
            route=routes[0],
            all_routes=routes,
            optimization_mode="cost",
        )
        
        assert any("lower foreign exchange spreads" in e for e in explanations), \
            "Should include low FX spread explanation"

    def test_lower_variable_fees_rule(self):
        """Route with lower variable fees should get fee explanation."""
        routes = [
            {
                "total_cost_usd": 10.0,
                "settlement_hours": 24,
                "hop_count": 1,
                "is_recommended": True,
                "steps": [
                    {"amount_sent": 1000, "fx_cost_usd": 5, "variable_fee_usd": 5},
                ],
            },
            {
                "total_cost_usd": 10.0,
                "settlement_hours": 24,
                "hop_count": 1,
                "is_recommended": False,
                "steps": [
                    {"amount_sent": 1000, "fx_cost_usd": 5, "variable_fee_usd": 20},
                ],
            },
        ]
        
        explanations = ExplanationService.generate(
            route=routes[0],
            all_routes=routes,
            optimization_mode="cost",
        )
        
        assert any("percentage-based processing fees" in e for e in explanations), \
            "Should include lower variable fees explanation"

    def test_kyc_filtered_context_rule(self):
        """When KYC routes are filtered, should get context explanation."""
        route = {
            "total_cost_usd": 10.0,
            "settlement_hours": 24,
            "hop_count": 1,
            "is_recommended": True,
            "steps": [],
        }
        
        context = ConstraintContext(kyc_filtered_count=2)
        
        explanations = ExplanationService.generate(
            route=route,
            all_routes=[route],
            optimization_mode="cost",
            constraint_context=context,
        )
        
        assert any("KYC tier" in e for e in explanations), \
            "Should include KYC filter explanation"

    def test_amount_limit_context_rule(self):
        """When amount limits exclude routes, should get context explanation."""
        route = {
            "total_cost_usd": 10.0,
            "settlement_hours": 24,
            "hop_count": 1,
            "is_recommended": True,
            "steps": [],
        }
        
        context = ConstraintContext(amount_filtered_count=3)
        
        explanations = ExplanationService.generate(
            route=route,
            all_routes=[route],
            optimization_mode="cost",
            constraint_context=context,
        )
        
        assert any("transfer amount limits" in e for e in explanations), \
            "Should include amount limit explanation"

    def test_balanced_mode_rule(self):
        """In balanced mode, recommended route should get balanced explanation."""
        route = {
            "total_cost_usd": 10.0,
            "settlement_hours": 24,
            "hop_count": 1,
            "is_recommended": True,
            "steps": [],
        }
        
        explanations = ExplanationService.generate(
            route=route,
            all_routes=[route],
            optimization_mode="balanced",
        )
        
        assert any("balance" in e.lower() for e in explanations), \
            "Should include balanced mode explanation"

    def test_maximum_five_explanations(self):
        """Should never return more than 5 explanations."""
        route = {
            "total_cost_usd": 5.0,
            "settlement_hours": 0,
            "hop_count": 1,
            "is_recommended": True,
            "steps": [
                {"amount_sent": 1000, "fx_cost_usd": 5, "variable_fee_usd": 5},
            ],
        }
        
        routes = [
            route,
            {"total_cost_usd": 25.0, "settlement_hours": 24, "hop_count": 3, "is_recommended": False, "steps": []},
        ]
        
        explanations = ExplanationService.generate(
            route=route,
            all_routes=routes,
            optimization_mode="cost",
            constraint_context=ConstraintContext(kyc_filtered_count=1, amount_filtered_count=1),
        )
        
        assert len(explanations) <= 5, "Should never exceed 5 explanations"

    def test_explanations_are_deterministic(self):
        """Same input should always produce same explanations in same order."""
        route = {
            "total_cost_usd": 10.0,
            "settlement_hours": 24,
            "hop_count": 1,
            "is_recommended": True,
            "steps": [],
        }
        
        routes = [
            route,
            {"total_cost_usd": 15.0, "settlement_hours": 24, "hop_count": 1, "is_recommended": False, "steps": []},
        ]
        
        exp1 = ExplanationService.generate(
            route=route,
            all_routes=routes,
            optimization_mode="cost",
        )
        
        exp2 = ExplanationService.generate(
            route=route,
            all_routes=routes,
            optimization_mode="cost",
        )
        
        assert exp1 == exp2, "Explanations should be deterministic"

    def test_no_duplicate_explanations(self):
        """Returned explanations should be unique."""
        route = {
            "total_cost_usd": 5.0,
            "settlement_hours": 0,
            "hop_count": 1,
            "is_recommended": True,
            "steps": [
                {"amount_sent": 1000, "fx_cost_usd": 5, "variable_fee_usd": 5},
            ],
        }
        
        explanations = ExplanationService.generate(
            route=route,
            all_routes=[route],
            optimization_mode="cost",
        )
        
        assert len(explanations) == len(set(explanations)), \
            "Explanations should be unique (no duplicates)"

    def test_empty_routes_list(self):
        """Should handle empty routes list gracefully."""
        explanations = ExplanationService.generate(
            route={},
            all_routes=[],
            optimization_mode="cost",
        )
        
        assert isinstance(explanations, list), "Should return a list"
