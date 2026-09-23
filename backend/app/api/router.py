from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.documents import router as documents_router
from app.api.v1.rag import router as rag_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(transactions_router)
api_router.include_router(documents_router)
api_router.include_router(rag_router)
