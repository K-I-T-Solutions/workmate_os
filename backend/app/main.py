"""
WorkmateOS Backend - Main Application
"""
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.core.settings.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from pathlib import Path
import logging

# Logging aktivieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Core
from app.core.auth.routes import auth_router

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
from app.modules.backoffice.products.routes import router as products_router
from app.modules.backoffice.chat import routes as chat_routes
from app.modules.backoffice.finance import routes as finance_routes
from app.modules.admin.audit_routes import router as audit_router
from app.modules.admin.settings_routes import router as settings_router
from app.modules.hr import router as hr_router
from app.modules.support.routes import router as support_router
from app.modules.knowledge.routes import router as kb_router
from app.modules.email_intake.routes import router as email_intake_router


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

# ProxyHeadersMiddleware — MUSS VOR CORS kommen (respektiert X-Forwarded-Proto von Caddy)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

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
app.include_router(audit_router, tags=["Admin"])
app.include_router(settings_router, tags=["Admin"])
app.include_router(hr_router, prefix="/api", tags=["HR"])
app.include_router(support_router, tags=["Support"])
app.include_router(kb_router, tags=["Knowledge Base"])
app.include_router(email_intake_router, tags=["Email Intake"])

# === Core Endpoints ===

def _status_html(extra_rows: str = "") -> str:
    env = settings.ENVIRONMENT
    env_color = "#22c55e" if env == "production" else "#f59e0b"
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WorkmateOS API</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f1117;
      color: #e2e8f0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }}
    .card {{
      background: #1a1f2e;
      border: 1px solid #2d3748;
      border-radius: 16px;
      padding: 2.5rem 3rem;
      width: 100%;
      max-width: 520px;
      box-shadow: 0 25px 50px rgba(0,0,0,0.4);
    }}
    .logo {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 2rem;
    }}
    .logo-icon {{
      width: 40px; height: 40px;
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 20px;
    }}
    .logo-text {{ font-size: 1.25rem; font-weight: 700; color: #f8fafc; }}
    .logo-sub {{ font-size: 0.75rem; color: #64748b; margin-top: 2px; }}
    .badge {{
      display: inline-flex; align-items: center; gap: 6px;
      padding: 4px 12px; border-radius: 999px;
      font-size: 0.75rem; font-weight: 600;
      background: #14532d; color: #86efac;
      border: 1px solid #166534;
      margin-bottom: 1.5rem;
    }}
    .dot {{ width: 7px; height: 7px; border-radius: 50%; background: #22c55e; animation: pulse 2s infinite; }}
    @keyframes pulse {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.4 }} }}
    table {{ width: 100%; border-collapse: collapse; }}
    tr {{ border-bottom: 1px solid #1e293b; }}
    tr:last-child {{ border-bottom: none; }}
    td {{ padding: 10px 0; font-size: 0.875rem; }}
    td:first-child {{ color: #64748b; width: 45%; }}
    td:last-child {{ color: #f1f5f9; font-weight: 500; text-align: right; }}
    .env-badge {{
      display: inline-block; padding: 2px 8px; border-radius: 4px;
      font-size: 0.75rem; font-weight: 600;
      background: {env_color}22; color: {env_color};
    }}
    .links {{ margin-top: 2rem; display: flex; gap: 10px; }}
    .link {{
      flex: 1; text-align: center; padding: 10px;
      border-radius: 8px; border: 1px solid #2d3748;
      color: #94a3b8; text-decoration: none; font-size: 0.8rem;
      transition: all .15s;
    }}
    .link:hover {{ background: #2d3748; color: #f1f5f9; border-color: #3b82f6; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">
      <div class="logo-icon">⚡</div>
      <div>
        <div class="logo-text">WorkmateOS</div>
        <div class="logo-sub">K.I.T. Solutions — Backend API</div>
      </div>
    </div>
    <div class="badge"><span class="dot"></span> Operational</div>
    <table>
      <tr><td>Version</td><td>{settings.APP_VERSION}</td></tr>
      <tr><td>Environment</td><td><span class="env-badge">{env}</span></td></tr>
      {extra_rows}
    </table>
    <div class="links">
      <a class="link" href="/docs">Swagger UI</a>
      <a class="link" href="/redoc">ReDoc</a>
      <a class="link" href="/health">Health</a>
      <a class="link" href="/system/info">System Info</a>
    </div>
  </div>
</body>
</html>"""


@app.get("/", tags=["Root"], response_class=HTMLResponse)
async def root():
    return HTMLResponse(_status_html())


@app.get("/health", tags=["System"], response_class=HTMLResponse)
async def health_check():
    """Health check endpoint"""
    from app.modules.system.router import _info_html, _uptime_str
    return HTMLResponse(_info_html(_uptime_str()))


@app.get("/health/json", tags=["System"], include_in_schema=False)
async def health_check_json():
    """JSON Health check für Docker / Monitoring"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
