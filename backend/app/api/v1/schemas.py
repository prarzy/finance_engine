from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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


class RouteOut(BaseModel):
    """Response model for a payment route."""
    model_config = ConfigDict(from_attributes=True)

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


class AnalyzeResponse(BaseModel):
    """Response model for payment route analysis."""
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
    """Response model for recommendations endpoint."""
    model_config = ConfigDict(from_attributes=True)

    recommended: RouteOut
    alternatives: list[RouteOut]
    savings_vs_worst_usd: float
    timestamp: str


class UserOut(BaseModel):
    """Response model for user data."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    created_at: datetime


class TokenOut(BaseModel):
    """Response model for authentication token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TransactionOut(BaseModel):
    """Response model for transaction data."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: float
    source_currency: str
    target_currency: str
    recommended_method: str | None
    estimated_cost_usd: float | None
    savings_vs_worst_usd: float | None
    created_at: datetime
    routes: list[RouteOut] = []
