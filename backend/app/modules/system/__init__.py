from fastapi import APIRouter

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
        "version": "0.1.0",
        "environment": "development"
    }
