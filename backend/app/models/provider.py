from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, Integer, Numeric, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Provider(Base):
    """Payment method/provider definition with cost structure."""
    __tablename__ = "providers"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    fx_spread_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    fixed_fee_usd: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    variable_fee_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    settlement_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

    corridors: Mapped[list["ProviderCorridor"]] = relationship(back_populates="provider")
