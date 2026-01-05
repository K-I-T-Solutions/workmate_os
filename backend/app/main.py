"""
WorkmateOS Backend - Main Application
"""
import os
from fastapi import FastAPI, Request
from app.core.settings import config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware import Middleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from pathlib import Path
import logging
from app.core.settings.config import settings

# Module Imports
from app.core.auth.routes import auth_router
from app.modules.system.router import router as system_router
from app.modules.employees.routes import router as employee_router
from app.modules.documents.routes import router as documents_router
from app.modules.reminders.routes import router as reminders_router
from app.modules.dashboards.routes import router as dashboards_router
from app.modules.backoffice.crm.routes import router as crm_router
from app.modules.backoffice.projects.routes import router as projects_router
from app.modules.backoffice.time_tracking.routes import router as time_tracking_router
from app.modules.backoffice.invoices.routes import router as invoices_router
from app.modules.backoffice.products.routes import router as products_router
from app.modules.backoffice.chat import routes as chat_routes
from app.modules.backoffice.finance import routes as finance_routes
from app.modules.admin.audit_routes import router as audit_router
from app.modules.admin.settings_routes import router as settings_router


# Logging aktivieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:5173",
    "http://workmate_ui:5173",

    # Production Domains
    "https://workmate.kit-it-koblenz.de",
    "https://api.workmate.kit-it-koblenz.de",
    "http://workmate.kit-it-koblenz.de",
    "http://api.workmate.kit-it-koblenz.de",

    # Interne Domains - ALLE Kombinationen
    "http://workmate.intern.phudevelopement.xyz",
    "http://workmate.intern.phudevelopement.xyz:5173",
    "https://workmate.intern.phudevelopement.xyz",
    "https://workmate.intern.phudevelopement.xyz:5173",

    "http://api.workmate.intern.phudevelopement.xyz",
    "http://api.workmate.intern.phudevelopement.xyz:8000",
    "https://api.workmate.intern.phudevelopement.xyz",
    "https://api.workmate.intern.phudevelopement.xyz:8000",

    # API Domain für Frontend
    "https://workmate-api.phudevelopement.xyz",
    "http://workmate-api.phudevelopement.xyz",

    "https://login.intern.phudevelopement.xyz",

    # Docker Services
    "http://keycloak:8080",
]
# ProxyHeadersMiddleware - MUSS VOR CORS kommen!
# Respektiert X-Forwarded-Proto, X-Forwarded-Host von Caddy
app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts=["*"],  # In Production: nur trusted IPs
)

# Debug Middleware um Origin zu sehen
@app.middleware("http")
async def log_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    logger.info(f"📨 Request from Origin: {origin}")
    response = await call_next(request)
    return response

# CORS Middleware
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
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(system_router, prefix="/system", tags=["System"])
app.include_router(employee_router, prefix="/api", tags=["Core"])
app.include_router(documents_router, prefix="/api", tags=["Documents"])
app.include_router(reminders_router, prefix="/api", tags=["Reminders"])
app.include_router(dashboards_router, prefix="/api", tags=["Dashboards"])
app.include_router(crm_router, prefix="/api", tags=["Backoffice CRM"])
app.include_router(projects_router, prefix="/api", tags=["Backoffice Projects"])
app.include_router(time_tracking_router, prefix="/api", tags=["Backoffice Time Tracking"])
app.include_router(products_router, prefix="/api", tags=["Backoffice Products"])
app.include_router(invoices_router, prefix="/api", tags=["Backoffice Invoices"])
app.include_router(chat_routes.router, prefix="/api", tags=["Backoffice Chat"])
app.include_router(finance_routes.router, prefix="/api", tags=["Backoffice Finance"])

# Admin Module
app.include_router(audit_router, tags=["Admin"])
app.include_router(settings_router, tags=["Admin"])

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
