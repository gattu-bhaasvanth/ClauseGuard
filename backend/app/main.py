from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db, AsyncSessionLocal
from app.services.seed_service import seed_demo_data
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema exists and seed demo bundles
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_demo_data(session)
    yield
    # Shutdown logic if needed


app = FastAPI(
    title=settings.APP_NAME,
    description="ClauseGuard: AI-Powered Real-Estate Transaction Intelligence Platform API",
    version="0.1.0-phase2",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS for Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "message": "ClauseGuard Real-Estate Transaction Intelligence API",
        "documentation": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "transactions": f"{settings.API_V1_PREFIX}/transactions",
    }
