import pytest

from app.core.graph import PaymentGraph, PAYMENT_RAILS
from app.core.security import get_password_hash, verify_password


def test_password_hashing():
    """Test that password hashing and verification work correctly."""
    password = "pass1234"
    hashed = get_password_hash(password)
    assert isinstance(hashed, str)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpass", hashed)


def test_all_routes_returns_seven_methods():
    """Test that all seven payment methods are returned."""
    routes = PaymentGraph(1000, "USD", "EUR").get_all_routes()
    assert len(routes) == 7


def test_routes_sorted_ascending():
    """Test that routes are sorted by cost (ascending)."""
    routes = PaymentGraph(1000, "USD", "EUR").get_all_routes()
    costs = [r["total_cost_usd"] for r in routes]
    assert costs == sorted(costs)


def test_optimal_is_cheapest():
    """Test that optimal route matches the cheapest route."""
    g = PaymentGraph(1000, "USD", "EUR")
    optimal = g.get_optimal_route()
    cheapest = g.get_all_routes()[0]
    assert optimal["total_cost_usd"] == cheapest["total_cost_usd"]


def test_savings_positive():
    """Test that savings is positive (difference between worst and best)."""
    savings = PaymentGraph(1000, "USD", "EUR").get_savings_vs_worst()
    assert savings > 0


def test_revolut_cheapest_when_all_spreads_zero():
    """Test that Revolut is cheapest when all spreads are zero."""
    spreads = {m: 0.0 for m in PAYMENT_RAILS}
    g = PaymentGraph(1000, "USD", "EUR", live_spreads=spreads)
    optimal = g.get_optimal_route()
    assert optimal["method_name"] == "revolut"


def test_wise_cost_formula():
    """Test that Wise costs are calculated correctly."""
    amount = 1000.0
    spread = 0.45
    expected = amount * (spread / 100) + 0.60 + amount * (0.45 / 100)
    
    g = PaymentGraph(amount, "USD", "EUR", live_spreads={"wise": spread})
    wise = next(r for r in g.get_all_routes() if r["method_name"] == "wise")
    
    assert abs(wise["total_cost_usd"] - expected) < 0.01


def test_ranks_assigned_correctly():
    """Test that ranks are assigned 1 through 7."""
    routes = PaymentGraph(500, "USD", "GBP").get_all_routes()
    ranks = [r["rank"] for r in routes]
    assert ranks == list(range(1, 8))


def test_only_one_recommended():
    """Test that only the first (cheapest) route is marked as recommended."""
    routes = PaymentGraph(500, "USD", "GBP").get_all_routes()
    recommended_count = sum(1 for r in routes if r["is_recommended"])
    assert recommended_count == 1
    assert routes[0]["is_recommended"] is True
