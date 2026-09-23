from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.config import settings

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
        "version": "0.1.0-phase2",
        "database": db_status,
        "llm_provider": settings.LLM_PROVIDER,
    }
