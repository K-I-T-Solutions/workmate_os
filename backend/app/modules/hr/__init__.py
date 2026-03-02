"""
HR Module for WorkmateOS
Vollständiges Human Resources Management System.
"""
from fastapi import APIRouter

# Router wird schrittweise mit Sub-Modulen erweitert
router = APIRouter(prefix="/hr", tags=["HR"])

# Sub-Router
# from .recruiting.routes import router as recruiting_router
# from .onboarding.routes import router as onboarding_router
from .leave.routes import router as leave_router
# from .training.routes import router as training_router
# from .compensation.routes import router as compensation_router
# from .documents.routes import router as hr_documents_router
# from .analytics.routes import router as analytics_router

# Registriere Sub-Router
# router.include_router(recruiting_router)
# router.include_router(onboarding_router)
router.include_router(leave_router)
# router.include_router(training_router)
# router.include_router(compensation_router)
# router.include_router(hr_documents_router)
# router.include_router(analytics_router)

__all__ = ["router"]
