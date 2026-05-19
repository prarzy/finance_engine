from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active     = Column(Boolean, default=True, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=text("now()"))

    transactions  = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
