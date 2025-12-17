from fastapi import APIRouter
from app.core.settings.config import settings

router = APIRouter(tags=["System"])

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "module": "system",
        "message": "Workmate OS Backend operational 🚀"
    }

@router.get("/info")
async def system_info():
    return {
        "version": settings.APP_VERSION,
        "environment": "development"
    }
