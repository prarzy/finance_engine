import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from app.core.config import settings
from app.services.constraint_service import constraint_service
from app.db.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Application starting up...")
    async with AsyncSessionLocal() as session:
        await constraint_service.load(session)
    logger.info("Constraint service loaded.")
    yield
    # Shutdown
    logger.info("Application shutting down...")


app = FastAPI(
    title="Smart Payment Route Optimizer",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health endpoint
@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


# Include routers
try:
    from app.api.v1.auth import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
except Exception as e:
    logger.warning(f"Failed to load auth router: {e}")

try:
    from app.api.v1.analyze import router as analyze_router
    app.include_router(analyze_router, prefix="/api/v1", tags=["analyze"])
except Exception as e:
    logger.warning(f"Failed to load analyze router: {e}")

try:
    from app.api.v1.corridors import router as corridors_router
    app.include_router(corridors_router, prefix="/api/v1", tags=["corridors"])
except Exception as e:
    logger.warning(f"Failed to load corridors router: {e}")

try:
    from app.api.v1.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
except Exception as e:
    logger.warning(f"Failed to load dashboard router: {e}")


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )
