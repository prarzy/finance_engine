import pytest
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.database import Base, get_db
from app.main import app
from app.services.fx_service import FXService

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def db_session():
    """Create a fresh in-memory SQLite database for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    AsyncSessionLocal = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    
    async with AsyncSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def client_no_mock(db_session):
    """Create a test client without any mocking - use actual FX calls."""
    app.dependency_overrides.clear()  # Ensure clean slate
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def client(db_session, monkeypatch):
    """Create a test client with mocked FX service."""
    app.dependency_overrides.clear()  # Ensure clean slate
    
    # Mock FX methods on the class before client creation
    async def fake_get_rate(self, base, target):
        if base == target:
            return 1.0
        return 0.92
    
    async def fake_get_spread(self, method):
        return FXService.SPREAD_BY_METHOD.get(method, 2.0)
    
    monkeypatch.setattr(FXService, "get_rate", fake_get_rate, raising=False)
    monkeypatch.setattr(FXService, "get_spread_estimate", fake_get_spread, raising=False)
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()
