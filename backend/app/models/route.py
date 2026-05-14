from uuid import uuid4

from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Route(Base):
    """Payment route (method) analysis result."""
    __tablename__ = "routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False, index=True)
    method_name = Column(String(50), nullable=False)
    total_cost_usd = Column(Numeric(18, 4))
    fx_spread_pct = Column(Numeric(6, 4))
    fx_cost_usd = Column(Numeric(18, 4))
    fixed_fee_usd = Column(Numeric(10, 4))
    variable_fee_pct = Column(Numeric(6, 4))
    variable_fee_usd = Column(Numeric(18, 4))
    processing_days = Column(Integer)
    rank = Column(Integer)
    is_recommended = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transaction = relationship("Transaction", back_populates="routes")
