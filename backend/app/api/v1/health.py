from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.config import settings

from datetime import datetime

router = APIRouter(tags=["Health"])


@router.get("/health")
async def check_health(db: AsyncSession = Depends(get_db)):
    """Health check endpoint verifying API service and database connectivity."""
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unavailable ({str(e)})"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.0.0-phase11",
        "database": db_status,
        "llm_provider": settings.LLM_PROVIDER,
    }


@router.get("/health/ready")
async def check_readiness(db: AsyncSession = Depends(get_db)):
    """Readiness probe: verifies database, storage directories, and local ML status."""
    from pathlib import Path
    from app.intelligence.ml.local_inference_engine import local_intelligence_engine

    db_ready = False
    try:
        await db.execute(text("SELECT 1"))
        db_ready = True
    except Exception:
        db_ready = False

    from app.ingestion.storage import storage_manager

    storage_ready = storage_manager.upload_dir.exists() or Path(settings.STORAGE_LOCAL_DIR).exists()
    ml_ready = local_intelligence_engine.is_loaded

    is_ready = db_ready and storage_ready

    return {
        "ready": is_ready,
        "database": "ready" if db_ready else "error",
        "storage": "ready" if storage_ready else "error",
        "ml_engine": "loaded" if ml_ready else "heuristic_fallback_active",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/live")
async def check_liveness():
    """Liveness probe: verifies process is alive and responsive."""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
