from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ComplianceRule(Base):
    """Compliance rules for country blocks and corridor-specific KYC requirements."""
    __tablename__ = "compliance_rules"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    rule_type: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_slug: Mapped[str | None] = mapped_column(String(32), ForeignKey("providers.slug"), nullable=True)
    currency_code: Mapped[str | None] = mapped_column(String(3), ForeignKey("currencies.code"), nullable=True)
    rule_value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    source_citation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
