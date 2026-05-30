"""Dashboard and user statistics endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.core.exceptions import UnauthorizedError
from app.db.database import get_db
from app.models import User, Transaction
from pydantic import BaseModel

router = APIRouter()


class TransactionSummary(BaseModel):
    """Summary of a recent transaction."""
    id: str
    source: str
    target: str
    amount: float
    hop_count: int
    created_at: str


class CorridorCount(BaseModel):
    """Corridor usage count."""
    corridor: str
    count: int


class DashboardSummary(BaseModel):
    """User dashboard summary statistics."""
    total_analyses: int
    most_analyzed_corridor: Optional[str] = None
    recent_transactions: list[TransactionSummary]
    top_corridors: list[CorridorCount]


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get the current authenticated user."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise UnauthorizedError()

    token = auth_header.split(" ", 1)[1]
    payload = verify_token(token)
    if not payload:
        raise UnauthorizedError()

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError()

    from uuid import UUID
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError()

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise UnauthorizedError()

    return user


@router.get("/dashboard/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardSummary:
    """Get user dashboard summary with statistics and recent analyses."""

    # Total number of analyses
    count_query = select(func.count(Transaction.id)).where(
        Transaction.user_id == current_user.id
    )
    count_result = await db.execute(count_query)
    total_analyses = count_result.scalar() or 0

    # Most analyzed corridor
    corridor_query = select(
        Transaction.source_currency,
        Transaction.target_currency,
        func.count(Transaction.id).label("count")
    ).where(
        Transaction.user_id == current_user.id
    ).group_by(
        Transaction.source_currency,
        Transaction.target_currency
    ).order_by(
        desc(func.count(Transaction.id))
    ).limit(1)
    
    corridor_result = await db.execute(corridor_query)
    most_analyzed_row = corridor_result.first()
    most_analyzed_corridor = f"{most_analyzed_row[0]} → {most_analyzed_row[1]}" if most_analyzed_row else None

    # Recent transactions (last 5)
    recent_query = select(Transaction).where(
        Transaction.user_id == current_user.id
    ).order_by(
        desc(Transaction.created_at)
    ).limit(5)
    
    recent_result = await db.execute(recent_query)
    recent_txns = recent_result.scalars().all()
    
    recent_transactions = [
        TransactionSummary(
            id=str(t.id),
            source=t.source_currency,
            target=t.target_currency,
            amount=float(t.amount),
            hop_count=t.hop_count or 1,
            created_at=t.created_at.isoformat() if t.created_at else "",
        )
        for t in recent_txns
    ]

    # Top corridors (group by corridor)
    top_corridors_query = select(
        Transaction.source_currency,
        Transaction.target_currency,
        func.count(Transaction.id).label("count")
    ).where(
        Transaction.user_id == current_user.id
    ).group_by(
        Transaction.source_currency,
        Transaction.target_currency
    ).order_by(
        desc(func.count(Transaction.id))
    ).limit(5)
    
    top_result = await db.execute(top_corridors_query)
    top_rows = top_result.all()
    
    top_corridors = [
        CorridorCount(corridor=f"{row[0]} → {row[1]}", count=row[2])
        for row in top_rows
    ]

    return DashboardSummary(
        total_analyses=total_analyses,
        most_analyzed_corridor=most_analyzed_corridor,
        recent_transactions=recent_transactions,
        top_corridors=top_corridors,
    )
