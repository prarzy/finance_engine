from uuid import uuid4

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


class Transaction(Base):
    """Payment transaction model — stores the full multi-hop route result."""
    __tablename__ = "transactions"

    id                   = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id              = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    amount               = Column(Numeric(18, 4), nullable=False)
    source_currency      = Column(String(3), nullable=False)
    target_currency      = Column(String(3), nullable=False)
    mid_market_rate      = Column(Numeric(18, 6))
    recommended_method   = Column(String(50))
    estimated_cost_usd   = Column(Numeric(18, 4))
    savings_vs_worst_usd = Column(Numeric(18, 4))
    # Multi-hop additions
    hop_count            = Column(Integer, default=1)
    route_path           = Column(JSONB, nullable=True)   # e.g. ["USD","revolut__USD__EUR","EUR"]
    constraint_snapshot  = Column(JSONB, nullable=True)   # Constraints active at time of analysis
    created_at           = Column(DateTime(timezone=True), server_default=text("now()"), index=True)

    user   = relationship("User", back_populates="transactions")
    routes = relationship("Route", back_populates="transaction", cascade="all, delete-orphan")
