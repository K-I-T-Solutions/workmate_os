from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.core.settings.config import settings
from datetime import datetime, timezone
import sys
import platform

router = APIRouter(tags=["System"])

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "module": "system",
        "message": "Workmate OS Backend operational 🚀"
    }

@router.get("/info", response_class=HTMLResponse)
async def system_info():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    py_version = sys.version.split(" ")[0]
    os_info = f"{platform.system()} {platform.release()}"

    env = settings.ENVIRONMENT
    env_color = "#22c55e" if env == "production" else "#f59e0b"

    # Keycloak URL nur Host, kein Passwort
    keycloak_host = settings.KEYCLOAK_URL
    realm = settings.KEYCLOAK_REALM

    sections = [
        ("Anwendung", [
            ("Name", settings.APP_NAME),
            ("Version", f"v{settings.APP_VERSION}"),
            ("Umgebung", settings.ENVIRONMENT),
        ]),
        ("Laufzeit", [
            ("Python", py_version),
            ("Betriebssystem", os_info),
            ("Zeitstempel", now),
        ]),
        ("Auth & Sicherheit", [
            ("Provider", "Keycloak OIDC"),
            ("Realm", realm),
            ("Issuer", keycloak_host),
            ("JWT-Algorithmus", settings.JWT_ALGORITHM),
            ("Token-Laufzeit", f"{settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES // 60}h"),
        ]),
        ("Speicher", [
            ("Backend", settings.STORAGE_BACKEND.upper()),
            ("Upload-Verzeichnis", settings.UPLOAD_DIR),
        ]),
    ]

    def make_card(title, rows):
        trs = "\n".join(
            f"<tr><td>{k}</td><td>{v}</td></tr>"
            for k, v in rows
        )
        return f"""<div class="card">
            <div class="card-title">{title}</div>
            <table>{trs}</table>
        </div>"""

    cards = "\n".join(make_card(t, r) for t, r in sections)

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Info — {settings.APP_NAME}</title>
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

        .env-banner {{
            background: {env_color}0d;
            border: 1px solid {env_color}33;
            border-radius: 10px;
            padding: 0.9rem 1.2rem;
            margin-bottom: 1.5rem;
            font-size: 0.82rem;
            color: {env_color};
            display: flex; align-items: center; gap: 0.5rem;
        }}
        .env-dot {{
            width: 8px; height: 8px; border-radius: 50%;
            background: {env_color}; flex-shrink: 0;
        }}

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
            padding: 0.8rem 1.2rem;
            font-size: 0.875rem;
            border-bottom: 1px solid #1a2030;
            word-break: break-all;
        }}
        tr:last-child td {{ border-bottom: none; }}
        td:first-child {{ color: #94a3b8; width: 40%; word-break: normal; }}
        td:last-child {{
            font-family: "SF Mono", "Fira Code", Consolas, monospace;
            font-size: 0.8rem;
            color: #c4b5fd;
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
                <div class="logo-icon">ℹ️</div>
                <div>
                    <h1>System Info</h1>
                    <span>{settings.APP_NAME} — v{settings.APP_VERSION}</span>
                </div>
            </div>
            <a href="/" class="back-link">← Zurück</a>
        </header>

        <div class="env-banner">
            <div class="env-dot"></div>
            Umgebung: <strong>{env.upper()}</strong>
        </div>

        {cards}

        <p class="meta">
            <a href="/">Status</a> &bull;
            <a href="/health">Health</a> &bull;
            <a href="/docs">API-Docs</a>
        </p>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=200)
