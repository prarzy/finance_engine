from uuid import uuid4

from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


class Route(Base):
    """
    One ranked route per transaction.
    For single-hop routes: method_name is the rail name.
    For multi-hop routes: method_name = 'multi_hop', breakdown contains full steps.
    """
    __tablename__ = "routes"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False, index=True)
    method_name    = Column(String(50), nullable=False)
    total_cost_usd = Column(Numeric(18, 4))
    fx_spread_pct  = Column(Numeric(6, 4))
    fx_cost_usd    = Column(Numeric(18, 4))
    fixed_fee_usd  = Column(Numeric(10, 4))
    variable_fee_pct  = Column(Numeric(6, 4))
    variable_fee_usd  = Column(Numeric(18, 4))
    processing_days   = Column(Integer)
    rank           = Column(Integer)
    is_recommended = Column(Boolean, default=False)
    # Multi-hop additions
    hop_count      = Column(Integer, default=1)
    path           = Column(JSONB, nullable=True)   # full node path
    breakdown      = Column(JSONB, nullable=True)   # list of RouteStep dicts
    created_at     = Column(DateTime(timezone=True), server_default=text("now()"))

    transaction = relationship("Transaction", back_populates="routes")
