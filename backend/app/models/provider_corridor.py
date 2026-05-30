from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, Integer, Numeric, ForeignKey, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ProviderCorridor(Base):
    """Valid (provider, source_currency, target_currency) corridors with constraints."""
    __tablename__ = "provider_corridors"
    __table_args__ = (
        UniqueConstraint("provider_slug", "source_currency", "target_currency", name="unique_corridor"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    provider_slug: Mapped[str] = mapped_column(String(32), ForeignKey("providers.slug"), nullable=False)
    source_currency: Mapped[str] = mapped_column(String(3), ForeignKey("currencies.code"), nullable=False)
    target_currency: Mapped[str] = mapped_column(String(3), ForeignKey("currencies.code"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_transfer_usd: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    min_transfer_usd: Mapped[float] = mapped_column(Numeric(10, 2), default=1.00, nullable=False)
    kyc_tier_required: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

    provider: Mapped["Provider"] = relationship(back_populates="corridors")
