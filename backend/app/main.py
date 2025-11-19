"""
WorkmateOS Backend - Main Application
"""
import os
from fastapi import FastAPI
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path


# Module Imports
from app.modules.system.router import router as system_router
from app.modules.employees.routes import router as employee_router
from app.modules.documents.routes import router as documents_router
from app.modules.reminders.routes import router as reminders_router
from app.modules.dashboards.routes import router as dashboards_router
from app.modules.backoffice.crm.routes import router as crm_router
from app.modules.backoffice.projects.routes import router as projects_router
from app.modules.backoffice.time_tracking.routes import router as time_tracking_router
from app.modules.backoffice.invoices.routes import router as invoices_router


# ====== Basis Verzeichnis =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Workmate OS - The internal toolkit for K.I.T. Solutions",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = [
    # Lokale Entwicklung
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://workmate_ui:5173",

    # Interne Domains (Homelab / Unraid / Cisco)
    "https://workmate.intern.phudevelopement.xyz",
    "https://api.workmate.intern.phudevelopement.xyz",
    "https://login.intern.phudevelopement.xyz",

    # Docker Services (nur intern via Docker-Netzwerk)
    "http://keycloak:8080",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
# === Static Files ===
UPLOAD_DIR = Path(settings.UPLOAD_DIR or (BASE_DIR + "/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# === Module-Router ===
app.include_router(system_router, prefix="/system", tags=["System"])
app.include_router(employee_router, prefix="/api", tags=["Core"])
app.include_router(documents_router, prefix="/api", tags=["Documents"])
app.include_router(reminders_router, prefix="/api", tags=["Reminders"])  # ← FIXED!
app.include_router(dashboards_router, prefix="/api", tags=["Dashboards"])  # ← FIXED!
app.include_router(crm_router, prefix="/api", tags=["Backoffice CRM"])  # ← FIXED!
app.include_router(projects_router, prefix="/api", tags=["Backoffice Projects"])  # ← FIXED!
app.include_router(time_tracking_router, prefix="/api", tags=["Backoffice Time Tracking"])  # ← FIXED!
app.include_router(invoices_router, prefix="/api", tags=["Backoffice Invoices"])  # ← FIXED!
# === Core Endpoints ===
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"{settings.APP_NAME} API online ✅",
        "docs": "/docs",
        "version": settings.APP_VERSION
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
