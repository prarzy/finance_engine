from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.schemas import AnalyzeRequest, AnalyzeResponse, RecommendResponse, TransactionOut
from app.core.security import verify_token
from app.core.config import Settings, get_settings
from app.db.database import get_db
from app.models import User, Transaction, Route
from app.services.route_analyzer import RouteAnalyzer, get_route_analyzer
from app.services.fx_service import FXService, get_fx_service

router = APIRouter()


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Dependency to optionally get the current user (no error if not authenticated)."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ", 1)[1]
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    
    from uuid import UUID
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        return None
    
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        return None
    
    return user


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    body: AnalyzeRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
    route_analyzer: RouteAnalyzer = Depends(get_route_analyzer),
) -> AnalyzeResponse:
    """Analyze payment routes."""
    result = await route_analyzer.analyze(
        body.amount,
        body.source_currency,
        body.target_currency,
        body.available_methods,
    )
    
    # Persist transaction if user is authenticated
    if current_user is not None:
        rec = result["recommended"]
        txn = Transaction(
            user_id=current_user.id,
            amount=body.amount,
            source_currency=body.source_currency,
            target_currency=body.target_currency,
            mid_market_rate=result["mid_market_rate"],
            recommended_method=rec["method_name"],
            estimated_cost_usd=rec["total_cost_usd"],
            savings_vs_worst_usd=result["savings_vs_worst_usd"],
            hop_count=rec.get("hop_count", 1),
            route_path=rec.get("path"),
        )
        db.add(txn)
        await db.flush()

        # Persist all ranked routes with multi-hop breakdown
        for r in result["all_routes"]:
            db.add(Route(
                transaction_id=txn.id,
                method_name=r["method_name"],
                total_cost_usd=r["total_cost_usd"],
                fx_spread_pct=r["fx_spread_pct"],
                fx_cost_usd=r["fx_cost_usd"],
                fixed_fee_usd=r["fixed_fee_usd"],
                variable_fee_pct=r["variable_fee_pct"],
                variable_fee_usd=r["variable_fee_usd"],
                processing_days=r["processing_days"],
                rank=r["rank"],
                is_recommended=r["is_recommended"],
                hop_count=r.get("hop_count", 1),
                path=r.get("path"),
                breakdown=r.get("steps"),
            ))

        await db.commit()
    
    return AnalyzeResponse(**result)


@router.get("/recommend", response_model=RecommendResponse)
async def recommend(
    amount: float,
    source_currency: str,
    target_currency: str,
    route_analyzer: RouteAnalyzer = Depends(get_route_analyzer),
) -> RecommendResponse:
    """Get payment route recommendations."""
    result = await route_analyzer.analyze(amount, source_currency, target_currency)
    
    return RecommendResponse(
        recommended=result["recommended"],
        alternatives=result["all_routes"][1:4],
        savings_vs_worst_usd=result["savings_vs_worst_usd"],
        timestamp=result["timestamp"],
    )


@router.get("/history", response_model=list[TransactionOut])
async def get_history(
    page: int = 1,
    page_size: int = Query(default=20, le=100),
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> list[TransactionOut]:
    """Get transaction history for the current user."""
    from app.core.exceptions import UnauthorizedError
    
    if current_user is None:
        raise UnauthorizedError()
    
    query = (
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .options(selectinload(Transaction.routes))
        .order_by(Transaction.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return [TransactionOut.model_validate(t) for t in transactions]
