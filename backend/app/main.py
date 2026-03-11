"""
WorkmateOS Backend - Main Application
"""
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.core.settings import config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware import Middleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from pathlib import Path
import logging
from datetime import datetime, timezone
from app.core.settings.config import settings

# Module Imports
from app.core.auth.routes import auth_router
from app.modules.system.router import router as system_router
from app.modules.employees.routes import router as employee_router
from app.modules.documents.routes import router as documents_router
from app.modules.reminders.routes import router as reminders_router
from app.modules.dashboards.routes import router as dashboards_router, user_settings_router
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
app.include_router(user_settings_router, prefix="/api", tags=["User Settings"])
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

# HR Module
app.include_router(hr_router, prefix="/api", tags=["HR"])

# === Core Endpoints ===
@app.get("/", tags=["Root"], response_class=HTMLResponse)
async def root():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    env = settings.ENVIRONMENT
    env_color = "#22c55e" if env == "production" else "#f59e0b"
    env_label = env.upper()

    modules = [
        ("Authentication", "/api/auth", "Keycloak OIDC Login & Token-Verwaltung"),
        ("Mitarbeiter", "/api/employees", "Mitarbeiterverwaltung & Profile"),
        ("CRM", "/api/backoffice/crm", "Kundenverwaltung & Kontakte"),
        ("Projekte", "/api/backoffice/projects", "Projektverwaltung & Aufgaben"),
        ("Zeiterfassung", "/api/backoffice/time-tracking", "Arbeitszeiterfassung & Auswertung"),
        ("Rechnungen", "/api/backoffice/invoices", "Rechnungsverwaltung & Zahlungen"),
        ("Produkte", "/api/backoffice/products", "Produktkatalog & Preise"),
        ("Finanzen", "/api/backoffice/finance", "Bankintegration & Buchhaltung"),
        ("Chat", "/api/backoffice/chat", "Internes Kommunikationssystem"),
        ("Dokumente", "/api/documents", "Dokumentenverwaltung & Speicher"),
        ("Erinnerungen", "/api/reminders", "Aufgaben & Erinnerungen"),
        ("Dashboards", "/api/dashboards", "Übersichten & KPIs"),
        ("HR", "/api/hr", "Personalwesen & Urlaub"),
        ("Audit-Logs", "/api/audit-logs", "Systemverwaltung & Audit-Logs"),
        ("Einstellungen", "/api/settings", "Systemeinstellungen & Konfiguration"),
    ]

    module_cards = "\n".join(
        f"""
        <div class="module-card">
            <div class="module-header">
                <span class="module-dot"></span>
                <strong>{name}</strong>
            </div>
            <code>{path}</code>
            <p>{desc}</p>
        </div>"""
        for name, path, desc in modules
    )

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{settings.APP_NAME} — Status</title>
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f1117;
            color: #e2e8f0;
            min-height: 100vh;
            padding: 2rem 1rem;
        }}

        .container {{
            max-width: 960px;
            margin: 0 auto;
        }}

        /* Header */
        header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 2.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid #1e2330;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .logo-icon {{
            width: 42px;
            height: 42px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
        }}

        .logo-text h1 {{
            font-size: 1.2rem;
            font-weight: 700;
            color: #f1f5f9;
            letter-spacing: -0.02em;
        }}

        .logo-text span {{
            font-size: 0.75rem;
            color: #64748b;
        }}

        .env-badge {{
            font-size: 0.7rem;
            font-weight: 600;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            background: {env_color}22;
            color: {env_color};
            border: 1px solid {env_color}44;
            letter-spacing: 0.05em;
        }}

        /* Status Banner */
        .status-banner {{
            background: #12181f;
            border: 1px solid #1e2a3a;
            border-left: 4px solid #22c55e;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .status-dot {{
            width: 10px;
            height: 10px;
            background: #22c55e;
            border-radius: 50%;
            box-shadow: 0 0 0 3px #22c55e33;
            animation: pulse 2s ease-in-out infinite;
            flex-shrink: 0;
        }}

        @keyframes pulse {{
            0%, 100% {{ box-shadow: 0 0 0 3px #22c55e33; }}
            50% {{ box-shadow: 0 0 0 6px #22c55e11; }}
        }}

        .status-text strong {{
            color: #22c55e;
            font-size: 0.95rem;
        }}

        .status-text p {{
            font-size: 0.78rem;
            color: #64748b;
            margin-top: 0.15rem;
        }}

        /* Info Grid */
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .info-card {{
            background: #12181f;
            border: 1px solid #1e2330;
            border-radius: 12px;
            padding: 1.2rem;
        }}

        .info-card .label {{
            font-size: 0.7rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.4rem;
        }}

        .info-card .value {{
            font-size: 1rem;
            font-weight: 600;
            color: #f1f5f9;
            font-variant-numeric: tabular-nums;
        }}

        /* Quick Links */
        .section-title {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #475569;
            margin-bottom: 0.75rem;
            font-weight: 600;
        }}

        .links {{
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-bottom: 2rem;
        }}

        .link-btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.55rem 1.1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.15s;
        }}

        .link-btn.primary {{
            background: #6366f1;
            color: #fff;
        }}

        .link-btn.primary:hover {{
            background: #4f46e5;
        }}

        .link-btn.secondary {{
            background: #1e2330;
            color: #94a3b8;
            border: 1px solid #2d3748;
        }}

        .link-btn.secondary:hover {{
            background: #252d40;
            color: #e2e8f0;
        }}

        /* Modules */
        .modules-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 0.75rem;
            margin-bottom: 2rem;
        }}

        .module-card {{
            background: #12181f;
            border: 1px solid #1e2330;
            border-radius: 10px;
            padding: 1rem 1.1rem;
            transition: border-color 0.15s;
        }}

        .module-card:hover {{
            border-color: #374151;
        }}

        .module-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.35rem;
        }}

        .module-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #6366f1;
            flex-shrink: 0;
        }}

        .module-header strong {{
            font-size: 0.875rem;
            color: #e2e8f0;
        }}

        .module-card code {{
            font-family: "SF Mono", "Fira Code", Consolas, monospace;
            font-size: 0.72rem;
            color: #6366f1;
            background: #1e1e3a;
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 0.4rem;
        }}

        .module-card p {{
            font-size: 0.78rem;
            color: #64748b;
            line-height: 1.4;
        }}

        /* Footer */
        footer {{
            text-align: center;
            font-size: 0.75rem;
            color: #334155;
            padding-top: 1.5rem;
            border-top: 1px solid #1e2330;
        }}

        footer span {{
            color: #475569;
        }}
    </style>
