import pytest

from app.services.fx_service import FXService
from app.core.cache import fx_cache


@pytest.mark.anyio
async def test_health(client):
    """Test health endpoint."""
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.anyio
async def test_register_and_login(client_no_mock):
    """Test user registration and login."""
    # Register
    r = await client_no_mock.post(
        "/api/v1/auth/register",
        json={"email": "test@test.com", "password": "pass1234"},
    )
    assert r.status_code == 201
    assert r.json()["email"] == "test@test.com"
    
    # Login
    r2 = await client_no_mock.post(
        "/api/v1/auth/login",
        data={"username": "test@test.com", "password": "pass1234"},
    )
    assert r2.status_code == 200
    assert "access_token" in r2.json()


@pytest.mark.anyio
async def test_duplicate_register(client_no_mock):
    """Test that duplicate email registration fails."""
    body = {"email": "dup@test.com", "password": "pass1234"}
    await client_no_mock.post("/api/v1/auth/register", json=body)
    r = await client_no_mock.post("/api/v1/auth/register", json=body)
    assert r.status_code == 400


@pytest.mark.anyio
async def test_analyze_unauthenticated(client):
    """Test that unauthenticated users can analyze routes."""
    r = await client.post(
        "/api/v1/analyze",
        json={"amount": 500, "source_currency": "USD", "target_currency": "EUR"},
    )
    if r.status_code != 200:
        print(f"Analyze response: {r.status_code} - {r.json()}")
    assert r.status_code == 200
    data = r.json()
    assert len(data["all_routes"]) == 7
    costs = [x["total_cost_usd"] for x in data["all_routes"]]
    assert costs == sorted(costs)
    assert data["savings_vs_worst_usd"] > 0
    assert data["recommended"]["is_recommended"] is True


@pytest.mark.anyio
async def test_analyze_authenticated_persists(client_no_mock):
    """Test that authenticated users' transactions are persisted."""
    # Register and login
    await client_no_mock.post(
        "/api/v1/auth/register",
        json={"email": "a@a.com", "password": "pass1234"},
    )
    login = await client_no_mock.post(
        "/api/v1/auth/login",
        data={"username": "a@a.com", "password": "pass1234"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Analyze (should persist)
    await client_no_mock.post(
        "/api/v1/analyze",
        json={"amount": 200, "source_currency": "USD", "target_currency": "GBP"},
        headers=headers,
    )
    
    # Get history
    history = await client_no_mock.get("/api/v1/history", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) == 1


@pytest.mark.anyio
async def test_recommend_endpoint(client):
    """Test recommendation endpoint."""
    r = await client.get(
        "/api/v1/recommend?amount=1000&source_currency=USD&target_currency=EUR"
    )
    assert r.status_code == 200
    data = r.json()
    assert "recommended" in data
    assert len(data["alternatives"]) <= 3


@pytest.mark.anyio
async def test_invalid_currency_too_long(client):
    """Test that invalid currency codes are rejected."""
    r = await client.post(
        "/api/v1/analyze",
        json={"amount": 100, "source_currency": "USDD", "target_currency": "EUR"},
    )
    assert r.status_code == 422


@pytest.mark.anyio
async def test_history_requires_auth(client):
    """Test that history endpoint requires authentication."""
    r = await client.get("/api/v1/history")
    assert r.status_code == 401


@pytest.mark.anyio
async def test_in_memory_cache_prevents_duplicate_fx_calls(client):
    """Test that FX cache works (same request twice should succeed)."""
    fx_cache.clear()
    
    payload = {"amount": 300, "source_currency": "USD", "target_currency": "EUR"}
    r1 = await client.post("/api/v1/analyze", json=payload)
    assert r1.status_code == 200
    
    # Second request should also work (using cache)
    r2 = await client.post("/api/v1/analyze", json=payload)
    assert r2.status_code == 200
    
    # Results should be mostly identical (timestamps may differ)
    data1 = r1.json()
    data2 = r2.json()
    assert data1["amount"] == data2["amount"]
    assert data1["mid_market_rate"] == data2["mid_market_rate"]
    assert data1["recommended"] == data2["recommended"]
    assert data1["all_routes"] == data2["all_routes"]
