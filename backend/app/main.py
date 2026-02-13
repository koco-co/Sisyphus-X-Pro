"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import Base, engine
from app.init_builtin import init_builtin_keywords
from app.routers import (
    auth,
    dashboard,
    db_configs,
    environments,
    global_params,
    interfaces,
    keywords,
    projects,
    reports,
    scenarios,
    test_plans,
    upload,
)
from app.services.global_param_service import GlobalParamService
from app.services.report_scheduler import init_report_scheduler, shutdown_report_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize built-in keywords
    async with AsyncSession(engine) as db:
        count = await init_builtin_keywords(db)
        await db.commit()
        print(f"✓ Initialized {count} built-in keywords")

    # Initialize built-in global parameters
    async with AsyncSession(engine) as db:
        service = GlobalParamService(db)
        param_count = await service.initialize_builtin_params()
        await db.commit()
        print(f"✓ Initialized {param_count} built-in global parameters")

    # Initialize report scheduler
    def async_session_maker():
        return AsyncSession(engine)

    init_report_scheduler(async_session_maker)

    yield
    # Shutdown: Close database connections and stop scheduler
    shutdown_report_scheduler()
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(db_configs.router, prefix=settings.API_V1_STR)
app.include_router(keywords.router, prefix=settings.API_V1_STR)
app.include_router(environments.router, prefix=settings.API_V1_STR)
app.include_router(interfaces.router, prefix=settings.API_V1_STR)
app.include_router(scenarios.router, prefix=settings.API_V1_STR)
app.include_router(test_plans.router, prefix=settings.API_V1_STR)
app.include_router(global_params.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(upload.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Sisyphus-X-Pro API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