</head>
<body>
    <div class="container">

        <header>
            <div class="logo">
                <div class="logo-icon">⚙️</div>
                <div class="logo-text">
                    <h1>{settings.APP_NAME}</h1>
                    <span>REST API — v{settings.APP_VERSION}</span>
                </div>
            </div>
            <span class="env-badge">{env_label}</span>
        </header>

        <div class="status-banner">
            <div class="status-dot"></div>
            <div class="status-text">
                <strong>Alle Systeme betriebsbereit</strong>
                <p>Letzte Prüfung: {now}</p>
            </div>
        </div>

        <div class="info-grid">
            <div class="info-card">
                <div class="label">Version</div>
                <div class="value">v{settings.APP_VERSION}</div>
            </div>
            <div class="info-card">
                <div class="label">Umgebung</div>
                <div class="value">{env}</div>
            </div>
            <div class="info-card">
                <div class="label">Auth-Provider</div>
                <div class="value">Keycloak OIDC</div>
            </div>
            <div class="info-card">
                <div class="label">Module</div>
                <div class="value">{len(modules)} aktiv</div>
            </div>
        </div>

        <p class="section-title">Dokumentation & Tools</p>
        <div class="links">
            <a href="/docs" class="link-btn primary">⚡ Swagger UI</a>
            <a href="/redoc" class="link-btn secondary">📖 ReDoc</a>
            <a href="/health" class="link-btn secondary">💚 Health Check</a>
            <a href="/system/info" class="link-btn secondary">ℹ️ System Info</a>
        </div>

        <p class="section-title">API-Module ({len(modules)})</p>
        <div class="modules-grid">
            {module_cards}
        </div>

        <footer>
            <span>{settings.APP_NAME}</span> &mdash; Betrieben von K.I.T. Solutions &bull; {now}
        </footer>

    </div>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=200)


