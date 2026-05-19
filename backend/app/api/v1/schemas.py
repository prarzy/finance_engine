from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ── Request schemas ────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """Request model for payment route analysis."""
    amount: float = Field(gt=0)
    source_currency: str = Field(min_length=3, max_length=3)
    target_currency: str = Field(min_length=3, max_length=3)
    available_methods: list[str] | None = None

    @field_validator("source_currency", "target_currency", mode="before")
    @classmethod
    def uppercase_currency(cls, v: str) -> str:
        return v.upper()


class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr
    password: str = Field(min_length=8)


# ── Multi-hop route step ───────────────────────────────────────────────────────

class RouteStepOut(BaseModel):
    """A single hop in a multi-hop route."""
    from_currency: str
    method: str
    to_currency: str
    fx_spread_pct: float
    fx_cost_usd: float
    fixed_fee_usd: float
    variable_fee_pct: float
    variable_fee_usd: float
    step_cost_usd: float
    processing_days: int


# ── Route response ─────────────────────────────────────────────────────────────

class RouteOut(BaseModel):
    """
    Payment route response — backward-compatible with single-hop usage,
    extended with multi-hop path and steps.
    """
    model_config = ConfigDict(from_attributes=True)

    # ── Backward-compatible fields (always present) ──
    method_name: str
    total_cost_usd: float
    fx_spread_pct: float
    fx_cost_usd: float
    fixed_fee_usd: float
    variable_fee_pct: float
    variable_fee_usd: float
    processing_days: int
    rank: int
    is_recommended: bool

    # ── Multi-hop fields (present for all routes, hop_count=1 for single-hop) ──
    hop_count: int = 1
    path: list[str] = Field(default_factory=list)
    currency_path: list[str] = Field(default_factory=list)
    steps: list[RouteStepOut] = Field(default_factory=list)


# ── Analyze response ───────────────────────────────────────────────────────────

class AnalyzeResponse(BaseModel):
    """Response model for /analyze endpoint."""
    model_config = ConfigDict(from_attributes=True)

    amount: float
    source_currency: str
    target_currency: str
    mid_market_rate: float
    amount_usd: float
    recommended: RouteOut
    all_routes: list[RouteOut]
    savings_vs_worst_usd: float
    savings_vs_worst_pct: float
    timestamp: str


class RecommendResponse(BaseModel):
    """Response model for /recommend endpoint."""
    model_config = ConfigDict(from_attributes=True)

    recommended: RouteOut
    alternatives: list[RouteOut]
    savings_vs_worst_usd: float
    timestamp: str


# ── Auth / user schemas ────────────────────────────────────────────────────────

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ── Transaction / history schemas ─────────────────────────────────────────────

class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: float
    source_currency: str
    target_currency: str
    recommended_method: str | None
    estimated_cost_usd: float | None
    savings_vs_worst_usd: float | None
    hop_count: int | None = 1
    route_path: list[str] | None = None
    created_at: datetime
    routes: list[RouteOut] = []
