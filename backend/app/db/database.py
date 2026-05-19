from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

Base = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    # PostgreSQL connection pool settings
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,   # recycle connections after 30 min
    pool_pre_ping=True,  # verify connection health before use
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