@app.get("/health", tags=["System"], response_class=HTMLResponse)
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    from app.core.settings.database import engine
    from sqlalchemy import text

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # DB-Check
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
        db_label = "Verbunden"
        db_color = "#22c55e"
    except Exception as e:
        db_status = "error"
        db_label = f"Fehler: {e}"
        db_color = "#ef4444"

    overall_ok = db_status == "ok"
    overall_color = "#22c55e" if overall_ok else "#ef4444"
    overall_text = "Alle Systeme betriebsbereit" if overall_ok else "Systemfehler erkannt"

    checks = [
        ("API", "Betriebsbereit", "#22c55e"),
        ("Datenbank (PostgreSQL)", db_label, db_color),
        ("Auth-Provider (Keycloak)", "Konfiguriert", "#22c55e"),
        ("Storage-Backend", settings.STORAGE_BACKEND.upper(), "#22c55e"),
    ]

    rows = "\n".join(
        f"""<tr>
            <td>{name}</td>
            <td><span class="badge" style="color:{color};background:{color}22;border-color:{color}44">{label}</span></td>
        </tr>"""
        for name, label, color in checks
    )

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30">
    <title>Health Check — {settings.APP_NAME}</title>
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f1117;
            color: #e2e8f0;
            min-height: 100vh;
            padding: 2rem 1rem;
        }}
        .container {{ max-width: 680px; margin: 0 auto; }}

        header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 2rem;
            padding-bottom: 1.25rem;
            border-bottom: 1px solid #1e2330;
        }}
        .logo {{ display: flex; align-items: center; gap: 0.75rem; }}
        .logo-icon {{
            width: 38px; height: 38px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border-radius: 9px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.2rem;
        }}
        .logo h1 {{ font-size: 1.05rem; font-weight: 700; color: #f1f5f9; }}
        .logo span {{ font-size: 0.72rem; color: #64748b; }}
        .back-link {{
            font-size: 0.78rem; color: #64748b; text-decoration: none;
            padding: 0.3rem 0.75rem; border: 1px solid #1e2330; border-radius: 6px;
        }}
        .back-link:hover {{ color: #e2e8f0; border-color: #374151; }}

        .status-banner {{
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid {overall_color}33;
            background: {overall_color}0d;
            display: flex; align-items: center; gap: 1rem;
        }}
        .big-dot {{
            width: 14px; height: 14px; border-radius: 50%;
            background: {overall_color};
            box-shadow: 0 0 0 4px {overall_color}33;
            animation: pulse 2s ease-in-out infinite;
            flex-shrink: 0;
        }}
        @keyframes pulse {{
            0%, 100% {{ box-shadow: 0 0 0 4px {overall_color}33; }}
            50% {{ box-shadow: 0 0 0 8px {overall_color}11; }}
        }}
        .status-banner strong {{ font-size: 1.1rem; color: {overall_color}; }}
        .status-banner p {{ font-size: 0.78rem; color: #64748b; margin-top: 0.2rem; }}

        .card {{
            background: #12181f;
            border: 1px solid #1e2330;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 1rem;
        }}
        .card-title {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #475569;
            font-weight: 600;
            padding: 0.85rem 1.2rem;
            border-bottom: 1px solid #1e2330;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        td {{
            padding: 0.85rem 1.2rem;
            font-size: 0.875rem;
            border-bottom: 1px solid #1a2030;
        }}
        tr:last-child td {{ border-bottom: none; }}
        td:first-child {{ color: #94a3b8; }}
        td:last-child {{ text-align: right; }}
        .badge {{
            font-size: 0.72rem; font-weight: 600;
            padding: 0.2rem 0.6rem; border-radius: 999px;
            border: 1px solid;
        }}

        .meta {{
            font-size: 0.72rem; color: #334155; text-align: center; margin-top: 1.5rem;
        }}
        .meta a {{ color: #475569; text-decoration: none; }}
        .meta a:hover {{ color: #94a3b8; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">
                <div class="logo-icon">💚</div>
                <div>
                    <h1>Health Check</h1>
                    <span>{settings.APP_NAME} — v{settings.APP_VERSION}</span>
                </div>
            </div>
            <a href="/" class="back-link">← Zurück</a>
        </header>

        <div class="status-banner">
            <div class="big-dot"></div>
            <div>
                <strong>{overall_text}</strong>
                <p>Geprüft am {now} &bull; Aktualisiert alle 30 Sekunden</p>
            </div>
        </div>

        <div class="card">
            <div class="card-title">Systemprüfungen</div>
            <table>{rows}</table>
        </div>

        <div class="card">
            <div class="card-title">Details</div>
            <table>
                <tr><td>Anwendung</td><td>{settings.APP_NAME}</td></tr>
                <tr><td>Version</td><td>v{settings.APP_VERSION}</td></tr>
                <tr><td>Umgebung</td><td>{settings.ENVIRONMENT}</td></tr>
                <tr><td>Zeitstempel</td><td>{now}</td></tr>
            </table>
        </div>

        <p class="meta">
            <a href="/">Status</a> &bull;
            <a href="/docs">API-Docs</a> &bull;
            <a href="/system/info">System-Info</a>
        </p>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=200 if overall_ok else 503)
