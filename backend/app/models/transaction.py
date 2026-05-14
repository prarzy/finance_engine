from uuid import uuid4

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Transaction(Base):
    """Payment transaction model."""
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    amount = Column(Numeric(18, 4), nullable=False)
    source_currency = Column(String(3), nullable=False)
    target_currency = Column(String(3), nullable=False)
    mid_market_rate = Column(Numeric(18, 6))
    recommended_method = Column(String(50))
    estimated_cost_usd = Column(Numeric(18, 4))
    savings_vs_worst_usd = Column(Numeric(18, 4))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="transactions")
    routes = relationship("Route", back_populates="transaction", cascade="all, delete-orphan")
